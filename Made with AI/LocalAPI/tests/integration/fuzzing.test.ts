/**
 * Fuzzing Service Integration Tests
 * Tests the full fuzzing workflow with mocked HTTP calls
 */

import { getFuzzingService, FuzzingOptions } from '../../src/main/services/FuzzingService';

// Mock axios to avoid real HTTP calls
jest.mock('axios');
const axios = require('axios');

describe('Fuzzing Integration Tests', () => {
  let service: ReturnType<typeof getFuzzingService>;

  beforeEach(() => {
    service = getFuzzingService();
    jest.clearAllMocks();
    
    // Mock successful HTTP responses
    axios.mockResolvedValue({
      status: 200,
      statusText: 'OK',
      data: { success: true },
      headers: {},
      config: { url: 'https://httpbin.org/post' },
    });
  });

  describe('Full Fuzzing Workflow', () => {
    it('should complete full fuzzing workflow', async () => {
      const result = await service.runFuzzing({
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'all',
        intensity: 'low',
        maxRequests: 20,
      });

      expect(result).toBeDefined();
      expect(result.testId).toMatch(/^fuzz-/);
      expect(result.timestamp).toBeInstanceOf(Date);
      expect(result.duration).toBeGreaterThanOrEqual(0);
      expect(result.findings).toBeInstanceOf(Array);
      expect(result.summary).toBeDefined();
    });

    it('should test all fuzzing types', async () => {
      const types = ['string', 'number', 'format', 'injection', 'boundary', 'encoding'];

      for (const type of types) {
        const result = await service.runFuzzing({
          targetUrl: 'https://httpbin.org/post',
          fuzzingType: type as any,
          maxRequests: 10,
        });

        expect(result.fuzzingType).toBe(type);
        expect(result.findings).toBeInstanceOf(Array);
      }
    });

    it('should handle concurrent fuzzing tests', async () => {
      const options1: FuzzingOptions = {
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'string' as const,
        maxRequests: 5,
      };

      const options2: FuzzingOptions = {
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'number' as const,
        maxRequests: 5,
      };

      const [result1, result2] = await Promise.all([
        service.runFuzzing(options1),
        service.runFuzzing(options2),
      ]);

      // Test IDs should exist (uniqueness depends on implementation)
      expect(result1.testId).toBeDefined();
      expect(result2.testId).toBeDefined();
      expect(result1.fuzzingType).toBe('string');
      expect(result2.fuzzingType).toBe('number');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty base payload', async () => {
      const result = await service.runFuzzing({
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'string',
        maxRequests: 5,
      });

      expect(result).toBeDefined();
      expect(result.findings).toBeInstanceOf(Array);
    });

    it('should handle custom headers', async () => {
      const result = await service.runFuzzing({
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'string',
        headers: {
          'Authorization': 'Bearer token',
          'X-Custom': 'value',
        },
        maxRequests: 5,
      });

      expect(result).toBeDefined();
    });

    it('should handle different HTTP methods', async () => {
      const methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];

      for (const method of methods) {
        const result = await service.runFuzzing({
          targetUrl: 'https://httpbin.org/post',
          method,
          fuzzingType: 'string',
          maxRequests: 3,
        });

        expect(result).toBeDefined();
      }
    });
  });

  describe('Finding Detection', () => {
    it('should detect anomalies in responses', async () => {
      // Mock error response
      axios.mockResolvedValue({
        status: 500,
        statusText: 'Internal Server Error',
        data: 'Error occurred',
        headers: {},
        config: { url: 'https://httpbin.org/status/500' },
      });

      const result = await service.runFuzzing({
        targetUrl: 'https://httpbin.org/status/500',
        fuzzingType: 'string',
        maxRequests: 5,
      });

      expect(result.findings.length).toBeGreaterThan(0);
    });
  });

  describe('Intensity Levels', () => {
    it('should generate different request counts for different intensities', async () => {
      const lowResult = await service.runFuzzing({
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'string',
        intensity: 'low',
      });

      const mediumResult = await service.runFuzzing({
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'string',
        intensity: 'medium',
      });

      const highResult = await service.runFuzzing({
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'string',
        intensity: 'high',
      });

      expect(lowResult.totalTests).toBeLessThanOrEqual(mediumResult.totalTests);
      expect(mediumResult.totalTests).toBeLessThanOrEqual(highResult.totalTests);
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      axios.mockRejectedValue(new Error('Network error'));

      const result = await service.runFuzzing({
        targetUrl: 'https://invalid-url.com',
        fuzzingType: 'string',
        maxRequests: 3,
      });

      expect(result).toBeDefined();
      expect(result.findings.some(f => f.type === 'error' || f.type === 'crash')).toBe(true);
    });

    it('should handle timeout errors', async () => {
      axios.mockRejectedValue({ code: 'ECONNABORTED' });

      const result = await service.runFuzzing({
        targetUrl: 'https://httpbin.org/delay/10',
        fuzzingType: 'string',
        maxRequests: 3,
      });

      expect(result).toBeDefined();
      expect(result.findings.some(f => f.type === 'timeout')).toBe(true);
    });
  });

  describe('Bomb Testing', () => {
    it('should test bomb payloads', async () => {
      const result = await service.runFuzzing({
        targetUrl: 'https://httpbin.org/post',
        fuzzingType: 'bomb',
        maxRequests: 5,
      });

      expect(result).toBeDefined();
      expect(result.fuzzingType).toBe('bomb');
      expect(result.findings).toBeInstanceOf(Array);
    });
  });
});
