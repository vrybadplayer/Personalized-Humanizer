import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import OUTPUT_DIR, BASE_DIR

PROSE_GUIDE = OUTPUT_DIR / "Personalized-Humanizer.md"           # from LLM (optional)
TEMPLATE_GUIDE = OUTPUT_DIR / "Personalized-Humanizer-Template.md"
ANTI_AI_CHUNKS_DIR = BASE_DIR / "config" / "anti_ai_chunks"
ANTI_AI_STATIC = BASE_DIR / "config" / "anti_ai_static.md"
FINAL_OUTPUT = OUTPUT_DIR / "Personalized-Humanizer-Complete.md"

def read_file(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""

def read_all_chunks():
    """Read and return all anti-AI chunk files in order."""
    if not ANTI_AI_CHUNKS_DIR.exists():
        return ""
    chunk_files = sorted(ANTI_AI_CHUNKS_DIR.glob("C*.md"))
    parts = []
    for cf in chunk_files:
        content = read_file(cf)
        if content:
            parts.append(f"<!-- Start of {cf.name} -->\n{content}")
    return "\n\n".join(parts)

def main():
    prose = read_file(PROSE_GUIDE)
    template = read_file(TEMPLATE_GUIDE)
    anti_ai_chunks = read_all_chunks()
    anti_ai_static = read_file(ANTI_AI_STATIC)

    if not template:
        print("Template guide missing. Run build_guide_from_template.py first.")
        sys.exit(1)

    # Build final content
    parts = []
    if prose:
        parts.append("# Narrative Overview\n\n" + prose)
    parts.append(template)

    if anti_ai_chunks:
        parts.append("# Anti-AI Writing Rules (Full)\n\n" + anti_ai_chunks)
    elif anti_ai_static:
        parts.append("# Anti-AI Writing Rules (Condensed)\n\n" + anti_ai_static)

    final_content = "\n\n---\n\n".join(parts)

    FINAL_OUTPUT.write_text(final_content, encoding="utf-8")
    print(f"Merged guide saved to {FINAL_OUTPUT}")

if __name__ == "__main__":
    main()