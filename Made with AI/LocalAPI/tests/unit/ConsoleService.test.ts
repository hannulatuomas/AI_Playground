/**
 * ConsoleService Unit Tests
 * 
 * Tests all methods of ConsoleService:
 * - Logging methods (logRequest, logResponse, logWebSocketMessage, logSSEMessage, logScriptOutput, logError)
 * - Entry retrieval (getEntries, getEntry, searchEntries)
 * - Entry management (clearEntries, deleteEntry)
 * - Export functionality (exportEntries - JSON, CSV, HAR)
 * - Settings (setPersistence, setMaxEntries, setPaused)
 * - Statistics (getStats)
 */

import { ConsoleService } from '../../src/main/services/ConsoleService';
import { createTestDatabase, clearMockDatabase } from '../utils/database-test-utils';

describe('ConsoleService', () => {
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

  describe('logRequest', () => {
    it('should log an HTTP request', () => {
      const entry = consoleService.logRequest({
        method: 'GET',
        url: 'https://api.example.com/users',
        headers: { 'Content-Type': 'application/json' },
        body: null,
      });

      expect(entry).toBeDefined();
      expect(entry.type).toBe('request');
      expect(entry.method).toBe('GET');
      expect(entry.url).toBe('https://api.example.com/users');
      expect(entry.headers).toEqual({ 'Content-Type': 'application/json' });
      expect(entry.requestId).toBeDefined();
    });

    it('should generate unique request IDs', () => {
      const entry1 = consoleService.logRequest({ method: 'GET', url: '/test1' });
      const entry2 = consoleService.logRequest({ method: 'GET', url: '/test2' });

      expect(entry1.requestId).toBeDefined();
      expect(entry2.requestId).toBeDefined();
      expect(entry1.requestId).not.toBe(entry2.requestId);
    });

    it('should use provided request ID if given', () => {
      const customRequestId = 'custom-request-123';
      const entry = consoleService.logRequest(
        { method: 'POST', url: '/api/test' },
        { requestId: customRequestId }
      );

      expect(entry.requestId).toBe(customRequestId);
    });
  });

  describe('logResponse', () => {
    it('should log an HTTP response', () => {
      const entry = consoleService.logResponse(
        {
          status: 200,
          statusText: 'OK',
          headers: { 'Content-Type': 'application/json' },
          body: { data: 'test' },
        },
        {
          method: 'GET',
          url: 'https://api.example.com/users',
        },
        {
          duration: 245,
          cached: false,
        }
      );

      expect(entry).toBeDefined();
      expect(entry.type).toBe('response');
      expect(entry.status).toBe(200);
      expect(entry.statusText).toBe('OK');
      expect(entry.duration).toBe(245);
      expect(entry.cached).toBe(false);
    });

    it('should link response to request with same requestId', () => {
      const requestId = 'test-request-123';
      
      consoleService.logRequest(
        { method: 'POST', url: '/api/login' },
        { requestId }
      );

      const responseEntry = consoleService.logResponse(
        { status: 200, statusText: 'OK' },
        { method: 'POST', url: '/api/login' },
        { requestId }
      );

      expect(responseEntry.requestId).toBe(requestId);
    });

    it('should log cached responses', () => {
      const entry = consoleService.logResponse(
        { status: 200, statusText: 'OK', body: { cached: true } },
        { method: 'GET', url: '/api/data' },
        { cached: true, duration: 5 }
      );

      expect(entry.cached).toBe(true);
    });
  });

  describe('logWebSocketMessage', () => {
    it('should log a sent WebSocket message', () => {
      const entry = consoleService.logWebSocketMessage(
        'Hello WebSocket',
        'sent',
        'ws-connection-123'
      );

      expect(entry).toBeDefined();
      expect(entry.type).toBe('websocket');
      expect(entry.body).toBe('Hello WebSocket');
      expect(entry.direction).toBe('sent');
      expect(entry.connectionId).toBe('ws-connection-123');
      expect(entry.protocol).toBe('WebSocket');
    });

    it('should log a received WebSocket message', () => {
      const entry = consoleService.logWebSocketMessage(
        Buffer.from('Binary data'),
        'received',
        'ws-connection-456'
      );

      expect(entry.direction).toBe('received');
      expect(entry.body).toBe('Binary data');
    });
  });

  describe('logSSEMessage', () => {
    it('should log a Server-Sent Event', () => {
      const entry = consoleService.logSSEMessage(
        {
          type: 'update',
          data: '{"message": "New update"}',
          id: 'event-123',
        },
        'sse-connection-789',
        {
          url: 'https://api.example.com/events',
        }
      );

      expect(entry).toBeDefined();
      expect(entry.type).toBe('sse');
      expect(entry.eventType).toBe('update');
      expect(entry.body).toBe('{"message": "New update"}');
      expect(entry.connectionId).toBe('sse-connection-789');
      expect(entry.protocol).toBe('SSE');
    });
  });

  describe('logScriptOutput', () => {
    it('should log script console.log output', () => {
      const entry = consoleService.logScriptOutput(
        'Test log message',
        'log',
        'request-123'
      );

      expect(entry).toBeDefined();
      expect(entry.type).toBe('script');
      expect(entry.scriptOutput).toBe('Test log message');
      expect(entry.logLevel).toBe('log');
      expect(entry.requestId).toBe('request-123');
    });

    it('should log script console.error output', () => {
      const entry = consoleService.logScriptOutput(
        'Error in script',
        'error'
      );

      expect(entry.logLevel).toBe('error');
      expect(entry.scriptOutput).toBe('Error in script');
    });

    it('should log script console.warn output', () => {
      const entry = consoleService.logScriptOutput(
        'Warning message',
        'warn'
      );

      expect(entry.logLevel).toBe('warn');
    });
  });

  describe('logError', () => {
    it('should log an error with context', () => {
      const error = new Error('Network timeout');
      const entry = consoleService.logError(error, {
        url: 'https://api.example.com/data',
        method: 'GET',
        requestId: 'req-456',
      });

      expect(entry).toBeDefined();
      expect(entry.type).toBe('error');
      expect(entry.error).toBe('Network timeout');
      expect(entry.url).toBe('https://api.example.com/data');
      expect(entry.method).toBe('GET');
      expect(entry.logLevel).toBe('error');
    });

    it('should log string errors', () => {
      const entry = consoleService.logError('Simple error message');

      expect(entry.error).toBe('Simple error message');
    });
  });

  describe('getEntries', () => {
    beforeEach(() => {
      // Add test entries
      consoleService.logRequest({ method: 'GET', url: '/api/users' });
      consoleService.logRequest({ method: 'POST', url: '/api/login' });
      consoleService.logResponse(
        { status: 200, statusText: 'OK' },
        { method: 'GET', url: '/api/users' }
      );
      consoleService.logError('Test error');
    });

    it('should return all entries', () => {
      const entries = consoleService.getEntries();
      expect(entries.length).toBe(4);
    });

    it('should filter by type', () => {
      const entries = consoleService.getEntries({
        types: ['request'],
      });

      expect(entries.length).toBe(2);
      entries.forEach(entry => {
        expect(entry.type).toBe('request');
      });
    });

    it('should filter by method', () => {
      const entries = consoleService.getEntries({
        methods: ['GET'],
      });

      expect(entries.length).toBe(2); // 1 request + 1 response
    });

    it('should filter by status', () => {
      const entries = consoleService.getEntries({
        statuses: [200],
      });

      expect(entries.length).toBe(1);
      expect(entries[0].status).toBe(200);
    });

    it('should filter by error', () => {
      const entries = consoleService.getEntries({
        hasError: true,
      });

      expect(entries.length).toBe(1);
      expect(entries[0].type).toBe('error');
    });

    it('should search entries', () => {
      const entries = consoleService.getEntries({
        search: 'login',
      });

      expect(entries.length).toBe(1);
      expect(entries[0].url).toContain('login');
    });

    it('should apply pagination', () => {
      const entries = consoleService.getEntries({}, 2, 0);
      expect(entries.length).toBe(2);
    });
  });

  describe('getEntry', () => {
    it('should get entry by ID', () => {
      const loggedEntry = consoleService.logRequest({ method: 'GET', url: '/test' });
      const entry = consoleService.getEntry(loggedEntry.id);

      expect(entry).toBeDefined();
      expect(entry?.id).toBe(loggedEntry.id);
    });

    it('should return null for non-existent ID', () => {
      const entry = consoleService.getEntry('non-existent-id');
      expect(entry).toBeNull();
    });
  });

  describe('searchEntries', () => {
    beforeEach(() => {
      consoleService.logRequest({ method: 'GET', url: '/api/users' });
      consoleService.logRequest({ method: 'POST', url: '/api/products' });
      consoleService.logError('Database connection failed');
    });

    it('should search by URL', () => {
      const entries = consoleService.searchEntries('users');
      expect(entries.length).toBe(1);
      expect(entries[0].url).toContain('users');
    });

    it('should search by error message', () => {
      const entries = consoleService.searchEntries('Database');
      expect(entries.length).toBe(1);
      expect(entries[0].error).toContain('Database');
    });

    it('should be case-insensitive', () => {
      const entries = consoleService.searchEntries('PRODUCTS');
      expect(entries.length).toBe(1);
    });
  });

  describe('clearEntries', () => {
    beforeEach(() => {
      consoleService.logRequest({ method: 'GET', url: '/test1' });
      consoleService.logRequest({ method: 'GET', url: '/test2' });
      consoleService.logRequest({ method: 'GET', url: '/test3' });
    });

    it('should clear all entries', () => {
      consoleService.clearEntries();
      const entries = consoleService.getEntries();
      expect(entries.length).toBe(0);
    });

    it('should clear entries older than timestamp', () => {
      const now = Date.now();
      
      // Wait a bit and add another entry
      setTimeout(() => {
        consoleService.logRequest({ method: 'GET', url: '/test4' });
      }, 10);

      setTimeout(() => {
        consoleService.clearEntries(now + 5);
        const entries = consoleService.getEntries();
        expect(entries.length).toBe(1); // Only the newest entry remains
      }, 20);
    });
  });

  describe('deleteEntry', () => {
    it('should delete an entry by ID', () => {
      const entry = consoleService.logRequest({ method: 'GET', url: '/test' });
      
      const deleted = consoleService.deleteEntry(entry.id);
      expect(deleted).toBe(true);

      const retrieved = consoleService.getEntry(entry.id);
      expect(retrieved).toBeNull();
    });

    it('should return false for non-existent ID', () => {
      const deleted = consoleService.deleteEntry('non-existent');
      expect(deleted).toBe(false);
    });
  });

  describe('exportEntries', () => {
    beforeEach(() => {
      consoleService.logRequest({ 
        method: 'GET', 
        url: 'https://api.example.com/users',
        headers: { 'Authorization': 'Bearer token' },
      });
      consoleService.logResponse(
        { 
          status: 200, 
          statusText: 'OK',
          headers: { 'Content-Type': 'application/json' },
          body: { users: [] },
        },
        { method: 'GET', url: 'https://api.example.com/users' },
        { duration: 123 }
      );
    });

    it('should export to JSON format', () => {
      const json = consoleService.exportEntries({
        format: 'json',
        includeHeaders: true,
        includeBody: true,
      });

      expect(json).toBeDefined();
      const parsed = JSON.parse(json);
      expect(Array.isArray(parsed)).toBe(true);
      expect(parsed.length).toBe(2);
    });

    it('should export to CSV format', () => {
      const csv = consoleService.exportEntries({
        format: 'csv',
      });

      expect(csv).toBeDefined();
      expect(csv).toContain('ID,Timestamp,Type,Method,URL');
      expect(csv).toContain('GET');
      expect(csv).toContain('https://api.example.com/users');
    });

    it('should export to HAR format', () => {
      const har = consoleService.exportEntries({
        format: 'har',
        includeHeaders: true,
        includeBody: true,
      });

      expect(har).toBeDefined();
      const parsed = JSON.parse(har);
      expect(parsed.log).toBeDefined();
      expect(parsed.log.version).toBe('1.2');
      expect(parsed.log.creator.name).toBe('LocalAPI');
      expect(Array.isArray(parsed.log.entries)).toBe(true);
    });

    it('should throw error for unsupported format', () => {
      expect(() => {
        consoleService.exportEntries({
          format: 'xml' as any,
        });
      }).toThrow('Unsupported export format');
    });
  });

  describe('setPersistence', () => {
    it('should enable persistence', () => {
      consoleService.setPersistence(true);
      // Persistence is enabled, entries should be saved to database
      const entry = consoleService.logRequest({ method: 'GET', url: '/test' });
      expect(entry).toBeDefined();
    });

    it('should disable persistence', () => {
      consoleService.setPersistence(false);
      const entry = consoleService.logRequest({ method: 'GET', url: '/test' });
      expect(entry).toBeDefined();
    });
  });

  describe('setMaxEntries', () => {
    it('should set max entries limit', () => {
      consoleService.setMaxEntries(5);

      // Log more than max entries
      for (let i = 0; i < 10; i++) {
        consoleService.logRequest({ method: 'GET', url: `/test${i}` });
      }

      const entries = consoleService.getEntries();
      expect(entries.length).toBe(5);
    });

    it('should trim existing entries if new max is lower', () => {
      // Log 10 entries
      for (let i = 0; i < 10; i++) {
        consoleService.logRequest({ method: 'GET', url: `/test${i}` });
      }

      consoleService.setMaxEntries(3);
      const entries = consoleService.getEntries();
      expect(entries.length).toBe(3);
    });
  });

  describe('setPaused', () => {
    it('should pause logging', () => {
      consoleService.setPaused(true);
      
      consoleService.logRequest({ method: 'GET', url: '/test' });
      
      const entries = consoleService.getEntries();
      expect(entries.length).toBe(0); // Entry not logged when paused
    });

    it('should resume logging', () => {
      consoleService.setPaused(true);
      consoleService.setPaused(false);
      
      consoleService.logRequest({ method: 'GET', url: '/test' });
      
      const entries = consoleService.getEntries();
      expect(entries.length).toBe(1);
    });

    it('should report paused state', () => {
      consoleService.setPaused(true);
      expect(consoleService.isPausedState()).toBe(true);

      consoleService.setPaused(false);
      expect(consoleService.isPausedState()).toBe(false);
    });
  });

  describe('getStats', () => {
    beforeEach(() => {
      consoleService.logRequest({ method: 'GET', url: '/test1' });
      consoleService.logRequest({ method: 'POST', url: '/test2' });
      consoleService.logResponse(
        { status: 200, statusText: 'OK' },
        { method: 'GET', url: '/test1' },
        { duration: 100 }
      );
      consoleService.logResponse(
        { status: 404, statusText: 'Not Found' },
        { method: 'POST', url: '/test2' },
        { duration: 200 }
      );
      consoleService.logError('Test error');
    });

    it('should calculate statistics', () => {
      const stats = consoleService.getStats();

      expect(stats.totalEntries).toBe(5);
      expect(stats.requestCount).toBe(2);
      expect(stats.responseCount).toBe(2);
      expect(stats.errorCount).toBe(1);
      expect(stats.averageDuration).toBe(150); // (100 + 200) / 2
    });
  });

  describe('circular buffer behavior', () => {
    it('should maintain max entries as circular buffer', () => {
      consoleService.setMaxEntries(3);

      consoleService.logRequest({ method: 'GET', url: '/test1' });
      consoleService.logRequest({ method: 'GET', url: '/test2' });
      consoleService.logRequest({ method: 'GET', url: '/test3' });
      consoleService.logRequest({ method: 'GET', url: '/test4' }); // This should remove /test1

      const entries = consoleService.getEntries();
      expect(entries.length).toBe(3);
      expect(entries.find(e => e.url === '/test1')).toBeUndefined();
      expect(entries.find(e => e.url === '/test4')).toBeDefined();
    });
  });
});
