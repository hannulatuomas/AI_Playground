# Reporting Guide

**Version:** 0.7.0  
**Last Updated:** October 23, 2025

## Overview

LocalAPI includes a comprehensive PDF reporting system for security analysis, vulnerability assessments, and performance tracking. Reports are generated using PDFKit with Chart.js visualizations.

## Report Types

### 1. Security Scan Report

Comprehensive security analysis of API collections.

**Includes:**
- Security score (0-100)
- Findings categorized by severity (Critical, High, Medium, Low, Info)
- Vulnerability distribution pie chart
- Detailed findings with recommendations
- Pass/fail statistics

**Use Cases:**
- Regular security audits
- Compliance reporting
- Security posture assessment

### 2. Vulnerability Scan Report

Detailed vulnerability assessment with OWASP classifications.

**Includes:**
- Risk score calculation
- Vulnerability summary by severity
- Detailed vulnerability listings with:
  - Type, method, URL, parameter
  - Evidence and payloads
  - CWE/CVSS information
  - Remediation guidance

**Use Cases:**
- Penetration testing reports
- Vulnerability disclosure
- Security remediation tracking

### 3. Security Trends Report

Historical analysis of security posture over time.

**Includes:**
- Security score trend charts
- Top security issues with trend indicators
- Security improvements tracking
- Stacked bar charts for severity trends
- Date range analysis

**Use Cases:**
- Executive summaries
- Progress tracking
- Trend analysis
- Compliance reporting

### 4. Performance Trends Report

Performance metrics analysis over time.

**Includes:**
- Average response time trends
- Slowest endpoints analysis
- Error rate tracking
- Cache hit statistics
- Performance charts

**Use Cases:**
- Performance monitoring
- Capacity planning
- SLA reporting
- Optimization tracking

## Generating Reports

### Using the UI

1. Open Report Manager
2. Select report type
3. Configure options:
   - Title and subtitle
   - Author name
   - Date range (for trends)
   - Include charts/summary/details
4. Click "Generate PDF Report"
5. Report saved to reports directory

### Using the API

```typescript
// Generate security scan report
const reportData = {
  scanDate: new Date(),
  collectionName: 'My API',
  totalRequests: 50,
  passedChecks: 45,
  failedChecks: 5,
  warnings: 2,
  securityScore: 85,
  findings: [...],
  summary: {
    critical: 0,
    high: 2,
    medium: 3,
    low: 5,
    info: 10
  }
};

const result = await window.electronAPI.reports.generate(reportData, {
  type: 'security-scan',
  format: 'pdf',
  title: 'Q4 Security Audit',
  subtitle: 'Production API',
  author: 'Security Team',
  includeCharts: true,
  includeDetails: true
});

if (result.success) {
  console.log(`Report saved to: ${result.filePath}`);
}
```

## Report Options

### Common Options

- **type**: Report type ('security-scan', 'vulnerability-scan', 'security-trends', 'performance-trends')
- **format**: Output format ('pdf')
- **title**: Report title (optional, defaults to report type)
- **subtitle**: Report subtitle (optional)
- **author**: Author name (optional, defaults to 'LocalAPI')
- **includeCharts**: Include visualizations (default: true)
- **includeSummary**: Include executive summary (default: true)
- **includeDetails**: Include detailed findings (default: true)

### Trend Report Options

- **dateRange**: Date range for analysis
  - **start**: Start date
  - **end**: End date

## Chart Types

### Pie Charts
- Vulnerability distribution
- Severity breakdown
- Category distribution

### Line Charts
- Security score trends
- Response time trends
- Error rate trends

### Bar Charts
- Stacked severity trends
- Endpoint performance comparison
- Issue frequency

### Doughnut Charts
- Risk distribution
- Category breakdown

## Report Structure

### Title Page
- Report title
- Subtitle
- Metadata (date, author, generation time)

### Executive Summary
- Key metrics
- Scores and ratings
- High-level statistics

### Visualizations
- Charts and graphs
- Trend analysis
- Distribution charts

### Detailed Sections
- Findings by severity
- Vulnerability details
- Recommendations
- Evidence and payloads

### Footer
- Page numbers
- Generation info
- Branding

## Color Scheme

