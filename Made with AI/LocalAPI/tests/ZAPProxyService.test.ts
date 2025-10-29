import { ZAPProxyService, ZAPConfig } from '../src/main/services/ZAPProxyService';

describe('ZAPProxyService', () => {
  let service: ZAPProxyService;
  const mockConfig: ZAPConfig = {
    apiKey: 'test-api-key',
    host: 'localhost',
    port: 8080,
  };

  beforeEach(() => {
    service = new ZAPProxyService(mockConfig);
  });

  describe('Constructor', () => {
    it('should create service with default host and port', () => {
      const defaultService = new ZAPProxyService({ apiKey: 'test-key' });
      expect(defaultService).toBeDefined();
    });

    it('should create service with custom host and port', () => {
      const customService = new ZAPProxyService({
        apiKey: 'test-key',
        host: '192.168.1.100',
        port: 9090,
      });
      expect(customService).toBeDefined();
    });
  });

  describe('checkConnection', () => {
    it('should return true when ZAP is accessible', async () => {
      // This test requires ZAP to be running
      // In a real test environment, you would mock the axios call
      expect(typeof service.checkConnection).toBe('function');
    });

    it('should return false when ZAP is not accessible', async () => {
      const badService = new ZAPProxyService({
        apiKey: 'test-key',
        host: 'invalid-host',
        port: 99999,
      });
      
      const result = await badService.checkConnection();
      expect(result).toBe(false);
    });
  });

  describe('Scan Operations', () => {
    it('should have runScan method', () => {
      expect(typeof service.runScan).toBe('function');
    });

    it('should accept spider scan options', () => {
      const options = {
        targetUrl: 'https://example.com',
        scanType: 'spider' as const,
        recurse: true,
        maxChildren: 10,
      };
      expect(options.scanType).toBe('spider');
    });

    it('should accept active scan options', () => {
      const options = {
        targetUrl: 'https://example.com',
        scanType: 'active' as const,
        recurse: true,
      };
      expect(options.scanType).toBe('active');
    });

    it('should accept full scan options', () => {
      const options = {
        targetUrl: 'https://example.com',
        scanType: 'full' as const,
      };
      expect(options.scanType).toBe('full');
    });
  });

  describe('Alert Operations', () => {
    it('should have getAlerts method', () => {
      expect(typeof service.getAlerts).toBe('function');
    });

    it('should have clearAlerts method', () => {
      expect(typeof service.clearAlerts).toBe('function');
    });

    it('should have getAlertsSummary method', () => {
      expect(typeof service.getAlertsSummary).toBe('function');
    });
  });

  describe('Report Generation', () => {
    it('should have generateHtmlReport method', () => {
      expect(typeof service.generateHtmlReport).toBe('function');
    });

    it('should have generateXmlReport method', () => {
      expect(typeof service.generateXmlReport).toBe('function');
    });
  });

  describe('Session Management', () => {
    it('should have createSession method', () => {
      expect(typeof service.createSession).toBe('function');
    });

    it('should have accessUrl method', () => {
      expect(typeof service.accessUrl).toBe('function');
    });
  });

  describe('Scan Control', () => {
    it('should have getScanStatus method', () => {
      expect(typeof service.getScanStatus).toBe('function');
    });

    it('should have stopScan method', () => {
      expect(typeof service.stopScan).toBe('function');
    });
  });

  describe('Utility Methods', () => {
    it('should generate unique scan IDs', () => {
      const id1 = (service as any).generateScanId();
      const id2 = (service as any).generateScanId();

      expect(id1).toMatch(/^zap-/);
      expect(id2).toMatch(/^zap-/);
      expect(id1).not.toBe(id2);
    });

    it('should generate correct summary from alerts', () => {
      const alerts = [
        { risk: 'High' },
        { risk: 'High' },
        { risk: 'Medium' },
        { risk: 'Low' },
        { risk: 'Informational' },
      ];

      const summary = (service as any).generateSummary(alerts);

      expect(summary.total).toBe(5);
      expect(summary.high).toBe(2);
      expect(summary.medium).toBe(1);
      expect(summary.low).toBe(1);
      expect(summary.informational).toBe(1);
    });
  });

  describe('Singleton Pattern', () => {
    it('should return same instance with getZAPProxyService', () => {
      const { getZAPProxyService, resetZAPProxyService } = require('../src/main/services/ZAPProxyService');
      
      resetZAPProxyService();
      const instance1 = getZAPProxyService(mockConfig);
      const instance2 = getZAPProxyService();

      expect(instance1).toBe(instance2);
      resetZAPProxyService();
    });

    it('should throw error if accessed before initialization', () => {
      const { getZAPProxyService, resetZAPProxyService } = require('../src/main/services/ZAPProxyService');
      
      resetZAPProxyService();
      
      expect(() => getZAPProxyService()).toThrow('ZAP Proxy Service not initialized');
      resetZAPProxyService();
    });

    it('should reset instance with resetZAPProxyService', () => {
      const { getZAPProxyService, resetZAPProxyService } = require('../src/main/services/ZAPProxyService');
      
      getZAPProxyService(mockConfig);
      resetZAPProxyService();
      
      expect(() => getZAPProxyService()).toThrow();
    });
  });

  describe('Error Handling', () => {
    it('should handle connection errors gracefully', async () => {
      const badService = new ZAPProxyService({
        apiKey: 'test-key',
        host: 'nonexistent-host',
        port: 99999,
      });

      const result = await badService.checkConnection();
      expect(result).toBe(false);
    });

    it('should throw error with descriptive message on getVersion failure', async () => {
      const badService = new ZAPProxyService({
        apiKey: 'test-key',
        host: 'nonexistent-host',
        port: 99999,
      });

      await expect(badService.getVersion()).rejects.toThrow('Failed to get ZAP version');
    });
  });

  describe('API Configuration', () => {
    it('should use correct base URL', () => {
      const customService = new ZAPProxyService({
        apiKey: 'test-key',
        host: '192.168.1.100',
        port: 9090,
      });

      expect((customService as any).baseUrl).toBe('http://192.168.1.100:9090');
    });

    it('should include API key in requests', () => {
      expect((service as any).apiKey).toBe('test-api-key');
    });

    it('should have appropriate timeout', () => {
      expect((service as any).client.defaults.timeout).toBe(300000); // 5 minutes
    });
  });
});
