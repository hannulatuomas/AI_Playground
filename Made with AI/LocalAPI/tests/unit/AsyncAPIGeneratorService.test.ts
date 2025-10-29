/**
 * AsyncAPIGeneratorService Unit Tests
 */

import { AsyncAPIGeneratorService } from '../../src/main/services/AsyncAPIGeneratorService';
import type { ConsoleEntry } from '../../src/main/services/ConsoleService';

describe('AsyncAPIGeneratorService', () => {
  let service: AsyncAPIGeneratorService;

  beforeEach(() => {
    service = new AsyncAPIGeneratorService();
  });

  describe('generateSpec', () => {
    it('should generate AsyncAPI spec for WebSocket', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'websocket',
          url: 'ws://localhost:8080/chat',
          direction: 'sent',
          body: { message: 'Hello' },
        },
      ];

      const options = {
        title: 'Chat API',
        version: '1.0.0',
      };

      const spec = service.generateSpec(entries, options);

      expect(spec.asyncapi).toBe('2.6.0');
      expect(spec.info.title).toBe('Chat API');
      expect(spec.servers.wsServer).toBeDefined();
      expect(spec.servers.wsServer.protocol).toBe('ws');
    });

    it('should detect channels from event types', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'websocket',
          eventType: 'chat.message',
          direction: 'sent',
          body: { text: 'Hello' },
        },
        {
          id: '2',
          timestamp: Date.now(),
          type: 'websocket',
          eventType: 'chat.message',
          direction: 'received',
          body: { text: 'Hi' },
        },
      ];

      const spec = service.generateSpec(entries, {
        title: 'API',
        version: '1.0',
      });

      expect(spec.channels['chat.message']).toBeDefined();
      expect(spec.channels['chat.message'].publish).toBeDefined();
      expect(spec.channels['chat.message'].subscribe).toBeDefined();
    });

    it('should include examples when enabled', () => {
      const entries: ConsoleEntry[] = [
        {
          id: '1',
          timestamp: Date.now(),
          type: 'websocket',
          eventType: 'notification',
          direction: 'received',
          body: { type: 'info', message: 'Test' },
        },
      ];

      const spec = service.generateSpec(entries, {
        title: 'API',
        version: '1.0',
        includeExamples: true,
      });

      const operation = spec.channels['notification'].subscribe!;
      const message = operation.message as any;
      expect(message.examples).toBeDefined();
    });

    it('should return minimal spec for no entries', () => {
      const spec = service.generateSpec([], {
        title: 'Empty API',
        version: '1.0',
      });

      expect(spec.asyncapi).toBe('2.6.0');
      expect(spec.info.title).toBe('Empty API');
      expect(spec.servers.defaultServer).toBeDefined();
      expect(Object.keys(spec.channels)).toHaveLength(0);
    });
  });

  describe('validateSpec', () => {
    it('should validate valid spec', () => {
      const spec = {
        asyncapi: '2.6.0',
        info: { title: 'API', version: '1.0.0' },
        servers: { default: { url: 'ws://localhost', protocol: 'ws' as const } },
        channels: {},
      };

      const result = service.validateSpec(spec);
      expect(result.valid).toBe(true);
    });

    it('should detect missing title', () => {
      const spec = {
        asyncapi: '2.6.0',
        info: { title: '', version: '1.0.0' },
        servers: {},
        channels: {},
      };

      const result = service.validateSpec(spec);
      expect(result.valid).toBe(false);
    });
  });

  describe('toJSON', () => {
    it('should export as JSON', () => {
      const spec = {
        asyncapi: '2.6.0',
        info: { title: 'API', version: '1.0' },
        servers: {},
        channels: {},
      };

      const json = service.toJSON(spec);
      expect(JSON.parse(json).asyncapi).toBe('2.6.0');
    });
  });

  describe('toYAML', () => {
    it('should export as YAML', () => {
      const spec = {
        asyncapi: '2.6.0',
        info: { title: 'API', version: '1.0' },
        servers: {},
        channels: {},
      };

      const yaml = service.toYAML(spec);
      expect(yaml).toContain('asyncapi: 2.6.0');
    });
  });
});
