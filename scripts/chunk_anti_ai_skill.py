#!/usr/bin/env python3
"""
Chunk the raw anti-AI writing skill markdown into 10 thematic chunks.
Usage: python scripts/chunk_anti_ai_skill.py [input_file] [output_dir]
Defaults are read from config/settings.py:
    CHUNK_INPUT_FILE (default: anti_ai_skill_raw.md)
    CHUNK_OUTPUT_DIR (default: config/anti_ai_chunks)
"""

import sys
import re
from pathlib import Path

# Add project root to sys.path for settings
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import CHUNK_INPUT_FILE, CHUNK_OUTPUT_DIR

# Mapping from heading text (lowercased, stripped) to chunk ID.
# We include both top-level (##) and subsection (###) headings.
CHUNK_MAP = {
    # Top-level headings
    "severity tiers": "C09",
    "context profiles": "C10",
    "voice profiles": "C07",
    "house style": "C10",
    "output format": "C10",
    "tone calibration": "C07",
    "never inject these": "C07",
    "self-reference escape hatch": "C10",

    # Subsections under "What to remove or fix"
    "formatting": "C01",
    "sentence structure": "C02",
    "words and phrases to replace": "C03",
    "template phrases (avoid)": "C03",
    "transition phrases to remove or rewrite": "C04",
    "structural issues": "C05",
    "significance inflation": "C03",
    "aphorism formulas": "C03",
    "generic future-narrative closers": "C03",
    "hedge-stacked predictions": "C03",
    "\"real/actual\" adjective inflation": "C03",
    "moral-adjective category errors": "C03",
    "hashtag stuffing": "C01",
    "bullet lists of bare noun phrases": "C01",
    "copula avoidance": "C02",
    "subjectless fragments and agentless passives": "C02",
    "synonym cycling": "C02",
    "vague attributions": "C02",
    "filler phrases": "C02",
    "generic conclusions": "C03",
    "chatbot artifacts": "C06",
    "\"let's\" constructions": "C02",
    "notability name-dropping": "C06",
    "vague third-party validation": "C06",
    "superficial -ing analyses": "C03",
    "promotional language": "C03",
    "formulaic challenges": "C03",
    "speculative scenario openers": "C05",
    "false ranges": "C03",
    "inline-header lists": "C01",
    "list-label periods": "C01",
    "title case headings": "C01",
    "hyphenated modifier stacking": "C01",
    "unnecessary hyphenation": "C01",
    "cutoff disclaimers": "C06",
    "speculative gap-filling": "C06",
    "unfilled placeholders": "C06",
    "chatbot citation markup leaks": "C06",
    "ai-tool url parameters": "C06",
    "novelty inflation": "C03",
    "infomercial engagement hooks": "C06",
    "social endorsement closers": "C06",
    "emotional flatline": "C06",
    "lingering-attention claims": "C06",
    "false concession structure": "C02",
    "invented contrast-pair mirroring": "C03",
    "rhetorical question openers": "C04",
    "parenthetical hedging": "C04",
    "numbered list inflation": "C05",
    "reasoning chain artifacts": "C05",
    "sycophantic tone": "C06",
    "narrated candor": "C06",
    "acknowledgment loops": "C06",
    "confidence calibration phrases": "C04",
    "self-labeling significance": "C04",
    "wall-of-text replies (missing line breaks)": "C05",
    "recap-flattery opener": "C06",
    "excessive structure": "C05",
    "diff-anchored writing": "C05",
    "manufactured punchlines and staccato drama": "C02",
    "rhythm and uniformity": "C02",
    "vocabulary diversity (stylometric)": "C08",
    "paragraph-reshuffle immunity (structure test)": "C05",
    "treadmill effect / low information density (content test)": "C05",
    "when to rewrite from scratch vs. patch": "C09",
}

# Chunk file names (without extension)
CHUNK_FILES = {
    "C01": "C01_formatting_typography",
    "C02": "C02_sentence_structure_rhythm",
    "C03": "C03_vocabulary_word_choices",
    "C04": "C04_transitions_discourse",
    "C05": "C05_structural_issues",
    "C06": "C06_ai_specific_artifacts",
    "C07": "C07_tone_calibration_voice",
    "C08": "C08_stylometric_signals",
    "C09": "C09_severity_tiers",
    "C10": "C10_self_reference_meta",
}

def normalize_heading(text):
    """Normalize heading text for mapping."""
    return text.strip().lower()

