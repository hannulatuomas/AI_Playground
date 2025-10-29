// Postman Collection Exporter
import type {
  Exporter,
  ImportExportFormat,
  ImportExportOptions,
  ExportResult,
} from '../../../types/import-export';
import type { Collection, Request } from '../../../types/models';

/**
 * Postman Collection v2.1 Exporter
 */
export class PostmanExporter implements Exporter {
  readonly format: ImportExportFormat = 'postman-v2.1';
  readonly name = 'Postman Collection';
  readonly description = 'Export to Postman Collection v2.1 format';
  readonly fileExtensions = ['.json'];

  /**
   * Export collections to Postman format
   */
  async exportCollections(
    collections: Collection[],
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    try {
      // For multiple collections, export as separate collections or merge
      const postmanCollections = collections.map((col) =>
        this.convertCollection(col)
      );

      // If single collection, return it directly
      // If multiple, wrap in array or merge based on options
      const data =
        postmanCollections.length === 1
          ? JSON.stringify(postmanCollections[0], null, options.prettify ? 2 : 0)
          : JSON.stringify(postmanCollections, null, options.prettify ? 2 : 0);

      console.log(
        `[PostmanExporter] Exported ${collections.length} collections`
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
      console.error('[PostmanExporter] Export error:', error);
      return {
        success: false,
        format: this.format,
        errors: [
          error instanceof Error
            ? error.message
            : 'Failed to export Postman collection',
        ],
      };
    }
  }

  /**
   * Export a single request to Postman format
   */
  async exportRequest(
    request: Request,
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    try {
      const postmanRequest = this.convertRequest(request);
      const data = JSON.stringify(postmanRequest, null, options.prettify ? 2 : 0);

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
      console.error('[PostmanExporter] Export error:', error);
      return {
        success: false,
        format: this.format,
        errors: [
          error instanceof Error ? error.message : 'Failed to export request',
        ],
      };
    }
  }

  /**
   * Export multiple requests to Postman format
   */
  async exportRequests(
    requests: Request[],
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    try {
      // Create a collection containing all requests
      const collection = {
        info: {
          name: 'Exported Requests',
          schema:
            'https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
        },
        item: requests.map((req) => this.convertRequest(req)),
      };

      const data = JSON.stringify(collection, null, options.prettify ? 2 : 0);

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
      console.error('[PostmanExporter] Export error:', error);
      return {
        success: false,
        format: this.format,
        errors: [
          error instanceof Error ? error.message : 'Failed to export requests',
        ],
      };
    }
  }

  /**
   * Convert LocalAPI Collection to Postman Collection
   */
  private convertCollection(collection: Collection): any {
    return {
      info: {
        _postman_id: collection.id,
        name: collection.name,
        description: collection.description || '',
        schema:
          'https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
      },
      item: collection.requests.map((req) => this.convertRequest(req)),
    };
  }

  /**
   * Convert LocalAPI Request to Postman Request
   */
  private convertRequest(request: Request): any {
    return {
      name: request.name,
      request: {
        method: request.method,
        header: request.headers.map((h) => ({
          key: h.key,
          value: h.value,
          disabled: !h.enabled,
        })),
        url: {
          raw: this.buildUrl(request),
          protocol: new URL(request.url).protocol.replace(':', ''),
          host: new URL(request.url).hostname.split('.'),
          port: new URL(request.url).port || undefined,
          path: new URL(request.url).pathname.split('/').filter(Boolean),
          query: request.queryParams.map((q) => ({
            key: q.key,
            value: q.value,
            disabled: !q.enabled,
          })),
        },
        body: this.convertBody(request.body),
        description: request.description || '',
      },
    };
  }

  /**
   * Build full URL with query params
   */
  private buildUrl(request: Request): string {
    const url = new URL(request.url);
    const enabledParams = request.queryParams.filter((q) => q.enabled);

    enabledParams.forEach((param) => {
      url.searchParams.append(param.key, param.value);
    });

    return url.toString();
  }

  /**
   * Convert request body to Postman format
   */
  private convertBody(body?: any): any {
    if (!body) {
      return undefined;
    }

    switch (body.type) {
      case 'raw':
      case 'json':
      case 'xml':
        return {
          mode: 'raw',
          raw: body.content,
        };

      case 'x-www-form-urlencoded':
        return {
          mode: 'urlencoded',
          urlencoded: this.parseUrlEncoded(body.content),
        };

      case 'form-data':
        return {
          mode: 'formdata',
          formdata: this.parseFormData(body.content),
        };

      case 'graphql':
        return {
          mode: 'graphql',
          graphql: JSON.parse(body.content || '{}'),
        };

      default:
        return {
          mode: 'raw',
          raw: body.content,
        };
    }
  }

  /**
   * Parse URL-encoded body
   */
  private parseUrlEncoded(content: string): any[] {
    try {
      const parsed = JSON.parse(content);
      if (Array.isArray(parsed)) {
        return parsed.map((item) => ({
          key: item.key,
          value: item.value,
          disabled: item.disabled || false,
        }));
      }
    } catch {
      // If not JSON, try to parse as URL params
      const params = new URLSearchParams(content);
      const result: any[] = [];
      params.forEach((value, key) => {
        result.push({ key, value, disabled: false });
      });
      return result;
    }
    return [];
  }

  /**
   * Parse form data body
   */
  private parseFormData(content: string): any[] {
    try {
      const parsed = JSON.parse(content);
      if (Array.isArray(parsed)) {
        return parsed.map((item) => ({
          key: item.key,
          value: item.value,
          type: item.type || 'text',
          disabled: item.disabled || false,
        }));
      }
    } catch {
      // Return empty array if parsing fails
    }
    return [];
  }
}
