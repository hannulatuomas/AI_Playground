// Security Assertion Service
// Performs security checks on HTTP responses

export interface SecurityCheck {
  id: string;
  name: string;
  category: 'headers' | 'leaks' | 'cookies' | 'ssl';
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  passed: boolean;
  message: string;
  recommendation?: string;
  details?: any;
}

export interface SecurityReport {
  url: string;
  timestamp: Date;
  checks: SecurityCheck[];
  score: number;
  criticalCount: number;
  highCount: number;
  mediumCount: number;
  lowCount: number;
  passedCount: number;
  failedCount: number;
}

export class SecurityAssertionService {
  /**
   * Run all security checks on response
   */
  runSecurityChecks(response: {
    url: string;
    status: number;
    headers: Record<string, string>;
    body: string;
    ssl?: any;
  }): SecurityReport {
    const checks: SecurityCheck[] = [];

    // Header security checks
    checks.push(...this.checkSecurityHeaders(response.headers));

    // Information leak checks
    checks.push(...this.checkInformationLeaks(response.headers, response.body));

    // Cookie security checks
    checks.push(...this.checkCookieSecurity(response.headers));

    // SSL/TLS checks
    if (response.ssl) {
      checks.push(...this.checkSSLSecurity(response.ssl));
    }

    // Calculate statistics
    const stats = this.calculateStatistics(checks);

    return {
      url: response.url,
      timestamp: new Date(),
      checks,
      ...stats,
    };
  }

  /**
   * Check security headers
   */
  private checkSecurityHeaders(headers: Record<string, string>): SecurityCheck[] {
    const checks: SecurityCheck[] = [];
    const lowerHeaders = this.toLowerCaseKeys(headers);

    // Strict-Transport-Security
    checks.push(
      this.checkHeader(
        'strict-transport-security',
        lowerHeaders,
        'critical',
        'HSTS (HTTP Strict Transport Security)',
        'Enforces HTTPS connections',
        'Add: Strict-Transport-Security: max-age=31536000; includeSubDomains'
      )
    );

    // X-Frame-Options
    checks.push(
      this.checkHeader(
        'x-frame-options',
        lowerHeaders,
        'high',
        'X-Frame-Options',
        'Prevents clickjacking attacks',
        'Add: X-Frame-Options: DENY or SAMEORIGIN'
      )
    );

    // X-Content-Type-Options
    checks.push(
      this.checkHeader(
        'x-content-type-options',
        lowerHeaders,
        'medium',
        'X-Content-Type-Options',
        'Prevents MIME-type sniffing',
        'Add: X-Content-Type-Options: nosniff'
      )
    );

    // Content-Security-Policy
    checks.push(
      this.checkHeader(
        'content-security-policy',
        lowerHeaders,
        'high',
        'Content-Security-Policy',
        'Prevents XSS and injection attacks',
        "Add: Content-Security-Policy: default-src 'self'"
      )
    );

    // X-XSS-Protection
    checks.push(
      this.checkHeader(
        'x-xss-protection',
        lowerHeaders,
        'medium',
        'X-XSS-Protection',
        'Enables browser XSS filtering',
        'Add: X-XSS-Protection: 1; mode=block'
      )
    );

    // Referrer-Policy
    checks.push(
      this.checkHeader(
        'referrer-policy',
        lowerHeaders,
        'low',
        'Referrer-Policy',
        'Controls referrer information',
        'Add: Referrer-Policy: no-referrer or strict-origin-when-cross-origin'
      )
    );

    // Permissions-Policy
    checks.push(
      this.checkHeader(
        'permissions-policy',
        lowerHeaders,
        'low',
        'Permissions-Policy',
        'Controls browser features',
        'Add: Permissions-Policy: geolocation=(), microphone=()'
      )
    );

    // Check for insecure headers
    if (lowerHeaders['server']) {
      checks.push({
        id: this.generateId(),
        name: 'Server Header Disclosure',
        category: 'headers',
        severity: 'low',
        passed: false,
        message: `Server header reveals: ${lowerHeaders['server']}`,
        recommendation: 'Remove or obfuscate Server header to hide server information',
        details: { value: lowerHeaders['server'] },
      });
    }

    if (lowerHeaders['x-powered-by']) {
      checks.push({
        id: this.generateId(),
        name: 'X-Powered-By Header Disclosure',
        category: 'headers',
        severity: 'low',
        passed: false,
        message: `X-Powered-By header reveals: ${lowerHeaders['x-powered-by']}`,
        recommendation: 'Remove X-Powered-By header to hide technology stack',
        details: { value: lowerHeaders['x-powered-by'] },
      });
    }

    return checks;
  }

