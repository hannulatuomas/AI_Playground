// Shared schema types for File and Database schemas
// Use these types in both backend and frontend for clarity and maintainability

// --- File Schema Types ---
export interface FileColumnSchema {
  name: string;
  type: string; // e.g., 'string', 'int', 'float', 'boolean', 'date', etc.
}

export interface FileSchema {
  file: string;
  columns: FileColumnSchema[];
}

// --- Database Schema Types ---
export interface DbColumnSchema {
  name: string;
  type: string; // e.g., 'varchar', 'int', 'boolean', etc.
  nullable?: boolean;
}

export interface DbTableSchema {
  table: string;
  columns: DbColumnSchema[];
}

// --- Discriminated API Response Types ---
export type SchemaApiResponse =
  | { type: 'database'; tables: DbTableSchema[]; success: boolean; error?: string }
  | { type: 'file'; files: FileSchema[]; success: boolean; error?: string }
