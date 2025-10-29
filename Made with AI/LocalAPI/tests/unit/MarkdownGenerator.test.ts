// Unit tests for MarkdownGenerator
import { MarkdownGenerator } from '../../src/main/services/MarkdownGenerator';
import type { Collection, Request } from '../../src/types/models';

describe('MarkdownGenerator', () => {
  let generator: MarkdownGenerator;

  beforeEach(() => {
    generator = new MarkdownGenerator();
  });

  describe('Collection Documentation', () => {
    test('should generate basic documentation', () => {
      const collection: Collection = {
        id: 'col1',
        name: 'Test API',
        description: 'A test API collection',
        requests: [],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const markdown = generator.generateFromCollection(collection);

      expect(markdown).toContain('# Test API');
      expect(markdown).toContain('A test API collection');
      expect(markdown).toContain('**Total Endpoints:** 0');
    });

    test('should generate documentation with requests', () => {
      const request: Request = {
        id: 'req1',
        name: 'Get Users',
        description: 'Retrieve all users',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com/users',
        headers: [],
        queryParams: [],
        assertions: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const collection: Collection = {
        id: 'col1',
        name: 'Test API',
        requests: [request],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const markdown = generator.generateFromCollection(collection);

      expect(markdown).toContain('Get Users');
      expect(markdown).toContain('Retrieve all users');
      expect(markdown).toContain('GET https://api.example.com/users');
    });

    test('should include table of contents', () => {
      const request: Request = {
        id: 'req1',
        name: 'Get Users',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com/users',
        headers: [],
        queryParams: [],
        assertions: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const collection: Collection = {
        id: 'col1',
        name: 'Test API',
        requests: [request],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const markdown = generator.generateFromCollection(collection, {
        includeTableOfContents: true,
      });

      expect(markdown).toContain('## Table of Contents');
      expect(markdown).toContain('[Get Users]');
    });

    test('should generate cURL examples', () => {
      const request: Request = {
        id: 'req1',
        name: 'Get Users',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com/users',
        headers: [
          { key: 'Authorization', value: 'Bearer token', enabled: true },
        ],
        queryParams: [],
        assertions: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const collection: Collection = {
        id: 'col1',
        name: 'Test API',
        requests: [request],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const markdown = generator.generateFromCollection(collection, {
        includeExamples: true,
      });

      expect(markdown).toContain('curl -X GET');
      expect(markdown).toContain('Authorization: Bearer token');
    });
  });

  describe('Headers and Parameters', () => {
    test('should include headers table', () => {
      const request: Request = {
        id: 'req1',
        name: 'Get Users',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com/users',
        headers: [
          { key: 'Content-Type', value: 'application/json', enabled: true },
          { key: 'Authorization', value: 'Bearer token', enabled: true },
        ],
        queryParams: [],
        assertions: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const collection: Collection = {
        id: 'col1',
        name: 'Test API',
        requests: [request],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const markdown = generator.generateFromCollection(collection, {
        includeHeaders: true,
      });

      expect(markdown).toContain('**Headers:**');
      expect(markdown).toContain('Content-Type');
      expect(markdown).toContain('application/json');
    });

    test('should include query parameters table', () => {
      const request: Request = {
        id: 'req1',
        name: 'Get Users',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com/users',
        headers: [],
        queryParams: [
          { key: 'limit', value: '10', enabled: true },
          { key: 'offset', value: '0', enabled: true },
        ],
        assertions: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const collection: Collection = {
        id: 'col1',
        name: 'Test API',
        requests: [request],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const markdown = generator.generateFromCollection(collection, {
        includeQueryParams: true,
      });

      expect(markdown).toContain('**Query Parameters:**');
      expect(markdown).toContain('limit');
      expect(markdown).toContain('10');
    });
  });
});
