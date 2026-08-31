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
ANTI_AI_CRITICAL_PROFILE = OUTPUT_DIR / "anti_ai_critical_profile.md"
USAGE_TEMPLATE_FILE = BASE_DIR / "config" / "usage_prompt_template.md"

FINAL_OUTPUT = OUTPUT_DIR / "Personalized-Humanizer-Complete.md"

PRIORITY_PREAMBLE = """# Priority Hierarchy (Important)

This document contains two types of instructions:

1. **Personalized Style Instructions** (Narrative Overview, Style Guide Template, Few‑Shot Examples)  
   These describe the **writer’s actual habits** and **must be followed first**. They define the core voice, sentence rhythm, punctuation, and phrasing patterns.

2. **Anti‑AI Writing Rules** (Profile‑Specific Critical, Full Anti‑AI Rules)  
   These are **secondary** and are provided only to help avoid machine‑detectable patterns. **If any anti‑AI rule conflicts with the writer’s measured style, the writer’s style wins.** Do not sacrifice the user’s authentic voice to satisfy a generic anti‑AI rule.

Unless a rule is a hard constraint (e.g., “do not mention AI,” “do not invent facts”), apply the anti‑AI rules only where they do not contradict the personalized metrics.

---
"""

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
    usage_template = read_file(USAGE_TEMPLATE_FILE)

    if not template:
        print("Template guide missing. Run build_guide_from_template.py first.")
        sys.exit(1)

    parts = []

    # Insert priority preamble at the very top
    parts.append(PRIORITY_PREAMBLE)

    if prose:
        parts.append("# Narrative Overview\n\n" + prose)
    parts.append(template)
    if few_shot:
        parts.append("# Few‑Shot Examples\n\n" + few_shot)

    # Critical anti-AI rules (profile-specific takes precedence)
    if anti_ai_critical_profile:
        parts.append("# Anti‑AI Writing Rules (Profile‑Specific Critical)\n\n" + anti_ai_critical_profile)
    elif anti_ai_critical:
        parts.append("# Anti‑AI Writing Rules (Quick Reference)\n\n" + anti_ai_critical)

    # Full chunks or static fallback
    if anti_ai_chunks:
        parts.append("# Anti‑AI Writing Rules (Full)\n\n" + anti_ai_chunks)
    elif anti_ai_static:
        parts.append("# Anti‑AI Writing Rules (Condensed)\n\n" + anti_ai_static)

    # Usage prompt template
    if usage_template:
        parts.append(usage_template)

    final_content = "\n\n---\n\n".join(parts)
    FINAL_OUTPUT.write_text(final_content, encoding="utf-8")
    print(f"Merged guide saved to {FINAL_OUTPUT}")

if __name__ == "__main__":
    main()