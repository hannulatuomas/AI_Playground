export enum FieldType {
  Text = 'text',
  Number = 'number',
  Date = 'date',
  Boolean = 'boolean',
  Select = 'select',
  MultiSelect = 'multiselect',
  Reference = 'reference'
}

export interface IFieldConfig {
  id: string;
  name: string;
  type: FieldType;
  label?: string;
  parentTypeId: string;
  required?: boolean;
  defaultValue?: string;
  length?: number;
  description?: string;
  // Text field validation
  pattern?: string;
  // Number field validation
  min?: number;
  max?: number;
  step?: number;
  // Date field validation
  minDate?: string;
  maxDate?: string;
  // Select/MultiSelect options
  options?: string[];
  createdAt: string;
  updatedAt: string;
}

export interface IAssetTypeConfig {
  id: string;
  name: string;
  label: string;
  fields: IFieldConfig[];
  subtypes: IAssetSubTypeConfig[];
  createdAt: string;
  updatedAt: string;
}

export interface IAssetSubTypeConfig {
  id: string;
  name: string;
  label: string;
  parentTypeId: string;
  fields: IFieldConfig[];
  hiddenFields: string[];
  overriddenFields: string[];
  createdAt: string;
  updatedAt: string;
  isEditing?: boolean;
} 