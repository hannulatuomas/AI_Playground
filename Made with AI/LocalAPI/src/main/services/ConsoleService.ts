/**
 * ConsoleService - Debug Console Logging Service
 * 
 * Provides comprehensive logging for all application activities:
 * - HTTP requests/responses
 * - WebSocket messages
 * - Server-Sent Events
 * - Script console output
 * - Errors and warnings
 * 
 * Features:
 * - Real-time logging with circular buffer
 * - Persistent storage to SQLite
 * - Filtering, searching, and sorting
 * - Export to JSON, CSV, and HAR formats
 * - Performance metrics tracking
 */

import { randomUUID } from 'crypto';
import type { IDatabaseDriver } from './DatabaseService';

export interface ConsoleEntry {
  id: string;
  timestamp: number;
  type: 'request' | 'response' | 'websocket' | 'sse' | 'script' | 'error';
  
  // Request/Response data
  method?: string;
  url?: string;
  status?: number;
  statusText?: string;
  headers?: Record<string, string>;
  body?: any;
  
  // Timing data
  duration?: number;
  timings?: {
    dns?: number;
    tcp?: number;
    ssl?: number;
    request?: number;
    response?: number;
    total: number;
  };
  
  // Metadata
  requestId?: string;
  protocol?: string;
  cached?: boolean;
  error?: string;
  
  // WebSocket/SSE
  direction?: 'sent' | 'received';
  connectionId?: string;
  eventType?: string;
  
  // Script output
  scriptOutput?: string;
  logLevel?: 'log' | 'info' | 'warn' | 'error';
}

export interface ConsoleFilter {
  methods?: string[];
  statuses?: number[];
  types?: string[];
  timeRange?: { start: number; end: number };
  search?: string;
  requestId?: string;
  hasError?: boolean;
}

export interface ConsoleExportOptions {
  format: 'json' | 'csv' | 'har';
  filters?: ConsoleFilter;
  includeHeaders?: boolean;
  includeBody?: boolean;
}

export class ConsoleService {
  private entries: ConsoleEntry[] = [];
  private maxEntries: number = 10000;
  private persistenceEnabled: boolean = true;
  private db: IDatabaseDriver | null = null;
  private autoScrollEnabled: boolean = true;
  private isPaused: boolean = false;

  constructor(db?: IDatabaseDriver | null) {
    this.db = db || null;
    if (this.db && this.persistenceEnabled) {
      this.initializeDatabase();
      this.loadFromDisk();
    }
  }

  /**
   * Initialize database schema for console entries
   */
  private initializeDatabase(): void {
    if (!this.db) return;

    this.db.exec(`
      CREATE TABLE IF NOT EXISTS console_entries (
        id TEXT PRIMARY KEY,
        timestamp INTEGER NOT NULL,
        type TEXT NOT NULL,
        method TEXT,
        url TEXT,
        status INTEGER,
        status_text TEXT,
        headers TEXT,
        body TEXT,
        duration INTEGER,
        timings TEXT,
        request_id TEXT,
        protocol TEXT,
        cached INTEGER,
        error TEXT,
        direction TEXT,
        connection_id TEXT,
        event_type TEXT,
        script_output TEXT,
        log_level TEXT,
        created_at INTEGER NOT NULL
      );

      CREATE INDEX IF NOT EXISTS idx_console_timestamp ON console_entries(timestamp);
      CREATE INDEX IF NOT EXISTS idx_console_type ON console_entries(type);
      CREATE INDEX IF NOT EXISTS idx_console_request_id ON console_entries(request_id);
      CREATE INDEX IF NOT EXISTS idx_console_status ON console_entries(status);
    `);
  }

  /**
   * Log an HTTP request
   */
  logRequest(
    request: {
      method: string;
      url: string;
      headers?: Record<string, string>;
      body?: any;
    },
    metadata?: {
      requestId?: string;
      protocol?: string;
    }
  ): ConsoleEntry {
    const entry: ConsoleEntry = {
      id: randomUUID(),
      timestamp: Date.now(),
      type: 'request',
      method: request.method,
      url: request.url,
      headers: request.headers,
      body: request.body,
      requestId: metadata?.requestId || randomUUID(),
      protocol: metadata?.protocol || 'HTTP/1.1',
    };

    this.addEntry(entry);
    return entry;
  }

