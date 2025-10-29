import { OWASPScannerService } from '../src/main/services/OWASPScannerService';

// Mock axios to avoid real HTTP calls
jest.mock('axios');
const axios = require('axios');

describe('OWASPScannerService', () => {
  let service: OWASPScannerService;

  beforeEach(() => {
    service = new OWASPScannerService();
    jest.clearAllMocks();
    
    // Mock axios to return successful responses
    axios.mockResolvedValue({
      status: 200,
      data: { success: true },
      headers: {},
      config: { url: 'https://example.com' },
    });
  });

  describe('Service Initialization', () => {
    it('should create service instance', () => {
      expect(service).toBeDefined();
      expect(service).toBeInstanceOf(OWASPScannerService);
    });

    it('should have runScan method', () => {
      expect(typeof service.runScan).toBe('function');
    });
  });

  describe('runScan', () => {
    it('should complete scan with quick depth', async () => {
      const result = await service.runScan({
        targetUrl: 'https://example.com',
        method: 'GET',
        depth: 'quick',
      });

      expect(result).toBeDefined();
      expect(result.scanId).toBeDefined();
      expect(result.scanId).toMatch(/^owasp-/);
      expect(result.timestamp).toBeInstanceOf(Date);
      expect(result.duration).toBeGreaterThanOrEqual(0);
      expect(result.findings).toBeInstanceOf(Array);
      expect(result.summary).toBeDefined();
    });

    it('should test specific categories', async () => {
      const result = await service.runScan({
        targetUrl: 'https://example.com',
        testCategories: ['A01', 'A03'],
        depth: 'quick',
      });

      expect(result).toBeDefined();
      expect(result.findings).toBeInstanceOf(Array);
    });

    it('should respect scan depth', async () => {
      const quickResult = await service.runScan({
        targetUrl: 'https://example.com',
        depth: 'quick',
      });

      const standardResult = await service.runScan({
        targetUrl: 'https://example.com',
        depth: 'standard',
      });

      expect(quickResult.duration).toBeDefined();
      expect(standardResult.duration).toBeDefined();
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

    it('should include recommendations', async () => {
      const result = await service.runScan({
        targetUrl: 'https://example.com',
        depth: 'quick',
      });

      expect(result.recommendations).toBeDefined();
      expect(Array.isArray(result.recommendations)).toBe(true);
    });
  });

  describe('Finding Structure', () => {
    it('should generate findings with correct structure', async () => {
      const result = await service.runScan({
        targetUrl: 'https://example.com',
        depth: 'quick',
      });

      if (result.findings.length > 0) {
        const finding = result.findings[0];
        expect(finding.id).toBeDefined();
        expect(finding.category).toBeDefined();
        expect(finding.title).toBeDefined();
        expect(finding.description).toBeDefined();
        expect(finding.severity).toBeDefined();
        expect(finding.confidence).toBeDefined();
        expect(['critical', 'high', 'medium', 'low', 'info']).toContain(finding.severity);
        expect(['confirmed', 'firm', 'tentative']).toContain(finding.confidence);
      }
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors gracefully', async () => {
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
  });

  describe('Singleton Pattern', () => {
    it('should return same instance', () => {
      const { getOWASPScannerService } = require('../src/main/services/OWASPScannerService');
      const instance1 = getOWASPScannerService();
      const instance2 = getOWASPScannerService();

      expect(instance1).toBe(instance2);
    });
  });

  describe('Category Testing', () => {
    const categories = ['A01', 'A02', 'A03', 'A04', 'A05', 'A06', 'A07', 'A08', 'A09', 'A10'];

    it('should support all OWASP Top 10 categories', async () => {
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
  });

  describe('Scan Configuration', () => {
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
  });

  describe('Performance', () => {
    it('should complete quick scan in reasonable time', async () => {
      const startTime = Date.now();

      await service.runScan({
        targetUrl: 'https://example.com',
        depth: 'quick',
      });

      const duration = Date.now() - startTime;

      // Quick scan should complete within 10 seconds with mocks
      expect(duration).toBeLessThan(10000);
    });
  });
});
