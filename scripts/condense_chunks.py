#!/usr/bin/env python3
"""
Condense selected anti-AI chunks by extracting actionable rules.
Usage: python scripts/condense_chunks.py
Reads data/output/selected_chunks.txt, condenses each chunk, writes data/output/condensed_chunks.md
"""

import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import OUTPUT_DIR, BASE_DIR

SELECTED_FILE = OUTPUT_DIR / "selected_chunks.txt"
CONDENSED_FILE = OUTPUT_DIR / "condensed_chunks.md"

def condense_chunk(content: str) -> str:
    """
    Extract lines that look like rules:
    - Bullet points starting with '-', '*', or '•'
    - Lines containing '→' (replacement arrows)
    - Lines that are short and start with capital letter (heuristic)
    Remove headings except the first, long paragraphs, and meta text.
    """
    lines = content.splitlines()
    kept = []
    current_heading = ""
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Keep headings (but only the first two levels)
        if stripped.startswith("###") or stripped.startswith("##"):
            if stripped.startswith("###"):
                kept.append(stripped)
            elif stripped.startswith("##"):
                # For ## headings, keep if it's the first (title) or short
                if len(kept) == 0:
                    kept.append(stripped)
                else:
                    # Skip long section headings to save space
                    if len(stripped) < 80:
                        kept.append(stripped)
            continue
        # Keep bullet points, replacement arrows, and short actionable sentences
        if stripped.startswith(("-", "*", "•")) or "→" in stripped:
            kept.append(stripped)
        elif len(stripped.split()) < 25 and (stripped[0].isupper() or stripped[0].isdigit()):
            # Short sentence that might be a rule
            if not stripped.startswith(("Example:", "Note:", "Distinct from", "Adapted from", "Carve-out", "The", "This", "These", "When", "In", "For", "If", "As")):
                kept.append(stripped)

    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for line in kept:
        if line.lower() not in seen:
            seen.add(line.lower())
            unique.append(line)

    # If too few lines, fallback to original content
    if len(unique) < 5:
        return content

    return "\n".join(unique)

def main():
    if not SELECTED_FILE.exists():
        print("Selected chunks file not found. Run select_chunks.py first.")
        sys.exit(1)

    chunk_paths = []
    with open(SELECTED_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunk_paths.append(line)

    condensed_parts = []
    for path_str in chunk_paths:
        chunk_file = Path(path_str)
        if not chunk_file.exists():
            print(f"Missing chunk file: {path_str}")
            continue
        content = chunk_file.read_text(encoding="utf-8")
        # Use the filename as a mini header
        header = f"### {chunk_file.stem.replace('_', ' ')}"
        condensed = condense_chunk(content)
        condensed_parts.append(f"{header}\n{condensed}")

    final_condensed = "\n\n".join(condensed_parts)

    CONDENSED_FILE.write_text(final_condensed, encoding="utf-8")
    print(f"Condensed chunks saved to {CONDENSED_FILE}")
    print(f"Original selected: {len(chunk_paths)} chunks, condensed length: {len(final_condensed.split())} words")

if __name__ == "__main__":
    main()