// Integration tests for the complete reporting system
import { ReportGenerator } from '../../src/main/services/ReportGenerator';
import { ChartGenerator } from '../../src/main/services/ChartGenerator';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import type {
  SecurityScanReportData,
  VulnerabilityScanReportData,
  SecurityTrendsReportData,
} from '../../src/types/report';

describe('Reporting System Integration', () => {
  let reportGenerator: ReportGenerator;
  let chartGenerator: ChartGenerator;
  let testReportsDir: string;

  beforeEach(() => {
    testReportsDir = fs.mkdtempSync(path.join(os.tmpdir(), 'reports-integration-'));
    reportGenerator = new ReportGenerator(testReportsDir);
    chartGenerator = new ChartGenerator();
  });

  afterEach(() => {
    if (fs.existsSync(testReportsDir)) {
      fs.rmSync(testReportsDir, { recursive: true, force: true });
    }
  });

  describe('End-to-End Report Generation', () => {
    test('should generate complete security scan report with charts', async () => {
      const data: SecurityScanReportData = {
        scanDate: new Date(),
        collectionName: 'Production API',
        totalRequests: 100,
        passedChecks: 85,
        failedChecks: 15,
        warnings: 5,
        securityScore: 82,
        findings: [
          {
            id: '1',
            severity: 'high',
            category: 'Authentication',
            title: 'Missing Authentication Header',
            description: 'Endpoint does not require authentication',
            recommendation: 'Implement JWT authentication',
          },
          {
            id: '2',
            severity: 'medium',
            category: 'Input Validation',
            title: 'Insufficient Input Validation',
            description: 'User input not properly sanitized',
            recommendation: 'Add input validation middleware',
          },
        ],
        summary: {
          critical: 0,
          high: 5,
          medium: 10,
          low: 15,
          info: 20,
        },
      };

      const result = await reportGenerator.generateReport(data, {
        type: 'security-scan',
        format: 'pdf',
        title: 'Integration Test Security Report',
        includeCharts: true,
        includeDetails: true,
      });

      expect(result.success).toBe(true);
      expect(result.filePath).toBeDefined();
      expect(fs.existsSync(result.filePath!)).toBe(true);
      expect(result.metadata?.size).toBeGreaterThan(10000); // Should be substantial with charts
    }, 30000);

    test('should generate vulnerability scan report with evidence', async () => {
      const data: VulnerabilityScanReportData = {
        scanDate: new Date(),
        targetUrl: 'https://api.example.com',
        scanDuration: 15000,
        vulnerabilities: [
          {
            id: 'vuln-1',
            type: 'SQL Injection',
            severity: 'critical',
            title: 'SQL Injection in User Endpoint',
            description: 'Unparameterized SQL query allows injection',
            url: 'https://api.example.com/users',
            method: 'GET',
            parameter: 'id',
            payload: "1' OR '1'='1",
            evidence: 'Database error: syntax error near OR',
            recommendation: 'Use parameterized queries or ORM',
            cwe: 'CWE-89',
            cvss: 9.8,
          },
        ],
        summary: {
          critical: 1,
          high: 3,
          medium: 5,
          low: 8,
          info: 10,
        },
        riskScore: 68,
      };

      const result = await reportGenerator.generateReport(data, {
        type: 'vulnerability-scan',
        format: 'pdf',
        title: 'Vulnerability Assessment Report',
        includeCharts: true,
      });

      expect(result.success).toBe(true);
      expect(result.filePath).toBeDefined();
      expect(fs.existsSync(result.filePath!)).toBe(true);
    }, 30000);

    test('should generate security trends report with historical data', async () => {
      const data: SecurityTrendsReportData = {
        dateRange: {
          start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
          end: new Date(),
        },
        totalScans: 30,
        averageScore: 78.5,
        trendData: Array.from({ length: 30 }, (_, i) => ({
          date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000),
          score: 70 + Math.random() * 20,
          scans: 1,
          critical: Math.floor(Math.random() * 2),
          high: Math.floor(Math.random() * 5),
          medium: Math.floor(Math.random() * 10),
          low: Math.floor(Math.random() * 15),
        })),
        topIssues: [
          {
            category: 'Authentication',
            count: 15,
            trend: 'down',
          },
          {
            category: 'Input Validation',
            count: 12,
            trend: 'up',
          },
        ],
        improvements: [
          {
            category: 'HTTPS Usage',
            before: 80,
            after: 95,
            improvement: 18.75,
          },
        ],
      };

      const result = await reportGenerator.generateReport(data, {
        type: 'security-trends',
        format: 'pdf',
        title: 'Monthly Security Trends',
        includeCharts: true,
      });

      expect(result.success).toBe(true);
      expect(result.filePath).toBeDefined();
      expect(fs.existsSync(result.filePath!)).toBe(true);
    }, 30000);
  });

  describe('Chart Integration', () => {
    test('should generate and embed vulnerability chart', async () => {
      const summary = {
        critical: 2,
        high: 5,
        medium: 8,
        low: 12,
        info: 20,
      };

      const chartBuffer = await chartGenerator.generateVulnerabilityChart(summary);

      expect(chartBuffer).toBeInstanceOf(Buffer);
      expect(chartBuffer.length).toBeGreaterThan(1000); // Chart should be substantial
    }, 30000);

    test('should generate security trend chart', async () => {
      const dates = Array.from({ length: 7 }, (_, i) => 
        new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toLocaleDateString()
      );
      const scores = [75, 78, 80, 82, 85, 87, 90];

      const chartBuffer = await chartGenerator.generateSecurityTrendChart(dates, scores);

      expect(chartBuffer).toBeInstanceOf(Buffer);
      expect(chartBuffer.length).toBeGreaterThan(1000);
    }, 30000);
  });

  describe('Report Metadata', () => {
    test('should include correct metadata in all reports', async () => {
      const data: SecurityScanReportData = {
        scanDate: new Date(),
        collectionName: 'Test',
        totalRequests: 10,
        passedChecks: 10,
        failedChecks: 0,
        warnings: 0,
        securityScore: 100,
        findings: [],
        summary: { critical: 0, high: 0, medium: 0, low: 0, info: 0 },
      };

      const result = await reportGenerator.generateReport(data, {
        type: 'security-scan',
        format: 'pdf',
        title: 'Metadata Test',
        author: 'Test Suite',
      });

      expect(result.metadata).toBeDefined();
      expect(result.metadata?.format).toBe('pdf');
      expect(result.metadata?.generatedAt).toBeInstanceOf(Date);
      expect(result.metadata?.size).toBeGreaterThan(0);
    }, 30000);
  });

  describe('Error Handling', () => {
    test('should handle invalid data gracefully', async () => {
      const result = await reportGenerator.generateReport(null as any, {
        type: 'security-scan',
        format: 'pdf',
      });

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });

    test('should handle unsupported report type', async () => {
      const result = await reportGenerator.generateReport({}, {
        type: 'invalid-type' as any,
        format: 'pdf',
      });

      expect(result.success).toBe(false);
      expect(result.error).toContain('Unsupported report type');
    });
  });

  describe('Performance', () => {
    test('should generate report in reasonable time', async () => {
      const data: SecurityScanReportData = {
        scanDate: new Date(),
        collectionName: 'Performance Test',
        totalRequests: 50,
        passedChecks: 45,
        failedChecks: 5,
        warnings: 2,
        securityScore: 85,
        findings: Array.from({ length: 20 }, (_, i) => ({
          id: `finding-${i}`,
          severity: ['critical', 'high', 'medium', 'low'][i % 4] as any,
          category: 'Test Category',
          title: `Test Finding ${i}`,
          description: 'Test description',
          recommendation: 'Test recommendation',
        })),
        summary: { critical: 5, high: 5, medium: 5, low: 5, info: 0 },
      };

      const startTime = Date.now();
      const result = await reportGenerator.generateReport(data, {
        type: 'security-scan',
        format: 'pdf',
        includeCharts: true,
        includeDetails: true,
      });
      const duration = Date.now() - startTime;

      expect(result.success).toBe(true);
      expect(duration).toBeLessThan(30000); // Should complete within 30 seconds
    }, 40000); // 40 seconds to allow for the 30 second test duration
  });
});
