import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
CLEAN_DATA_DIR = BASE_DIR / "data" / "clean"
PROFILE_DIR = BASE_DIR / "data" / "profiles"
OUTPUT_DIR = BASE_DIR / "data" / "output"

# Virtual environment and requirements
VENV_DIR = BASE_DIR / ".venv311"
REQUIREMENTS_FILE = BASE_DIR / "requirements.txt"
RAW_ANTI_AI_FILE = BASE_DIR / "anti_ai_skill_raw.md"

# Python versions to look for in setup orchestrator
SUPPORTED_PYTHON_MINORS = [11, 12]

# spaCy model to use (install with: python -m spacy download en_core_web_md)
SPACY_MODEL = "en_core_web_md"
SPACY_MODEL_DOWNLOAD = "en_core_web_md-3.7.1"   # versioned download command
SPACY_MODEL_PIP = "en-core-web-md"              # fallback pip package

# NLTK data directory inside the virtual environment
NLTK_DATA_DIR = Path(sys.prefix) / "nltk_data"

# NLTK data packages to download
NLTK_DOWNLOADS = ["punkt", "averaged_perceptron_tagger"]

# Paths to key scripts
CHUNK_ANTI_AI_SCRIPT = BASE_DIR / "scripts" / "chunk_anti_ai_skill.py"
PIPELINE_SCRIPT = BASE_DIR / "scripts" / "run_pipeline.py"

# LLM settings (Ollama)
OLLAMA_MODEL = "deepseek-r1:8b"          # for narrative generation
VALIDATION_MODEL = "llama3.2:3b"         # for validation (non-reasoning)
OLLAMA_API_URL = "http://localhost:11434"
OLLAMA_CONTEXT_SIZE = 8192      # 12288    18000

# Generation parameters for narrative style guide (used in generate_guide.py)
GENERATION_TEMPERATURE = 0.5     # Can be tweaked to be more creative
GENERATION_NUM_PREDICT = 1200
GENERATION_TOP_P = 0.5

# Few-shot prompt settings for Final result
FEW_SHOT_EXAMPLE_COUNT = 100

# Number of examples used in summarize.py to feed LLM prompt
SUMMARIZE_EXAMPLE_COUNT = 8

# Burstiness parameters (used in usage prompt template)
SENTENCE_WORD_COUNT_DEVIATION = 10   # allowed +/- words around the average sentence length
PARAGRAPH_WORD_COUNT_DEVIATION = 40  # allowed +/- words around the average paragraph length
BURSTINESS_STRENGTH = 0.7            # optional: not directly used in template, but could be referenced

# Validation settings
VALIDATION_TOPIC = "the importance of time management in daily life"
VALIDATION_NUM_PREDICT = 800             # enough for a non-reasoning model to produce 200 words

# Anti-AI chunking defaults
CHUNK_INPUT_FILE = "anti_ai_skill_raw.md"
CHUNK_OUTPUT_DIR = "config/anti_ai_chunks"