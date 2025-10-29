import { ContainerService } from './ContainerService';
import { IAssetTypeConfig, IAssetSubTypeConfig, FieldType } from '../types/FieldConfig';
import { logger } from './logger';
import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { BaseService } from './BaseService';
import { v4 as uuidv4 } from 'uuid';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const mkdir = promisify(fs.mkdir);
const unlink = promisify(fs.unlink);

export class AssetTypeService extends BaseService {
  private containerService: ContainerService;
  private static readonly REQUEST_TIMEOUT = 30000;
  private static readonly MAX_RETRIES = 3;
  private static readonly BACKOFF_MULTIPLIER = 2;
  private static readonly INITIAL_BACKOFF = 1000;

  constructor() {
    super();
    this.containerService = new ContainerService();
  }

  private getAssetTypesFile(containerId: string): string {
    return path.join(this.dataDir, `${containerId}_asset_types.json`);
  }

  private getSubTypesFile(containerId: string, assetTypeId: string): string {
    return path.join(this.dataDir, `${containerId}_${assetTypeId}_subtypes.json`);
  }

  private async ensureFileExists(filePath: string): Promise<void> {
    try {
      await mkdir(path.dirname(filePath), { recursive: true });
      if (!fs.existsSync(filePath)) {
        await writeFile(filePath, JSON.stringify([]));
      }
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('Error ensuring file exists:', { filePath, error: errorMessage });
      throw new Error(`Failed to ensure file exists: ${errorMessage}`);
    }
  }

  protected async readJsonFile<T>(filePath: string): Promise<T> {
    try {
      const data = await readFile(filePath, 'utf8');
      return JSON.parse(data);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('Error reading JSON file:', { filePath, error: errorMessage });
      throw new Error(`Failed to read JSON file: ${errorMessage}`);
    }
  }

  protected async writeJsonFile<T>(filePath: string, data: T): Promise<void> {
    try {
      await writeFile(filePath, JSON.stringify(data, null, 2));
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('Error writing JSON file:', { filePath, error: errorMessage });
      throw new Error(`Failed to write JSON file: ${errorMessage}`);
    }
  }

  async getContainer(containerId: string) {
    try {
      const container = await this.containerService.getContainer(containerId);
      if (!container) {
        throw new Error('Container not found');
      }
      return container;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('Error getting container:', { containerId, error: errorMessage });
      throw new Error(`Failed to get container: ${errorMessage}`);
    }
  }

  async saveAssetTypeConfig(containerId: string, config: IAssetTypeConfig): Promise<void> {
    try {
      logger.info('Saving asset type config:', { containerId, config });

      const container = await this.getContainer(containerId);
      if (!container) {
        throw new Error('Container not found');
      }

      const errors = this.validateAssetType(config);
      if (errors.length > 0) {
        throw new Error(`Validation failed: ${errors.join(', ')}`);
      }

      const existingIndex = container.assetTypeConfigs.findIndex(c => c.id === config.id);
      if (existingIndex >= 0) {
        container.assetTypeConfigs[existingIndex] = config;
      } else {
        container.assetTypeConfigs.push(config);
      }

      await this.containerService.saveContainer(container);
      logger.info('Asset type config saved successfully:', { containerId, config });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('Error saving asset type config:', { containerId, config, error: errorMessage });
      throw new Error(`Failed to save asset type config: ${errorMessage}`);
    }
  }

  async getAssetTypeConfig(containerId: string, typeId: string): Promise<IAssetTypeConfig | null> {
    try {
      logger.info('Getting asset type config:', { containerId, typeId });

      const container = await this.getContainer(containerId);
      if (!container) {
        throw new Error('Container not found');
      }

      const config = container.assetTypeConfigs.find(c => c.id === typeId) || null;
      logger.info('Asset type config retrieved successfully:', { containerId, typeId, config });

      return config;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('Error getting asset type config:', { containerId, typeId, error: errorMessage });
      throw new Error(`Failed to get asset type config: ${errorMessage}`);
    }
  }

  async getAssetTypeConfigs(containerId: string): Promise<IAssetTypeConfig[]> {
    try {
      logger.info('Getting asset type configs for container:', { containerId });

      const container = await this.getContainer(containerId);
      if (!container) {
        throw new Error('Container not found');
      }

      logger.info('Asset type configs retrieved successfully:', { containerId, configs: container.assetTypeConfigs });

      return container.assetTypeConfigs || [];
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('Error getting asset type configs:', { containerId, error: errorMessage });
      throw new Error(`Failed to get asset type configs: ${errorMessage}`);
    }
  }

