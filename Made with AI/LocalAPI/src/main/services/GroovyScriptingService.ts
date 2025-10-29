// Groovy-style Scripting Service
// Provides Groovy-like syntax and features using JavaScript/Node.js VM
// Note: This is a JavaScript implementation with Groovy-style API, not actual Groovy/JVM

import * as vm from 'vm';
import * as jsonpath from 'jsonpath';
import type { Response } from '../../types/models';

interface TestResult {
  name: string;
  passed: boolean;
  error?: string;
}

interface GroovyContext {
  // Groovy-style pm object
  pm: {
    test: (name: string, closure: () => void) => void;
    expect: (value: any) => any;
    response: any;
    variables: any;
    environment: any;
    globals: any;
    request: any;
    jsonPath: (obj: any, path: string) => any[];
    extractJson: (path: string, varName?: string) => any;
  };
  
  // Groovy-style assert methods
  assert: (condition: boolean, message?: string) => void;
  assertEquals: (expected: any, actual: any, message?: string) => void;
  assertNotEquals: (expected: any, actual: any, message?: string) => void;
  assertTrue: (condition: boolean, message?: string) => void;
  assertFalse: (condition: boolean, message?: string) => void;
  assertNull: (value: any, message?: string) => void;
  assertNotNull: (value: any, message?: string) => void;
  assertContains: (collection: any[], item: any, message?: string) => void;
  
  // Groovy-style collection methods
  each: (collection: any[], closure: (item: any, index?: number) => void) => void;
  collect: (collection: any[], closure: (item: any) => any) => any[];
  find: (collection: any[], closure: (item: any) => boolean) => any;
  findAll: (collection: any[], closure: (item: any) => boolean) => any[];
  
  // Groovy-style string methods
  capitalize: (str: string) => string;
  reverse: (str: string) => string;
  
  // Console
  println: (...args: any[]) => void;
  print: (...args: any[]) => void;
  console: any;
}

export class GroovyScriptingService {
  private testResults: TestResult[] = [];
  private consoleLogs: string[] = [];
  private variables: Map<string, any> = new Map();
  private environmentVars: Map<string, any> = new Map();
  private globalVars: Map<string, any> = new Map();

  /**
   * Execute Groovy-style test script
   */
  executeGroovyScript(
    script: string,
    response: Response,
    requestData: {
      url: string;
      method: string;
      headers: Record<string, string>;
      body?: any;
    }
  ): {
    success: boolean;
    error?: string;
    testResults: TestResult[];
    consoleLogs: string[];
    variables: Map<string, any>;
  } {
    this.testResults = [];
    this.consoleLogs = [];

    try {
      const context = this.createGroovyContext(response, requestData);
      const vmContext = vm.createContext(context);
      
      vm.runInContext(script, vmContext, {
        timeout: 5000,
        displayErrors: true,
      });

      return {
        success: true,
        testResults: this.testResults,
        consoleLogs: this.consoleLogs,
        variables: this.variables,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message,
        testResults: this.testResults,
        consoleLogs: this.consoleLogs,
        variables: this.variables,
      };
    }
  }

  /**
   * Create Groovy-style context
   */
  private createGroovyContext(
    response: Response | null,
    requestData: {
      url: string;
      method: string;
      headers: Record<string, string>;
      body?: any;
    }
  ): GroovyContext {
    const self = this;

    // Groovy-style assert methods
    const assert = (condition: boolean, message?: string) => {
      if (!condition) {
        throw new Error(message || 'Assertion failed');
      }
    };

    const assertEquals = (expected: any, actual: any, message?: string) => {
      if (expected !== actual) {
        throw new Error(message || `Expected ${expected} but got ${actual}`);
      }
    };

    const assertNotEquals = (expected: any, actual: any, message?: string) => {
      if (expected === actual) {
        throw new Error(message || `Expected not to equal ${expected}`);
      }
    };

    const assertTrue = (condition: boolean, message?: string) => {
      if (condition !== true) {
        throw new Error(message || 'Expected true');
      }
    };

    const assertFalse = (condition: boolean, message?: string) => {
      if (condition !== false) {
        throw new Error(message || 'Expected false');
      }
    };

    const assertNull = (value: any, message?: string) => {
      if (value !== null) {
        throw new Error(message || 'Expected null');
      }
    };

    const assertNotNull = (value: any, message?: string) => {
      if (value === null || value === undefined) {
        throw new Error(message || 'Expected not null');
      }
    };

    const assertContains = (collection: any[], item: any, message?: string) => {
      if (!collection.includes(item)) {
        throw new Error(message || `Collection does not contain ${item}`);
      }
    };

    // Groovy-style collection methods
    const each = (collection: any[], closure: (item: any, index?: number) => void) => {
      collection.forEach((item, index) => closure(item, index));
    };

    const collect = (collection: any[], closure: (item: any) => any) => {
      return collection.map(closure);
    };

    const find = (collection: any[], closure: (item: any) => boolean) => {
      return collection.find(closure);
    };

    const findAll = (collection: any[], closure: (item: any) => boolean) => {
      return collection.filter(closure);
    };

    // Groovy-style string methods
    const capitalize = (str: string) => {
      return str.charAt(0).toUpperCase() + str.slice(1);
    };

    const reverse = (str: string) => {
      return str.split('').reverse().join('');
    };

    // Console methods
    const println = (...args: any[]) => {
      self.consoleLogs.push(args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
      ).join(' '));
    };

