// GraphQL Schema Importer
import type {
  Importer,
  ImportExportFormat,
  ImportExportOptions,
  ImportResult,
} from '../../../types/import-export';
import type { Collection, Request, RequestBody } from '../../../types/models';

/**
 * GraphQL Schema Importer
 * Imports GraphQL schemas and generates query/mutation requests
 */
export class GraphQLImporter implements Importer {
  readonly format: ImportExportFormat = 'graphql-schema';
  readonly name = 'GraphQL Schema';
  readonly description = 'Import GraphQL schema definitions';
  readonly fileExtensions = ['.graphql', '.gql'];

  canImport(content: string): boolean {
    const trimmed = content.trim();
    return (
      trimmed.includes('type Query') ||
      trimmed.includes('type Mutation') ||
      trimmed.includes('type Subscription') ||
      trimmed.includes('schema {')
    );
  }

  async import(
    content: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const collection: Collection = {
        id: `col-${Date.now()}`,
        name: 'GraphQL API',
        description: 'Imported from GraphQL schema',
        requests: [],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const requests: Request[] = [];

      // Parse schema
      const queries = this.extractOperations(content, 'Query');
      const mutations = this.extractOperations(content, 'Mutation');
      const subscriptions = this.extractOperations(content, 'Subscription');

      // Create requests for queries
      for (const query of queries) {
        requests.push(this.createRequest(query, 'query', collection.id));
      }

      // Create requests for mutations
      for (const mutation of mutations) {
        requests.push(this.createRequest(mutation, 'mutation', collection.id));
      }

      // Create requests for subscriptions
      for (const subscription of subscriptions) {
        requests.push(this.createRequest(subscription, 'subscription', collection.id));
      }

      console.log(`[GraphQLImporter] Imported ${requests.length} GraphQL operations`);

      return {
        success: true,
        collections: [collection],
        requests,
        metadata: {
          format: this.format,
          itemCount: 1 + requests.length,
          importedAt: new Date(),
        },
      };
    } catch (error) {
      console.error('[GraphQLImporter] Import error:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to import GraphQL schema',
        ],
      };
    }
  }

  private extractOperations(schema: string, typeName: string): Array<{ name: string; fields: string; args: string }> {
    const operations: Array<{ name: string; fields: string; args: string }> = [];
    
    // Find the type definition
    const typeRegex = new RegExp(`type\\s+${typeName}\\s*{([^}]*)}`, 's');
    const match = schema.match(typeRegex);
    
    if (!match) return operations;

    const typeBody = match[1];
    
    // Extract each operation
    const operationRegex = /(\w+)\s*(\([^)]*\))?\s*:\s*([^\n]+)/g;
    let operationMatch;

    while ((operationMatch = operationRegex.exec(typeBody)) !== null) {
      const name = operationMatch[1];
      const args = operationMatch[2] || '';
      const returnType = operationMatch[3].trim();

      // Try to infer fields from return type
      const fields = this.inferFields(returnType, schema);

      operations.push({ name, fields, args });
    }

    return operations;
  }

  private inferFields(returnType: string, schema: string): string {
    // Remove array/non-null markers
    const cleanType = returnType.replace(/[\[\]!]/g, '');

    // Check if it's a custom type
    const typeRegex = new RegExp(`type\\s+${cleanType}\\s*{([^}]*)}`, 's');
    const match = schema.match(typeRegex);

    if (match) {
      const typeBody = match[1];
      const fieldRegex = /(\w+)\s*:\s*([^\n]+)/g;
      const fields: string[] = [];
      let fieldMatch;

      while ((fieldMatch = fieldRegex.exec(typeBody)) !== null) {
        const fieldName = fieldMatch[1];
        const fieldType = fieldMatch[2].trim();
        
        // Only include scalar fields for simplicity
        if (this.isScalarType(fieldType)) {
          fields.push(fieldName);
        }
      }

      return fields.join('\n    ');
    }

    return 'id';
  }

  private isScalarType(type: string): boolean {
    const cleanType = type.replace(/[\[\]!]/g, '');
    const scalars = ['String', 'Int', 'Float', 'Boolean', 'ID'];
    return scalars.includes(cleanType);
  }

  private createRequest(
    operation: { name: string; fields: string; args: string },
    operationType: 'query' | 'mutation' | 'subscription',
    collectionId: string
  ): Request {
    // Generate GraphQL query/mutation
    const argsStr = operation.args ? operation.args.replace(/:/g, ':') : '';
    const graphqlQuery = `${operationType} {
  ${operation.name}${argsStr} {
    ${operation.fields || 'id'}
  }
}`;

    const body: RequestBody = {
      type: 'graphql' as const,
      content: JSON.stringify({
        query: graphqlQuery,
        variables: {},
      }, null, 2),
    };

    return {
      id: `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: `${operationType}: ${operation.name}`,
      description: `GraphQL ${operationType} operation`,
      protocol: 'GraphQL' as const,
      method: 'POST' as const,
      url: 'https://api.example.com/graphql',
      headers: [
        { key: 'Content-Type', value: 'application/json', enabled: true },
      ],
      queryParams: [],
      body,
      collectionId,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  }

  getExample(): string {
    return `type Query {
  users: [User!]!
  user(id: ID!): User
}

type Mutation {
  createUser(name: String!, email: String!): User!
}

type User {
  id: ID!
  name: String!
  email: String!
}`;
  }
}
