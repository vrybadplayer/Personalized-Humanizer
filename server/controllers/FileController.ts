import { Request, Response } from 'express';
import { FileModel } from '../models/FileModel.js';

export class FileController {
  public static getFiles(req: Request, res: Response): void {
    try {
      const files = FileModel.listRawFiles();
      const status = FileModel.getStatus();
      res.json({ success: true, files, status });
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  }

  public static uploadFile(req: Request, res: Response): void {
    try {
      if (req.file) {
        const saved = FileModel.saveRawFile(req.file.originalname, req.file.buffer);
        const files = FileModel.listRawFiles();
        res.json({ success: true, file: saved, files, message: 'File uploaded successfully' });
        return;
      }

      const { filename, content } = req.body;
      if (!filename || content === undefined) {
        res.status(400).json({ success: false, error: 'Missing filename or content' });
        return;
      }

      const saved = FileModel.saveRawFile(filename, content);
      const files = FileModel.listRawFiles();
      res.json({ success: true, file: saved, files, message: 'File saved successfully' });
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  }

  public static addTextSample(req: Request, res: Response): void {
    try {
      const { title, text } = req.body;
      if (!text || !text.trim()) {
        res.status(400).json({ success: false, error: 'Text sample cannot be empty' });
        return;
      }

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const safeTitle = (title && title.trim()) ? title.trim().replace(/[^a-zA-Z0-9_-]/g, '_') : `sample_${timestamp}`;
      const filename = `${safeTitle}.txt`;

      const saved = FileModel.saveRawFile(filename, text.trim());
      const files = FileModel.listRawFiles();
      res.json({ success: true, file: saved, files, message: 'Writing sample added to data/raw' });
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  }

  public static deleteFile(req: Request, res: Response): void {
    try {
      const { filename } = req.params;
      const success = FileModel.deleteRawFile(filename);
      const files = FileModel.listRawFiles();
      res.json({ success, files, message: success ? 'File removed' : 'File not found' });
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  }

  public static clearAllData(req: Request, res: Response): void {
    try {
      const result = FileModel.clearAllData();
      const files = FileModel.listRawFiles();
      const status = FileModel.getStatus();
      res.json({
        success: result.success,
        clearedDirs: result.clearedDirs,
        files,
        status,
        message: 'All user files and pipeline outputs have been cleared (data/raw, data/clean, data/profiles, data/output).'
      });
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  }
}
