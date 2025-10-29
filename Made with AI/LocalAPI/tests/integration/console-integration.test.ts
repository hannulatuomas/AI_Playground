/**
 * Console Integration Tests
 * 
 * Tests the complete console logging workflow:
 * - Request/Response logging integration
 * - Script console output integration
 * - Filtering and searching workflows
 * - Export workflows
 * - Persistence and recovery
 */

import { ConsoleService } from '../../src/main/services/ConsoleService';
import { createTestDatabase, clearMockDatabase } from '../utils/database-test-utils';

describe('Console Integration Tests', () => {
  let consoleService: ConsoleService;
  let testDb: any;
  let mockDb: any;

  beforeEach(() => {
    const result = createTestDatabase();
    testDb = result.db;
    mockDb = result.mockDb;
    consoleService = new ConsoleService(testDb.getDatabase());
  });

  afterEach(() => {
    clearMockDatabase(mockDb);
  });

  describe('End-to-end request/response logging', () => {
    it('should log complete HTTP request/response cycle', () => {
      const requestId = 'req-123';

      // Log request
      const requestEntry = consoleService.logRequest({
        method: 'POST',
        url: 'https://api.example.com/login',
        headers: { 'Content-Type': 'application/json' },
        body: { username: 'test', password: 'pass' },
      }, { requestId });

      expect(requestEntry.requestId).toBe(requestId);
      expect(requestEntry.type).toBe('request');

      // Log response
      const responseEntry = consoleService.logResponse({
        status: 200,
        statusText: 'OK',
        headers: { 'Set-Cookie': 'session=abc123' },
        body: { token: 'jwt-token' },
      }, {
        method: 'POST',
        url: 'https://api.example.com/login',
      }, {
        requestId,
        duration: 145,
      });

      expect(responseEntry.requestId).toBe(requestId);
      expect(responseEntry.type).toBe('response');

      // Verify both entries are retrievable
      const entries = consoleService.getEntries({ requestId });
      expect(entries.length).toBe(2);
      expect(entries.some(e => e.type === 'request')).toBe(true);
      expect(entries.some(e => e.type === 'response')).toBe(true);
    });

    it('should handle multiple concurrent requests', () => {
      const requests = [
        { id: 'req-1', url: '/api/users', method: 'GET' },
        { id: 'req-2', url: '/api/products', method: 'GET' },
        { id: 'req-3', url: '/api/orders', method: 'POST' },
      ];

      // Log all requests
      requests.forEach(req => {
        consoleService.logRequest({
          method: req.method,
          url: req.url,
        }, { requestId: req.id });
      });

      // Log responses
      requests.forEach(req => {
        consoleService.logResponse({
          status: 200,
          statusText: 'OK',
        }, {
          method: req.method,
          url: req.url,
        }, {
          requestId: req.id,
          duration: Math.random() * 200,
        });
      });

      const allEntries = consoleService.getEntries();
      expect(allEntries.length).toBe(6); // 3 requests + 3 responses
    });

    it('should log failed requests with errors', () => {
      const requestId = 'req-error';

      consoleService.logRequest({
        method: 'GET',
        url: 'https://api.example.com/data',
      }, { requestId });

      consoleService.logError('Network timeout', {
        requestId,
        url: 'https://api.example.com/data',
        method: 'GET',
      });

      const entries = consoleService.getEntries({ requestId });
      expect(entries.length).toBe(2);
      expect(entries.some(e => e.type === 'error')).toBe(true);
    });
  });

  describe('Script console output integration', () => {
    it('should capture script console output during request', () => {
      const requestId = 'req-script-123';

      consoleService.logRequest({
        method: 'GET',
        url: '/api/test',
      }, { requestId });

      // Simulate script execution
      consoleService.logScriptOutput('Starting test execution', 'log', requestId);
      consoleService.logScriptOutput('Validating response', 'info', requestId);
      consoleService.logScriptOutput('Test passed!', 'log', requestId);

      const entries = consoleService.getEntries({ requestId });
      expect(entries.length).toBe(4); // 1 request + 3 script outputs

      const scriptEntries = entries.filter(e => e.type === 'script');
      expect(scriptEntries.length).toBe(3);
    });

    it('should capture script errors', () => {
      const requestId = 'req-error-123';

      consoleService.logScriptOutput('Assertion failed: status !== 200', 'error', requestId);

      const entries = consoleService.getEntries({ requestId });
      const errorEntry = entries.find(e => e.logLevel === 'error');
      
      expect(errorEntry).toBeDefined();
      expect(errorEntry?.scriptOutput).toContain('Assertion failed');
    });
  });

  describe('WebSocket and SSE logging', () => {
    it('should log WebSocket bidirectional communication', () => {
      const connectionId = 'ws-conn-123';

      consoleService.logWebSocketMessage('Hello Server', 'sent', connectionId);
      consoleService.logWebSocketMessage('Hello Client', 'received', connectionId);
      consoleService.logWebSocketMessage('Message 2', 'sent', connectionId);
      consoleService.logWebSocketMessage('Response 2', 'received', connectionId);

      const entries = consoleService.getEntries({ types: ['websocket'] });
      expect(entries.length).toBe(4);

      const sent = entries.filter(e => e.direction === 'sent');
      const received = entries.filter(e => e.direction === 'received');
      
      expect(sent.length).toBe(2);
      expect(received.length).toBe(2);
    });

    it('should log Server-Sent Events stream', () => {
      const connectionId = 'sse-conn-456';

      for (let i = 0; i < 5; i++) {
        consoleService.logSSEMessage({
          type: 'update',
          data: `Event ${i}`,
        }, connectionId, {
          url: 'https://api.example.com/events',
        });
      }

      const entries = consoleService.getEntries({ types: ['sse'] });
      expect(entries.length).toBe(5);
      
      entries.forEach((entry, index) => {
        expect(entry.eventType).toBe('update');
        expect(entry.body).toBe(`Event ${index}`);
      });
    });
  });

  describe('Filtering and searching workflows', () => {
    beforeEach(() => {
      // Setup test data
      consoleService.logRequest({ method: 'GET', url: '/api/users' });
      consoleService.logResponse(
        { status: 200, statusText: 'OK' },
        { method: 'GET', url: '/api/users' },
        { duration: 100 }
      );

      consoleService.logRequest({ method: 'POST', url: '/api/products' });
      consoleService.logResponse(
        { status: 201, statusText: 'Created' },
        { method: 'POST', url: '/api/products' },
        { duration: 200 }
      );

      consoleService.logRequest({ method: 'GET', url: '/api/orders' });
      consoleService.logResponse(
        { status: 500, statusText: 'Internal Server Error' },
        { method: 'GET', url: '/api/orders' },
        { duration: 50 }
      );

      consoleService.logError('Database connection failed');
    });

    it('should filter by HTTP method', () => {
      const getEntries = consoleService.getEntries({ methods: ['GET'] });
      expect(getEntries.length).toBe(4); // 2 GET requests + 2 GET responses
    });

    it('should filter by status code', () => {
      const successEntries = consoleService.getEntries({ statuses: [200, 201] });
      expect(successEntries.length).toBe(2);

      const errorEntries = consoleService.getEntries({ statuses: [500] });
      expect(errorEntries.length).toBe(1);
    });

    it('should filter by multiple criteria', () => {
      const entries = consoleService.getEntries({
        types: ['response'],
        methods: ['POST'],
        statuses: [201],
      });

      expect(entries.length).toBe(1);
      expect(entries[0].method).toBe('POST');
      expect(entries[0].status).toBe(201);
    });

    it('should search across multiple fields', () => {
      const results = consoleService.searchEntries('products');
      expect(results.length).toBe(2); // request + response

      const errorResults = consoleService.searchEntries('Database');
      expect(errorResults.length).toBe(1);
    });

    it('should filter entries with errors', () => {
      const errorEntries = consoleService.getEntries({ hasError: true });
      expect(errorEntries.length).toBe(1);
      expect(errorEntries[0].type).toBe('error');
    });
  });

  describe('Export workflows', () => {
    beforeEach(() => {
      // Create sample data for export
      for (let i = 0; i < 5; i++) {
        consoleService.logRequest({
          method: i % 2 === 0 ? 'GET' : 'POST',
          url: `/api/resource/${i}`,
          headers: { 'X-Request-ID': `req-${i}` },
        });

        consoleService.logResponse({
          status: 200,
          statusText: 'OK',
          headers: { 'Content-Type': 'application/json' },
          body: { id: i, data: 'test' },
        }, {
          method: i % 2 === 0 ? 'GET' : 'POST',
          url: `/api/resource/${i}`,
        }, {
          duration: 100 + i * 10,
        });
      }
    });

    it('should export filtered entries to JSON', () => {
      const json = consoleService.exportEntries({
        format: 'json',
        filters: { methods: ['GET'] },
        includeHeaders: true,
        includeBody: true,
      });

      const parsed = JSON.parse(json);
      expect(Array.isArray(parsed)).toBe(true);
      expect(parsed.every((entry: any) => entry.method === 'GET')).toBe(true);
    });

    it('should export to CSV with proper formatting', () => {
      const csv = consoleService.exportEntries({
        format: 'csv',
      });

      const lines = csv.split('\n');
      expect(lines[0]).toContain('ID,Timestamp,Type,Method,URL');
      expect(lines.length).toBeGreaterThan(1);
    });

    it('should export to HAR format with proper structure', () => {
      const har = consoleService.exportEntries({
        format: 'har',
        includeHeaders: true,
        includeBody: true,
      });

      const parsed = JSON.parse(har);
      expect(parsed.log).toBeDefined();
      expect(parsed.log.version).toBe('1.2');
      expect(parsed.log.creator.name).toBe('LocalAPI');
      expect(Array.isArray(parsed.log.entries)).toBe(true);
      expect(parsed.log.entries.length).toBeGreaterThan(0);
    });
  });

  describe('Persistence and recovery', () => {
    it('should persist entries to database', () => {
      consoleService.setPersistence(true);

      consoleService.logRequest({ method: 'GET', url: '/test' });
      consoleService.logResponse(
        { status: 200, statusText: 'OK' },
        { method: 'GET', url: '/test' }
      );

      // Entries should be persisted
      const entries = consoleService.getEntries();
      expect(entries.length).toBe(2);
    });

    it('should recover entries after restart', async () => {
      consoleService.setPersistence(true);

      // Log some entries
      for (let i = 0; i < 3; i++) {
        consoleService.logRequest({ method: 'GET', url: `/test${i}` });
      }

      // Simulate restart by creating new service instance
      const newService = new ConsoleService(testDb.getDatabase());
      await newService.loadFromDisk();

      const entries = newService.getEntries();
      expect(entries.length).toBe(3);
    });

    it('should respect max entries limit on recovery', async () => {
      consoleService.setMaxEntries(5);
      consoleService.setPersistence(true);

      // Log 10 entries
      for (let i = 0; i < 10; i++) {
        consoleService.logRequest({ method: 'GET', url: `/test${i}` });
      }

      // Create new service and load
      const newService = new ConsoleService(testDb.getDatabase());
      newService.setMaxEntries(5);
      await newService.loadFromDisk();

      const entries = newService.getEntries();
      expect(entries.length).toBe(5);
    });
  });

  describe('Performance and stress tests', () => {
    it('should handle large number of entries efficiently', () => {
      const startTime = Date.now();

      // Log 1000 entries
      for (let i = 0; i < 1000; i++) {
        consoleService.logRequest({
          method: 'GET',
          url: `/api/resource/${i}`,
          headers: { 'X-Index': `${i}` },
        });
      }

      const endTime = Date.now();
      const duration = endTime - startTime;

      // Should complete in reasonable time (less than 1 second)
      expect(duration).toBeLessThan(1000);

      const entries = consoleService.getEntries();
      expect(entries.length).toBe(1000);
    });

    it('should handle concurrent logging', () => {
      const promises = [];

      for (let i = 0; i < 100; i++) {
        promises.push(
          Promise.resolve(consoleService.logRequest({
            method: 'GET',
            url: `/concurrent/${i}`,
          }))
        );
      }

      return Promise.all(promises).then(() => {
        const entries = consoleService.getEntries();
        expect(entries.length).toBe(100);
      });
    });

    it('should maintain circular buffer efficiently', () => {
      consoleService.setMaxEntries(100);

      // Log 500 entries
      for (let i = 0; i < 500; i++) {
        consoleService.logRequest({ method: 'GET', url: `/test${i}` });
      }

      const entries = consoleService.getEntries();
      expect(entries.length).toBe(100);

      // Verify oldest entries were removed
      const hasOldEntry = entries.some(e => e.url === '/test0');
      expect(hasOldEntry).toBe(false);

      const hasNewEntry = entries.some(e => e.url === '/test499');
      expect(hasNewEntry).toBe(true);
    });
  });

  describe('Statistics and analytics', () => {
    beforeEach(() => {
      // Create varied test data
      consoleService.logRequest({ method: 'GET', url: '/api/fast' });
      consoleService.logResponse(
        { status: 200, statusText: 'OK' },
        { method: 'GET', url: '/api/fast' },
        { duration: 50 }
      );

      consoleService.logRequest({ method: 'GET', url: '/api/slow' });
      consoleService.logResponse(
        { status: 200, statusText: 'OK' },
        { method: 'GET', url: '/api/slow' },
        { duration: 250 }
      );

      consoleService.logRequest({ method: 'POST', url: '/api/error' });
      consoleService.logError('Server error');
    });

    it('should calculate accurate statistics', () => {
      const stats = consoleService.getStats();

      expect(stats.totalEntries).toBe(6);
      expect(stats.requestCount).toBe(3);
      expect(stats.responseCount).toBe(2);
      expect(stats.errorCount).toBe(1);
      expect(stats.averageDuration).toBe(150); // (50 + 250) / 2
    });

    it('should update stats as entries are added', () => {
      const statsBefore = consoleService.getStats();
      
      consoleService.logRequest({ method: 'GET', url: '/new' });
      consoleService.logResponse(
        { status: 200, statusText: 'OK' },
        { method: 'GET', url: '/new' },
        { duration: 100 }
      );

      const statsAfter = consoleService.getStats();

      expect(statsAfter.totalEntries).toBe(statsBefore.totalEntries + 2);
      expect(statsAfter.requestCount).toBe(statsBefore.requestCount + 1);
      expect(statsAfter.responseCount).toBe(statsBefore.responseCount + 1);
    });
  });
});
