/**
 * ChangelogGeneratorService Unit Tests
 */

import { ChangelogGeneratorService } from '../../src/main/services/ChangelogGeneratorService';
import type { OpenAPISpec } from '../../src/main/services/OpenAPIGeneratorService';

describe('ChangelogGeneratorService', () => {
  let service: ChangelogGeneratorService;

  beforeEach(() => {
    service = new ChangelogGeneratorService();
  });

  describe('generateChangelog', () => {
    it('should detect new endpoints', () => {
      const oldSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0.0' },
        paths: {},
      };

      const newSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '2.0.0' },
        paths: {
          '/users': {
            get: { responses: {} },
          },
        },
      };

      const changelog = service.generateChangelog(oldSpec, newSpec);

      expect(changelog.version).toBe('2.0.0');
      expect(changelog.changes).toHaveLength(1);
      expect(changelog.changes[0].type).toBe('added');
      expect(changelog.changes[0].category).toBe('endpoint');
      expect(changelog.changes[0].description).toContain('GET /users');
    });

    it('should detect removed endpoints as breaking', () => {
      const oldSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0.0' },
        paths: {
          '/users': {
            get: { responses: {} },
          },
        },
      };

      const newSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '2.0.0' },
        paths: {},
      };

      const changelog = service.generateChangelog(oldSpec, newSpec);

      expect(changelog.changes).toHaveLength(1);
      expect(changelog.changes[0].type).toBe('removed');
      expect(changelog.changes[0].breaking).toBe(true);
    });

    it('should detect new methods on existing paths', () => {
      const oldSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0.0' },
        paths: {
          '/users': {
            get: { responses: {} },
          },
        },
      };

      const newSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '2.0.0' },
        paths: {
          '/users': {
            get: { responses: {} },
            post: { responses: {} },
          },
        },
      };

      const changelog = service.generateChangelog(oldSpec, newSpec);

      const addedMethod = changelog.changes.find(c => c.type === 'added' && c.method === 'post');
      expect(addedMethod).toBeDefined();
      expect(addedMethod!.description).toContain('POST /users');
    });

    it('should detect new required parameters as breaking', () => {
      const oldSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0.0' },
        paths: {
          '/users': {
            get: {
              parameters: [],
              responses: {},
            },
          },
        },
      };

      const newSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '2.0.0' },
        paths: {
          '/users': {
            get: {
              parameters: [
                {
                  name: 'filter',
                  in: 'query',
                  required: true,
                  schema: { type: 'string' },
                },
              ],
              responses: {},
            },
          },
        },
      };

      const changelog = service.generateChangelog(oldSpec, newSpec);

      const newParam = changelog.changes.find(c => c.type === 'added' && c.category === 'parameter');
      expect(newParam).toBeDefined();
      expect(newParam!.breaking).toBe(true);
    });

    it('should detect parameter becoming required as breaking', () => {
      const oldSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0.0' },
        paths: {
          '/users': {
            get: {
              parameters: [
                {
                  name: 'filter',
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

      const newSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '2.0.0' },
        paths: {
          '/users': {
            get: {
              parameters: [
                {
                  name: 'filter',
                  in: 'query',
                  required: true,
                  schema: { type: 'string' },
                },
              ],
              responses: {},
            },
          },
        },
      };

      const changelog = service.generateChangelog(oldSpec, newSpec);

      const changedParam = changelog.changes.find(c => c.type === 'changed' && c.category === 'parameter');
      expect(changedParam).toBeDefined();
      expect(changedParam!.breaking).toBe(true);
      expect(changedParam!.description).toContain('now required');
    });

    it('should detect new response codes', () => {
      const oldSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0.0' },
        paths: {
          '/users': {
            get: {
              responses: {
                '200': { description: 'Success' },
              },
            },
          },
        },
      };

      const newSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '2.0.0' },
        paths: {
          '/users': {
            get: {
              responses: {
                '200': { description: 'Success' },
                '404': { description: 'Not found' },
              },
            },
          },
        },
      };

      const changelog = service.generateChangelog(oldSpec, newSpec);

      const newResponse = changelog.changes.find(c => c.type === 'added' && c.category === 'response');
      expect(newResponse).toBeDefined();
      expect(newResponse!.description).toContain('404');
    });

    it('should detect removed schemas as breaking', () => {
      const oldSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0.0' },
        paths: {},
        components: {
          schemas: {
            User: { type: 'object' },
          },
        },
      };

      const newSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '2.0.0' },
        paths: {},
        components: {
          schemas: {},
        },
      };

      const changelog = service.generateChangelog(oldSpec, newSpec);

      const removedSchema = changelog.changes.find(c => c.type === 'removed' && c.category === 'schema');
      expect(removedSchema).toBeDefined();
      expect(removedSchema!.breaking).toBe(true);
    });

    it('should detect new security schemes', () => {
      const oldSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0.0' },
        paths: {},
      };

      const newSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '2.0.0' },
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

      const changelog = service.generateChangelog(oldSpec, newSpec);

      const newAuth = changelog.changes.find(c => c.type === 'added' && c.category === 'auth');
      expect(newAuth).toBeDefined();
      expect(newAuth!.description).toContain('bearerAuth');
    });

    it('should handle multiple changes in one spec', () => {
      const oldSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '1.0.0' },
        paths: {
          '/users': {
            get: { responses: {} },
          },
        },
      };

      const newSpec: OpenAPISpec = {
        openapi: '3.0.0',
        info: { title: 'API', version: '2.0.0' },
        paths: {
          '/users': {
            get: { responses: {} },
            post: { responses: {} },
          },
          '/products': {
            get: { responses: {} },
          },
        },
      };

      const changelog = service.generateChangelog(oldSpec, newSpec);

      expect(changelog.changes.length).toBeGreaterThan(0);
      expect(changelog.changes.some(c => c.type === 'added')).toBe(true);
    });
  });

  describe('formatAsMarkdown', () => {
    it('should format changelog as markdown', () => {
      const changelog = {
        version: '2.0.0',
        date: '2025-01-01',
        changes: [
          {
            type: 'added' as const,
            category: 'endpoint' as const,
            description: 'New endpoint: GET /users',
          },
          {
            type: 'removed' as const,
            category: 'endpoint' as const,
            description: 'Removed endpoint: DELETE /old',
            breaking: true,
          },
        ],
      };

      const markdown = service.formatAsMarkdown(changelog);

      expect(markdown).toContain('## [2.0.0] - 2025-01-01');
      expect(markdown).toContain('### Added');
      expect(markdown).toContain('New endpoint: GET /users');
      expect(markdown).toContain('### Removed');
      expect(markdown).toContain('**[BREAKING]**');
    });
  });

  describe('getBreakingChanges', () => {
    it('should filter only breaking changes', () => {
      const changelog = {
        version: '2.0.0',
        date: '2025-01-01',
        changes: [
          {
            type: 'added' as const,
            category: 'endpoint' as const,
            description: 'New endpoint',
            breaking: false,
          },
          {
            type: 'removed' as const,
            category: 'endpoint' as const,
            description: 'Removed endpoint',
            breaking: true,
          },
          {
            type: 'changed' as const,
            category: 'parameter' as const,
            description: 'Parameter now required',
            breaking: true,
          },
        ],
      };

      const breaking = service.getBreakingChanges(changelog);

      expect(breaking).toHaveLength(2);
      expect(breaking.every(c => c.breaking)).toBe(true);
    });
  });
});
