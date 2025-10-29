# Changelog

All notable changes to the AI Agent Console project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - October 10, 2025

#### Memory System 🆕
- **Complete Memory Management System**: Implemented robust conversation history and context persistence
  - `core/memory.py`: Full-featured `MemoryManager` class with session management
  - **Session Management**: Create, retrieve, delete, and list conversation sessions
  - **Message Tracking**: Automatic tracking of user messages, agent responses, and system messages
  - **Context Retrieval**: Agents can access previous conversation history for context-aware responses
  - **Automatic Summarization**: LLM-based summarization when context window limits are exceeded
  - **Persistent Storage**: Sessions automatically saved to `memory_storage/` directory in JSON format
  - **Search Capabilities**: Search through conversation history with filters
  - **Token Management**: Automatic token counting and context window management

- **Agent Memory Integration**: Enhanced base `Agent` class with memory support
  - `memory_manager` parameter in agent initialization
  - `_get_memory_context()`: Retrieve conversation history for an agent
  - `_add_to_memory()`: Add agent responses to memory
  - `_format_memory_context_for_prompt()`: Format memory for LLM prompts
  - Backward-compatible design - agents work with or without memory

- **Orchestrator Memory Integration**: Automatic memory management during task execution
  - Auto-create memory sessions for each task execution
  - Track all user tasks and agent responses
  - Pass session ID through context for multi-turn conversations
  - Memory persistence across agent chains

- **Memory System Documentation**: Comprehensive documentation in `docs/MEMORY_SYSTEM.md`
  - Architecture overview and integration points
  - Complete API reference
  - Usage examples and best practices
  - Troubleshooting guide
  - Performance considerations

### Added - October 10, 2025

#### Model Assignments System
- **MODEL_ASSIGNMENTS.md**: Comprehensive documentation of which LLM model is assigned to which agent and why
  - Detailed reasoning for each model selection
  - Performance benchmarks and trade-offs
  - Configuration override instructions
  - Best practices and maintenance guidelines

- **Smart Default Model Assignments**: Configured optimal model assignments for all agents based on user's available Ollama models:
  - `deepseek-r1:32b` for reasoning-heavy tasks (planning, security analysis, architecture)
  - `qwen3-coder:30b` for code editing and generation tasks
  - `gemma3:27b` for general-purpose tasks
  - `qwen3:30b-a3b` for data analysis and complex reasoning
  - `mistral-nemo:12b` for faster, lighter tasks
  - `mistral:7b` for simple administrative tasks
  - Individual temperature settings per agent for optimal results

- **Config-Based Model Selection**: Enhanced base Agent class with automatic model selection from configuration
  - `_get_assigned_model()`: Retrieves primary model from config
  - `_get_fallback_model()`: Retrieves fallback model for error recovery
  - `_get_assigned_temperature()`: Retrieves optimal temperature setting
  - Automatic fallback to secondary model on primary model failure
  - Detailed logging of model selection and fallback attempts

#### New Agents

##### WebSearch Agent (`agents/web_search.py`)
- **Multi-engine web search** capability with support for:
  - DuckDuckGo (primary, privacy-friendly, no API key required)
  - Google Custom Search (requires API key)
  - Bing Search (requires API key)
- **Intelligent features**:
  - LLM-powered query refinement for better search results
  - Rate limiting to prevent API abuse
  - Search result caching for repeated queries
  - Automatic engine selection based on availability
  - Structured result output with ranking
- **Security**:
  - Rate limiting (1 second delay between requests)
  - Error handling and graceful degradation
  - HTTP fallback methods when SDK unavailable
- **Model Assignment**: Uses `mistral-nemo:12b` for fast search query processing

##### Database Agent (`agents/database.py`)
- **Multi-database support** for SQL and NoSQL databases:
  - **SQLite**: Embedded SQL database (no dependencies)
  - **MySQL/MariaDB**: Popular open-source SQL database
  - **PostgreSQL**: Advanced open-source SQL database
  - **MS SQL Server**: Microsoft SQL database (requires ODBC driver)
  - **MongoDB**: Document-oriented NoSQL database
  - **Redis**: Key-value store and cache
  - **Neo4j**: Graph database
- **Intelligent features**:
  - LLM-powered SQL query generation from natural language
  - Query validation and security checks
  - Connection pooling and management
  - Transaction support with automatic rollback on errors
  - Schema inspection and analysis
  - Parameterized queries for SQL injection prevention
- **Security**:
  - Dangerous keyword detection (DROP, DELETE, TRUNCATE, etc.)
  - Safe mode requiring confirmation for destructive operations
  - Connection validation and authentication
  - Automatic connection cleanup on agent deletion
- **Model Assignment**: Uses `qwen3:30b-a3b` for complex SQL generation and data reasoning

#### Configuration Enhancements

##### config.yaml Updates
- Added `agents.model_assignments` section with comprehensive model configurations for all agents
- Each agent can specify:
  - `primary`: Main model to use (required)
  - `fallback`: Backup model if primary unavailable (optional)
  - `temperature`: Generation temperature 0.0-2.0 (optional)
  - `max_tokens`: Maximum response tokens (optional)
