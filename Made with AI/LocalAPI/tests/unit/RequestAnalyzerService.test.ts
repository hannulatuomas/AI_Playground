/**
 * RequestAnalyzerService Unit Tests
 * 
 * Tests for request pattern analysis and schema inference
 */

import { RequestAnalyzerService } from '../../src/main/services/RequestAnalyzerService';
import type { ConsoleEntry } from '../../src/main/services/ConsoleService';

describe('RequestAnalyzerService', () => {
  let service: RequestAnalyzerService;

  beforeEach(() => {
    service = new RequestAnalyzerService();
  });

  describe('analyzeRequests', () => {
    it('should analyze HTTP requests and detect endpoints', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'request',
          method: 'GET',
          url: 'https://api.example.com/users',
        },
        {
          id: '2',
          timestamp: Date.now(),
          type: 'response',
          status: 200,
          body: { users: [{ id: 1, name: 'John' }] },
          requestId: '1',
        },
      ];

      const result = service.analyzeRequests(entries);

      expect(result.endpoints).toHaveLength(1);
      expect(result.endpoints[0].path).toBe('/users');
      expect(result.endpoints[0].method).toBe('GET');
    });

    it('should normalize paths with numeric IDs', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'request',
          method: 'GET',
          url: 'https://api.example.com/users/123',
        },
        {
          id: '2',
          timestamp: Date.now(),
          type: 'request',
          method: 'GET',
          url: 'https://api.example.com/users/456',
        },
      ];

      const result = service.analyzeRequests(entries);

      expect(result.endpoints).toHaveLength(1);
      expect(result.endpoints[0].path).toBe('/users/{id}');
    });

    it('should detect UUID patterns in paths', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'request',
          method: 'GET',
          url: 'https://api.example.com/users/550e8400-e29b-41d4-a716-446655440000',
        },
      ];

      const result = service.analyzeRequests(entries);

      expect(result.endpoints[0].path).toBe('/users/{id}');
    });

    it('should detect query parameters', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'request',
          method: 'GET',
          url: 'https://api.example.com/users?page=1&limit=10',
        },
      ];

      const result = service.analyzeRequests(entries);

      expect(result.endpoints[0].queryParameters).toHaveLength(2);
      expect(result.endpoints[0].queryParameters[0].name).toBe('page');
      expect(result.endpoints[0].queryParameters[1].name).toBe('limit');
    });

    it('should detect authentication patterns - Bearer', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'request',
          method: 'GET',
          url: 'https://api.example.com/users',
          headers: {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
          },
        },
      ];

      const result = service.analyzeRequests(entries);

      expect(result.authentication).toHaveLength(1);
      expect(result.authentication[0].type).toBe('bearer');
    });

    it('should detect authentication patterns - API Key', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'request',
          method: 'GET',
          url: 'https://api.example.com/users',
          headers: {
            'X-API-Key': 'abc123def456',
          },
        },
      ];

      const result = service.analyzeRequests(entries);

      expect(result.authentication).toHaveLength(1);
      expect(result.authentication[0].type).toBe('apiKey');
    });
  });

  describe('inferSchema', () => {
    it('should infer string type', () => {
      const schema = service.inferSchema('hello');

      expect(schema.type).toBe('string');
      expect(schema.example).toBe('hello');
    });

    it('should infer integer type', () => {
      const schema = service.inferSchema(42);

      expect(schema.type).toBe('integer');
      expect(schema.example).toBe(42);
    });

    it('should infer number type for floats', () => {
      const schema = service.inferSchema(3.14);

      expect(schema.type).toBe('number');
      expect(schema.example).toBe(3.14);
    });

    it('should infer boolean type', () => {
      const schema = service.inferSchema(true);

      expect(schema.type).toBe('boolean');
      expect(schema.example).toBe(true);
    });

    it('should infer email format', () => {
      const schema = service.inferSchema('user@example.com');

      expect(schema.type).toBe('string');
      expect(schema.format).toBe('email');
    });

    it('should infer date-time format', () => {
      const schema = service.inferSchema('2023-10-31T10:30:00Z');

      expect(schema.type).toBe('string');
      expect(schema.format).toBe('date-time');
    });

    it('should infer UUID format', () => {
      const schema = service.inferSchema('550e8400-e29b-41d4-a716-446655440000');

      expect(schema.type).toBe('string');
      expect(schema.format).toBe('uuid');
    });

    it('should infer URI format', () => {
      const schema = service.inferSchema('https://example.com');

      expect(schema.type).toBe('string');
      expect(schema.format).toBe('uri');
    });

    it('should infer object type with properties', () => {
      const data = {
        id: 1,
        name: 'John',
        email: 'john@example.com',
      };

      const schema = service.inferSchema(data);

      expect(schema.type).toBe('object');
      expect(schema.properties).toBeDefined();
      expect(schema.properties!.id.type).toBe('integer');
      expect(schema.properties!.name.type).toBe('string');
      expect(schema.properties!.email.format).toBe('email');
      expect(schema.required).toContain('id');
      expect(schema.required).toContain('name');
    });

    it('should infer array type', () => {
      const data = [1, 2, 3];

      const schema = service.inferSchema(data);

      expect(schema.type).toBe('array');
      expect(schema.items).toBeDefined();
      expect(schema.items!.type).toBe('integer');
    });

    it('should infer array of objects', () => {
      const data = [
        { id: 1, name: 'John' },
        { id: 2, name: 'Jane' },
      ];

      const schema = service.inferSchema(data);

      expect(schema.type).toBe('array');
      expect(schema.items!.type).toBe('object');
      expect(schema.items!.properties).toBeDefined();
    });

    it('should handle null values', () => {
      const schema = service.inferSchema(null);

      expect(schema.type).toBe('null');
    });

    it('should handle empty arrays', () => {
      const schema = service.inferSchema([]);

      expect(schema.type).toBe('array');
      expect(schema.items).toBeDefined();
    });
  });

  describe('mergeSchemas', () => {
    it('should merge object schemas', () => {
      const schema1 = {
        type: 'object' as const,
        properties: {
          id: { type: 'integer' as const },
          name: { type: 'string' as const },
        },
        required: ['id', 'name'],
      };

      const schema2 = {
        type: 'object' as const,
        properties: {
          id: { type: 'integer' as const },
          email: { type: 'string' as const },
        },
        required: ['id', 'email'],
      };

      const merged = service.mergeSchemas(schema1, schema2);

      expect(merged.type).toBe('object');
      expect(merged.properties).toHaveProperty('id');
      expect(merged.properties).toHaveProperty('name');
      expect(merged.properties).toHaveProperty('email');
      expect(merged.required).toContain('id'); // Common required field
      expect(merged.required).not.toContain('name'); // Not in both
    });

    it('should merge array schemas', () => {
      const schema1 = {
        type: 'array' as const,
        items: {
          type: 'object' as const,
          properties: {
            id: { type: 'integer' as const },
          },
        },
      };

      const schema2 = {
        type: 'array' as const,
        items: {
          type: 'object' as const,
          properties: {
            name: { type: 'string' as const },
          },
        },
      };

      const merged = service.mergeSchemas(schema1, schema2);

      expect(merged.type).toBe('array');
      expect(merged.items).toBeDefined();
      expect(merged.items!.properties).toHaveProperty('id');
      expect(merged.items!.properties).toHaveProperty('name');
    });

    it('should preserve format when both schemas have same format', () => {
      const schema1 = {
        type: 'string' as const,
        format: 'email',
      };

      const schema2 = {
        type: 'string' as const,
        format: 'email',
      };

      const merged = service.mergeSchemas(schema1, schema2);

      expect(merged.format).toBe('email');
    });
  });

  describe('groupByBasePath', () => {
    it('should group endpoints by base path', () => {
      const endpoints = [
        {
          path: '/api/users',
          method: 'GET',
          pathParameters: [],
          queryParameters: [],
          headers: [],
          responses: {},
        },
        {
          path: '/api/users/{id}',
          method: 'GET',
          pathParameters: [],
          queryParameters: [],
          headers: [],
          responses: {},
        },
        {
          path: '/api/products',
          method: 'GET',
          pathParameters: [],
          queryParameters: [],
          headers: [],
          responses: {},
        },
      ];

      const groups = service.groupByBasePath(endpoints);

      // All endpoints share the same base path /api, so expect 1 group
      expect(groups).toHaveLength(1);
      const apiGroup = groups.find(g => g.basePath === '/api');
      expect(apiGroup).toBeDefined();
      expect(apiGroup!.endpoints).toHaveLength(3);
    });
  });

  describe('end-to-end analysis', () => {
    it('should perform complete analysis with multiple requests', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'request',
          method: 'GET',
          url: 'https://api.example.com/users?page=1',
          headers: {
            'Authorization': 'Bearer token123',
          },
        },
        {
          id: '2',
          timestamp: Date.now(),
          type: 'response',
          status: 200,
          statusText: 'OK',
          body: {
            users: [
              { id: 1, name: 'John', email: 'john@example.com' },
            ],
            total: 100,
          },
          requestId: '1',
        },
        {
          id: '3',
          timestamp: Date.now(),
          type: 'request',
          method: 'POST',
          url: 'https://api.example.com/users',
          headers: {
            'Authorization': 'Bearer token123',
            'Content-Type': 'application/json',
          },
          body: {
            name: 'Jane',
            email: 'jane@example.com',
          },
        },
        {
          id: '4',
          timestamp: Date.now(),
          type: 'response',
          status: 201,
          statusText: 'Created',
          body: {
            id: 2,
            name: 'Jane',
            email: 'jane@example.com',
          },
          requestId: '3',
        },
      ];

      const result = service.analyzeRequests(entries);

      // Check metadata
      expect(result.metadata.totalRequests).toBe(4);
      expect(result.metadata.uniqueEndpoints).toBe(2);

      // Check endpoints
      expect(result.endpoints).toHaveLength(2);
      
      const getEndpoint = result.endpoints.find(e => e.method === 'GET');
      expect(getEndpoint).toBeDefined();
      expect(getEndpoint!.queryParameters).toHaveLength(1);
      expect(getEndpoint!.responses[200]).toBeDefined();
      expect(getEndpoint!.responses[200].schema.type).toBe('object');

      const postEndpoint = result.endpoints.find(e => e.method === 'POST');
      expect(postEndpoint).toBeDefined();
      expect(postEndpoint!.requestBody).toBeDefined();
      expect(postEndpoint!.responses[201]).toBeDefined();

      // Check authentication
      expect(result.authentication).toHaveLength(1);
      expect(result.authentication[0].type).toBe('bearer');

      // Check base paths
      expect(result.basePaths).toContain('/users');
    });
  });
});
