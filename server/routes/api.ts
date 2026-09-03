import { Router } from 'express';
import multer from 'multer';
import { SettingsController } from '../controllers/SettingsController.js';
import { FileController } from '../controllers/FileController.js';
import { SetupController } from '../controllers/SetupController.js';
import { PipelineController } from '../controllers/PipelineController.js';

const router = Router();
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 25 * 1024 * 1024 } // 25MB max
});

// Setup Orchestrator Endpoints
router.get('/setup/status', SetupController.getStatus);
router.post('/setup/run', SetupController.runSetup);

// Settings Configuration Endpoints (sync with settings.py)
router.get('/settings', SettingsController.getSettings);
router.post('/settings', SettingsController.updateSettings);

// File Management Endpoints (data/raw & data folders)
router.get('/files', FileController.getFiles);
router.post('/files/upload', upload.single('file'), FileController.uploadFile);
router.post('/files/sample', FileController.addTextSample);
router.delete('/files/item/:filename', FileController.deleteFile);
router.delete('/files/clear', FileController.clearAllData);

// Pipeline Execution Endpoints
router.post('/pipeline/run', PipelineController.runPipeline);
router.get('/pipeline/status', PipelineController.getPipelineStatus);
router.get('/pipeline/output', PipelineController.getLatestOutput);
router.get('/pipeline/download', PipelineController.downloadSkill);

export default router;
