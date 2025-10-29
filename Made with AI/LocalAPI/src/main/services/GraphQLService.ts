// GraphQL Service
// Handles GraphQL queries, mutations, and schema introspection using Apollo Client

import { ApolloClient, InMemoryCache, HttpLink, gql, DocumentNode } from '@apollo/client';
import fetch from 'cross-fetch';

interface GraphQLRequest {
  endpoint: string;
  query: string;
  variables?: Record<string, any>;
  headers?: Record<string, string>;
  operationName?: string;
}

interface GraphQLResponse {
  data?: any;
  errors?: readonly any[];
  extensions?: any;
}

interface IntrospectionResult {
  schema: any;
  types: TypeInfo[];
  queries: OperationInfo[];
  mutations: OperationInfo[];
  subscriptions: OperationInfo[];
}

interface TypeInfo {
  name: string;
  kind: string;
  description?: string;
  fields?: FieldInfo[];
}

interface FieldInfo {
  name: string;
  type: string;
  description?: string;
  args?: ArgumentInfo[];
}

interface ArgumentInfo {
  name: string;
  type: string;
  defaultValue?: any;
  description?: string;
}

interface OperationInfo {
  name: string;
  type: string;
  description?: string;
  args?: ArgumentInfo[];
}

export class GraphQLService {
  /**
   * Execute GraphQL query or mutation
   */
  async executeQuery(request: GraphQLRequest): Promise<GraphQLResponse> {
    try {
      const client = this.createClient(request.endpoint, request.headers);

      const result = await client.query({
        query: gql(request.query),
        variables: request.variables,
        fetchPolicy: 'no-cache',
      });

      return {
        data: result.data,
        errors: result.errors,
      };
    } catch (error: any) {
      return {
        errors: [
          {
            message: error.message,
            extensions: {
              code: error.extensions?.code || 'INTERNAL_ERROR',
            },
          },
        ],
      };
    }
  }

  /**
   * Execute GraphQL mutation
   */
  async executeMutation(request: GraphQLRequest): Promise<GraphQLResponse> {
    try {
      const client = this.createClient(request.endpoint, request.headers);

      const result = await client.mutate({
        mutation: gql(request.query),
        variables: request.variables,
      });

      return {
        data: result.data,
        errors: result.errors,
      };
    } catch (error: any) {
      return {
        errors: [
          {
            message: error.message,
            extensions: {
              code: error.extensions?.code || 'INTERNAL_ERROR',
            },
          },
        ],
      };
    }
  }

  /**
   * Perform schema introspection
   */
  async introspectSchema(endpoint: string, headers?: Record<string, string>): Promise<IntrospectionResult> {
    const introspectionQuery = `
      query IntrospectionQuery {
        __schema {
          queryType { name }
          mutationType { name }
          subscriptionType { name }
          types {
            ...FullType
          }
          directives {
            name
            description
            locations
            args {
              ...InputValue
            }
          }
        }
      }

      fragment FullType on __Type {
        kind
        name
        description
        fields(includeDeprecated: true) {
          name
          description
          args {
            ...InputValue
          }
          type {
            ...TypeRef
          }
          isDeprecated
          deprecationReason
        }
        inputFields {
          ...InputValue
        }
        interfaces {
          ...TypeRef
        }
        enumValues(includeDeprecated: true) {
          name
          description
          isDeprecated
          deprecationReason
        }
        possibleTypes {
          ...TypeRef
        }
      }

      fragment InputValue on __InputValue {
        name
        description
        type { ...TypeRef }
        defaultValue
      }

      fragment TypeRef on __Type {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                    }
                  }
                }
              }
            }
          }
        }
      }
    `;

    try {
      const response = await this.executeQuery({
        endpoint,
        query: introspectionQuery,
        headers,
      });

      if (response.errors) {
        throw new Error(response.errors[0]?.message || 'Introspection failed');
      }

      const schema = response.data.__schema;
      return this.parseIntrospectionResult(schema);
    } catch (error: any) {
      throw new Error(`Schema introspection failed: ${error.message}`);
    }
  }

