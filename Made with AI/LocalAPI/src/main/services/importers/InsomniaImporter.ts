// Insomnia Importer
import type {
  Importer,
  ImportExportFormat,
  ImportExportOptions,
  ImportResult,
} from '../../../types/import-export';
import type { Collection, Request, Environment, Variable, HttpMethod, RequestBody } from '../../../types/models';

/**
 * Insomnia v4/v5 Importer
 * Supports Insomnia export format
 */
export class InsomniaImporter implements Importer {
  readonly format: ImportExportFormat = 'insomnia-v4';
  readonly name = 'Insomnia';
  readonly description = 'Import Insomnia v4/v5 collections';
  readonly fileExtensions = ['.json', '.yaml'];

  /**
   * Check if content can be imported
   */
  canImport(content: string): boolean {
    try {
      const json = JSON.parse(content);
      return !!(json._type && json._type.startsWith('export'));
    } catch {
      return false;
    }
  }

  /**
   * Import Insomnia export
   */
  async import(
    content: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const insomniaExport = JSON.parse(content);
      const resources = insomniaExport.resources || [];

      const collections: Collection[] = [];
      const requests: Request[] = [];
      const environments: Environment[] = [];
      const variables: Variable[] = [];

      // Group resources by type
      const workspaces = resources.filter((r: any) => r._type === 'workspace');
      const requestGroups = resources.filter((r: any) => r._type === 'request_group');
      const requestResources = resources.filter((r: any) => r._type === 'request');
      const envResources = resources.filter((r: any) => r._type === 'environment');

      // Create collections from workspaces and request groups
      for (const workspace of workspaces) {
        const collection: Collection = {
          id: workspace._id,
          name: workspace.name,
          description: workspace.description || '',
          requests: [],
          folders: [],
          createdAt: new Date(),
          updatedAt: new Date(),
        };
        collections.push(collection);
      }

      // If no workspaces, create a default collection
      if (collections.length === 0) {
        collections.push({
          id: `col-${Date.now()}`,
          name: 'Imported Collection',
          description: 'Imported from Insomnia',
          requests: [],
          folders: [],
          createdAt: new Date(),
          updatedAt: new Date(),
        });
      }

      // Convert requests
      for (const insomniaReq of requestResources) {
        const request = this.convertRequest(insomniaReq, collections[0].id);
        if (request) {
          requests.push(request);
        }
      }

      // Convert environments
      for (const env of envResources) {
        if (env.data) {
          const environment: Environment = {
            id: env._id,
            name: env.name,
            variables: Object.entries(env.data).map(([key, value]) => ({
              key,
              value: value as any,
              type: 'string' as const,
              scope: 'environment' as const,
              enabled: true,
            })),
            isActive: false,
            createdAt: new Date(),
            updatedAt: new Date(),
          };
          environments.push(environment);
        }
      }

      console.log(
        `[InsomniaImporter] Imported ${collections.length} collections, ${requests.length} requests, ${environments.length} environments`
      );

      return {
        success: true,
        collections,
        requests,
        environments,
        variables,
        metadata: {
          format: this.format,
          itemCount: collections.length + requests.length,
          importedAt: new Date(),
        },
      };
    } catch (error) {
      console.error('[InsomniaImporter] Import error:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to import Insomnia export',
        ],
      };
    }
  }

  /**
   * Convert Insomnia request to LocalAPI request
   */
  private convertRequest(insomniaReq: any, collectionId: string): Request | null {
    try {
      const method = insomniaReq.method?.toUpperCase() as HttpMethod;
      const url = insomniaReq.url;

      if (!method || !url) return null;

      // Extract headers
      const headers = (insomniaReq.headers || []).map((h: any) => ({
        key: h.name,
        value: h.value,
        enabled: !h.disabled,
      }));

      // Extract query params
      const queryParams = (insomniaReq.parameters || []).map((p: any) => ({
        key: p.name,
        value: p.value,
        enabled: !p.disabled,
      }));

      // Extract body
      let body: RequestBody | undefined;
      if (insomniaReq.body) {
        const bodyObj = insomniaReq.body;
        switch (bodyObj.mimeType) {
          case 'application/json':
            body = {
              type: 'raw' as const,
              content: bodyObj.text || '',
            };
            break;
          case 'application/x-www-form-urlencoded':
            body = {
              type: 'x-www-form-urlencoded' as const,
              content: JSON.stringify(bodyObj.params || []),
            };
            break;
          case 'multipart/form-data':
            body = {
              type: 'form-data' as const,
              content: JSON.stringify(bodyObj.params || []),
            };
            break;
          case 'application/graphql':
            body = {
              type: 'graphql' as const,
              content: bodyObj.text || '',
            };
            break;
          default:
            body = {
              type: 'raw' as const,
              content: bodyObj.text || '',
            };
        }
      }

      // Create request
      const request: Request = {
        id: insomniaReq._id,
        name: insomniaReq.name,
        description: insomniaReq.description || '',
        protocol: 'REST' as const,
        method,
        url,
        headers,
        queryParams,
        body,
        collectionId,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      return request;
    } catch (error) {
      console.error('[InsomniaImporter] Error converting request:', error);
      return null;
    }
  }

  /**
   * Get example Insomnia export
   */
  getExample(): string {
    return JSON.stringify(
      {
        _type: 'export',
        __export_format: 4,
        __export_date: '2024-01-01T00:00:00.000Z',
        __export_source: 'insomnia.desktop.app:v2023.1.0',
        resources: [
          {
            _id: 'wrk_1',
            _type: 'workspace',
            name: 'Example Workspace',
            description: '',
          },
          {
            _id: 'req_1',
            _type: 'request',
            parentId: 'wrk_1',
            name: 'Get Users',
            method: 'GET',
            url: 'https://api.example.com/users',
            headers: [],
            parameters: [],
          },
        ],
      },
      null,
      2
    );
  }
}
