import { AssetType, IAssetType } from '../types/AssetType';
import { AssetSubType, IAssetSubType } from '../types/AssetSubType';
import { IFieldConfig } from '../types/FieldConfig';
import { IdUtils } from '../utils/IdUtils';

export class AssetTypeService {
  private static instance: AssetTypeService;
  private baseUrl: string;

  private constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  public static getInstance(baseUrl: string = 'http://localhost:3001'): AssetTypeService {
    if (!AssetTypeService.instance) {
      AssetTypeService.instance = new AssetTypeService(baseUrl);
    }
    return AssetTypeService.instance;
  }

  async getAssetTypes(containerId: string): Promise<IAssetType[]> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${containerId}/asset-types`);
      if (!response.ok) {
        throw new Error('Failed to fetch asset types');
      }
      const data = await response.json();
      return data.map((item: any) => new AssetType(item));
    } catch (error) {
      console.error('Error fetching asset types:', error);
      throw error;
    }
  }

  async getAssetType(containerId: string, assetTypeId: string): Promise<IAssetType> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${containerId}/asset-types/${assetTypeId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch asset type');
      }
      const data = await response.json();
      return new AssetType(data);
    } catch (error) {
      console.error('Error fetching asset type:', error);
      throw error;
    }
  }

  async saveAssetType(containerId: string, assetType: IAssetType): Promise<IAssetType> {
    try {
      const method = assetType.id ? 'PUT' : 'POST';
      const url = assetType.id 
        ? `${this.baseUrl}/containers/${containerId}/asset-types/${assetType.id}`
        : `${this.baseUrl}/containers/${containerId}/asset-types`;

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(assetType),
      });

      if (!response.ok) {
        throw new Error('Failed to save asset type');
      }

      const data = await response.json();
      return new AssetType(data);
    } catch (error) {
      console.error('Error saving asset type:', error);
      throw error;
    }
  }

  async deleteAssetType(containerId: string, id: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${containerId}/asset-types/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete asset type');
      }
    } catch (error) {
      console.error('Error deleting asset type:', error);
      throw error;
    }
  }

  async getSubTypes(containerId: string, assetTypeId: string): Promise<IAssetSubType[]> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${containerId}/asset-types/${assetTypeId}/subtypes`);
      if (!response.ok) {
        throw new Error('Failed to fetch subtypes');
      }
      const data = await response.json();
      return data.map((item: any) => new AssetSubType(item));
    } catch (error) {
      console.error('Error fetching subtypes:', error);
      throw error;
    }
  }

  async getSubType(containerId: string, assetTypeId: string, subTypeId: string): Promise<IAssetSubType> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${containerId}/asset-types/${assetTypeId}/subtypes/${subTypeId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch subtype');
      }
      const data = await response.json();
      return new AssetSubType(data);
    } catch (error) {
      console.error('Error fetching subtype:', error);
      throw error;
    }
  }

  async saveSubType(containerId: string, assetTypeId: string, subType: IAssetSubType): Promise<IAssetSubType> {
    try {
      const method = subType.id ? 'PUT' : 'POST';
      const url = subType.id
        ? `${this.baseUrl}/containers/${containerId}/asset-types/${assetTypeId}/subtypes/${subType.id}`
        : `${this.baseUrl}/containers/${containerId}/asset-types/${assetTypeId}/subtypes`;

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(subType),
      });

      if (!response.ok) {
        throw new Error('Failed to save subtype');
      }

      const data = await response.json();
      return new AssetSubType(data);
    } catch (error) {
      console.error('Error saving subtype:', error);
      throw error;
    }
  }

  async deleteSubType(containerId: string, assetTypeId: string, subTypeId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${containerId}/asset-types/${assetTypeId}/subtypes/${subTypeId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete subtype');
      }
    } catch (error) {
      console.error('Error deleting subtype:', error);
      throw error;
    }
  }

  async addField(assetTypeId: string, field: IFieldConfig): Promise<IFieldConfig> {
    try {
      const response = await fetch(`${this.baseUrl}/asset-types/${assetTypeId}/fields`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(field),
      });

      if (!response.ok) {
        throw new Error('Failed to add field');
      }

      return await response.json();
    } catch (error) {
      console.error('Error adding field:', error);
      throw error;
    }
  }

  async updateField(assetTypeId: string, fieldId: string, field: IFieldConfig): Promise<IFieldConfig> {
    try {
      const response = await fetch(`${this.baseUrl}/asset-types/${assetTypeId}/fields/${fieldId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(field),
      });

      if (!response.ok) {
        throw new Error('Failed to update field');
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating field:', error);
      throw error;
    }
  }

  async deleteField(assetTypeId: string, fieldId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/asset-types/${assetTypeId}/fields/${fieldId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete field');
      }
    } catch (error) {
      console.error('Error deleting field:', error);
      throw error;
    }
  }
} 