import { IAssetTypeConfig, IFieldConfig } from './FieldConfig';

// Asset types enum
export enum AssetType {
  Hardware = 'Hardware',
  Software = 'Software',
  Identity = 'Identity',
  Network = 'Network',
  VirtualHardware = 'VirtualHardware',
  HackingGadget = 'HackingGadget',
  StorageDrive = 'StorageDrive',
  Cable = 'Cable'
}

// Base Asset interface
export interface IAsset {
  id: string;
  name: string;
  label?: string;
  fields: IFieldConfig[];
  createdAt: string;
  updatedAt: string;
}

// Base Asset class
export class Asset implements IAsset {
  id: string;
  name: string;
  label?: string;
  fields: IFieldConfig[];
  createdAt: string;
  updatedAt: string;

  constructor(data: Partial<IAsset>) {
    this.id = data.id || '';
    this.name = data.name || '';
    this.label = data.label;
    this.fields = data.fields || [];
    this.createdAt = data.createdAt || new Date().toISOString();
    this.updatedAt = data.updatedAt || new Date().toISOString();
  }

  addField(field: IFieldConfig): void {
    this.fields.push(field);
    this.updatedAt = new Date().toISOString();
  }

  updateField(fieldId: string, updatedField: IFieldConfig): void {
    const index = this.fields.findIndex(f => f.id === fieldId);
    if (index !== -1) {
      this.fields[index] = updatedField;
      this.updatedAt = new Date().toISOString();
    }
  }

  removeField(fieldId: string): void {
    this.fields = this.fields.filter(f => f.id !== fieldId);
    this.updatedAt = new Date().toISOString();
  }

  getField(fieldId: string): IFieldConfig | undefined {
    return this.fields.find(f => f.id === fieldId);
  }
}

export interface IAssetWithType extends IAsset {
  assetType: IAssetTypeConfig;
} 