// Unit tests for Variables functionality
import { DatabaseService } from '../../src/main/services/DatabaseService';
import type { Variable } from '../../src/types/models';
import { createTestDatabase } from '../utils/database-test-utils';
import { MockDatabase } from '../mocks/better-sqlite3.mock';

describe('Variables', () => {
  let db: DatabaseService;
  let mockDb: MockDatabase;

  beforeEach(() => {
    // Use mock database for tests
    const testDb = createTestDatabase();
    db = testDb.db;
    mockDb = testDb.mockDb;
  });

  afterEach(() => {
    db.close();
  });

  describe('Create Variable', () => {
    test('should create a global variable', () => {
      db.setVariable({
        key: 'apiKey',
        value: 'abc123',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables).toHaveLength(1);
      expect(variables[0].key).toBe('apiKey');
      expect(variables[0].value).toBe('abc123');
      expect(variables[0].type).toBe('string');
      expect(variables[0].scope).toBe('global');
      expect(variables[0].enabled).toBe(true);
    });

    test('should create an environment variable', () => {
      db.setVariable({
        key: 'baseUrl',
        value: 'https://api.example.com',
        type: 'string',
        scope: 'environment',
        enabled: true,
      });

      const variables = db.getVariablesByScope('environment');
      expect(variables).toHaveLength(1);
      expect(variables[0].key).toBe('baseUrl');
      expect(variables[0].value).toBe('https://api.example.com');
    });

    test('should create a collection-scoped variable', () => {
      const collection = db.createCollection({
        id: 'test-collection-1',
        name: 'Test Collection',
        requests: [],
        folders: [],
      });

      db.setVariable({
        key: 'userId',
        value: '12345',
        type: 'string',
        scope: collection.id as any,
        enabled: true,
      });

      const variables = db.getVariablesByScope(collection.id);
      expect(variables).toHaveLength(1);
      expect(variables[0].key).toBe('userId');
    });

    test('should create variables with different types', () => {
      db.setVariable({
        key: 'stringVar',
        value: 'text',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      db.setVariable({
        key: 'numberVar',
        value: 42,
        type: 'number',
        scope: 'global',
        enabled: true,
      });

      db.setVariable({
        key: 'boolVar',
        value: true,
        type: 'boolean',
        scope: 'global',
        enabled: true,
      });

      db.setVariable({
        key: 'secretVar',
        value: 'password123',
        type: 'secret',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables).toHaveLength(4);
      expect(variables.find(v => v.key === 'stringVar')?.type).toBe('string');
      expect(variables.find(v => v.key === 'numberVar')?.type).toBe('number');
      expect(variables.find(v => v.key === 'boolVar')?.type).toBe('boolean');
      expect(variables.find(v => v.key === 'secretVar')?.type).toBe('secret');
    });

    test('should create variable with description', () => {
      db.setVariable({
        key: 'apiKey',
        value: 'abc123',
        type: 'string',
        scope: 'global',
        enabled: true,
        description: 'Production API key',
      });

      const variables = db.getVariablesByScope('global');
      expect(variables[0].description).toBe('Production API key');
    });

    test('should create disabled variable', () => {
      db.setVariable({
        key: 'disabledVar',
        value: 'value',
        type: 'string',
        scope: 'global',
        enabled: false,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables[0].enabled).toBe(false);
    });
  });

  describe('Get Variables by Scope', () => {
    test('should return empty array for scope with no variables', () => {
      const variables = db.getVariablesByScope('global');
      expect(variables).toEqual([]);
    });

    test('should return only variables for specified scope', () => {
      db.setVariable({
        key: 'globalVar',
        value: 'global',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      db.setVariable({
        key: 'envVar',
        value: 'env',
        type: 'string',
        scope: 'environment',
        enabled: true,
      });

      const globalVars = db.getVariablesByScope('global');
      const envVars = db.getVariablesByScope('environment');

      expect(globalVars).toHaveLength(1);
      expect(envVars).toHaveLength(1);
      expect(globalVars[0].key).toBe('globalVar');
      expect(envVars[0].key).toBe('envVar');
    });

    test('should return multiple variables in same scope', () => {
      db.setVariable({
        key: 'var1',
        value: 'value1',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      db.setVariable({
        key: 'var2',
        value: 'value2',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      db.setVariable({
        key: 'var3',
        value: 'value3',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables).toHaveLength(3);
    });

    test('should include both enabled and disabled variables', () => {
      db.setVariable({
        key: 'enabledVar',
        value: 'value',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      db.setVariable({
        key: 'disabledVar',
        value: 'value',
        type: 'string',
        scope: 'global',
        enabled: false,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables).toHaveLength(2);
      expect(variables.some(v => v.enabled)).toBe(true);
      expect(variables.some(v => !v.enabled)).toBe(true);
    });
  });

  describe('Update Variable', () => {
    test('should update variable value', () => {
      db.setVariable({
        key: 'apiKey',
        value: 'oldValue',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      db.setVariable({
        key: 'apiKey',
        value: 'newValue',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables[0].value).toBe('newValue');
    });

    test('should update variable in specific scope', () => {
      db.setVariable({
        key: 'sameKey',
        value: 'globalValue',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      db.setVariable({
        key: 'sameKey',
        value: 'envValue',
        type: 'string',
        scope: 'environment',
        enabled: true,
      });

      db.setVariable({
        key: 'sameKey',
        value: 'updatedGlobal',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      const globalVars = db.getVariablesByScope('global');
      const envVars = db.getVariablesByScope('environment');

      expect(globalVars[0].value).toBe('updatedGlobal');
      expect(envVars[0].value).toBe('envValue');
    });

    test('should update number variable', () => {
      db.setVariable({
        key: 'count',
        value: 10,
        type: 'number',
        scope: 'global',
        enabled: true,
      });

      db.setVariable({
        key: 'count',
        value: 20,
        type: 'number',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables[0].value).toBe(20);
    });

    test('should update boolean variable', () => {
      db.setVariable({
        key: 'isActive',
        value: false,
        type: 'boolean',
        scope: 'global',
        enabled: true,
      });

      db.setVariable({
        key: 'isActive',
        value: true,
        type: 'boolean',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables[0].value).toBe(true);
    });
  });

  describe('Delete Variable', () => {
    test('should delete a variable', () => {
      db.setVariable({
        key: 'apiKey',
        value: 'abc123',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      db.deleteVariable('global', 'apiKey');

      const variables = db.getVariablesByScope('global');
      expect(variables).toHaveLength(0);
    });

    test('should delete only specified variable', () => {
      db.setVariable({
        key: 'var1',
        value: 'value1',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      db.setVariable({
        key: 'var2',
        value: 'value2',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      db.deleteVariable('global', 'var1');

      const variables = db.getVariablesByScope('global');
      expect(variables).toHaveLength(1);
      expect(variables[0].key).toBe('var2');
    });

    test('should delete variable from specific scope only', () => {
      db.setVariable({
        key: 'sameKey',
        value: 'globalValue',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      db.setVariable({
        key: 'sameKey',
        value: 'envValue',
        type: 'string',
        scope: 'environment',
        enabled: true,
      });

      db.deleteVariable('global', 'sameKey');

      const globalVars = db.getVariablesByScope('global');
      const envVars = db.getVariablesByScope('environment');

      expect(globalVars).toHaveLength(0);
      expect(envVars).toHaveLength(1);
    });
  });

  describe('Variable Scoping', () => {
    test('should support global scope', () => {
      db.setVariable({
        key: 'globalVar',
        value: 'value',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables).toHaveLength(1);
      expect(variables[0].scope).toBe('global');
    });

    test('should support environment scope', () => {
      db.setVariable({
        key: 'envVar',
        value: 'value',
        type: 'string',
        scope: 'environment',
        enabled: true,
      });

      const variables = db.getVariablesByScope('environment');
      expect(variables).toHaveLength(1);
      expect(variables[0].scope).toBe('environment');
    });

    test('should support collection scope', () => {
      const collection = db.createCollection({
        id: 'test-collection-2',
        name: 'Test Collection',
        requests: [],
        folders: [],
      });

      db.setVariable({
        key: 'collectionVar',
        value: 'value',
        type: 'string',
        scope: collection.id as any,
        enabled: true,
      });

      const variables = db.getVariablesByScope(collection.id);
      expect(variables).toHaveLength(1);
      expect(variables[0].scope).toBe(collection.id);
    });

    test('should allow same key in different scopes', () => {
      db.setVariable({
        key: 'apiKey',
        value: 'global-key',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      db.setVariable({
        key: 'apiKey',
        value: 'env-key',
        type: 'string',
        scope: 'environment',
        enabled: true,
      });

      const globalVars = db.getVariablesByScope('global');
      const envVars = db.getVariablesByScope('environment');

      expect(globalVars[0].value).toBe('global-key');
      expect(envVars[0].value).toBe('env-key');
    });
  });

  describe('Variable Types', () => {
    test('should handle string values', () => {
      db.setVariable({
        key: 'stringVar',
        value: 'Hello World',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(typeof variables[0].value).toBe('string');
      expect(variables[0].value).toBe('Hello World');
    });

    test('should handle number values', () => {
      db.setVariable({
        key: 'numberVar',
        value: 42.5,
        type: 'number',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(typeof variables[0].value).toBe('number');
      expect(variables[0].value).toBe(42.5);
    });

    test('should handle boolean values', () => {
      db.setVariable({
        key: 'boolVar',
        value: true,
        type: 'boolean',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(typeof variables[0].value).toBe('boolean');
      expect(variables[0].value).toBe(true);
    });

    test('should handle secret type', () => {
      db.setVariable({
        key: 'password',
        value: 'secret123',
        type: 'secret',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables[0].type).toBe('secret');
      expect(variables[0].value).toBe('secret123');
    });
  });

  describe('Edge Cases', () => {
    test('should handle empty string values', () => {
      db.setVariable({
        key: 'emptyVar',
        value: '',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables[0].value).toBe('');
    });

    test('should handle zero as number value', () => {
      db.setVariable({
        key: 'zeroVar',
        value: 0,
        type: 'number',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables[0].value).toBe(0);
    });

    test('should handle very long variable values', () => {
      const longValue = 'A'.repeat(10000);
      db.setVariable({
        key: 'longVar',
        value: longValue,
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables[0].value).toBe(longValue);
    });

    test('should handle special characters in keys', () => {
      db.setVariable({
        key: 'api_key-v2.0',
        value: 'value',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables[0].key).toBe('api_key-v2.0');
    });

    test('should handle unicode in values', () => {
      db.setVariable({
        key: 'unicodeVar',
        value: '你好世界 🌍 émojis',
        type: 'string',
        scope: 'global',
        enabled: true,
      });

      const variables = db.getVariablesByScope('global');
      expect(variables[0].value).toBe('你好世界 🌍 émojis');
    });

    test('should handle multiple rapid operations', () => {
      // Create many variables
      for (let i = 0; i < 100; i++) {
        db.setVariable({
          key: `var${i}`,
          value: `value${i}`,
          type: 'string',
          scope: 'global',
          enabled: true,
        });
      }

      const variables = db.getVariablesByScope('global');
      expect(variables).toHaveLength(100);

      // Update all
      for (let i = 0; i < 100; i++) {
        db.setVariable({
          key: `var${i}`,
          value: `updated${i}`,
          type: 'string',
          scope: 'global',
          enabled: true,
        });
      }

      const updated = db.getVariablesByScope('global');
      expect(updated[0].value).toBe('updated0');
      expect(updated[99].value).toBe('updated99');

      // Delete half
      for (let i = 0; i < 50; i++) {
        db.deleteVariable('global', `var${i}`);
      }

      const remaining = db.getVariablesByScope('global');
      expect(remaining).toHaveLength(50);
    });
  });
});
