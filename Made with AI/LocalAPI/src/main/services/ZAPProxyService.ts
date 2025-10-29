/**
 * OWASP ZAP (Zed Attack Proxy) Integration Service
 * 
 * Integrates with OWASP ZAP for advanced security testing:
 * - Spider scanning (crawl target)
 * - Active scanning (automated attack)
 * - Passive scanning (analyze traffic)
 * - Alert retrieval and analysis
 * - Session management
 */

import axios, { AxiosInstance } from 'axios';

export interface ZAPConfig {
  apiKey: string;
  host?: string;
  port?: number;
}

export interface ZAPScanOptions {
  targetUrl: string;
  scanType: 'spider' | 'active' | 'passive' | 'full';
  contextName?: string;
  recurse?: boolean;
  maxChildren?: number;
  subtreeOnly?: boolean;
}

export interface ZAPScanResult {
  scanId: string;
  targetUrl: string;
  scanType: string;
  status: 'running' | 'completed' | 'failed';
  progress: number;
  alerts: ZAPAlert[];
  summary: {
    total: number;
    high: number;
    medium: number;
    low: number;
    informational: number;
  };
  duration?: number;
}

export interface ZAPAlert {
  id: string;
  alert: string;
  risk: 'High' | 'Medium' | 'Low' | 'Informational';
  confidence: 'High' | 'Medium' | 'Low';
  description: string;
  solution: string;
  reference: string;
  cweid: string;
  wascid: string;
  url: string;
  method?: string;
  param?: string;
  attack?: string;
  evidence?: string;
}

export class ZAPProxyService {
  private client: AxiosInstance;
  private apiKey: string;
  private baseUrl: string;

