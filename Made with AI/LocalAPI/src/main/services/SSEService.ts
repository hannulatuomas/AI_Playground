// Server-Sent Events (SSE) Service
// Handles SSE connections and event streaming

import EventSource from 'eventsource';

interface SSEConnection {
  id: string;
  url: string;
  eventSource: EventSource | null;
  status: 'connecting' | 'connected' | 'disconnected' | 'error';
  events: SSEEvent[];
  eventTypes: Set<string>;
  createdAt: Date;
}

interface SSEEvent {
  id: string;
  timestamp: Date;
  type: string;
  data: string;
  eventId?: string;
  retry?: number;
  parsedData?: any;
}

export class SSEService {
  private connections: Map<string, SSEConnection> = new Map();
  private eventCallbacks: Map<string, (event: any) => void> = new Map();

  /**
   * Create new SSE connection
   */
  connect(url: string, headers?: Record<string, string>): string {
    const connectionId = this.generateId();

    const connection: SSEConnection = {
      id: connectionId,
      url,
      eventSource: null,
      status: 'connecting',
      events: [],
      eventTypes: new Set(),
      createdAt: new Date(),
    };

    this.connections.set(connectionId, connection);

    try {
      // Create EventSource
      const eventSource = new EventSource(url, {
        headers: headers || {},
      });

      connection.eventSource = eventSource;

      // Add event
      this.addEvent(connectionId, {
        type: 'connection',
        data: `Connecting to ${url}...`,
      });

      // Setup event handlers
      eventSource.onopen = () => {
        connection.status = 'connected';
        this.addEvent(connectionId, {
          type: 'connection',
          data: 'Connection established',
        });
        this.emitEvent(connectionId, { type: 'open' });
      };

      eventSource.onerror = (error: any) => {
        connection.status = 'error';
        this.addEvent(connectionId, {
          type: 'error',
          data: error.message || 'Connection error',
        });
        this.emitEvent(connectionId, { type: 'error', error });
      };

      eventSource.onmessage = (event: MessageEvent) => {
        this.addEvent(connectionId, {
          type: 'message',
          data: event.data,
          eventId: (event as any).lastEventId,
        });
        this.emitEvent(connectionId, { type: 'message', data: event.data });
      };

      // Listen for custom event types
      // Note: Custom events need to be registered separately
    } catch (error: any) {
      connection.status = 'error';
      this.addEvent(connectionId, {
        type: 'error',
        data: `Connection failed: ${error.message}`,
      });
    }

    return connectionId;
  }

  /**
   * Register custom event listener
   */
  addEventListener(connectionId: string, eventType: string): boolean {
    const connection = this.connections.get(connectionId);

    if (!connection || !connection.eventSource) {
      return false;
    }

    try {
      connection.eventSource.addEventListener(eventType, (event: MessageEvent) => {
        this.addEvent(connectionId, {
          type: eventType,
          data: event.data,
          eventId: (event as any).lastEventId,
        });
        this.emitEvent(connectionId, { type: eventType, data: event.data });
      });

      connection.eventTypes.add(eventType);
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Close SSE connection
   */
  disconnect(connectionId: string): boolean {
    const connection = this.connections.get(connectionId);

    if (!connection || !connection.eventSource) {
      return false;
    }

    try {
      connection.eventSource.close();
      connection.status = 'disconnected';
      this.addEvent(connectionId, {
        type: 'connection',
        data: 'Connection closed',
      });
      return true;
    } catch (error: any) {
      this.addEvent(connectionId, {
        type: 'error',
        data: `Failed to disconnect: ${error.message}`,
      });
      return false;
    }
  }

  /**
   * Get connection info
   */
  getConnection(connectionId: string): SSEConnection | null {
    return this.connections.get(connectionId) || null;
  }

  /**
   * Get all connections
   */
  getAllConnections(): SSEConnection[] {
    return Array.from(this.connections.values());
  }

  /**
   * Get connection events
   */
  getEvents(connectionId: string): SSEEvent[] {
    const connection = this.connections.get(connectionId);
    return connection?.events || [];
  }

  /**
   * Get event types
   */
  getEventTypes(connectionId: string): string[] {
    const connection = this.connections.get(connectionId);
    return connection ? Array.from(connection.eventTypes) : [];
  }

  /**
   * Filter events by type
   */
  filterEvents(connectionId: string, eventType: string): SSEEvent[] {
    const events = this.getEvents(connectionId);
    return events.filter(event => event.type === eventType);
  }

  /**
   * Clear events
   */
  clearEvents(connectionId: string): boolean {
    const connection = this.connections.get(connectionId);
    if (connection) {
      connection.events = [];
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
      if (connection.eventSource) {
        connection.eventSource.close();
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
   * Add event to connection
   */
  private addEvent(
    connectionId: string,
    event: Omit<SSEEvent, 'id' | 'timestamp' | 'parsedData'>
  ): void {
    const connection = this.connections.get(connectionId);
    if (connection) {
      const sseEvent: SSEEvent = {
        id: this.generateId(),
        timestamp: new Date(),
        parsedData: this.tryParseJSON(event.data),
        ...event,
      };

      connection.events.push(sseEvent);
      connection.eventTypes.add(event.type);

      // Limit events to 1000 entries
      if (connection.events.length > 1000) {
        connection.events.shift();
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

    if (!connection.eventSource) return connection.status;

    switch (connection.eventSource.readyState) {
      case EventSource.CONNECTING:
        return 'connecting';
      case EventSource.OPEN:
        return 'connected';
      case EventSource.CLOSED:
        return 'disconnected';
      default:
        return 'unknown';
    }
  }

  /**
   * Get event statistics
   */
  getStatistics(connectionId: string): {
    totalEvents: number;
    eventTypes: Record<string, number>;
    connectionDuration: number;
  } | null {
    const connection = this.connections.get(connectionId);
    if (!connection) return null;

    const eventTypes: Record<string, number> = {};
    for (const event of connection.events) {
      eventTypes[event.type] = (eventTypes[event.type] || 0) + 1;
    }

    const connectionDuration = Date.now() - connection.createdAt.getTime();

    return {
      totalEvents: connection.events.length,
      eventTypes,
      connectionDuration,
    };
  }
}

// Singleton instance
let sseServiceInstance: SSEService | null = null;

export function getSSEService(): SSEService {
  if (!sseServiceInstance) {
    sseServiceInstance = new SSEService();
  }
  return sseServiceInstance;
}
