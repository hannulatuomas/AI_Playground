/**
 * OWASP A08:2021 - Software and Data Integrity Failures Tests
 */

import { OWASPScanOptions } from '../OWASPScannerService';

export async function testInsecureDeserialization(this: any, options: OWASPScanOptions): Promise<void> {
  // Test for potential deserialization vulnerabilities
  const payloads = [
    'O:8:"stdClass":0:{}',  // PHP serialized object
    'rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcAUH2sHDFmDRAwACRgAKbG9hZEZhY3RvckkACXRocmVzaG9sZHhwP0AAAAAAAAB3CAAAABAAAAAAdAAEdGVzdHQABHRlc3R4',  // Java serialized
    '{"__proto__":{"isAdmin":true}}',  // Prototype pollution
  ];

  for (const payload of payloads) {
    try {
      const testOptions = {
        ...options,
        method: 'POST',
        body: payload,
        headers: {
          ...options.headers,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      };

      const response = await this.makeRequest(options.targetUrl, testOptions);

      // Check for deserialization errors
      if (response.data && (
        response.data.includes('unserialize') ||
        response.data.includes('ObjectInputStream') ||
        response.data.includes('pickle') ||
        response.data.includes('__proto__')
      )) {
        this.addFinding({
          category: 'A08',
          title: 'Potential Insecure Deserialization',
          description: 'Application may be vulnerable to insecure deserialization attacks',
          severity: 'high',
          confidence: 'tentative',
          evidence: {
            request: options.targetUrl,
            payload,
          },
          remediation: 'Avoid deserializing untrusted data. Use safe data formats like JSON. Implement integrity checks.',
          references: [
            'https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data',
            'https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html',
          ],
          cwe: 'CWE-502',
          cvss: 8.1,
        });
        break;
      }
    } catch (error) {
      // Continue
    }
  }
}

export async function testSubresourceIntegrity(this: any, options: OWASPScanOptions): Promise<void> {
  try {
    const response = await this.makeRequest(options.targetUrl, options);
    const body = response.data;

    // Check for external scripts without SRI
    const scriptPattern = /<script[^>]+src=["']https?:\/\/[^"']+["'][^>]*>/gi;
    const linkPattern = /<link[^>]+href=["']https?:\/\/[^"']+["'][^>]*>/gi;
    
    const scripts = body.match(scriptPattern) || [];
    const links = body.match(linkPattern) || [];

    let missingIntegrity = 0;

    for (const script of scripts) {
      if (!script.includes('integrity=')) {
        missingIntegrity++;
      }
    }

    for (const link of links) {
      if (link.includes('stylesheet') && !link.includes('integrity=')) {
        missingIntegrity++;
      }
    }

    if (missingIntegrity > 0) {
      this.addFinding({
        category: 'A08',
        title: 'Missing Subresource Integrity',
        description: `${missingIntegrity} external resources loaded without Subresource Integrity (SRI) checks`,
        severity: 'medium',
        confidence: 'confirmed',
        evidence: {
          request: options.targetUrl,
          payload: `${missingIntegrity} resources without SRI`,
        },
        remediation: 'Implement Subresource Integrity (SRI) for all external scripts and stylesheets.',
        references: [
          'https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity',
          'https://www.srihash.org/',
        ],
        cwe: 'CWE-353',
      });
    }
  } catch (error) {
    // Continue
  }
}
