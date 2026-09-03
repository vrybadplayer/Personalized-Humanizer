import sys
import re
from pathlib import Path

# Add project root to sys.path to import settings
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import RAW_DATA_DIR, CLEAN_DATA_DIR
import docx
import pdfplumber

def extract_docx_text(file_path: Path) -> str:
    """Extract text from a .docx file, excluding tables."""
    doc = docx.Document(file_path)
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)
    return "\n\n".join(paragraphs)

def extract_pdf_text(file_path: Path) -> str:
    """Extract text from a PDF file, excluding table content."""
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            tables = page.find_tables()
            if not tables:
                # No tables, extract whole page
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
            else:
                # Exclude table areas by filtering words outside any table bbox
                words = page.extract_words()
                table_bboxes = [table.bbox for table in tables]
                kept_words = []
                for w in words:
                    x0, top, x1, bottom = w['x0'], w['top'], w['x1'], w['bottom']
                    inside = False
                    for tb in table_bboxes:
                        if (x0 >= tb[0] and x1 <= tb[2] and top >= tb[1] and bottom <= tb[3]):
                            inside = True
                            break
                    if not inside:
                        kept_words.append(w)
                # Sort by vertical position, then horizontal
                kept_words.sort(key=lambda w: (round(w['top'], 1), w['x0']))
                # Rebuild lines based on similar top coordinates
                lines = []
                current_line = []
                last_top = None
                for w in kept_words:
                    if last_top is None or abs(w['top'] - last_top) > 3:  # new line
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = [w['text']]
                        last_top = w['top']
                    else:
                        current_line.append(w['text'])
                if current_line:
                    lines.append(' '.join(current_line))
                page_text = '\n'.join(lines)
                text_parts.append(page_text)
    return '\n\n'.join(text_parts)

def clean_text(text: str) -> str:
    """Clean text but preserve paragraph breaks (double newlines)."""
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Collapse 3+ newlines into 2 (paragraph break)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Replace single newlines (line wraps) with spaces
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    # Collapse multiple spaces/tabs
    text = re.sub(r'[ \t]+', ' ', text)
    # Clean up spaces around paragraph breaks
    text = re.sub(r' *\n\n *', '\n\n', text)
    return text.strip()

def process_file(file_path: Path) -> str | None:
    """Process a single file based on extension."""
    ext = file_path.suffix.lower()
    if ext == ".docx":
        raw_text = extract_docx_text(file_path)
    elif ext == ".pdf":
        raw_text = extract_pdf_text(file_path)
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
    if not RAW_DATA_DIR.exists():
        print(f"Raw data directory {RAW_DATA_DIR} does not exist. Creating it...")
        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Process all supported files in RAW_DATA_DIR
    for raw_file in RAW_DATA_DIR.iterdir():
        if raw_file.is_file():
            print(f"Processing {raw_file.name}...")
            cleaned = process_file(raw_file)
            if cleaned:
                output_file = CLEAN_DATA_DIR / (raw_file.stem + ".txt")
                output_file.write_text(cleaned, encoding="utf-8")
                print(f"  Saved to {output_file.name}")

if __name__ == "__main__":
    main()