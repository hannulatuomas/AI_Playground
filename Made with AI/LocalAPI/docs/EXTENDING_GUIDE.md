# Extending LocalAPI

**Version:** 0.7.0  
**Last Updated:** October 23, 2025

Guide for extending LocalAPI with plugins, custom protocols, and themes.

## Plugin System (v0.6.0)

LocalAPI v0.6.0 includes a complete plugin system with dynamic loading, lifecycle hooks, and permission management.

### Complete Plugin Development Guide

For comprehensive plugin development documentation, see:
📖 **[Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md)**

The guide includes:
- Quick start tutorial
- Complete API reference
- All available hooks
- Permission system
- Storage API
- Best practices
- Example plugins
- Debugging guide

### Quick Start

1. **Create Plugin Directory**
```bash
mkdir plugins/my-plugin
cd plugins/my-plugin
```

2. **Create plugin.json Manifest**
```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "My awesome plugin",
  "author": "Your Name",
  "main": "plugin.js",
  "permissions": ["network", "storage"]
}
```

3. **Create plugin.js**
```javascript
module.exports = {
  onLoad(context) {
    console.log('Plugin loaded!');
    context.storage.set('initialized', true);
  },
  
  onBeforeRequest(request, context) {
    // Modify request before sending
    request.headers.push({
      key: 'X-Plugin',
      value: 'My Plugin',
      enabled: true
    });
    return request;
  },
  
  onAfterRequest(request, response, context) {
    // Process response
    console.log('Response received:', response.status);
    return response;
  },
  
  onUnload(context) {
    console.log('Plugin unloaded');
  }
};
```

4. **Load Plugin**
- Open LocalAPI
- Go to **Plugins** tab
- Click **Discover Plugins**
- Enable your plugin

### Available Hooks

- `onLoad(context)` - Called when plugin loads
- `onUnload(context)` - Called when plugin unloads
- `onBeforeRequest(request, context)` - Before sending request
- `onAfterRequest(request, response, context)` - After receiving response
- `onCollectionCreate(collection, context)` - When collection created
- `onCollectionUpdate(collection, context)` - When collection updated
- `onCollectionDelete(collectionId, context)` - When collection deleted
- `onSettingsChange(settings, context)` - When settings change

### Plugin Context API

```javascript
// Storage
context.storage.get(key)
context.storage.set(key, value)
context.storage.delete(key)
context.storage.clear()

// HTTP Client
context.http.get(url, options)
context.http.post(url, data, options)

// Logging
context.logger.info(message)
context.logger.warn(message)
context.logger.error(message)

// Configuration
context.config.get(key)
context.config.set(key, value)
```

### Permission System

Plugins must declare required permissions in `plugin.json`:

- `network` - Make HTTP requests
- `filesystem` - Read/write files
- `database` - Access database
- `storage` - Use plugin storage
- `clipboard` - Access clipboard
- `notifications` - Show notifications

Place in `plugins/` directory and reload LocalAPI.

## Custom Protocols

Implement `ProtocolHandler` interface:

```typescript
export class MyProtocolHandler implements ProtocolHandler {
  async send(request: Request): Promise<Response> {
    // Protocol implementation
  }
  
  async loadSchema(url: string): Promise<any> {
    // Schema loading
  }
}
```

## Custom Themes

Create CSS file with theme variables:

```css
[data-theme='my-theme'] {
  --bg-primary: #1a1a2e;
  --text-primary: #e94560;
  --accent-color: #e94560;
}
```

## Script Extensions

Extend pm object:

```typescript
pm.custom = {
  hash(value: string): string {
    // Custom function
  }
};
```

See full documentation for detailed examples.
