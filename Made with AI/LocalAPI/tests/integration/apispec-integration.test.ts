/**
 * API Specification Generation Integration Tests
 * 
 * Tests the complete flow from console entries to generated specifications
 */

import { RequestAnalyzerService } from '../../src/main/services/RequestAnalyzerService';
import { OpenAPIGeneratorService } from '../../src/main/services/OpenAPIGeneratorService';
import { AsyncAPIGeneratorService } from '../../src/main/services/AsyncAPIGeneratorService';
import { GraphQLSchemaGeneratorService } from '../../src/main/services/GraphQLSchemaGeneratorService';
import type { ConsoleEntry } from '../../src/main/services/ConsoleService';

describe('API Specification Generation Integration Tests', () => {
  let analyzer: RequestAnalyzerService;
  let openApiGen: OpenAPIGeneratorService;
  let asyncApiGen: AsyncAPIGeneratorService;
  let graphqlGen: GraphQLSchemaGeneratorService;

  beforeEach(() => {
    analyzer = new RequestAnalyzerService();
    openApiGen = new OpenAPIGeneratorService();
    asyncApiGen = new AsyncAPIGeneratorService();
    graphqlGen = new GraphQLSchemaGeneratorService();
  });

  describe('End-to-end OpenAPI generation', () => {
    it('should generate complete OpenAPI spec from HTTP traffic', () => {
      // Simulate captured HTTP traffic
      const entries: ConsoleEntry[] = [
        // GET /users request
        {
          id: '1',
          timestamp: Date.now(),
          type: 'request',
          method: 'GET',
          url: 'https://api.example.com/users?page=1&limit=10',
          headers: {
            'Authorization': 'Bearer token123',
            'Accept': 'application/json',
          },
        },
        // GET /users response
        {
          id: '2',
          timestamp: Date.now(),
          type: 'response',
          status: 200,
          statusText: 'OK',
          headers: { 'Content-Type': 'application/json' },
          body: {
            users: [
              {
                id: 1,
                name: 'John Doe',
                email: 'john@example.com',
                createdAt: '2023-10-31T10:30:00Z',
              },
            ],
            total: 100,
            page: 1,
          },
          requestId: '1',
        },
        // POST /users request
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
            name: 'Jane Smith',
            email: 'jane@example.com',
          },
        },
        // POST /users response
        {
          id: '4',
          timestamp: Date.now(),
          type: 'response',
          status: 201,
          statusText: 'Created',
          body: {
            id: 2,
            name: 'Jane Smith',
            email: 'jane@example.com',
            createdAt: '2023-10-31T11:00:00Z',
          },
          requestId: '3',
        },
        // GET /users/{id} request
        {
          id: '5',
          timestamp: Date.now(),
          type: 'request',
          method: 'GET',
          url: 'https://api.example.com/users/1',
          headers: { 'Authorization': 'Bearer token123' },
        },
        // GET /users/{id} response
        {
          id: '6',
          timestamp: Date.now(),
          type: 'response',
          status: 200,
          body: {
            id: 1,
            name: 'John Doe',
            email: 'john@example.com',
          },
          requestId: '5',
        },
      ];

      // Step 1: Analyze requests
      const analysis = analyzer.analyzeRequests(entries);

      // Verify analysis
      expect(analysis.endpoints).toHaveLength(3);
      expect(analysis.authentication).toHaveLength(1);
      expect(analysis.authentication[0].type).toBe('bearer');

      // Step 2: Generate OpenAPI spec
      const spec = openApiGen.generateSpec(analysis, {
        title: 'User Management API',
        version: '1.0.0',
        description: 'API for managing users',
        servers: [{ url: 'https://api.example.com' }],
        includeExamples: true,
        includeAuth: true,
        groupByTags: true,
      });

      // Verify spec structure
      expect(spec.openapi).toBe('3.0.0');
      expect(spec.info.title).toBe('User Management API');
      expect(spec.servers).toHaveLength(1);

      // Verify paths
      expect(spec.paths['/users']).toBeDefined();
      expect(spec.paths['/users'].get).toBeDefined();
      expect(spec.paths['/users'].post).toBeDefined();
      expect(spec.paths['/users/{id}']).toBeDefined();
      expect(spec.paths['/users/{id}'].get).toBeDefined();

      // Verify query parameters on GET /users
      const getUsersOp = spec.paths['/users'].get!;
      expect(getUsersOp.parameters).toBeDefined();
      const pageParam = getUsersOp.parameters?.find(p => p.name === 'page');
      expect(pageParam).toBeDefined();
      expect(pageParam?.in).toBe('query');

      // Verify path parameter on GET /users/{id}
      const getUserOp = spec.paths['/users/{id}'].get!;
      expect(getUserOp.parameters).toBeDefined();
      const idParam = getUserOp.parameters?.find(p => p.name === 'id');
      expect(idParam).toBeDefined();
      expect(idParam?.in).toBe('path');
      expect(idParam?.required).toBe(true);

      // Verify request body on POST /users
      const createUserOp = spec.paths['/users'].post!;
      expect(createUserOp.requestBody).toBeDefined();
      expect(createUserOp.requestBody?.content['application/json']).toBeDefined();

      // Verify responses
      expect(getUsersOp.responses['200']).toBeDefined();
      expect(createUserOp.responses['201']).toBeDefined();

      // Verify security
      expect(spec.components?.securitySchemes).toBeDefined();
      expect(spec.components?.securitySchemes?.bearerAuth).toBeDefined();

      // Step 3: Validate spec
      const validation = openApiGen.validateSpec(spec);
      expect(validation.valid).toBe(true);
      expect(validation.errors).toHaveLength(0);

      // Step 4: Export
      const json = openApiGen.toJSON(spec);
      expect(json).toBeTruthy();
      expect(JSON.parse(json).openapi).toBe('3.0.0');

      const yaml = openApiGen.toYAML(spec);
      expect(yaml).toContain('openapi: 3.0.0');
    });
  });

  describe('End-to-end AsyncAPI generation', () => {
    it('should generate AsyncAPI spec from WebSocket traffic', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'websocket',
          url: 'wss://api.example.com/chat',
          direction: 'sent',
          eventType: 'chat.message',
          body: {
            type: 'message',
            text: 'Hello',
            userId: 1,
          },
        },
        {
          id: '2',
          timestamp: Date.now(),
          type: 'websocket',
          url: 'wss://api.example.com/chat',
          direction: 'received',
          eventType: 'chat.message',
          body: {
            type: 'message',
            text: 'Hi there',
            userId: 2,
            timestamp: Date.now(),
          },
        },
      ];

      const spec = asyncApiGen.generateSpec(entries, {
        title: 'Chat API',
        version: '1.0.0',
        description: 'Real-time chat API',
        includeExamples: true,
        extractComponents: true,
      });

      expect(spec.asyncapi).toBe('2.6.0');
      expect(spec.info.title).toBe('Chat API');
      expect(spec.servers.wssServer).toBeDefined();
      expect(spec.channels['chat.message']).toBeDefined();
      expect(spec.channels['chat.message'].publish).toBeDefined();
      expect(spec.channels['chat.message'].subscribe).toBeDefined();

      const validation = asyncApiGen.validateSpec(spec);
      expect(validation.valid).toBe(true);
    });
  });

  describe('End-to-end GraphQL generation', () => {
    it('should generate GraphQL schema from GraphQL traffic', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'request',
          url: 'https://api.example.com/graphql',
          method: 'POST',
          body: {
            query: `
              query GetUser($id: ID!) {
                user(id: $id) {
                  id
                  name
                  email
                }
              }
            `,
            variables: { id: '1' },
          },
        },
        {
          id: '2',
          timestamp: Date.now(),
          type: 'response',
          body: {
            data: {
              user: {
                id: '1',
                name: 'John Doe',
                email: 'john@example.com',
              },
            },
          },
          requestId: '1',
        },
      ];

      const schema = graphqlGen.generateSchema(entries);

      expect(schema.queries.length).toBeGreaterThan(0);
      expect(schema.types.length).toBeGreaterThan(0);

      const sdl = graphqlGen.generateSDL(schema);

      expect(sdl).toBeTruthy();
      expect(sdl).toContain('type Query');

      const validation = graphqlGen.validateSchema(schema);
      expect(validation.valid).toBe(true);
    });
  });

  describe('Schema inference accuracy', () => {
    it('should correctly infer complex nested schemas', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'request',
          method: 'GET',
          url: 'https://api.example.com/data',
        },
        {
          id: '2',
          timestamp: Date.now(),
          type: 'response',
          status: 200,
          body: {
            user: {
              id: 1,
              profile: {
                name: 'John',
                email: 'john@example.com',
                avatar: 'https://example.com/avatar.jpg',
              },
              tags: ['admin', 'verified'],
              metadata: {
                createdAt: '2023-10-31T10:30:00Z',
                lastLogin: '2023-11-01T09:00:00Z',
              },
            },
            stats: {
              posts: 42,
              followers: 1337,
              following: 256,
            },
          },
          requestId: '1',
        },
      ];

      const analysis = analyzer.analyzeRequests(entries);

      const endpoint = analysis.endpoints[0];
      const responseSchema = endpoint.responses[200].schema;

      expect(responseSchema.type).toBe('object');
      expect(responseSchema.properties).toBeDefined();
      expect(responseSchema.properties!.user.type).toBe('object');
      expect(responseSchema.properties!.user.properties!.profile.type).toBe('object');
      expect(responseSchema.properties!.user.properties!.profile.properties!.email.format).toBe('email');
      expect(responseSchema.properties!.user.properties!.profile.properties!.avatar.format).toBe('uri');
      expect(responseSchema.properties!.user.properties!.tags.type).toBe('array');
      expect(responseSchema.properties!.user.properties!.metadata.properties!.createdAt.format).toBe('date-time');
    });
  });

  describe('Schema merging', () => {
    it('should merge schemas from multiple similar requests', () => {
      const entries: ConsoleEntry[] = [
        // First request with partial data
        {
          id: '1',
          timestamp: Date.now(),
          type: 'request',
          method: 'GET',
          url: 'https://api.example.com/users/1',
        },
        {
          id: '2',
          timestamp: Date.now(),
          type: 'response',
          status: 200,
          body: {
            id: 1,
            name: 'John',
          },
          requestId: '1',
        },
        // Second request with additional fields
        {
          id: '3',
          timestamp: Date.now(),
          type: 'request',
          method: 'GET',
          url: 'https://api.example.com/users/2',
        },
        {
          id: '4',
          timestamp: Date.now(),
          type: 'response',
          status: 200,
          body: {
            id: 2,
            name: 'Jane',
            email: 'jane@example.com',
            role: 'admin',
          },
          requestId: '3',
        },
      ];

      const analysis = analyzer.analyzeRequests(entries);

      expect(analysis.endpoints).toHaveLength(1);
      const endpoint = analysis.endpoints[0];
      const schema = endpoint.responses[200].schema;

      // Should have merged all properties
      expect(schema.properties).toHaveProperty('id');
      expect(schema.properties).toHaveProperty('name');
      expect(schema.properties).toHaveProperty('email');
      expect(schema.properties).toHaveProperty('role');

      // Only 'id' and 'name' are in both responses, so only they should be required
      expect(schema.required).toContain('id');
      expect(schema.required).toContain('name');
      expect(schema.required).not.toContain('email');
      expect(schema.required).not.toContain('role');
    });
  });
});
