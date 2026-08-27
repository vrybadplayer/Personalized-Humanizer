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

def get_nested_value(data: dict, path: str) -> Any:
    """Retrieve value from nested dict using dot notation and list indices."""
    # Handle list indices like 'sentence_length_percentiles[0]'
    tokens = re.split(r'\.|\[|\]', path)
    current = data
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        if token.isdigit():
            if isinstance(current, list):
                current = current[int(token)]
            else:
                return None
        else:
            if isinstance(current, dict):
                current = current.get(token)
            else:
                return None
    return current

def format_value(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.4f}".rstrip('0').rstrip('.')
    if isinstance(value, list):
        # e.g., top_content_words is list of lists
        if len(value) > 0 and isinstance(value[0], list):
            return ", ".join([f"{item[0]} ({item[1]})" for item in value])
        return ", ".join(map(str, value))
    if isinstance(value, dict):
        # For things like marker_positions, frequencies, etc.
        items = []
        for k, v in value.items():
            if isinstance(v, dict):
                items.append(f"{k}: {v}")
            else:
                items.append(f"{k} ({v})")
        return "; ".join(items[:10])  # limit length
    return str(value)

def fill_template(template: str, profile: dict) -> str:
    # Replace placeholders like {{path.to.value}}
    pattern = re.compile(r'\{\{(.+?)\}\}')
    def replacer(match):
        path = match.group(1).strip()
        val = get_nested_value(profile, path)
        return format_value(val)
    return pattern.sub(replacer, template)

def main():
    profile = load_profile()
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    filled = fill_template(template, profile)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(filled, encoding="utf-8")
    print(f"Template-based style guide saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()