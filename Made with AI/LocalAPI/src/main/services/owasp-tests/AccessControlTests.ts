/**
 * OWASP A01:2021 - Broken Access Control Tests
 */

import { OWASPScanOptions } from '../OWASPScannerService';

export async function testPathTraversal(this: any, options: OWASPScanOptions): Promise<void> {
  const payloads = [
    '../../../etc/passwd',
    '..\\..\\..\\windows\\win.ini',
    '....//....//....//etc/passwd',
    '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd',
    '..%252f..%252f..%252fetc%252fpasswd',
  ];

  for (const payload of payloads) {
    try {
      const testUrl = this.injectPayload(options.targetUrl, payload);
      const response = await this.makeRequest(testUrl, options);

      if (this.detectPathTraversal(response.data)) {
        this.addFinding({
          category: 'A01',
          title: 'Path Traversal Vulnerability',
          description: 'Application is vulnerable to path traversal attacks, allowing access to files outside the intended directory',
          severity: 'high',
          confidence: 'confirmed',
          evidence: {
            request: testUrl,
            response: response.data.substring(0, 500),
            payload,
          },
          remediation: 'Implement proper input validation and use whitelisting for file access. Never concatenate user input directly into file paths.',
          references: [
            'https://owasp.org/www-community/attacks/Path_Traversal',
            'https://cwe.mitre.org/data/definitions/22.html',
          ],
          cwe: 'CWE-22',
        });
        break;
      }
    } catch (error) {
      // Continue testing
    }
  }
}

export async function testForcedBrowsing(this: any, options: OWASPScanOptions): Promise<void> {
  const commonPaths = [
    '/admin',
    '/administrator',
    '/admin.php',
    '/admin/login',
    '/admin/dashboard',
    '/api/admin',
    '/api/v1/admin',
    '/dashboard',
    '/config',
    '/backup',
    '/.env',
    '/.git/config',
    '/phpinfo.php',
    '/server-status',
  ];

  for (const path of commonPaths) {
    try {
      const testUrl = new URL(options.targetUrl);
      testUrl.pathname = path;
      
      const response = await this.makeRequest(testUrl.toString(), options);

      if (response.status === 200 && !this.isLoginPage(response.data)) {
        this.addFinding({
          category: 'A01',
          title: 'Unprotected Administrative Interface',
          description: `Administrative path ${path} is accessible without authentication`,
          severity: 'critical',
          confidence: 'confirmed',
          evidence: {
            request: testUrl.toString(),
            location: path,
          },
          remediation: 'Implement proper authentication and authorization for all administrative interfaces',
          references: [
            'https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control',
          ],
          cwe: 'CWE-284',
        });
      }
    } catch (error) {
      // Path not accessible - good
    }
  }
}

export async function testCORSMisconfiguration(this: any, options: OWASPScanOptions): Promise<void> {
  const testOrigins = [
    'https://evil.com',
    'null',
    'https://attacker.com',
    'http://localhost',
  ];

  for (const origin of testOrigins) {
    try {
      const testOptions = {
        ...options,
        headers: {
          ...options.headers,
          'Origin': origin,
        },
      };

      const response = await this.makeRequest(options.targetUrl, testOptions);
      const corsHeader = response.headers['access-control-allow-origin'];
      const credentialsHeader = response.headers['access-control-allow-credentials'];

      if (corsHeader === origin || corsHeader === '*') {
        const severity = (corsHeader === '*' && credentialsHeader === 'true') ? 'high' : 'medium';
        
        this.addFinding({
          category: 'A01',
          title: 'CORS Misconfiguration',
          description: 'Server reflects arbitrary origins in CORS headers, potentially allowing cross-origin attacks',
          severity,
          confidence: 'confirmed',
          evidence: {
            request: `Origin: ${origin}`,
            response: `Access-Control-Allow-Origin: ${corsHeader}`,
          },
          remediation: 'Implement strict CORS policy with whitelisted origins. Never use wildcard (*) with credentials.',
          references: [
            'https://owasp.org/www-community/attacks/CORS_OriginHeaderScrutiny',
            'https://portswigger.net/web-security/cors',
          ],
          cwe: 'CWE-346',
        });
        break;
      }
    } catch (error) {
      // Continue testing
    }
  }
}
