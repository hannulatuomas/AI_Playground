// Batch Runner Service
// Executes multiple requests in sequence with variable extraction

export interface BatchRequest {
  id: string;
  name: string;
  method: string;
  url: string;
  headers?: Record<string, string>;
  body?: any;
  auth?: any;
  preRequestScript?: string;
  testScript?: string;
  extractVariables?: VariableExtraction[];
  continueOnError?: boolean;
}

export interface VariableExtraction {
  name: string;
  source: 'body' | 'headers' | 'status';
  path?: string; // JSONPath for body extraction
  headerName?: string;
}

export interface BatchResult {
  id: string;
  requestId: string;
  requestName: string;
  status: 'success' | 'failed' | 'skipped';
  response?: {
    status: number;
    statusText: string;
    headers: Record<string, string>;
    body: any;
    time: number;
  };
  error?: string;
  extractedVariables?: Record<string, any>;
  testResults?: {
    passed: number;
    failed: number;
    tests: Array<{ name: string; passed: boolean; error?: string }>;
  };
}

export interface BatchRunResult {
  id: string;
  name: string;
  startTime: Date;
  endTime?: Date;
  duration?: number;
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  results: BatchResult[];
  variables: Record<string, any>;
  totalRequests: number;
  successCount: number;
  failedCount: number;
  skippedCount: number;
}

export interface BatchRunOptions {
  name: string;
  requests: BatchRequest[];
  initialVariables?: Record<string, any>;
  stopOnError?: boolean;
  delay?: number; // Delay between requests in ms
}

export class BatchRunnerService {
  private activeRuns: Map<string, BatchRunResult> = new Map();

  /**
   * Execute batch of requests
   */
  async executeBatch(options: BatchRunOptions): Promise<BatchRunResult> {
    const runId = this.generateId();
    const startTime = new Date();

    const batchRun: BatchRunResult = {
      id: runId,
      name: options.name,
      startTime,
      status: 'running',
      results: [],
      variables: options.initialVariables ? { ...options.initialVariables } : {},
      totalRequests: options.requests.length,
      successCount: 0,
      failedCount: 0,
      skippedCount: 0,
    };

    this.activeRuns.set(runId, batchRun);

    try {
      for (let i = 0; i < options.requests.length; i++) {
        const request = options.requests[i];

        // Check if should skip due to previous error
        if (options.stopOnError && batchRun.failedCount > 0) {
          batchRun.results.push({
            id: this.generateId(),
            requestId: request.id,
            requestName: request.name,
            status: 'skipped',
          });
          batchRun.skippedCount++;
          continue;
        }

        // Execute request
        const result = await this.executeRequest(request, batchRun.variables);
        batchRun.results.push(result);

        // Update statistics
        if (result.status === 'success') {
          batchRun.successCount++;
        } else if (result.status === 'failed') {
          batchRun.failedCount++;
        } else {
          batchRun.skippedCount++;
        }

        // Extract variables from response
        if (result.extractedVariables) {
          Object.assign(batchRun.variables, result.extractedVariables);
        }

        // Apply delay before next request
        if (options.delay && i < options.requests.length - 1) {
          await this.sleep(options.delay);
        }
      }

      batchRun.status = batchRun.failedCount > 0 ? 'failed' : 'completed';
    } catch (error: any) {
      batchRun.status = 'failed';
    }

    batchRun.endTime = new Date();
    batchRun.duration = batchRun.endTime.getTime() - batchRun.startTime.getTime();

    return batchRun;
  }

