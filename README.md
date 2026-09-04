# Personalized Humanizer

An end-to-end writing style extraction and personalization platform. It analyzes authentic human writing samples, extracts detailed stylometric features (sentence length variance, burstiness index, vocabulary richness, punctuation cadence), synthesizes custom Anti-AI detector bypass rules, and packages the result into a calibrated prompt guide (`SKILL.md`).

---

## 🚀 One-Time Local Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/vrybadplayer/Personalized-Humanizer.git
cd Personalized-Humanizer
```

### 2. Run Setup Orchestrator (Python 3.11 Required)
The system requires **Python 3.11**. The automated setup orchestrator creates the dedicated virtual environment (`.venv311`), upgrades `pip`, installs all Python dependencies, and downloads required NLP models (`spaCy en_core_web_md` & `NLTK` datasets):

```bash
# On Windows (using the Python launcher for 3.11)
py -3.11 backend/setup_orchestrator.py

# On Linux / macOS
python3.11 backend/setup_orchestrator.py
```

### 3. Install Node.js Dependencies
Install all required Node.js packages for the web dashboard and Express API bridge:

```bash
npm install
```

### 4. Launch the Application
Start the dev server (Express bridge + React single page application):

```bash
npm run dev
```

Open your browser and navigate to **`http://localhost:3000`**.

---

## 🏗️ System Architecture

```
Personalized-Humanizer/
├── backend/                  # Python Stylometry Engine & Pipeline Scripts
│   ├── config/               # Settings (settings.py), templates & chunked Anti-AI rules
│   ├── scripts/              # Pipeline scripts (ingest, extract, generate, merge)
│   ├── setup_orchestrator.py # Automated Python 3.11 venv & NLP model downloader
│   ├── anti_ai_skill_raw.md  # Core Anti-AI rule repository
│   └── requirements.txt      # Python dependencies (spaCy, NLTK, docx, pdfplumber, etc.)
├── server/                   # Express API Bridge & Controller Models
│   ├── models/               # PipelineModel, SettingsModel, RawFilesModel
│   └── routes/               # Express API endpoints
├── src/                      # React Single Page Application (UI Dashboard)
│   ├── components/           # PipelineRunner, RawFilesList, SettingsModal, etc.
│   └── types.ts              # Global TypeScript interfaces
├── data/                     # Workspace Data Storage
│   ├── raw/                  # Uploaded user corpus documents (.txt, .docx, .pdf)
│   ├── clean/                # Converted plain-text documents
│   ├── profiles/             # Extracted JSON style profile (style_profile.json)
│   └── output/               # Calibrated outputs (SKILL.md, Complete.md)
├── server.ts                 # Main Express Backend Entrypoint
├── vite.config.ts            # Vite Build & Server Configuration
└── README.md
```

---

## ⚡ Execution Pipeline & Backend Scripts

When you execute the pipeline from the web interface or CLI, the backend runs a sequential multi-stage processing pipeline:

```
[Upload Documents] ➔ [Ingest & Clean] ➔ [Extract Features] ➔ [Anti-AI Rules Synthesis] ➔ [Build & Merge] ➔ [SKILL.md]
```

### Pipeline Script Flow:

1. **`backend/scripts/ingest.py`**
   - Scans `data/raw/` for uploaded corpus files (`.txt`, `.docx`, `.pdf`).
   - Converts rich formats to clean UTF-8 text and outputs files to `data/clean/`.

2. **`backend/scripts/extract_features.py`**
   - Parses the cleaned text using `spaCy` and `NLTK`.
   - Computes statistical metrics: mean sentence length, sentence length variance/standard deviation, paragraph length variance, type-token ratio (vocabulary richness), and burstiness index.
   - Saves the extracted profile to `data/profiles/style_profile.json`.

3. **`backend/scripts/generate_profile_specific_anti_ai.py`**
   - Matches the extracted stylometric features against `backend/anti_ai_skill_raw.md`.
   - Produces tailored Anti-AI critical rules suited to the author's writing style in `data/output/anti_ai_critical_profile.md`.

4. **`backend/scripts/build_guide_from_template.py` & `generate_few_shot_prompt.py`**
   - Generates few-shot prompt examples from authentic text snippets.
   - Constructs a structured style guide template in `data/output/Personalized-Humanizer-Template.md`.

5. **`backend/scripts/summarize.py` & `generate_guide.py`**
   - Packages representative samples and queries the local Ollama LLM model (`llama3.2:3b` or `deepseek-r1:8b`) to synthesize human writing guidelines.
   - Output saved to `data/output/Personalized-Humanizer.md`.

6. **`backend/scripts/merge_guides.py`**
   - Merges the Anti-AI critical rules, template guidelines, and LLM-generated narrative into the final output files: `data/output/SKILL.md` and `data/output/Personalized-Humanizer-Complete.md`.

---

## ⚙️ Configuration & Settings Management

All hyperparameter settings (Ollama model selection, generation temperature, sentence word count deviation targets, paragraph word count deviation targets, and burstiness strength) are stored in `backend/config/settings.py`.

* **Web UI Synchronization**: You can adjust hyperparameters directly in the web app settings modal.
* **Non-Destructive In-Place Updates**: The backend `SettingsModel` uses regex line replacement to update settings variables in `settings.py` without wiping out structural paths (`ROOT_DIR`, `VENV_DIR`, script locations, etc.).
