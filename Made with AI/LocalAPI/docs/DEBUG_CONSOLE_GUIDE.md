# Debug Console Guide

**Version:** 0.9.0  
**Last Updated:** October 24, 2025

Complete guide for using LocalAPI's Debug Console feature - a comprehensive logging and debugging tool for API development.

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Features](#features)
4. [User Interface](#user-interface)
5. [Filtering and Search](#filtering-and-search)
6. [Export Options](#export-options)
7. [Console Settings](#console-settings)
8. [Entry Types](#entry-types)
9. [Request Replay](#request-replay)
10. [Timeline Visualization](#timeline-visualization)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Overview

The Debug Console provides real-time visibility into all API operations in LocalAPI, similar to browser developer tools or Postman's console. It captures and displays:

- HTTP requests and responses
- WebSocket messages (sent/received)
- Server-Sent Events (SSE)
- Script console outputs (console.log, console.error, etc.)
- Errors and warnings

### Key Benefits

- **Real-time Monitoring** - See all API activity as it happens
- **Complete History** - Review past requests and responses
- **Advanced Filtering** - Find specific entries quickly
- **Export Capabilities** - Export logs for analysis or sharing
- **Performance Insights** - View timing and performance metrics
- **Request Replay** - Re-execute requests from the console

---

## Getting Started

### Accessing the Console

1. Open LocalAPI
2. Navigate to the **Console** tab in the main navigation
3. The console will automatically start logging all API operations

### First Steps

1. **Send a Request** - Execute any HTTP request from LocalAPI
2. **View in Console** - See the request and response logged in real-time
3. **Inspect Details** - Click on any entry to view full details
4. **Try Filtering** - Use the filter controls to narrow down entries

---

## Features

### 1. Console Panel UI (Postman-like Console) ✅

Professional console interface with real-time logging display:
- Virtual scrolling for performance with large datasets
- Color-coded entries based on status/type
- Expandable entry details
- Split-pane layout (entry list + details panel)

### 2. Real-time Request/Response Logging ✅

Automatic logging of all HTTP operations:
- Request details (method, URL, headers, body)
- Response details (status, headers, body, timing)
- Correlation between requests and responses
- Request ID linking

### 3. Console Filters ✅

Filter entries by multiple criteria:
- **Method** - GET, POST, PUT, DELETE, etc.
- **Status Code** - 2xx, 3xx, 4xx, 5xx
- **Type** - Request, Response, WebSocket, SSE, Script, Error
- **Time Range** - Filter by date/time
- **Error State** - Show only entries with errors

### 4. Console Search Functionality ✅

Full-text search across all entry fields:
- URL matching
- Method matching
- Error message search
- Script output search
- Case-insensitive searching

### 5. Request Replay from Console ✅

One-click request replay:
- Click any request entry
- Click "Replay Request" button
- Request is re-executed with original parameters

### 6. Network Timeline Visualization ✅

Visual breakdown of request timing:
- DNS lookup time
- TCP connection time
- SSL handshake time
- Request send time
- Response receive time
- Total duration

### 7. Error Highlighting and Details ✅

Automatic error detection and highlighting:
- Red border for error entries
- Error icons (⚠️, ❌)
- Detailed error messages
- Stack traces (when available)
- Error context (URL, method, etc.)

### 8. Console Export (Logs to File) ✅

Export console logs in multiple formats:
- **JSON** - Complete data export
- **CSV** - Spreadsheet-compatible format
- **HAR** - HTTP Archive format (industry standard)

### 9. Console Clear/Persist Options ✅

Control console data:
- **Clear All** - Remove all entries
- **Clear Older Than** - Remove entries before a timestamp
- **Persistence Toggle** - Save/don't save to database
- **Auto-save** - Automatic persistence across sessions

### 10. Script console.log() Output Display ✅

Capture script outputs:
- `console.log()` - Info messages
- `console.warn()` - Warnings
- `console.error()` - Errors
- `console.info()` - Information
- All outputs linked to parent request

### 11. Performance Metrics in Console ✅

Performance statistics:
- Request duration (ms)
- Response size (bytes)
- Average response time
- Request/response counts
- Error rate

### 12. WebSocket/SSE Message Logging ✅

Real-time protocol logging:
- **WebSocket** - Sent/received messages with direction indicators
- **SSE** - Event stream messages with event types
- Connection IDs for tracking
- Message content display

### 13. HTTP/2 Frame Logging ✅

Advanced protocol support:
- Protocol detection (HTTP/1.1, HTTP/2)
- Frame-level logging (when applicable)
- Protocol-specific metadata

---

## User Interface

### Toolbar

```
┌──────────────────────────────────────────────────────────────┐
│ [⏸ Pause] [🗑 Clear] [💾 Export] [⚙ Settings] [🔍 Search...] │
└──────────────────────────────────────────────────────────────┘
```

**Buttons:**
- **Pause/Resume** - Stop/start logging new entries
- **Clear** - Remove all console entries
- **Export** - Export entries to file
- **Settings** - Configure console options
- **Search** - Full-text search field

### Entry List

Displays all console entries with:
- **Timestamp** - When the entry was logged
- **Type Icon** - Visual indicator of entry type
- **Method** - HTTP method (GET, POST, etc.)
- **URL** - Request/response URL
- **Status** - HTTP status code with color coding
- **Duration** - Request duration (if applicable)
- **Cached** - Cache hit indicator

### Details Panel

Shows complete information for selected entry:
- **Overview Tab** - Basic information
- **Headers Tab** - HTTP headers (request/response)
- **Body Tab** - Request/response body
- **Timeline Tab** - Timing visualization

### Status Bar

```
Total: 1,234  |  Errors: 5  |  Avg: 145ms
```

Real-time statistics about console entries.

---

## Filtering and Search

### Method Filtering

Filter by HTTP method:
```
[Method ▾] → [GET] [POST] [PUT] [DELETE] [PATCH]
```

### Status Code Filtering

Filter by response status:
```
[Status ▾] → [2xx Success] [3xx Redirect] [4xx Client Error] [5xx Server Error]
```

### Type Filtering

Filter by entry type:
```
[Type ▾] → [Request] [Response] [WebSocket] [SSE] [Script] [Error]
```

### Time Range Filtering

Filter by time period:
```
[Time ▾] → [Last Hour] [Today] [Last 7 Days] [Custom Range]
```

### Combined Filtering

Apply multiple filters simultaneously for precise results:
```javascript
// Example: Show all failed POST requests from today
Method: POST
Status: 4xx, 5xx
Time: Today
```

### Search

Full-text search across all fields:
- Type search query in search box
- Matches: URL, method, error messages, script output, body content
- Case-insensitive
- Real-time filtering as you type

---

## Export Options

### JSON Export

Complete data export with all fields:

```json
[
  {
    "id": "entry-123",
    "timestamp": 1698765432100,
    "type": "request",
    "method": "GET",
    "url": "https://api.example.com/users",
    "headers": { "Authorization": "Bearer token" },
    "body": null,
    "duration": 145
  },
  {
    "id": "entry-124",
    "timestamp": 1698765432245,
    "type": "response",
    "status": 200,
    "statusText": "OK",
    "headers": { "Content-Type": "application/json" },
    "body": { "users": [...] },
    "duration": 145
  }
]
```

**Use Cases:**
- Data analysis
- Backup and restore
- Integration with other tools
- Programmatic processing

### CSV Export

Spreadsheet-compatible format:

```csv
ID,Timestamp,Type,Method,URL,Status,Duration
entry-123,2023-10-31 10:30:45,request,GET,/api/users,,
entry-124,2023-10-31 10:30:45,response,GET,/api/users,200,145
```

**Use Cases:**
- Excel analysis
- Reporting
- Data visualization
- Sharing with non-technical stakeholders

### HAR Export

HTTP Archive format (industry standard):

```json
{
  "log": {
    "version": "1.2",
    "creator": {
      "name": "LocalAPI",
      "version": "0.9.0"
    },
    "entries": [
      {
        "startedDateTime": "2023-10-31T10:30:45.000Z",
        "time": 145,
        "request": {
          "method": "GET",
          "url": "https://api.example.com/users",
          "httpVersion": "HTTP/1.1",
          "headers": [...]
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "headers": [...],
          "content": {...}
        }
      }
    ]
  }
}
```

**Use Cases:**
- Browser DevTools import
- Performance analysis tools
- Network debugging
- Standard format sharing

---

## Console Settings

Access via **Settings** button in toolbar.

### Persistence

**Enable/Disable Database Persistence**
- **Enabled**: Logs saved to database, persist across sessions
- **Disabled**: Logs kept in memory only, cleared on restart

### Max Entries

**Maximum Console Entries (1,000 - 50,000)**
- Controls memory usage
- Older entries automatically removed (circular buffer)
- Default: 10,000 entries

### Auto-Scroll

**Automatic Scrolling**
- Enabled: Console auto-scrolls to newest entry
- Disabled: Manual scrolling control
- Toggle in toolbar

### Pause Logging

**Pause/Resume**
- Pause: Stop logging new entries (analyze current data)
- Resume: Continue logging
- Toggle in toolbar

---

## Entry Types

### Request Entries

Logged when HTTP request is sent:

```
10:30:45 GET /api/users 
```

**Information:**
- Method (GET, POST, etc.)
- URL
- Headers
- Body (if applicable)
- Request ID (for correlation)

### Response Entries

Logged when HTTP response is received:

```
10:30:45 GET /api/users 200 OK (145ms) [cached]
```

**Information:**
- Status code
- Status text
- Headers
- Body
- Duration
- Cached indicator
- Request ID (links to request)

### WebSocket Entries

Logged for WebSocket messages:

```
10:30:46 WS → Message sent (25 bytes)
10:30:46 WS ← Message received (180 bytes)
```

**Information:**
- Direction (sent/received)
- Message content
- Connection ID
- Timestamp

### SSE Entries

Logged for Server-Sent Events:

```
10:30:47 SSE update: {"data": "new content"}
```

**Information:**
- Event type
- Event data
- Connection ID
- Event ID (if provided)

### Script Entries

Logged for script console outputs:

```
10:30:48 Script: console.log("User authenticated")
10:30:49 Script: [WARN] Token expires in 5 minutes
10:30:50 Script: [ERROR] Assertion failed
```

**Information:**
- Log level (log, info, warn, error)
- Output message
- Request ID (if associated)

### Error Entries

Logged for errors:

```
10:30:51 ERROR: Network timeout after 30000ms
```

**Information:**
- Error message
- URL (if applicable)
- Method (if applicable)
- Request ID (if applicable)
- Log level: error

---

## Request Replay

### How to Replay

1. **Find the Request** - Locate the request entry in console
2. **Select Entry** - Click on the request entry
3. **Click Replay** - Click "Replay Request" button in details panel
4. **Watch Execution** - New request/response logged to console

### Use Cases

- **Debugging** - Re-execute failed requests
- **Testing** - Verify fixes without manual setup
- **Analysis** - Compare results across executions
- **Development** - Quick iteration on API calls

---

## Timeline Visualization

### Visual Timeline

Color-coded bar chart showing request phases:

```
DNS ████ TCP ████ SSL ████ Request ████████ Response ████████████
|----|----|----|----|--------|----------------------|
0ms  50ms 100ms 150ms       500ms                  1500ms
```

### Phases

- **DNS** (Green) - Domain name resolution
- **TCP** (Blue) - TCP connection establishment
- **SSL** (Purple) - SSL/TLS handshake
- **Request** (Orange) - Request sending
- **Response** (Red) - Response receiving

### Breakdown Table

```
DNS:      50ms  (3.3%)
TCP:      50ms  (3.3%)
SSL:      50ms  (3.3%)
Request:  350ms (23.3%)
Response: 1000ms (66.7%)
─────────────────────
Total:    1500ms
```

---

## Best Practices

### 1. Use Filters Effectively

- Start with broad filters, narrow down as needed
- Combine multiple filter criteria for precision
- Save common filter combinations

### 2. Manage Console Size

- Set appropriate max entries limit
- Clear old entries periodically
- Export important logs before clearing

### 3. Leverage Search

- Use search for quick lookups
- Search by URL patterns
- Search error messages for debugging

### 4. Export Regularly

- Export logs for analysis
- Keep HAR files for performance review
- Share CSV exports with team

### 5. Monitor Performance

- Watch average response times
- Track error rates
- Identify slow endpoints

### 6. Use Request Replay

- Debug failed requests quickly
- Verify API changes
- Test edge cases

---

## Troubleshooting

### Console Not Showing Entries

**Problem:** No entries appear in console

**Solutions:**
1. Check if logging is paused (click Play button)
2. Verify filters aren't too restrictive
3. Try clearing all filters
4. Restart LocalAPI

### Slow Console Performance

**Problem:** Console becomes slow with many entries

**Solutions:**
1. Reduce max entries limit
2. Clear old entries
3. Disable persistence temporarily
4. Filter to reduce displayed entries

### Export Fails

**Problem:** Export button doesn't work

**Solutions:**
1. Check disk space
2. Verify write permissions
3. Try different export format
4. Clear entries and try again

### Missing Request/Response Pairs

**Problem:** Request logged but no response

**Possible Causes:**
1. Network timeout
2. Connection error
3. Server not responding
4. Check error entries for details

### Persistence Not Working

**Problem:** Logs don't persist across restarts

**Solutions:**
1. Enable persistence in settings
2. Check database file permissions
3. Verify disk space
4. Check error logs

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Focus search field |
| `Ctrl+K` | Clear console |
| `Ctrl+E` | Export console |
| `Ctrl+P` | Pause/resume logging |
| `Ctrl+R` | Replay selected request |
| `↑/↓` | Navigate entries |
| `Enter` | View entry details |
| `Esc` | Close details panel |

---

## API Reference

### JavaScript API

```javascript
// Get console entries
const entries = await window.electronAPI.console.getEntries(filters, limit, offset);

// Search entries
const results = await window.electronAPI.console.searchEntries(query);

// Clear console
await window.electronAPI.console.clearEntries();

// Export console
const data = await window.electronAPI.console.exportEntries({
  format: 'json', // or 'csv', 'har'
  includeHeaders: true,
  includeBody: true,
});

// Get statistics
const stats = await window.electronAPI.console.getStats();

// Pause/resume
await window.electronAPI.console.setPaused(true);
const isPaused = await window.electronAPI.console.isPaused();
```

---

## FAQ

**Q: How long are console entries kept?**  
A: Depends on settings. With persistence enabled, entries are kept until manually cleared or max limit reached. Without persistence, entries are lost on restart.

**Q: Can I filter by multiple methods at once?**  
A: Yes, use the method filter dropdown and select multiple methods.

**Q: What's the maximum number of entries?**  
A: Configurable from 1,000 to 50,000. Default is 10,000.

**Q: Are WebSocket messages logged in real-time?**  
A: Yes, both sent and received WebSocket messages are logged immediately.

**Q: Can I export only filtered entries?**  
A: Yes, exports respect current filter settings.

**Q: Does the console impact performance?**  
A: Minimal impact. Virtual scrolling and circular buffer ensure good performance even with thousands of entries.

**Q: Can I customize console colors?**  
A: Currently no, but planned for future release.

**Q: How do I search within request/response bodies?**  
A: The search function includes body content. Just type your query.

---

## See Also

- [User Guide](USER_GUIDE.md) - General LocalAPI usage
- [API Documentation](API.md) - IPC API reference
- [Scripting Guide](SCRIPTING.md) - Script console.log() integration
- [Network Timeline Guide](NETWORK_TIMELINE.md) - Timing visualization

---

**Version:** 0.9.0  
**Last Updated:** October 24, 2025
