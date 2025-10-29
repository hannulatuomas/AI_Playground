# Codebase Structure

**Version:** 0.7.0  
**Last Updated:** October 23, 2025

Comprehensive overview of LocalAPI's architecture and file organization.

## Directory Overview

```
LocalAPI/
├── src/                    # Source code
│   ├── main/              # Electron main process
│   │   ├── index.ts       # Main process entry point
│   │   ├── ipc/           # IPC handlers
│   │   ├── services/      # Backend services
│   │   └── utils/         # Utility functions
│   ├── preload/           # Electron preload scripts
│   │   └── index.ts       # Preload script with API exposure
│   ├── renderer/          # React frontend
│   │   ├── index.tsx      # React entry point
│   │   ├── App.tsx        # Main App component
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── contexts/      # React contexts
│   │   ├── styles/        # CSS/styling files
│   │   └── utils/         # Frontend utilities
│   └── types/             # TypeScript type definitions
│       └── models.ts      # Core data models
├── tests/                 # Test files
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── scripts/              # Build and utility scripts
│   ├── setup.bat         # Windows setup script
│   ├── run.bat           # Windows run script
│   └── test.bat          # Windows test script
├── docs/                 # Documentation
│   ├── API.md            # API documentation
│   ├── USER_GUIDE.md     # User guide
│   ├── QUICKSTART.md     # Quick start guide
│   ├── EXTENDING_GUIDE.md # Extension guide
│   ├── STATUS.md         # Current status
│   ├── USER_PREFERENCES.md # User preferences
│   └── AI_CONTEXT.md     # AI context information
├── commits/              # Commit scripts and summaries
│   └── summaries/        # Phase summaries
├── Plans/                # Project planning
│   ├── InitialPlan.md    # Initial project plan
│   ├── ROADMAP.md        # Development roadmap
│   └── TODO.md           # TODO list
├── data/                 # User data (gitignored)
├── build/                # Build resources (icons, etc.)
├── dist/                 # Compiled output
└── release/              # Packaged applications
```

## Key Files

### Configuration Files

- **package.json** - NPM dependencies and scripts
- **tsconfig.json** - TypeScript configuration (base)
- **tsconfig.main.json** - TypeScript config for main process
- **tsconfig.preload.json** - TypeScript config for preload
- **vite.config.ts** - Vite bundler configuration
- **jest.config.js** - Jest testing configuration
- **.eslintrc.json** - ESLint linting rules
- **.prettierrc** - Prettier formatting rules
- **.gitignore** - Git ignore patterns

### Entry Points

- **src/main/index.ts** - Electron main process
- **src/preload/index.ts** - Electron preload script
- **src/renderer/index.tsx** - React application
- **src/renderer/index.html** - HTML template

## Architecture Layers

### Main Process (Electron)
- Handles system-level operations
- Manages windows and application lifecycle
- Provides IPC handlers for renderer communication
- Manages database and file system access
- Executes scripts in sandboxed VM

### Preload Script
- Bridge between main and renderer processes
- Exposes safe APIs to renderer via contextBridge
- Type-safe API definitions

### Renderer Process (React)
- User interface and interactions
- State management
- Component-based architecture
- Communicates with main via IPC

## Module Organization

### Main Process Services (`src/main/services/`)

**Total Services:** 30

### Core Services (8)
- **DatabaseService.ts** - SQLite database operations
- **CollectionService.ts** - Collection CRUD operations
- **RequestService.ts** - HTTP request execution
- **VariableService.ts** - Variable management and resolution
- **EnvironmentService.ts** - Environment management
- **ScriptService.ts** - Pre-request and test script execution
- **OpenAPIParser.ts** - OpenAPI/Swagger specification parsing
- **MarkdownGenerator.ts** - Documentation generation from collections

### Protocol Services (10)
- **GraphQLService.ts** - GraphQL query execution and introspection (500 lines)
- **SOAPService.ts** - SOAP/WSDL parsing and execution (450 lines)
- **GRPCService.ts** - gRPC proto file parsing and calls (430 lines)
- **WebSocketService.ts** - WebSocket connection management (350 lines)
- **SSEService.ts** - Server-Sent Events streaming (340 lines)
- **AMQPService.ts** - AMQP/JMS queue operations (450 lines)
- **MQTTService.ts** - MQTT pub/sub messaging (400 lines)
- **AsyncAPIParser.ts** - AsyncAPI 2.x/3.x specification parsing
- **AvroParser.ts** - Avro schema parsing and serialization
- **WSSecurityService.ts** - WS-Security for SOAP (280 lines)

