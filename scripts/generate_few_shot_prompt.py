import json
import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import spacy
from config.settings import CLEAN_DATA_DIR, OUTPUT_DIR, PROFILE_DIR

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

def select_passages(num_passages=8):
    """Select varied, non-citation, low-domain passages from clean texts."""
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
            domain_score = sum(chunk.lower().count(w.lower()) for w in top_content)
            avg_len = sum(len(s.split()) for s in chunk_sentences) / len(chunk_sentences)
            candidates.append({
                "chunk": chunk,
                "domain_score": domain_score,
                "avg_sentence_len": avg_len,
                "word_count": word_count
            })

    if not candidates:
        return []

    # Sort by domain score
    candidates.sort(key=lambda x: x["domain_score"])

    # Select passages ensuring variety in average sentence length
    bins = {
        "short": [c for c in candidates if c["avg_sentence_len"] < 12],
        "medium": [c for c in candidates if 12 <= c["avg_sentence_len"] <= 20],
        "long": [c for c in candidates if c["avg_sentence_len"] > 20],
    }

    selected = []
    # Cycle through bins until we reach num_passages
    bin_names = ["medium", "short", "long"]
    idx = 0
    while len(selected) < num_passages and any(bins.values()):
        bin_name = bin_names[idx % len(bin_names)]
        if bins[bin_name]:
            chosen = bins[bin_name].pop(0)
            selected.append(chosen["chunk"])
        idx += 1
        # Break if no more candidates
        if all(not bins[b] for b in bins):
            break

    # If still not enough, fill from remaining candidates
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
    passages = select_passages(8)
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