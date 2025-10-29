# Phase 0.9.0 - Debug Console Implementation Plan

**Version:** 0.9.0  
**Feature:** Debug Console (Postman-like)  
**Status:** Planning  
**Date:** October 24, 2025

---

## Overview

Implementing a comprehensive Debug Console feature similar to Postman's console, providing real-time request/response logging, filtering, search, replay, and network timeline visualization.

## TODO Tasks (13 items - ALL REQUIRED)

From TODO.md lines 233-247:

1. ✅ Console panel UI (Postman-like console)
2. ✅ Real-time request/response logging
3. ✅ Console filters (by method, status, time)
4. ✅ Console search functionality
5. ✅ Request replay from console
6. ✅ Network timeline visualization
7. ✅ Error highlighting and details
8. ✅ Console export (logs to file)
9. ✅ Console clear/persist options
10. ✅ Script console.log() output display
11. ✅ Performance metrics in console
12. ✅ WebSocket/SSE message logging in console
13. ✅ HTTP/2 frame logging

---

## Architecture Design

### 1. Backend Service: ConsoleService

**File:** `src/main/services/ConsoleService.ts`  
**Estimated Lines:** ~450 lines

#### Responsibilities
- Store console log entries in memory (with max limit)
- Persist logs to SQLite for history
- Provide filtering, searching, and sorting
- Export logs to various formats (JSON, CSV, HAR)
- Integration points for all services

#### Key Methods
```typescript
class ConsoleService {
  // Logging
  logRequest(request, metadata): ConsoleEntry
  logResponse(response, request, metadata): void
  logWebSocketMessage(message, direction, connectionId): void
  logSSEMessage(event, connectionId): void
  logScriptOutput(output, type, requestId): void
  logError(error, context): void
  
  // Retrieval
  getEntries(filters?, limit?, offset?): ConsoleEntry[]
  getEntry(id): ConsoleEntry | null
  searchEntries(query): ConsoleEntry[]
  
  // Management
  clearEntries(olderThan?): void
  deleteEntry(id): boolean
  exportEntries(format, filters?): string | Buffer
  
  // Persistence
  saveToDisk(): Promise<void>
  loadFromDisk(): Promise<void>
  setPersistence(enabled): void
}
```

#### Data Model
```typescript
interface ConsoleEntry {
  id: string;
  timestamp: number;
  type: 'request' | 'response' | 'websocket' | 'sse' | 'script' | 'error';
  
  // Request/Response data
  method?: string;
  url?: string;
  status?: number;
  statusText?: string;
  headers?: Record<string, string>;
  body?: any;
  
  // Timing
  duration?: number;
  timings?: {
    dns?: number;
    tcp?: number;
    ssl?: number;
    request?: number;
    response?: number;
    total: number;
  };
  
  // Metadata
  requestId?: string;
  protocol?: string;
  cached?: boolean;
  error?: string;
  
  // WebSocket/SSE
  direction?: 'sent' | 'received';
  connectionId?: string;
  eventType?: string;
  
  // Script output
  scriptOutput?: string;
  logLevel?: 'log' | 'info' | 'warn' | 'error';
}
```

---

### 2. UI Component: DebugConsole

**File:** `src/renderer/components/DebugConsole.tsx`  
**Estimated Lines:** ~600 lines

#### Features
- **Real-time log display** with virtual scrolling for performance
- **Filter panel** - Method, status code, protocol, time range, type
- **Search bar** - Full-text search across all fields
- **Entry details panel** - Expandable view with all data
- **Toolbar** - Clear, export, pause/resume, settings
- **Timeline view** - Visual timeline of requests
- **Error highlighting** - Red for errors, yellow for warnings
- **Request replay** - One-click replay from console
- **Auto-scroll toggle** - Stick to bottom or manual scroll
- **Persist toggle** - Save logs across sessions

#### Layout
```
┌─────────────────────────────────────────────────────────────┐
│  [🗑 Clear] [⏸ Pause] [💾 Export] [⚙ Settings]  [🔍 Search]│
├─────────────────────────────────────────────────────────────┤
│  Filters: [Method ▾] [Status ▾] [Type ▾] [Time ▾]          │
├─────────────────────────────────────────────────────────────┤
│  📋 Console Entries (Virtual List)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 10:30:45 GET /api/users 200 OK (245ms)              │   │
│  │ 10:30:46 POST /api/login 401 Unauthorized (123ms)  │   │
│  │ 10:30:47 WS ← Message received (12 bytes)           │   │
│  │ 10:30:48 Script: console.log("Hello")               │   │
│  │ 10:30:49 GET /api/data 200 OK (89ms) [cached]      │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  📊 Entry Details (when selected)                           │
│  [Request] [Response] [Headers] [Timeline] [Script Output]  │
└─────────────────────────────────────────────────────────────┘
```

