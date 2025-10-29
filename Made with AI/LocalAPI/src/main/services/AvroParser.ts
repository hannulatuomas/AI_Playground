// Avro Parser Service
// Parses Avro schemas and handles serialization/deserialization

import * as avro from 'avsc';

interface AvroSchemaInfo {
  name: string;
  namespace?: string;
  type: string;
  fields?: AvroField[];
  symbols?: string[];
  items?: any;
  values?: any;
  doc?: string;
}

interface AvroField {
  name: string;
  type: any;
  doc?: string;
  default?: any;
  order?: string;
}

export class AvroParser {
  /**
   * Parse Avro schema from JSON
   */
  parseSchema(schemaJson: string | object): AvroSchemaInfo {
    try {
      const schema = typeof schemaJson === 'string' ? JSON.parse(schemaJson) : schemaJson;
      
      // Validate by creating a type
      avro.Type.forSchema(schema);

      return this.extractSchemaInfo(schema);
    } catch (error: any) {
      throw new Error(`Failed to parse Avro schema: ${error.message}`);
    }
  }

  /**
   * Extract schema information
   */
  private extractSchemaInfo(schema: any): AvroSchemaInfo {
    const info: AvroSchemaInfo = {
      name: schema.name || 'Unnamed',
      namespace: schema.namespace,
      type: schema.type,
      doc: schema.doc,
    };

    if (schema.type === 'record' && schema.fields) {
      info.fields = schema.fields.map((field: any) => ({
        name: field.name,
        type: this.getTypeName(field.type),
        doc: field.doc,
        default: field.default,
        order: field.order,
      }));
    }

    if (schema.type === 'enum' && schema.symbols) {
      info.symbols = schema.symbols;
    }

    if (schema.type === 'array' && schema.items) {
      info.items = this.getTypeName(schema.items);
    }

    if (schema.type === 'map' && schema.values) {
      info.values = this.getTypeName(schema.values);
    }

    return info;
  }

  /**
   * Get type name from type definition
   */
  private getTypeName(type: any): string {
    if (typeof type === 'string') {
      return type;
    }

    if (Array.isArray(type)) {
      return `[${type.map(t => this.getTypeName(t)).join(', ')}]`;
    }

    if (typeof type === 'object') {
      if (type.type === 'array') {
        return `array<${this.getTypeName(type.items)}>`;
      }
      if (type.type === 'map') {
        return `map<${this.getTypeName(type.values)}>`;
      }
      if (type.type === 'record') {
        return type.name || 'record';
      }
      if (type.type === 'enum') {
        return type.name || 'enum';
      }
      return type.type || 'unknown';
    }

    return 'unknown';
  }

  /**
   * Serialize data using Avro schema
   */
  serialize(schemaJson: string | object, data: any): Buffer {
    try {
      const schema = typeof schemaJson === 'string' ? JSON.parse(schemaJson) : schemaJson;
      const type = avro.Type.forSchema(schema);
      return type.toBuffer(data);
    } catch (error: any) {
      throw new Error(`Failed to serialize data: ${error.message}`);
    }
  }

  /**
   * Deserialize Avro data
   */
  deserialize(schemaJson: string | object, buffer: Buffer): any {
    try {
      const schema = typeof schemaJson === 'string' ? JSON.parse(schemaJson) : schemaJson;
      const type = avro.Type.forSchema(schema);
      return type.fromBuffer(buffer);
    } catch (error: any) {
      throw new Error(`Failed to deserialize data: ${error.message}`);
    }
  }

  /**
   * Validate data against schema
   */
  validate(schemaJson: string | object, data: any): { valid: boolean; errors?: string[] } {
    try {
      const schema = typeof schemaJson === 'string' ? JSON.parse(schemaJson) : schemaJson;
      const type = avro.Type.forSchema(schema);
      
      const valid = type.isValid(data);
      
      if (!valid) {
        return {
          valid: false,
          errors: ['Data does not match schema'],
        };
      }

      return { valid: true };
    } catch (error: any) {
      return {
        valid: false,
        errors: [error.message],
      };
    }
  }

