// cURL Command Exporter
import type {
  Exporter,
  ImportExportFormat,
  ImportExportOptions,
  ExportResult,
} from '../../../types/import-export';
import type { Request } from '../../../types/models';

/**
 * cURL Command Exporter
 * Generates bash-compatible cURL commands
 */
export class CurlExporter implements Exporter {
  readonly format: ImportExportFormat = 'curl';
  readonly name = 'cURL Command';
  readonly description = 'Export as cURL commands';
  readonly fileExtensions = ['.sh', '.txt'];

  /**
   * Export collections to cURL format
   */
  async exportCollections(
    collections: any[],
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    try {
      const commands: string[] = [];

      for (const collection of collections) {
        commands.push(`# Collection: ${collection.name}`);
        if (collection.description) {
          commands.push(`# ${collection.description}`);
        }
        commands.push('');

        for (const request of collection.requests) {
          const curlCommand = this.generateCurlCommand(request);
          commands.push(`# ${request.name}`);
          commands.push(curlCommand);
          commands.push('');
        }
      }

      const data = commands.join('\n');

      console.log(
        `[CurlExporter] Exported ${collections.length} collections as cURL commands`
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
      console.error('[CurlExporter] Export error:', error);
      return {
        success: false,
        format: this.format,
        errors: [
          error instanceof Error
            ? error.message
            : 'Failed to export as cURL',
        ],
      };
    }
  }

  /**
   * Export a single request to cURL format
   */
  async exportRequest(
    request: Request,
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    try {
      const data = this.generateCurlCommand(request);

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
      console.error('[CurlExporter] Export error:', error);
      return {
        success: false,
        format: this.format,
        errors: [
          error instanceof Error ? error.message : 'Failed to export as cURL',
        ],
      };
    }
  }

  /**
   * Export multiple requests to cURL format
   */
  async exportRequests(
    requests: Request[],
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    try {
      const commands: string[] = [];

      for (const request of requests) {
        commands.push(`# ${request.name}`);
        if (request.description) {
          commands.push(`# ${request.description}`);
        }
        commands.push(this.generateCurlCommand(request));
        commands.push('');
      }

      const data = commands.join('\n');

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
      console.error('[CurlExporter] Export error:', error);
      return {
        success: false,
        format: this.format,
        errors: [
          error instanceof Error ? error.message : 'Failed to export as cURL',
        ],
      };
    }
  }

  /**
   * Generate cURL command for a request
   */
  private generateCurlCommand(request: Request): string {
    const parts: string[] = ['curl'];

    // Add method if not GET
    if (request.method !== 'GET') {
      parts.push(`-X ${request.method}`);
    }

    // Build URL with query params
    const url = this.buildUrl(request);
    parts.push(`'${url}'`);

    // Add headers
    const enabledHeaders = request.headers.filter((h) => h.enabled);
    for (const header of enabledHeaders) {
      parts.push(`-H '${header.key}: ${this.escapeValue(header.value)}'`);
    }

    // Add body
    if (request.body && request.body.content) {
      switch (request.body.type) {
        case 'raw':
        case 'json':
        case 'xml':
          parts.push(`-d '${this.escapeValue(request.body.content)}'`);
          break;

        case 'x-www-form-urlencoded':
          parts.push(`--data-urlencode '${this.escapeValue(request.body.content)}'`);
          break;

        case 'form-data':
          // For form data, add multiple -F flags
          try {
            const formData = JSON.parse(request.body.content);
            if (Array.isArray(formData)) {
              for (const item of formData) {
                parts.push(`-F '${item.key}=${this.escapeValue(item.value)}'`);
              }
            }
          } catch {
            parts.push(`-d '${this.escapeValue(request.body.content)}'`);
          }
          break;

        default:
          parts.push(`-d '${this.escapeValue(request.body.content)}'`);
      }
    }

    // Join with line continuation for readability
    return parts.join(' \\\n  ');
  }

  /**
   * Build URL with query parameters
   */
  private buildUrl(request: Request): string {
    const url = new URL(request.url);
    const enabledParams = request.queryParams.filter((q) => q.enabled);

    // Clear existing params and add enabled ones
    url.search = '';
    enabledParams.forEach((param) => {
      url.searchParams.append(param.key, param.value);
    });

    return url.toString();
  }

  /**
   * Escape special characters in values
   */
  private escapeValue(value: string): string {
    return value
      .replace(/\\/g, '\\\\')
      .replace(/'/g, "\\'")
      .replace(/\n/g, '\\n')
      .replace(/\r/g, '\\r')
      .replace(/\t/g, '\\t');
  }
}
