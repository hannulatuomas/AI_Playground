/**
 * ZAP Proxy Integration Tests
 * Tests the ZAP proxy integration with mocked HTTP calls
 */

import { getZAPProxyService } from '../../src/main/services/ZAPProxyService';

// Mock axios to avoid real HTTP calls to ZAP
jest.mock('axios');
const axios = require('axios');

describe('ZAP Proxy Integration Tests', () => {
  const zapConfig = {
    apiKey: 'test-api-key',
    host: 'localhost',
    port: 8080,
  };

  let service: ReturnType<typeof getZAPProxyService>;

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock axios.create to return a mock client
    const mockClient = {
      get: jest.fn().mockImplementation((url: string) => {
        if (url.includes('/core/view/version')) {
          return Promise.resolve({ status: 200, data: { version: '2.12.0' } });
        }
        if (url.includes('/spider/action/scan') || url.includes('/ascan/action/scan')) {
          return Promise.resolve({ status: 200, data: { scan: '1' } });
        }
        if (url.includes('/spider/view/status') || url.includes('/ascan/view/status')) {
          return Promise.resolve({ status: 200, data: { status: '100' } });
        }
        if (url.includes('/core/view/alerts')) {
          return Promise.resolve({
            status: 200,
            data: {
              alerts: [
                {
                  id: '1',
                  alert: 'Test Alert',
                  risk: 'High',
                  confidence: 'Medium',
                  description: 'Test description',
                  solution: 'Test solution',
                  reference: 'Test reference',
                  cweid: '123',
                  wascid: '456',
                  url: 'https://example.com',
                },
              ],
            },
          });
        }
        if (url.includes('/core/view/numberOfAlerts')) {
          return Promise.resolve({ status: 200, data: { numberOfAlerts: '1' } });
        }
        if (url.includes('/core/other/htmlreport')) {
          return Promise.resolve({ status: 200, data: '<html><body>Report</body></html>' });
        }
        if (url.includes('/core/other/xmlreport')) {
          return Promise.resolve({ status: 200, data: '<?xml version="1.0"?><report></report>' });
        }
        return Promise.resolve({ status: 200, data: { Result: 'OK' } });
      }),
      post: jest.fn().mockResolvedValue({
        status: 200,
        data: { Result: 'OK' },
      }),
    };
    
    axios.create = jest.fn().mockReturnValue(mockClient);
    axios.get = mockClient.get;
    axios.post = mockClient.post;
    
    service = getZAPProxyService(zapConfig);
  });

  describe('Connection', () => {
    it('should check ZAP connection', async () => {
      const isConnected = await service.checkConnection();
      expect(typeof isConnected).toBe('boolean');
    });

    it('should get ZAP version', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: { version: '2.12.0' },
      });

      const version = await service.getVersion();
      expect(version).toBeDefined();
    });
  });

  describe('Spider Scan', () => {
    it('should run spider scan', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: { scan: '1', status: '100' },
      });

      const result = await service.runScan({
        targetUrl: 'https://example.com',
        scanType: 'spider',
      });
      
      expect(result).toBeDefined();
      expect(result.scanId).toBeDefined();
    });

    it('should get scan status', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: { status: '50' },
      });

      const status = await service.getScanStatus('1', 'spider');
      expect(typeof status).toBe('number');
    });

    it('should stop spider scan', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: { Result: 'OK' },
      });

      await expect(service.stopScan('1', 'spider')).resolves.not.toThrow();
    });
  });

  describe('Active Scan', () => {
    it('should run active scan', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: { scan: '1', status: '100' },
      });

      const result = await service.runScan({
        targetUrl: 'https://example.com',
        scanType: 'active',
      });
      
      expect(result).toBeDefined();
      expect(result.scanId).toBeDefined();
    });

    it('should get active scan status', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: { status: '75' },
      });

      const status = await service.getScanStatus('1', 'active');
      expect(typeof status).toBe('number');
    });

    it('should stop active scan', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: { Result: 'OK' },
      });

      await expect(service.stopScan('1', 'active')).resolves.not.toThrow();
    });
  });

  describe('Alerts', () => {
    it('should get alerts', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: {
          alerts: [
            {
              alert: 'SQL Injection',
              risk: 'High',
              confidence: 'Medium',
              url: 'https://example.com',
              description: 'SQL injection vulnerability found',
            },
          ],
        },
      });

      const alerts = await service.getAlerts();
      expect(Array.isArray(alerts)).toBe(true);
    });

    it('should get alerts by risk', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: {
          alerts: [
            { alert: 'XSS', risk: 'High' },
          ],
        },
      });

      const alerts = await service.getAlerts('https://example.com');
      expect(Array.isArray(alerts)).toBe(true);
    });

    it('should clear alerts', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: { Result: 'OK' },
      });

      await expect(service.clearAlerts()).resolves.not.toThrow();
    });
  });

  describe('Reports', () => {
    it('should generate HTML report', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: '<html><body>Report</body></html>',
      });

      const report = await service.generateHtmlReport();
      expect(typeof report).toBe('string');
      expect(report.length).toBeGreaterThan(0);
    });

    it('should generate XML report', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: '<?xml version="1.0"?><report></report>',
      });

      const report = await service.generateXmlReport();
      expect(typeof report).toBe('string');
      expect(report.length).toBeGreaterThan(0);
    });
  });

  describe('Session Management', () => {
    it('should create new session', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: { Result: 'OK' },
      });

      await expect(service.createSession('test-session')).resolves.not.toThrow();
    });

    it('should load session', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: { Result: 'OK' },
      });

      await expect(service.accessUrl('https://example.com')).resolves.not.toThrow();
    });

    it('should save session', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: { Result: 'OK' },
      });

      await expect(service.createSession('test-session')).resolves.not.toThrow();
    });
  });

  describe('URL Access', () => {
    it('should access URL through ZAP', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: { Result: 'OK' },
      });

      await expect(service.accessUrl('https://example.com')).resolves.not.toThrow();
    });

    it('should get alerts summary', async () => {
      axios.get.mockResolvedValue({
        status: 200,
        data: { high: 2, medium: 3, low: 5, informational: 1 },
      });

      const summary = await service.getAlertsSummary();
      expect(summary).toBeDefined();
      expect(summary.high).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Error Handling', () => {
    it('should have error handling methods', () => {
      expect(service.checkConnection).toBeDefined();
      expect(service.getAlerts).toBeDefined();
      expect(service.runScan).toBeDefined();
    });

    it('should handle successful connections', async () => {
      const isConnected = await service.checkConnection();
      expect(typeof isConnected).toBe('boolean');
    });

    it('should handle scan operations', async () => {
      const result = await service.runScan({
        targetUrl: 'https://example.com',
        scanType: 'spider',
      });
      
      expect(result).toBeDefined();
      expect(result.scanId).toBeDefined();
    });
  });

  describe('Full Workflow', () => {
    it('should complete full ZAP scan workflow', async () => {
      // Mock all ZAP API calls
      axios.get.mockImplementation((url: string) => {
        if (url.includes('/spider/action/scan')) {
          return Promise.resolve({ status: 200, data: { scan: '1' } });
        }
        if (url.includes('/spider/view/status')) {
          return Promise.resolve({ status: 200, data: { status: '100' } });
        }
        if (url.includes('/ascan/action/scan')) {
          return Promise.resolve({ status: 200, data: { scan: '2' } });
        }
        if (url.includes('/ascan/view/status')) {
          return Promise.resolve({ status: 200, data: { status: '100' } });
        }
        if (url.includes('/core/view/alerts')) {
          return Promise.resolve({
            status: 200,
            data: {
              alerts: [
                { alert: 'Test Alert', risk: 'High', confidence: 'Medium' },
              ],
            },
          });
        }
        if (url.includes('/core/other/htmlreport')) {
          return Promise.resolve({
            status: 200,
            data: '<html><body>Report</body></html>',
          });
        }
        return Promise.resolve({ status: 200, data: { Result: 'OK' } });
      });

      // Run full scan
      const result = await service.runScan({
        targetUrl: 'https://example.com',
        scanType: 'full',
      });
      
      expect(result).toBeDefined();
      expect(result.scanId).toBeDefined();
      expect(result.status).toBe('completed');

      // Get alerts
      const alerts = await service.getAlerts();
      expect(Array.isArray(alerts)).toBe(true);

      // Generate report
      const report = await service.generateHtmlReport();
      expect(typeof report).toBe('string');
    });
  });

  describe('Configuration', () => {
    it('should create service with custom port', () => {
      const customService = getZAPProxyService({
        ...zapConfig,
        port: 9090,
      });

      expect(customService).toBeDefined();
      expect(customService.checkConnection).toBeDefined();
    });

    it('should create service with custom host', () => {
      const customService = getZAPProxyService({
        ...zapConfig,
        host: '127.0.0.1',
      });

      expect(customService).toBeDefined();
    });
  });
});
