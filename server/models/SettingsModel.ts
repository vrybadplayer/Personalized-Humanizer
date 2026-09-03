import * as fs from 'fs';
import * as path from 'path';

export interface AppSettings {
  GENERATION_TEMPERATURE: number;
  FEW_SHOT_EXAMPLE_COUNT: number;
  SUMMARIZE_EXAMPLE_COUNT: number;
  SENTENCE_WORD_COUNT_DEVIATION: number;
  PARAGRAPH_WORD_COUNT_DEVIATION: number;
  OLLAMA_MODEL: string;
  BURSTINESS_TARGET_INDEX?: number;
  VOCABULARY_DIVERSITY_FLOOR?: number;
}

const SETTINGS_FILE_PATH = path.resolve(process.cwd(), 'backend/config/settings.py');

export class SettingsModel {
  private static defaultSettings: AppSettings = {
    GENERATION_TEMPERATURE: 0.72,
    FEW_SHOT_EXAMPLE_COUNT: 3,
    SUMMARIZE_EXAMPLE_COUNT: 5,
    SENTENCE_WORD_COUNT_DEVIATION: 4.5,
    PARAGRAPH_WORD_COUNT_DEVIATION: 15.0,
    OLLAMA_MODEL: 'llama3:latest',
    BURSTINESS_TARGET_INDEX: 0.68,
    VOCABULARY_DIVERSITY_FLOOR: 0.42
  };

  /**
   * Reads settings directly from settings.py using regex parsing
   */
  public static getSettings(): AppSettings {
    try {
      if (!fs.existsSync(SETTINGS_FILE_PATH)) {
        this.saveSettings(this.defaultSettings);
        return { ...this.defaultSettings };
      }

      const content = fs.readFileSync(SETTINGS_FILE_PATH, 'utf-8');
      
      const tempMatch = content.match(/GENERATION_TEMPERATURE\s*=\s*([0-9.]+)/);
      const fewShotMatch = content.match(/FEW_SHOT_EXAMPLE_COUNT\s*=\s*([0-9]+)/);
      const summarizeMatch = content.match(/SUMMARIZE_EXAMPLE_COUNT\s*=\s*([0-9]+)/);
      const sentDevMatch = content.match(/SENTENCE_WORD_COUNT_DEVIATION\s*=\s*([0-9.]+)/);
      const paraDevMatch = content.match(/PARAGRAPH_WORD_COUNT_DEVIATION\s*=\s*([0-9.]+)/);
      const modelMatch = content.match(/OLLAMA_MODEL\s*=\s*["']([^"']+)["']/);
      const burstMatch = content.match(/BURSTINESS_TARGET_INDEX\s*=\s*([0-9.]+)/);
      const vocabMatch = content.match(/VOCABULARY_DIVERSITY_FLOOR\s*=\s*([0-9.]+)/);

      return {
        GENERATION_TEMPERATURE: tempMatch ? parseFloat(tempMatch[1]) : this.defaultSettings.GENERATION_TEMPERATURE,
        FEW_SHOT_EXAMPLE_COUNT: fewShotMatch ? parseInt(fewShotMatch[1], 10) : this.defaultSettings.FEW_SHOT_EXAMPLE_COUNT,
        SUMMARIZE_EXAMPLE_COUNT: summarizeMatch ? parseInt(summarizeMatch[1], 10) : this.defaultSettings.SUMMARIZE_EXAMPLE_COUNT,
        SENTENCE_WORD_COUNT_DEVIATION: sentDevMatch ? parseFloat(sentDevMatch[1]) : this.defaultSettings.SENTENCE_WORD_COUNT_DEVIATION,
        PARAGRAPH_WORD_COUNT_DEVIATION: paraDevMatch ? parseFloat(paraDevMatch[1]) : this.defaultSettings.PARAGRAPH_WORD_COUNT_DEVIATION,
        OLLAMA_MODEL: modelMatch ? modelMatch[1] : this.defaultSettings.OLLAMA_MODEL,
        BURSTINESS_TARGET_INDEX: burstMatch ? parseFloat(burstMatch[1]) : this.defaultSettings.BURSTINESS_TARGET_INDEX,
        VOCABULARY_DIVERSITY_FLOOR: vocabMatch ? parseFloat(vocabMatch[1]) : this.defaultSettings.VOCABULARY_DIVERSITY_FLOOR,
      };
    } catch (err) {
      console.error('Error reading settings.py:', err);
      return { ...this.defaultSettings };
    }
  }

