import { Request, Response } from 'express';
import { PipelineModel } from '../models/PipelineModel.js';

export class PipelineController {
  public static async runPipeline(req: Request, res: Response): Promise<void> {
    try {
      // Trigger execution
      const executionPromise = PipelineModel.execute();
      
      // If client requests immediate status or waits
      const waitParam = req.query.wait === 'true';
      if (waitParam) {
        const finalState = await executionPromise;
        res.json({ success: true, state: finalState });
      } else {
        // Return running state immediately and let client poll status
        const state = PipelineModel.getState();
        res.json({ success: true, state });
      }
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  }

  public static getPipelineStatus(req: Request, res: Response): void {
    try {
      const state = PipelineModel.getState();
      res.json({ success: true, state });
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  }

  public static downloadSkill(req: Request, res: Response): void {
    try {
      const streamInfo = PipelineModel.getSkillFileStream();
      if (!streamInfo.exists) {
        res.status(404).json({ success: false, error: 'SKILL.md has not been generated yet. Please run the pipeline first.' });
        return;
      }

      res.setHeader('Content-Type', 'text/markdown; charset=utf-8');
      res.setHeader('Content-Disposition', 'attachment; filename="SKILL.md"');
      res.sendFile(streamInfo.path);
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  }

  public static getLatestOutput(req: Request, res: Response): void {
    try {
      const state = PipelineModel.getState();
      res.json({
        success: true,
        skillContent: state.skillContent,
        profile: state.profile,
        hasOutput: Boolean(state.skillContent)
      });
    } catch (err: any) {
      res.status(500).json({ success: false, error: err.message });
    }
  }
}
