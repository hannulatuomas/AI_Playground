# UAIDE Codebase Structure

**Last Updated**: January 20, 2025  
**Version**: 1.6.0

This document describes the organization and structure of the UAIDE codebase.

---

## Directory Structure

```
ultimate-ai-ide/
├── .windsurf/              # Windsurf IDE configuration
│   ├── rules/              # Project-specific rules for AI
│   └── workflows/          # Reusable workflows
│
├── Initial_Plans/          # Original planning documents
│   ├── Initial_Plan.md
│   ├── Initial_Prompt.txt
│   └── Initial_Workflow.txt
│
├── src/                    # Source code (main application)
│   ├── main.py             # Application entry point
│   │
│   ├── ai/                 # AI backend integration
│   │   ├── backend.py      # llama.cpp wrapper
│   │   ├── prompt_formatter.py
│   │   └── response_parser.py
│   │
│   ├── db/                 # Database layer
│   │   ├── database.py     # Database manager
│   │   ├── models.py       # Data models
│   │   └── migrations.py   # Schema migrations
│   │
│   ├── ui/                 # User interface
│   │   ├── cli.py          # CLI interface
│   │   ├── commands.py     # Command implementations
│   │   └── formatters.py   # Output formatting
│   │
│   ├── config/             # Configuration management
│   │   ├── config.py       # Config manager
│   │   └── defaults.py     # Default settings
│   │
│   ├── core/               # Core orchestration
│   │   ├── orchestrator.py # Main orchestrator
│   │   ├── event_bus.py    # Event system
│   │   └── plugin_system.py # Plugin architecture
│   │
│   ├── modules/            # Feature modules
│   │   ├── project_manager/   # Project scaffolding
│   │   │   ├── manager.py
│   │   │   ├── detector.py
│   │   │   ├── scaffolder.py
│   │   │   └── templates/     # Project templates
│   │   │
│   │   ├── code_generator/    # Code generation
│   │   │   ├── generator.py
│   │   │   ├── analyzer.py
│   │   │   ├── editor.py
│   │   │   └── validator.py
│   │   │
│   │   ├── tester/            # Testing & bug fixing
│   │   │   ├── test_generator.py
│   │   │   ├── test_runner.py
│   │   │   ├── bug_fixer.py
│   │   │   └── coverage_analyzer.py
│   │   │
│   │   ├── doc_manager/       # Documentation
│   │   │   ├── manager.py
│   │   │   ├── scanner.py
│   │   │   ├── generator.py
│   │   │   └── templates/
│   │   │
│   │   ├── refactorer/        # Code refactoring
│   │   │   ├── analyzer.py
│   │   │   ├── refactor.py
│   │   │   ├── splitter.py
│   │   │   └── optimizer.py
│   │   │
│   │   ├── api_manager/       # API development
│   │   │   ├── rest_generator.py
│   │   │   ├── graphql_generator.py
│   │   │   ├── soap_generator.py
│   │   │   ├── api_tester.py
│   │   │   └── templates/
│   │   │
│   │   ├── db_manager/        # Database development
│   │   │   ├── schema_generator.py
│   │   │   ├── migration_manager.py
│   │   │   ├── query_optimizer.py
│   │   │   ├── debugger.py
│   │   │   └── connectors/
│   │   │
│   │   ├── context_manager/   # Context & memory
│   │   │   ├── manager.py
│   │   │   ├── summarizer.py
│   │   │   ├── embedder.py
│   │   │   ├── retriever.py
│   │   │   └── window_manager.py
│   │   │
│   │   ├── rule_manager/      # Rule enforcement
│   │   │   ├── manager.py
│   │   │   ├── parser.py
│   │   │   ├── validator.py
│   │   │   └── defaults.py
│   │   │
│   │   ├── task_decomposer/   # Task management
│   │   │   ├── decomposer.py
│   │   │   ├── planner.py
│   │   │   ├── executor.py
│   │   │   └── tracker.py
│   │   │
│   │   ├── self_improver/     # Self-improvement
│   │   │   ├── logger.py
│   │   │   ├── analyzer.py
│   │   │   ├── learner.py
│   │   │   └── adapter.py
│   │   │
│   │   └── prompt_manager/    # Prompt management
│   │       ├── manager.py
│   │       ├── template_engine.py
│   │       └── defaults.py
│   │
│   └── utils/              # Utility functions
│       ├── file_ops.py     # File operations
│       ├── path_utils.py   # Path utilities
│       ├── validators.py   # Validation functions
│       ├── constants.py    # Constants and enums
│       └── logger.py       # Logging setup
│
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── e2e/                # End-to-end tests
│   ├── performance/        # Performance tests
│   └── stress/             # Stress tests
│
├── scripts/                # Utility scripts
│   ├── setup.py            # Installation script
│   ├── download_model.py   # Model download
│   └── ...
│
├── docs/                   # Documentation
│   ├── QUICKSTART.md
│   ├── USER_GUIDE.md
│   ├── API.md
│   ├── EXTENDING_GUIDE.md
│   ├── AI_CONTEXT.md
│   ├── USER_PREFERENCES.md
│   ├── STATUS.md
│   ├── CODEBASE_STRUCTURE.md (this file)
│   └── PHASE_*_PLAN.md     # Implementation plans
│
├── commits/                # Commit scripts and summaries
│   └── phase_*.bat         # Git commit scripts
│
├── data/                   # Runtime data (gitignored)
│   ├── uaide.db            # SQLite database
│   └── faiss_index/        # Vector embeddings
│
├── models/                 # AI models (gitignored)
│   └── *.gguf              # llama.cpp models
│
├── logs/                   # Application logs (gitignored)
│   └── uaide.log
│
├── config.json             # User configuration
├── config.example.json     # Example configuration
├── requirements.txt        # Python dependencies
├── setup.py                # Package setup
├── pyproject.toml          # Project metadata
├── .gitignore
├── LICENSE
├── README.md
├── CHANGELOG.md
└── TODO.md
```

