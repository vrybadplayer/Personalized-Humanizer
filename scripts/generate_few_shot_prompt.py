import json
import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import spacy
from config.settings import CLEAN_DATA_DIR, OUTPUT_DIR, PROFILE_DIR, FEW_SHOT_EXAMPLE_COUNT

try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    nlp = None

def load_profile():
    profile_file = PROFILE_DIR / "style_profile.json"
    if not profile_file.exists():
        return {}
    with open(profile_file, "r", encoding="utf-8") as f:
        return json.load(f)

def is_code_snippet(text: str) -> bool:
    """Return True if text looks like code or pseudocode."""
    # Patterns indicative of code or pseudo-code
    code_indicators = [
        r'\b(void|int|char|float|double|string|boolean|bool)\s+\w+\s*\(',
        r'#include\s*<',
        r'\b(if|for|while|switch|case|return|break|continue|else|do|end|BEGIN|END)\b\s*[({:]?\s*$',
        r'\b\d+\s*(=|==|<|>|<=|>=|!=)\s*\d+',
        r'\b(start|end)\s+program\b',
        r'\b(read|write|display|update)\s+[A-Z_]+\b',
        r'[{};]',
        r'\]\s*$',
        r'^\s*(<[A-Za-z0-9]+>|</[A-Za-z0-9]+>)\s*$',
        r'^\s*[-*]?\s*(Figure|Table|Use Case|Diagram|Sequence|Collaboration|Chapter|Appendix|Section)\s+[\d.:]',
        r'^\s*(Figure|Table)\s+\d+\.\d+',
        r'^\s*[A-Z][a-z]+ \d+\.\d+\s*$',
    ]
    compiled = [re.compile(p, re.IGNORECASE) for p in code_indicators]
    lines = text.strip().splitlines()
    code_lines = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if any(p.search(line) for p in compiled):
            code_lines += 1
    # If more than 30% of lines look like code, reject
    if code_lines / max(1, len(lines)) > 0.3:
        return True
    return False

def is_figure_or_table_caption(text: str) -> bool:
    """Return True if text is mostly a caption or reference to figures/tables."""
    patterns = [
        r'^\s*(Figure|Table)\s+\d+\.\d+',
        r'^\s*(Use Case Description|Sequence Diagram|Collaboration Diagram)\s*$',
        r'^\s*(View|Add|Delete|Modify|Calibrate|Link|Irrigation Control|Media Management|Backend & Infrastructure Module)\s*$',
        r'^\s*Table of Contents',
        r'^\s*Chapter\s+\d+',
        r'^\s*References',
    ]
    compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
    lines = text.strip().splitlines()
    matches = sum(1 for line in lines if any(p.search(line.strip()) for p in compiled))
    return matches / max(1, len(lines)) > 0.5

def is_mostly_non_prose(text: str) -> bool:
    """Return True if text contains many non-alphabetic characters or fragmentary lines."""
    alpha_ratio = sum(c.isalpha() for c in text) / max(1, len(text))
    if alpha_ratio < 0.6:
        return True
    # Check for many very short sentences (<4 words), indicative of lists or captions
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    if len(sentences) == 0:
        return True
    short_sentences = sum(1 for s in sentences if len(s.split()) < 4)
    if short_sentences / max(1, len(sentences)) > 0.5:
        return True
    return False

def select_passages(num_passages):
    """Select varied, non-code, non-caption, low-domain, deduplicated prose passages."""
    clean_files = list(CLEAN_DATA_DIR.glob("*.txt"))
    if not clean_files or nlp is None:
        return []

    profile = load_profile()
    top_content = [w for w, _ in profile.get("domain_specific", {}).get("top_content_words", [])[:10]]

    citation_patterns = [
        r'\bdoi\b', r'https?://', r'retrieved', r'et al\.', r'\(\d{4}\)',
        r'vol\.', r'pp\.', r'[A-Z][a-z]+,\s+[A-Z]\.\s*\('
    ]
    citation_re = re.compile('|'.join(citation_patterns), re.IGNORECASE)

    candidates = []
    seen_chunks = set()  # for deduplication

    for file_path in clean_files:
        text = file_path.read_text(encoding="utf-8")
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        total = len(sentences)

        for i in range(0, total - 2, 3):
            chunk_sentences = sentences[i:i+5]
            chunk = " ".join(chunk_sentences)
            word_count = len(chunk.split())
            if word_count < 30 or word_count > 200:
                continue
            if citation_re.search(chunk):
                continue
            if is_code_snippet(chunk) or is_figure_or_table_caption(chunk) or is_mostly_non_prose(chunk):
                continue

            # Normalize for dedup
            normalized = re.sub(r'\s+', ' ', chunk).strip().lower()
            if normalized in seen_chunks:
                continue
            seen_chunks.add(normalized)

            domain_score = sum(chunk.lower().count(w.lower()) for w in top_content)
            avg_len = sum(len(s.split()) for s in chunk_sentences if s.strip()) / max(1, len(chunk_sentences))
            candidates.append({
                "chunk": chunk,
                "domain_score": domain_score,
                "avg_sentence_len": avg_len,
                "word_count": word_count
            })

    if not candidates:
        return []

    # Sort by domain score ascending (lower domain first)
    candidates.sort(key=lambda x: (x["domain_score"], -x["word_count"]))

    # Binning by average sentence length for variety
    bins = {
        "short": [c for c in candidates if c["avg_sentence_len"] < 12],
        "medium": [c for c in candidates if 12 <= c["avg_sentence_len"] <= 20],
        "long": [c for c in candidates if c["avg_sentence_len"] > 20],
    }

    selected = []
    bin_names = ["medium", "short", "long"]
    idx = 0
    while len(selected) < num_passages and any(bins.values()):
        bin_name = bin_names[idx % len(bin_names)]
        if bins[bin_name]:
            chosen = bins[bin_name].pop(0)
            selected.append(chosen["chunk"])
        idx += 1
        if all(not bins[b] for b in bins):
            break

    if len(selected) < num_passages:
        for c in candidates:
            if len(selected) >= num_passages:
                break
            if c["chunk"] not in selected:
                selected.append(c["chunk"])

    return selected[:num_passages]

def build_few_shot_prompt(passages):
    header = """You are an AI assistant that mimics the writing style of the user. Below are several excerpts from the user's own writing. Study them carefully. When the user asks you to write something, you must produce text that is stylistically indistinguishable from these examples. Pay attention to sentence length, word choice, punctuation, tone, and overall rhythm.

Here are the examples:

"""
    examples_text = "\n\n".join(f"[Example {i+1}]\n{p}" for i, p in enumerate(passages))
    footer = """

Now, write a response on the given topic using this exact style. Do not include explanations about style; just produce the content.
"""
    return header + examples_text + footer

def main():
    passages = select_passages(FEW_SHOT_EXAMPLE_COUNT)
    if not passages:
        print("No suitable passages found. Ensure clean data exists.")
        sys.exit(1)

    prompt = build_few_shot_prompt(passages)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "few_shot_prompt.md"
    output_file.write_text(prompt, encoding="utf-8")
    print(f"Few-shot prompt saved to {output_file}")

if __name__ == "__main__":
    main()