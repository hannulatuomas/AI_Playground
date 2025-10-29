# API Documentation

**Version:** 0.7.0  
**Last Updated:** October 23, 2025

Internal API documentation for LocalAPI's IPC communication and services.

## IPC API (Renderer ↔ Main)

The IPC API is exposed through the preload script and available in the renderer process via `window.electron`.

### Request Operations

#### `request:send`
Send an HTTP request.

**Parameters:**
```typescript
{
  method: HttpMethod;
  url: string;
  headers?: Header[];
  body?: RequestBody;
  auth?: Auth;
}
```

**Returns:**
```typescript
{
  status: number;
  statusText: string;
  headers: Record<string, string>;
  body: any;
  time: number;
  size: number;
}
```

### Collection Operations

#### `collections:getAll`
Get all collections.

**Returns:** `Collection[]`

#### `collections:create`
Create a new collection.

**Parameters:** `Collection`  
**Returns:** `Collection`

#### `collections:update`
Update a collection.

**Parameters:** `id: string, collection: Partial<Collection>`  
**Returns:** `Collection`

#### `collections:delete`
Delete a collection.

**Parameters:** `id: string`  
**Returns:** `void`

### Environment Operations

#### `environments:getAll`
Get all environments.

**Returns:** `Environment[]`

#### `environments:create`
Create a new environment.

**Parameters:** `Environment`  
**Returns:** `Environment`

#### `environments:update`
Update an environment.

**Parameters:** `id: string, environment: Partial<Environment>`  
**Returns:** `Environment`

#### `environments:delete`
Delete an environment.

**Parameters:** `id: string`  
**Returns:** `void`

### Variable Operations

#### `variables:get`
Get variables for a scope.

**Parameters:** `scope: VariableScope`  
**Returns:** `Record<string, any>`

#### `variables:set`
Set a variable.

**Parameters:** `scope: VariableScope, key: string, value: any`  
**Returns:** `void`

#### `variables:delete`
Delete a variable.

**Parameters:** `scope: VariableScope, key: string`  
**Returns:** `void`

### Script Operations

#### `script:execute`
Execute a script.

**Parameters:**
```typescript
{
  script: string;
  context: {
    request?: Request;
    response?: Response;
    variables?: Record<string, any>;
  };
}
```

**Returns:**
```typescript
{
  success: boolean;
  result?: any;
  error?: string;
  logs?: string[];
}
```

### Settings Operations

#### `settings:get`
Get application settings.

**Returns:** `Settings`

#### `settings:update`
Update settings.

**Parameters:** `Partial<Settings>`  
**Returns:** `void`

## Database Schema

### Collections Table

```sql
CREATE TABLE collections (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  parent_id TEXT,
  variables TEXT, -- JSON
  created_at INTEGER,
  updated_at INTEGER
);
```

### Requests Table

```sql
CREATE TABLE requests (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  collection_id TEXT,
  protocol TEXT,
  method TEXT,
  url TEXT,
  headers TEXT, -- JSON
  query_params TEXT, -- JSON
  body TEXT, -- JSON
  auth TEXT, -- JSON
  pre_request_script TEXT,
  test_script TEXT,
  assertions TEXT, -- JSON
  created_at INTEGER,
  updated_at INTEGER,
  FOREIGN KEY (collection_id) REFERENCES collections(id)
);
```

### Environments Table

```sql
CREATE TABLE environments (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  variables TEXT, -- JSON
  is_active INTEGER,
  created_at INTEGER,
  updated_at INTEGER
);
```

### Variables Table

```sql
CREATE TABLE variables (
  id TEXT PRIMARY KEY,
  key TEXT NOT NULL,
  value TEXT,
  type TEXT,
  scope TEXT,
  scope_id TEXT,
  enabled INTEGER,
  description TEXT,
  created_at INTEGER,
  updated_at INTEGER
);
```

## Service APIs

### DatabaseService

```typescript
class DatabaseService {
  constructor(dbPath: string);
  
  // Generic CRUD
  create<T>(table: string, data: T): Promise<T>;
  read<T>(table: string, id: string): Promise<T | null>;
  update<T>(table: string, id: string, data: Partial<T>): Promise<T>;
  delete(table: string, id: string): Promise<void>;
  list<T>(table: string, filter?: any): Promise<T[]>;
  
  // Transactions
  transaction<T>(callback: () => Promise<T>): Promise<T>;
}
```

### RequestService

```typescript
class RequestService {
  async send(request: Request, variables: Record<string, any>): Promise<Response>;
  async sendGraphQL(query: string, variables: any, endpoint: string): Promise<Response>;
  async sendSOAP(operation: string, params: any, wsdl: string): Promise<Response>;
  async sendGRPC(service: string, method: string, data: any, proto: string): Promise<Response>;
}
```

### ScriptService

```typescript
class ScriptService {
  execute(script: string, context: ScriptContext): Promise<ScriptResult>;
  createSandbox(context: ScriptContext): any;
  validateScript(script: string): { valid: boolean; errors?: string[] };
}
```

### MockServerService

