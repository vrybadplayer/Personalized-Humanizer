#!/usr/bin/env python3
"""
Select top N anti-AI chunks based on the user's style profile and relevance rules.
Usage: python scripts/select_chunks.py [--top N]
Default N = 3
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import PROFILE_DIR, OUTPUT_DIR, BASE_DIR

CHUNK_DIR = BASE_DIR / "config" / "anti_ai_chunks"
RELEVANCE_FILE = BASE_DIR / "config" / "chunk_relevance.json"
PROFILE_FILE = PROFILE_DIR / "style_profile.json"
OUTPUT_FILE = OUTPUT_DIR / "selected_chunks.txt"

def load_json(file_path: Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_nested_value(data: dict, path: str) -> Any:
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

def select_chunks(profile: dict, rules: dict, top_n: int = 3) -> list[str]:
    # Priority order for always_include chunks (lower number = higher priority)
    priority = {
        "C01": 1,   # Formatting
        "C02": 2,   # Sentence structure
        "C03": 3,   # Vocabulary
        "C06": 4,   # AI-specific artifacts
        "C07": 5,   # Tone calibration
    }
    always = rules.get("always_include", [])
    # Sort always_include by priority (if not in priority, put at end)
    always_sorted = sorted(always, key=lambda x: priority.get(x, 99))

    conditional = rules.get("conditional", {})
    selected_conditional = []
    for chunk_id, chunk_rules in conditional.items():
        if any(check_trigger(profile, t) for t in chunk_rules.get("triggers", [])):
            selected_conditional.append(chunk_id)

    # Combine: always first (by priority), then conditional in order of appearance
    combined = always_sorted + [c for c in selected_conditional if c not in always_sorted]
    # Take top N
    return combined[:top_n]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=3, help="Number of chunks to select (default 3)")
    args = parser.parse_args()

    if not PROFILE_FILE.exists():
        print(f"Profile not found: {PROFILE_FILE}. Run extract_features.py first.")
        sys.exit(1)
    if not RELEVANCE_FILE.exists():
        print(f"Relevance rules not found: {RELEVANCE_FILE}")
        sys.exit(1)

    profile = load_json(PROFILE_FILE)
    rules = load_json(RELEVANCE_FILE)

    selected = select_chunks(profile, rules, top_n=args.top)
    print("Selected chunks:", selected)

    chunk_files = []
    for chunk_id in selected:
        matches = list(CHUNK_DIR.glob(f"{chunk_id}_*.md"))
        if matches:
            chunk_files.append(str(matches[0]))
        else:
            print(f"Warning: No file found for chunk {chunk_id}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for path in chunk_files:
            f.write(path + "\n")

    print("Chunk files selected:")
    for p in chunk_files:
        print(" ", p)

if __name__ == "__main__":
    main()