---

## Module Descriptions

### AI Backend (`src/ai/`)
Wraps llama.cpp for local AI inference. Handles model loading, prompt formatting, and response parsing.

**Key Classes**:
- `AIBackend`: Main interface to AI model
- `PromptFormatter`: Formats prompts for model
- `ResponseParser`: Parses and validates AI responses

### Database (`src/db/`)
SQLite database for persistent storage and FAISS for vector embeddings.

**Key Classes**:
- `Database`: Database manager with connection pooling
- `Models`: ORM-like data models
- `Migrations`: Schema version management

### User Interface (`src/ui/`)
Command-line interface for user interaction.

**Key Classes**:
- `CLI`: Main CLI controller
- `Commands`: Command implementations
- `Formatters`: Output formatting utilities

### Project Manager (`src/modules/project_manager/`)
Creates and maintains projects in various languages/frameworks.

**Features**:
- Project detection
- Scaffolding with templates
- Git initialization
- Dependency management

### Code Generator (`src/modules/code_generator/`)
AI-powered code generation with context awareness.

**Features**:
- Feature analysis
- Code generation
- Duplicate detection
- Code insertion and validation

### Tester (`src/modules/tester/`)
Automated testing and bug fixing.

**Features**:
- Test generation
- Test execution
- Coverage analysis
- Bug diagnosis and fixing

### Documentation Manager (`src/modules/doc_manager/`)
Automatic documentation generation and synchronization.

**Features**:
- Code scanning
- README generation
- API documentation
- Docstring generation

### Refactorer (`src/modules/refactorer/`)
Code quality improvements and refactoring.

**Features**:
- Code analysis
- Structure optimization
- File splitting
- Best practices enforcement

### API Manager (`src/modules/api_manager/`)
API development tools for REST, GraphQL, and SOAP.

**Features**:
- API generation
- Endpoint creation
- API testing
- Documentation

