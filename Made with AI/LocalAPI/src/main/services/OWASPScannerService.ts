/**
 * OWASP Top 10 Security Scanner Service
 * 
 * Implements automated security testing for OWASP Top 10 (2021) vulnerabilities
 */

import axios, { AxiosRequestConfig } from 'axios';
import * as crypto from 'crypto';

export interface OWASPScanOptions {
  targetUrl: string;
  method?: string;
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  followRedirects?: boolean;
  testCategories?: OWASPCategory[];
  depth?: 'quick' | 'standard' | 'thorough';
}

export type OWASPCategory = 
  | 'A01' | 'A02' | 'A03' | 'A04' | 'A05' 
  | 'A06' | 'A07' | 'A08' | 'A09' | 'A10';

export interface OWASPScanResult {
  scanId: string;
  timestamp: Date;
  targetUrl: string;
  duration: number;
  summary: {
    total: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
  findings: OWASPFinding[];
  recommendations: string[];
}

export interface OWASPFinding {
  id: string;
  category: OWASPCategory;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  confidence: 'confirmed' | 'firm' | 'tentative';
  evidence: {
    request?: string;
    response?: string;
    payload?: string;
    location?: string;
  };
  remediation: string;
  references: string[];
  cwe?: string;
  cvss?: number;
}

export class OWASPScannerService {
  private scanId: string = '';
  private findings: OWASPFinding[] = [];
  private startTime: number = 0;

  /**
   * Run comprehensive OWASP Top 10 scan
   */
  async runScan(options: OWASPScanOptions): Promise<OWASPScanResult> {
    this.scanId = this.generateScanId();
    this.findings = [];
    this.startTime = Date.now();

    const categories = options.testCategories || [
      'A01', 'A02', 'A03', 'A04', 'A05',
      'A06', 'A07', 'A08', 'A09', 'A10'
    ];

    // Run tests for each category
    for (const category of categories) {
      await this.runCategoryTests(category, options);
    }

    const duration = Date.now() - this.startTime;

    return {
      scanId: this.scanId,
      timestamp: new Date(),
      targetUrl: options.targetUrl,
      duration,
      summary: this.generateSummary(),
      findings: this.findings,
      recommendations: this.generateRecommendations(),
    };
  }

  /**
   * Run tests for specific OWASP category
   */
  private async runCategoryTests(
    category: OWASPCategory,
    options: OWASPScanOptions
  ): Promise<void> {
    switch (category) {
      case 'A01':
        await this.testBrokenAccessControl(options);
        break;
      case 'A02':
        await this.testCryptographicFailures(options);
        break;
      case 'A03':
        await this.testInjection(options);
        break;
      case 'A04':
        await this.testInsecureDesign(options);
        break;
      case 'A05':
        await this.testSecurityMisconfiguration(options);
        break;
      case 'A06':
        await this.testVulnerableComponents(options);
        break;
      case 'A07':
        await this.testAuthenticationFailures(options);
        break;
      case 'A08':
        await this.testIntegrityFailures(options);
        break;
      case 'A09':
        await this.testLoggingFailures(options);
        break;
      case 'A10':
        await this.testSSRF(options);
        break;
    }
  }

  // Category test methods will be imported from separate modules
  private async testBrokenAccessControl(options: OWASPScanOptions): Promise<void> {
    const { testPathTraversal, testForcedBrowsing, testCORSMisconfiguration } = 
      require('./owasp-tests/AccessControlTests');
    
    await testPathTraversal.call(this, options);
    await testForcedBrowsing.call(this, options);
    await testCORSMisconfiguration.call(this, options);
  }

  private async testCryptographicFailures(options: OWASPScanOptions): Promise<void> {
    const { testInsecureTransport, testWeakSSL, testSensitiveDataInURL } = 
      require('./owasp-tests/CryptographicTests');
    
    await testInsecureTransport.call(this, options);
    await testWeakSSL.call(this, options);
    await testSensitiveDataInURL.call(this, options);
  }

  private async testInjection(options: OWASPScanOptions): Promise<void> {
    const { testSQLInjection, testXSS, testCommandInjection } = 
      require('./owasp-tests/InjectionTests');
    
    await testSQLInjection.call(this, options);
    await testXSS.call(this, options);
    await testCommandInjection.call(this, options);
  }

  private async testInsecureDesign(options: OWASPScanOptions): Promise<void> {
    const { testRateLimiting, testBusinessLogic } = 
      require('./owasp-tests/DesignTests');
    
    await testRateLimiting.call(this, options);
    await testBusinessLogic.call(this, options);
  }

  private async testSecurityMisconfiguration(options: OWASPScanOptions): Promise<void> {
    const { testSecurityHeaders, testDirectoryListing, testVerboseErrors } = 
      require('./owasp-tests/MisconfigurationTests');
    
    await testSecurityHeaders.call(this, options);
    await testDirectoryListing.call(this, options);
    await testVerboseErrors.call(this, options);
  }

  private async testVulnerableComponents(options: OWASPScanOptions): Promise<void> {
    const { testOutdatedLibraries } = require('./owasp-tests/ComponentTests');
    await testOutdatedLibraries.call(this, options);
  }

