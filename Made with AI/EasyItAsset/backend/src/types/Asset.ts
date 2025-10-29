import { IAssetTypeConfig } from './FieldConfig';

export interface IAsset {
  id: string;
  name: string;
  containerId: string;
  assetTypeId: string;
  assetSubTypeId?: string;
  values: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export interface IAssetWithType extends IAsset {
  assetType: IAssetTypeConfig;
} 