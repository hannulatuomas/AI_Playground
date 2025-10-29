// Export Service - Core export functionality with generator registry
import type {
  ImportExportFormat,
  ImportExportOptions,
  ExportResult,
  Exporter,
  ExportHistoryEntry,
} from '../../types/import-export';
import type { Collection, Request } from '../../types/models';
import { DatabaseService } from './DatabaseService';

/**
 * Export Service
 * Manages export operations with pluggable format generators
 */
export class ExportService {
  private generators: Map<ImportExportFormat, Exporter> = new Map();
  private history: ExportHistoryEntry[] = [];
  private db: DatabaseService;

  constructor(db: DatabaseService) {
    this.db = db;
  }

  /**
   * Register an export generator for a specific format
   */
  registerGenerator(generator: Exporter): void {
    this.generators.set(generator.format, generator);
    console.log(`[ExportService] Registered generator for format: ${generator.format}`);
  }

  /**
   * Unregister an export generator
   */
  unregisterGenerator(format: ImportExportFormat): void {
    this.generators.delete(format);
    console.log(`[ExportService] Unregistered generator for format: ${format}`);
  }

  /**
   * Get all registered generators
   */
  getGenerators(): Exporter[] {
    return Array.from(this.generators.values());
  }

  /**
   * Get generator for a specific format
   */
  getGenerator(format: ImportExportFormat): Exporter | undefined {
    return this.generators.get(format);
  }

  /**
   * Export collections to specified format
   */
  async exportCollections(
    collectionIds: string[],
    format: ImportExportFormat,
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    const startTime = Date.now();
    const historyEntry: ExportHistoryEntry = {
      id: `export-${Date.now()}`,
      timestamp: new Date(),
      format,
      destination: 'file',
      itemCount: 0,
      success: false,
    };

    try {
      // Get generator
      const generator = this.generators.get(format);
      if (!generator) {
        historyEntry.metadata = { duration: Date.now() - startTime };
        this.history.push(historyEntry);
        return {
          success: false,
          format,
          errors: [`No export generator registered for format: ${format}`],
        };
      }

      // Fetch collections from database
      const collections: Collection[] = [];
      for (const id of collectionIds) {
        const collection = await this.db.getCollectionById(id);
        if (collection) {
          // Fetch requests for this collection
          const requests = await this.db.getRequestsByCollection(id);
          collection.requests = requests;
          collections.push(collection);
        }
      }

      if (collections.length === 0) {
        return {
          success: false,
          format,
          errors: ['No collections found with provided IDs'],
        };
      }

      // Export with generator
      console.log(`[ExportService] Exporting ${collections.length} collections to ${format}`);
      const result = await generator.exportCollections(collections, options);

      if (result.success) {
        historyEntry.success = true;
        historyEntry.itemCount = collections.length;
        historyEntry.metadata = {
          ...historyEntry.metadata,
          duration: Date.now() - startTime,
          fileSize: result.data?.length || 0,
        };
      }

      this.history.push(historyEntry);

      const duration = Date.now() - startTime;
      console.log(
        `[ExportService] Export completed ${result.success ? 'successfully' : 'with errors'} in ${duration}ms`
      );

      return result;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Export failed';
      console.error('[ExportService] Export error:', error);

      historyEntry.metadata = { duration: Date.now() - startTime };
      this.history.push(historyEntry);

      return {
        success: false,
        format,
        errors: [errorMessage],
      };
    }
  }

  /**
   * Export a single request
   */
  async exportRequest(
    requestId: string,
    format: ImportExportFormat,
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    const startTime = Date.now();

    try {
      // Get generator
      const generator = this.generators.get(format);
      if (!generator) {
        return {
          success: false,
          format,
          errors: [`No export generator registered for format: ${format}`],
        };
      }

      // Fetch request from database
      const request = await this.db.getRequestById(requestId);
      if (!request) {
        return {
          success: false,
          format,
          errors: ['Request not found'],
        };
      }

      // Export with generator
      console.log(`[ExportService] Exporting request to ${format}`);
      const result = await generator.exportRequest(request, options);

      const duration = Date.now() - startTime;
      console.log(
        `[ExportService] Export completed ${result.success ? 'successfully' : 'with errors'} in ${duration}ms`
      );

      return result;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Export failed';
      console.error('[ExportService] Export error:', error);

      return {
        success: false,
        format,
        errors: [errorMessage],
      };
    }
  }

