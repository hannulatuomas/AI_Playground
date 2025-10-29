// WADL (Web Application Description Language) Importer
import type {
  Importer,
  ImportExportFormat,
  ImportExportOptions,
  ImportResult,
} from '../../../types/import-export';
import type { Collection, Request, HttpMethod, RequestBody } from '../../../types/models';

/**
 * WADL Importer
 */
export class WADLImporter implements Importer {
  readonly format: ImportExportFormat = 'wadl';
  readonly name = 'WADL';
  readonly description = 'Import WADL (Web Application Description Language)';
  readonly fileExtensions = ['.wadl', '.xml'];

  canImport(content: string): boolean {
    return content.includes('<application') && content.includes('wadl');
  }

  async import(
    content: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const xml2js = await import('xml2js');
      const parser = new xml2js.Parser();
      const result = await parser.parseStringPromise(content);

      const application = result.application;
      if (!application) {
        throw new Error('Invalid WADL format');
      }

      const collection: Collection = {
        id: `col-${Date.now()}`,
        name: 'WADL API',
        description: application.doc?.[0] || '',
        requests: [],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const requests: Request[] = [];
      const baseUrl = this.extractBaseUrl(application);

      // Process resources
      if (application.resources) {
        for (const resources of application.resources) {
          this.processResources(resources.resource || [], baseUrl, '', collection.id, requests);
        }
      }

      console.log(`[WADLImporter] Imported ${requests.length} requests`);

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
      console.error('[WADLImporter] Import error:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to import WADL',
        ],
      };
    }
  }

  private extractBaseUrl(application: any): string {
    if (application.resources?.[0]?.$?.base) {
      return application.resources[0].$.base;
    }
    return 'https://api.example.com';
  }

  private processResources(
    resources: any[],
    baseUrl: string,
    parentPath: string,
    collectionId: string,
    requests: Request[]
  ): void {
    for (const resource of resources) {
      const path = parentPath + (resource.$?.path || '');

      // Process methods
      if (resource.method) {
        for (const method of resource.method) {
          const request = this.createRequest(method, baseUrl + path, collectionId);
          if (request) requests.push(request);
        }
      }

      // Process nested resources
      if (resource.resource) {
        this.processResources(resource.resource, baseUrl, path, collectionId, requests);
      }
    }
  }

  private createRequest(method: any, url: string, collectionId: string): Request | null {
    try {
      const methodName = method.$?.name || method.$?.id || 'GET';
      
      const request: Request = {
        id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: method.$?.id || `${methodName} ${url}`,
        description: method.doc?.[0] || '',
        protocol: 'REST' as const,
        method: methodName.toUpperCase() as HttpMethod,
        url,
        headers: [],
        queryParams: [],
        collectionId,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      // Extract query parameters
      if (method.request?.[0]?.param) {
        for (const param of method.request[0].param) {
          if (param.$?.style === 'query') {
            request.queryParams.push({
              key: param.$?.name || '',
              value: param.$?.default || '',
              enabled: param.$?.required === 'true',
            });
          }
        }
      }

      return request;
    } catch (error) {
      return null;
    }
  }

  getExample(): string {
    return `<?xml version="1.0"?>
<application xmlns="http://wadl.dev.java.net/2009/02">
  <resources base="https://api.example.com">
    <resource path="/users">
      <method name="GET" id="getUsers">
        <doc>Get all users</doc>
      </method>
    </resource>
  </resources>
</application>`;
  }
}
