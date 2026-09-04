import { Request, Response } from 'express';
import { SetupModel } from '../models/SetupModel.js';

export class SetupController {
  public static getStatus(req: Request, res: Response): void {
    try {
      const status = SetupModel.checkStatus();
      res.json({ success: true, ...status });
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  }

  public static async runSetup(req: Request, res: Response): Promise<void> {
    try {
      const status = await SetupModel.runSetup();
      res.json({ success: true, ...status, message: 'Setup orchestrator ran successfully.' });
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  }
}
