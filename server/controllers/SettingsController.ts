import { Request, Response } from 'express';
import { SettingsModel } from '../models/SettingsModel.js';

export class SettingsController {
  public static getSettings(req: Request, res: Response): void {
    try {
      const settings = SettingsModel.getSettings();
      res.json({ success: true, settings });
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  }

  public static updateSettings(req: Request, res: Response): void {
    try {
      const updated = SettingsModel.saveSettings(req.body);
      res.json({ success: true, settings: updated, message: 'Settings saved to backend/config/settings.py' });
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  }
}
