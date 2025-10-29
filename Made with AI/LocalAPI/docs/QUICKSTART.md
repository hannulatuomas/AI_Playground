# Quick Start Guide

**Version:** 0.7.0  
**Last Updated:** October 23, 2025

Get up and running with LocalAPI in minutes.

## Installation

### Prerequisites

Before you begin, ensure you have:
- **Node.js** 18.x or higher ([Download](https://nodejs.org/))
- **npm** (comes with Node.js)
- **Python** 3.x (for native dependencies)
- **Build tools** (Windows: Visual Studio Build Tools, macOS: Xcode, Linux: build-essential)

### Step 1: Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd LocalAPI

# Install dependencies
npm install
```

### Step 2: Run Development Server

```bash
npm run dev
```

This will:
1. Start the Vite dev server on http://localhost:5173
2. Launch the Electron app in development mode
3. Open DevTools automatically

## First Request

### 1. Create a Request

1. Click the **"+"** button in the sidebar
2. Enter a name for your request (e.g., "Get Users")
3. Select **GET** method
4. Enter URL: `https://jsonplaceholder.typicode.com/users`

### 2. Send Request

1. Click the **Send** button
2. View the response in the Response panel
3. Check status code, headers, and body

### 3. Save to Collection

1. Click **Save** button
2. Create a new collection or select existing
3. Request is now saved and can be reused

## Using Variables

### Global Variables

1. Go to **Settings** → **Variables**
2. Add a variable:
   - Key: `baseUrl`
   - Value: `https://api.example.com`
3. Use in requests: `{{baseUrl}}/users`

### Environment Variables

1. Create an environment (e.g., "Development")
2. Add variables specific to that environment
3. Switch environments from the dropdown

## Collections

### Create a Collection

1. Click **New Collection** in sidebar
2. Name it (e.g., "User API")
3. Add description (optional)

### Organize Requests

- Drag and drop requests into collections
- Create folders within collections
- Nest folders for better organization

## Testing

### Add Test Script

1. Open a request
2. Go to **Tests** tab
3. Write test script:

```javascript
pm.test("Status is 200", function() {
  pm.response.to.have.status(200);
});

pm.test("Response has users", function() {
  const json = pm.response.json();
  pm.expect(json).to.be.an('array');
});
```

### Auto-Extract Variables

```javascript
// Extract token from response
const json = pm.response.json();
pm.environment.set("authToken", json.token);
```

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Send Request | `Ctrl+Enter` |
| New Request | `Ctrl+N` |
| Save Request | `Ctrl+S` |
| Toggle Theme | `Ctrl+T` |
| Open Settings | `Ctrl+,` |

## Next Steps

- Read the [User Guide](USER_GUIDE.md) for detailed features
- Explore [API Documentation](API.md)
- Learn about [Extending LocalAPI](EXTENDING_GUIDE.md)

## Troubleshooting

### App Won't Start

1. Check Node.js version: `node --version` (should be 18+)
2. Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
3. Check for port conflicts (5173 should be free)

### Native Dependencies Fail

**Windows:**
```bash
npm install --global windows-build-tools
```

**macOS:**
```bash
xcode-select --install
```

**Linux:**
```bash
sudo apt-get install build-essential
```

### Database Errors

1. Delete database file: `data/*.db`
2. Restart application (will recreate database)

## Using Cache (v0.6.0)

### Enable Caching

1. Click the **Cache** tab in the top navigation
2. Toggle **Enable Caching** on
3. Configure TTL (default: 5 minutes)
4. Set max cache size (default: 100 MB)

### View Statistics

- **Cache Hits**: Requests served from cache
- **Cache Misses**: Requests that weren't cached
- **Hit Rate**: Percentage of cached responses
- **Current Size**: Cache size in MB

### Clear Cache

- **Clear All**: Remove all cached responses
- **Clean Expired**: Remove only expired entries
- **Invalidate by Pattern**: Use regex to remove specific entries

## Import/Export (v0.6.0)

### Import Collections

1. Click the **Import/Export** button (toolbar)
2. Select **Import** tab
3. Choose format (JSON or cURL) or use auto-detect
4. Paste content or select file
5. Click **Import**

### Export Collections

1. Click the **Import/Export** button
2. Select **Export** tab
3. Choose collections to export
4. Select format (JSON or cURL)
5. Export to clipboard or file

### cURL Commands

**Import cURL:**
```bash
curl -X POST 'https://api.example.com/users' \
  -H 'Content-Type: application/json' \
  -d '{"name":"John"}'
```

**Export to cURL:** Select requests and export as cURL format

## Git Version Control (v0.6.0)

### Initialize Repository

1. Click the **Git** tab
2. Click **Initialize Repository**
3. .gitignore created automatically

### Commit Changes

1. View file status (modified, created, deleted)
2. Click **+** to stage files
3. Enter commit message
4. Click **Commit**

### Branch Management

- **Create Branch**: Click "New Branch" button
- **Switch Branch**: Select from dropdown
- **View History**: See commit log with pagination

## Plugins (v0.6.0)

### Install Plugin

1. Place plugin folder in `plugins/` directory
2. Click the **Plugins** tab
3. Click **Discover Plugins**
4. Enable the plugin

### Manage Plugins

- **Enable/Disable**: Toggle plugin status
- **Reload**: Reload plugin after changes
- **View Info**: See plugin details and permissions

## Generate Reports (v0.6.0)

### Create PDF Report

1. Click the **Reports** tab
2. Select report type:
   - Security Scan Report
   - Vulnerability Scan Report
   - Security Trends Report
   - Performance Trends Report
3. Configure options:
   - Title and author
   - Date range (for trends)
   - Include charts
   - Include summary/details
4. Click **Generate Report**
5. Save PDF to desired location

### Report Types

- **Security Scan**: Current security status with findings
- **Vulnerability Scan**: Detailed vulnerability assessment
- **Security Trends**: Historical security analysis with charts
- **Performance Trends**: Performance metrics over time

## Getting Help

- Check [Documentation](../docs/)
- Review [GitHub Issues](https://github.com/localapi/localapi/issues)
- Read [FAQ](USER_GUIDE.md#faq)
- See [Git Integration Guide](GIT_INTEGRATION_GUIDE.md)
- See [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md)
- See [Reporting Guide](REPORTING_GUIDE.md)

---

**Version:** 0.7.0  
**Last Updated:** October 23, 2025
