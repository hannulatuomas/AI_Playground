# LocalAPI Features

**Version:** 0.8.0  
**Last Updated:** October 24, 2025

## Complete Feature List

### Core API Development (v0.1.0 - v0.3.0)

#### Request Building
- HTTP methods: GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD
- URL parameters and query strings
- Request headers management
- Request body (JSON, XML, Form Data, Raw)
- Authentication (Basic, Bearer, API Key, OAuth 2.0)

#### Collections Management
- Organize requests in folders
- Import/export collections (JSON, cURL)
- Duplicate and clone requests
- Search and filter
- Git version control integration

#### Variables & Environments
- Global variables
- Environment variables
- Collection variables
- Dynamic variable resolution
- Secret management

#### Scripting & Testing
- Pre-request scripts (JavaScript)
- Test scripts (JavaScript/Groovy)
- Assertions and validations
- pm API compatibility
- Console logging

#### API Documentation
- OpenAPI/Swagger import
- Automatic documentation generation
- Markdown export
- Schema validation

---

### Protocol Support (v0.4.0)

#### GraphQL
- Apollo Client integration
- Schema introspection
- Query and mutation execution
- Variable management
- Template generation

#### SOAP/WSDL
- WSDL 1.1 and 2.0 support
- Service and operation browsing
- WS-Security (Username token, password digest)
- XML request/response handling

#### gRPC
- Proto file parsing
- Service discovery
- Unary, server streaming, client streaming, bidirectional
- Method execution

#### WebSocket
- Real-time bidirectional communication
- Connection management
- Message sending/receiving
- Message logging

#### Server-Sent Events (SSE)
- Event streaming
- Event filtering
- Connection statistics
- Auto-reconnect

#### AMQP/JMS
- Queue operations
- Exchange operations
- Message publishing
- Message consuming

#### MQTT
- Broker connection
- Publish with QoS
- Subscribe with wildcards
- Topic management

#### AsyncAPI & Avro
- AsyncAPI 2.x/3.x parsing
- Avro schema support
- Validation and examples

---

### Automation & Security (v0.5.0)

#### Mock Servers
- Express-based HTTP servers
- Route generation from collections
- Request/response logging (1000 entries)
- Custom delays and responses
- CORS support
- Statistics tracking
- Multiple concurrent servers

#### Batch Runner
- Sequential request execution
- Variable extraction (JSONPath)
- Variable passing between requests
- Continue/stop on error options
- Delay between requests
- Export to JSON/CSV
- Collection-based batch generation

#### Cron Monitoring
- Cron expression scheduling
- 9 preset schedules
- Automated API health checks
- Execution logging
- Statistics dashboard
- Job management (start/stop/delete)
- Real-time monitoring

#### Data-Driven Testing
- CSV parsing (PapaParse)
- JSON array support
- XML parsing
- Variable substitution (`{{column}}`)
- Iteration runner
- Statistics and export
- Preview data sets

#### Security Assertions
- **Header Checks (7)**:
  - Strict-Transport-Security (HSTS)
  - X-Frame-Options
  - X-Content-Type-Options
  - Content-Security-Policy
  - X-XSS-Protection
  - Referrer-Policy
  - Permissions-Policy

- **Information Leak Detection (8)**:
  - API keys
  - AWS access keys
  - Private keys
  - JWT tokens
  - Passwords
  - Database connection strings
  - Email addresses
  - Stack traces

- **Cookie Security (3)**:
  - Secure flag
  - HttpOnly flag
  - SameSite attribute

- **Security Scoring**: 0-100 score
- **Export**: JSON and Markdown formats

#### Vulnerability Scanner
- **SQL Injection (14 payloads)**
- **XSS (11 payloads)**
- **Command Injection (12 payloads)**
- **Path Traversal (9 payloads)**
- **XXE (3 payloads)**
- **Fuzzing (10 payloads)**
- Severity classification
- Evidence collection
- Recommendations
- Export results

---

## Performance Optimization & Integrations (v0.6.0) ✅

### Request Caching
- Intelligent caching with SHA-256 key generation
- TTL (Time To Live) configuration (1-60 minutes)
- LRU (Least Recently Used) eviction strategy
- Tag-based cache invalidation
- URL pattern-based invalidation (regex support)
- Cache statistics (hits, misses, hit rate, size)
- Configurable max size (10-500 MB)
- Enable/disable per request or globally

### Import/Export System
- **JSON Import/Export**: Full collection and request data
- **cURL Import/Export**: Parse and generate cURL commands
- Modular architecture with handler registry
- Format auto-detection
- Validation and error handling
- Export to clipboard or file
- Import from text or file

### Git Integration
- Repository initialization with .gitignore
- Visual status display (modified, created, deleted, staged)
- File staging and unstaging
- Commit with messages and descriptions
- Branch management (create, checkout, list)
- Commit history viewer with pagination
- Diff generation (staged and unstaged)
- Configuration management
- Discard changes functionality

