import { Router } from 'express';
import { AssetTypeController } from '../controllers/AssetTypeController';
import { AssetTypeService } from '../services/AssetTypeService';
import { AssetSubTypeService } from '../services/AssetSubTypeService';

export const createAssetTypeRoutes = (assetTypeService: AssetTypeService, assetSubTypeService: AssetSubTypeService) => {
  const router = Router();
  const controller = new AssetTypeController(assetTypeService, assetSubTypeService);

  // Asset Type routes
  router.post('/:containerId/asset-types', controller.createAssetType.bind(controller));
  router.get('/:containerId/asset-types', controller.getAssetTypes.bind(controller));
  router.get('/:containerId/asset-types/:assetTypeId', controller.getAssetType.bind(controller));
  router.put('/:containerId/asset-types/:assetTypeId', controller.updateAssetType.bind(controller));
  router.delete('/:containerId/asset-types/:assetTypeId', controller.deleteAssetType.bind(controller));

  // Asset Subtype routes
  router.post('/:containerId/asset-types/:assetTypeId/subtypes', controller.createSubType.bind(controller));
  router.get('/:containerId/asset-types/:assetTypeId/subtypes', controller.getSubTypes.bind(controller));
  router.get('/:containerId/asset-types/:assetTypeId/subtypes/:subTypeId', controller.getSubType.bind(controller));
  router.put('/:containerId/asset-types/:assetTypeId/subtypes/:subTypeId', controller.updateSubType.bind(controller));
  router.delete('/:containerId/asset-types/:assetTypeId/subtypes/:subTypeId', controller.deleteSubType.bind(controller));

  return router;
}; 