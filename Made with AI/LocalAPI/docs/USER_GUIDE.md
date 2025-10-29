# LocalAPI User Guide

**Version:** 0.7.0  
**Last Updated:** October 23, 2025

Complete guide to using LocalAPI for API development and testing.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Making Requests](#making-requests)
3. [Collections](#collections)
4. [Variables & Environments](#variables--environments)
5. [Scripting](#scripting)
6. [Testing & Assertions](#testing--assertions)
7. [API Documentation](#api-documentation)
8. [Protocol Support](#protocol-support)
9. [Mock Servers](#mock-servers)
10. [Batch Runner](#batch-runner)
11. [Monitoring](#monitoring)
12. [Data-Driven Testing](#data-driven-testing)
13. [Security Testing](#security-testing)
14. [Cache Management](#cache-management) ⭐ v0.6.0
15. [Import/Export](#importexport) ⭐ v0.6.0
16. [Git Version Control](#git-version-control) ⭐ v0.6.0
17. [Plugin System](#plugin-system) ⭐ v0.6.0
18. [PDF Reports](#pdf-reports) ⭐ v0.6.0
19. [Settings](#settings)
20. [FAQ](#faq)

## Introduction

LocalAPI is a fully local, offline-capable API development tool that helps you:
- Build and test API requests
- Organize requests in collections
- Automate testing with scripts
- Mock API servers
- Support multiple protocols (REST, GraphQL, SOAP, gRPC, etc.)

## Getting Started

See [Quick Start Guide](QUICKSTART.md) for installation and first steps.

## Request Builder

### HTTP Methods

Supported methods:
- **GET** - Retrieve data
- **POST** - Create data
- **PUT** - Update/replace data
- **PATCH** - Partial update
- **DELETE** - Remove data
- **HEAD** - Get headers only
- **OPTIONS** - Get supported methods

### Request Components

#### URL
- Enter full URL or use variables: `{{baseUrl}}/api/users`
- Query parameters can be added in URL or Params tab

#### Headers
- Add custom headers
- Common headers auto-suggested
- Enable/disable individual headers

#### Body
- **None** - No request body
- **JSON** - JSON data with syntax highlighting
- **XML** - XML data
- **Form Data** - Multipart form data
- **URL Encoded** - x-www-form-urlencoded
- **Raw** - Plain text
- **Binary** - File upload

#### Authentication
- **None** - No authentication
- **Basic Auth** - Username/password
- **Bearer Token** - JWT or OAuth token
- **API Key** - Header or query parameter
- **OAuth 2.0** - Full OAuth flow
- **Digest Auth** - Digest authentication

## Collections

### Creating Collections

1. Click **New Collection**
2. Enter name and description
3. Optionally add variables

### Organizing Requests

- Create folders within collections
- Drag and drop to reorder
- Nest folders for hierarchy
- Duplicate requests

### Sharing Collections

Export collections as JSON:
1. Right-click collection
2. Select **Export**
3. Save JSON file
4. Share with team

Import collections:
1. Click **Import**
2. Select JSON file
3. Collection added to sidebar

## Variables & Environments

### Variable Scopes

1. **Global** - Available everywhere
2. **Environment** - Specific to environment
3. **Collection** - Specific to collection

### Using Variables

In any field, use double curly braces:
```
{{variableName}}
```

Examples:
- URL: `{{baseUrl}}/api/{{version}}/users`
- Header: `Authorization: Bearer {{token}}`
- Body: `{"userId": "{{userId}}"}`

### Environments

Create environments for different stages:
- **Development** - Local API
- **Staging** - Test server
- **Production** - Live API

Switch environments from dropdown in header.

### Auto-Extraction

Extract values from responses:

```javascript
// In test script
const json = pm.response.json();
pm.environment.set("userId", json.id);
pm.environment.set("token", json.token);
```

## Scripting

### Pre-Request Scripts

Run before sending request:

```javascript
// Set timestamp
pm.variables.set("timestamp", Date.now());

// Generate random data
pm.variables.set("randomId", Math.floor(Math.random() * 1000));

// Compute signature
const signature = computeSignature();
pm.request.headers.add({key: "X-Signature", value: signature});
```

### Test Scripts

Run after receiving response:

```javascript
// Status code test
pm.test("Status is 200", function() {
  pm.response.to.have.status(200);
});

// Response time test
pm.test("Response time < 500ms", function() {
  pm.expect(pm.response.responseTime).to.be.below(500);
});

// JSON validation
pm.test("Has user data", function() {
  const json = pm.response.json();
  pm.expect(json).to.have.property('id');
  pm.expect(json).to.have.property('name');
});

// Header test
pm.test("Has content-type", function() {
  pm.response.to.have.header('Content-Type');
});
```

### Available APIs

#### pm.request
- `pm.request.url` - Request URL
- `pm.request.method` - HTTP method
- `pm.request.headers` - Headers object
- `pm.request.body` - Request body

#### pm.response
- `pm.response.code` - Status code
- `pm.response.status` - Status text
- `pm.response.headers` - Response headers
- `pm.response.json()` - Parse JSON body
- `pm.response.text()` - Get text body
- `pm.response.responseTime` - Time in ms

#### pm.variables
- `pm.variables.get(key)` - Get variable
- `pm.variables.set(key, value)` - Set variable

#### pm.environment
- `pm.environment.get(key)` - Get env variable
- `pm.environment.set(key, value)` - Set env variable

#### pm.globals
- `pm.globals.get(key)` - Get global variable
- `pm.globals.set(key, value)` - Set global variable

## Testing

### Assertions

Built-in assertion builders:
- **Status Code** - Equals, not equals, in range
- **Response Time** - Less than, greater than
- **Header** - Exists, equals, contains
- **Body** - Contains, equals, matches regex
- **JSON Path** - Extract and validate JSON
- **XML Path** - Extract and validate XML

### Test Groups

Organize tests into groups:
```javascript
pm.test.group("User validation", function() {
  pm.test("Has ID", () => {
    pm.expect(json.id).to.exist;
  });
  
  pm.test("Has email", () => {
    pm.expect(json.email).to.be.a('string');
  });
});
```

## Mock Servers

### Creating Mock Server

1. Select a collection
2. Click **Mock Server**
3. Configure port and routes
4. Start server

### Mock Responses

Define responses for each endpoint:
- Status code
- Headers
- Body (JSON, XML, etc.)
- Response delay

### Dynamic Mocks

Use scripts for dynamic responses:
```javascript
// Generate dynamic data
return {
  id: Math.random(),
  timestamp: Date.now(),
  data: generateRandomData()
};
```

## Workflows

### Creating Workflows

1. Click **New Workflow**
2. Add requests in sequence
3. Configure variable extraction
4. Set error handling

### Scheduling

Schedule workflows to run automatically:
- Cron expression: `0 */5 * * *` (every 5 minutes)
- Monitor API health
- Generate reports

## Protocol Support

### GraphQL

1. Select **GraphQL** protocol
2. Enter endpoint URL
3. Use introspection to load schema
4. Build query in editor
5. Add variables

### SOAP

1. Select **SOAP** protocol
2. Load WSDL file
3. Select operation
4. Fill parameters
5. Send request

### gRPC

1. Select **gRPC** protocol
2. Load .proto file
3. Select service and method
4. Fill message fields
5. Send request

### WebSockets

1. Select **WebSocket** protocol
2. Enter WS URL
3. Connect
4. Send/receive messages
5. View message log

## Settings

### General
- Theme (Light/Dark)
- Auto-save
- Request timeout
- Follow redirects

### Security
- SSL validation
- Proxy settings
- Certificate management

### Editor
- Font size
- Theme
- Key bindings

### Storage
- Database location
- Backup settings
- Export/import

## FAQ

### How do I import Postman collections?

1. Export from Postman as JSON
2. In LocalAPI, click **Import**
3. Select Postman JSON file
4. Collections will be converted

### Can I use LocalAPI offline?

Yes! LocalAPI is fully offline-capable. All data is stored locally.

### How do I backup my data?

1. Go to **Settings** → **Storage**
2. Click **Export All**
3. Save backup file
4. Restore with **Import All**

## Cache Management (v0.6.0)

### Overview

LocalAPI includes intelligent request caching to improve performance and reduce unnecessary API calls.

### Enabling Cache

1. Navigate to the **Cache** tab
2. Toggle **Enable Caching** on
3. Configure settings:
   - **TTL**: Time to live (1-60 minutes, default: 5)
   - **Max Size**: Maximum cache size (10-500 MB, default: 100)

### Cache Statistics

View real-time statistics:
- **Cache Hits**: Requests served from cache
- **Cache Misses**: Requests not in cache
- **Hit Rate**: Percentage of cached responses
- **Current Size**: Cache size in MB
- **Entry Count**: Number of cached entries

### Cache Operations

**Clear All Cache**
- Removes all cached responses
- Useful when testing API changes

**Clean Expired Entries**
- Removes only expired entries
- Keeps valid cache intact

**Invalidate by Pattern**
- Use regex to remove specific entries
- Example: `/api/users/.*` removes all user API cache

**Invalidate by Tags**
- Remove entries with specific tags
- Useful for grouped invalidation

### Per-Request Caching

Override global settings per request:
1. Open request settings
2. Set custom TTL or disable caching
3. Add cache tags for grouped invalidation

## Import/Export (v0.6.0)

### Supported Formats

- **JSON**: Full collection and request data
- **cURL**: Command-line compatible format

### Importing Data

1. Click **Import/Export** button (toolbar)
2. Select **Import** tab
3. Choose format or use auto-detect
4. Paste content or select file
5. Click **Import**

**Import JSON Collection:**
```json
{
  "name": "My API",
  "requests": [
    {
      "name": "Get Users",
      "method": "GET",
      "url": "https://api.example.com/users"
    }
  ]
}
```

**Import cURL Command:**
```bash
curl -X POST 'https://api.example.com/users' \
  -H 'Content-Type: application/json' \
  -d '{"name":"John Doe"}'
```

### Exporting Data

1. Click **Import/Export** button
2. Select **Export** tab
3. Choose collections to export
4. Select format (JSON or cURL)
5. Export to clipboard or file

**Export Options:**
- Single request
- Multiple requests
- Entire collection
- All collections

## Git Version Control (v0.6.0)

### Setting Up Git

1. Navigate to **Git** tab
2. Click **Initialize Repository**
3. .gitignore created automatically

### Making Commits

**Stage Files:**
1. View file status in Git panel
2. Click **+** button next to files to stage
3. Or click **Stage All** for all changes

**Commit Changes:**
1. Enter commit message (required)
2. Add description (optional)
3. Click **Commit**

### Branch Management

**Create Branch:**
1. Click **New Branch** button
2. Enter branch name
3. Choose to checkout immediately

**Switch Branches:**
- Select branch from dropdown
- Current branch shown in panel

**View History:**
- See commit log with pagination
- View commit details and changes

### Viewing Diffs

- **Unstaged Changes**: See what's modified
- **Staged Changes**: See what will be committed
- **File-specific Diffs**: Click on file to view

### Discarding Changes

1. Select files to discard
2. Click **Discard Changes**
3. Confirm action

**Note**: This cannot be undone!

## Plugin System (v0.6.0)

### Installing Plugins

1. Place plugin folder in `plugins/` directory
2. Navigate to **Plugins** tab
3. Click **Discover Plugins**
4. Enable the plugin

### Managing Plugins

**Enable/Disable:**
- Toggle switch next to plugin name
- Takes effect immediately

**Reload Plugin:**
- Click reload button
- Useful after plugin updates

**View Plugin Info:**
- Click on plugin name
- See description, version, permissions

### Plugin Permissions

Plugins may request permissions:
- **Network**: Make HTTP requests
- **Filesystem**: Read/write files
- **Database**: Access database
- **Storage**: Use plugin storage
- **Clipboard**: Access clipboard
- **Notifications**: Show notifications

### Developing Plugins

See [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md) for:
- Quick start tutorial
- Complete API reference
- Available hooks
- Best practices
- Example plugins

## PDF Reports (v0.6.0)

### Report Types

**Security Scan Report**
- Current security status
- Security findings
- Recommendations

**Vulnerability Scan Report**
- Detailed vulnerability assessment
- Severity levels
- Remediation steps

**Security Trends Report**
- Historical security analysis
- Trend charts
- Score progression

**Performance Trends Report**
- Performance metrics over time
- Response time trends
- Success rate analysis

### Generating Reports

1. Navigate to **Reports** tab
2. Select report type
3. Configure options:
   - **Title**: Report title
   - **Author**: Your name
   - **Date Range**: For trend reports
   - **Include Charts**: Visual data
   - **Include Summary**: Executive summary
   - **Include Details**: Detailed findings
4. Click **Generate Report**
5. Save PDF to desired location

### Report Options

**Charts:**
- Line charts for trends
- Bar charts for comparisons
- Pie charts for distributions
- Doughnut charts for breakdowns

**Customization:**
- Custom title and author
- Date range selection
- Toggle sections on/off
- Professional formatting

### Does LocalAPI support plugins?

Yes! v0.6.0 includes a complete plugin system. See [Plugin System](#plugin-system) above and [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md).

### How do I report bugs?

Open an issue on GitHub with:
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Version number

---

## Security Testing (v0.7.0) ⭐

### OWASP Top 10 Scanner

Run comprehensive security scans against your APIs:

1. Open **Security Runner** tab
2. Enter target URL
3. Select scan depth (quick/standard/deep)
4. Choose OWASP categories to test
5. Click **Run OWASP Scan**
6. Review findings with severity levels

**Scan Depths:**
- **Quick**: Fast scan, basic checks
- **Standard**: Comprehensive scan, recommended
- **Deep**: Thorough scan, all tests

### Fuzzing & Bomb Testing

Test API resilience with fuzzing:

1. Open **Fuzzing Tester** tab
2. Configure target endpoint
3. Select fuzzing types:
   - String fuzzing
   - Number fuzzing
   - Injection fuzzing
   - Bomb testing
4. Set intensity level
5. Click **Start Fuzzing**
6. Analyze crash reports and anomalies

### ZAP Proxy Integration

Integrate with OWASP ZAP for advanced testing:

1. Start OWASP ZAP locally
2. Open **ZAP Proxy** tab
3. Configure connection (host, port, API key)
4. Run spider scan to discover URLs
5. Execute active scan for vulnerabilities
6. Review alerts and generate reports

### Security Runner Dashboard

Unified interface for all security tests:

1. Open **Security Runner** tab
2. Select **Quick Scan** for all tests
3. Or choose individual tests
4. Configure per-test settings
5. Monitor real-time progress
6. Export consolidated findings

---

**Version:** 0.7.0  
**Last Updated:** October 23, 2025

For more help, see:
- [Quick Start Guide](QUICKSTART.md)
- [API Documentation](API.md)
- [Features Guide](FEATURES.md)
- [Git Integration Guide](GIT_INTEGRATION_GUIDE.md)
- [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md)
- [Reporting Guide](REPORTING_GUIDE.md)
