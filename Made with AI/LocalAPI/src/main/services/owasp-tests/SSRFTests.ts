/**
 * OWASP A10:2021 - Server-Side Request Forgery (SSRF) Tests
 */

import { OWASPScanOptions } from '../OWASPScannerService';

export async function testSSRFVulnerability(this: any, options: OWASPScanOptions): Promise<void> {
  const ssrfPayloads = [
    'http://localhost',
    'http://127.0.0.1',
    'http://0.0.0.0',
    'http://[::1]',
    'http://169.254.169.254',  // AWS metadata
    'http://metadata.google.internal',  // GCP metadata
    'file:///etc/passwd',
    'http://localhost:22',
    'http://internal-server',
  ];

  for (const payload of ssrfPayloads) {
    try {
      const testUrl = this.injectPayload(options.targetUrl, payload);
      const response = await this.makeRequest(testUrl, options);

      // Check for SSRF indicators
      if (response.status === 200 && (
        response.data.includes('root:x:') ||  // /etc/passwd
        response.data.includes('ami-id') ||  // AWS metadata
        response.data.includes('instance-id') ||
        response.data.includes('SSH-') ||  // SSH banner
        response.data.length > 0  // Any response from internal resource
      )) {
        this.addFinding({
          category: 'A10',
          title: 'Server-Side Request Forgery (SSRF) Vulnerability',
          description: 'Application makes requests to attacker-controlled URLs, potentially accessing internal resources',
          severity: 'high',
          confidence: 'firm',
          evidence: {
            request: testUrl,
            payload,
            response: response.data.substring(0, 500),
          },
          remediation: 'Implement URL whitelist validation. Block requests to private IP ranges and localhost. Use network segmentation.',
          references: [
            'https://owasp.org/www-community/attacks/Server_Side_Request_Forgery',
            'https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html',
          ],
          cwe: 'CWE-918',
          cvss: 8.6,
        });
        break;
      }
    } catch (error) {
      // Continue testing
    }
  }

  // Test for DNS rebinding
  try {
    const testUrl = this.injectPayload(options.targetUrl, 'http://spoofed.burpcollaborator.net');
    const response = await this.makeRequest(testUrl, options);

    if (response.status === 200) {
      this.addFinding({
        category: 'A10',
        title: 'Potential SSRF - External DNS Resolution',
        description: 'Application resolves and connects to external DNS names, which could be exploited for SSRF',
        severity: 'medium',
        confidence: 'tentative',
        evidence: {
          request: testUrl,
        },
        remediation: 'Implement DNS resolution validation. Use whitelist of allowed domains.',
        references: [
          'https://owasp.org/www-community/attacks/Server_Side_Request_Forgery',
        ],
        cwe: 'CWE-918',
      });
    }
  } catch (error) {
    // Continue
  }
}
