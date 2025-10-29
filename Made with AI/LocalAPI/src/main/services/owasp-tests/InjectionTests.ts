/**
 * OWASP A03:2021 - Injection Tests
 */

import { OWASPScanOptions } from '../OWASPScannerService';

export async function testSQLInjection(this: any, options: OWASPScanOptions): Promise<void> {
  const payloads = [
    "' OR '1'='1",
    "' OR '1'='1' --",
    "' OR '1'='1' /*",
    "admin'--",
    "1' UNION SELECT NULL--",
    "' AND 1=CONVERT(int, (SELECT @@version))--",
    "' AND 1=2 UNION SELECT NULL, NULL--",
    "1' ORDER BY 1--",
  ];

  for (const payload of payloads) {
    try {
      const testUrl = this.injectPayload(options.targetUrl, payload);
      const response = await this.makeRequest(testUrl, options);

      if (this.detectSQLError(response.data)) {
        this.addFinding({
          category: 'A03',
          title: 'SQL Injection Vulnerability',
          description: 'Application is vulnerable to SQL injection attacks, allowing unauthorized database access',
          severity: 'critical',
          confidence: 'confirmed',
          evidence: {
            request: testUrl,
            payload,
            response: response.data.substring(0, 500),
          },
          remediation: 'Use parameterized queries or prepared statements. Never concatenate user input into SQL queries. Implement input validation.',
          references: [
            'https://owasp.org/www-community/attacks/SQL_Injection',
            'https://cwe.mitre.org/data/definitions/89.html',
            'https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html',
          ],
          cwe: 'CWE-89',
          cvss: 9.8,
        });
        break;
      }
    } catch (error) {
      // Continue testing
    }
  }
}

export async function testXSS(this: any, options: OWASPScanOptions): Promise<void> {
  const payloads = [
    '<script>alert(1)</script>',
    '<img src=x onerror=alert(1)>',
    '<svg onload=alert(1)>',
    'javascript:alert(1)',
    '"><script>alert(1)</script>',
    '<iframe src="javascript:alert(1)">',
    '<body onload=alert(1)>',
  ];

  for (const payload of payloads) {
    try {
      const testUrl = this.injectPayload(options.targetUrl, payload);
      const response = await this.makeRequest(testUrl, options);

      if (response.data.includes(payload) || response.data.includes(payload.replace(/"/g, '&quot;'))) {
        this.addFinding({
          category: 'A03',
          title: 'Cross-Site Scripting (XSS) Vulnerability',
          description: 'Application reflects user input without proper encoding, allowing script injection',
          severity: 'high',
          confidence: 'confirmed',
          evidence: {
            request: testUrl,
            payload,
            response: response.data.substring(0, 500),
          },
          remediation: 'Implement proper output encoding for all user input. Use Content Security Policy (CSP) headers.',
          references: [
            'https://owasp.org/www-community/attacks/xss/',
            'https://cwe.mitre.org/data/definitions/79.html',
            'https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html',
          ],
          cwe: 'CWE-79',
          cvss: 7.5,
        });
        break;
      }
    } catch (error) {
      // Continue testing
    }
  }
}

export async function testCommandInjection(this: any, options: OWASPScanOptions): Promise<void> {
  const payloads = [
    '; ls',
    '| whoami',
    '`id`',
    '$(whoami)',
    '; cat /etc/passwd',
    '&& dir',
    '| type C:\\Windows\\win.ini',
  ];

  for (const payload of payloads) {
    try {
      const testUrl = this.injectPayload(options.targetUrl, payload);
      const response = await this.makeRequest(testUrl, options);

      if (this.detectCommandInjection(response.data)) {
        this.addFinding({
          category: 'A03',
          title: 'Command Injection Vulnerability',
          description: 'Application executes system commands with user input, allowing arbitrary command execution',
          severity: 'critical',
          confidence: 'firm',
          evidence: {
            request: testUrl,
            payload,
            response: response.data.substring(0, 500),
          },
          remediation: 'Never execute system commands with user input. Use safe APIs and libraries instead. Implement strict input validation.',
          references: [
            'https://owasp.org/www-community/attacks/Command_Injection',
            'https://cwe.mitre.org/data/definitions/78.html',
          ],
          cwe: 'CWE-78',
          cvss: 9.8,
        });
        break;
      }
    } catch (error) {
      // Continue testing
    }
  }
}
