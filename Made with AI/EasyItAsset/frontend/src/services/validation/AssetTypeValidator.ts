import { IAssetTypeConfig, IAssetSubTypeConfig } from '../../types/FieldConfig';
import { FieldValidator } from './FieldValidator';

export class AssetTypeValidator {
  static validateAssetType(assetType: IAssetTypeConfig): void {
    if (!assetType.name?.trim()) {
      throw new Error('Asset type name is required');
    }
    if (!assetType.label?.trim()) {
      throw new Error('Asset type label is required');
    }
    if (!Array.isArray(assetType.fields)) {
      throw new Error('Asset type fields must be an array');
    }

    const fieldNames = new Set<string>();
    assetType.fields.forEach(field => {
      FieldValidator.validateField(field);
      if (fieldNames.has(field.name)) {
        throw new Error(`Duplicate field name: ${field.name}`);
      }
      fieldNames.add(field.name);
    });

    if (assetType.subtypes) {
      const subTypeNames = new Set<string>();
      assetType.subtypes.forEach(subType => {
        if (!subType.name?.trim()) {
          throw new Error('Subtype name is required');
        }
        if (!subType.label?.trim()) {
          throw new Error('Subtype label is required');
        }
        if (subTypeNames.has(subType.name)) {
          throw new Error(`Duplicate subtype name: ${subType.name}`);
        }
        subTypeNames.add(subType.name);
      });
    }
  }
} 