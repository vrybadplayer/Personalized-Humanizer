import * as fs from 'fs';
import * as path from 'path';

export interface RawFileSummary {
  id: string;
  name: string;
  size: number;
  sizeFormatted: string;
  createdAt: string;
  estimatedWords: number;
  preview: string;
}

export interface DataFolderStatus {
  rawCount: number;
  cleanExists: boolean;
  profileExists: boolean;
  outputExists: boolean;
  outputFileSize?: number;
  lastUpdated?: string;
}

const DATA_DIR = path.resolve(process.cwd(), 'data');
const RAW_DIR = path.join(DATA_DIR, 'raw');
const CLEAN_DIR = path.join(DATA_DIR, 'clean');
const PROFILES_DIR = path.join(DATA_DIR, 'profiles');
const OUTPUT_DIR = path.join(DATA_DIR, 'output');

export class FileModel {
  /**
   * Ensures all base data directories exist
   */
  public static ensureDirectories(): void {
    const dirs = [RAW_DIR, CLEAN_DIR, PROFILES_DIR, OUTPUT_DIR];
    for (const dir of dirs) {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    }
  }

  /**
   * Format byte size nicely
   */
  private static formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  /**
   * List all user raw documents in data/raw
   */
  public static listRawFiles(): RawFileSummary[] {
    this.ensureDirectories();
    try {
      const files = fs.readdirSync(RAW_DIR);
      const summaries: RawFileSummary[] = [];

      for (const file of files) {
        if (file.startsWith('.')) continue;
        const filePath = path.join(RAW_DIR, file);
        const stat = fs.statSync(filePath);

        if (!stat.isFile()) continue;

        let content = '';
        try {
          content = fs.readFileSync(filePath, 'utf-8');
        } catch {
          content = '(Binary or encoded file content)';
        }

        const words = content.trim().split(/\s+/).filter(Boolean).length;
        const preview = content.slice(0, 180).trim().replace(/\s+/g, ' ');

        summaries.push({
          id: file,
          name: file,
          size: stat.size,
          sizeFormatted: this.formatBytes(stat.size),
          createdAt: stat.mtime.toISOString(),
          estimatedWords: words,
          preview: preview || '(Empty file)'
        });
      }

      // Sort newest first
      return summaries.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    } catch (err) {
      console.error('Error listing raw files:', err);
      return [];
    }
  }

  /**
   * Save a file or raw text sample into data/raw
   */
  public static saveRawFile(filename: string, content: Buffer | string): RawFileSummary {
    this.ensureDirectories();
    
    // Sanitize filename
    const safeName = filename.replace(/[^a-zA-Z0-9._-]/g, '_');
    const filePath = path.join(RAW_DIR, safeName);

    if (typeof content === 'string') {
      fs.writeFileSync(filePath, content, 'utf-8');
    } else {
      fs.writeFileSync(filePath, content);
    }

    const stat = fs.statSync(filePath);
    let textSample = '';
    try {
      textSample = typeof content === 'string' ? content : fs.readFileSync(filePath, 'utf-8');
    } catch {
      textSample = '';
    }

    const words = textSample.trim().split(/\s+/).filter(Boolean).length;

    return {
      id: safeName,
      name: safeName,
      size: stat.size,
      sizeFormatted: this.formatBytes(stat.size),
      createdAt: stat.mtime.toISOString(),
      estimatedWords: words,
      preview: textSample.slice(0, 180).trim().replace(/\s+/g, ' ') || '(Uploaded file)'
    };
  }

  /**
   * Delete an individual raw file
   */
  public static deleteRawFile(filename: string): boolean {
    this.ensureDirectories();
    const safeName = path.basename(filename);
    const filePath = path.join(RAW_DIR, safeName);
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
      return true;
    }
    return false;
  }

  /**
   * Clears user uploaded files and deletes/clears data/clean, data/output, data/profiles, and data/raw
   */
  public static clearAllData(): { success: boolean; clearedDirs: string[] } {
    const dirs = [RAW_DIR, CLEAN_DIR, PROFILES_DIR, OUTPUT_DIR];
    const cleared: string[] = [];

    for (const dir of dirs) {
      if (fs.existsSync(dir)) {
        try {
          fs.rmSync(dir, { recursive: true, force: true });
        } catch (err) {
          console.warn(`Could not rmSync ${dir}, emptying files instead:`, err);
          const files = fs.readdirSync(dir);
          for (const f of files) {
            fs.unlinkSync(path.join(dir, f));
          }
        }
      }
      // Recreate clean empty directory
      fs.mkdirSync(dir, { recursive: true });
      cleared.push(path.basename(dir));
    }

    return {
      success: true,
      clearedDirs: cleared
    };
  }

  /**
   * Get folder status
   */
  public static getStatus(): DataFolderStatus {
    this.ensureDirectories();
    const rawFiles = fs.readdirSync(RAW_DIR).filter(f => !f.startsWith('.'));
    const cleanFile = path.join(CLEAN_DIR, 'cleaned_corpus.txt');
    const profileFile = path.join(PROFILES_DIR, 'style_profile.json');
    const outputFile = path.join(OUTPUT_DIR, 'SKILL.md');

    let outputSize = 0;
    let lastUpdated: string | undefined = undefined;

    if (fs.existsSync(outputFile)) {
      const stat = fs.statSync(outputFile);
      outputSize = stat.size;
      lastUpdated = stat.mtime.toISOString();
    }

    return {
      rawCount: rawFiles.length,
      cleanExists: fs.existsSync(cleanFile),
      profileExists: fs.existsSync(profileFile),
      outputExists: fs.existsSync(outputFile),
      outputFileSize: outputSize,
      lastUpdated
    };
  }
}
