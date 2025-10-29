// API Gateway Exporter (AWS/Azure)
import type {
  Exporter,
  ImportExportFormat,
  ImportExportOptions,
  ExportResult,
} from '../../../types/import-export';
import type { Collection, Request } from '../../../types/models';

/**
 * API Gateway Exporter
 * Exports to AWS API Gateway and Azure API Management formats
 */
export class APIGatewayExporter implements Exporter {
  readonly format: ImportExportFormat = 'aws-gateway';
  readonly name = 'API Gateway';
  readonly description = 'Export to AWS/Azure API Gateway format';
  readonly fileExtensions = ['.json', '.yaml'];

  async exportCollections(
    collections: Collection[],
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    try {
      const isAzure = options.format === 'azure-gateway';
      
      if (isAzure) {
        return this.exportToAzure(collections, options);
      } else {
        return this.exportToAWS(collections, options);
      }
    } catch (error) {
      return {
        success: false,
        format: options.format || 'aws-gateway',
        errors: [error instanceof Error ? error.message : 'Export failed'],
      };
    }
  }

  private async exportToAWS(
    collections: Collection[],
    options: ImportExportOptions
  ): Promise<ExportResult> {
    const swagger: any = {
      swagger: '2.0',
      info: {
        title: collections[0]?.name || 'API',
        version: '1.0.0',
        description: collections[0]?.description || '',
      },
      schemes: ['https'],
      paths: {},
      'x-amazon-apigateway-request-validators': {
        all: {
          validateRequestBody: true,
          validateRequestParameters: true,
        },
      },
    };

    // Convert collections to paths
    for (const collection of collections) {
      for (const request of collection.requests || []) {
        const path = this.extractPath(request.url);
        const method = request.method.toLowerCase();

        if (!swagger.paths[path]) {
          swagger.paths[path] = {};
        }

        swagger.paths[path][method] = {
          summary: request.name,
          description: request.description || '',
          produces: ['application/json'],
          parameters: this.convertParameters(request),
          responses: {
            '200': {
              description: 'Successful response',
            },
          },
          'x-amazon-apigateway-integration': {
            type: 'http',
            httpMethod: request.method,
            uri: request.url,
            responses: {
              default: {
                statusCode: '200',
              },
            },
          },
        };
      }
    }

    const data = options.prettify
      ? JSON.stringify(swagger, null, 2)
      : JSON.stringify(swagger);

    return {
      success: true,
      format: 'aws-gateway',
      data,
      metadata: {
        itemCount: collections.length,
        exportedAt: new Date(),
        size: data.length,
      },
    };
  }

  private async exportToAzure(
    collections: Collection[],
    options: ImportExportOptions
  ): Promise<ExportResult> {
    const openapi: any = {
      openapi: '3.0.0',
      info: {
        title: collections[0]?.name || 'API',
        version: '1.0.0',
        description: collections[0]?.description || '',
      },
      servers: [
        {
          url: 'https://api.example.com',
        },
      ],
      paths: {},
    };

    // Convert collections to paths
    for (const collection of collections) {
      for (const request of collection.requests || []) {
        const path = this.extractPath(request.url);
        const method = request.method.toLowerCase();

        if (!openapi.paths[path]) {
          openapi.paths[path] = {};
        }

        openapi.paths[path][method] = {
          summary: request.name,
          description: request.description || '',
          parameters: this.convertParameters(request),
          responses: {
            '200': {
              description: 'Successful response',
              content: {
                'application/json': {
                  schema: {
                    type: 'object',
                  },
                },
              },
            },
          },
          'x-ms-api-management': {
            backend: {
              url: request.url,
            },
          },
        };
      }
    }

    const data = options.prettify
      ? JSON.stringify(openapi, null, 2)
      : JSON.stringify(openapi);

    return {
      success: true,
      format: 'azure-gateway',
      data,
      metadata: {
        itemCount: collections.length,
        exportedAt: new Date(),
        size: data.length,
      },
    };
  }

  async exportRequest(
    request: Request,
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    return this.exportRequests([request], options);
  }

  async exportRequests(
    requests: Request[],
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    const collection: Collection = {
      id: 'temp-col',
      name: 'Exported Requests',
      description: '',
      requests: [],
      folders: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    return this.exportCollections([collection], options);
  }

  private extractPath(url: string): string {
    try {
      const urlObj = new URL(url);
      return urlObj.pathname || '/';
    } catch {
      return '/';
    }
  }

  private convertParameters(request: Request): any[] {
    const params: any[] = [];

    // Query parameters
    if (request.queryParams) {
      for (const param of request.queryParams) {
        params.push({
          name: param.key,
          in: 'query',
          required: param.enabled !== false,
          schema: {
            type: 'string',
          },
        });
      }
    }

    // Headers
    if (request.headers) {
      for (const header of request.headers) {
        if (header.key.toLowerCase() !== 'content-type') {
          params.push({
            name: header.key,
            in: 'header',
            required: header.enabled !== false,
            schema: {
              type: 'string',
            },
          });
        }
      }
    }

    return params;
  }

  getExample(): string {
    return JSON.stringify(
      {
        swagger: '2.0',
        info: {
          title: 'Example API',
          version: '1.0.0',
        },
        paths: {
          '/users': {
            get: {
              summary: 'Get users',
              'x-amazon-apigateway-integration': {
                type: 'http',
                httpMethod: 'GET',
                uri: 'https://api.example.com/users',
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
