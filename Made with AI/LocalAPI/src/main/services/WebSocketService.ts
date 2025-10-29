// WebSocket Service
// Handles WebSocket connections and message logging

import WebSocket from 'ws';

interface WebSocketConnection {
  id: string;
  url: string;
  ws: WebSocket | null;
  status: 'connecting' | 'connected' | 'disconnected' | 'error';
  logs: LogEntry[];
  createdAt: Date;
}

interface LogEntry {
  id: string;
  timestamp: Date;
  type: 'sent' | 'received' | 'error' | 'info' | 'connection';
  message: string;
  data?: any;
}

interface WebSocketMessage {
  connectionId: string;
  message: string;
}

export class WebSocketService {
  private connections: Map<string, WebSocketConnection> = new Map();
  private eventCallbacks: Map<string, (event: any) => void> = new Map();

  /**
   * Create new WebSocket connection
   */
  connect(
    url: string,
    protocols?: string | string[],
    headers?: Record<string, string>
  ): string {
    const connectionId = this.generateId();

    const connection: WebSocketConnection = {
      id: connectionId,
      url,
      ws: null,
      status: 'connecting',
      logs: [],
      createdAt: new Date(),
    };

    this.connections.set(connectionId, connection);

    try {
      // Create WebSocket connection
      const ws = new WebSocket(url, protocols, {
        headers,
      });

      connection.ws = ws;

      // Add log entry
      this.addLog(connectionId, {
        type: 'connection',
        message: `Connecting to ${url}...`,
      });

      // Setup event handlers
      ws.on('open', () => {
        connection.status = 'connected';
        this.addLog(connectionId, {
          type: 'connection',
          message: 'Connection established',
        });
        this.emitEvent(connectionId, { type: 'open' });
      });

      ws.on('message', (data: WebSocket.Data) => {
        const message = data.toString();
        this.addLog(connectionId, {
          type: 'received',
          message,
          data: this.tryParseJSON(message),
        });
        this.emitEvent(connectionId, { type: 'message', data: message });
      });

      ws.on('close', (code: number, reason: Buffer) => {
        connection.status = 'disconnected';
        this.addLog(connectionId, {
          type: 'connection',
          message: `Connection closed (${code}): ${reason.toString()}`,
        });
        this.emitEvent(connectionId, { type: 'close', code, reason: reason.toString() });
      });

      ws.on('error', (error: Error) => {
        connection.status = 'error';
        this.addLog(connectionId, {
          type: 'error',
          message: error.message,
        });
        this.emitEvent(connectionId, { type: 'error', error: error.message });
      });

      ws.on('ping', (data: Buffer) => {
        this.addLog(connectionId, {
          type: 'info',
          message: `Ping received: ${data.toString()}`,
        });
      });

      ws.on('pong', (data: Buffer) => {
        this.addLog(connectionId, {
          type: 'info',
          message: `Pong received: ${data.toString()}`,
        });
      });
    } catch (error: any) {
      connection.status = 'error';
      this.addLog(connectionId, {
        type: 'error',
        message: `Connection failed: ${error.message}`,
      });
    }

    return connectionId;
  }

  /**
   * Send message through WebSocket
   */
  send(connectionId: string, message: string): boolean {
    const connection = this.connections.get(connectionId);

    if (!connection || !connection.ws) {
      return false;
    }

    if (connection.ws.readyState !== WebSocket.OPEN) {
      this.addLog(connectionId, {
        type: 'error',
        message: 'Cannot send message: Connection not open',
      });
      return false;
    }

    try {
      connection.ws.send(message);
      this.addLog(connectionId, {
        type: 'sent',
        message,
        data: this.tryParseJSON(message),
      });
      return true;
    } catch (error: any) {
      this.addLog(connectionId, {
        type: 'error',
        message: `Failed to send message: ${error.message}`,
      });
      return false;
    }
  }

