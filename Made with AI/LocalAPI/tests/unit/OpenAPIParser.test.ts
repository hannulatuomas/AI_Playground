// Unit tests for OpenAPIParser
import { OpenAPIParser } from '../../src/main/services/OpenAPIParser';

describe('OpenAPIParser', () => {
  let parser: OpenAPIParser;

  beforeEach(() => {
    parser = new OpenAPIParser();
  });

  describe('OpenAPI 3.x Parsing', () => {
    test('should parse basic OpenAPI 3.0 spec', async () => {
      const spec = {
        openapi: '3.0.0',
        info: {
          title: 'Test API',
          version: '1.0.0',
          description: 'A test API',
        },
        servers: [{ url: 'https://api.example.com' }],
        paths: {
          '/users': {
            get: {
              summary: 'Get users',
              responses: {
                '200': { description: 'Success' },
              },
            },
          },
        },
      };

      const result = await parser.parseFromObject(spec);

      expect(result.info.title).toBe('Test API');
      expect(result.info.version).toBe('1.0.0');
      expect(result.servers).toContain('https://api.example.com');
      expect(result.requests).toHaveLength(1);
      expect(result.requests[0].name).toBe('Get users');
      expect(result.requests[0].method).toBe('GET');
    });

    test('should extract path parameters', async () => {
      const spec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        servers: [{ url: 'https://api.example.com' }],
        paths: {
          '/users/{userId}': {
            get: {
              summary: 'Get user',
              parameters: [
                {
                  name: 'userId',
                  in: 'path',
                  required: true,
                  schema: { type: 'integer', example: 123 },
                },
              ],
              responses: { '200': { description: 'Success' } },
            },
          },
        },
      };

      const result = await parser.parseFromObject(spec);

      // URL should contain the path
      expect(result.requests[0].url).toContain('/users/');
      expect(result.requests[0].name).toBe('Get user');
    });

    test('should extract query parameters', async () => {
      const spec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        servers: [{ url: 'https://api.example.com' }],
        paths: {
          '/users': {
            get: {
              summary: 'Get users',
              parameters: [
                {
                  name: 'limit',
                  in: 'query',
                  required: false,
                  schema: { type: 'integer', default: 10 },
                },
              ],
              responses: { '200': { description: 'Success' } },
            },
          },
        },
      };

      const result = await parser.parseFromObject(spec);

      expect(result.requests[0].queryParams).toHaveLength(1);
      expect(result.requests[0].queryParams[0].key).toBe('limit');
      expect(result.requests[0].queryParams[0].value).toBe('10');
    });

    test('should extract tags', async () => {
      const spec = {
        openapi: '3.0.0',
        info: { title: 'Test', version: '1.0.0' },
        tags: [{ name: 'Users' }, { name: 'Posts' }],
        servers: [{ url: 'https://api.example.com' }],
        paths: {},
      };

      const result = await parser.parseFromObject(spec);

      expect(result.tags).toContain('Users');
      expect(result.tags).toContain('Posts');
    });
  });

  describe('Swagger 2.0 Parsing', () => {
    test('should parse basic Swagger 2.0 spec', async () => {
      const spec = {
        swagger: '2.0',
        info: {
          title: 'Test API',
          version: '1.0.0',
        },
        host: 'api.example.com',
        basePath: '/v1',
        schemes: ['https'],
        paths: {
          '/users': {
            get: {
              summary: 'Get users',
              responses: {
                '200': { description: 'Success' },
              },
            },
          },
        },
      };

      const result = await parser.parseFromObject(spec);

      expect(result.info.title).toBe('Test API');
      expect(result.servers[0]).toBe('https://api.example.com/v1');
      expect(result.requests).toHaveLength(1);
    });
  });

  describe('Collection Creation', () => {
    test('should create collection from parsed API', async () => {
      const spec = {
        openapi: '3.0.0',
        info: {
          title: 'Test API',
          version: '1.0.0',
          description: 'Test description',
        },
        servers: [{ url: 'https://api.example.com' }],
        paths: {
          '/users': {
            get: {
              summary: 'Get users',
              responses: { '200': { description: 'Success' } },
            },
          },
        },
      };

      const parsedAPI = await parser.parseFromObject(spec);
      const collection = parser.createCollectionFromAPI(parsedAPI);

      expect(collection.name).toBe('Test API');
      expect(collection.description).toContain('Test description');
      expect(collection.description).toContain('1.0.0');
      expect(collection.requests).toHaveLength(1);
    });
  });
});