def split_markdown_by_headings(content):
    """
    Parse markdown content into a list of (level, heading, body) tuples.
    Handles both ## and ### headings.
    """
    lines = content.splitlines()
    sections = []
    current_level = None
    current_heading = None
    current_body = []

    for line in lines:
        if line.startswith('## ') or line.startswith('### '):
            # Save previous section
            if current_heading is not None:
                sections.append((current_level, current_heading, '\n'.join(current_body).strip()))
            # Start new section
            level = 2 if line.startswith('## ') else 3
            heading = line[3:].strip() if level == 2 else line[4:].strip()
            current_level = level
            current_heading = heading
            current_body = []
        else:
            if current_heading is not None:
                current_body.append(line)
    # Add last section
    if current_heading is not None:
        sections.append((current_level, current_heading, '\n'.join(current_body).strip()))
    return sections

def assign_chunk(level, heading):
    """Return chunk ID for a heading, or None if not mapped."""
    norm = normalize_heading(heading)
    if norm in CHUNK_MAP:
        return CHUNK_MAP[norm]

    # Fallback keyword matching
    if 'format' in norm or 'typography' in norm or 'dash' in norm or 'bold' in norm or 'emoji' in norm or 'curly' in norm:
        return "C01"
    if 'sentence' in norm or 'rhythm' in norm or 'uniformity' in norm or 'fragment' in norm or 'passive' in norm or 'synonym' in norm or 'filler' in norm or 'let' in norm:
        return "C02"
    if 'word' in norm or 'phrase' in norm or 'vocabulary' in norm or 'template' in norm or 'promotional' in norm or 'false range' in norm or 'hedge' in norm or 'aphorism' in norm or 'moral' in norm or 'real' in norm or 'significance' in norm or 'inflation' in norm or 'novelty' in norm:
        return "C03"
    if 'transition' in norm or 'discourse' in norm or 'rhetorical question' in norm or 'parenthetical' in norm or 'confidence' in norm or 'self-labeling' in norm:
        return "C04"
    if 'structur' in norm or 'paragraph' in norm or 'heading' in norm or 'list' in norm or 'number' in norm or 'reasoning' in norm or 'wall' in norm or 'reshuffle' in norm or 'treadmill' in norm or 'diff' in norm or 'excessive' in norm:
        return "C05"
    if 'artifact' in norm or 'cutoff' in norm or 'speculative gap' in norm or 'placeholder' in norm or 'citation' in norm or 'url' in norm or 'chatbot' in norm or 'sycophant' in norm or 'narrated' in norm or 'acknowledgment' in norm or 'lingering' in norm or 'social endorsement' in norm or 'emotional' in norm or 'infomercial' in norm or 'recap' in norm or 'notability' in norm or 'third-party' in norm:
        return "C06"
    if 'tone' in norm or 'voice' in norm or 'never inject' in norm or 'calibration' in norm:
        return "C07"
    if 'stylometric' in norm or 'ttr' in norm or 'burstiness' in norm:
        return "C08"
    if 'severity' in norm or 'quick pass' in norm or 'rewrite from scratch' in norm:
        return "C09"
    if 'self-reference' in norm or 'context profile' in norm or 'house style' in norm or 'output format' in norm or 'mechanical' in norm:
        return "C10"

    print(f"Warning: unmapped heading '{heading}' -> defaulting to C10")
    return "C10"

def main(input_file=None, output_dir=None):
    if input_file is None:
        input_file = CHUNK_INPUT_FILE
    if output_dir is None:
        output_dir = CHUNK_OUTPUT_DIR

    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Input file {input_path} not found.")
        sys.exit(1)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    content = input_path.read_text(encoding='utf-8')
    sections = split_markdown_by_headings(content)

    chunk_buffers = {chunk_id: [] for chunk_id in CHUNK_FILES.keys()}

    for level, heading, body in sections:
        chunk_id = assign_chunk(level, heading)
        heading_prefix = '#' * level + ' '
        chunk_buffers[chunk_id].append(f"{heading_prefix}{heading}\n{body}")

    for chunk_id, buffer in chunk_buffers.items():
        if not buffer:
            print(f"Chunk {chunk_id} has no content; skipping file.")
            continue
        chunk_text = "\n\n".join(buffer)
        file_name = CHUNK_FILES[chunk_id] + ".md"
        file_path = output_path / file_name
        file_path.write_text(chunk_text, encoding='utf-8')
        print(f"Wrote {file_path}")

    print("Chunking complete.")

if __name__ == "__main__":
    args = sys.argv[1:]
    input_file = args[0] if len(args) >= 1 else CHUNK_INPUT_FILE
    output_dir = args[1] if len(args) >= 2 else CHUNK_OUTPUT_DIR
    main(input_file, output_dir)