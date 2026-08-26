#!/usr/bin/env python3
"""
Select anti-AI chunks based on the user's style profile and relevance rules.
Usage: python scripts/select_chunks.py
Output: prints selected chunk file paths (one per line) and saves a list to data/output/selected_chunks.txt
"""

import json
import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import PROFILE_DIR, OUTPUT_DIR, BASE_DIR

# Paths
CHUNK_DIR = BASE_DIR / "config" / "anti_ai_chunks"
RELEVANCE_FILE = BASE_DIR / "config" / "chunk_relevance.json"
PROFILE_FILE = PROFILE_DIR / "style_profile.json"
OUTPUT_FILE = OUTPUT_DIR / "selected_chunks.txt"

def load_json(file_path: Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_nested_value(data: dict, path: str) -> Any:
    """Retrieve value from nested dict using dot-separated path."""
    current = data
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current

def check_trigger(profile: dict, trigger: dict) -> bool:
    feature_path = trigger["feature"]
    operator = trigger["operator"]
    threshold = trigger["value"]

    value = get_nested_value(profile, feature_path)
    if value is None:
        return False

    if operator == "any_value_gt":
        # value should be a dict; check if any item's value > threshold
        if isinstance(value, dict):
            return any(v > threshold for v in value.values())
        return False
    elif operator == "lt":
        return value < threshold
    elif operator == "gt":
        return value > threshold
    else:
        print(f"Unknown operator '{operator}'")
        return False

def select_chunks(profile: dict, rules: dict) -> list[str]:
    selected = set(rules.get("always_include", []))

    for chunk_id, chunk_rules in rules.get("conditional", {}).items():
        triggers = chunk_rules.get("triggers", [])
        if any(check_trigger(profile, t) for t in triggers):
            selected.add(chunk_id)

    # Sort by chunk ID for stable order
    return sorted(selected)

def main():
    if not PROFILE_FILE.exists():
        print(f"Profile not found: {PROFILE_FILE}. Run extract_features.py first.")
        sys.exit(1)
    if not RELEVANCE_FILE.exists():
        print(f"Relevance rules not found: {RELEVANCE_FILE}")
        sys.exit(1)

    profile = load_json(PROFILE_FILE)
    rules = load_json(RELEVANCE_FILE)

    selected = select_chunks(profile, rules)
    print("Selected chunks:", selected)

    # Map chunk IDs to filenames
    chunk_files = []
    for chunk_id in selected:
        # Find file with prefix chunk_id in CHUNK_DIR
        matches = list(CHUNK_DIR.glob(f"{chunk_id}_*.md"))
        if matches:
            chunk_files.append(str(matches[0]))
        else:
            print(f"Warning: No file found for chunk {chunk_id}")

    # Save list to output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for path in chunk_files:
            f.write(path + "\n")

    # Also print
    print("Chunk files selected:")
    for p in chunk_files:
        print(" ", p)

if __name__ == "__main__":
    main()