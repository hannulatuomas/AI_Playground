// API Gateway Importer (AWS & Azure)
import type {
  Importer,
  ImportExportFormat,
  ImportExportOptions,
  ImportResult,
} from '../../../types/import-export';
import type { Collection, Request, HttpMethod, RequestBody } from '../../../types/models';

/**
 * API Gateway Importer
 * Supports AWS API Gateway and Azure API Management exports
 */
export class APIGatewayImporter implements Importer {
  readonly format: ImportExportFormat = 'aws-gateway';
  readonly name = 'API Gateway';
  readonly description = 'Import AWS/Azure API Gateway exports';
  readonly fileExtensions = ['.json', '.xml'];

  canImport(content: string): boolean {
    try {
      const json = JSON.parse(content);
      // AWS API Gateway
      if (json.swagger || json.openapi) {
        return json['x-amazon-apigateway-integration'] !== undefined ||
               json.info?.['x-amazon-apigateway-integration'] !== undefined;
      }
      // Azure APIM
      if (json.apiVersion && json.type === 'Microsoft.ApiManagement/service/apis') {
        return true;
      }
    } catch {
      // Try XML for Azure
      return content.includes('Microsoft.ApiManagement') || 
             content.includes('x-amazon-apigateway');
    }
    return false;
  }

  async import(
    content: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const json = JSON.parse(content);

      // Detect gateway type
      if (this.isAWSGateway(json)) {
        return this.importAWSGateway(json);
      } else if (this.isAzureAPIM(json)) {
        return this.importAzureAPIM(json);
      }

      throw new Error('Unknown API Gateway format');
    } catch (error) {
      console.error('[APIGatewayImporter] Import error:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to import API Gateway',
        ],
      };
    }
  }

  private isAWSGateway(json: any): boolean {
    return json['x-amazon-apigateway-integration'] !== undefined ||
           (json.paths && Object.values(json.paths).some((path: any) =>
             Object.values(path).some((method: any) =>
               method['x-amazon-apigateway-integration'] !== undefined
             )
           ));
  }

  private isAzureAPIM(json: any): boolean {
    return json.apiVersion && json.type === 'Microsoft.ApiManagement/service/apis';
  }

  private async importAWSGateway(spec: any): Promise<ImportResult> {
    const collection: Collection = {
      id: `col-${Date.now()}`,
      name: spec.info?.title || 'AWS API Gateway',
      description: spec.info?.description || '',
      requests: [],
      folders: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    const requests: Request[] = [];
    const baseUrl = this.extractAWSBaseUrl(spec);

    // Process paths
    for (const [path, pathItem] of Object.entries(spec.paths || {})) {
      const methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head'];
      for (const method of methods) {
        const operation = (pathItem as any)[method];
        if (operation) {
          const request = this.createAWSRequest(method, path, operation, baseUrl, collection.id);
          requests.push(request);
        }
      }
    }

    console.log(`[APIGatewayImporter] Imported ${requests.length} AWS API Gateway requests`);

    return {
      success: true,
      collections: [collection],
      requests,
      metadata: {
        format: 'aws-gateway',
        itemCount: 1 + requests.length,
        importedAt: new Date(),
      },
    };
  }

  private async importAzureAPIM(spec: any): Promise<ImportResult> {
    const collection: Collection = {
      id: `col-${Date.now()}`,
      name: spec.properties?.displayName || 'Azure APIM',
      description: spec.properties?.description || '',
      requests: [],
      folders: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    const requests: Request[] = [];
    const baseUrl = spec.properties?.serviceUrl || 'https://api.azure.com';

    // Process operations
    if (spec.properties?.apiRevision || spec.properties?.path) {
      // Create a sample request
      const request: Request = {
        id: `req-${Date.now()}`,
        name: spec.properties.displayName || 'Azure API',
        description: spec.properties.description || '',
        protocol: 'REST' as const,
        method: 'GET' as const,
        url: baseUrl + (spec.properties.path || '/'),
        headers: [],
        queryParams: [],
        collectionId: collection.id,
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      requests.push(request);
    }

    console.log(`[APIGatewayImporter] Imported ${requests.length} Azure APIM requests`);

    return {
      success: true,
      collections: [collection],
      requests,
      metadata: {
        format: 'azure-apim',
        itemCount: 1 + requests.length,
        importedAt: new Date(),
      },
    };
  }

  private extractAWSBaseUrl(spec: any): string {
    if (spec.servers && spec.servers.length > 0) {
      return spec.servers[0].url;
    }
    if (spec.host) {
      const scheme = spec.schemes?.[0] || 'https';
      const basePath = spec.basePath || '';
      return `${scheme}://${spec.host}${basePath}`;
    }
    return 'https://api.execute-api.amazonaws.com';
  }

  private createAWSRequest(
    method: string,
    path: string,
    operation: any,
    baseUrl: string,
    collectionId: string
  ): Request {
    const url = baseUrl + path;

    const headers: any[] = [];
    const queryParams: any[] = [];

    // Extract parameters
    if (operation.parameters) {
      for (const param of operation.parameters) {
        if (param.in === 'query') {
          queryParams.push({
            key: param.name,
            value: param.example || param.default || '',
            enabled: param.required || false,
          });
        } else if (param.in === 'header') {
          headers.push({
            key: param.name,
            value: param.example || param.default || '',
            enabled: param.required || false,
          });
        }
      }
    }

    return {
      id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: operation.summary || operation.operationId || `${method.toUpperCase()} ${path}`,
      description: operation.description || '',
      protocol: 'REST' as const,
      method: method.toUpperCase() as HttpMethod,
      url,
      headers,
      queryParams,
      collectionId,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  }

  getExample(): string {
    return JSON.stringify({
      swagger: '2.0',
      info: {
        title: 'AWS API Gateway',
        version: '1.0.0',
      },
      paths: {
        '/users': {
          get: {
            'x-amazon-apigateway-integration': {
              type: 'aws_proxy',
              httpMethod: 'POST',
              uri: 'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:GetUsers/invocations',
            },
          },
        },
      },
    }, null, 2);
  }
}
