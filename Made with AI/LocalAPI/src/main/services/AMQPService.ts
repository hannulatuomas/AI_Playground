// AMQP Service (JMS)
// Handles AMQP connections for message queue operations

import * as amqp from 'amqplib';

interface AMQPConnection {
  id: string;
  url: string;
  connection: amqp.Connection | null;
  channel: amqp.Channel | null;
  status: 'connecting' | 'connected' | 'disconnected' | 'error';
  messages: Message[];
  queues: Set<string>;
  exchanges: Set<string>;
  createdAt: Date;
}

interface Message {
  id: string;
  timestamp: Date;
  type: 'sent' | 'received' | 'error' | 'info';
  queue?: string;
  exchange?: string;
  routingKey?: string;
  content: string;
  properties?: any;
  parsedContent?: any;
}

interface SendMessageOptions {
  connectionId: string;
  queue?: string;
  exchange?: string;
  routingKey?: string;
  message: string;
  properties?: amqp.Options.Publish;
}

interface ConsumeOptions {
  connectionId: string;
  queue: string;
  autoAck?: boolean;
}

export class AMQPService {
  private connections: Map<string, AMQPConnection> = new Map();
  private consumers: Map<string, amqp.Replies.Consume> = new Map();

  /**
   * Create AMQP connection
   */
  async connect(url: string): Promise<string> {
    const connectionId = this.generateId();

    const conn: AMQPConnection = {
      id: connectionId,
      url,
      connection: null,
      channel: null,
      status: 'connecting',
      messages: [],
      queues: new Set(),
      exchanges: new Set(),
      createdAt: new Date(),
    };

    this.connections.set(connectionId, conn);

    try {
      this.addMessage(connectionId, {
        type: 'info',
        content: `Connecting to ${url}...`,
      });

      // Create connection
      const connection = await amqp.connect(url);
      conn.connection = connection as any;

      // Create channel
      const channel = await connection.createChannel();
      conn.channel = channel as any;

      conn.status = 'connected';
      this.addMessage(connectionId, {
        type: 'info',
        content: 'Connection established',
      });

      // Handle connection errors
      connection.on('error', (error: Error) => {
        conn.status = 'error';
        this.addMessage(connectionId, {
          type: 'error',
          content: `Connection error: ${error.message}`,
        });
      });

      connection.on('close', () => {
        conn.status = 'disconnected';
        this.addMessage(connectionId, {
          type: 'info',
          content: 'Connection closed',
        });
      });

      // Handle channel errors
      channel.on('error', (error: Error) => {
        this.addMessage(connectionId, {
          type: 'error',
          content: `Channel error: ${error.message}`,
        });
      });

      channel.on('close', () => {
        this.addMessage(connectionId, {
          type: 'info',
          content: 'Channel closed',
        });
      });
    } catch (error: any) {
      conn.status = 'error';
      this.addMessage(connectionId, {
        type: 'error',
        content: `Connection failed: ${error.message}`,
      });
    }

    return connectionId;
  }

  /**
   * Disconnect from AMQP
   */
  async disconnect(connectionId: string): Promise<boolean> {
    const conn = this.connections.get(connectionId);

    if (!conn) return false;

    try {
      if (conn.channel) {
        await (conn.channel as any).close();
      }
      if (conn.connection) {
        await (conn.connection as any).close();
      }

      conn.status = 'disconnected';
      this.addMessage(connectionId, {
        type: 'info',
        content: 'Disconnected',
      });

      return true;
    } catch (error: any) {
      this.addMessage(connectionId, {
        type: 'error',
        content: `Disconnect failed: ${error.message}`,
      });
      return false;
    }
  }

  /**
   * Assert queue (create if doesn't exist)
   */
  async assertQueue(
    connectionId: string,
    queueName: string,
    options?: amqp.Options.AssertQueue
  ): Promise<boolean> {
    const conn = this.connections.get(connectionId);

    if (!conn || !conn.channel) return false;

    try {
      await conn.channel.assertQueue(queueName, options);
      conn.queues.add(queueName);
      this.addMessage(connectionId, {
        type: 'info',
        content: `Queue asserted: ${queueName}`,
        queue: queueName,
      });
      return true;
    } catch (error: any) {
      this.addMessage(connectionId, {
        type: 'error',
        content: `Failed to assert queue: ${error.message}`,
      });
      return false;
    }
  }

  /**
   * Assert exchange
   */
  async assertExchange(
    connectionId: string,
    exchangeName: string,
    type: string,
    options?: amqp.Options.AssertExchange
  ): Promise<boolean> {
    const conn = this.connections.get(connectionId);

    if (!conn || !conn.channel) return false;

    try {
      await conn.channel.assertExchange(exchangeName, type, options);
      conn.exchanges.add(exchangeName);
      this.addMessage(connectionId, {
        type: 'info',
        content: `Exchange asserted: ${exchangeName} (${type})`,
        exchange: exchangeName,
      });
      return true;
    } catch (error: any) {
      this.addMessage(connectionId, {
        type: 'error',
        content: `Failed to assert exchange: ${error.message}`,
      });
      return false;
    }
  }

