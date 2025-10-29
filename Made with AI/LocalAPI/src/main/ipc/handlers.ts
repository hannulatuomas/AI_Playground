// IPC Handlers for database operations
import { ipcMain, app } from 'electron';
import { getDatabaseService } from '../services/DatabaseService';
import { getRequestService } from '../services/RequestService';
import { getSecretsService } from '../services/SecretsService';
import { getImportExportService } from '../services/ImportExportService';
import { initializeGitService, getGitService } from '../services/GitService';
import { initializePluginLoader, getPluginLoader } from '../services/PluginLoader';
import { initializeReportGenerator, getReportGenerator } from '../services/ReportGenerator';
import { getVariableExtractorService } from '../services/VariableExtractorService';
import { getWorkspaceService } from '../services/WorkspaceService';
import { ConsoleService } from '../services/ConsoleService';
import { RequestAnalyzerService } from '../services/RequestAnalyzerService';
import { OpenAPIGeneratorService } from '../services/OpenAPIGeneratorService';
import { AsyncAPIGeneratorService } from '../services/AsyncAPIGeneratorService';
import { GraphQLSchemaGeneratorService } from '../services/GraphQLSchemaGeneratorService';
import { LayoutService } from '../services/LayoutService';
import type { Collection, Request, Environment, Variable, Response, Workspace } from '../../types/models';
import type { ImportExportFormat, ImportExportOptions } from '../../types/import-export';
import type { GitCommitOptions } from '../services/GitService';
import type { ReportOptions } from '../../types/report';
import type { ExtractionRule } from '../services/VariableExtractorService';
import * as path from 'path';

/**
 * Register all IPC handlers
 */
