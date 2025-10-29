import * as fs from 'fs';
import * as path from 'path';
import { parse } from 'csv-parse/sync';
import { stringify } from 'csv-stringify/sync';
import { IAsset } from '../types/Asset';
import { logger } from './logger';
import { BaseService } from './BaseService';

export class AssetService extends BaseService {
  constructor() {
    super();
  }

  private getAssetsFile(containerId: string): string {
    return path.join(this.dataDir, `${containerId}_assets.csv`);
  }

  private ensureFileExists(filePath: string, headers: string): void {
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }
    if (!fs.existsSync(filePath)) {
      fs.writeFileSync(filePath, headers);
    }
  }

  async saveAsset(containerId: string, asset: IAsset): Promise<void> {
    try {
      const assetsFile = this.getAssetsFile(containerId);
      this.ensureFileExists(assetsFile, 'id,containerId,assetTypeId,assetSubTypeId,values,createdAt,updatedAt\n');

      const content = fs.readFileSync(assetsFile, 'utf-8');
      const records = parse(content, { columns: true, skip_empty_lines: true });
      records.push({
        ...asset,
        values: JSON.stringify(asset.values),
        createdAt: new Date(asset.createdAt).toISOString(),
        updatedAt: new Date(asset.updatedAt).toISOString()
      });
      fs.writeFileSync(assetsFile, stringify(records, { header: true }));
      logger.info('Asset saved', { containerId, assetId: asset.id });
    } catch (error) {
      logger.error('Error saving asset', { error, containerId, assetId: asset.id });
      throw error;
    }
  }

  async getAsset(containerId: string, assetId: string): Promise<IAsset | null> {
    try {
      const assetsFile = this.getAssetsFile(containerId);
      if (!fs.existsSync(assetsFile)) {
        return null;
      }

      const content = fs.readFileSync(assetsFile, 'utf-8');
      const records = parse(content, { columns: true, skip_empty_lines: true });
      const asset = records.find((r: any) => r.id === assetId);

      if (!asset) {
        return null;
      }

      return {
        ...asset,
        values: JSON.parse(asset.values),
        createdAt: new Date(asset.createdAt),
        updatedAt: new Date(asset.updatedAt)
      };
    } catch (error) {
      logger.error('Error getting asset', { error, containerId, assetId });
      throw error;
    }
  }

  async getAssets(containerId: string): Promise<IAsset[]> {
    try {
      const assetsFile = this.getAssetsFile(containerId);
      if (!fs.existsSync(assetsFile)) {
        return [];
      }

      const content = fs.readFileSync(assetsFile, 'utf-8');
      const records = parse(content, { columns: true, skip_empty_lines: true });

      return records.map((record: any) => ({
        ...record,
        values: JSON.parse(record.values),
        createdAt: new Date(record.createdAt),
        updatedAt: new Date(record.updatedAt)
      }));
    } catch (error) {
      logger.error('Error getting assets', { error, containerId });
      throw error;
    }
  }

  async getAssetsByType(containerId: string, assetTypeId: string): Promise<IAsset[]> {
    try {
      const assetsFile = this.getAssetsFile(containerId);
      if (!fs.existsSync(assetsFile)) return [];

      const content = fs.readFileSync(assetsFile, 'utf-8');
      const records = parse(content, { columns: true, skip_empty_lines: true });
      return records
        .filter((r: any) => r.assetTypeId === assetTypeId)
        .map((r: any) => ({
          ...r,
          values: JSON.parse(r.values || '{}'),
          createdAt: new Date(r.createdAt),
          updatedAt: new Date(r.updatedAt)
        }));
    } catch (error) {
      logger.error('Error getting assets by type', { error, containerId, assetTypeId });
      throw error;
    }
  }

  async updateAsset(containerId: string, assetId: string, updates: Partial<IAsset>): Promise<void> {
    try {
      const assetsFile = this.getAssetsFile(containerId);
      if (!fs.existsSync(assetsFile)) throw new Error('Asset not found');

      const content = fs.readFileSync(assetsFile, 'utf-8');
      const records = parse(content, { columns: true, skip_empty_lines: true });
      const index = records.findIndex((r: any) => r.id === assetId);
      if (index === -1) throw new Error('Asset not found');

      records[index] = {
        ...records[index],
        ...updates,
        values: JSON.stringify(updates.values || JSON.parse(records[index].values || '{}')),
        updatedAt: new Date().toISOString()
      };
      fs.writeFileSync(assetsFile, stringify(records, { header: true }));
      logger.info('Asset updated', { containerId, assetId });
    } catch (error) {
      logger.error('Error updating asset', { error, containerId, assetId });
      throw error;
    }
  }

  async deleteAsset(containerId: string, assetId: string): Promise<void> {
    try {
      const assetsFile = this.getAssetsFile(containerId);
      if (!fs.existsSync(assetsFile)) return;

      const content = fs.readFileSync(assetsFile, 'utf-8');
      const records = parse(content, { columns: true, skip_empty_lines: true });
      const filteredRecords = records.filter((r: any) => r.id !== assetId);
      fs.writeFileSync(assetsFile, stringify(filteredRecords, { header: true }));
      logger.info('Asset deleted', { containerId, assetId });
    } catch (error) {
      logger.error('Error deleting asset', { error, containerId, assetId });
      throw error;
    }
  }
} 