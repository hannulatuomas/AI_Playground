import { IAssetTypeConfig, IAssetSubTypeConfig } from './IAssetConfig';

export interface IDataService {
  saveAssetTypeConfig(containerId: string, config: IAssetTypeConfig): Promise<void>;
  saveAssetSubTypeConfig(containerId: string, parentTypeId: string, config: IAssetSubTypeConfig): Promise<void>;
  updateAssetSubTypeConfig(containerId: string, parentTypeId: string, subTypeName: string, config: IAssetSubTypeConfig): Promise<void>;
} 