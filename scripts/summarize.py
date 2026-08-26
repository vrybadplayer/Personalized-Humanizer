import json
import sys
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

def select_examples(num_examples=2):
    """Select short, less domain-specific examples."""
    clean_files = list(CLEAN_DATA_DIR.glob("*.txt"))
    if not clean_files or nlp is None:
        return []

    profile = load_profile()
    top_content = [w for w, _ in profile.get("domain_specific", {}).get("top_content_words", [])[:5]]

    candidates = []
    for file_path in clean_files:
        text = file_path.read_text(encoding="utf-8")
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        for i in range(0, len(sentences) - 3, 2):
            chunk = " ".join(sentences[i:i+3])
            if 30 <= len(chunk.split()) <= 120:
                domain_score = sum(chunk.lower().count(w.lower()) for w in top_content)
                candidates.append((chunk, domain_score))
        if len(candidates) < num_examples:
            for p in text.split('\n\n')[:num_examples]:
                if 30 <= len(p.split()) <= 120:
                    candidates.append((p, 0))

    candidates.sort(key=lambda x: x[1])
    return [c[0] for c in candidates[:num_examples]]

def build_prompt(summary, examples):
    examples_text = "\n".join(f"{i+1}. \"{ex}\"" for i, ex in enumerate(examples))
    prompt = f"""You are an expert in stylometry. Based on the following summary and examples, create a concise style guide for mimicking this writer.

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

Use bullet points. Be specific and actionable. Do not include domain-specific terms.
"""
    return prompt

def main():
    profile = load_profile()
    summary = create_summary(profile)
    examples = select_examples(2)

    prompt = build_prompt(summary, examples)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prompt_file = OUTPUT_DIR / "prompt.txt"
    prompt_file.write_text(prompt, encoding="utf-8")
    print(f"Prompt saved to {prompt_file}")
    print(f"Prompt length: {len(prompt.split())} words")

if __name__ == "__main__":
    main()