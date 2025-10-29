// AsyncAPI Importer
import type {
  Importer,
  ImportExportFormat,
  ImportExportOptions,
  ImportResult,
} from '../../../types/import-export';
import type { Collection, Request, RequestBody } from '../../../types/models';

/**
 * AsyncAPI 2.0/3.0 Importer
 * Imports AsyncAPI specifications for event-driven APIs
 */
export class AsyncAPIImporter implements Importer {
  readonly format: ImportExportFormat = 'asyncapi-2.0';
  readonly name = 'AsyncAPI';
  readonly description = 'Import AsyncAPI 2.0/3.0 specifications';
  readonly fileExtensions = ['.json', '.yaml', '.yml'];

  canImport(content: string): boolean {
    try {
      const json = JSON.parse(content);
      return !!json.asyncapi;
    } catch {
      return content.includes('asyncapi:');
    }
  }

  async import(
    content: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const spec = await this.parseContent(content);
      const version = spec.asyncapi.startsWith('3.') ? 'asyncapi-3.0' : 'asyncapi-2.0';

      const collection: Collection = {
        id: `col-${Date.now()}`,
        name: spec.info?.title || 'AsyncAPI',
        description: spec.info?.description || '',
        requests: [],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const requests: Request[] = [];

      // Process channels (AsyncAPI 2.x) or operations (AsyncAPI 3.x)
      if (version === 'asyncapi-2.0') {
        this.processChannels(spec.channels || {}, collection.id, requests);
      } else {
        this.processOperations(spec.operations || {}, collection.id, requests);
      }

      console.log(`[AsyncAPIImporter] Imported ${requests.length} operations`);

      return {
        success: true,
        collections: [collection],
        requests,
        metadata: {
          format: version as ImportExportFormat,
          itemCount: 1 + requests.length,
          importedAt: new Date(),
        },
      };
    } catch (error) {
      console.error('[AsyncAPIImporter] Import error:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to import AsyncAPI',
        ],
      };
    }
  }

  private async parseContent(content: string): Promise<any> {
    try {
      return JSON.parse(content);
    } catch {
      const yaml = await import('js-yaml');
      return yaml.load(content);
    }
  }

  private processChannels(channels: any, collectionId: string, requests: Request[]): void {
    for (const [channelName, channel] of Object.entries(channels)) {
      // Create request for publish operation
      if ((channel as any).publish) {
        requests.push(
          this.createRequest(
            channelName,
            'publish',
            (channel as any).publish,
            collectionId
          )
        );
      }

      // Create request for subscribe operation
      if ((channel as any).subscribe) {
        requests.push(
          this.createRequest(
            channelName,
            'subscribe',
            (channel as any).subscribe,
            collectionId
          )
        );
      }
    }
  }

  private processOperations(operations: any, collectionId: string, requests: Request[]): void {
    for (const [operationId, operation] of Object.entries(operations)) {
      const op = operation as any;
      requests.push(
        this.createRequest(
          op.channel || operationId,
          op.action || 'send',
          op,
          collectionId
        )
      );
    }
  }

  private createRequest(
    channel: string,
    action: string,
    operation: any,
    collectionId: string
  ): Request {
    const message = operation.message || {};
    const payload = message.payload || {};

    const body: RequestBody = {
      type: 'json' as const,
      content: JSON.stringify(this.generateExample(payload), null, 2),
    };

    return {
      id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: operation.summary || operation.operationId || `${action} ${channel}`,
      description: operation.description || '',
      protocol: 'MQTT' as const, // Default to MQTT, could be WebSocket, AMQP, etc.
      method: 'POST' as const,
      url: `mqtt://broker.example.com/${channel}`,
      headers: [
        { key: 'Content-Type', value: 'application/json', enabled: true },
      ],
      queryParams: [],
      body,
      collectionId,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  }

  private generateExample(schema: any): any {
    if (!schema) return {};

    if (schema.example) return schema.example;

    switch (schema.type) {
      case 'object':
        const obj: any = {};
        if (schema.properties) {
          for (const [key, prop] of Object.entries(schema.properties)) {
            obj[key] = this.generateExample(prop);
          }
        }
        return obj;

      case 'array':
        return [this.generateExample(schema.items || {})];

      case 'string':
        return schema.enum ? schema.enum[0] : 'string';

      case 'number':
      case 'integer':
        return 0;

      case 'boolean':
        return true;

      default:
        return null;
    }
  }

  getExample(): string {
    return JSON.stringify(
      {
        asyncapi: '2.0.0',
        info: {
          title: 'Example API',
          version: '1.0.0',
        },
        channels: {
          'user/signedup': {
            subscribe: {
              message: {
                payload: {
                  type: 'object',
                  properties: {
                    userId: { type: 'string' },
                    email: { type: 'string' },
                  },
                },
              },
            },
          },
        },
      },
      null,
      2
    );
  }
}
