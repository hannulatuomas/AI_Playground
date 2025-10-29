import { AssetTypeService } from './AssetTypeService';
import { IAssetSubTypeConfig, FieldType } from '../types/FieldConfig';
import { logger } from './logger';
import { BaseService } from './BaseService';
import * as path from 'path';
import * as fs from 'fs';
import { promisify } from 'util';
import { v4 as uuidv4 } from 'uuid';

const mkdir = promisify(fs.mkdir);

export class AssetSubTypeService extends BaseService {
  private static readonly REQUEST_TIMEOUT = 30000;
  private static readonly MAX_RETRIES = 3;
  private static readonly BACKOFF_MULTIPLIER = 2;
  private static readonly INITIAL_BACKOFF = 1000;

  constructor(private assetTypeService: AssetTypeService) {
    super();
  }

  protected async ensureDirectoryExists(dirPath: string): Promise<void> {
    try {
      await mkdir(dirPath, { recursive: true });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('Error ensuring directory exists:', { dirPath, error: errorMessage });
      throw new Error(`Failed to ensure directory exists: ${errorMessage}`);
    }
  }

  async saveAssetSubTypeConfig(containerId: string, assetTypeId: string, subType: IAssetSubTypeConfig): Promise<void> {
    let retries = 0;
    let backoff = AssetSubTypeService.INITIAL_BACKOFF;

    while (retries < AssetSubTypeService.MAX_RETRIES) {
      try {
        const assetType = await this.assetTypeService.getAssetTypeConfig(containerId, assetTypeId);
        if (!assetType) {
          throw new Error('Asset type not found');
        }

        const errors = this.validateSubType(subType);
        if (errors.length > 0) {
          throw new Error(`Validation failed: ${errors.join(', ')}`);
        }

        const subTypesDir = path.join(this.dataDir, containerId, 'asset-types', assetTypeId, 'subtypes');
        await this.ensureDirectoryExists(subTypesDir);
        
        const configPath = path.join(subTypesDir, `${subType.id}.json`);
        await this.writeJsonFile(configPath, subType);
        
        assetType.subtypes = assetType.subtypes || [];
        const existingIndex = assetType.subtypes.findIndex(st => st.id === subType.id);
        
        if (existingIndex >= 0) {
          assetType.subtypes[existingIndex] = subType;
        } else {
          assetType.subtypes.push(subType);
        }
        
        await this.assetTypeService.saveAssetTypeConfig(containerId, assetType);
        logger.info('Asset subtype config saved successfully:', { containerId, assetTypeId, subTypeId: subType.id });
        return;
      } catch (error: unknown) {
        retries++;
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        if (retries === AssetSubTypeService.MAX_RETRIES) {
          logger.error('Failed to save asset subtype config after maximum retries:', { error: errorMessage });
          throw new Error(`Failed to save asset subtype config: ${errorMessage}`);
        }
        await new Promise(resolve => setTimeout(resolve, backoff));
        backoff *= AssetSubTypeService.BACKOFF_MULTIPLIER;
      }
    }
    throw new Error('Failed to save asset subtype config: Maximum retries exceeded');
  }

  async getAssetSubTypeConfig(containerId: string, assetTypeId: string, subTypeId: string): Promise<IAssetSubTypeConfig | null> {
    let retries = 0;
    let backoff = AssetSubTypeService.INITIAL_BACKOFF;

    while (retries < AssetSubTypeService.MAX_RETRIES) {
      try {
        const assetType = await this.assetTypeService.getAssetTypeConfig(containerId, assetTypeId);
        if (!assetType) {
          return null;
        }
        return assetType.subtypes?.find(st => st.id === subTypeId) || null;
      } catch (error: unknown) {
        retries++;
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        if (retries === AssetSubTypeService.MAX_RETRIES) {
          logger.error('Failed to get asset subtype config after maximum retries:', { error: errorMessage });
          throw new Error(`Failed to get asset subtype config: ${errorMessage}`);
        }
        await new Promise(resolve => setTimeout(resolve, backoff));
        backoff *= AssetSubTypeService.BACKOFF_MULTIPLIER;
      }
    }
    throw new Error('Failed to get asset subtype config: Maximum retries exceeded');
  }

  async updateAssetSubTypeConfig(containerId: string, assetTypeId: string, subTypeId: string, updates: Partial<IAssetSubTypeConfig>): Promise<void> {
    let retries = 0;
    let backoff = AssetSubTypeService.INITIAL_BACKOFF;

    while (retries < AssetSubTypeService.MAX_RETRIES) {
      try {
        const existingSubType = await this.getAssetSubTypeConfig(containerId, assetTypeId, subTypeId);
        if (!existingSubType) {
          throw new Error('Subtype not found');
        }

        const updatedSubType: IAssetSubTypeConfig = {
          ...existingSubType,
          ...updates,
          id: subTypeId,
          parentTypeId: assetTypeId,
          updatedAt: new Date().toISOString()
        };

        const errors = this.validateSubType(updatedSubType);
        if (errors.length > 0) {
          throw new Error(`Validation failed: ${errors.join(', ')}`);
        }

        await this.saveAssetSubTypeConfig(containerId, assetTypeId, updatedSubType);
        return;
      } catch (error: unknown) {
        retries++;
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        if (retries === AssetSubTypeService.MAX_RETRIES) {
          logger.error('Failed to update asset subtype config after maximum retries:', { error: errorMessage });
          throw new Error(`Failed to update asset subtype config: ${errorMessage}`);
        }
        await new Promise(resolve => setTimeout(resolve, backoff));
        backoff *= AssetSubTypeService.BACKOFF_MULTIPLIER;
      }
    }
    throw new Error('Failed to update asset subtype config: Maximum retries exceeded');
  }

  async deleteAssetSubTypeConfig(containerId: string, assetTypeId: string, subTypeId: string): Promise<void> {
    let retries = 0;
    let backoff = AssetSubTypeService.INITIAL_BACKOFF;

    while (retries < AssetSubTypeService.MAX_RETRIES) {
      try {
        const assetType = await this.assetTypeService.getAssetTypeConfig(containerId, assetTypeId);
        if (!assetType) {
          throw new Error('Asset type not found');
        }

        const configPath = path.join(this.dataDir, containerId, 'asset-types', assetTypeId, 'subtypes', `${subTypeId}.json`);
        
        try {
          await this.deleteFile(configPath);
        } catch (error: unknown) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          logger.warn('Failed to delete subtype config file:', { configPath, error: errorMessage });
          // Continue with removing from asset type even if file deletion fails
        }
        
        assetType.subtypes = assetType.subtypes?.filter(st => st.id !== subTypeId) || [];
        await this.assetTypeService.saveAssetTypeConfig(containerId, assetType);
        
        logger.info('Asset subtype config deleted successfully:', { containerId, assetTypeId, subTypeId });
        return;
      } catch (error: unknown) {
        retries++;
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        if (retries === AssetSubTypeService.MAX_RETRIES) {
          logger.error('Failed to delete asset subtype config after maximum retries:', { error: errorMessage });
          throw new Error(`Failed to delete asset subtype config: ${errorMessage}`);
        }
        await new Promise(resolve => setTimeout(resolve, backoff));
        backoff *= AssetSubTypeService.BACKOFF_MULTIPLIER;
      }
    }
    throw new Error('Failed to delete asset subtype config: Maximum retries exceeded');
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