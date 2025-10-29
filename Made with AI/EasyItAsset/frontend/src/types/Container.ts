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

export class Container implements IContainer {
  id: string;
  name: string;
  description?: string;
  ownerId: string;
  createdAt: string;
  updatedAt: string;
  assetTypeConfigs: IAssetTypeConfig[];
  assets: IAsset[];

  constructor(
    id: string,
    name: string,
    ownerId: string,
    description?: string,
    assetTypeConfigs: IAssetTypeConfig[] = []
  ) {
    this.id = id;
    this.name = name;
    this.description = description;
    this.ownerId = ownerId;
    this.createdAt = new Date().toISOString();
    this.updatedAt = new Date().toISOString();
    this.assetTypeConfigs = assetTypeConfigs;
    this.assets = [];
  }

  addAssetTypeConfig(config: IAssetTypeConfig): void {
    this.assetTypeConfigs.push(config);
    this.updatedAt = new Date().toISOString();
  }

  removeAssetTypeConfig(typeName: string): void {
    this.assetTypeConfigs = this.assetTypeConfigs.filter(
      config => config.name !== typeName
    );
    this.updatedAt = new Date().toISOString();
  }

  updateAssetTypeConfig(typeName: string, newConfig: IAssetTypeConfig): void {
    const index = this.assetTypeConfigs.findIndex(
      config => config.name === typeName
    );
    if (index !== -1) {
      this.assetTypeConfigs[index] = newConfig;
      this.updatedAt = new Date().toISOString();
    }
  }
} 