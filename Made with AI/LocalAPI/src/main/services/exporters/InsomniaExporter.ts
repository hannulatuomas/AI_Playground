// Insomnia Exporter
import type {
  Exporter,
  ImportExportFormat,
  ImportExportOptions,
  ExportResult,
} from '../../../types/import-export';
import type { Collection, Request } from '../../../types/models';

export class InsomniaExporter implements Exporter {
  readonly format: ImportExportFormat = 'insomnia-v4';
  readonly name = 'Insomnia';
  readonly description = 'Export to Insomnia v4 format';
  readonly fileExtensions = ['.json'];

  async exportCollections(collections: Collection[], options: ImportExportOptions = {}): Promise<ExportResult> {
    try {
      const resources: any[] = [];
      
      for (const collection of collections) {
        resources.push({
          _id: collection.id,
          _type: 'workspace',
          name: collection.name,
          description: collection.description || '',
        });

        for (const request of collection.requests) {
          resources.push(this.convertRequest(request, collection.id));
        }
      }

      const insomniaExport = {
        _type: 'export',
        __export_format: 4,
        __export_date: new Date().toISOString(),
        __export_source: 'localapi',
        resources,
      };

      const data = JSON.stringify(insomniaExport, null, options.prettify ? 2 : 0);

      return {
        success: true,
        data,
        format: this.format,
        metadata: { exportedAt: new Date(), itemCount: collections.length, size: data.length },
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
      const resource = this.convertRequest(request, 'wrk_default');
      const data = JSON.stringify(resource, null, options.prettify ? 2 : 0);

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
      const resources = requests.map(req => this.convertRequest(req, 'wrk_default'));
      const data = JSON.stringify({ _type: 'export', __export_format: 4, resources }, null, options.prettify ? 2 : 0);

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

  private convertRequest(request: Request, workspaceId: string): any {
    return {
      _id: request.id,
      _type: 'request',
      parentId: workspaceId,
      name: request.name,
      method: request.method,
      url: request.url,
      headers: request.headers.map(h => ({ name: h.key, value: h.value, disabled: !h.enabled })),
      parameters: request.queryParams.map(q => ({ name: q.key, value: q.value, disabled: !q.enabled })),
      body: request.body ? {
        mimeType: request.body.type === 'json' ? 'application/json' : 'text/plain',
        text: request.body.content,
      } : undefined,
    };
  }
}
