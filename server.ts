import express from 'express';
import path from 'path';
import { createServer as createViteServer } from 'vite';
import apiRoutes from './server/routes/api.js';
import { SetupModel } from './server/models/SetupModel.js';
import { FileModel } from './server/models/FileModel.js';

async function startServer() {
  const app = express();
  const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 3000;

  // Ensure base data directories exist
  FileModel.ensureDirectories();

  // Middleware
  app.use(express.json({ limit: '50mb' }));
  app.use(express.urlencoded({ extended: true, limit: '50mb' }));

  // API Routes FIRST
  app.use('/api', apiRoutes);

  // Health check endpoint
  app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', service: 'personalized-humanizer-backend', timestamp: new Date().toISOString() });
  });

  // Vite middleware for development vs Static files in production
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`\n=============================================================`);
    console.log(` [Personalized Humanizer] Server is running at http://0.0.0.0:${PORT}`);
    console.log(` Ready to process handwriting & stylometry writing profiles.`);
    console.log(`=============================================================\n`);
  });
}

startServer().catch((err) => {
  console.error('Fatal server startup error:', err);
  process.exit(1);
});
