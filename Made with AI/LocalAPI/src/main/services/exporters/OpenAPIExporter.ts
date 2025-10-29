// OpenAPI 3.0 Exporter
import type {
  Exporter,
  ImportExportFormat,
  ImportExportOptions,
  ExportResult,
} from '../../../types/import-export';
import type { Collection, Request } from '../../../types/models';

/**
 * OpenAPI 3.0 Exporter
 * Generates OpenAPI 3.0 specifications from collections
 */
export class OpenAPIExporter implements Exporter {
  readonly format: ImportExportFormat = 'openapi-3.0';
  readonly name = 'OpenAPI 3.0';
  readonly description = 'Export as OpenAPI 3.0 specification';
  readonly fileExtensions = ['.json', '.yaml'];

  /**
   * Export collections to OpenAPI format
   */
  async exportCollections(
    collections: Collection[],
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    try {
      // For multiple collections, create separate specs or merge
      const specs = collections.map((col) => this.generateSpec(col));

      // If single collection, return it directly
      const spec = specs.length === 1 ? specs[0] : this.mergeSpecs(specs);

      const data = JSON.stringify(spec, null, options.prettify ? 2 : 0);

      console.log(
        `[OpenAPIExporter] Exported ${collections.length} collections as OpenAPI`
      );

      return {
        success: true,
        data,
        format: this.format,
        metadata: {
          exportedAt: new Date(),
          itemCount: collections.length,
          size: data.length,
        },
      };
    } catch (error) {
      console.error('[OpenAPIExporter] Export error:', error);
      return {
        success: false,
        format: this.format,
        errors: [
          error instanceof Error
            ? error.message
            : 'Failed to export as OpenAPI',
        ],
      };
    }
  }

  /**
   * Export a single request to OpenAPI format
   */
  async exportRequest(
    request: Request,
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    try {
      const spec = {
        openapi: '3.0.0',
        info: {
          title: request.name,
          version: '1.0.0',
          description: request.description || '',
        },
        paths: {
          [this.getPath(request.url)]: {
            [request.method.toLowerCase()]: this.convertRequest(request),
          },
        },
      };

      const data = JSON.stringify(spec, null, options.prettify ? 2 : 0);

      return {
        success: true,
        data,
        format: this.format,
        metadata: {
          exportedAt: new Date(),
          itemCount: 1,
          size: data.length,
        },
      };
    } catch (error) {
      console.error('[OpenAPIExporter] Export error:', error);
      return {
        success: false,
        format: this.format,
        errors: [
          error instanceof Error ? error.message : 'Failed to export as OpenAPI',
        ],
      };
    }
  }

  /**
   * Export multiple requests to OpenAPI format
   */
  async exportRequests(
    requests: Request[],
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    try {
      const paths: any = {};

      for (const request of requests) {
        const path = this.getPath(request.url);
        const method = request.method.toLowerCase();

        if (!paths[path]) {
          paths[path] = {};
        }

        paths[path][method] = this.convertRequest(request);
      }

      const spec = {
        openapi: '3.0.0',
        info: {
          title: 'Exported API',
          version: '1.0.0',
        },
        paths,
      };

      const data = JSON.stringify(spec, null, options.prettify ? 2 : 0);

      return {
        success: true,
        data,
        format: this.format,
        metadata: {
          exportedAt: new Date(),
          itemCount: requests.length,
          size: data.length,
        },
      };
    } catch (error) {
      console.error('[OpenAPIExporter] Export error:', error);
      return {
        success: false,
        format: this.format,
        errors: [
          error instanceof Error ? error.message : 'Failed to export as OpenAPI',
        ],
      };
    }
  }

