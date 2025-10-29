// OpenAPI/Swagger Parser Service
// Parses OpenAPI 2.0 (Swagger) and OpenAPI 3.x specifications
// Generates request collections from API definitions

const SwaggerParser = require('swagger-parser');
import type { OpenAPI, OpenAPIV2, OpenAPIV3 } from 'openapi-types';
import type { Collection, Request, Header, QueryParam } from '../../types/models';

interface ParsedAPI {
  info: {
    title: string;
    version: string;
    description?: string;
    contact?: {
      name?: string;
      email?: string;
      url?: string;
    };
    license?: {
      name: string;
      url?: string;
    };
  };
  servers: string[];
  requests: Request[];
  tags?: string[];
  securitySchemes?: Record<string, any>;
}

export class OpenAPIParser {
  /**
   * Parse OpenAPI specification from URL or file path
   */
  async parseFromURL(urlOrPath: string): Promise<ParsedAPI> {
    try {
      const api = await SwaggerParser.default.validate(urlOrPath);
      return this.parseOpenAPI(api);
    } catch (error: any) {
      throw new Error(`Failed to parse OpenAPI spec: ${error.message}`);
    }
  }

  /**
   * Parse OpenAPI specification from JSON object
   */
  async parseFromObject(spec: any): Promise<ParsedAPI> {
    try {
      const api = await SwaggerParser.default.validate(spec);
      return this.parseOpenAPI(api);
    } catch (error: any) {
      throw new Error(`Failed to parse OpenAPI spec: ${error.message}`);
    }
  }

  /**
   * Parse OpenAPI specification
   */
  private parseOpenAPI(api: OpenAPI.Document): ParsedAPI {
    const isV3 = 'openapi' in api && api.openapi.startsWith('3');
    
    if (isV3) {
      return this.parseOpenAPIV3(api as OpenAPIV3.Document);
    } else {
      return this.parseSwaggerV2(api as OpenAPIV2.Document);
    }
  }

  /**
   * Parse OpenAPI 3.x specification
   */
  private parseOpenAPIV3(api: OpenAPIV3.Document): ParsedAPI {
    const info = {
      title: api.info.title,
      version: api.info.version,
      description: api.info.description,
      contact: api.info.contact,
      license: api.info.license,
    };

    // Extract server URLs
    const servers = api.servers?.map(s => s.url) || ['http://localhost'];

    // Extract tags
    const tags = api.tags?.map(t => t.name) || [];

    // Extract security schemes
    const securitySchemes = api.components?.securitySchemes || {};

    // Parse paths and operations
    const requests: Request[] = [];
    const paths = api.paths || {};

    for (const [path, pathItem] of Object.entries(paths)) {
      if (!pathItem) continue;

      // Extract path-level parameters
      const pathParameters = pathItem.parameters as OpenAPIV3.ParameterObject[] || [];

      const operations = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options'] as const;
      
      for (const method of operations) {
        const operation = pathItem[method] as OpenAPIV3.OperationObject | undefined;
        if (!operation) continue;

        const request = this.createRequestFromV3Operation(
          method.toUpperCase(),
          path,
          operation,
          servers[0],
          pathParameters,
          securitySchemes
        );

        requests.push(request);
      }
    }

    return { info, servers, requests, tags, securitySchemes };
  }

  /**
   * Parse Swagger 2.0 specification
   */
  private parseSwaggerV2(api: OpenAPIV2.Document): ParsedAPI {
    const info = {
      title: api.info.title,
      version: api.info.version,
      description: api.info.description,
    };

    // Construct base URL
    const scheme = api.schemes?.[0] || 'http';
    const host = api.host || 'localhost';
    const basePath = api.basePath || '';
    const baseUrl = `${scheme}://${host}${basePath}`;
    const servers = [baseUrl];

    // Parse paths and operations
    const requests: Request[] = [];
    const paths = api.paths || {};

    for (const [path, pathItem] of Object.entries(paths)) {
      if (!pathItem) continue;

      const operations = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options'] as const;
      
      for (const method of operations) {
        const operation = pathItem[method] as OpenAPIV2.OperationObject | undefined;
        if (!operation) continue;

        const request = this.createRequestFromV2Operation(
          method.toUpperCase(),
          path,
          operation,
          baseUrl
        );

        requests.push(request);
      }
    }

    return { info, servers, requests };
  }

