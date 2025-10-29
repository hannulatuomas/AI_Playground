/**
 * OWASP A05:2021 - Security Misconfiguration Tests
 */

import { OWASPScanOptions } from '../OWASPScannerService';

export async function testSecurityHeaders(this: any, options: OWASPScanOptions): Promise<void> {
  try {
    const response = await this.makeRequest(options.targetUrl, options);
    const headers = response.headers;

    const requiredHeaders = {
      'x-frame-options': { name: 'X-Frame-Options', severity: 'medium' as const },
      'x-content-type-options': { name: 'X-Content-Type-Options', severity: 'medium' as const },
      'content-security-policy': { name: 'Content-Security-Policy', severity: 'high' as const },
      'x-xss-protection': { name: 'X-XSS-Protection', severity: 'low' as const },
      'referrer-policy': { name: 'Referrer-Policy', severity: 'low' as const },
    };

    const missingHeaders: string[] = [];
    let highestSeverity: 'high' | 'medium' | 'low' = 'low';

    for (const [key, { name, severity }] of Object.entries(requiredHeaders)) {
      if (!headers[key]) {
        missingHeaders.push(name);
        if (severity === 'high' || (severity === 'medium' && highestSeverity === 'low')) {
          highestSeverity = severity;
        }
      }
    }

    if (missingHeaders.length > 0) {
      this.addFinding({
        category: 'A05',
        title: 'Missing Security Headers',
        description: `Missing security headers: ${missingHeaders.join(', ')}`,
        severity: highestSeverity,
        confidence: 'confirmed',
        evidence: {
          request: options.targetUrl,
        },
        remediation: 'Implement all recommended security headers to protect against common attacks.',
        references: [
          'https://owasp.org/www-project-secure-headers/',
          'https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html',
        ],
        cwe: 'CWE-16',
      });
    }

    // Check for server version disclosure
    const serverHeader = headers['server'];
    const poweredBy = headers['x-powered-by'];
    
    if (serverHeader || poweredBy) {
      this.addFinding({
        category: 'A05',
        title: 'Server Version Disclosure',
        description: 'Server reveals version information in headers',
        severity: 'low',
        confidence: 'confirmed',
        evidence: {
          request: options.targetUrl,
          response: `Server: ${serverHeader || 'N/A'}, X-Powered-By: ${poweredBy || 'N/A'}`,
        },
        remediation: 'Remove or obfuscate server version headers to prevent information disclosure.',
        references: [
          'https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/02-Fingerprint_Web_Server',
        ],
        cwe: 'CWE-200',
      });
    }
  } catch (error) {
    // Continue
  }
}

export async function testDirectoryListing(this: any, options: OWASPScanOptions): Promise<void> {
  const testPaths = ['/', '/images/', '/uploads/', '/files/', '/assets/'];

  for (const testPath of testPaths) {
    try {
      const url = new URL(options.targetUrl);
      url.pathname = testPath;
      
      const response = await this.makeRequest(url.toString(), options);

      if (this.detectDirectoryListing(response.data)) {
        this.addFinding({
          category: 'A05',
          title: 'Directory Listing Enabled',
          description: `Server allows directory listing at ${testPath}`,
          severity: 'low',
          confidence: 'confirmed',
          evidence: {
            request: url.toString(),
            location: testPath,
          },
          remediation: 'Disable directory listing in web server configuration.',
          references: [
            'https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/04-Review_Old_Backup_and_Unreferenced_Files_for_Sensitive_Information',
          ],
          cwe: 'CWE-548',
        });
        break;
      }
    } catch (error) {
      // Continue
    }
  }
}

export async function testVerboseErrors(this: any, options: OWASPScanOptions): Promise<void> {
  const errorTriggers = [
    '/nonexistent-page-12345',
    '/?id=abc',
    '/?page=999999',
  ];

  for (const trigger of errorTriggers) {
    try {
      const testUrl = options.targetUrl + trigger;
      const response = await this.makeRequest(testUrl, options);

      if (this.detectVerboseError(response.data)) {
        this.addFinding({
          category: 'A05',
          title: 'Verbose Error Messages',
          description: 'Application reveals sensitive information in error messages (stack traces, file paths, etc.)',
          severity: 'low',
          confidence: 'confirmed',
          evidence: {
            request: testUrl,
            response: response.data.substring(0, 500),
          },
          remediation: 'Implement generic error messages for users and log detailed errors server-side only.',
          references: [
            'https://owasp.org/www-community/Improper_Error_Handling',
            'https://cwe.mitre.org/data/definitions/209.html',
          ],
          cwe: 'CWE-209',
        });
        break;
      }
    } catch (error) {
      // Continue
    }
  }
}
