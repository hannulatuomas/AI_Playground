// SoapUI XML Project Exporter
import type { Exporter, ImportExportFormat, ImportExportOptions, ExportResult } from '../../../types/import-export';
import type { Request } from '../../../types/models';

export class SoapUIExporter implements Exporter {
  readonly format: ImportExportFormat = 'soapui';
  readonly name = 'SoapUI Project';
  readonly description = 'Export as SoapUI XML project';
  readonly fileExtensions = ['.xml'];

  async exportCollections(collections: any[], options: ImportExportOptions = {}): Promise<ExportResult> {
    try {
      const interfaces: string[] = [];
      
      for (const collection of collections) {
        interfaces.push(`  <con:interface type="rest" name="${this.escapeXml(collection.name)}">`);
        for (const request of collection.requests) {
          const path = new URL(request.url).pathname;
          interfaces.push(`    <con:resource path="${this.escapeXml(path)}">`);
          interfaces.push(`      <con:method name="${this.escapeXml(request.name)}" method="${request.method}"/>`);
          interfaces.push(`    </con:resource>`);
        }
        interfaces.push(`  </con:interface>`);
      }

      const xml = `<?xml version="1.0" encoding="UTF-8"?>
<con:soapui-project name="Exported Project" xmlns:con="http://eviware.com/soapui/config">
${interfaces.join('\n')}
</con:soapui-project>`;

      return { success: true, data: xml, format: this.format, metadata: { exportedAt: new Date(), itemCount: collections.length, size: xml.length } };
    } catch (error) {
      return { success: false, format: this.format, errors: [error instanceof Error ? error.message : 'Export failed'] };
    }
  }

  async exportRequest(request: Request, options: ImportExportOptions = {}): Promise<ExportResult> {
    return this.exportRequests([request], options);
  }

  async exportRequests(requests: Request[], options: ImportExportOptions = {}): Promise<ExportResult> {
    return this.exportCollections([{ name: 'Exported', requests }], options);
  }

  private escapeXml(str: string): string {
    return str.replace(/[<>&'"]/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;' }[c] || c));
  }
}
