import { BatchRunnerService } from '../../src/main/services/BatchRunnerService';

describe('BatchRunnerService', () => {
  let service: BatchRunnerService;

  beforeEach(() => {
    service = new BatchRunnerService();
  });

  describe('Batch Execution', () => {
    test('should execute batch of requests', async () => {
      const result = await service.executeBatch({
        name: 'Test Batch',
        requests: [
          {
            id: '1',
            name: 'Request 1',
            method: 'GET',
            url: 'https://example.com/api/1',
          },
          {
            id: '2',
            name: 'Request 2',
            method: 'GET',
            url: 'https://example.com/api/2',
          },
        ],
      });

      expect(result).toBeDefined();
      expect(result.name).toBe('Test Batch');
      expect(result.results.length).toBe(2);
      expect(result.status).toBe('completed');
    });

    test('should track success and failure counts', async () => {
      const result = await service.executeBatch({
        name: 'Count Test',
        requests: [
          {
            id: '1',
            name: 'Request 1',
            method: 'GET',
            url: 'https://example.com/api',
          },
        ],
      });

      expect(result.totalRequests).toBe(1);
      expect(result.successCount + result.failedCount + result.skippedCount).toBe(1);
    });
  });

  describe('Variable Extraction', () => {
    test('should extract variables from response', async () => {
      const result = await service.executeBatch({
        name: 'Variable Test',
        requests: [
          {
            id: '1',
            name: 'Login',
            method: 'POST',
            url: 'https://example.com/login',
            extractVariables: [
              {
                name: 'token',
                source: 'body',
                path: 'access_token',
              },
            ],
          },
        ],
      });

      expect(result.variables).toBeDefined();
    });
  });

  describe('Collection Generation', () => {
    test('should generate batch from collection', () => {
      const collection = {
        name: 'Test Collection',
        children: [
          {
            type: 'request',
            id: '1',
            name: 'Request 1',
            method: 'GET',
            url: 'https://example.com/api',
          },
          {
            type: 'folder',
            children: [
              {
                type: 'request',
                id: '2',
                name: 'Request 2',
                method: 'POST',
                url: 'https://example.com/api',
              },
            ],
          },
        ],
      };

      const requests = service.generateBatchFromCollection(collection);
      expect(requests.length).toBe(2);
    });
  });

  describe('Export', () => {
    test('should export results as JSON', async () => {
      const result = await service.executeBatch({
        name: 'Export Test',
        requests: [
          {
            id: '1',
            name: 'Request 1',
            method: 'GET',
            url: 'https://example.com/api',
          },
        ],
      });

      const json = service.exportResults(result.id, 'json');
      expect(json).toBeDefined();
      expect(() => JSON.parse(json)).not.toThrow();
    });

    test('should export results as CSV', async () => {
      const result = await service.executeBatch({
        name: 'CSV Test',
        requests: [
          {
            id: '1',
            name: 'Request 1',
            method: 'GET',
            url: 'https://example.com/api',
          },
        ],
      });

      const csv = service.exportResults(result.id, 'csv');
      expect(csv).toContain('Request,Status');
    });
  });

  describe('Statistics', () => {
    test('should calculate summary statistics', async () => {
      const result = await service.executeBatch({
        name: 'Stats Test',
        requests: [
          {
            id: '1',
            name: 'Request 1',
            method: 'GET',
            url: 'https://example.com/api',
          },
        ],
      });

      const summary = service.getSummary(result.id);
      expect(summary).toBeDefined();
      expect(summary?.totalRequests).toBe(1);
    });
  });
});
