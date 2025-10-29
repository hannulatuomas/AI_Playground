/**
 * RequestAnalyzerService - Request Pattern Analysis and Schema Inference
 * 
 * Analyzes HTTP requests and responses to detect patterns and generate API specifications.
 * 
 * Features:
 * - Endpoint detection and grouping
 * - Path parameter extraction
 * - Query parameter detection
 * - Header analysis
 * - JSON schema inference from request/response bodies
 * - Authentication pattern detection
 * - Response status code analysis
 * 
 * Used by OpenAPI, AsyncAPI, and GraphQL generators to create specifications.
 */

import type { ConsoleEntry } from './ConsoleService';

export interface Parameter {
  name: string;
  type: string;
  required: boolean;
  description?: string;
  example?: any;
  enum?: any[];
}

export interface Header {
  name: string;
  value: string;
  required: boolean;
}

export interface JSONSchema {
  type: string;
  properties?: Record<string, JSONSchema>;
  items?: JSONSchema;
  required?: string[];
  enum?: any[];
  format?: string;
  example?: any;
  description?: string;
  pattern?: string;
  minimum?: number;
  maximum?: number;
  minLength?: number;
  maxLength?: number;
}

export interface Endpoint {
  path: string;
  method: string;
  pathParameters: Parameter[];
  queryParameters: Parameter[];
  headers: Header[];
  requestBody?: {
    contentType: string;
    schema: JSONSchema;
    examples: any[];
  };
  responses: {
    [status: number]: {
      description: string;
      schema: JSONSchema;
      examples: any[];
    };
  };
  security?: SecurityRequirement[];
  tags?: string[];
  summary?: string;
  description?: string;
  operationId?: string;
}

export interface SecurityRequirement {
  type: 'apiKey' | 'http' | 'oauth2' | 'openIdConnect';
  scheme?: string; // bearer, basic, etc.
  in?: 'header' | 'query' | 'cookie';
  name?: string;
}

export interface AuthPattern {
  type: 'apiKey' | 'bearer' | 'basic' | 'oauth2' | 'custom';
  headerName?: string;
  queryParamName?: string;
  scheme?: string;
  endpoints: string[];
}

export interface EndpointGroup {
  basePath: string;
  tag: string;
  endpoints: Endpoint[];
}

export interface AnalysisResult {
  endpoints: Endpoint[];
  schemas: Map<string, JSONSchema>;
  authentication: AuthPattern[];
  commonHeaders: Header[];
  basePaths: string[];
  metadata: {
    totalRequests: number;
    uniqueEndpoints: number;
    protocols: string[];
    analyzedAt: number;
  };
}

export class RequestAnalyzerService {
  /**
   * Analyze requests from console entries
   */
  analyzeRequests(entries: ConsoleEntry[]): AnalysisResult {
    const requestEntries = entries.filter(e => e.type === 'request' || e.type === 'response');
    
    // Group request/response pairs
    const pairs = this.groupRequestResponsePairs(requestEntries);
    
    // Detect endpoints
    const endpoints = this.detectEndpoints(pairs);
    
    // Detect authentication patterns
    const authentication = this.detectAuthPatterns(requestEntries);
    
    // Find common headers
    const commonHeaders = this.detectCommonHeaders(requestEntries);
    
    // Extract base paths
    const basePaths = this.extractBasePaths(endpoints);
    
    // Generate component schemas
    const schemas = this.generateComponentSchemas(endpoints);
    
    return {
      endpoints,
      schemas,
      authentication,
      commonHeaders,
      basePaths,
      metadata: {
        totalRequests: requestEntries.length,
        uniqueEndpoints: endpoints.length,
        protocols: this.extractProtocols(requestEntries),
        analyzedAt: Date.now(),
      },
    };
  }

  /**
   * Group request and response entries by request ID
   */
  private groupRequestResponsePairs(entries: ConsoleEntry[]): Map<string, { request?: ConsoleEntry; response?: ConsoleEntry }> {
    const pairs = new Map<string, { request?: ConsoleEntry; response?: ConsoleEntry }>();
    
    for (const entry of entries) {
      const requestId = entry.requestId || entry.id;
      
      if (!pairs.has(requestId)) {
        pairs.set(requestId, {});
      }
      
      const pair = pairs.get(requestId)!;
      if (entry.type === 'request') {
        pair.request = entry;
      } else if (entry.type === 'response') {
        pair.response = entry;
      }
    }
    
    return pairs;
  }

