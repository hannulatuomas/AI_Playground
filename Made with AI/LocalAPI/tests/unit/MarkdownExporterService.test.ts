/**
 * MarkdownExporterService Unit Tests
 */

import { MarkdownExporterService } from '../../src/main/services/MarkdownExporterService';
import type { OpenAPISpec } from '../../src/main/services/OpenAPIGeneratorService';

describe('MarkdownExporterService', () => {
  let service: MarkdownExporterService;

  beforeEach(() => {
    service = new MarkdownExporterService();
  });

  describe('exportToMarkdown', () => {
    it('should export basic spec to markdown', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: {
          title: 'Test API',
          version: '1.0.0',
          description: 'Test description',
        },
        paths: {},
      };

      const markdown = service.exportToMarkdown(spec);

      expect(markdown).toContain('# Test API');
      expect(markdown).toContain('**Version:** 1.0.0');
      expect(markdown).toContain('Test description');
    });

    it('should include table of contents by default', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {
          '/users': { get: { responses: {} } },
        },
      };

      const markdown = service.exportToMarkdown(spec);

      expect(markdown).toContain('## Table of Contents');
      expect(markdown).toContain('- [Overview](#overview)');
    });

    it('should skip table of contents when disabled', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
      };

      const markdown = service.exportToMarkdown(spec, { includeTableOfContents: false });

      expect(markdown).not.toContain('## Table of Contents');
    });

    it('should document servers', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
        servers: [
          { url: 'https://api.example.com', description: 'Production' },
        ],
      };

      const markdown = service.exportToMarkdown(spec);

      expect(markdown).toContain('### Base URLs');
      expect(markdown).toContain('https://api.example.com');
      expect(markdown).toContain('Production');
    });

    it('should document authentication', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
        components: {
          securitySchemes: {
            bearerAuth: {
              type: 'http',
              scheme: 'bearer',
              bearerFormat: 'JWT',
            },
          },
        },
      };

      const markdown = service.exportToMarkdown(spec);

      expect(markdown).toContain('## Authentication');
      expect(markdown).toContain('### bearerAuth');
      expect(markdown).toContain('**Type:** http');
      expect(markdown).toContain('**Scheme:** bearer');
      expect(markdown).toContain('**Bearer Format:** JWT');
    });

    it('should document endpoints', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {
          '/users': {
            get: {
              summary: 'Get all users',
              description: 'Returns a list of users',
              responses: {
                '200': {
                  description: 'Success',
                },
              },
            },
          },
        },
      };

      const markdown = service.exportToMarkdown(spec);

      expect(markdown).toContain('## Endpoints');
      expect(markdown).toContain('### /users');
      expect(markdown).toContain('#### GET /users');
      expect(markdown).toContain('**Summary:** Get all users');
      expect(markdown).toContain('Returns a list of users');
    });

    it('should document parameters in table format', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {
          '/users/{id}': {
            get: {
              parameters: [
                {
                  name: 'id',
                  in: 'path',
                  required: true,
                  schema: { type: 'string' },
                  description: 'User ID',
                },
                {
                  name: 'include',
                  in: 'query',
                  required: false,
                  schema: { type: 'string' },
                },
              ],
              responses: {},
            },
          },
        },
      };

      const markdown = service.exportToMarkdown(spec);

      expect(markdown).toContain('**Parameters:**');
      expect(markdown).toContain('| Name | In | Type | Required | Description |');
      expect(markdown).toContain('| `id` | path | `string` | Yes | User ID |');
      expect(markdown).toContain('| `include` | query | `string` | No |');
    });

    it('should include examples when enabled', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {
          '/users': {
            post: {
              requestBody: {
                content: {
                  'application/json': {
                    schema: { type: 'object' },
                    example: { name: 'John', email: 'john@example.com' },
                  },
                },
              },
              responses: {},
            },
          },
        },
      };

      const markdown = service.exportToMarkdown(spec, { includeExamples: true });

      expect(markdown).toContain('```json');
      expect(markdown).toContain('"name": "John"');
      expect(markdown).toContain('"email": "john@example.com"');
    });

    it('should not include examples when disabled', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {
          '/users': {
            post: {
              requestBody: {
                content: {
                  'application/json': {
                    schema: { type: 'object' },
                    example: { name: 'John' },
                  },
                },
              },
              responses: {},
            },
          },
        },
      };

      const markdown = service.exportToMarkdown(spec, { includeExamples: false });

      expect(markdown).not.toContain('```json');
      expect(markdown).not.toContain('"name": "John"');
    });

    it('should document responses', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {
          '/users': {
            get: {
              responses: {
                '200': {
                  description: 'Success',
                },
                '404': {
                  description: 'Not found',
                },
              },
            },
          },
        },
      };

      const markdown = service.exportToMarkdown(spec);

      expect(markdown).toContain('**Responses:**');
      expect(markdown).toContain('**200** - Success');
      expect(markdown).toContain('**404** - Not found');
    });

    it('should include schemas when enabled', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
        components: {
          schemas: {
            User: {
              type: 'object',
              properties: {
                id: { type: 'string' },
                name: { type: 'string' },
              },
            },
          },
        },
      };

      const markdown = service.exportToMarkdown(spec, { includeSchemas: true });

      expect(markdown).toContain('## Schemas');
      expect(markdown).toContain('### User');
      expect(markdown).toContain('"type": "object"');
    });

    it('should not include schemas when disabled', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
        components: {
          schemas: {
            User: { type: 'object' },
          },
        },
      };

      const markdown = service.exportToMarkdown(spec, { includeSchemas: false });

      expect(markdown).not.toContain('## Schemas');
    });

    it('should handle contact information', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: {
          title: 'API',
          version: '1.0',
          contact: {
            name: 'Support Team',
            email: 'support@example.com',
            url: 'https://example.com/support',
          },
        },
        paths: {},
      };

      const markdown = service.exportToMarkdown(spec);

      expect(markdown).toContain('### Contact');
      expect(markdown).toContain('**Name:** Support Team');
      expect(markdown).toContain('**Email:** support@example.com');
      expect(markdown).toContain('**URL:** https://example.com/support');
    });
  });
});
