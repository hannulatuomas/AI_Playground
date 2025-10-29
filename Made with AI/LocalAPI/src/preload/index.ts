// Electron preload script
import { contextBridge, ipcRenderer } from 'electron';

// Unified electronAPI exposure (v0.8.0+)

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('api', {
  database: {
    // Collections
    getAllCollections: () => ipcRenderer.invoke('collections:getAll'),
    getCollection: (id: string) => ipcRenderer.invoke('collections:getById', id),
    createCollection: (collection: any) => ipcRenderer.invoke('collections:create', collection),
    updateCollection: (id: string, updates: any) => ipcRenderer.invoke('collections:update', id, updates),
    deleteCollection: (id: string) => ipcRenderer.invoke('collections:delete', id),
    
    // Requests
    getRequest: (id: string) => ipcRenderer.invoke('requests:getById', id),
    getRequestsByCollection: (collectionId: string) => ipcRenderer.invoke('requests:getByCollection', collectionId),
    createRequest: (request: any) => ipcRenderer.invoke('requests:create', request),
    updateRequest: (id: string, updates: any) => ipcRenderer.invoke('requests:update', id, updates),
    deleteRequest: (id: string) => ipcRenderer.invoke('requests:delete', id),
    
    // Environments
    getAllEnvironments: () => ipcRenderer.invoke('environments:getAll'),
    getEnvironment: (id: string) => ipcRenderer.invoke('environments:getActive'),
    createEnvironment: (environment: any) => ipcRenderer.invoke('environments:create', environment),
    updateEnvironment: (id: string, updates: any) => ipcRenderer.invoke('environments:update', id, updates),
    deleteEnvironment: (id: string) => ipcRenderer.invoke('environments:delete', id),
    
    // Variables
    getVariablesByScope: (scope: string, scopeId?: string) => ipcRenderer.invoke('variables:get', scope, scopeId),
    createVariable: (variable: any) => ipcRenderer.invoke('variables:set', variable.scope, variable.key, variable.value, variable.scopeId),
    updateVariable: (scope: string, key: string, value: any, scopeId?: string) => ipcRenderer.invoke('variables:set', scope, key, value, scopeId),
    deleteVariable: (scope: string, key: string, scopeId?: string) => ipcRenderer.invoke('variables:delete', scope, key, scopeId),
    
    // Settings
    getAllSettings: () => ipcRenderer.invoke('settings:get'),
    setSetting: (key: string, value: any) => ipcRenderer.invoke('settings:set', key, value),
  },
  
  request: {
    send: (request: any, variables?: any) => ipcRenderer.invoke('request:send', request, variables),
  },
  
  secrets: {
    isAvailable: () => ipcRenderer.invoke('secrets:isAvailable'),
    set: (scope: string, key: string, value: string, description?: string) => ipcRenderer.invoke('secrets:set', scope, key, value, description),
    get: (scope: string, key: string) => ipcRenderer.invoke('secrets:get', scope, key),
    delete: (scope: string, key: string) => ipcRenderer.invoke('secrets:delete', scope, key),
    getByScope: (scope: string) => ipcRenderer.invoke('secrets:getByScope', scope),
    deleteByScope: (scope: string) => ipcRenderer.invoke('secrets:deleteByScope', scope),
    has: (scope: string, key: string) => ipcRenderer.invoke('secrets:has', scope, key),
  },

  // Cache operations (v0.6.0)
  cache: {
    getStats: () => ipcRenderer.invoke('cache:getStats'),
    clear: () => ipcRenderer.invoke('cache:clear'),
    cleanExpired: () => ipcRenderer.invoke('cache:cleanExpired'),
    invalidateByTags: (tags: string[]) => ipcRenderer.invoke('cache:invalidateByTags', tags),
    invalidateByPattern: (pattern: string) => ipcRenderer.invoke('cache:invalidateByPattern', pattern),
    configure: (config: any) => ipcRenderer.invoke('cache:configure', config),
  },

  // Import/Export operations (v0.6.0)
  importExport: {
    getSupportedFormats: () => ipcRenderer.invoke('importExport:getSupportedFormats'),
    detectFormat: (content: string) => ipcRenderer.invoke('importExport:detectFormat', content),
    import: (content: string, format?: string, options?: any) => 
      ipcRenderer.invoke('importExport:import', content, format, options),
    exportCollections: (collectionIds: string[], format: string, options?: any) => 
      ipcRenderer.invoke('importExport:exportCollections', collectionIds, format, options),
    exportRequest: (requestId: string, format: string, options?: any) => 
      ipcRenderer.invoke('importExport:exportRequest', requestId, format, options),
    exportRequests: (requestIds: string[], format: string, options?: any) => 
      ipcRenderer.invoke('importExport:exportRequests', requestIds, format, options),
    getHandlerInfo: (format: string) => ipcRenderer.invoke('importExport:getHandlerInfo', format),
    getExample: (format: string) => ipcRenderer.invoke('importExport:getExample', format),
  },

  // Enhanced Import operations (v0.8.0)
  import: {
    detectFormat: (content: string) => ipcRenderer.invoke('import:detectFormat', content),
    validate: (content: string, format?: string) => ipcRenderer.invoke('import:validate', content, format),
    import: (content: string, options?: any) => ipcRenderer.invoke('import:import', content, options),
    importFromFile: (filePath: string, options?: any) => ipcRenderer.invoke('import:importFromFile', filePath, options),
    importFromURL: (url: string, options?: any) => ipcRenderer.invoke('import:importFromURL', url, options),
    getSupportedFormats: () => ipcRenderer.invoke('import:getSupportedFormats'),
    getHandlers: () => ipcRenderer.invoke('import:getHandlers'),
    getHistory: () => ipcRenderer.invoke('import:getHistory'),
    clearHistory: () => ipcRenderer.invoke('import:clearHistory'),
  },

  // Git operations (v0.6.0)
  git: {
    isRepository: () => ipcRenderer.invoke('git:isRepository'),
    init: () => ipcRenderer.invoke('git:init'),
    getStatus: () => ipcRenderer.invoke('git:getStatus'),
    add: (files: string[] | string) => ipcRenderer.invoke('git:add', files),
    reset: (files?: string[]) => ipcRenderer.invoke('git:reset', files),
    commit: (options: any) => ipcRenderer.invoke('git:commit', options),
    getLog: (maxCount?: number) => ipcRenderer.invoke('git:getLog', maxCount),
    getDiff: (file?: string) => ipcRenderer.invoke('git:getDiff', file),
    getDiffStaged: (file?: string) => ipcRenderer.invoke('git:getDiffStaged', file),
    getBranches: () => ipcRenderer.invoke('git:getBranches'),
    createBranch: (branchName: string, checkout: boolean) => 
      ipcRenderer.invoke('git:createBranch', branchName, checkout),
    checkout: (branchName: string) => ipcRenderer.invoke('git:checkout', branchName),
    hasChanges: () => ipcRenderer.invoke('git:hasChanges'),
    discardChanges: (files?: string[]) => ipcRenderer.invoke('git:discardChanges', files),
    getConfig: (key: string) => ipcRenderer.invoke('git:getConfig', key),
    setConfig: (key: string, value: string) => ipcRenderer.invoke('git:setConfig', key, value),
  },

  // Plugin operations (v0.6.0)
  plugins: {
    discover: () => ipcRenderer.invoke('plugins:discover'),
    load: (pluginDir: string) => ipcRenderer.invoke('plugins:load', pluginDir),
    unload: (pluginId: string) => ipcRenderer.invoke('plugins:unload', pluginId),
    reload: (pluginId: string) => ipcRenderer.invoke('plugins:reload', pluginId),
    setEnabled: (pluginId: string, enabled: boolean) => 
      ipcRenderer.invoke('plugins:setEnabled', pluginId, enabled),
    getAll: () => ipcRenderer.invoke('plugins:getAll'),
    getInfo: (pluginId: string) => ipcRenderer.invoke('plugins:getInfo', pluginId),
    openPluginsFolder: () => ipcRenderer.invoke('plugins:openPluginsFolder'),
  },

  // Report operations (v0.6.0)
  reports: {
    generate: (data: any, options: any) => ipcRenderer.invoke('reports:generate', data, options),
  },

  // Mock Server operations (v0.5.0)
  mockServer: {
    create: (options: any) => ipcRenderer.invoke('mockServer:create', options),
    start: (serverId: string) => ipcRenderer.invoke('mockServer:start', serverId),
    stop: (serverId: string) => ipcRenderer.invoke('mockServer:stop', serverId),
    delete: (serverId: string) => ipcRenderer.invoke('mockServer:delete', serverId),
    getAll: () => ipcRenderer.invoke('mockServer:getAll'),
    getInfo: (serverId: string) => ipcRenderer.invoke('mockServer:getInfo', serverId),
    getLogs: (serverId: string) => ipcRenderer.invoke('mockServer:getLogs', serverId),
    getStats: (serverId: string) => ipcRenderer.invoke('mockServer:getStats', serverId),
  },

  // Batch Runner operations (v0.5.0)
  batch: {
    run: (requests: any[], variables?: any) => ipcRenderer.invoke('batch:run', requests, variables),
    getResults: (batchId: string) => ipcRenderer.invoke('batch:getResults', batchId),
  },

  // Monitoring operations (v0.5.0)
  monitor: {
    create: (options: any) => ipcRenderer.invoke('monitor:create', options),
    start: (monitorId: string) => ipcRenderer.invoke('monitor:start', monitorId),
    stop: (monitorId: string) => ipcRenderer.invoke('monitor:stop', monitorId),
    delete: (monitorId: string) => ipcRenderer.invoke('monitor:delete', monitorId),
    getAll: () => ipcRenderer.invoke('monitor:getAll'),
    getLogs: (monitorId: string) => ipcRenderer.invoke('monitor:getLogs', monitorId),
    getStats: (monitorId: string) => ipcRenderer.invoke('monitor:getStats', monitorId),
  },

  // Security operations (v0.5.0)
  security: {
    scan: (request: any, response: any) => ipcRenderer.invoke('security:scan', request, response),
    scanCollection: (collectionId: string) => ipcRenderer.invoke('security:scanCollection', collectionId),
  },

  // Vulnerability Scanner operations (v0.5.0)
  vulnerability: {
    scan: (request: any, options?: any) => ipcRenderer.invoke('vulnerability:scan', request, options),
    scanEndpoint: (url: string, method: string, options?: any) => 
      ipcRenderer.invoke('vulnerability:scanEndpoint', url, method, options),
  },
});

