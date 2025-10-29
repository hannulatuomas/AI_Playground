// Import Service - Core import functionality with handler registry
import type {
  ImportExportFormat,
  ImportMethod,
  ImportExportOptions,
  ImportResult,
  ValidationResult,
  Importer,
  ImportConflict,
  ImportHistoryEntry,
} from '../../types/import-export';
import type { Collection, Request, Environment, Variable } from '../../types/models';
import { DatabaseService } from './DatabaseService';

/**
 * Import Service
 * Manages import operations with pluggable format handlers
 */
export class ImportService {
  private handlers: Map<ImportExportFormat, Importer> = new Map();
  private history: ImportHistoryEntry[] = [];
  private db: DatabaseService;

  constructor(db: DatabaseService) {
    this.db = db;
  }

  /**
   * Register an import handler for a specific format
   */
  registerHandler(handler: Importer): void {
    this.handlers.set(handler.format, handler);
    console.log(`[ImportService] Registered handler for format: ${handler.format}`);
  }

  /**
   * Unregister an import handler
   */
  unregisterHandler(format: ImportExportFormat): void {
    this.handlers.delete(format);
    console.log(`[ImportService] Unregistered handler for format: ${format}`);
  }

  /**
   * Get all registered handlers
   */
  getHandlers(): Importer[] {
    return Array.from(this.handlers.values());
  }

  /**
   * Get handler for a specific format
   */
  getHandler(format: ImportExportFormat): Importer | undefined {
    return this.handlers.get(format);
  }

  /**
   * Detect format from content
   */
  async detectFormat(content: string): Promise<ImportExportFormat | null> {
    // Try each handler's canImport method
    for (const [format, handler] of this.handlers.entries()) {
      try {
        if (handler.canImport(content)) {
          console.log(`[ImportService] Detected format: ${format}`);
          return format;
        }
      } catch (error) {
        // Continue to next handler
        console.warn(`[ImportService] Error checking format ${format}:`, error);
      }
    }

    // Fallback: try to detect by structure
    const detected = this.detectFormatByStructure(content);
    if (detected) {
      console.log(`[ImportService] Detected format by structure: ${detected}`);
      return detected;
    }

    console.warn('[ImportService] Could not detect format');
    return null;
  }

  /**
   * Detect format by analyzing content structure
   */
  private detectFormatByStructure(content: string): ImportExportFormat | null {
    try {
      const trimmed = content.trim();

      // cURL command
      if (trimmed.startsWith('curl ')) {
        return 'curl';
      }

      // Try to parse as JSON
      try {
        const json = JSON.parse(trimmed);

        // Postman Collection
        if (json.info && json.info.schema && json.info.schema.includes('postman')) {
          if (json.info.schema.includes('v2.1')) return 'postman-v2.1';
          return 'postman-v2';
        }

        // Insomnia
        if (json._type && json._type.startsWith('export')) {
          return 'insomnia-v4';
        }

        // OpenAPI/Swagger
        if (json.openapi) {
          if (json.openapi.startsWith('3.1')) return 'openapi-3.1';
          if (json.openapi.startsWith('3.0')) return 'openapi-3.0';
        }
        if (json.swagger) {
          if (json.swagger === '2.0') return 'swagger-2.0';
          return 'swagger-1.2';
        }

        // HAR
        if (json.log && json.log.entries) {
          return 'har';
        }

        // AsyncAPI
        if (json.asyncapi) {
          if (json.asyncapi.startsWith('3.')) return 'asyncapi-3.0';
          return 'asyncapi-2.0';
        }

        // Generic JSON
        return 'json';
      } catch {
        // Not JSON, continue
      }

      // Try to parse as YAML
      if (trimmed.includes('openapi:') || trimmed.includes('swagger:')) {
        if (trimmed.includes('openapi: 3.1')) return 'openapi-3.1';
        if (trimmed.includes('openapi: 3.0')) return 'openapi-3.0';
        if (trimmed.includes('swagger: 2.0')) return 'swagger-2.0';
      }

      // RAML
      if (trimmed.startsWith('#%RAML')) {
        if (trimmed.includes('1.0')) return 'raml-1.0';
        return 'raml-0.8';
      }

      // XML-based formats
      if (trimmed.startsWith('<?xml') || trimmed.startsWith('<')) {
        if (trimmed.includes('<definitions') || trimmed.includes('wsdl:')) {
          return 'wsdl-1.1';
        }
        if (trimmed.includes('<application') && trimmed.includes('wadl')) {
          return 'wadl';
        }
        if (trimmed.includes('<soapui:')) {
          return 'soapui';
        }
        return 'xml';
      }

      return null;
    } catch (error) {
      console.error('[ImportService] Error detecting format:', error);
      return null;
    }
  }

