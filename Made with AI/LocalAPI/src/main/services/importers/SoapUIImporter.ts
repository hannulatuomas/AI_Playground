// SoapUI XML Project Importer
import type {
  Importer,
  ImportExportFormat,
  ImportExportOptions,
  ImportResult,
} from '../../../types/import-export';
import type { Collection, Request, HttpMethod, RequestBody } from '../../../types/models';

/**
 * SoapUI XML Project Importer
 */
export class SoapUIImporter implements Importer {
  readonly format: ImportExportFormat = 'soapui';
  readonly name = 'SoapUI Project';
  readonly description = 'Import SoapUI XML project files';
  readonly fileExtensions = ['.xml'];

  canImport(content: string): boolean {
    return content.includes('<soapui:') || content.includes('soapui-project');
  }

  async import(
    content: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const xml2js = await import('xml2js');
      const parser = new xml2js.Parser();
      const result = await parser.parseStringPromise(content);

      const project = result['con:soapui-project'] || result['soapui-project'];
      if (!project) {
        throw new Error('Invalid SoapUI project format');
      }

      const collection: Collection = {
        id: `col-${Date.now()}`,
        name: project.$?.name || 'SoapUI Project',
        description: project.$?.description || '',
        requests: [],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const requests: Request[] = [];

      // Process REST interfaces
      if (project['con:interface']) {
        for (const iface of project['con:interface']) {
          if (iface.$?.type === 'rest') {
            this.processRestInterface(iface, collection.id, requests);
          }
        }
      }

      // Process SOAP interfaces
      if (project['con:interface']) {
        for (const iface of project['con:interface']) {
          if (iface.$?.type === 'wsdl' || !iface.$?.type) {
            this.processSoapInterface(iface, collection.id, requests);
          }
        }
      }

      console.log(`[SoapUIImporter] Imported ${requests.length} requests`);

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
      console.error('[SoapUIImporter] Import error:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to import SoapUI project',
        ],
      };
    }
  }

  private processRestInterface(iface: any, collectionId: string, requests: Request[]): void {
    const resources = iface['con:resource'] || [];
    for (const resource of resources) {
      const methods = resource['con:method'] || [];
      for (const method of methods) {
        const request = this.createRestRequest(method, resource, collectionId);
        if (request) requests.push(request);
      }
    }
  }

  private processSoapInterface(iface: any, collectionId: string, requests: Request[]): void {
    const operations = iface['con:operation'] || [];
    for (const operation of operations) {
      const request = this.createSoapRequest(operation, iface, collectionId);
      if (request) requests.push(request);
    }
  }

  private createRestRequest(method: any, resource: any, collectionId: string): Request | null {
    try {
      const methodName = method.$?.method || 'GET';
      const path = resource.$?.path || '/';
      const endpoint = resource.$?.endpoint || 'https://api.example.com';

      const request: Request = {
        id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: method.$?.name || `${methodName} ${path}`,
        description: '',
        protocol: 'REST' as const,
        method: methodName.toUpperCase() as HttpMethod,
        url: endpoint + path,
        headers: [],
        queryParams: [],
        collectionId,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      return request;
    } catch (error) {
      return null;
    }
  }

  private createSoapRequest(operation: any, iface: any, collectionId: string): Request | null {
    try {
      const body: RequestBody = {
        type: 'xml' as const,
        content: operation['con:request']?.[0]?.['con:request']?.[0] || '<soap:Envelope></soap:Envelope>',
      };

      const request: Request = {
        id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: operation.$?.name || 'SOAP Request',
        description: '',
        protocol: 'SOAP' as const,
        method: 'POST' as const,
        url: iface.$?.endpoint || 'https://api.example.com/soap',
        headers: [
          { key: 'Content-Type', value: 'text/xml', enabled: true },
          { key: 'SOAPAction', value: operation.$?.action || '', enabled: true },
        ],
        queryParams: [],
        body,
        collectionId,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      return request;
    } catch (error) {
      return null;
    }
  }

  getExample(): string {
    return `<?xml version="1.0" encoding="UTF-8"?>
<soapui-project name="Example">
  <con:interface type="rest" name="API">
    <con:resource path="/users">
      <con:method name="Get Users" method="GET"/>
    </con:resource>
  </con:interface>
</soapui-project>`;
  }
}