  /**
   * Export multiple requests
   */
  async exportRequests(
    requestIds: string[],
    format: ImportExportFormat,
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    const startTime = Date.now();

    try {
      // Get generator
      const generator = this.generators.get(format);
      if (!generator) {
        return {
          success: false,
          format,
          errors: [`No export generator registered for format: ${format}`],
        };
      }

      // Fetch requests from database
      const requests: Request[] = [];
      for (const id of requestIds) {
        const request = await this.db.getRequestById(id);
        if (request) {
          requests.push(request);
        }
      }

      if (requests.length === 0) {
        return {
          success: false,
          format,
          errors: ['No requests found with provided IDs'],
        };
      }

      // Export with generator
      console.log(`[ExportService] Exporting ${requests.length} requests to ${format}`);
      const result = await generator.exportRequests(requests, options);

      const duration = Date.now() - startTime;
      console.log(
        `[ExportService] Export completed ${result.success ? 'successfully' : 'with errors'} in ${duration}ms`
      );

      return result;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Export failed';
      console.error('[ExportService] Export error:', error);

      return {
        success: false,
        format,
        errors: [errorMessage],
      };
    }
  }

  /**
   * Save export to file
   */
  async saveToFile(
    content: string,
    filePath: string,
    format: ImportExportFormat
  ): Promise<void> {
    try {
      const fs = await import('fs/promises');
      await fs.writeFile(filePath, content, 'utf-8');
      console.log(`[ExportService] Saved export to file: ${filePath}`);
    } catch (error) {
      console.error('[ExportService] Error saving to file:', error);
      throw error;
    }
  }

  /**
   * Copy export to clipboard
   */
  async copyToClipboard(content: string): Promise<void> {
    try {
      const { clipboard } = await import('electron');
      clipboard.writeText(content);
      console.log('[ExportService] Copied export to clipboard');
    } catch (error) {
      console.error('[ExportService] Error copying to clipboard:', error);
      throw error;
    }
  }

  /**
   * Bulk export to ZIP archive
   */
  async exportToZip(
    collectionIds: string[],
    format: ImportExportFormat,
    zipPath: string,
    options: ImportExportOptions = {}
  ): Promise<ExportResult> {
    try {
      const fs = await import('fs/promises');
      const path = await import('path');
      const { createWriteStream } = await import('fs');
      const { pipeline } = await import('stream/promises');
      const { createGzip } = await import('zlib');
      const { create: createTar } = await import('tar');

      console.log(`[ExportService] Creating bulk export archive`);

      const tempDir = path.join(path.dirname(zipPath), `temp_export_${Date.now()}`);
      await fs.mkdir(tempDir, { recursive: true });

      // Export each collection to a separate file
      const exportedFiles: string[] = [];
      for (const collectionId of collectionIds) {
        const result = await this.exportCollections([collectionId], format, options);
        if (result.success && result.data) {
          const fileName = `collection_${collectionId}.${this.getFileExtension(format)}`;
          const filePath = path.join(tempDir, fileName);
          await fs.writeFile(filePath, result.data);
          exportedFiles.push(fileName);
        }
      }

      // Create tar.gz archive
      await createTar(
        {
          gzip: true,
          file: zipPath,
          cwd: tempDir,
        },
        exportedFiles
      );

      // Cleanup temp directory
      await fs.rm(tempDir, { recursive: true, force: true });

      console.log(`[ExportService] Created archive with ${exportedFiles.length} files`);

      return {
        success: true,
        format,
        metadata: {
          exportedAt: new Date(),
          itemCount: exportedFiles.length,
          size: 0,
        },
      };
    } catch (error) {
      console.error('[ExportService] Bulk export error:', error);
      return {
        success: false,
        format,
        errors: [error instanceof Error ? error.message : 'Bulk export failed'],
      };
    }
  }

  /**
   * Get file extension for format
   */
  private getFileExtension(format: ImportExportFormat): string {
    const generator = this.generators.get(format);
    return generator?.fileExtensions[0]?.replace('.', '') || 'txt';
  }

  /**
   * Get export history
   */
  getHistory(): ExportHistoryEntry[] {
    return [...this.history];
  }

  /**
   * Clear export history
   */
  clearHistory(): void {
    this.history = [];
    console.log('[ExportService] Export history cleared');
  }

  /**
   * Get supported formats
   */
  getSupportedFormats(): ImportExportFormat[] {
    return Array.from(this.generators.keys());
  }

  /**
   * Save export template/preset
   */
  async saveTemplate(name: string, format: ImportExportFormat, options: ImportExportOptions): Promise<void> {
    try {
      const fs = await import('fs/promises');
      const path = await import('path');
      
      const templatesDir = path.join(process.cwd(), 'data', 'export-templates');
      await fs.mkdir(templatesDir, { recursive: true });
      
      const template = { name, format, options, createdAt: new Date() };
      const filePath = path.join(templatesDir, `${name.replace(/[^a-z0-9]/gi, '_')}.json`);
      
      await fs.writeFile(filePath, JSON.stringify(template, null, 2));
      console.log(`[ExportService] Saved export template: ${name}`);
    } catch (error) {
      console.error('[ExportService] Error saving template:', error);
      throw error;
    }
  }

