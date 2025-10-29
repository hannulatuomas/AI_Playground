import * as fs from 'fs';
import * as path from 'path';
import { parse } from 'csv-parse/sync';
import { stringify } from 'csv-stringify/sync';
import { IContainer } from '../types/Container';
import { IAssetTypeConfig, IAssetSubTypeConfig } from '../types/FieldConfig';
import { IAsset } from '../types/Asset';
import { IDataService } from './IDataService';
import { logger } from './logger';
import { mkdir, writeFile, readFile } from 'fs/promises';
import { BaseService } from './BaseService';

export class ContainerService extends BaseService implements IDataService {
  private readonly containersFile: string;
  private readonly containersDir: string;

  constructor() {
    super();
    this.containersDir = path.join(this.dataDir, 'containers');
    this.containersFile = path.join(this.containersDir, 'index.csv');
    this.ensureFileExists();
  }

  private async ensureFileExists(): Promise<void> {
    try {
      await mkdir(this.containersDir, { recursive: true });
      if (!fs.existsSync(this.containersFile)) {
        await writeFile(this.containersFile, 'id,name,description,ownerId,createdAt,updatedAt\n');
      }
    } catch (error) {
      logger.error('Error ensuring containers file exists:', error);
      throw error;
    }
  }

  private async readContainers(): Promise<IContainer[]> {
    try {
      const content = await readFile(this.containersFile, 'utf-8');
      if (!content.trim()) return [];
      
      const containers = parse(content, {
        columns: true,
        skip_empty_lines: true
      });

      // Load asset types for each container
      for (const container of containers) {
        const assetTypesFile = path.join(this.containersDir, `${container.id}_assetTypes.json`);
        if (fs.existsSync(assetTypesFile)) {
          container.assetTypeConfigs = JSON.parse(await readFile(assetTypesFile, 'utf-8'));
        } else {
          container.assetTypeConfigs = [];
        }
      }

      return containers;
    } catch (error) {
      logger.error('Error reading containers:', error);
      throw error;
    }
  }

  private async writeContainers(containers: IContainer[]): Promise<void> {
    try {
      // Write container metadata to CSV
      const containerMetadata = containers.map(c => ({
        id: c.id,
        name: c.name,
        description: c.description,
        ownerId: c.ownerId,
        createdAt: c.createdAt,
        updatedAt: c.updatedAt
      }));
      
      const content = stringify(containerMetadata, { header: true });
      await writeFile(this.containersFile, content);

      // Write asset types to separate JSON files
      for (const container of containers) {
        const assetTypesFile = path.join(this.containersDir, `${container.id}_assetTypes.json`);
        await writeFile(assetTypesFile, JSON.stringify(container.assetTypeConfigs, null, 2));
      }
    } catch (error) {
      logger.error('Error writing containers:', error);
      throw error;
    }
  }

  async saveContainer(container: IContainer): Promise<IContainer> {
    try {
      const containers = await this.readContainers();
      const existingIndex = containers.findIndex(c => c.id === container.id);
      
      if (existingIndex >= 0) {
        containers[existingIndex] = container;
      } else {
        containers.push(container);
      }
      
      await this.writeContainers(containers);
      return container;
    } catch (error) {
      logger.error('Error saving container:', error);
      throw error;
    }
  }

  async getContainer(containerId: string): Promise<IContainer | null> {
    try {
      const containers = await this.readContainers();
      return containers.find(c => c.id === containerId) || null;
    } catch (error) {
      logger.error('Error getting container:', error);
      throw error;
    }
  }

  async getContainers(): Promise<IContainer[]> {
    try {
      return await this.readContainers();
    } catch (error) {
      logger.error('Error getting containers:', error);
      throw error;
    }
  }

  async deleteContainer(containerId: string): Promise<void> {
    try {
      const containers = await this.readContainers();
      const filteredContainers = containers.filter(c => c.id !== containerId);
      await this.writeContainers(filteredContainers);
    } catch (error) {
      logger.error('Error deleting container:', error);
      throw error;
    }
  }

  async getContainersByOwner(ownerId: string): Promise<IContainer[]> {
    try {
      const containers = await this.readContainers();
      return containers.filter(c => c.ownerId === ownerId);
    } catch (error) {
      logger.error('Error getting containers by owner:', error);
      throw error;
    }
  }

  async updateContainer(id: string, container: Partial<IContainer>): Promise<IContainer> {
    try {
      const existingContainer = await this.getContainer(id);
      if (!existingContainer) {
        throw new Error('Container not found');
      }

      const updatedContainer = {
        ...existingContainer,
        ...container,
        id,
        updatedAt: new Date().toISOString()
      };

      await this.saveContainer(updatedContainer);
      return updatedContainer;
    } catch (error) {
      logger.error('Error updating container:', error);
      throw error;
    }
  }

  // Asset type operations - these are not implemented as they are handled by AssetTypeService
  async saveAssetTypeConfig(containerId: string, config: IAssetTypeConfig): Promise<void> {
    throw new Error('Method not implemented');
  }

  async getAssetTypeConfig(containerId: string, typeName: string): Promise<IAssetTypeConfig | null> {
    throw new Error('Method not implemented');
  }

  async updateAssetTypeConfig(containerId: string, typeName: string, config: IAssetTypeConfig): Promise<void> {
    throw new Error('Method not implemented');
  }

  async deleteAssetTypeConfig(containerId: string, typeId: string): Promise<void> {
    try {
      const containers = await this.readContainers();
      const containerIndex = containers.findIndex(c => c.id === containerId);
      
      if (containerIndex === -1) {
        throw new Error('Container not found');
      }

      const container = containers[containerIndex];
      container.assetTypeConfigs = container.assetTypeConfigs.filter(t => t.id !== typeId);
      container.updatedAt = new Date().toISOString();
      
      await this.writeContainers(containers);
    } catch (error) {
      logger.error('Error deleting asset type config:', error);
      throw error;
    }
  }

  // Asset subtype operations - these are not implemented as they are handled by AssetTypeService
  async saveAssetSubTypeConfig(containerId: string, parentTypeId: string, config: IAssetSubTypeConfig): Promise<void> {
    throw new Error('Method not implemented');
  }

  async getAssetSubTypeConfig(containerId: string, parentTypeId: string, subTypeName: string): Promise<IAssetSubTypeConfig | null> {
    throw new Error('Method not implemented');
  }

  async updateAssetSubTypeConfig(containerId: string, parentTypeId: string, subTypeName: string, config: IAssetSubTypeConfig): Promise<void> {
    throw new Error('Method not implemented');
  }

  async deleteAssetSubTypeConfig(containerId: string, parentTypeId: string, subTypeName: string): Promise<void> {
    throw new Error('Method not implemented');
  }

  // Asset operations - these are not implemented as they are handled by AssetService
  async saveAsset(containerId: string, asset: IAsset): Promise<void> {
    throw new Error('Method not implemented');
  }

  async getAsset(containerId: string, assetId: string): Promise<IAsset | null> {
    throw new Error('Method not implemented');
  }

  async getAssetsByType(containerId: string, assetTypeId: string): Promise<IAsset[]> {
    throw new Error('Method not implemented');
  }

  async updateAsset(containerId: string, assetId: string, updates: Partial<IAsset>): Promise<void> {
    throw new Error('Method not implemented');
  }

  async deleteAsset(containerId: string, assetId: string): Promise<void> {
    throw new Error('Method not implemented');
  }
} 