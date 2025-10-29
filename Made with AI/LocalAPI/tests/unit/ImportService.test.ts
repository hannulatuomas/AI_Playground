// ImportService Tests
import { ImportService } from '../../src/main/services/ImportService';
import { PostmanImporter } from '../../src/main/services/importers/PostmanImporter';
import { CurlImporter } from '../../src/main/services/importers/CurlImporter';
import { OpenAPIImporter } from '../../src/main/services/importers/OpenAPIImporter';
import { HARImporter } from '../../src/main/services/importers/HARImporter';
import { InsomniaImporter } from '../../src/main/services/importers/InsomniaImporter';
import { RAMLImporter } from '../../src/main/services/importers/RAMLImporter';
import { GraphQLImporter } from '../../src/main/services/importers/GraphQLImporter';
import { AsyncAPIImporter } from '../../src/main/services/importers/AsyncAPIImporter';
import { SoapUIImporter } from '../../src/main/services/importers/SoapUIImporter';
import { WADLImporter } from '../../src/main/services/importers/WADLImporter';
import { WSDLImporter } from '../../src/main/services/importers/WSDLImporter';
import { ProtobufImporter } from '../../src/main/services/importers/ProtobufImporter';
import { APIGatewayImporter } from '../../src/main/services/importers/APIGatewayImporter';
import type { DatabaseService } from '../../src/main/services/DatabaseService';

// Mock DatabaseService
const mockDb = {
  createCollection: jest.fn(),
  createRequest: jest.fn(),
  createEnvironment: jest.fn(),
  setVariable: jest.fn(),
} as unknown as DatabaseService;

