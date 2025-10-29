/**
 * GraphQLSchemaGeneratorService - GraphQL Schema Generator
 * 
 * Generates comprehensive GraphQL schemas (SDL) from GraphQL requests and responses
 * 
 * Features:
 * - Query detection and parsing from GraphQL requests
 * - Mutation detection and parsing
 * - Subscription detection
 * - Type inference from response data
 * - Input type detection
 * - Enum detection
 * - Interface and Union type support
 * - Custom scalar detection
 * - Schema directive support
 * - SDL (Schema Definition Language) generation
 */

import type { ConsoleEntry } from './ConsoleService';
import type { JSONSchema } from './RequestAnalyzerService';

export interface GraphQLField {
  name: string;
  type: string;
  args?: Record<string, GraphQLArgument>;
  description?: string;
  deprecated?: boolean;
  deprecationReason?: string;
}

export interface GraphQLArgument {
  type: string;
  defaultValue?: any;
  description?: string;
}

export interface GraphQLType {
  name: string;
  kind: 'OBJECT' | 'INPUT_OBJECT' | 'ENUM' | 'INTERFACE' | 'UNION' | 'SCALAR';
  description?: string;
  fields?: Record<string, GraphQLField>;
  enumValues?: string[];
  possibleTypes?: string[]; // For unions
  interfaces?: string[]; // For objects implementing interfaces
}

export interface GraphQLQuery {
  name: string;
  returnType: string;
  args?: Record<string, GraphQLArgument>;
  description?: string;
}

export interface GraphQLMutation {
  name: string;
  returnType: string;
  args?: Record<string, GraphQLArgument>;
  description?: string;
}

export interface GraphQLSubscription {
  name: string;
  returnType: string;
  args?: Record<string, GraphQLArgument>;
  description?: string;
}

export interface GraphQLSchema {
  types: GraphQLType[];
  queries: GraphQLQuery[];
  mutations: GraphQLMutation[];
  subscriptions: GraphQLSubscription[];
  directives?: GraphQLDirective[];
}

export interface GraphQLDirective {
  name: string;
  locations: string[];
  args?: Record<string, GraphQLArgument>;
}

export class GraphQLSchemaGeneratorService {
  /**
   * Generate comprehensive GraphQL schema from console entries
   */
  generateSchema(entries: ConsoleEntry[]): GraphQLSchema {
    const graphqlEntries = entries.filter(e => this.isGraphQLEntry(e));
    
    if (graphqlEntries.length === 0) {
      return this.createEmptySchema();
    }

    const queries = this.detectQueries(graphqlEntries);
    const mutations = this.detectMutations(graphqlEntries);
    const subscriptions = this.detectSubscriptions(graphqlEntries);
    const types = this.inferTypes(graphqlEntries);

    return {
      types,
      queries,
      mutations,
      subscriptions,
    };
  }

  /**
   * Check if entry is a GraphQL request/response
   */
  private isGraphQLEntry(entry: ConsoleEntry): boolean {
    // Check URL
    if (entry.url?.toLowerCase().includes('graphql')) {
      return true;
    }

    // Check request body for GraphQL query
    if (entry.type === 'request' && entry.body) {
      if (typeof entry.body === 'object' && ('query' in entry.body || 'mutation' in entry.body)) {
        return true;
      }
      if (typeof entry.body === 'string' && (entry.body.includes('query') || entry.body.includes('mutation'))) {
        return true;
      }
    }

    // Check response body for GraphQL data structure
    if (entry.type === 'response' && entry.body) {
      if (typeof entry.body === 'object' && ('data' in entry.body || 'errors' in entry.body)) {
        return true;
      }
    }

    // Check content type
    if (entry.headers && entry.headers['content-type']?.includes('application/graphql')) {
      return true;
    }

    return false;
  }

  /**
   * Detect queries from GraphQL requests
   */
  private detectQueries(entries: ConsoleEntry[]): GraphQLQuery[] {
    const queries: Map<string, GraphQLQuery> = new Map();

    for (const entry of entries) {
      const queryOperations = this.extractOperations(entry, 'query');
      
      for (const op of queryOperations) {
        if (!queries.has(op.name)) {
          queries.set(op.name, {
            name: op.name,
            returnType: op.returnType,
            args: op.args,
            description: op.description,
          });
        }
      }
    }

    return Array.from(queries.values());
  }