  /**
   * Load export template/preset
   */
  async loadTemplate(name: string): Promise<{ format: ImportExportFormat; options: ImportExportOptions } | null> {
    try {
      const fs = await import('fs/promises');
      const path = await import('path');
      
      const filePath = path.join(process.cwd(), 'data', 'export-templates', `${name.replace(/[^a-z0-9]/gi, '_')}.json`);
      const content = await fs.readFile(filePath, 'utf-8');
      const template = JSON.parse(content);
      
      return { format: template.format, options: template.options };
    } catch (error) {
      console.error('[ExportService] Error loading template:', error);
      return null;
    }
  }

  /**
   * List all export templates
   */
  async listTemplates(): Promise<string[]> {
    try {
      const fs = await import('fs/promises');
      const path = await import('path');
      
      const templatesDir = path.join(process.cwd(), 'data', 'export-templates');
      const files = await fs.readdir(templatesDir);
      
      return files.filter(f => f.endsWith('.json')).map(f => f.replace('.json', ''));
    } catch (error) {
      return [];
    }
  }

  /**
   * Schedule export (basic implementation)
   */
  async scheduleExport(
    collectionIds: string[],
    format: ImportExportFormat,
    schedule: string,
    outputPath: string,
    options: ImportExportOptions = {}
  ): Promise<void> {
    try {
      const cron = await import('node-cron');
      
      cron.schedule(schedule, async () => {
        console.log(`[ExportService] Running scheduled export`);
        const result = await this.exportCollections(collectionIds, format, options);
        
        if (result.success && result.data) {
          await this.saveToFile(result.data, outputPath, format);
        }
      });
      
      console.log(`[ExportService] Scheduled export: ${schedule}`);
    } catch (error) {
      console.error('[ExportService] Error scheduling export:', error);
      throw error;
    }
  }
}

// Singleton instance
let exportServiceInstance: ExportService | null = null;

/**
 * Get or create ExportService singleton
 */
export function getExportService(): ExportService {
  if (!exportServiceInstance) {
    const { getDatabaseService } = require('./DatabaseService');
    const db = getDatabaseService();
    exportServiceInstance = new ExportService(db);
    
    // Register default generators
    const { PostmanExporter } = require('./exporters/PostmanExporter');
    const { CurlExporter } = require('./exporters/CurlExporter');
    const { OpenAPIExporter } = require('./exporters/OpenAPIExporter');
    const { InsomniaExporter } = require('./exporters/InsomniaExporter');
    const { HARExporter } = require('./exporters/HARExporter');
    const { GraphQLExporter } = require('./exporters/GraphQLExporter');
    const { AsyncAPIExporter } = require('./exporters/AsyncAPIExporter');
    const { SoapUIExporter } = require('./exporters/SoapUIExporter');
    const { RAMLExporter } = require('./exporters/RAMLExporter');
    const { WADLExporter } = require('./exporters/WADLExporter');
    const { ProtobufExporter } = require('./exporters/ProtobufExporter');
    const { WSDLExporter } = require('./exporters/WSDLExporter');
    const { APIGatewayExporter } = require('./exporters/APIGatewayExporter');
    
    exportServiceInstance.registerGenerator(new PostmanExporter());
    exportServiceInstance.registerGenerator(new CurlExporter());
    exportServiceInstance.registerGenerator(new OpenAPIExporter());
    exportServiceInstance.registerGenerator(new InsomniaExporter());
    exportServiceInstance.registerGenerator(new HARExporter());
    exportServiceInstance.registerGenerator(new GraphQLExporter());
    exportServiceInstance.registerGenerator(new AsyncAPIExporter());
    exportServiceInstance.registerGenerator(new SoapUIExporter());
    exportServiceInstance.registerGenerator(new RAMLExporter());
    exportServiceInstance.registerGenerator(new WADLExporter());
    exportServiceInstance.registerGenerator(new ProtobufExporter());
    exportServiceInstance.registerGenerator(new WSDLExporter());
    exportServiceInstance.registerGenerator(new APIGatewayExporter());
    
    console.log('[ExportService] Initialized with 13 default generators');
  }
  return exportServiceInstance;
}

/**
 * Reset ExportService singleton (for testing)
 */
export function resetExportService(): void {
  exportServiceInstance = null;
}
