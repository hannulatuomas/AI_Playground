# Phase 1: Core Setup - Detailed Implementation Plan

**Timeline**: Weeks 1-2  
**Status**: In Progress  
**Priority**: Critical - Foundation for all other phases

---

## Overview

Phase 1 establishes the foundational infrastructure for the Ultimate AI-Powered IDE. This includes setting up the AI backend, database, basic UI, and core utilities that all other modules will depend on.

---

## Goals

1. ✅ Create working integration with llama.cpp
2. ✅ Establish database schema and operations
3. ✅ Build functional CLI interface
4. ✅ Set up configuration and logging systems
5. ✅ Create project structure and utilities

---

## Task Breakdown

### 1.1 AI Backend Integration (3-4 days)

**Files to Create**:
- `src/ai/__init__.py`
- `src/ai/backend.py`
- `src/ai/prompt_formatter.py`
- `src/ai/response_parser.py`
- `tests/test_ai_backend.py`

**Implementation Steps**:

1. **Create AIBackend Class** (`src/ai/backend.py`)
   - Initialize llama-cpp-python
   - Load model with configuration
   - Manage model lifecycle
   - Handle GPU/CPU selection
   
2. **Implement Query Method**
   - Format prompts correctly
   - Send to model
   - Parse responses
   - Handle streaming/non-streaming
   - Error handling
   
3. **Add Context Management**
   - Conversation history tracking
   - Context window management
   - Token counting
   - Context pruning strategies
   
4. **Implement Caching**
   - Cache frequent queries
   - LRU cache for responses
   - Cache invalidation logic
   
5. **Error Handling**
   - Model loading failures
   - Out of memory errors
   - Invalid prompts
   - Timeout handling

**AI Prompt to Use**:
```
Implement a Python class AIBackend in src/ai/backend.py that wraps llama.cpp via llama-cpp-python.

Requirements:
- Class should handle model loading with configurable parameters
- Implement query(prompt, max_tokens, temperature, top_p, top_k) method
- Support conversation history management
- Add LRU cache for repeated queries (using functools.lru_cache)
- Include comprehensive error handling
- Add type hints and docstrings
- Log all operations
- Support both streaming and non-streaming responses

Use Python 3.12.10 features. Keep code modular and under 500 lines.
```

**Testing**:
- Unit tests for all methods
- Mock llama.cpp for testing
- Test with sample prompts
- Performance benchmarks

---

### 1.2 Database Setup (2-3 days)

**Files to Create**:
- `src/db/__init__.py`
- `src/db/database.py`
- `src/db/models.py`
- `src/db/migrations.py`
- `tests/test_database.py`

**Schema Design**:

```sql
-- Projects Table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,
    language TEXT,
    framework TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rules Table
CREATE TABLE rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    scope TEXT CHECK(scope IN ('global', 'project')),
    category TEXT,
    rule_text TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Memory Table
CREATE TABLE memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL,
    value TEXT,
    embedding BLOB,
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Logs Table
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    level TEXT CHECK(level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    module TEXT,
    action TEXT,
    success BOOLEAN,
    error_message TEXT,
    feedback TEXT
);

-- Prompts Table
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT,
    template TEXT NOT NULL,
    variables TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Code Summaries Table (for context management)
CREATE TABLE code_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    file_path TEXT NOT NULL,
    summary TEXT,
    classes TEXT,
    functions TEXT,
    imports TEXT,
    embedding BLOB,
    last_modified TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_rules_project ON rules(project_id);
CREATE INDEX idx_rules_scope ON rules(scope);
CREATE INDEX idx_memory_key ON memory(key);
CREATE INDEX idx_logs_timestamp ON logs(timestamp);
CREATE INDEX idx_logs_module ON logs(module);
CREATE INDEX idx_prompts_name ON prompts(name);
CREATE INDEX idx_code_summaries_project ON code_summaries(project_id);
CREATE INDEX idx_code_summaries_path ON code_summaries(file_path);
```

**Implementation Steps**:

1. **Create Database Manager**
   - Connection pooling
   - Transaction management
   - Query builders
   - CRUD operations
   
2. **Implement Models**
   - ORM-like classes for each table
   - Validation logic
   - Serialization/deserialization
   
3. **Create Migration System**
   - Version tracking
   - Up/down migrations
   - Schema updates
   
4. **FAISS Integration**
   - Vector store setup
   - Embedding storage/retrieval
   - Similarity search

**Testing**:
- Test all CRUD operations
- Test transactions
- Test migrations
- Test concurrent access

---

### 1.3 User Interface - CLI (2-3 days)

