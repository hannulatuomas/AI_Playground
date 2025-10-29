// AsyncAPI Exporter
import type {
  Exporter,
  ImportExportFormat,
  ImportExportOptions,
  ExportResult,
} from '../../../types/import-export';
import type { Request } from '../../../types/models';

export class AsyncAPIExporter implements Exporter {
  readonly format: ImportExportFormat = 'asyncapi-2.0';
  readonly name = 'AsyncAPI';
  readonly description = 'Export as AsyncAPI 2.0 specification';
  readonly fileExtensions = ['.json', '.yaml'];

  async exportCollections(collections: any[], options: ImportExportOptions = {}): Promise<ExportResult> {
    try {
      const channels: any = {};

      for (const collection of collections) {
        for (const request of collection.requests) {
          const channelName = new URL(request.url).pathname;
          channels[channelName] = {
            publish: {
              message: {
                payload: request.body ? JSON.parse(request.body.content) : {},
              },
            },
          };
        }
      }

      const spec = {
        asyncapi: '2.0.0',
        info: {
          title: collections[0]?.name || 'API',
          version: '1.0.0',
        },
        channels,
      };

      const data = JSON.stringify(spec, null, options.prettify ? 2 : 0);

      return {
        success: true,
        data,
        format: this.format,
        metadata: { exportedAt: new Date(), itemCount: Object.keys(channels).length, size: data.length },
      };
    } catch (error) {
      return {
        success: false,
        format: this.format,
        errors: [error instanceof Error ? error.message : 'Export failed'],
      };
    }
  }

  async exportRequest(request: Request, options: ImportExportOptions = {}): Promise<ExportResult> {
    try {
      const spec = {
        asyncapi: '2.0.0',
        info: { title: request.name, version: '1.0.0' },
        channels: {
          [new URL(request.url).pathname]: {
            publish: {
              message: {
                payload: request.body ? JSON.parse(request.body.content) : {},
              },
            },
          },
        },
      };

      const data = JSON.stringify(spec, null, options.prettify ? 2 : 0);

      return {
        success: true,
        data,
        format: this.format,
        metadata: { exportedAt: new Date(), itemCount: 1, size: data.length },
      };
    } catch (error) {
      return {
        success: false,
        format: this.format,
        errors: [error instanceof Error ? error.message : 'Export failed'],
      };
    }
  }

  async exportRequests(requests: Request[], options: ImportExportOptions = {}): Promise<ExportResult> {
    return this.exportCollections([{ name: 'API', requests }], options);
  }
}