  /**
   * Generate OpenAPI spec from collection
   */
  private generateSpec(collection: Collection): any {
    const paths: any = {};

    for (const request of collection.requests) {
      const path = this.getPath(request.url);
      const method = request.method.toLowerCase();

      if (!paths[path]) {
        paths[path] = {};
      }

      paths[path][method] = this.convertRequest(request);
    }

    return {
      openapi: '3.0.0',
      info: {
        title: collection.name,
        version: '1.0.0',
        description: collection.description || '',
      },
      paths,
    };
  }

  /**
   * Convert request to OpenAPI operation
   */
  private convertRequest(request: Request): any {
    const operation: any = {
      summary: request.name,
      description: request.description || '',
      parameters: [],
      responses: {
        '200': {
          description: 'Successful response',
        },
      },
    };

    // Add query parameters
    const enabledQueryParams = request.queryParams.filter((q) => q.enabled);
    for (const param of enabledQueryParams) {
      operation.parameters.push({
        name: param.key,
        in: 'query',
        required: false,
        schema: {
          type: 'string',
        },
        description: param.description || '',
      });
    }

    // Add header parameters
    const enabledHeaders = request.headers.filter((h) => h.enabled);
    for (const header of enabledHeaders) {
      // Skip common headers
      if (
        ['content-type', 'accept', 'authorization'].includes(
          header.key.toLowerCase()
        )
      ) {
        continue;
      }

      operation.parameters.push({
        name: header.key,
        in: 'header',
        required: false,
        schema: {
          type: 'string',
        },
      });
    }

    // Add request body
    if (request.body && request.body.content) {
      const contentType = this.getContentType(request.body.type, request.headers);

      operation.requestBody = {
        required: true,
        content: {
          [contentType]: {
            schema: this.inferSchema(request.body.content),
          },
        },
      };
    }

    return operation;
  }

  /**
   * Extract path from URL
   */
  private getPath(url: string): string {
    try {
      const urlObj = new URL(url);
      return urlObj.pathname || '/';
    } catch {
      return '/';
    }
  }

  /**
   * Get content type from body type and headers
   */
  private getContentType(bodyType: string, headers: any[]): string {
    // Check if Content-Type header exists
    const contentTypeHeader = headers.find(
      (h) => h.key.toLowerCase() === 'content-type' && h.enabled
    );

    if (contentTypeHeader) {
      return contentTypeHeader.value;
    }

    // Default based on body type
    switch (bodyType) {
      case 'json':
        return 'application/json';
      case 'xml':
        return 'application/xml';
      case 'x-www-form-urlencoded':
        return 'application/x-www-form-urlencoded';
      case 'form-data':
        return 'multipart/form-data';
      default:
        return 'text/plain';
    }
  }

  /**
   * Infer schema from content
   */
  private inferSchema(content: string): any {
    try {
      const parsed = JSON.parse(content);
      return this.generateSchemaFromValue(parsed);
    } catch {
      return {
        type: 'string',
      };
    }
  }

  /**
   * Generate schema from value
   */
  private generateSchemaFromValue(value: any): any {
    if (value === null) {
      return { type: 'null' };
    }

    if (Array.isArray(value)) {
      return {
        type: 'array',
        items: value.length > 0 ? this.generateSchemaFromValue(value[0]) : {},
      };
    }

    if (typeof value === 'object') {
      const properties: any = {};
      for (const [key, val] of Object.entries(value)) {
        properties[key] = this.generateSchemaFromValue(val);
      }
      return {
        type: 'object',
        properties,
      };
    }

    if (typeof value === 'number') {
      return { type: Number.isInteger(value) ? 'integer' : 'number' };
    }

    if (typeof value === 'boolean') {
      return { type: 'boolean' };
    }

    return { type: 'string' };
  }

  /**
   * Merge multiple specs into one
   */
  private mergeSpecs(specs: any[]): any {
    const merged = {
      openapi: '3.0.0',
      info: {
        title: 'Merged API',
        version: '1.0.0',
      },
      paths: {},
    };

    for (const spec of specs) {
      Object.assign(merged.paths, spec.paths);
    }

    return merged;
  }
}
