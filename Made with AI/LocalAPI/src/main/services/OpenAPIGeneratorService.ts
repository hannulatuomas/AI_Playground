/**
 * OpenAPIGeneratorService - OpenAPI 3.0 Specification Generator
 * 
 * Generates OpenAPI 3.0 specifications from analyzed request patterns.
 * 
 * Features:
 * - Complete OpenAPI 3.0 structure
 * - Paths, operations, parameters
 * - Request/response schemas
 * - Component schemas
 * - Security schemes
 * - Examples from actual requests
 * - Server definitions
 * - Tags and metadata
 */

import type {
  AnalysisResult,
  Endpoint,
  Parameter,
  Header,
  JSONSchema,
  SecurityRequirement,
} from './RequestAnalyzerService';

export interface OpenAPISpec {
  openapi: string;
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
  servers?: Array<{
    url: string;
    description?: string;
  }>;
  paths: {
    [path: string]: PathItem;
  };
  components?: {
    schemas?: Record<string, JSONSchema>;
    securitySchemes?: Record<string, SecurityScheme>;
  };
  security?: Array<Record<string, string[]>>;
  tags?: Array<{
    name: string;
    description?: string;
  }>;
}

export interface PathItem {
  get?: Operation;
  post?: Operation;
  put?: Operation;
  patch?: Operation;
  delete?: Operation;
  head?: Operation;
  options?: Operation;
  parameters?: ParameterObject[];
}

export interface Operation {
  summary?: string;
  description?: string;
  operationId?: string;
  tags?: string[];
  parameters?: ParameterObject[];
  requestBody?: RequestBody;
  responses: {
    [status: string]: Response;
  };
  security?: Array<Record<string, string[]>>;
}

export interface ParameterObject {
  name: string;
  in: 'path' | 'query' | 'header' | 'cookie';
  required?: boolean;
  description?: string;
  schema: JSONSchema;
  example?: any;
}

export interface RequestBody {
  description?: string;
  required?: boolean;
  content: {
    [mediaType: string]: {
      schema: JSONSchema;
      example?: any;
      examples?: Record<string, { value: any }>;
    };
  };
}

export interface Response {
  description: string;
  content?: {
    [mediaType: string]: {
      schema: JSONSchema;
      example?: any;
      examples?: Record<string, { value: any }>;
    };
  };
}

export interface SecurityScheme {
  type: 'apiKey' | 'http' | 'oauth2' | 'openIdConnect';
  scheme?: string;
  bearerFormat?: string;
  in?: 'header' | 'query' | 'cookie';
  name?: string;
  description?: string;
}

export interface GeneratorOptions {
  title: string;
  version: string;
  description?: string;
  servers?: Array<{ url: string; description?: string }>;
  includeExamples?: boolean;
  includeAuth?: boolean;
  groupByTags?: boolean;
  contact?: {
    name?: string;
    email?: string;
    url?: string;
  };
  license?: {
    name: string;
    url?: string;
  };
}

export class OpenAPIGeneratorService {
  /**
   * Generate OpenAPI 3.0 specification from analysis result
   */
  generateSpec(analysis: AnalysisResult, options: GeneratorOptions): OpenAPISpec {
    const spec: OpenAPISpec = {
      openapi: '3.0.0',
      info: {
        title: options.title,
        version: options.version,
        description: options.description,
        contact: options.contact,
        license: options.license,
      },
      paths: {},
    };

    // Add servers
    if (options.servers && options.servers.length > 0) {
      spec.servers = options.servers;
    }

    // Generate paths (merge operations for same path)
    for (const endpoint of analysis.endpoints) {
      const pathItem = this.createPathItem(endpoint, options);
      
      // Merge with existing path item if it exists
      if (spec.paths[endpoint.path]) {
        spec.paths[endpoint.path] = {
          ...spec.paths[endpoint.path],
          ...pathItem,
        };
      } else {
        spec.paths[endpoint.path] = pathItem;
      }
    }

    // Generate components
    if (analysis.schemas.size > 0 || (options.includeAuth && analysis.authentication.length > 0)) {
      spec.components = {};
      
      if (analysis.schemas.size > 0) {
        spec.components.schemas = this.convertSchemasToRecord(analysis.schemas);
      }
      
      if (options.includeAuth && analysis.authentication.length > 0) {
        spec.components.securitySchemes = this.createSecuritySchemes(analysis.authentication);
        spec.security = this.createGlobalSecurity(analysis.authentication);
      }
    }

    // Generate tags
    if (options.groupByTags) {
      spec.tags = this.createTags(analysis.endpoints);
    }

    return spec;
  }

