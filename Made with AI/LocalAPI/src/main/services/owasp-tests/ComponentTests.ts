/**
 * OWASP A06:2021 - Vulnerable and Outdated Components Tests
 */

import { OWASPScanOptions } from '../OWASPScannerService';

export async function testOutdatedLibraries(this: any, options: OWASPScanOptions): Promise<void> {
  try {
    const response = await this.makeRequest(options.targetUrl, options);
    const body = response.data;

    // Check for known vulnerable libraries in response
    const vulnerablePatterns = [
      { pattern: /jquery[/-]([0-9.]+)/i, name: 'jQuery', minVersion: '3.5.0', severity: 'medium' as const },
      { pattern: /angular[/-]([0-9.]+)/i, name: 'Angular', minVersion: '12.0.0', severity: 'medium' as const },
      { pattern: /react[/-]([0-9.]+)/i, name: 'React', minVersion: '17.0.0', severity: 'medium' as const },
      { pattern: /vue[/-]([0-9.]+)/i, name: 'Vue.js', minVersion: '3.0.0', severity: 'medium' as const },
      { pattern: /bootstrap[/-]([0-9.]+)/i, name: 'Bootstrap', minVersion: '5.0.0', severity: 'low' as const },
      { pattern: /moment[/-]([0-9.]+)/i, name: 'Moment.js', minVersion: '2.29.0', severity: 'low' as const },
    ];

    for (const { pattern, name, minVersion, severity } of vulnerablePatterns) {
      const match = body.match(pattern);
      if (match) {
        const version = match[1];
        if (this.isVersionOutdated(version, minVersion)) {
          this.addFinding({
            category: 'A06',
            title: `Outdated ${name} Version`,
            description: `Application uses ${name} version ${version}, which may contain known vulnerabilities`,
            severity,
            confidence: 'firm',
            evidence: {
              request: options.targetUrl,
              payload: `${name} ${version}`,
            },
            remediation: `Update ${name} to version ${minVersion} or later. Check for security advisories.`,
            references: [
              'https://owasp.org/www-community/vulnerabilities/Using_Components_with_Known_Vulnerabilities',
              'https://snyk.io/vuln/',
            ],
            cwe: 'CWE-1104',
          });
        }
      }
    }

    // Check for deprecated libraries
    const deprecatedLibraries = [
      { pattern: /bower_components/i, name: 'Bower' },
      { pattern: /prototype\.js/i, name: 'Prototype.js' },
      { pattern: /mootools/i, name: 'MooTools' },
    ];

    for (const { pattern, name } of deprecatedLibraries) {
      if (pattern.test(body)) {
        this.addFinding({
          category: 'A06',
          title: `Deprecated Library: ${name}`,
          description: `Application uses ${name}, which is no longer maintained`,
          severity: 'medium',
          confidence: 'confirmed',
          evidence: {
            request: options.targetUrl,
          },
          remediation: `Replace ${name} with a modern, maintained alternative.`,
          references: [
            'https://owasp.org/www-community/vulnerabilities/Using_Components_with_Known_Vulnerabilities',
          ],
          cwe: 'CWE-1104',
        });
      }
    }
  } catch (error) {
    // Continue
  }
}
