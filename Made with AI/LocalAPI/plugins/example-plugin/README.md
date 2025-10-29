# Example Plugin

This is an example plugin for LocalAPI that demonstrates the plugin system capabilities.

## Features

- **Request Modification**: Adds a custom header to all outgoing requests
- **Response Tracking**: Tracks response times and stores them
- **Slow Request Alerts**: Shows notifications for requests taking over 1 second
- **Load Counter**: Tracks how many times the plugin has been loaded
- **Collection Hooks**: Logs when collections are created, updated, or deleted

## What It Does

### On Load
- Shows a success notification
- Increments and logs the load counter
- Stores the load count in plugin storage

### Before Each Request
- Adds `X-Plugin-Example` header to the request
- Logs the request method and URL
- Stores the last request details

### After Each Response
- Logs the response status
- Tracks response times (keeps last 100)
- Shows warning for slow requests (>1000ms)

### Collection Events
- Logs when collections are created, updated, or deleted

## Files

- `plugin.json` - Plugin manifest with metadata and permissions
- `index.js` - Main plugin code with hook implementations
- `README.md` - This file

## Permissions

This plugin requires:
- `network` - To make HTTP requests (if needed)
- `notifications` - To show notifications to the user

## Storage

The plugin stores:
- `loadCount` - Number of times plugin has been loaded
- `lastRequest` - Details of the last request
- `responseTimes` - Array of last 100 response times

## Hooks Used

- `onLoad` - Plugin initialization
- `onUnload` - Plugin cleanup
- `onBeforeRequest` - Modify requests before sending
- `onAfterResponse` - Process responses after receiving
- `onCollectionCreate` - React to collection creation
- `onCollectionUpdate` - React to collection updates
- `onCollectionDelete` - React to collection deletion

## Development

To modify this plugin:

1. Edit `index.js` to change behavior
2. Update `plugin.json` if you change permissions or hooks
3. Reload the plugin in LocalAPI

## License

MIT
