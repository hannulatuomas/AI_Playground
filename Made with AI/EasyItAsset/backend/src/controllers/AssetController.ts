import { Request, Response } from 'express';
import { AssetService } from '../services/AssetService';
import { IAsset } from '../types/Asset';
import { logger } from '../services/logger';

export class AssetController {
  constructor(private assetService: AssetService) {}

  async createAsset(req: Request, res: Response) {
    try {
      const { containerId } = req.params;
      const asset: IAsset = {
        ...req.body,
        id: Math.random().toString(36).substring(2, 15),
        containerId,
        createdAt: new Date(),
        updatedAt: new Date()
      };

      await this.assetService.saveAsset(containerId, asset);
      res.status(201).json(asset);
    } catch (error) {
      logger.error('Error creating asset:', error);
      res.status(500).json({ error: 'Failed to create asset' });
    }
  }

  async getAsset(req: Request, res: Response) {
    try {
      const { containerId, assetId } = req.params;
      const asset = await this.assetService.getAsset(containerId, assetId);

      if (!asset) {
        return res.status(404).json({ error: 'Asset not found' });
      }

      res.json(asset);
    } catch (error) {
      logger.error('Error getting asset:', error);
      res.status(500).json({ error: 'Failed to get asset' });
    }
  }

  async getAssetsByType(req: Request, res: Response) {
    try {
      const { containerId, assetTypeId } = req.params;
      const assets = await this.assetService.getAssetsByType(containerId, assetTypeId);
      res.json(assets);
    } catch (error) {
      logger.error('Error getting assets:', error);
      res.status(500).json({ error: 'Failed to get assets' });
    }
  }

  async updateAsset(req: Request, res: Response) {
    try {
      const { containerId, assetId } = req.params;
      const updates: Partial<IAsset> = {
        ...req.body,
        updatedAt: new Date()
      };

      await this.assetService.updateAsset(containerId, assetId, updates);
      res.json(updates);
    } catch (error) {
      logger.error('Error updating asset:', error);
      res.status(500).json({ error: 'Failed to update asset' });
    }
  }

  async deleteAsset(req: Request, res: Response) {
    try {
      const { containerId, assetId } = req.params;
      await this.assetService.deleteAsset(containerId, assetId);
      res.status(204).send();
    } catch (error) {
      logger.error('Error deleting asset:', error);
      res.status(500).json({ error: 'Failed to delete asset' });
    }
  }
} 