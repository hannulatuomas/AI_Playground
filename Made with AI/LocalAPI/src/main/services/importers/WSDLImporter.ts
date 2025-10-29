// WSDL (Web Services Description Language) Importer
import type {
  Importer,
  ImportExportFormat,
  ImportExportOptions,
  ImportResult,
} from '../../../types/import-export';
import type { Collection, Request, RequestBody } from '../../../types/models';

/**
 * WSDL 1.0/1.1/2.0 Importer
 */
export class WSDLImporter implements Importer {
  readonly format: ImportExportFormat = 'wsdl-1.1';
  readonly name = 'WSDL';
  readonly description = 'Import WSDL 1.0/1.1/2.0 specifications';
  readonly fileExtensions = ['.wsdl', '.xml'];

  canImport(content: string): boolean {
    return (content.includes('<definitions') || content.includes('<wsdl:definitions')) && 
           (content.includes('wsdl') || content.includes('xmlns:wsdl'));
  }

  async import(
    content: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const xml2js = await import('xml2js');
      const parser = new xml2js.Parser();
      const result = await parser.parseStringPromise(content);

      const definitions = result.definitions || result['wsdl:definitions'];
      if (!definitions) {
        throw new Error('Invalid WSDL format');
      }

      const collection: Collection = {
        id: `col-${Date.now()}`,
        name: definitions.$?.name || 'WSDL Service',
        description: definitions['wsdl:documentation']?.[0] || definitions.documentation?.[0] || '',
        requests: [],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const requests: Request[] = [];
      const endpoint = this.extractEndpoint(definitions);

      // Process port types and operations
      const portTypes = definitions['wsdl:portType'] || definitions.portType || [];
      for (const portType of portTypes) {
        const operations = portType['wsdl:operation'] || portType.operation || [];
        for (const operation of operations) {
          const request = this.createRequest(operation, endpoint, collection.id);
          if (request) requests.push(request);
        }
      }

      console.log(`[WSDLImporter] Imported ${requests.length} SOAP operations`);

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
      console.error('[WSDLImporter] Import error:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to import WSDL',
        ],
      };
    }
  }

  private extractEndpoint(definitions: any): string {
    const services = definitions['wsdl:service'] || definitions.service || [];
    for (const service of services) {
      const ports = service['wsdl:port'] || service.port || [];
      for (const port of ports) {
        const address = port['soap:address'] || port['soap12:address'] || port.address;
        if (address?.[0]?.$?.location) {
          return address[0].$.location;
        }
      }
    }
    return 'https://api.example.com/soap';
  }

  private createRequest(operation: any, endpoint: string, collectionId: string): Request | null {
    try {
      const operationName = operation.$?.name || 'Operation';
      const documentation = operation['wsdl:documentation']?.[0] || operation.documentation?.[0] || '';

      // Generate basic SOAP envelope
      const soapEnvelope = `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header/>
  <soap:Body>
    <${operationName}/>
  </soap:Body>
</soap:Envelope>`;

      const body: RequestBody = {
        type: 'xml' as const,
        content: soapEnvelope,
      };

      const request: Request = {
        id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: operationName,
        description: documentation,
        protocol: 'SOAP' as const,
        method: 'POST' as const,
        url: endpoint,
        headers: [
          { key: 'Content-Type', value: 'text/xml; charset=utf-8', enabled: true },
          { key: 'SOAPAction', value: `"${operationName}"`, enabled: true },
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
    return `<?xml version="1.0"?>
<definitions name="ExampleService"
  xmlns="http://schemas.xmlsoap.org/wsdl/"
  xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/">
  <portType name="ExamplePortType">
    <operation name="GetUser">
      <documentation>Get user by ID</documentation>
    </operation>
  </portType>
  <service name="ExampleService">
    <port>
      <soap:address location="https://api.example.com/soap"/>
    </port>
  </service>
</definitions>`;
  }
}
