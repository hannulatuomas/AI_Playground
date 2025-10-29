// Report Generator Service using PDFKit
import PDFDocument from 'pdfkit';
import * as fs from 'fs';
import * as path from 'path';
import { getChartGenerator } from './ChartGenerator';
import type {
  ReportOptions,
  ReportResult,
  SecurityScanReportData,
  VulnerabilityScanReportData,
  SecurityTrendsReportData,
  PerformanceTrendsReportData,
  SecurityFinding,
  Vulnerability,
} from '../../types/report';

export class ReportGenerator {
  private reportsDir: string;
  private chartGenerator: ReturnType<typeof getChartGenerator>;

  constructor(reportsDir: string) {
    this.reportsDir = reportsDir;
    this.chartGenerator = getChartGenerator();
    
    // Ensure reports directory exists
    if (!fs.existsSync(this.reportsDir)) {
      fs.mkdirSync(this.reportsDir, { recursive: true });
    }
  }

  /**
   * Generate a report
   */
  async generateReport(
    data: any,
    options: ReportOptions
  ): Promise<ReportResult> {
    try {
      switch (options.type) {
        case 'security-scan':
          return await this.generateSecurityScanReport(data, options);
        case 'vulnerability-scan':
          return await this.generateVulnerabilityScanReport(data, options);
        case 'security-trends':
          return await this.generateSecurityTrendsReport(data, options);
        case 'performance-trends':
          return await this.generatePerformanceTrendsReport(data, options);
        default:
          throw new Error(`Unsupported report type: ${options.type}`);
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * Generate security scan report
   */
  private async generateSecurityScanReport(
    data: SecurityScanReportData,
    options: ReportOptions
  ): Promise<ReportResult> {
    // Validate data
    if (!data || !data.collectionName) {
      return {
        success: false,
        error: 'Invalid security scan data: missing required fields',
      };
    }

    const fileName = `security-scan-${Date.now()}.pdf`;
    const filePath = path.join(this.reportsDir, fileName);

    return new Promise(async (resolve, reject) => {
      const doc = new PDFDocument({ size: 'A4', margin: 50 });
      const stream = fs.createWriteStream(filePath);

      doc.pipe(stream);

      // Title Page
      this.addTitle(doc, options.title || 'Security Scan Report');
      this.addSubtitle(doc, options.subtitle || data.collectionName);
      this.addMetadata(doc, {
        'Scan Date': data.scanDate.toLocaleString(),
        'Generated': new Date().toLocaleString(),
        'Author': options.author || 'LocalAPI',
      });

      doc.moveDown(2);

      // Executive Summary
      this.addSectionHeader(doc, 'Executive Summary');
      
      const scoreColor = this.getScoreColor(data.securityScore);
      doc.fontSize(12)
         .fillColor('#333333')
         .text(`Security Score: `, { continued: true })
         .fillColor(scoreColor)
         .text(`${data.securityScore}/100`, { continued: false });

      doc.moveDown(0.5);
      doc.fillColor('#333333')
         .fontSize(10)
         .text(`Total Requests: ${data.totalRequests}`)
         .text(`Passed Checks: ${data.passedChecks}`)
         .text(`Failed Checks: ${data.failedChecks}`)
         .text(`Warnings: ${data.warnings}`);

      doc.moveDown(1);

      // Findings Summary
      this.addSectionHeader(doc, 'Findings Summary');
      this.addFindingsSummaryTable(doc, data.summary);

      // Add vulnerability distribution chart
      if (options.includeCharts !== false) {
        doc.moveDown(1);
        try {
          const chartBuffer = await this.chartGenerator.generateVulnerabilityChart(data.summary);
          doc.image(chartBuffer, {
            fit: [450, 300],
            align: 'center',
          });
        } catch (error) {
          console.error('Failed to generate chart:', error);
        }
      }

      doc.addPage();

      // Detailed Findings
      if (options.includeDetails !== false) {
        this.addSectionHeader(doc, 'Detailed Findings');
        
        const criticalFindings = data.findings.filter(f => f.severity === 'critical');
        const highFindings = data.findings.filter(f => f.severity === 'high');
        const mediumFindings = data.findings.filter(f => f.severity === 'medium');
        const lowFindings = data.findings.filter(f => f.severity === 'low');

        if (criticalFindings.length > 0) {
          this.addFindingsSection(doc, 'Critical', criticalFindings);
        }
        if (highFindings.length > 0) {
          this.addFindingsSection(doc, 'High', highFindings);
        }
        if (mediumFindings.length > 0) {
          this.addFindingsSection(doc, 'Medium', mediumFindings);
        }
        if (lowFindings.length > 0) {
          this.addFindingsSection(doc, 'Low', lowFindings);
        }
      }

      // Footer
      this.addFooter(doc);

      doc.end();

      stream.on('finish', () => {
        const stats = fs.statSync(filePath);
        resolve({
          success: true,
          filePath,
          metadata: {
            format: 'pdf',
            size: stats.size,
            generatedAt: new Date(),
          },
        });
      });

      stream.on('error', reject);
    });
  }

  /**
   * Generate vulnerability scan report
   */
  private async generateVulnerabilityScanReport(
    data: VulnerabilityScanReportData,
    options: ReportOptions
  ): Promise<ReportResult> {
    // Validate data
    if (!data || !data.targetUrl) {
      return {
        success: false,
        error: 'Invalid vulnerability scan data: missing required fields',
      };
    }

    const fileName = `vulnerability-scan-${Date.now()}.pdf`;
    const filePath = path.join(this.reportsDir, fileName);

    return new Promise((resolve, reject) => {
      const doc = new PDFDocument({ size: 'A4', margin: 50 });
      const stream = fs.createWriteStream(filePath);

      doc.pipe(stream);

      // Title Page
      this.addTitle(doc, options.title || 'Vulnerability Scan Report');
      this.addSubtitle(doc, options.subtitle || data.targetUrl);
      this.addMetadata(doc, {
        'Scan Date': data.scanDate.toLocaleString(),
        'Duration': `${data.scanDuration}ms`,
        'Risk Score': `${data.riskScore}/100`,
        'Generated': new Date().toLocaleString(),
      });

      doc.moveDown(2);

      // Summary
      this.addSectionHeader(doc, 'Vulnerability Summary');
      this.addFindingsSummaryTable(doc, data.summary);

      doc.addPage();

      // Vulnerabilities
      if (options.includeDetails !== false && data.vulnerabilities.length > 0) {
        this.addSectionHeader(doc, 'Vulnerabilities');
        
        const grouped = {
          critical: data.vulnerabilities.filter(v => v.severity === 'critical'),
          high: data.vulnerabilities.filter(v => v.severity === 'high'),
          medium: data.vulnerabilities.filter(v => v.severity === 'medium'),
          low: data.vulnerabilities.filter(v => v.severity === 'low'),
        };

        for (const [severity, vulns] of Object.entries(grouped)) {
          if (vulns.length > 0) {
            this.addVulnerabilitiesSection(doc, severity, vulns);
          }
        }
      }

      this.addFooter(doc);
      doc.end();

      stream.on('finish', () => {
        const stats = fs.statSync(filePath);
        resolve({
          success: true,
          filePath,
          metadata: {
            format: 'pdf',
            size: stats.size,
            generatedAt: new Date(),
          },
        });
      });

      stream.on('error', reject);
    });
  }

  /**
   * Generate security trends report
   */
  private async generateSecurityTrendsReport(
    data: SecurityTrendsReportData,
    options: ReportOptions
  ): Promise<ReportResult> {
    // Validate data
    if (!data || !data.dateRange) {
      return {
        success: false,
        error: 'Invalid security trends data: missing required fields',
      };
    }

    const fileName = `security-trends-${Date.now()}.pdf`;
    const filePath = path.join(this.reportsDir, fileName);

    return new Promise((resolve, reject) => {
      const doc = new PDFDocument({ size: 'A4', margin: 50 });
      const stream = fs.createWriteStream(filePath);

      doc.pipe(stream);

      // Title Page
      this.addTitle(doc, options.title || 'Security Trends Report');
      const dateRange = `${data.dateRange.start.toLocaleDateString()} - ${data.dateRange.end.toLocaleDateString()}`;
      this.addSubtitle(doc, dateRange);
      this.addMetadata(doc, {
        'Total Scans': data.totalScans.toString(),
        'Average Score': `${data.averageScore.toFixed(1)}/100`,
        'Generated': new Date().toLocaleString(),
      });

      doc.moveDown(2);

      // Overview
      this.addSectionHeader(doc, 'Overview');
      doc.fontSize(10)
         .fillColor('#333333')
         .text(`This report analyzes security trends over ${data.totalScans} scans.`);
      
      doc.moveDown(1);

      // Top Issues
      if (data.topIssues.length > 0) {
        this.addSectionHeader(doc, 'Top Security Issues');
        this.addTopIssuesTable(doc, data.topIssues);
      }

      doc.addPage();

      // Improvements
      if (data.improvements.length > 0) {
        this.addSectionHeader(doc, 'Security Improvements');
        this.addImprovementsTable(doc, data.improvements);
      }

      // Trend Chart with actual visualization
      if (options.includeCharts !== false && data.trendData.length > 0) {
        doc.moveDown(2);
        this.addSectionHeader(doc, 'Score Trend');
        
        // Generate and embed actual chart
        (async () => {
          try {
            const dates = data.trendData.map(d => d.date.toLocaleDateString());
            const scores = data.trendData.map(d => d.score);
            const chartBuffer = await this.chartGenerator.generateSecurityTrendChart(dates, scores);
            doc.image(chartBuffer, {
              fit: [500, 300],
              align: 'center',
            });
          } catch (error) {
            console.error('Failed to generate trend chart:', error);
            // Fallback to text representation
            this.addTrendData(doc, data.trendData);
          }
        })();
      }

      this.addFooter(doc);
      doc.end();

      stream.on('finish', () => {
        const stats = fs.statSync(filePath);
        resolve({
          success: true,
          filePath,
          metadata: {
            format: 'pdf',
            size: stats.size,
            generatedAt: new Date(),
          },
        });
      });

      stream.on('error', reject);
    });
  }

  /**
   * Generate performance trends report
   */
  private async generatePerformanceTrendsReport(
    data: PerformanceTrendsReportData,
    options: ReportOptions
  ): Promise<ReportResult> {
    // Validate data
    if (!data || !data.dateRange) {
      return {
        success: false,
        error: 'Invalid performance trends data: missing required fields',
      };
    }

    const fileName = `performance-trends-${Date.now()}.pdf`;
    const filePath = path.join(this.reportsDir, fileName);

    return new Promise((resolve, reject) => {
      const doc = new PDFDocument({ size: 'A4', margin: 50 });
      const stream = fs.createWriteStream(filePath);

      doc.pipe(stream);

      // Title Page
      this.addTitle(doc, options.title || 'Performance Trends Report');
      const dateRange = `${data.dateRange.start.toLocaleDateString()} - ${data.dateRange.end.toLocaleDateString()}`;
      this.addSubtitle(doc, dateRange);
      this.addMetadata(doc, {
        'Total Requests': data.totalRequests.toString(),
        'Avg Response Time': `${data.averageResponseTime.toFixed(0)}ms`,
        'Generated': new Date().toLocaleString(),
      });

      doc.moveDown(2);

      // Slowest Endpoints
      if (data.slowestEndpoints.length > 0) {
        this.addSectionHeader(doc, 'Slowest Endpoints');
        this.addSlowestEndpointsTable(doc, data.slowestEndpoints);
      }

      this.addFooter(doc);
      doc.end();

      stream.on('finish', () => {
        const stats = fs.statSync(filePath);
        resolve({
          success: true,
          filePath,
          metadata: {
            format: 'pdf',
            size: stats.size,
            generatedAt: new Date(),
          },
        });
      });

      stream.on('error', reject);
    });
  }

  // Helper methods for PDF formatting

  private addTitle(doc: PDFKit.PDFDocument, title: string): void {
    doc.fontSize(24)
       .fillColor('#2c3e50')
       .text(title, { align: 'center' });
    doc.moveDown(0.5);
  }

  private addSubtitle(doc: PDFKit.PDFDocument, subtitle: string): void {
    doc.fontSize(14)
       .fillColor('#7f8c8d')
       .text(subtitle, { align: 'center' });
    doc.moveDown(1);
  }

  private addMetadata(doc: PDFKit.PDFDocument, metadata: Record<string, string>): void {
    doc.fontSize(10).fillColor('#95a5a6');
    for (const [key, value] of Object.entries(metadata)) {
      doc.text(`${key}: ${value}`, { align: 'center' });
    }
  }

  private addSectionHeader(doc: PDFKit.PDFDocument, title: string): void {
    doc.fontSize(16)
       .fillColor('#34495e')
       .text(title);
    doc.moveDown(0.5);
    doc.moveTo(50, doc.y)
       .lineTo(550, doc.y)
       .stroke('#bdc3c7');
    doc.moveDown(0.5);
  }

  private addFindingsSummaryTable(
    doc: PDFKit.PDFDocument,
    summary: { critical: number; high: number; medium: number; low: number; info: number }
  ): void {
    const tableData = [
      { severity: 'Critical', count: summary.critical, color: '#e74c3c' },
      { severity: 'High', count: summary.high, color: '#e67e22' },
      { severity: 'Medium', count: summary.medium, color: '#f39c12' },
      { severity: 'Low', count: summary.low, color: '#3498db' },
      { severity: 'Info', count: summary.info, color: '#95a5a6' },
    ];

    tableData.forEach(row => {
      doc.fontSize(10)
         .fillColor(row.color)
         .text(`${row.severity}: `, { continued: true })
         .fillColor('#333333')
         .text(row.count.toString());
    });
    
    doc.moveDown(1);
  }

  private addFindingsSection(
    doc: PDFKit.PDFDocument,
    severity: string,
    findings: SecurityFinding[]
  ): void {
    doc.fontSize(14)
       .fillColor('#34495e')
       .text(`${severity} Severity Findings`);
    doc.moveDown(0.5);

    findings.forEach((finding, index) => {
      if (index > 0) doc.moveDown(1);
      
      doc.fontSize(12)
         .fillColor('#2c3e50')
         .text(finding.title);
      
      doc.fontSize(9)
         .fillColor('#7f8c8d')
         .text(`Category: ${finding.category}`);
      
      if (finding.url) {
        doc.text(`URL: ${finding.url}`);
      }
      
      doc.moveDown(0.3);
      doc.fontSize(10)
         .fillColor('#333333')
         .text(finding.description, { width: 500 });
      
      doc.moveDown(0.3);
      doc.fontSize(10)
         .fillColor('#27ae60')
         .text('Recommendation:', { continued: true })
         .fillColor('#333333')
         .text(` ${finding.recommendation}`, { width: 500 });
      
      // Check if we need a new page
      if (doc.y > 700) {
        doc.addPage();
      }
    });
    
    doc.moveDown(1);
  }

  private addVulnerabilitiesSection(
    doc: PDFKit.PDFDocument,
    severity: string,
    vulnerabilities: Vulnerability[]
  ): void {
    doc.fontSize(14)
       .fillColor('#34495e')
       .text(`${severity.charAt(0).toUpperCase() + severity.slice(1)} Severity`);
    doc.moveDown(0.5);

    vulnerabilities.forEach((vuln, index) => {
      if (index > 0) doc.moveDown(1);
      
      doc.fontSize(12)
         .fillColor('#2c3e50')
         .text(vuln.title);
      
      doc.fontSize(9)
         .fillColor('#7f8c8d')
         .text(`Type: ${vuln.type} | Method: ${vuln.method}`);
      
      doc.text(`URL: ${vuln.url}`);
      
      if (vuln.parameter) {
        doc.text(`Parameter: ${vuln.parameter}`);
      }
      
      doc.moveDown(0.3);
      doc.fontSize(10)
         .fillColor('#333333')
         .text(vuln.description, { width: 500 });
      
      if (vuln.evidence) {
        doc.moveDown(0.3);
        doc.fontSize(9)
           .fillColor('#7f8c8d')
           .text('Evidence:', { continued: true })
           .fillColor('#333333')
           .text(` ${vuln.evidence.substring(0, 200)}...`, { width: 500 });
      }
      
      doc.moveDown(0.3);
      doc.fontSize(10)
         .fillColor('#27ae60')
         .text('Recommendation:', { continued: true })
         .fillColor('#333333')
         .text(` ${vuln.recommendation}`, { width: 500 });
      
      if (doc.y > 700) {
        doc.addPage();
      }
    });
    
    doc.moveDown(1);
  }

  private addTopIssuesTable(
    doc: PDFKit.PDFDocument,
    issues: { category: string; count: number; trend: string }[]
  ): void {
    issues.forEach(issue => {
      const trendIcon = issue.trend === 'up' ? '↑' : issue.trend === 'down' ? '↓' : '→';
      const trendColor = issue.trend === 'up' ? '#e74c3c' : issue.trend === 'down' ? '#27ae60' : '#95a5a6';
      
      doc.fontSize(10)
         .fillColor('#333333')
         .text(`${issue.category}: ${issue.count} `, { continued: true })
         .fillColor(trendColor)
         .text(trendIcon);
    });
    
    doc.moveDown(1);
  }

  private addImprovementsTable(
    doc: PDFKit.PDFDocument,
    improvements: { category: string; before: number; after: number; improvement: number }[]
  ): void {
    improvements.forEach(imp => {
      doc.fontSize(10)
         .fillColor('#333333')
         .text(`${imp.category}: `, { continued: true })
         .fillColor('#27ae60')
         .text(`${imp.improvement.toFixed(1)}% improvement `, { continued: true })
         .fillColor('#7f8c8d')
         .text(`(${imp.before} → ${imp.after})`);
    });
    
    doc.moveDown(1);
  }

  private addTrendData(
    doc: PDFKit.PDFDocument,
    trendData: { date: Date; score: number }[]
  ): void {
    doc.fontSize(9).fillColor('#7f8c8d');
    trendData.slice(0, 10).forEach(point => {
      doc.text(`${point.date.toLocaleDateString()}: ${point.score.toFixed(1)}/100`);
    });
    
    doc.moveDown(1);
  }

  private addSlowestEndpointsTable(
    doc: PDFKit.PDFDocument,
    endpoints: { url: string; method: string; avgTime: number; count: number }[]
  ): void {
    endpoints.slice(0, 10).forEach(endpoint => {
      doc.fontSize(10)
         .fillColor('#333333')
         .text(`${endpoint.method} ${endpoint.url}`, { continued: true })
         .fillColor('#e67e22')
         .text(` - ${endpoint.avgTime.toFixed(0)}ms `, { continued: true })
         .fillColor('#7f8c8d')
         .text(`(${endpoint.count} requests)`);
    });
    
    doc.moveDown(1);
  }

  private addFooter(doc: PDFKit.PDFDocument): void {
    const range = doc.bufferedPageRange();
    const pageCount = range.count;
    
    // PDFKit pages are 0-indexed internally but bufferedPageRange gives 1-indexed start
    for (let i = 0; i < pageCount; i++) {
      try {
        doc.switchToPage(i);
        doc.fontSize(8)
           .fillColor('#95a5a6')
           .text(
             `Generated by LocalAPI - Page ${i + 1} of ${pageCount}`,
             50,
             doc.page.height - 50,
             { align: 'center' }
           );
      } catch (error) {
        // Skip if page doesn't exist
        console.warn(`Could not add footer to page ${i}:`, error);
      }
    }
  }

  private getScoreColor(score: number): string {
    if (score >= 80) return '#27ae60';
    if (score >= 60) return '#f39c12';
    if (score >= 40) return '#e67e22';
    return '#e74c3c';
  }
}

// Singleton instance
let reportGeneratorInstance: ReportGenerator | null = null;

export function getReportGenerator(reportsDir?: string): ReportGenerator {
  if (!reportGeneratorInstance && reportsDir) {
    reportGeneratorInstance = new ReportGenerator(reportsDir);
  }
  if (!reportGeneratorInstance) {
    throw new Error('ReportGenerator not initialized');
  }
  return reportGeneratorInstance;
}

export function initializeReportGenerator(reportsDir: string): ReportGenerator {
  reportGeneratorInstance = new ReportGenerator(reportsDir);
  return reportGeneratorInstance;
}