  /**
   * Validate import content
   */
  async validate(
    content: string,
    format?: ImportExportFormat
  ): Promise<ValidationResult> {
    const startTime = Date.now();

    try {
      // Auto-detect format if not provided
      const detectedFormat = format || (await this.detectFormat(content));

      if (!detectedFormat) {
        return {
          valid: false,
          errors: [
            {
              code: 'UNKNOWN_FORMAT',
              message: 'Could not detect import format',
            },
          ],
          warnings: [],
        };
      }

      // Get handler
      const handler = this.handlers.get(detectedFormat);
      if (!handler) {
        return {
          valid: false,
          format: detectedFormat,
          errors: [
            {
              code: 'NO_HANDLER',
              message: `No import handler registered for format: ${detectedFormat}`,
            },
          ],
          warnings: [],
        };
      }

      // Validate with handler
      if (!handler.canImport(content)) {
        return {
          valid: false,
          format: detectedFormat,
          errors: [
            {
              code: 'INVALID_CONTENT',
              message: `Content is not valid ${detectedFormat} format`,
            },
          ],
          warnings: [],
        };
      }

      const duration = Date.now() - startTime;
      console.log(`[ImportService] Validation completed in ${duration}ms`);

      return {
        valid: true,
        format: detectedFormat,
        errors: [],
        warnings: [],
        metadata: {
          detectedFormat,
        },
      };
    } catch (error) {
      return {
        valid: false,
        errors: [
          {
            code: 'VALIDATION_ERROR',
            message: error instanceof Error ? error.message : 'Validation failed',
          },
        ],
        warnings: [],
      };
    }
  }

  /**
   * Import content
   */
  async import(
    content: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    const startTime = Date.now();
    const historyEntry: ImportHistoryEntry = {
      id: `import-${Date.now()}`,
      timestamp: new Date(),
      format: options.format || 'json',
      method: options.method || 'text',
      itemCount: 0,
      success: false,
    };

    try {
      // Validate first
      const validation = await this.validate(content, options.format);
      if (!validation.valid) {
        historyEntry.errors = validation.errors.map((e) => e.message);
        this.history.push(historyEntry);
        return {
          success: false,
          errors: validation.errors.map((e) => e.message),
          warnings: validation.warnings.map((w) => w.message),
        };
      }

      const format = validation.format!;
      const handler = this.handlers.get(format)!;

      // Import with handler
      console.log(`[ImportService] Importing with format: ${format}`);
      const result = await handler.import(content, options);

      if (!result.success) {
        historyEntry.errors = result.errors;
        this.history.push(historyEntry);
        return result;
      }

      // Handle conflicts if needed
      if (options.conflictResolution && options.conflictResolution !== 'ask') {
        await this.resolveConflicts(result, options.conflictResolution);
      }

      // Save to database if requested
      if (options.preview !== true) {
        await this.saveImportedData(result, options);
      }

      // Update history
      historyEntry.success = true;
      historyEntry.itemCount =
        (result.collections?.length || 0) +
        (result.requests?.length || 0) +
        (result.environments?.length || 0) +
        (result.variables?.length || 0);
      historyEntry.metadata = {
        ...historyEntry.metadata,
        duration: Date.now() - startTime,
      };
      this.history.push(historyEntry);

      const duration = Date.now() - startTime;
      console.log(
        `[ImportService] Import completed successfully in ${duration}ms (${historyEntry.itemCount} items)`
      );

      return result;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Import failed';
      console.error('[ImportService] Import error:', error);

      historyEntry.errors = [errorMessage];
      this.history.push(historyEntry);

      return {
        success: false,
        errors: [errorMessage],
      };
    }
  }

