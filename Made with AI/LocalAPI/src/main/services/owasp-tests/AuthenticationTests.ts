/**
 * OWASP A07:2021 - Identification and Authentication Failures Tests
 */

import { OWASPScanOptions } from '../OWASPScannerService';

export async function testWeakPasswordPolicy(this: any, options: OWASPScanOptions): Promise<void> {
  // This is informational - actual password policy testing requires registration endpoint
  this.addFinding({
    category: 'A07',
    title: 'Password Policy Verification Recommended',
    description: 'Manual verification of password policy is recommended',
    severity: 'info',
    confidence: 'tentative',
    evidence: {
      request: options.targetUrl,
    },
    remediation: 'Implement strong password policy: minimum 8 characters, complexity requirements, password history, account lockout after failed attempts.',
    references: [
      'https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html',
      'https://pages.nist.gov/800-63-3/sp800-63b.html',
    ],
    cwe: 'CWE-521',
  });
}

export async function testSessionFixation(this: any, options: OWASPScanOptions): Promise<void> {
  try {
    // Test 1: Check if session ID changes after login
    const response1 = await this.makeRequest(options.targetUrl, options);
    const cookies1 = response1.headers['set-cookie'];

    if (cookies1) {
      const sessionCookie1 = this.extractSessionCookie(cookies1);
      
      if (sessionCookie1) {
        // Make another request
        const response2 = await this.makeRequest(options.targetUrl, options);
        const cookies2 = response2.headers['set-cookie'];
        
        if (cookies2) {
          const sessionCookie2 = this.extractSessionCookie(cookies2);
          
          // If session cookie is the same, might be vulnerable
          if (sessionCookie1 === sessionCookie2) {
            this.addFinding({
              category: 'A07',
              title: 'Potential Session Fixation Vulnerability',
              description: 'Session ID does not change between requests, which may indicate session fixation vulnerability',
              severity: 'medium',
              confidence: 'tentative',
              evidence: {
                request: options.targetUrl,
              },
              remediation: 'Regenerate session ID after authentication. Implement proper session management.',
              references: [
                'https://owasp.org/www-community/attacks/Session_fixation',
                'https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html',
              ],
              cwe: 'CWE-384',
            });
          }
        }
      }

      // Check for secure and httpOnly flags
      const cookieString = Array.isArray(cookies1) ? cookies1.join('; ') : cookies1;
      
      if (!cookieString.toLowerCase().includes('secure')) {
        this.addFinding({
          category: 'A07',
          title: 'Missing Secure Flag on Cookie',
          description: 'Session cookies do not have Secure flag set',
          severity: 'medium',
          confidence: 'confirmed',
          evidence: {
            request: options.targetUrl,
            response: cookieString,
          },
          remediation: 'Set Secure flag on all session cookies to prevent transmission over unencrypted connections.',
          references: [
            'https://owasp.org/www-community/controls/SecureCookieAttribute',
          ],
          cwe: 'CWE-614',
        });
      }

      if (!cookieString.toLowerCase().includes('httponly')) {
        this.addFinding({
          category: 'A07',
          title: 'Missing HttpOnly Flag on Cookie',
          description: 'Session cookies do not have HttpOnly flag set',
          severity: 'medium',
          confidence: 'confirmed',
          evidence: {
            request: options.targetUrl,
            response: cookieString,
          },
          remediation: 'Set HttpOnly flag on all session cookies to prevent JavaScript access.',
          references: [
            'https://owasp.org/www-community/HttpOnly',
          ],
          cwe: 'CWE-1004',
        });
      }
    }
  } catch (error) {
    // Continue
  }
}

// Helper method
function extractSessionCookie(cookies: string | string[]): string | null {
  const cookieArray = Array.isArray(cookies) ? cookies : [cookies];
  const sessionPatterns = [/PHPSESSID=([^;]+)/, /JSESSIONID=([^;]+)/, /sessionid=([^;]+)/i];
  
  for (const cookie of cookieArray) {
    for (const pattern of sessionPatterns) {
      const match = cookie.match(pattern);
      if (match) {
        return match[1];
      }
    }
  }
  
  return null;
}

// Add helper to class prototype
(testSessionFixation as any).extractSessionCookie = extractSessionCookie;
