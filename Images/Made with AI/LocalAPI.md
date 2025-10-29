# LocalAPI v0.8.0

A fully local, offline-capable API development tool inspired by Postman, built with Electron, React, and TypeScript.

## Features

### Core API Development
- **Request Building**: Support for REST, GraphQL, SOAP, gRPC, WebSockets, SSE, JMS, and MQTT
- **Collections Management**: Organize requests in collections and folders
- **Environment & Variables**: Manage variables across global, environment, and collection scopes
- **Testing & Scripting**: Pre-request and test scripts with JavaScript/Groovy support
- **Response Handling**: View and analyze API responses with syntax highlighting

### Protocol Support
- **REST**: Full HTTP method support with automatic OpenAPI/Swagger extraction
- **GraphQL**: Query builder with introspection support
- **SOAP**: WSDL parsing and WS-Security
- **gRPC**: Proto file support and automatic request generation
- **WebSockets**: Real-time message logging
- **SSE**: Server-Sent Events stream viewer
- **JMS**: Message queue support via AMQP
- **MQTT**: Pub/sub messaging

### Advanced Features
- **Mock Servers**: Create mock APIs from collections
- **Workflow Automation**: Chain requests and schedule monitoring
- **Data-Driven Testing**: CSV/JSON data iterations
- **Security Testing**: 
  - **OWASP Top 10 Scanner**: Automated security testing for all OWASP Top 10 (2021) vulnerabilities
  - **Fuzzing & Bomb Testing**: Comprehensive fuzzing with 7 types (string, number, format, injection, boundary, encoding, bomb)
  - **Bomb Attacks**: Billion Laughs (XML bomb), JSON bomb, large payloads, many keys
  - **OWASP ZAP Integration**: Full integration with ZAP proxy for spider/active/passive scanning
  - Security assertions and leak detection
- **Performance Optimization**: 
  - Intelligent request caching with TTL and LRU eviction
  - Configurable timeouts (per-request and global)
  - React component memoization for faster UI
  - Cache management UI with statistics
- **Git Integration**: Version control for collections
- **Plugin System**: Extend functionality with custom plugins

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.x (for some native dependencies)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd LocalAPI
```

2. Install dependencies:
```bash
# PowerShell
.\scripts\setup.ps1

# CMD
scripts\setup.bat

# Or directly
npm install
```

3. Run the development server:
```bash
# PowerShell
.\scripts\run.ps1

# CMD
scripts\run.bat

# Or directly
npm run dev
```

### Building

Build for production:
```bash
npm run build
```

Package for your platform:
```bash
# Windows
npm run package:win

# macOS
npm run package:mac

# Linux
npm run package:linux
```

## Project Structure

```
LocalAPI/
├── src/
│   ├── main/           # Electron main process
│   ├── preload/        # Electron preload scripts
│   ├── renderer/       # React frontend
│   └── types/          # TypeScript type definitions
├── tests/              # Test files
├── scripts/            # Build and utility scripts
├── docs/               # Documentation
├── commits/            # Commit scripts and summaries
└── Plans/              # Project planning documents
```

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run test` - Run tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Generate coverage report
- `npm run lint` - Lint code
- `npm run lint:fix` - Fix linting issues
- `npm run type-check` - Check TypeScript types

### Testing

Run all tests:
```bash
npm test
```

Run tests with coverage:
```bash
npm run test:coverage
```

## Documentation

### General
- [API Documentation](docs/API.md)
- [User Guide](docs/USER_GUIDE.md)
- [Quick Start](docs/QUICKSTART.md)
- [Codebase Structure](docs/CODEBASE_STRUCTURE.md)
- [Test Coverage](docs/TEST_COVERAGE.md)

### Features
- [Scripting Guide](docs/SCRIPTING.md)
- [Groovy Scripting](docs/GROOVY_SCRIPTING.md)
- [Extending Guide](docs/EXTENDING_GUIDE.md)
- [Git Integration Guide](docs/GIT_INTEGRATION_GUIDE.md)
- [Plugin Development Guide](docs/PLUGIN_DEVELOPMENT_GUIDE.md)
- [Reporting Guide](docs/REPORTING_GUIDE.md)

## Roadmap

See [ROADMAP.md](Plans/ROADMAP.md) for the detailed development roadmap.

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## License

MIT License - see LICENSE file for details.

## Troubleshooting

Having issues? Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for common problems and solutions.

**Quick fix for native module errors:**
```bash
npm run fix:native
```

## Status

Current Version: **v0.8.0** (Import/Export & Advanced Features)

See [STATUS.md](docs/STATUS.md) for current development status and [CHANGELOG.md](CHANGELOG.md) for release notes.
