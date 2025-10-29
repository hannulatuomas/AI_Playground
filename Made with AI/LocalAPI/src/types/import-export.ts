// Import/Export Type Definitions
import type { Request, Collection } from './models';

/**
 * Supported import/export formats
 */
export type ImportExportFormat = 
  // API Testing Tools
  | 'postman-v2'
  | 'postman-v2.1'
  | 'insomnia-v4'
  | 'insomnia-v5'
  | 'soapui'
  | 'thunder-client'
  // API Specifications
  | 'openapi-2.0'
  | 'openapi-3.0'
  | 'openapi-3.1'
  | 'swagger-1.2'
  | 'swagger-2.0'
  | 'raml-0.8'
  | 'raml-1.0'
  | 'wadl'
  | 'wsdl-1.0'
  | 'wsdl-1.1'
  | 'wsdl-2.0'
  | 'graphql-schema'
  | 'asyncapi-2.0'
  | 'asyncapi-3.0'
  | 'protobuf-2'
  | 'protobuf-3'
  // Request Formats
  | 'curl'
  | 'har'
  | 'http-raw'
  | 'httpie'
  // API Gateways
  | 'aws-gateway'
  | 'azure-gateway'
  | 'azure-apim'
  | 'kong'
  | 'apigee'
  // Documentation
  | 'markdown'
  | 'html'
  | 'pdf'
  // Generic
  | 'json'
  | 'yaml'
  | 'xml';

/**
 * Import methods
 */
export type ImportMethod = 
  | 'file'        // File upload
  | 'url'         // URL fetch
  | 'clipboard'   // Clipboard paste
  | 'folder'      // Folder import
  | 'git'         // Git repository
  | 'text';       // Raw text input

/**
 * Import/Export options
 */
export interface ImportExportOptions {
  format?: ImportExportFormat;
  method?: ImportMethod;
  includeEnvironments?: boolean;
  includeVariables?: boolean;
  includeSecrets?: boolean;
  includeCollections?: boolean;
  includeRequests?: boolean;
  prettify?: boolean;
  validate?: boolean;
  preview?: boolean;
  conflictResolution?: 'merge' | 'replace' | 'skip' | 'ask';
  targetCollectionId?: string;
  // Partial import support
  selectedCollectionIds?: string[];
  selectedRequestIds?: string[];
  selectedEnvironmentIds?: string[];
  selectiveImport?: boolean;
  [key: string]: any; // Allow format-specific options
}

/**
 * Import validation result
 */
export interface ValidationResult {
  valid: boolean;
  format?: ImportExportFormat;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  metadata?: {
    detectedFormat?: ImportExportFormat;
    itemCount?: number;
    hasEnvironments?: boolean;
    hasVariables?: boolean;
    hasCollections?: boolean;
  };
}

export interface ValidationError {
  code: string;
  message: string;
  path?: string;
  line?: number;
}

export interface ValidationWarning {
  code: string;
  message: string;
  suggestion?: string;
}

/**
 * Import result
 */
export interface ImportResult {
  success: boolean;
  collections?: Collection[];
  requests?: Request[];
  environments?: any[];
  variables?: any[];
  errors?: string[];
  warnings?: string[];
  metadata?: {
    format: ImportExportFormat;
    itemCount: number;
    importedAt: Date;
  };
}

/**
 * Export result
 */
export interface ExportResult {
  success: boolean;
  data?: string;
  format: ImportExportFormat;
  errors?: string[];
  metadata?: {
    exportedAt: Date;
    itemCount: number;
    size: number;
  };
}

/**
 * Base interface for importers
 */
export interface Importer {
  readonly format: ImportExportFormat;
  readonly name: string;
  readonly description: string;
  readonly fileExtensions: string[];
  
  /**
   * Validate if the content can be imported
   */
  canImport(content: string): boolean;
  
  /**
   * Import content and convert to LocalAPI format
   */
  import(content: string, options?: ImportExportOptions): Promise<ImportResult>;
  
  /**
   * Get example content for this format
   */
  getExample?(): string;
}

/**
 * Base interface for exporters
 */
export interface Exporter {
  readonly format: ImportExportFormat;
  readonly name: string;
  readonly description: string;
  readonly fileExtensions: string[];
  
  /**
   * Export collections to the target format
   */
  exportCollections(collections: Collection[], options?: ImportExportOptions): Promise<ExportResult>;
  
  /**
   * Export a single request to the target format
   */
  exportRequest(request: Request, options?: ImportExportOptions): Promise<ExportResult>;
  
  /**
   * Export multiple requests to the target format
   */
  exportRequests(requests: Request[], options?: ImportExportOptions): Promise<ExportResult>;
}

/**
 * Combined importer/exporter interface
 */
export interface ImporterExporter extends Importer, Exporter {}

/**
 * Registry entry for import/export handlers
 */
export interface ImportExportHandler {
  format: ImportExportFormat;
  importer?: Importer;
  exporter?: Exporter;
  enabled: boolean;
}

/**
 * Import conflict information
 */
export interface ImportConflict {
  type: 'collection' | 'request' | 'environment' | 'variable';
  existingItem: any;
  newItem: any;
  resolution?: 'merge' | 'replace' | 'skip';
}

/**
 * Import history entry
 */
export interface ImportHistoryEntry {
  id: string;
  timestamp: Date;
  format: ImportExportFormat;
  method: ImportMethod;
  itemCount: number;
  success: boolean;
  errors?: string[];
  metadata?: {
    fileName?: string;
    fileSize?: number;
    url?: string;
    duration?: number;
  };
}

/**
 * Export history entry
 */
export interface ExportHistoryEntry {
  id: string;
  timestamp: Date;
  format: ImportExportFormat;
  destination: 'file' | 'clipboard' | 'server';
  itemCount: number;
  success: boolean;
  metadata?: {
    fileName?: string;
    fileSize?: number;
    duration?: number;
  };
}