  /**
   * Import from file
   */
  async importFromFile(
    filePath: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const fs = await import('fs/promises');
      const content = await fs.readFile(filePath, 'utf-8');

      return this.import(content, {
        ...options,
        method: 'file',
      });
    } catch (error) {
      console.error('[ImportService] Error reading file:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to read file',
        ],
      };
    }
  }

  /**
   * Import from multiple files (batch import)
   */
  async importFromFiles(
    filePaths: string[],
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    const startTime = Date.now();
    
    try {
      const allCollections: Collection[] = [];
      const allRequests: Request[] = [];
      const allEnvironments: Environment[] = [];
      const allVariables: Variable[] = [];
      const allErrors: string[] = [];
      const allWarnings: string[] = [];

      console.log(`[ImportService] Batch importing ${filePaths.length} files`);

      for (const filePath of filePaths) {
        const result = await this.importFromFile(filePath, {
          ...options,
          preview: true, // Always preview in batch mode
        });

        if (result.success) {
          if (result.collections) allCollections.push(...result.collections);
          if (result.requests) allRequests.push(...result.requests);
          if (result.environments) allEnvironments.push(...result.environments);
          if (result.variables) allVariables.push(...result.variables);
          if (result.warnings) allWarnings.push(...result.warnings);
        } else {
          allErrors.push(`${filePath}: ${result.errors?.join(', ')}`);
        }
      }

      const duration = Date.now() - startTime;
      console.log(
        `[ImportService] Batch import completed in ${duration}ms: ${allCollections.length} collections, ${allRequests.length} requests`
      );

      return {
        success: allErrors.length === 0 || (allCollections.length > 0 || allRequests.length > 0),
        collections: allCollections,
        requests: allRequests,
        environments: allEnvironments,
        variables: allVariables,
        errors: allErrors.length > 0 ? allErrors : undefined,
        warnings: allWarnings.length > 0 ? allWarnings : undefined,
        metadata: {
          format: 'json' as any,
          itemCount: allCollections.length + allRequests.length,
          importedAt: new Date(),
        },
      };
    } catch (error) {
      console.error('[ImportService] Batch import error:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Batch import failed',
        ],
      };
    }
  }

  /**
   * Import from ZIP file
   */
  async importFromZip(
    zipPath: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const fs = await import('fs/promises');
      const path = await import('path');
      const { createReadStream } = await import('fs');
      const { pipeline } = await import('stream/promises');
      const { createGunzip } = await import('zlib');
      const { Extract } = await import('tar');

      console.log(`[ImportService] Extracting ZIP/archive file: ${zipPath}`);

      const tempDir = path.join(path.dirname(zipPath), `temp_${Date.now()}`);
      await fs.mkdir(tempDir, { recursive: true });

      // Try to extract as tar.gz or zip
      try {
        // For tar.gz files
        await pipeline(
          createReadStream(zipPath),
          createGunzip(),
          Extract({ cwd: tempDir })
        );
      } catch {
        // If not tar.gz, try simple extraction (assuming it's a simple archive)
        // For now, just return an error asking for specific format
        throw new Error('ZIP extraction requires adm-zip package. Please use tar.gz format or extract manually.');
      }

      // Get all extracted files
      const filePaths: string[] = [];
      const getAllFiles = async (dir: string): Promise<void> => {
        const entries = await fs.readdir(dir, { withFileTypes: true });
        for (const entry of entries) {
          const fullPath = path.join(dir, entry.name);
          if (entry.isDirectory()) {
            await getAllFiles(fullPath);
          } else {
            filePaths.push(fullPath);
          }
        }
      };
      await getAllFiles(tempDir);

      console.log(`[ImportService] Extracted ${filePaths.length} files`);

      // Import all extracted files
      const result = await this.importFromFiles(filePaths, options);

      // Cleanup temp directory
      try {
        await fs.rm(tempDir, { recursive: true, force: true });
      } catch (cleanupError) {
        console.warn('[ImportService] Failed to cleanup temp directory:', cleanupError);
      }

      return result;
    } catch (error) {
      console.error('[ImportService] Error importing from archive:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to import from archive',
        ],
      };
    }
  }

  /**
   * Import from URL
   */
  async importFromURL(
    url: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const axios = (await import('axios')).default;
      const response = await axios.get(url, {
        timeout: 30000,
        responseType: 'text',
      });

      return this.import(response.data, {
        ...options,
        method: 'url',
      });
    } catch (error) {
      console.error('[ImportService] Error fetching URL:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to fetch URL',
        ],
      };
    }
  }

  /**
   * Import from Git repository
   */
  async importFromGit(
    repoUrl: string,
    options: ImportExportOptions = {}
  ): Promise<ImportResult> {
    try {
      const simpleGit = (await import('simple-git')).default;
      const fs = await import('fs/promises');
      const path = await import('path');

      console.log(`[ImportService] Cloning Git repository: ${repoUrl}`);

      const tempDir = path.join(process.cwd(), `temp_git_${Date.now()}`);
      await fs.mkdir(tempDir, { recursive: true });

      // Clone repository
      const git = simpleGit();
      await git.clone(repoUrl, tempDir, ['--depth', '1']);

      console.log('[ImportService] Repository cloned successfully');

      // Find all API spec files in the repository
      const filePaths: string[] = [];
      const extensions = ['.json', '.yaml', '.yml', '.raml', '.proto', '.graphql', '.wsdl', '.wadl'];

      const getAllFiles = async (dir: string): Promise<void> => {
        const entries = await fs.readdir(dir, { withFileTypes: true });
        for (const entry of entries) {
          const fullPath = path.join(dir, entry.name);
          
          // Skip .git directory
          if (entry.name === '.git') continue;

          if (entry.isDirectory()) {
            await getAllFiles(fullPath);
          } else if (extensions.some(ext => entry.name.endsWith(ext))) {
            filePaths.push(fullPath);
          }
        }
      };
      await getAllFiles(tempDir);

      console.log(`[ImportService] Found ${filePaths.length} API spec files in repository`);

      // Import all found files
      const result = await this.importFromFiles(filePaths, options);

      // Cleanup temp directory
      try {
        await fs.rm(tempDir, { recursive: true, force: true });
      } catch (cleanupError) {
        console.warn('[ImportService] Failed to cleanup temp directory:', cleanupError);
      }

      return result;
    } catch (error) {
      console.error('[ImportService] Error importing from Git:', error);
      return {
        success: false,
        errors: [
          error instanceof Error ? error.message : 'Failed to import from Git repository',
        ],
      };
    }
  }

  /**
   * Resolve conflicts between existing and imported data
   */
  private async resolveConflicts(
    result: ImportResult,
    resolution: 'merge' | 'replace' | 'skip'
  ): Promise<void> {
    console.log(`[ImportService] Resolving conflicts with strategy: ${resolution}`);

    try {
      // Handle collection conflicts
      if (result.collections) {
        const resolvedCollections: Collection[] = [];
        
        for (const newCollection of result.collections) {
          const existing = await this.db.getCollectionById(newCollection.id);
          
          if (!existing) {
            // No conflict, keep as is
            resolvedCollections.push(newCollection);
            continue;
          }

          switch (resolution) {
            case 'replace':
              // Replace existing with new
              resolvedCollections.push(newCollection);
              break;

            case 'merge':
              // Merge: keep existing metadata, add new requests
              const merged: Collection = {
                ...existing,
                name: newCollection.name, // Update name
                description: newCollection.description || existing.description,
                requests: [...existing.requests, ...newCollection.requests],
                folders: [...existing.folders, ...newCollection.folders],
                updatedAt: new Date(),
              };
              resolvedCollections.push(merged);
              break;

            case 'skip':
              // Skip new, keep existing
              resolvedCollections.push(existing);
              break;
          }
        }
        
        result.collections = resolvedCollections;
      }

      // Handle request conflicts
      if (result.requests) {
        const resolvedRequests: Request[] = [];
        
        for (const newRequest of result.requests) {
          const existing = await this.db.getRequestById(newRequest.id);
          
          if (!existing) {
            // No conflict, keep as is
            resolvedRequests.push(newRequest);
            continue;
          }

          switch (resolution) {
            case 'replace':
              // Replace existing with new
              resolvedRequests.push(newRequest);
              break;

            case 'merge':
              // Merge: update fields but keep some existing data
              const merged: Request = {
                ...existing,
                name: newRequest.name,
                method: newRequest.method,
                url: newRequest.url,
                headers: newRequest.headers,
                queryParams: newRequest.queryParams,
                body: newRequest.body,
                updatedAt: new Date(),
              };
              resolvedRequests.push(merged);
              break;

            case 'skip':
              // Skip new, keep existing
              resolvedRequests.push(existing);
              break;
          }
        }
        
        result.requests = resolvedRequests;
      }

      // Handle variable conflicts
      if (result.variables) {
        const resolvedVariables: Variable[] = [];
        
        for (const newVariable of result.variables) {
          const existingVars = await this.db.getVariablesByScope(
            newVariable.scope,
            newVariable.scope === 'collection' ? newVariable.key : undefined
          );
          
          const existing = existingVars.find(v => v.key === newVariable.key);
          
          if (!existing) {
            // No conflict, keep as is
            resolvedVariables.push(newVariable);
            continue;
          }

          switch (resolution) {
            case 'replace':
              // Replace existing with new
              resolvedVariables.push(newVariable);
              break;

            case 'merge':
              // For variables, merge means update value
              resolvedVariables.push({
                ...existing,
                value: newVariable.value,
                type: newVariable.type,
              });
              break;

            case 'skip':
              // Skip new, keep existing
              resolvedVariables.push(existing);
              break;
          }
        }
        
        result.variables = resolvedVariables;
      }

      console.log('[ImportService] Conflicts resolved successfully');
    } catch (error) {
      console.error('[ImportService] Error resolving conflicts:', error);
      throw error;
    }
  }

  /**
   * Save imported data to database
   */
  private async saveImportedData(
    result: ImportResult,
    options: ImportExportOptions
  ): Promise<void> {
    try {
      // Apply selective import filtering if enabled
      if (options.selectiveImport) {
        this.applySelectiveFiltering(result, options);
      }

      // Save collections
      if (result.collections && options.includeCollections !== false) {
        for (const collection of result.collections) {
          await this.db.createCollection(collection);
        }
      }

      // Save requests
      if (result.requests && options.includeRequests !== false) {
        for (const request of result.requests) {
          await this.db.createRequest(request);
        }
      }

      // Save environments
      if (result.environments && options.includeEnvironments) {
        for (const env of result.environments) {
          await this.db.createEnvironment(env);
        }
      }

      // Save variables
      if (result.variables && options.includeVariables) {
        for (const variable of result.variables) {
          this.db.setVariable(variable);
        }
      }

      console.log('[ImportService] Imported data saved to database');
    } catch (error) {
      console.error('[ImportService] Error saving imported data:', error);
      throw error;
    }
  }

  /**
   * Apply selective filtering to import result
   */
  private applySelectiveFiltering(
    result: ImportResult,
    options: ImportExportOptions
  ): void {
    // Filter collections
    if (options.selectedCollectionIds && result.collections) {
      result.collections = result.collections.filter(col =>
        options.selectedCollectionIds!.includes(col.id)
      );
    }

    // Filter requests
    if (options.selectedRequestIds && result.requests) {
      result.requests = result.requests.filter(req =>
        options.selectedRequestIds!.includes(req.id)
      );
    }

    // Filter environments
    if (options.selectedEnvironmentIds && result.environments) {
      result.environments = result.environments.filter(env =>
        options.selectedEnvironmentIds!.includes(env.id)
      );
    }

    console.log('[ImportService] Applied selective import filtering');
  }

  /**
   * Get import history
   */
  getHistory(): ImportHistoryEntry[] {
    return [...this.history];
  }

  /**
   * Clear import history
   */
  clearHistory(): void {
    this.history = [];
    console.log('[ImportService] Import history cleared');
  }

  /**
   * Get supported formats
   */
  getSupportedFormats(): ImportExportFormat[] {
    return Array.from(this.handlers.keys());
  }
}

