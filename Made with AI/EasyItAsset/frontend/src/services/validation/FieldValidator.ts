import { IFieldConfig, FieldType } from '../../types/FieldConfig';

export class FieldValidator {
  static validateField(field: IFieldConfig): void {
    if (!field.name?.trim()) {
      throw new Error('Field name is required');
    }
    if (!field.label?.trim()) {
      throw new Error('Field label is required');
    }
    if (!Object.values(FieldType).includes(field.type)) {
      throw new Error(`Invalid field type: ${field.type}`);
    }

    if (field.validation) {
      if (field.validation.pattern && !FieldValidator.isValidRegex(field.validation.pattern)) {
        throw new Error(`Invalid regex pattern: ${field.validation.pattern}`);
      }
      if (field.validation.min !== undefined && field.validation.max !== undefined && field.validation.min > field.validation.max) {
        throw new Error('Minimum value cannot be greater than maximum value');
      }
      if (field.validation.minLength !== undefined && field.validation.maxLength !== undefined && field.validation.minLength > field.validation.maxLength) {
        throw new Error('Minimum length cannot be greater than maximum length');
      }
      if (field.validation.minDate && field.validation.maxDate && new Date(field.validation.minDate) > new Date(field.validation.maxDate)) {
        throw new Error('Minimum date cannot be greater than maximum date');
      }
    }

    if (field.type === FieldType.Select || field.type === FieldType.MultiSelect) {
      if (!field.options || field.options.length === 0) {
        throw new Error('Select and MultiSelect fields must have options');
      }
      const uniqueOptions = new Set(field.options);
      if (uniqueOptions.size !== field.options.length) {
        throw new Error('Select and MultiSelect fields cannot have duplicate options');
      }
    }
  }

  private static isValidRegex(pattern: string): boolean {
    try {
      new RegExp(pattern);
      return true;
    } catch {
      return false;
    }
  }
} 