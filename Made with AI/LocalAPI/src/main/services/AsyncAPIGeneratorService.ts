/**
 * AsyncAPIGeneratorService - AsyncAPI 2.x/3.x Specification Generator
 * 
 * Generates comprehensive AsyncAPI specifications for event-driven APIs
 * Supports: WebSocket, SSE, MQTT, AMQP
 * 
 * Features:
 * - Server detection with protocol analysis
 * - Channel detection from message patterns
 * - Bidirectional message flow (publish/subscribe)
 * - Message schema inference
 * - Component message extraction
 * - Examples from actual messages
 * - Multiple protocol support
 */

import type { ConsoleEntry } from './ConsoleService';
import type { JSONSchema } from './RequestAnalyzerService';

export interface AsyncAPISpec {
  asyncapi: string;
  info: {
    title: string;
    version: string;
    description?: string;
    contact?: {
      name?: string;
      email?: string;
      url?: string;
    };
    license?: {
      name: string;
      url?: string;
    };
  };
  servers: Record<string, ServerObject>;
  channels: Record<string, ChannelObject>;
  components?: {
    messages?: Record<string, MessageObject>;
    schemas?: Record<string, JSONSchema>;
  };
}

export interface ServerObject {
  url: string;
  protocol: 'ws' | 'wss' | 'sse' | 'http' | 'https' | 'mqtt' | 'mqtts' | 'amqp' | 'amqps';
  description?: string;
  protocolVersion?: string;
  variables?: Record<string, ServerVariable>;
}

export interface ServerVariable {
  enum?: string[];
  default?: string;
  description?: string;
}

export interface ChannelObject {
  description?: string;
  subscribe?: OperationObject;
  publish?: OperationObject;
  parameters?: Record<string, ParameterObject>;
}

export interface ParameterObject {
  description?: string;
  schema: JSONSchema;
}

export interface OperationObject {
  summary?: string;
  description?: string;
  operationId?: string;
  message: MessageReference | { oneOf: MessageReference[] };
  tags?: Array<{ name: string }>;
}

export interface MessageReference {
  $ref?: string;
  name?: string;
  title?: string;
  summary?: string;
  description?: string;
  payload: JSONSchema;
  headers?: JSONSchema;
  correlationId?: {
    location: string;
  };
  examples?: Array<{ 
    name?: string;
    summary?: string;
    payload: any;
    headers?: any;
  }>;
}

export interface MessageObject extends MessageReference {}

export interface GeneratorOptions {
  title: string;
  version: string;
  description?: string;
  includeExamples?: boolean;
  extractComponents?: boolean;
  contact?: {
    name?: string;
    email?: string;
    url?: string;
  };
  license?: {
    name: string;
    url?: string;
  };
}

export class AsyncAPIGeneratorService {
  /**
   * Generate comprehensive AsyncAPI specification
   */
  generateSpec(entries: ConsoleEntry[], options: GeneratorOptions): AsyncAPISpec {
    const eventEntries = entries.filter(e => 
      e.type === 'websocket' || 
      e.type === 'sse' || 
      e.connectionId // Any entry with connection ID is likely event-driven
    );
    
    if (eventEntries.length === 0) {
      // Return minimal valid spec
      return this.createMinimalSpec(options);
    }

    const spec: AsyncAPISpec = {
      asyncapi: '2.6.0',
      info: {
        title: options.title,
        version: options.version,
        description: options.description,
        contact: options.contact,
        license: options.license,
      },
      servers: this.detectServers(eventEntries),
      channels: this.detectChannels(eventEntries, options),
    };

    // Add components if extraction enabled
    if (options.extractComponents) {
      const components = this.extractComponents(eventEntries, options);
      if (Object.keys(components.messages || {}).length > 0 || 
          Object.keys(components.schemas || {}).length > 0) {
        spec.components = components;
      }
    }

    return spec;
  }

