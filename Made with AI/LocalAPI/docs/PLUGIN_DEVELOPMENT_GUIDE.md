# Plugin Development Guide

**Version:** 0.7.0  
**Last Updated:** October 23, 2025

## Overview

LocalAPI supports a powerful plugin system that allows you to extend functionality with JavaScript modules. Plugins can hook into the application lifecycle, modify requests/responses, and add custom features.

## Quick Start

### 1. Create Plugin Directory

```
plugins/
  └── my-plugin/
      ├── plugin.json
      ├── index.js
      └── README.md
```

### 2. Create Manifest (plugin.json)

```json
{
  "id": "com.example.myplugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "My awesome plugin",
  "author": "Your Name",
  "license": "MIT",
  "main": "index.js",
  "permissions": ["network", "notifications"],
  "hooks": ["onLoad", "onBeforeRequest", "onAfterResponse"]
}
```

### 3. Create Plugin Code (index.js)

```javascript
module.exports = {
  async onLoad(context) {
    context.api.log('Plugin loaded!');
    context.api.notify('My plugin is active', 'success');
  },

  async onBeforeRequest(request, context) {
    // Modify request before sending
    request.headers.push({
      key: 'X-My-Plugin',
      value: 'Hello',
      enabled: true
    });
    return request;
  },

  async onAfterResponse(response, request, context) {
    // Process response after receiving
    context.api.log('Response:', response.status);
    return response;
  }
};
```

### 4. Load Plugin

1. Place plugin folder in `{userData}/plugins/`
2. Open Plugin Manager in LocalAPI
3. Your plugin will appear in the list
4. Enable it with the toggle switch

## Plugin Manifest

### Required Fields

- **id**: Unique identifier (reverse domain notation recommended)
- **name**: Display name
- **version**: Semantic version (e.g., "1.0.0")
- **description**: Brief description
- **main**: Entry point file (usually "index.js")

### Optional Fields

- **author**: Plugin author name
- **homepage**: Plugin website URL
- **license**: License type (e.g., "MIT", "Apache-2.0")
- **dependencies**: NPM dependencies (object)
- **permissions**: Required permissions array
- **hooks**: List of hooks used by plugin

## Permissions

Plugins must declare required permissions:

- **network**: Make HTTP requests
- **filesystem**: Read/write files
- **database**: Access database
- **clipboard**: Access clipboard
- **notifications**: Show notifications
- **settings**: Read/write settings
- **all**: All permissions (use sparingly)

Example:
```json
{
  "permissions": ["network", "notifications"]
}
```

## Plugin Context

Every hook receives a `context` object with:

### Plugin Info

```javascript
context.plugin.id          // Plugin ID
context.plugin.name        // Plugin name
context.plugin.version     // Plugin version
context.plugin.dataDir     // Plugin data directory
```

### API Methods

#### Make HTTP Requests
```javascript
const response = await context.api.request({
  method: 'GET',
  url: 'https://api.example.com/data'
});
```

#### Show Notifications
```javascript
context.api.notify('Message', 'success'); // success, info, warning, error
```

#### Log Messages
```javascript
context.api.log('Debug message', data);
```

#### Storage (Plugin-specific)
```javascript
// Store data
await context.api.storage.set('key', value);

// Retrieve data
const value = await context.api.storage.get('key');

// Delete data
await context.api.storage.delete('key');

// Clear all data
await context.api.storage.clear();
```

#### Settings
```javascript
// Get setting
const value = await context.api.settings.get('settingKey');

// Set setting
await context.api.settings.set('settingKey', value);
```

### Utility Functions

```javascript
// Parse JSON safely
const data = context.utils.parseJSON(jsonString);

// Format date
const formatted = context.utils.formatDate(new Date());

// Generate UUID
const id = context.utils.uuid();
```

## Lifecycle Hooks

### onLoad

Called when plugin is loaded.

```javascript
async onLoad(context) {
  context.api.log('Plugin initialized');
  
  // Initialize plugin state
  const count = await context.api.storage.get('loadCount') || 0;
  await context.api.storage.set('loadCount', count + 1);
}
```

### onUnload

Called when plugin is unloaded.

```javascript
async onUnload(context) {
  context.api.log('Plugin cleanup');
  
  // Clean up resources
  await context.api.storage.clear();
}
```

## Request/Response Hooks

### onBeforeRequest

Modify requests before they're sent.

```javascript
async onBeforeRequest(request, context) {
  // Add custom header
  request.headers.push({
    key: 'X-Custom-Header',
    value: 'value',
    enabled: true
  });

  // Log request
  context.api.log('Sending:', request.method, request.url);

  // Must return modified request
  return request;
}
```

### onAfterResponse

Process responses after they're received.

```javascript
async onAfterResponse(response, request, context) {
  // Log response time
  context.api.log(`${request.url} took ${response.time}ms`);

  // Alert on errors
  if (response.status >= 400) {
    context.api.notify(`Request failed: ${response.status}`, 'error');
  }

  // Must return response (modified or not)
  return response;
}
```

## Collection Hooks

### onCollectionCreate

```javascript
async onCollectionCreate(collection, context) {
  context.api.log('New collection:', collection.name);
}
```