### Automation & Security Services (6)
- **MockServerService.ts** (450 lines) - Express-based mock servers
- **BatchRunnerService.ts** (550 lines) - Request chaining and batch execution
- **CronMonitorService.ts** (450 lines) - Scheduled API monitoring
- **DataDrivenService.ts** (500 lines) - CSV/JSON/XML parsing with iterations
- **SecurityAssertionService.ts** (550 lines) - Security checks and leak detection
- **VulnerabilityScannerService.ts** (600 lines) - Injection and fuzzing tests

### Performance & Integration Services (6) - v0.6.0
- **CacheService.ts** (350 lines) - Request caching with TTL and LRU eviction
- **ImportExportService.ts** (200 lines) - Registry-based import/export system
  - **importers/JsonImporterExporter.ts** (250 lines) - JSON format handler
  - **importers/CurlImporterExporter.ts** (300 lines) - cURL format handler
- **GitService.ts** (450 lines) - Git version control integration
- **PluginLoader.ts** (450 lines) - Dynamic plugin management
- **ReportGenerator.ts** (650 lines) - PDF report generation
- **ChartGenerator.ts** (320 lines) - Chart generation with chartjs-to-image

### Components (Renderer)

**Total Components:** 35+

#### Core Components
- **Layout** - Application layout components
- **Request** - Request builder components
- **Response** - Response viewer components
- **Collections** - Collection tree and management
- **Variables** - Variable editor
- **Scripts** - Script editor (Monaco)
- **Settings** - Settings panel

#### v0.6.0 Components
- **CacheSettings.tsx** (330 lines) - Cache management UI with statistics
- **ImportExportDialog.tsx** (200 lines) - Import/export interface
- **GitPanel.tsx** (450 lines) - Git version control UI
- **PluginManager.tsx** (220 lines) - Plugin management interface
- **ReportManager.tsx** (370 lines) - PDF report generation UI

## Data Flow

1. User interacts with React UI
2. UI calls electronAPI methods (from preload)
3. Preload forwards to main process via IPC
4. Main process executes logic (services)
5. Main process returns result via IPC
6. Preload forwards to renderer
7. React updates UI

## Testing Strategy

- **Unit Tests** - Individual functions and services
- **Integration Tests** - Service interactions
- **E2E Tests** - Full application workflows
- **Coverage Target** - 70%+ for v0.2.0, 90%+ for v1.0.0

## Build Process

1. **Development**: Vite dev server + Electron in dev mode
2. **Build**: TypeScript compilation + Vite build
3. **Package**: Electron-builder creates installers

## Naming Conventions

- **Files**: camelCase for utilities, PascalCase for components
- **Components**: PascalCase (e.g., RequestEditor.tsx)
- **Services**: PascalCase with Service suffix (e.g., DatabaseService.ts)
- **Types**: PascalCase (e.g., Request, Collection)
- **Constants**: UPPER_SNAKE_CASE
- **Functions**: camelCase
- **CSS Classes**: kebab-case

## Code Style

- **Indentation**: 2 spaces
- **Quotes**: Single quotes for strings
- **Semicolons**: Required
- **Line Length**: 100 characters max
- **Trailing Commas**: ES5 style

## Dependencies

### Production
- **electron** - Desktop application framework
- **react** - UI library
- **axios** - HTTP client
- **better-sqlite3** - Database
- **Protocol libraries** - GraphQL, SOAP, gRPC, etc.

### Development
- **typescript** - Type safety
- **vite** - Build tool
- **jest** - Testing framework
- **eslint** - Linting
- **electron-builder** - Packaging

## Extension Points

- **Plugins** - Dynamic plugin system with PluginLoader (v0.6.0)
  - See [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md)
  - Lifecycle hooks: onLoad, onUnload, onBeforeRequest, onAfterRequest
  - Permission system for security
  - Plugin-specific storage
- **Themes** - CSS variables in src/renderer/styles/
- **Protocols** - New protocol handlers in src/main/services/protocols/
- **Script APIs** - Extend pm object in src/main/services/ScriptService.ts
- **Import/Export** - Add new format handlers to ImportExportService (v0.6.0)
- **Reports** - Extend ReportGenerator with new report types (v0.6.0)

---

**Version:** 0.6.0  
**Last Updated:** October 23, 2025
