// Plugin Loader Service
import * as fs from 'fs';
import * as path from 'path';
import { randomUUID } from 'crypto';
import type {
  Plugin,
  PluginManifest,
  PluginContext,
  PluginInfo,
  PluginLoadResult,
  PluginRegistryEntry,
  PluginPermission,
} from '../../types/plugin';
import type { Request, Response } from '../../types/models';

export class PluginLoader {
  private plugins: Map<string, PluginRegistryEntry>;
  private pluginsDir: string;
  private dataDir: string;
  private hooks: Map<string, Set<string>>; // hook name -> plugin IDs

  constructor(pluginsDir: string, dataDir: string) {
    this.plugins = new Map();
    this.pluginsDir = pluginsDir;
    this.dataDir = dataDir;
    this.hooks = new Map();

    // Ensure directories exist
    if (!fs.existsSync(this.pluginsDir)) {
      fs.mkdirSync(this.pluginsDir, { recursive: true });
    }
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }
  }

  /**
   * Discover all plugins in plugins directory
   */
  async discoverPlugins(): Promise<string[]> {
    const pluginDirs: string[] = [];

    try {
      const entries = fs.readdirSync(this.pluginsDir, { withFileTypes: true });

      for (const entry of entries) {
        if (entry.isDirectory()) {
          const manifestPath = path.join(this.pluginsDir, entry.name, 'plugin.json');
          if (fs.existsSync(manifestPath)) {
            pluginDirs.push(entry.name);
          }
        }
      }
    } catch (error) {
      console.error('Failed to discover plugins:', error);
    }

    return pluginDirs;
  }

  /**
   * Load a plugin from directory
   */
  async loadPlugin(pluginDir: string): Promise<PluginLoadResult> {
    try {
      const pluginPath = path.join(this.pluginsDir, pluginDir);
      const manifestPath = path.join(pluginPath, 'plugin.json');

      // Read manifest
      if (!fs.existsSync(manifestPath)) {
        return {
          success: false,
          error: 'plugin.json not found',
        };
      }

      const manifestContent = fs.readFileSync(manifestPath, 'utf-8');
      const manifest: PluginManifest = JSON.parse(manifestContent);

      // Validate manifest
      if (!manifest.id || !manifest.name || !manifest.version || !manifest.main) {
        return {
          success: false,
          error: 'Invalid plugin manifest: missing required fields',
        };
      }

      // Check if already loaded
      if (this.plugins.has(manifest.id)) {
        return {
          success: false,
          error: 'Plugin already loaded',
        };
      }

      // Load main module
      const mainPath = path.join(pluginPath, manifest.main);
      if (!fs.existsSync(mainPath)) {
        return {
          success: false,
          error: `Main file not found: ${manifest.main}`,
        };
      }

      // Clear require cache for hot reload
      delete require.cache[require.resolve(mainPath)];

      // Load plugin module
      const pluginModule = require(mainPath);
      const plugin: Plugin = pluginModule.default || pluginModule;

      // Attach manifest
      plugin.manifest = manifest;

      // Create plugin context
      const context = this.createPluginContext(manifest);

      // Register plugin
      const entry: PluginRegistryEntry = {
        manifest,
        plugin,
        context,
        enabled: true,
        loaded: false,
      };

      this.plugins.set(manifest.id, entry);

      // Register hooks
      this.registerHooks(manifest.id, plugin);

      // Call onLoad hook
      try {
        if (plugin.onLoad) {
          await plugin.onLoad(context);
        }
        entry.loaded = true;
      } catch (error) {
        entry.error = error instanceof Error ? error.message : 'Load failed';
        entry.loaded = false;
      }

      return {
        success: true,
        plugin: this.getPluginInfo(manifest.id) || undefined,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * Unload a plugin
   */
  async unloadPlugin(pluginId: string): Promise<boolean> {
    const entry = this.plugins.get(pluginId);
    if (!entry) {
      return false;
    }

    try {
      // Call onUnload hook
      if (entry.plugin.onUnload && entry.loaded) {
        await entry.plugin.onUnload(entry.context);
      }

      // Unregister hooks
      this.unregisterHooks(pluginId);

      // Remove from registry
      this.plugins.delete(pluginId);

      return true;
    } catch (error) {
      console.error(`Failed to unload plugin ${pluginId}:`, error);
      return false;
    }
  }

  /**
   * Reload a plugin
   */
  async reloadPlugin(pluginId: string): Promise<PluginLoadResult> {
    const entry = this.plugins.get(pluginId);
    if (!entry) {
      return {
        success: false,
        error: 'Plugin not found',
      };
    }

    // Get plugin directory from manifest
    const pluginDir = path.basename(path.dirname(path.join(this.pluginsDir, entry.manifest.main)));

    // Unload
    await this.unloadPlugin(pluginId);

    // Load again
    return await this.loadPlugin(pluginDir);
  }

  /**
   * Enable/disable a plugin
   */
  setPluginEnabled(pluginId: string, enabled: boolean): boolean {
    const entry = this.plugins.get(pluginId);
    if (!entry) {
      return false;
    }

    entry.enabled = enabled;
    return true;
  }

  /**
   * Get all plugins
   */
  getAllPlugins(): PluginInfo[] {
    return Array.from(this.plugins.keys()).map(id => this.getPluginInfo(id)!);
  }

  /**
   * Get plugin info
   */
  getPluginInfo(pluginId: string): PluginInfo | null {
    const entry = this.plugins.get(pluginId);
    if (!entry) {
      return null;
    }

    return {
      id: entry.manifest.id,
      name: entry.manifest.name,
      version: entry.manifest.version,
      description: entry.manifest.description,
      author: entry.manifest.author,
      enabled: entry.enabled,
      loaded: entry.loaded,
      error: entry.error,
      permissions: entry.manifest.permissions || [],
    };
  }

  /**
   * Execute hook for all plugins
   */
  async executeHook(hookName: string, ...args: any[]): Promise<any> {
    const pluginIds = this.hooks.get(hookName);
    if (!pluginIds || pluginIds.size === 0) {
      return args[0]; // Return first argument unchanged
    }

    let result = args[0];

    for (const pluginId of pluginIds) {
      const entry = this.plugins.get(pluginId);
      if (!entry || !entry.enabled || !entry.loaded) {
        continue;
      }

      try {
        const hook = (entry.plugin as any)[hookName];
        if (hook && typeof hook === 'function') {
          result = await hook(result, ...args.slice(1), entry.context);
        }
      } catch (error) {
        console.error(`Plugin ${pluginId} hook ${hookName} failed:`, error);
        entry.error = error instanceof Error ? error.message : 'Hook execution failed';
      }
    }

    return result;
  }

  /**
   * Create plugin context
   */
  private createPluginContext(manifest: PluginManifest): PluginContext {
    const pluginDataDir = path.join(this.dataDir, manifest.id);
    if (!fs.existsSync(pluginDataDir)) {
      fs.mkdirSync(pluginDataDir, { recursive: true });
    }

    return {
      plugin: {
        id: manifest.id,
        name: manifest.name,
        version: manifest.version,
        dataDir: pluginDataDir,
      },
      api: {
        request: async (config: any) => {
          // Check permission
          if (!this.hasPermission(manifest, 'network')) {
            throw new Error('Plugin does not have network permission');
          }
          // Use axios or similar
          const axios = require('axios');
          return await axios(config);
        },
        notify: (message: string, type = 'info') => {
          console.log(`[${manifest.name}] ${type.toUpperCase()}: ${message}`);
          // TODO: Send to renderer for UI notification
        },
        log: (...args: any[]) => {
          console.log(`[${manifest.name}]`, ...args);
        },
        storage: {
          get: async (key: string) => {
            const storePath = path.join(pluginDataDir, 'storage.json');
            if (!fs.existsSync(storePath)) {
              return undefined;
            }
            const data: Record<string, any> = JSON.parse(fs.readFileSync(storePath, 'utf-8'));
            return data[key];
          },
          set: async (key: string, value: any) => {
            const storePath = path.join(pluginDataDir, 'storage.json');
            let data: Record<string, any> = {};
            if (fs.existsSync(storePath)) {
              data = JSON.parse(fs.readFileSync(storePath, 'utf-8'));
            }
            data[key] = value;
            fs.writeFileSync(storePath, JSON.stringify(data, null, 2));
          },
          delete: async (key: string) => {
            const storePath = path.join(pluginDataDir, 'storage.json');
            if (!fs.existsSync(storePath)) {
              return;
            }
            const data = JSON.parse(fs.readFileSync(storePath, 'utf-8'));
            delete data[key];
            fs.writeFileSync(storePath, JSON.stringify(data, null, 2));
          },
          clear: async () => {
            const storePath = path.join(pluginDataDir, 'storage.json');
            if (fs.existsSync(storePath)) {
              fs.unlinkSync(storePath);
            }
          },
        },
        settings: {
          get: async (key: string) => {
            // TODO: Integrate with settings service
            return null;
          },
          set: async (key: string, value: any) => {
            // TODO: Integrate with settings service
          },
        },
      },
      utils: {
        parseJSON: (text: string) => {
          try {
            return JSON.parse(text);
          } catch {
            return null;
          }
        },
        formatDate: (date: Date, format?: string) => {
          return date.toISOString();
        },
        uuid: () => randomUUID(),
      },
    };
  }

  /**
   * Register plugin hooks
   */
  private registerHooks(pluginId: string, plugin: Plugin): void {
    const hookNames = [
      'onLoad',
      'onUnload',
      'onBeforeRequest',
      'onAfterResponse',
      'onCollectionCreate',
      'onCollectionUpdate',
      'onCollectionDelete',
      'onSettingsChange',
    ];

    for (const hookName of hookNames) {
      if ((plugin as any)[hookName]) {
        if (!this.hooks.has(hookName)) {
          this.hooks.set(hookName, new Set());
        }
        this.hooks.get(hookName)!.add(pluginId);
      }
    }
  }

  /**
   * Unregister plugin hooks
   */
  private unregisterHooks(pluginId: string): void {
    for (const [hookName, pluginIds] of this.hooks.entries()) {
      pluginIds.delete(pluginId);
      if (pluginIds.size === 0) {
        this.hooks.delete(hookName);
      }
    }
  }

  /**
   * Check if plugin has permission
   */
  private hasPermission(manifest: PluginManifest, permission: PluginPermission): boolean {
    if (!manifest.permissions) {
      return false;
    }
    return manifest.permissions.includes(permission) || manifest.permissions.includes('all');
  }
}

// Singleton instance
let pluginLoaderInstance: PluginLoader | null = null;

export function getPluginLoader(pluginsDir?: string, dataDir?: string): PluginLoader {
  if (!pluginLoaderInstance && pluginsDir && dataDir) {
    pluginLoaderInstance = new PluginLoader(pluginsDir, dataDir);
  }
  if (!pluginLoaderInstance) {
    throw new Error('PluginLoader not initialized');
  }
  return pluginLoaderInstance;
}

export function initializePluginLoader(pluginsDir: string, dataDir: string): PluginLoader {
  pluginLoaderInstance = new PluginLoader(pluginsDir, dataDir);
  return pluginLoaderInstance;
}