  async updateAssetTypeConfig(containerId: string, typeId: string, config: IAssetTypeConfig): Promise<void> {
    try {
      logger.info('Updating asset type config:', { containerId, typeId, config });

      const container = await this.getContainer(containerId);
      if (!container) {
        throw new Error('Container not found');
      }

      const errors = this.validateAssetType(config);
      if (errors.length > 0) {
        throw new Error(`Validation failed: ${errors.join(', ')}`);
      }

      const index = container.assetTypeConfigs.findIndex(c => c.id === typeId);
      if (index === -1) {
        throw new Error('Asset type config not found');
      }

      container.assetTypeConfigs[index] = config;
      await this.containerService.saveContainer(container);
      logger.info('Asset type config updated successfully:', { containerId, typeId, config });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('Error updating asset type config:', { containerId, typeId, config, error: errorMessage });
      throw new Error(`Failed to update asset type config: ${errorMessage}`);
    }
  }

  async deleteAssetTypeConfig(containerId: string, typeId: string): Promise<void> {
    try {
      logger.info('Deleting asset type config:', { containerId, typeId });

      const container = await this.getContainer(containerId);
      if (!container) {
        throw new Error('Container not found');
      }

      container.assetTypeConfigs = container.assetTypeConfigs.filter(c => c.id !== typeId);
      await this.containerService.saveContainer(container);
      logger.info('Asset type config deleted successfully:', { containerId, typeId });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('Error deleting asset type config:', { containerId, typeId, error: errorMessage });
      throw new Error(`Failed to delete asset type config: ${errorMessage}`);
    }
  }

  async saveAssetSubTypeConfig(containerId: string, parentTypeId: string, config: IAssetSubTypeConfig): Promise<void> {
    try {
      logger.info('Saving asset subtype config:', { containerId, parentTypeId, config });

      const assetType = await this.getAssetTypeConfig(containerId, parentTypeId);
      if (!assetType) {
        throw new Error('Asset type not found');
      }

      const errors = this.validateSubType(config);
      if (errors.length > 0) {
        throw new Error(`Validation failed: ${errors.join(', ')}`);
      }

      const existingIndex = assetType.subtypes.findIndex(s => s.id === config.id);
      if (existingIndex >= 0) {
        assetType.subtypes[existingIndex] = config;
      } else {
        assetType.subtypes.push(config);
      }

      await this.updateAssetTypeConfig(containerId, parentTypeId, assetType);
      logger.info('Asset subtype config saved successfully:', { containerId, parentTypeId, config });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('Error saving asset subtype config:', { containerId, parentTypeId, config, error: errorMessage });
      throw new Error(`Failed to save asset subtype config: ${errorMessage}`);
    }
  }

  async getAssetSubTypeConfig(containerId: string, parentTypeId: string, subTypeId: string): Promise<IAssetSubTypeConfig | null> {
    try {
      logger.info('Getting asset subtype config:', { containerId, parentTypeId, subTypeId });

      const assetType = await this.getAssetTypeConfig(containerId, parentTypeId);
      if (!assetType) {
        throw new Error('Asset type not found');
      }

      const subType = assetType.subtypes.find(s => s.id === subTypeId) || null;
      logger.info('Asset subtype config retrieved successfully:', { containerId, parentTypeId, subTypeId, subType });

      return subType;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('Error getting asset subtype config:', { containerId, parentTypeId, subTypeId, error: errorMessage });
      throw new Error(`Failed to get asset subtype config: ${errorMessage}`);
    }
  }

  async updateAssetSubTypeConfig(containerId: string, parentTypeId: string, subTypeId: string, config: IAssetSubTypeConfig): Promise<void> {
    try {
      logger.info('Updating asset subtype config:', { containerId, parentTypeId, subTypeId, config });

      const assetType = await this.getAssetTypeConfig(containerId, parentTypeId);
      if (!assetType) {
        throw new Error('Asset type not found');
      }

      const errors = this.validateSubType(config);
      if (errors.length > 0) {
        throw new Error(`Validation failed: ${errors.join(', ')}`);
      }

      const index = assetType.subtypes.findIndex(s => s.id === subTypeId);
      if (index === -1) {
        throw new Error('Asset subtype not found');
      }

      assetType.subtypes[index] = config;
      await this.updateAssetTypeConfig(containerId, parentTypeId, assetType);
      logger.info('Asset subtype config updated successfully:', { containerId, parentTypeId, subTypeId, config });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('Error updating asset subtype config:', { containerId, parentTypeId, subTypeId, config, error: errorMessage });
      throw new Error(`Failed to update asset subtype config: ${errorMessage}`);
    }
  }