  /**
   * Detect servers from event entries
   */
  private detectServers(entries: ConsoleEntry[]): Record<string, ServerObject> {
    const servers: Record<string, ServerObject> = {};
    const protocolData = new Map<string, { urls: Set<string>; versions: Set<string> }>();
    
    for (const entry of entries) {
      let protocol: string | null = null;
      let url: string | null = null;
      let version: string | null = null;

      // Detect protocol
      if (entry.type === 'websocket' || entry.protocol?.toLowerCase().includes('websocket')) {
        protocol = entry.url?.startsWith('wss://') ? 'wss' : 'ws';
        url = this.extractBaseUrl(entry.url || '');
        version = entry.protocol?.includes('13') ? '13' : null;
      } else if (entry.type === 'sse' || entry.protocol?.toLowerCase().includes('sse')) {
        protocol = entry.url?.startsWith('https://') ? 'https' : 'http';
        url = this.extractBaseUrl(entry.url || '');
      } else if (entry.protocol?.toLowerCase().includes('mqtt')) {
        protocol = entry.protocol.toLowerCase().includes('secure') ? 'mqtts' : 'mqtt';
        url = 'mqtt://localhost:1883';
        version = entry.protocol?.includes('5') ? '5.0' : '3.1.1';
      } else if (entry.protocol?.toLowerCase().includes('amqp')) {
        protocol = entry.protocol.toLowerCase().includes('secure') ? 'amqps' : 'amqp';
        url = 'amqp://localhost:5672';
        version = '0.9.1';
      }

      if (protocol && url) {
        if (!protocolData.has(protocol)) {
          protocolData.set(protocol, { urls: new Set(), versions: new Set() });
        }
        const data = protocolData.get(protocol)!;
        data.urls.add(url);
        if (version) data.versions.add(version);
      }
    }

    // Create server objects
    protocolData.forEach((data, protocol) => {
      const url = Array.from(data.urls)[0]; // Use first URL
      const version = Array.from(data.versions)[0]; // Use first version
      
      servers[`${protocol}Server`] = {
        url,
        protocol: protocol as any,
        description: this.getProtocolDescription(protocol),
        protocolVersion: version,
      };
    });

    // If no servers detected, add default
    if (Object.keys(servers).length === 0) {
      servers['defaultServer'] = {
        url: 'ws://localhost:8080',
        protocol: 'ws',
        description: 'Default WebSocket server',
      };
    }

    return servers;
  }

  /**
   * Detect channels from message patterns
   */
  private detectChannels(entries: ConsoleEntry[], options: GeneratorOptions): Record<string, ChannelObject> {
    const channels: Record<string, ChannelObject> = {};
    const channelData = new Map<string, {
      sent: ConsoleEntry[];
      received: ConsoleEntry[];
      eventTypes: Set<string>;
    }>();

    // Group entries by channel
    for (const entry of entries) {
      const channelName = this.extractChannelName(entry);
      
      if (!channelData.has(channelName)) {
        channelData.set(channelName, {
          sent: [],
          received: [],
          eventTypes: new Set(),
        });
      }

      const data = channelData.get(channelName)!;
      
      if (entry.direction === 'sent') {
        data.sent.push(entry);
      } else if (entry.direction === 'received') {
        data.received.push(entry);
      }
      
      if (entry.eventType) {
        data.eventTypes.add(entry.eventType);
      }
    }

    // Create channel objects
    channelData.forEach((data, channelName) => {
      const channel: ChannelObject = {
        description: `Channel for ${channelName} messages`,
      };

      // Add publish operation (client sends to server)
      if (data.sent.length > 0) {
        channel.publish = this.createOperation(
          data.sent,
          'publish',
          channelName,
          options
        );
      }

      // Add subscribe operation (client receives from server)
      if (data.received.length > 0) {
        channel.subscribe = this.createOperation(
          data.received,
          'subscribe',
          channelName,
          options
        );
      }

      channels[channelName] = channel;
    });

    return channels;
  }

