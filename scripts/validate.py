import json
import sys
from pathlib import Path

# Add both project root and scripts directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
sys.path.append(str(Path(__file__).resolve().parent))

import ollama
from config.settings import PROFILE_DIR, OUTPUT_DIR, VALIDATION_MODEL, OLLAMA_CONTEXT_SIZE
from extract_features import extract_features

# Metrics to compare (keys in the feature dict)
COMPARISON_METRICS = [
    ("basic_counts.avg_sentence_length", "Avg sentence length"),
    ("basic_counts.stdev_sentence_length", "Std sentence length"),
    ("syntactic_complexity.passive_voice_ratio", "Passive ratio"),
    ("lexical_diversity.ttr", "Type-token ratio"),
    ("punctuation.per_100_words.,", "Commas/100w"),
    ("punctuation.per_100_words..", "Periods/100w"),
    ("pos_distribution.NOUN", "Noun ratio"),
    ("pos_distribution.VERB", "Verb ratio"),
    ("contractions_per_100_words", "Contractions/100w"),
    ("pronoun_usage.first_person", "First person ratio"),
]

def get_nested(data, path):
    current = data
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current

def load_profile():
    profile_file = PROFILE_DIR / "style_profile.json"
    if not profile_file.exists():
        print("Profile not found. Run extract_features.py first.")
        sys.exit(1)
    with open(profile_file, "r", encoding="utf-8") as f:
        return json.load(f)

def load_style_guide():
    combined = OUTPUT_DIR / "Personalized-Humanizer-Complete.md"
    simple = OUTPUT_DIR / "Personalized-Humanizer.md"
    for f in [combined, simple]:
        if f.exists():
            return f.read_text(encoding="utf-8")
    print("No style guide found. Run generate_guide.py (and merge_guides.py) first.")
    sys.exit(1)

def generate_sample(style_guide, topic):
    prompt = f"""Using the writing style described in the guide below, write a paragraph of about 200 words on the topic: {topic}.

Style guide:
---
{style_guide}
---
"""

    response = ollama.generate(
        model=VALIDATION_MODEL,
        prompt=prompt,
        options={
            "temperature": 0.5,
            "num_predict": 3000,
            "num_ctx": OLLAMA_CONTEXT_SIZE,
        },
    )
    # For ollama.generate, the result is in response["response"]
    content = response.get("response", "").strip()
    if not content:
        print("Warning: Model returned empty response. Raw response:")
        print(response)
    return content

def main():
    profile = load_profile()
    style_guide = load_style_guide()

    # Neutral topic (can be overridden)
    topic = "the importance of time management in daily life"
    print(f"Generating sample on: '{topic}'...")
    generated_text = generate_sample(style_guide, topic)
    print("\n--- Generated Paragraph ---\n")
    print(generated_text)
    print("\n---------------------------\n")

    # Save the generated sample
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sample_file = OUTPUT_DIR / "validation_sample.txt"
    sample_file.write_text(generated_text, encoding="utf-8")
    print(f"Sample saved to {sample_file}\n")

    # Extract features from generated text
    print("Extracting features from generated text...")
    gen_features = extract_features(generated_text)
    print("Feature extraction complete.\n")

    # Compare metrics
    report_lines = []
    report_lines.append("Validation Report")
    report_lines.append("=" * 50)
    report_lines.append(f"Topic: {topic}\n")
    report_lines.append(f"{'Metric':<30} {'Original':>12} {'Generated':>12} {'Diff':>10}")
    report_lines.append("-" * 70)

    total_diff = 0.0
    count = 0
    for path, label in COMPARISON_METRICS:
        orig_val = get_nested(profile, path)
        gen_val = get_nested(gen_features, path)

        if orig_val is None or gen_val is None:
            continue

        diff = abs(orig_val - gen_val)
        total_diff += diff
        count += 1

        # Format numbers nicely
        if isinstance(orig_val, float) and abs(orig_val) < 0.1:
            orig_str = f"{orig_val:.4f}"
            gen_str = f"{gen_val:.4f}"
            diff_str = f"{diff:.4f}"
        else:
            orig_str = f"{orig_val:.2f}"
            gen_str = f"{gen_val:.2f}"
            diff_str = f"{diff:.2f}"

        report_lines.append(f"{label:<30} {orig_str:>12} {gen_str:>12} {diff_str:>10}")

    report_lines.append("-" * 70)
    avg_diff = total_diff / count if count else 0
    report_lines.append(f"Average absolute difference across {count} metrics: {avg_diff:.4f}")
    report_lines.append("Lower values indicate better style mimicry.")

    report = "\n".join(report_lines)

    report_file = OUTPUT_DIR / "validation_report.txt"
    report_file.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nReport saved to {report_file}")

if __name__ == "__main__":
    main()