- **Critical**: Red (#e74c3c)
- **High**: Orange (#e67e22)
- **Medium**: Yellow (#f39c12)
- **Low**: Blue (#3498db)
- **Info**: Gray (#95a5a6)
- **Success**: Green (#27ae60)

## Best Practices

### Report Generation

1. **Regular Schedules**: Generate reports on a regular schedule
2. **Version Control**: Save reports with timestamps
3. **Archiving**: Archive old reports for historical reference
4. **Distribution**: Share reports with stakeholders
5. **Action Items**: Track remediation from reports

### Data Quality

1. **Complete Scans**: Ensure scans are complete before reporting
2. **Accurate Data**: Verify data accuracy
3. **Context**: Include relevant context in titles/subtitles
4. **Trends**: Collect data over time for trend analysis
5. **Baselines**: Establish baselines for comparison

### Customization

1. **Branding**: Customize author and titles
2. **Scope**: Adjust detail level based on audience
3. **Charts**: Include charts for visual impact
4. **Date Ranges**: Choose appropriate time periods
5. **Filters**: Filter data for specific areas

## File Management

### Report Location

Reports are saved to: `{userData}/reports/`

### File Naming

- Security Scan: `security-scan-{timestamp}.pdf`
- Vulnerability Scan: `vulnerability-scan-{timestamp}.pdf`
- Security Trends: `security-trends-{timestamp}.pdf`
- Performance Trends: `performance-trends-{timestamp}.pdf`

### File Size

Typical report sizes:
- Without charts: 50-200 KB
- With charts: 200-500 KB
- Large datasets: 500 KB - 2 MB

## Troubleshooting

### Report Generation Fails

**Problem**: Report generation fails with error
**Solutions**:
- Check data format matches expected structure
- Verify reports directory is writable
- Check for sufficient disk space
- Review error message for specifics

### Charts Not Appearing

**Problem**: Charts missing from report
**Solutions**:
- Ensure `includeCharts: true` in options
- Check chart.js and chartjs-node-canvas are installed
- Verify data has sufficient points for charts
- Check console for chart generation errors

### Large File Sizes

**Problem**: Report files are too large
**Solutions**:
- Reduce number of detailed findings
- Set `includeDetails: false` for summaries only
- Limit date range for trend reports
- Compress images if adding custom content

### Slow Generation

**Problem**: Report generation takes too long
**Solutions**:
- Reduce data volume
- Disable charts if not needed
- Limit detailed findings
- Check system resources

## API Reference

### ReportGenerator

```typescript
class ReportGenerator {
  constructor(reportsDir: string)
  
  async generateReport(
    data: ReportData,
    options: ReportOptions
  ): Promise<ReportResult>
}
```

### ChartGenerator

```typescript
class ChartGenerator {
  async generateLineChart(labels, datasets): Promise<Buffer>
  async generateBarChart(labels, datasets): Promise<Buffer>
  async generatePieChart(labels, data, colors?): Promise<Buffer>
  async generateDoughnutChart(labels, data, colors?): Promise<Buffer>
  async generateSecurityTrendChart(dates, scores): Promise<Buffer>
  async generateVulnerabilityChart(summary): Promise<Buffer>
  async generatePerformanceTrendChart(dates, times): Promise<Buffer>
}
```

## Examples

### Monthly Security Report

```typescript
const data = await getSecurityScanData('monthly');

await window.electronAPI.reports.generate(data, {
  type: 'security-scan',
  format: 'pdf',
  title: 'Monthly Security Report',
  subtitle: `${new Date().toLocaleString('default', { month: 'long' })} ${new Date().getFullYear()}`,
  author: 'Security Team',
  includeCharts: true,
  includeDetails: true
});
```

### Quarterly Trends

```typescript
const startDate = new Date();
startDate.setMonth(startDate.getMonth() - 3);

const data = await getSecurityTrendsData(startDate, new Date());

await window.electronAPI.reports.generate(data, {
  type: 'security-trends',
  format: 'pdf',
  title: 'Q4 Security Trends',
  author: 'Security Team',
  includeCharts: true,
  dateRange: {
    start: startDate,
    end: new Date()
  }
});
```

### Executive Summary

```typescript
await window.electronAPI.reports.generate(data, {
  type: 'security-scan',
  format: 'pdf',
  title: 'Executive Security Summary',
  includeCharts: true,
  includeSummary: true,
  includeDetails: false  // Summary only
});
```

## Future Enhancements

Planned features:
- HTML report format
- CSV data export
- Custom templates
- Report scheduling
- Email distribution
- Multi-language support
- Custom branding
- Interactive charts (HTML)

## Related Documentation

- [Security Guide](SECURITY_GUIDE.md)
- [API Documentation](API.md)
- [User Guide](USER_GUIDE.md)
