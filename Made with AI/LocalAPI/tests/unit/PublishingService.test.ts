/**
 * PublishingService Unit Tests
 */

import { PublishingService } from '../../src/main/services/PublishingService';
import * as fs from 'fs';
import * as path from 'path';

// Mock fs
jest.mock('fs');

describe('PublishingService', () => {
  let service: PublishingService;

  beforeEach(() => {
    service = new PublishingService();
    jest.clearAllMocks();
  });

  afterEach(async () => {
    await service.cleanup();
  });

  const mockDoc = {
    html: '<html><body>Test</body></html>',
    css: 'body { color: red; }',
    js: 'console.log("test");',
  };

  describe('publish', () => {
    it('should publish to server', async () => {
      const result = await service.publish(mockDoc, {
        target: 'server',
        port: 3001,
      });

      expect(result.success).toBe(true);
      expect(result.url).toBe('http://localhost:3001');
    });

    it('should publish to directory', async () => {
      (fs.existsSync as jest.Mock).mockReturnValue(true);
      (fs.writeFileSync as jest.Mock).mockImplementation(() => {});

      const result = await service.publish(mockDoc, {
        target: 'directory',
        directory: './test-docs',
      });

      expect(result.success).toBe(true);
      expect(result.path).toBeTruthy();
      expect(fs.writeFileSync).toHaveBeenCalled();
    });

    it('should publish to PDF', async () => {
      (fs.writeFileSync as jest.Mock).mockImplementation(() => {});

      const result = await service.publish(mockDoc, {
        target: 'pdf',
        filename: 'test.pdf',
      });

      expect(result.success).toBe(true);
      expect(result.path).toBeTruthy();
      expect(fs.writeFileSync).toHaveBeenCalled();
    });

    it('should return error for unknown target', async () => {
      const result = await service.publish(mockDoc, {
        target: 'unknown' as any,
      });

      expect(result.success).toBe(false);
      expect(result.error).toContain('Unknown target');
    });
  });

  describe('server management', () => {
    it('should start server', async () => {
      const result = await service.publish(mockDoc, {
        target: 'server',
        port: 3002,
      });

      expect(service.isServerRunning()).toBe(true);
      expect(service.getServerUrl()).toBe('http://localhost:3002');
    });

    it('should stop server', async () => {
      await service.publish(mockDoc, {
        target: 'server',
        port: 3003,
      });

      expect(service.isServerRunning()).toBe(true);

      await service.stopServer();

      expect(service.isServerRunning()).toBe(false);
      expect(service.getServerUrl()).toBeNull();
    });

    it('should replace existing server', async () => {
      await service.publish(mockDoc, {
        target: 'server',
        port: 3004,
      });

      const firstUrl = service.getServerUrl();

      await service.publish(mockDoc, {
        target: 'server',
        port: 3005,
      });

      const secondUrl = service.getServerUrl();

      expect(firstUrl).not.toBe(secondUrl);
      expect(secondUrl).toBe('http://localhost:3005');
    });
  });

  describe('directory publishing', () => {
    it('should create directory if not exists', async () => {
      (fs.existsSync as jest.Mock).mockReturnValue(false);
      (fs.mkdirSync as jest.Mock).mockImplementation(() => {});
      (fs.writeFileSync as jest.Mock).mockImplementation(() => {});

      await service.publish(mockDoc, {
        target: 'directory',
        directory: './new-docs',
      });

      expect(fs.mkdirSync).toHaveBeenCalledWith('./new-docs', { recursive: true });
    });

    it('should write HTML file', async () => {
      (fs.existsSync as jest.Mock).mockReturnValue(true);
      (fs.writeFileSync as jest.Mock).mockImplementation(() => {});

      await service.publish(mockDoc, {
        target: 'directory',
        directory: './docs',
      });

      expect(fs.writeFileSync).toHaveBeenCalledWith(
        expect.stringContaining('index.html'),
        mockDoc.html
      );
    });

    it('should write JS file if present', async () => {
      (fs.existsSync as jest.Mock).mockReturnValue(true);
      (fs.writeFileSync as jest.Mock).mockImplementation(() => {});

      await service.publish(mockDoc, {
        target: 'directory',
        directory: './docs',
      });

      expect(fs.writeFileSync).toHaveBeenCalledWith(
        expect.stringContaining('explorer.js'),
        mockDoc.js
      );
    });
  });

  describe('publishMultiple', () => {
    it('should publish to multiple targets', async () => {
      (fs.existsSync as jest.Mock).mockReturnValue(true);
      (fs.writeFileSync as jest.Mock).mockImplementation(() => {});

      const results = await service.publishMultiple(mockDoc, [
        { target: 'server', port: 3006 },
        { target: 'directory', directory: './docs' },
      ]);

      expect(results).toHaveLength(2);
      expect(results[0].success).toBe(true);
      expect(results[1].success).toBe(true);
    });
  });

  describe('getStatus', () => {
    it('should return status when server not running', () => {
      const status = service.getStatus();

      expect(status.serverRunning).toBe(false);
      expect(status.serverUrl).toBeNull();
    });

    it('should return status when server running', async () => {
      await service.publish(mockDoc, {
        target: 'server',
        port: 3007,
      });

      const status = service.getStatus();

      expect(status.serverRunning).toBe(true);
      expect(status.serverUrl).toBe('http://localhost:3007');
    });
  });

  describe('error handling', () => {
    it('should handle directory write errors', async () => {
      (fs.existsSync as jest.Mock).mockReturnValue(true);
      (fs.writeFileSync as jest.Mock).mockImplementation(() => {
        throw new Error('Write failed');
      });

      const result = await service.publish(mockDoc, {
        target: 'directory',
        directory: './docs',
      });

      expect(result.success).toBe(false);
      expect(result.error).toContain('Write failed');
    });
  });
});
