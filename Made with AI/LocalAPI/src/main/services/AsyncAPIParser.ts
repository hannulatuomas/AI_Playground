// AsyncAPI Parser Service
// Parses AsyncAPI specifications for event-driven APIs

import { Parser } from '@asyncapi/parser';

interface AsyncAPIInfo {
  title: string;
  version: string;
  description?: string;
  channels: ChannelInfo[];
  messages: MessageInfo[];
  servers: ServerInfo[];
}

interface ServerInfo {
  name: string;
  url: string;
  protocol: string;
  description?: string;
}

interface ChannelInfo {
  name: string;
  description?: string;
  operations: OperationInfo[];
  parameters?: ParameterInfo[];
}

interface OperationInfo {
  type: 'publish' | 'subscribe';
  summary?: string;
  description?: string;
  message?: string;
}

interface MessageInfo {
  name: string;
  title?: string;
  summary?: string;
  description?: string;
  payload?: any;
  headers?: any;
  contentType?: string;
}

interface ParameterInfo {
  name: string;
  description?: string;
  schema?: any;
}

export class AsyncAPIParser {
  /**
   * Parse AsyncAPI specification from object
   */
  async parseFromObject(spec: any): Promise<AsyncAPIInfo> {
    try {
      const parser = new Parser();
      const document = await parser.parse(JSON.stringify(spec));

      if (!document.document) {
        throw new Error('Invalid AsyncAPI document');
      }

      const doc = document.document;

      return {
        title: doc.info().title(),
        version: doc.info().version(),
        description: doc.info().description(),
        channels: this.extractChannels(doc),
        messages: this.extractMessages(doc),
        servers: this.extractServers(doc),
      };
    } catch (error: any) {
      throw new Error(`Failed to parse AsyncAPI spec: ${error.message}`);
    }
  }

  /**
   * Parse AsyncAPI specification from JSON string
   */
  async parseFromJSON(json: string): Promise<AsyncAPIInfo> {
    try {
      const spec = JSON.parse(json);
      return await this.parseFromObject(spec);
    } catch (error: any) {
      throw new Error(`Failed to parse JSON: ${error.message}`);
    }
  }

  /**
   * Parse AsyncAPI specification from YAML string
   */
  async parseFromYAML(yaml: string): Promise<AsyncAPIInfo> {
    try {
      const parser = new Parser();
      const document = await parser.parse(yaml);

      if (!document.document) {
        throw new Error('Invalid AsyncAPI document');
      }

      const doc = document.document;

      return {
        title: doc.info().title(),
        version: doc.info().version(),
        description: doc.info().description(),
        channels: this.extractChannels(doc),
        messages: this.extractMessages(doc),
        servers: this.extractServers(doc),
      };
    } catch (error: any) {
      throw new Error(`Failed to parse YAML: ${error.message}`);
    }
  }

  /**
   * Extract servers from document
   */
  private extractServers(doc: any): ServerInfo[] {
    const servers: ServerInfo[] = [];

    if (doc.servers && doc.servers()) {
      const serverMap = doc.servers().all();
      for (const server of serverMap) {
        servers.push({
          name: server.id(),
          url: server.url(),
          protocol: server.protocol(),
          description: server.description(),
        });
      }
    }

    return servers;
  }

  /**
   * Extract channels from document
   */
  private extractChannels(doc: any): ChannelInfo[] {
    const channels: ChannelInfo[] = [];

    if (doc.channels && doc.channels()) {
      const channelMap = doc.channels().all();
      for (const channel of channelMap) {
        const operations: OperationInfo[] = [];

        // Check for publish operation
        if (channel.hasPublish && channel.hasPublish()) {
          const publish = channel.publish();
          operations.push({
            type: 'publish',
            summary: publish.summary?.(),
            description: publish.description?.(),
            message: publish.messages?.()[0]?.id?.(),
          });
        }

        // Check for subscribe operation
        if (channel.hasSubscribe && channel.hasSubscribe()) {
          const subscribe = channel.subscribe();
          operations.push({
            type: 'subscribe',
            summary: subscribe.summary?.(),
            description: subscribe.description?.(),
            message: subscribe.messages?.()[0]?.id?.(),
          });
        }

        const parameters: ParameterInfo[] = [];
        if (channel.parameters && channel.parameters()) {
          const paramMap = channel.parameters().all();
          for (const param of paramMap) {
            parameters.push({
              name: param.id(),
              description: param.description?.(),
              schema: param.schema?.()?.json(),
            });
          }
        }

        channels.push({
          name: channel.address(),
          description: channel.description?.(),
          operations,
          parameters: parameters.length > 0 ? parameters : undefined,
        });
      }
    }

    return channels;
  }

