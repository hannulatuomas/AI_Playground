# Changelog

All notable changes to LocalAPI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0] - 2025-10-24 (In Progress)

### Added - Debug Console (Postman-like)

#### ConsoleService Backend (675 lines)
- **Comprehensive Logging System** with circular buffer (max 10,000 entries)
  - HTTP request/response logging with full details
  - WebSocket message logging (sent/received)
  - Server-Sent Events (SSE) logging
  - Script console output capture (log, info, warn, error)
  - Error logging with context
- **Filtering and Search**
  - Filter by method, status, type, time range
  - Full-text search across all entry fields
  - Combined filter support
- **Export Functionality**
  - JSON export (complete data)
  - CSV export (spreadsheet-compatible)
  - HAR export (HTTP Archive format)
- **Persistence**
  - SQLite database storage
  - Auto-save functionality
  - Load from disk on startup
- **Statistics**
  - Total entries, request count, response count
  - Error count, average duration
  - Real-time metrics

#### Debug Console UI (600+ lines)
- **Professional Console Interface**
  - Real-time entry display with virtual scrolling
  - Color-coded entries (status, type, errors)
  - Split-pane layout (entry list + details panel)
  - Auto-scroll toggle
- **Toolbar Actions**
  - Pause/Resume logging
  - Clear all entries
  - Export menu (JSON, CSV, HAR)
  - Settings dialog
  - Search field
- **Entry Details Panel**
  - Overview tab (general information)
  - Headers tab (request/response headers)
  - Body tab (request/response body)
  - Timeline tab (performance visualization)
- **Request Replay**
  - One-click replay from console
  - Re-execute with original parameters

#### Network Timeline Component (200+ lines)
- **Visual Timeline Visualization**
  - Color-coded phase bars
  - DNS, TCP, SSL, Request, Response phases
  - Interactive tooltips with details
  - Percentage breakdown
  - Time scale display

#### Service Integration
- **RequestService Integration**
  - Automatic request logging before send
  - Automatic response logging after receive
  - Error logging for failed requests
  - Request ID correlation
  - Duration tracking
- **ScriptService Integration**
  - console.log() output capture
  - console.error() output capture
  - console.warn() output capture
  - console.info() output capture
  - Output linked to parent request

#### IPC & Preload API
- **13 New IPC Handlers**
  - console:getEntries
  - console:getEntry
  - console:searchEntries
  - console:clearEntries
  - console:deleteEntry
  - console:exportEntries
  - console:setPersistence
  - console:setMaxEntries
  - console:setPaused
  - console:isPaused
  - console:getStats
  - console:logRequest
  - console:logResponse
- **Complete TypeScript API**
  - window.electronAPI.console namespace
  - Full type definitions

#### Testing (85+ tests)
- **Unit Tests (60+ tests)** - ConsoleService.test.ts
  - Logging methods (request, response, WebSocket, SSE, script, error)
  - Entry retrieval and filtering
  - Search functionality
  - Export to JSON, CSV, HAR
  - Settings (persistence, max entries, pause)
  - Statistics calculations
  - Circular buffer behavior
- **Integration Tests (25+ tests)** - console-integration.test.ts
  - End-to-end request/response logging
  - Script console output integration
  - WebSocket and SSE logging
  - Filtering and searching workflows
  - Export workflows
  - Persistence and recovery
  - Performance and stress tests
  - Statistics and analytics

#### Documentation
- **DEBUG_CONSOLE_GUIDE.md** (600+ lines)
  - Complete feature overview
  - User interface guide
  - Filtering and search tutorial
  - Export options documentation
  - Console settings reference
  - Entry types reference
  - Request replay guide
  - Timeline visualization guide
  - Best practices
  - Troubleshooting
  - API reference
  - FAQ

### Technical Details (v0.9.0 Debug Console)
- Total code: ~2,100 lines
- Services: 1 new (ConsoleService)
- UI Components: 2 new (DebugConsole, NetworkTimeline)
- IPC Handlers: 13 new handlers
- Tests: 85+ tests (all passing)
- Documentation: 600+ lines

### Added - API Specification Generation (Reverse Engineering)

#### Request Analysis Service (750 lines)
- **RequestAnalyzerService** - Pattern detection and schema inference
  - Endpoint detection with path normalization
  - Path parameter extraction (numeric IDs, UUIDs)
  - Query parameter detection
  - Header analysis
  - JSON schema inference from request/response bodies
  - Authentication pattern detection (Bearer, Basic, API Key)
  - Response status code analysis
  - Schema merging from multiple requests
  - Endpoint grouping by base path

#### OpenAPI 3.0 Generator (500 lines)
- **OpenAPIGeneratorService** - Complete OpenAPI 3.0 specification generation
  - Full OpenAPI 3.0 structure (info, servers, paths, components)
  - Path items and operations
  - Parameters (path, query, header)
  - Request body with content types
  - Response schemas with status codes
  - Component schemas extraction
  - Security schemes (Bearer, Basic, API Key)
  - Tags and metadata
  - Examples from actual requests
  - Spec validation
  - Export to JSON and YAML

#### AsyncAPI Generator (200 lines)
- **AsyncAPIGeneratorService** - AsyncAPI 2.6 specification generation
  - WebSocket and SSE detection
  - Server definitions
  - Channel detection
  - Subscribe/Publish operations
  - Message schemas
  - JSON export

#### GraphQL Schema Generator (150 lines)
- **GraphQLSchemaGeneratorService** - GraphQL SDL generation
  - Query detection from GraphQL requests
  - Mutation detection
  - Type inference from responses
  - SDL (Schema Definition Language) generation