  /**
   * Generate example data from schema
   */
  generateExample(schemaJson: string | object): any {
    try {
      const schema = typeof schemaJson === 'string' ? JSON.parse(schemaJson) : schemaJson;
      return this.generateExampleFromSchema(schema);
    } catch (error: any) {
      throw new Error(`Failed to generate example: ${error.message}`);
    }
  }

  /**
   * Generate example from schema definition
   */
  private generateExampleFromSchema(schema: any): any {
    if (typeof schema === 'string') {
      return this.getPrimitiveExample(schema);
    }

    if (Array.isArray(schema)) {
      // Union type - use first non-null type
      const nonNullType = schema.find(t => t !== 'null');
      return this.generateExampleFromSchema(nonNullType || schema[0]);
    }

    if (typeof schema === 'object') {
      switch (schema.type) {
        case 'record':
          const record: any = {};
          if (schema.fields) {
            for (const field of schema.fields) {
              record[field.name] = field.default !== undefined
                ? field.default
                : this.generateExampleFromSchema(field.type);
            }
          }
          return record;

        case 'enum':
          return schema.symbols && schema.symbols[0];

        case 'array':
          return [this.generateExampleFromSchema(schema.items)];

        case 'map':
          return {
            key1: this.generateExampleFromSchema(schema.values),
          };

        case 'fixed':
          return Buffer.alloc(schema.size || 0);

        default:
          return this.getPrimitiveExample(schema.type);
      }
    }

    return null;
  }

  /**
   * Get example value for primitive type
   */
  private getPrimitiveExample(type: string): any {
    switch (type) {
      case 'null':
        return null;
      case 'boolean':
        return false;
      case 'int':
      case 'long':
        return 0;
      case 'float':
      case 'double':
        return 0.0;
      case 'bytes':
        return Buffer.alloc(0);
      case 'string':
        return '';
      default:
        return null;
    }
  }

  /**
   * Get schema fingerprint
   */
  getFingerprint(schemaJson: string | object): string {
    try {
      const schema = typeof schemaJson === 'string' ? JSON.parse(schemaJson) : schemaJson;
      const type = avro.Type.forSchema(schema);
      return type.fingerprint().toString('hex');
    } catch (error: any) {
      throw new Error(`Failed to get fingerprint: ${error.message}`);
    }
  }

  /**
   * Compare two schemas for compatibility
   */
  isCompatible(
    writerSchemaJson: string | object,
    readerSchemaJson: string | object
  ): { compatible: boolean; errors?: string[] } {
    try {
      const writerSchema = typeof writerSchemaJson === 'string' ? JSON.parse(writerSchemaJson) : writerSchemaJson;
      const readerSchema = typeof readerSchemaJson === 'string' ? JSON.parse(readerSchemaJson) : readerSchemaJson;

      const writerType = avro.Type.forSchema(writerSchema);
      const readerType = avro.Type.forSchema(readerSchema);

      // Create a resolver to check compatibility
      try {
        readerType.createResolver(writerType);
        return { compatible: true };
      } catch (error: any) {
        return {
          compatible: false,
          errors: [error.message],
        };
      }
    } catch (error: any) {
      return {
        compatible: false,
        errors: [error.message],
      };
    }
  }

  /**
   * Get all field names from record schema
   */
  getFieldNames(schemaJson: string | object): string[] {
    try {
      const schema = typeof schemaJson === 'string' ? JSON.parse(schemaJson) : schemaJson;
      
      if (schema.type === 'record' && schema.fields) {
        return schema.fields.map((field: any) => field.name);
      }

      return [];
    } catch (error: any) {
      return [];
    }
  }
}

// Singleton instance
let avroParserInstance: AvroParser | null = null;

export function getAvroParser(): AvroParser {
  if (!avroParserInstance) {
    avroParserInstance = new AvroParser();
  }
  return avroParserInstance;
}
