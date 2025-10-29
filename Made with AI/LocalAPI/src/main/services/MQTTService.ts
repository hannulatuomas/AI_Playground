// MQTT Service
// Handles MQTT connections for publish/subscribe messaging

import * as mqtt from 'mqtt';

interface MQTTConnection {
  id: string;
  brokerUrl: string;
  client: mqtt.MqttClient | null;
  status: 'connecting' | 'connected' | 'disconnected' | 'error';
  messages: MQTTMessage[];
  subscriptions: Map<string, number>; // topic -> QoS
  createdAt: Date;
}

interface MQTTMessage {
  id: string;
  timestamp: Date;
  type: 'published' | 'received' | 'error' | 'info';
  topic: string;
  payload: string;
  qos?: number;
  retain?: boolean;
  parsedPayload?: any;
}

interface PublishOptions {
  connectionId: string;
  topic: string;
  message: string;
  qos?: 0 | 1 | 2;
  retain?: boolean;
}

interface SubscribeOptions {
  connectionId: string;
  topic: string;
  qos?: 0 | 1 | 2;
}

export class MQTTService {
  private connections: Map<string, MQTTConnection> = new Map();

  /**
   * Create MQTT connection
   */
  connect(
    brokerUrl: string,
    options?: mqtt.IClientOptions
  ): string {
    const connectionId = this.generateId();

    const conn: MQTTConnection = {
      id: connectionId,
      brokerUrl,
      client: null,
      status: 'connecting',
      messages: [],
      subscriptions: new Map(),
      createdAt: new Date(),
    };

    this.connections.set(connectionId, conn);

    try {
      this.addMessage(connectionId, {
        type: 'info',
        topic: 'system',
        payload: `Connecting to ${brokerUrl}...`,
      });

      // Create MQTT client
      const client = mqtt.connect(brokerUrl, {
        ...options,
        reconnectPeriod: 5000,
      });

      conn.client = client;

      // Setup event handlers
      client.on('connect', () => {
        conn.status = 'connected';
        this.addMessage(connectionId, {
          type: 'info',
          topic: 'system',
          payload: 'Connected to broker',
        });
      });

      client.on('message', (topic: string, payload: Buffer, packet: mqtt.IPublishPacket) => {
        const message = payload.toString();
        this.addMessage(connectionId, {
          type: 'received',
          topic,
          payload: message,
          qos: packet.qos,
          retain: packet.retain,
        });
      });

      client.on('error', (error: Error) => {
        conn.status = 'error';
        this.addMessage(connectionId, {
          type: 'error',
          topic: 'system',
          payload: error.message,
        });
      });

      client.on('close', () => {
        conn.status = 'disconnected';
        this.addMessage(connectionId, {
          type: 'info',
          topic: 'system',
          payload: 'Connection closed',
        });
      });

      client.on('reconnect', () => {
        conn.status = 'connecting';
        this.addMessage(connectionId, {
          type: 'info',
          topic: 'system',
          payload: 'Reconnecting...',
        });
      });

      client.on('offline', () => {
        conn.status = 'disconnected';
        this.addMessage(connectionId, {
          type: 'info',
          topic: 'system',
          payload: 'Client offline',
        });
      });
    } catch (error: any) {
      conn.status = 'error';
      this.addMessage(connectionId, {
        type: 'error',
        topic: 'system',
        payload: `Connection failed: ${error.message}`,
      });
    }

    return connectionId;
  }

  /**
   * Disconnect from MQTT broker
   */
  async disconnect(connectionId: string): Promise<boolean> {
    const conn = this.connections.get(connectionId);

    if (!conn || !conn.client) return false;

    return new Promise((resolve) => {
      conn.client!.end(false, {}, () => {
        conn.status = 'disconnected';
        this.addMessage(connectionId, {
          type: 'info',
          topic: 'system',
          payload: 'Disconnected',
        });
        resolve(true);
      });
    });
  }

  /**
   * Publish message to topic
   */
  async publish(options: PublishOptions): Promise<boolean> {
    const conn = this.connections.get(options.connectionId);

    if (!conn || !conn.client) return false;

    return new Promise((resolve) => {
      conn.client!.publish(
        options.topic,
        options.message,
        {
          qos: options.qos || 0,
          retain: options.retain || false,
        },
        (error) => {
          if (error) {
            this.addMessage(options.connectionId, {
              type: 'error',
              topic: options.topic,
              payload: `Publish failed: ${error.message}`,
            });
            resolve(false);
          } else {
            this.addMessage(options.connectionId, {
              type: 'published',
              topic: options.topic,
              payload: options.message,
              qos: options.qos,
              retain: options.retain,
            });
            resolve(true);
          }
        }
      );
    });
  }