  /**
   * Create request from OpenAPI 3.x operation
   */
  private createRequestFromV3Operation(
    method: string,
    path: string,
    operation: OpenAPIV3.OperationObject,
    baseUrl: string,
    pathParameters: OpenAPIV3.ParameterObject[] = [],
    securitySchemes: Record<string, any> = {}
  ): Request {
    const name = operation.summary || operation.operationId || `${method} ${path}`;
    
    // Enhanced description with tags and operation ID
    let description = operation.description || '';
    if (operation.tags && operation.tags.length > 0) {
      description += `\n\n**Tags:** ${operation.tags.join(', ')}`;
    }
    if (operation.operationId) {
      description += `\n\n**Operation ID:** ${operation.operationId}`;
    }
    if (operation.deprecated) {
      description += `\n\n⚠️ **DEPRECATED**`;
    }

    // Extract headers
    const headers: Header[] = [];
    const queryParams: QueryParam[] = [];
    let urlWithParams = path;

    // Combine path-level and operation-level parameters
    const allParameters = [...pathParameters];
    if (operation.parameters) {
      allParameters.push(...(operation.parameters as OpenAPIV3.ParameterObject[]));
    }

    for (const parameter of allParameters) {
        if (parameter.in === 'header') {
          headers.push({
            key: parameter.name,
            value: this.getDefaultValue(parameter.schema),
            enabled: parameter.required || false,
          });
        } else if (parameter.in === 'query') {
          queryParams.push({
            key: parameter.name,
            value: this.getDefaultValue(parameter.schema),
            enabled: parameter.required || false,
          });
        } else if (parameter.in === 'path') {
          // Replace path parameter with example value
          const exampleValue = this.getDefaultValue(parameter.schema) || `{${parameter.name}}`;
          urlWithParams = urlWithParams.replace(`{${parameter.name}}`, exampleValue);
        }
    }

    // Extract request body
    let body: any = { type: 'none', content: '' };
    if (operation.requestBody) {
      const requestBody = operation.requestBody as OpenAPIV3.RequestBodyObject;
      const content = requestBody.content;
      
      if (content?.['application/json']) {
        headers.push({
          key: 'Content-Type',
          value: 'application/json',
          enabled: true,
        });
        
        const schema = content['application/json'].schema;
        body = {
          type: 'json',
          content: JSON.stringify(this.generateExampleFromSchema(schema), null, 2),
        };
      }
    }

    return {
      id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name,
      description,
      protocol: 'REST',
      method: method as any,
      url: `${baseUrl}${path}`,
      headers,
      queryParams,
      body,
      auth: { type: 'none' },
      assertions: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  }

  /**
   * Create request from Swagger 2.0 operation
   */
  private createRequestFromV2Operation(
    method: string,
    path: string,
    operation: OpenAPIV2.OperationObject,
    baseUrl: string
  ): Request {
    const name = operation.summary || operation.operationId || `${method} ${path}`;
    const description = operation.description;

    // Extract headers and query params
    const headers: Header[] = [];
    const queryParams: QueryParam[] = [];

    if (operation.parameters) {
      for (const param of operation.parameters) {
        if ('in' in param) {
          if (param.in === 'header') {
            headers.push({
              key: param.name,
              value: param.default?.toString() || '',
              enabled: param.required || false,
            });
          } else if (param.in === 'query') {
            queryParams.push({
              key: param.name,
              value: param.default?.toString() || '',
              enabled: param.required || false,
            });
          }
        }
      }
    }

    // Extract request body
    let body: any = { type: 'none', content: '' };
    const bodyParam = operation.parameters?.find(p => 'in' in p && p.in === 'body') as OpenAPIV2.InBodyParameterObject | undefined;
    
    if (bodyParam?.schema) {
      headers.push({
        key: 'Content-Type',
        value: 'application/json',
        enabled: true,
      });
      
      body = {
        type: 'json',
        content: JSON.stringify(this.generateExampleFromSchemaV2(bodyParam.schema), null, 2),
      };
    }

    return {
      id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name,
      description,
      protocol: 'REST',
      method: method as any,
      url: `${baseUrl}${path}`,
      headers,
      queryParams,
      body,
      auth: { type: 'none' },
      assertions: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  }

  /**
   * Get default value from OpenAPI 3.x schema
   */
  private getDefaultValue(schema: any): string {
    if (!schema) return '';
    if (schema.default !== undefined) return String(schema.default);
    if (schema.example !== undefined) return String(schema.example);
    return '';
  }

  /**
   * Generate example object from OpenAPI 3.x schema
   */
  private generateExampleFromSchema(schema: any): any {
    if (!schema) return {};
    
    if (schema.example) return schema.example;
    if (schema.examples && schema.examples.length > 0) return schema.examples[0];

    if (schema.type === 'object' && schema.properties) {
      const example: any = {};
      for (const [key, prop] of Object.entries(schema.properties)) {
        example[key] = this.generateExampleFromSchema(prop);
      }
      return example;
    }

    if (schema.type === 'array' && schema.items) {
      return [this.generateExampleFromSchema(schema.items)];
    }

    // Default values by type
    switch (schema.type) {
      case 'string':
        return schema.format === 'date-time' ? new Date().toISOString() : 'string';
      case 'number':
      case 'integer':
        return 0;
      case 'boolean':
        return false;
      default:
        return null;
    }
  }

  /**
   * Generate example object from Swagger 2.0 schema
   */
  private generateExampleFromSchemaV2(schema: OpenAPIV2.SchemaObject): any {
    if (schema.example) return schema.example;

    if (schema.type === 'object' && schema.properties) {
      const example: any = {};
      for (const [key, prop] of Object.entries(schema.properties)) {
        example[key] = this.generateExampleFromSchemaV2(prop as OpenAPIV2.SchemaObject);
      }
      return example;
    }

    if (schema.type === 'array' && schema.items) {
      return [this.generateExampleFromSchemaV2(schema.items as OpenAPIV2.SchemaObject)];
    }

    // Default values by type
    switch (schema.type) {
      case 'string':
        return schema.format === 'date-time' ? new Date().toISOString() : 'string';
      case 'number':
      case 'integer':
        return 0;
      case 'boolean':
        return false;
      default:
        return null;
    }
  }

  /**
   * Convert parsed API to collection
   */
  createCollectionFromAPI(parsedAPI: ParsedAPI): Omit<Collection, 'createdAt' | 'updatedAt'> {
    return {
      id: `col-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: parsedAPI.info.title,
      description: `${parsedAPI.info.description || ''}\n\nVersion: ${parsedAPI.info.version}\nBase URL: ${parsedAPI.servers[0]}`,
      requests: parsedAPI.requests,
      folders: [],
    };
  }
}

// Singleton instance
let openAPIParserInstance: OpenAPIParser | null = null;

export function getOpenAPIParser(): OpenAPIParser {
  if (!openAPIParserInstance) {
    openAPIParserInstance = new OpenAPIParser();
  }
  return openAPIParserInstance;
}
