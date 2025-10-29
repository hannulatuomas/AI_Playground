/**
 * OWASP A02:2021 - Cryptographic Failures Tests
 */

import { OWASPScanOptions } from '../OWASPScannerService';

export async function testInsecureTransport(this: any, options: OWASPScanOptions): Promise<void> {
  if (options.targetUrl.startsWith('http://')) {
    this.addFinding({
      category: 'A02',
      title: 'Insecure Transport - No HTTPS',
      description: 'Application uses unencrypted HTTP protocol, exposing data to interception',
      severity: 'high',
      confidence: 'confirmed',
      evidence: {
        request: options.targetUrl,
      },
      remediation: 'Use HTTPS for all communications. Implement HTTP Strict Transport Security (HSTS) header.',
      references: [
        'https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure',
        'https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html',
      ],
      cwe: 'CWE-319',
    });
  }
}

export async function testWeakSSL(this: any, options: OWASPScanOptions): Promise<void> {
  if (!options.targetUrl.startsWith('https://')) {
    return;
  }

  try {
    const response = await this.makeRequest(options.targetUrl, options);
    const headers = response.headers;

    // Check for HSTS
    const hsts = headers['strict-transport-security'];
    if (!hsts) {
      this.addFinding({
        category: 'A02',
        title: 'Missing HSTS Header',
        description: 'Server does not implement HTTP Strict Transport Security',
        severity: 'medium',
        confidence: 'confirmed',
        evidence: {
          request: options.targetUrl,
        },
        remediation: 'Implement HSTS header: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload',
        references: [
          'https://owasp.org/www-project-secure-headers/',
          'https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Strict_Transport_Security_Cheat_Sheet.html',
        ],
        cwe: 'CWE-319',
      });
    } else if (!hsts.includes('includeSubDomains')) {
      this.addFinding({
        category: 'A02',
        title: 'Weak HSTS Configuration',
        description: 'HSTS header does not include subdomains',
        severity: 'low',
        confidence: 'confirmed',
        evidence: {
          request: options.targetUrl,
          response: `Strict-Transport-Security: ${hsts}`,
        },
        remediation: 'Add includeSubDomains directive to HSTS header',
        references: [
          'https://owasp.org/www-project-secure-headers/',
        ],
        cwe: 'CWE-319',
      });
    }
  } catch (error) {
    // Continue
  }
}

export async function testSensitiveDataInURL(this: any, options: OWASPScanOptions): Promise<void> {
  const sensitivePatterns = [
    { pattern: /password=/i, name: 'password' },
    { pattern: /token=/i, name: 'token' },
    { pattern: /api[_-]?key=/i, name: 'API key' },
    { pattern: /secret=/i, name: 'secret' },
    { pattern: /ssn=/i, name: 'SSN' },
    { pattern: /credit[_-]?card=/i, name: 'credit card' },
    { pattern: /auth=/i, name: 'authentication data' },
  ];

  for (const { pattern, name } of sensitivePatterns) {
    if (pattern.test(options.targetUrl)) {
      this.addFinding({
        category: 'A02',
        title: 'Sensitive Data in URL',
        description: `Sensitive information (${name}) detected in URL parameters`,
        severity: 'high',
        confidence: 'confirmed',
        evidence: {
          request: options.targetUrl,
        },
        remediation: 'Never pass sensitive data in URL parameters. Use POST body with HTTPS or secure headers instead.',
        references: [
          'https://owasp.org/www-community/vulnerabilities/Information_exposure_through_query_strings_in_url',
          'https://cwe.mitre.org/data/definitions/598.html',
        ],
        cwe: 'CWE-598',
      });
      break;
    }
  }
}