  /**
   * Bind queue to exchange
   */
  async bindQueue(
    connectionId: string,
    queue: string,
    exchange: string,
    routingKey: string
  ): Promise<boolean> {
    const conn = this.connections.get(connectionId);

    if (!conn || !conn.channel) return false;

    try {
      await conn.channel.bindQueue(queue, exchange, routingKey);
      this.addMessage(connectionId, {
        type: 'info',
        content: `Queue bound: ${queue} -> ${exchange} (${routingKey})`,
        queue,
        exchange,
        routingKey,
      });
      return true;
    } catch (error: any) {
      this.addMessage(connectionId, {
        type: 'error',
        content: `Failed to bind queue: ${error.message}`,
      });
      return false;
    }
  }

  /**
   * Send message to queue
   */
  async sendToQueue(options: SendMessageOptions): Promise<boolean> {
    const conn = this.connections.get(options.connectionId);

    if (!conn || !conn.channel || !options.queue) return false;

    try {
      const buffer = Buffer.from(options.message);
      const sent = conn.channel.sendToQueue(
        options.queue,
        buffer,
        options.properties
      );

      if (sent) {
        this.addMessage(options.connectionId, {
          type: 'sent',
          queue: options.queue,
          content: options.message,
          properties: options.properties,
        });
      }

      return sent;
    } catch (error: any) {
      this.addMessage(options.connectionId, {
        type: 'error',
        content: `Failed to send message: ${error.message}`,
      });
      return false;
    }
  }

  /**
   * Publish message to exchange
   */
  async publish(options: SendMessageOptions): Promise<boolean> {
    const conn = this.connections.get(options.connectionId);

    if (!conn || !conn.channel || !options.exchange) return false;

    try {
      const buffer = Buffer.from(options.message);
      const published = conn.channel.publish(
        options.exchange,
        options.routingKey || '',
        buffer,
        options.properties
      );

      if (published) {
        this.addMessage(options.connectionId, {
          type: 'sent',
          exchange: options.exchange,
          routingKey: options.routingKey,
          content: options.message,
          properties: options.properties,
        });
      }

      return published;
    } catch (error: any) {
      this.addMessage(options.connectionId, {
        type: 'error',
        content: `Failed to publish message: ${error.message}`,
      });
      return false;
    }
  }

  /**
   * Start consuming messages from queue
   */
  async consume(options: ConsumeOptions): Promise<boolean> {
    const conn = this.connections.get(options.connectionId);

    if (!conn || !conn.channel) return false;

    try {
      const consumerTag = `${options.connectionId}-${options.queue}`;

      const result = await conn.channel.consume(
        options.queue,
        (msg) => {
          if (msg) {
            const content = msg.content.toString();
            this.addMessage(options.connectionId, {
              type: 'received',
              queue: options.queue,
              content,
              properties: msg.properties,
              routingKey: msg.fields.routingKey,
            });

            if (options.autoAck !== false) {
              conn.channel?.ack(msg);
            }
          }
        },
        { noAck: options.autoAck !== false }
      );

      this.consumers.set(consumerTag, result);

      this.addMessage(options.connectionId, {
        type: 'info',
        content: `Started consuming from queue: ${options.queue}`,
        queue: options.queue,
      });

      return true;
    } catch (error: any) {
      this.addMessage(options.connectionId, {
        type: 'error',
        content: `Failed to consume: ${error.message}`,
      });
      return false;
    }
  }

  /**
   * Stop consuming messages
   */
  async stopConsuming(connectionId: string, queue: string): Promise<boolean> {
    const conn = this.connections.get(connectionId);

    if (!conn || !conn.channel) return false;

    try {
      const consumerTag = `${connectionId}-${queue}`;
      const consumer = this.consumers.get(consumerTag);

      if (consumer) {
        await conn.channel.cancel(consumer.consumerTag);
        this.consumers.delete(consumerTag);

        this.addMessage(connectionId, {
          type: 'info',
          content: `Stopped consuming from queue: ${queue}`,
          queue,
        });
      }

      return true;
    } catch (error: any) {
      this.addMessage(connectionId, {
        type: 'error',
        content: `Failed to stop consuming: ${error.message}`,
      });
      return false;
    }
  }

  /**
   * Get connection info
   */
  getConnection(connectionId: string): AMQPConnection | null {
    return this.connections.get(connectionId) || null;
  }

  /**
   * Get all connections
   */
  getAllConnections(): AMQPConnection[] {
    return Array.from(this.connections.values());
  }

  /**
   * Get messages
   */
  getMessages(connectionId: string): Message[] {
    const conn = this.connections.get(connectionId);
    return conn?.messages || [];
  }

  /**
   * Get queues
   */
  getQueues(connectionId: string): string[] {
    const conn = this.connections.get(connectionId);
    return conn ? Array.from(conn.queues) : [];
  }

  /**
   * Get exchanges
   */
  getExchanges(connectionId: string): string[] {
    const conn = this.connections.get(connectionId);
    return conn ? Array.from(conn.exchanges) : [];
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
    message: Omit<Message, 'id' | 'timestamp' | 'parsedContent'>
  ): void {
    const conn = this.connections.get(connectionId);
    if (conn) {
      const msg: Message = {
        id: this.generateId(),
        timestamp: new Date(),
        parsedContent: this.tryParseJSON(message.content),
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
}

// Singleton instance
let amqpServiceInstance: AMQPService | null = null;

export function getAMQPService(): AMQPService {
  if (!amqpServiceInstance) {
    amqpServiceInstance = new AMQPService();
  }
  return amqpServiceInstance;
}
