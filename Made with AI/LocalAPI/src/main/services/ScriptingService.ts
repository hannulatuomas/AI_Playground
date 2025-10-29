// Scripting Service with Node VM
import vm from 'vm';
import jsonpath from 'jsonpath';
import { getGlobalConsoleService } from '../ipc/handlers';
import type { Response } from '../../types/models';

interface TestResult {
  name: string;
  passed: boolean;
  error?: string;
}

interface ScriptContext {
  pm: {
    test: (name: string, fn: () => void) => void;
    expect: (value: any) => any;
    response: {
      code: number;
      status: string;
      headers: Record<string, string>;
      json: () => any;
      text: () => string;
      responseTime: number;
      responseSize: number;
    };
    variables: {
      get: (key: string) => any;
      set: (key: string, value: any) => void;
    };
    environment: {
      get: (key: string) => any;
      set: (key: string, value: any) => void;
    };
    globals: {
      get: (key: string) => any;
      set: (key: string, value: any) => void;
    };
    request: {
      url: string;
      method: string;
      headers: Record<string, string>;
      body?: any;
    };
    jsonPath: (obj: any, path: string) => any[];
    extractJson: (path: string, varName?: string) => any;
  };
  console: {
    log: (...args: any[]) => void;
    error: (...args: any[]) => void;
    warn: (...args: any[]) => void;
  };
}

export class ScriptingService {
  private testResults: TestResult[] = [];
  private consoleLogs: string[] = [];
  private variables: Map<string, any> = new Map();
  private environmentVars: Map<string, any> = new Map();
  private globalVars: Map<string, any> = new Map();

  /**
   * Execute a pre-request script
   */
  executePreRequestScript(
    script: string,
    requestData: {
      url: string;
      method: string;
      headers: Record<string, string>;
      body?: any;
    }
  ): { success: boolean; error?: string; variables: Map<string, any> } {
    this.testResults = [];
    this.consoleLogs = [];

    try {
      const context = this.createContext(null, requestData);
      const vmContext = vm.createContext(context);
      
      vm.runInContext(script, vmContext, {
        timeout: 5000,
        displayErrors: true,
      });

      return {
        success: true,
        variables: this.variables,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message,
        variables: this.variables,
      };
    }
  }

