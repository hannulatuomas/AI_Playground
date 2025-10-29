import { FuzzingService, FuzzingOptions } from '../src/main/services/FuzzingService';

// Mock axios to avoid real HTTP calls
jest.mock('axios');
const axios = require('axios');

describe('FuzzingService', () => {
  let service: FuzzingService;

  beforeEach(() => {
    service = new FuzzingService();
    jest.clearAllMocks();
    
    // Mock axios to return successful responses
    axios.mockResolvedValue({
      status: 200,
      data: { success: true },
      config: { url: 'https://httpbin.org/post' },
    });
  });

  describe('runFuzzing', () => {
    it('should run string fuzzing tests', async () => {
      const options: FuzzingOptions = {
        targetUrl: 'https://httpbin.org/post',
        method: 'POST',
        fuzzingType: 'string',
        intensity: 'low',
        maxRequests: 10,
      };

      const result = await service.runFuzzing(options);

      expect(result).toBeDefined();
      expect(result.testId).toMatch(/^fuzz-/);
      expect(result.fuzzingType).toBe('string');
      expect(result.totalTests).toBeGreaterThan(0);
      expect(result.totalTests).toBeLessThanOrEqual(10);
      expect(result.findings).toBeInstanceOf(Array);
      expect(result.summary).toBeDefined();
    });

    it('should run number fuzzing tests', async () => {
      const options: FuzzingOptions = {
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'number',
        intensity: 'low',
        maxRequests: 10,
      };

      const result = await service.runFuzzing(options);

      expect(result.fuzzingType).toBe('number');
      expect(result.totalTests).toBeGreaterThan(0);
    });

    it('should run injection fuzzing tests', async () => {
      const options: FuzzingOptions = {
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'injection',
        intensity: 'low',
        maxRequests: 10,
      };

      const result = await service.runFuzzing(options);

      expect(result.fuzzingType).toBe('injection');
      expect(result.totalTests).toBeGreaterThan(0);
    });

    it('should run all fuzzing types', async () => {
      const options: FuzzingOptions = {
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'all',
        intensity: 'low',
        maxRequests: 30,
      };

      const result = await service.runFuzzing(options);

      expect(result.fuzzingType).toBe('all');
      expect(result.totalTests).toBeGreaterThan(0);
    });

    it('should respect maxRequests limit', async () => {
      const options: FuzzingOptions = {
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'string',
        maxRequests: 5,
      };

      const result = await service.runFuzzing(options);

      expect(result.totalTests).toBeLessThanOrEqual(5);
    });

    it('should respect intensity settings', async () => {
      const lowOptions: FuzzingOptions = {
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'string',
        intensity: 'low',
      };

      const highOptions: FuzzingOptions = {
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'string',
        intensity: 'high',
      };

      const lowResult = await service.runFuzzing(lowOptions);
      const highResult = await service.runFuzzing(highOptions);

      expect(highResult.totalTests).toBeGreaterThanOrEqual(lowResult.totalTests);
      expect(lowResult.totalTests).toBeGreaterThan(0);
      expect(highResult.totalTests).toBeGreaterThan(0);
    });

    it('should include duration in results', async () => {
      const options: FuzzingOptions = {
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'string',
        intensity: 'low',
        maxRequests: 5,
      };

      const result = await service.runFuzzing(options);

      expect(result.duration).toBeGreaterThanOrEqual(0);
      expect(typeof result.duration).toBe('number');
    });

    it('should generate summary statistics', async () => {
      const options: FuzzingOptions = {
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'string',
        intensity: 'low',
        maxRequests: 10,
      };

      const result = await service.runFuzzing(options);

      expect(result.summary).toBeDefined();
      expect(result.summary.crashes).toBeGreaterThanOrEqual(0);
      expect(result.summary.errors).toBeGreaterThanOrEqual(0);
      expect(result.summary.timeouts).toBeGreaterThanOrEqual(0);
      expect(result.summary.anomalies).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Payload Generators', () => {
    it('should generate string fuzzing payloads', () => {
      const payloads = (service as any).generateStringFuzzPayloads();

      expect(payloads).toBeInstanceOf(Array);
      expect(payloads.length).toBeGreaterThan(0);
      expect(payloads.some((p: any) => typeof p.test === 'string')).toBe(true);
    });

    it('should generate number fuzzing payloads', () => {
      const payloads = (service as any).generateNumberFuzzPayloads();

      expect(payloads).toBeInstanceOf(Array);
      expect(payloads.length).toBeGreaterThan(0);
      expect(payloads.some((p: any) => typeof p.value === 'number')).toBe(true);
    });

    it('should generate injection fuzzing payloads', () => {
      const payloads = (service as any).generateInjectionFuzzPayloads();

      expect(payloads).toBeInstanceOf(Array);
      expect(payloads.length).toBeGreaterThan(0);
      expect(payloads.some((p: any) => p.input && p.input.includes("'"))).toBe(true);
    });

    it('should generate bomb payloads', () => {
      const payloads = (service as any).generateBombPayloads();

      expect(payloads).toBeInstanceOf(Array);
      expect(payloads.length).toBeGreaterThan(0);
      expect(payloads.some((p: any) => p.xml && p.xml.includes('lolz'))).toBe(true);
    });

    it('should generate deeply nested JSON', () => {
      const nested = (service as any).generateDeepNestedJSON(10);

      expect(nested).toBeDefined();
      expect(nested.nested).toBeDefined();
      
      let depth = 0;
      let current = nested;
      while (current.nested) {
        depth++;
        current = current.nested;
      }
      expect(depth).toBe(10);
    });

    it('should generate object with many keys', () => {
      const obj = (service as any).generateManyKeys(100);

      expect(Object.keys(obj).length).toBe(100);
      expect(obj.key0).toBe('value0');
      expect(obj.key99).toBe('value99');
    });
  });

  describe('Detection Methods', () => {
    it('should have detection methods available', () => {
      // Just verify the service has these methods
      expect(service).toBeDefined();
      expect(typeof service.runFuzzing).toBe('function');
    });

    it('should process responses', async () => {
      const result = await service.runFuzzing({
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'string',
        maxRequests: 3,
      });

      expect(result).toBeDefined();
      expect(result.findings).toBeInstanceOf(Array);
    });
  });

  describe('Findings Management', () => {
    it('should add findings with generated IDs', () => {
      const finding = {
        testCase: 'Test case',
        payload: { test: 'data' },
        severity: 'high' as const,
        type: 'error' as const,
        request: 'https://example.com',
        description: 'Test description',
      };

      (service as any).findings = [];
      (service as any).addFinding(finding);

      expect((service as any).findings).toHaveLength(1);
      expect((service as any).findings[0].id).toBeDefined();
      expect((service as any).findings[0].id).toMatch(/^finding-/);
    });

    it('should generate correct summary', () => {
      (service as any).findings = [
        { type: 'crash', severity: 'critical' },
        { type: 'error', severity: 'high' },
        { type: 'timeout', severity: 'medium' },
        { type: 'anomaly', severity: 'low' },
        { type: 'error', severity: 'high' },
      ];

      const summary = (service as any).generateSummary();

      expect(summary.crashes).toBe(1);
      expect(summary.errors).toBe(2);
      expect(summary.timeouts).toBe(1);
      expect(summary.anomalies).toBe(1);
    });
  });

  describe('Utility Methods', () => {
    it('should generate unique test IDs', () => {
      const id1 = (service as any).generateTestId();
      const id2 = (service as any).generateTestId();

      expect(id1).toMatch(/^fuzz-/);
      expect(id2).toMatch(/^fuzz-/);
      expect(id1).not.toBe(id2);
    });

    it('should get correct max requests for intensity', () => {
      expect((service as any).getMaxRequests('low')).toBe(50);
      expect((service as any).getMaxRequests('medium')).toBe(200);
      expect((service as any).getMaxRequests('high')).toBe(500);
    });
  });

  describe('Error Handling', () => {
    it('should handle connection errors', async () => {
      axios.mockRejectedValue({ code: 'ECONNREFUSED' });

      const options: FuzzingOptions = {
        targetUrl: 'http://invalid',
        fuzzingType: 'string',
        maxRequests: 2,
      };

      const result = await service.runFuzzing(options);

      expect(result).toBeDefined();
      expect(result.findings.some(f => f.type === 'crash' || f.type === 'error')).toBe(true);
    });
  });

  describe('Delay Between Requests', () => {
    it('should accept delay parameter', async () => {
      const options: FuzzingOptions = {
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'string',
        maxRequests: 3,
        delayMs: 100,
      };

      const result = await service.runFuzzing(options);

      // Just verify it completes with delay parameter
      expect(result).toBeDefined();
      expect(result.totalTests).toBeGreaterThan(0);
    });
  });

  describe('Singleton Pattern', () => {
    it('should return same instance', () => {
      const { getFuzzingService } = require('../src/main/services/FuzzingService');
      const instance1 = getFuzzingService();
      const instance2 = getFuzzingService();

      expect(instance1).toBe(instance2);
    });
  });
});