  /**
   * Close WebSocket connection
   */
  disconnect(connectionId: string, code?: number, reason?: string): boolean {
    const connection = this.connections.get(connectionId);

    if (!connection || !connection.ws) {
      return false;
    }

    try {
      connection.ws.close(code, reason);
      this.addLog(connectionId, {
        type: 'connection',
        message: 'Disconnecting...',
      });
      return true;
    } catch (error: any) {
      this.addLog(connectionId, {
        type: 'error',
        message: `Failed to disconnect: ${error.message}`,
      });
      return false;
    }
  }

  /**
   * Send ping
   */
  ping(connectionId: string, data?: string): boolean {
    const connection = this.connections.get(connectionId);

    if (!connection || !connection.ws) {
      return false;
    }

    if (connection.ws.readyState !== WebSocket.OPEN) {
      return false;
    }

    try {
      connection.ws.ping(data);
      this.addLog(connectionId, {
        type: 'info',
        message: `Ping sent${data ? `: ${data}` : ''}`,
      });
      return true;
    } catch (error: any) {
      this.addLog(connectionId, {
        type: 'error',
        message: `Failed to send ping: ${error.message}`,
      });
      return false;
    }
  }

  /**
   * Get connection info
   */
  getConnection(connectionId: string): WebSocketConnection | null {
    return this.connections.get(connectionId) || null;
  }

  /**
   * Get all connections
   */
  getAllConnections(): WebSocketConnection[] {
    return Array.from(this.connections.values());
  }

  /**
   * Get connection logs
   */
  getLogs(connectionId: string): LogEntry[] {
    const connection = this.connections.get(connectionId);
    return connection?.logs || [];
  }

  /**
   * Clear logs
   */
  clearLogs(connectionId: string): boolean {
    const connection = this.connections.get(connectionId);
    if (connection) {
      connection.logs = [];
      return true;
    }
    return false;
  }

  /**
   * Remove connection
   */
  removeConnection(connectionId: string): boolean {
    const connection = this.connections.get(connectionId);
    if (connection) {
      if (connection.ws) {
        connection.ws.close();
      }
      this.connections.delete(connectionId);
      this.eventCallbacks.delete(connectionId);
      return true;
    }
    return false;
  }

  /**
   * Register event callback
   */
  onEvent(connectionId: string, callback: (event: any) => void): void {
    this.eventCallbacks.set(connectionId, callback);
  }

  /**
   * Unregister event callback
   */
  offEvent(connectionId: string): void {
    this.eventCallbacks.delete(connectionId);
  }

  /**
   * Add log entry
   */
  private addLog(
    connectionId: string,
    log: Omit<LogEntry, 'id' | 'timestamp'>
  ): void {
    const connection = this.connections.get(connectionId);
    if (connection) {
      const logEntry: LogEntry = {
        id: this.generateId(),
        timestamp: new Date(),
        ...log,
      };
      connection.logs.push(logEntry);

      // Limit logs to 1000 entries
      if (connection.logs.length > 1000) {
        connection.logs.shift();
      }
    }
  }

  /**
   * Emit event to callback
   */
  private emitEvent(connectionId: string, event: any): void {
    const callback = this.eventCallbacks.get(connectionId);
    if (callback) {
      callback(event);
    }
  }

  /**
   * Try to parse JSON
   */
  private tryParseJSON(str: string): any {
    try {
      return JSON.parse(str);
    } catch {
      return null;
    }
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get connection status
   */
  getStatus(connectionId: string): string | null {
    const connection = this.connections.get(connectionId);
    if (!connection) return null;

    if (!connection.ws) return connection.status;

    switch (connection.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'disconnecting';
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'unknown';
    }
  }
}

// Singleton instance
let webSocketServiceInstance: WebSocketService | null = null;

export function getWebSocketService(): WebSocketService {
  if (!webSocketServiceInstance) {
    webSocketServiceInstance = new WebSocketService();
  }
  return webSocketServiceInstance;
}
