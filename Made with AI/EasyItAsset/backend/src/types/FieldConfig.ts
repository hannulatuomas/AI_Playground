export enum FieldType {
  Text = 'Text',
  Number = 'Number',
  Date = 'Date',
  Boolean = 'Boolean',
  Select = 'Select',
  MultiSelect = 'MultiSelect',
  Reference = 'Reference'
}

export interface IFieldConfig {
  id: string;
  name: string;
  label: string;
  type: string;
  defaultValue?: any;
  options?: string[];
  validation?: {
    pattern?: string;
    min?: number;
    max?: number;
    required?: boolean;
    minLength?: number;
    maxLength?: number;
    minDate?: string;
    maxDate?: string;
  };
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
} 