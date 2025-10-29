// Data-Driven Service
// Parses CSV/JSON/XML data and runs requests with iterations

import * as Papa from 'papaparse';
import { parseString } from 'xml2js';

export interface DataSet {
  id: string;
  name: string;
  format: 'csv' | 'json' | 'xml';
  data: any[];
  columns: string[];
  rowCount: number;
  createdAt: Date;
}

export interface DataDrivenRun {
  id: string;
  name: string;
  dataSetId: string;
  requestTemplate: {
    method: string;
    url: string;
    headers?: Record<string, string>;
    body?: any;
  };
  iterations: IterationResult[];
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  startTime: Date;
  endTime?: Date;
  duration?: number;
  totalIterations: number;
  successCount: number;
  failedCount: number;
}

export interface IterationResult {
  id: string;
  index: number;
  data: Record<string, any>;
  status: 'success' | 'failed';
  response?: {
    status: number;
    statusText: string;
    time: number;
    body?: any;
  };
  error?: string;
}

export class DataDrivenService {
  private dataSets: Map<string, DataSet> = new Map();
  private runs: Map<string, DataDrivenRun> = new Map();

  /**
   * Parse CSV data
   */
  async parseCSV(content: string, name: string): Promise<string> {
    return new Promise((resolve, reject) => {
      Papa.parse(content, {
        header: true,
        skipEmptyLines: true,
        complete: (results) => {
          if (results.errors.length > 0) {
            reject(new Error(`CSV parsing errors: ${results.errors[0].message}`));
            return;
          }

          const dataSetId = this.generateId();
          const columns = results.meta.fields || [];

          const dataSet: DataSet = {
            id: dataSetId,
            name,
            format: 'csv',
            data: results.data as any[],
            columns,
            rowCount: results.data.length,
            createdAt: new Date(),
          };

          this.dataSets.set(dataSetId, dataSet);
          resolve(dataSetId);
        },
        error: (error: Error) => {
          reject(error);
        },
      });
    });
  }

  /**
   * Parse JSON data
   */
  async parseJSON(content: string, name: string): Promise<string> {
    try {
      const parsed = JSON.parse(content);
      
      // Handle both array and object with array property
      let data: any[];
      if (Array.isArray(parsed)) {
        data = parsed;
      } else if (parsed.data && Array.isArray(parsed.data)) {
        data = parsed.data;
      } else {
        throw new Error('JSON must be an array or contain a "data" array property');
      }

      if (data.length === 0) {
        throw new Error('JSON data is empty');
      }

      // Extract columns from first object
      const columns = Object.keys(data[0]);

      const dataSetId = this.generateId();
      const dataSet: DataSet = {
        id: dataSetId,
        name,
        format: 'json',
        data,
        columns,
        rowCount: data.length,
        createdAt: new Date(),
      };

      this.dataSets.set(dataSetId, dataSet);
      return dataSetId;
    } catch (error: any) {
      throw new Error(`JSON parsing error: ${error.message}`);
    }
  }

  /**
   * Parse XML data
   */
  async parseXML(content: string, name: string): Promise<string> {
    return new Promise((resolve, reject) => {
      parseString(content, { explicitArray: false }, (error, result) => {
        if (error) {
          reject(new Error(`XML parsing error: ${error.message}`));
          return;
        }

        try {
          // Try to find array data in XML
          let data: any[] = [];
          
          // Common patterns: <root><item>...</item><item>...</item></root>
          const root = result[Object.keys(result)[0]];
          
          if (root.item) {
            data = Array.isArray(root.item) ? root.item : [root.item];
          } else if (root.row) {
            data = Array.isArray(root.row) ? root.row : [root.row];
          } else if (root.record) {
            data = Array.isArray(root.record) ? root.record : [root.record];
          } else {
            // Try to find any array in the root
            for (const key of Object.keys(root)) {
              if (Array.isArray(root[key])) {
                data = root[key];
                break;
              }
            }
          }

          if (data.length === 0) {
            reject(new Error('No array data found in XML'));
            return;
          }

          // Extract columns
          const columns = Object.keys(data[0]);

          const dataSetId = this.generateId();
          const dataSet: DataSet = {
            id: dataSetId,
            name,
            format: 'xml',
            data,
            columns,
            rowCount: data.length,
            createdAt: new Date(),
          };

          this.dataSets.set(dataSetId, dataSet);
          resolve(dataSetId);
        } catch (error: any) {
          reject(new Error(`XML data extraction error: ${error.message}`));
        }
      });
    });
  }

  /**
   * Run data-driven test
   */
  async runDataDriven(options: {
    name: string;
    dataSetId: string;
    requestTemplate: {
      method: string;
      url: string;
      headers?: Record<string, string>;
      body?: any;
    };
    delay?: number;
  }): Promise<DataDrivenRun> {
    const dataSet = this.dataSets.get(options.dataSetId);
    if (!dataSet) {
      throw new Error('Data set not found');
    }

    const runId = this.generateId();
    const run: DataDrivenRun = {
      id: runId,
      name: options.name,
      dataSetId: options.dataSetId,
      requestTemplate: options.requestTemplate,
      iterations: [],
      status: 'running',
      startTime: new Date(),
      totalIterations: dataSet.rowCount,
      successCount: 0,
      failedCount: 0,
    };

    this.runs.set(runId, run);

    try {
      for (let i = 0; i < dataSet.data.length; i++) {
        const rowData = dataSet.data[i];

        // Execute iteration
        const result = await this.executeIteration(
          i,
          rowData,
          options.requestTemplate
        );

        run.iterations.push(result);

        if (result.status === 'success') {
          run.successCount++;
        } else {
          run.failedCount++;
        }

        // Apply delay
        if (options.delay && i < dataSet.data.length - 1) {
          await this.sleep(options.delay);
        }
      }

      run.status = 'completed';
    } catch (error: any) {
      run.status = 'failed';
    }

    run.endTime = new Date();
    run.duration = run.endTime.getTime() - run.startTime.getTime();

    return run;
  }

