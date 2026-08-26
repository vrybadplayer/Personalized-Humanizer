import sys
from pathlib import Path

# Add project root to sys.path to import settings
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import RAW_DATA_DIR, CLEAN_DATA_DIR
import docx
import re

def extract_docx_text(file_path: Path) -> str:
    """Extract text from a .docx file, excluding tables."""
    doc = docx.Document(file_path)
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)
    return "\n\n".join(paragraphs)

def clean_text(text: str) -> str:
    """Basic cleaning: remove extra whitespace, normalize newlines."""
    # Remove page numbers, headers/footers (customize as needed)
    # For now, just collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def process_file(file_path: Path) -> str | None:
    """Process a single file based on extension."""
    ext = file_path.suffix.lower()
    if ext == ".docx":
        raw_text = extract_docx_text(file_path)
    elif ext == ".txt":
        raw_text = file_path.read_text(encoding="utf-8")
    else:
        print(f"Skipping unsupported file: {file_path.name}")
        return None

    # Clean and return
    return clean_text(raw_text)

def main():
    # Ensure directories exist
    CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Process all supported files in RAW_DATA_DIR
    for raw_file in RAW_DATA_DIR.iterdir():
        if raw_file.is_file():
            print(f"Processing {raw_file.name}...")
            clean_text = process_file(raw_file)
            if clean_text:
                output_file = CLEAN_DATA_DIR / (raw_file.stem + ".txt")
                output_file.write_text(clean_text, encoding="utf-8")
                print(f"  Saved to {output_file.name}")

if __name__ == "__main__":
    main()