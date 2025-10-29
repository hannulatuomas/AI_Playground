import { Asset, IAsset } from './Asset';

export interface IAssetSubType extends IAsset {
  parentTypeId: string;
  hiddenFields: string[];
  overriddenFields: string[];
}

export class AssetSubType extends Asset implements IAssetSubType {
  parentTypeId: string;
  hiddenFields: string[];
  overriddenFields: string[];

  constructor(data: Partial<IAssetSubType>) {
    super(data);
    this.parentTypeId = data.parentTypeId || '';
    this.hiddenFields = data.hiddenFields || [];
    this.overriddenFields = data.overriddenFields || [];
  }

  hideField(fieldId: string): void {
    if (!this.hiddenFields.includes(fieldId)) {
      this.hiddenFields.push(fieldId);
      this.updatedAt = new Date().toISOString();
    }
  }

  showField(fieldId: string): void {
    this.hiddenFields = this.hiddenFields.filter(id => id !== fieldId);
    this.updatedAt = new Date().toISOString();
  }

  overrideField(fieldId: string): void {
    if (!this.overriddenFields.includes(fieldId)) {
      this.overriddenFields.push(fieldId);
      this.updatedAt = new Date().toISOString();
    }
  }

  removeOverride(fieldId: string): void {
    this.overriddenFields = this.overriddenFields.filter(id => id !== fieldId);
    this.updatedAt = new Date().toISOString();
  }

  isFieldHidden(fieldId: string): boolean {
    return this.hiddenFields.includes(fieldId);
  }

  isFieldOverridden(fieldId: string): boolean {
    return this.overriddenFields.includes(fieldId);
  }
} 