import { AvroParser } from '../../src/main/services/AvroParser';

describe('AvroParser', () => {
  let parser: AvroParser;

  beforeEach(() => {
    parser = new AvroParser();
  });

  describe('Schema Parsing', () => {
    test('should parse record schema', () => {
      const schema = {
        type: 'record',
        name: 'User',
        fields: [
          { name: 'id', type: 'string' },
          { name: 'age', type: 'int' },
        ],
      };

      const info = parser.parseSchema(schema);

      expect(info.name).toBe('User');
      expect(info.type).toBe('record');
      expect(info.fields).toHaveLength(2);
      expect(info.fields?.[0].name).toBe('id');
      expect(info.fields?.[1].name).toBe('age');
    });

    test('should parse enum schema', () => {
      const schema = {
        type: 'enum',
        name: 'Status',
        symbols: ['ACTIVE', 'INACTIVE', 'PENDING'],
      };

      const info = parser.parseSchema(schema);

      expect(info.name).toBe('Status');
      expect(info.type).toBe('enum');
      expect(info.symbols).toEqual(['ACTIVE', 'INACTIVE', 'PENDING']);
    });

    test('should parse array schema', () => {
      const schema = {
        type: 'array',
        items: 'string',
      };

      const info = parser.parseSchema(schema);

      expect(info.type).toBe('array');
      expect(info.items).toBe('string');
    });

    test('should parse map schema', () => {
      const schema = {
        type: 'map',
        values: 'int',
      };

      const info = parser.parseSchema(schema);

      expect(info.type).toBe('map');
      expect(info.values).toBe('int');
    });
  });

  describe('Data Serialization', () => {
    test('should serialize and deserialize data', () => {
      const schema = {
        type: 'record',
        name: 'User',
        fields: [
          { name: 'id', type: 'string' },
          { name: 'age', type: 'int' },
        ],
      };

      const data = { id: '123', age: 25 };

      const buffer = parser.serialize(schema, data);
      expect(buffer).toBeInstanceOf(Buffer);

      const decoded = parser.deserialize(schema, buffer);
      expect(decoded).toEqual(data);
    });
  });

  describe('Data Validation', () => {
    test('should validate correct data', () => {
      const schema = {
        type: 'record',
        name: 'User',
        fields: [
          { name: 'id', type: 'string' },
          { name: 'age', type: 'int' },
        ],
      };

      const data = { id: '123', age: 25 };

      const result = parser.validate(schema, data);
      expect(result.valid).toBe(true);
    });

    test('should detect invalid data', () => {
      const schema = {
        type: 'record',
        name: 'User',
        fields: [
          { name: 'id', type: 'string' },
          { name: 'age', type: 'int' },
        ],
      };

      const data = { id: '123', age: 'not a number' };

      const result = parser.validate(schema, data);
      expect(result.valid).toBe(false);
    });
  });

  describe('Example Generation', () => {
    test('should generate example for record', () => {
      const schema = {
        type: 'record',
        name: 'User',
        fields: [
          { name: 'id', type: 'string' },
          { name: 'age', type: 'int' },
          { name: 'active', type: 'boolean' },
        ],
      };

      const example = parser.generateExample(schema);

      expect(example).toHaveProperty('id');
      expect(example).toHaveProperty('age');
      expect(example).toHaveProperty('active');
      expect(typeof example.id).toBe('string');
      expect(typeof example.age).toBe('number');
      expect(typeof example.active).toBe('boolean');
    });

    test('should use default values when provided', () => {
      const schema = {
        type: 'record',
        name: 'User',
        fields: [
          { name: 'id', type: 'string', default: 'default-id' },
          { name: 'age', type: 'int', default: 18 },
        ],
      };

      const example = parser.generateExample(schema);

      expect(example.id).toBe('default-id');
      expect(example.age).toBe(18);
    });
  });

  describe('Schema Compatibility', () => {
    test('should detect compatible schemas', () => {
      const writerSchema = {
        type: 'record',
        name: 'User',
        fields: [
          { name: 'id', type: 'string' },
          { name: 'name', type: 'string' },
        ],
      };

      const readerSchema = {
        type: 'record',
        name: 'User',
        fields: [
          { name: 'id', type: 'string' },
          { name: 'name', type: 'string' },
          { name: 'email', type: ['null', 'string'], default: null },
        ],
      };

      const result = parser.isCompatible(writerSchema, readerSchema);
      expect(result.compatible).toBe(true);
    });
  });

  describe('Field Names', () => {
    test('should extract field names from record', () => {
      const schema = {
        type: 'record',
        name: 'User',
        fields: [
          { name: 'id', type: 'string' },
          { name: 'name', type: 'string' },
          { name: 'email', type: 'string' },
        ],
      };

      const fieldNames = parser.getFieldNames(schema);

      expect(fieldNames).toEqual(['id', 'name', 'email']);
    });

    test('should return empty array for non-record schema', () => {
      const schema = {
        type: 'string',
      };

      const fieldNames = parser.getFieldNames(schema);

      expect(fieldNames).toEqual([]);
    });
  });
});