  /**
   * Detect unique endpoints from request/response pairs
   */
  private detectEndpoints(pairs: Map<string, { request?: ConsoleEntry; response?: ConsoleEntry }>): Endpoint[] {
    const endpointMap = new Map<string, Endpoint>();
    
    for (const [_, pair] of pairs) {
      if (!pair.request) continue;
      
      const path = this.normalizePath(pair.request.url || '');
      const method = pair.request.method || 'GET';
      const key = `${method} ${path}`;
      
      if (!endpointMap.has(key)) {
        endpointMap.set(key, {
          path,
          method,
          pathParameters: this.extractPathParameters(path),
          queryParameters: [],
          headers: [],
          responses: {},
          tags: this.generateTags(path),
          summary: this.generateSummary(method, path),
          operationId: this.generateOperationId(method, path),
        });
      }
      
      const endpoint = endpointMap.get(key)!;
      
      // Update query parameters
      this.updateQueryParameters(endpoint, pair.request);
      
      // Update headers
      this.updateHeaders(endpoint, pair.request);
      
      // Update request body
      this.updateRequestBody(endpoint, pair.request);
      
      // Update responses
      if (pair.response) {
        this.updateResponses(endpoint, pair.response);
      }
    }
    
    return Array.from(endpointMap.values());
  }