  private async testAuthenticationFailures(options: OWASPScanOptions): Promise<void> {
    const { testWeakPasswordPolicy, testSessionFixation } = 
      require('./owasp-tests/AuthenticationTests');
    
    await testWeakPasswordPolicy.call(this, options);
    await testSessionFixation.call(this, options);
  }

  private async testIntegrityFailures(options: OWASPScanOptions): Promise<void> {
    const { testInsecureDeserialization, testSubresourceIntegrity } = 
      require('./owasp-tests/IntegrityTests');
    
    await testInsecureDeserialization.call(this, options);
    await testSubresourceIntegrity.call(this, options);
  }

  private async testLoggingFailures(options: OWASPScanOptions): Promise<void> {
    const { testLoggingAndMonitoring } = require('./owasp-tests/LoggingTests');
    await testLoggingAndMonitoring.call(this, options);
  }

  private async testSSRF(options: OWASPScanOptions): Promise<void> {
    const { testSSRFVulnerability } = require('./owasp-tests/SSRFTests');
    await testSSRFVulnerability.call(this, options);
  }

  // Utility methods
  protected async makeRequest(url: string, options: OWASPScanOptions): Promise<any> {
    const config: AxiosRequestConfig = {
      method: options.method || 'GET',
      url,
      headers: options.headers,
      data: options.body,
      timeout: options.timeout || 10000,
      maxRedirects: options.followRedirects ? 5 : 0,
      validateStatus: () => true, // Don't throw on any status
    };

    return await axios(config);
  }

  protected injectPayload(url: string, payload: string): string {
    const urlObj = new URL(url);
    const params = new URLSearchParams(urlObj.search);
    
    // Add payload to first parameter or create test parameter
    if (params.toString()) {
      const firstParam = Array.from(params.keys())[0];
      params.set(firstParam, payload);
    } else {
      params.set('test', payload);
    }
    
    urlObj.search = params.toString();
    return urlObj.toString();
  }

  protected addFinding(finding: Omit<OWASPFinding, 'id'>): void {
    this.findings.push({
      id: this.generateFindingId(),
      ...finding,
    });
  }

  private generateScanId(): string {
    return `owasp-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`;
  }

  private generateFindingId(): string {
    return `finding-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`;
  }

  private generateSummary() {
    const summary = {
      total: this.findings.length,
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
      info: 0,
    };

    for (const finding of this.findings) {
      summary[finding.severity]++;
    }

    return summary;
  }

  private generateRecommendations(): string[] {
    const recommendations: string[] = [];
    const categories = new Set(this.findings.map(f => f.category));

    if (categories.has('A01')) {
      recommendations.push('Implement proper access control checks on all endpoints');
    }
    if (categories.has('A02')) {
      recommendations.push('Use HTTPS for all communications and implement proper encryption');
    }
    if (categories.has('A03')) {
      recommendations.push('Use parameterized queries and input validation to prevent injection attacks');
    }
    if (categories.has('A05')) {
      recommendations.push('Implement all security headers and remove verbose error messages');
    }

    return recommendations;
  }

  // Detection helpers
  protected detectPathTraversal(data: string): boolean {
    return /root:x:|win\.ini|\[boot loader\]/i.test(data);
  }

  protected detectSQLError(data: string): boolean {
    const patterns = [
      /SQL syntax.*MySQL/i,
      /Warning.*mysql_/i,
      /valid MySQL result/i,
      /MySqlClient\./i,
      /PostgreSQL.*ERROR/i,
      /Warning.*pg_/i,
      /valid PostgreSQL result/i,
      /Npgsql\./i,
      /Driver.* SQL[\-\_\ ]*Server/i,
      /OLE DB.* SQL Server/i,
      /SQLServer JDBC Driver/i,
      /SqlClient\./i,
      /Oracle error/i,
      /Oracle.*Driver/i,
      /Warning.*oci_/i,
      /Warning.*ora_/i,
    ];

    return patterns.some(pattern => pattern.test(data));
  }

  protected detectCommandInjection(data: string): boolean {
    return /uid=\d+|gid=\d+|root:|bin\/bash/i.test(data);
  }

  protected detectLDAPError(data: string): boolean {
    return /LDAP|javax\.naming/i.test(data);
  }

  protected isLoginPage(data: string): boolean {
    return /login|sign.?in|password|username/i.test(data);
  }

  protected detectDirectoryListing(data: string): boolean {
    return /Index of|Directory listing|Parent Directory/i.test(data);
  }

  protected detectVerboseError(data: string): boolean {
    return /stack trace|exception|error at line|syntax error/i.test(data);
  }

  protected isVersionOutdated(current: string, minimum: string): boolean {
    const currentParts = current.split('.').map(Number);
    const minimumParts = minimum.split('.').map(Number);

    for (let i = 0; i < Math.max(currentParts.length, minimumParts.length); i++) {
      const curr = currentParts[i] || 0;
      const min = minimumParts[i] || 0;
      
      if (curr < min) return true;
      if (curr > min) return false;
    }

    return false;
  }
}

// Singleton instance
let scannerInstance: OWASPScannerService | null = null;

export function getOWASPScannerService(): OWASPScannerService {
  if (!scannerInstance) {
    scannerInstance = new OWASPScannerService();
  }
  return scannerInstance;
}
