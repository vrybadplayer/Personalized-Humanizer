import json
import sys
import re
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import spacy
from config.settings import PROFILE_DIR, CLEAN_DATA_DIR, OUTPUT_DIR

try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    nlp = None

def load_profile():
    profile_file = PROFILE_DIR / "style_profile.json"
    if not profile_file.exists():
        print(f"Profile not found at {profile_file}. Run extract_features.py first.")
        sys.exit(1)
    with open(profile_file, "r", encoding="utf-8") as f:
        return json.load(f)

def create_summary(profile):
    """Create a brief natural-language summary of the user's stylistic traits."""
    lines = []

    basic = profile.get("basic_counts", {})
    avg_len = basic.get("avg_sentence_length", 0)
    stdev_len = basic.get("stdev_sentence_length", 0)
    lines.append(f"- Average sentence length: {avg_len:.1f} words (std {stdev_len:.1f}).")

    passive = profile.get("syntactic_complexity", {}).get("passive_voice_ratio", 0)
    lines.append(f"- Passive voice: about {passive*100:.0f}% of sentences.")

    lex = profile.get("lexical_diversity", {})
    ttr = lex.get("ttr", 0)
    lines.append(f"- Vocabulary: type-token ratio {ttr:.2f}.")

    read = profile.get("readability", {})
    lines.append(f"- Readability: Flesch {read.get('flesch_reading_ease', 0):.0f}, grade {read.get('flesch_kincaid_grade', 0):.1f}.")

    punct = profile.get("punctuation", {}).get("per_100_words", {})
    if punct:
        punct_str = ", ".join(f"{k}: {v:.1f}" for k, v in sorted(punct.items()))
        lines.append(f"- Punctuation (per 100 words): {punct_str}.")

    trans = profile.get("transitions", {}).get("frequencies", {})
    if trans:
        top = sorted(trans.items(), key=lambda x: x[1], reverse=True)[:3]
        lines.append(f"- Common transitions: {', '.join(w for w, _ in top)}.")

    pron = profile.get("pronoun_usage", {})
    lines.append(f"- Pronouns: 1st {pron.get('first_person', 0):.2%}, 2nd {pron.get('second_person', 0):.2%}, 3rd {pron.get('third_person', 0):.2%}.")

    contractions = profile.get("contractions_per_100_words", 0)
    lines.append(f"- Contractions: {contractions:.1f} per 100 words.")

    starters = profile.get("sentence_starters", [])
    if starters:
        top_starters = ", ".join(f"'{w}'" for w, _ in starters[:3])
        lines.append(f"- Frequent sentence starters: {top_starters}.")

    return "\n".join(lines)

def select_examples(num_examples=3):
    """Select varied, non-citation-heavy, low-domain examples from clean texts."""
    clean_files = list(CLEAN_DATA_DIR.glob("*.txt"))
    if not clean_files or nlp is None:
        return []

    # Load profile to get top content words (domain-specific)
    profile = load_profile()
    top_content = [w for w, _ in profile.get("domain_specific", {}).get("top_content_words", [])[:10]]

    # Citation-like patterns to reject a passage
    citation_patterns = [
        r'\bdoi\b', r'https?://', r'retrieved', r'et al\.', r'\(\d{4}\)',
        r'vol\.', r'pp\.', r'[A-Z][a-z]+,\s+[A-Z]\.\s*\('  # Author, A. (Year)
    ]
    citation_re = re.compile('|'.join(citation_patterns), re.IGNORECASE)

    candidates = []
    for file_path in clean_files:
        text = file_path.read_text(encoding="utf-8")
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        total_sentences = len(sentences)

        # Generate candidate passages of 3-5 sentences, non-overlapping
        for i in range(0, total_sentences - 2, 3):
            # Use up to 5 sentences, but stop at end
            chunk_sentences = sentences[i:i+5]
            chunk = " ".join(chunk_sentences)
            word_count = len(chunk.split())
            if word_count < 30 or word_count > 200:
                continue

            # Reject if citation-heavy
            if citation_re.search(chunk):
                continue

            # Domain score: count occurrences of top content words
            domain_score = sum(chunk.lower().count(w.lower()) for w in top_content)

            # Average sentence length (in words) of the passage
            sent_lengths = [len(s.split()) for s in chunk_sentences if s.strip()]
            avg_len = sum(sent_lengths) / len(sent_lengths) if sent_lengths else 0

            candidates.append({
                "chunk": chunk,
                "domain_score": domain_score,
                "avg_sentence_len": avg_len,
                "word_count": word_count,
                "file_index": len(candidates)  # just for uniqueness
            })

    if not candidates:
        return []

    # Sort by domain score ascending (prefer low domain)
    candidates.sort(key=lambda x: x["domain_score"])

    # Select examples ensuring variety in average sentence length
    selected = []
    # Categorize into short, medium, long based on avg sentence length
    # Short: < 12, Medium: 12-20, Long: >20
    bins = {
        "short": [c for c in candidates if c["avg_sentence_len"] < 12],
        "medium": [c for c in candidates if 12 <= c["avg_sentence_len"] <= 20],
        "long": [c for c in candidates if c["avg_sentence_len"] > 20],
    }

    # Try to pick one from each bin, in order of bin preference
    bin_order = ["medium", "short", "long"]  # medium most common, short/long for variety
    for bin_name in bin_order:
        if len(selected) >= num_examples:
            break
        if bins[bin_name]:
            # Pick the candidate with lowest domain score from that bin
            chosen = bins[bin_name][0]  # already sorted by domain_score
            selected.append(chosen["chunk"])
            # Remove from candidates to avoid duplicates
            candidates = [c for c in candidates if c["chunk"] != chosen["chunk"]]
            # Recompute bins? Not necessary if we just pick the first of each bin.
            # But to be safe, we could re-bin remaining, but for simplicity we'll keep.

    # If still need more, fill with best remaining
    if len(selected) < num_examples:
        for c in candidates:
            if len(selected) >= num_examples:
                break
            if c["chunk"] not in selected:
                selected.append(c["chunk"])

    return selected[:num_examples]

def build_prompt(summary, examples):
    examples_text = "\n".join(f"{i+1}. \"{ex}\"" for i, ex in enumerate(examples))
    prompt = f"""You are an expert in stylometry and anti-AI writing. Based on the following summary and examples, create a concise style guide for mimicking this writer, and also include explicit anti-AI writing instructions.

Summary:
{summary}

Examples:
{examples_text}

Output only a Markdown guide with these sections:
- Tone & Voice
- Sentence Structure
- Vocabulary & Phrasing
- Punctuation & Formatting
- Transitions & Discourse Markers
- Anti-AI Writing Instructions (list key rules to avoid machine detection, such as varying sentence length, avoiding em dashes, not using hollow intensifiers, etc.)

Use bullet points. Be specific and actionable. Do not include domain-specific terms.
"""
    return prompt

def main():
    profile = load_profile()
    summary = create_summary(profile)
    examples = select_examples(5)

    prompt = build_prompt(summary, examples)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prompt_file = OUTPUT_DIR / "prompt.txt"
    prompt_file.write_text(prompt, encoding="utf-8")
    print(f"Prompt saved to {prompt_file}")
    print(f"Prompt length: {len(prompt.split())} words")

if __name__ == "__main__":
    main()