export function registerIpcHandlers(): void {
  const db = getDatabaseService();
  const requestService = getRequestService();
  const secretsService = getSecretsService();
  const importExportService = getImportExportService();
  
  // Initialize Git service with app data directory
  const workingDir = path.join(app.getPath('userData'), 'collections');
  let gitService = initializeGitService({ workingDir });

  // Initialize Plugin Loader
  const pluginsDir = path.join(app.getPath('userData'), 'plugins');
  const pluginDataDir = path.join(app.getPath('userData'), 'plugin-data');
  let pluginLoader = initializePluginLoader(pluginsDir, pluginDataDir);

  // Initialize Report Generator
  const reportsDir = path.join(app.getPath('userData'), 'reports');
  let reportGenerator = initializeReportGenerator(reportsDir);

  // Initialize Console Service
  const consoleService = new ConsoleService(db.getDatabase());
  setGlobalConsoleService(consoleService);

  // Initialize API Spec Generation Services
  const analyzerService = new RequestAnalyzerService();
  const openApiService = new OpenAPIGeneratorService();
  const asyncApiService = new AsyncAPIGeneratorService();
  const graphqlService = new GraphQLSchemaGeneratorService();

  // ==================== Collections ====================

  ipcMain.handle('collections:getAll', () => {
    try {
      return db.getAllCollections();
    } catch (error) {
      console.error('Error getting collections:', error);
      throw error;
    }
  });

  ipcMain.handle('collections:getById', (_event, id: string) => {
    try {
      return db.getCollectionById(id);
    } catch (error) {
      console.error('Error getting collection:', error);
      throw error;
    }
  });

  ipcMain.handle('collections:create', (_event, collection: Omit<Collection, 'createdAt' | 'updatedAt'>) => {
    try {
      return db.createCollection(collection);
    } catch (error) {
      console.error('Error creating collection:', error);
      throw error;
    }
  });

  ipcMain.handle('collections:update', (_event, id: string, updates: Partial<Collection>) => {
    try {
      return db.updateCollection(id, updates);
    } catch (error) {
      console.error('Error updating collection:', error);
      throw error;
    }
  });

  ipcMain.handle('collections:delete', (_event, id: string) => {
    try {
      db.deleteCollection(id);
    } catch (error) {
      console.error('Error deleting collection:', error);
      throw error;
    }
  });

  // ==================== Requests ====================

  ipcMain.handle('requests:getAll', () => {
    try {
      return db.getAllRequests();
    } catch (error) {
      console.error('Error getting requests:', error);
      throw error;
    }
  });

  ipcMain.handle('requests:getByCollection', (_event, collectionId: string) => {
    try {
      return db.getRequestsByCollection(collectionId);
    } catch (error) {
      console.error('Error getting requests by collection:', error);
      throw error;
    }
  });

  ipcMain.handle('requests:getById', (_event, id: string) => {
    try {
      return db.getRequestById(id);
    } catch (error) {
      console.error('Error getting request:', error);
      throw error;
    }
  });

  ipcMain.handle('requests:create', (_event, request: Omit<Request, 'createdAt' | 'updatedAt'>) => {
    try {
      return db.createRequest(request);
    } catch (error) {
      console.error('Error creating request:', error);
      throw error;
    }
  });

  ipcMain.handle('requests:update', (_event, id: string, updates: Partial<Request>) => {
    try {
      return db.updateRequest(id, updates);
    } catch (error) {
      console.error('Error updating request:', error);
      throw error;
    }
  });

  ipcMain.handle('requests:delete', (_event, id: string) => {
    try {
      db.deleteRequest(id);
    } catch (error) {
      console.error('Error deleting request:', error);
      throw error;
    }
  });

  // ==================== Environments ====================

  ipcMain.handle('environments:getAll', () => {
    try {
      return db.getAllEnvironments();
    } catch (error) {
      console.error('Error getting environments:', error);
      throw error;
    }
  });

  ipcMain.handle('environments:getActive', () => {
    try {
      return db.getActiveEnvironment();
    } catch (error) {
      console.error('Error getting active environment:', error);
      throw error;
    }
  });

  ipcMain.handle('environments:create', (_event, environment: Omit<Environment, 'createdAt' | 'updatedAt'>) => {
    try {
      return db.createEnvironment(environment);
    } catch (error) {
      console.error('Error creating environment:', error);
      throw error;
    }
  });

  ipcMain.handle('environments:update', (_event, id: string, updates: Partial<Environment>) => {
    try {
      return db.updateEnvironment(id, updates);
    } catch (error) {
      console.error('Error updating environment:', error);
      throw error;
    }
  });

  ipcMain.handle('environments:delete', (_event, id: string) => {
    try {
      db.deleteEnvironment(id);
    } catch (error) {
      console.error('Error deleting environment:', error);
      throw error;
    }
  });

  // ==================== Variables ====================

  ipcMain.handle('variables:get', (_event, scope: string, scopeId?: string) => {
    try {
      const variables = db.getVariablesByScope(scope, scopeId);
      const result: Record<string, any> = {};
      variables.forEach(v => {
        if (v.enabled) {
          result[v.key] = v.value;
        }
      });
      return result;
    } catch (error) {
      console.error('Error getting variables:', error);
      throw error;
    }
  });

  ipcMain.handle('variables:set', (_event, scope: string, key: string, value: any, scopeId?: string) => {
    try {
      return db.setVariable({
        key,
        value,
        type: typeof value as any,
        scope: scope as any,
        scopeId,
        enabled: true,
      });
    } catch (error) {
      console.error('Error setting variable:', error);
      throw error;
    }
  });

  ipcMain.handle('variables:delete', (_event, scope: string, key: string, scopeId?: string) => {
    try {
      db.deleteVariable(scope, key, scopeId);
    } catch (error) {
      console.error('Error deleting variable:', error);
      throw error;
    }
  });

  // ==================== Settings ====================

  ipcMain.handle('settings:get', (_event, key?: string) => {
    try {
      const allSettings = db.getAllSettings();
      if (key) {
        return (allSettings as any)[key];
      }
      return allSettings;
    } catch (error) {
      console.error('Error getting settings:', error);
      throw error;
    }
  });

  ipcMain.handle('settings:set', (_event, key: string, value: any) => {
    try {
      db.setSetting(key, value);
    } catch (error) {
      console.error('Error setting setting:', error);
      throw error;
    }
  });

  ipcMain.handle('settings:update', (_event, settings: Record<string, any>) => {
    try {
      Object.entries(settings).forEach(([key, value]) => {
        db.setSetting(key, value);
      });
    } catch (error) {
      console.error('Error updating settings:', error);
      throw error;
    }
  });

  // ==================== Request Sending ====================

  ipcMain.handle('request:send', async (_event, request: Request, variables?: Record<string, any>) => {
    try {
      console.log('Sending request:', request.method, request.url);
      const response = await requestService.sendRequest(request, variables || {});
      console.log('Response received:', response.status, response.statusText);
      return response;
    } catch (error) {
      console.error('Error sending request:', error);
      throw error;
    }
  });

  // ==================== Secrets ====================

  ipcMain.handle('secrets:isAvailable', () => {
    return secretsService.isAvailable();
  });

  ipcMain.handle('secrets:set', async (_event, scope: string, key: string, value: string, description?: string) => {
    try {
      return await secretsService.setSecret(scope, key, value, description);
    } catch (error) {
      console.error('Error setting secret:', error);
      throw error;
    }
  });

  ipcMain.handle('secrets:get', async (_event, scope: string, key: string) => {
    try {
      return await secretsService.getSecret(scope, key);
    } catch (error) {
      console.error('Error getting secret:', error);
      throw error;
    }
  });

  ipcMain.handle('secrets:delete', async (_event, scope: string, key: string) => {
    try {
      return await secretsService.deleteSecret(scope, key);
    } catch (error) {
      console.error('Error deleting secret:', error);
      throw error;
    }
  });

  ipcMain.handle('secrets:getByScope', async (_event, scope: string) => {
    try {
      const secrets = await secretsService.getSecretsByScope(scope);
      return Object.fromEntries(secrets);
    } catch (error) {
      console.error('Error getting secrets by scope:', error);
      throw error;
    }
  });

  ipcMain.handle('secrets:deleteByScope', async (_event, scope: string) => {
    try {
      return await secretsService.deleteSecretsByScope(scope);
    } catch (error) {
      console.error('Error deleting secrets by scope:', error);
      throw error;
    }
  });

  ipcMain.handle('secrets:has', async (_event, scope: string, key: string) => {
    try {
      return await secretsService.hasSecret(scope, key);
    } catch (error) {
      console.error('Error checking secret:', error);
      throw error;
    }
  });

  // ==================== Cache ====================

  ipcMain.handle('cache:getStats', () => {
    try {
      return requestService.getCacheStats();
    } catch (error) {
      console.error('Error getting cache stats:', error);
      throw error;
    }
  });

  ipcMain.handle('cache:clear', () => {
    try {
      requestService.clearCache();
      return true;
    } catch (error) {
      console.error('Error clearing cache:', error);
      throw error;
    }
  });

  ipcMain.handle('cache:cleanExpired', () => {
    try {
      return requestService.getCacheService().cleanExpired();
    } catch (error) {
      console.error('Error cleaning expired cache:', error);
      throw error;
    }
  });

  ipcMain.handle('cache:invalidateByTags', (_event, tags: string[]) => {
    try {
      return requestService.invalidateCacheByTags(tags);
    } catch (error) {
      console.error('Error invalidating cache by tags:', error);
      throw error;
    }
  });

  ipcMain.handle('cache:invalidateByPattern', (_event, pattern: string) => {
    try {
      const regex = new RegExp(pattern);
      return requestService.invalidateCacheByPattern(regex);
    } catch (error) {
      console.error('Error invalidating cache by pattern:', error);
      throw error;
    }
  });

  ipcMain.handle('cache:configure', (_event, config: { enabled?: boolean; defaultTTL?: number; maxSize?: number }) => {
    try {
      const cacheService = requestService.getCacheService();
      
      if (config.enabled !== undefined) {
        config.enabled ? cacheService.enable() : cacheService.disable();
      }
      
      if (config.defaultTTL !== undefined) {
        cacheService.setDefaultTTL(config.defaultTTL * 60 * 1000); // Convert minutes to ms
      }
      
      if (config.maxSize !== undefined) {
        cacheService.setMaxSize(config.maxSize);
      }
      
      return true;
    } catch (error) {
      console.error('Error configuring cache:', error);
      throw error;
    }
  });

  // ==================== Import/Export ====================

  ipcMain.handle('importExport:getSupportedFormats', () => {
    try {
      return {
        import: importExportService.getSupportedImportFormats(),
        export: importExportService.getSupportedExportFormats(),
      };
    } catch (error) {
      console.error('Error getting supported formats:', error);
      throw error;
    }
  });

  ipcMain.handle('importExport:detectFormat', (_event, content: string) => {
    try {
      return importExportService.detectFormat(content);
    } catch (error) {
      console.error('Error detecting format:', error);
      throw error;
    }
  });

  ipcMain.handle('importExport:import', async (_event, content: string, format?: ImportExportFormat, options?: ImportExportOptions) => {
    try {
      return await importExportService.import(content, format, options);
    } catch (error) {
      console.error('Error importing:', error);
      throw error;
    }
  });

  ipcMain.handle('importExport:exportCollections', async (_event, collectionIds: string[], format: ImportExportFormat, options?: ImportExportOptions) => {
    try {
      const collections = collectionIds
        .map(id => db.getCollectionById(id))
        .filter((col): col is Collection => col !== null);
      return await importExportService.exportCollections(collections, format, options);
    } catch (error) {
      console.error('Error exporting collections:', error);
      throw error;
    }
  });

  ipcMain.handle('importExport:exportRequest', async (_event, requestId: string, format: ImportExportFormat, options?: ImportExportOptions) => {
    try {
      const request = db.getRequestById(requestId);
      if (!request) {
        throw new Error(`Request not found: ${requestId}`);
      }
      return await importExportService.exportRequest(request, format, options);
    } catch (error) {
      console.error('Error exporting request:', error);
      throw error;
    }
  });

  ipcMain.handle('importExport:exportRequests', async (_event, requestIds: string[], format: ImportExportFormat, options?: ImportExportOptions) => {
    try {
      const requests = requestIds
        .map(id => db.getRequestById(id))
        .filter((req): req is Request => req !== null);
      return await importExportService.exportRequests(requests, format, options);
    } catch (error) {
      console.error('Error exporting requests:', error);
      throw error;
    }
  });

  ipcMain.handle('importExport:getHandlerInfo', (_event, format: ImportExportFormat) => {
    try {
      return importExportService.getHandlerInfo(format);
    } catch (error) {
      console.error('Error getting handler info:', error);
      throw error;
    }
  });

  ipcMain.handle('importExport:getExample', (_event, format: ImportExportFormat) => {
    try {
      return importExportService.getExample(format);
    } catch (error) {
      console.error('Error getting example:', error);
      throw error;
    }
  });

  // ==================== Git ====================

  ipcMain.handle('git:isRepository', async () => {
    try {
      return await gitService.isRepository();
    } catch (error) {
      console.error('Error checking repository:', error);
      throw error;
    }
  });

  ipcMain.handle('git:init', async () => {
    try {
      await gitService.init();
      return true;
    } catch (error) {
      console.error('Error initializing repository:', error);
      throw error;
    }
  });

  ipcMain.handle('git:getStatus', async () => {
    try {
      return await gitService.getStatus();
    } catch (error) {
      console.error('Error getting status:', error);
      throw error;
    }
  });

  ipcMain.handle('git:add', async (_event, files: string[] | string) => {
    try {
      await gitService.add(files);
      return true;
    } catch (error) {
      console.error('Error staging files:', error);
      throw error;
    }
  });

  ipcMain.handle('git:reset', async (_event, files?: string[]) => {
    try {
      await gitService.reset(files);
      return true;
    } catch (error) {
      console.error('Error unstaging files:', error);
      throw error;
    }
  });

  ipcMain.handle('git:commit', async (_event, options: GitCommitOptions) => {
    try {
      const hash = await gitService.commit(options);
      return hash;
    } catch (error) {
      console.error('Error committing:', error);
      throw error;
    }
  });

  ipcMain.handle('git:getLog', async (_event, maxCount?: number) => {
    try {
      return await gitService.getLog(maxCount);
    } catch (error) {
      console.error('Error getting log:', error);
      throw error;
    }
  });

  ipcMain.handle('git:getDiff', async (_event, file?: string) => {
    try {
      return await gitService.getDiff(file);
    } catch (error) {
      console.error('Error getting diff:', error);
      throw error;
    }
  });

  ipcMain.handle('git:getDiffStaged', async (_event, file?: string) => {
    try {
      return await gitService.getDiffStaged(file);
    } catch (error) {
      console.error('Error getting staged diff:', error);
      throw error;
    }
  });

  ipcMain.handle('git:getBranches', async () => {
    try {
      return await gitService.getBranches();
    } catch (error) {
      console.error('Error getting branches:', error);
      throw error;
    }
  });

  ipcMain.handle('git:createBranch', async (_event, branchName: string, checkout: boolean) => {
    try {
      await gitService.createBranch(branchName, checkout);
      return true;
    } catch (error) {
      console.error('Error creating branch:', error);
      throw error;
    }
  });

  ipcMain.handle('git:checkout', async (_event, branchName: string) => {
    try {
      await gitService.checkout(branchName);
      return true;
    } catch (error) {
      console.error('Error checking out branch:', error);
      throw error;
    }
  });

  ipcMain.handle('git:hasChanges', async () => {
    try {
      return await gitService.hasChanges();
    } catch (error) {
      console.error('Error checking changes:', error);
      return false;
    }
  });

  ipcMain.handle('git:discardChanges', async (_event, files?: string[]) => {
    try {
      await gitService.discardChanges(files);
      return true;
    } catch (error) {
      console.error('Error discarding changes:', error);
      throw error;
    }
  });

  ipcMain.handle('git:getConfig', async (_event, key: string) => {
    try {
      return await gitService.getConfig(key);
    } catch (error) {
      console.error('Error getting config:', error);
      throw error;
    }
  });

  ipcMain.handle('git:setConfig', async (_event, key: string, value: string) => {
    try {
      await gitService.setConfig(key, value);
      return true;
    } catch (error) {
      console.error('Error setting config:', error);
      throw error;
    }
  });

  // ==================== Plugins ====================

  ipcMain.handle('plugins:discover', async () => {
    try {
      return await pluginLoader.discoverPlugins();
    } catch (error) {
      console.error('Error discovering plugins:', error);
      throw error;
    }
  });

  ipcMain.handle('plugins:load', async (_event, pluginDir: string) => {
    try {
      return await pluginLoader.loadPlugin(pluginDir);
    } catch (error) {
      console.error('Error loading plugin:', error);
      throw error;
    }
  });

  ipcMain.handle('plugins:unload', async (_event, pluginId: string) => {
    try {
      return await pluginLoader.unloadPlugin(pluginId);
    } catch (error) {
      console.error('Error unloading plugin:', error);
      throw error;
    }
  });

  ipcMain.handle('plugins:reload', async (_event, pluginId: string) => {
    try {
      return await pluginLoader.reloadPlugin(pluginId);
    } catch (error) {
      console.error('Error reloading plugin:', error);
      throw error;
    }
  });

  ipcMain.handle('plugins:setEnabled', async (_event, pluginId: string, enabled: boolean) => {
    try {
      return pluginLoader.setPluginEnabled(pluginId, enabled);
    } catch (error) {
      console.error('Error setting plugin enabled:', error);
      throw error;
    }
  });

  ipcMain.handle('plugins:getAll', async () => {
    try {
      return pluginLoader.getAllPlugins();
    } catch (error) {
      console.error('Error getting plugins:', error);
      throw error;
    }
  });

  ipcMain.handle('plugins:getInfo', async (_event, pluginId: string) => {
    try {
      return pluginLoader.getPluginInfo(pluginId);
    } catch (error) {
      console.error('Error getting plugin info:', error);
      throw error;
    }
  });

  ipcMain.handle('plugins:openPluginsFolder', async () => {
    try {
      const { shell, app } = require('electron');
      const path = require('path');
      const pluginsPath = path.join(app.getPath('userData'), 'plugins');
      await shell.openPath(pluginsPath);
      return { success: true };
    } catch (error) {
      console.error('Error opening plugins folder:', error);
      throw error;
    }
  });

  // ==================== Reports ====================

  ipcMain.handle('reports:generate', async (_event, data: any, options: ReportOptions) => {
    try {
      return await reportGenerator.generateReport(data, options);
    } catch (error) {
      console.error('Error generating report:', error);
      throw error;
    }
  });

  // ==================== Mock Server ====================

  const { MockServerService } = require('../services/MockServerService');
  const mockServerService = new MockServerService();

  ipcMain.handle('mockServer:create', async (_event, options: any) => {
    try {
      return await mockServerService.createServer(options);
    } catch (error) {
      console.error('Error creating mock server:', error);
      throw error;
    }
  });

  ipcMain.handle('mockServer:start', async (_event, serverId: string) => {
    try {
      return await mockServerService.startServer(serverId);
    } catch (error) {
      console.error('Error starting mock server:', error);
      throw error;
    }
  });

  ipcMain.handle('mockServer:stop', async (_event, serverId: string) => {
    try {
      return await mockServerService.stopServer(serverId);
    } catch (error) {
      console.error('Error stopping mock server:', error);
      throw error;
    }
  });

  ipcMain.handle('mockServer:delete', async (_event, serverId: string) => {
    try {
      return await mockServerService.deleteServer(serverId);
    } catch (error) {
      console.error('Error deleting mock server:', error);
      throw error;
    }
  });

  ipcMain.handle('mockServer:getAll', () => {
    try {
      return mockServerService.getAllServers();
    } catch (error) {
      console.error('Error getting mock servers:', error);
      throw error;
    }
  });

  ipcMain.handle('mockServer:getInfo', (_event, serverId: string) => {
    try {
      return mockServerService.getServerInfo(serverId);
    } catch (error) {
      console.error('Error getting mock server info:', error);
      throw error;
    }
  });

  ipcMain.handle('mockServer:getLogs', (_event, serverId: string) => {
    try {
      return mockServerService.getServerLogs(serverId);
    } catch (error) {
      console.error('Error getting mock server logs:', error);
      throw error;
    }
  });

  ipcMain.handle('mockServer:getStats', (_event, serverId: string) => {
    try {
      return mockServerService.getServerStats(serverId);
    } catch (error) {
      console.error('Error getting mock server stats:', error);
      throw error;
    }
  });

  // ==================== Batch Runner ====================

  const { BatchRunnerService } = require('../services/BatchRunnerService');
  const batchRunnerService = new BatchRunnerService(requestService);

  ipcMain.handle('batch:run', async (_event, requests: any[], variables?: any) => {
    try {
      return await batchRunnerService.runBatch(requests, variables);
    } catch (error) {
      console.error('Error running batch:', error);
      throw error;
    }
  });

  ipcMain.handle('batch:getResults', (_event, batchId: string) => {
    try {
      return batchRunnerService.getBatchResults(batchId);
    } catch (error) {
      console.error('Error getting batch results:', error);
      throw error;
    }
  });

  // ==================== Monitoring ====================

  const { CronMonitorService } = require('../services/CronMonitorService');
  const monitorService = new CronMonitorService(requestService);

  ipcMain.handle('monitor:create', async (_event, options: any) => {
    try {
      return await monitorService.createMonitor(options);
    } catch (error) {
      console.error('Error creating monitor:', error);
      throw error;
    }
  });

  ipcMain.handle('monitor:start', async (_event, monitorId: string) => {
    try {
      return await monitorService.startMonitor(monitorId);
    } catch (error) {
      console.error('Error starting monitor:', error);
      throw error;
    }
  });

  ipcMain.handle('monitor:stop', async (_event, monitorId: string) => {
    try {
      return await monitorService.stopMonitor(monitorId);
    } catch (error) {
      console.error('Error stopping monitor:', error);
      throw error;
    }
  });

  ipcMain.handle('monitor:delete', async (_event, monitorId: string) => {
    try {
      return await monitorService.deleteMonitor(monitorId);
    } catch (error) {
      console.error('Error deleting monitor:', error);
      throw error;
    }
  });

  ipcMain.handle('monitor:getAll', () => {
    try {
      return monitorService.getAllMonitors();
    } catch (error) {
      console.error('Error getting monitors:', error);
      throw error;
    }
  });

  ipcMain.handle('monitor:getLogs', (_event, monitorId: string) => {
    try {
      return monitorService.getMonitorLogs(monitorId);
    } catch (error) {
      console.error('Error getting monitor logs:', error);
      throw error;
    }
  });

  ipcMain.handle('monitor:getStats', (_event, monitorId: string) => {
    try {
      return monitorService.getMonitorStats(monitorId);
    } catch (error) {
      console.error('Error getting monitor stats:', error);
      throw error;
    }
  });

  // ==================== Security ====================

  const { SecurityAssertionService } = require('../services/SecurityAssertionService');
  const securityService = new SecurityAssertionService();

  ipcMain.handle('security:scan', async (_event, request: any, response: any) => {
    try {
      return await securityService.runSecurityAssertions(request, response);
    } catch (error) {
      console.error('Error running security scan:', error);
      throw error;
    }
  });

  ipcMain.handle('security:scanCollection', async (_event, collectionId: string) => {
    try {
      const requests = db.getRequestsByCollection(collectionId);
      const results = [];
      
      for (const request of requests) {
        const response = await requestService.sendRequest(request, {});
        const scanResult = await securityService.runSecurityAssertions(request, response);
        results.push({ request, scanResult });
      }
      
      return results;
    } catch (error) {
      console.error('Error scanning collection:', error);
      throw error;
    }
  });

  // ==================== Vulnerability Scanner ====================

  const { VulnerabilityScannerService } = require('../services/VulnerabilityScannerService');
  const vulnerabilityService = new VulnerabilityScannerService(requestService);

  ipcMain.handle('vulnerability:scan', async (_event, request: any, options?: any) => {
    try {
      return await vulnerabilityService.scanRequest(request, options);
    } catch (error) {
      console.error('Error running vulnerability scan:', error);
      throw error;
    }
  });

  ipcMain.handle('vulnerability:scanEndpoint', async (_event, url: string, method: string, options?: any) => {
    try {
      return await vulnerabilityService.scanEndpoint(url, method, options);
    } catch (error) {
      console.error('Error scanning endpoint:', error);
      throw error;
    }
  });

  // ==================== OWASP Scanner ====================

  const { getOWASPScannerService } = require('../services/OWASPScannerService');
  const owaspScanner = getOWASPScannerService();

  ipcMain.handle('owasp:scan', async (_event, options: any) => {
    try {
      return await owaspScanner.runScan(options);
    } catch (error) {
      console.error('Error running OWASP scan:', error);
      throw error;
    }
  });

  // ==================== Fuzzing Service ====================

  const { getFuzzingService } = require('../services/FuzzingService');
  const fuzzingService = getFuzzingService();

  ipcMain.handle('fuzzing:run', async (_event, options: any) => {
    try {
      return await fuzzingService.runFuzzing(options);
    } catch (error) {
      console.error('Error running fuzzing test:', error);
      throw error;
    }
  });

  // ==================== ZAP Proxy Service ====================

  const { getZAPProxyService, resetZAPProxyService } = require('../services/ZAPProxyService');

  ipcMain.handle('zap:checkConnection', async (_event, config: any) => {
    try {
      const zapService = getZAPProxyService(config);
      return await zapService.checkConnection();
    } catch (error) {
      console.error('Error checking ZAP connection:', error);
      return false;
    }
  });

  ipcMain.handle('zap:getVersion', async (_event) => {
    try {
      const zapService = getZAPProxyService();
      return await zapService.getVersion();
    } catch (error) {
      console.error('Error getting ZAP version:', error);
      throw error;
    }
  });

  ipcMain.handle('zap:runScan', async (_event, options: any) => {
    try {
      const zapService = getZAPProxyService();
      return await zapService.runScan(options);
    } catch (error) {
      console.error('Error running ZAP scan:', error);
      throw error;
    }
  });

  ipcMain.handle('zap:getAlerts', async (_event, url?: string) => {
    try {
      const zapService = getZAPProxyService();
      return await zapService.getAlerts(url);
    } catch (error) {
      console.error('Error getting ZAP alerts:', error);
      throw error;
    }
  });

  ipcMain.handle('zap:clearAlerts', async (_event) => {
    try {
      const zapService = getZAPProxyService();
      await zapService.clearAlerts();
    } catch (error) {
      console.error('Error clearing ZAP alerts:', error);
      throw error;
    }
  });

  ipcMain.handle('zap:generateHtmlReport', async (_event) => {
    try {
      const zapService = getZAPProxyService();
      return await zapService.generateHtmlReport();
    } catch (error) {
      console.error('Error generating HTML report:', error);
      throw error;
    }
  });

  ipcMain.handle('zap:generateXmlReport', async (_event) => {
    try {
      const zapService = getZAPProxyService();
      return await zapService.generateXmlReport();
    } catch (error) {
      console.error('Error generating XML report:', error);
      throw error;
    }
  });

  ipcMain.handle('zap:disconnect', async (_event) => {
    try {
      resetZAPProxyService();
    } catch (error) {
      console.error('Error disconnecting ZAP:', error);
      throw error;
    }
  });

  // ==================== Enhanced Import/Export (v0.8.0) ====================

  ipcMain.handle('import:detectFormat', async (_event, content: string) => {
    try {
      const { getImportService } = await import('../services/ImportService');
      const importService = getImportService();
      return await importService.detectFormat(content);
    } catch (error) {
      console.error('Error detecting import format:', error);
      throw error;
    }
  });

  ipcMain.handle('import:validate', async (_event, content: string, format?: ImportExportFormat) => {
    try {
      const { getImportService } = await import('../services/ImportService');
      const importService = getImportService();
      return await importService.validate(content, format);
    } catch (error) {
      console.error('Error validating import:', error);
      throw error;
    }
  });

  ipcMain.handle('import:import', async (_event, content: string, options: ImportExportOptions) => {
    try {
      const { getImportService } = await import('../services/ImportService');
      const importService = getImportService();
      return await importService.import(content, options);
    } catch (error) {
      console.error('Error importing:', error);
      throw error;
    }
  });

  ipcMain.handle('import:importFromFile', async (_event, filePath: string, options: ImportExportOptions) => {
    try {
      const { getImportService } = await import('../services/ImportService');
      const importService = getImportService();
      return await importService.importFromFile(filePath, options);
    } catch (error) {
      console.error('Error importing from file:', error);
      throw error;
    }
  });

  ipcMain.handle('import:importFromURL', async (_event, url: string, options: ImportExportOptions) => {
    try {
      const { getImportService } = await import('../services/ImportService');
      const importService = getImportService();
      return await importService.importFromURL(url, options);
    } catch (error) {
      console.error('Error importing from URL:', error);
      throw error;
    }
  });

  ipcMain.handle('import:getSupportedFormats', async (_event) => {
    try {
      const { getImportService } = await import('../services/ImportService');
      const importService = getImportService();
      return importService.getSupportedFormats();
    } catch (error) {
      console.error('Error getting supported formats:', error);
      throw error;
    }
  });

  ipcMain.handle('import:getHandlers', async (_event) => {
    try {
      const { getImportService } = await import('../services/ImportService');
      const importService = getImportService();
      return importService.getHandlers().map(h => ({
        format: h.format,
        name: h.name,
        description: h.description,
        fileExtensions: h.fileExtensions,
      }));
    } catch (error) {
      console.error('Error getting import handlers:', error);
      throw error;
    }
  });

  ipcMain.handle('import:getHistory', async (_event) => {
    try {
      const { getImportService } = await import('../services/ImportService');
      const importService = getImportService();
      return importService.getHistory();
    } catch (error) {
      console.error('Error getting import history:', error);
      throw error;
    }
  });

  ipcMain.handle('import:clearHistory', async (_event) => {
    try {
      const { getImportService } = await import('../services/ImportService');
      const importService = getImportService();
      importService.clearHistory();
    } catch (error) {
      console.error('Error clearing import history:', error);
      throw error;
    }
  });

  // ==================== Enhanced Export (v0.8.0) ====================

  ipcMain.handle('export:exportCollections', async (_event, collectionIds: string[], format: ImportExportFormat, options: ImportExportOptions) => {
    try {
      const { getExportService } = await import('../services/ExportService');
      const exportService = getExportService();
      return await exportService.exportCollections(collectionIds, format, options);
    } catch (error) {
      console.error('Error exporting collections:', error);
      throw error;
    }
  });

  ipcMain.handle('export:exportRequest', async (_event, requestId: string, format: ImportExportFormat, options: ImportExportOptions) => {
    try {
      const { getExportService } = await import('../services/ExportService');
      const exportService = getExportService();
      return await exportService.exportRequest(requestId, format, options);
    } catch (error) {
      console.error('Error exporting request:', error);
      throw error;
    }
  });

  ipcMain.handle('export:exportRequests', async (_event, requestIds: string[], format: ImportExportFormat, options: ImportExportOptions) => {
    try {
      const { getExportService } = await import('../services/ExportService');
      const exportService = getExportService();
      return await exportService.exportRequests(requestIds, format, options);
    } catch (error) {
      console.error('Error exporting requests:', error);
      throw error;
    }
  });

  ipcMain.handle('export:saveToFile', async (_event, content: string, filePath: string, format: ImportExportFormat) => {
    try {
      const { getExportService } = await import('../services/ExportService');
      const exportService = getExportService();
      await exportService.saveToFile(content, filePath, format);
    } catch (error) {
      console.error('Error saving export to file:', error);
      throw error;
    }
  });

  ipcMain.handle('export:copyToClipboard', async (_event, content: string) => {
    try {
      const { getExportService } = await import('../services/ExportService');
      const exportService = getExportService();
      await exportService.copyToClipboard(content);
    } catch (error) {
      console.error('Error copying to clipboard:', error);
      throw error;
    }
  });

  ipcMain.handle('export:getSupportedFormats', async (_event) => {
    try {
      const { getExportService } = await import('../services/ExportService');
      const exportService = getExportService();
      return exportService.getSupportedFormats();
    } catch (error) {
      console.error('Error getting supported export formats:', error);
      throw error;
    }
  });

  ipcMain.handle('export:getGenerators', async (_event) => {
    try {
      const { getExportService } = await import('../services/ExportService');
      const exportService = getExportService();
      return exportService.getGenerators().map(g => ({
        format: g.format,
        name: g.name,
        description: g.description,
        fileExtensions: g.fileExtensions,
      }));
    } catch (error) {
      console.error('Error getting export generators:', error);
      throw error;
    }
  });

  ipcMain.handle('export:getHistory', async (_event) => {
    try {
      const { getExportService } = await import('../services/ExportService');
      const exportService = getExportService();
      return exportService.getHistory();
    } catch (error) {
      console.error('Error getting export history:', error);
      throw error;
    }
  });

  ipcMain.handle('export:clearHistory', async (_event) => {
    try {
      const { getExportService } = await import('../services/ExportService');
      const exportService = getExportService();
      exportService.clearHistory();
    } catch (error) {
      console.error('Error clearing export history:', error);
      throw error;
    }
  });

  // ==================== Variable Extraction ====================

  const extractorService = getVariableExtractorService();

  ipcMain.handle('extractor:extractFromJSON', (_event, body: any, path: string, variableName: string, scope: string) => {
    try {
      return extractorService.extractFromJSON(body, path, variableName, scope as any);
    } catch (error) {
      console.error('Error extracting from JSON:', error);
      throw error;
    }
  });

  ipcMain.handle('extractor:extractFromXML', async (_event, body: string, xpath: string, variableName: string, scope: string) => {
    try {
      return await extractorService.extractFromXML(body, xpath, variableName, scope as any);
    } catch (error) {
      console.error('Error extracting from XML:', error);
      throw error;
    }
  });

  ipcMain.handle('extractor:extractFromHeader', (_event, headers: Record<string, string>, headerName: string, variableName: string, scope: string) => {
    try {
      return extractorService.extractFromHeader(headers, headerName, variableName, scope as any);
    } catch (error) {
      console.error('Error extracting from header:', error);
      throw error;
    }
  });

  ipcMain.handle('extractor:extractWithRegex', (_event, content: string, pattern: string, variableName: string, scope: string, source: 'body' | 'header') => {
    try {
      return extractorService.extractWithRegex(content, pattern, variableName, scope as any, source);
    } catch (error) {
      console.error('Error extracting with regex:', error);
      throw error;
    }
  });

  ipcMain.handle('extractor:extractWithRules', async (_event, response: Response, rules: ExtractionRule[]) => {
    try {
      return await extractorService.extractWithRules(response, rules);
    } catch (error) {
      console.error('Error extracting with rules:', error);
      throw error;
    }
  });

  ipcMain.handle('extractor:addRule', (_event, rule: Omit<ExtractionRule, 'id' | 'createdAt' | 'updatedAt'>) => {
    try {
      return extractorService.addRule(rule);
    } catch (error) {
      console.error('Error adding extraction rule:', error);
      throw error;
    }
  });

  ipcMain.handle('extractor:updateRule', (_event, id: string, updates: Partial<ExtractionRule>) => {
    try {
      return extractorService.updateRule(id, updates);
    } catch (error) {
      console.error('Error updating extraction rule:', error);
      throw error;
    }
  });

  ipcMain.handle('extractor:deleteRule', (_event, id: string) => {
    try {
      return extractorService.deleteRule(id);
    } catch (error) {
      console.error('Error deleting extraction rule:', error);
      throw error;
    }
  });

  ipcMain.handle('extractor:getRules', () => {
    try {
      return extractorService.getRules();
    } catch (error) {
      console.error('Error getting extraction rules:', error);
      throw error;
    }
  });

  ipcMain.handle('extractor:getRule', (_event, id: string) => {
    try {
      return extractorService.getRule(id);
    } catch (error) {
      console.error('Error getting extraction rule:', error);
      throw error;
    }
  });

  ipcMain.handle('extractor:recordHistory', (_event, variableName: string, oldValue: any, newValue: any, scope: string, source: string, requestId?: string) => {
    try {
      extractorService.recordHistory(variableName, oldValue, newValue, scope as any, source, requestId);
    } catch (error) {
      console.error('Error recording variable history:', error);
      throw error;
    }
  });

  ipcMain.handle('extractor:getHistory', (_event, variableName?: string, limit?: number) => {
    try {
      return extractorService.getHistory(variableName, limit);
    } catch (error) {
      console.error('Error getting variable history:', error);
      throw error;
    }
  });

  ipcMain.handle('extractor:clearHistory', (_event, variableName?: string) => {
    try {
      extractorService.clearHistory(variableName);
    } catch (error) {
      console.error('Error clearing variable history:', error);
      throw error;
    }
  });

  ipcMain.handle('extractor:suggestMethod', (_event, response: Response) => {
    try {
      return extractorService.suggestExtractionMethod(response);
    } catch (error) {
      console.error('Error suggesting extraction method:', error);
      throw error;
    }
  });

  ipcMain.handle('extractor:exportRules', () => {
    try {
      return extractorService.exportRules();
    } catch (error) {
      console.error('Error exporting rules:', error);
      throw error;
    }
  });

  ipcMain.handle('extractor:importRules', (_event, json: string) => {
    try {
      return extractorService.importRules(json);
    } catch (error) {
      console.error('Error importing rules:', error);
      throw error;
    }
  });

  // ==================== Workspace ====================

  const workspaceService = getWorkspaceService();

  ipcMain.handle('workspace:create', (_event, name: string, description?: string) => {
    try {
      return workspaceService.createWorkspace(name, description);
    } catch (error) {
      console.error('Error creating workspace:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:save', (_event, workspace?: Workspace) => {
    try {
      return workspaceService.saveWorkspace(workspace);
    } catch (error) {
      console.error('Error saving workspace:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:load', (_event, workspaceId: string) => {
    try {
      return workspaceService.loadWorkspace(workspaceId);
    } catch (error) {
      console.error('Error loading workspace:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:getCurrent', () => {
    try {
      return workspaceService.getCurrentWorkspace();
    } catch (error) {
      console.error('Error getting current workspace:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:update', (_event, updates: Partial<Workspace>) => {
    try {
      workspaceService.updateWorkspace(updates);
      return workspaceService.getCurrentWorkspace();
    } catch (error) {
      console.error('Error updating workspace:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:delete', (_event, workspaceId: string) => {
    try {
      return workspaceService.deleteWorkspace(workspaceId);
    } catch (error) {
      console.error('Error deleting workspace:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:list', () => {
    try {
      return workspaceService.listWorkspaces();
    } catch (error) {
      console.error('Error listing workspaces:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:getRecent', () => {
    try {
      return workspaceService.getRecentWorkspaces();
    } catch (error) {
      console.error('Error getting recent workspaces:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:export', (_event, workspaceId: string, exportPath: string) => {
    try {
      return workspaceService.exportWorkspace(workspaceId, exportPath);
    } catch (error) {
      console.error('Error exporting workspace:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:import', (_event, importPath: string) => {
    try {
      return workspaceService.importWorkspace(importPath);
    } catch (error) {
      console.error('Error importing workspace:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:createSnapshot', (_event, name: string, description?: string) => {
    try {
      return workspaceService.createSnapshot(name, description);
    } catch (error) {
      console.error('Error creating snapshot:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:restoreSnapshot', (_event, snapshotId: string) => {
    try {
      return workspaceService.restoreSnapshot(snapshotId);
    } catch (error) {
      console.error('Error restoring snapshot:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:listSnapshots', (_event, workspaceId: string) => {
    try {
      return workspaceService.listSnapshots(workspaceId);
    } catch (error) {
      console.error('Error listing snapshots:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:deleteSnapshot', (_event, snapshotId: string) => {
    try {
      return workspaceService.deleteSnapshot(snapshotId);
    } catch (error) {
      console.error('Error deleting snapshot:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:saveAsTemplate', (_event, name: string, description?: string, tags?: string[]) => {
    try {
      return workspaceService.saveAsTemplate(name, description, tags);
    } catch (error) {
      console.error('Error saving template:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:loadFromTemplate', (_event, templateId: string, workspaceName: string) => {
    try {
      return workspaceService.loadFromTemplate(templateId, workspaceName);
    } catch (error) {
      console.error('Error loading from template:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:listTemplates', () => {
    try {
      return workspaceService.listTemplates();
    } catch (error) {
      console.error('Error listing templates:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:deleteTemplate', (_event, templateId: string) => {
    try {
      return workspaceService.deleteTemplate(templateId);
    } catch (error) {
      console.error('Error deleting template:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:startAutoSave', (_event, intervalSeconds?: number) => {
    try {
      workspaceService.startAutoSave(intervalSeconds);
    } catch (error) {
      console.error('Error starting auto-save:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:stopAutoSave', () => {
    try {
      workspaceService.stopAutoSave();
    } catch (error) {
      console.error('Error stopping auto-save:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:markDirty', () => {
    try {
      workspaceService.markDirty();
    } catch (error) {
      console.error('Error marking workspace dirty:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:isDirty', () => {
    try {
      return workspaceService.isDirtyWorkspace();
    } catch (error) {
      console.error('Error checking dirty status:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:backup', (_event, workspaceId: string, backupPath: string) => {
    try {
      return workspaceService.backupWorkspace(workspaceId, backupPath);
    } catch (error) {
      console.error('Error backing up workspace:', error);
      throw error;
    }
  });

  ipcMain.handle('workspace:restoreFromBackup', (_event, backupPath: string) => {
    try {
      return workspaceService.restoreFromBackup(backupPath);
    } catch (error) {
      console.error('Error restoring from backup:', error);
      throw error;
    }
  });

  // ==================== Console ====================

  ipcMain.handle('console:getEntries', (_event, filters?: any, limit?: number, offset?: number) => {
    try {
      return consoleService.getEntries(filters, limit, offset);
    } catch (error) {
      console.error('Error getting console entries:', error);
      throw error;
    }
  });

  ipcMain.handle('console:getEntry', (_event, id: string) => {
    try {
      return consoleService.getEntry(id);
    } catch (error) {
      console.error('Error getting console entry:', error);
      throw error;
    }
  });

  ipcMain.handle('console:searchEntries', (_event, query: string) => {
    try {
      return consoleService.searchEntries(query);
    } catch (error) {
      console.error('Error searching console entries:', error);
      throw error;
    }
  });

  ipcMain.handle('console:clearEntries', (_event, olderThan?: number) => {
    try {
      consoleService.clearEntries(olderThan);
    } catch (error) {
      console.error('Error clearing console entries:', error);
      throw error;
    }
  });

  ipcMain.handle('console:deleteEntry', (_event, id: string) => {
    try {
      return consoleService.deleteEntry(id);
    } catch (error) {
      console.error('Error deleting console entry:', error);
      throw error;
    }
  });

  ipcMain.handle('console:exportEntries', (_event, options: any) => {
    try {
      return consoleService.exportEntries(options);
    } catch (error) {
      console.error('Error exporting console entries:', error);
      throw error;
    }
  });

  ipcMain.handle('console:setPersistence', (_event, enabled: boolean) => {
    try {
      consoleService.setPersistence(enabled);
    } catch (error) {
      console.error('Error setting console persistence:', error);
      throw error;
    }
  });

  ipcMain.handle('console:setMaxEntries', (_event, max: number) => {
    try {
      consoleService.setMaxEntries(max);
    } catch (error) {
      console.error('Error setting max console entries:', error);
      throw error;
    }
  });

  ipcMain.handle('console:setPaused', (_event, paused: boolean) => {
    try {
      consoleService.setPaused(paused);
    } catch (error) {
      console.error('Error setting console paused state:', error);
      throw error;
    }
  });

  ipcMain.handle('console:isPaused', () => {
    try {
      return consoleService.isPausedState();
    } catch (error) {
      console.error('Error getting console paused state:', error);
      throw error;
    }
  });

  ipcMain.handle('console:getStats', () => {
    try {
      return consoleService.getStats();
    } catch (error) {
      console.error('Error getting console stats:', error);
      throw error;
    }
  });

  ipcMain.handle('console:logRequest', (_event, request: any, metadata?: any) => {
    try {
      return consoleService.logRequest(request, metadata);
    } catch (error) {
      console.error('Error logging request:', error);
      throw error;
    }
  });

  ipcMain.handle('console:logResponse', (_event, response: any, request: any, metadata?: any) => {
    try {
      return consoleService.logResponse(response, request, metadata);
    } catch (error) {
      console.error('Error logging response:', error);
      throw error;
    }
  });

  // ==================== API Specification Generation ====================

  ipcMain.handle('apispec:analyze', async (_event, entries: any[]) => {
    try {
      return analyzerService.analyzeRequests(entries);
    } catch (error) {
      console.error('Error analyzing requests:', error);
      throw error;
    }
  });

  ipcMain.handle('apispec:generateOpenAPI', async (_event, analysis: any, options: any) => {
    try {
      const spec = openApiService.generateSpec(analysis, options);
      return spec;
    } catch (error) {
      console.error('Error generating OpenAPI spec:', error);
      throw error;
    }
  });

  ipcMain.handle('apispec:generateAsyncAPI', async (_event, entries: any[], options: any) => {
    try {
      const spec = asyncApiService.generateSpec(entries, options);
      return spec;
    } catch (error) {
      console.error('Error generating AsyncAPI spec:', error);
      throw error;
    }
  });

  ipcMain.handle('apispec:generateGraphQL', async (_event, entries: any[]) => {
    try {
      const schema = graphqlService.generateSchema(entries);
      const sdl = graphqlService.generateSDL(schema);
      return { schema, sdl };
    } catch (error) {
      console.error('Error generating GraphQL schema:', error);
      throw error;
    }
  });

  ipcMain.handle('apispec:exportOpenAPIJSON', async (_event, spec: any) => {
    try {
      return openApiService.toJSON(spec);
    } catch (error) {
      console.error('Error exporting OpenAPI to JSON:', error);
      throw error;
    }
  });

  ipcMain.handle('apispec:exportOpenAPIYAML', async (_event, spec: any) => {
    try {
      return openApiService.toYAML(spec);
    } catch (error) {
      console.error('Error exporting OpenAPI to YAML:', error);
      throw error;
    }
  });

  ipcMain.handle('apispec:validateOpenAPI', async (_event, spec: any) => {
    try {
      return openApiService.validateSpec(spec);
    } catch (error) {
      console.error('Error validating OpenAPI spec:', error);
      throw error;
    }
  });

  ipcMain.handle('apispec:loadOpenAPIFile', async (_event, filePath: string) => {
    try {
      const fs = require('fs');
      const content = fs.readFileSync(filePath, 'utf-8');
      return JSON.parse(content);
    } catch (error) {
      console.error('Error loading OpenAPI file:', error);
      throw error;
    }
  });

  // Publishing handlers
  const { DocumentationGeneratorService } = require('../services/DocumentationGeneratorService');
  const { MarkdownExporterService } = require('../services/MarkdownExporterService');
  const { SDKGeneratorService } = require('../services/SDKGeneratorService');
  const { ChangelogGeneratorService } = require('../services/ChangelogGeneratorService');
  const { PublishingService } = require('../services/PublishingService');

  const docGenService = new DocumentationGeneratorService();
  const markdownService = new MarkdownExporterService();
  const sdkService = new SDKGeneratorService();
  const changelogService = new ChangelogGeneratorService();
  const publishingService = new PublishingService();

  ipcMain.handle('publishing:generateDocumentation', async (_event, spec: any, options: any) => {
    try {
      return docGenService.generateDocumentation(spec, options);
    } catch (error) {
      console.error('Error generating documentation:', error);
      throw error;
    }
  });

  ipcMain.handle('publishing:exportMarkdown', async (_event, spec: any, options: any) => {
    try {
      return markdownService.exportToMarkdown(spec, options);
    } catch (error) {
      console.error('Error exporting markdown:', error);
      throw error;
    }
  });

  ipcMain.handle('publishing:generateSDK', async (_event, spec: any, options: any) => {
    try {
      return sdkService.generateSDK(spec, options);
    } catch (error) {
      console.error('Error generating SDK:', error);
      throw error;
    }
  });

  ipcMain.handle('publishing:generateChangelog', async (_event, oldSpec: any, newSpec: any) => {
    try {
      return changelogService.generateChangelog(oldSpec, newSpec);
    } catch (error) {
      console.error('Error generating changelog:', error);
      throw error;
    }
  });

  ipcMain.handle('publishing:publish', async (_event, doc: any, options: any) => {
    try {
      return await publishingService.publish(doc, options);
    } catch (error) {
      console.error('Error publishing:', error);
      throw error;
    }
  });

  ipcMain.handle('publishing:stopServer', async () => {
    try {
      await publishingService.stopServer();
      return { success: true };
    } catch (error) {
      console.error('Error stopping server:', error);
      throw error;
    }
  });

  ipcMain.handle('publishing:getStatus', async () => {
    try {
      return publishingService.getStatus();
    } catch (error) {
      console.error('Error getting status:', error);
      throw error;
    }
  });

  ipcMain.handle('publishing:openDirectory', async (_event, directory: string) => {
    try {
      const { shell } = require('electron');
      await shell.openPath(directory);
      return { success: true };
    } catch (error) {
      console.error('Error opening directory:', error);
      throw error;
    }
  });

  // Settings handlers
  const { SettingsService } = require('../services/SettingsService');
  const settingsService = new SettingsService();

  ipcMain.handle('settings:getAll', async () => {
    try {
      return settingsService.getAllSettings();
    } catch (error) {
      console.error('Error getting settings:', error);
      throw error;
    }
  });

  ipcMain.handle('settings:save', async (_event, settings: any) => {
    try {
      // Update each section
      if (settings.network) await settingsService.updateNetworkSettings(settings.network);
      if (settings.editor) await settingsService.updateEditorSettings(settings.editor);
      if (settings.shortcuts) await settingsService.updateShortcuts(settings.shortcuts);
      if (settings.language) await settingsService.updateLanguageSettings(settings.language);
      if (settings.cache) await settingsService.updateCacheSettings(settings.cache);
      if (settings.autoSave) await settingsService.updateAutoSaveSettings(settings.autoSave);
      if (settings.privacy) await settingsService.updatePrivacySettings(settings.privacy);
      if (settings.plugins) await settingsService.updatePluginSettings(settings.plugins);
      if (settings.backup) await settingsService.updateBackupSettings(settings.backup);
      settingsService.saveSettings();
      return { success: true };
    } catch (error) {
      console.error('Error saving settings:', error);
      throw error;
    }
  });

  ipcMain.handle('settings:getNetwork', async () => {
    try {
      return settingsService.getNetworkSettings();
    } catch (error) {
      console.error('Error getting network settings:', error);
      throw error;
    }
  });

  ipcMain.handle('settings:getEditor', async () => {
    try {
      return settingsService.getEditorSettings();
    } catch (error) {
      console.error('Error getting editor settings:', error);
      throw error;
    }
  });

  ipcMain.handle('settings:export', async () => {
    try {
      const { dialog } = require('electron');
      const result = await dialog.showSaveDialog({
        title: 'Export Settings',
        defaultPath: 'localapi-settings.json',
        filters: [{ name: 'JSON', extensions: ['json'] }],
      });

      if (!result.canceled && result.filePath) {
        settingsService.exportSettings(result.filePath);
        return { success: true, path: result.filePath };
      }
      return { success: false };
    } catch (error) {
      console.error('Error exporting settings:', error);
      throw error;
    }
  });

  ipcMain.handle('settings:import', async () => {
    try {
      const { dialog } = require('electron');
      const result = await dialog.showOpenDialog({
        title: 'Import Settings',
        filters: [{ name: 'JSON', extensions: ['json'] }],
        properties: ['openFile'],
      });

      if (!result.canceled && result.filePaths.length > 0) {
        settingsService.importSettings(result.filePaths[0]);
        return { success: true };
      }
      return { success: false };
    } catch (error) {
      console.error('Error importing settings:', error);
      throw error;
    }
  });

  ipcMain.handle('settings:createBackup', async () => {
    try {
      const backupFile = settingsService.createBackup();
      return { success: true, file: backupFile };
    } catch (error) {
      console.error('Error creating backup:', error);
      throw error;
    }
  });

  ipcMain.handle('settings:listBackups', async () => {
    try {
      return settingsService.listBackups();
    } catch (error) {
      console.error('Error listing backups:', error);
      throw error;
    }
  });

  ipcMain.handle('settings:restoreBackup', async (_event, backupFile: string) => {
    try {
      settingsService.restoreBackup(backupFile);
      return { success: true };
    } catch (error) {
      console.error('Error restoring backup:', error);
      throw error;
    }
  });

  ipcMain.handle('settings:resetToDefaults', async () => {
    try {
      settingsService.resetToDefaults();
      return { success: true };
    } catch (error) {
      console.error('Error resetting settings:', error);
      throw error;
    }
  });

  ipcMain.handle('settings:validate', async (_event, settings: any) => {
    try {
      return settingsService.validateSettings(settings);
    } catch (error) {
      console.error('Error validating settings:', error);
      throw error;
    }
  });

  // Tab Manager handlers
  const { TabManagerService } = require('../services/TabManagerService');
  const tabManagerService = new TabManagerService();

  ipcMain.handle('tabs:create', async (_event, tab: any) => {
    try {
      return tabManagerService.createTab(tab);
    } catch (error) {
      console.error('Error creating tab:', error);
      throw error;
    }
  });

  ipcMain.handle('tabs:getAll', async () => {
    try {
      return tabManagerService.getAllTabs();
    } catch (error) {
      console.error('Error getting tabs:', error);
      throw error;
    }
  });

  ipcMain.handle('tabs:update', async (_event, id: string, updates: any) => {
    try {
      return tabManagerService.updateTab(id, updates);
    } catch (error) {
      console.error('Error updating tab:', error);
      throw error;
    }
  });

  ipcMain.handle('tabs:close', async (_event, id: string) => {
    try {
      return tabManagerService.closeTab(id);
    } catch (error) {
      console.error('Error closing tab:', error);
      throw error;
    }
  });

  ipcMain.handle('tabs:closeOthers', async (_event, keepId: string) => {
    try {
      return tabManagerService.closeOthers(keepId);
    } catch (error) {
      console.error('Error closing other tabs:', error);
      throw error;
    }
  });

  ipcMain.handle('tabs:closeAll', async () => {
    try {
      return tabManagerService.closeAll();
    } catch (error) {
      console.error('Error closing all tabs:', error);
      throw error;
    }
  });

  ipcMain.handle('tabs:setActive', async (_event, id: string) => {
    try {
      return tabManagerService.setActiveTab(id);
    } catch (error) {
      console.error('Error setting active tab:', error);
      throw error;
    }
  });

  ipcMain.handle('tabs:getActive', async () => {
    try {
      return tabManagerService.getActiveTab();
    } catch (error) {
      console.error('Error getting active tab:', error);
      throw error;
    }
  });

  ipcMain.handle('tabs:goBack', async () => {
    try {
      return tabManagerService.goBack();
    } catch (error) {
      console.error('Error going back:', error);
      throw error;
    }
  });

  ipcMain.handle('tabs:goForward', async () => {
    try {
      return tabManagerService.goForward();
    } catch (error) {
      console.error('Error going forward:', error);
      throw error;
    }
  });

  ipcMain.handle('tabs:search', async (_event, query: string) => {
    try {
      return tabManagerService.searchTabs(query);
    } catch (error) {
      console.error('Error searching tabs:', error);
      throw error;
    }
  });

  ipcMain.handle('tabs:reorder', async (_event, tabId: string, newIndex: number) => {
    try {
      return tabManagerService.reorderTab(tabId, newIndex);
    } catch (error) {
      console.error('Error reordering tab:', error);
      throw error;
    }
  });

  ipcMain.handle('tabs:createGroup', async (_event, name: string, color?: string) => {
    try {
      return tabManagerService.createGroup(name, color);
    } catch (error) {
      console.error('Error creating group:', error);
      throw error;
    }
  });

  ipcMain.handle('tabs:getAllGroups', async () => {
    try {
      return tabManagerService.getAllGroups();
    } catch (error) {
      console.error('Error getting groups:', error);
      throw error;
    }
  });

  ipcMain.handle('tabs:addToGroup', async (_event, tabId: string, groupId: string) => {
    try {
      return tabManagerService.addTabToGroup(tabId, groupId);
    } catch (error) {
      console.error('Error adding tab to group:', error);
      throw error;
    }
  });

  // Command Palette handlers
  const { CommandPaletteService } = require('../services/CommandPaletteService');
  const commandPaletteService = new CommandPaletteService();

  ipcMain.handle('commands:search', async (_event, query: string) => {
    try {
      return commandPaletteService.searchCommands(query);
    } catch (error) {
      console.error('Error searching commands:', error);
      throw error;
    }
  });

  ipcMain.handle('commands:execute', async (_event, id: string) => {
    try {
      return await commandPaletteService.executeCommand(id);
    } catch (error) {
      console.error('Error executing command:', error);
      throw error;
    }
  });

  ipcMain.handle('commands:getAll', async () => {
    try {
      return commandPaletteService.getAllCommands();
    } catch (error) {
      console.error('Error getting commands:', error);
      throw error;
    }
  });

  ipcMain.handle('commands:getRecent', async () => {
    try {
      return commandPaletteService.getRecentCommands();
    } catch (error) {
      console.error('Error getting recent commands:', error);
      throw error;
    }
  });

  // Favorites handlers
  const { FavoritesService } = require('../services/FavoritesService');
  const favoritesService = new FavoritesService();

  ipcMain.handle('favorites:add', async (_event, favorite: any) => {
    try {
      return favoritesService.addFavorite(favorite);
    } catch (error) {
      console.error('Error adding favorite:', error);
      throw error;
    }
  });

  ipcMain.handle('favorites:remove', async (_event, id: string) => {
    try {
      return favoritesService.removeFavorite(id);
    } catch (error) {
      console.error('Error removing favorite:', error);
      throw error;
    }
  });

  ipcMain.handle('favorites:getAll', async () => {
    try {
      return favoritesService.getAllFavorites();
    } catch (error) {
      console.error('Error getting favorites:', error);
      throw error;
    }
  });

  ipcMain.handle('favorites:toggle', async (_event, favorite: any) => {
    try {
      return favoritesService.toggleFavorite(favorite);
    } catch (error) {
      console.error('Error toggling favorite:', error);
      throw error;
    }
  });

  ipcMain.handle('favorites:isFavorite', async (_event, entityId: string) => {
    try {
      return favoritesService.isFavorite(entityId);
    } catch (error) {
      console.error('Error checking favorite:', error);
      throw error;
    }
  });

  ipcMain.handle('favorites:search', async (_event, query: string) => {
    try {
      return favoritesService.searchFavorites(query);
    } catch (error) {
      console.error('Error searching favorites:', error);
      throw error;
    }
  });

  ipcMain.handle('favorites:createFolder', async (_event, name: string, color?: string) => {
    try {
      return favoritesService.createFolder(name, color);
    } catch (error) {
      console.error('Error creating folder:', error);
      throw error;
    }
  });

  ipcMain.handle('favorites:getAllFolders', async () => {
    try {
      return favoritesService.getAllFolders();
    } catch (error) {
      console.error('Error getting folders:', error);
      throw error;
    }
  });

  // Layout Service handlers
  const layoutService = new LayoutService();

  ipcMain.handle('layout:getAll', async () => {
    try {
      return layoutService.getAllLayouts();
    } catch (error) {
      console.error('Error getting layouts:', error);
      throw error;
    }
  });

  ipcMain.handle('layout:getActive', async () => {
    try {
      return layoutService.getActiveLayout();
    } catch (error) {
      console.error('Error getting active layout:', error);
      throw error;
    }
  });

  ipcMain.handle('layout:setActive', async (_event, layoutId: string) => {
    try {
      return layoutService.setActiveLayout(layoutId);
    } catch (error) {
      console.error('Error setting active layout:', error);
      throw error;
    }
  });

  ipcMain.handle('layout:create', async (_event, name: string, panels: any[], description?: string) => {
    try {
      return layoutService.createLayout(name, panels, description);
    } catch (error) {
      console.error('Error creating layout:', error);
      throw error;
    }
  });

  ipcMain.handle('layout:update', async (_event, layoutId: string, updates: any) => {
    try {
      return layoutService.updateLayout(layoutId, updates);
    } catch (error) {
      console.error('Error updating layout:', error);
      throw error;
    }
  });

  ipcMain.handle('layout:delete', async (_event, layoutId: string) => {
    try {
      return layoutService.deleteLayout(layoutId);
    } catch (error) {
      console.error('Error deleting layout:', error);
      throw error;
    }
  });

  console.log('IPC handlers registered successfully');
}

// Export console service for use by other services
let globalConsoleService: ConsoleService | null = null;

export function setGlobalConsoleService(service: ConsoleService): void {
  globalConsoleService = service;
}

export function getGlobalConsoleService(): ConsoleService | null {
  return globalConsoleService;
}