  /**
   * Create a path item for an endpoint
   */
  private createPathItem(endpoint: Endpoint, options: GeneratorOptions): PathItem {
    const pathItem: PathItem = {};
    const operation = this.createOperation(endpoint, options);
    
    const method = endpoint.method.toLowerCase();
    if (method === 'get') pathItem.get = operation;
    else if (method === 'post') pathItem.post = operation;
    else if (method === 'put') pathItem.put = operation;
    else if (method === 'patch') pathItem.patch = operation;
    else if (method === 'delete') pathItem.delete = operation;
    else if (method === 'head') pathItem.head = operation;
    else if (method === 'options') pathItem.options = operation;

    return pathItem;
  }

  /**
   * Create an operation for an endpoint
   */
  private createOperation(endpoint: Endpoint, options: GeneratorOptions): Operation {
    const operation: Operation = {
      summary: endpoint.summary,
      description: endpoint.description,
      operationId: endpoint.operationId,
      tags: endpoint.tags,
      responses: {},
    };

    // Add parameters
    const parameters: ParameterObject[] = [];
    
    // Path parameters
    for (const param of endpoint.pathParameters) {
      parameters.push(this.createParameter(param, 'path'));
    }
    
    // Query parameters
    for (const param of endpoint.queryParameters) {
      parameters.push(this.createParameter(param, 'query'));
    }
    
    // Header parameters
    for (const header of endpoint.headers) {
      if (!this.isAuthHeader(header.name)) {
        parameters.push({
          name: header.name,
          in: 'header',
          required: header.required,
          schema: { type: 'string' },
          example: header.value,
        });
      }
    }
    
    if (parameters.length > 0) {
      operation.parameters = parameters;
    }

    // Add request body
    if (endpoint.requestBody) {
      operation.requestBody = this.createRequestBody(endpoint.requestBody, options);
    }

    // Add responses
    for (const [status, response] of Object.entries(endpoint.responses)) {
      operation.responses[status] = this.createResponse(response, options);
    }

    // Add security if needed
    if (options.includeAuth && endpoint.security) {
      operation.security = endpoint.security.map(sec => ({
        [this.getSecuritySchemeName(sec)]: [],
      }));
    }

    return operation;
  }

  /**
   * Create a parameter object
   */
  private createParameter(param: Parameter, location: 'path' | 'query' | 'header'): ParameterObject {
    return {
      name: param.name,
      in: location,
      required: param.required,
      description: param.description,
      schema: {
        type: param.type,
        enum: param.enum,
      },
      example: param.example,
    };
  }

  /**
   * Create request body
   */
  private createRequestBody(
    requestBody: { contentType: string; schema: JSONSchema; examples: any[] },
    options: GeneratorOptions
  ): RequestBody {
    const body: RequestBody = {
      required: true,
      content: {
        [requestBody.contentType]: {
          schema: requestBody.schema,
        },
      },
    };

    // Add examples
    if (options.includeExamples && requestBody.examples.length > 0) {
      const content = body.content[requestBody.contentType];
      content.example = requestBody.examples[0];
      
      if (requestBody.examples.length > 1) {
        content.examples = {};
        requestBody.examples.forEach((ex, i) => {
          content.examples![`example${i + 1}`] = { value: ex };
        });
      }
    }

    return body;
  }

  /**
   * Create response object
   */
  private createResponse(
    response: { description: string; schema: JSONSchema; examples: any[] },
    options: GeneratorOptions
  ): Response {
    const resp: Response = {
      description: response.description,
    };

    if (response.schema.type !== 'null') {
      resp.content = {
        'application/json': {
          schema: response.schema,
        },
      };

      // Add examples
      if (options.includeExamples && response.examples.length > 0) {
        const content = resp.content['application/json'];
        content.example = response.examples[0];
        
        if (response.examples.length > 1) {
          content.examples = {};
          response.examples.forEach((ex, i) => {
            content.examples![`example${i + 1}`] = { value: ex };
          });
        }
      }
    }

    return resp;
  }

  /**
   * Create security schemes
   */
  private createSecuritySchemes(authPatterns: any[]): Record<string, SecurityScheme> {
    const schemes: Record<string, SecurityScheme> = {};
    
    for (const pattern of authPatterns) {
      const name = this.getSecuritySchemeName(pattern);
      
      if (pattern.type === 'bearer') {
        schemes[name] = {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
          description: 'Bearer token authentication',
        };
      } else if (pattern.type === 'basic') {
        schemes[name] = {
          type: 'http',
          scheme: 'basic',
          description: 'Basic HTTP authentication',
        };
      } else if (pattern.type === 'apiKey') {
        schemes[name] = {
          type: 'apiKey',
          in: 'header',
          name: pattern.headerName || 'X-API-Key',
          description: 'API Key authentication',
        };
      }
    }
    
    return schemes;
  }

