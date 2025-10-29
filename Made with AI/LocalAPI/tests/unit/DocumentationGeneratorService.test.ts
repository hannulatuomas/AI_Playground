/**
 * DocumentationGeneratorService Unit Tests
 */

import { DocumentationGeneratorService } from '../../src/main/services/DocumentationGeneratorService';
import type { OpenAPISpec } from '../../src/main/services/OpenAPIGeneratorService';

describe('DocumentationGeneratorService', () => {
  let service: DocumentationGeneratorService;

  beforeEach(() => {
    service = new DocumentationGeneratorService();
  });

  describe('generateDocumentation', () => {
    it('should generate HTML documentation with default theme', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: {
          title: 'Test API',
          version: '1.0.0',
          description: 'Test description',
        },
        paths: {
          '/users': {
            get: {
              summary: 'Get users',
              responses: {
                '200': {
                  description: 'Success',
                },
              },
            },
          },
        },
      };

      const doc = service.generateDocumentation(spec);

      expect(doc.html).toContain('<!DOCTYPE html>');
      expect(doc.html).toContain('Test API');
      expect(doc.html).toContain('/users');
      expect(doc.css).toBeTruthy();
    });

    it('should include CSS with modern theme by default', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
      };

      const doc = service.generateDocumentation(spec);

      expect(doc.css).toContain('--accent-color: #2ea44f');
    });

    it('should use light theme when specified', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
      };

      const doc = service.generateDocumentation(spec, { theme: 'light' });

      expect(doc.css).toContain('--accent-color: #0366d6');
    });

    it('should use dark theme when specified', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
      };

      const doc = service.generateDocumentation(spec, { theme: 'dark' });

      expect(doc.css).toContain('--bg-color: #0d1117');
    });

    it('should use classic theme when specified', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
      };

      const doc = service.generateDocumentation(spec, { theme: 'classic' });

      expect(doc.css).toContain('--accent-color: #007bff');
    });

    it('should include JavaScript when includeExplorer is true', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
      };

      const doc = service.generateDocumentation(spec, { includeExplorer: true });

      expect(doc.js).toBeTruthy();
      expect(doc.js).toContain('Try It Out');
    });

    it('should not include JavaScript when includeExplorer is false', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
      };

      const doc = service.generateDocumentation(spec, { includeExplorer: false });

      expect(doc.js).toBeUndefined();
    });

    it('should include custom CSS when provided', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
      };

      const customCss = '.custom { color: red; }';
      const doc = service.generateDocumentation(spec, { customCss });

      expect(doc.css).toContain(customCss);
    });

    it('should override title and version from options', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'Original', version: '1.0' },
        paths: {},
      };

      const doc = service.generateDocumentation(spec, {
        title: 'Custom Title',
        version: '2.0',
      });

      expect(doc.html).toContain('Custom Title');
      expect(doc.html).toContain('v2.0');
      expect(doc.html).not.toContain('Original');
    });
  });

  describe('authentication documentation', () => {
    it('should include authentication section when includeAuth is true', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
        components: {
          securitySchemes: {
            bearerAuth: {
              type: 'http',
              scheme: 'bearer',
            },
          },
        },
      };

      const doc = service.generateDocumentation(spec, { includeAuth: true });

      expect(doc.html).toContain('Authentication');
      expect(doc.html).toContain('bearerAuth');
      expect(doc.html).toContain('bearer');
    });

    it('should not include authentication section when includeAuth is false', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
        components: {
          securitySchemes: {
            bearerAuth: {
              type: 'http',
              scheme: 'bearer',
            },
          },
        },
      };

      const doc = service.generateDocumentation(spec, { includeAuth: false });

      expect(doc.html).not.toContain('id="authentication"');
      expect(doc.html).not.toContain('bearerAuth');
    });
  });

  describe('examples in documentation', () => {
    it('should include examples when includeExamples is true', () => {
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

      const doc = service.generateDocumentation(spec, { includeExamples: true });

      expect(doc.html).toContain('&quot;name&quot;: &quot;John&quot;');
    });

    it('should not include examples when includeExamples is false', () => {
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

      const doc = service.generateDocumentation(spec, { includeExamples: false });

      expect(doc.html).not.toContain('&quot;name&quot;: &quot;John&quot;');
    });
  });

  describe('changelog', () => {
    it('should include changelog when provided', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
      };

      const changelog = [
        {
          version: '1.0.0',
          date: '2025-01-01',
          changes: ['Initial release', 'Added users endpoint'],
        },
      ];

      const doc = service.generateDocumentation(spec, {
        includeChangelog: true,
        changelog,
      });

      expect(doc.html).toContain('Changelog');
      expect(doc.html).toContain('1.0.0');
      expect(doc.html).toContain('Initial release');
    });
  });

  describe('endpoints documentation', () => {
    it('should document GET endpoint', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {
          '/users': {
            get: {
              summary: 'Get all users',
              responses: {
                '200': {
                  description: 'Success',
                },
              },
            },
          },
        },
      };

      const doc = service.generateDocumentation(spec);

      expect(doc.html).toContain('GET');
      expect(doc.html).toContain('/users');
      expect(doc.html).toContain('Get all users');
    });

    it('should document POST endpoint with request body', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {
          '/users': {
            post: {
              summary: 'Create user',
              requestBody: {
                content: {
                  'application/json': {
                    schema: { type: 'object' },
                  },
                },
              },
              responses: {
                '201': {
                  description: 'Created',
                },
              },
            },
          },
        },
      };

      const doc = service.generateDocumentation(spec);

      expect(doc.html).toContain('POST');
      expect(doc.html).toContain('Request Body');
    });

    it('should document parameters', () => {
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
                },
              ],
              responses: {},
            },
          },
        },
      };

      const doc = service.generateDocumentation(spec);

      expect(doc.html).toContain('Parameters');
      expect(doc.html).toContain('id');
      expect(doc.html).toContain('path');
    });
  });

  describe('responsive design', () => {
    it('should include responsive CSS', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
      };

      const doc = service.generateDocumentation(spec);

      expect(doc.css).toContain('@media (max-width: 1024px)');
      expect(doc.css).toContain('@media (max-width: 768px)');
    });
  });

  describe('HTML escaping', () => {
    it('should escape HTML in titles', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: '<script>alert("xss")</script>', version: '1.0' },
        paths: {},
      };

      const doc = service.generateDocumentation(spec);

      expect(doc.html).not.toContain('<script>');
      expect(doc.html).toContain('&lt;script&gt;');
    });
  });

  describe('navigation', () => {
    it('should generate sidebar navigation', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {
          '/users': { get: { responses: {} } },
          '/products': { get: { responses: {} } },
        },
      };

      const doc = service.generateDocumentation(spec);

      expect(doc.html).toContain('sidebar');
      expect(doc.html).toContain('Overview');
      expect(doc.html).toContain('/users');
      expect(doc.html).toContain('/products');
    });
  });

  describe('servers', () => {
    it('should display server URLs', () => {
      const spec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0' },
        paths: {},
        servers: [
          { url: 'https://api.example.com', description: 'Production' },
          { url: 'https://staging.example.com', description: 'Staging' },
        ],
      };

      const doc = service.generateDocumentation(spec);

      expect(doc.html).toContain('Base URLs');
      expect(doc.html).toContain('https://api.example.com');
      expect(doc.html).toContain('https://staging.example.com');
    });
  });
});
