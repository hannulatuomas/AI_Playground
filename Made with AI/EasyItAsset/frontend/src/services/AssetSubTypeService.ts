import { BaseService } from './BaseService';
import { IAssetSubTypeConfig } from '../types/FieldConfig';
import { AssetSubTypeValidator } from './validation/AssetSubTypeValidator';
import { AssetTypeUtils } from '../utils/assetTypeUtils';

export class AssetSubTypeService extends BaseService {
  private static instance: AssetSubTypeService;

  private constructor() {
    super('/api');
  }

  public static getInstance(): AssetSubTypeService {
    if (!AssetSubTypeService.instance) {
      AssetSubTypeService.instance = new AssetSubTypeService();
    }
    return AssetSubTypeService.instance;
  }

  async getAssetSubTypes(containerId: string, assetTypeId: string): Promise<IAssetSubTypeConfig[]> {
    return this.retryRequest(async () => {
      const response = await this.axiosInstance.get(`/containers/${containerId}/asset-types/${assetTypeId}/subtypes`);
      return response.data.map((item: any) => AssetTypeUtils.convertToFrontendSubType(item));
    });
  }

  async getAssetSubType(containerId: string, assetTypeId: string, subTypeId: string): Promise<IAssetSubTypeConfig> {
    return this.retryRequest(async () => {
      const response = await this.axiosInstance.get(`/containers/${containerId}/asset-types/${assetTypeId}/subtypes/${subTypeId}`);
      return AssetTypeUtils.convertToFrontendSubType(response.data);
    });
  }

  async createAssetSubType(containerId: string, assetTypeId: string, subType: IAssetSubTypeConfig): Promise<IAssetSubTypeConfig> {
    try {
      if (!containerId) {
        throw new Error('Container ID is required');
      }
      if (!assetTypeId) {
        throw new Error('Asset type ID is required');
      }
      if (!subType.parentTypeId) {
        subType.parentTypeId = assetTypeId;
      }
      
      AssetSubTypeValidator.validateSubType(subType);
      const backendData = AssetTypeUtils.convertToBackendSubType(subType);
      
      return this.retryRequest(async () => {
        try {
          const response = await this.axiosInstance.post(`/containers/${containerId}/asset-types/${assetTypeId}/subtypes`, backendData);
          return AssetTypeUtils.convertToFrontendSubType(response.data);
        } catch (error: any) {
          if (error.response?.data?.message) {
            throw new Error(error.response.data.message);
          }
          throw error;
        }
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create subtype';
      throw new Error(errorMessage);
    }
  }

  async updateAssetSubType(containerId: string, assetTypeId: string, subTypeId: string, subType: IAssetSubTypeConfig): Promise<IAssetSubTypeConfig> {
    try {
      if (!containerId) {
        throw new Error('Container ID is required');
      }
      if (!assetTypeId) {
        throw new Error('Asset type ID is required');
      }
      if (!subTypeId) {
        throw new Error('Subtype ID is required');
      }
      if (!subType.parentTypeId) {
        subType.parentTypeId = assetTypeId;
      }
      
      AssetSubTypeValidator.validateSubType(subType);
      const backendData = AssetTypeUtils.convertToBackendSubType(subType);
      
      return this.retryRequest(async () => {
        try {
          const response = await this.axiosInstance.put(`/containers/${containerId}/asset-types/${assetTypeId}/subtypes/${subTypeId}`, backendData);
          return AssetTypeUtils.convertToFrontendSubType(response.data);
        } catch (error: any) {
          if (error.response?.data?.message) {
            throw new Error(error.response.data.message);
          }
          throw error;
        }
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update subtype';
      throw new Error(errorMessage);
    }
  }

  async deleteAssetSubType(containerId: string, assetTypeId: string, subTypeId: string): Promise<void> {
    return this.retryRequest(async () => {
      await this.axiosInstance.delete(`/containers/${containerId}/asset-types/${assetTypeId}/subtypes/${subTypeId}`);
    });
  }
} 