```typescript
class MockServerService {
  create(config: MockServerConfig): Promise<MockServer>;
  start(id: string): Promise<void>;
  stop(id: string): Promise<void>;
  update(id: string, config: Partial<MockServerConfig>): Promise<void>;
  delete(id: string): Promise<void>;
}
```

### WorkflowService

```typescript
class WorkflowService {
  create(workflow: Workflow): Promise<Workflow>;
  run(id: string): Promise<WorkflowResult>;
  schedule(id: string, cron: string): Promise<void>;
  unschedule(id: string): Promise<void>;
}
```

## Script Context API

### pm Object

```typescript
interface PM {
  request: {
    url: string;
    method: string;
    headers: Record<string, string>;
    body: any;
  };
  
  response: {
    code: number;
    status: string;
    headers: Record<string, string>;
    json(): any;
    text(): string;
    responseTime: number;
  };
  
  variables: {
    get(key: string): any;
    set(key: string, value: any): void;
  };
  
  environment: {
    get(key: string): any;
    set(key: string, value: any): void;
  };
  
  globals: {
    get(key: string): any;
    set(key: string, value: any): void;
  };
  
  test(name: string, fn: () => void): void;
  
  expect(value: any): Assertion;
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 1000 | Database error |
| 2000 | Request failed |
| 2001 | Request timeout |
| 2002 | Network error |
| 3000 | Script execution error |
| 3001 | Script syntax error |
| 4000 | Mock server error |
| 5000 | Workflow error |
| 9000 | Unknown error |

## Events

### Main Process Events

```typescript
// Request sent
ipcMain.emit('request:sent', request);

// Request completed
ipcMain.emit('request:completed', response);

// Request failed
ipcMain.emit('request:failed', error);

// Collection updated
ipcMain.emit('collection:updated', collection);

