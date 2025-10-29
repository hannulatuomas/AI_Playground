// Shared schema types for File and Database schemas (frontend copy)
// Keep this in sync with backend/src/schemaTypes.ts

export interface FileColumnSchema {
  name: string;
  type: string;
}

export interface FileSchema {
  file: string;
  columns: FileColumnSchema[];
}

export interface DbColumnSchema {
  name: string;
  type: string;
  nullable?: boolean;
}

export interface DbTableSchema {
  table: string;
  columns: DbColumnSchema[];
}

export type SchemaApiResponse =
  | { type: 'database'; tables: DbTableSchema[]; success: boolean; error?: string }
  | { type: 'file'; files: FileSchema[]; success: boolean; error?: string }