  /**
   * Check for information leaks
   */
  private checkInformationLeaks(headers: Record<string, string>, body: string): SecurityCheck[] {
    const checks: SecurityCheck[] = [];

    // Check for sensitive data patterns in response body
    const patterns = [
      {
        name: 'API Key Leak',
        pattern: /(?:api[_-]?key|apikey|api[_-]?secret)[\s:=]+['"]?([a-zA-Z0-9_\-]{20,})['"]?/gi,
        severity: 'critical' as const,
      },
      {
        name: 'AWS Access Key Leak',
        pattern: /AKIA[0-9A-Z]{16}/g,
        severity: 'critical' as const,
      },
      {
        name: 'Private Key Leak',
        pattern: /-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----/g,
        severity: 'critical' as const,
      },
      {
        name: 'JWT Token Leak',
        pattern: /eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/g,
        severity: 'high' as const,
      },
      {
        name: 'Email Address Leak',
        pattern: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g,
        severity: 'low' as const,
      },
      {
        name: 'IP Address Leak',
        pattern: /\b(?:\d{1,3}\.){3}\d{1,3}\b/g,
        severity: 'low' as const,
      },
      {
        name: 'Password in Response',
        pattern: /(?:password|passwd|pwd)[\s:=]+['"]?([^'"\s]{6,})['"]?/gi,
        severity: 'critical' as const,
      },
      {
        name: 'Database Connection String',
        pattern: /(?:mongodb|mysql|postgresql|mssql):\/\/[^\s]+/gi,
        severity: 'critical' as const,
      },
    ];

    for (const { name, pattern, severity } of patterns) {
      const matches = body.match(pattern);
      if (matches && matches.length > 0) {
        checks.push({
          id: this.generateId(),
          name,
          category: 'leaks',
          severity,
          passed: false,
          message: `Found ${matches.length} potential leak(s) in response body`,
          recommendation: 'Remove sensitive data from API responses',
          details: {
            count: matches.length,
            samples: matches.slice(0, 3), // First 3 matches
          },
        });
      }
    }

    // Check for stack traces
    if (body.includes('at ') && (body.includes('.js:') || body.includes('.ts:'))) {
      checks.push({
        id: this.generateId(),
        name: 'Stack Trace Leak',
        category: 'leaks',
        severity: 'high',
        passed: false,
        message: 'Response contains stack trace information',
        recommendation: 'Disable detailed error messages in production',
      });
    }

    // Check for SQL errors
    const sqlErrors = [
      'SQL syntax',
      'mysql_fetch',
      'ORA-',
      'PostgreSQL',
      'SQLite',
      'SQLSTATE',
    ];
    for (const error of sqlErrors) {
      if (body.includes(error)) {
        checks.push({
          id: this.generateId(),
          name: 'SQL Error Leak',
          category: 'leaks',
          severity: 'high',
          passed: false,
          message: 'Response contains SQL error messages',
          recommendation: 'Use generic error messages and log details server-side',
        });
        break;
      }
    }

    return checks;
  }

  /**
   * Check cookie security
   */
  private checkCookieSecurity(headers: Record<string, string>): SecurityCheck[] {
    const checks: SecurityCheck[] = [];
    const lowerHeaders = this.toLowerCaseKeys(headers);
    const setCookie = lowerHeaders['set-cookie'];

    if (setCookie) {
      const cookies = Array.isArray(setCookie) ? setCookie : [setCookie];

      for (const cookie of cookies) {
        const cookieLower = cookie.toLowerCase();

        // Check for Secure flag
        if (!cookieLower.includes('secure')) {
          checks.push({
            id: this.generateId(),
            name: 'Cookie Missing Secure Flag',
            category: 'cookies',
            severity: 'high',
            passed: false,
            message: 'Cookie does not have Secure flag',
            recommendation: 'Add Secure flag to cookies: Set-Cookie: name=value; Secure',
            details: { cookie: cookie.split(';')[0] },
          });
        }

        // Check for HttpOnly flag
        if (!cookieLower.includes('httponly')) {
          checks.push({
            id: this.generateId(),
            name: 'Cookie Missing HttpOnly Flag',
            category: 'cookies',
            severity: 'medium',
            passed: false,
            message: 'Cookie does not have HttpOnly flag',
            recommendation: 'Add HttpOnly flag to cookies: Set-Cookie: name=value; HttpOnly',
            details: { cookie: cookie.split(';')[0] },
          });
        }

        // Check for SameSite attribute
        if (!cookieLower.includes('samesite')) {
          checks.push({
            id: this.generateId(),
            name: 'Cookie Missing SameSite Attribute',
            category: 'cookies',
            severity: 'medium',
            passed: false,
            message: 'Cookie does not have SameSite attribute',
            recommendation: 'Add SameSite attribute: Set-Cookie: name=value; SameSite=Strict',
            details: { cookie: cookie.split(';')[0] },
          });
        }
      }
    }

    return checks;
  }

  /**
   * Check SSL/TLS security
   */
  private checkSSLSecurity(ssl: any): SecurityCheck[] {
    const checks: SecurityCheck[] = [];

    if (ssl.protocol && ssl.protocol.includes('TLSv1.0')) {
      checks.push({
        id: this.generateId(),
        name: 'Weak TLS Version',
        category: 'ssl',
        severity: 'high',
        passed: false,
        message: 'Server uses TLS 1.0 which is deprecated',
        recommendation: 'Upgrade to TLS 1.2 or higher',
        details: { protocol: ssl.protocol },
      });
    }

    if (ssl.protocol && ssl.protocol.includes('TLSv1.1')) {
      checks.push({
        id: this.generateId(),
        name: 'Weak TLS Version',
        category: 'ssl',
        severity: 'medium',
        passed: false,
        message: 'Server uses TLS 1.1 which is deprecated',
        recommendation: 'Upgrade to TLS 1.2 or higher',
        details: { protocol: ssl.protocol },
      });
    }

    return checks;
  }

  /**
   * Helper: Check if header exists
   */
  private checkHeader(
    headerName: string,
    headers: Record<string, string>,
    severity: 'critical' | 'high' | 'medium' | 'low' | 'info',
    name: string,
    description: string,
    recommendation: string
  ): SecurityCheck {
    const exists = headerName in headers;

    return {
      id: this.generateId(),
      name,
      category: 'headers',
      severity,
      passed: exists,
      message: exists
        ? `${name} header is present`
        : `${name} header is missing`,
      recommendation: exists ? undefined : recommendation,
      details: exists ? { value: headers[headerName] } : undefined,
    };
  }

  /**
   * Calculate statistics
   */
  private calculateStatistics(checks: SecurityCheck[]): {
    score: number;
    criticalCount: number;
    highCount: number;
    mediumCount: number;
    lowCount: number;
    passedCount: number;
    failedCount: number;
  } {
    const criticalCount = checks.filter(c => c.severity === 'critical' && !c.passed).length;
    const highCount = checks.filter(c => c.severity === 'high' && !c.passed).length;
    const mediumCount = checks.filter(c => c.severity === 'medium' && !c.passed).length;
    const lowCount = checks.filter(c => c.severity === 'low' && !c.passed).length;
    const passedCount = checks.filter(c => c.passed).length;
    const failedCount = checks.filter(c => !c.passed).length;

    // Calculate score (0-100)
    const totalChecks = checks.length;
    const weightedFails =
      criticalCount * 10 +
      highCount * 5 +
      mediumCount * 3 +
      lowCount * 1;
    const maxPossibleScore = totalChecks * 10;
    const score = Math.max(0, Math.round(((maxPossibleScore - weightedFails) / maxPossibleScore) * 100));

    return {
      score,
      criticalCount,
      highCount,
      mediumCount,
      lowCount,
      passedCount,
      failedCount,
    };
  }

  /**
   * Convert headers to lowercase keys
   */
  private toLowerCaseKeys(obj: Record<string, string>): Record<string, string> {
    const result: Record<string, string> = {};
    for (const [key, value] of Object.entries(obj)) {
      result[key.toLowerCase()] = value;
    }
    return result;
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get security recommendations
   */
  getRecommendations(report: SecurityReport): string[] {
    return report.checks
      .filter(check => !check.passed && check.recommendation)
      .map(check => check.recommendation!);
  }

  /**
   * Export report as JSON
   */
  exportReport(report: SecurityReport): string {
    return JSON.stringify(report, null, 2);
  }

  /**
   * Export report as Markdown
   */
  exportReportAsMarkdown(report: SecurityReport): string {
    const lines: string[] = [];

    lines.push(`# Security Report`);
    lines.push(`**URL:** ${report.url}`);
    lines.push(`**Date:** ${report.timestamp.toISOString()}`);
    lines.push(`**Score:** ${report.score}/100`);
    lines.push('');

    lines.push(`## Summary`);
    lines.push(`- **Passed:** ${report.passedCount}`);
    lines.push(`- **Failed:** ${report.failedCount}`);
    lines.push(`- **Critical:** ${report.criticalCount}`);
    lines.push(`- **High:** ${report.highCount}`);
    lines.push(`- **Medium:** ${report.mediumCount}`);
    lines.push(`- **Low:** ${report.lowCount}`);
    lines.push('');

    const failedChecks = report.checks.filter(c => !c.passed);
    if (failedChecks.length > 0) {
      lines.push(`## Failed Checks`);
      lines.push('');

      for (const check of failedChecks) {
        lines.push(`### ${check.name} (${check.severity.toUpperCase()})`);
        lines.push(`- **Message:** ${check.message}`);
        if (check.recommendation) {
          lines.push(`- **Recommendation:** ${check.recommendation}`);
        }
        lines.push('');
      }
    }

    return lines.join('\n');
  }
}

// Singleton instance
let securityAssertionServiceInstance: SecurityAssertionService | null = null;

export function getSecurityAssertionService(): SecurityAssertionService {
  if (!securityAssertionServiceInstance) {
    securityAssertionServiceInstance = new SecurityAssertionService();
  }
  return securityAssertionServiceInstance;
}