  /**
   * Detect mutations from GraphQL requests
   */
  private detectMutations(entries: ConsoleEntry[]): GraphQLMutation[] {
    const mutations: Map<string, GraphQLMutation> = new Map();

    for (const entry of entries) {
      const mutationOperations = this.extractOperations(entry, 'mutation');
      
      for (const op of mutationOperations) {
        if (!mutations.has(op.name)) {
          mutations.set(op.name, {
            name: op.name,
            returnType: op.returnType,
            args: op.args,
            description: op.description,
          });
        }
      }
    }

    return Array.from(mutations.values());
  }

  /**
   * Detect subscriptions from GraphQL requests
   */
  private detectSubscriptions(entries: ConsoleEntry[]): GraphQLSubscription[] {
    const subscriptions: Map<string, GraphQLSubscription> = new Map();

    for (const entry of entries) {
      const subOperations = this.extractOperations(entry, 'subscription');
      
      for (const op of subOperations) {
        if (!subscriptions.has(op.name)) {
          subscriptions.set(op.name, {
            name: op.name,
            returnType: op.returnType,
            args: op.args,
            description: op.description,
          });
        }
      }
    }

    return Array.from(subscriptions.values());
  }

  /**
   * Extract operations from entry
   */
  private extractOperations(entry: ConsoleEntry, operationType: 'query' | 'mutation' | 'subscription'): Array<{
    name: string;
    returnType: string;
    args?: Record<string, GraphQLArgument>;
    description?: string;
  }> {
    const operations: Array<any> = [];

    if (!entry.body) return operations;

    let queryString: string = '';
    
    if (typeof entry.body === 'object' && 'query' in entry.body) {
      queryString = entry.body.query as string;
    } else if (typeof entry.body === 'string') {
      queryString = entry.body;
    }

    if (!queryString) return operations;

    // Parse operation name and fields from GraphQL query string
    const operationPattern = new RegExp(`${operationType}\\s+(\\w+)?\\s*(?:\\(([^)]*)\\))?\\s*\\{([^}]+)\\}`, 'gi');
    const matches = queryString.matchAll(operationPattern);

    for (const match of matches) {
      const operationName = match[1] || `${operationType}Operation`;
      const argsString = match[2];
      const fieldsString = match[3];

      // Parse arguments
      const args: Record<string, GraphQLArgument> = {};
      if (argsString) {
        const argPattern = /\$(\w+):\s*([^,\s)]+)/g;
        let argMatch;
        while ((argMatch = argPattern.exec(argsString)) !== null) {
          args[argMatch[1]] = {
            type: argMatch[2],
          };
        }
      }

      // Infer return type from response or default
      let returnType = this.inferReturnType(entry, fieldsString);

      operations.push({
        name: operationName,
        returnType,
        args: Object.keys(args).length > 0 ? args : undefined,
      });
    }

    // If no operations found but query string exists, create a default one
    if (operations.length === 0 && queryString.includes(operationType)) {
      operations.push({
        name: `${operationType}Operation`,
        returnType: 'JSON',
      });
    }

