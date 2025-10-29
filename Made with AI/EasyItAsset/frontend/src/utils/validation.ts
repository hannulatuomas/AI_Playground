import { IContainer } from '../types/Container';
import { IAssetTypeConfig, IFieldConfig, IFieldOption } from '../types/FieldConfig';

export const validateContainer = (container: Omit<IContainer, 'id'>): string[] => {
  const errors: string[] = [];

  if (!container.name || container.name.trim().length === 0) {
    errors.push('Container name is required');
  }

  if (container.name && container.name.length > 100) {
    errors.push('Container name must be less than 100 characters');
  }

  if (container.description && container.description.length > 500) {
    errors.push('Container description must be less than 500 characters');
  }

  if (!container.ownerId) {
    errors.push('Owner ID is required');
  }

  if (!container.assetTypeConfigs || container.assetTypeConfigs.length === 0) {
    errors.push('At least one asset type is required');
  } else {
    container.assetTypeConfigs.forEach((config, index) => {
      const assetTypeErrors = validateAssetTypeConfig(config);
      errors.push(...assetTypeErrors.map(error => `Asset Type ${index + 1}: ${error}`));
    });
  }

  return errors;
};

export const validateAssetTypeConfig = (config: IAssetTypeConfig): string[] => {
  const errors: string[] = [];

  if (!config.name || config.name.trim().length === 0) {
    errors.push('Asset type name is required');
  }

  if (config.name && config.name.length > 50) {
    errors.push('Asset type name must be less than 50 characters');
  }

  if (!config.label || config.label.trim().length === 0) {
    errors.push('Asset type label is required');
  }

  if (config.label && config.label.length > 100) {
    errors.push('Asset type label must be less than 100 characters');
  }

  if (!config.fields || config.fields.length === 0) {
    errors.push('At least one field is required');
  } else {
    config.fields.forEach((field, index) => {
      const fieldErrors = validateFieldConfig(field);
      errors.push(...fieldErrors.map(error => `Field ${index + 1}: ${error}`));
    });
  }

  return errors;
};

export const validateFieldConfig = (field: IFieldConfig): string[] => {
  const errors: string[] = [];

  if (!field.name || field.name.trim().length === 0) {
    errors.push('Field name is required');
  }

  if (field.name && field.name.length > 50) {
    errors.push('Field name must be less than 50 characters');
  }

  if (!field.label || field.label.trim().length === 0) {
    errors.push('Field label is required');
  }

  if (field.label && field.label.length > 100) {
    errors.push('Field label must be less than 100 characters');
  }

  if (!field.type) {
    errors.push('Field type is required');
  }

  // Validate field options if they exist
  if (field.options) {
    if (field.options.length === 0) {
      errors.push('Field options cannot be empty if provided');
    } else {
      field.options.forEach((option: IFieldOption, index) => {
        if (!option.value || option.value.trim().length === 0) {
          errors.push(`Option ${index + 1} value is required`);
        }
        if (!option.label || option.label.trim().length === 0) {
          errors.push(`Option ${index + 1} label is required`);
        }
      });
    }
  }

  return errors;
}; 