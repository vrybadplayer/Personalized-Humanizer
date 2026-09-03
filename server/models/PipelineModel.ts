import * as fs from 'fs';
import * as path from 'path';
import { spawn } from 'child_process';
import { SettingsModel } from './SettingsModel.js';
import { FileModel } from './FileModel.js';
import { StylometryEngine, StylometryProfile } from '../utils/stylometryEngine.js';

export interface PipelineProgressStage {
  step: number;
  totalSteps: number;
  percent: number;
  stage: string;
  details: string;
  timestamp: number;
}

export interface PipelineState {
  status: 'idle' | 'running' | 'completed' | 'error';
  currentStage: PipelineProgressStage | null;
  logs: string[];
  lastError: string | null;
  startedAt: string | null;
  finishedAt: string | null;
  profile: StylometryProfile | null;
  skillContent: string | null;
}

const DATA_DIR = path.resolve(process.cwd(), 'data');
const RAW_DIR = path.join(DATA_DIR, 'raw');
const CLEAN_DIR = path.join(DATA_DIR, 'clean');
const PROFILES_DIR = path.join(DATA_DIR, 'profiles');
const OUTPUT_DIR = path.join(DATA_DIR, 'output');
const SKILL_FILE = path.join(OUTPUT_DIR, 'SKILL.md');
const PROFILE_FILE = path.join(PROFILES_DIR, 'style_profile.json');

export class PipelineModel {
  private static state: PipelineState = {
    status: 'idle',
    currentStage: null,
    logs: [],
    lastError: null,
    startedAt: null,
    finishedAt: null,
    profile: null,
    skillContent: null,
  };

  public static getState(): PipelineState {
    // If completed file exists on disk and state is idle, load it
    if (this.state.status === 'idle' && fs.existsSync(SKILL_FILE)) {
      try {
        const skillContent = fs.readFileSync(SKILL_FILE, 'utf-8');
        let profile: StylometryProfile | null = null;
        if (fs.existsSync(PROFILE_FILE)) {
          profile = JSON.parse(fs.readFileSync(PROFILE_FILE, 'utf-8'));
        }
        return {
          ...this.state,
          status: 'completed',
          skillContent,
          profile,
        };
      } catch (e) {
        console.warn('Error reading saved skill file:', e);
      }
    }
    return this.state;
  }

  private static appendLog(msg: string) {
    const timestamp = new Date().toLocaleTimeString();
    this.state.logs.push(`[${timestamp}] ${msg}`);
  }

  private static getPythonExecutable(): string {
    const projectRoot = path.resolve(process.cwd());
    const candidates = process.platform === 'win32'
      ? ['.venv/Scripts/python.exe', 'venv/Scripts/python.exe', 'venv311/Scripts/python.exe']
      : ['.venv/bin/python', 'venv/bin/python', 'venv311/bin/python'];

    for (const relPath of candidates) {
      const fullPath = path.join(projectRoot, relPath);
      if (fs.existsSync(fullPath)) {
        return fullPath;
      }
    }
    return process.platform === 'win32' ? 'python' : 'python3';
  }

  private static async extractText(filePath: string): Promise<string> {
    const pythonPath = this.getPythonExecutable();
    const scriptPath = path.join(process.cwd(), 'server', 'utils', 'extract_text.py');

    if (!fs.existsSync(scriptPath)) {
      return fs.readFileSync(filePath, 'utf-8');
    }

    return new Promise((resolve, reject) => {
      const proc = spawn(pythonPath, [scriptPath, filePath]);
      let output = '';
      proc.stdout.on('data', (data) => {
        output += data.toString();
      });
      proc.stderr.on('data', (data) => {
        console.error(`[Text Extractor] stderr: ${data}`);
      });
      proc.on('close', (code) => {
        if (code !== 0) {
          try {
            const fallback = fs.readFileSync(filePath, 'utf-8');
            resolve(fallback);
          } catch (fallbackErr: any) {
            reject(new Error(`Python extractor failed with code ${code} and fallback also failed: ${fallbackErr.message}`));
          }
        } else {
          resolve(output.trim());
        }
      });
    });
  }