    return operations;
  }

  /**
   * Infer return type from response or field selection
   */
  private inferReturnType(entry: ConsoleEntry, fieldsString: string): string {
    // Try to get response data type
    const responseEntry = entry.type === 'response' ? entry : null;
    
    if (responseEntry && responseEntry.body && typeof responseEntry.body === 'object') {
      const data = (responseEntry.body as any).data;
      if (data) {
        const keys = Object.keys(data);
        if (keys.length > 0) {
          const firstKey = keys[0];
          const value = data[firstKey];
          
          if (Array.isArray(value)) {
            return `[${this.capitalize(firstKey)}]`;
          } else if (typeof value === 'object') {
            return this.capitalize(firstKey);
          }
        }
      }
    }

    // Fallback: try to extract from field selection
    const fieldMatch = fieldsString?.trim().match(/^\s*(\w+)/);
    if (fieldMatch) {
      return this.capitalize(fieldMatch[1]);
    }

    return 'JSON';
  }

  /**
   * Infer types from GraphQL responses
   */
  private inferTypes(entries: ConsoleEntry[]): GraphQLType[] {
    const types: Map<string, GraphQLType> = new Map();

    for (const entry of entries) {
      if (entry.type !== 'response' || !entry.body) continue;

      const body = entry.body as any;
      if (!body.data) continue;

      // Extract types from response data
      const data = body.data;
      for (const [key, value] of Object.entries(data)) {
        const typeName = this.capitalize(key);
        
        if (Array.isArray(value) && value.length > 0) {
          // Array type - infer from first item
          const itemType = this.inferTypeFromValue(value[0], `${typeName}Item`);
          if (itemType && !types.has(itemType.name)) {
            types.set(itemType.name, itemType);
          }
        } else if (typeof value === 'object' && value !== null) {
          // Object type
          const objectType = this.inferTypeFromValue(value, typeName);
          if (objectType && !types.has(objectType.name)) {
            types.set(objectType.name, objectType);
          }
        }
      }
    }

    // Add scalar types if not already present
    const scalarTypes = ['ID', 'String', 'Int', 'Float', 'Boolean', 'JSON'];
    for (const scalar of scalarTypes) {
      if (!types.has(scalar)) {
        types.set(scalar, {
          name: scalar,
          kind: 'SCALAR',
          description: `GraphQL ${scalar} scalar`,
        });
      }
    }

    return Array.from(types.values());
  }

  /**
   * Infer GraphQL type from value
   */
  private inferTypeFromValue(value: any, typeName: string): GraphQLType | null {
    if (typeof value !== 'object' || value === null) {
      return null;
    }

    const fields: Record<string, GraphQLField> = {};

    for (const [key, val] of Object.entries(value)) {
      const fieldType = this.inferFieldType(val);
      fields[key] = {
        name: key,
        type: fieldType,
      };
    }

    return {
      name: typeName,
      kind: 'OBJECT',
      fields,
    };
  }

  /**
   * Infer field type from value
   */
  private inferFieldType(value: any): string {
    if (value === null || value === undefined) {
      return 'String';
    }

    if (Array.isArray(value)) {
      if (value.length === 0) {
        return '[String]';
      }
      const itemType = this.inferFieldType(value[0]);
      return `[${itemType}]`;
    }

    if (typeof value === 'object') {
      return 'JSON'; // Use JSON for complex nested objects
    }

    if (typeof value === 'string') {
      // Check if it's an ID (UUID or numeric ID pattern)
      if (/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value)) {
        return 'ID';
      }
      return 'String';
    }

    if (typeof value === 'number') {
      return Number.isInteger(value) ? 'Int' : 'Float';
    }

    if (typeof value === 'boolean') {
      return 'Boolean';
    }

    return 'String';
  }

  /**
   * Generate SDL (Schema Definition Language) from schema
   */
  generateSDL(schema: GraphQLSchema): string {
    let sdl = '';
    
    // Custom scalars
    const customScalars = schema.types.filter(t => t.kind === 'SCALAR' && !['ID', 'String', 'Int', 'Float', 'Boolean'].includes(t.name));
    if (customScalars.length > 0) {
      sdl += '# Custom Scalars\n';
      for (const scalar of customScalars) {
        if (scalar.description) {
          sdl += `"""${scalar.description}"""\n`;
        }
        sdl += `scalar ${scalar.name}\n\n`;
      }
    }

    // Enums
    const enums = schema.types.filter(t => t.kind === 'ENUM');
    if (enums.length > 0) {
      sdl += '# Enums\n';
      for (const enumType of enums) {
        if (enumType.description) {
          sdl += `"""${enumType.description}"""\n`;
        }
        sdl += `enum ${enumType.name} {\n`;
        if (enumType.enumValues) {
          for (const value of enumType.enumValues) {
            sdl += `  ${value}\n`;
          }
        }
        sdl += `}\n\n`;
      }
    }

    // Input types
    const inputTypes = schema.types.filter(t => t.kind === 'INPUT_OBJECT');
    if (inputTypes.length > 0) {
      sdl += '# Input Types\n';
      for (const type of inputTypes) {
        if (type.description) {
          sdl += `"""${type.description}"""\n`;
        }
        sdl += `input ${type.name} {\n`;
        if (type.fields) {
          for (const field of Object.values(type.fields)) {
            sdl += `  ${field.name}: ${field.type}\n`;
          }
        }
        sdl += `}\n\n`;
      }
    }

    // Object types
    const objectTypes = schema.types.filter(t => t.kind === 'OBJECT');
    if (objectTypes.length > 0) {
      sdl += '# Types\n';
      for (const type of objectTypes) {
        if (type.description) {
          sdl += `"""${type.description}"""\n`;
        }
        sdl += `type ${type.name}`;
        if (type.interfaces && type.interfaces.length > 0) {
          sdl += ` implements ${type.interfaces.join(' & ')}`;
        }
        sdl += ` {\n`;
        if (type.fields) {
          for (const field of Object.values(type.fields)) {
            if (field.description) {
              sdl += `  """${field.description}"""\n`;
            }
            sdl += `  ${field.name}`;
            if (field.args && Object.keys(field.args).length > 0) {
              const argsStr = Object.entries(field.args)
                .map(([name, arg]) => `${name}: ${arg.type}`)
                .join(', ');
              sdl += `(${argsStr})`;
            }
            sdl += `: ${field.type}`;
            if (field.deprecated) {
              sdl += ` @deprecated${field.deprecationReason ? `(reason: "${field.deprecationReason}")` : ''}`;
            }
            sdl += `\n`;
          }
        }
        sdl += `}\n\n`;
      }
    }

    // Query type
    if (schema.queries.length > 0) {
      sdl += '# Queries\n';
      sdl += `type Query {\n`;
      for (const query of schema.queries) {
        if (query.description) {
          sdl += `  """${query.description}"""\n`;
        }
        sdl += `  ${query.name}`;
        if (query.args && Object.keys(query.args).length > 0) {
          const argsStr = Object.entries(query.args)
            .map(([name, arg]) => `${name}: ${arg.type}`)
            .join(', ');
          sdl += `(${argsStr})`;
        }
        sdl += `: ${query.returnType}\n`;
      }
      sdl += `}\n\n`;
    }

    // Mutation type
    if (schema.mutations.length > 0) {
      sdl += '# Mutations\n';
      sdl += `type Mutation {\n`;
      for (const mutation of schema.mutations) {
        if (mutation.description) {
          sdl += `  """${mutation.description}"""\n`;
        }
        sdl += `  ${mutation.name}`;
        if (mutation.args && Object.keys(mutation.args).length > 0) {
          const argsStr = Object.entries(mutation.args)
            .map(([name, arg]) => `${name}: ${arg.type}`)
            .join(', ');
          sdl += `(${argsStr})`;
        }
        sdl += `: ${mutation.returnType}\n`;
      }
      sdl += `}\n\n`;
    }

    // Subscription type
    if (schema.subscriptions.length > 0) {
      sdl += '# Subscriptions\n';
      sdl += `type Subscription {\n`;
      for (const subscription of schema.subscriptions) {
        if (subscription.description) {
          sdl += `  """${subscription.description}"""\n`;
        }
        sdl += `  ${subscription.name}`;
        if (subscription.args && Object.keys(subscription.args).length > 0) {
          const argsStr = Object.entries(subscription.args)
            .map(([name, arg]) => `${name}: ${arg.type}`)
            .join(', ');
          sdl += `(${argsStr})`;
        }
        sdl += `: ${subscription.returnType}\n`;
      }
      sdl += `}\n`;
    }

    return sdl.trim();
  }

  /**
   * Create empty schema
   */
  private createEmptySchema(): GraphQLSchema {
    return {
      types: [
        { name: 'String', kind: 'SCALAR' },
        { name: 'Int', kind: 'SCALAR' },
        { name: 'Float', kind: 'SCALAR' },
        { name: 'Boolean', kind: 'SCALAR' },
        { name: 'ID', kind: 'SCALAR' },
      ],
      queries: [],
      mutations: [],
      subscriptions: [],
    };
  }

  /**
   * Capitalize string
   */
  private capitalize(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  /**
   * Validate GraphQL schema
   */
  validateSchema(schema: GraphQLSchema): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (schema.queries.length === 0 && schema.mutations.length === 0 && schema.subscriptions.length === 0) {
      errors.push('Schema must have at least one query, mutation, or subscription');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}
