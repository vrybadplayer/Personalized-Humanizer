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
    GENERATION_TEMPERATURE: 0.5,
    FEW_SHOT_EXAMPLE_COUNT: 100,
    SUMMARIZE_EXAMPLE_COUNT: 8,
    SENTENCE_WORD_COUNT_DEVIATION: 10.0,
    PARAGRAPH_WORD_COUNT_DEVIATION: 40.0,
    OLLAMA_MODEL: 'deepseek-r1:8b',
    BURSTINESS_TARGET_INDEX: 0.7,
    VOCABULARY_DIVERSITY_FLOOR: 0.42
  };

  /**
   * Reads settings directly from settings.py using regex parsing
   */
  public static getSettings(): AppSettings {
    try {
      if (!fs.existsSync(SETTINGS_FILE_PATH)) {
        return { ...this.defaultSettings };
      }

      const content = fs.readFileSync(SETTINGS_FILE_PATH, 'utf-8');
      
      const tempMatch = content.match(/^GENERATION_TEMPERATURE\s*=\s*([0-9.]+)/m);
      const fewShotMatch = content.match(/^FEW_SHOT_EXAMPLE_COUNT\s*=\s*([0-9]+)/m);
      const summarizeMatch = content.match(/^SUMMARIZE_EXAMPLE_COUNT\s*=\s*([0-9]+)/m);
      const sentDevMatch = content.match(/^SENTENCE_WORD_COUNT_DEVIATION\s*=\s*([0-9.]+)/m);
      const paraDevMatch = content.match(/^PARAGRAPH_WORD_COUNT_DEVIATION\s*=\s*([0-9.]+)/m);
      const modelMatch = content.match(/^OLLAMA_MODEL\s*=\s*["']([^"']+)["']/m);
      const burstMatch = content.match(/^BURSTINESS_TARGET_INDEX\s*=\s*([0-9.]+)/m);
      const vocabMatch = content.match(/^VOCABULARY_DIVERSITY_FLOOR\s*=\s*([0-9.]+)/m);

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
   * Safely updates variable lines inside settings.py WITHOUT overwriting other constants/paths
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

    if (!fs.existsSync(SETTINGS_FILE_PATH)) {
      console.error(`settings.py not found at ${SETTINGS_FILE_PATH}`);
      return updated;
    }

    let fileContent = fs.readFileSync(SETTINGS_FILE_PATH, 'utf-8');

    // Helper function to update or append variable assignment in Python
    const setPyVar = (key: string, value: string | number) => {
      const formattedVal = typeof value === 'string' ? `"${value}"` : value;
      const regex = new RegExp(`^${key}\\s*=.*$`, 'm');
      
      if (regex.test(fileContent)) {
        fileContent = fileContent.replace(regex, `${key} = ${formattedVal}`);
      } else {
        fileContent += `\n${key} = ${formattedVal}`;
      }
    };

    // Replace ONLY the user-configurable hyperparameters
    setPyVar('GENERATION_TEMPERATURE', updated.GENERATION_TEMPERATURE);
    setPyVar('FEW_SHOT_EXAMPLE_COUNT', updated.FEW_SHOT_EXAMPLE_COUNT);
    setPyVar('SUMMARIZE_EXAMPLE_COUNT', updated.SUMMARIZE_EXAMPLE_COUNT);
    setPyVar('SENTENCE_WORD_COUNT_DEVIATION', updated.SENTENCE_WORD_COUNT_DEVIATION);
    setPyVar('PARAGRAPH_WORD_COUNT_DEVIATION', updated.PARAGRAPH_WORD_COUNT_DEVIATION);
    setPyVar('OLLAMA_MODEL', updated.OLLAMA_MODEL);

    if (updated.BURSTINESS_TARGET_INDEX !== undefined) {
      setPyVar('BURSTINESS_TARGET_INDEX', updated.BURSTINESS_TARGET_INDEX);
    }
    if (updated.VOCABULARY_DIVERSITY_FLOOR !== undefined) {
      setPyVar('VOCABULARY_DIVERSITY_FLOOR', updated.VOCABULARY_DIVERSITY_FLOOR);
    }

    // Overwrite file safely while keeping ROOT_DIR, RAW_DATA_DIR, VENV_DIR, etc. intact
    fs.writeFileSync(SETTINGS_FILE_PATH, fileContent, 'utf-8');
    return updated;
  }
}