  /**
   * Parse introspection result into structured format
   */
  private parseIntrospectionResult(schema: any): IntrospectionResult {
    const types: TypeInfo[] = [];
    const queries: OperationInfo[] = [];
    const mutations: OperationInfo[] = [];
    const subscriptions: OperationInfo[] = [];

    // Parse types
    for (const type of schema.types) {
      if (type.name.startsWith('__')) continue; // Skip introspection types

      const typeInfo: TypeInfo = {
        name: type.name,
        kind: type.kind,
        description: type.description,
      };

      if (type.fields) {
        typeInfo.fields = type.fields.map((field: any) => ({
          name: field.name,
          type: this.getTypeName(field.type),
          description: field.description,
          args: field.args?.map((arg: any) => ({
            name: arg.name,
            type: this.getTypeName(arg.type),
            defaultValue: arg.defaultValue,
            description: arg.description,
          })),
        }));
      }

      types.push(typeInfo);
    }

    // Parse queries
    if (schema.queryType) {
      const queryType = schema.types.find((t: any) => t.name === schema.queryType.name);
      if (queryType?.fields) {
        for (const field of queryType.fields) {
          queries.push({
            name: field.name,
            type: this.getTypeName(field.type),
            description: field.description,
            args: field.args?.map((arg: any) => ({
              name: arg.name,
              type: this.getTypeName(arg.type),
              defaultValue: arg.defaultValue,
              description: arg.description,
            })),
          });
        }
      }
    }

    // Parse mutations
    if (schema.mutationType) {
      const mutationType = schema.types.find((t: any) => t.name === schema.mutationType.name);
      if (mutationType?.fields) {
        for (const field of mutationType.fields) {
          mutations.push({
            name: field.name,
            type: this.getTypeName(field.type),
            description: field.description,
            args: field.args?.map((arg: any) => ({
              name: arg.name,
              type: this.getTypeName(arg.type),
              defaultValue: arg.defaultValue,
              description: arg.description,
            })),
          });
        }
      }
    }

    // Parse subscriptions
    if (schema.subscriptionType) {
      const subscriptionType = schema.types.find((t: any) => t.name === schema.subscriptionType.name);
      if (subscriptionType?.fields) {
        for (const field of subscriptionType.fields) {
          subscriptions.push({
            name: field.name,
            type: this.getTypeName(field.type),
            description: field.description,
            args: field.args?.map((arg: any) => ({
              name: arg.name,
              type: this.getTypeName(arg.type),
              defaultValue: arg.defaultValue,
              description: arg.description,
            })),
          });
        }
      }
    }

    return {
      schema,
      types,
      queries,
      mutations,
      subscriptions,
    };
  }

  /**
   * Get type name from type object
   */
  private getTypeName(type: any): string {
    if (!type) return 'Unknown';

    if (type.kind === 'NON_NULL') {
      return `${this.getTypeName(type.ofType)}!`;
    }

    if (type.kind === 'LIST') {
      return `[${this.getTypeName(type.ofType)}]`;
    }

    return type.name || 'Unknown';
  }

  /**
   * Generate query template from operation info
   */
  generateQueryTemplate(operation: OperationInfo, operationType: 'query' | 'mutation' | 'subscription'): string {
    const args = operation.args || [];
    const argDefinitions = args.map(arg => `$${arg.name}: ${arg.type}`).join(', ');
    const argValues = args.map(arg => `${arg.name}: $${arg.name}`).join(', ');

    let template = `${operationType} ${operation.name}`;
    
    if (argDefinitions) {
      template += `(${argDefinitions})`;
    }

    template += ` {\n  ${operation.name}`;

    if (argValues) {
      template += `(${argValues})`;
    }

    template += ` {\n    # Add fields here\n  }\n}`;

    return template;
  }

  /**
   * Validate GraphQL query syntax
   */
  validateQuery(query: string): { valid: boolean; errors?: string[] } {
    try {
      gql(query);
      return { valid: true };
    } catch (error: any) {
      return {
        valid: false,
        errors: [error.message],
      };
    }
  }

  /**
   * Format GraphQL query
   */
  formatQuery(query: string): string {
    try {
      const parsed = gql(query);
      // Basic formatting - could be enhanced with prettier-plugin-graphql
      return query.trim();
    } catch {
      return query;
    }
  }

  /**
   * Create Apollo Client instance
   */
  private createClient(endpoint: string, headers?: Record<string, string>): ApolloClient<any> {
    const httpLink = new HttpLink({
      uri: endpoint,
      fetch,
      headers: headers || {},
    });

    return new ApolloClient({
      link: httpLink,
      cache: new InMemoryCache(),
      defaultOptions: {
        query: {
          fetchPolicy: 'no-cache',
        },
        mutate: {
          fetchPolicy: 'no-cache',
        },
      },
    });
  }

  /**
   * Extract variables from query
   */
  extractVariables(query: string): string[] {
    const variableRegex = /\$(\w+)/g;
    const variables: string[] = [];
    let match;

    while ((match = variableRegex.exec(query)) !== null) {
      if (!variables.includes(match[1])) {
        variables.push(match[1]);
      }
    }

    return variables;
  }

  /**
   * Generate example variables object
   */
  generateExampleVariables(operation: OperationInfo): Record<string, any> {
    const variables: Record<string, any> = {};

    if (operation.args) {
      for (const arg of operation.args) {
        variables[arg.name] = this.getExampleValue(arg.type);
      }
    }

    return variables;
  }

  /**
   * Get example value for a type
   */
  private getExampleValue(type: string): any {
    // Remove non-null and list markers
    const baseType = type.replace(/[!\[\]]/g, '');

    switch (baseType) {
      case 'String':
      case 'ID':
        return '';
      case 'Int':
        return 0;
      case 'Float':
        return 0.0;
      case 'Boolean':
        return false;
      default:
        return null;
    }
  }
}

// Singleton instance
let graphQLServiceInstance: GraphQLService | null = null;

export function getGraphQLService(): GraphQLService {
  if (!graphQLServiceInstance) {
    graphQLServiceInstance = new GraphQLService();
  }
  return graphQLServiceInstance;
}