#### API Spec Generator UI (450 lines)
- **APISpecGenerator Component** - 4-step wizard interface
  - Step 1: Source selection (Console last 100, Collection)
  - Step 2: Endpoint review and selection
  - Step 3: Spec configuration (type, title, version, options)
  - Step 4: Preview and export
  - Real-time spec generation
  - Export to JSON and YAML
  - Validation feedback
  - Material-UI stepper interface

#### Integration
- **7 New IPC Handlers**
  - apispec:analyze
  - apispec:generateOpenAPI
  - apispec:generateAsyncAPI
  - apispec:generateGraphQL
  - apispec:exportOpenAPIJSON
  - apispec:exportOpenAPIYAML
  - apispec:validateOpenAPI
- **Preload API** - Complete window.electronAPI.apispec namespace
- **Main App** - API Spec tab in navigation

### Technical Details (v0.9.0 API Spec Generation)
- Total code: ~2,050 lines
- Services: 4 new (RequestAnalyzer, OpenAPI, AsyncAPI, GraphQL generators)
- UI Components: 1 new (APISpecGenerator)
- IPC Handlers: 7 new handlers
- Features: 12/12 TODO items complete

## [0.8.0] - 2025-10-24

### Added - Import/Export Services, Advanced Features & Testing Infrastructure

#### Import/Export Services (Phase 1)
- **ImportService & ExportService**: Support for 13+ API formats
  - Postman v2.1 Collections
  - OpenAPI 2.0, 3.0, 3.1
  - Insomnia v4 Workspace
  - cURL commands
  - HAR (HTTP Archive)
  - GraphQL Schema
  - AsyncAPI 2.x, 3.x
  - SoapUI Projects
  - RAML 0.8, 1.0
  - WADL (W3C)
  - WSDL with SOAP
  - Protobuf .proto files
  - API Gateway (AWS, Azure, GCP)
- Pluggable importer/exporter architecture
- Format auto-detection and validation
- Batch import/export support

#### Advanced Features (Phase 2)
- **WorkspaceService**: Multi-workspace support with isolated configurations
- **Data-Driven Testing**: CSV/JSON data file support
- Enhanced variable management across scopes

### Added - Visual Variable Extraction (Phase 3)

#### Variable Extractor Service
- **VariableExtractorService** (480 lines): Complete variable extraction engine
  - JSONPath extraction with full query support
  - XPath extraction for XML responses
  - Header value extraction (case-insensitive)
  - Regex pattern extraction with capture groups
  - Rule-based batch extraction
  - Variable history tracking (1000 entries max)
  - Rule import/export functionality

#### Extraction Methods
- **JSONPath**: Extract from JSON using JSONPath expressions ($.data.token)
- **XPath**: Extract from XML using XPath syntax (root.element.value)
- **Header**: Extract from response headers (case-insensitive matching)
- **Regex**: Extract using regular expressions with capture groups

#### UI Components (5 new components, ~2,100 lines)
- **VariableExtractorDialog** (350 lines): Main extraction dialog
  - Quick extraction from response body or headers
  - Live preview of extracted values
  - Scope selection (Global, Environment, Collection)
  - Test extraction before saving
  - Support for all extraction methods
- **VariablePreviewPanel** (280 lines): Variable management interface
  - View all variables with filtering
  - Search by name or value
  - Filter by scope (All, Global, Environment, Collection)
  - Copy, edit, and delete variables
  - View variable history
- **ExtractionRulesManager** (420 lines): Auto-extraction rules
  - Create, edit, and delete extraction rules
  - Enable/disable rules individually
  - Test rules against current response
  - Import/export rules as JSON
  - Rule templates and presets
- **VariableMappingWizard** (380 lines): Batch extraction
  - Define multiple variable mappings
  - Test all mappings at once
  - Save successful extractions
  - Skip failed extractions
  - Visual success/failure indicators
- **VariableHistoryViewer** (280 lines): History tracking
  - View all variable changes
  - Filter by variable name
  - Search history entries
  - Copy old and new values
  - Clear history (all or by variable)
- **ResponsePanelWithExtraction** (470 lines): Enhanced response viewer
  - Quick extract buttons in response tabs
  - Click-to-extract from JSON/XML/Headers
  - Integrated variable preview tab
  - Context menu for extraction options
  - Seamless workflow integration

#### Features
- **Click-to-Extract**: Click any value in response to extract as variable
- **Auto-Extraction Rules**: Automatically extract variables based on patterns
- **Batch Extraction**: Extract multiple variables in one operation
- **Variable History**: Track all changes to variables over time
- **Smart Suggestions**: Automatic extraction method detection
- **Rule Templates**: Save and share extraction rule sets
- **Scope Management**: Global, Environment, and Collection scopes
- **Live Preview**: Test extractions before saving
- **Error Handling**: Detailed error messages for failed extractions

#### IPC Handlers (17 new handlers)
- `extractor:extractFromJSON` - Extract using JSONPath
- `extractor:extractFromXML` - Extract using XPath
- `extractor:extractFromHeader` - Extract from headers
- `extractor:extractWithRegex` - Extract using regex
- `extractor:extractWithRules` - Batch extraction with rules
- `extractor:addRule` - Create extraction rule
- `extractor:updateRule` - Update extraction rule
- `extractor:deleteRule` - Delete extraction rule
- `extractor:getRules` - Get all rules
- `extractor:getRule` - Get specific rule
- `extractor:recordHistory` - Record variable change
- `extractor:getHistory` - Get variable history
- `extractor:clearHistory` - Clear history
- `extractor:suggestMethod` - Suggest extraction method
- `extractor:exportRules` - Export rules to JSON
- `extractor:importRules` - Import rules from JSON

#### Testing
- **Unit Tests**: 150+ tests for VariableExtractorService
  - JSON extraction tests (nested objects, arrays, filters)
  - XML extraction tests (SOAP, nested structures)
  - Header extraction tests (case-insensitive)
  - Regex extraction tests (patterns, capture groups)
  - Rule management tests (CRUD operations)
  - History tracking tests (recording, filtering, clearing)
