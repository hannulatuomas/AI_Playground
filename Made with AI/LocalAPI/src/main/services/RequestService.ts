// HTTP Request Service using Axios
import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import type { Request, Response, Header, QueryParam } from '../../types/models';
import { ScriptingService } from './ScriptingService';
import { CacheService, CacheOptions } from './CacheService';
import { getGlobalConsoleService } from '../ipc/handlers';

export interface RequestOptions {
  timeout?: number; // Request timeout in milliseconds
  cache?: boolean; // Enable caching for this request
  cacheTTL?: number; // Cache TTL in milliseconds
  cacheTags?: string[]; // Cache tags for invalidation
}

export class RequestService {
  private scriptingService: ScriptingService;
  private cacheService: CacheService;
  private defaultTimeout: number;

  constructor() {
    this.scriptingService = new ScriptingService();
    this.cacheService = new CacheService({
      ttl: 5 * 60 * 1000, // 5 minutes default
      maxSize: 50, // 50MB
      enabled: true,
    });
    this.defaultTimeout = 30000; // 30 seconds default
  }
  /**
   * Send HTTP request
   */
  async sendRequest(
    request: Request,
    variables: Record<string, any> = {},
    options: RequestOptions = {}
  ): Promise<Response & { testResults?: any[]; consoleLogs?: string[]; cached?: boolean }> {
    const startTime = Date.now();

    try {
      // Check cache for GET requests if caching is enabled
      const shouldCache = options.cache !== false && request.method === 'GET';
      
      if (shouldCache) {
        const cacheKey = this.cacheService.generateKey(
          request.url,
          request.method,
          this.buildParamsObject(request.queryParams),
          this.buildHeadersObject(request.headers),
          request.body?.content
        );

        const cachedResponse = this.cacheService.get<Response>(cacheKey);
        if (cachedResponse) {
          console.log('Cache hit for request:', request.url);
          return { ...cachedResponse, cached: true };
        }
      }
      // Execute pre-request script if present
      if (request.preRequestScript) {
        const preRequestResult = this.scriptingService.executePreRequestScript(
          request.preRequestScript,
          {
            url: request.url,
            method: request.method,
            headers: this.buildHeadersObject(request.headers),
            body: request.body?.content,
          }
        );

        if (!preRequestResult.success) {
          console.error('Pre-request script error:', preRequestResult.error);
        }

        // Merge script variables with existing variables
        preRequestResult.variables.forEach((value, key) => {
          variables[key] = value;
        });
      }

      // Resolve variables in URL
      const resolvedUrl = this.resolveVariables(request.url, variables);

      // Build headers
      const headers: Record<string, string> = {};
      request.headers
        .filter(h => h.enabled)
        .forEach(h => {
          headers[h.key] = this.resolveVariables(h.value, variables);
        });

      // Build query params
      const params: Record<string, string> = {};
      request.queryParams
        .filter(p => p.enabled)
        .forEach(p => {
          params[p.key] = this.resolveVariables(p.value, variables);
        });

      // Add authentication
      this.addAuthentication(request, headers, variables);

      // Build request body
      let data: any = undefined;
      if (request.body && request.body.type !== 'none') {
        data = this.buildRequestBody(request.body, variables);
      }

      // Configure axios request
      const timeout = options.timeout || this.defaultTimeout;
      const config: AxiosRequestConfig = {
        method: request.method.toLowerCase() as any,
        url: resolvedUrl,
        headers,
        params,
        data,
        timeout,
        validateStatus: () => true, // Accept all status codes
        maxRedirects: 5,
      };

      // Log request to console
      const consoleService = getGlobalConsoleService();
      const requestId = consoleService?.logRequest({
        method: request.method,
        url: resolvedUrl,
        headers,
        body: data,
      }, {
        protocol: 'HTTP/1.1',
      })?.id;

      // Send request
      const axiosResponse: AxiosResponse = await axios(config);
      const endTime = Date.now();

      // Build response object
      const response: Response = {
        status: axiosResponse.status,
        statusText: axiosResponse.statusText,
        headers: axiosResponse.headers as Record<string, string>,
        body: axiosResponse.data,
        time: endTime - startTime,
        size: this.calculateSize(axiosResponse.data),
        timestamp: new Date(),
      };

      // Log response to console
      consoleService?.logResponse({
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
        body: response.body,
      }, {
        method: request.method,
        url: resolvedUrl,
      }, {
        requestId,
        duration: endTime - startTime,
        cached: false,
        protocol: 'HTTP/1.1',
      });

      // Cache response if enabled and successful
      if (shouldCache && response.status >= 200 && response.status < 300) {
        const cacheKey = this.cacheService.generateKey(
          request.url,
          request.method,
          this.buildParamsObject(request.queryParams),
          this.buildHeadersObject(request.headers),
          request.body?.content
        );

        const cacheTags = options.cacheTags || [`url:${request.url}`];
        this.cacheService.set(cacheKey, response, {
          ttl: options.cacheTTL,
          tags: cacheTags,
        });
      }

      // Execute test script if present
      let testResults: any[] = [];
      let consoleLogs: string[] = [];

      if (request.testScript) {
        const testResult = this.scriptingService.executeTestScript(
          request.testScript,
          response,
          {
            url: request.url,
            method: request.method,
            headers: this.buildHeadersObject(request.headers),
            body: request.body?.content,
          }
        );

        testResults = testResult.testResults;
        consoleLogs = testResult.consoleLogs;

        if (!testResult.success) {
          console.error('Test script error:', testResult.error);
        }
      }

      return { ...response, testResults, consoleLogs, cached: false };
    } catch (error) {
      const endTime = Date.now();

      // Log error to console
      const consoleService = getGlobalConsoleService();
      consoleService?.logError(error as Error, {
        url: request.url,
        method: request.method,
      });

      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError;

        if (axiosError.response) {
          // Server responded with error status
          return {
            status: axiosError.response.status,
            statusText: axiosError.response.statusText,
            headers: axiosError.response.headers as Record<string, string>,
            body: axiosError.response.data,
            time: endTime - startTime,
            size: this.calculateSize(axiosError.response.data),
            timestamp: new Date(),
          };
        } else if (axiosError.request) {
          // Request made but no response
          throw new Error(`Network Error: ${axiosError.message}`);
        }
      }

      throw error;
    }
  }

  /**
   * Resolve variables in string
   */
  private resolveVariables(str: string, variables: Record<string, any>): string {
    return str.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      return variables[key] !== undefined ? String(variables[key]) : match;
    });
  }

  /**
   * Add authentication to headers
   */
  private addAuthentication(
    request: Request,
    headers: Record<string, string>,
    variables: Record<string, any>
  ): void {
    if (!request.auth || request.auth.type === 'none') return;

    switch (request.auth.type) {
      case 'basic':
        if (request.auth.basic) {
          const username = this.resolveVariables(request.auth.basic.username, variables);
          const password = this.resolveVariables(request.auth.basic.password, variables);
          const encoded = Buffer.from(`${username}:${password}`).toString('base64');
          headers['Authorization'] = `Basic ${encoded}`;
        }
        break;

      case 'bearer':
        if (request.auth.bearer) {
          const token = this.resolveVariables(request.auth.bearer.token, variables);
          headers['Authorization'] = `Bearer ${token}`;
        }
        break;

      case 'apikey':
        if (request.auth.apikey) {
          const key = this.resolveVariables(request.auth.apikey.key, variables);
          const value = this.resolveVariables(request.auth.apikey.value, variables);
          if (request.auth.apikey.addTo === 'header') {
            headers[key] = value;
          }
          // Query params handled separately
        }
        break;

      case 'digest':
        // Digest auth is handled by axios automatically
        break;
    }
  }

  /**
   * Build request body based on type
   */
  private buildRequestBody(body: any, variables: Record<string, any>): any {
    if (!body || !body.content) return undefined;

    const resolvedContent = this.resolveVariables(body.content, variables);

    switch (body.type) {
      case 'json':
        try {
          return JSON.parse(resolvedContent);
        } catch {
          return resolvedContent;
        }

      case 'xml':
      case 'raw':
        return resolvedContent;

      case 'form-data':
        // FormData would be handled differently in browser context
        return body.formData || {};

      case 'x-www-form-urlencoded':
        const params = new URLSearchParams();
        try {
          const data = JSON.parse(resolvedContent);
          Object.entries(data).forEach(([key, value]) => {
            params.append(key, String(value));
          });
          return params;
        } catch {
          return resolvedContent;
        }

      default:
        return resolvedContent;
    }
  }

  /**
   * Calculate response size
   */
  private calculateSize(data: any): number {
    if (!data) return 0;

    if (typeof data === 'string') {
      return new Blob([data]).size;
    }

    try {
      return new Blob([JSON.stringify(data)]).size;
    } catch {
      return 0;
    }
  }

  /**
   * Build headers object from headers array
   */
  private buildHeadersObject(headers: Header[]): Record<string, string> {
    const headersObj: Record<string, string> = {};
    headers
      .filter(h => h.enabled)
      .forEach(h => {
        headersObj[h.key] = h.value;
      });
    return headersObj;
  }

  /**
   * Build params object from query params array
   */
  private buildParamsObject(params: QueryParam[]): Record<string, string> {
    const paramsObj: Record<string, string> = {};
    params
      .filter(p => p.enabled)
      .forEach(p => {
        paramsObj[p.key] = p.value;
      });
    return paramsObj;
  }

  /**
   * Get cache service instance
   */
  getCacheService(): CacheService {
    return this.cacheService;
  }

  /**
   * Set default timeout
   */
  setDefaultTimeout(timeout: number): void {
    this.defaultTimeout = timeout;
  }

  /**
   * Get default timeout
   */
  getDefaultTimeout(): number {
    return this.defaultTimeout;
  }

  /**
   * Clear request cache
   */
  clearCache(): void {
    this.cacheService.clear();
  }

  /**
   * Invalidate cache by tags
   */
  invalidateCacheByTags(tags: string[]): number {
    return this.cacheService.invalidateByTags(tags);
  }

  /**
   * Invalidate cache by URL pattern
   */
  invalidateCacheByPattern(pattern: RegExp): number {
    return this.cacheService.invalidateByPattern(pattern);
  }

  /**
   * Get cache statistics
   */
  getCacheStats() {
    return this.cacheService.getStats();
  }
}

// Singleton instance
let requestServiceInstance: RequestService | null = null;

export function getRequestService(): RequestService {
  if (!requestServiceInstance) {
    requestServiceInstance = new RequestService();
  }
  return requestServiceInstance;
}
