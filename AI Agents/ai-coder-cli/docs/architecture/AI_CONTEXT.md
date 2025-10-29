
# AI Agent Console - AI Assistant Context

**Version:** 2.5.0  
**Last Updated:** October 14, 2025

**IMPORTANT: Architecture v2.0 Update**  
The agent system has been refactored to use an inheritance-based architecture. See the Architecture & Design section for details.

This document provides comprehensive context for AI assistants (like Claude, GPT-4, etc.) working on the AI Agent Console codebase. It explains what has been implemented, what hasn't, key architectural decisions, and how to approach working with this project.

## Table of Contents

1. [Quick Overview](#quick-overview)
2. [What Has Been Implemented](#what-has-been-implemented)
3. [What Has NOT Been Implemented](#what-has-not-been-implemented)
4. [Architecture & Design](#architecture--design)
5. [Key Patterns & Conventions](#key-patterns--conventions)
6. [Common Pitfalls](#common-pitfalls)
7. [How to Approach This Codebase](#how-to-approach-this-codebase)
8. [Critical Implementation Details](#critical-implementation-details)
9. [Testing Guidance](#testing-guidance)
10. [Quick Reference](#quick-reference)

---

## Quick Overview

**What is this?**  
A Python-based AI agent orchestration system that uses local LLMs (via Ollama and llama-cpp) and cloud LLMs (via OpenAI) to coordinate specialized agents for code generation, debugging, building, web search, database operations, and more.

**Current State:**  
✅ **Production-ready foundation** with 42 specialized agents, 8 tools, memory management, rich UI, and comprehensive configuration system.

**Technology:**  
Python 3.10+, Pydantic, Typer, Rich, Ollama, OpenAI API

**Key Feature:**  
Intelligent task decomposition → automatic agent selection → coordinated execution with memory persistence.

---

## What Has Been Implemented

### ✅ Core Infrastructure (100% Complete)

1. **Configuration System** (`core/config.py`)
   - YAML-based configuration with Pydantic validation
   - Environment variable overrides (`AI_AGENT_*`)
   - Hierarchical settings (ollama, openai, agents, tools, security, ui)
   - Type-safe with comprehensive validation
   - Backward compatible with TOML (deprecated)

2. **LLM Router** (`core/llm_router.py`)
   - Multi-provider support (Ollama, llama-cpp, OpenAI)
   - Intelligent routing with automatic fallback
   - Exponential backoff retry logic
   - Per-agent model assignments
   - Temperature control per agent
   - Health checking for providers

3. **Engine** (`core/engine.py`)
   - Central orchestration coordinator
   - Task analysis using LLM
   - Automatic agent selection
   - Agent chain execution with context passing
   - Rich UI integration for progress tracking
   - Memory session management

4. **Memory System** (`core/memory.py`, `core/vector_memory.py`) ✨ENHANCED✨
   - Persistent conversation history
   - Session management (create, retrieve, delete)
   - Automatic message tracking (user, agent, system)
   - Context retrieval for agents
   - LLM-based automatic summarization
   - JSON file persistence in `memory_storage/`
   - Token counting and window management
   - **Vector Database Integration** (`VectorMemoryManager`):
     - Semantic search across conversation history
     - Context-aware memory retrieval using embeddings
     - Task and interaction tracking in ChromaDB
     - Agent collaboration context storage
     - File reference tracking with embeddings
     - Hybrid retrieval (vector + recency + metadata)
     - nomic-embed-text:latest for embeddings

5. **Saved Prompts & Snippets** (`core/prompt_manager.py`) ⭐ **NEW v2.5.0**
   - Save and reuse prompts and code snippets
   - Global and project-scoped storage
   - Variable substitution with `{{variable}}` syntax
   - Tag-based organization and filtering
   - Import/export functionality (JSON)
   - Usage statistics tracking
   - 10 CLI commands: save, list, show, edit, delete, copy, import, export, search, use
   - Automatic variable detection
   - Sample prompt library included

### ✅ Agent System (100% Complete - 43 Agents)

**Base Infrastructure:**
- `Agent` abstract base class (`agents/base.py`)
- `AgentRegistry` singleton for management (`agents/registry.py`)
- Memory integration in all agents
- LLM integration with model assignment
- Tool access through registry

**Code Editors (8 agents):**
- `CodeEditorAgent` - Base multi-language editor
- `PythonCodeEditorAgent` - Python-specific
- `CSharpCodeEditorAgent` - C# .NET
- `CppCodeEditorAgent` - C/C++
- `WebDevCodeEditorAgent` - JS/TS/HTML/CSS/React
- `ShellScriptEditorAgent` - Bash/Zsh
- `PowerShellEditorAgent` - PowerShell
- `BatchFileEditorAgent` - Windows Batch

**Debug Agents (7 agents):**
- `PythonDebugAgent` - Python debugging
- `CSharpDebugAgent` - C# debugging
- `CppDebugAgent` - C++ debugging (GDB/LLDB)
- `ShellDebugAgent` - Shell script debugging
- `PowerShellDebugAgent` - PowerShell debugging
- `BatchDebugAgent` - Batch script debugging
- `WebDevDebugAgent` - Web debugging (DevTools, Node.js)

**Build Agents (7 agents):**
- `PythonBuildAgent` - Python (pip, poetry, setuptools)
- `CSharpBuildAgent` - C# (MSBuild, dotnet)
- `CppBuildAgent` - C++ (CMake, Make, MSBuild)
- `ShellBuildAgent` - Shell projects
- `PowerShellBuildAgent` - PowerShell modules
- `BatchBuildAgent` - Batch scripts
- `WebDevBuildAgent` - Web (npm, yarn, webpack, vite)

**Project Initialization Agents (8 agents) ✨NEW✨:**
- `GenericProjectInitAgent` - General project initialization for any language (located in agents/generic/)
- `PythonProjectInitAgent` - Python project setup (pip, poetry, pyproject.toml)
- `CSharpProjectInitAgent` - C#/.NET project setup (.csproj, .sln)
- `WebDevProjectInitAgent` - Web project setup (npm, package.json, tsconfig)
- `ShellProjectInitAgent` - Bash/shell script project setup
- `PowerShellProjectInitAgent` - PowerShell module setup (.psd1, .psm1)
- `CppProjectInitAgent` - C++ project setup (CMake, headers)
- `BatchProjectInitAgent` - Windows batch script project setup

**Core Agents (4 agents):**
- `CodePlannerAgent` - Project planning and architecture
- `CodeTesterAgent` - Test generation and execution
- `GitAgent` - Git operations with confirmations
- `PromptRefinerAgent` - Prompt optimization

**Specialized Agents (8 agents):**
- `WebDataAgent` - Web scraping and data extraction
- `WebSearchAgent` - Multi-engine search (DuckDuckGo, Google, Bing)
- `DatabaseAgent` - Multi-database ops (SQL and NoSQL)
- `DataAnalysisAgent` - Data analysis with pandas
- `CybersecurityAgent` - Security analysis
- `WindowsAdminAgent` - Windows administration
- `LinuxAdminAgent` - Linux administration
- `APIAgent` ✨NEW✨ - API integration (REST, SOAP, GraphQL)

**Orchestration & Coordination (1 agent) ✨NEW✨:**
- `TaskOrchestrator` - Complex multi-step workflow orchestration
  - Task decomposition into AI-friendly sub-tasks
  - Specification extraction (goals, rules, preferences, success measures)
  - Intelligent agent selection for tasks
  - Prompt enhancement while preserving user intent
  - Context management with vector database integration
  - Workflow execution coordination
  - Progress tracking and reporting

### ✅ Tool System (100% Complete - 8 Tools)

**Base Infrastructure:**
- `Tool` abstract base class (`tools/base.py`)
- `ToolRegistry` singleton for management (`tools/registry.py`)
- Retry logic with exponential backoff
- Parameter validation
- Sensitive data masking

**Available Tools:**
- `WebFetchTool` - HTTP/HTTPS requests with async (httpx)
- `GitTool` - Git operations (gitpython + subprocess fallback)
- `MCPClientTool` - Model Context Protocol client (stdio, SSE, HTTP)
- `OllamaManagerTool` - Ollama server management and health checks
- `LlamaCppManagerTool` - Llama-cpp direct GGUF model loading and management
- `FileOperationsTool` ✨NEW✨ - Comprehensive file operations (read, write, edit, move, delete)
- `FileSystemTool` - File I/O operations (legacy)
- `WebScraperTool` - Advanced web scraping (BeautifulSoup)
- `ShellExecTool` - Shell command execution with safety

### ✅ User Interface (100% Complete)

**CLI (Typer + Rich):**
- `main.py` - Command-line entry point
- Commands: `run`, `task`, `agents`, `tools`, `status`, `config`
- Rich console output with colors, panels, tables
- Progress bars and spinners
- Emoji support (✓, ✗, ⚠, ℹ)
- Interactive mode
- Beautiful formatted output

**Features:**
- Syntax highlighting
- Structured output (tables, panels)
- Real-time progress tracking
- Error highlighting
- Status indicators

### ✅ Security (100% Complete)

**Implemented Features:**
- File operation confirmations
- Git operation confirmations
- Shell command confirmations
- Path validation and sandboxing
- File extension whitelisting
- Command blacklisting
- SQL injection prevention (parameterized queries)
- Sensitive data masking in logs
- Configurable sandboxing levels (none, basic, strict)
- Protected system paths

### ✅ Configuration (100% Complete)

**Files:**
- `config.yaml` - Main configuration
- Environment variables for overrides

**Coverage:**
- All agents configured with model assignments
- All tools configured with settings
- Security settings
- UI settings
- Logging settings
- Retry policies
- Fallback preferences

### ✅ Documentation (Comprehensive)

**Existing Documentation:**
- `README.md` - Project overview and quick start
- `MODEL_ASSIGNMENTS.md` - LLM model assignments and rationale
- `AGENT_INVENTORY.md` - Complete agent listing
- `AGENT_TOOL_GUIDE.md` - Agent and tool usage guide
- `CHANGELOG.md` - Version history
- `docs/user_guide.md` - Comprehensive user guide
- `docs/MEMORY_SYSTEM.md` - Memory system documentation
- `docs/DESIGN_PRINCIPLES.md` - Architecture and design patterns
- `docs/EXTENDING_GUIDE.md` - Developer guide for extending
- `docs/FUTURE_IMPROVEMENTS.md` - Roadmap and enhancements
- `docs/AI_CONTEXT.md` - This file
- `docs/TODO.md` - Prioritized task list
- `docs/LLAMA_CPP_INTEGRATION.md` - Llama-cpp setup guide ⭐ NEW v2.5
- `docs/TASK_LOOP_PROCESSING.md` - Task loop system ⭐ NEW v2.5
- `docs/guides/SAVED_PROMPTS.md` - Saved prompts and snippets guide ⭐ NEW v2.5.0
- `docs/guides/VERSIONING_SYSTEM.md` - Automated versioning system ⭐ NEW v2.5.0
- `docs/guides/VIRTUAL_ENV_SETUP.md` - Virtual environment setup ⭐ NEW v2.5.0
- `docs/guides/WINDOWS_INSTALLATION.md` - Windows installation guide ⭐ NEW v2.5.0
- `docs/WINDOWS_COMPATIBILITY.md` - Windows compatibility notes ⭐ NEW v2.5.0
- `BUILD_INSTRUCTIONS.md` - Windows binary build instructions ⭐ NEW v2.5.0

---

## What Has NOT Been Implemented

### ❌ Missing Features

1. **Web Interface**
   - No web UI (only CLI exists)
   - No REST API
   - No WebSocket support
   - No web dashboard

2. **Authentication & Authorization**
   - No user authentication
   - No multi-user support
   - No API keys
   - No role-based access control
   - Single-user system only

3. **Advanced Memory Features**
   - No vector database integration
   - No semantic search (only keyword search)
   - No embeddings
   - No long-term knowledge graphs
   - No memory importance scoring

4. **Testing**
   - No comprehensive test suite
   - No unit tests (some test files exist but incomplete)
   - No integration tests
   - No CI/CD pipeline
   - No coverage tracking

5. **Monitoring & Observability**
   - No metrics collection
   - No performance monitoring
   - No dashboard for metrics
   - No alerting system
   - Basic logging only

6. **Advanced Features**
   - No workflow automation system
   - No scheduled tasks
   - No event system
   - No webhooks
   - No plugin marketplace

7. **Cloud Integration**
   - No AWS integration
   - No Azure integration
   - No GCP integration
   - No Docker/Kubernetes integration

8. **Multi-Modal**
   - No image processing
   - No audio processing
   - No video processing
   - Text-only system

### ⚠️ Partially Implemented

1. **MCP Integration**
   - Tool exists (`tools/mcp.py`)
   - Configuration defined in `config.yaml`
   - But no active MCP servers configured
   - Untested in production

2. **Code Analysis**
   - Basic code generation exists
   - No static analysis
   - No complexity metrics
   - No refactoring suggestions

3. **Error Recovery**
   - Basic retry logic exists
   - No advanced recovery strategies
   - No automatic rollback
   - Limited error classification

---

## Architecture & Design

### Core Design Philosophy

**Principles:**
1. **Modularity**: Components are independent and reusable
2. **Configuration over Code**: Behavior controlled via config.yaml
3. **Fail-Safe**: Automatic fallbacks and retry logic
4. **Security First**: Confirmations for destructive operations
5. **Memory-Aware**: All agents can access conversation history
6. **LLM-Powered**: Use AI for intelligent decisions

### Architecture Layers

```
┌─────────────────────────────────────────────┐
│           User Interface (CLI)              │
│              (main.py, Typer)               │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│            Engine (Orchestrator)            │
│  - Task Analysis (LLM)                      │
│  - Agent Selection                          │
│  - Memory Management                        │
│  - Context Passing                          │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                      │
┌───────▼───────┐    ┌────────▼────────┐
│ Agent System  │    │  Tool System    │
│ (33 agents)   │    │  (7 tools)      │
│               │    │                 │
│ - Code Editors│    │ - File I/O     │
│ - Debug       │    │ - Git          │
│ - Build       │    │ - Web Fetch    │
│ - Search      │    │ - Shell Exec   │
│ - Database    │    │ - MCP          │
│ - Security    │    │ - Ollama Mgr   │
│ - Admin       │    │ - Web Scraper  │
└───────┬───────┘    └────────┬────────┘
        │                      │
        └──────────┬───────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          Infrastructure Layer               │
│  - LLM Router (Ollama + OpenAI)            │
│  - Configuration (Pydantic)                 │
│  - Memory Storage (JSON files)              │
│  - Logging (Rich + file)                    │
└─────────────────────────────────────────────┘
```

### Refactored Agent Architecture (v2.0)

**NEW: Inheritance-Based Structure**

The agent system has been refactored into a hierarchical structure with base classes:

```
agents/
├── base/                           # Base classes for all agent types
│   ├── agent_base.py              # Core Agent ABC
│   ├── code_editor_base.py        # CodeEditorBase ABC
│   ├── build_agent_base.py        # BuildAgentBase ABC
│   └── debug_agent_base.py        # DebugAgentBase ABC
│
├── generic/                        # Generic fallback agents
│   ├── generic_code_editor.py     # For unsupported languages
│   ├── generic_build_agent.py     # Generic build support
│   └── generic_debug_agent.py     # Generic debug support
│
└── languages/                      # Language-specific implementations
    ├── python/                    # Python agents
    │   ├── code_editor.py         # PythonCodeEditorAgent
    │   ├── build_agent.py         # PythonBuildAgent
    │   └── debug_agent.py         # PythonDebugAgent
    │
    ├── csharp/                    # C# agents
    │   ├── code_editor.py         # CSharpCodeEditorAgent
    │   ├── build_agent.py         # CSharpBuildAgent
    │   └── debug_agent.py         # CSharpDebugAgent
    │
    ├── cpp/                       # C++ agents
    ├── web/                       # Web development agents
    ├── bash/                      # Bash/shell agents
    ├── powershell/                # PowerShell agents
    └── batch/                     # Batch script agents
```

**Base Classes:**

1. **CodeEditorBase**: 
   - Provides: File operations, syntax validation, formatting
   - Abstract methods: `_generate_code_content()`, `_validate_syntax()`, `_apply_formatting()`
   - Used by all code editor agents

2. **BuildAgentBase**:
   - Provides: Build system detection, test execution, clean operations
   - Abstract methods: `_detect_build_system()`, `_install_dependencies()`, `_build_package()`
   - Used by all build agents

3. **DebugAgentBase**:
   - Provides: Breakpoint management, variable inspection, exception debugging
   - Abstract methods: `_detect_debugger()`, `_set_breakpoint()`, `_analyze_stack_trace()`
   - Used by all debug agents

**Benefits:**
- **Code Reuse**: Common logic in base classes (~40% reduction in duplication)
- **Consistency**: All agents follow same patterns
- **Extensibility**: Adding new languages requires only implementing abstract methods
- **Fallback**: Generic agents handle unsupported languages
- **Maintainability**: Changes to base classes benefit all derived agents

**Migration Notes:**
- All existing agents have been refactored to use base classes
- Backward compatibility maintained through import redirects
- Old `agents/base.py` redirects to `agents/base/agent_base.py`

### Key Design Patterns

1. **Abstract Factory**: Agent and Tool base classes (enhanced with inheritance)
2. **Singleton**: Registries (AgentRegistry, ToolRegistry)
3. **Strategy**: LLM provider implementations
4. **Template Method**: Base classes define workflow, subclasses implement details (NEW)
5. **Facade**: Engine simplifies complex subsystems
6. **Chain of Responsibility**: Agent orchestration
7. **Observer**: Memory system tracks agent actions
8. **Dependency Injection**: Components receive dependencies

---

## Key Patterns & Conventions

### Agent Pattern

**Structure:**
```python
class MyAgent(Agent):
    def __init__(self, name, description, llm_router, tool_registry, config, memory_manager):
        super().__init__(...)
        # Agent-specific init
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Get memory context
        session_id = context.get('session_id')
        memory = self._get_memory_context(session_id) if session_id else []
        
        # 2. Process task (LLM or tools)
        result = self._process(task, context, memory)
        
        # 3. Add to memory
        if session_id:
            self._add_to_memory(session_id, result['message'])
        
        # 4. Return standardized result
        return self._build_success_result(message, data, next_context)
```

**Return Format (ALWAYS):**
```python
{
    'success': bool,           # True if succeeded, False if failed
    'message': str,            # Human-readable status message
    'data': Any,               # Result data (None if error)
    'next_context': dict,      # Context updates for next agent
    'error': str,              # (Optional) Error details if failed
    'error_type': str          # (Optional) Exception type if failed
}
```

### Tool Pattern

**Structure:**
```python
class MyTool(Tool):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name, description, config)
        # Tool-specific init
    
    def invoke(self, params: Dict[str, Any]) -> Any:
        # 1. Log invocation
        self._log_invocation(params)
        
        # 2. Validate params
        self.validate_params(params, ['required_param'])
        
        # 3. Perform operation
        result = self._do_operation(params)
        
        # 4. Return result (format varies by tool)
        return result
```

### Configuration Pattern

**Access:**
```python
# In agent/tool
setting = self.config.get('setting_name', default_value)

# From config.yaml
agents:
  model_assignments:
    my_agent:
      primary: "model_name"
      fallback: "fallback_model"
      temperature: 0.7
```

### Logging Pattern

**Usage:**
```python
self.logger.info(f"Operation started: {operation}")
self.logger.debug(f"Parameters: {params}")
self.logger.warning(f"Unexpected condition: {condition}")
self.logger.error(f"Operation failed: {error}")
self.logger.error(f"Critical failure: {error}", exc_info=True)  # With traceback
```

### Memory Pattern

**Usage in Agents:**
```python
def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
    session_id = context.get('session_id')
    
    # Get conversation history
    if session_id and self.memory_manager:
        memory = self._get_memory_context(session_id, max_messages=10)
        context_str = self._format_memory_context_for_prompt(memory)
        # Use context_str in your LLM prompt
    
    # Process task...
    result = self._process(task)
    
    # Add to memory
    if session_id and self.memory_manager:
        self._add_to_memory(
            session_id=session_id,
            message=result['message'],
            metadata={'operation': 'my_operation'}
        )
    
    return self._build_success_result(...)
```

---

## Common Pitfalls

### 1. Forgetting to Register Components

**Pitfall:** Creating agent/tool but not registering it

**Solution:**
- Add to `agents/__init__.py` or `tools/__init__.py`
- Add to `core/engine.py` registration methods
- Add to `config.yaml` enabled lists

### 2. Wrong Return Format

**Pitfall:** Agent returns non-standard format

**Solution:** Always use `_build_success_result()` or `_build_error_result()`

```python
# ❌ WRONG
return {'result': 'done'}

# ✅ CORRECT
return self._build_success_result(message="Task completed", data={'result': 'done'})
```

### 3. Not Handling Memory

**Pitfall:** Agent doesn't check if memory is available

**Solution:** Always check before using memory

```python
# ✅ CORRECT
if session_id and self.memory_manager:
    memory = self._get_memory_context(session_id)
```

### 4. Hard-Coding Values

**Pitfall:** Hard-coding timeouts, paths, models

**Solution:** Use configuration

```python
# ❌ WRONG
timeout = 30

# ✅ CORRECT
timeout = self.config.get('timeout', 30)
```

### 5. No Error Handling

**Pitfall:** Not catching exceptions

**Solution:** Wrap in try-except

```python
# ✅ CORRECT
try:
    result = risky_operation()
    return self._build_success_result(result)
except SpecificError as e:
    self.logger.error(f"Operation failed: {e}")
    return self._build_error_result(str(e), e)
```

### 6. Ignoring Type Hints

**Pitfall:** Missing type hints

**Solution:** Always include type hints

```python
# ✅ CORRECT
def method(self, param: str, count: int = 10) -> Dict[str, Any]:
    pass
```

### 7. Missing Docstrings

**Pitfall:** No docstrings on classes/methods

**Solution:** Add Google-style docstrings

```python
def method(self, param: str) -> int:
    """
    Short description.
    
    Args:
        param: Parameter description
        
    Returns:
        Return value description
    """
    pass
```

### 8. Not Using Base Class Methods

**Pitfall:** Reimplementing functionality

**Solution:** Use base class helpers

```python
# ✅ USE BASE CLASS METHODS
self._log_action("Operation", details)
self._get_tool('tool_name')
self._get_llm_response(prompt)
self._build_success_result(message, data)
```

---

## How to Approach This Codebase

### When Adding a New Agent

1. **Understand the Domain**: Research what the agent should do
2. **Check Existing Agents**: Look at similar agents as examples
3. **Copy Template**: Use an existing agent as a template
4. **Implement Execute**: Focus on the `execute()` method
5. **Use LLM or Tools**: Decide if agent needs LLM, tools, or both
6. **Handle Memory**: Add memory integration
7. **Register Everywhere**: Don't forget registration steps
8. **Test Manually**: Use `python main.py task "test task" --agents my_agent`
9. **Document**: Update AGENT_INVENTORY.md

### When Adding a New Tool

1. **Define Operations**: What actions should the tool support?
2. **Check Existing Tools**: Look at similar tools
3. **Copy Template**: Use an existing tool as template
4. **Implement Invoke**: Focus on the `invoke()` method
5. **Validate Params**: Always validate parameters
6. **Handle Errors**: Comprehensive error handling
7. **Register Everywhere**: Registration in multiple places
8. **Test Directly**: Test tool.invoke() directly
9. **Document**: Update documentation

### When Modifying Core

1. **Understand Impact**: Core changes affect everything
2. **Test Thoroughly**: Test with multiple agents
3. **Backward Compatibility**: Don't break existing agents
4. **Update Documentation**: Update all affected docs
5. **Version Control**: Commit frequently

### When Debugging

1. **Check Logs**: Look at `logs/app.log`
2. **Enable Debug**: Set `logging.level: "DEBUG"` in config.yaml
3. **Test Components**: Test agents/tools in isolation
4. **Use Breakpoints**: Python debugger
5. **Check Registration**: Ensure components are registered
6. **Verify Config**: Use `python main.py config --show`

---

## Critical Implementation Details

### 1. Agent Execution Flow

```
User Command
    ↓
Engine.execute_task()
    ↓
Memory Session Created (if not provided)
    ↓
TaskAnalyzer.analyze() [LLM selects agents]
    ↓
Orchestrator.execute()
    ↓
For each agent:
    1. context.update({'session_id': session_id})
    2. result = agent.execute(task, context)
    3. if not result['success']: break
    4. context.update(result['next_context'])
    ↓
Memory Auto-Saved
    ↓
Results Formatted (Rich UI)
    ↓
Displayed to User
```

### 2. LLM Query Flow

```
agent._get_llm_response(prompt)
    ↓
Get assigned model from config
    ↓
Get assigned temperature from config
    ↓
Try primary model
    ↓
If fails → Try fallback model
    ↓
If still fails → Raise exception
    ↓
Return result dict with 'response', 'model', 'provider'
```

### 3. Memory Flow

```
Engine creates session
    ↓
Session ID passed in context
    ↓
User message added to memory
    ↓
Agent retrieves memory context
    ↓
Agent processes with context
    ↓
Agent adds result to memory
    ↓
Session auto-saved to memory_storage/
```

### 4. Configuration Loading

```
Load config.yaml (or legacy config.toml fallback)
    ↓
Parse with Pydantic models
    ↓
Apply environment variable overrides (AI_AGENT_*)
    ↓
Validate all settings
    ↓
Create AppConfig instance
    ↓
Pass to Engine, Agents, Tools
```

### 5. Tool Invocation

```
agent._get_tool('tool_name')
    ↓
Registry returns tool instance
    ↓
agent calls tool.invoke(params)
    ↓
Tool validates params
    ↓
Tool performs operation
    ↓
Tool returns result
    ↓
Agent processes result
```

---

## Testing Guidance

### Manual Testing

**Test a New Agent:**
```bash
# Register agent first, then:
python main.py task "test task" --agents my_new_agent
```

**Test with Auto-Confirm (skip prompts):**
```bash
python main.py task "test task" --auto-confirm
```

**Test with Specific Model:**
```yaml
# In config.yaml
agents:
  model_assignments:
    my_agent:
      primary: "llama3.3:latest"  # Change to test different models
```

**Check Agent Registration:**
```bash
python main.py agents --verbose
```

**Check Tool Registration:**
```bash
python main.py tools --verbose
```

**View Configuration:**
```bash
python main.py config --show
```

### Unit Testing (When Implemented)

**Structure:**
```python
import pytest
from unittest.mock import Mock

def test_agent_success():
    agent = MyAgent()
    result = agent.execute("test task", {})
    assert result['success'] == True

def test_agent_with_mock_llm():
    mock_llm = Mock()
    mock_llm.query.return_value = {'response': 'test'}
    agent = MyAgent(llm_router=mock_llm)
    result = agent.execute("test", {})
    assert result['success'] == True
```

---

## Quick Reference

### File Locations

- **Core**: `core/*.py`
- **Agents**: `agents/*.py`
- **Tools**: `tools/*.py`
- **Config**: `config.yaml`
- **CLI**: `main.py`
- **Docs**: `docs/*.md`
- **Memory**: `memory_storage/*.json`
- **Logs**: `logs/app.log`

### Key Classes

- `Agent` - Base agent class
- `Tool` - Base tool class
- `Engine` - Main orchestrator
- `LLMRouter` - LLM provider routing
- `MemoryManager` - Memory management
- `AppConfig` - Configuration model

### Key Methods

**Agent:**
- `execute()` - Main execution method
- `_get_llm_response()` - Query LLM
- `_get_tool()` - Get tool from registry
- `_get_memory_context()` - Get conversation history
- `_add_to_memory()` - Add to memory
- `_build_success_result()` - Build success dict
- `_build_error_result()` - Build error dict

**Tool:**
- `invoke()` - Main invocation method
- `validate_params()` - Validate parameters
- `invoke_with_retry()` - Invoke with retry logic

**Engine:**
- `execute_task()` - Execute task with agents
- `get_status()` - Get system status

### Environment Variables

```bash
export AI_AGENT_OLLAMA__HOST="http://localhost"
export AI_AGENT_OPENAI__API_KEY="sk-..."
export AI_AGENT_LOGGING__LEVEL="DEBUG"
export AI_AGENT_AGENTS__AUTO_CONFIRM="false"
```

### Common Commands

```bash
# Run task
python main.py task "create a Python script"

# Specify agents
python main.py task "task" --agents code_planner,code_editor

# Auto-confirm
python main.py task "task" --auto-confirm

# List agents
python main.py agents

# List tools
python main.py tools

# Check status
python main.py status

# View config
python main.py config --show

# Interactive mode
python main.py run --interactive
```

---

## Summary

**For AI Assistants:**

1. **Implemented**: 33 agents, 7 tools, memory system, LLM routing, rich UI, comprehensive config
2. **Not Implemented**: Web UI, authentication, testing, advanced memory (vectors), monitoring
3. **Patterns**: Abstract base classes, registries, dependency injection, standard return formats
4. **Critical**: Always use base class methods, handle memory, return standard format, register everywhere
5. **Testing**: Manual testing via CLI, unit tests not yet implemented
6. **Documentation**: Comprehensive docs in `docs/` directory
7. **Common Issues**: Forgetting registration, wrong return format, not handling memory

**Start Here:**
- Read `README.md` for overview
- Check `agents/base.py` for agent pattern
- Look at existing agents as examples
- Follow `EXTENDING_GUIDE.md` for development

**Key Insight:**  
This is a well-structured, production-ready foundation. The architecture is solid, patterns are consistent, and extending is straightforward. The main gaps are in testing, advanced features, and web interface. When working on this codebase, follow the existing patterns closely—they're well thought out.

---

**Version:** 1.0.0  
**Last Updated:** October 10, 2025  
**For AI Assistants:** Claude, GPT-4, and other LLMs working on this codebase  
**Maintained by:** AI Agent Console Development Team




---

## Project Context Awareness (v2.1)

### Overview

All code-related agents now have comprehensive project context awareness, enabling them to understand project goals, architecture, current tasks, and coding standards automatically.

### Project Root Detection

Agents automatically locate the project root by searching for the `.codebase_root` marker file:

- Searches upward from the current working directory
- No manual configuration required
- Works across nested directory structures
- Falls back gracefully if marker not found

### .project_ai Structure

When a project is initialized, a comprehensive `.project_ai` folder is created with:

#### 1. `.codebase_root`
- Marker file at project root
- Helps agents locate project root quickly
- Empty file with explanatory comments

#### 2. `codebase_structure.md`
- Documents project structure and organization
- Automatically maintained by agents
- Provides context for code generation

#### 3. `rules/project_preferences.md` ⭐ HIGHEST PRIORITY
- Project-specific coding standards
- Overrides user_preferences.md and best_practices.md
- Customizable per project
- Examples: indentation, naming conventions, architecture patterns

#### 4. `initial_plan.md`
- Initial project plan and architecture
- Technology stack decisions
- Key architectural choices
- Development phases

#### 5. `goals.md`
- Project goals and objectives
- Success criteria and measures
- Long-term vision
- Helps agents align work with project objectives

#### 6. `todo.md`
- Project task list
- High/medium/low priority tasks
- Backlog and completed items
- Helps agents understand current priorities

### 3-Level Rules Hierarchy

Agents follow a clear priority order for coding standards:

**Priority 1 (Highest): Project Preferences**
- Location: `<project>/.project_ai/rules/project_preferences.md`
- Scope: This specific project only
- Use: Project-specific rules and standards
- **Always takes precedence**

**Priority 2: User Preferences**
- Location: `agents/languages/<lang>/user_preferences.md`
- Scope: All projects by this user
- Use: Personal coding preferences
- Overrides best practices only

**Priority 3 (Baseline): Best Practices**
- Location: `agents/languages/<lang>/best_practices.md`
- Scope: Language-level defaults
- Use: Community standards and conventions
- Applied when no higher-priority rules exist

### Context Loading in Agents

All code-related base classes now inherit from `CodebaseAwarenessMixin`:

- `CodeEditorBase` - Loads context when editing code
- `DebugAgentBase` - Loads context when debugging
- `BuildAgentBase` - Loads context when building
- `DocumentationAgentBase` - Loads context when documenting

**Context Loading Process:**
1. Agent execution starts
2. `ensure_codebase_awareness_initialized()` called
3. Project root located via `.codebase_root` marker
4. All context files loaded from `.project_ai/`
5. Context included in LLM prompts automatically

### Helper Methods for Agents

**CodebaseAwarenessMixin Methods:**
- `find_project_root()` - Locate project root
- `load_project_context()` - Load all context files
- `get_project_context_for_prompt()` - Format context for LLM
- `load_project_preferences()` - Load project-specific rules
- `load_project_goals()` - Load project goals
- `load_initial_plan()` - Load initial plan
- `load_project_todo()` - Load task list

**Example Usage in Agent:**
```python
# In _generate_code_content method
base_prompt = "Generate a Python function that..."
enriched_prompt = self._get_enriched_prompt_context(base_prompt)
# enriched_prompt now includes project context automatically
```

### Clarification Mechanisms

New `clarification_templates.py` module provides:

- `ClarificationTemplate` - Templates for common clarification scenarios
- `ambiguous_requirements()` - When requirements unclear
- `multiple_approaches()` - When multiple solutions exist
- `missing_context()` - When context incomplete
- `validate_understanding()` - Confirm understanding before proceeding
- `project_context_missing()` - When .project_ai not found

**Usage Example:**
```python
from agents.utils.clarification_templates import ClarificationTemplate

# When requirements are unclear
message = ClarificationTemplate.ambiguous_requirements(
    agent_name=self.name,
    task_description=task,
    ambiguous_aspects=[
        "Which database to use?",
        "Should include authentication?",
        "What's the target API version?"
    ]
)
return self._build_clarification_result(message)
```

### Benefits

1. **Contextual Code Generation** - Code aligns with project goals and architecture
2. **Consistent Standards** - Project-specific rules always followed
3. **Better Decision Making** - Agents understand priorities and trade-offs
4. **No Repetition** - Project structure and patterns remembered
5. **Seamless Collaboration** - New agents understand project immediately
6. **Proactive Clarification** - Agents ask questions instead of guessing

### Migration Guide

**For Existing Projects:**
1. Run a `project_init` agent to create `.project_ai` structure
2. Customize `rules/project_preferences.md` with project standards
3. Fill in `goals.md` with project objectives
4. Update `todo.md` with current tasks

**For New Language Support:**
1. Create `best_practices.md` for language baseline
2. Create `user_preferences.md` for your preferences
3. Inherit from appropriate base class with `CodebaseAwarenessMixin`
4. Use `_get_enriched_prompt_context()` in code generation

### Implementation Details

**Files Modified:**
- `agents/utils/codebase_awareness.py` - Extended with context loading functions
- `agents/base/project_init_base.py` - Creates full .project_ai structure
- `agents/base/code_editor_base.py` - Added project context awareness
- `agents/base/debug_agent_base.py` - Added project context awareness  
- `agents/base/build_agent_base.py` - Added project context awareness
- `agents/base/documentation_agent.py` - Added project context awareness
- `agents/utils/clarification_templates.py` - NEW: Clarification mechanisms

**API Additions:**
- `create_project_ai_structure()` - Create complete .project_ai folder
- `load_project_context()` - Load all context files
- `get_rules_hierarchy_context()` - Format rules hierarchy for prompts
- `load_project_preferences()` - Load project-level preferences
- `get_project_context_for_prompt()` - Format project context for LLM

---

**Last Updated:** October 12, 2025
**Version:** 2.1 - Project Context Awareness



---

## Version 2.2 Updates - Workflow Automation & Development Tools

**Date:** October 12, 2025

### New Feature: Workflow Automation System

The AI Agent Console now includes a comprehensive workflow automation system that allows complex development workflows to be defined, discovered, and executed automatically.

**Key Components:**

1. **BaseWorkflow Class** (`orchestration/workflows/base_workflow.py`)
   - Foundation for all workflow definitions
   - WorkflowStep class for individual steps
   - Support for dependencies, conditions, and error handling
   - Status tracking and progress reporting

2. **WorkflowManager** (`orchestration/workflows/workflow_manager.py`)
   - Discovers workflows from YAML definitions
   - Auto-selects workflows based on task description
   - Prompts user when selection is ambiguous
   - Executes workflows by coordinating agents
   - Tracks active workflows and execution state

3. **Default Workflows** (`orchestration/workflows/definitions/`)
   - `new_project_workflow.yaml` - Initialize new projects
   - `new_feature_workflow.yaml` - Implement new features
   - `refactor_workflow.yaml` - Code refactoring
   - `extend_project_workflow.yaml` - Extend existing projects
   - `debug_workflow.yaml` - Debug and fix issues
   - `test_workflow.yaml` - Test suite execution
   - `analyze_workflow.yaml` - Comprehensive code analysis
   - `build_workflow.yaml` - Project building

**Workflow Features:**
- Step dependencies (steps wait for dependencies to complete)
- Conditional execution (steps can have conditions)
- Error handling strategies (fail, continue, retry)
- Context passing between steps
- Integration with task orchestrator
- YAML-based workflow definitions

**Configuration:**
- Added `workflows` section to config.yaml
- Configurable workflow directory
- Auto-selection and LLM-based selection options
- Workflow execution settings

### New Feature: Development Tools Integration

Integrated support for common development tools including linters, formatters, static analyzers, and code quality metrics.

**Key Components:**

1. **LinterTool** (`tools/development/linter_tool.py`)
   - Multi-language linting support
   - Supports: pylint, flake8, ruff, eslint, shellcheck, golint, etc.
   - JSON and text output parsing
   - File and directory linting

2. **FormatterTool** (`tools/development/formatter_tool.py`)
   - Multi-language code formatting
   - Supports: black, prettier, autopep8, yapf, clang-format, gofmt, rustfmt
   - Dry-run mode for checking without modifying
   - File and directory formatting

3. **StaticAnalyzerTool** (`tools/development/static_analyzer_tool.py`)
   - Static code analysis
   - Supports: mypy, bandit, radon, tsc, cppcheck, clang-tidy
   - Type checking, security analysis, complexity analysis
   - JSON and text output parsing

4. **CodeQualityTool** (`tools/development/code_quality_tool.py`)
   - Code quality metrics
   - Lines of code, complexity, maintainability index
   - Code duplication detection
   - Overall quality score (0-100)
   - Report generation (text, markdown, JSON)

5. **DevToolsManager** (`tools/development/dev_tools_manager.py`)
   - Central coordinator for all dev tools
   - `run_full_check()` - Runs all checks
   - Individual tool access (lint, format, analyze, measure_quality)
   - Tool status checking
   - Result aggregation and summarization

**Language Support:**
- Python (pylint, flake8, ruff, black, autopep8, mypy, bandit, radon)
- JavaScript/TypeScript (eslint, prettier, tsc)
- C/C++ (cpplint, cppcheck, clang-format, clang-tidy)
- Shell (shellcheck)
- Go (golint, gofmt)
- Rust (rustfmt)

**Configuration:**
- Added `development_tools` section to config.yaml
- Configurable linter, formatter, and analyzer preferences
- Quality thresholds (min_quality_score, max_complexity, etc.)
- Auto-format and auto-lint options

### Enhanced Task Orchestration

**Updates to Task Orchestrator** (`agents/generic/task_orchestrator.py`):

1. **Enhanced Agent Selection**
   - Complete coding workflow awareness
   - Language-specific agent selection
   - Support for all specialized agents:
     * Project initialization (by language)
     * Code planning
     * Code editing (by language)
     * Code analysis
     * Debugging (by language)
     * Testing (by language)
     * Building (by language)
     * Documentation
     * Git operations

2. **Language Detection**
   - Automatic language detection from specifications
   - Tech stack detection
   - Keyword-based language inference
   - Language-specific agent mapping

3. **Workflow Integration**
   - Task orchestrator can use workflow automation
   - Automatic workflow selection based on task type
   - Workflow execution coordination

### Integration Points

**How Workflows Integrate:**
1. User provides high-level task
2. Task orchestrator analyzes task
3. WorkflowManager selects appropriate workflow
4. Workflow executes steps using agents
5. Results tracked and reported

**How DevTools Integrate:**
1. Code editor agents can use DevToolsManager
2. Build agents use linters and formatters
3. Debug agents use static analyzers
4. Code analysis agents use CodeQualityTool
5. Quality checks in workflows

### File Structure Changes

```
ai-agent-console/
├── orchestration/                    # NEW
│   ├── __init__.py
│   └── workflows/
│       ├── __init__.py
│       ├── base_workflow.py         # BaseWorkflow class
│       ├── workflow_manager.py      # WorkflowManager
│       └── definitions/             # Workflow YAML files
│           ├── new_project_workflow.yaml
│           ├── new_feature_workflow.yaml
│           ├── refactor_workflow.yaml
│           ├── extend_project_workflow.yaml
│           ├── debug_workflow.yaml
│           ├── test_workflow.yaml
│           ├── analyze_workflow.yaml
│           └── build_workflow.yaml
└── tools/
    └── development/                  # NEW
        ├── __init__.py
        ├── linter_tool.py
        ├── formatter_tool.py
        ├── static_analyzer_tool.py
        ├── code_quality_tool.py
        └── dev_tools_manager.py
```

### Configuration Updates

**New config.yaml sections:**
1. `development_tools` - Development tools configuration
2. `workflows` - Workflow automation configuration

### Usage Examples

**Using Workflows:**
```python
from orchestration.workflows import WorkflowManager

# Initialize manager
wf_manager = WorkflowManager(
    workflows_dir=Path("./orchestration/workflows/definitions"),
    agent_registry=agent_registry
)

# Auto-select workflow
workflow_id = wf_manager.select_workflow("Create a new Python project")

# Execute workflow
result = await wf_manager.execute_workflow(
    workflow_id,
    context={'project_name': 'my_app'}
)
```

**Using DevTools:**
```python
from tools.development import DevToolsManager

# Initialize manager
dev_tools = DevToolsManager(config)

# Run full check
results = dev_tools.run_full_check(
    target_path=Path("./src"),
    language="python",
    fix_issues=True
)

# Generate quality report
report = dev_tools.generate_quality_report(
    project_path=Path("."),
    output_format="markdown"
)
```

### Best Practices

**Creating Custom Workflows:**
1. Define workflow in YAML with clear steps
2. Specify dependencies between steps
3. Use appropriate agents for each step
4. Add error handling strategies
5. Include conditions for optional steps
6. Test workflow with sample projects

**Using Development Tools:**
1. Configure preferred tools in config.yaml
2. Run checks before committing
3. Use auto-format for consistency
4. Review quality reports regularly
5. Set quality thresholds for CI/CD
6. Integrate with build workflows

### Vector Database Integration Status

The vector database integration is now **FULLY COMPLETE** and integrated with:
- ✅ Agent system (agents can store and retrieve context)
- ✅ Memory system (VectorMemoryManager in use)
- ✅ Task orchestrator (uses VectorMemoryManager)
- ✅ Document retrieval for best practices, user preferences

---

**Version:** 2.2 - Workflow Automation & Development Tools
**Last Updated:** October 12, 2025