---

### 3. Timeline Visualization Component

**File:** `src/renderer/components/NetworkTimeline.tsx`  
**Estimated Lines:** ~350 lines

#### Features
- Visual timeline showing request phases (DNS, TCP, SSL, Request, Response)
- Color-coded bars for different phases
- Tooltip showing detailed timing breakdown
- Zoom and pan controls
- Export timeline as image

#### Timeline Phases
```
DNS ████ TCP ████ SSL ████ Request ████████ Response ████████████
|----|----|----|----|--------|----------------------|
0ms  50ms 100ms 150ms       500ms                  1500ms
```

---

### 4. Integration Points

#### RequestService Integration
**File:** `src/main/services/RequestService.ts` (modify)

Add console logging:
```typescript
// Before request
consoleService.logRequest(config, { type: 'http' });

// After response
consoleService.logResponse(response, request, {
  duration,
  timings: calculateTimings(response),
  cached: response.cached
});

// On error
consoleService.logError(error, { requestId, url });
```

#### WebSocketService Integration
**File:** `src/main/services/WebSocketService.ts` (modify)

```typescript
// On message sent
consoleService.logWebSocketMessage(message, 'sent', connectionId);

// On message received
consoleService.logWebSocketMessage(message, 'received', connectionId);
```

#### SSEService Integration
**File:** `src/main/services/SSEService.ts` (modify)

```typescript
// On event received
consoleService.logSSEMessage(event, connectionId);
```

#### ScriptService Integration
**File:** `src/main/services/ScriptService.ts` (modify)

Override console methods in VM:
```typescript
const consoleOverride = {
  log: (...args) => consoleService.logScriptOutput(args.join(' '), 'log', requestId),
  info: (...args) => consoleService.logScriptOutput(args.join(' '), 'info', requestId),
  warn: (...args) => consoleService.logScriptOutput(args.join(' '), 'warn', requestId),
  error: (...args) => consoleService.logScriptOutput(args.join(' '), 'error', requestId)
};
```

---

## Implementation Steps

### Step 1: ConsoleService Backend (Phase 1)
- [ ] Create ConsoleService.ts with core logging methods
- [ ] Implement in-memory storage with circular buffer (max 10,000 entries)
- [ ] Add SQLite schema for persistent storage
- [ ] Implement filtering and search logic
- [ ] Add export functionality (JSON, CSV, HAR formats)
- [ ] Write unit tests (20+ tests)

### Step 2: IPC Integration (Phase 1)
- [ ] Create IPC handlers for console operations
- [ ] Add preload API for console
- [ ] Update type definitions

### Step 3: DebugConsole UI Component (Phase 2)
- [ ] Create DebugConsole.tsx with basic layout
- [ ] Implement virtual scrolling for performance
- [ ] Add filter controls (method, status, type, time)
- [ ] Add search functionality
- [ ] Implement entry details panel
- [ ] Add toolbar actions (clear, pause, export)
- [ ] Add auto-scroll toggle
- [ ] Add persist toggle

### Step 4: NetworkTimeline Component (Phase 2)
- [ ] Create NetworkTimeline.tsx
- [ ] Implement timeline visualization
- [ ] Add tooltip with timing details
- [ ] Add zoom/pan controls
- [ ] Add export to image functionality

### Step 5: Service Integration (Phase 3)
- [ ] Integrate with RequestService
- [ ] Integrate with WebSocketService
- [ ] Integrate with SSEService
- [ ] Integrate with ScriptService
- [ ] Add HTTP/2 frame logging (if supported)
- [ ] Test all integration points

### Step 6: Advanced Features (Phase 4)
- [ ] Implement request replay from console
- [ ] Add error highlighting with details
- [ ] Add performance metrics display
- [ ] Add console settings (max entries, persistence, etc.)
- [ ] Implement export to HAR format
- [ ] Add keyboard shortcuts

### Step 7: Testing (Phase 5)
- [ ] Unit tests for ConsoleService (25+ tests)
- [ ] Unit tests for DebugConsole component (20+ tests)
- [ ] Unit tests for NetworkTimeline (15+ tests)
- [ ] Integration tests for logging flows (15+ tests)
- [ ] E2E tests for console workflows (10+ tests)
- [ ] Performance tests with large datasets

