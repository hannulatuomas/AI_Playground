// ExportService Tests
import { ExportService } from '../../src/main/services/ExportService';
import { PostmanExporter } from '../../src/main/services/exporters/PostmanExporter';
import { CurlExporter } from '../../src/main/services/exporters/CurlExporter';
import { OpenAPIExporter } from '../../src/main/services/exporters/OpenAPIExporter';
import { InsomniaExporter } from '../../src/main/services/exporters/InsomniaExporter';
import { HARExporter } from '../../src/main/services/exporters/HARExporter';
import { GraphQLExporter } from '../../src/main/services/exporters/GraphQLExporter';
import { AsyncAPIExporter } from '../../src/main/services/exporters/AsyncAPIExporter';
import { SoapUIExporter } from '../../src/main/services/exporters/SoapUIExporter';
import { RAMLExporter } from '../../src/main/services/exporters/RAMLExporter';
import { WADLExporter } from '../../src/main/services/exporters/WADLExporter';
import { ProtobufExporter } from '../../src/main/services/exporters/ProtobufExporter';
import { WSDLExporter } from '../../src/main/services/exporters/WSDLExporter';
import type { DatabaseService } from '../../src/main/services/DatabaseService';
import type { Collection, Request } from '../../src/types/models';

// Mock DatabaseService
const mockDb = {
  getCollectionById: jest.fn(),
  getRequestsByCollection: jest.fn(),
  getRequestById: jest.fn(),
} as unknown as DatabaseService;

