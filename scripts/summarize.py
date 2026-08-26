import json
import sys
import random
from pathlib import Path
from collections import Counter

sys.path.append(str(Path(__file__).resolve().parent.parent))

import spacy
from config.settings import PROFILE_DIR, CLEAN_DATA_DIR, OUTPUT_DIR

# Load spaCy for sentence splitting in example selection
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
    """Create a rich natural-language summary from the profile."""
    lines = []

    # Basic sentence stats
    basic = profile.get("basic_counts", {})
    avg_len = basic.get("avg_sentence_length", 0)
    median_len = basic.get("median_sentence_length", 0)
    stdev_len = basic.get("stdev_sentence_length", 0)
    pcts = basic.get("sentence_length_percentiles", [0,0,0])
    lines.append(f"Sentence length: average {avg_len:.1f} words, median {median_len:.1f}, standard deviation {stdev_len:.1f}. 25th percentile {pcts[0]}, 75th percentile {pcts[2]}. This indicates sentence length is {'consistent' if stdev_len < 5 else 'varied'}.")

    # Passive voice
    passive = profile.get("syntactic_complexity", {}).get("passive_voice_ratio", 0)
    lines.append(f"Passive voice: used in about {passive*100:.0f}% of sentences. The writer {'prefers' if passive > 0.2 else 'avoids'} passive constructions.")

    # Lexical diversity
    lex = profile.get("lexical_diversity", {})
    ttr = lex.get("ttr", 0)
    mattr = lex.get("mattr", 0)
    hapax = lex.get("hapax_legomena_ratio", 0)
    lines.append(f"Vocabulary: type-token ratio {ttr:.2f} (low, typical for technical/academic texts), MATTR {mattr:.2f} (moderate), hapax legomena {hapax:.2f}. The writer uses a mix of repeated technical terms and varied general vocabulary.")

    # Readability
    read = profile.get("readability", {})
    flesch = read.get("flesch_reading_ease", 0)
    grade = read.get("flesch_kincaid_grade", 0)
    lines.append(f"Readability: Flesch Reading Ease {flesch:.1f} (difficult), Flesch-Kincaid Grade {grade:.1f} (college level). The text is formal and complex.")

    # Punctuation
    punct100 = profile.get("punctuation", {}).get("per_100_words", {})
    if punct100:
        punct_desc = ", ".join(f"{char}: {val:.1f}/100w" for char, val in sorted(punct100.items()))
        lines.append(f"Punctuation: {punct_desc}. Commas are used {'frequently' if punct100.get(',',0) > 4 else 'moderately'}, semicolons {'appear occasionally' if punct100.get(';',0) > 0.5 else 'are rare'}.")
    else:
        lines.append("Punctuation: minimal usage.")

    # Transitions
    trans_freq = profile.get("transitions", {}).get("frequencies", {})
    trans_init = profile.get("transitions", {}).get("sentence_initial_counts", {})
    if trans_freq:
        top_trans = sorted(trans_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        trans_desc = ", ".join(f"{w} ({c:.2%})" for w, c in top_trans)
        lines.append(f"Transitions: frequent use of {trans_desc}. Many transitions appear at the start of sentences.")
    else:
        lines.append("Transitions: rarely used.")

    # Function word deviations
    over = profile.get("function_words", {}).get("overused", [])
    under = profile.get("function_words", {}).get("underused", [])
    if over:
        over_desc = ", ".join(f"{w} ({d['ratio']:.1f}x baseline)" for w, d in over[:3])
        lines.append(f"Function words overused: {over_desc}.")
    if under:
        under_desc = ", ".join(f"{w} ({d['ratio']:.1f}x baseline)" for w, d in under[:3])
        lines.append(f"Function words underused: {under_desc}.")

    # POS
    pos = profile.get("pos_distribution", {})
    if pos:
        noun = pos.get("NOUN", 0)
        verb = pos.get("VERB", 0)
        adj = pos.get("ADJ", 0)
        adv = pos.get("ADV", 0)
        pron = pos.get("PRON", 0)
        lines.append(f"Parts of speech: nouns {noun:.0%}, verbs {verb:.0%}, adjectives {adj:.0%}, adverbs {adv:.0%}, pronouns {pron:.0%}. {'Heavy noun usage suggests a descriptive, formal style.' if noun > 0.28 else 'Balanced POS distribution.'}")

    # Hedging and boosters
    hedging = profile.get("hedging", {})
    boosters = profile.get("boosters", {})
    if hedging:
        top_hedge = sorted(hedging.items(), key=lambda x: x[1], reverse=True)[:3]
        lines.append(f"Hedging: uses words like {', '.join(w for w,_ in top_hedge)} to qualify statements.")
    if boosters:
        top_boost = sorted(boosters.items(), key=lambda x: x[1], reverse=True)[:3]
        lines.append(f"Boosters: uses {', '.join(w for w,_ in top_boost)} for emphasis.")

    # Contractions
    contractions = profile.get("contractions_per_100_words", 0)
    lines.append(f"Contractions: {contractions:.1f} per 100 words ({'very rare' if contractions < 1 else 'occasional' if contractions < 3 else 'frequent'}). The writer tends to use {'full forms' if contractions < 1 else 'some contractions'}.")

    # Pronouns
    pron = profile.get("pronoun_usage", {})
    first = pron.get("first_person", 0)
    second = pron.get("second_person", 0)
    third = pron.get("third_person", 0)
    lines.append(f"Pronoun usage: first person {first:.2%}, second person {second:.2%}, third person {third:.2%}. {'Impersonal style with little use of I/we.' if first < 0.01 else 'Personal involvement through first person.'}")

    # Sentence starters
    starters = profile.get("sentence_starters", [])
    if starters:
        start_desc = ", ".join(f"'{w}' ({c})" for w, c in starters[:5])
        lines.append(f"Sentence starters often include: {start_desc}.")

    # Paragraph stats
    para = profile.get("paragraph_stats")
    if para:
        lines.append(f"Paragraphs: average {para['avg_words']:.0f} words, median {para['median_words']:.0f} words. {'Relatively short paragraphs.' if para['avg_words'] < 60 else 'Longer, more developed paragraphs.'}")

    return "\n".join(lines)

def select_examples(num_examples=3):
    """Select varied, non-domain-heavy examples from clean texts."""
    clean_files = list(CLEAN_DATA_DIR.glob("*.txt"))
    if not clean_files or nlp is None:
        return []

    # Load profile to get top content words (domain-specific)
    profile = load_profile()
    top_content = [w for w, _ in profile.get("domain_specific", {}).get("top_content_words", [])[:10]]

    candidates = []
    for file_path in clean_files:
        text = file_path.read_text(encoding="utf-8")
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        # Group sentences into chunks of 3-5 sentences
        for i in range(0, len(sentences) - 4, 3):
            chunk = " ".join(sentences[i:i+4])
            word_count = len(chunk.split())
            if word_count < 30 or word_count > 200:
                continue
            # Domain score: count occurrences of top content words
            domain_score = sum(chunk.lower().count(w.lower()) for w in top_content)
            # Prefer lower domain score (less domain-specific)
            candidates.append((chunk, domain_score, word_count))
        # Also add from start of text (if few candidates)
        if len(candidates) < num_examples:
            # Take first few paragraphs
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            for p in paragraphs[:num_examples]:
                if 30 <= len(p.split()) <= 200:
                    candidates.append((p, 0, len(p.split())))

    if not candidates:
        return []

    # Sort by domain score ascending, then word count descending (prefer moderate)
    candidates.sort(key=lambda x: (x[1], -abs(x[2]-80)))
    selected = []
    for chunk, _, _ in candidates[:num_examples]:
        selected.append(chunk)

    return selected

def build_prompt(summary, examples):
    examples_text = "\n".join(f"{i+1}. \"{ex}\"" for i, ex in enumerate(examples))
    prompt = f"""You are an expert in writing style analysis. Based on the following detailed stylometric summary and the provided examples from the writer, create a style guide in Markdown that can be used to instruct another AI to write in this person’s voice.

Stylometric Summary:
{summary}

Examples from the writer:
{examples_text}

The style guide should include sections for:
- General tone and voice
- Sentence structure and rhythm
- Vocabulary and phrasing preferences
- Punctuation and formatting habits
- Transitional phrases and discourse markers
- Any other noticeable habits (e.g., hedging, use of pronouns, paragraphing)

Important: Do not include domain-specific vocabulary (like technical terms from a particular field) in the style guide. Focus only on structural, syntactic, and stylistic patterns that are independent of the topic. Use the examples to infer patterns beyond the numbers.

Output only the Markdown content.
"""
    return prompt

def main():
    profile = load_profile()
    summary = create_summary(profile)
    print("Stylometric Summary:\n", summary)

    examples = select_examples(3)
    if not examples:
        print("Warning: Could not auto-select examples. You may need to manually add them to the prompt file.")
    else:
        print("\nSelected examples:")
        for i, ex in enumerate(examples):
            print(f"Example {i+1}: {ex[:100]}...")

    prompt = build_prompt(summary, examples)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prompt_file = OUTPUT_DIR / "prompt.txt"
    prompt_file.write_text(prompt, encoding="utf-8")
    print(f"\nPrompt saved to {prompt_file}")

if __name__ == "__main__":
    main()