  /**
   * Normalize URL path by removing query parameters and extracting path pattern
   */
  private normalizePath(url: string): string {
    try {
      const urlObj = new URL(url);
      let path = urlObj.pathname;
      
      // Convert UUID-like segments to parameters (do this BEFORE numeric to avoid partial matches)
      path = path.replace(/\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi, '/{id}');
      
      // Convert numeric path segments to parameters
      path = path.replace(/\/\d+/g, '/{id}');
      
      // Remove trailing slash
      if (path.length > 1 && path.endsWith('/')) {
        path = path.slice(0, -1);
      }
      
      return path || '/';
    } catch {
      // If URL parsing fails, try to extract path
      const match = url.match(/^https?:\/\/[^\/]+(\/[^?#]*)/);
      return match ? match[1] : url;
    }
  }

  /**
   * Extract path parameters from a path pattern
   */
  private extractPathParameters(path: string): Parameter[] {
    const params: Parameter[] = [];
    const matches = path.matchAll(/\{([^}]+)\}/g);
    
    for (const match of matches) {
      const name = match[1];
      params.push({
        name,
        type: name === 'id' || name.endsWith('Id') ? 'integer' : 'string',
        required: true,
        description: `${name} parameter`,
      });
    }
    
    return params;
  }

  /**
   * Update query parameters from request
   */
  private updateQueryParameters(endpoint: Endpoint, request: ConsoleEntry): void {
    if (!request.url) return;
    
    try {
      const urlObj = new URL(request.url);
      const searchParams = urlObj.searchParams;
      
      for (const [name, value] of searchParams.entries()) {
        const existing = endpoint.queryParameters.find(p => p.name === name);
        if (!existing) {
          endpoint.queryParameters.push({
            name,
            type: this.inferType(value),
            required: false,
            example: value,
          });
        }
      }
    } catch {
      // Ignore URL parsing errors
    }
  }

  /**
   * Update headers from request
   */
  private updateHeaders(endpoint: Endpoint, request: ConsoleEntry): void {
    if (!request.headers) return;
    
    for (const [name, value] of Object.entries(request.headers)) {
      // Skip common auto-generated headers
      if (this.isCommonHeader(name)) continue;
      
      const existing = endpoint.headers.find(h => h.name === name);
      if (!existing) {
        endpoint.headers.push({
          name,
          value,
          required: false,
        });
      }
    }
  }

  /**
   * Update request body schema from request
   */
  private updateRequestBody(endpoint: Endpoint, request: ConsoleEntry): void {
    if (!request.body) return;
    
    const contentType = request.headers?.['content-type'] || 'application/json';
    
    if (!endpoint.requestBody) {
      endpoint.requestBody = {
        contentType,
        schema: this.inferSchema(request.body),
        examples: [request.body],
      };
    } else {
      // Merge schemas
      endpoint.requestBody.schema = this.mergeSchemas(
        endpoint.requestBody.schema,
        this.inferSchema(request.body)
      );
      
      // Add example if unique
      if (!endpoint.requestBody.examples.some(ex => JSON.stringify(ex) === JSON.stringify(request.body))) {
        endpoint.requestBody.examples.push(request.body);
      }
    }
  }

  /**
   * Update responses from response entry
   */
  private updateResponses(endpoint: Endpoint, response: ConsoleEntry): void {
    const status = response.status || 200;
    
    if (!endpoint.responses[status]) {
      endpoint.responses[status] = {
        description: response.statusText || this.getStatusDescription(status),
        schema: response.body ? this.inferSchema(response.body) : { type: 'null' },
        examples: response.body ? [response.body] : [],
      };
    } else {
      // Merge schemas
      if (response.body) {
        endpoint.responses[status].schema = this.mergeSchemas(
          endpoint.responses[status].schema,
          this.inferSchema(response.body)
        );
        
        // Add example if unique
        const existingExamples = endpoint.responses[status].examples;
        if (!existingExamples.some(ex => JSON.stringify(ex) === JSON.stringify(response.body))) {
          existingExamples.push(response.body);
        }
      }
    }
  }

  /**
   * Infer JSON schema from data
   */
  inferSchema(data: any): JSONSchema {
    if (data === null) {
      return { type: 'null' };
    }
    
    if (Array.isArray(data)) {
      if (data.length === 0) {
        return { type: 'array', items: { type: 'object' } };
      }
      
      // Infer schema from first item and merge with others
      let itemSchema = this.inferSchema(data[0]);
      for (let i = 1; i < Math.min(data.length, 5); i++) {
        itemSchema = this.mergeSchemas(itemSchema, this.inferSchema(data[i]));
      }
      
      return { type: 'array', items: itemSchema };
    }
    
    if (typeof data === 'object') {
      const properties: Record<string, JSONSchema> = {};
      const required: string[] = [];
      
      for (const [key, value] of Object.entries(data)) {
        properties[key] = this.inferSchema(value);
        if (value !== null && value !== undefined) {
          required.push(key);
        }
      }
      
      return {
        type: 'object',
        properties,
        required: required.length > 0 ? required : undefined,
      };
    }
    
    // Primitive types
    const type = typeof data;
    const schema: JSONSchema = { type };
    
    // Add format for specific patterns
    if (type === 'string') {
      const str = data as string;
      
      // Email
      if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(str)) {
        schema.format = 'email';
      }
      // Date-time
      else if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(str)) {
        schema.format = 'date-time';
      }
      // Date
      else if (/^\d{4}-\d{2}-\d{2}$/.test(str)) {
        schema.format = 'date';
      }
      // URL
      else if (/^https?:\/\//.test(str)) {
        schema.format = 'uri';
      }
      // UUID
      else if (/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str)) {
        schema.format = 'uuid';
      }
      
      schema.example = data;
    } else if (type === 'number') {
      schema.example = data;
      // Check if it's an integer
      if (Number.isInteger(data)) {
        schema.type = 'integer';
      }
    } else if (type === 'boolean') {
      schema.example = data;
    }
    