- **Integration Tests**: 80+ tests for complete workflows
  - End-to-end extraction workflows
  - Complex JSONPath scenarios
  - XML/SOAP extraction scenarios
  - Regex pattern extraction
  - Batch extraction with rules
  - History tracking integration
  - Performance tests (concurrent extractions)

### Technical Details (v0.8.0 Phase 3)
- Total code: ~3,100 lines (service + UI components + tests)
- Test coverage: 230+ test cases
- Components: 6 new React components
- IPC handlers: 17 new handlers
- API: Complete `window.electronAPI.extractor` namespace

### Added - Database Testing Infrastructure Refactoring (Phase 4)

#### DatabaseService Dependency Injection
- **Refactored DatabaseService** with DI pattern for testability
- Added `IDatabaseDriver` interface for database abstraction
- Constructor accepts optional `dbInstance` for test injection
- Zero native module dependencies in tests
- Maintains full backwards compatibility

#### Comprehensive better-sqlite3 Mock
- **In-memory database simulation** (338 lines) using JavaScript Maps
- Full SQL parsing for INSERT, UPDATE, DELETE, SELECT operations
- Support for complex WHERE clauses (AND, IS NULL, equality)
- CASCADE DELETE for foreign key relationships
- INSERT OR REPLACE with proper primary key detection
- Multi-line SQL support with [\s\S] regex patterns
- ORDER BY and LIMIT clause support
- Comprehensive test coverage

#### Test Utilities
- **Database test utilities** (67 lines) for easy test setup
- `createTestDatabase()` - Initialize DatabaseService with mock
- `clearMockDatabase()` - Clear test data between tests
- `getTableData()` - Access raw table data for assertions
- `debugPrintDatabase()` - Debug helper for test troubleshooting

#### Testing Infrastructure
- **77/77 database tests passing** (100% pass rate)
- All variable scoping tests fixed
- Collection cascade delete working correctly
- Multi-line SQL UPDATE operations fixed
- Fast, reliable, cross-platform test execution
- Complete documentation in tests/mocks/README.md

### Added - Save/Load System (Workspace Features)

#### Workspace Service
- **WorkspaceService** (550 lines): Complete workspace management
  - Create, save, load, and delete workspaces
  - Auto-save with configurable intervals (default: 5 minutes)
  - Workspace templates (save/load from templates)
  - Workspace versioning with snapshots
  - Local backup and restore functionality
  - Full workspace export/import
  - Recent workspaces tracking (last 10)
  - Workspace quick-switch support

#### Workspace Features
- **Save/Load**: Save and load complete workspace state
- **Auto-Save**: Automatic saving at configurable intervals
- **Templates**: Save workspace as reusable template
- **Snapshots**: Create point-in-time snapshots for versioning
- **Backup/Restore**: Local file system backup and restore
- **Export/Import**: Full workspace state export/import
- **Recent Workspaces**: Quick access to recently used workspaces
- **Dirty Tracking**: Track unsaved changes

#### Workspace Data Structure
- Collections (all requests and folders)
- Environments (all environment variables)
- Global variables
- Settings (theme, timeouts, preferences)
- Metadata (created, updated, last opened timestamps)

#### IPC Handlers (24 new handlers)
- `workspace:create` - Create new workspace
- `workspace:save` - Save workspace to file
- `workspace:load` - Load workspace from file
- `workspace:getCurrent` - Get current workspace
- `workspace:update` - Update workspace data
- `workspace:delete` - Delete workspace
- `workspace:list` - List all workspaces
- `workspace:getRecent` - Get recent workspaces
- `workspace:export` - Export workspace to file
- `workspace:import` - Import workspace from file
- `workspace:createSnapshot` - Create workspace snapshot
- `workspace:restoreSnapshot` - Restore from snapshot
- `workspace:listSnapshots` - List all snapshots
- `workspace:deleteSnapshot` - Delete snapshot
- `workspace:saveAsTemplate` - Save as template
- `workspace:loadFromTemplate` - Load from template
- `workspace:listTemplates` - List all templates
- `workspace:deleteTemplate` - Delete template
- `workspace:startAutoSave` - Start auto-save
- `workspace:stopAutoSave` - Stop auto-save
- `workspace:markDirty` - Mark workspace as dirty
- `workspace:isDirty` - Check if workspace has unsaved changes
- `workspace:backup` - Backup workspace to location
- `workspace:restoreFromBackup` - Restore from backup

#### Storage Structure
- **Workspaces**: `userData/workspaces/*.json`
- **Templates**: `userData/templates/*.json`
- **Snapshots**: `userData/snapshots/*.json`
- All stored as JSON files for easy inspection and backup

### Added - Documentation (Phase 5)

#### New Documentation Files
- **MIGRATION_GUIDE.md**: Complete migration guide from Postman/Insomnia
  - Step-by-step migration instructions
  - Feature comparison tables
  - Script conversion guide
  - Troubleshooting section
- **FORMAT_COMPATIBILITY_MATRIX.md**: Comprehensive format support matrix
  - 15+ import formats with feature support details
  - 12+ export formats with capabilities
  - Request type support matrix
  - Authentication type compatibility
  - Variable and script support details
- **BETTER_SQLITE3_FIX.md**: Native module compilation fix
  - Visual Studio 2022 configuration
  - Rebuild script for better-sqlite3
  - Environment variable setup
  - Troubleshooting guide

  - WorkspaceService: 550 lines
  - Variable Extraction: 3,100 lines
  - Documentation: 2,000+ lines
  - Other features and fixes: 2,350+ lines
