/**
 * OWASP A04:2021 - Insecure Design Tests
 */

import { OWASPScanOptions } from '../OWASPScannerService';

export async function testRateLimiting(this: any, options: OWASPScanOptions): Promise<void> {
  const requests = 20;
  let successCount = 0;
  const startTime = Date.now();

  for (let i = 0; i < requests; i++) {
    try {
      const response = await this.makeRequest(options.targetUrl, options);
      if (response.status === 200 || response.status === 201) {
        successCount++;
      }
      if (response.status === 429) {
        // Rate limit detected - good!
        return;
      }
    } catch (error) {
      // Rate limit might have been hit
    }
  }

  const duration = Date.now() - startTime;

  if (successCount === requests) {
    this.addFinding({
      category: 'A04',
      title: 'Missing Rate Limiting',
      description: `Endpoint does not implement rate limiting. ${requests} requests succeeded in ${duration}ms without throttling.`,
      severity: 'medium',
      confidence: 'confirmed',
      evidence: {
        request: options.targetUrl,
        payload: `${requests} requests in ${duration}ms`,
      },
      remediation: 'Implement rate limiting to prevent abuse, brute force attacks, and denial of service.',
      references: [
        'https://owasp.org/www-community/controls/Blocking_Brute_Force_Attacks',
        'https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html',
      ],
      cwe: 'CWE-307',
    });
  }
}

export async function testBusinessLogic(this: any, options: OWASPScanOptions): Promise<void> {
  // Test for negative quantities, prices, etc.
  const testValues = [
    { value: '-1', desc: 'negative value' },
    { value: '-999', desc: 'large negative value' },
    { value: '0', desc: 'zero value' },
    { value: '999999999', desc: 'extremely large value' },
    { value: '0.00001', desc: 'very small decimal' },
  ];
  
  for (const { value, desc } of testValues) {
    try {
      const testUrl = this.injectPayload(options.targetUrl, value);
      const response = await this.makeRequest(testUrl, options);

      // Check if the application accepts invalid business values
      if ((response.status === 200 || response.status === 201) && 
          !response.data.toLowerCase().includes('error') &&
          !response.data.toLowerCase().includes('invalid')) {
        this.addFinding({
          category: 'A04',
          title: 'Potential Business Logic Flaw',
          description: `Application accepts invalid business values (${desc})`,
          severity: 'medium',
          confidence: 'tentative',
          evidence: {
            request: testUrl,
            payload: value,
          },
          remediation: 'Implement proper business logic validation. Ensure all values are within acceptable ranges and make business sense.',
          references: [
            'https://owasp.org/www-community/vulnerabilities/Business_logic_vulnerability',
            'https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/',
          ],
          cwe: 'CWE-840',
        });
        break;
      }
    } catch (error) {
      // Continue
    }
  }
}