    return schema;
  }

  /**
   * Merge two JSON schemas
   */
  mergeSchemas(schema1: JSONSchema, schema2: JSONSchema): JSONSchema {
    // If types don't match, use anyOf
    if (schema1.type !== schema2.type) {
      return { type: 'object' }; // Fallback to object
    }
    
    const merged: JSONSchema = { type: schema1.type };
    
    if (schema1.type === 'object' && schema1.properties && schema2.properties) {
      merged.properties = { ...schema1.properties };
      
      // Merge properties
      for (const [key, value] of Object.entries(schema2.properties)) {
        if (merged.properties[key]) {
          merged.properties[key] = this.mergeSchemas(merged.properties[key], value);
        } else {
          merged.properties[key] = value;
        }
      }
      
      // Merge required fields (only include if present in both)
      const required1 = new Set(schema1.required || []);
      const required2 = new Set(schema2.required || []);
      const commonRequired = [...required1].filter(r => required2.has(r));
      
      if (commonRequired.length > 0) {
        merged.required = commonRequired;
      }
    } else if (schema1.type === 'array' && schema1.items && schema2.items) {
      merged.items = this.mergeSchemas(schema1.items, schema2.items);
    }
    
    // Preserve format if both have the same format
    if (schema1.format === schema2.format) {
      merged.format = schema1.format;
    }
    
    return merged;
  }

  /**
   * Detect authentication patterns
   */
  private detectAuthPatterns(entries: ConsoleEntry[]): AuthPattern[] {
    const patterns: Map<string, AuthPattern> = new Map();
    
    for (const entry of entries) {
      if (entry.type !== 'request' || !entry.headers) continue;
      
      // Check for Authorization header
      const authHeader = entry.headers['authorization'] || entry.headers['Authorization'];
      if (authHeader) {
        const type = authHeader.startsWith('Bearer ') ? 'bearer' : 
                     authHeader.startsWith('Basic ') ? 'basic' : 'custom';
        
        const key = `header:authorization:${type}`;
        if (!patterns.has(key)) {
          patterns.set(key, {
            type,
            headerName: 'Authorization',
            scheme: type,
            endpoints: [],
          });
        }
        
        if (entry.url) {
          patterns.get(key)!.endpoints.push(entry.url);
        }
      }
      
      // Check for API key in headers (case-insensitive)
      const apiKeyHeaders = ['x-api-key', 'api-key', 'apikey'];
      for (const headerName of apiKeyHeaders) {
        // Check both exact case and lowercase
        const headerValue = entry.headers[headerName] || entry.headers[headerName.toLowerCase()] || 
                           Object.entries(entry.headers).find(([k]) => k.toLowerCase() === headerName)?.[1];
        
        if (headerValue) {
          const key = `header:${headerName}:apiKey`;
          if (!patterns.has(key)) {
            patterns.set(key, {
              type: 'apiKey',
              headerName,
              endpoints: [],
            });
          }
          
          if (entry.url) {
            patterns.get(key)!.endpoints.push(entry.url);
          }
        }
      }
    }
    
    return Array.from(patterns.values());
  }

  /**
   * Detect common headers across requests
   */
  private detectCommonHeaders(entries: ConsoleEntry[]): Header[] {
    const headerCounts = new Map<string, { count: number; value: string }>();
    const totalRequests = entries.filter(e => e.type === 'request').length;
    
    for (const entry of entries) {
      if (entry.type !== 'request' || !entry.headers) continue;
      
      for (const [name, value] of Object.entries(entry.headers)) {
        if (this.isCommonHeader(name)) continue;
        
        const key = name.toLowerCase();
        if (!headerCounts.has(key)) {
          headerCounts.set(key, { count: 0, value });
        }
        headerCounts.get(key)!.count++;
      }
    }
    
    // Headers present in >50% of requests are considered common
    const threshold = totalRequests * 0.5;
    const commonHeaders: Header[] = [];
    
    for (const [name, data] of headerCounts) {
      if (data.count >= threshold) {
        commonHeaders.push({
          name,
          value: data.value,
          required: data.count > totalRequests * 0.9, // >90% = required
        });
      }
    }
    
    return commonHeaders;
  }

  /**
   * Extract base paths from endpoints
   */
  private extractBasePaths(endpoints: Endpoint[]): string[] {
    const paths = endpoints.map(e => e.path);
    const basePaths = new Set<string>();
    
    for (const path of paths) {
      const parts = path.split('/').filter(p => p && !p.startsWith('{'));
      if (parts.length > 0) {
        basePaths.add('/' + parts[0]);
      }
    }
    
    return Array.from(basePaths);
  }

  /**
   * Generate component schemas from endpoints
   */
  private generateComponentSchemas(endpoints: Endpoint[]): Map<string, JSONSchema> {
    const schemas = new Map<string, JSONSchema>();
    
    for (const endpoint of endpoints) {
      // Extract request body schemas
      if (endpoint.requestBody?.schema.type === 'object') {
        const schemaName = this.generateSchemaName(endpoint.path, endpoint.method, 'Request');
        schemas.set(schemaName, endpoint.requestBody.schema);
      }
      
      // Extract response schemas
      for (const [status, response] of Object.entries(endpoint.responses)) {
        if (response.schema.type === 'object' || response.schema.type === 'array') {
          const schemaName = this.generateSchemaName(endpoint.path, endpoint.method, `Response${status}`);
          schemas.set(schemaName, response.schema);
        }
      }
    }
    
    return schemas;
  }

  /**
   * Extract protocols from entries
   */
  private extractProtocols(entries: ConsoleEntry[]): string[] {
    const protocols = new Set<string>();
    
    for (const entry of entries) {
      if (entry.protocol) {
        protocols.add(entry.protocol);
      }
    }
    
    return Array.from(protocols);
  }

  /**
   * Group endpoints by base path
   */
  groupByBasePath(endpoints: Endpoint[]): EndpointGroup[] {
    const groups = new Map<string, EndpointGroup>();
    
    for (const endpoint of endpoints) {
      const basePath = this.extractBasePath(endpoint.path);
      
      if (!groups.has(basePath)) {
        groups.set(basePath, {
          basePath,
          tag: this.pathToTag(basePath),
          endpoints: [],
        });
      }
      
      groups.get(basePath)!.endpoints.push(endpoint);
    }
    
    return Array.from(groups.values());
  }

  /**
   * Helper: Extract base path from full path
   */
  private extractBasePath(path: string): string {
    const parts = path.split('/').filter(p => p && !p.startsWith('{'));
    return parts.length > 0 ? '/' + parts[0] : '/';
  }

  /**
   * Helper: Convert path to tag name
   */
  private pathToTag(path: string): string {
    return path.slice(1).replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Default';
  }

  /**
   * Helper: Generate tags for endpoint
   */
  private generateTags(path: string): string[] {
    const tag = this.pathToTag(this.extractBasePath(path));
    return [tag];
  }

  /**
   * Helper: Generate summary for endpoint
   */
  private generateSummary(method: string, path: string): string {
    const action = method === 'GET' ? 'Get' :
                   method === 'POST' ? 'Create' :
                   method === 'PUT' ? 'Update' :
                   method === 'PATCH' ? 'Modify' :
                   method === 'DELETE' ? 'Delete' : method;
    
    const resource = path.split('/').filter(p => p && !p.startsWith('{')).pop() || 'resource';
    
    return `${action} ${resource}`;
  }

  /**
   * Helper: Generate operation ID
   */
  private generateOperationId(method: string, path: string): string {
    const parts = path.split('/').filter(p => p && !p.startsWith('{'));
    const resource = parts.join('_');
    return `${method.toLowerCase()}_${resource}`.replace(/[^a-zA-Z0-9_]/g, '_');
  }

  /**
   * Helper: Generate schema name
   */
  private generateSchemaName(path: string, method: string, suffix: string): string {
    const parts = path.split('/').filter(p => p && !p.startsWith('{'));
    const resource = parts.map(p => p.charAt(0).toUpperCase() + p.slice(1)).join('');
    return `${resource}${suffix}`;
  }

  /**
   * Helper: Get status code description
   */
  private getStatusDescription(status: number): string {
    const descriptions: Record<number, string> = {
      200: 'Successful response',
      201: 'Created',
      204: 'No content',
      400: 'Bad request',
      401: 'Unauthorized',
      403: 'Forbidden',
      404: 'Not found',
      500: 'Internal server error',
    };
    
    return descriptions[status] || 'Response';
  }

  /**
   * Helper: Check if header is common/auto-generated
   */
  private isCommonHeader(name: string): boolean {
    const common = [
      'host', 'user-agent', 'accept', 'accept-encoding', 'accept-language',
      'connection', 'cache-control', 'content-length', 'content-type',
    ];
    return common.includes(name.toLowerCase());
  }

  /**
   * Helper: Infer type from value
   */
  private inferType(value: string): string {
    if (/^\d+$/.test(value)) return 'integer';
    if (/^\d+\.\d+$/.test(value)) return 'number';
    if (value === 'true' || value === 'false') return 'boolean';
    return 'string';
  }
}