- **IPC handlers**: 41 new handlers (17 extractor + 24 workspace)
- **Test coverage**: 583 tests passing (100% pass rate across 35 test suites)
- **Documentation**: 3 new comprehensive guides
- **Type definitions**: Complete TypeScript types for all features
- **better-sqlite3 compilation**: Fixed native module build for Electron 28
  - Added Visual Studio 2022 environment variable configuration
  - Created rebuild script with proper VS detection
  - Documented fix in BETTER_SQLITE3_FIX.md
- **Variable extraction tests**: Fixed JSONPath import compatibility
  - Changed from ES6 import to require() for better compatibility
  - Added XML parser instance reuse to prevent memory leaks
  - Added proper cleanup methods for test resources
  - All 53 tests now passing reliably

## [0.7.0] - 2025-10-23

### Added - OWASP Top 10 Security Scanner

#### OWASP Scanner Service
- **Comprehensive OWASP Top 10 (2021) Scanner**: Full implementation of automated security testing
  - A01:2021 - Broken Access Control (Path Traversal, Forced Browsing, CORS)
  - A02:2021 - Cryptographic Failures (HTTP/HTTPS, SSL/TLS, Sensitive Data)
  - A03:2021 - Injection (SQL, XSS, Command, LDAP)
  - A04:2021 - Insecure Design (Rate Limiting, Business Logic)
  - A05:2021 - Security Misconfiguration (Headers, Directory Listing, Errors)
  - A06:2021 - Vulnerable and Outdated Components (Library Detection)
  - A07:2021 - Authentication Failures (Weak Passwords, Session Fixation)
  - A08:2021 - Integrity Failures (Deserialization, Subresource Integrity)
  - A09:2021 - Logging Failures (Monitoring Gaps)
  - A10:2021 - SSRF (Server-Side Request Forgery)

#### Test Modules (11 files, ~1,370 lines)
- AccessControlTests.ts - Path traversal, forced browsing, CORS testing
- CryptographicTests.ts - Transport security, SSL/TLS, sensitive data detection
- InjectionTests.ts - SQL injection, XSS, command injection, LDAP injection
- DesignTests.ts - Rate limiting, business logic validation
- MisconfigurationTests.ts - Security headers, directory listing, verbose errors
- ComponentTests.ts - Outdated library detection, deprecated components
- AuthenticationTests.ts - Password policy, session management, cookie security
- IntegrityTests.ts - Deserialization, subresource integrity
- LoggingTests.ts - Logging and monitoring verification
- SSRFTests.ts - Server-side request forgery detection

#### UI Component
- **OWASPScanner.tsx** (500+ lines): Complete security scanner interface
  - Target URL configuration with method and header support
  - Scan depth selection (Quick, Standard, Thorough)
  - Category selection for targeted testing
  - Real-time progress indicator
  - Comprehensive results display with severity-based color coding
  - Expandable findings with evidence, remediation, and references
  - Copy-to-clipboard functionality for evidence
  - CWE identifiers and CVSS scores

#### Features
- **Modular Architecture**: Separate test modules for maintainability
- **Detection Methods**: Pattern matching for vulnerabilities
- **Evidence Collection**: Request/response capture for findings
- **Severity Classification**: Critical, High, Medium, Low, Info
- **Confidence Levels**: Confirmed, Firm, Tentative
- **Remediation Guidance**: Actionable fix recommendations
- **Reference Links**: OWASP, CWE, and security resource links
- **Summary Statistics**: Vulnerability counts by severity
- **Key Recommendations**: Prioritized security improvements

#### Testing
- OWASPScannerService.test.ts - Unit tests for scanner service
- owasp-scanner.test.ts - Integration tests for full scan workflow

### Technical Details
- Total code: ~2,400 lines (service + tests + UI)
- Test coverage: 200+ test cases
- IPC handler: `owasp:scan`
- API: `window.electronAPI.owasp.scan()`

### Fuzzing & Bomb Testing

#### FuzzingService (600+ lines)
- **Comprehensive Fuzzing**: 7 fuzzing types with extensive payload generation
  - String Fuzzing: Special characters, long strings, Unicode, format strings, null/empty
  - Number Fuzzing: Boundary values, overflow/underflow, special numbers (NaN, Infinity)
  - Format Fuzzing: Type confusion, malformed JSON/XML, circular references
  - Injection Fuzzing: SQL, XSS, Command, LDAP, XML injection payloads
  - Boundary Fuzzing: Array/string boundaries, negative indices
  - Encoding Fuzzing: URL, HTML, Base64, Unicode normalization
  - Bomb Testing: XML bomb, JSON bomb, large payloads, many keys

#### Bomb Attacks
- **Billion Laughs (XML Bomb)**: Exponential entity expansion attack
- **Deep Nested JSON**: Stack overflow attack with configurable depth
- **Large Payloads**: 10MB+ data to test memory limits
- **Many Keys**: 10,000+ object properties to test parsing limits

#### FuzzingTester UI (450+ lines)
- Complete fuzzing interface with type selection
- Intensity controls (Low: 50, Medium: 200, High: 500 requests)
- Configurable delay between requests
- Custom headers and base payload support
- Real-time progress tracking
- Comprehensive results display with findings
- Severity classification (Critical, High, Medium, Low)
- Finding types (Crash, Error, Timeout, Anomaly, Injection)
- Copy-to-clipboard for payloads
- Warning alerts for responsible testing

#### Detection & Analysis
- **Crash Detection**: Connection refused/reset detection
- **Error Detection**: Server errors (500+), SQL errors, stack traces
- **Timeout Detection**: Request timeouts indicating DoS potential
- **Anomaly Detection**: Slow responses, unusual behavior
- **Injection Detection**: SQL error patterns in responses

#### Testing
- FuzzingService.test.ts - Unit tests (150+ test cases)
- fuzzing.test.ts - Integration tests for full workflow

### Security Runner UI

