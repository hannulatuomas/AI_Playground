import { GraphQLService } from '../../src/main/services/GraphQLService';

describe('GraphQLService', () => {
  let service: GraphQLService;

  beforeEach(() => {
    service = new GraphQLService();
  });

  describe('Query Validation', () => {
    test('should validate correct GraphQL query', () => {
      const query = `
        query GetUser {
          user(id: "1") {
            id
            name
          }
        }
      `;

      const result = service.validateQuery(query);
      expect(result.valid).toBe(true);
    });

    test('should detect invalid GraphQL query', () => {
      const query = 'invalid query {';

      const result = service.validateQuery(query);
      expect(result.valid).toBe(false);
      expect(result.errors).toBeDefined();
    });
  });

  describe('Variable Extraction', () => {
    test('should extract variables from query', () => {
      const query = `
        query GetUser($id: ID!, $includeEmail: Boolean) {
          user(id: $id, includeEmail: $includeEmail) {
            id
            name
          }
        }
      `;

      const variables = service.extractVariables(query);
      expect(variables).toContain('id');
      expect(variables).toContain('includeEmail');
      expect(variables).toHaveLength(2);
    });

    test('should return empty array for query without variables', () => {
      const query = `
        query {
          users {
            id
          }
        }
      `;

      const variables = service.extractVariables(query);
      expect(variables).toHaveLength(0);
    });
  });

  describe('Query Template Generation', () => {
    test('should generate query template', () => {
      const operation = {
        name: 'getUser',
        type: 'User',
        args: [
          { name: 'id', type: 'ID!' },
          { name: 'includeEmail', type: 'Boolean' }
        ]
      };

      const template = service.generateQueryTemplate(operation, 'query');
      
      expect(template).toContain('query getUser');
      expect(template).toContain('$id: ID!');
      expect(template).toContain('$includeEmail: Boolean');
      expect(template).toContain('getUser(id: $id, includeEmail: $includeEmail)');
    });

    test('should generate mutation template', () => {
      const operation = {
        name: 'createUser',
        type: 'User',
        args: [
          { name: 'name', type: 'String!' }
        ]
      };

      const template = service.generateQueryTemplate(operation, 'mutation');
      
      expect(template).toContain('mutation createUser');
      expect(template).toContain('$name: String!');
    });
  });

  describe('Example Variables', () => {
    test('should generate example variables', () => {
      const operation = {
        name: 'getUser',
        type: 'User',
        args: [
          { name: 'id', type: 'ID!' },
          { name: 'age', type: 'Int' },
          { name: 'active', type: 'Boolean' }
        ]
      };

      const variables = service.generateExampleVariables(operation);
      
      expect(variables).toHaveProperty('id');
      expect(variables).toHaveProperty('age');
      expect(variables).toHaveProperty('active');
      expect(typeof variables.age).toBe('number');
      expect(typeof variables.active).toBe('boolean');
    });
  });
});
