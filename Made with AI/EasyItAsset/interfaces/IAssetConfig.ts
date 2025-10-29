export interface IField {
  name: string;
  label: string;
  type: string;
  required: boolean;
  options?: string[];
}

export interface IAssetTypeConfig {
  id: string;
  containerId: string;
  name: string;
  label: string;
  fields: IField[];
  subtypes: string[];
  createdAt: Date;
  updatedAt: Date;
}

export interface IAssetSubTypeConfig {
  id: string;
  containerId: string;
  parentTypeId: string;
  name: string;
  label: string;
  fields: IField[];
  createdAt: Date;
  updatedAt: Date;
} 