  /**
   * Create operation object
   */
  private createOperation(
    entries: ConsoleEntry[],
    type: 'publish' | 'subscribe',
    channelName: string,
    options: GeneratorOptions
  ): OperationObject {
    const messages: MessageReference[] = [];
    const messagesByType = new Map<string, ConsoleEntry[]>();

    // Group by event type or message pattern
    for (const entry of entries) {
      const messageType = entry.eventType || 'message';
      if (!messagesByType.has(messageType)) {
        messagesByType.set(messageType, []);
      }
      messagesByType.get(messageType)!.push(entry);
    }

    // Create message for each type
    messagesByType.forEach((typeEntries, messageType) => {
      const message = this.createMessage(typeEntries, messageType, options);
      messages.push(message);
    });

    const operation: OperationObject = {
      summary: `${type === 'publish' ? 'Send' : 'Receive'} messages on ${channelName}`,
      operationId: `${type}_${channelName}`.replace(/[^a-zA-Z0-9_]/g, '_'),
      message: messages.length === 1 ? messages[0] : { oneOf: messages },
    };

    return operation;
  }

  /**
   * Create message object
   */
  private createMessage(
    entries: ConsoleEntry[],
    messageType: string,
    options: GeneratorOptions
  ): MessageReference {
    // Infer schema from message bodies
    const schemas: JSONSchema[] = [];
    const examples: any[] = [];

    for (const entry of entries) {
      if (entry.body) {
        schemas.push(this.inferSchema(entry.body));
        if (options.includeExamples && examples.length < 3) {
          examples.push(entry.body);
        }
      }
    }

    // Merge schemas
    const payload = schemas.length > 0
      ? schemas.reduce((acc, schema) => this.mergeSchemas(acc, schema))
      : { type: 'object' };

    const message: MessageReference = {
      name: messageType,
      title: this.formatMessageTitle(messageType),
      summary: `${messageType} message`,
      payload,
    };

    // Add examples
    if (options.includeExamples && examples.length > 0) {
      message.examples = examples.map((ex, i) => ({
        name: `example${i + 1}`,
        payload: ex,
      }));
    }

    return message;
  }

  /**
   * Extract components (messages and schemas)
   */
  private extractComponents(entries: ConsoleEntry[], options: GeneratorOptions): {
    messages?: Record<string, MessageObject>;
    schemas?: Record<string, JSONSchema>;
  } {
    const messages: Record<string, MessageObject> = {};
    const schemas: Record<string, JSONSchema> = {};
    
    const messageTypes = new Map<string, ConsoleEntry[]>();

    // Group by message type
    for (const entry of entries) {
      const messageType = entry.eventType || 'Message';
      if (!messageTypes.has(messageType)) {
        messageTypes.set(messageType, []);
      }
      messageTypes.get(messageType)!.push(entry);
    }

    // Create component messages
    messageTypes.forEach((typeEntries, messageType) => {
      const message = this.createMessage(typeEntries, messageType, options);
      const componentName = this.formatComponentName(messageType);
      
      messages[componentName] = message as MessageObject;
      
      // Extract schema
      if (message.payload.type === 'object' && message.payload.properties) {
        schemas[`${componentName}Payload`] = message.payload;
      }
    });

    return { messages, schemas };
  }

  /**
   * Infer JSON schema from data
   */
  private inferSchema(data: any): JSONSchema {
    if (data === null || data === undefined) {
      return { type: 'null' };
    }

    if (Array.isArray(data)) {
      if (data.length === 0) {
        return { type: 'array', items: { type: 'object' } };
      }
      const itemSchema = this.inferSchema(data[0]);
      return { type: 'array', items: itemSchema };
    }

    if (typeof data === 'object') {
      const properties: Record<string, JSONSchema> = {};
      for (const [key, value] of Object.entries(data)) {
        properties[key] = this.inferSchema(value);
      }
      return { type: 'object', properties };
    }

    const type = typeof data;
    return { type, example: data };
  }

  /**
   * Merge two schemas
   */
  private mergeSchemas(schema1: JSONSchema, schema2: JSONSchema): JSONSchema {
    if (schema1.type !== schema2.type) {
      return schema1; // Fallback
    }

    if (schema1.type === 'object' && schema1.properties && schema2.properties) {
      const merged: JSONSchema = { type: 'object', properties: { ...schema1.properties } };
      
      for (const [key, value] of Object.entries(schema2.properties)) {
        if (merged.properties![key]) {
          merged.properties![key] = this.mergeSchemas(merged.properties![key], value);
        } else {
          merged.properties![key] = value;
        }
      }
      
      return merged;
    }

    return schema1;
  }

