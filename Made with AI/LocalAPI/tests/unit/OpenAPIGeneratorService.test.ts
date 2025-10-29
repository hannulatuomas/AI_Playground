/**
 * OpenAPIGeneratorService Unit Tests
 * 
 * Tests for OpenAPI 3.0 specification generation
 */

import { OpenAPIGeneratorService } from '../../src/main/services/OpenAPIGeneratorService';
import type { AnalysisResult } from '../../src/main/services/RequestAnalyzerService';

describe('OpenAPIGeneratorService', () => {
  let service: OpenAPIGeneratorService;

  beforeEach(() => {
    service = new OpenAPIGeneratorService();
  });

  describe('generateSpec', () => {
    it('should generate basic OpenAPI 3.0 spec', () => {
      const analysis: AnalysisResult = {
        endpoints: [
          {
            path: '/users',
            method: 'GET',
            pathParameters: [],
            queryParameters: [],
            headers: [],
            responses: {
              200: {
                description: 'Successful response',
                schema: { type: 'array', items: { type: 'object' } },
                examples: [],
              },
            },
            tags: ['Users'],
            summary: 'Get users',
            operationId: 'get_users',
          },
        ],
        schemas: new Map(),
        authentication: [],
        commonHeaders: [],
        basePaths: ['/users'],
        metadata: {
          totalRequests: 2,
          uniqueEndpoints: 1,
          protocols: ['HTTP/1.1'],
          analyzedAt: Date.now(),
        },
      };

      const options = {
        title: 'Test API',
        version: '1.0.0',
        description: 'Test description',
      };

      const spec = service.generateSpec(analysis, options);

      expect(spec.openapi).toBe('3.0.0');
      expect(spec.info.title).toBe('Test API');
      expect(spec.info.version).toBe('1.0.0');
      expect(spec.paths['/users']).toBeDefined();
      expect(spec.paths['/users'].get).toBeDefined();
    });

    it('should include path parameters', () => {
      const analysis: AnalysisResult = {
        endpoints: [
          {
            path: '/users/{id}',
            method: 'GET',
            pathParameters: [
              { name: 'id', type: 'integer', required: true },
            ],
            queryParameters: [],
            headers: [],
            responses: {
              200: {
                description: 'User found',
                schema: { type: 'object' },
                examples: [],
              },
            },
            summary: 'Get user by ID',
          },
        ],
        schemas: new Map(),
        authentication: [],
        commonHeaders: [],
        basePaths: [],
        metadata: { totalRequests: 1, uniqueEndpoints: 1, protocols: [], analyzedAt: 0 },
      };

      const spec = service.generateSpec(analysis, { title: 'API', version: '1.0' });

      expect(spec.paths['/users/{id}'].get?.parameters).toHaveLength(1);
      expect(spec.paths['/users/{id}'].get?.parameters?.[0].name).toBe('id');
      expect(spec.paths['/users/{id}'].get?.parameters?.[0].in).toBe('path');
      expect(spec.paths['/users/{id}'].get?.parameters?.[0].required).toBe(true);
    });

    it('should include query parameters', () => {
      const analysis: AnalysisResult = {
        endpoints: [
          {
            path: '/users',
            method: 'GET',
            pathParameters: [],
            queryParameters: [
              { name: 'page', type: 'integer', required: false },
              { name: 'limit', type: 'integer', required: false },
            ],
            headers: [],
            responses: {},
          },
        ],
        schemas: new Map(),
        authentication: [],
        commonHeaders: [],
        basePaths: [],
        metadata: { totalRequests: 1, uniqueEndpoints: 1, protocols: [], analyzedAt: 0 },
      };

      const spec = service.generateSpec(analysis, { title: 'API', version: '1.0' });

      expect(spec.paths['/users'].get?.parameters).toHaveLength(2);
      const pageParam = spec.paths['/users'].get?.parameters?.find(p => p.name === 'page');
      expect(pageParam?.in).toBe('query');
    });

    it('should include request body', () => {
      const analysis: AnalysisResult = {
        endpoints: [
          {
            path: '/users',
            method: 'POST',
            pathParameters: [],
            queryParameters: [],
            headers: [],
            requestBody: {
              contentType: 'application/json',
              schema: {
                type: 'object',
                properties: {
                  name: { type: 'string' },
                  email: { type: 'string', format: 'email' },
                },
              },
              examples: [{ name: 'John', email: 'john@example.com' }],
            },
            responses: {},
          },
        ],
        schemas: new Map(),
        authentication: [],
        commonHeaders: [],
        basePaths: [],
        metadata: { totalRequests: 1, uniqueEndpoints: 1, protocols: [], analyzedAt: 0 },
      };

      const spec = service.generateSpec(analysis, { title: 'API', version: '1.0', includeExamples: true });

      expect(spec.paths['/users'].post?.requestBody).toBeDefined();
      expect(spec.paths['/users'].post?.requestBody?.content['application/json']).toBeDefined();
      expect(spec.paths['/users'].post?.requestBody?.content['application/json'].example).toBeDefined();
    });

    it('should include security schemes when includeAuth is true', () => {
      const analysis: AnalysisResult = {
        endpoints: [],
        schemas: new Map(),
        authentication: [
          {
            type: 'bearer',
            headerName: 'Authorization',
            scheme: 'bearer',
            endpoints: ['/users'],
          },
        ],
        commonHeaders: [],
        basePaths: [],
        metadata: { totalRequests: 1, uniqueEndpoints: 1, protocols: [], analyzedAt: 0 },
      };

      const spec = service.generateSpec(analysis, { title: 'API', version: '1.0', includeAuth: true });

      expect(spec.components?.securitySchemes).toBeDefined();
      expect(spec.components?.securitySchemes?.bearerAuth).toBeDefined();
      expect(spec.components?.securitySchemes?.bearerAuth.type).toBe('http');
      expect(spec.components?.securitySchemes?.bearerAuth.scheme).toBe('bearer');
    });

    it('should include servers', () => {
      const analysis: AnalysisResult = {
        endpoints: [],
        schemas: new Map(),
        authentication: [],
        commonHeaders: [],
        basePaths: [],
        metadata: { totalRequests: 0, uniqueEndpoints: 0, protocols: [], analyzedAt: 0 },
      };

      const spec = service.generateSpec(analysis, {
        title: 'API',
        version: '1.0',
        servers: [
          { url: 'https://api.example.com', description: 'Production' },
          { url: 'https://staging.example.com', description: 'Staging' },
        ],
      });

      expect(spec.servers).toHaveLength(2);
      expect(spec.servers?.[0].url).toBe('https://api.example.com');
    });

    it('should include tags when groupByTags is true', () => {
      const analysis: AnalysisResult = {
        endpoints: [
          { path: '/users', method: 'GET', tags: ['Users'], pathParameters: [], queryParameters: [], headers: [], responses: {} },
          { path: '/products', method: 'GET', tags: ['Products'], pathParameters: [], queryParameters: [], headers: [], responses: {} },
        ],
        schemas: new Map(),
        authentication: [],
        commonHeaders: [],
        basePaths: [],
        metadata: { totalRequests: 2, uniqueEndpoints: 2, protocols: [], analyzedAt: 0 },
      };

      const spec = service.generateSpec(analysis, { title: 'API', version: '1.0', groupByTags: true });

      expect(spec.tags).toBeDefined();
      expect(spec.tags).toHaveLength(2);
      expect(spec.tags?.find(t => t.name === 'Users')).toBeDefined();
      expect(spec.tags?.find(t => t.name === 'Products')).toBeDefined();
    });
  });

  describe('validateSpec', () => {
    it('should validate valid spec', () => {
      const spec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0.0' },
        paths: {
          '/users': {
            get: {
              responses: {
                '200': { description: 'OK' },
              },
            },
          },
        },
      };

      const result = service.validateSpec(spec);

      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should detect missing title', () => {
      const spec = {
        openapi: '3.0.0',
        info: { title: '', version: '1.0.0' },
        paths: {},
      };

      const result = service.validateSpec(spec);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Spec must have a title');
    });

    it('should detect missing version', () => {
      const spec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '' },
        paths: {},
      };

      const result = service.validateSpec(spec);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Spec must have a version');
    });

    it('should detect missing paths', () => {
      const spec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0.0' },
        paths: {},
      };

      const result = service.validateSpec(spec);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Spec must have at least one path');
    });

    it('should detect operation without responses', () => {
      const spec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0.0' },
        paths: {
          '/users': {
            get: {
              responses: {},
            },
          },
        },
      };

      const result = service.validateSpec(spec);

      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });

  describe('toJSON', () => {
    it('should export spec as JSON', () => {
      const spec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0.0' },
        paths: {},
      };

      const json = service.toJSON(spec);
      const parsed = JSON.parse(json);

      expect(parsed.openapi).toBe('3.0.0');
      expect(parsed.info.title).toBe('API');
    });
  });

  describe('toYAML', () => {
    it('should export spec as YAML', () => {
      const spec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0.0' },
        paths: {},
      };

      const yaml = service.toYAML(spec);

      expect(yaml).toContain('openapi: 3.0.0');
      expect(yaml).toContain('title: API');
      expect(yaml).toContain('version: 1.0.0');
    });
  });

  describe('end-to-end generation', () => {
    it('should generate complete OpenAPI spec', () => {
      const analysis: AnalysisResult = {
        endpoints: [
          {
            path: '/users',
            method: 'GET',
            pathParameters: [],
            queryParameters: [
              { name: 'page', type: 'integer', required: false },
            ],
            headers: [],
            responses: {
              200: {
                description: 'Successful response',
                schema: {
                  type: 'object',
                  properties: {
                    users: { type: 'array', items: { type: 'object' } },
                    total: { type: 'integer' },
                  },
                },
                examples: [],
              },
            },
            tags: ['Users'],
            summary: 'Get users',
            operationId: 'get_users',
          },
          {
            path: '/users',
            method: 'POST',
            pathParameters: [],
            queryParameters: [],
            headers: [],
            requestBody: {
              contentType: 'application/json',
              schema: {
                type: 'object',
                properties: {
                  name: { type: 'string' },
                  email: { type: 'string', format: 'email' },
                },
                required: ['name', 'email'],
              },
              examples: [],
            },
            responses: {
              201: {
                description: 'Created',
                schema: { type: 'object' },
                examples: [],
              },
            },
            tags: ['Users'],
            summary: 'Create user',
            operationId: 'post_users',
          },
        ],
        schemas: new Map(),
        authentication: [
          { type: 'bearer', headerName: 'Authorization', scheme: 'bearer', endpoints: [] },
        ],
        commonHeaders: [],
        basePaths: ['/users'],
        metadata: {
          totalRequests: 4,
          uniqueEndpoints: 2,
          protocols: ['HTTP/1.1'],
          analyzedAt: Date.now(),
        },
      };

      const spec = service.generateSpec(analysis, {
        title: 'User Management API',
        version: '1.0.0',
        description: 'API for managing users',
        servers: [{ url: 'https://api.example.com' }],
        includeExamples: true,
        includeAuth: true,
        groupByTags: true,
      });

      // Validate structure
      expect(spec.openapi).toBe('3.0.0');
      expect(spec.info.title).toBe('User Management API');
      expect(spec.servers).toHaveLength(1);
      expect(spec.paths['/users'].get).toBeDefined();
      expect(spec.paths['/users'].post).toBeDefined();
      expect(spec.components?.securitySchemes).toBeDefined();
      expect(spec.tags).toHaveLength(1);
      expect(spec.security).toBeDefined();

      // Validate spec
      const validation = service.validateSpec(spec);
      expect(validation.valid).toBe(true);
    });
  });
});
