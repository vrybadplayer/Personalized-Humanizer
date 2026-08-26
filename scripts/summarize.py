import json
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import PROFILE_DIR, CLEAN_DATA_DIR, OUTPUT_DIR

def load_profile():
    profile_file = PROFILE_DIR / "style_profile.json"
    if not profile_file.exists():
        print(f"Profile not found at {profile_file}. Run extract_features.py first.")
        sys.exit(1)
    with open(profile_file, "r", encoding="utf-8") as f:
        return json.load(f)

def create_summary(profile):
    """Convert stylometric features into a natural-language summary."""
    basic = profile.get("basic_counts", {})
    lexical = profile.get("lexical_diversity", {})
    syntactic = profile.get("syntactic_complexity", {})
    readability = profile.get("readability", {})
    punct = profile.get("punctuation_usage_per_100_words", {})
    transitions = profile.get("transition_word_frequencies", {})

    lines = []

    # Sentence length
    avg = basic.get("avg_sentence_length", 0)
    stdev = basic.get("stdev_sentence_length", 0)
    median = basic.get("median_sentence_length", 0)
    lines.append(f"- Average sentence length: {avg:.1f} words (median {median:.1f}, std {stdev:.1f}).")

    # Passive voice
    passive = syntactic.get("passive_voice_ratio", 0)
    lines.append(f"- Passive voice appears in about {passive*100:.0f}% of sentences.")

    # Lexical diversity
    ttr = lexical.get("ttr", 0)
    mattr = lexical.get("mattr", 0)
    hapax = lexical.get("hapax_legomena_ratio", 0)
    lines.append(f"- Lexical diversity: type-token ratio {ttr:.2f}, MATTR {mattr:.2f}, hapax legomena ratio {hapax:.2f}.")

    # Readability
    flesch = readability.get("flesch_reading_ease", 0)
    grade = readability.get("flesch_kincaid_grade", 0)
    lines.append(f"- Readability: Flesch Reading Ease {flesch:.1f}, Flesch-Kincaid Grade {grade:.1f}.")

    # Punctuation
    if punct:
        punct_desc = ", ".join(f"{char}: {count:.1f}/100 words" for char, count in sorted(punct.items()))
        lines.append(f"- Punctuation usage (per 100 words): {punct_desc}.")
    else:
        lines.append("- Punctuation usage: minimal.")

    # Transition words
    if transitions:
        top_trans = sorted(transitions.items(), key=lambda x: x[1], reverse=True)[:5]
        trans_desc = ", ".join(f"{word} ({count:.2%})" for word, count in top_trans)
        lines.append(f"- Frequent transition words/phrases: {trans_desc}.")
    else:
        lines.append("- Transition words: rarely used.")

    # Function word frequencies (optional: mention distinctive ones)
    func_freq = profile.get("function_word_frequencies", {})
    if func_freq:
        # Show top 5 most frequent function words (relative to typical English)
        typical = {"the": 0.06, "and": 0.03, "of": 0.03, "to": 0.02, "a": 0.02}
        distinctive = []
        for word, freq in func_freq.items():
            if word in typical and freq > typical[word] * 1.5:
                distinctive.append(f"{word} ({freq:.2%} vs typical {typical[word]:.2%})")
        if distinctive:
            lines.append(f"- Uses function words more than typical: {', '.join(distinctive[:5])}.")

    # POS distribution (optional: highlight unusual proportions)
    pos = profile.get("pos_distribution", {})
    if pos:
        # Common proportions: NOUN 0.2, VERB 0.15, ADJ 0.08, ADV 0.05, PRON 0.1
        interesting = []
        for tag, prop in pos.items():
            if tag in ["NOUN", "VERB", "ADJ", "ADV", "PRON"] and prop > 0.25:
                interesting.append(f"{tag} ({prop:.0%})")
        if interesting:
            lines.append(f"- High proportion of: {', '.join(interesting)}.")

    return "\n".join(lines)

def select_few_shot_examples(num_examples=3):
    """
    Simple heuristic to pick few-shot examples:
    - Read all clean text files, split into paragraphs.
    - Choose paragraphs of moderate length (50-150 words) that are not too domain-specific.
    - Return list of strings.
    """
    examples = []
    clean_files = list(CLEAN_DATA_DIR.glob("*.txt"))
    if not clean_files:
        print("No clean text files found for examples.")
        return examples

    for file_path in clean_files:
        text = file_path.read_text(encoding="utf-8")
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        # Filter by length
        candidates = [p for p in paragraphs if 50 <= len(p.split()) <= 150]
        # Heuristic: avoid paragraphs containing many of the top content words (we don't know them yet)
        # For now, just take first few candidates
        for para in candidates[:num_examples]:
            examples.append(para)
        if len(examples) >= num_examples:
            break

    # If not enough, take longer paragraphs
    if len(examples) < num_examples:
        for file_path in clean_files:
            text = file_path.read_text(encoding="utf-8")
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            for para in paragraphs:
                if para not in examples and 20 <= len(para.split()) <= 200:
                    examples.append(para)
                if len(examples) >= num_examples:
                    break

    return examples[:num_examples]

def build_prompt(summary, examples):
    prompt_template = """You are an expert in writing style analysis. Based on the following stylometric summary and the provided examples, create a detailed style guide in Markdown that can be used to instruct another AI to write in this person’s voice.

Stylometric Summary:
{summary}

Examples from the writer:
{examples}

The style guide should include sections for:
- General tone and voice
- Sentence structure and length
- Vocabulary and phrasing
- Punctuation and formatting
- Transitional phrases and discourse markers
- Any other noticeable habits

Important: Do not include domain-specific vocabulary (like technical terms from a particular field) in the style guide. Focus only on structural, syntactic, and stylistic patterns that are independent of the topic.

Output only the Markdown content.
"""
    examples_text = "\n".join(f"{i+1}. \"{ex}\"" for i, ex in enumerate(examples))
    return prompt_template.format(summary=summary, examples=examples_text)

def main():
    profile = load_profile()
    summary = create_summary(profile)
    print("Stylometric Summary:\n", summary)

    # Select few-shot examples automatically (or you can manually provide)
    examples = select_few_shot_examples(3)
    if not examples:
        print("Warning: No suitable examples found. You may need to manually add some.")
    else:
        print("\nSelected examples:")
        for i, ex in enumerate(examples):
            print(f"Example {i+1}: {ex[:100]}...")

    prompt = build_prompt(summary, examples)

    # Save prompt to file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prompt_file = OUTPUT_DIR / "prompt.txt"
    prompt_file.write_text(prompt, encoding="utf-8")
    print(f"\nPrompt saved to {prompt_file}")

if __name__ == "__main__":
    main()