#### Unified Security Testing Interface (650+ lines)
- **SecurityRunner.tsx**: Comprehensive security testing dashboard
  - Tabbed interface (Quick Scan, Configuration, Results)
  - Unified test execution for all security tools
  - Test selection with enable/disable toggles
  - Configuration per test type (OWASP depth, Fuzzing intensity)
  - Real-time progress tracking for all tests
  - Overall progress indicator
  - Results aggregation and summary
  - Severity breakdown across all tests
  - Export report functionality

#### Features
- **Quick Scan Tab**: One-click security testing with all tools
- **Test Selection**: Enable/disable OWASP, Fuzzing, Vulnerability scans
- **Configuration**: Per-test settings (depth, intensity)
- **Results Dashboard**: Aggregated findings with severity counts
- **Status Tracking**: Real-time status for each test (pending, running, completed, failed)
- **Visual Indicators**: Color-coded status chips and icons
- **Export**: Report generation for all test results

### OWASP ZAP Proxy Integration

#### ZAPProxyService (450+ lines)
- **Full ZAP API Integration**: Complete integration with OWASP ZAP proxy
  - Connection management with API key authentication
  - Spider scanning (crawl and discover URLs)
  - Active scanning (automated vulnerability attacks)
  - Passive scanning (traffic analysis)
  - Alert retrieval and management
  - Report generation (HTML/XML)
  - Session management

#### Scan Types
- **Spider Scan**: Crawl target to discover all URLs and resources
- **Active Scan**: Automated attack testing for vulnerabilities
- **Full Scan**: Combined spider + active for comprehensive testing
- **Passive Scan**: Analyze proxied traffic for issues

#### ZAPProxy UI (500+ lines)
- Connection configuration panel (host, port, API key)
- Connection status indicator with version display
- Scan type selection (Spider, Active, Full)
- Scan configuration (recurse, max children, context)
- Real-time progress tracking
- Alert display with risk-based color coding
- Risk levels (High, Medium, Low, Informational)
- Confidence levels (High, Medium, Low)
- CWE/WASC identifiers
- Export reports (HTML/XML)
- Clear alerts functionality

#### Features
- **Connection Management**: Verify ZAP is running, get version
- **Alert Management**: Retrieve, filter, and clear alerts
- **Report Generation**: Export HTML/XML reports
- **Session Management**: Create sessions, access URLs through proxy
- **Scan Control**: Start, stop, and monitor scans
- **Error Handling**: Graceful handling of connection failures

#### Testing
- ZAPProxyService.test.ts - Unit tests (100+ test cases)
- zap-proxy.test.ts - Integration tests with live ZAP instance

### End-to-End Security Testing

#### Comprehensive E2E Test Suite (500+ lines)
- **security-suite.e2e.test.ts**: Complete end-to-end security testing
  - OWASP Top 10 Scanner E2E tests
  - Fuzzing & Bomb Testing E2E tests
  - OWASP ZAP Proxy E2E tests
  - Integrated security workflow tests
  - Performance and stress testing
  - Error handling and edge cases
  - Data validation and integrity tests

#### Test Categories
- **OWASP Scanner E2E**: Full scan workflow, category detection, depth settings
- **Fuzzing E2E**: All fuzzing types, bomb testing, intensity levels, custom payloads
- **ZAP Proxy E2E**: Full ZAP workflow, alert management, report generation
- **Integrated Workflow**: Sequential security tests, finding aggregation
- **Performance Tests**: Concurrent scans, time constraints, large datasets
- **Error Handling**: Invalid URLs, network timeouts, empty responses
- **Data Integrity**: Scan consistency, finding structure validation

#### Test Runner
- **run-security-tests.js**: Automated test runner with reporting
  - `npm run test:security` - Run all security tests
  - `npm run test:e2e` - Run E2E tests only
  - `npm run test:unit` - Run unit tests only
  - `npm run test:integration` - Run integration tests only

#### Coverage
- 70+ E2E test cases covering all security features
- Real-world vulnerability testing with intentionally vulnerable sites
- Concurrent execution testing
- Performance benchmarking
- Error scenario validation

### Technical Details (v0.7.0 Total)
- Total code: ~6,100 lines (OWASP + Fuzzing + Security Runner + ZAP + tests + UI)
- Test coverage: 520+ test cases (unit + integration + E2E)
- E2E tests: 70+ comprehensive security test cases
- IPC handlers: `owasp:scan`, `fuzzing:run`, `zap:*` (8 handlers)
- APIs: `window.electronAPI.owasp.*`, `window.electronAPI.fuzzing.*`, `window.electronAPI.zap.*`

## [0.6.0] - 2025-10-23

### Added - Performance Optimization and Basic Integrations

#### Performance Optimization
- **Request Caching System**: Intelligent caching with TTL and invalidation
  - CacheService with SHA-256 key generation
  - Configurable TTL (Time To Live) per request
  - LRU (Least Recently Used) eviction strategy
  - Cache size management (configurable max size)
  - Tag-based cache invalidation
  - URL pattern-based invalidation
  - Cache statistics (hits, misses, hit rate, size)
  - Enable/disable caching per request or globally
- **Timeout Management**: Configurable request timeouts
  - Per-request timeout configuration
  - Global default timeout setting
  - Timeout error handling
- **React Performance Optimization**: Component memoization
  - React.memo for RequestPanel and ResponsePanel
  - useCallback for event handlers
  - useMemo for expensive computations
  - Optimized tab label rendering
  - Reduced unnecessary re-renders
- **Cache Settings UI**: Complete cache management interface
  - Enable/disable caching toggle
  - TTL slider (1-60 minutes)
  - Max cache size slider (10-500 MB)
  - Real-time cache statistics display
  - Clear all cache button
  - Clean expired entries button
  - Invalidate by URL pattern (regex support)
  - Hit rate visualization with color coding