### Plugin System
- Dynamic plugin loading and unloading
- Hot reload support
- Plugin lifecycle hooks (onLoad, onUnload)
- Request/Response hooks
- Collection event hooks
- Settings change hooks
- Permission system (network, filesystem, database, etc.)
- Plugin-specific storage
- Error isolation
- Example plugin included

### PDF Reporting
- **Security Scan Reports**: Professional PDF reports with findings
- **Vulnerability Scan Reports**: Detailed vulnerability assessments
- **Security Trends Reports**: Historical security analysis
- **Performance Trends Reports**: Performance metrics over time
- **Chart Generation**: 7 chart types (line, bar, pie, doughnut, stacked)
- Pure JavaScript implementation (no native dependencies)
- Professional formatting with metadata
- Configurable options (charts, summary, details)

---

## Security Testing Suite (v0.7.0) ✅

### OWASP Top 10 Scanner
- **Complete OWASP Top 10 (2021) Coverage**:
  - A01:2021 - Broken Access Control
  - A02:2021 - Cryptographic Failures
  - A03:2021 - Injection
  - A04:2021 - Insecure Design
  - A05:2021 - Security Misconfiguration
  - A06:2021 - Vulnerable and Outdated Components
  - A07:2021 - Identification and Authentication Failures
  - A08:2021 - Software and Data Integrity Failures
  - A09:2021 - Security Logging and Monitoring Failures
  - A10:2021 - Server-Side Request Forgery (SSRF)
- Individual test modules for each category (1,370 lines)
- Scan depth options (quick, standard, deep)
- Severity classification (critical, high, medium, low, info)
- Confidence levels (confirmed, firm, tentative)
- Detailed findings with evidence
- Recommendations and remediation guidance
- Export to JSON and reports

### Fuzzing & Bomb Testing
- **7 Fuzzing Types**:
  - String Fuzzing (special chars, Unicode, format strings)
  - Number Fuzzing (boundaries, overflow, special numbers)
  - Format Fuzzing (malformed data, type confusion)
  - Injection Fuzzing (SQL, XSS, Command, LDAP)
  - Boundary Fuzzing (array/string limits)
  - Encoding Fuzzing (URL, HTML, Base64)
  - Bomb Testing (XML bomb, JSON bomb, large payloads)
- Intensity levels (low, medium, high)
- Custom payload support
- Request rate limiting
- Crash detection
- Anomaly detection
- Finding categorization
- Summary statistics

### OWASP ZAP Integration
- Full ZAP API integration (450+ lines)
- Spider scanning (URL discovery)
- Active scanning (automated attacks)
- Passive scanning (traffic analysis)
- Alert management (retrieve, filter, clear)
- Report generation (HTML/XML)
- Session management
- Context configuration
- Real-time scan progress
- Risk-based alert filtering

### Security Runner Dashboard
- Unified security testing interface (650+ lines)
- Quick Scan mode (all tests at once)
- Individual test selection
- Per-test configuration
- Real-time progress tracking
- Results aggregation
- Finding summary with severity counts
- Export all findings
- Test history tracking

### End-to-End Security Testing
- 70+ comprehensive E2E test cases
- Full workflow testing
- Performance benchmarking
- Error scenario validation
- Data integrity verification
- Concurrent execution testing

---

## Import/Export Services & Advanced Features (v0.8.0) ✅

### Import/Export Services
- **13+ Format Support**:
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

### Advanced Features
- **Workspaces**: Multi-workspace support with isolated configurations
- **Variable Extraction**: JSONPath, XPath, Header, Regex extraction with auto-rules
- **Data-Driven Testing**: CSV/JSON data file support with parameterized requests
- **Variable History**: Track variable changes over time
- **Extraction Rules**: Automated variable extraction from responses

### Database Testing Infrastructure
- **DatabaseService Refactoring**: Dependency Injection pattern for testability
- **Comprehensive Mocks**: better-sqlite3 mock with full SQL support
- **Test Utilities**: Easy test setup and debugging tools
- **77/77 database tests passing**: Complete test coverage with zero native dependencies

---

## Feature Statistics (v0.8.0)

### Services
- **Total Services**: 33
- **Core Services**: 3
- **Security Services**: 5
- **Protocol Services**: 8
- **Workflow Services**: 4
- **Utility Services**: 4
- **Parser & Generator Services**: 7
- **Scripting Services**: 2

### UI Components
- **Total Components**: 35+
- **Security Components**: 4 (OWASPScanner, FuzzingTester, SecurityRunner, ZAPProxy)
- **Core Components**: 5+
- **Protocol Components**: 11+
- **Automation Components**: 5+

### Testing
- **Total Tests**: 583
- **Passing Tests**: 583 (100%)
- **Test Suites**: 35
- **Unit Tests**: 380
- **Integration Tests**: 133
- **E2E Tests**: 70

### Code Metrics
- **Total Lines**: 33,000+
- **Services**: ~15,000 lines
- **Components**: ~11,000 lines
- **Tests**: ~7,000 lines
- **Security Code**: ~6,100 lines
- **Import/Export Code**: ~4,000 lines

---

**Last Updated:** October 24, 2025  
**Version:** 0.8.0