  /**
   * Log an HTTP response
   */
  logResponse(
    response: {
      status: number;
      statusText: string;
      headers?: Record<string, string>;
      body?: any;
    },
    request: {
      method: string;
      url: string;
    },
    metadata?: {
      requestId?: string;
      duration?: number;
      timings?: any;
      cached?: boolean;
      protocol?: string;
    }
  ): ConsoleEntry {
    const entry: ConsoleEntry = {
      id: randomUUID(),
      timestamp: Date.now(),
      type: 'response',
      method: request.method,
      url: request.url,
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
      body: response.body,
      duration: metadata?.duration,
      timings: metadata?.timings,
      requestId: metadata?.requestId,
      cached: metadata?.cached,
      protocol: metadata?.protocol || 'HTTP/1.1',
    };

    this.addEntry(entry);
    return entry;
  }

  /**
   * Log a WebSocket message
   */
  logWebSocketMessage(
    message: string | Buffer,
    direction: 'sent' | 'received',
    connectionId: string,
    metadata?: {
      requestId?: string;
    }
  ): ConsoleEntry {
    const entry: ConsoleEntry = {
      id: randomUUID(),
      timestamp: Date.now(),
      type: 'websocket',
      body: typeof message === 'string' ? message : message.toString(),
      direction,
      connectionId,
      requestId: metadata?.requestId,
      protocol: 'WebSocket',
    };

    this.addEntry(entry);
    return entry;
  }

  /**
   * Log a Server-Sent Event
   */
  logSSEMessage(
    event: {
      type?: string;
      data: string;
      id?: string;
    },
    connectionId: string,
    metadata?: {
      requestId?: string;
      url?: string;
    }
  ): ConsoleEntry {
    const entry: ConsoleEntry = {
      id: randomUUID(),
      timestamp: Date.now(),
      type: 'sse',
      eventType: event.type,
      body: event.data,
      connectionId,
      requestId: metadata?.requestId,
      url: metadata?.url,
      protocol: 'SSE',
    };

    this.addEntry(entry);
    return entry;
  }

  /**
   * Log script console output
   */
  logScriptOutput(
    output: string,
    logLevel: 'log' | 'info' | 'warn' | 'error',
    requestId?: string
  ): ConsoleEntry {
    const entry: ConsoleEntry = {
      id: randomUUID(),
      timestamp: Date.now(),
      type: 'script',
      scriptOutput: output,
      logLevel,
      requestId,
    };

    this.addEntry(entry);
    return entry;
  }

  /**
   * Log an error
   */
  logError(
    error: Error | string,
    context?: {
      requestId?: string;
      url?: string;
      method?: string;
    }
  ): ConsoleEntry {
    const errorMessage = typeof error === 'string' ? error : error.message;
    const entry: ConsoleEntry = {
      id: randomUUID(),
      timestamp: Date.now(),
      type: 'error',
      error: errorMessage,
      requestId: context?.requestId,
      url: context?.url,
      method: context?.method,
      logLevel: 'error',
    };

    this.addEntry(entry);
    return entry;
  }

  /**
   * Add entry to in-memory storage and persist if enabled
   */
  private addEntry(entry: ConsoleEntry): void {
    if (this.isPaused) return;

    // Add to in-memory storage
    this.entries.push(entry);

    // Maintain max entries limit (circular buffer)
    if (this.entries.length > this.maxEntries) {
      this.entries.shift();
    }

    // Persist to database if enabled
    if (this.persistenceEnabled && this.db) {
      this.persistEntry(entry);
    }
  }