  /**
   * Subscribe to topic
   */
  async subscribe(options: SubscribeOptions): Promise<boolean> {
    const conn = this.connections.get(options.connectionId);

    if (!conn || !conn.client) return false;

    return new Promise((resolve) => {
      conn.client!.subscribe(
        options.topic,
        { qos: options.qos || 0 },
        (error, granted) => {
          if (error) {
            this.addMessage(options.connectionId, {
              type: 'error',
              topic: options.topic,
              payload: `Subscribe failed: ${error.message}`,
            });
            resolve(false);
          } else {
            const qos = granted && granted[0] ? granted[0].qos : options.qos || 0;
            conn.subscriptions.set(options.topic, qos);
            this.addMessage(options.connectionId, {
              type: 'info',
              topic: options.topic,
              payload: `Subscribed to topic (QoS ${qos})`,
            });
            resolve(true);
          }
        }
      );
    });
  }

  /**
   * Unsubscribe from topic
   */
  async unsubscribe(connectionId: string, topic: string): Promise<boolean> {
    const conn = this.connections.get(connectionId);

    if (!conn || !conn.client) return false;

    return new Promise((resolve) => {
      conn.client!.unsubscribe(topic, {}, (error) => {
        if (error) {
          this.addMessage(connectionId, {
            type: 'error',
            topic,
            payload: `Unsubscribe failed: ${error.message}`,
          });
          resolve(false);
        } else {
          conn.subscriptions.delete(topic);
          this.addMessage(connectionId, {
            type: 'info',
            topic,
            payload: 'Unsubscribed from topic',
          });
          resolve(true);
        }
      });
    });
  }

  /**
   * Get connection info
   */
  getConnection(connectionId: string): MQTTConnection | null {
    return this.connections.get(connectionId) || null;
  }

  /**
   * Get all connections
   */
  getAllConnections(): MQTTConnection[] {
    return Array.from(this.connections.values());
  }

  /**
   * Get messages
   */
  getMessages(connectionId: string): MQTTMessage[] {
    const conn = this.connections.get(connectionId);
    return conn?.messages || [];
  }

  /**
   * Get subscriptions
   */
  getSubscriptions(connectionId: string): Array<{ topic: string; qos: number }> {
    const conn = this.connections.get(connectionId);
    if (!conn) return [];

    return Array.from(conn.subscriptions.entries()).map(([topic, qos]) => ({
      topic,
      qos,
    }));
  }

  /**
   * Clear messages
   */
  clearMessages(connectionId: string): boolean {
    const conn = this.connections.get(connectionId);
    if (conn) {
      conn.messages = [];
      return true;
    }
    return false;
  }

  /**
   * Remove connection
   */
  async removeConnection(connectionId: string): Promise<boolean> {
    const conn = this.connections.get(connectionId);
    if (conn) {
      await this.disconnect(connectionId);
      this.connections.delete(connectionId);
      return true;
    }
    return false;
  }

  /**
   * Add message to connection
   */
  private addMessage(
    connectionId: string,
    message: Omit<MQTTMessage, 'id' | 'timestamp' | 'parsedPayload'>
  ): void {
    const conn = this.connections.get(connectionId);
    if (conn) {
      const msg: MQTTMessage = {
        id: this.generateId(),
        timestamp: new Date(),
        parsedPayload: this.tryParseJSON(message.payload),
        ...message,
      };

      conn.messages.push(msg);

      // Limit messages to 1000 entries
      if (conn.messages.length > 1000) {
        conn.messages.shift();
      }
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
    const conn = this.connections.get(connectionId);
    return conn?.status || null;
  }

  /**
   * Get message statistics
   */
  getStatistics(connectionId: string): {
    totalMessages: number;
    publishedCount: number;
    receivedCount: number;
    subscriptionCount: number;
  } | null {
    const conn = this.connections.get(connectionId);
    if (!conn) return null;

    const publishedCount = conn.messages.filter(m => m.type === 'published').length;
    const receivedCount = conn.messages.filter(m => m.type === 'received').length;

    return {
      totalMessages: conn.messages.length,
      publishedCount,
      receivedCount,
      subscriptionCount: conn.subscriptions.size,
    };
  }
}

// Singleton instance
let mqttServiceInstance: MQTTService | null = null;

export function getMQTTService(): MQTTService {
  if (!mqttServiceInstance) {
    mqttServiceInstance = new MQTTService();
  }
  return mqttServiceInstance;
}
