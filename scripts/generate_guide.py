import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import ollama
from config.settings import OUTPUT_DIR, OLLAMA_MODEL, OLLAMA_CONTEXT_SIZE

def main():
    prompt_file = OUTPUT_DIR / "prompt.txt"
    if not prompt_file.exists():
        print(f"Prompt file not found at {prompt_file}. Run summarize.py first.")
        sys.exit(1)

    prompt = prompt_file.read_text(encoding="utf-8")
    print("Sending prompt to Ollama...")

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0.4,
            "num_predict": 1200,
            "top_p": 0.9,
            "num_ctx": OLLAMA_CONTEXT_SIZE,
        },
    )

    style_guide = response["message"]["content"].strip()

    output_file = OUTPUT_DIR / "Personalized-Humanizer.md"
    output_file.write_text(style_guide, encoding="utf-8")
    print(f"Style guide saved to {output_file}")

if __name__ == "__main__":
    main()