  /**
   * Execute single request
   */
  private async executeRequest(
    request: BatchRequest,
    variables: Record<string, any>
  ): Promise<BatchResult> {
    const result: BatchResult = {
      id: this.generateId(),
      requestId: request.id,
      requestName: request.name,
      status: 'success',
    };

    try {
      // Resolve variables in URL, headers, and body
      const resolvedUrl = this.resolveVariables(request.url, variables);
      const resolvedHeaders = this.resolveObjectVariables(request.headers || {}, variables);
      const resolvedBody = this.resolveObjectVariables(request.body, variables);

      // Execute pre-request script
      if (request.preRequestScript) {
        await this.executeScript(request.preRequestScript, variables);
      }

      // Make HTTP request (placeholder - integrate with actual RequestService)
      const response = await this.makeRequest({
        method: request.method,
        url: resolvedUrl,
        headers: resolvedHeaders,
        body: resolvedBody,
        auth: request.auth,
      });

      result.response = response;

      // Extract variables
      if (request.extractVariables && request.extractVariables.length > 0) {
        result.extractedVariables = this.extractVariables(
          request.extractVariables,
          response
        );
      }

      // Execute test script
      if (request.testScript) {
        result.testResults = await this.executeTestScript(
          request.testScript,
          response,
          variables
        );

        if (result.testResults.failed > 0) {
          result.status = 'failed';
        }
      }
    } catch (error: any) {
      result.status = 'failed';
      result.error = error.message;
    }

    return result;
  }

