// JSON Import/Export Handler
import type { 
  ImporterExporter, 
  ImportExportFormat, 
  ImportExportOptions, 
  ImportResult, 
  ExportResult 
} from '../../../types/import-export';
import type { Request, Collection } from '../../../types/models';

/**
 * LocalAPI JSON format structure
 */
interface LocalAPIExport {
  version: string;
  exportedAt: string;
  collections?: Collection[];
  requests?: Request[];
  environments?: any[];
  variables?: any[];
}

export class JsonImporterExporter implements ImporterExporter {
  readonly format: ImportExportFormat = 'json';
  readonly name = 'LocalAPI JSON';
  readonly description = 'LocalAPI native JSON format';
  readonly fileExtensions = ['.json'];

  /**
   * Check if content is valid JSON
   */
  canImport(content: string): boolean {
    try {
      const parsed = JSON.parse(content);
      // Check if it has LocalAPI structure or generic request/collection structure
      return (
        typeof parsed === 'object' &&
        (parsed.version !== undefined ||
         parsed.collections !== undefined ||
         parsed.requests !== undefined ||
         parsed.method !== undefined) // Single request
      );
    } catch {
      return false;
    }
  }

  /**
   * Import JSON content
   */
  async import(content: string, options?: ImportExportOptions): Promise<ImportResult> {
    try {
      const parsed = JSON.parse(content);
      const result: ImportResult = {
        success: true,
        collections: [],
        requests: [],
        environments: [],
        variables: [],
        errors: [],
        warnings: [],
        metadata: {
          format: this.format,
          itemCount: 0,
          importedAt: new Date(),
        },
      };

      // Handle LocalAPI export format
      if (parsed.version && parsed.collections) {
        result.collections = this.validateCollections(parsed.collections);
        result.requests = this.validateRequests(parsed.requests || []);
        
        if (options?.includeEnvironments && parsed.environments) {
          result.environments = parsed.environments;
        }
        
        if (options?.includeVariables && parsed.variables) {
          result.variables = parsed.variables;
        }
      }
      // Handle single collection
      else if (parsed.id && parsed.name && parsed.requests) {
        result.collections = this.validateCollections([parsed]);
      }
      // Handle array of collections
      else if (Array.isArray(parsed) && parsed.length > 0 && parsed[0].name) {
        result.collections = this.validateCollections(parsed);
      }
      // Handle single request
      else if (parsed.method && parsed.url) {
        result.requests = this.validateRequests([parsed]);
      }
      // Handle array of requests
      else if (Array.isArray(parsed) && parsed.length > 0 && parsed[0].method) {
        result.requests = this.validateRequests(parsed);
      }
      else {
        result.success = false;
        result.errors?.push('Unrecognized JSON structure');
        return result;
      }

      // Calculate item count
      result.metadata!.itemCount = 
        (result.collections?.length || 0) + 
        (result.requests?.length || 0);

      return result;
    } catch (error) {
      return {
        success: false,
        errors: [`Failed to parse JSON: ${error instanceof Error ? error.message : 'Unknown error'}`],
        metadata: {
          format: this.format,
          itemCount: 0,
          importedAt: new Date(),
        },
      };
    }
  }

  /**
   * Export collections to JSON
   */
  async exportCollections(
    collections: Collection[], 
    options?: ImportExportOptions
  ): Promise<ExportResult> {
    try {
      const exportData: LocalAPIExport = {
        version: '1.0.0',
        exportedAt: new Date().toISOString(),
        collections,
      };

      const jsonString = options?.prettify !== false
        ? JSON.stringify(exportData, null, 2)
        : JSON.stringify(exportData);

      return {
        success: true,
        data: jsonString,
        format: this.format,
        metadata: {
          exportedAt: new Date(),
          itemCount: collections.length,
          size: new Blob([jsonString]).size,
        },
      };
    } catch (error) {
      return {
        success: false,
        format: this.format,
        errors: [`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
      };
    }
  }

  /**
   * Export a single request to JSON
   */
  async exportRequest(
    request: Request, 
    options?: ImportExportOptions
  ): Promise<ExportResult> {
    try {
      const jsonString = options?.prettify !== false
        ? JSON.stringify(request, null, 2)
        : JSON.stringify(request);

      return {
        success: true,
        data: jsonString,
        format: this.format,
        metadata: {
          exportedAt: new Date(),
          itemCount: 1,
          size: new Blob([jsonString]).size,
        },
      };
    } catch (error) {
      return {
        success: false,
        format: this.format,
        errors: [`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
      };
    }
  }

  /**
   * Export multiple requests to JSON
   */
  async exportRequests(
    requests: Request[], 
    options?: ImportExportOptions
  ): Promise<ExportResult> {
    try {
      const exportData: LocalAPIExport = {
        version: '1.0.0',
        exportedAt: new Date().toISOString(),
        requests,
      };

      const jsonString = options?.prettify !== false
        ? JSON.stringify(exportData, null, 2)
        : JSON.stringify(exportData);

      return {
        success: true,
        data: jsonString,
        format: this.format,
        metadata: {
          exportedAt: new Date(),
          itemCount: requests.length,
          size: new Blob([jsonString]).size,
        },
      };
    } catch (error) {
      return {
        success: false,
        format: this.format,
        errors: [`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
      };
    }
  }

  /**
   * Get example JSON
   */
  getExample(): string {
    return JSON.stringify({
      version: '1.0.0',
      exportedAt: new Date().toISOString(),
      collections: [
        {
          id: 'col-1',
          name: 'Example Collection',
          description: 'Example API collection',
          requests: [
            {
              id: 'req-1',
              name: 'Get Users',
              method: 'GET',
              url: 'https://api.example.com/users',
              headers: [
                { key: 'Content-Type', value: 'application/json', enabled: true }
              ],
              queryParams: [],
            }
          ],
        }
      ],
    }, null, 2);
  }

  /**
   * Validate and sanitize collections
   */
  private validateCollections(collections: any[]): Collection[] {
    return collections.filter(col => col && col.name).map(col => ({
      id: col.id || `col-${Date.now()}-${Math.random()}`,
      name: col.name,
      description: col.description || '',
      parentId: col.parentId,
      folders: col.folders || [],
      requests: col.requests || [],
      createdAt: col.createdAt ? new Date(col.createdAt) : new Date(),
      updatedAt: col.updatedAt ? new Date(col.updatedAt) : new Date(),
    }));
  }

  /**
   * Validate and sanitize requests
   */
  private validateRequests(requests: any[]): Request[] {
    return requests.filter(req => req && req.method && req.url).map(req => ({
      id: req.id || `req-${Date.now()}-${Math.random()}`,
      collectionId: req.collectionId,
      name: req.name || `${req.method} ${req.url}`,
      protocol: req.protocol || 'REST',
      method: req.method,
      url: req.url,
      headers: req.headers || [],
      queryParams: req.queryParams || [],
      body: req.body,
      auth: req.auth,
      preRequestScript: req.preRequestScript,
      testScript: req.testScript,
      assertions: req.assertions || [],
      createdAt: req.createdAt ? new Date(req.createdAt) : new Date(),
      updatedAt: req.updatedAt ? new Date(req.updatedAt) : new Date(),
    }));
  }
}
