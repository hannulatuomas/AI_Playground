/**
 * OWASP A09:2021 - Security Logging and Monitoring Failures Tests
 */

import { OWASPScanOptions } from '../OWASPScannerService';

export async function testLoggingAndMonitoring(this: any, options: OWASPScanOptions): Promise<void> {
  // This is mostly informational as we can't directly test logging
  this.addFinding({
    category: 'A09',
    title: 'Security Logging Verification Recommended',
    description: 'Manual verification of security logging and monitoring is recommended',
    severity: 'info',
    confidence: 'tentative',
    evidence: {
      request: options.targetUrl,
    },
    remediation: `Implement comprehensive security logging:
- Log all authentication attempts (success and failure)
- Log all access control failures
- Log all input validation failures
- Log all application errors
- Implement real-time monitoring and alerting
- Ensure logs are tamper-proof and backed up`,
    references: [
      'https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html',
      'https://owasp.org/www-project-top-ten/2017/A10_2017-Insufficient_Logging%2526Monitoring',
    ],
    cwe: 'CWE-778',
  });

  // Test for information disclosure in logs
  try {
    const testUrl = options.targetUrl + '/debug';
    const response = await this.makeRequest(testUrl, options);

    if (response.status === 200 && (
      response.data.includes('debug') ||
      response.data.includes('log') ||
      response.data.includes('trace')
    )) {
      this.addFinding({
        category: 'A09',
        title: 'Debug/Log Endpoint Exposed',
        description: 'Application exposes debug or log information publicly',
        severity: 'medium',
        confidence: 'firm',
        evidence: {
          request: testUrl,
        },
        remediation: 'Remove or properly secure debug and log endpoints. Never expose logs publicly.',
        references: [
          'https://owasp.org/www-community/Improper_Error_Handling',
        ],
        cwe: 'CWE-532',
      });
    }
  } catch (error) {
    // Continue
  }
}
