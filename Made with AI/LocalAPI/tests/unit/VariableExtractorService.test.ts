// Unit tests for VariableExtractorService

import { VariableExtractorService } from '../../src/main/services/VariableExtractorService';
import type { Response } from '../../src/types/models';

describe('VariableExtractorService', () => {
  let service: VariableExtractorService;

  beforeEach(() => {
    service = new VariableExtractorService();
  });

  afterEach(() => {
    // Cleanup after each test
    service.cleanup();
  });

  afterAll(() => {
    // Force cleanup to prevent Jest hanging
    jest.clearAllTimers();
  });

  describe('extractFromJSON', () => {
    it('should extract simple value from JSON', () => {
      const body = { data: { token: 'abc123' } };
      const result = service.extractFromJSON(body, '$.data.token', 'authToken', 'global');

      expect(result.success).toBe(true);
      expect(result.value).toBe('abc123');
      expect(result.variableName).toBe('authToken');
      expect(result.scope).toBe('global');
    });

    it('should extract array element from JSON', () => {
      const body = { users: [{ id: 1, name: 'John' }, { id: 2, name: 'Jane' }] };
      const result = service.extractFromJSON(body, '$.users[0].name', 'userName', 'global');

      expect(result.success).toBe(true);
      expect(result.value).toBe('John');
    });

    it('should extract multiple values as array', () => {
      const body = { users: [{ id: 1 }, { id: 2 }, { id: 3 }] };
      const result = service.extractFromJSON(body, '$.users[*].id', 'userIds', 'global');

      expect(result.success).toBe(true);
      expect(Array.isArray(result.value)).toBe(true);
      expect(result.value).toEqual([1, 2, 3]);
    });

    it('should handle nested objects', () => {
      const body = { response: { data: { user: { profile: { email: 'test@example.com' } } } } };
      const result = service.extractFromJSON(body, '$.response.data.user.profile.email', 'email', 'global');

      expect(result.success).toBe(true);
      expect(result.value).toBe('test@example.com');
    });

    it('should fail on invalid JSONPath', () => {
      const body = { data: { token: 'abc123' } };
      const result = service.extractFromJSON(body, '$.invalid.path', 'token', 'global');

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });

    it('should parse JSON string', () => {
      const body = '{"data":{"token":"abc123"}}';
      const result = service.extractFromJSON(body, '$.data.token', 'token', 'global');

      expect(result.success).toBe(true);
      expect(result.value).toBe('abc123');
    });

    it('should handle invalid JSON string', () => {
      const body = 'not valid json';
      const result = service.extractFromJSON(body, '$.data', 'token', 'global');

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      // Error message varies, just check it failed
    });
  });

  describe('extractFromXML', () => {
    it('should extract simple value from XML', async () => {
      const xml = '<root><element><value>test123</value></element></root>';
      const result = await service.extractFromXML(xml, 'root.element.value', 'xmlValue', 'global');

      expect(result.success).toBe(true);
      expect(result.value).toBe('test123');
    });

    it('should handle nested XML elements', async () => {
      const xml = '<response><data><user><name>John</name></user></data></response>';
      const result = await service.extractFromXML(xml, 'response.data.user.name', 'userName', 'global');

      expect(result.success).toBe(true);
      expect(result.value).toBe('John');
    });

    it('should fail on invalid XML', async () => {
      const xml = '<root><unclosed>';
      const result = await service.extractFromXML(xml, 'root.element', 'value', 'global');

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });

    it('should fail on invalid XPath', async () => {
      const xml = '<root><element>value</element></root>';
      const result = await service.extractFromXML(xml, 'root.nonexistent', 'value', 'global');

      expect(result.success).toBe(false);
      expect(result.error).toContain('No matches found');
    });
  });

  describe('extractFromHeader', () => {
    it('should extract header value', () => {
      const headers = { 'Authorization': 'Bearer token123', 'Content-Type': 'application/json' };
      const result = service.extractFromHeader(headers, 'Authorization', 'authHeader', 'global');

      expect(result.success).toBe(true);
      expect(result.value).toBe('Bearer token123');
    });

    it('should be case-insensitive', () => {
      const headers = { 'Content-Type': 'application/json' };
      const result = service.extractFromHeader(headers, 'content-type', 'contentType', 'global');

      expect(result.success).toBe(true);
      expect(result.value).toBe('application/json');
    });

    it('should fail on missing header', () => {
      const headers = { 'Content-Type': 'application/json' };
      const result = service.extractFromHeader(headers, 'Authorization', 'auth', 'global');

      expect(result.success).toBe(false);
      expect(result.error).toContain('not found');
    });
  });

  describe('extractWithRegex', () => {
    it('should extract with simple regex', () => {
      const content = 'The token is abc123 and the id is 456';
      const result = service.extractWithRegex(content, 'token is (\\w+)', 'token', 'global', 'body');

      expect(result.success).toBe(true);
      expect(result.value).toBe('abc123');
    });

    it('should extract full match if no capture group', () => {
      const content = 'email: test@example.com';
      const result = service.extractWithRegex(content, '\\S+@\\S+\\.\\S+', 'email', 'global', 'body');

      expect(result.success).toBe(true);
      expect(result.value).toBe('test@example.com');
    });

    it('should fail on no match', () => {
      const content = 'no match here';
      const result = service.extractWithRegex(content, 'token: (\\w+)', 'token', 'global', 'body');

      expect(result.success).toBe(false);
      expect(result.error).toContain('No matches found');
    });

    it('should handle invalid regex', () => {
      const content = 'test';
      const result = service.extractWithRegex(content, '[invalid(regex', 'value', 'global', 'body');

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      // Error message varies by environment
    });
  });

  describe('extractWithRules', () => {
    it('should extract using multiple rules', async () => {
      const response: Response = {
        status: 200,
        statusText: 'OK',
        headers: { 'X-Token': 'header-token' },
        body: { data: { id: 123, name: 'Test' } },
        time: 100,
        size: 1024,
        timestamp: new Date(),
      };

      const rules = [
        {
          id: '1',
          name: 'Extract ID',
          enabled: true,
          source: 'body' as const,
          extractionType: 'jsonpath' as const,
          pattern: '$.data.id',
          variableName: 'userId',
          scope: 'global' as const,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
        {
          id: '2',
          name: 'Extract Token',
          enabled: true,
          source: 'header' as const,
          extractionType: 'header' as const,
          pattern: 'X-Token',
          variableName: 'token',
          scope: 'global' as const,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      const results = await service.extractWithRules(response, rules);

      expect(results).toHaveLength(2);
      
      // Find results by variable name
      const userIdResult = results.find(r => r.variableName === 'userId');
      const tokenResult = results.find(r => r.variableName === 'token');
      
      expect(userIdResult).toBeDefined();
      expect(userIdResult?.success).toBe(true);
      expect(userIdResult?.value).toBe(123);
      
      expect(tokenResult).toBeDefined();
      expect(tokenResult?.success).toBe(true);
      expect(tokenResult?.value).toBe('header-token');
    });

    it('should skip disabled rules', async () => {
      const response: Response = {
        status: 200,
        statusText: 'OK',
        headers: {},
        body: { data: 'test' },
        time: 100,
        size: 1024,
        timestamp: new Date(),
      };

      const rules = [
        {
          id: '1',
          name: 'Disabled Rule',
          enabled: false,
          source: 'body' as const,
          extractionType: 'jsonpath' as const,
          pattern: '$.data',
          variableName: 'data',
          scope: 'global' as const,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      const results = await service.extractWithRules(response, rules);

      expect(results).toHaveLength(0);
    });
  });

  describe('Rule Management', () => {
    it('should add a rule', () => {
      const rule = service.addRule({
        name: 'Test Rule',
        enabled: true,
        source: 'body',
        extractionType: 'jsonpath',
        pattern: '$.data',
        variableName: 'testVar',
        scope: 'global',
      });

      expect(rule.id).toBeDefined();
      expect(rule.name).toBe('Test Rule');
      expect(rule.createdAt).toBeInstanceOf(Date);
    });

    it('should update a rule', async () => {
      const rule = service.addRule({
        name: 'Test Rule',
        enabled: true,
        source: 'body',
        extractionType: 'jsonpath',
        pattern: '$.data',
        variableName: 'testVar',
        scope: 'global',
      });

      // Wait a tiny bit to ensure timestamp difference
      await new Promise(resolve => setTimeout(resolve, 10));

      const updated = service.updateRule(rule.id, { name: 'Updated Rule' });

      expect(updated).not.toBeNull();
      expect(updated?.name).toBe('Updated Rule');
      expect(updated?.updatedAt.getTime()).toBeGreaterThanOrEqual(rule.createdAt.getTime());
    });

    it('should delete a rule', () => {
      const rule = service.addRule({
        name: 'Test Rule',
        enabled: true,
        source: 'body',
        extractionType: 'jsonpath',
        pattern: '$.data',
        variableName: 'testVar',
        scope: 'global',
      });

      const deleted = service.deleteRule(rule.id);
      expect(deleted).toBe(true);

      const retrieved = service.getRule(rule.id);
      expect(retrieved).toBeNull();
    });

    it('should get all rules', () => {
      service.addRule({
        name: 'Rule 1',
        enabled: true,
        source: 'body',
        extractionType: 'jsonpath',
        pattern: '$.data',
        variableName: 'var1',
        scope: 'global',
      });

      service.addRule({
        name: 'Rule 2',
        enabled: true,
        source: 'header',
        extractionType: 'header',
        pattern: 'X-Token',
        variableName: 'var2',
        scope: 'global',
      });

      const rules = service.getRules();
      expect(rules).toHaveLength(2);
    });
  });

  describe('History Management', () => {
    it('should record variable history', () => {
      service.recordHistory('testVar', 'oldValue', 'newValue', 'global', 'manual');

      const history = service.getHistory('testVar');
      expect(history).toHaveLength(1);
      expect(history[0].variableName).toBe('testVar');
      expect(history[0].oldValue).toBe('oldValue');
      expect(history[0].newValue).toBe('newValue');
    });

    it('should filter history by variable name', () => {
      service.recordHistory('var1', 'old1', 'new1', 'global', 'source1');
      service.recordHistory('var2', 'old2', 'new2', 'global', 'source2');

      const history = service.getHistory('var1');
      expect(history).toHaveLength(1);
      expect(history[0].variableName).toBe('var1');
    });

    it('should limit history entries', () => {
      service.recordHistory('var1', 'old', 'new', 'global', 'source');
      service.recordHistory('var2', 'old', 'new', 'global', 'source');

      const history = service.getHistory(undefined, 1);
      expect(history).toHaveLength(1);
    });

    it('should clear history', () => {
      service.recordHistory('var1', 'old', 'new', 'global', 'source');
      service.recordHistory('var2', 'old', 'new', 'global', 'source');

      service.clearHistory();
      const history = service.getHistory();
      expect(history).toHaveLength(0);
    });

    it('should clear history for specific variable', () => {
      service.recordHistory('var1', 'old', 'new', 'global', 'source');
      service.recordHistory('var2', 'old', 'new', 'global', 'source');

      service.clearHistory('var1');
      const history = service.getHistory();
      expect(history).toHaveLength(1);
      expect(history[0].variableName).toBe('var2');
    });
  });

  describe('suggestExtractionMethod', () => {
    it('should suggest jsonpath for JSON responses', () => {
      const response: Response = {
        status: 200,
        statusText: 'OK',
        headers: { 'content-type': 'application/json' },
        body: {},
        time: 100,
        size: 1024,
        timestamp: new Date(),
      };

      const method = service.suggestExtractionMethod(response);
      expect(method).toBe('jsonpath');
    });

    it('should suggest xpath for XML responses', () => {
      const response: Response = {
        status: 200,
        statusText: 'OK',
        headers: { 'content-type': 'application/xml' },
        body: '',
        time: 100,
        size: 1024,
        timestamp: new Date(),
      };

      const method = service.suggestExtractionMethod(response);
      expect(method).toBe('xpath');
    });

    it('should suggest regex for other content types', () => {
      const response: Response = {
        status: 200,
        statusText: 'OK',
        headers: { 'content-type': 'text/plain' },
        body: '',
        time: 100,
        size: 1024,
        timestamp: new Date(),
      };

      const method = service.suggestExtractionMethod(response);
      expect(method).toBe('regex');
    });
  });

  describe('Import/Export Rules', () => {
    it('should export rules to JSON', () => {
      service.addRule({
        name: 'Test Rule',
        enabled: true,
        source: 'body',
        extractionType: 'jsonpath',
        pattern: '$.data',
        variableName: 'testVar',
        scope: 'global',
      });

      const json = service.exportRules();
      expect(json).toBeDefined();

      const parsed = JSON.parse(json);
      expect(Array.isArray(parsed)).toBe(true);
      expect(parsed).toHaveLength(1);
    });

    it('should import rules from JSON', () => {
      const rules = [
        {
          id: 'imported-1',
          name: 'Imported Rule',
          enabled: true,
          source: 'body',
          extractionType: 'jsonpath',
          pattern: '$.data',
          variableName: 'importedVar',
          scope: 'global',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ];

      const json = JSON.stringify(rules);
      const count = service.importRules(json);

      expect(count).toBe(1);
      const allRules = service.getRules();
      expect(allRules).toHaveLength(1);
      expect(allRules[0].name).toBe('Imported Rule');
    });

    it('should fail on invalid JSON import', () => {
      expect(() => {
        service.importRules('invalid json');
      }).toThrow();
    });
  });
});
