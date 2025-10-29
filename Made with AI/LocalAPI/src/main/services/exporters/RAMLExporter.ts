// RAML Exporter
import type { Exporter, ImportExportFormat, ImportExportOptions, ExportResult } from '../../../types/import-export';
import type { Request } from '../../../types/models';

export class RAMLExporter implements Exporter {
  readonly format: ImportExportFormat = 'raml-1.0';
  readonly name = 'RAML';
  readonly description = 'Export as RAML 1.0 specification';
  readonly fileExtensions = ['.raml'];

  async exportCollections(collections: any[], options: ImportExportOptions = {}): Promise<ExportResult> {
    try {
      const paths: Record<string, any> = {};
      
      for (const collection of collections) {
        for (const request of collection.requests) {
          const path = new URL(request.url).pathname;
          if (!paths[path]) paths[path] = {};
          paths[path][request.method.toLowerCase()] = {
            displayName: request.name,
            description: request.description || '',
          };
        }
      }

      let raml = `#%RAML 1.0\ntitle: ${collections[0]?.name || 'Exported API'}\nversion: v1\nbaseUri: https://api.example.com\n\n`;
      
      for (const [path, methods] of Object.entries(paths)) {
        raml += `${path}:\n`;
        for (const [method, details] of Object.entries(methods)) {
          const d = details as any;
          raml += `  ${method}:\n`;
          raml += `    displayName: ${d.displayName}\n`;
          if (d.description) raml += `    description: ${d.description}\n`;
        }
      }

      return { success: true, data: raml, format: this.format, metadata: { exportedAt: new Date(), itemCount: Object.keys(paths).length, size: raml.length } };
    } catch (error) {
      return { success: false, format: this.format, errors: [error instanceof Error ? error.message : 'Export failed'] };
    }
  }

  async exportRequest(request: Request, options: ImportExportOptions = {}): Promise<ExportResult> {
    return this.exportRequests([request], options);
  }

  async exportRequests(requests: Request[], options: ImportExportOptions = {}): Promise<ExportResult> {
    return this.exportCollections([{ name: 'API', requests }], options);
  }
}
