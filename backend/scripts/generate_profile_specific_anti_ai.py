import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import PROFILE_DIR, OUTPUT_DIR

PROFILE_FILE = PROFILE_DIR / "style_profile.json"
OUTPUT_FILE = OUTPUT_DIR / "anti_ai_critical_profile.md"

def load_profile():
    if not PROFILE_FILE.exists():
        print(f"Profile not found at {PROFILE_FILE}. Run extract_features.py first.")
        sys.exit(1)
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_rules(profile):
    lines = ["## Critical Anti‑AI Writing Rules (Profile‑Specific)\n"]

    # 1. Em dash usage based on punctuation counts
    punct = profile.get("punctuation", {}).get("per_100_words", {})
    em_dash_count = punct.get("—", 0) + punct.get("–", 0)
    if em_dash_count < 0.1:
        lines.append("- **Em dashes**: The writer rarely uses them. Avoid em dashes entirely; use commas, periods, or parentheses.")
    else:
        lines.append(f"- **Em dashes**: Used sparingly (~{em_dash_count:.1f}/100w). Do not exceed one per 1000 words.")

    # 2. Sentence length variation
    stdev = profile.get("basic_counts", {}).get("stdev_sentence_length", 0)
    if stdev < 5:
        lines.append("- **Sentence length**: The writer shows low variation. Vary sentence length more than the profile suggests to avoid monotony.")
    else:
        lines.append("- **Sentence length**: The writer naturally varies sentence length. Mix short and long sentences as indicated.")

    # 3. Passive voice ratio
    passive = profile.get("syntactic_complexity", {}).get("passive_voice_ratio", 0)
    if passive > 0.2:
        lines.append(f"- **Passive voice**: The writer uses passive voice frequently (~{passive*100:.0f}%). Preserve this tendency, but use active voice when clarity demands it.")
    else:
        lines.append("- **Passive voice**: The writer rarely uses passive voice. Prefer active voice unless the actor is unknown or unimportant.")

    # 4. Contractions
    contractions = profile.get("contractions_per_100_words", 0)
    if contractions < 1:
        lines.append("- **Contractions**: The writer avoids contractions. Use full forms.")
    elif contractions < 3:
        lines.append("- **Contractions**: The writer uses contractions occasionally. Use them sparingly.")
    else:
        lines.append("- **Contractions**: The writer uses contractions frequently. Feel free to use them naturally.")

    # 5. Transition words (overuse)
    trans = profile.get("transitions", {}).get("frequencies", {})
    if trans:
        top_trans = sorted(trans.items(), key=lambda x: x[1], reverse=True)[:3]
        trans_names = ", ".join(w for w, _ in top_trans)
        lines.append(f"- **Transitions**: The writer uses {trans_names} frequently. Avoid overusing these; vary transitions or omit them where the connection is clear.")

    # 6. Pronoun usage
    pron = profile.get("pronoun_usage", {})
    first_person = pron.get("first_person", 0)
    if first_person < 0.01:
        lines.append("- **First person**: The writer writes impersonally. Avoid using 'I' or 'we' unless explicitly required.")
    else:
        lines.append("- **First person**: The writer uses first person sometimes. Use it where natural, but do not overuse.")

    # 7. Hedging
    hedging = profile.get("hedging", {})
    if hedging:
        top_hedge = sorted(hedging.items(), key=lambda x: x[1], reverse=True)[:3]
        hedge_names = ", ".join(w for w, _ in top_hedge)
        lines.append(f"- **Hedging**: The writer uses {hedge_names} to qualify statements. Use similar hedging where appropriate, but avoid stacking multiple hedges.")

    # 8. Boosters
    boosters = profile.get("boosters", {})
    if boosters:
        top_boost = sorted(boosters.items(), key=lambda x: x[1], reverse=True)[:3]
        boost_names = ", ".join(w for w, _ in top_boost)
        lines.append(f"- **Boosters**: The writer uses {boost_names} for emphasis. Use them sparingly and only when the statement truly warrants emphasis.")

    # 9. Function word over/underuse
    over = profile.get("function_words", {}).get("overused", [])
    under = profile.get("function_words", {}).get("underused", [])
    if over:
        over_names = ", ".join(w for w, _ in over[:3])
        lines.append(f"- **Function words overused**: {over_names}. Avoid overusing these words.")
    if under:
        under_names = ", ".join(w for w, _ in under[:3])
        lines.append(f"- **Function words underused**: {under_names}. Do not force these; natural variation is fine.")

    # 10. Sentence starters
    starters = profile.get("sentence_starters", [])
    if starters:
        top_starters = ", ".join(f"'{w}'" for w, _ in starters[:3])
        lines.append(f"- **Sentence starters**: The writer often starts with {top_starters}. Use these patterns, but do not repeat the same starter in every sentence.")

    return "\n".join(lines)

def main():
    profile = load_profile()
    rules = generate_rules(profile)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(rules, encoding="utf-8")
    print(f"Profile-specific anti-AI critical rules saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()