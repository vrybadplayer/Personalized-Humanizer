import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import OUTPUT_DIR, BASE_DIR

def main():
    guide_file = OUTPUT_DIR / "Personalized-Humanizer.md"
    if not guide_file.exists():
        print(f"Style guide not found at {guide_file}. Run generate_guide.py first.")
        sys.exit(1)

    anti_ai_file = BASE_DIR / "config" / "anti_ai_static.md"
    if not anti_ai_file.exists():
        print(f"Anti-AI static file not found at {anti_ai_file}.")
        sys.exit(1)

    guide_content = guide_file.read_text(encoding="utf-8").strip()
    anti_ai_content = anti_ai_file.read_text(encoding="utf-8").strip()

    combined = guide_content + "\n\n---\n\n" + anti_ai_content + "\n"

    combined_file = OUTPUT_DIR / "Personalized-Humanizer-Complete.md"
    combined_file.write_text(combined, encoding="utf-8")
    print(f"Combined guide saved to {combined_file}")

if __name__ == "__main__":
    main()