- Updated `enabled_agents` list to include new agents
- Enhanced documentation with detailed comments

##### core/config.py Updates
- Added `ModelAssignment` Pydantic model for type-safe model configuration
- Added `model_assignments` field to `AgentSettings` with proper validation
- Configured `protected_namespaces = ()` to allow `model_` prefix without warnings
- Maintained full backward compatibility with existing configurations

#### Dependencies

##### New Required Dependencies
- `duckduckgo-search>=4.0.0`: DuckDuckGo web search (WebSearch agent)
- `pymysql>=1.1.0`: MySQL database support (Database agent)
- `psycopg2-binary>=2.9.9`: PostgreSQL database support (Database agent)
- `pymongo>=4.6.0`: MongoDB NoSQL database support (Database agent)
- `redis>=5.0.0`: Redis key-value store support (Database agent)
- `neo4j>=5.14.0`: Neo4j graph database support (Database agent)

##### Optional Dependencies (commented in requirements.txt)
- `pyodbc>=5.0.0`: MS SQL Server support (requires system ODBC driver)
- `pymssql>=2.2.10`: Alternative MS SQL Server support (pure Python)

### Changed

#### Base Agent Class (`agents/base.py`)
- Enhanced `_get_llm_response()` method with:
  - Automatic model selection from config
  - Automatic temperature selection from config
  - Fallback model retry logic on primary model failure
  - Improved logging with model and provider information
- Added helper methods:
  - `_get_assigned_model()`: Get primary model from config
  - `_get_fallback_model()`: Get fallback model from config
  - `_get_assigned_temperature()`: Get temperature from config
- All existing agents automatically benefit from these improvements through inheritance

#### Agent Registry (`agents/__init__.py`)
- Registered `WebSearchAgent` class
- Registered `DatabaseAgent` class
- Updated `__all__` exports to include new agents
- Maintained backward compatibility with existing agents

#### Configuration System
- Updated language_editors from LanguageEditorSettings model to Dict for flexibility
- Added support for nested model assignment configuration
- Enhanced validation and error messages

### Fixed
- Resolved Pydantic protected namespace warning for `model_assignments` field
- Improved error handling in agent model selection

### Documentation

#### New Documentation Files
1. **MODEL_ASSIGNMENTS.md**: 
   - Complete reference for model assignments
   - 19 agent model configurations documented
   - Performance benchmarks for Lenovo Thinkpad T14s
   - Configuration override examples
   - Best practices and maintenance guidelines

2. **CHANGELOG.md**: 
   - Comprehensive changelog following Keep a Changelog format
   - Detailed documentation of all changes

#### Updated Documentation
- config.yaml: Enhanced inline documentation with detailed comments
- requirements.txt: Organized dependencies by agent with explanatory comments
- All new agent files include comprehensive docstrings

### Testing
- Verified agent import and initialization
- Validated config loading and model assignments
- Confirmed agent registry operations
- Syntax validation for all new agent files
- Integration testing with base agent class

### Security
- Database agent includes SQL injection prevention
- Dangerous operation detection and safe mode
- Rate limiting for web search to prevent abuse
- Connection validation and secure credential handling
- Parameterized queries for all database operations

### Performance
- Optimized model assignments based on task complexity
- Smart temperature settings per agent type
- Automatic fallback for faster response on primary model failure
- Search result caching in WebSearch agent
- Connection pooling in Database agent

---

## Version History

### [1.0.0] - 2025-10-10

Initial improvements including:
- Model assignment system
- WebSearch agent
- Database agent
- Configuration enhancements
- Documentation improvements

---

## Migration Guide

### For Existing Users

1. **No Breaking Changes**: All existing functionality continues to work
2. **Optional New Features**: New agents can be enabled by adding to `enabled_agents` in config.yaml
3. **Model Assignments**: Automatic for all agents, but can be customized per agent in config.yaml
4. **Dependencies**: Run `pip install -r requirements.txt` to get new optional dependencies

### Enabling New Agents

Add to your `config.yaml`:

```yaml
agents:
  enabled_agents:
    - "code_planner"
    - "code_editor"
    - "git_agent"
    - "web_data"
    - "web_search"      # NEW
    - "database"        # NEW
```

### Customizing Model Assignments

Override any model assignment in `config.yaml`:

```yaml
agents:
  model_assignments:
    web_search:
      primary: "gemma3:27b"
      fallback: "mistral-nemo:12b"
      temperature: 0.5
```

---

## Contributors

- AI Agent Console Development Team
- Model assignment optimizations based on user hardware specifications

---

## Roadmap

### Planned Enhancements
- [ ] Google and Bing API integration for WebSearch agent
- [ ] Advanced database query optimization
- [ ] Visual query builder for Database agent
- [ ] Elasticsearch support
- [ ] GraphQL query generation
- [ ] Database migration tools
- [ ] Performance monitoring and analytics

---

## Support

For issues, questions, or contributions:
- Check MODEL_ASSIGNMENTS.md for model configuration questions
- Review config.yaml inline documentation for configuration help
- Consult agent docstrings for usage examples

---

**Last Updated**: October 10, 2025  
**Version**: 1.0.0
