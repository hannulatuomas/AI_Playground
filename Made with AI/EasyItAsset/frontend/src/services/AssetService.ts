import { BaseService } from './BaseService';
import { IAsset } from '../types/Asset';
import { IAssetTypeConfig } from '../types/FieldConfig';

export class AssetService extends BaseService {
  private static instance: AssetService;

  private constructor() {
    super('/api');
  }

  public static getInstance(): AssetService {
    if (!AssetService.instance) {
      AssetService.instance = new AssetService();
    }
    return AssetService.instance;
  }

  private handleResponse<T>(response: any): T {
    if (!response.data) {
      throw new Error('No data received from server');
    }
    return response.data;
  }

  private handleError(error: any): never {
    if (error.response?.data) {
      const { code, message, details } = error.response.data;
      throw new Error(`${message}${details ? `: ${details}` : ''}`);
    }
    throw error;
  }

  private convertToFrontendAsset(backendAsset: any): IAsset {
    return {
      ...backendAsset,
      createdAt: new Date(backendAsset.createdAt).toISOString(),
      updatedAt: new Date(backendAsset.updatedAt).toISOString()
    };
  }

  private convertToBackendAsset(frontendAsset: Partial<IAsset>): any {
    return {
      ...frontendAsset,
      createdAt: frontendAsset.createdAt || new Date().toISOString(),
      updatedAt: frontendAsset.updatedAt || new Date().toISOString()
    };
  }

  public async createAsset(
    containerId: string,
    asset: Omit<IAsset, 'id'>,
    assetType: IAssetTypeConfig
  ): Promise<IAsset> {
    try {
      if (!containerId || !asset.name || !asset.assetTypeId) {
        throw new Error('Container ID, name, and asset type ID are required');
      }

      const errors = this.validateAsset(asset, assetType);
      if (errors.length > 0) {
        throw new Error(errors.join(', '));
      }

      const response = await this.axiosInstance.post(
        `/containers/${containerId}/assets`,
        this.convertToBackendAsset({
          ...asset,
          containerId,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        })
      );
      return this.convertToFrontendAsset(this.handleResponse<IAsset>(response));
    } catch (error) {
      return this.handleError(error);
    }
  }

  public async getAssets(containerId: string): Promise<IAsset[]> {
    try {
      if (!containerId) {
        throw new Error('Container ID is required');
      }

      const response = await this.axiosInstance.get(
        `/containers/${containerId}/assets`
      );
      const assets = this.handleResponse<any[]>(response);
      return assets.map(asset => this.convertToFrontendAsset(asset));
    } catch (error) {
      return this.handleError(error);
    }
  }

  public async getAsset(containerId: string, assetId: string): Promise<IAsset> {
    try {
      if (!containerId || !assetId) {
        throw new Error('Container ID and asset ID are required');
      }

      const response = await this.axiosInstance.get(
        `/containers/${containerId}/assets/${assetId}`
      );
      const asset = this.handleResponse<any>(response);
      return this.convertToFrontendAsset(asset);
    } catch (error) {
      return this.handleError(error);
    }
  }

  public async updateAsset(
    containerId: string,
    assetId: string,
    asset: Partial<IAsset>,
    assetType: IAssetTypeConfig
  ): Promise<IAsset> {
    try {
      if (!containerId || !assetId) {
        throw new Error('Container ID and asset ID are required');
      }

      const errors = this.validateAsset(asset, assetType);
      if (errors.length > 0) {
        throw new Error(errors.join(', '));
      }

      const response = await this.axiosInstance.put(
        `/containers/${containerId}/assets/${assetId}`,
        this.convertToBackendAsset({
          ...asset,
          updatedAt: new Date().toISOString()
        })
      );
      return this.convertToFrontendAsset(this.handleResponse<IAsset>(response));
    } catch (error) {
      return this.handleError(error);
    }
  }

  public async deleteAsset(containerId: string, assetId: string): Promise<void> {
    try {
      if (!containerId || !assetId) {
        throw new Error('Container ID and asset ID are required');
      }

      const response = await this.axiosInstance.delete(
        `/containers/${containerId}/assets/${assetId}`
      );
      return this.handleResponse<void>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  private validateAsset(asset: Partial<IAsset>, assetType: IAssetTypeConfig): string[] {
    const errors: string[] = [];

    if (!asset.name) {
      errors.push('Name is required');
    }

    if (!asset.assetTypeId) {
      errors.push('Asset type is required');
    }

    // Validate fields based on their validation rules
    assetType.fields.forEach(field => {
      const value = asset.values?.[field.name];
      
      // Check if value exists
      if (value === undefined || value === null || value === '') {
        if (field.validation?.min !== undefined || field.validation?.pattern) {
          errors.push(`${field.label} is required`);
        }
        return;
      }

      // Validate pattern if specified
      if (field.validation?.pattern) {
        const regex = new RegExp(field.validation.pattern);
        if (!regex.test(String(value))) {
          errors.push(`${field.label} does not match the required format`);
        }
      }

      // Validate numeric constraints
      if (field.type === 'number' && field.validation) {
        const numValue = Number(value);
        if (field.validation.min !== undefined && numValue < field.validation.min) {
          errors.push(`${field.label} must be at least ${field.validation.min}`);
        }
        if (field.validation.max !== undefined && numValue > field.validation.max) {
          errors.push(`${field.label} must be at most ${field.validation.max}`);
        }
      }
    });

    return errors;
  }
} 