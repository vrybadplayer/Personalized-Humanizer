import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import PROFILE_DIR, OUTPUT_DIR, BASE_DIR

TEMPLATE_FILE = BASE_DIR / "config" / "style_template.md"
OUTPUT_FILE = OUTPUT_DIR / "Personalized-Humanizer-Template.md"

def load_profile():
    profile_file = PROFILE_DIR / "style_profile.json"
    if not profile_file.exists():
        print(f"Profile not found at {profile_file}. Run extract_features.py first.")
        sys.exit(1)
    with open(profile_file, "r", encoding="utf-8") as f:
        return json.load(f)

def format_value(value: Any) -> str:
    """Convert a value to a nice string for insertion."""
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.4f}".rstrip('0').rstrip('.')
    if isinstance(value, list):
        # Format list of tuples like [["word", 123], ...] or list of strings
        if len(value) > 0 and isinstance(value[0], (list, tuple)):
            return ", ".join([f"{item[0]} ({item[1]})" for item in value])
        return ", ".join(map(str, value))
    if isinstance(value, dict):
        # For dicts like frequencies, marker_positions, etc.
        items = []
        for k, v in value.items():
            if isinstance(v, dict):
                # e.g., marker_positions: {"however": {"total_count": 20, ...}}
                inner = ", ".join(f"{ik}: {iv}" for ik, iv in v.items())
                items.append(f"{k} ({inner})")
            else:
                items.append(f"{k} ({v})")
        return "; ".join(items)
    return str(value)

def extract_simple_values(profile: dict) -> dict:
    """Map simple placeholder names to values from the profile."""
    v = {}

    # Basic counts
    basic = profile.get("basic_counts", {})
    v["avg_sentence_length"] = format_value(basic.get("avg_sentence_length"))
    percentiles = basic.get("sentence_length_percentiles", [0,0,0])
    v["sentence_length_p25"] = format_value(percentiles[0] if len(percentiles) > 0 else None)
    v["sentence_length_p75"] = format_value(percentiles[2] if len(percentiles) > 2 else None)

    # Syntactic complexity
    syntactic = profile.get("syntactic_complexity", {})
    v["avg_clauses_per_sentence"] = format_value(syntactic.get("clause_complexity", {}).get("avg_clauses_per_sentence"))
    v["subordinate_clause_ratio"] = format_value(syntactic.get("clause_complexity", {}).get("subordinate_clause_ratio"))
    v["passive_voice_ratio"] = format_value(syntactic.get("passive_voice_ratio"))

    # Lexical diversity
    lex = profile.get("lexical_diversity", {})
    v["ttr"] = format_value(lex.get("ttr"))
    v["mattr"] = format_value(lex.get("mattr"))
    v["hapax_legomena_ratio"] = format_value(lex.get("hapax_legomena_ratio"))

    # Domain specific
    domain = profile.get("domain_specific", {})
    v["top_content_words"] = format_value(domain.get("top_content_words"))
    v["favorite_phrases"] = format_value(domain.get("favorite_phrases"))

    # Function words
    func = profile.get("function_words", {})
    v["function_words_overused"] = format_value(func.get("overused"))
    v["function_words_underused"] = format_value(func.get("underused"))

    # POS distribution
    pos = profile.get("pos_distribution", {})
    v["pos_noun"] = format_value(pos.get("NOUN"))
    v["pos_verb"] = format_value(pos.get("VERB"))
    v["pos_adj"] = format_value(pos.get("ADJ"))
    v["pos_adv"] = format_value(pos.get("ADV"))
    v["pos_pron"] = format_value(pos.get("PRON"))
    v["pos_det"] = format_value(pos.get("DET"))
    v["pos_adp"] = format_value(pos.get("ADP"))
    v["pos_cconj"] = format_value(pos.get("CCONJ"))

    # Punctuation per 100 words
    punct100 = profile.get("punctuation", {}).get("per_100_words", {})
    v["punct_100_comma"] = format_value(punct100.get(","))
    v["punct_100_period"] = format_value(punct100.get("."))
    v["punct_100_semicolon"] = format_value(punct100.get(";"))
    v["punct_100_colon"] = format_value(punct100.get(":"))
    v["punct_100_question"] = format_value(punct100.get("?"))
    v["punct_100_exclamation"] = format_value(punct100.get("!"))
    v["punct_100_em_dash"] = format_value(punct100.get("—"))
    v["punct_100_en_dash"] = format_value(punct100.get("–"))

    # Punctuation per sentence
    punct_sent = profile.get("punctuation", {}).get("per_sentence", {})
    v["punct_sent_comma"] = format_value(punct_sent.get(","))
    v["punct_sent_period"] = format_value(punct_sent.get("."))
    v["punct_sent_semicolon"] = format_value(punct_sent.get(";"))
    v["punct_sent_colon"] = format_value(punct_sent.get(":"))
    v["punct_sent_question"] = format_value(punct_sent.get("?"))
    v["punct_sent_exclamation"] = format_value(punct_sent.get("!"))

    # Readability
    read = profile.get("readability", {})
    v["flesch_reading_ease"] = format_value(read.get("flesch_reading_ease"))
    v["flesch_kincaid_grade"] = format_value(read.get("flesch_kincaid_grade"))
    v["gunning_fog"] = format_value(read.get("gunning_fog"))

    # Transitions
    trans = profile.get("transitions", {})
    v["frequent_transitions"] = format_value(trans.get("frequencies"))
    v["marker_positions"] = format_value(trans.get("marker_positions"))

    # Hedging & boosters
    v["hedging_words"] = format_value(profile.get("hedging"))
    v["boosters"] = format_value(profile.get("boosters"))
    v["contractions_per_100_words"] = format_value(profile.get("contractions_per_100_words"))

    # Pronoun usage
    pron = profile.get("pronoun_usage", {})
    v["pronoun_first_person"] = format_value(pron.get("first_person"))
    v["pronoun_second_person"] = format_value(pron.get("second_person"))
    v["pronoun_third_person"] = format_value(pron.get("third_person"))

    # Sentence starters
    v["sentence_starters"] = format_value(profile.get("sentence_starters"))

    # Paragraph stats
    para = profile.get("paragraph_stats")
    if para:
        v["paragraph_avg_words"] = format_value(para.get("avg_words"))
        v["paragraph_median_words"] = format_value(para.get("median_words"))
        v["paragraph_stdev_words"] = format_value(para.get("stdev_words"))
        pcts = para.get("percentiles", [0,0,0])
        v["paragraph_p25"] = format_value(pcts[0] if len(pcts) > 0 else None)
        v["paragraph_p50"] = format_value(pcts[1] if len(pcts) > 1 else None)
        v["paragraph_p75"] = format_value(pcts[2] if len(pcts) > 2 else None)
    else:
        for key in ["paragraph_avg_words", "paragraph_median_words", "paragraph_stdev_words",
                    "paragraph_p25", "paragraph_p50", "paragraph_p75"]:
            v[key] = "N/A"

    return v

def fill_template(template: str, values: dict) -> str:
    """Replace {{placeholder}} with values from the dict."""
    pattern = re.compile(r'\{\{(\w+)\}\}')
    def replacer(match):
        key = match.group(1)
        return values.get(key, "N/A")
    return pattern.sub(replacer, template)

def main():
    profile = load_profile()
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    values = extract_simple_values(profile)
    filled = fill_template(template, values)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(filled, encoding="utf-8")
    print(f"Template-based style guide saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()