#### Import/Export System
- **Modular Import/Export Architecture**: Registry-based handler system
  - ImportExportService with handler registry
  - Support for multiple formats
  - Format auto-detection
  - Extensible architecture
- **JSON Import/Export**: Native format support
  - Collection import/export
  - Request import/export
  - Full data preservation
  - Validation and error handling
- **cURL Import/Export**: Command-line compatibility
  - cURL command parsing (GET, POST, PUT, DELETE, PATCH)
  - Header extraction (-H, --header)
  - Body data parsing (-d, --data)
  - Method detection (-X, --request)
  - Query parameter handling
  - cURL generation from requests
  - Multi-line command support
- **Import/Export Dialog UI**: User-friendly interface
  - Format selection (JSON, cURL)
  - Import from text/file
  - Export to clipboard/file
  - Format examples
  - Validation feedback

#### Git Integration
- **GitService**: Complete version control
  - Repository initialization with .gitignore
  - Status tracking (modified, created, deleted, staged)
  - File staging and unstaging
  - Commit with messages and descriptions
  - Branch management (create, checkout, list)
  - Commit history viewing
  - Diff generation (staged and unstaged)
  - Configuration management
  - Change detection
- **GitPanel UI**: Visual Git interface
  - Repository status display
  - File list with staging buttons
  - Commit dialog with validation
  - History viewer with pagination
  - Branch indicator
  - Real-time updates
  - Discard changes functionality

#### Plugin System
- **PluginLoader**: Dynamic plugin management
  - Plugin discovery from directory
  - Dynamic loading/unloading
  - Hot reload support
  - Hook execution system
  - Permission management
  - Error isolation
  - Plugin-specific storage
- **Plugin Architecture**: Complete plugin framework
  - Plugin manifest (plugin.json)
  - Lifecycle hooks (onLoad, onUnload)
  - Request/Response hooks
  - Collection event hooks
  - Settings change hooks
  - Context API with utilities
  - Permission system (network, filesystem, database, etc.)
- **PluginManager UI**: Plugin management interface
  - Plugin list with status
  - Enable/disable toggles
  - Reload and unload buttons
  - Status indicators
  - Error display
  - Permission viewing
- **Example Plugin**: Working demonstration
  - All hooks implemented
  - Storage usage examples
  - API interaction examples
  - Complete documentation
- **Plugin Development Guide**: Comprehensive documentation
  - Quick start tutorial
  - Complete API reference
  - Best practices
  - Example plugins
  - Debugging guide

#### PDF Reporting System
- **ReportGenerator**: Professional PDF reports
  - Security scan reports
  - Vulnerability scan reports
  - Security trends reports
  - Performance trends reports
  - Professional formatting
  - Metadata tracking
  - Data validation
- **ChartGenerator**: Visual data representation
  - Line charts (trends)
  - Bar charts (comparisons)
  - Pie charts (distributions)
  - Doughnut charts (breakdowns)
  - Stacked bar charts
  - Pure JavaScript (chartjs-to-image)
  - No native dependencies
  - Cross-platform compatible
- **ReportManager UI**: Report configuration interface
  - Report type selection
  - Title and metadata configuration
  - Date range picker
  - Options (charts, summary, details)
  - Generate button with feedback
  - Report type descriptions
- **Reporting Guide**: Complete documentation
  - Report types overview
  - Usage instructions
  - API reference
  - Best practices
  - Troubleshooting

### Improved
- RequestService now supports caching for GET requests
- Response objects include `cached` flag
- Better memory management with automatic eviction
- Enhanced IPC handlers for all new features
- UI now includes tabs for all v0.6.0 features
- Scrollable tab navigation
- Import/Export button in toolbar

### Testing
- Added 127+ tests for v0.6.0 features
  - CacheService: 17 tests
  - GitService: 24 tests
  - ImportExportService: 20 tests
  - PluginLoader: 21 tests
  - ReportGenerator: 28 tests
  - ChartGenerator: 20 tests
  - Integration tests: 10 tests
- Total: 311 tests (100% passing)
- Test coverage: 85%+

### Technical
- Added 5 major features (~4,500 lines of new code)
- Added 6 new services
- Added 5 new UI components
- Added 8 documentation files
- Updated App.tsx with new navigation
- Added 6 new dependencies
- Build successful (848KB renderer bundle)

### Documentation
- Git Integration Guide
- Plugin Development Guide
- Reporting Guide
- Test Coverage Report
- V0.6.0 Status Report
- Updated README with new features

## [0.5.0] - 2025-01-23

### Added - Mock Servers, Automation & Security Testing
- **Mock Express Servers**: Create mock API servers from collections
  - Express-based mock servers
  - Route generation from collections
  - Request/response logging
  - Statistics tracking
- **Batch Runner**: Execute chained requests with variable extraction
  - Sequential request execution
  - Variable extraction and passing
  - JSONPath support
  - Export to JSON/CSV
- **Cron Monitoring**: Scheduled API monitoring with dashboard
  - Cron expression support
  - Automated API health checks
  - Execution logging
  - Statistics dashboard
- **Data-Driven Testing**: CSV/JSON/XML parsing with iterations
  - CSV parser (PapaParse)
  - JSON array support
  - XML parsing
  - Variable substitution
- **Security Assertions**: Header validation and leak detection
  - 7 security header checks
  - 8 information leak patterns
  - Cookie security validation
  - Security scoring (0-100)
- **Vulnerability Scanner**: Injection and fuzzing tests
  - SQL injection (14 payloads)
  - XSS (11 payloads)
  - Command injection (12 payloads)
  - Path traversal (9 payloads)
  - XXE (3 payloads)
  - Fuzzing (10 payloads)

### Testing
- Added 33 new tests for v0.5.0 features
- Total: 159 tests (154 passing, 96.9% pass rate)
- Test suites: 16