// Expose electronAPI with all operations
contextBridge.exposeInMainWorld('electronAPI', {
  // Enhanced Import operations (v0.8.0)
  import: {
    detectFormat: (content: string) => ipcRenderer.invoke('import:detectFormat', content),
    validate: (content: string, format?: string) => ipcRenderer.invoke('import:validate', content, format),
    import: (content: string, options?: any) => ipcRenderer.invoke('import:import', content, options),
    importFromFile: (filePath: string, options?: any) => ipcRenderer.invoke('import:importFromFile', filePath, options),
    importFromURL: (url: string, options?: any) => ipcRenderer.invoke('import:importFromURL', url, options),
    getSupportedFormats: () => ipcRenderer.invoke('import:getSupportedFormats'),
    getHandlers: () => ipcRenderer.invoke('import:getHandlers'),
    getHistory: () => ipcRenderer.invoke('import:getHistory'),
    clearHistory: () => ipcRenderer.invoke('import:clearHistory'),
  },
  // Enhanced Export operations (v0.8.0)
  export: {
    exportCollections: (collectionIds: string[], format: string, options?: any) => 
      ipcRenderer.invoke('export:exportCollections', collectionIds, format, options),
    exportRequest: (requestId: string, format: string, options?: any) => 
      ipcRenderer.invoke('export:exportRequest', requestId, format, options),
    exportRequests: (requestIds: string[], format: string, options?: any) => 
      ipcRenderer.invoke('export:exportRequests', requestIds, format, options),
    saveToFile: (content: string, filePath: string, format: string) => 
      ipcRenderer.invoke('export:saveToFile', content, filePath, format),
    copyToClipboard: (content: string) => 
      ipcRenderer.invoke('export:copyToClipboard', content),
    getSupportedFormats: () => ipcRenderer.invoke('export:getSupportedFormats'),
    getGenerators: () => ipcRenderer.invoke('export:getGenerators'),
    getHistory: () => ipcRenderer.invoke('export:getHistory'),
    clearHistory: () => ipcRenderer.invoke('export:clearHistory'),
  },
  
  collections: {
    getAll: () => ipcRenderer.invoke('collections:getAll'),
    getById: (id: string) => ipcRenderer.invoke('collections:getById', id),
    create: (collection: any) => ipcRenderer.invoke('collections:create', collection),
    update: (id: string, updates: any) => ipcRenderer.invoke('collections:update', id, updates),
    delete: (id: string) => ipcRenderer.invoke('collections:delete', id),
  },
  
  // Request operations
  requests: {
    getAll: () => ipcRenderer.invoke('requests:getAll'),
    getByCollection: (collectionId: string) => ipcRenderer.invoke('requests:getByCollection', collectionId),
    getById: (id: string) => ipcRenderer.invoke('requests:getById', id),
    create: (request: any) => ipcRenderer.invoke('requests:create', request),
    update: (id: string, updates: any) => ipcRenderer.invoke('requests:update', id, updates),
    delete: (id: string) => ipcRenderer.invoke('requests:delete', id),
    send: (request: any, variables?: any) => ipcRenderer.invoke('request:send', request, variables),
  },
  
  // Environment operations
  environments: {
    getAll: () => ipcRenderer.invoke('environments:getAll'),
    getActive: () => ipcRenderer.invoke('environments:getActive'),
    create: (environment: any) => ipcRenderer.invoke('environments:create', environment),
    update: (id: string, updates: any) => ipcRenderer.invoke('environments:update', id, updates),
    delete: (id: string) => ipcRenderer.invoke('environments:delete', id),
  },
  
  // Variable operations
  variables: {
    get: (scope: string, scopeId?: string) => ipcRenderer.invoke('variables:get', scope, scopeId),
    set: (scope: string, key: string, value: any, scopeId?: string) => 
      ipcRenderer.invoke('variables:set', scope, key, value, scopeId),
    delete: (scope: string, key: string, scopeId?: string) => 
      ipcRenderer.invoke('variables:delete', scope, key, scopeId),
  },

  // Variable Extraction operations (v0.8.0)
  extractor: {
    extractFromJSON: (body: any, path: string, variableName: string, scope: string) =>
      ipcRenderer.invoke('extractor:extractFromJSON', body, path, variableName, scope),
    extractFromXML: (body: string, xpath: string, variableName: string, scope: string) =>
      ipcRenderer.invoke('extractor:extractFromXML', body, xpath, variableName, scope),
    extractFromHeader: (headers: Record<string, string>, headerName: string, variableName: string, scope: string) =>
      ipcRenderer.invoke('extractor:extractFromHeader', headers, headerName, variableName, scope),
    extractWithRegex: (content: string, pattern: string, variableName: string, scope: string, source: 'body' | 'header') =>
      ipcRenderer.invoke('extractor:extractWithRegex', content, pattern, variableName, scope, source),
    extractWithRules: (response: any, rules: any[]) =>
      ipcRenderer.invoke('extractor:extractWithRules', response, rules),
    addRule: (rule: any) => ipcRenderer.invoke('extractor:addRule', rule),
    updateRule: (id: string, updates: any) => ipcRenderer.invoke('extractor:updateRule', id, updates),
    deleteRule: (id: string) => ipcRenderer.invoke('extractor:deleteRule', id),
    getRules: () => ipcRenderer.invoke('extractor:getRules'),
    getRule: (id: string) => ipcRenderer.invoke('extractor:getRule', id),
    recordHistory: (variableName: string, oldValue: any, newValue: any, scope: string, source: string, requestId?: string) =>
      ipcRenderer.invoke('extractor:recordHistory', variableName, oldValue, newValue, scope, source, requestId),
    getHistory: (variableName?: string, limit?: number) =>
      ipcRenderer.invoke('extractor:getHistory', variableName, limit),
    clearHistory: (variableName?: string) =>
      ipcRenderer.invoke('extractor:clearHistory', variableName),
    suggestMethod: (response: any) =>
      ipcRenderer.invoke('extractor:suggestMethod', response),
    exportRules: () => ipcRenderer.invoke('extractor:exportRules'),
    importRules: (json: string) => ipcRenderer.invoke('extractor:importRules', json),
  },

  // Workspace operations (v0.8.0)
  workspace: {
    create: (name: string, description?: string) => ipcRenderer.invoke('workspace:create', name, description),
    save: (workspace?: any) => ipcRenderer.invoke('workspace:save', workspace),
    load: (workspaceId: string) => ipcRenderer.invoke('workspace:load', workspaceId),
    getCurrent: () => ipcRenderer.invoke('workspace:getCurrent'),
    update: (updates: any) => ipcRenderer.invoke('workspace:update', updates),
    delete: (workspaceId: string) => ipcRenderer.invoke('workspace:delete', workspaceId),
    list: () => ipcRenderer.invoke('workspace:list'),
    getRecent: () => ipcRenderer.invoke('workspace:getRecent'),
    export: (workspaceId: string, exportPath: string) => ipcRenderer.invoke('workspace:export', workspaceId, exportPath),
    import: (importPath: string) => ipcRenderer.invoke('workspace:import', importPath),
    createSnapshot: (name: string, description?: string) => ipcRenderer.invoke('workspace:createSnapshot', name, description),
    restoreSnapshot: (snapshotId: string) => ipcRenderer.invoke('workspace:restoreSnapshot', snapshotId),
    listSnapshots: (workspaceId: string) => ipcRenderer.invoke('workspace:listSnapshots', workspaceId),
    deleteSnapshot: (snapshotId: string) => ipcRenderer.invoke('workspace:deleteSnapshot', snapshotId),
    saveAsTemplate: (name: string, description?: string, tags?: string[]) => 
      ipcRenderer.invoke('workspace:saveAsTemplate', name, description, tags),
    loadFromTemplate: (templateId: string, workspaceName: string) => 
      ipcRenderer.invoke('workspace:loadFromTemplate', templateId, workspaceName),
    listTemplates: () => ipcRenderer.invoke('workspace:listTemplates'),
    deleteTemplate: (templateId: string) => ipcRenderer.invoke('workspace:deleteTemplate', templateId),
    startAutoSave: (intervalSeconds?: number) => ipcRenderer.invoke('workspace:startAutoSave', intervalSeconds),
    stopAutoSave: () => ipcRenderer.invoke('workspace:stopAutoSave'),
    markDirty: () => ipcRenderer.invoke('workspace:markDirty'),
    isDirty: () => ipcRenderer.invoke('workspace:isDirty'),
    backup: (workspaceId: string, backupPath: string) => ipcRenderer.invoke('workspace:backup', workspaceId, backupPath),
    restoreFromBackup: (backupPath: string) => ipcRenderer.invoke('workspace:restoreFromBackup', backupPath),
  },
  
  // Settings operations (comprehensive)
  settings: {
    getAll: () => ipcRenderer.invoke('settings:getAll'),
    save: (settings: any) => ipcRenderer.invoke('settings:save', settings),
    getNetwork: () => ipcRenderer.invoke('settings:getNetwork'),
    getEditor: () => ipcRenderer.invoke('settings:getEditor'),
    export: () => ipcRenderer.invoke('settings:export'),
    import: () => ipcRenderer.invoke('settings:import'),
    createBackup: () => ipcRenderer.invoke('settings:createBackup'),
    listBackups: () => ipcRenderer.invoke('settings:listBackups'),
    restoreBackup: (backupFile: string) => ipcRenderer.invoke('settings:restoreBackup', backupFile),
    resetToDefaults: () => ipcRenderer.invoke('settings:resetToDefaults'),
    validate: (settings: any) => ipcRenderer.invoke('settings:validate', settings),
    // Legacy methods (kept for compatibility)
    get: (key?: string) => ipcRenderer.invoke('settings:get', key),
    set: (key: string, value: any) => ipcRenderer.invoke('settings:set', key, value),
    update: (settings: any) => ipcRenderer.invoke('settings:update', settings),
  },

  // Secrets operations
  secrets: {
    isAvailable: () => ipcRenderer.invoke('secrets:isAvailable'),
    set: (scope: string, key: string, value: string, description?: string) => 
      ipcRenderer.invoke('secrets:set', scope, key, value, description),
    get: (scope: string, key: string) => ipcRenderer.invoke('secrets:get', scope, key),
    delete: (scope: string, key: string) => ipcRenderer.invoke('secrets:delete', scope, key),
    getByScope: (scope: string) => ipcRenderer.invoke('secrets:getByScope', scope),
    deleteByScope: (scope: string) => ipcRenderer.invoke('secrets:deleteByScope', scope),
    has: (scope: string, key: string) => ipcRenderer.invoke('secrets:has', scope, key),
  },

  // Cache operations
  cache: {
    getStats: () => ipcRenderer.invoke('cache:getStats'),
    clear: () => ipcRenderer.invoke('cache:clear'),
    cleanExpired: () => ipcRenderer.invoke('cache:cleanExpired'),
    invalidateByTags: (tags: string[]) => ipcRenderer.invoke('cache:invalidateByTags', tags),
    invalidateByPattern: (pattern: string) => ipcRenderer.invoke('cache:invalidateByPattern', pattern),
    configure: (config: any) => ipcRenderer.invoke('cache:configure', config),
  },

  // Import/Export operations
  importExport: {
    getSupportedFormats: () => ipcRenderer.invoke('importExport:getSupportedFormats'),
    detectFormat: (content: string) => ipcRenderer.invoke('importExport:detectFormat', content),
    import: (content: string, format?: string, options?: any) => 
      ipcRenderer.invoke('importExport:import', content, format, options),
    exportCollections: (collectionIds: string[], format: string, options?: any) => 
      ipcRenderer.invoke('importExport:exportCollections', collectionIds, format, options),
    exportRequest: (requestId: string, format: string, options?: any) => 
      ipcRenderer.invoke('importExport:exportRequest', requestId, format, options),
    exportRequests: (requestIds: string[], format: string, options?: any) => 
      ipcRenderer.invoke('importExport:exportRequests', requestIds, format, options),
    getHandlerInfo: (format: string) => ipcRenderer.invoke('importExport:getHandlerInfo', format),
    getExample: (format: string) => ipcRenderer.invoke('importExport:getExample', format),
  },

  // Git operations
  git: {
    isRepository: () => ipcRenderer.invoke('git:isRepository'),
    init: () => ipcRenderer.invoke('git:init'),
    getStatus: () => ipcRenderer.invoke('git:getStatus'),
    add: (files: string[] | string) => ipcRenderer.invoke('git:add', files),
    reset: (files?: string[]) => ipcRenderer.invoke('git:reset', files),
    commit: (options: any) => ipcRenderer.invoke('git:commit', options),
    getLog: (maxCount?: number) => ipcRenderer.invoke('git:getLog', maxCount),
    getDiff: (file?: string) => ipcRenderer.invoke('git:getDiff', file),
    getDiffStaged: (file?: string) => ipcRenderer.invoke('git:getDiffStaged', file),
    getBranches: () => ipcRenderer.invoke('git:getBranches'),
    createBranch: (branchName: string, checkout: boolean) => ipcRenderer.invoke('git:createBranch', branchName, checkout),
    checkout: (branchName: string) => ipcRenderer.invoke('git:checkout', branchName),
    hasChanges: () => ipcRenderer.invoke('git:hasChanges'),
    discardChanges: (files?: string[]) => ipcRenderer.invoke('git:discardChanges', files),
    getConfig: (key: string) => ipcRenderer.invoke('git:getConfig', key),
    setConfig: (key: string, value: string) => ipcRenderer.invoke('git:setConfig', key, value),
  },

  // Plugin operations
  plugins: {
    discover: () => ipcRenderer.invoke('plugins:discover'),
    load: (pluginDir: string) => ipcRenderer.invoke('plugins:load', pluginDir),
    unload: (pluginId: string) => ipcRenderer.invoke('plugins:unload', pluginId),
    reload: (pluginId: string) => ipcRenderer.invoke('plugins:reload', pluginId),
    setEnabled: (pluginId: string, enabled: boolean) => ipcRenderer.invoke('plugins:setEnabled', pluginId, enabled),
    getAll: () => ipcRenderer.invoke('plugins:getAll'),
    getInfo: (pluginId: string) => ipcRenderer.invoke('plugins:getInfo', pluginId),
    openPluginsFolder: () => ipcRenderer.invoke('plugins:openPluginsFolder'),
  },

  // Report operations
  reports: {
    generate: (data: any, options: any) => ipcRenderer.invoke('reports:generate', data, options),
  },

  // Mock Server operations
  mockServer: {
    create: (options: any) => ipcRenderer.invoke('mockServer:create', options),
    start: (serverId: string) => ipcRenderer.invoke('mockServer:start', serverId),
    stop: (serverId: string) => ipcRenderer.invoke('mockServer:stop', serverId),
    delete: (serverId: string) => ipcRenderer.invoke('mockServer:delete', serverId),
    getAll: () => ipcRenderer.invoke('mockServer:getAll'),
    getInfo: (serverId: string) => ipcRenderer.invoke('mockServer:getInfo', serverId),
    getLogs: (serverId: string) => ipcRenderer.invoke('mockServer:getLogs', serverId),
    getStats: (serverId: string) => ipcRenderer.invoke('mockServer:getStats', serverId),
  },

  // Batch Runner operations
  batch: {
    run: (requests: any[], variables?: any) => ipcRenderer.invoke('batch:run', requests, variables),
    getResults: (batchId: string) => ipcRenderer.invoke('batch:getResults', batchId),
  },

  // Monitoring operations
  monitor: {
    create: (options: any) => ipcRenderer.invoke('monitor:create', options),
    start: (monitorId: string) => ipcRenderer.invoke('monitor:start', monitorId),
    stop: (monitorId: string) => ipcRenderer.invoke('monitor:stop', monitorId),
    delete: (monitorId: string) => ipcRenderer.invoke('monitor:delete', monitorId),
    getAll: () => ipcRenderer.invoke('monitor:getAll'),
    getLogs: (monitorId: string) => ipcRenderer.invoke('monitor:getLogs', monitorId),
    getStats: (monitorId: string) => ipcRenderer.invoke('monitor:getStats', monitorId),
  },

  // Security operations
  security: {
    scan: (request: any, response: any) => ipcRenderer.invoke('security:scan', request, response),
    scanCollection: (collectionId: string) => ipcRenderer.invoke('security:scanCollection', collectionId),
  },

  // Vulnerability Scanner operations
  vulnerability: {
    scan: (request: any, options?: any) => ipcRenderer.invoke('vulnerability:scan', request, options),
    scanEndpoint: (url: string, method: string, options?: any) => ipcRenderer.invoke('vulnerability:scanEndpoint', url, method, options),
  },

  // OWASP Scanner operations (v0.7.0)
  owasp: {
    scan: (options: any) => ipcRenderer.invoke('owasp:scan', options),
  },

  // Fuzzing operations (v0.7.0)
  fuzzing: {
    run: (options: any) => ipcRenderer.invoke('fuzzing:run', options),
  },

  // ZAP Proxy operations (v0.7.0)
  zap: {
    checkConnection: (config: any) => ipcRenderer.invoke('zap:checkConnection', config),
    getVersion: () => ipcRenderer.invoke('zap:getVersion'),
    runScan: (options: any) => ipcRenderer.invoke('zap:runScan', options),
    getAlerts: (url?: string) => ipcRenderer.invoke('zap:getAlerts', url),
    clearAlerts: () => ipcRenderer.invoke('zap:clearAlerts'),
    generateHtmlReport: () => ipcRenderer.invoke('zap:generateHtmlReport'),
    generateXmlReport: () => ipcRenderer.invoke('zap:generateXmlReport'),
    disconnect: () => ipcRenderer.invoke('zap:disconnect'),
  },

  // Console operations (v0.9.0)
  console: {
    getEntries: (filters?: any, limit?: number, offset?: number) => ipcRenderer.invoke('console:getEntries', filters, limit, offset),
    getEntry: (id: string) => ipcRenderer.invoke('console:getEntry', id),
    searchEntries: (query: string) => ipcRenderer.invoke('console:searchEntries', query),
    clearEntries: (olderThan?: number) => ipcRenderer.invoke('console:clearEntries', olderThan),
    deleteEntry: (id: string) => ipcRenderer.invoke('console:deleteEntry', id),
    exportEntries: (options: any) => ipcRenderer.invoke('console:exportEntries', options),
    setPersistence: (enabled: boolean) => ipcRenderer.invoke('console:setPersistence', enabled),
    setMaxEntries: (max: number) => ipcRenderer.invoke('console:setMaxEntries', max),
    setPaused: (paused: boolean) => ipcRenderer.invoke('console:setPaused', paused),
    isPaused: () => ipcRenderer.invoke('console:isPaused'),
    getStats: () => ipcRenderer.invoke('console:getStats'),
    logRequest: (request: any, metadata?: any) => ipcRenderer.invoke('console:logRequest', request, metadata),
    logResponse: (response: any, request: any, metadata?: any) => ipcRenderer.invoke('console:logResponse', response, request, metadata),
  },

  // API Specification Generation (v0.9.0)
  apispec: {
    analyze: (entries: any[]) => ipcRenderer.invoke('apispec:analyze', entries),
    generateOpenAPI: (analysis: any, options: any) => ipcRenderer.invoke('apispec:generateOpenAPI', analysis, options),
    generateAsyncAPI: (entries: any[], options: any) => ipcRenderer.invoke('apispec:generateAsyncAPI', entries, options),
    generateGraphQL: (entries: any[]) => ipcRenderer.invoke('apispec:generateGraphQL', entries),
    exportOpenAPIJSON: (spec: any) => ipcRenderer.invoke('apispec:exportOpenAPIJSON', spec),
    exportOpenAPIYAML: (spec: any) => ipcRenderer.invoke('apispec:exportOpenAPIYAML', spec),
    validateOpenAPI: (spec: any) => ipcRenderer.invoke('apispec:validateOpenAPI', spec),
    loadOpenAPIFile: (filePath: string) => ipcRenderer.invoke('apispec:loadOpenAPIFile', filePath),
  },
  publishing: {
    generateDocumentation: (spec: any, options: any) => ipcRenderer.invoke('publishing:generateDocumentation', spec, options),
    exportMarkdown: (spec: any, options: any) => ipcRenderer.invoke('publishing:exportMarkdown', spec, options),
    generateSDK: (spec: any, options: any) => ipcRenderer.invoke('publishing:generateSDK', spec, options),
    generateChangelog: (oldSpec: any, newSpec: any) => ipcRenderer.invoke('publishing:generateChangelog', oldSpec, newSpec),
    publish: (doc: any, options: any) => ipcRenderer.invoke('publishing:publish', doc, options),
    stopServer: () => ipcRenderer.invoke('publishing:stopServer'),
    getStatus: () => ipcRenderer.invoke('publishing:getStatus'),
    openDirectory: (directory: string) => ipcRenderer.invoke('publishing:openDirectory', directory),
  },
  
  // Tab Manager operations
  tabs: {
    create: (tab: any) => ipcRenderer.invoke('tabs:create', tab),
    getAll: () => ipcRenderer.invoke('tabs:getAll'),
    update: (id: string, updates: any) => ipcRenderer.invoke('tabs:update', id, updates),
    close: (id: string) => ipcRenderer.invoke('tabs:close', id),
    closeOthers: (keepId: string) => ipcRenderer.invoke('tabs:closeOthers', keepId),
    closeAll: () => ipcRenderer.invoke('tabs:closeAll'),
    setActive: (id: string) => ipcRenderer.invoke('tabs:setActive', id),
    getActive: () => ipcRenderer.invoke('tabs:getActive'),
    goBack: () => ipcRenderer.invoke('tabs:goBack'),
    goForward: () => ipcRenderer.invoke('tabs:goForward'),
    search: (query: string) => ipcRenderer.invoke('tabs:search', query),
    reorder: (tabId: string, newIndex: number) => ipcRenderer.invoke('tabs:reorder', tabId, newIndex),
    createGroup: (name: string, color?: string) => ipcRenderer.invoke('tabs:createGroup', name, color),
    getAllGroups: () => ipcRenderer.invoke('tabs:getAllGroups'),
    addToGroup: (tabId: string, groupId: string) => ipcRenderer.invoke('tabs:addToGroup', tabId, groupId),
  },
  
  // Command Palette operations
  commands: {
    search: (query: string) => ipcRenderer.invoke('commands:search', query),
    execute: (id: string) => ipcRenderer.invoke('commands:execute', id),
    getAll: () => ipcRenderer.invoke('commands:getAll'),
    getRecent: () => ipcRenderer.invoke('commands:getRecent'),
  },
  
  // Favorites operations
  favorites: {
    add: (favorite: any) => ipcRenderer.invoke('favorites:add', favorite),
    remove: (id: string) => ipcRenderer.invoke('favorites:remove', id),
    getAll: () => ipcRenderer.invoke('favorites:getAll'),
    toggle: (favorite: any) => ipcRenderer.invoke('favorites:toggle', favorite),
    isFavorite: (entityId: string) => ipcRenderer.invoke('favorites:isFavorite', entityId),
    search: (query: string) => ipcRenderer.invoke('favorites:search', query),
    createFolder: (name: string, color?: string) => ipcRenderer.invoke('favorites:createFolder', name, color),
    getAllFolders: () => ipcRenderer.invoke('favorites:getAllFolders'),
  },
  
  // Layout operations
  layout: {
    getAll: () => ipcRenderer.invoke('layout:getAll'),
    getActive: () => ipcRenderer.invoke('layout:getActive'),
    setActive: (layoutId: string) => ipcRenderer.invoke('layout:setActive', layoutId),
    create: (name: string, panels: any[], description?: string) => ipcRenderer.invoke('layout:create', name, panels, description),
    update: (layoutId: string, updates: any) => ipcRenderer.invoke('layout:update', layoutId, updates),
    delete: (layoutId: string) => ipcRenderer.invoke('layout:delete', layoutId),
  },
});

