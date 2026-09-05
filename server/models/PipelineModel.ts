import * as fs from 'fs';
import * as path from 'path';
import { spawn } from 'child_process';
import { SettingsModel } from './SettingsModel.js';
import { FileModel } from './FileModel.js';
import { StylometryEngine, StylometryProfile } from '../utils/stylometryEngine.js';
import { ParsedPipelineError, PipelineProgressStage, PipelineState } from '../../src/types/index.js';
import { ErrorClassifier } from '../utils/ErrorClassifier.js';
import { Logger } from '../utils/logger.js';

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
    parsedError: null,
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
      parsedError: null,
      startedAt: new Date().toISOString(),
      finishedAt: null,
      profile: null,
      skillContent: null,
    };

    Logger.logPipelineStart(settings.OLLAMA_MODEL, 'Environment Verification');
    this.appendLog('Starting Personalized Humanizer pipeline execution...');
    this.appendLog(`Active Model: ${settings.OLLAMA_MODEL}, Temp: ${settings.GENERATION_TEMPERATURE}`);

    try {
      // Step 1: Environment Verification
      await new Promise((r) => setTimeout(r, 200));
      this.state.currentStage = {
        step: 1,
        totalSteps: 5,
        percent: 20,
        stage: 'Environment Verification',
        details: 'Verified data/raw, data/clean, data/profiles, data/output',
        timestamp: Date.now(),
      };
      Logger.logPipelineStage(1, 5, 'Environment Verification', 'Workspace directories verified.');
      this.appendLog('Workspace directories verified and ready.');

      // Step 2: Ingestion & Sanitization (backend/scripts/ingest.py)
      await new Promise((r) => setTimeout(r, 200));
      const stage2Name = 'Ingestion & Sanitization';
      this.state.currentStage = {
        step: 2,
        totalSteps: 5,
        percent: 40,
        stage: stage2Name,
        details: 'Scanning raw writing samples and aggregating clean text corpus',
        timestamp: Date.now(),
      };
      Logger.logPipelineStage(2, 5, stage2Name, 'Aggregating corpus text.');
      this.appendLog('Starting ingestion and text sanitization...');
      await this.runPythonScript('backend/scripts/ingest.py', stage2Name, settings.OLLAMA_MODEL);
      this.appendLog('Ingestion completed. Cleaned corpus written to data/clean/.');

      // Step 3: Feature Extraction (backend/scripts/extract_features.py)
      await new Promise((r) => setTimeout(r, 200));
      const stage3Name = 'Stylometry Feature Extraction';
      this.state.currentStage = {
        step: 3,
        totalSteps: 5,
        percent: 65,
        stage: stage3Name,
        details: 'Computing sentence length variance, burstiness index, and punctuation frequencies',
        timestamp: Date.now(),
      };
      Logger.logPipelineStage(3, 5, stage3Name, 'Computing sentence length variance & burstiness.');
      this.appendLog('Starting feature extraction...');
      await this.runPythonScript('backend/scripts/extract_features.py', stage3Name, settings.OLLAMA_MODEL);
      this.appendLog('Feature extraction completed. Style profile written to data/profiles/style_profile.json.');

      // Step 4: Anti-AI Rule Synthesis and Guide Generation
      await new Promise((r) => setTimeout(r, 200));
      const stage4Name = 'Anti-AI Rule Synthesis & Guide Generation';
      this.state.currentStage = {
        step: 4,
        totalSteps: 5,
        percent: 85,
        stage: stage4Name,
        details: 'Formulating detector bypass constraints, burstiness rules & prompt templates',
        timestamp: Date.now(),
      };
      Logger.logPipelineStage(4, 5, stage4Name, 'Formulating rules and prompt templates.');
      this.appendLog('Starting Anti-AI rule synthesis and guide generation...');
      await this.runPythonScript('backend/scripts/generate_profile_specific_anti_ai.py', stage4Name, settings.OLLAMA_MODEL);
      await this.runPythonScript('backend/scripts/build_guide_from_template.py', stage4Name, settings.OLLAMA_MODEL);
      await this.runPythonScript('backend/scripts/generate_few_shot_prompt.py', stage4Name, settings.OLLAMA_MODEL);
      await this.runPythonScript('backend/scripts/summarize.py', stage4Name, settings.OLLAMA_MODEL);
      this.appendLog('Anti-AI rules and intermediate guides generated.');

      // Step 5: Output Packaging (generate_guide.py, merge_guides.py) and final SKILL.md creation
      await new Promise((r) => setTimeout(r, 200));
      const stage5Name = 'Output Packaging (SKILL.md)';
      this.state.currentStage = {
        step: 5,
        totalSteps: 5,
        percent: 100,
        stage: stage5Name,
        details: 'Exporting final skill definition to data/output/SKILL.md',
        timestamp: Date.now(),
      };
      Logger.logPipelineStage(5, 5, stage5Name, 'Exporting skill definition.');
      this.appendLog('Starting final guide assembly and SKILL.md creation...');
      await this.runPythonScript('backend/scripts/generate_guide.py', stage5Name, settings.OLLAMA_MODEL);
      await this.runPythonScript('backend/scripts/merge_guides.py', stage5Name, settings.OLLAMA_MODEL);

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
      this.state.status = 'error';
      if (!this.state.parsedError) {
        const parsed = ErrorClassifier.classify(
          err?.message || 'Unknown pipeline execution failure',
          'PipelineModel',
          this.state.currentStage?.stage || 'Pipeline Execution',
          settings.OLLAMA_MODEL
        );
        this.state.parsedError = parsed;
        this.state.lastError = parsed.userMessage;
        Logger.logPipelineError(parsed);
      } else {
        this.state.lastError = this.state.parsedError.userMessage;
      }

      this.appendLog(`ERROR [${this.state.parsedError.code}]: ${this.state.parsedError.userMessage}`);
      return this.state;
    }
  }

  private static async runPythonScript(
    scriptPath: string,
    stageName?: string,
    configuredModel?: string
  ): Promise<void> {
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
          const parsed = ErrorClassifier.classify(stderr || stdout || `Process exited with code ${code}`, scriptPath, stageName, configuredModel);
          this.state.parsedError = parsed;
          this.state.lastError = parsed.userMessage;
          Logger.logPipelineError(parsed);
          reject(new Error(parsed.userMessage));
        } else {
          resolve();
        }
      });

      proc.on('error', (err) => {
        const parsed = ErrorClassifier.classify(`Failed to spawn python process: ${err.message}`, scriptPath, stageName, configuredModel);
        this.state.parsedError = parsed;
        this.state.lastError = parsed.userMessage;
        Logger.logPipelineError(parsed);
        reject(new Error(parsed.userMessage));
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