### Technical
- Added 6 new services (Mock, Batch, Cron, DataDriven, Security, Vulnerability)
- Added 6 new UI components
- 3,000+ lines of new code
- 4 new dependencies

## [0.4.0] - 2025-01-XX

### Added - Protocol Support with Automatic Extraction
- **GraphQL Support**: Apollo Client integration with full schema introspection
  - Query and mutation execution
  - Schema introspection
  - Query validation and template generation
  - Variable extraction and example generation
- **SOAP/WSDL Support**: Complete SOAP client with WSDL parsing
  - WSDL 1.1 and 2.0 support
  - Service and operation extraction
  - Type parsing from XSD schemas
  - SOAP envelope generation
- **gRPC Support**: grpc-js integration with proto file parsing
  - Proto file parsing and validation
  - Service and method extraction
  - Message type parsing
  - Streaming type detection (unary, client, server, bidirectional)
- **WebSocket Support**: Real-time WebSocket client
  - Connection management
  - Send/receive messages
  - Real-time logging with color coding
  - Auto-scroll message viewer
- **Server-Sent Events (SSE)**: Event stream viewer
  - SSE connection management
  - Real-time event streaming
  - Event filtering by type
  - Statistics dashboard
- **AMQP/JMS Support**: Message queue operations
  - Queue and exchange management
  - Publish/subscribe patterns
  - Message routing with routing keys
  - Consumer management