  async deleteAssetSubTypeConfig(containerId: string, parentTypeId: string, subTypeId: string): Promise<void> {
    try {
      logger.info('Deleting asset subtype config:', { containerId, parentTypeId, subTypeId });

      const assetType = await this.getAssetTypeConfig(containerId, parentTypeId);
      if (!assetType) {
        throw new Error('Asset type not found');
      }

      assetType.subtypes = assetType.subtypes.filter(s => s.id !== subTypeId);
      await this.updateAssetTypeConfig(containerId, parentTypeId, assetType);
      logger.info('Asset subtype config deleted successfully:', { containerId, parentTypeId, subTypeId });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('Error deleting asset subtype config:', { containerId, parentTypeId, subTypeId, error: errorMessage });
      throw new Error(`Failed to delete asset subtype config: ${errorMessage}`);
    }
  }

  private validateAssetType(assetType: IAssetTypeConfig): string[] {
    const errors: string[] = [];

    if (!assetType.name) {
      errors.push('Name is required');
    }

    if (!assetType.label) {
      errors.push('Label is required');
    }

    if (assetType.fields) {
      assetType.fields.forEach((field, index) => {
        if (!field.name) {
          errors.push(`Field ${index + 1}: Name is required`);
        }

        if (!field.label) {
          errors.push(`Field ${index + 1}: Label is required`);
        }

        if (!field.type) {
          errors.push(`Field ${index + 1}: Type is required`);
        }

        if (field.validation) {
          if (field.validation.required && !field.defaultValue) {
            errors.push(`Field ${index + 1}: Default value is required for required fields`);
          }

          if (field.validation.min !== undefined && field.validation.max !== undefined && field.validation.min > field.validation.max) {
            errors.push(`Field ${index + 1}: Min value cannot be greater than max value`);
          }

          if (field.type === FieldType.Select || field.type === FieldType.MultiSelect) {
            if (!field.options || field.options.length === 0) {
              errors.push(`Field ${index + 1}: Options are required for select/multiselect fields`);
            }
          }

          if (field.type === FieldType.Date) {
            if (field.defaultValue && isNaN(Date.parse(field.defaultValue as string))) {
              errors.push(`Field ${index + 1}: Invalid default date value`);
            }
          }
        }
      });
    }

    if (assetType.subtypes) {
      assetType.subtypes.forEach((subType, index) => {
        const subTypeErrors = this.validateSubType(subType);
        subTypeErrors.forEach(error => errors.push(`Subtype ${index + 1}: ${error}`));
      });
    }

    return errors;
  }

  private validateSubType(subType: IAssetSubTypeConfig): string[] {
    const errors: string[] = [];

    if (!subType.name) {
      errors.push('Name is required');
    }

    if (!subType.label) {
      errors.push('Label is required');
    }

    if (subType.fields) {
      subType.fields.forEach((field, index) => {
        if (!field.name) {
          errors.push(`Field ${index + 1}: Name is required`);
        }

        if (!field.label) {
          errors.push(`Field ${index + 1}: Label is required`);
        }

        if (!field.type) {
          errors.push(`Field ${index + 1}: Type is required`);
        }

        if (field.validation) {
          if (field.validation.required && !field.defaultValue) {
            errors.push(`Field ${index + 1}: Default value is required for required fields`);
          }

          if (field.validation.min !== undefined && field.validation.max !== undefined && field.validation.min > field.validation.max) {
            errors.push(`Field ${index + 1}: Min value cannot be greater than max value`);
          }

          if (field.type === FieldType.Select || field.type === FieldType.MultiSelect) {
            if (!field.options || field.options.length === 0) {
              errors.push(`Field ${index + 1}: Options are required for select/multiselect fields`);
            }
          }

          if (field.type === FieldType.Date) {
            if (field.defaultValue && isNaN(Date.parse(field.defaultValue as string))) {
              errors.push(`Field ${index + 1}: Invalid default date value`);
            }
          }
        }
      });
    }

    if (subType.hiddenFields) {
      subType.hiddenFields.forEach(fieldName => {
        if (!subType.fields?.some(field => field.name === fieldName)) {
          errors.push(`Hidden field "${fieldName}" does not exist in fields`);
        }
      });
    }

    if (subType.overriddenFields) {
      subType.overriddenFields.forEach(fieldName => {
        if (!subType.fields?.some(field => field.name === fieldName)) {
          errors.push(`Overridden field "${fieldName}" does not exist in fields`);
        }
      });
    }

    return errors;
  }
} 