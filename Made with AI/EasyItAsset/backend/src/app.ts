import express from 'express';
import cors from 'cors';
import { createContainerRoutes } from './routes/containerRoutes';
import { createAssetTypeRoutes } from './routes/assetTypeRoutes';
import { createAssetRoutes } from './routes/assetRoutes';
import { ContainerService } from './services/ContainerService';
import { AssetTypeService } from './services/AssetTypeService';
import { AssetSubTypeService } from './services/AssetSubTypeService';
import { AssetService } from './services/AssetService';
import { logger } from './services/logger';
import { ErrorCode, AppError } from './utils/errors';
import { RateLimiter } from './middleware/rateLimiter';
import { InputSanitizer } from './middleware/sanitizer';

const app = express();

// Initialize services
const containerService = new ContainerService();
const assetTypeService = new AssetTypeService();
const assetSubTypeService = new AssetSubTypeService(assetTypeService);
const assetService = new AssetService();

// Initialize rate limiter
const rateLimiter = new RateLimiter({
  windowMs: 15 * 60 * 1000, // 15 minutes
  maxRequests: 100 // limit each IP to 100 requests per windowMs
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(InputSanitizer.middleware());
app.use(rateLimiter.middleware());

// Routes
app.use('/containers', createContainerRoutes(containerService));
app.use('/containers', createAssetTypeRoutes(assetTypeService, assetSubTypeService));
app.use('/containers', createAssetRoutes(assetService));

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  logger.error('Error:', err);

  if (err instanceof AppError) {
    const statusCode = err.code >= 1000 && err.code < 2000 ? 400 :
                      err.code >= 2000 && err.code < 3000 ? 404 :
                      err.code >= 3000 && err.code < 4000 ? 422 :
                      err.code >= 4000 && err.code < 5000 ? 500 :
                      err.code >= 5000 && err.code < 6000 ? 404 :
                      err.code >= 6000 ? 400 : 500;

    res.status(statusCode).json({
      code: err.code,
      message: err.message,
      details: err.details
    });
  } else {
    res.status(500).json({
      code: ErrorCode.UNKNOWN_ERROR,
      message: 'An unexpected error occurred',
      details: process.env.NODE_ENV === 'development' ? err.message : undefined
    });
  }
});

// Start server
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT}`);
});

// Cleanup on process exit
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received. Shutting down gracefully...');
  try {
    await rateLimiter.destroy();
    await containerService.cleanup();
    await assetTypeService.cleanup();
    await assetService.cleanup();
    process.exit(0);
  } catch (error) {
    logger.error('Error during cleanup:', error);
    process.exit(1);
  }
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received. Shutting down gracefully...');
  try {
    await rateLimiter.destroy();
    await containerService.cleanup();
    await assetTypeService.cleanup();
    await assetService.cleanup();
    process.exit(0);
  } catch (error) {
    logger.error('Error during cleanup:', error);
    process.exit(1);
  }
});

export default app; 