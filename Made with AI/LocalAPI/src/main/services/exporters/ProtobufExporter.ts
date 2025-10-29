// Protobuf Exporter
import type { Exporter, ImportExportFormat, ImportExportOptions, ExportResult } from '../../../types/import-export';
import type { Request } from '../../../types/models';

export class ProtobufExporter implements Exporter {
  readonly format: ImportExportFormat = 'protobuf-3';
  readonly name = 'Protobuf';
  readonly description = 'Export as Protobuf .proto file';
  readonly fileExtensions = ['.proto'];

  async exportCollections(collections: any[], options: ImportExportOptions = {}): Promise<ExportResult> {
    try {
      const rpcs: string[] = [];
      
      for (const collection of collections) {
        for (const request of collection.requests) {
          const methodName = request.name.replace(/[^a-zA-Z0-9]/g, '');
          rpcs.push(`  rpc ${methodName} (${methodName}Request) returns (${methodName}Response);`);
        }
      }

      const proto = `syntax = "proto3";

package api;

service APIService {
${rpcs.join('\n')}
}

message Empty {}
`;

      return { success: true, data: proto, format: this.format, metadata: { exportedAt: new Date(), itemCount: rpcs.length, size: proto.length } };
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
