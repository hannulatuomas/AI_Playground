// Protobuf (.proto) Importer
import type {
  Importer,
  ImportExportFormat,
  ImportExportOptions,
  ImportResult,
} from '../../../types/import-export';
import type { Collection, Request, RequestBody } from '../../../types/models';

/**
 * Protobuf 2/3 Importer
 * Imports .proto files and generates gRPC requests
 */
export class ProtobufImporter implements Importer {
  readonly format: ImportExportFormat = 'protobuf-3';
  readonly name = 'Protobuf';
  readonly description = 'Import Protobuf 2/3 (.proto files)';
  readonly fileExtensions = ['.proto'];

  canImport(content: string): boolean {
    return content.includes('syntax = "proto') || content.includes('service ') && content.includes('rpc ');
  }

  async import(
    content: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const collection: Collection = {
        id: `col-${Date.now()}`,
        name: this.extractPackageName(content) || 'Protobuf API',
        description: 'Imported from Protobuf definition',
        requests: [],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const requests: Request[] = [];

      // Extract services and RPCs
      const services = this.extractServices(content);
      for (const service of services) {
        for (const rpc of service.rpcs) {
          const request = this.createRequest(service.name, rpc, collection.id);
          requests.push(request);
        }
      }

      console.log(`[ProtobufImporter] Imported ${requests.length} gRPC methods`);

      return {
        success: true,
        collections: [collection],
        requests,
        metadata: {
          format: this.format,
          itemCount: 1 + requests.length,
          importedAt: new Date(),
        },
      };
    } catch (error) {
      console.error('[ProtobufImporter] Import error:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to import Protobuf',
        ],
      };
    }
  }

  private extractPackageName(content: string): string | null {
    const match = content.match(/package\s+([a-zA-Z0-9_.]+);/);
    return match ? match[1] : null;
  }

  private extractServices(content: string): Array<{ name: string; rpcs: Array<{ name: string; request: string; response: string }> }> {
    const services: Array<{ name: string; rpcs: Array<{ name: string; request: string; response: string }> }> = [];
    
    // Match service blocks
    const serviceRegex = /service\s+(\w+)\s*\{([^}]+)\}/g;
    let serviceMatch;

    while ((serviceMatch = serviceRegex.exec(content)) !== null) {
      const serviceName = serviceMatch[1];
      const serviceBody = serviceMatch[2];

      const rpcs: Array<{ name: string; request: string; response: string }> = [];

      // Match RPC methods
      const rpcRegex = /rpc\s+(\w+)\s*\(([^)]+)\)\s*returns\s*\(([^)]+)\)/g;
      let rpcMatch;

      while ((rpcMatch = rpcRegex.exec(serviceBody)) !== null) {
        rpcs.push({
          name: rpcMatch[1],
          request: rpcMatch[2].trim(),
          response: rpcMatch[3].trim(),
        });
      }

      services.push({ name: serviceName, rpcs });
    }

    return services;
  }

  private createRequest(
    serviceName: string,
    rpc: { name: string; request: string; response: string },
    collectionId: string
  ): Request {
    const body: RequestBody = {
      type: 'json' as const,
      content: JSON.stringify({
        // Placeholder for gRPC request
        message: rpc.request,
      }, null, 2),
    };

    return {
      id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: `${serviceName}.${rpc.name}`,
      description: `gRPC method: ${rpc.request} → ${rpc.response}`,
      protocol: 'gRPC' as const,
      method: 'POST' as const,
      url: `grpc://localhost:50051/${serviceName}/${rpc.name}`,
      headers: [
        { key: 'Content-Type', value: 'application/grpc', enabled: true },
      ],
      queryParams: [],
      body,
      collectionId,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  }

  getExample(): string {
    return `syntax = "proto3";

package example;

service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
  rpc ListUsers (Empty) returns (UserList);
}

message UserRequest {
  string id = 1;
}

message UserResponse {
  string id = 1;
  string name = 2;
}`;
  }
}