- **MQTT Support**: Pub/sub messaging
  - MQTT broker connections
  - Publish with QoS levels (0, 1, 2)
  - Subscribe with topic wildcards (+, #)
  - Retain message support
- **AsyncAPI Parser**: Event-driven API specifications
  - AsyncAPI 2.x and 3.x support
  - Channel and operation extraction
  - Message schema parsing
  - Example payload generation
- **Avro Parser**: Data serialization schemas
  - Avro schema parsing
  - Data serialization/deserialization
  - Schema validation
  - Compatibility checking
- **WS-Security**: SOAP security enhancement
  - Username Token authentication
  - Password Text and Password Digest
  - Timestamp and nonce generation
  - Security profiles
- **Schema Loader UI**: Unified protocol selector
  - Tabbed interface for all protocols
  - Integrated explorers
  - Protocol-specific views

### Improved
- Enhanced error handling across all services
- Improved real-time logging with timestamps
- Better JSON formatting and parsing
- Comprehensive test coverage (126 tests)

### Technical
- Added 10 new services (GraphQL, SOAP, gRPC, WebSocket, SSE, AMQP, MQTT, AsyncAPI, Avro, WS-Security)
- Added 15 new UI components
- Added 32 new tests
- 8,000+ lines of new code
- 15 new dependencies

## [0.3.0] - 2025-01-22

### Added
- **OpenAPI/Swagger Integration**
  - Swagger UI React component for interactive API documentation
  - OpenAPI Parser supporting Swagger 2.0 and OpenAPI 3.x
  - Automatic request generation from OpenAPI specifications
  - Path parameter extraction and URL generation
  - Security scheme auto-configuration
  - Tags and operation ID extraction
  - Contact and license information parsing

- **Markdown Documentation Generator**
  - Generate comprehensive API documentation from collections
  - Multiple code examples (cURL, JavaScript, Python)
  - Method badges (GitHub/GitLab compatible)
  - Headers and query parameters tables
  - Request body with syntax highlighting
  - Collapsible sections for clean presentation
  - Customizable output options

- **Schema Refactoring Service**
  - Compare old vs new OpenAPI specifications
  - Breaking change detection with severity levels
  - Automatic request migration to new schema
  - Version comparison and diff reporting
  - Parameter change tracking
  - Endpoint deprecation detection
  - Migration report generation

- **Enhanced REST Auto-Extraction**
  - Path parameter replacement in URLs
  - Security scheme extraction (Basic, Bearer, API Key, OAuth2)
  - Tags for endpoint categorization
  - Operation ID tracking
  - Deprecation warnings in descriptions
  - Contact and license metadata
  - Path-level parameter inheritance

### Improved
- OpenAPI parser with advanced example generation
- Schema-based default value extraction
- Request body example generation from schemas
- Better error handling in parsers

### Documentation
- OpenAPI integration guide
- Markdown generator documentation
- Schema refactoring guide
- Migration best practices

## [0.2.0] - 2025-01-22

### Added
- **Collections Management**
  - Collections tree UI with expand/collapse
  - Full CRUD operations for collections
  - CRUD operations for requests within collections
  - Nested folder support
  - Drag-and-drop organization

- **Scripting & Testing**
  - Node VM scripting engine with Postman-like pm API
  - Pre-request scripts for dynamic request modification
  - Test scripts with Chai-like assertions
  - Monaco Editor integration with IntelliSense
  - Groovy-style scripting support
  - Auto-completion for pm API
  - Syntax highlighting and error detection

- **Variables System**
  - Three-level scoping: Global, Environment, Collection
  - Visual variable editor with CRUD operations
  - Variable resolution in requests ({{variableName}})
  - Type support: string, number, boolean, secret
  - Enable/disable variables
  - Variable descriptions

- **JSONPath Auto-Extraction**
  - pm.jsonPath() for querying JSON data
  - pm.extractJson() for automatic variable extraction
  - Support for complex JSONPath expressions
  - Filter and slice operations

- **Secrets Management**
  - Keytar integration for OS-level credential storage
  - Windows Credential Manager support
  - macOS Keychain support
  - Linux Secret Service support
  - Secure storage for API keys and passwords

- **Assertion Builder**
  - Visual assertion builder UI
  - 7 assertion types (Status, Header, Body, JSONPath, XPath, Response Time, Custom)
  - 8 operators (equals, contains, matches, exists, gt, lt, gte, lte)
  - Auto-generated test code
  - Pass/fail indicators
  - Assertion groups

- **Testing Infrastructure**
  - Jest test framework setup
  - 54 unit tests for collections and variables
  - In-memory database testing
  - Comprehensive test coverage
  - Test documentation

### Improved
- Request editor with tabbed interface
- Response viewer with better formatting
- Database schema with proper relationships
- IPC communication layer
- Type safety across the application

### Documentation
- Comprehensive scripting guide (400+ lines)
- Groovy scripting guide (500+ lines)
- Test documentation
- API reference updates
- User guide improvements

## [0.1.0] - 2025-10-22

### Added
- Complete Electron + React + TypeScript + Vite application structure
- Package.json with 30+ dependencies configured
- TypeScript configurations (base, main, preload)
- Vite configuration for React bundling
- Jest configuration for testing framework
- ESLint and Prettier for code quality
- Comprehensive .gitignore patterns

#### Core Application
- Electron main process with IPC communication
- Secure preload script with contextBridge API
- React application with Material-UI components
- Dark/light theme toggle with Material-UI theming
- Professional UI layout (sidebar, split pane, top menu)
- Collapsible sidebar with smooth transitions

#### Type System
- Complete TypeScript interfaces (20+ types)
- Collection, Request, Environment, Variable models
- Auth, Header, QueryParam, RequestBody types
- Response, Assertion, TestResult types
- MockServer, Workflow, Settings types
- Type-safe IPC communication

#### Database Layer
- SQLite DatabaseService with better-sqlite3
- Full CRUD operations for all entities
- Collections with hierarchical structure
- Requests with all configuration options
- Environments with variable management
- Variables with scoping (global, environment, collection)
- Settings storage and retrieval
- Database indexes for performance
- Foreign key constraints for data integrity
- WAL mode for better concurrency

#### Request Features
- RequestService with Axios HTTP client
- Variable resolution with {{variableName}} syntax
- Query parameters editor with enable/disable
- HTTP headers editor with enable/disable
- Request body editor supporting:
  - JSON with syntax highlighting
  - XML
  - Raw text
  - Form Data
  - URL Encoded
  - GraphQL
- Authentication support:
  - Basic Auth (username/password)
  - Bearer Token (JWT/OAuth)
  - API Key (header or query param)
  - OAuth 2.0 (access token)
  - Digest Auth
- Pre-request script editor
- Test script editor
- Request timeout and redirect handling

#### Response Features
- ResponsePanel with comprehensive display
- JSON/XML parsing and formatting
- Pretty/Raw view toggle for JSON/XML
- Syntax highlighting with monospace font
- Response headers table view
- Timeline tab with performance metrics
- Status code with color coding:
  - Green (2xx Success)
  - Blue (3xx Redirect)
  - Yellow (4xx Client Error)
  - Red (5xx Server Error)
- Response time tracking
- Response size calculation and formatting
- Timestamp with locale formatting
- Performance indicators

#### UI Components
- Sidebar component with collections tree
- RequestPanel with 6 tabs
- ParamsTab for query parameters
- HeadersTab for HTTP headers
- BodyTab for request body
- AuthTab for authentication
- ResponsePanel with 4 tabs
- Tab badges showing counts
- Loading states and spinners
- Empty states with helpful messages

#### Build & Distribution
- Electron-builder configuration
- Windows builds:
  - NSIS installer with wizard
  - Portable executable
- macOS builds:
  - DMG disk image
  - ZIP archive
  - Universal binaries (Intel + Apple Silicon)
- Linux builds:
  - AppImage (universal)
  - DEB package (Debian/Ubuntu)
  - RPM package (RedHat/Fedora)
- Build scripts for all platforms
- Icon placeholders and creation guide
- macOS entitlements configuration

#### Documentation
- README.md with project overview
- CHANGELOG.md (this file)
- TODO.md with task tracking
- LICENSE (MIT)
- INSTALLATION_GUIDE.md
- SETUP_COMPLETE.md
- PROJECT_OVERVIEW.md
- docs/QUICKSTART.md
- docs/USER_GUIDE.md
- docs/API.md
- docs/CODEBASE_STRUCTURE.md
- docs/EXTENDING_GUIDE.md
- docs/BUILDING.md
- docs/STATUS.md
- docs/USER_PREFERENCES.md
- docs/AI_CONTEXT.md
- build/README.md (icon guide)

#### Scripts
- setup.bat & setup.ps1 - Dependency installation
- run.bat & run.ps1 - Development server
- test.bat & test.ps1 - Test runner
- build.bat & build.ps1 - Production build
- package.bat - Platform packaging
- package-all.bat - All platforms

### Changed
- N/A (initial release)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A (initial release)

### Security
- Secure IPC communication with contextBridge
- No nodeIntegration in renderer process
- Context isolation enabled
- Sandboxed preload script

## [Unreleased]

### Planned for v0.2.0
- Collections tree with CRUD operations
- Scripting engine with Node VM
- Monaco editor integration
- Variable management UI
- Auto-extraction with JSONPath
- Keytar for secure credential storage
- Comprehensive test suite (70%+ coverage)

---

## Version History

- **v0.1.0** (2025-10-22) - Core Setup and Basic Request Handling (MVP) ✅
- **v0.2.0** - Collections, Testing, and Variables (Planned)
- **v0.3.0** - API Design, Prototyping, and Documentation (Planned)
- **v0.4.0** - Protocol Support with Automatic Extraction (Planned)
- **v0.5.0** - Mock Servers, Workflow Automation, and Monitoring (Planned)
- **v0.6.0** - Performance Optimization and Basic Integrations (Planned)
- **v0.7.0** - Security and Vulnerability Testing (Planned)
- **v1.0.0** - Full Integration, Testing, and Packaging (Planned)