### Database Manager (`src/modules/db_manager/`)
Database schema management and debugging.

**Features**:
- Schema generation
- Migration management
- Query optimization
- Multi-database support

### Context Manager (`src/modules/context_manager/`)
Manages context for large codebases using embeddings.

**Features**:
- Code summarization
- Vector embeddings
- Similarity search
- Context window management

### Rule Manager (`src/modules/rule_manager/`)
Enforces coding standards and best practices.

**Features**:
- Rule storage (global/project)
- Rule injection into prompts
- Rule validation
- Default rule sets

### Task Decomposer (`src/modules/task_decomposer/`)
Breaks down complex tasks into manageable sub-tasks.

**Features**:
- Task analysis
- Sub-task generation
- Dependency management
- Progress tracking

### Self-Improver (`src/modules/self_improver/`)
Learns from errors and adapts behavior.

**Features**:
- Event logging
- Pattern analysis
- Behavior adaptation
- Improvement suggestions

---

## Design Principles

### 1. Modularity
- Each module is independent
- Clear interfaces between modules
- Easy to add/remove modules

### 2. File Size Limit
- Maximum 500 lines per file
- Automatic splitting when exceeded
- Promotes maintainability

### 3. Separation of Concerns
- AI logic separate from business logic
- Database separate from application
- UI separate from core functionality

### 4. Event-Driven Architecture
- Modules communicate via events
- Loose coupling
- Easy to extend

### 5. Plugin Architecture
- Core functionality is extensible
- Third-party plugins supported
- No core code modification needed

---

## Data Flow

### Code Generation Workflow
```
User Request
    ↓
CLI (ui/cli.py)
    ↓
Task Decomposer (modules/task_decomposer/)
    ↓
Context Manager (modules/context_manager/) ← Retrieve relevant code
    ↓
Rule Manager (modules/rule_manager/) ← Get applicable rules
    ↓
Code Generator (modules/code_generator/)
    ↓
Tester (modules/tester/) ← Generate and run tests
    ↓
Doc Manager (modules/doc_manager/) ← Update documentation
    ↓
Self-Improver (modules/self_improver/) ← Log results
    ↓
Result to User
```

---

## Testing Structure

### Unit Tests (`tests/unit/`)
- One test file per module
- Mock external dependencies
- Fast execution
- High coverage

### Integration Tests (`tests/integration/`)
- Test module interactions
- Use real database (test instance)
- Real AI model (or mock)
- Slower but comprehensive

### E2E Tests (`tests/e2e/`)
- Full user workflows
- Real projects created
- All features tested
- Most realistic

---

## Configuration Files

### `config.json`
User-specific configuration (runtime settings)

### `.windsurf/rules/`
Project-specific rules for AI assistance

### `requirements.txt`
Python dependencies

### `pyproject.toml`
Project metadata and build configuration

---

## Development Workflow

1. **Read Documentation**: Understand architecture
2. **Create Branch**: Feature/fix branches
3. **Write Tests**: Test-driven development
4. **Implement**: Follow coding standards
5. **Test**: All tests must pass
6. **Document**: Update relevant docs
7. **Commit**: Use provided commit scripts
8. **PR**: Submit for review

---

## Adding New Modules

1. Create module directory in `src/modules/`
2. Implement module following patterns
3. Add tests in `tests/unit/`
4. Update this documentation
5. Register module in `src/core/orchestrator.py`
6. Add to `src/main.py` CLI

---

## Code Style

- **Python**: PEP 8, Black formatter
- **Docstrings**: Google style
- **Type Hints**: Required for all functions
- **Comments**: Explain why, not what
- **Naming**: Descriptive, no abbreviations

---

## Version Control

- **Main Branch**: Stable, production-ready
- **Develop Branch**: Active development
- **Feature Branches**: Individual features
- **Tags**: Semantic versioning (vX.Y.Z)

---

## Questions?

See [EXTENDING_GUIDE.md](EXTENDING_GUIDE.md) for development details or file an issue.
