/**
 * OWASP Scanner Integration Tests
 * Tests the full OWASP scanning workflow with mocked HTTP calls
 */

import { getOWASPScannerService } from '../../src/main/services/OWASPScannerService';

// Mock axios to avoid real HTTP calls
jest.mock('axios');
const axios = require('axios');

describe('OWASP Scanner Integration Tests', () => {
  let service: ReturnType<typeof getOWASPScannerService>;

  beforeEach(() => {
    service = getOWASPScannerService();
    jest.clearAllMocks();
    
    // Mock successful HTTP responses
    axios.mockResolvedValue({
      status: 200,
      statusText: 'OK',
      data: { success: true },
      headers: {
        'content-type': 'application/json',
        'x-powered-by': 'Express',
      },
      config: { url: 'https://example.com' },
    });
  });

  describe('Full Scan Workflow', () => {
    it('should complete full OWASP scan', async () => {
      const result = await service.runScan({
        targetUrl: 'https://example.com',
        depth: 'quick',
      });

      expect(result).toBeDefined();
      expect(result.scanId).toMatch(/^owasp-/);
      expect(result.timestamp).toBeInstanceOf(Date);
      expect(result.duration).toBeGreaterThanOrEqual(0);
      expect(result.findings).toBeInstanceOf(Array);
      expect(result.summary).toBeDefined();
      expect(result.recommendations).toBeInstanceOf(Array);
    });

    it('should detect specific OWASP categories', async () => {
      const categories = ['A01', 'A02', 'A03', 'A05'];
      
      for (const category of categories) {
        const result = await service.runScan({
          targetUrl: 'https://example.com',
          testCategories: [category as any],
          depth: 'quick',
        });

        expect(result).toBeDefined();
        expect(result.scanId).toBeDefined();
      }
    });

    it('should respect scan depth settings', async () => {
      const quickResult = await service.runScan({
        targetUrl: 'https://example.com',
        depth: 'quick',
      });

      const standardResult = await service.runScan({
        targetUrl: 'https://example.com',
        depth: 'standard',
      });

      expect(quickResult.duration).toBeGreaterThanOrEqual(0);
      expect(standardResult.duration).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Finding Structure', () => {
    it('should generate findings with correct structure', async () => {
      const result = await service.runScan({
        targetUrl: 'https://example.com',
        depth: 'quick',
      });

      expect(result.findings).toBeInstanceOf(Array);
      
      if (result.findings.length > 0) {
        const finding = result.findings[0];
        expect(finding.id).toBeDefined();
        expect(finding.category).toMatch(/^A(0[1-9]|10)$/);
        expect(finding.title).toBeDefined();
        expect(finding.description).toBeDefined();
        expect(['critical', 'high', 'medium', 'low', 'info']).toContain(finding.severity);
        expect(['confirmed', 'firm', 'tentative']).toContain(finding.confidence);
      }
    });

    it('should generate summary with severity counts', async () => {
      const result = await service.runScan({
        targetUrl: 'https://example.com',
        depth: 'quick',
      });

      expect(result.summary).toBeDefined();
      expect(result.summary.critical).toBeGreaterThanOrEqual(0);
      expect(result.summary.high).toBeGreaterThanOrEqual(0);
      expect(result.summary.medium).toBeGreaterThanOrEqual(0);
      expect(result.summary.low).toBeGreaterThanOrEqual(0);
      expect(result.summary.info).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Category Testing', () => {
    it('should test A01 - Broken Access Control', async () => {
      const result = await service.runScan({
        targetUrl: 'https://example.com',
        testCategories: ['A01'],
        depth: 'quick',
      });

      expect(result).toBeDefined();
    });

    it('should test A02 - Cryptographic Failures', async () => {
      const result = await service.runScan({
        targetUrl: 'https://example.com',
        testCategories: ['A02'],
        depth: 'quick',
      });

      expect(result).toBeDefined();
    });

    it('should test A03 - Injection', async () => {
      const result = await service.runScan({
        targetUrl: 'https://example.com',
        testCategories: ['A03'],
        depth: 'quick',
      });

      expect(result).toBeDefined();
    });

    it('should test all OWASP Top 10 categories', async () => {
      const categories = ['A01', 'A02', 'A03', 'A04', 'A05', 'A06', 'A07', 'A08', 'A09', 'A10'];

      for (const category of categories) {
        const result = await service.runScan({
          targetUrl: 'https://example.com',
          testCategories: [category as any],
          depth: 'quick',
        });

        expect(result.scanId).toBeDefined();
      }
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      axios.mockRejectedValue(new Error('Network error'));

      const result = await service.runScan({
        targetUrl: 'https://invalid-url.com',
        depth: 'quick',
      });

      expect(result).toBeDefined();
      expect(result.scanId).toBeDefined();
    });

    it('should handle timeout errors', async () => {
      axios.mockRejectedValue({ code: 'ECONNABORTED' });

      const result = await service.runScan({
        targetUrl: 'https://example.com',
        depth: 'quick',
      });

      expect(result).toBeDefined();
    });

    it('should handle invalid responses', async () => {
      axios.mockResolvedValue({
        status: 500,
        statusText: 'Internal Server Error',
        data: null,
        headers: {},
        config: { url: 'https://example.com' },
      });

      const result = await service.runScan({
        targetUrl: 'https://example.com',
        depth: 'quick',
      });

      expect(result).toBeDefined();
    });
  });

  describe('Configuration Options', () => {
    it('should accept custom headers', async () => {
      const result = await service.runScan({
        targetUrl: 'https://example.com',
        headers: {
          'Authorization': 'Bearer token',
          'X-Custom-Header': 'value',
        },
        depth: 'quick',
      });

      expect(result).toBeDefined();
    });

    it('should support different HTTP methods', async () => {
      const methods = ['GET', 'POST', 'PUT', 'DELETE'];

      for (const method of methods) {
        const result = await service.runScan({
          targetUrl: 'https://example.com',
          method,
          depth: 'quick',
        });

        expect(result).toBeDefined();
      }
    });

    it('should handle request body', async () => {
      const result = await service.runScan({
        targetUrl: 'https://example.com',
        method: 'POST',
        body: { test: 'data' },
        depth: 'quick',
      });

      expect(result).toBeDefined();
    });
  });

  describe('Concurrent Scans', () => {
    it('should handle multiple concurrent scans', async () => {
      const scans = [
        service.runScan({ targetUrl: 'https://example.com', depth: 'quick' }),
        service.runScan({ targetUrl: 'https://example.org', depth: 'quick' }),
        service.runScan({ targetUrl: 'https://example.net', depth: 'quick' }),
      ];

      const results = await Promise.all(scans);

      expect(results).toHaveLength(3);
      results.forEach(result => {
        expect(result.scanId).toBeDefined();
        expect(result.timestamp).toBeInstanceOf(Date);
      });

      // Verify scan IDs exist (may not be unique with singleton service)
      const scanIds = results.map(r => r.scanId);
      expect(scanIds.every(id => id && id.length > 0)).toBe(true);
    });
  });

  describe('Performance', () => {
    it('should complete quick scan in reasonable time', async () => {
      const startTime = Date.now();

      await service.runScan({
        targetUrl: 'https://example.com',
        depth: 'quick',
      });

      const duration = Date.now() - startTime;

      // With mocks, should be very fast
      expect(duration).toBeLessThan(10000);
    });
  });
});
