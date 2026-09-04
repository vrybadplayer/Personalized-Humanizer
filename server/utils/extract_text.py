#!/usr/bin/env python3
"""
Personalized Humanizer - Text Extractor
Extracts text from various file formats (PDF, DOCX, TXT, MD, RTF) for processing.
"""

import sys
import os
from pathlib import Path

def extract_text(file_path: str) -> str:
    """Extract text from a file based on its extension."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    ext = path.suffix.lower()
    
    try:
        if ext == '.pdf':
            return extract_text_pdf(file_path)
        elif ext == '.docx':
            return extract_text_docx(file_path)
        elif ext == '.doc':
            # For old .doc format, we try antiword if available, else fallback to reading as binary?
            # For simplicity, we'll try to read as text and hope it's not too corrupted.
            return extract_text_as_text(file_path)
        elif ext == '.rtf':
            return extract_text_rtf(file_path)
        elif ext in ['.txt', '.md', '.markdown', '.json']:
            return extract_text_as_text(file_path)
        else:
            # Unsupported format, return empty string
            return ''
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}", file=sys.stderr)
        return ''

def extract_text_as_text(file_path: str) -> str:
    """Read file as plain text (UTF-8)."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def extract_text_pdf(file_path: str) -> str:
    """Extract text from PDF using PyPDF2."""
    try:
        import PyPDF2
        text = []
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text() or '')
        return '\n'.join(text)
    except ImportError:
        raise ImportError("PyPDF2 is not installed. Install it with 'pip install PyPDF2'")
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")

def extract_text_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        import docx
        doc = docx.Document(file_path)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return '\n'.join(text)
    except ImportError:
        raise ImportError("python-docx is not installed. Install it with 'pip install python-docx'")
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from DOCX: {e}")

def extract_text_rtf(file_path: str) -> str:
    """Extract text from RTF by stripping RTF codes (simple approach)."""
    try:
        # Try to read as text and remove RTF syntax
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        # Very basic RTF stripping: remove everything between {\\* and } and remove {\\fonttbl, etc.
        # This is a naive implementation; for better results, use striprtf library.
        import re
        # Remove RTF font table, color table, etc.
        content = re.sub(r'{\\*\\\\fonttbl.*?}', '', content, flags=re.DOTALL)
        content = re.sub(r'{\\*\\\\colortbl.*?}', '', content, flags=re.DOTALL)
        content = re.sub(r'{\\*\\\\list.*?}', '', content, flags=re.DOTALL)
        content = re.sub(r'{\\*\\\\listoverridetable.*?}', '', content, flags=re.DOTALL)
        content = re.sub(r'{\\.*?}', '', content)  # Remove any remaining RTF groups
        # Replace RTF line breaks
        content = content.replace('\\par', '\n')
        # Remove any remaining backslashes (except those that are part of normal text?)
        # We'll just remove standalone backslashes followed by space or newline?
        # For simplicity, we'll leave as is and let the cleaning step handle.
        return content
    except Exception as e:
        print(f"Warning: RTF extraction failed, falling back to raw text: {e}", file=sys.stderr)
        return extract_text_as_text(file_path)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python extract_text.py <file_path>", file=sys.stderr)
        sys.exit(1)
    file_path = sys.argv[1]
    text = extract_text(file_path)
    if text is None:
        text = ''
    print(text)