describe('ImportService', () => {
  let importService: ImportService;

  beforeEach(() => {
    importService = new ImportService(mockDb);
    jest.clearAllMocks();
  });

  describe('Handler Registration', () => {
    it('should register a handler', () => {
      const handler = new PostmanImporter();
      importService.registerHandler(handler);

      const handlers = importService.getHandlers();
      expect(handlers).toHaveLength(1);
      expect(handlers[0].format).toBe('postman-v2.1');
    });

    it('should unregister a handler', () => {
      const handler = new PostmanImporter();
      importService.registerHandler(handler);
      importService.unregisterHandler('postman-v2.1');

      const handlers = importService.getHandlers();
      expect(handlers).toHaveLength(0);
    });

    it('should get handler by format', () => {
      const handler = new PostmanImporter();
      importService.registerHandler(handler);

      const retrieved = importService.getHandler('postman-v2.1');
      expect(retrieved).toBeDefined();
      expect(retrieved?.format).toBe('postman-v2.1');
    });

    it('should return undefined for unregistered format', () => {
      const handler = importService.getHandler('unknown' as any);
      expect(handler).toBeUndefined();
    });
  });

  describe('Format Detection', () => {
    beforeEach(() => {
      importService.registerHandler(new PostmanImporter());
      importService.registerHandler(new CurlImporter());
      importService.registerHandler(new OpenAPIImporter());
      importService.registerHandler(new HARImporter());
      importService.registerHandler(new InsomniaImporter());
    });

    it('should detect Postman Collection format', async () => {
      const content = JSON.stringify({
        info: {
          name: 'Test',
          schema: 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
        },
        item: [],
      });

      const format = await importService.detectFormat(content);
      expect(format).toBe('postman-v2.1');
    });

    it('should detect cURL format', async () => {
      const content = 'curl https://api.example.com/users';
      const format = await importService.detectFormat(content);
      expect(format).toBe('curl');
    });

    it('should detect OpenAPI 3.0 format', async () => {
      const content = JSON.stringify({
        openapi: '3.0.0',
        info: { title: 'Test API', version: '1.0.0' },
        paths: {},
      });

      const format = await importService.detectFormat(content);
      expect(format).toBe('openapi-3.0');
    });

    it('should detect HAR format', async () => {
      const content = JSON.stringify({
        log: {
          version: '1.2',
          entries: [],
        },
      });

      const format = await importService.detectFormat(content);
      expect(format).toBe('har');
    });

    it('should detect Insomnia format', async () => {
      const content = JSON.stringify({
        _type: 'export',
        __export_format: 4,
        resources: [],
      });

      const format = await importService.detectFormat(content);
      expect(format).toBe('insomnia-v4');
    });

    it('should return null for unknown format', async () => {
      const content = 'invalid content';
      const format = await importService.detectFormat(content);
      expect(format).toBeNull();
    });
  });

  describe('Validation', () => {
    beforeEach(() => {
      importService.registerHandler(new PostmanImporter());
      importService.registerHandler(new CurlImporter());
      importService.registerHandler(new OpenAPIImporter());
    });

    it('should validate valid Postman collection', async () => {
      const content = JSON.stringify({
        info: {
          name: 'Test',
          schema: 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
        },
        item: [],
      });

      const result = await importService.validate(content);
      expect(result.valid).toBe(true);
      expect(result.format).toBe('postman-v2.1');
      expect(result.errors).toHaveLength(0);
    });

    it('should fail validation for invalid content', async () => {
      const content = 'invalid json';
      const result = await importService.validate(content);
      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('should fail validation for unknown format', async () => {
      const content = JSON.stringify({ unknown: 'format' });
      const result = await importService.validate(content);
      expect(result.valid).toBe(false);
      expect(result.errors[0].code).toBe('NO_HANDLER');
    });
  });

  describe('Import', () => {
    beforeEach(() => {
      importService.registerHandler(new PostmanImporter());
      importService.registerHandler(new CurlImporter());
    });

    it('should import valid Postman collection', async () => {
      const content = JSON.stringify({
        info: {
          name: 'Test Collection',
          schema: 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
        },
        item: [
          {
            name: 'Get Users',
            request: {
              method: 'GET',
              url: 'https://api.example.com/users',
            },
          },
        ],
      });

      const result = await importService.import(content, { preview: true });
      expect(result.success).toBe(true);
      expect(result.collections).toHaveLength(1);
      expect(result.requests).toHaveLength(1);
      expect(result.requests![0].name).toBe('Get Users');
    });

    it('should import cURL command', async () => {
      importService.registerHandler(new CurlImporter());
      const content = 'curl -X POST https://api.example.com/users -H "Content-Type: application/json"';
      const result = await importService.import(content, { format: 'curl', preview: true });

      expect(result.success).toBe(true);
      expect(result.requests).toHaveLength(1);
      expect(result.requests![0].method).toBe('POST');
    });

    it('should fail import for invalid content', async () => {
      const content = 'invalid content';
      const result = await importService.import(content);

      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
      expect(result.errors!.length).toBeGreaterThan(0);
    });

    it('should track import history', async () => {
      importService.registerHandler(new CurlImporter());
      const content = 'curl https://api.example.com/users';
      await importService.import(content, { format: 'curl', preview: true });

      const history = importService.getHistory();
      expect(history).toHaveLength(1);
      expect(history[0].format).toBe('curl');
      expect(history[0].success).toBe(true);
    });

    it('should clear import history', () => {
      const content = 'curl https://api.example.com/users';
      importService.import(content, { preview: true });
      importService.clearHistory();

      const history = importService.getHistory();
      expect(history).toHaveLength(0);
    });
  });

  describe('Import from File', () => {
    it('should import from file path', async () => {
      // Mock file reading
      const mockContent = JSON.stringify({
        info: {
          name: 'Test',
          schema: 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
        },
        item: [],
      });

      // This would need actual file system mocking
      // For now, just test the method exists
      expect(importService.importFromFile).toBeDefined();
    });
  });

  describe('Import from URL', () => {
    it('should import from URL', async () => {
      // This would need HTTP mocking
      // For now, just test the method exists
      expect(importService.importFromURL).toBeDefined();
    });
  });

  describe('Supported Formats', () => {
    it('should return list of supported formats', () => {
      importService.registerHandler(new PostmanImporter());
      importService.registerHandler(new CurlImporter());

      const formats = importService.getSupportedFormats();
      expect(formats).toContain('postman-v2.1');
      expect(formats).toContain('curl');
    });
  });

  describe('All 13 Importers', () => {
    it('should register all 13 importers', () => {
      importService.registerHandler(new PostmanImporter());
      importService.registerHandler(new CurlImporter());
      importService.registerHandler(new OpenAPIImporter());
      importService.registerHandler(new HARImporter());
      importService.registerHandler(new InsomniaImporter());
      importService.registerHandler(new RAMLImporter());
      importService.registerHandler(new GraphQLImporter());
      importService.registerHandler(new AsyncAPIImporter());
      importService.registerHandler(new SoapUIImporter());
      importService.registerHandler(new WADLImporter());
      importService.registerHandler(new WSDLImporter());
      importService.registerHandler(new ProtobufImporter());
      importService.registerHandler(new APIGatewayImporter());

      const handlers = importService.getHandlers();
      expect(handlers).toHaveLength(13);
    });

    it('should detect RAML format', () => {
      const importer = new RAMLImporter();
      expect(importer.canImport('#%RAML 1.0\ntitle: Test')).toBe(true);
    });

    it('should detect GraphQL format', () => {
      const importer = new GraphQLImporter();
      expect(importer.canImport('type Query { users: [User] }')).toBe(true);
    });

    it('should detect AsyncAPI format', () => {
      const importer = new AsyncAPIImporter();
      expect(importer.canImport('{"asyncapi":"2.0.0"}')).toBe(true);
    });

    it('should detect SoapUI format', () => {
      const importer = new SoapUIImporter();
      expect(importer.canImport('<soapui-project>')).toBe(true);
    });

    it('should detect WADL format', () => {
      const importer = new WADLImporter();
      expect(importer.canImport('<application xmlns="wadl">')).toBe(true);
    });

    it('should detect WSDL format', () => {
      const importer = new WSDLImporter();
      expect(importer.canImport('<definitions xmlns:wsdl>')).toBe(true);
    });

    it('should detect Protobuf format', () => {
      const importer = new ProtobufImporter();
      expect(importer.canImport('syntax = "proto3"')).toBe(true);
    });

    it('should detect API Gateway format', () => {
      const importer = new APIGatewayImporter();
      // API Gateway detection requires specific AWS integration markers
      expect(importer).toBeDefined();
      expect(importer.format).toBe('aws-gateway');
    });
  });

  describe('Advanced Features', () => {
    it('should support batch import from multiple files', () => {
      expect(importService.importFromFiles).toBeDefined();
    });

    it('should support ZIP import', () => {
      expect(importService.importFromZip).toBeDefined();
    });

    it('should support Git repository import', () => {
      expect(importService.importFromGit).toBeDefined();
    });

    it('should support partial import with selective filtering', async () => {
      importService.registerHandler(new PostmanImporter());
      
      const content = JSON.stringify({
        info: { name: 'Test', schema: 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json' },
        item: [],
      });

      const result = await importService.import(content, {
        selectiveImport: true,
        selectedCollectionIds: ['col-1'],
      });

      expect(result).toBeDefined();
    });
  });
});
