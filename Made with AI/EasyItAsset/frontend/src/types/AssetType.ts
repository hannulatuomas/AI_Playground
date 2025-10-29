import { Asset, IAsset } from './Asset';
import { IAssetSubType } from './AssetSubType';

export interface IAssetType extends IAsset {
  subtypes: IAssetSubType[];
}

export class AssetType extends Asset implements IAssetType {
  subtypes: IAssetSubType[];

  constructor(data: Partial<IAssetType>) {
    super(data);
    this.subtypes = data.subtypes || [];
  }

  addSubType(subType: IAssetSubType): void {
    this.subtypes.push(subType);
    this.updatedAt = new Date().toISOString();
  }

  updateSubType(subTypeId: string, updatedSubType: IAssetSubType): void {
    const index = this.subtypes.findIndex(s => s.id === subTypeId);
    if (index !== -1) {
      this.subtypes[index] = updatedSubType;
      this.updatedAt = new Date().toISOString();
    }
  }

  removeSubType(subTypeId: string): void {
    this.subtypes = this.subtypes.filter(s => s.id !== subTypeId);
    this.updatedAt = new Date().toISOString();
  }

  getSubType(subTypeId: string): IAssetSubType | undefined {
    return this.subtypes.find(s => s.id === subTypeId);
  }
} 