  /**
   * Writes updated parameters directly into settings.py
   */
  public static saveSettings(settings: Partial<AppSettings>): AppSettings {
    const current = this.getSettings();
    const updated: AppSettings = {
      GENERATION_TEMPERATURE: settings.GENERATION_TEMPERATURE !== undefined ? Number(settings.GENERATION_TEMPERATURE) : current.GENERATION_TEMPERATURE,
      FEW_SHOT_EXAMPLE_COUNT: settings.FEW_SHOT_EXAMPLE_COUNT !== undefined ? Number(settings.FEW_SHOT_EXAMPLE_COUNT) : current.FEW_SHOT_EXAMPLE_COUNT,
      SUMMARIZE_EXAMPLE_COUNT: settings.SUMMARIZE_EXAMPLE_COUNT !== undefined ? Number(settings.SUMMARIZE_EXAMPLE_COUNT) : current.SUMMARIZE_EXAMPLE_COUNT,
      SENTENCE_WORD_COUNT_DEVIATION: settings.SENTENCE_WORD_COUNT_DEVIATION !== undefined ? Number(settings.SENTENCE_WORD_COUNT_DEVIATION) : current.SENTENCE_WORD_COUNT_DEVIATION,
      PARAGRAPH_WORD_COUNT_DEVIATION: settings.PARAGRAPH_WORD_COUNT_DEVIATION !== undefined ? Number(settings.PARAGRAPH_WORD_COUNT_DEVIATION) : current.PARAGRAPH_WORD_COUNT_DEVIATION,
      OLLAMA_MODEL: settings.OLLAMA_MODEL ? String(settings.OLLAMA_MODEL).trim() : current.OLLAMA_MODEL,
      BURSTINESS_TARGET_INDEX: settings.BURSTINESS_TARGET_INDEX !== undefined ? Number(settings.BURSTINESS_TARGET_INDEX) : current.BURSTINESS_TARGET_INDEX,
      VOCABULARY_DIVERSITY_FLOOR: settings.VOCABULARY_DIVERSITY_FLOOR !== undefined ? Number(settings.VOCABULARY_DIVERSITY_FLOOR) : current.VOCABULARY_DIVERSITY_FLOOR,
    };

    const pythonCode = `"""
Personalized Humanizer - Global Configuration & Hyperparameters
Generated and dynamically synchronized via the Personalized Humanizer UI.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_CLEAN_DIR = DATA_DIR / "clean"
DATA_PROFILES_DIR = DATA_DIR / "profiles"
DATA_OUTPUT_DIR = DATA_DIR / "output"

# Output target file (Changed to SKILL.md per specification)
OUTPUT_SKILL_FILE = DATA_OUTPUT_DIR / "SKILL.md"

# -------------------------------------------------------------
# User-Configurable Parameters (Synced with UI Settings)
# -------------------------------------------------------------
GENERATION_TEMPERATURE = ${updated.GENERATION_TEMPERATURE.toFixed(2)}
FEW_SHOT_EXAMPLE_COUNT = ${updated.FEW_SHOT_EXAMPLE_COUNT}
SUMMARIZE_EXAMPLE_COUNT = ${updated.SUMMARIZE_EXAMPLE_COUNT}
SENTENCE_WORD_COUNT_DEVIATION = ${updated.SENTENCE_WORD_COUNT_DEVIATION.toFixed(1)}
PARAGRAPH_WORD_COUNT_DEVIATION = ${updated.PARAGRAPH_WORD_COUNT_DEVIATION.toFixed(1)}
OLLAMA_MODEL = "${updated.OLLAMA_MODEL}"

# -------------------------------------------------------------
# Anti-AI Detection & Stylometry Tuning Parameters
# -------------------------------------------------------------
BURSTINESS_TARGET_INDEX = ${(updated.BURSTINESS_TARGET_INDEX || 0.68).toFixed(2)}
VOCABULARY_DIVERSITY_FLOOR = ${(updated.VOCABULARY_DIVERSITY_FLOOR || 0.42).toFixed(2)}
BAN_ROBOTIC_TRANSITIONS = True
INJECT_AUTHENTIC_IDIOSYNCRASIES = True
MAX_TOKEN_CONTEXT = 8192
`;

    fs.writeFileSync(SETTINGS_FILE_PATH, pythonCode, 'utf-8');
    return updated;
  }
}