**Files to Create**:
- `src/ui/__init__.py`
- `src/ui/cli.py`
- `src/ui/commands.py`
- `src/ui/formatters.py`
- `tests/test_cli.py`

**CLI Commands to Implement**:

```bash
uaide init                          # Initialize UAIDE in current directory
uaide new-project <name> [options]  # Create new project
uaide generate <description>        # Generate code feature
uaide test [file]                   # Run tests
uaide fix [file]                    # Fix bugs
uaide refactor [file]               # Refactor code
uaide docs [update|generate]        # Manage documentation
uaide rules [add|list|remove]       # Manage rules
uaide config [get|set] <key>        # Configuration
uaide status                        # Show project status
uaide chat                          # Interactive AI chat mode
```

**Implementation Steps**:

1. **Create CLI Framework**
   - Use Click or argparse
   - Command routing
   - Help system
   - Auto-completion support
   
2. **Implement Core Commands**
   - Project creation
   - Code generation
   - Testing
   - Configuration
   
3. **Add Interactive Mode**
   - REPL interface
   - Command history
   - Tab completion
   
4. **Output Formatting**
   - Progress indicators
   - Color coding
   - Tables and lists
   - Error messages

**Testing**:
- Test each command
- Test error handling
- Test interactive mode
- Integration tests

---

### 1.4 Configuration System (1-2 days)

**Files to Create**:
- `src/config/__init__.py`
- `src/config/config.py`
- `src/config/defaults.py`
- `config.example.json`
- `tests/test_config.py`

**Configuration Structure**:

```json
{
  "ai": {
    "model_path": "models/llama-3-8b-q4.gguf",
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "context_length": 8192,
    "gpu_layers": 0,
    "cache_size": 100
  },
  "database": {
    "path": "data/uaide.db",
    "backup_enabled": true,
    "backup_interval": 86400
  },
  "logging": {
    "level": "INFO",
    "file": "logs/uaide.log",
    "max_size": 10485760,
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  },
  "code_generation": {
    "max_file_length": 500,
    "auto_format": true,
    "auto_import": true,
    "style_guide": "pep8"
  },
  "testing": {
    "auto_test": true,
    "coverage_threshold": 80,
    "test_framework": "pytest"
  },
  "ui": {
    "theme": "dark",
    "editor": "default",
    "auto_save": true
  }
}
```

**Implementation Steps**:

1. **Create Config Manager**
   - Load/save configuration
   - Validation
   - Environment variable support
   - Default values
   
2. **Implement Config Access**
   - Dot notation access
   - Type conversion
   - Config updates
   - Config reset

**Testing**:
- Test loading/saving
- Test validation
- Test defaults
- Test updates

---

### 1.5 Setup Script (1 day)

**Files to Create**:
- `scripts/setup.py`
- `scripts/download_model.py`
- `requirements.txt`
- `.env.example`

**Setup Script Tasks**:

1. Check Python version (>=3.12)
2. Install dependencies
3. Download AI model if needed
4. Initialize database
5. Create configuration file
6. Set up logging directory
7. Run initial tests

**requirements.txt**:
```
llama-cpp-python>=0.2.0
faiss-cpu>=1.7.4
click>=8.1.0
pydantic>=2.0.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.0
pytest>=7.4.0
black>=23.0.0
pylint>=3.0.0
```

---

### 1.6 Core Utilities (1-2 days)

**Files to Create**:
- `src/utils/__init__.py`
- `src/utils/file_ops.py`
- `src/utils/path_utils.py`
- `src/utils/validators.py`
- `src/utils/constants.py`
- `src/utils/logger.py`
- `tests/test_utils.py`

**Utility Functions Needed**:

- File operations (read, write, copy, delete)
- Path manipulation
- Code parsing utilities
- Validation functions
- Common constants
- Logging setup

---

## Deliverables

- [ ] Working AI backend that can query llama.cpp
- [ ] Functional database with all tables
- [ ] CLI interface with basic commands
- [ ] Configuration system
- [ ] Setup script
- [ ] Core utilities
- [ ] Unit tests for all components (>80% coverage)
- [ ] Documentation for Phase 1

---

## Testing Strategy

1. **Unit Tests**: Each module independently
2. **Integration Tests**: Database + AI backend
3. **CLI Tests**: Command execution
4. **Manual Testing**: End-to-end workflows

---

## Success Criteria

✅ AI backend can load model and generate responses  
✅ Database operations work correctly  
✅ CLI commands execute without errors  
✅ Configuration loads and saves properly  
✅ All tests pass  
✅ Code follows project rules (<500 lines per file)  
✅ Documentation is complete

---

## Next Steps

After Phase 1 completion, proceed to Phase 2: Basic Features
- Project Management Module
- Code Generation Module
- Testing Module