  /**
   * Resolve variables in string
   */
  private resolveVariables(str: string, variables: Record<string, any>): string {
    if (!str) return str;

    return str.replace(/\{\{([^}]+)\}\}/g, (match, varName) => {
      const trimmed = varName.trim();
      return variables[trimmed] !== undefined ? String(variables[trimmed]) : match;
    });
  }

  /**
   * Resolve variables in object
   */
  private resolveObjectVariables(obj: any, variables: Record<string, any>): any {
    if (!obj) return obj;

    if (typeof obj === 'string') {
      return this.resolveVariables(obj, variables);
    }

    if (Array.isArray(obj)) {
      return obj.map(item => this.resolveObjectVariables(item, variables));
    }

    if (typeof obj === 'object') {
      const resolved: any = {};
      for (const [key, value] of Object.entries(obj)) {
        resolved[key] = this.resolveObjectVariables(value, variables);
      }
      return resolved;
    }

    return obj;
  }

  /**
   * Extract variables from response
   */
  private extractVariables(
    extractions: VariableExtraction[],
    response: any
  ): Record<string, any> {
    const extracted: Record<string, any> = {};

    for (const extraction of extractions) {
      try {
        let value: any;

        switch (extraction.source) {
          case 'body':
            if (extraction.path) {
              value = this.extractFromPath(response.body, extraction.path);
            } else {
              value = response.body;
            }
            break;

          case 'headers':
            if (extraction.headerName) {
              value = response.headers[extraction.headerName.toLowerCase()];
            }
            break;

          case 'status':
            value = response.status;
            break;
        }

        if (value !== undefined) {
          extracted[extraction.name] = value;
        }
      } catch (error) {
        // Skip failed extractions
      }
    }

    return extracted;
  }

  /**
   * Extract value from object using path (simple JSONPath)
   */
  private extractFromPath(obj: any, path: string): any {
    if (!path) return obj;

    const parts = path.split('.');
    let current = obj;

    for (const part of parts) {
      if (current === null || current === undefined) {
        return undefined;
      }

      // Handle array index
      const arrayMatch = part.match(/^(.+)\[(\d+)\]$/);
      if (arrayMatch) {
        const [, key, index] = arrayMatch;
        current = current[key];
        if (Array.isArray(current)) {
          current = current[parseInt(index)];
        }
      } else {
        current = current[part];
      }
    }

    return current;
  }

  /**
   * Execute pre-request script
   */
  private async executeScript(
    script: string,
    variables: Record<string, any>
  ): Promise<void> {
    // Placeholder - integrate with ScriptService
    // This would execute the script in a VM context with access to variables
  }

  /**
   * Execute test script
   */
  private async executeTestScript(
    script: string,
    response: any,
    variables: Record<string, any>
  ): Promise<{
    passed: number;
    failed: number;
    tests: Array<{ name: string; passed: boolean; error?: string }>;
  }> {
    // Placeholder - integrate with ScriptService
    // This would execute tests and return results
    return {
      passed: 0,
      failed: 0,
      tests: [],
    };
  }

  /**
   * Make HTTP request (placeholder)
   */
  private async makeRequest(params: {
    method: string;
    url: string;
    headers?: Record<string, string>;
    body?: any;
    auth?: any;
  }): Promise<{
    status: number;
    statusText: string;
    headers: Record<string, string>;
    body: any;
    time: number;
  }> {
    // Placeholder - integrate with RequestService
    const startTime = Date.now();

    // Simulate request
    await this.sleep(100);

    return {
      status: 200,
      statusText: 'OK',
      headers: { 'content-type': 'application/json' },
      body: { success: true },
      time: Date.now() - startTime,
    };
  }

  /**
   * Sleep utility
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get batch run status
   */
  getBatchRun(runId: string): BatchRunResult | null {
    return this.activeRuns.get(runId) || null;
  }

  /**
   * Get all batch runs
   */
  getAllBatchRuns(): BatchRunResult[] {
    return Array.from(this.activeRuns.values());
  }

  /**
   * Cancel batch run
   */
  cancelBatchRun(runId: string): boolean {
    const run = this.activeRuns.get(runId);
    if (run && run.status === 'running') {
      run.status = 'cancelled';
      run.endTime = new Date();
      run.duration = run.endTime.getTime() - run.startTime.getTime();
      return true;
    }
    return false;
  }

  /**
   * Delete batch run
   */
  deleteBatchRun(runId: string): boolean {
    return this.activeRuns.delete(runId);
  }

  /**
   * Generate batch from collection
   */
  generateBatchFromCollection(collection: any): BatchRequest[] {
    const requests: BatchRequest[] = [];

    const processItem = (item: any) => {
      if (item.type === 'request') {
        requests.push({
          id: item.id,
          name: item.name,
          method: item.method || 'GET',
          url: item.url,
          headers: item.headers,
          body: item.body,
          auth: item.auth,
          preRequestScript: item.preRequestScript,
          testScript: item.testScript,
          extractVariables: item.extractVariables,
          continueOnError: item.continueOnError !== false,
        });
      } else if (item.type === 'folder' && item.children) {
        item.children.forEach(processItem);
      }
    };

    if (collection.children) {
      collection.children.forEach(processItem);
    }

    return requests;
  }

  /**
   * Export batch run results
   */
  exportResults(runId: string, format: 'json' | 'csv'): string {
    const run = this.activeRuns.get(runId);
    if (!run) return '';

    if (format === 'json') {
      return JSON.stringify(run, null, 2);
    } else {
      // CSV format
      const lines: string[] = [];
      lines.push('Request,Status,Response Time,Status Code,Error');

      for (const result of run.results) {
        lines.push([
          result.requestName,
          result.status,
          result.response?.time || '',
          result.response?.status || '',
          result.error || '',
        ].join(','));
      }

      return lines.join('\n');
    }
  }

  /**
   * Get summary statistics
   */
  getSummary(runId: string): {
    totalRequests: number;
    successCount: number;
    failedCount: number;
    skippedCount: number;
    totalTime: number;
    averageTime: number;
  } | null {
    const run = this.activeRuns.get(runId);
    if (!run) return null;

    const totalTime = run.results.reduce((sum, r) => sum + (r.response?.time || 0), 0);
    const completedCount = run.successCount + run.failedCount;
    const averageTime = completedCount > 0 ? totalTime / completedCount : 0;

    return {
      totalRequests: run.totalRequests,
      successCount: run.successCount,
      failedCount: run.failedCount,
      skippedCount: run.skippedCount,
      totalTime,
      averageTime,
    };
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Singleton instance
let batchRunnerServiceInstance: BatchRunnerService | null = null;

export function getBatchRunnerService(): BatchRunnerService {
  if (!batchRunnerServiceInstance) {
    batchRunnerServiceInstance = new BatchRunnerService();
  }
  return batchRunnerServiceInstance;
}