  /**
   * Extract channel name from entry
   */
  private extractChannelName(entry: ConsoleEntry): string {
    if (entry.eventType) {
      return entry.eventType;
    }
    if (entry.url) {
      const match = entry.url.match(/\/([^\/\?]+)(?:\?|$)/);
      if (match) return match[1];
    }
    return entry.connectionId || 'messages';
  }

  /**
   * Extract base URL
   */
  private extractBaseUrl(url: string): string {
    try {
      const urlObj = new URL(url);
      return `${urlObj.protocol}//${urlObj.host}`;
    } catch {
      return url;
    }
  }

  /**
   * Get protocol description
   */
  private getProtocolDescription(protocol: string): string {
    const descriptions: Record<string, string> = {
      'ws': 'WebSocket server',
      'wss': 'Secure WebSocket server',
      'http': 'HTTP server for SSE',
      'https': 'Secure HTTP server for SSE',
      'mqtt': 'MQTT broker',
      'mqtts': 'Secure MQTT broker',
      'amqp': 'AMQP broker',
      'amqps': 'Secure AMQP broker',
    };
    return descriptions[protocol] || `${protocol.toUpperCase()} server`;
  }

  /**
   * Format message title
   */
  private formatMessageTitle(messageType: string): string {
    return messageType
      .split(/[_-]/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  /**
   * Format component name
   */
  private formatComponentName(name: string): string {
    return name
      .split(/[_-]/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join('');
  }

  /**
   * Create minimal valid spec
   */
  private createMinimalSpec(options: GeneratorOptions): AsyncAPISpec {
    return {
      asyncapi: '2.6.0',
      info: {
        title: options.title,
        version: options.version,
        description: options.description || 'No event-driven API traffic detected',
      },
      servers: {
        defaultServer: {
          url: 'ws://localhost:8080',
          protocol: 'ws',
          description: 'Default WebSocket server',
        },
      },
      channels: {},
    };
  }

  /**
   * Validate AsyncAPI spec
   */
  validateSpec(spec: AsyncAPISpec): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!spec.info?.title) {
      errors.push('Spec must have a title');
    }

    if (!spec.info?.version) {
      errors.push('Spec must have a version');
    }

    if (!spec.servers || Object.keys(spec.servers).length === 0) {
      errors.push('Spec must have at least one server');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  /**
   * Export to JSON
   */
  toJSON(spec: AsyncAPISpec): string {
    return JSON.stringify(spec, null, 2);
  }

  /**
   * Export to YAML
   */
  toYAML(spec: AsyncAPISpec): string {
    return this.objectToYAML(spec, 0);
  }

  /**
   * Convert object to YAML
   */
  private objectToYAML(obj: any, indent: number): string {
    const spaces = '  '.repeat(indent);
    let yaml = '';
    
    if (Array.isArray(obj)) {
      for (const item of obj) {
        if (typeof item === 'object') {
          yaml += `${spaces}-\n${this.objectToYAML(item, indent + 1)}`;
        } else {
          yaml += `${spaces}- ${item}\n`;
        }
      }
    } else if (typeof obj === 'object' && obj !== null) {
      for (const [key, value] of Object.entries(obj)) {
        if (value === undefined) continue;
        
        if (Array.isArray(value)) {
          yaml += `${spaces}${key}:\n`;
          yaml += this.objectToYAML(value, indent + 1);
        } else if (typeof value === 'object' && value !== null) {
          yaml += `${spaces}${key}:\n`;
          yaml += this.objectToYAML(value, indent + 1);
        } else if (typeof value === 'string') {
          // Only quote strings if they contain special characters or spaces
          const needsQuotes = value.includes(':') || value.includes('#') || value.includes(' ') || value.includes('\n');
          yaml += `${spaces}${key}: ${needsQuotes ? `"${value}"` : value}\n`;
        } else {
          yaml += `${spaces}${key}: ${value}\n`;
        }
      }
    }
    
    return yaml;
  }
}
