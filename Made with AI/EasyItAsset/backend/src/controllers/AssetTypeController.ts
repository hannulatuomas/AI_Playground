import { Request, Response } from 'express';
import { AssetTypeService } from '../services/AssetTypeService';
import { AssetSubTypeService } from '../services/AssetSubTypeService';
import { IAssetTypeConfig, IAssetSubTypeConfig } from '../types/FieldConfig';
import { logger } from '../utils/logger';
import { IdUtils } from '../utils/IdUtils';

export class AssetTypeController {
  private assetTypeService: AssetTypeService;
  private assetSubTypeService: AssetSubTypeService;

  constructor(assetTypeService: AssetTypeService, assetSubTypeService: AssetSubTypeService) {
    this.assetTypeService = assetTypeService;
    this.assetSubTypeService = assetSubTypeService;
  }

  public createAssetType = async (req: Request, res: Response): Promise<void> => {
    try {
      const { containerId } = req.params;
      const assetTypeData: Partial<IAssetTypeConfig> = req.body;

      logger.info('Creating asset type:', { containerId, assetTypeData });

      if (!containerId) {
        logger.error('Container ID is missing');
        res.status(400).json({ error: 'Container ID is required' });
        return;
      }

      if (!assetTypeData.name) {
        logger.error('Name is missing');
        res.status(400).json({ error: 'Name is required' });
        return;
      }

      if (!assetTypeData.label) {
        logger.error('Label is missing');
        res.status(400).json({ error: 'Label is required' });
        return;
      }

      const assetTypeId = IdUtils.generateAssetTypeId(containerId);
      const assetType: IAssetTypeConfig = {
        id: assetTypeId,
        name: assetTypeData.name,
        label: assetTypeData.label,
        fields: (assetTypeData.fields || []).map(field => ({
          ...field,
          id: IdUtils.generateFieldId(assetTypeId),
          parentTypeId: assetTypeId
        })),
        subtypes: (assetTypeData.subtypes || []).map(subType => {
          const subtypeId = IdUtils.generateSubtypeId(assetTypeId);
          return {
            ...subType,
            id: subtypeId,
            parentTypeId: assetTypeId,
            fields: subType.fields.map(field => ({
              ...field,
              id: IdUtils.generateFieldId(subtypeId),
              parentTypeId: subtypeId
            }))
          };
        }),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      await this.assetTypeService.saveAssetTypeConfig(containerId, assetType);

      logger.info('Asset type created successfully:', { containerId, assetTypeId });

      res.status(201).json(assetType);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create asset type';
      logger.error('Error creating asset type:', { error: errorMessage });
      res.status(500).json({ error: errorMessage });
    }
  };

  public getAssetTypes = async (req: Request, res: Response): Promise<void> => {
    try {
      const { containerId } = req.params;
      const assetTypes = await this.assetTypeService.getAssetTypeConfigs(containerId);
      res.json(assetTypes);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to get asset types';
      logger.error('Error getting asset types:', { error: errorMessage });
      res.status(500).json({ error: errorMessage });
    }
  };

  public getAssetType = async (req: Request, res: Response): Promise<void> => {
    try {
      const { containerId, assetTypeId } = req.params;
      const assetType = await this.assetTypeService.getAssetTypeConfig(containerId, assetTypeId);
      if (!assetType) {
        res.status(404).json({ error: 'Asset type not found' });
        return;
      }
      res.json(assetType);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to get asset type';
      logger.error('Error getting asset type:', { error: errorMessage });
      res.status(500).json({ error: errorMessage });
    }
  };

  public updateAssetType = async (req: Request, res: Response): Promise<void> => {
    try {
      const { containerId, assetTypeId } = req.params;
      const updates: Partial<IAssetTypeConfig> = req.body;

      if (updates.id && updates.id !== assetTypeId) {
        res.status(400).json({ error: 'Asset type ID mismatch' });
        return;
      }

      const completeAssetType: IAssetTypeConfig = {
        id: assetTypeId,
        name: updates.name || '',
        label: updates.label || '',
        fields: (updates.fields || []).map(field => ({
          ...field,
          id: field.id || IdUtils.generateFieldId(assetTypeId),
          parentTypeId: assetTypeId
        })),
        subtypes: (updates.subtypes || []).map(subType => {
          const subtypeId = subType.id || IdUtils.generateSubtypeId(assetTypeId);
          return {
            ...subType,
            id: subtypeId,
            parentTypeId: assetTypeId,
            fields: subType.fields.map(field => ({
              ...field,
              id: field.id || IdUtils.generateFieldId(subtypeId),
              parentTypeId: subtypeId
            }))
          };
        }),
        createdAt: updates.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      await this.assetTypeService.updateAssetTypeConfig(containerId, assetTypeId, completeAssetType);
      res.json({ message: 'Asset type updated successfully' });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update asset type';
      logger.error('Error updating asset type:', { error: errorMessage });
      res.status(500).json({ error: errorMessage });
    }
  };

  public deleteAssetType = async (req: Request, res: Response): Promise<void> => {
    try {
      const { containerId, assetTypeId } = req.params;
      await this.assetTypeService.deleteAssetTypeConfig(containerId, assetTypeId);
      res.json({ message: 'Asset type deleted successfully' });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete asset type';
      logger.error('Error deleting asset type:', { error: errorMessage });
      res.status(500).json({ error: errorMessage });
    }
  };

  async getSubTypes(req: Request, res: Response) {
    try {
      const { containerId, assetTypeId } = req.params;

      if (!containerId || !assetTypeId) {
        return res.status(400).json({ message: 'Container ID and Asset Type ID are required' });
      }

      const assetType = await this.assetTypeService.getAssetTypeConfig(containerId, assetTypeId);
      if (!assetType) {
        return res.status(404).json({ message: 'Asset type not found' });
      }

      res.json(assetType.subtypes || []);
    } catch (error) {
      logger.error('Error getting subtypes:', error);
      res.status(500).json({ message: 'Failed to get subtypes' });
    }
  }

  async createSubType(req: Request, res: Response) {
    try {
      const { containerId, assetTypeId } = req.params;
      const subTypeData = req.body;

      if (!containerId || !assetTypeId) {
        return res.status(400).json({ message: 'Container ID and Asset Type ID are required' });
      }

      if (!subTypeData.name || !subTypeData.label) {
        return res.status(400).json({ message: 'Name and label are required' });
      }

      const subType: IAssetSubTypeConfig = {
        ...subTypeData,
        id: Date.now().toString(),
        parentTypeId: assetTypeId,
        fields: subTypeData.fields || [],
        hiddenFields: subTypeData.hiddenFields || [],
        overriddenFields: subTypeData.overriddenFields || [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      await this.assetSubTypeService.saveAssetSubTypeConfig(containerId, assetTypeId, subType);
      res.status(201).json(subType);
    } catch (error) {
      logger.error('Error creating subtype:', error);
      res.status(500).json({ message: 'Failed to create subtype' });
    }
  }

  async getSubType(req: Request, res: Response) {
    try {
      const { containerId, assetTypeId, subTypeId } = req.params;

      if (!containerId || !assetTypeId || !subTypeId) {
        return res.status(400).json({ message: 'Container ID, Asset Type ID, and Subtype ID are required' });
      }

      const subType = await this.assetSubTypeService.getAssetSubTypeConfig(containerId, assetTypeId, subTypeId);

      if (!subType) {
        return res.status(404).json({ message: 'Subtype not found' });
      }

      res.json(subType);
    } catch (error) {
      logger.error('Error getting subtype:', error);
      res.status(500).json({ message: 'Failed to get subtype' });
    }
  }

  async updateSubType(req: Request, res: Response) {
    try {
      const { containerId, assetTypeId, subTypeId } = req.params;
      const updates = req.body;

      if (!containerId || !assetTypeId || !subTypeId) {
        return res.status(400).json({ message: 'Container ID, Asset Type ID, and Subtype ID are required' });
      }

      if (!updates.name || !updates.label) {
        return res.status(400).json({ message: 'Name and label are required' });
      }

      const existingSubType = await this.assetSubTypeService.getAssetSubTypeConfig(containerId, assetTypeId, subTypeId);
      if (!existingSubType) {
        return res.status(404).json({ message: 'Subtype not found' });
      }

      const updatedSubType: IAssetSubTypeConfig = {
        ...updates,
        id: subTypeId,
        parentTypeId: assetTypeId,
        fields: updates.fields || existingSubType.fields,
        hiddenFields: updates.hiddenFields || existingSubType.hiddenFields,
        overriddenFields: updates.overriddenFields || existingSubType.overriddenFields,
        createdAt: existingSubType.createdAt,
        updatedAt: new Date().toISOString()
      };

      await this.assetSubTypeService.updateAssetSubTypeConfig(containerId, assetTypeId, subTypeId, updatedSubType);
      res.json(updatedSubType);
    } catch (error) {
      logger.error('Error updating subtype:', error);
      res.status(500).json({ message: 'Failed to update subtype' });
    }
  }

  async deleteSubType(req: Request, res: Response) {
    try {
      const { containerId, assetTypeId, subTypeId } = req.params;

      if (!containerId || !assetTypeId || !subTypeId) {
        return res.status(400).json({ message: 'Container ID, Asset Type ID, and Subtype ID are required' });
      }

      const existingSubType = await this.assetSubTypeService.getAssetSubTypeConfig(containerId, assetTypeId, subTypeId);
      if (!existingSubType) {
        return res.status(404).json({ message: 'Subtype not found' });
      }

      await this.assetSubTypeService.deleteAssetSubTypeConfig(containerId, assetTypeId, subTypeId);
      res.status(204).send();
    } catch (error) {
      logger.error('Error deleting subtype:', error);
      res.status(500).json({ message: 'Failed to delete subtype' });
    }
  }
} 