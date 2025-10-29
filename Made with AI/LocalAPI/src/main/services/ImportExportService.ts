// Import/Export Service with Registry
import type {
  ImportExportFormat,
  ImportExportHandler,
  Importer,
  Exporter,
  ImportExportOptions,
  ImportResult,
  ExportResult,
} from '../../types/import-export';
import type { Request, Collection } from '../../types/models';
import { JsonImporterExporter } from './importers/JsonImporterExporter';
import { CurlImporterExporter } from './importers/CurlImporterExporter';

export class ImportExportService {
  private handlers: Map<ImportExportFormat, ImportExportHandler>;

  constructor() {
    this.handlers = new Map();
    this.registerDefaultHandlers();
  }

  /**
   * Register default import/export handlers
   */
  private registerDefaultHandlers(): void {
    // Register JSON handler
    const jsonHandler = new JsonImporterExporter();
    this.registerHandler('json', jsonHandler, jsonHandler);

    // Register cURL handler
    const curlHandler = new CurlImporterExporter();
    this.registerHandler('curl', curlHandler, curlHandler);
  }

  /**
   * Register a new import/export handler
   */
  registerHandler(
    format: ImportExportFormat,
    importer?: Importer,
    exporter?: Exporter
  ): void {
    this.handlers.set(format, {
      format,
      importer,
      exporter,
      enabled: true,
    });
  }

  /**
   * Unregister a handler
   */
  unregisterHandler(format: ImportExportFormat): boolean {
    return this.handlers.delete(format);
  }

  /**
   * Get all registered handlers
   */
  getHandlers(): ImportExportHandler[] {
    return Array.from(this.handlers.values());
  }

  /**
   * Get supported import formats
   */
  getSupportedImportFormats(): ImportExportFormat[] {
    return Array.from(this.handlers.values())
      .filter(h => h.enabled && h.importer)
      .map(h => h.format);
  }

  /**
   * Get supported export formats
   */
  getSupportedExportFormats(): ImportExportFormat[] {
    return Array.from(this.handlers.values())
      .filter(h => h.enabled && h.exporter)
      .map(h => h.format);
  }

  /**
   * Auto-detect format from content
   */
  detectFormat(content: string): ImportExportFormat | null {
    for (const handler of this.handlers.values()) {
      if (handler.enabled && handler.importer?.canImport(content)) {
        return handler.format;
      }
    }
    return null;
  }

  /**
   * Import content
   */
  async import(
    content: string,
    format?: ImportExportFormat,
    options?: ImportExportOptions
  ): Promise<ImportResult> {
    try {
      // Auto-detect format if not provided
      const detectedFormat = format || this.detectFormat(content);
      
      if (!detectedFormat) {
        return {
          success: false,
          errors: ['Unable to detect format. Please specify format explicitly.'],
          metadata: {
            format: 'json',
            itemCount: 0,
            importedAt: new Date(),
          },
        };
      }

      const handler = this.handlers.get(detectedFormat);
      
      if (!handler || !handler.enabled || !handler.importer) {
        return {
          success: false,
          errors: [`No importer registered for format: ${detectedFormat}`],
          metadata: {
            format: detectedFormat,
            itemCount: 0,
            importedAt: new Date(),
          },
        };
      }

      return await handler.importer.import(content, options);
    } catch (error) {
      return {
        success: false,
        errors: [`Import failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
        metadata: {
          format: format || 'json',
          itemCount: 0,
          importedAt: new Date(),
        },
      };
    }
  }

  /**
   * Export collections
   */
  async exportCollections(
    collections: Collection[],
    format: ImportExportFormat,
    options?: ImportExportOptions
  ): Promise<ExportResult> {
    try {
      const handler = this.handlers.get(format);
      
      if (!handler || !handler.enabled || !handler.exporter) {
        return {
          success: false,
          format,
          errors: [`No exporter registered for format: ${format}`],
        };
      }

      return await handler.exporter.exportCollections(collections, options);
    } catch (error) {
      return {
        success: false,
        format,
        errors: [`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
      };
    }
  }

  /**
   * Export a single request
   */
  async exportRequest(
    request: Request,
    format: ImportExportFormat,
    options?: ImportExportOptions
  ): Promise<ExportResult> {
    try {
      const handler = this.handlers.get(format);
      
      if (!handler || !handler.enabled || !handler.exporter) {
        return {
          success: false,
          format,
          errors: [`No exporter registered for format: ${format}`],
        };
      }

      return await handler.exporter.exportRequest(request, options);
    } catch (error) {
      return {
        success: false,
        format,
        errors: [`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
      };
    }
  }

  /**
   * Export multiple requests
   */
  async exportRequests(
    requests: Request[],
    format: ImportExportFormat,
    options?: ImportExportOptions
  ): Promise<ExportResult> {
    try {
      const handler = this.handlers.get(format);
      
      if (!handler || !handler.enabled || !handler.exporter) {
        return {
          success: false,
          format,
          errors: [`No exporter registered for format: ${format}`],
        };
      }

      return await handler.exporter.exportRequests(requests, options);
    } catch (error) {
      return {
        success: false,
        format,
        errors: [`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
      };
    }
  }

  /**
   * Get example for a format
   */
  getExample(format: ImportExportFormat): string | null {
    const handler = this.handlers.get(format);
    return handler?.importer?.getExample?.() || null;
  }

  /**
   * Get handler info
   */
  getHandlerInfo(format: ImportExportFormat): {
    name: string;
    description: string;
    fileExtensions: string[];
    canImport: boolean;
    canExport: boolean;
  } | null {
    const handler = this.handlers.get(format);
    if (!handler) return null;

    return {
      name: handler.importer?.name || handler.exporter?.name || format,
      description: handler.importer?.description || handler.exporter?.description || '',
      fileExtensions: handler.importer?.fileExtensions || handler.exporter?.fileExtensions || [],
      canImport: !!handler.importer,
      canExport: !!handler.exporter,
    };
  }
}

// Singleton instance
let importExportServiceInstance: ImportExportService | null = null;

export function getImportExportService(): ImportExportService {
  if (!importExportServiceInstance) {
    importExportServiceInstance = new ImportExportService();
  }
  return importExportServiceInstance;
}
