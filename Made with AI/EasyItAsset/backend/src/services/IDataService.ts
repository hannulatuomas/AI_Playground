import { IContainer } from '../types/Container';
import { IAssetTypeConfig, IAssetSubTypeConfig } from '../types/FieldConfig';
import { IAsset } from '../types/Asset';

export interface IDataService {
  // Container operations
  saveContainer(container: IContainer): Promise<IContainer>;
  getContainer(containerId: string): Promise<IContainer | null>;
  getContainers(): Promise<IContainer[]>;
  deleteContainer(containerId: string): Promise<void>;

  // Asset type operations
  saveAssetTypeConfig(containerId: string, config: IAssetTypeConfig): Promise<void>;
  getAssetTypeConfig(containerId: string, typeName: string): Promise<IAssetTypeConfig | null>;
  updateAssetTypeConfig(containerId: string, typeName: string, config: IAssetTypeConfig): Promise<void>;
  deleteAssetTypeConfig(containerId: string, typeName: string): Promise<void>;

  // Asset subtype operations
  saveAssetSubTypeConfig(containerId: string, parentTypeId: string, config: IAssetSubTypeConfig): Promise<void>;
  getAssetSubTypeConfig(containerId: string, parentTypeId: string, subTypeName: string): Promise<IAssetSubTypeConfig | null>;
  updateAssetSubTypeConfig(containerId: string, parentTypeId: string, subTypeName: string, config: IAssetSubTypeConfig): Promise<void>;
  deleteAssetSubTypeConfig(containerId: string, parentTypeId: string, subTypeName: string): Promise<void>;

  // Asset operations
  saveAsset(containerId: string, asset: IAsset): Promise<void>;
  getAsset(containerId: string, assetId: string): Promise<IAsset | null>;
  getAssetsByType(containerId: string, assetTypeId: string): Promise<IAsset[]>;
  updateAsset(containerId: string, assetId: string, updates: Partial<IAsset>): Promise<void>;
  deleteAsset(containerId: string, assetId: string): Promise<void>;
} 