  /**
   * Execute single iteration
   */
  private async executeIteration(
    index: number,
    data: Record<string, any>,
    template: {
      method: string;
      url: string;
      headers?: Record<string, string>;
      body?: any;
    }
  ): Promise<IterationResult> {
    const result: IterationResult = {
      id: this.generateId(),
      index,
      data,
      status: 'success',
    };

    try {
      // Resolve variables in template
      const resolvedUrl = this.resolveVariables(template.url, data);
      const resolvedHeaders = this.resolveObjectVariables(template.headers || {}, data);
      const resolvedBody = this.resolveObjectVariables(template.body, data);

      // Make request
      const response = await this.makeRequest({
        method: template.method,
        url: resolvedUrl,
        headers: resolvedHeaders,
        body: resolvedBody,
      });

      result.response = response;
      result.status = response.status >= 200 && response.status < 300 ? 'success' : 'failed';
    } catch (error: any) {
      result.status = 'failed';
      result.error = error.message;
    }

    return result;
  }

  /**
   * Resolve variables in string
   */
  private resolveVariables(str: string, data: Record<string, any>): string {
    if (!str) return str;

    return str.replace(/\{\{([^}]+)\}\}/g, (match, varName) => {
      const trimmed = varName.trim();
      return data[trimmed] !== undefined ? String(data[trimmed]) : match;
    });
  }

  /**
   * Resolve variables in object
   */
  private resolveObjectVariables(obj: any, data: Record<string, any>): any {
    if (!obj) return obj;

    if (typeof obj === 'string') {
      return this.resolveVariables(obj, data);
    }

    if (Array.isArray(obj)) {
      return obj.map(item => this.resolveObjectVariables(item, data));
    }

    if (typeof obj === 'object') {
      const resolved: any = {};
      for (const [key, value] of Object.entries(obj)) {
        resolved[key] = this.resolveObjectVariables(value, data);
      }
      return resolved;
    }

    return obj;
  }

  /**
   * Make HTTP request (placeholder)
   */
  private async makeRequest(params: {
    method: string;
    url: string;
    headers?: Record<string, string>;
    body?: any;
  }): Promise<{
    status: number;
    statusText: string;
    time: number;
    body?: any;
  }> {
    // Placeholder - integrate with RequestService
    const startTime = Date.now();
    await this.sleep(100);

    return {
      status: 200,
      statusText: 'OK',
      time: Date.now() - startTime,
      body: { success: true },
    };
  }

  /**
   * Sleep utility
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get data set
   */
  getDataSet(dataSetId: string): DataSet | null {
    return this.dataSets.get(dataSetId) || null;
  }

  /**
   * Get all data sets
   */
  getAllDataSets(): DataSet[] {
    return Array.from(this.dataSets.values());
  }

  /**
   * Delete data set
   */
  deleteDataSet(dataSetId: string): boolean {
    return this.dataSets.delete(dataSetId);
  }

  /**
   * Get run
   */
  getRun(runId: string): DataDrivenRun | null {
    return this.runs.get(runId) || null;
  }

  /**
   * Get all runs
   */
  getAllRuns(): DataDrivenRun[] {
    return Array.from(this.runs.values());
  }

  /**
   * Delete run
   */
  deleteRun(runId: string): boolean {
    return this.runs.delete(runId);
  }

  /**
   * Export run results
   */
  exportResults(runId: string, format: 'json' | 'csv'): string {
    const run = this.runs.get(runId);
    if (!run) return '';

    if (format === 'json') {
      return JSON.stringify(run, null, 2);
    } else {
      // CSV format
      const lines: string[] = [];
      lines.push('Index,Status,Response Time,Status Code,Error');

      for (const iteration of run.iterations) {
        lines.push([
          iteration.index,
          iteration.status,
          iteration.response?.time || '',
          iteration.response?.status || '',
          iteration.error || '',
        ].join(','));
      }

      return lines.join('\n');
    }
  }

  /**
   * Get run statistics
   */
  getRunStatistics(runId: string): {
    totalIterations: number;
    successCount: number;
    failedCount: number;
    successRate: number;
    averageResponseTime: number;
    minResponseTime: number;
    maxResponseTime: number;
  } | null {
    const run = this.runs.get(runId);
    if (!run) return null;

    const times = run.iterations
      .filter(i => i.response?.time)
      .map(i => i.response!.time);

    const averageResponseTime = times.length > 0
      ? times.reduce((sum, t) => sum + t, 0) / times.length
      : 0;

    const minResponseTime = times.length > 0 ? Math.min(...times) : 0;
    const maxResponseTime = times.length > 0 ? Math.max(...times) : 0;
    const successRate = run.totalIterations > 0
      ? (run.successCount / run.totalIterations) * 100
      : 0;

    return {
      totalIterations: run.totalIterations,
      successCount: run.successCount,
      failedCount: run.failedCount,
      successRate,
      averageResponseTime,
      minResponseTime,
      maxResponseTime,
    };
  }

  /**
   * Preview data set
   */
  previewDataSet(dataSetId: string, limit: number = 10): any[] {
    const dataSet = this.dataSets.get(dataSetId);
    if (!dataSet) return [];

    return dataSet.data.slice(0, limit);
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Singleton instance
let dataDrivenServiceInstance: DataDrivenService | null = null;

export function getDataDrivenService(): DataDrivenService {
  if (!dataDrivenServiceInstance) {
    dataDrivenServiceInstance = new DataDrivenService();
  }
  return dataDrivenServiceInstance;
}