### Step 8: Documentation (Phase 6)
- [ ] Create DEBUG_CONSOLE_GUIDE.md
- [ ] Update README.md with console feature
- [ ] Update CHANGELOG.md
- [ ] Update STATUS.md
- [ ] Update TODO.md (mark all 13 items complete)
- [ ] Update API.md with new IPC handlers
- [ ] Update USER_GUIDE.md with console usage

---

## Files to Create

### New Files (11 files)
1. `src/main/services/ConsoleService.ts` (~450 lines)
2. `src/renderer/components/DebugConsole.tsx` (~600 lines)
3. `src/renderer/components/NetworkTimeline.tsx` (~350 lines)
4. `src/renderer/components/ConsoleFilterPanel.tsx` (~200 lines)
5. `src/renderer/components/ConsoleEntryDetails.tsx` (~250 lines)
6. `tests/unit/ConsoleService.test.ts` (~350 lines)
7. `tests/unit/DebugConsole.test.ts` (~300 lines)
8. `tests/integration/console-integration.test.ts` (~400 lines)
9. `tests/e2e/console.e2e.test.ts` (~250 lines)
10. `docs/DEBUG_CONSOLE_GUIDE.md` (~600 lines)
11. `commits/phase_0.9.0_debug_console.bat`

### Files to Modify (8 files)
1. `src/main/services/RequestService.ts` - Add console logging
2. `src/main/services/WebSocketService.ts` - Add console logging
3. `src/main/services/SSEService.ts` - Add console logging
4. `src/main/services/ScriptService.ts` - Override console methods
5. `src/main/ipc/handlers.ts` - Add console IPC handlers
6. `src/preload/index.ts` - Add console API
7. `src/renderer/App.tsx` - Add console tab
8. `src/main/services/DatabaseService.ts` - Add console_entries table

---

## Database Schema Addition

```sql
CREATE TABLE IF NOT EXISTS console_entries (
  id TEXT PRIMARY KEY,
  timestamp INTEGER NOT NULL,
  type TEXT NOT NULL,
  method TEXT,
  url TEXT,
  status INTEGER,
  status_text TEXT,
  headers TEXT,
  body TEXT,
  duration INTEGER,
  timings TEXT,
  request_id TEXT,
  protocol TEXT,
  cached INTEGER,
  error TEXT,
  direction TEXT,
  connection_id TEXT,
  event_type TEXT,
  script_output TEXT,
  log_level TEXT,
  created_at INTEGER NOT NULL
);

CREATE INDEX idx_console_timestamp ON console_entries(timestamp);
CREATE INDEX idx_console_type ON console_entries(type);
CREATE INDEX idx_console_request_id ON console_entries(request_id);
CREATE INDEX idx_console_status ON console_entries(status);
```

---

## Estimated Metrics

| Metric | Estimate |
|--------|----------|
| **Total Lines of Code** | ~3,500 lines |
| **New Services** | 1 (ConsoleService) |
| **New UI Components** | 5 components |
| **IPC Handlers** | 12 handlers |
| **Unit Tests** | 60+ tests |
| **Integration Tests** | 15+ tests |
| **E2E Tests** | 10+ tests |
| **Documentation** | 600+ lines |
| **Implementation Time** | Full implementation |

---

## Success Criteria

- ✅ All 13 TODO items implemented and working
- ✅ Real-time logging of all HTTP/WebSocket/SSE/Script activities
- ✅ Filtering by method, status, type, time range
- ✅ Full-text search across all log entries
- ✅ Request replay functionality
- ✅ Network timeline visualization
- ✅ Export to JSON, CSV, and HAR formats
- ✅ Script console.log() output captured and displayed
- ✅ Performance metrics shown in console
- ✅ Error highlighting with detailed information
- ✅ All tests passing (85+ tests)
- ✅ Complete documentation
- ✅ No performance degradation with large datasets (10,000+ entries)

---

## Next Steps After Completion

After Debug Console is 100% complete, move to next feature in order:
1. ✅ Debug Console (current)
2. ⏳ Create API Specification from Requests
3. ⏳ API Publishing
4. ⏳ Settings & Configuration
5. ⏳ Tab System Redesign
6. ⏳ UI/UX Overhaul
7. ⏳ Testing & Documentation

---

**Status:** Ready to begin implementation  
**Next Action:** Create ConsoleService.ts
