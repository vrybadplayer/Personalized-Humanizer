import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import OUTPUT_DIR, BASE_DIR

PROSE_GUIDE = OUTPUT_DIR / "Personalized-Humanizer.md"           # from LLM
TEMPLATE_GUIDE = OUTPUT_DIR / "Personalized-Humanizer-Template.md"
ANTI_AI_STATIC = BASE_DIR / "config" / "anti_ai_static.md"
FINAL_OUTPUT = OUTPUT_DIR / "Personalized-Humanizer-Complete.md"

def read_file(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""

def main():
    prose = read_file(PROSE_GUIDE)
    template = read_file(TEMPLATE_GUIDE)
    anti_ai = read_file(ANTI_AI_STATIC)

    if not template:
        print("Template guide missing. Run build_guide_from_template.py first.")
        sys.exit(1)

    # Structure:
    # 1. Narrative Overview (prose guide) if available
    # 2. Template guide (metrics)
    # 3. Anti-AI rules
    parts = []
    if prose:
        parts.append("# Narrative Overview\n\n" + prose)
    parts.append(template)
    if anti_ai:
        parts.append("# Anti-AI Writing Rules\n\n" + anti_ai)

    final_content = "\n\n---\n\n".join(parts)

    FINAL_OUTPUT.write_text(final_content, encoding="utf-8")
    print(f"Merged guide saved to {FINAL_OUTPUT}")

if __name__ == "__main__":
    main()