### onCollectionUpdate

```javascript
async onCollectionUpdate(collection, context) {
  context.api.log('Updated collection:', collection.name);
}
```

### onCollectionDelete

```javascript
async onCollectionDelete(collectionId, context) {
  context.api.log('Deleted collection:', collectionId);
}
```

## Settings Hook

### onSettingsChange

```javascript
async onSettingsChange(key, value, context) {
  context.api.log(`Setting changed: ${key} = ${value}`);
}
```

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```javascript
async onBeforeRequest(request, context) {
  try {
    // Your code
    return request;
  } catch (error) {
    context.api.log('Error:', error.message);
    return request; // Return unmodified on error
  }
}
```

### 2. Async Operations

Use async/await for asynchronous operations:

```javascript
async onLoad(context) {
  const data = await context.api.storage.get('data');
  // Process data
}
```

### 3. State Management

Use plugin storage for persistent state:

```javascript
// Save state
await context.api.storage.set('state', {
  counter: 0,
  lastRun: new Date().toISOString()
});

// Load state
const state = await context.api.storage.get('state') || {};
```

### 4. Performance

- Keep hooks fast (< 100ms)
- Don't block request/response flow
- Use storage sparingly
- Cache expensive computations

### 5. Security

- Validate all external data
- Don't store sensitive data in storage
- Request only needed permissions
- Sanitize user input

## Example Plugins

### Request Logger

```javascript
module.exports = {
  async onAfterResponse(response, request, context) {
    const log = {
      timestamp: new Date().toISOString(),
      method: request.method,
      url: request.url,
      status: response.status,
      time: response.time
    };

    const logs = await context.api.storage.get('logs') || [];
    logs.push(log);
    
    // Keep last 100
    if (logs.length > 100) logs.shift();
    
    await context.api.storage.set('logs', logs);
    return response;
  }
};
```

### Auto-Retry

```javascript
module.exports = {
  async onAfterResponse(response, request, context) {
    if (response.status === 429) { // Rate limited
      context.api.notify('Rate limited, consider retrying', 'warning');
    }
    return response;
  }
};
```

### Request Timer

```javascript
module.exports = {
  async onBeforeRequest(request, context) {
    await context.api.storage.set('requestStart', Date.now());
    return request;
  },

  async onAfterResponse(response, request, context) {
    const start = await context.api.storage.get('requestStart');
    const duration = Date.now() - start;
    
    if (duration > 5000) {
      context.api.notify(
        `Slow request: ${request.url} took ${duration}ms`,
        'warning'
      );
    }
    
    return response;
  }
};
```

## Debugging

### Console Logging

Use `context.api.log()` for debug output:

```javascript
context.api.log('Debug:', data);
```

Logs appear in the main process console.

### Error Messages

Check Plugin Manager for error messages if plugin fails to load.

### Hot Reload

Use the "Reload" button in Plugin Manager to reload after changes.

## Testing

### Manual Testing

1. Make changes to plugin code
2. Click "Reload" in Plugin Manager
3. Test functionality
4. Check logs for errors

### Unit Testing

Create tests for your plugin logic:

```javascript
// test.js
const plugin = require('./index');

async function test() {
  const mockContext = {
    api: {
      log: console.log,
      storage: new Map()
    }
  };

  const request = {
    method: 'GET',
    url: 'https://example.com',
    headers: []
  };

  const result = await plugin.onBeforeRequest(request, mockContext);
  console.assert(result.headers.length > 0, 'Should add header');
}

test();
```

## Distribution

### Package Structure

```
my-plugin/
├── plugin.json
├── index.js
├── README.md
├── LICENSE
└── package.json (if using npm modules)
```

### Installation

Users install by:
1. Downloading plugin folder
2. Placing in `{userData}/plugins/`
3. Restarting LocalAPI or clicking "Discover" in Plugin Manager

### Versioning

Follow Semantic Versioning:
- **1.0.0**: Initial release
- **1.0.1**: Bug fixes
- **1.1.0**: New features (backward compatible)
- **2.0.0**: Breaking changes

## Troubleshooting

### Plugin Not Loading

- Check `plugin.json` syntax
- Verify `main` file exists
- Check console for errors
- Ensure all required fields present

### Permission Denied

- Add required permission to `permissions` array
- Reload plugin after manifest changes

### Hook Not Called

- Add hook name to `hooks` array in manifest
- Verify hook function name matches exactly
- Check for JavaScript errors in hook

### Storage Not Working

- Ensure using `await` with storage methods
- Check plugin has write permissions
- Verify data directory exists

## API Reference

See [Plugin Type Definitions](../src/types/plugin.ts) for complete API documentation.

## Examples

Check the `plugins/example-plugin/` directory for a complete working example.

## Support

For questions or issues:
1. Check this guide
2. Review example plugin
3. Check Plugin Manager for errors
4. Review console logs

## Future Features

Planned plugin capabilities:
- Custom UI components
- Menu items
- Keyboard shortcuts
- Protocol handlers
- Export formats
- Import formats
- Custom assertions
- Custom authentication methods

## Contributing

To contribute to plugin system:
1. Submit issues for bugs
2. Request features
3. Share your plugins
4. Improve documentation