// Singleton instance
let importServiceInstance: ImportService | null = null;

/**
 * Get or create ImportService singleton
 */
export function getImportService(): ImportService {
  if (!importServiceInstance) {
    const { getDatabaseService } = require('./DatabaseService');
    const db = getDatabaseService();
    importServiceInstance = new ImportService(db);
    
    // Register default handlers
    const { PostmanImporter } = require('./importers/PostmanImporter');
    const { CurlImporter } = require('./importers/CurlImporter');
    const { OpenAPIImporter } = require('./importers/OpenAPIImporter');
    const { HARImporter } = require('./importers/HARImporter');
    const { InsomniaImporter } = require('./importers/InsomniaImporter');
    const { RAMLImporter } = require('./importers/RAMLImporter');
    const { GraphQLImporter } = require('./importers/GraphQLImporter');
    const { AsyncAPIImporter } = require('./importers/AsyncAPIImporter');
    const { SoapUIImporter } = require('./importers/SoapUIImporter');
    const { WADLImporter } = require('./importers/WADLImporter');
    const { WSDLImporter } = require('./importers/WSDLImporter');
    const { ProtobufImporter } = require('./importers/ProtobufImporter');
    const { APIGatewayImporter } = require('./importers/APIGatewayImporter');
    
    importServiceInstance.registerHandler(new PostmanImporter());
    importServiceInstance.registerHandler(new CurlImporter());
    importServiceInstance.registerHandler(new OpenAPIImporter());
    importServiceInstance.registerHandler(new HARImporter());
    importServiceInstance.registerHandler(new InsomniaImporter());
    importServiceInstance.registerHandler(new RAMLImporter());
    importServiceInstance.registerHandler(new GraphQLImporter());
    importServiceInstance.registerHandler(new AsyncAPIImporter());
    importServiceInstance.registerHandler(new SoapUIImporter());
    importServiceInstance.registerHandler(new WADLImporter());
    importServiceInstance.registerHandler(new WSDLImporter());
    importServiceInstance.registerHandler(new ProtobufImporter());
    importServiceInstance.registerHandler(new APIGatewayImporter());
    
    console.log('[ImportService] Initialized with 13 default handlers');
  }
  return importServiceInstance;
}

/**
 * Reset ImportService singleton (for testing)
 */
export function resetImportService(): void {
  importServiceInstance = null;
}
