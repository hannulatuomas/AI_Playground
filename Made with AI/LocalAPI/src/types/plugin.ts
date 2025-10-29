// Plugin Type Definitions
import type { Request, Response } from './models';

/**
 * Plugin metadata
 */
export interface PluginManifest {
  id: string;
  name: string;
  version: string;
  description: string;
  author?: string;
  homepage?: string;
  license?: string;
  main: string; // Entry point file
  dependencies?: Record<string, string>;
  permissions?: PluginPermission[];
  hooks?: string[]; // List of hooks this plugin uses
}

/**
 * Plugin permissions
 */
export type PluginPermission =
  | 'network' // Make network requests
  | 'filesystem' // Read/write files
  | 'database' // Access database
  | 'clipboard' // Access clipboard
  | 'notifications' // Show notifications
  | 'settings' // Read/write settings
  | 'all'; // All permissions

/**
 * Plugin context provided to plugins
 */
export interface PluginContext {
  // Plugin info
  plugin: {
    id: string;
    name: string;
    version: string;
    dataDir: string; // Plugin's data directory
  };

  // API access
  api: {
    // Make HTTP requests
    request: (config: any) => Promise<any>;
    
    // Show notifications
    notify: (message: string, type?: 'info' | 'success' | 'warning' | 'error') => void;
    
    // Log messages
    log: (...args: any[]) => void;
    
    // Store plugin data
    storage: {
      get: (key: string) => Promise<any>;
      set: (key: string, value: any) => Promise<void>;
      delete: (key: string) => Promise<void>;
      clear: () => Promise<void>;
    };

    // Access settings
    settings: {
      get: (key: string) => Promise<any>;
      set: (key: string, value: any) => Promise<void>;
    };
  };

  // Utilities
  utils: {
    // Parse JSON safely
    parseJSON: (text: string) => any;
    
    // Format date
    formatDate: (date: Date, format?: string) => string;
    
    // Generate UUID
    uuid: () => string;
  };
}

/**
 * Plugin lifecycle hooks
 */
export interface PluginHooks {
  /**
   * Called when plugin is loaded
   */
  onLoad?: (context: PluginContext) => Promise<void> | void;

  /**
   * Called when plugin is unloaded
   */
  onUnload?: (context: PluginContext) => Promise<void> | void;

  /**
   * Called before a request is sent
   */
  onBeforeRequest?: (request: Request, context: PluginContext) => Promise<Request> | Request;

  /**
   * Called after a response is received
   */
  onAfterResponse?: (response: Response, request: Request, context: PluginContext) => Promise<Response> | Response;

  /**
   * Called when a collection is created
   */
  onCollectionCreate?: (collection: any, context: PluginContext) => Promise<void> | void;

  /**
   * Called when a collection is updated
   */
  onCollectionUpdate?: (collection: any, context: PluginContext) => Promise<void> | void;

  /**
   * Called when a collection is deleted
   */
  onCollectionDelete?: (collectionId: string, context: PluginContext) => Promise<void> | void;

  /**
   * Called when settings change
   */
  onSettingsChange?: (key: string, value: any, context: PluginContext) => Promise<void> | void;

  /**
   * Custom menu items
   */
  menuItems?: PluginMenuItem[];

  /**
   * Custom UI components
   */
  components?: PluginComponent[];
}

/**
 * Plugin menu item
 */
export interface PluginMenuItem {
  id: string;
  label: string;
  icon?: string;
  location: 'toolbar' | 'context' | 'menu';
  onClick: (context: PluginContext) => Promise<void> | void;
}

/**
 * Plugin UI component
 */
export interface PluginComponent {
  id: string;
  name: string;
  location: 'sidebar' | 'panel' | 'tab';
  render: (container: HTMLElement, context: PluginContext) => void;
}

/**
 * Main plugin interface
 */
export interface Plugin extends PluginHooks {
  manifest: PluginManifest;
}

/**
 * Plugin info for UI
 */
export interface PluginInfo {
  id: string;
  name: string;
  version: string;
  description: string;
  author?: string;
  enabled: boolean;
  loaded: boolean;
  error?: string;
  permissions: PluginPermission[];
}

/**
 * Plugin load result
 */
export interface PluginLoadResult {
  success: boolean;
  plugin?: PluginInfo;
  error?: string;
}

/**
 * Plugin registry entry
 */
export interface PluginRegistryEntry {
  manifest: PluginManifest;
  plugin: Plugin;
  context: PluginContext;
  enabled: boolean;
  loaded: boolean;
  error?: string;
}
