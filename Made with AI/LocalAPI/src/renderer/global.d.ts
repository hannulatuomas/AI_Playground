// Global type declarations for renderer process

import type { Collection, Request, Environment, Variable, Settings } from '../types/models';
import type { ImportExportFormat, ImportResult, ValidationResult } from '../types/import-export';

declare global {
  interface Window {
    electronAPI: {
      import: {
        detectFormat: (content: string) => Promise<ImportExportFormat | null>;
        validate: (content: string, format?: ImportExportFormat) => Promise<ValidationResult>;
        import: (content: string, options?: any) => Promise<ImportResult>;
        importFromFile: (filePath: string, options?: any) => Promise<ImportResult>;
        importFromURL: (url: string, options?: any) => Promise<ImportResult>;
        getSupportedFormats: () => Promise<ImportExportFormat[]>;
        getHandlers: () => Promise<any[]>;
        getHistory: () => Promise<any[]>;
        clearHistory: () => Promise<void>;
      };
      export: {
        exportCollections: (collectionIds: string[], format: ImportExportFormat, options?: any) => Promise<any>;
        exportRequest: (requestId: string, format: ImportExportFormat, options?: any) => Promise<any>;
        exportRequests: (requestIds: string[], format: ImportExportFormat, options?: any) => Promise<any>;
        saveToFile: (content: string, filePath: string, format: ImportExportFormat) => Promise<void>;
        copyToClipboard: (content: string) => Promise<void>;
        getSupportedFormats: () => Promise<ImportExportFormat[]>;
        getGenerators: () => Promise<any[]>;
        getHistory: () => Promise<any[]>;
        clearHistory: () => Promise<void>;
      };
    };
    api: {
      database: {
        // Collections
        getAllCollections: () => Promise<Collection[]>;
        getCollection: (id: string) => Promise<Collection | null>;
        createCollection: (data: Partial<Collection>) => Promise<Collection>;
        updateCollection: (id: string, data: Partial<Collection>) => Promise<void>;
        deleteCollection: (id: string) => Promise<void>;

        // Requests
        getRequest: (id: string) => Promise<Request | null>;
        getRequestsByCollection: (collectionId: string) => Promise<Request[]>;
        createRequest: (data: Partial<Request>) => Promise<Request>;
        updateRequest: (id: string, data: Partial<Request>) => Promise<void>;
        deleteRequest: (id: string) => Promise<void>;

        // Environments
        getAllEnvironments: () => Promise<Environment[]>;
        getEnvironment: (id: string) => Promise<Environment | null>;
        createEnvironment: (data: Partial<Environment>) => Promise<Environment>;
        updateEnvironment: (id: string, data: Partial<Environment>) => Promise<void>;
        deleteEnvironment: (id: string) => Promise<void>;

        // Variables
        getVariablesByScope: (scope: string) => Promise<Variable[]>;
        createVariable: (data: Partial<Variable>) => Promise<Variable>;
        updateVariable: (scope: string, key: string, value: string) => Promise<void>;
        deleteVariable: (scope: string, key: string) => Promise<void>;

        // Settings
        getAllSettings: () => Promise<Settings>;
        setSetting: (key: keyof Settings, value: any) => Promise<void>;
      };
      request: {
        send: (request: Request) => Promise<any>;
      };
      secrets: {
        isAvailable: () => Promise<boolean>;
        set: (scope: string, key: string, value: string, description?: string) => Promise<boolean>;
        get: (scope: string, key: string) => Promise<string | null>;
        delete: (scope: string, key: string) => Promise<boolean>;
        getByScope: (scope: string) => Promise<Record<string, string>>;
        deleteByScope: (scope: string) => Promise<number>;
        has: (scope: string, key: string) => Promise<boolean>;
      };
    };
  }
}

export {};