  /**
   * Persist entry to SQLite
   */
  private persistEntry(entry: ConsoleEntry): void {
    if (!this.db) return;

    const stmt = this.db.prepare(`
      INSERT INTO console_entries (
        id, timestamp, type, method, url, status, status_text,
        headers, body, duration, timings, request_id, protocol,
        cached, error, direction, connection_id, event_type,
        script_output, log_level, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      entry.id,
      entry.timestamp,
      entry.type,
      entry.method || null,
      entry.url || null,
      entry.status || null,
      entry.statusText || null,
      entry.headers ? JSON.stringify(entry.headers) : null,
      entry.body ? JSON.stringify(entry.body) : null,
      entry.duration || null,
      entry.timings ? JSON.stringify(entry.timings) : null,
      entry.requestId || null,
      entry.protocol || null,
      entry.cached ? 1 : 0,
      entry.error || null,
      entry.direction || null,
      entry.connectionId || null,
      entry.eventType || null,
      entry.scriptOutput || null,
      entry.logLevel || null,
      Date.now()
    );
  }

  /**
   * Get entries with optional filtering
   */
  getEntries(filters?: ConsoleFilter, limit?: number, offset?: number): ConsoleEntry[] {
    let filtered = [...this.entries];

    if (filters) {
      // Filter by type
      if (filters.types && filters.types.length > 0) {
        filtered = filtered.filter(e => filters.types!.includes(e.type));
      }

      // Filter by method
      if (filters.methods && filters.methods.length > 0) {
        filtered = filtered.filter(e => e.method && filters.methods!.includes(e.method));
      }

      // Filter by status
      if (filters.statuses && filters.statuses.length > 0) {
        filtered = filtered.filter(e => e.status && filters.statuses!.includes(e.status));
      }

      // Filter by time range
      if (filters.timeRange) {
        filtered = filtered.filter(
          e =>
            e.timestamp >= filters.timeRange!.start &&
            e.timestamp <= filters.timeRange!.end
        );
      }

      // Filter by request ID
      if (filters.requestId) {
        filtered = filtered.filter(e => e.requestId === filters.requestId);
      }

      // Filter by error
      if (filters.hasError !== undefined) {
        filtered = filtered.filter(e => (e.error !== undefined) === filters.hasError);
      }

      // Search
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        filtered = filtered.filter(e => {
          return (
            e.url?.toLowerCase().includes(searchLower) ||
            e.method?.toLowerCase().includes(searchLower) ||
            e.error?.toLowerCase().includes(searchLower) ||
            e.scriptOutput?.toLowerCase().includes(searchLower) ||
            e.statusText?.toLowerCase().includes(searchLower) ||
            (e.body && JSON.stringify(e.body).toLowerCase().includes(searchLower))
          );
        });
      }
    }

    // Apply pagination
    if (offset !== undefined) {
      filtered = filtered.slice(offset);
    }
    if (limit !== undefined) {
      filtered = filtered.slice(0, limit);
    }

    return filtered;
  }

  /**
   * Get a single entry by ID
   */
  getEntry(id: string): ConsoleEntry | null {
    return this.entries.find(e => e.id === id) || null;
  }

  /**
   * Search entries by query
   */
  searchEntries(query: string): ConsoleEntry[] {
    return this.getEntries({ search: query });
  }

  /**
   * Clear entries (optionally only older than timestamp)
   */
  clearEntries(olderThan?: number): void {
    if (olderThan) {
      this.entries = this.entries.filter(e => e.timestamp >= olderThan);
      
      if (this.db) {
        this.db.prepare('DELETE FROM console_entries WHERE timestamp < ?').run(olderThan);
      }
    } else {
      this.entries = [];
      
      if (this.db) {
        this.db.prepare('DELETE FROM console_entries').run();
      }
    }
  }

  /**
   * Delete a specific entry
   */
  deleteEntry(id: string): boolean {
    const index = this.entries.findIndex(e => e.id === id);
    if (index === -1) return false;

    this.entries.splice(index, 1);

    if (this.db) {
      this.db.prepare('DELETE FROM console_entries WHERE id = ?').run(id);
    }

    return true;
  }

  /**
   * Export entries to various formats
   */
  exportEntries(options: ConsoleExportOptions): string {
    const entries = this.getEntries(options.filters);

    switch (options.format) {
      case 'json':
        return this.exportToJSON(entries, options);
      case 'csv':
        return this.exportToCSV(entries, options);
      case 'har':
        return this.exportToHAR(entries, options);
      default:
        throw new Error(`Unsupported export format: ${options.format}`);
    }
  }

  /**
   * Export to JSON format
   */
  private exportToJSON(entries: ConsoleEntry[], options: ConsoleExportOptions): string {
    const data = entries.map(entry => {
      const exported: any = {
        id: entry.id,
        timestamp: entry.timestamp,
        type: entry.type,
      };

      if (entry.method) exported.method = entry.method;
      if (entry.url) exported.url = entry.url;
      if (entry.status) exported.status = entry.status;
      if (entry.statusText) exported.statusText = entry.statusText;
      if (entry.duration) exported.duration = entry.duration;
      if (entry.timings) exported.timings = entry.timings;
      if (entry.protocol) exported.protocol = entry.protocol;
      if (entry.cached) exported.cached = entry.cached;
      if (entry.error) exported.error = entry.error;
      if (entry.direction) exported.direction = entry.direction;
      if (entry.connectionId) exported.connectionId = entry.connectionId;
      if (entry.eventType) exported.eventType = entry.eventType;
      if (entry.scriptOutput) exported.scriptOutput = entry.scriptOutput;
      if (entry.logLevel) exported.logLevel = entry.logLevel;
      if (entry.requestId) exported.requestId = entry.requestId;

      if (options.includeHeaders && entry.headers) {
        exported.headers = entry.headers;
      }

      if (options.includeBody && entry.body) {
        exported.body = entry.body;
      }

      return exported;
    });

    return JSON.stringify(data, null, 2);
  }

  /**
   * Export to CSV format
   */
  private exportToCSV(entries: ConsoleEntry[], options: ConsoleExportOptions): string {
    const headers = [
      'ID',
      'Timestamp',
      'Type',
      'Method',
      'URL',
      'Status',
      'Status Text',
      'Duration',
      'Protocol',
      'Cached',
      'Error',
      'Request ID',
    ];

    const rows = entries.map(entry => [
      entry.id,
      new Date(entry.timestamp).toISOString(),
      entry.type,
      entry.method || '',
      entry.url || '',
      entry.status || '',
      entry.statusText || '',
      entry.duration || '',
      entry.protocol || '',
      entry.cached ? 'true' : 'false',
      entry.error || '',
      entry.requestId || '',
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(',')),
    ].join('\n');

    return csvContent;
  }

  /**
   * Export to HAR (HTTP Archive) format
   */
  private exportToHAR(entries: ConsoleEntry[], options: ConsoleExportOptions): string {
    const harEntries = entries
      .filter(e => e.type === 'request' || e.type === 'response')
      .reduce((acc: any[], entry) => {
        if (entry.type === 'request') {
          const harEntry: any = {
            startedDateTime: new Date(entry.timestamp).toISOString(),
            time: 0,
            request: {
              method: entry.method || 'GET',
              url: entry.url || '',
              httpVersion: entry.protocol || 'HTTP/1.1',
              headers: [],
              queryString: [],
              cookies: [],
              headersSize: -1,
              bodySize: -1,
            },
            response: {
              status: 0,
              statusText: '',
              httpVersion: entry.protocol || 'HTTP/1.1',
              headers: [],
              cookies: [],
              content: { size: 0, mimeType: '' },
              redirectURL: '',
              headersSize: -1,
              bodySize: -1,
            },
            cache: {},
            timings: {
              send: 0,
              wait: 0,
              receive: 0,
            },
          };

          if (options.includeHeaders && entry.headers) {
            harEntry.request.headers = Object.entries(entry.headers).map(([name, value]) => ({
              name,
              value,
            }));
          }

          acc.push(harEntry);
        } else if (entry.type === 'response') {
          const matchingEntry = acc.find(e => e.request.url === entry.url);
          if (matchingEntry) {
            matchingEntry.response.status = entry.status || 0;
            matchingEntry.response.statusText = entry.statusText || '';
            matchingEntry.time = entry.duration || 0;

            if (entry.timings) {
              matchingEntry.timings = {
                send: entry.timings.request || 0,
                wait: entry.timings.response || 0,
                receive: 0,
              };
            }

            if (options.includeHeaders && entry.headers) {
              matchingEntry.response.headers = Object.entries(entry.headers).map(
                ([name, value]) => ({ name, value })
              );
            }

            if (options.includeBody && entry.body) {
              matchingEntry.response.content = {
                size: JSON.stringify(entry.body).length,
                mimeType: entry.headers?.['content-type'] || 'application/json',
                text: JSON.stringify(entry.body),
              };
            }
          }
        }
        return acc;
      }, []);

    const har = {
      log: {
        version: '1.2',
        creator: {
          name: 'LocalAPI',
          version: '0.9.0',
        },
        entries: harEntries,
      },
    };

    return JSON.stringify(har, null, 2);
  }

  /**
   * Load entries from SQLite database
   */
  async loadFromDisk(): Promise<void> {
    if (!this.db) return;

    const stmt = this.db.prepare(`
      SELECT * FROM console_entries
      ORDER BY timestamp DESC
      LIMIT ?
    `);

    const rows = stmt.all(this.maxEntries) as any[];

    this.entries = rows.map(row => {
      const entry: ConsoleEntry = {
        id: row.id,
        timestamp: row.timestamp,
        type: row.type,
      };

      if (row.method) entry.method = row.method;
      if (row.url) entry.url = row.url;
      if (row.status) entry.status = row.status;
      if (row.status_text) entry.statusText = row.status_text;
      if (row.headers) entry.headers = JSON.parse(row.headers);
      if (row.body) entry.body = JSON.parse(row.body);
      if (row.duration) entry.duration = row.duration;
      if (row.timings) entry.timings = JSON.parse(row.timings);
      if (row.request_id) entry.requestId = row.request_id;
      if (row.protocol) entry.protocol = row.protocol;
      if (row.cached) entry.cached = row.cached === 1;
      if (row.error) entry.error = row.error;
      if (row.direction) entry.direction = row.direction;
      if (row.connection_id) entry.connectionId = row.connection_id;
      if (row.event_type) entry.eventType = row.event_type;
      if (row.script_output) entry.scriptOutput = row.script_output;
      if (row.log_level) entry.logLevel = row.log_level;

      return entry;
    }).reverse(); // Reverse to maintain chronological order
    
    // Trim to maxEntries if needed (respects current limit)
    if (this.entries.length > this.maxEntries) {
      this.entries = this.entries.slice(-this.maxEntries);
    }
  }

  /**
   * Enable or disable persistence
   */
  setPersistence(enabled: boolean): void {
    this.persistenceEnabled = enabled;
  }

  /**
   * Set max entries limit
   */
  setMaxEntries(max: number): void {
    this.maxEntries = max;
    
    // Trim if necessary
    if (this.entries.length > this.maxEntries) {
      this.entries = this.entries.slice(-this.maxEntries);
    }
  }

  /**
   * Pause/resume logging
   */
  setPaused(paused: boolean): void {
    this.isPaused = paused;
  }

  /**
   * Get pause state
   */
  isPausedState(): boolean {
    return this.isPaused;
  }

  /**
   * Get statistics
   */
  getStats(): {
    totalEntries: number;
    requestCount: number;
    responseCount: number;
    errorCount: number;
    averageDuration: number;
  } {
    const requestCount = this.entries.filter(e => e.type === 'request').length;
    const responseCount = this.entries.filter(e => e.type === 'response').length;
    const errorCount = this.entries.filter(e => e.type === 'error' || e.error).length;
    
    const durations = this.entries
      .filter(e => e.duration !== undefined)
      .map(e => e.duration!);
    
    const averageDuration = durations.length > 0
      ? durations.reduce((a, b) => a + b, 0) / durations.length
      : 0;

    return {
      totalEntries: this.entries.length,
      requestCount,
      responseCount,
      errorCount,
      averageDuration: Math.round(averageDuration),
    };
  }
}
