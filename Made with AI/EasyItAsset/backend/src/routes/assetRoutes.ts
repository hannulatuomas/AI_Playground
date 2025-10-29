import { Router } from 'express';
import { AssetController } from '../controllers/AssetController';
import { AssetService } from '../services/AssetService';

export const createAssetRoutes = (assetService: AssetService) => {
  const router = Router();
  const controller = new AssetController(assetService);

  router.post('/:containerId/assets', (req, res) => controller.createAsset(req, res));
  router.get('/:containerId/assets/:assetId', (req, res) => controller.getAsset(req, res));
  router.get('/:containerId/assets/type/:assetTypeId', (req, res) => controller.getAssetsByType(req, res));
  router.put('/:containerId/assets/:assetId', (req, res) => controller.updateAsset(req, res));
  router.delete('/:containerId/assets/:assetId', (req, res) => controller.deleteAsset(req, res));

  return router;
}; 