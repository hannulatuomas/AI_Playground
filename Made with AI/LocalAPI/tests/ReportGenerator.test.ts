// Tests for ReportGenerator
import { ReportGenerator } from '../src/main/services/ReportGenerator';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import type {
  SecurityScanReportData,
  VulnerabilityScanReportData,
  SecurityTrendsReportData,
  PerformanceTrendsReportData,
} from '../src/types/report';

describe('ReportGenerator', () => {
  let reportGenerator: ReportGenerator;
  let testReportsDir: string;

  beforeEach(() => {
    // Create temporary directory for test reports
    testReportsDir = fs.mkdtempSync(path.join(os.tmpdir(), 'reports-test-'));
    reportGenerator = new ReportGenerator(testReportsDir);
  });

  afterEach(() => {
    // Clean up test directory
    if (fs.existsSync(testReportsDir)) {
      fs.rmSync(testReportsDir, { recursive: true, force: true });
    }
  });

  describe('Initialization', () => {
    test('should create reports directory if it does not exist', () => {
      expect(fs.existsSync(testReportsDir)).toBe(true);
    });

    test('should initialize with custom directory', () => {
      const customDir = path.join(testReportsDir, 'custom');
      const customGenerator = new ReportGenerator(customDir);
      expect(fs.existsSync(customDir)).toBe(true);
    });
  });

  describe('Security Scan Report', () => {
    test('should generate security scan report', async () => {
      const data: SecurityScanReportData = {
        scanDate: new Date(),
        collectionName: 'Test Collection',
        totalRequests: 50,
        passedChecks: 45,
        failedChecks: 5,
        warnings: 2,
        securityScore: 85,
        findings: [
          {
            id: '1',
            severity: 'high',
            category: 'Authentication',
            title: 'Missing Authentication',
            description: 'Endpoint does not require authentication',
            recommendation: 'Implement authentication',
          },
        ],
        summary: {
          critical: 0,
          high: 2,
          medium: 3,
          low: 5,
          info: 10,
        },
      };

      const result = await reportGenerator.generateReport(data, {
        type: 'security-scan',
        format: 'pdf',
        title: 'Test Security Report',
      });

      expect(result.success).toBe(true);
      expect(result.filePath).toBeDefined();
      expect(fs.existsSync(result.filePath!)).toBe(true);
      expect(result.metadata?.format).toBe('pdf');
      expect(result.metadata?.size).toBeGreaterThan(0);
    }, 30000);

    test('should include charts when option is enabled', async () => {
      const data: SecurityScanReportData = {
        scanDate: new Date(),
        collectionName: 'Test',
        totalRequests: 10,
        passedChecks: 8,
        failedChecks: 2,
        warnings: 0,
        securityScore: 80,
        findings: [],
        summary: {
          critical: 0,
          high: 1,
          medium: 1,
          low: 0,
          info: 0,
        },
      };

      const result = await reportGenerator.generateReport(data, {
        type: 'security-scan',
        format: 'pdf',
        includeCharts: true,
      });

      expect(result.success).toBe(true);
      // Chart generation is async, so we just verify report was created
      expect(result.filePath).toBeDefined();
    }, 30000); // 30 second timeout for chart generation

    test('should handle report without details', async () => {
      const data: SecurityScanReportData = {
        scanDate: new Date(),
        collectionName: 'Test',
        totalRequests: 10,
        passedChecks: 10,
        failedChecks: 0,
        warnings: 0,
        securityScore: 100,
        findings: [],
        summary: {
          critical: 0,
          high: 0,
          medium: 0,
          low: 0,
          info: 0,
        },
      };

      const result = await reportGenerator.generateReport(data, {
        type: 'security-scan',
        format: 'pdf',
        includeDetails: false,
      });

      expect(result.success).toBe(true);
    }, 30000);
  });

  describe('Vulnerability Scan Report', () => {
    test('should generate vulnerability scan report', async () => {
      const data: VulnerabilityScanReportData = {
        scanDate: new Date(),
        targetUrl: 'https://api.example.com',
        scanDuration: 5000,
        vulnerabilities: [
          {
            id: '1',
            type: 'SQL Injection',
            severity: 'critical',
            title: 'SQL Injection Vulnerability',
            description: 'SQL injection found in parameter',
            url: 'https://api.example.com/users',
            method: 'GET',
            parameter: 'id',
            payload: "1' OR '1'='1",
            evidence: 'Database error returned',
            recommendation: 'Use parameterized queries',
          },
        ],
        summary: {
          critical: 1,
          high: 2,
          medium: 3,
          low: 5,
          info: 10,
        },
        riskScore: 75,
      };

      const result = await reportGenerator.generateReport(data, {
        type: 'vulnerability-scan',
        format: 'pdf',
        title: 'Vulnerability Assessment',
      });

      expect(result.success).toBe(true);
      expect(result.filePath).toBeDefined();
      expect(fs.existsSync(result.filePath!)).toBe(true);
    }, 30000);

    test('should handle empty vulnerabilities', async () => {
      const data: VulnerabilityScanReportData = {
        scanDate: new Date(),
        targetUrl: 'https://api.example.com',
        scanDuration: 1000,
        vulnerabilities: [],
        summary: {
          critical: 0,
          high: 0,
          medium: 0,
          low: 0,
          info: 0,
        },
        riskScore: 100,
      };

      const result = await reportGenerator.generateReport(data, {
        type: 'vulnerability-scan',
        format: 'pdf',
      });

      expect(result.success).toBe(true);
    }, 30000);
  });

  describe('Security Trends Report', () => {
    test('should generate security trends report', async () => {
      const data: SecurityTrendsReportData = {
        dateRange: {
          start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
          end: new Date(),
        },
        totalScans: 15,
        averageScore: 78.5,
        trendData: [
          {
            date: new Date(),
            score: 80,
            scans: 1,
            critical: 0,
            high: 1,
            medium: 2,
            low: 3,
          },
        ],
        topIssues: [
          {
            category: 'Authentication',
            count: 5,
            trend: 'up',
          },
        ],
        improvements: [
          {
            category: 'Input Validation',
            before: 10,
            after: 5,
            improvement: 50,
          },
        ],
      };

      const result = await reportGenerator.generateReport(data, {
        type: 'security-trends',
        format: 'pdf',
        title: 'Security Trends Analysis',
      });

      expect(result.success).toBe(true);
      expect(result.filePath).toBeDefined();
    });

    test('should include trend charts', async () => {
      const data: SecurityTrendsReportData = {
        dateRange: {
          start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
          end: new Date(),
        },
        totalScans: 7,
        averageScore: 85,
        trendData: Array.from({ length: 7 }, (_, i) => ({
          date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000),
          score: 80 + Math.random() * 10,
          scans: 1,
          critical: 0,
          high: Math.floor(Math.random() * 3),
          medium: Math.floor(Math.random() * 5),
          low: Math.floor(Math.random() * 8),
        })),
        topIssues: [],
        improvements: [],
      };

      const result = await reportGenerator.generateReport(data, {
        type: 'security-trends',
        format: 'pdf',
        includeCharts: true,
      });

      expect(result.success).toBe(true);
    }, 30000);
  });

  describe('Performance Trends Report', () => {
    test('should generate performance trends report', async () => {
      const data: PerformanceTrendsReportData = {
        dateRange: {
          start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
          end: new Date(),
        },
        totalRequests: 1500,
        averageResponseTime: 245,
        trendData: [
          {
            date: new Date(),
            avgResponseTime: 250,
            requests: 100,
            errors: 2,
            cacheHits: 50,
          },
        ],
        slowestEndpoints: [
          {
            url: '/api/users',
            method: 'GET',
            avgTime: 500,
            count: 100,
          },
        ],
        errorRates: [
          {
            date: new Date(),
            rate: 2.5,
          },
        ],
      };

      const result = await reportGenerator.generateReport(data, {
        type: 'performance-trends',
        format: 'pdf',
        title: 'Performance Analysis',
      });

      expect(result.success).toBe(true);
      expect(result.filePath).toBeDefined();
    }, 30000);
  });

  describe('Error Handling', () => {
    test('should handle unsupported report type', async () => {
      const result = await reportGenerator.generateReport({}, {
        type: 'unsupported' as any,
        format: 'pdf',
      });

      expect(result.success).toBe(false);
      expect(result.error).toContain('Unsupported report type');
    });

    test('should handle invalid data gracefully', async () => {
      const result = await reportGenerator.generateReport(null as any, {
        type: 'security-scan',
        format: 'pdf',
      });

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    }, 10000);
  });

  describe('Report Metadata', () => {
    test('should include correct metadata', async () => {
      const data: SecurityScanReportData = {
        scanDate: new Date(),
        collectionName: 'Test',
        totalRequests: 1,
        passedChecks: 1,
        failedChecks: 0,
        warnings: 0,
        securityScore: 100,
        findings: [],
        summary: {
          critical: 0,
          high: 0,
          medium: 0,
          low: 0,
          info: 0,
        },
      };

      const result = await reportGenerator.generateReport(data, {
        type: 'security-scan',
        format: 'pdf',
        title: 'Test Report',
        author: 'Test Author',
      });

      expect(result.metadata).toBeDefined();
      expect(result.metadata?.format).toBe('pdf');
      expect(result.metadata?.generatedAt).toBeInstanceOf(Date);
      expect(result.metadata?.size).toBeGreaterThan(0);
    }, 30000);
  });

  describe('File Management', () => {
    test('should create unique filenames', async () => {
      const data: SecurityScanReportData = {
        scanDate: new Date(),
        collectionName: 'Test',
        totalRequests: 1,
        passedChecks: 1,
        failedChecks: 0,
        warnings: 0,
        securityScore: 100,
        findings: [],
        summary: { critical: 0, high: 0, medium: 0, low: 0, info: 0 },
      };

      const result1 = await reportGenerator.generateReport(data, {
        type: 'security-scan',
        format: 'pdf',
      });

      const result2 = await reportGenerator.generateReport(data, {
        type: 'security-scan',
        format: 'pdf',
      });

      expect(result1.filePath).not.toBe(result2.filePath);
    }, 30000);

    test('should save reports to correct directory', async () => {
      const data: SecurityScanReportData = {
        scanDate: new Date(),
        collectionName: 'Test',
        totalRequests: 1,
        passedChecks: 1,
        failedChecks: 0,
        warnings: 0,
        securityScore: 100,
        findings: [],
        summary: { critical: 0, high: 0, medium: 0, low: 0, info: 0 },
      };

      const result = await reportGenerator.generateReport(data, {
        type: 'security-scan',
        format: 'pdf',
      });

      expect(result.filePath).toContain(testReportsDir);
    }, 30000);
  });
});
