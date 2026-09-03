import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import { FileModel } from './FileModel.js';

export interface SetupStatusResult {
  isSetupComplete: boolean;
  directoriesStatus: {
    raw: boolean;
    clean: boolean;
    profiles: boolean;
    output: boolean;
  };
  settingsConfigured: boolean;
  lastChecked: string;
  message: string;
}

export class SetupModel {
  /**
   * Checks the environment setup status
   */
  public static checkStatus(): SetupStatusResult {
    const rawDir = path.resolve(process.cwd(), 'data/raw');
    const cleanDir = path.resolve(process.cwd(), 'data/clean');
    const profilesDir = path.resolve(process.cwd(), 'data/profiles');
    const outputDir = path.resolve(process.cwd(), 'data/output');
    const settingsPath = path.resolve(process.cwd(), 'backend/config/settings.py');

    const raw = fs.existsSync(rawDir);
    const clean = fs.existsSync(cleanDir);
    const profiles = fs.existsSync(profilesDir);
    const output = fs.existsSync(outputDir);
    const settings = fs.existsSync(settingsPath);

    const isComplete = raw && clean && profiles && output && settings;

    return {
      isSetupComplete: isComplete,
      directoriesStatus: { raw, clean, profiles, output },
      settingsConfigured: settings,
      lastChecked: new Date().toISOString(),
      message: isComplete
        ? 'Environment and data directories are initialized and verified.'
        : 'Setup requires directory initialization.'
    };
  }

  /**
   * Initializes data directories
   */
  public static async runSetup(): Promise<SetupStatusResult> {
    FileModel.ensureDirectories();
    return this.checkStatus();
  }
}
