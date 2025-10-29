// HAR (HTTP Archive) Exporter
import type {
  Exporter,
  ImportExportFormat,
  ImportExportOptions,
  ExportResult,
} from '../../../types/import-export';
import type { Request } from '../../../types/models';

export class HARExporter implements Exporter {
  readonly format: ImportExportFormat = 'har';
  readonly name = 'HAR';
  readonly description = 'Export to HAR (HTTP Archive) format';
  readonly fileExtensions = ['.har'];

  async exportCollections(collections: any[], options: ImportExportOptions = {}): Promise<ExportResult> {
    try {
      const entries: any[] = [];
      
      for (const collection of collections) {
        for (const request of collection.requests) {
          entries.push(this.convertRequest(request));
        }
      }

      const har = {
        log: {
          version: '1.2',
          creator: { name: 'LocalAPI', version: '1.0.0' },
          entries,
        },
      };

      const data = JSON.stringify(har, null, options.prettify ? 2 : 0);

      return {
        success: true,
        data,
        format: this.format,
        metadata: { exportedAt: new Date(), itemCount: entries.length, size: data.length },
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
      const entry = this.convertRequest(request);
      const har = {
        log: {
          version: '1.2',
          creator: { name: 'LocalAPI', version: '1.0.0' },
          entries: [entry],
        },
      };

      const data = JSON.stringify(har, null, options.prettify ? 2 : 0);

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
    try {
      const entries = requests.map(req => this.convertRequest(req));
      const har = {
        log: {
          version: '1.2',
          creator: { name: 'LocalAPI', version: '1.0.0' },
          entries,
        },
      };

      const data = JSON.stringify(har, null, options.prettify ? 2 : 0);

      return {
        success: true,
        data,
        format: this.format,
        metadata: { exportedAt: new Date(), itemCount: requests.length, size: data.length },
      };
    } catch (error) {
      return {
        success: false,
        format: this.format,
        errors: [error instanceof Error ? error.message : 'Export failed'],
      };
    }
  }

  private convertRequest(request: Request): any {
    return {
      startedDateTime: new Date().toISOString(),
      time: 0,
      request: {
        method: request.method,
        url: request.url,
        httpVersion: 'HTTP/1.1',
        headers: request.headers.map(h => ({ name: h.key, value: h.value })),
        queryString: request.queryParams.map(q => ({ name: q.key, value: q.value })),
        postData: request.body ? {
          mimeType: request.body.type === 'json' ? 'application/json' : 'text/plain',
          text: request.body.content,
        } : undefined,
        headersSize: -1,
        bodySize: request.body?.content.length || 0,
      },
      response: {
        status: 0,
        statusText: '',
        httpVersion: 'HTTP/1.1',
        headers: [],
        content: { size: 0, mimeType: 'text/plain' },
        redirectURL: '',
        headersSize: -1,
        bodySize: -1,
      },
      cache: {},
      timings: { send: 0, wait: 0, receive: 0 },
    };
  }
}