// Type definitions for TypeScript
export interface ElectronAPI {
  collections: {
    getAll: () => Promise<any[]>;
    getById: (id: string) => Promise<any>;
    create: (collection: any) => Promise<any>;
    update: (id: string, updates: any) => Promise<any>;
    delete: (id: string) => Promise<void>;
  };
  requests: {
    getAll: () => Promise<any[]>;
    getByCollection: (collectionId: string) => Promise<any[]>;
    getById: (id: string) => Promise<any>;
    create: (request: any) => Promise<any>;
    update: (id: string, updates: any) => Promise<any>;
    delete: (id: string) => Promise<void>;
    send: (request: any, variables?: any) => Promise<any>;
  };
  environments: {
    getAll: () => Promise<any[]>;
    getActive: () => Promise<any>;
    create: (environment: any) => Promise<any>;
    update: (id: string, updates: any) => Promise<any>;
    delete: (id: string) => Promise<void>;
  };
  variables: {
    get: (scope: string, scopeId?: string) => Promise<Record<string, any>>;
    set: (scope: string, key: string, value: any, scopeId?: string) => Promise<any>;
    delete: (scope: string, key: string, scopeId?: string) => Promise<void>;
  };
  extractor: {
    extractFromJSON: (body: any, path: string, variableName: string, scope: string) => Promise<any>;
    extractFromXML: (body: string, xpath: string, variableName: string, scope: string) => Promise<any>;
    extractFromHeader: (headers: Record<string, string>, headerName: string, variableName: string, scope: string) => Promise<any>;
    extractWithRegex: (content: string, pattern: string, variableName: string, scope: string, source: 'body' | 'header') => Promise<any>;
    extractWithRules: (response: any, rules: any[]) => Promise<any[]>;
    addRule: (rule: any) => Promise<any>;
    updateRule: (id: string, updates: any) => Promise<any>;
    deleteRule: (id: string) => Promise<boolean>;
    getRules: () => Promise<any[]>;
    getRule: (id: string) => Promise<any>;
    recordHistory: (variableName: string, oldValue: any, newValue: any, scope: string, source: string, requestId?: string) => Promise<void>;
    getHistory: (variableName?: string, limit?: number) => Promise<any[]>;
    clearHistory: (variableName?: string) => Promise<void>;
    suggestMethod: (response: any) => Promise<string>;
    exportRules: () => Promise<string>;
    importRules: (json: string) => Promise<number>;
  };
  workspace: {
    create: (name: string, description?: string) => Promise<any>;
    save: (workspace?: any) => Promise<string>;
    load: (workspaceId: string) => Promise<any>;
    getCurrent: () => Promise<any>;
    update: (updates: any) => Promise<any>;
    delete: (workspaceId: string) => Promise<void>;
    list: () => Promise<any[]>;
    getRecent: () => Promise<any[]>;
    export: (workspaceId: string, exportPath: string) => Promise<void>;
    import: (importPath: string) => Promise<any>;
    createSnapshot: (name: string, description?: string) => Promise<any>;
    restoreSnapshot: (snapshotId: string) => Promise<any>;
    listSnapshots: (workspaceId: string) => Promise<any[]>;
    deleteSnapshot: (snapshotId: string) => Promise<void>;
    saveAsTemplate: (name: string, description?: string, tags?: string[]) => Promise<any>;
    loadFromTemplate: (templateId: string, workspaceName: string) => Promise<any>;
    listTemplates: () => Promise<any[]>;
    deleteTemplate: (templateId: string) => Promise<void>;
    startAutoSave: (intervalSeconds?: number) => Promise<void>;
    stopAutoSave: () => Promise<void>;
    markDirty: () => Promise<void>;
    isDirty: () => Promise<boolean>;
    backup: (workspaceId: string, backupPath: string) => Promise<void>;
    restoreFromBackup: (backupPath: string) => Promise<any>;
  };
  settings: {
    getAll: () => Promise<any>;
    save: (settings: any) => Promise<any>;
    getNetwork: () => Promise<any>;
    getEditor: () => Promise<any>;
    export: () => Promise<any>;
    import: () => Promise<any>;
    createBackup: () => Promise<any>;
    listBackups: () => Promise<any[]>;
    restoreBackup: (backupFile: string) => Promise<any>;
    resetToDefaults: () => Promise<any>;
    validate: (settings: any) => Promise<{ valid: boolean; errors: string[] }>;
    // Legacy methods
    get: (key?: string) => Promise<any>;
    set: (key: string, value: any) => Promise<void>;
    update: (settings: any) => Promise<void>;
  };
  secrets: {
    isAvailable: () => Promise<boolean>;
    set: (scope: string, key: string, value: string, description?: string) => Promise<void>;
    get: (scope: string, key: string) => Promise<string | null>;
    delete: (scope: string, key: string) => Promise<void>;
    getByScope: (scope: string) => Promise<Record<string, string>>;
    deleteByScope: (scope: string) => Promise<number>;
    has: (scope: string, key: string) => Promise<boolean>;
  };
  cache: {
    getStats: () => Promise<{
      hits: number;
      misses: number;
      size: number;
      entries: number;
      hitRate: number;
    }>;
    clear: () => Promise<boolean>;
    cleanExpired: () => Promise<number>;
    invalidateByTags: (tags: string[]) => Promise<number>;
    invalidateByPattern: (pattern: string) => Promise<number>;
    configure: (config: { enabled?: boolean; defaultTTL?: number; maxSize?: number }) => Promise<boolean>;
  };
  importExport: {
    getSupportedFormats: () => Promise<{ import: string[]; export: string[] }>;
    detectFormat: (content: string) => Promise<string | null>;
    import: (content: string, format?: string, options?: any) => Promise<any>;
    exportCollections: (collectionIds: string[], format: string, options?: any) => Promise<any>;
    exportRequest: (requestId: string, format: string, options?: any) => Promise<any>;
    exportRequests: (requestIds: string[], format: string, options?: any) => Promise<any>;
    getHandlerInfo: (format: string) => Promise<any>;
    getExample: (format: string) => Promise<string | null>;
  };
  git: {
    isRepository: () => Promise<boolean>;
    init: () => Promise<boolean>;
    getStatus: () => Promise<any>;
    add: (files: string[] | string) => Promise<boolean>;
    reset: (files?: string[]) => Promise<boolean>;
    commit: (options: any) => Promise<string>;
    getLog: (maxCount?: number) => Promise<any[]>;
    getDiff: (file?: string) => Promise<string>;
    getDiffStaged: (file?: string) => Promise<string>;
    getBranches: () => Promise<{ current: string; all: string[] }>;
    createBranch: (branchName: string, checkout: boolean) => Promise<boolean>;
    checkout: (branchName: string) => Promise<boolean>;
    hasChanges: () => Promise<boolean>;
    discardChanges: (files?: string[]) => Promise<boolean>;
    getConfig: (key: string) => Promise<string | null>;
    setConfig: (key: string, value: string) => Promise<boolean>;
  };
  plugins: {
    discover: () => Promise<string[]>;
    load: (pluginDir: string) => Promise<any>;
    unload: (pluginId: string) => Promise<boolean>;
    reload: (pluginId: string) => Promise<any>;
    setEnabled: (pluginId: string, enabled: boolean) => Promise<boolean>;
    getAll: () => Promise<any[]>;
    getInfo: (pluginId: string) => Promise<any>;
    openPluginsFolder: () => Promise<any>;
  };
  reports: {
    generate: (data: any, options: any) => Promise<any>;
  };
  console: {
    getEntries: (filters?: any, limit?: number, offset?: number) => Promise<any[]>;
    getEntry: (id: string) => Promise<any>;
    searchEntries: (query: string) => Promise<any[]>;
    clearEntries: (olderThan?: number) => Promise<void>;
    deleteEntry: (id: string) => Promise<boolean>;
    exportEntries: (options: any) => Promise<string>;
    setPersistence: (enabled: boolean) => Promise<void>;
    setMaxEntries: (max: number) => Promise<void>;
    setPaused: (paused: boolean) => Promise<void>;
    isPaused: () => Promise<boolean>;
    getStats: () => Promise<any>;
    logRequest: (request: any, metadata?: any) => Promise<any>;
    logResponse: (response: any, request: any, metadata?: any) => Promise<any>;
  };
  apispec: {
    analyze: (entries: any[]) => Promise<any>;
    generateOpenAPI: (analysis: any, options: any) => Promise<any>;
    generateAsyncAPI: (entries: any[], options: any) => Promise<any>;
    generateGraphQL: (entries: any[]) => Promise<any>;
    exportOpenAPIJSON: (spec: any) => Promise<string>;
    exportOpenAPIYAML: (spec: any) => Promise<string>;
    validateOpenAPI: (spec: any) => Promise<{ valid: boolean; errors: string[] }>;
    loadOpenAPIFile: (filePath: string) => Promise<any>;
  };
  publishing: {
    generateDocumentation: (spec: any, options: any) => Promise<any>;
    exportMarkdown: (spec: any, options: any) => Promise<string>;
    generateSDK: (spec: any, options: any) => Promise<any>;
    generateChangelog: (oldSpec: any, newSpec: any) => Promise<any>;
    publish: (doc: any, options: any) => Promise<any>;
    stopServer: () => Promise<any>;
    getStatus: () => Promise<any>;
    openDirectory: (directory: string) => Promise<any>;
  };
  tabs: {
    create: (tab: any) => Promise<any>;
    getAll: () => Promise<any[]>;
    update: (id: string, updates: any) => Promise<boolean>;
    close: (id: string) => Promise<boolean>;
    closeOthers: (keepId: string) => Promise<number>;
    closeAll: () => Promise<number>;
    setActive: (id: string) => Promise<boolean>;
    getActive: () => Promise<any | null>;
    goBack: () => Promise<any | null>;
    goForward: () => Promise<any | null>;
    search: (query: string) => Promise<any[]>;
    reorder: (tabId: string, newIndex: number) => Promise<boolean>;
    createGroup: (name: string, color?: string) => Promise<any>;
    getAllGroups: () => Promise<any[]>;
    addToGroup: (tabId: string, groupId: string) => Promise<boolean>;
  };
  commands: {
    search: (query: string) => Promise<any[]>;
    execute: (id: string) => Promise<boolean>;
    getAll: () => Promise<any[]>;
    getRecent: () => Promise<any[]>;
  };
  favorites: {
    add: (favorite: any) => Promise<any>;
    remove: (id: string) => Promise<boolean>;
    getAll: () => Promise<any[]>;
    toggle: (favorite: any) => Promise<{ added: boolean; favorite?: any }>;
    isFavorite: (entityId: string) => Promise<boolean>;
    search: (query: string) => Promise<any[]>;
    createFolder: (name: string, color?: string) => Promise<any>;
    getAllFolders: () => Promise<any[]>;
  };
  layout: {
    getAll: () => Promise<any[]>;
    getActive: () => Promise<any | null>;
    setActive: (layoutId: string) => Promise<boolean>;
    create: (name: string, panels: any[], description?: string) => Promise<any>;
    update: (layoutId: string, updates: any) => Promise<boolean>;
    delete: (layoutId: string) => Promise<boolean>;
  };
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