  /**
   * Execute a test script
   */
  executeTestScript(
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
      const context = this.createContext(response, requestData);
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
   * Create the script execution context with pm API
   */
  private createContext(
    response: Response | null,
    requestData: {
      url: string;
      method: string;
      headers: Record<string, string>;
      body?: any;
    }
  ): ScriptContext {
    const self = this;

    // Chai-like expect implementation
    const createExpect = (value: any) => {
      return {
        to: {
          equal: (expected: any) => {
            if (value !== expected) {
              throw new Error(`Expected ${value} to equal ${expected}`);
            }
          },
          eql: (expected: any) => {
            if (JSON.stringify(value) !== JSON.stringify(expected)) {
              throw new Error(`Expected ${JSON.stringify(value)} to deep equal ${JSON.stringify(expected)}`);
            }
          },
          be: {
            a: (type: string) => {
              const actualType = Array.isArray(value) ? 'array' : typeof value;
              if (actualType !== type.toLowerCase()) {
                throw new Error(`Expected ${value} to be a ${type}`);
              }
            },
            an: (type: string) => {
              const actualType = Array.isArray(value) ? 'array' : typeof value;
              if (actualType !== type.toLowerCase()) {
                throw new Error(`Expected ${value} to be an ${type}`);
              }
            },
            true: () => {
              if (value !== true) {
                throw new Error(`Expected ${value} to be true`);
              }
            },
            false: () => {
              if (value !== false) {
                throw new Error(`Expected ${value} to be false`);
              }
            },
            null: () => {
              if (value !== null) {
                throw new Error(`Expected ${value} to be null`);
              }
            },
            undefined: () => {
              if (value !== undefined) {
                throw new Error(`Expected ${value} to be undefined`);
              }
            },
            above: (num: number) => {
              if (value <= num) {
                throw new Error(`Expected ${value} to be above ${num}`);
              }
            },
            below: (num: number) => {
              if (value >= num) {
                throw new Error(`Expected ${value} to be below ${num}`);
              }
            },
            greaterThan: (num: number) => {
              if (value <= num) {
                throw new Error(`Expected ${value} to be greater than ${num}`);
              }
            },
            lessThan: (num: number) => {
              if (value >= num) {
                throw new Error(`Expected ${value} to be less than ${num}`);
              }
            },
          },
          have: {
            property: (prop: string, val?: any) => {
              if (!value || typeof value !== 'object' || !(prop in value)) {
                throw new Error(`Expected object to have property ${prop}`);
              }
              if (val !== undefined && value[prop] !== val) {
                throw new Error(`Expected property ${prop} to equal ${val}`);
              }
            },
            length: (len: number) => {
              if (!value || !('length' in value) || value.length !== len) {
                throw new Error(`Expected length to be ${len}`);
              }
            },
          },
          include: (item: any) => {
            if (Array.isArray(value)) {
              if (!value.includes(item)) {
                throw new Error(`Expected array to include ${item}`);
              }
            } else if (typeof value === 'string') {
              if (!value.includes(item)) {
                throw new Error(`Expected string to include ${item}`);
              }
            }
          },
          match: (pattern: RegExp) => {
            if (typeof value !== 'string' || !pattern.test(value)) {
              throw new Error(`Expected ${value} to match ${pattern}`);
            }
          },
        },
        not: {
          to: {
            equal: (expected: any) => {
              if (value === expected) {
                throw new Error(`Expected ${value} not to equal ${expected}`);
              }
            },
            be: {
              null: () => {
                if (value === null) {
                  throw new Error(`Expected ${value} not to be null`);
                }
              },
              undefined: () => {
                if (value === undefined) {
                  throw new Error(`Expected ${value} not to be undefined`);
                }
              },
            },
          },
        },
      };
    };

    return {
      pm: {
        test: (name: string, fn: () => void) => {
          try {
            fn();
            self.testResults.push({ name, passed: true });
          } catch (error: any) {
            self.testResults.push({
              name,
              passed: false,
              error: error.message,
            });
          }
        },
        expect: createExpect,
        response: {
          code: response?.status || 0,
          status: response?.statusText || '',
          headers: response?.headers || {},
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
          responseTime: response?.time || 0,
          responseSize: response?.size || 0,
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

            // Auto-save to variable if name provided
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
      console: {
        log: (...args: any[]) => {
          const output = args.map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
          ).join(' ');
          self.consoleLogs.push(output);
          
          // Log to global console service
          const consoleService = getGlobalConsoleService();
          consoleService?.logScriptOutput(output, 'log');
        },
        error: (...args: any[]) => {
          const output = '[ERROR] ' + args.map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
          ).join(' ');
          self.consoleLogs.push(output);
          
          // Log to global console service
          const consoleService = getGlobalConsoleService();
          consoleService?.logScriptOutput(output, 'error');
        },
        warn: (...args: any[]) => {
          const output = '[WARN] ' + args.map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
          ).join(' ');
          self.consoleLogs.push(output);
          
          // Log to global console service
          const consoleService = getGlobalConsoleService();
          consoleService?.logScriptOutput(output, 'warn');
        },
      },
    };
  }

  /**
   * Set initial variables from database
   */
  setVariables(vars: Map<string, any>) {
    this.variables = new Map(vars);
  }

  /**
   * Set environment variables
   */
  setEnvironmentVariables(vars: Map<string, any>) {
    this.environmentVars = new Map(vars);
  }

  /**
   * Set global variables
   */
  setGlobalVariables(vars: Map<string, any>) {
    this.globalVars = new Map(vars);
  }

  /**
   * Get updated variables after script execution
   */
  getVariables(): Map<string, any> {
    return this.variables;
  }

  /**
   * Get environment variables
   */
  getEnvironmentVariables(): Map<string, any> {
    return this.environmentVars;
  }

  /**
   * Get global variables
   */
  getGlobalVariables(): Map<string, any> {
    return this.globalVars;
  }
}