  /**
   * Extract messages from document
   */
  private extractMessages(doc: any): MessageInfo[] {
    const messages: MessageInfo[] = [];
    const seenMessages = new Set<string>();

    if (doc.channels && doc.channels()) {
      const channelMap = doc.channels().all();
      for (const channel of channelMap) {
        // Get messages from publish
        if (channel.hasPublish && channel.hasPublish()) {
          const publish = channel.publish();
          const msgs = publish.messages?.();
          if (msgs) {
            for (const msg of msgs) {
              const msgId = msg.id?.();
              if (msgId && !seenMessages.has(msgId)) {
                seenMessages.add(msgId);
                messages.push(this.extractMessage(msg));
              }
            }
          }
        }

        // Get messages from subscribe
        if (channel.hasSubscribe && channel.hasSubscribe()) {
          const subscribe = channel.subscribe();
          const msgs = subscribe.messages?.();
          if (msgs) {
            for (const msg of msgs) {
              const msgId = msg.id?.();
              if (msgId && !seenMessages.has(msgId)) {
                seenMessages.add(msgId);
                messages.push(this.extractMessage(msg));
              }
            }
          }
        }
      }
    }

    return messages;
  }

  /**
   * Extract message information
   */
  private extractMessage(msg: any): MessageInfo {
    return {
      name: msg.id?.() || 'Unnamed',
      title: msg.title?.(),
      summary: msg.summary?.(),
      description: msg.description?.(),
      payload: msg.payload?.()?.json(),
      headers: msg.headers?.()?.json(),
      contentType: msg.contentType?.(),
    };
  }

  /**
   * Validate AsyncAPI specification
   */
  async validate(spec: string): Promise<{ valid: boolean; errors?: string[] }> {
    try {
      const parser = new Parser();
      const document = await parser.parse(spec);

      if (document.diagnostics && document.diagnostics.length > 0) {
        return {
          valid: false,
          errors: document.diagnostics.map((d: any) => d.message),
        };
      }

      return { valid: true };
    } catch (error: any) {
      return {
        valid: false,
        errors: [error.message],
      };
    }
  }

  /**
   * Generate example message payload
   */
  generateExamplePayload(message: MessageInfo): any {
    if (!message.payload) return {};

    return this.generateExample(message.payload);
  }

  /**
   * Generate example from schema
   */
  private generateExample(schema: any): any {
    if (!schema) return null;

    if (schema.example !== undefined) {
      return schema.example;
    }

    if (schema.type === 'object' && schema.properties) {
      const example: any = {};
      for (const [key, prop] of Object.entries(schema.properties)) {
        example[key] = this.generateExample(prop);
      }
      return example;
    }

    if (schema.type === 'array' && schema.items) {
      return [this.generateExample(schema.items)];
    }

    switch (schema.type) {
      case 'string':
        return schema.enum ? schema.enum[0] : 'string';
      case 'number':
      case 'integer':
        return 0;
      case 'boolean':
        return false;
      default:
        return null;
    }
  }
}

// Singleton instance
let asyncAPIParserInstance: AsyncAPIParser | null = null;

export function getAsyncAPIParser(): AsyncAPIParser {
  if (!asyncAPIParserInstance) {
    asyncAPIParserInstance = new AsyncAPIParser();
  }
  return asyncAPIParserInstance;
}
