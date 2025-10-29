import { IAssetSubTypeConfig } from '../../types/FieldConfig';
import { FieldValidator } from './FieldValidator';

export class AssetSubTypeValidator {
  static validateSubType(subType: IAssetSubTypeConfig): void {
    if (!subType.name?.trim()) {
      throw new Error('Subtype name is required');
    }
    if (!subType.label?.trim()) {
      throw new Error('Subtype label is required');
    }
    if (!subType.parentTypeId) {
      throw new Error('Parent type ID is required');
    }
    if (!Array.isArray(subType.fields)) {
      throw new Error('Subtype fields must be an array');
    }

    const fieldNames = new Set<string>();
    subType.fields.forEach(field => {
      FieldValidator.validateField(field);
      if (fieldNames.has(field.name)) {
        throw new Error(`Duplicate field name: ${field.name}`);
      }
      fieldNames.add(field.name);
    });

    if (subType.hiddenFields) {
      subType.hiddenFields.forEach(fieldName => {
        if (!subType.fields.some(field => field.name === fieldName)) {
          throw new Error(`Hidden field "${fieldName}" does not exist in fields`);
        }
      });
    }

    if (subType.overriddenFields) {
      subType.overriddenFields.forEach(fieldName => {
        if (!subType.fields.some(field => field.name === fieldName)) {
          throw new Error(`Overridden field "${fieldName}" does not exist in fields`);
        }
      });
    }
  }
} 