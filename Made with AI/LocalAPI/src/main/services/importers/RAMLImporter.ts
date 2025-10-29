// RAML Importer
import type {
  Importer,
  ImportExportFormat,
  ImportExportOptions,
  ImportResult,
} from '../../../types/import-export';
import type { Collection, Request, HttpMethod, RequestBody } from '../../../types/models';

/**
 * RAML 0.8/1.0 Importer
 */
export class RAMLImporter implements Importer {
  readonly format: ImportExportFormat = 'raml-1.0';
  readonly name = 'RAML';
  readonly description = 'Import RAML 0.8/1.0 API specifications';
  readonly fileExtensions = ['.raml', '.yaml'];

  canImport(content: string): boolean {
    return content.trim().startsWith('#%RAML');
  }

  async import(
    content: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const yaml = await import('js-yaml');
      const lines = content.split('\n');
      
      // Parse RAML header
      const header = lines[0];
      const version = header.includes('1.0') ? 'raml-1.0' : 'raml-0.8';
      
      // Remove RAML header and parse as YAML
      const yamlContent = lines.slice(1).join('\n');
      const raml: any = yaml.load(yamlContent);

      const collection: Collection = {
        id: `col-${Date.now()}`,
        name: raml.title || 'RAML API',
        description: raml.description || '',
        requests: [],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const requests: Request[] = [];
      const baseUrl = raml.baseUri || 'https://api.example.com';

      // Process resources
      this.processResources(raml, '', baseUrl, collection.id, requests);

      console.log(`[RAMLImporter] Imported ${requests.length} requests`);

      return {
        success: true,
        collections: [collection],
        requests,
        metadata: {
          format: version as ImportExportFormat,
          itemCount: 1 + requests.length,
          importedAt: new Date(),
        },
      };
    } catch (error) {
      console.error('[RAMLImporter] Import error:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to import RAML',
        ],
      };
    }
  }

  private processResources(
    obj: any,
    parentPath: string,
    baseUrl: string,
    collectionId: string,
    requests: Request[]
  ): void {
    for (const [key, value] of Object.entries(obj)) {
      if (key.startsWith('/')) {
        const path = parentPath + key;
        const resource = value as any;

        // Process HTTP methods
        const methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head'];
        for (const method of methods) {
          if (resource[method]) {
            const request = this.createRequest(
              method,
              path,
              resource[method],
              baseUrl,
              collectionId
            );
            requests.push(request);
          }
        }

        // Process nested resources
        this.processResources(resource, path, baseUrl, collectionId, requests);
      }
    }
  }

  private createRequest(
    method: string,
    path: string,
    operation: any,
    baseUrl: string,
    collectionId: string
  ): Request {
    const url = baseUrl + path;

    const headers: any[] = [];
    const queryParams: any[] = [];
    let body: RequestBody | undefined;

    // Extract query parameters
    if (operation.queryParameters) {
      for (const [name, param] of Object.entries(operation.queryParameters as any)) {
        const p = param as any;
        queryParams.push({
          key: name,
          value: p.example || p.default || '',
          enabled: p.required || false,
        });
      }
    }

    // Extract headers
    if (operation.headers) {
      for (const [name, header] of Object.entries(operation.headers as any)) {
        const h = header as any;
        headers.push({
          key: name,
          value: h.example || h.default || '',
          enabled: h.required || false,
        });
      }
    }

    // Extract body
    if (operation.body) {
      const contentTypes = Object.keys(operation.body);
      if (contentTypes.length > 0) {
        const contentType = contentTypes[0];
        const bodySpec = operation.body[contentType];

        body = {
          type: contentType.includes('json') ? 'json' as const : 'raw' as const,
          content: bodySpec.example || JSON.stringify(bodySpec.schema || {}, null, 2),
        };

        headers.push({
          key: 'Content-Type',
          value: contentType,
          enabled: true,
        });
      }
    }

    return {
      id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: operation.displayName || `${method.toUpperCase()} ${path}`,
      description: operation.description || '',
      protocol: 'REST' as const,
      method: method.toUpperCase() as HttpMethod,
      url,
      headers,
      queryParams,
      body,
      collectionId,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  }

  getExample(): string {
    return `#%RAML 1.0
title: Example API
version: v1
baseUri: https://api.example.com
/users:
  get:
    description: Get all users
  post:
    description: Create a user`;
  }
}
