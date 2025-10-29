import { IFieldConfig, FieldType } from '../types/FieldConfig';

export class FieldUtils {
  static convertDefaultValue(field: IFieldConfig): any {
    if (field.defaultValue === undefined || field.defaultValue === null) {
      return '';
    }

    try {
      switch (field.type) {
        case FieldType.Number:
          return Number(field.defaultValue);
        case FieldType.Boolean:
          return Boolean(field.defaultValue);
        case FieldType.Date:
          if (typeof field.defaultValue === 'string' || typeof field.defaultValue === 'number') {
            const date = new Date(field.defaultValue);
            if (isNaN(date.getTime())) {
              throw new Error('Invalid date format');
            }
            return date.toISOString();
          } else if (field.defaultValue instanceof Date) {
            return field.defaultValue.toISOString();
          }
          return new Date().toISOString();
        case FieldType.Select:
          return String(field.defaultValue);
        case FieldType.MultiSelect:
          return Array.isArray(field.defaultValue) ? field.defaultValue.map(String) : [String(field.defaultValue)];
        default:
          return String(field.defaultValue);
      }
    } catch (error) {
      console.error('Error converting default value:', error);
      return '';
    }
  }

  static convertToBackendField(field: IFieldConfig): any {
    try {
      const defaultValue = FieldUtils.convertDefaultValue(field);
      const options = field.type === FieldType.Select || field.type === FieldType.MultiSelect ? 
        (field.options || []).map((opt: string) => String(opt).trim()) : 
        undefined;

      return {
        id: field.id,
        name: field.name?.trim(),
        label: field.label?.trim(),
        type: field.type,
        defaultValue,
        options,
        validation: {
          ...field.validation,
          pattern: field.validation?.pattern?.trim(),
          min: field.validation?.min,
          max: field.validation?.max,
          minLength: field.validation?.minLength,
          maxLength: field.validation?.maxLength,
          required: field.validation?.required || false,
          minDate: field.validation?.minDate,
          maxDate: field.validation?.maxDate
        },
        createdAt: field.createdAt || new Date().toISOString(),
        updatedAt: field.updatedAt || new Date().toISOString()
      };
    } catch (error) {
      console.error('Error converting field to backend format:', error);
      throw error;
    }
  }

  static convertToFrontendField(backendField: any): IFieldConfig {
    try {
      const defaultValue = FieldUtils.convertDefaultValue(backendField);
      const options = backendField.type === FieldType.Select || backendField.type === FieldType.MultiSelect ? 
        (backendField.options || []).map((opt: string) => String(opt).trim()) : 
        undefined;

      return {
        id: backendField.id,
        name: backendField.name?.trim(),
        label: backendField.label?.trim(),
        type: backendField.type as FieldType,
        defaultValue,
        options,
        validation: {
          ...backendField.validation,
          pattern: backendField.validation?.pattern?.trim(),
          min: backendField.validation?.min,
          max: backendField.validation?.max,
          minLength: backendField.validation?.minLength,
          maxLength: backendField.validation?.maxLength,
          required: backendField.validation?.required || false,
          minDate: backendField.validation?.minDate,
          maxDate: backendField.validation?.maxDate
        },
        createdAt: new Date(backendField.createdAt).toISOString(),
        updatedAt: new Date(backendField.updatedAt).toISOString()
      };
    } catch (error) {
      console.error('Error converting field to frontend format:', error);
      throw error;
    }
  }
} 