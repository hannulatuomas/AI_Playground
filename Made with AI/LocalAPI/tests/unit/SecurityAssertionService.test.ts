import { SecurityAssertionService } from '../../src/main/services/SecurityAssertionService';

describe('SecurityAssertionService', () => {
  let service: SecurityAssertionService;

  beforeEach(() => {
    service = new SecurityAssertionService();
  });

  describe('Security Header Checks', () => {
    test('should detect missing security headers', () => {
      const report = service.runSecurityChecks({
        url: 'https://example.com',
        status: 200,
        headers: {},
        body: '{}',
      });

      expect(report.checks.length).toBeGreaterThan(0);
      const failedChecks = report.checks.filter(c => !c.passed);
      expect(failedChecks.length).toBeGreaterThan(0);
    });

    test('should pass with all security headers present', () => {
      const report = service.runSecurityChecks({
        url: 'https://example.com',
        status: 200,
        headers: {
          'strict-transport-security': 'max-age=31536000',
          'x-frame-options': 'DENY',
          'x-content-type-options': 'nosniff',
          'content-security-policy': "default-src 'self'",
          'x-xss-protection': '1; mode=block',
          'referrer-policy': 'no-referrer',
        },
        body: '{}',
      });

      const headerChecks = report.checks.filter(c => c.category === 'headers');
      const passedHeaders = headerChecks.filter(c => c.passed);
      expect(passedHeaders.length).toBeGreaterThan(0);
    });

    test('should detect server header disclosure', () => {
      const report = service.runSecurityChecks({
        url: 'https://example.com',
        status: 200,
        headers: {
          'server': 'Apache/2.4.41',
          'x-powered-by': 'PHP/7.4',
        },
        body: '{}',
      });

      const disclosureChecks = report.checks.filter(
        c => c.name.includes('Disclosure')
      );
      expect(disclosureChecks.length).toBeGreaterThan(0);
      expect(disclosureChecks.every(c => !c.passed)).toBe(true);
    });
  });

  describe('Information Leak Detection', () => {
    test('should detect API key leak', () => {
      const report = service.runSecurityChecks({
        url: 'https://example.com',
        status: 200,
        headers: {},
        body: 'api_key: sk_live_1234567890abcdefghijklmnop',
      });

      const leakChecks = report.checks.filter(
        c => c.category === 'leaks' && c.name.includes('API Key')
      );
      expect(leakChecks.length).toBeGreaterThan(0);
      expect(leakChecks[0].passed).toBe(false);
    });

    test('should detect JWT token leak', () => {
      const report = service.runSecurityChecks({
        url: 'https://example.com',
        status: 200,
        headers: {},
        body: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U',
      });

      const jwtChecks = report.checks.filter(
        c => c.category === 'leaks' && c.name.includes('JWT')
      );
      expect(jwtChecks.length).toBeGreaterThan(0);
    });

    test('should detect stack trace leak', () => {
      const report = service.runSecurityChecks({
        url: 'https://example.com',
        status: 500,
        headers: {},
        body: 'Error at app.js:123\n    at module.js:456',
      });

      const stackTraceChecks = report.checks.filter(
        c => c.name.includes('Stack Trace')
      );
      expect(stackTraceChecks.length).toBeGreaterThan(0);
    });
  });

  describe('Cookie Security', () => {
    test('should detect missing Secure flag', () => {
      const report = service.runSecurityChecks({
        url: 'https://example.com',
        status: 200,
        headers: {
          'set-cookie': 'sessionId=abc123; HttpOnly',
        },
        body: '{}',
      });

      const cookieChecks = report.checks.filter(
        c => c.category === 'cookies' && c.name.includes('Secure')
      );
      expect(cookieChecks.length).toBeGreaterThan(0);
    });

    test('should detect missing HttpOnly flag', () => {
      const report = service.runSecurityChecks({
        url: 'https://example.com',
        status: 200,
        headers: {
          'set-cookie': 'sessionId=abc123; Secure',
        },
        body: '{}',
      });

      const cookieChecks = report.checks.filter(
        c => c.category === 'cookies' && c.name.includes('HttpOnly')
      );
      expect(cookieChecks.length).toBeGreaterThan(0);
    });
  });

  describe('Security Scoring', () => {
    test('should calculate security score', () => {
      const report = service.runSecurityChecks({
        url: 'https://example.com',
        status: 200,
        headers: {},
        body: '{}',
      });

      expect(report.score).toBeGreaterThanOrEqual(0);
      expect(report.score).toBeLessThanOrEqual(100);
    });

    test('should have lower score with vulnerabilities', () => {
      const badReport = service.runSecurityChecks({
        url: 'https://example.com',
        status: 200,
        headers: {
          'server': 'Apache/2.4.41',
        },
        body: JSON.stringify({ api_key: 'sk_live_12345678901234567890' }),
      });

      const goodReport = service.runSecurityChecks({
        url: 'https://example.com',
        status: 200,
        headers: {
          'strict-transport-security': 'max-age=31536000',
          'x-frame-options': 'DENY',
          'x-content-type-options': 'nosniff',
        },
        body: '{}',
      });

      expect(badReport.score).toBeLessThan(goodReport.score);
    });
  });

  describe('Report Export', () => {
    test('should export report as JSON', () => {
      const report = service.runSecurityChecks({
        url: 'https://example.com',
        status: 200,
        headers: {},
        body: '{}',
      });

      const json = service.exportReport(report);
      expect(json).toBeDefined();
      expect(() => JSON.parse(json)).not.toThrow();
    });

    test('should export report as Markdown', () => {
      const report = service.runSecurityChecks({
        url: 'https://example.com',
        status: 200,
        headers: {},
        body: '{}',
      });

      const markdown = service.exportReportAsMarkdown(report);
      expect(markdown).toContain('# Security Report');
      expect(markdown).toContain('## Summary');
    });
  });

  describe('Recommendations', () => {
    test('should provide recommendations', () => {
      const report = service.runSecurityChecks({
        url: 'https://example.com',
        status: 200,
        headers: {},
        body: '{}',
      });

      const recommendations = service.getRecommendations(report);
      expect(Array.isArray(recommendations)).toBe(true);
      expect(recommendations.length).toBeGreaterThan(0);
    });
  });
});