  /**
   * Create global security requirements
   */
  private createGlobalSecurity(authPatterns: any[]): Array<Record<string, string[]>> {
    return authPatterns.map(pattern => ({
      [this.getSecuritySchemeName(pattern)]: [],
    }));
  }

  /**
   * Get security scheme name
   */
  private getSecuritySchemeName(security: any): string {
    if (security.type === 'bearer') return 'bearerAuth';
    if (security.type === 'basic') return 'basicAuth';
    if (security.type === 'apiKey') return 'apiKeyAuth';
    return 'customAuth';
  }

  /**
   * Create tags from endpoints
   */
  private createTags(endpoints: Endpoint[]): Array<{ name: string; description?: string }> {
    const tagSet = new Set<string>();
    
    for (const endpoint of endpoints) {
      if (endpoint.tags) {
        endpoint.tags.forEach(tag => tagSet.add(tag));
      }
    }
    
    return Array.from(tagSet).map(name => ({
      name,
      description: `Operations for ${name}`,
    }));
  }

  /**
   * Convert schemas Map to Record
   */
  private convertSchemasToRecord(schemas: Map<string, JSONSchema>): Record<string, JSONSchema> {
    const record: Record<string, JSONSchema> = {};
    for (const [name, schema] of schemas) {
      record[name] = schema;
    }
    return record;
  }

  /**
   * Check if header is auth header
   */
  private isAuthHeader(name: string): boolean {
    const authHeaders = ['authorization', 'x-api-key', 'api-key', 'apikey'];
    return authHeaders.includes(name.toLowerCase());
  }

  /**
   * Validate generated spec
   */
  validateSpec(spec: OpenAPISpec): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    // Check required fields
    if (!spec.info.title) {
      errors.push('Spec must have a title');
    }
    
    if (!spec.info.version) {
      errors.push('Spec must have a version');
    }
    
    if (!spec.paths || Object.keys(spec.paths).length === 0) {
      errors.push('Spec must have at least one path');
    }
    
    // Check each path
    for (const [path, pathItem] of Object.entries(spec.paths)) {
      if (!path.startsWith('/')) {
        errors.push(`Path must start with /: ${path}`);
      }
      
      // Check operations
      for (const method of ['get', 'post', 'put', 'patch', 'delete'] as const) {
        const operation = pathItem[method];
        if (operation) {
          if (!operation.responses || Object.keys(operation.responses).length === 0) {
            errors.push(`Operation ${method.toUpperCase()} ${path} must have at least one response`);
          }
        }
      }
    }
    
    return {
      valid: errors.length === 0,
      errors,
    };
  }

  /**
   * Export spec as YAML string
   */
  toYAML(spec: OpenAPISpec): string {
    // Simple YAML generation (for production, use a proper YAML library)
    return this.objectToYAML(spec, 0);
  }

  /**
   * Convert object to YAML format
   */
  private objectToYAML(obj: any, indent: number): string {
    const spaces = '  '.repeat(indent);
    let yaml = '';
    
    if (Array.isArray(obj)) {
      for (const item of obj) {
        if (typeof item === 'object') {
          yaml += `${spaces}-\n${this.objectToYAML(item, indent + 1)}`;
        } else {
          yaml += `${spaces}- ${item}\n`;
        }
      }
    } else if (typeof obj === 'object' && obj !== null) {
      for (const [key, value] of Object.entries(obj)) {
        if (value === undefined) continue;
        
        if (Array.isArray(value)) {
          yaml += `${spaces}${key}:\n`;
          yaml += this.objectToYAML(value, indent + 1);
        } else if (typeof value === 'object' && value !== null) {
          yaml += `${spaces}${key}:\n`;
          yaml += this.objectToYAML(value, indent + 1);
        } else if (typeof value === 'string') {
          // Only quote strings if they contain special characters or spaces
          const needsQuotes = value.includes(':') || value.includes('#') || value.includes(' ') || value.includes('\n');
          yaml += `${spaces}${key}: ${needsQuotes ? `"${value}"` : value}\n`;
        } else {
          yaml += `${spaces}${key}: ${value}\n`;
        }
      }
    }
    
    return yaml;
  }

  /**
   * Export spec as JSON string
   */
  toJSON(spec: OpenAPISpec): string {
    return JSON.stringify(spec, null, 2);
  }
}
