/**
 * GraphQLSchemaGeneratorService Unit Tests
 */

import { GraphQLSchemaGeneratorService } from '../../src/main/services/GraphQLSchemaGeneratorService';
import type { ConsoleEntry } from '../../src/main/services/ConsoleService';

describe('GraphQLSchemaGeneratorService', () => {
  let service: GraphQLSchemaGeneratorService;

  beforeEach(() => {
    service = new GraphQLSchemaGeneratorService();
  });

  describe('generateSchema', () => {
    it('should detect queries from GraphQL requests', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'request',
          url: 'https://api.example.com/graphql',
          body: {
            query: 'query GetUsers { users { id name } }',
          },
        },
      ];

      const schema = service.generateSchema(entries);

      expect(schema.queries.length).toBeGreaterThan(0);
      expect(schema.queries[0].name).toBe('GetUsers');
    });

    it('should detect mutations from GraphQL requests', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'request',
          url: 'https://api.example.com/graphql',
          body: {
            query: 'mutation CreateUser($name: String!) { createUser(name: $name) { id } }',
          },
        },
      ];

      const schema = service.generateSchema(entries);

      expect(schema.mutations.length).toBeGreaterThan(0);
      expect(schema.mutations[0].name).toBe('CreateUser');
    });

    it('should infer types from responses', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'request',
          url: 'https://api.example.com/graphql',
          body: {
            query: 'query { user { id name email } }',
          },
        },
        {
          id: '2',
          timestamp: Date.now(),
          type: 'response',
          body: {
            data: {
              user: {
                id: '123',
                name: 'John',
                email: 'john@example.com',
              },
            },
          },
          requestId: '1',
        },
      ];

      const schema = service.generateSchema(entries);

      expect(schema.types.length).toBeGreaterThan(0);
      const userType = schema.types.find(t => t.name === 'User');
      expect(userType).toBeDefined();
    });

    it('should return empty schema for non-GraphQL entries', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'request',
          url: 'https://api.example.com/users',
        },
      ];

      const schema = service.generateSchema(entries);

      expect(schema.queries).toHaveLength(0);
      expect(schema.mutations).toHaveLength(0);
    });
  });

  describe('generateSDL', () => {
    it('should generate SDL from schema', () => {
      const schema = {
        types: [
          {
            name: 'User',
            kind: 'OBJECT' as const,
            fields: {
              id: { name: 'id', type: 'ID!' },
              name: { name: 'name', type: 'String' },
            },
          },
        ],
        queries: [
          {
            name: 'getUser',
            returnType: 'User',
            args: { id: { type: 'ID!' } },
          },
        ],
        mutations: [],
        subscriptions: [],
      };

      const sdl = service.generateSDL(schema);

      expect(sdl).toContain('type User');
      expect(sdl).toContain('id: ID!');
      expect(sdl).toContain('name: String');
      expect(sdl).toContain('type Query');
      expect(sdl).toContain('getUser');
    });

    it('should handle empty schema', () => {
      const schema = {
        types: [],
        queries: [],
        mutations: [],
        subscriptions: [],
      };

      const sdl = service.generateSDL(schema);

      expect(sdl).toBeDefined();
      expect(typeof sdl).toBe('string');
    });
  });

  describe('validateSchema', () => {
    it('should validate schema with queries', () => {
      const schema = {
        types: [],
        queries: [{ name: 'test', returnType: 'String' }],
        mutations: [],
        subscriptions: [],
      };

      const result = service.validateSchema(schema);
      expect(result.valid).toBe(true);
    });

    it('should detect empty schema', () => {
      const schema = {
        types: [],
        queries: [],
        mutations: [],
        subscriptions: [],
      };

      const result = service.validateSchema(schema);
      expect(result.valid).toBe(false);
    });
  });
});