  /**
   * Run the complete pipeline by executing the backend pipeline scripts
   */
  public static async execute(): Promise<PipelineState> {
    if (this.state.status === 'running') {
      return this.state;
    }

    // Ensure directories exist
    FileModel.ensureDirectories();

    const settings = SettingsModel.getSettings();

    this.state = {
      status: 'running',
      currentStage: {
        step: 1,
        totalSteps: 5,
        percent: 10,
        stage: 'Environment Verification',
        details: 'Verifying data workspaces & settings configuration',
        timestamp: Date.now(),
      },
      logs: [],
      lastError: null,
      startedAt: new Date().toISOString(),
      finishedAt: null,
      profile: null,
      skillContent: null,
    };

    this.appendLog('Starting Personalized Humanizer pipeline execution...');
    this.appendLog(`Active Model: ${settings.OLLAMA_MODEL}, Temp: ${settings.GENERATION_TEMPERATURE}`);
    this.appendLog(`Configured Sentence Dev: ±${settings.SENTENCE_WORD_COUNT_DEVIATION}, Para Dev: ±${settings.PARAGRAPH_WORD_COUNT_DEVIATION}`);

    try {
      // Step 1: Environment Verification
      await new Promise((r) => setTimeout(r, 400));
      this.state.currentStage = {
        step: 1,
        totalSteps: 5,
        percent: 20,
        stage: 'Environment Verification',
        details: 'Verified data/raw, data/clean, data/profiles, data/output',
        timestamp: Date.now(),
      };
      this.appendLog('Workspace directories verified and ready.');

      // Step 2: Ingestion & Sanitization (backend/scripts/ingest.py)
      await new Promise((r) => setTimeout(r, 400));
      this.state.currentStage = {
        step: 2,
        totalSteps: 5,
        percent: 40,
        stage: 'Ingestion & Sanitization',
        details: 'Scanning raw writing samples and aggregating clean text corpus',
        timestamp: Date.now(),
      };
      this.appendLog('Starting ingestion and text sanitization...');
      await this.runPythonScript('backend/scripts/ingest.py');
      this.appendLog('Ingestion completed. Cleaned corpus written to data/clean/.');

      // Step 3: Feature Extraction (backend/scripts/extract_features.py)
      await new Promise((r) => setTimeout(r, 400));
      this.state.currentStage = {
        step: 3,
        totalSteps: 5,
        percent: 65,
        stage: 'Stylometry Feature Extraction',
        details: 'Computing sentence length variance, burstiness index, and punctuation frequencies',
        timestamp: Date.now(),
      };
      this.appendLog('Starting feature extraction...');
      await this.runPythonScript('backend/scripts/extract_features.py');
      this.appendLog('Feature extraction completed. Style profile written to data/profiles/style_profile.json.');

      // Step 4: Anti-AI Rule Synthesis and Guide Generation
      await new Promise((r) => setTimeout(r, 400));
      this.state.currentStage = {
        step: 4,
        totalSteps: 5,
        percent: 85,
        stage: 'Anti-AI Rule Synthesis & Guide Generation',
        details: 'Formulating detector bypass constraints, burstiness rules & prompt templates',
        timestamp: Date.now(),
      };
      this.appendLog('Starting Anti-AI rule synthesis and guide generation...');
      await this.runPythonScript('backend/scripts/generate_profile_specific_anti_ai.py');
      await this.runPythonScript('backend/scripts/build_guide_from_template.py');
      await this.runPythonScript('backend/scripts/generate_few_shot_prompt.py');
      await this.runPythonScript('backend/scripts/summarize.py');
      this.appendLog('Anti-AI rules and intermediate guides generated.');

      // Step 5: Output Packaging (generate_guide.py, merge_guides.py) and final SKILL.md creation
      await new Promise((r) => setTimeout(r, 400));
      this.state.currentStage = {
        step: 5,
        totalSteps: 5,
        percent: 100,
        stage: 'Output Packaging (SKILL.md)',
        details: 'Exporting final skill definition to data/output/SKILL.md',
        timestamp: Date.now(),
      };
      this.appendLog('Starting final guide assembly and SKILL.md creation...');
      await this.runPythonScript('backend/scripts/generate_guide.py');
      await this.runPythonScript('backend/scripts/merge_guides.py');

      const completePath = path.join(OUTPUT_DIR, 'Personalized-Humanizer-Complete.md');
      if (fs.existsSync(completePath)) {
        fs.copyFileSync(completePath, SKILL_FILE);
        this.appendLog('Copied Personalized-Humanizer-Complete.md to SKILL.md');
      } else {
        const files = fs.readdirSync(OUTPUT_DIR).filter(f => f.endsWith('.md'));
        if (files.length > 0) {
          const fallback = path.join(OUTPUT_DIR, files[0]);
          fs.copyFileSync(fallback, SKILL_FILE);
          this.appendLog(`Copied ${files[0]} to SKILL.md as fallback`);
        } else {
          throw new Error('No markdown output found after pipeline execution.');
        }
      }

      this.appendLog('Output successfully written to data/output/SKILL.md!');

      let skillContent: string | null = null;
      let profile: StylometryProfile | null = null;
      try {
        skillContent = fs.readFileSync(SKILL_FILE, 'utf-8');
        if (fs.existsSync(PROFILE_FILE)) {
          profile = JSON.parse(fs.readFileSync(PROFILE_FILE, 'utf-8'));
        }
      } catch (readErr) {
        console.warn('Could not read generated skill or profile:', readErr);
      }

      this.state.status = 'completed';
      this.state.finishedAt = new Date().toISOString();
      this.state.profile = profile ?? null;
      this.state.skillContent = skillContent ?? null;
      this.appendLog('Pipeline execution completed successfully.');

      return this.state;
    } catch (err: any) {
      console.error('Pipeline execution error:', err);
      this.state.status = 'error';
      this.state.lastError = err?.message || 'Unknown pipeline execution failure';
      this.appendLog(`ERROR: ${this.state.lastError}`);
      return this.state;
    }
  }

  private static async runPythonScript(scriptPath: string): Promise<void> {
    const projectRoot = path.resolve(process.cwd());
    const scriptAbsolute = path.join(projectRoot, scriptPath);
    const pythonPath = this.getPythonExecutable();

    return new Promise<void>((resolve, reject) => {
      const proc = spawn(pythonPath, [scriptAbsolute], { cwd: projectRoot });
      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', (data) => {
        stdout += data.toString();
        console.log(`[${scriptPath}] ${data.toString().trim()}`);
      });

      proc.stderr.on('data', (data) => {
        stderr += data.toString();
        console.error(`[${scriptPath} stderr] ${data.toString().trim()}`);
      });

      proc.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Python script ${scriptPath} exited with code ${code}. Stderr: ${stderr}`));
        } else {
          resolve();
        }
      });

      proc.on('error', (err) => {
        reject(new Error(`Failed to spawn python process for ${scriptPath}: ${err.message}`));
      });
    });
  }

  public static getSkillFileStream(): { exists: boolean; path: string; filename: string } {
    if (fs.existsSync(SKILL_FILE)) {
      return {
        exists: true,
        path: SKILL_FILE,
        filename: 'SKILL.md',
      };
    }
    return {
      exists: false,
      path: '',
      filename: 'SKILL.md',
    };
  }
}