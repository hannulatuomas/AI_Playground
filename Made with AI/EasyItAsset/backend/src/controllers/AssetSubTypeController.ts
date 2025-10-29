import { Request, Response } from 'express';
import { AssetTypeService } from '../services/AssetTypeService';
import { IAssetSubTypeConfig } from '../types/FieldConfig';

export class AssetSubTypeController {
  private assetTypeService: AssetTypeService;

  constructor() {
    this.assetTypeService = new AssetTypeService();
  }

  public createAssetSubType = async (req: Request, res: Response): Promise<void> => {
    try {
      const { containerId, assetTypeId } = req.params;
      const subtypeData: Partial<IAssetSubTypeConfig> = req.body;

      console.log('Creating asset subtype:', { containerId, assetTypeId, subtypeData });

      if (!containerId || !assetTypeId) {
        res.status(400).json({ message: 'Container ID and asset type ID are required' });
        return;
      }

      if (!subtypeData.name) {
        res.status(400).json({ message: 'Name is required' });
        return;
      }

      if (!subtypeData.label) {
        res.status(400).json({ message: 'Label is required' });
        return;
      }

      const assetType = await this.assetTypeService.getAssetTypeConfig(containerId, assetTypeId);
      if (!assetType) {
        res.status(404).json({ message: 'Asset type not found' });
        return;
      }

      const subtype: IAssetSubTypeConfig = {
        id: Date.now().toString(),
        name: subtypeData.name,
        label: subtypeData.label,
        parentTypeId: assetTypeId,
        fields: subtypeData.fields || [],
        hiddenFields: subtypeData.hiddenFields || [],
        overriddenFields: subtypeData.overriddenFields || [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      const savedSubtype = await this.assetTypeService.saveAssetSubTypeConfig(containerId, assetTypeId, subtype);

      console.log('Asset subtype created successfully:', savedSubtype);

      res.status(201).json(savedSubtype);
    } catch (error) {
      console.error('Error creating asset subtype:', error);
      res.status(500).json({ message: 'Failed to create asset subtype' });
    }
  };

  public getAssetSubTypes = async (req: Request, res: Response): Promise<void> => {
    try {
      const { containerId, assetTypeId } = req.params;

      console.log('Getting asset subtypes for asset type:', { containerId, assetTypeId });

      if (!containerId || !assetTypeId) {
        res.status(400).json({ message: 'Container ID and asset type ID are required' });
        return;
      }

      const assetType = await this.assetTypeService.getAssetTypeConfig(containerId, assetTypeId);
      if (!assetType) {
        res.status(404).json({ message: 'Asset type not found' });
        return;
      }

      console.log('Asset subtypes retrieved successfully:', assetType.subtypes);

      res.status(200).json(assetType.subtypes);
    } catch (error) {
      console.error('Error getting asset subtypes:', error);
      res.status(500).json({ message: 'Failed to get asset subtypes' });
    }
  };

  public getAssetSubType = async (req: Request, res: Response): Promise<void> => {
    try {
      const { containerId, assetTypeId, subtypeId } = req.params;

      console.log('Getting asset subtype:', { containerId, assetTypeId, subtypeId });

      if (!containerId || !assetTypeId || !subtypeId) {
        res.status(400).json({ message: 'Container ID, asset type ID, and subtype ID are required' });
        return;
      }

      const assetType = await this.assetTypeService.getAssetTypeConfig(containerId, assetTypeId);
      if (!assetType) {
        res.status(404).json({ message: 'Asset type not found' });
        return;
      }

      const subtype = assetType.subtypes.find(s => s.id === subtypeId);
      if (!subtype) {
        res.status(404).json({ message: 'Asset subtype not found' });
        return;
      }

      console.log('Asset subtype retrieved successfully:', subtype);

      res.status(200).json(subtype);
    } catch (error) {
      console.error('Error getting asset subtype:', error);
      res.status(500).json({ message: 'Failed to get asset subtype' });
    }
  };

  public updateAssetSubType = async (req: Request, res: Response): Promise<void> => {
    try {
      const { containerId, assetTypeId, subtypeId } = req.params;
      const subtypeData: Partial<IAssetSubTypeConfig> = req.body;

      console.log('Updating asset subtype:', { containerId, assetTypeId, subtypeId, subtypeData });

      if (!containerId || !assetTypeId || !subtypeId) {
        res.status(400).json({ message: 'Container ID, asset type ID, and subtype ID are required' });
        return;
      }

      if (!subtypeData.name) {
        res.status(400).json({ message: 'Name is required' });
        return;
      }

      if (!subtypeData.label) {
        res.status(400).json({ message: 'Label is required' });
        return;
      }

      const assetType = await this.assetTypeService.getAssetTypeConfig(containerId, assetTypeId);
      if (!assetType) {
        res.status(404).json({ message: 'Asset type not found' });
        return;
      }

      const existingSubtype = assetType.subtypes.find(s => s.id === subtypeId);
      if (!existingSubtype) {
        res.status(404).json({ message: 'Asset subtype not found' });
        return;
      }

      const updatedSubtype: IAssetSubTypeConfig = {
        ...existingSubtype,
        ...subtypeData,
        id: subtypeId,
        parentTypeId: assetTypeId,
        fields: subtypeData.fields || existingSubtype.fields,
        updatedAt: new Date().toISOString()
      };

      await this.assetTypeService.saveAssetSubTypeConfig(containerId, assetTypeId, updatedSubtype);

      console.log('Asset subtype updated successfully:', updatedSubtype);

      res.status(200).json(updatedSubtype);
    } catch (error) {
      console.error('Error updating asset subtype:', error);
      res.status(500).json({ message: 'Failed to update asset subtype' });
    }
  };

  public deleteAssetSubType = async (req: Request, res: Response): Promise<void> => {
    try {
      const { containerId, assetTypeId, subtypeId } = req.params;

      console.log('Deleting asset subtype:', { containerId, assetTypeId, subtypeId });

      if (!containerId || !assetTypeId || !subtypeId) {
        res.status(400).json({ message: 'Container ID, asset type ID, and subtype ID are required' });
        return;
      }

      const assetType = await this.assetTypeService.getAssetTypeConfig(containerId, assetTypeId);
      if (!assetType) {
        res.status(404).json({ message: 'Asset type not found' });
        return;
      }

      const existingSubtype = assetType.subtypes.find(s => s.id === subtypeId);
      if (!existingSubtype) {
        res.status(404).json({ message: 'Asset subtype not found' });
        return;
      }

      await this.assetTypeService.deleteAssetSubTypeConfig(containerId, assetTypeId, subtypeId);

      console.log('Asset subtype deleted successfully');

      res.status(204).send();
    } catch (error) {
      console.error('Error deleting asset subtype:', error);
      res.status(500).json({ message: 'Failed to delete asset subtype' });
    }
  };
} 