// OpenAPI/Swagger Importer
import type {
  Importer,
  ImportExportFormat,
  ImportExportOptions,
  ImportResult,
} from '../../../types/import-export';
import type { Collection, Request, HttpMethod, RequestBody } from '../../../types/models';

/**
 * OpenAPI 2.0/3.0/3.1 Importer
 * Supports Swagger 2.0 and OpenAPI 3.x specifications
 */
export class OpenAPIImporter implements Importer {
  readonly format: ImportExportFormat = 'openapi-3.0';
  readonly name = 'OpenAPI/Swagger';
  readonly description = 'Import OpenAPI 2.0/3.0/3.1 and Swagger specifications';
  readonly fileExtensions = ['.json', '.yaml', '.yml'];

  /**
   * Check if content can be imported
   */
  canImport(content: string): boolean {
    try {
      const json = JSON.parse(content);
      return !!(json.openapi || json.swagger);
    } catch {
      // Try YAML detection
      return (
        content.includes('openapi:') ||
        content.includes('swagger:') ||
        content.includes('paths:')
      );
    }
  }

  /**
   * Import OpenAPI specification
   */
  async import(
    content: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      // Parse content (JSON or YAML)
      const spec = await this.parseContent(content);

      // Detect version
      const version = this.detectVersion(spec);
      console.log(`[OpenAPIImporter] Detected OpenAPI version: ${version}`);

      // Convert to LocalAPI format
      const collection = this.createCollection(spec);
      const requests = this.createRequests(spec, collection.id);

      console.log(
        `[OpenAPIImporter] Imported 1 collection with ${requests.length} requests`
      );

      return {
        success: true,
        collections: [collection],
        requests,
        metadata: {
          format: version,
          itemCount: 1 + requests.length,
          importedAt: new Date(),
        },
      };
    } catch (error) {
      console.error('[OpenAPIImporter] Import error:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to import OpenAPI spec',
        ],
      };
    }
  }

  /**
   * Parse content (JSON or YAML)
   */
  private async parseContent(content: string): Promise<any> {
    try {
      // Try JSON first
      return JSON.parse(content);
    } catch {
      // Try YAML
      try {
        const yaml = await import('js-yaml');
        return yaml.load(content);
      } catch (error) {
        throw new Error('Failed to parse content as JSON or YAML');
      }
    }
  }

  /**
   * Detect OpenAPI/Swagger version
   */
  private detectVersion(spec: any): ImportExportFormat {
    if (spec.openapi) {
      if (spec.openapi.startsWith('3.1')) return 'openapi-3.1';
      if (spec.openapi.startsWith('3.0')) return 'openapi-3.0';
    }
    if (spec.swagger) {
      if (spec.swagger === '2.0') return 'swagger-2.0';
      return 'swagger-1.2';
    }
    return 'openapi-3.0';
  }

  /**
   * Create collection from spec
   */
  private createCollection(spec: any): Collection {
    const info = spec.info || {};

    return {
      id: `col-${Date.now()}`,
      name: info.title || 'Imported API',
      description: info.description || '',
      requests: [],
      folders: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  }

  /**
   * Create requests from spec paths
   */
  private createRequests(spec: any, collectionId: string): Request[] {
    const requests: Request[] = [];
    const paths = spec.paths || {};
    const baseUrl = this.getBaseUrl(spec);

    for (const [path, pathItem] of Object.entries(paths)) {
      const methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head'];

      for (const method of methods) {
        const operation = (pathItem as any)[method];
        if (!operation) continue;

        const request = this.createRequest(
          method,
          path,
          operation,
          baseUrl,
          collectionId,
          spec
        );
        requests.push(request);
      }
    }

    return requests;
  }

  /**
   * Get base URL from spec
   */
  private getBaseUrl(spec: any): string {
    // OpenAPI 3.x
    if (spec.servers && spec.servers.length > 0) {
      return spec.servers[0].url;
    }

    // Swagger 2.0
    if (spec.host) {
      const scheme = spec.schemes?.[0] || 'https';
      const basePath = spec.basePath || '';
      return `${scheme}://${spec.host}${basePath}`;
    }

    return 'https://api.example.com';
  }

  /**
   * Create a single request from operation
   */
  private createRequest(
    method: string,
    path: string,
    operation: any,
    baseUrl: string,
    collectionId: string,
    spec: any
  ): Request {
    // Build URL
    const url = `${baseUrl}${path}`;

    // Extract parameters
    const parameters = operation.parameters || [];
    const queryParams = parameters
      .filter((p: any) => p.in === 'query')
      .map((p: any) => ({
        key: p.name,
        value: this.getExampleValue(p),
        enabled: p.required || false,
      }));

    const headers = parameters
      .filter((p: any) => p.in === 'header')
      .map((p: any) => ({
        key: p.name,
        value: this.getExampleValue(p),
        enabled: p.required || false,
      }));

    // Extract request body (OpenAPI 3.x)
    let body: RequestBody | undefined;
    if (operation.requestBody) {
      const content = operation.requestBody.content;
      if (content) {
        const contentType = Object.keys(content)[0];
        const schema = content[contentType]?.schema;

        if (contentType.includes('json')) {
          body = {
            type: 'raw' as const,
            content: JSON.stringify(this.generateExample(schema, spec), null, 2),
          };
        } else if (contentType.includes('form')) {
          body = {
            type: contentType.includes('urlencoded') ? 'x-www-form-urlencoded' as const : 'form-data' as const,
            content: '',
          };
        }

        // Add Content-Type header
        headers.push({
          key: 'Content-Type',
          value: contentType,
          enabled: true,
        });
      }
    }

    // Swagger 2.0 body parameter
    const bodyParam = parameters.find((p: any) => p.in === 'body');
    if (bodyParam && bodyParam.schema) {
      body = {
        type: 'raw' as const,
        content: JSON.stringify(this.generateExample(bodyParam.schema, spec), null, 2),
      };
      headers.push({
        key: 'Content-Type',
        value: 'application/json',
        enabled: true,
      });
    }

    // Create request
    const request: Request = {
      id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: operation.summary || operation.operationId || `${method.toUpperCase()} ${path}`,
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

    return request;
  }

  /**
   * Get example value for parameter
   */
  private getExampleValue(param: any): string {
    if (param.example !== undefined) return String(param.example);
    if (param.default !== undefined) return String(param.default);

    const schema = param.schema || param;
    if (schema.example !== undefined) return String(schema.example);
    if (schema.default !== undefined) return String(schema.default);

    // Generate based on type
    switch (schema.type) {
      case 'string':
        return schema.format === 'email' ? 'user@example.com' : 'string';
      case 'number':
      case 'integer':
        return '0';
      case 'boolean':
        return 'true';
      case 'array':
        return '[]';
      case 'object':
        return '{}';
      default:
        return '';
    }
  }

  /**
   * Generate example from schema
   */
  private generateExample(schema: any, spec: any, depth: number = 0): any {
    if (depth > 5) return {}; // Prevent infinite recursion

    if (!schema) return {};

    // Handle $ref
    if (schema.$ref) {
      const refSchema = this.resolveRef(schema.$ref, spec);
      return this.generateExample(refSchema, spec, depth + 1);
    }

    // Use example if available
    if (schema.example !== undefined) return schema.example;

    // Generate based on type
    switch (schema.type) {
      case 'object':
        const obj: any = {};
        const properties = schema.properties || {};
        for (const [key, propSchema] of Object.entries(properties)) {
          obj[key] = this.generateExample(propSchema, spec, depth + 1);
        }
        return obj;

      case 'array':
        const itemSchema = schema.items || {};
        return [this.generateExample(itemSchema, spec, depth + 1)];

      case 'string':
        if (schema.enum) return schema.enum[0];
        if (schema.format === 'email') return 'user@example.com';
        if (schema.format === 'date') return '2024-01-01';
        if (schema.format === 'date-time') return '2024-01-01T00:00:00Z';
        if (schema.format === 'uuid') return '123e4567-e89b-12d3-a456-426614174000';
        return 'string';

      case 'number':
      case 'integer':
        return 0;

      case 'boolean':
        return true;

      default:
        return null;
    }
  }

  /**
   * Resolve $ref to actual schema
   */
  private resolveRef(ref: string, spec: any): any {
    const parts = ref.split('/');
    let current = spec;

    for (const part of parts) {
      if (part === '#') continue;
      current = current[part];
      if (!current) return {};
    }

    return current;
  }

  /**
   * Get example OpenAPI spec
   */
  getExample(): string {
    return JSON.stringify(
      {
        openapi: '3.0.0',
        info: {
          title: 'Example API',
          version: '1.0.0',
        },
        servers: [
          {
            url: 'https://api.example.com',
          },
        ],
        paths: {
          '/users': {
            get: {
              summary: 'Get all users',
              responses: {
                '200': {
                  description: 'Success',
                },
              },
            },
          },
        },
      },
      null,
      2
    );
  }
}
