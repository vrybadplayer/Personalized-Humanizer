import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import OUTPUT_DIR, BASE_DIR

PROSE_GUIDE = OUTPUT_DIR / "Personalized-Humanizer.md"
TEMPLATE_GUIDE = OUTPUT_DIR / "Personalized-Humanizer-Template.md"
FEW_SHOT_PROMPT = OUTPUT_DIR / "few_shot_prompt.md"
ANTI_AI_CHUNKS_DIR = BASE_DIR / "config" / "anti_ai_chunks"
ANTI_AI_STATIC = BASE_DIR / "config" / "anti_ai_static.md"
ANTI_AI_CRITICAL = BASE_DIR / "config" / "anti_ai_critical.md"
ANTI_AI_CRITICAL_PROFILE = OUTPUT_DIR / "anti_ai_critical_profile.md"   # profile-specific

FINAL_OUTPUT = OUTPUT_DIR / "Personalized-Humanizer-Complete.md"

def read_file(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""

def read_all_chunks():
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
    few_shot = read_file(FEW_SHOT_PROMPT)
    anti_ai_chunks = read_all_chunks()
    anti_ai_static = read_file(ANTI_AI_STATIC)
    anti_ai_critical = read_file(ANTI_AI_CRITICAL)
    anti_ai_critical_profile = read_file(ANTI_AI_CRITICAL_PROFILE)

    if not template:
        print("Template guide missing. Run build_guide_from_template.py first.")
        sys.exit(1)

    parts = []
    if prose:
        parts.append("# Narrative Overview\n\n" + prose)
    parts.append(template)
    if few_shot:
        parts.append("# Few‑Shot Examples\n\n" + few_shot)

    # Determine if the template already contains a critical anti-AI rules section
    template_has_critical = "Critical Anti‑AI Writing Rules" in template

    # Choose the best critical section to insert
    critical_section = None
    critical_title = None
    if anti_ai_critical_profile:
        critical_section = anti_ai_critical_profile
        critical_title = "# Anti‑AI Writing Rules (Profile‑Specific Critical)\n\n"
    elif anti_ai_critical and not template_has_critical:
        critical_section = anti_ai_critical
        critical_title = "# Anti‑AI Writing Rules (Quick Reference)\n\n"

    # Only add a critical section if not already in template, or if profile-specific supersedes
    if critical_section and not (template_has_critical and not anti_ai_critical_profile):
        # If template already has critical and we have profile-specific, we should replace template's? 
        # Safer: if template has critical and no profile-specific, skip; if profile-specific exists, add it anyway (could duplicate if template also has critical).
        # To avoid duplication, we assume template critical will be removed as recommended.
        if not template_has_critical or anti_ai_critical_profile:
            parts.append(critical_title + critical_section)

    # Full chunks or static fallback
    if anti_ai_chunks:
        parts.append("# Anti‑AI Writing Rules (Full)\n\n" + anti_ai_chunks)
    elif anti_ai_static:
        parts.append("# Anti‑AI Writing Rules (Condensed)\n\n" + anti_ai_static)

    final_content = "\n\n---\n\n".join(parts)
    FINAL_OUTPUT.write_text(final_content, encoding="utf-8")
    print(f"Merged guide saved to {FINAL_OUTPUT}")

if __name__ == "__main__":
    main()