    const print = (...args: any[]) => {
      self.consoleLogs.push(args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
      ).join(' '));
    };

    return {
      pm: {
        test: (name: string, closure: () => void) => {
          try {
            closure();
            self.testResults.push({ name, passed: true });
          } catch (error: any) {
            self.testResults.push({
              name,
              passed: false,
              error: error.message,
            });
          }
        },
        expect: (value: any) => ({
          toBe: (expected: any) => assertEquals(expected, value),
          toEqual: (expected: any) => assertEquals(expected, value),
          toBeGreaterThan: (expected: number) => {
            if (value <= expected) throw new Error(`Expected ${value} > ${expected}`);
          },
          toBeLessThan: (expected: number) => {
            if (value >= expected) throw new Error(`Expected ${value} < ${expected}`);
          },
          toContain: (item: any) => {
            if (!value.includes(item)) throw new Error(`Expected to contain ${item}`);
          },
          toBeNull: () => assertNull(value),
          toBeUndefined: () => {
            if (value !== undefined) throw new Error('Expected undefined');
          },
        }),
        response: {
          status: response?.status || 0,
          statusText: response?.statusText || '',
          headers: response?.headers || {},
          body: response?.body,
          time: response?.time || 0,
          size: response?.size || 0,
          json: () => {
            if (!response?.body) return null;
            if (typeof response.body === 'string') {
              try {
                return JSON.parse(response.body);
              } catch {
                return null;
              }
            }
            return response.body;
          },
          text: () => {
            if (!response?.body) return '';
            if (typeof response.body === 'string') return response.body;
            return JSON.stringify(response.body);
          },
        },
        variables: {
          get: (key: string) => self.variables.get(key),
          set: (key: string, value: any) => self.variables.set(key, value),
        },
        environment: {
          get: (key: string) => self.environmentVars.get(key),
          set: (key: string, value: any) => self.environmentVars.set(key, value),
        },
        globals: {
          get: (key: string) => self.globalVars.get(key),
          set: (key: string, value: any) => self.globalVars.set(key, value),
        },
        request: {
          url: requestData.url,
          method: requestData.method,
          headers: requestData.headers,
          body: requestData.body,
        },
        jsonPath: (obj: any, path: string) => {
          try {
            return jsonpath.query(obj, path);
          } catch (error: any) {
            self.consoleLogs.push(`[ERROR] JSONPath query failed: ${error.message}`);
            return [];
          }
        },
        extractJson: (path: string, varName?: string) => {
          try {
            const jsonData = response?.body;
            if (!jsonData) {
              throw new Error('No response body available');
            }

            const parsedData = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData;
            const results = jsonpath.query(parsedData, path);

            if (results.length === 0) {
              self.consoleLogs.push(`[WARN] JSONPath '${path}' returned no results`);
              return null;
            }

            const value = results.length === 1 ? results[0] : results;

            if (varName) {
              self.variables.set(varName, value);
              self.consoleLogs.push(`Extracted and saved to variable '${varName}': ${JSON.stringify(value)}`);
            }

            return value;
          } catch (error: any) {
            self.consoleLogs.push(`[ERROR] JSON extraction failed: ${error.message}`);
            return null;
          }
        },
      },
      assert,
      assertEquals,
      assertNotEquals,
      assertTrue,
      assertFalse,
      assertNull,
      assertNotNull,
      assertContains,
      each,
      collect,
      find,
      findAll,
      capitalize,
      reverse,
      println,
      print,
      console: {
        log: println,
        error: (...args: any[]) => {
          self.consoleLogs.push('[ERROR] ' + args.map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
          ).join(' '));
        },
        warn: (...args: any[]) => {
          self.consoleLogs.push('[WARN] ' + args.map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
          ).join(' '));
        },
      },
    };
  }

  /**
   * Set variables
   */
  setVariables(vars: Map<string, any>) {
    this.variables = new Map(vars);
  }

  setEnvironmentVariables(vars: Map<string, any>) {
    this.environmentVars = new Map(vars);
  }

  setGlobalVariables(vars: Map<string, any>) {
    this.globalVars = new Map(vars);
  }

  getVariables(): Map<string, any> {
    return this.variables;
  }

  getEnvironmentVariables(): Map<string, any> {
    return this.environmentVars;
  }

  getGlobalVariables(): Map<string, any> {
    return this.globalVars;
  }
}
