import { IFieldConfig, FieldType } from '../types/FieldConfig';

export const validateField = (field: IFieldConfig, value: any): string | null => {
  if (field.validation?.pattern && value && !new RegExp(field.validation.pattern).test(value)) {
    return `${field.label} must match the required pattern`;
  }

  if (field.validation?.min !== undefined && value < field.validation.min) {
    return `${field.label} must be at least ${field.validation.min}`;
  }

  if (field.validation?.max !== undefined && value > field.validation.max) {
    return `${field.label} must be at most ${field.validation.max}`;
  }

  if (!value) {
    return null;
  }

  switch (field.type) {
    case FieldType.Number:
      if (isNaN(Number(value))) {
        return `${field.label} must be a number`;
      }
      break;
    case FieldType.Date:
      if (isNaN(Date.parse(value))) {
        return `${field.label} must be a valid date`;
      }
      break;
    case FieldType.Select:
      if (!field.options?.includes(value)) {
        return `${field.label} must be one of the available options`;
      }
      break;
    case FieldType.MultiSelect:
      if (!Array.isArray(value) || !value.every(v => field.options?.includes(v))) {
        return `${field.label} must contain only available options`;
      }
      break;
  }

  return null;
}; 