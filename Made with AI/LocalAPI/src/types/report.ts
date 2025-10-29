// Report Type Definitions

export type ReportType = 
  | 'security-scan'
  | 'vulnerability-scan'
  | 'security-trends'
  | 'performance-trends'
  | 'api-usage';

export type ReportFormat = 'pdf' | 'html' | 'json' | 'csv';

/**
 * Report generation options
 */
export interface ReportOptions {
  type: ReportType;
  format: ReportFormat;
  title?: string;
  subtitle?: string;
  author?: string;
  includeCharts?: boolean;
  includeSummary?: boolean;
  includeDetails?: boolean;
  dateRange?: {
    start: Date;
    end: Date;
  };
  filters?: Record<string, any>;
}

/**
 * Security scan report data
 */
export interface SecurityScanReportData {
  scanDate: Date;
  collectionName: string;
  totalRequests: number;
  passedChecks: number;
  failedChecks: number;
  warnings: number;
  securityScore: number;
  findings: SecurityFinding[];
  summary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
}

/**
 * Security finding
 */
export interface SecurityFinding {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  category: string;
  title: string;
  description: string;
  url?: string;
  recommendation: string;
  cwe?: string;
  cvss?: number;
  evidence?: string;
}

/**
 * Vulnerability scan report data
 */
export interface VulnerabilityScanReportData {
  scanDate: Date;
  targetUrl: string;
  scanDuration: number;
  vulnerabilities: Vulnerability[];
  summary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
  riskScore: number;
}

/**
 * Vulnerability
 */
export interface Vulnerability {
  id: string;
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  title: string;
  description: string;
  url: string;
  method: string;
  parameter?: string;
  payload?: string;
  evidence: string;
  recommendation: string;
  references?: string[];
  cwe?: string;
  cvss?: number;
}

/**
 * Security trends report data
 */
export interface SecurityTrendsReportData {
  dateRange: {
    start: Date;
    end: Date;
  };
  totalScans: number;
  averageScore: number;
  trendData: TrendDataPoint[];
  topIssues: {
    category: string;
    count: number;
    trend: 'up' | 'down' | 'stable';
  }[];
  improvements: {
    category: string;
    before: number;
    after: number;
    improvement: number;
  }[];
}

/**
 * Trend data point
 */
export interface TrendDataPoint {
  date: Date;
  score: number;
  scans: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
}

/**
 * Performance trends report data
 */
export interface PerformanceTrendsReportData {
  dateRange: {
    start: Date;
    end: Date;
  };
  totalRequests: number;
  averageResponseTime: number;
  trendData: PerformanceDataPoint[];
  slowestEndpoints: {
    url: string;
    method: string;
    avgTime: number;
    count: number;
  }[];
  errorRates: {
    date: Date;
    rate: number;
  }[];
}

/**
 * Performance data point
 */
export interface PerformanceDataPoint {
  date: Date;
  avgResponseTime: number;
  requests: number;
  errors: number;
  cacheHits: number;
}

/**
 * Report generation result
 */
export interface ReportResult {
  success: boolean;
  filePath?: string;
  data?: Buffer | string;
  error?: string;
  metadata?: {
    format: ReportFormat;
    size: number;
    generatedAt: Date;
  };
}

/**
 * Chart data
 */
export interface ChartData {
  type: 'line' | 'bar' | 'pie' | 'doughnut';
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string;
    borderWidth?: number;
  }[];
  options?: Record<string, any>;
}