describe('ExportService', () => {
  let exportService: ExportService;

  beforeEach(() => {
    exportService = new ExportService(mockDb);
    jest.clearAllMocks();
  });

  describe('Generator Registration', () => {
    it('should register a generator', () => {
      const generator = new PostmanExporter();
      exportService.registerGenerator(generator);

      const generators = exportService.getGenerators();
      expect(generators).toHaveLength(1);
      expect(generators[0].format).toBe('postman-v2.1');
    });

    it('should unregister a generator', () => {
      const generator = new PostmanExporter();
      exportService.registerGenerator(generator);
      exportService.unregisterGenerator('postman-v2.1');

      const generators = exportService.getGenerators();
      expect(generators).toHaveLength(0);
    });

    it('should get generator by format', () => {
      const generator = new PostmanExporter();
      exportService.registerGenerator(generator);

      const retrieved = exportService.getGenerator('postman-v2.1');
      expect(retrieved).toBeDefined();
      expect(retrieved?.format).toBe('postman-v2.1');
    });
  });

  describe('Export Collections', () => {
    beforeEach(() => {
      exportService.registerGenerator(new PostmanExporter());
      exportService.registerGenerator(new CurlExporter());
      exportService.registerGenerator(new OpenAPIExporter());
    });

    it('should export collection to Postman format', async () => {
      const mockCollection: Collection = {
        id: 'col-1',
        name: 'Test Collection',
        description: 'Test',
        requests: [],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      mockDb.getCollectionById = jest.fn().mockResolvedValue(mockCollection);
      mockDb.getRequestsByCollection = jest.fn().mockResolvedValue([]);

      const result = await exportService.exportCollections(['col-1'], 'postman-v2.1');

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.format).toBe('postman-v2.1');
    });

    it('should handle export errors', async () => {
      mockDb.getCollectionById = jest.fn().mockResolvedValue(null);

      const result = await exportService.exportCollections(['col-1'], 'postman-v2.1');

      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
    });
  });

  describe('Export Request', () => {
    beforeEach(() => {
      exportService.registerGenerator(new CurlExporter());
    });

    it('should export single request to cURL', async () => {
      const mockRequest: Request = {
        id: 'req-1',
        name: 'Test Request',
        description: '',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com/users',
        headers: [],
        queryParams: [],
        collectionId: 'col-1',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      mockDb.getRequestById = jest.fn().mockResolvedValue(mockRequest);

      const result = await exportService.exportRequest('req-1', 'curl');

      expect(result.success).toBe(true);
      expect(result.data).toContain('curl');
      expect(result.data).toContain('https://api.example.com/users');
    });
  });

  describe('Export History', () => {
    beforeEach(() => {
      exportService.registerGenerator(new PostmanExporter());
    });

    it('should track export history', async () => {
      const mockCollection: Collection = {
        id: 'col-1',
        name: 'Test',
        description: '',
        requests: [],
        folders: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      mockDb.getCollectionById = jest.fn().mockResolvedValue(mockCollection);
      mockDb.getRequestsByCollection = jest.fn().mockResolvedValue([]);

      await exportService.exportCollections(['col-1'], 'postman-v2.1');

      const history = exportService.getHistory();
      expect(history).toHaveLength(1);
      expect(history[0].format).toBe('postman-v2.1');
      expect(history[0].success).toBe(true);
    });

    it('should clear export history', () => {
      exportService.clearHistory();
      const history = exportService.getHistory();
      expect(history).toHaveLength(0);
    });
  });

  describe('Supported Formats', () => {
    it('should return list of supported formats', () => {
      exportService.registerGenerator(new PostmanExporter());
      exportService.registerGenerator(new CurlExporter());

      const formats = exportService.getSupportedFormats();
      expect(formats).toContain('postman-v2.1');
      expect(formats).toContain('curl');
    });
  });

  describe('All 12 Exporters', () => {
    it('should register all 12 exporters', () => {
      exportService.registerGenerator(new PostmanExporter());
      exportService.registerGenerator(new CurlExporter());
      exportService.registerGenerator(new OpenAPIExporter());
      exportService.registerGenerator(new InsomniaExporter());
      exportService.registerGenerator(new HARExporter());
      exportService.registerGenerator(new GraphQLExporter());
      exportService.registerGenerator(new AsyncAPIExporter());
      exportService.registerGenerator(new SoapUIExporter());
      exportService.registerGenerator(new RAMLExporter());
      exportService.registerGenerator(new WADLExporter());
      exportService.registerGenerator(new ProtobufExporter());
      exportService.registerGenerator(new WSDLExporter());

      const generators = exportService.getGenerators();
      expect(generators).toHaveLength(12);
    });

    it('should export to Insomnia format', async () => {
      const exporter = new InsomniaExporter();
      const mockRequest: Request = {
        id: 'req-1',
        name: 'Test',
        description: '',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com',
        headers: [],
        queryParams: [],
        collectionId: 'col-1',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const result = await exporter.exportRequest(mockRequest);
      expect(result.success).toBe(true);
      expect(result.data).toContain('_type');
    });

    it('should export to HAR format', async () => {
      const exporter = new HARExporter();
      const mockRequest: Request = {
        id: 'req-1',
        name: 'Test',
        description: '',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com',
        headers: [],
        queryParams: [],
        collectionId: 'col-1',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const result = await exporter.exportRequest(mockRequest);
      expect(result.success).toBe(true);
      expect(result.data).toContain('log');
    });

    it('should export to GraphQL format', async () => {
      const exporter = new GraphQLExporter();
      const mockRequest: Request = {
        id: 'req-1',
        name: 'getUsers',
        description: '',
        protocol: 'GraphQL',
        method: 'POST',
        url: 'https://api.example.com/graphql',
        headers: [],
        queryParams: [],
        collectionId: 'col-1',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const result = await exporter.exportRequest(mockRequest);
      expect(result.success).toBe(true);
    });

    it('should export to AsyncAPI format', async () => {
      const exporter = new AsyncAPIExporter();
      const mockRequest: Request = {
        id: 'req-1',
        name: 'Test',
        description: '',
        protocol: 'MQTT',
        method: 'POST',
        url: 'mqtt://broker.example.com/topic',
        headers: [],
        queryParams: [],
        collectionId: 'col-1',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const result = await exporter.exportRequest(mockRequest);
      expect(result.success).toBe(true);
      expect(result.data).toContain('asyncapi');
    });

    it('should export to SoapUI format', async () => {
      const exporter = new SoapUIExporter();
      const result = await exporter.exportCollections([{ name: 'Test', requests: [] }]);
      expect(result.success).toBe(true);
      expect(result.data).toContain('soapui-project');
    });

    it('should export to RAML format', async () => {
      const exporter = new RAMLExporter();
      const result = await exporter.exportCollections([{ name: 'Test', requests: [] }]);
      expect(result.success).toBe(true);
      expect(result.data).toContain('#%RAML');
    });

    it('should export to WADL format', async () => {
      const exporter = new WADLExporter();
      const result = await exporter.exportCollections([{ name: 'Test', requests: [] }]);
      expect(result.success).toBe(true);
      expect(result.data).toContain('application');
    });

    it('should export to Protobuf format', async () => {
      const exporter = new ProtobufExporter();
      const result = await exporter.exportCollections([{ name: 'Test', requests: [] }]);
      expect(result.success).toBe(true);
      expect(result.data).toContain('syntax = "proto3"');
    });

    it('should export to WSDL format', async () => {
      const exporter = new WSDLExporter();
      const result = await exporter.exportCollections([{ name: 'Test', requests: [] }]);
      expect(result.success).toBe(true);
      expect(result.data).toContain('definitions');
    });
  });

  describe('Advanced Export Features', () => {
    it('should support bulk ZIP export', () => {
      expect(exportService.exportToZip).toBeDefined();
    });

    it('should support export templates', () => {
      expect(exportService.saveTemplate).toBeDefined();
      expect(exportService.loadTemplate).toBeDefined();
      expect(exportService.listTemplates).toBeDefined();
    });

    it('should support scheduled exports', () => {
      expect(exportService.scheduleExport).toBeDefined();
    });
  });
});