// Environment changed
ipcMain.emit('environment:changed', environment);
```

### Renderer Events

```typescript
// Listen for events
window.electronAPI.on('request:completed', (response) => {
  // Handle response
});
```

## Cache Operations (v0.6.0)

#### `cache:getStats`
Get cache statistics.

**Returns:** `{ hits: number; misses: number; hitRate: number; size: number; count: number }`

#### `cache:clear`
Clear all cached responses.

**Returns:** `boolean`

#### `cache:cleanExpired`
Remove expired cache entries.

**Returns:** `number` (count of removed entries)

#### `cache:invalidateByTags`
Invalidate cache entries by tags.

**Parameters:** `string[]` (tags)  
**Returns:** `number` (count of invalidated entries)

#### `cache:invalidateByPattern`
Invalidate cache entries matching URL pattern.

**Parameters:** `string` (regex pattern)  
**Returns:** `number` (count of invalidated entries)

#### `cache:configure`
Configure cache settings.

**Parameters:** `{ enabled?: boolean; defaultTTL?: number; maxSize?: number }`  
**Returns:** `boolean`

## Import/Export Operations (v0.6.0)

#### `importExport:getSupportedFormats`
Get supported import/export formats.

**Returns:** `{ import: string[]; export: string[] }`

#### `importExport:detectFormat`
Auto-detect format from content.

**Parameters:** `string` (content)  
**Returns:** `string | null` (format)

#### `importExport:import`
Import collections/requests.

**Parameters:** `content: string, format?: string, options?: any`  
**Returns:** `ImportResult`

#### `importExport:exportCollections`
Export collections to format.

**Parameters:** `collectionIds: string[], format: string, options?: any`  
**Returns:** `ExportResult`

#### `importExport:exportRequest`
Export single request.

**Parameters:** `requestId: string, format: string, options?: any`  
**Returns:** `ExportResult`

#### `importExport:exportRequests`
Export multiple requests.

**Parameters:** `requestIds: string[], format: string, options?: any`  
**Returns:** `ExportResult`

#### `importExport:getHandlerInfo`
Get handler information.

**Parameters:** `string` (format)  
**Returns:** `HandlerInfo`

#### `importExport:getExample`
Get format example.

**Parameters:** `string` (format)  
**Returns:** `string`

## Git Operations (v0.6.0)

#### `git:isRepository`
Check if directory is a git repository.

**Returns:** `boolean`

#### `git:init`
Initialize git repository.

**Returns:** `boolean`

#### `git:getStatus`
Get repository status.

**Returns:** `GitStatus`

#### `git:add`
Stage files.

**Parameters:** `string | string[]` (files)  
**Returns:** `boolean`

#### `git:reset`
Unstage files.

**Parameters:** `string[]?` (files)  
**Returns:** `boolean`

#### `git:commit`
Commit staged changes.

**Parameters:** `GitCommitOptions`  
**Returns:** `boolean`

#### `git:getLog`
Get commit history.

**Parameters:** `number?` (maxCount)  
**Returns:** `GitCommit[]`

#### `git:getDiff`
Get diff for unstaged changes.

**Parameters:** `string?` (file)  
**Returns:** `string`

#### `git:getDiffStaged`
Get diff for staged changes.

**Parameters:** `string?` (file)  
**Returns:** `string`

#### `git:getBranches`
Get list of branches.

**Returns:** `GitBranch[]`

#### `git:createBranch`
Create new branch.

**Parameters:** `branchName: string, checkout: boolean`  
**Returns:** `boolean`

#### `git:checkout`
Checkout branch.

**Parameters:** `string` (branchName)  
**Returns:** `boolean`

#### `git:hasChanges`
Check if repository has changes.

**Returns:** `boolean`

#### `git:discardChanges`
Discard changes to files.

**Parameters:** `string[]?` (files)  
**Returns:** `boolean`

#### `git:getConfig`
Get git configuration value.

**Parameters:** `string` (key)  
**Returns:** `string | null`

#### `git:setConfig`
Set git configuration value.

**Parameters:** `key: string, value: string`  
**Returns:** `boolean`

## Plugin Operations (v0.6.0)

#### `plugins:discover`
Discover plugins in plugins directory.

**Returns:** `string[]` (plugin directories)

#### `plugins:load`
Load a plugin.

**Parameters:** `string` (pluginDir)  
**Returns:** `Plugin`

#### `plugins:unload`
Unload a plugin.

**Parameters:** `string` (pluginId)  
**Returns:** `boolean`

#### `plugins:reload`
Reload a plugin.

**Parameters:** `string` (pluginId)  
**Returns:** `Plugin`

#### `plugins:setEnabled`
Enable/disable a plugin.

**Parameters:** `pluginId: string, enabled: boolean`  
**Returns:** `boolean`

#### `plugins:getAll`
Get all loaded plugins.

**Returns:** `Plugin[]`

#### `plugins:getInfo`
Get plugin information.

**Parameters:** `string` (pluginId)  
**Returns:** `PluginInfo`

## Report Operations (v0.6.0)

#### `reports:generate`
Generate PDF report.

**Parameters:** `data: any, options: ReportOptions`  
**Returns:** `ReportResult`

## Mock Server Operations (v0.5.0)

#### `mockServer:create`
Create mock server from collection.

**Parameters:** `CreateServerOptions`  
**Returns:** `string` (serverId)

#### `mockServer:start`
Start mock server.

**Parameters:** `string` (serverId)  
**Returns:** `boolean`

#### `mockServer:stop`
Stop mock server.

**Parameters:** `string` (serverId)  
**Returns:** `boolean`

#### `mockServer:delete`
Delete mock server.

**Parameters:** `string` (serverId)  
**Returns:** `boolean`

#### `mockServer:getAll`
Get all mock servers.

**Returns:** `MockServer[]`

#### `mockServer:getInfo`
Get mock server information.

**Parameters:** `string` (serverId)  
**Returns:** `MockServerInfo`

#### `mockServer:getLogs`
Get mock server logs.

**Parameters:** `string` (serverId)  
**Returns:** `MockServerLog[]`

#### `mockServer:getStats`
Get mock server statistics.

**Parameters:** `string` (serverId)  
**Returns:** `MockServerStats`

## Batch Runner Operations (v0.5.0)

#### `batch:run`
Run batch of requests.

**Parameters:** `requests: any[], variables?: any`  
**Returns:** `BatchResult`

#### `batch:getResults`
Get batch results.

**Parameters:** `string` (batchId)  
**Returns:** `BatchResult`

## Monitoring Operations (v0.5.0)

#### `monitor:create`
Create monitor.

**Parameters:** `MonitorOptions`  
**Returns:** `string` (monitorId)

#### `monitor:start`
Start monitor.

**Parameters:** `string` (monitorId)  
**Returns:** `boolean`

#### `monitor:stop`
Stop monitor.

**Parameters:** `string` (monitorId)  
**Returns:** `boolean`

#### `monitor:delete`
Delete monitor.

**Parameters:** `string` (monitorId)  
**Returns:** `boolean`

#### `monitor:getAll`
Get all monitors.

**Returns:** `Monitor[]`

#### `monitor:getLogs`
Get monitor logs.

**Parameters:** `string` (monitorId)  
**Returns:** `MonitorLog[]`

#### `monitor:getStats`
Get monitor statistics.

**Parameters:** `string` (monitorId)  
**Returns:** `MonitorStats`

## Security Operations (v0.5.0)

#### `security:scan`
Run security assertions on request/response.

**Parameters:** `request: any, response: any`  
**Returns:** `SecurityScanResult`

#### `security:scanCollection`
Scan entire collection for security issues.

**Parameters:** `string` (collectionId)  
**Returns:** `SecurityScanResult[]`

## Vulnerability Operations (v0.5.0)

#### `vulnerability:scan`
Scan request for vulnerabilities.

**Parameters:** `request: any, options?: any`  
**Returns:** `VulnerabilityScanResult`

#### `vulnerability:scanEndpoint`
Scan endpoint directly.

**Parameters:** `url: string, method: string, options?: any`  
**Returns:** `VulnerabilityScanResult`

## Type Definitions

See [src/types/models.ts](../src/types/models.ts) for complete type definitions.

---

**Version:** 0.6.0  
**Last Updated:** October 23, 2025

For usage examples, see [User Guide](USER_GUIDE.md).
