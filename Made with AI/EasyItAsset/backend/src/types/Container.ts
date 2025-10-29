import { IAssetTypeConfig } from './FieldConfig';
import { IAsset } from './Asset';

export interface IContainer {
  id: string;
  name: string;
  description?: string;
  ownerId: string;
  createdAt: string;
  updatedAt: string;
  assetTypeConfigs: IAssetTypeConfig[];
  assets: IAsset[];
} 