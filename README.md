# Personalized Humanizer

An end-to-end writing style extraction and personalization platform. It analyzes writing samples, extracts stylometric features (sentence length deviation, burstiness index, vocabulary richness, punctuation cadence), synthesizes custom Anti-AI detector bypass rules, and generates tailor-made prompt guides (`SKILL.md`).

---

## Clean System Architecture

```
Personalized-Humanizer/
├── backend/                  # Self-contained Python Engine & Config
│   ├── config/               # System settings (settings.py), templates & Anti-AI rules
│   ├── scripts/              # Pipeline scripts (ingest, extract_features, generate_guide, etc.)
│   ├── anti_ai_skill_raw.md  # Core Anti-AI rule repository
│   └── requirements.txt      # Python dependencies
├── server/                   # Express API Bridge & Data Models
├── src/                      # React Single Page Application (UI Dashboard)
├── data/                     # Data workspace (raw, clean, profiles, output)
├── server.ts                 # Express Server Entrypoint
└── README.md
```

---

## Environment & API Keys

- **No Gemini API keys required**: The pipeline runs using local LLM inference engines (e.g. Ollama via `deepseek-r1:8b` / `llama3.2:3b`) or local stylometry feature extractors.
- All system settings and hyper-parameters are read from and written directly to **`backend/config/settings.py`**.

---

## One-Time Local Setup

### Prerequisites

1. **Node.js**: v18 or higher
2. **Python**: Python 3.9+ with `pip` and `venv`
3. **Ollama** *(Optional)*: If running local LLM steps (`ollama pull deepseek-r1:8b`)

---

### Step-by-Step Terminal Setup

#### 1. Clone & Navigate into Directory
```bash
git clone https://github.com/vrybadplayer/Personalized-Humanizer.git
cd Personalized-Humanizer
```

#### 2. Create and Activate Python Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
npm install
```

#### 4. Launch Web Application
```bash
npm run dev
```

The Express bridge and React UI will start immediately on **`http://localhost:3000`**.
