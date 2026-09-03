# Personalized Humanizer

An end-to-end writing style extraction and personalization platform. It analyzes writing samples, extracts stylometric features (sentence length deviation, burstiness index, vocabulary richness, punctuation cadence), synthesizes custom Anti-AI detector bypass rules, and generates tailor-made prompt guides (`SKILL.md`).

---

## System Architecture

```
Personalized-Humanizer/
├── backend/                  # Self-contained Python Engine & Config
│   ├── config/               # System settings (settings.py), templates & Anti-AI rules
│   ├── scripts/              # Pipeline scripts (ingest, extract_features, generate_guide, etc.)
│   ├── setup_orchestrator.py # Automated setup script for venv & dependencies
│   ├── anti_ai_skill_raw.md  # Core Anti-AI rule repository
│   └── requirements.txt      # Python dependencies
├── server/                   # Express API Bridge & Data Models
├── src/                      # React Single Page Application (UI Dashboard)
├── data/                     # Data workspace (raw, clean, profiles, output)
├── server.ts                 # Express Server Entrypoint
└── README.md
```

---

## One-Time Local Setup

### 1. Clone & Navigate into Directory
```bash
git clone https://github.com/vrybadplayer/Personalized-Humanizer.git
cd Personalized-Humanizer
```

### 2. Run Setup Orchestrator & Install Node Packages
`setup_orchestrator.py` automatically creates the virtual environment (`.venv`), upgrades `pip`, installs `requirements.txt`, and downloads required NLP models (spaCy & NLTK data):

```bash
# Automated Python setup (creates .venv & installs dependencies)
python backend/setup_orchestrator.py

# Install Node.js dependencies
npm install
```

### 3. Launch Web Application
```bash
npm run dev
```

The Express bridge and React UI will start immediately on **`http://localhost:3000`**.
