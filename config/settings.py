from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
CLEAN_DATA_DIR = BASE_DIR / "data" / "clean"
PROFILE_DIR = BASE_DIR / "data" / "profiles"
OUTPUT_DIR = BASE_DIR / "data" / "output"

# spaCy model to use (install with: python -m spacy download en_core_web_md)
SPACY_MODEL = "en_core_web_md"

# LLM settings (Ollama)
OLLAMA_MODEL = "deepseek-r1:14b"
OLLAMA_API_URL = "http://localhost:11434"