  constructor(config: ZAPConfig) {
    this.apiKey = config.apiKey;
    const host = config.host || 'localhost';
    const port = config.port || 8080;
    this.baseUrl = `http://${host}:${port}`;

    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: 300000, // 5 minutes for long-running scans
    });
  }

  /**
   * Check if ZAP is running and accessible
   */
  async checkConnection(): Promise<boolean> {
    try {
      const response = await this.client.get('/JSON/core/view/version/', {
        params: { apikey: this.apiKey },
      });
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get ZAP version
   */
  async getVersion(): Promise<string> {
    try {
      const response = await this.client.get('/JSON/core/view/version/', {
        params: { apikey: this.apiKey },
      });
      return response.data.version;
    } catch (error) {
      throw new Error('Failed to get ZAP version: ' + (error as Error).message);
    }
  }

  /**
   * Run a scan based on type
   */
  async runScan(options: ZAPScanOptions): Promise<ZAPScanResult> {
    const scanId = this.generateScanId();
    const startTime = Date.now();

    try {
      let spiderScanId: string | null = null;
      let activeScanId: string | null = null;

      // Spider scan (crawl)
      if (options.scanType === 'spider' || options.scanType === 'full') {
        spiderScanId = await this.startSpiderScan(options);
        await this.waitForSpiderComplete(spiderScanId);
      }

      // Active scan (attack)
      if (options.scanType === 'active' || options.scanType === 'full') {
        activeScanId = await this.startActiveScan(options);
        await this.waitForActiveScanComplete(activeScanId);
      }

      // Get alerts
      const alerts = await this.getAlerts(options.targetUrl);
      const duration = Date.now() - startTime;

      return {
        scanId,
        targetUrl: options.targetUrl,
        scanType: options.scanType,
        status: 'completed',
        progress: 100,
        alerts,
        summary: this.generateSummary(alerts),
        duration,
      };
    } catch (error) {
      throw new Error('ZAP scan failed: ' + (error as Error).message);
    }
  }

  /**
   * Start spider scan
   */
  private async startSpiderScan(options: ZAPScanOptions): Promise<string> {
    try {
      const params: any = {
        apikey: this.apiKey,
        url: options.targetUrl,
      };

      if (options.maxChildren) params.maxChildren = options.maxChildren;
      if (options.recurse !== undefined) params.recurse = options.recurse;
      if (options.subtreeOnly !== undefined) params.subtreeOnly = options.subtreeOnly;
      if (options.contextName) params.contextName = options.contextName;

      const response = await this.client.get('/JSON/spider/action/scan/', { params });
      return response.data.scan;
    } catch (error) {
      throw new Error('Failed to start spider scan: ' + (error as Error).message);
    }
  }

  /**
   * Wait for spider scan to complete
   */
  private async waitForSpiderComplete(scanId: string): Promise<void> {
    while (true) {
      const progress = await this.getSpiderProgress(scanId);
      if (progress >= 100) break;
      await new Promise(resolve => setTimeout(resolve, 2000)); // Check every 2 seconds
    }
  }

  /**
   * Get spider scan progress
   */
  private async getSpiderProgress(scanId: string): Promise<number> {
    try {
      const response = await this.client.get('/JSON/spider/view/status/', {
        params: {
          apikey: this.apiKey,
          scanId,
        },
      });
      return parseInt(response.data.status);
    } catch (error) {
      throw new Error('Failed to get spider progress: ' + (error as Error).message);
    }
  }

  /**
   * Start active scan
   */
  private async startActiveScan(options: ZAPScanOptions): Promise<string> {
    try {
      const params: any = {
        apikey: this.apiKey,
        url: options.targetUrl,
      };

      if (options.recurse !== undefined) params.recurse = options.recurse;
      if (options.contextName) params.contextName = options.contextName;

      const response = await this.client.get('/JSON/ascan/action/scan/', { params });
      return response.data.scan;
    } catch (error) {
      throw new Error('Failed to start active scan: ' + (error as Error).message);
    }
  }

  /**
   * Wait for active scan to complete
   */
  private async waitForActiveScanComplete(scanId: string): Promise<void> {
    while (true) {
      const progress = await this.getActiveScanProgress(scanId);
      if (progress >= 100) break;
      await new Promise(resolve => setTimeout(resolve, 2000)); // Check every 2 seconds
    }
  }

  /**
   * Get active scan progress
   */
  private async getActiveScanProgress(scanId: string): Promise<number> {
    try {
      const response = await this.client.get('/JSON/ascan/view/status/', {
        params: {
          apikey: this.apiKey,
          scanId,
        },
      });
      return parseInt(response.data.status);
    } catch (error) {
      throw new Error('Failed to get active scan progress: ' + (error as Error).message);
    }
  }

  /**
   * Get alerts for a URL
   */
  async getAlerts(url?: string): Promise<ZAPAlert[]> {
    try {
      const params: any = {
        apikey: this.apiKey,
      };

      if (url) params.baseurl = url;

      const response = await this.client.get('/JSON/core/view/alerts/', { params });
      
      return response.data.alerts.map((alert: any) => ({
        id: alert.id || alert.alertId,
        alert: alert.alert,
        risk: alert.risk,
        confidence: alert.confidence,
        description: alert.description,
        solution: alert.solution,
        reference: alert.reference,
        cweid: alert.cweid,
        wascid: alert.wascid,
        url: alert.url,
        method: alert.method,
        param: alert.param,
        attack: alert.attack,
        evidence: alert.evidence,
      }));
    } catch (error) {
      throw new Error('Failed to get alerts: ' + (error as Error).message);
    }
  }

  /**
   * Get scan status
   */
  async getScanStatus(scanId: string, scanType: 'spider' | 'active'): Promise<number> {
    if (scanType === 'spider') {
      return await this.getSpiderProgress(scanId);
    } else {
      return await this.getActiveScanProgress(scanId);
    }
  }

  /**
   * Stop a scan
   */
  async stopScan(scanId: string, scanType: 'spider' | 'active'): Promise<void> {
    try {
      const endpoint = scanType === 'spider' 
        ? '/JSON/spider/action/stop/'
        : '/JSON/ascan/action/stop/';

      await this.client.get(endpoint, {
        params: {
          apikey: this.apiKey,
          scanId,
        },
      });
    } catch (error) {
      throw new Error('Failed to stop scan: ' + (error as Error).message);
    }
  }

  /**
   * Create a new session
   */
  async createSession(sessionName: string): Promise<void> {
    try {
      await this.client.get('/JSON/core/action/newSession/', {
        params: {
          apikey: this.apiKey,
          name: sessionName,
        },
      });
    } catch (error) {
      throw new Error('Failed to create session: ' + (error as Error).message);
    }
  }

  /**
   * Access a URL through ZAP (for passive scanning)
   */
  async accessUrl(url: string): Promise<void> {
    try {
      await this.client.get('/JSON/core/action/accessUrl/', {
        params: {
          apikey: this.apiKey,
          url,
        },
      });
    } catch (error) {
      throw new Error('Failed to access URL: ' + (error as Error).message);
    }
  }

  /**
   * Get number of alerts by risk level
   */
  async getAlertsSummary(url?: string): Promise<{ high: number; medium: number; low: number; informational: number }> {
    try {
      const params: any = {
        apikey: this.apiKey,
      };

      if (url) params.baseurl = url;

      const response = await this.client.get('/JSON/core/view/alertsSummary/', { params });
      
      return {
        high: parseInt(response.data.High) || 0,
        medium: parseInt(response.data.Medium) || 0,
        low: parseInt(response.data.Low) || 0,
        informational: parseInt(response.data.Informational) || 0,
      };
    } catch (error) {
      throw new Error('Failed to get alerts summary: ' + (error as Error).message);
    }
  }

  /**
   * Clear all alerts
   */
  async clearAlerts(): Promise<void> {
    try {
      await this.client.get('/JSON/core/action/deleteAllAlerts/', {
        params: {
          apikey: this.apiKey,
        },
      });
    } catch (error) {
      throw new Error('Failed to clear alerts: ' + (error as Error).message);
    }
  }

  /**
   * Generate HTML report
   */
  async generateHtmlReport(): Promise<string> {
    try {
      const response = await this.client.get('/OTHER/core/other/htmlreport/', {
        params: {
          apikey: this.apiKey,
        },
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to generate HTML report: ' + (error as Error).message);
    }
  }

  /**
   * Generate XML report
   */
  async generateXmlReport(): Promise<string> {
    try {
      const response = await this.client.get('/OTHER/core/other/xmlreport/', {
        params: {
          apikey: this.apiKey,
        },
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to generate XML report: ' + (error as Error).message);
    }
  }

  // Utility methods

  private generateScanId(): string {
    return `zap-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateSummary(alerts: ZAPAlert[]) {
    return {
      total: alerts.length,
      high: alerts.filter(a => a.risk === 'High').length,
      medium: alerts.filter(a => a.risk === 'Medium').length,
      low: alerts.filter(a => a.risk === 'Low').length,
      informational: alerts.filter(a => a.risk === 'Informational').length,
    };
  }
}

// Singleton instance
let zapInstance: ZAPProxyService | null = null;

export function getZAPProxyService(config?: ZAPConfig): ZAPProxyService {
  if (!zapInstance && config) {
    zapInstance = new ZAPProxyService(config);
  }
  if (!zapInstance) {
    throw new Error('ZAP Proxy Service not initialized. Provide config first.');
  }
  return zapInstance;
}

export function resetZAPProxyService(): void {
  zapInstance = null;
}
