# AI Agent Console

A production-ready AI agent orchestration system with LLM-based task analysis, multi-agent coordination, comprehensive tool integration, and persistent memory management.

## Features

### Core Infrastructure ✓
- **Configuration Management**: YAML-based config with Pydantic validation and environment variable overrides
- **LLM Routing**: Support for Ollama, llama-cpp, and OpenAI with intelligent model assignment and automatic fallback
- **Llama-cpp Integration**: ⭐ **NEW v2.5** - Direct GGUF model loading without server, GPU acceleration support, configurable context windows ([docs](docs/LLAMA_CPP_INTEGRATION.md))
- **Logging**: Comprehensive logging with file and console outputs using Rich UI
- **CLI Interface**: Typer-based command-line interface with beautiful Rich console output
- **Memory System**: Persistent conversation history and context management with automatic summarization
- **Vector Memory**: ChromaDB integration for semantic search, context-aware retrieval, and task tracking with nomic-embed-text embeddings
- **Task Orchestration**: Complex multi-step workflow management with task decomposition, specification extraction, and agent coordination
- **Task Loop Processing**: ⭐ **NEW v2.5** - Automated task lifecycle management with planning, implementation, testing, fixing, and documentation stages ([docs](docs/TASK_LOOP_PROCESSING.md))
- **Plugin System**: ⭐ **NEW v2.4** - Extensible plugin architecture for custom agents, tools, and hooks
- **Performance Benchmarks**: ⭐ **NEW v2.4** - Comprehensive benchmarking suite for performance monitoring and optimization
- **Virtual Environment Support**: ⭐ **NEW v2.5** - Automated virtual environment setup with cross-platform scripts (Linux, macOS, Windows) ([docs](docs/guides/VIRTUAL_ENV_SETUP.md))
- **Automated Versioning System**: ⭐ **NEW v2.5** - Semantic versioning with automatic bump detection, multi-file updates, and git integration ([docs](docs/guides/VERSIONING_SYSTEM.md))
- **Saved Prompts & Snippets**: ⭐ **NEW v2.5.0** - Save, manage, and reuse prompts and snippets with global/project scopes, variable substitution, tags, and import/export ([docs](docs/guides/SAVED_PROMPTS.md))
- **Windows Binary Builds**: ⭐ **NEW v2.5.0** - Pre-built Windows executables with PyInstaller, comprehensive installation guides, and automated build scripts ([docs](docs/guides/WINDOWS_INSTALLATION.md))

### Agent System ✓
The system includes **multiple specialized agent types**:

#### Core Orchestration Agents
- `task_orchestrator`: **✨NEW✨** Complex multi-step workflow orchestration with task decomposition, specification extraction, agent selection, and context management
- `code_planner`: Plans software projects and generates structures
- `code_editor`: Base code editor for file operations
- `git_agent`: Git operations (init, add, commit, push) with confirmations and **automated versioning support** ⭐ **NEW v2.5**
- `web_data`: Web data retrieval and parsing
- `web_search`: **Enhanced** multi-provider web search with intelligent fallback (DuckDuckGo, Langsearch, Google, Bing)
- `database`: Multi-database support (SQL and NoSQL)
- `data_analysis`: Data analysis with pandas and visualization
- `cybersecurity`: Security analysis and vulnerability testing

#### System Administration Agents
- `windows_admin`: Windows system administration with PowerShell integration
- `linux_admin`: Linux system administration and automation

#### Language-Specific Code Editor Agents
- `code_editor_python`: Python code generation and editing
- `code_editor_csharp`: C# code generation and editing
- `code_editor_cpp`: C++ code generation and editing
- `code_editor_shell`: Shell script generation and editing
- `code_editor_powershell`: PowerShell script generation and editing
- `code_editor_batch`: Batch script generation and editing
- `code_editor_webdev`: Web development (JS, TS, HTML, CSS, React, etc.)

#### Language-Specific Debug Agents
- `python_debug`: Python debugging and error analysis
- `csharp_debug`: C# debugging and error analysis
- `cpp_debug`: C++ debugging and error analysis
- `shell_debug`: Shell script debugging
- `powershell_debug`: PowerShell debugging
- `batch_debug`: Batch script debugging
- `webdev_debug`: Web development debugging

#### Language-Specific Build Agents
- `python_build`: Python project building (pip, poetry, setuptools)
- `csharp_build`: C# project building (MSBuild, dotnet)
- `cpp_build`: C++ project building (CMake, Make, MSBuild)
- `shell_build`: Shell script project building
- `powershell_build`: PowerShell project building
- `batch_build`: Batch script project building
- `webdev_build`: Web project building (npm, webpack, vite)

#### Testing & Quality Agents
- `code_tester`: Automated test generation and execution

#### Project Initialization Agents ✨NEW✨
- `project_init`: General project initialization for any language
- `project_init_python`: Python project initialization with proper package structure
- `project_init_csharp`: C#/.NET project initialization with .csproj and .sln files
- `project_init_webdev`: Web development project initialization (React, Vue, Angular, etc.)
- `project_init_bash`: Bash/shell script project initialization
- `project_init_powershell`: PowerShell module and script project initialization
- `project_init_cpp`: C++ project initialization with CMake support
- `project_init_batch`: Windows Batch script project initialization

**Features:**
- Creates clean project structure (no boilerplate code to remove)
- Generates comprehensive `.project_ai/` folder with:
  - `.codebase_root` marker for project root detection
  - `codebase_structure.md` for project structure documentation
  - `rules/project_preferences.md` for project-specific coding rules (highest priority)
  - `initial_plan.md` for project architecture and plans
  - `goals.md` for project objectives and success criteria
  - `todo.md` for project task tracking
- Asks clarifying questions for project requirements
- Supports multiple project types per language
- Integrates with version control
- Implements **3-level rules hierarchy** (see below)

#### API Integration Agent ✨NEW✨
- `api_agent`: API integration and testing
  - REST API support (GET, POST, PUT, DELETE, PATCH)
  - SOAP API support
  - GraphQL API support
  - Authentication support (Bearer, API Key, Basic Auth)
  - Response parsing and formatting

### Agent Architecture (v2.0) ✓

The agent system uses an **inheritance-based architecture** for better organization and code reuse:

```
agents/
├── base/                    # Base classes for all agent types
│   ├── agent_base.py       # Core Agent base class
│   ├── code_editor_base.py # Base for code editors
│   ├── build_agent_base.py # Base for build agents
│   └── debug_agent_base.py # Base for debug agents
│
├── generic/                 # Generic fallback agents
│   ├── generic_code_editor.py
│   ├── generic_build_agent.py
│   └── generic_debug_agent.py
│
└── languages/               # Language-specific implementations
    ├── python/             # Python agents
    ├── csharp/             # C# agents
    ├── cpp/                # C++ agents
    ├── web/                # Web dev agents
    ├── bash/               # Shell agents
    ├── powershell/         # PowerShell agents
    └── batch/              # Batch agents
```

**Benefits:**
- **Inheritance**: All agents inherit from specialized base classes
- **Code Reuse**: Common functionality in base classes
- **Extensibility**: Easy to add new languages
- **Fallback**: Generic agents for unsupported languages
- **Organization**: Clear structure by language and agent type

See [EXTENDING_GUIDE.md](docs/guides/EXTENDING_GUIDE.md) for detailed information on adding new language support.

### Project Context Awareness ✨NEW✨

All code-related agents (code editors, debug agents, build agents, documentation agents) now have **comprehensive project context awareness**:

#### Project Root Detection
- Agents automatically locate project root via `.codebase_root` marker
- No manual configuration needed
- Works across nested directory structures

#### Comprehensive Context Loading
When working on a project, agents automatically load and understand:
- **Project Goals** (from `.project_ai/goals.md`) - What the project aims to achieve
- **Initial Plan** (from `.project_ai/initial_plan.md`) - Architecture and design decisions
- **Current Tasks** (from `.project_ai/todo.md`) - High-priority work items
- **Codebase Structure** (from `.project_ai/codebase_structure.md`) - Project organization
- **Project Preferences** (from `.project_ai/rules/project_preferences.md`) - Project-specific coding standards

#### 3-Level Rules Hierarchy 🎯
Agents follow a clear priority order for coding standards:

1. **`project_preferences.md`** (Project-level) ← **HIGHEST PRIORITY**
   - Located in `<project>/.project_ai/rules/project_preferences.md`
   - Project-specific rules and standards
   - Overrides all other rules

2. **`user_preferences.md`** (User-level)
   - Located in `agents/languages/<lang>/user_preferences.md`
   - Your personal coding preferences
   - Applies across all your projects

3. **`best_practices.md`** (Language-level) ← Baseline
   - Located in `agents/languages/<lang>/best_practices.md`
   - Language community standards
   - Default baseline for all code

**Example:** If your project requires 2-space indentation but you usually prefer 4 spaces, the agent will use 2 spaces for that specific project while respecting your 4-space preference everywhere else.

#### Benefits
- **Contextual Code Generation**: Code aligns with project goals and architecture
- **Consistent Standards**: Project-specific rules are always followed
- **Better Decisions**: Agents understand current priorities and tasks
- **No Repetition**: Agents remember project structure and patterns
- **Seamless Collaboration**: New agents automatically understand the project context

#### Clarification Mechanisms
Agents now proactively ask for clarification when:
- Requirements are ambiguous
- Multiple implementation approaches exist
- Context is missing or incomplete
- Project goals are unclear

This ensures agents work confidently with full understanding rather than making assumptions.

### Tool System ✓
Reusable tools for agents:
- `web_fetch`: HTTP/HTTPS fetching with async support
- `git`: Git operations (gitpython with subprocess fallback)
- `ollama_manager`: Ollama LLM server management and health checks
- `mcp`: Model Context Protocol client (stdio, SSE, HTTP transports)
- `file_operations` ✨NEW✨: Comprehensive file operations (read, write, edit, move, delete)
- `filesystem`: File system operations
- `web_scraper`: Advanced web scraping and parsing
- `code_analyzer`: Code analysis and metrics

### Enhanced Web Search System ✨ENHANCED✨

The web search agent now supports **multi-provider search with intelligent fallback**:

**Supported Search Providers:**
- **DuckDuckGo** (free, no API key required) - Privacy-friendly search engine
- **Langsearch** (may require API key) - Powerful search API
- **Google Custom Search** (requires API key) - Google's search capabilities
- **Bing Search** (requires API key) - Microsoft's search engine

**Key Features:**
- **Intelligent Provider Selection**: Automatically chooses best available provider
- **Graceful Fallback**: If a provider fails, automatically tries next available provider
- **No Breaking on Missing Keys**: System never breaks due to missing API keys
- **Always Available**: DuckDuckGo serves as free fallback requiring no authentication
- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **Result Caching**: Caches search results for repeated queries
- **Multi-Engine Aggregation**: Can search across multiple engines and aggregate results

**Configuration:**
```yaml
web_search:
  provider_preference:
    - "duckduckgo"    # Free, always available
    - "langsearch"    # API-based, may require key
    - "google"        # Requires API key
    - "bing"          # Requires API key
  
  # Provider-specific settings
  langsearch:
    api_key: ""  # Optional
    endpoint: "https://api.langsearch.io/v1/search"
  
  google:
    api_key: ""              # Required for Google
    search_engine_id: ""     # Required for Google
  
  bing:
    api_key: ""  # Required for Bing
```

**Fallback Strategy:**
1. Try preferred provider from config
2. Check if provider is available (has API keys if needed)
3. On failure, mark provider as temporarily failed
4. Try next available provider in preference list
5. Always falls back to DuckDuckGo as last resort

**Usage Examples:**
```python
# Search with auto provider selection
result = web_search_agent.execute("search for Python async programming", {
    'max_results': 10
})

# Search with specific provider
result = web_search_agent.execute("latest AI news", {
    'engine': 'google',
    'max_results': 5
})

# Multi-engine search
result = web_search_agent.execute("machine learning tutorials", {
    'search_type': 'multi_engine',
    'engines': ['duckduckgo', 'google', 'bing'],
    'max_results': 5
})
```

### Workflow Automation ✨NEW✨
Comprehensive workflow automation system for complex development tasks:

**Available Workflows:**
- `new_project_workflow`: Initialize new projects with proper structure
- `new_feature_workflow`: Plan, implement, test, document, and commit features
- `refactor_workflow`: Analyze, plan, refactor, test, and commit improvements
- `extend_project_workflow`: Analyze, plan, extend, test, and commit extensions
- `debug_workflow`: Analyze, locate, fix, test, and commit bug fixes
- `test_workflow`: Create/run tests, analyze results, fix issues
- `analyze_workflow`: Comprehensive code analysis with quality reports
- `build_workflow`: Build projects with error handling and verification

**Features:**
- **Auto-Selection**: Automatically selects appropriate workflow based on task description
- **YAML-Based**: Workflows defined in easy-to-read YAML format
- **Step Dependencies**: Steps execute in correct order based on dependencies
- **Conditional Logic**: Steps can be skipped based on conditions
- **Error Handling**: Configurable error strategies (fail, continue, retry)
- **Context Passing**: Context flows between workflow steps
- **User Prompts**: Asks user when workflow selection is ambiguous

**Configuration:**
```yaml
workflows:
  enabled: true
  workflows_dir: "./orchestration/workflows/definitions"
  auto_select: true
  prompt_on_ambiguous: true
```

### Development Tools Integration ✨NEW✨
Integrated support for common development tools:

**Linting:**
- Python: pylint, flake8, ruff
- JavaScript/TypeScript: eslint
- C/C++: cpplint, cppcheck
- Shell: shellcheck
- Go: golint

**Formatting:**
- Python: black, autopep8, yapf
- JavaScript/TypeScript: prettier
- C/C++: clang-format
- Go: gofmt
- Rust: rustfmt

**Static Analysis:**
- Python: mypy (types), bandit (security), radon (complexity)
- JavaScript/TypeScript: tsc (type checking)
- C/C++: cppcheck, clang-tidy

**Code Quality:**
- Lines of code metrics
- Cyclomatic complexity
- Maintainability index
- Code duplication detection
- Overall quality score (0-100)
- Quality report generation (text, markdown, JSON)

**Features:**
- **Multi-Language Support**: Works across Python, JS/TS, C/C++, Shell, Go, Rust
- **Tool Coordination**: DevToolsManager coordinates all tools
- **Full Check**: Run all checks at once with `run_full_check()`
- **Auto-Fix**: Automatically fix formatting and linting issues
- **Quality Reports**: Generate comprehensive quality reports
- **CI/CD Ready**: Perfect for automated quality checks

**Configuration:**
```yaml
development_tools:
  enabled: true
  linter:
    auto_lint: false
    preferred_linters:
      python: "pylint"
      javascript: "eslint"
  formatter:
    auto_format: false
    preferred_formatters:
      python: "black"
      javascript: "prettier"
  quality:
    min_quality_score: 60
    max_complexity: 10
```

### Advanced Features ✓
- **Task Orchestration**: LLM-based task analysis and intelligent agent chaining with complete coding workflow awareness
- **Workflow Automation**: Automated complex development workflows with YAML definitions
- **Development Tools**: Integrated linting, formatting, static analysis, and quality metrics
- **Model Assignment**: Optimized model selection per agent based on task complexity
- **Memory Management**: Persistent conversation history with vector-enhanced semantic search
- **Saved Prompts & Snippets**: ⭐ **NEW v2.5.0** - Complete prompt management system with:
  - Global and project-scoped storage
  - Variable substitution ({{variable}} syntax)
  - Tag-based organization and filtering
  - Import/export functionality
  - Usage statistics tracking
  - 10 CLI commands for full management
  - Sample prompt library included
- **User Safety**: Comprehensive confirmation prompts for destructive operations
- **Rich UI**: Beautiful console output with progress bars, tables, and formatted results
- **Sandboxing**: Security controls for safe file and command execution

## Installation

### Quick Start with Virtual Environment (Recommended)

**Linux/macOS:**
```bash
# Clone the repository
git clone <repository-url>
cd ai-agent-console

# Setup virtual environment and install dependencies
chmod +x setup_venv.sh
./setup_venv.sh

# Activate virtual environment
source venv/bin/activate

# Configure
cp config.yaml my_config.yaml
# Edit my_config.yaml with your settings
```

**Windows (Command Prompt):**
```cmd
REM Clone the repository
git clone <repository-url>
cd ai-agent-console

REM Setup virtual environment and install dependencies
setup_venv.bat

REM Activate virtual environment
venv\Scripts\activate.bat

REM Configure
copy config.yaml my_config.yaml
REM Edit my_config.yaml with your settings
```

**Windows (PowerShell):**
```powershell
# Clone the repository
git clone <repository-url>
cd ai-agent-console

# Setup virtual environment and install dependencies
.\setup_venv.ps1

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Configure
Copy-Item config.yaml my_config.yaml
# Edit my_config.yaml with your settings
```

### Manual Installation (Without Virtual Environment)

```bash
# Clone the repository
git clone <repository-url>
cd ai-agent-console

# Install dependencies
pip install -r requirements.txt

# Configure (copy and edit config.yaml)
cp config.yaml my_config.yaml
# Edit my_config.yaml with your settings
```

📖 **For detailed virtual environment setup instructions, see [Virtual Environment Setup Guide](docs/guides/VIRTUAL_ENV_SETUP.md)**

### Windows Binary Installation (Pre-built Executable)

**✨ New!** Windows users can now use pre-built executables without installing Python!

#### Quick Start

1. **Download** the latest Windows binary release: `ai-agent-console-windows-vX.X.X.zip`
2. **Extract** the ZIP file to a folder (e.g., `C:\Program Files\AI-Agent-Console`)
3. **Configure** by editing `config.yaml` in the extracted folder
4. **Run** from Command Prompt or PowerShell:
   ```cmd
   cd "C:\Program Files\AI-Agent-Console\ai-agent-console"
   ai-agent-console.exe --help
   ```

#### Building Your Own Binary

You can build the Windows executable yourself using the provided build scripts:

**PowerShell:**
```powershell
.\build_windows.ps1
```

**Command Prompt:**
```cmd
build_windows.bat
```

The build process creates a standalone executable in `dist/ai-agent-console/` with all dependencies included.

📖 **For complete Windows installation instructions, troubleshooting, and configuration, see the [Windows Installation Guide](docs/guides/WINDOWS_INSTALLATION.md)**

## Configuration

The system uses **YAML configuration** (`config.yaml`) for all settings. See the [config.yaml](./config.yaml) file for complete configuration options.

### LLM Providers

**Option 1: Ollama (Local - Recommended)**
```bash
# Install Ollama: https://ollama.ai/
ollama serve

# Pull models (examples from config)
ollama pull llama3.2:latest
ollama pull qwen2.5-coder:latest
ollama pull deepseek-r1:latest
ollama pull phi4:latest
ollama pull mistral-small:latest
```

**Option 2: Llama-cpp (Local - Direct Model Loading)**
```bash
# Install llama-cpp-python
pip install llama-cpp-python

# Or with GPU support (NVIDIA)
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python

# Download GGUF models from Hugging Face
mkdir -p models
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf -O models/llama-2-7b-chat.gguf

# Configure in config.yaml
llamacpp:
  model_path: "./models/llama-2-7b-chat.gguf"
  context_size: 4096
  n_gpu_layers: 35  # GPU acceleration
```

See [Llama-cpp Integration Guide](docs/LLAMA_CPP_INTEGRATION.md) for detailed setup and configuration.

**Option 3: OpenAI (Cloud)**
```yaml
openai:
  api_key: "sk-..."
  base_url: "https://api.openai.com/v1"
  timeout: 120
```

Or set via environment variable:
```bash
export AI_AGENT_OPENAI__API_KEY="sk-..."
```

### Agent Configuration

```yaml
agents:
  enabled_agents:
    - "code_planner"
    - "code_editor"
    - "git_agent"
    - "web_data"
    - "web_search"
    - "database"
  auto_confirm: false  # ⚠️ Set to true to skip confirmations (dangerous!)
  max_iterations: 10
  
  # Model assignments per agent
  model_assignments:
    code_planner:
      primary: "deepseek-r1:32b"
      fallback: "gemma3:27b"
      temperature: 0.7
    code_editor_python:
      primary: "qwen3-coder:30b"
      fallback: "codellama:13b"
      temperature: 0.3
```

### Memory Configuration

Memory is automatically configured with default settings:
- **Storage**: `memory_storage/` directory
- **Context Window**: 4096 tokens (default)
- **Auto-save**: Enabled
- **Summarization**: Automatic when context exceeds limits

### Tool Configuration

```yaml
tools:
  enabled_tools:
    - "web_fetch"
    - "git"
    - "ollama_manager"
  use_gitpython: true
  web_timeout: 30
  enable_sandboxing: true
```

### Security Configuration

```yaml
security:
  require_file_confirmation: true
  require_git_confirmation: true
  require_shell_confirmation: true
  sandboxing_level: "basic"  # none, basic, strict
  allowed_file_extensions:
    - ".py"
    - ".js"
    - ".ts"
    # ... more extensions
  blocked_paths:
    - "/etc"
    - "/sys"
    # ... system directories
```

## Usage

### Check Status

```bash
python main.py status
```

Output:
```
Engine Status:
────────────────────────────────────────────────────────────
✓ Engine initialized: True
✓ Configuration loaded: True
✓ Agents system: Available
✓ Tools system: Available

LLM Providers:
────────────────────────────────────────────────────────────
  ✓ ollama

Registered Agents:
────────────────────────────────────────────────────────────
  • code_planner
  • code_editor
  • git_agent
  • web_data

Registered Tools:
────────────────────────────────────────────────────────────
  • web_fetch
  • git
```

### Execute Tasks with Auto Agent Selection

The system automatically analyzes tasks and selects appropriate agents:

```bash
# Plan and create a Python script
python main.py task "Plan and create a hello world Python script"

# Create a README
python main.py task "Create a README.md file for a Python project"

# Git operations
python main.py task "Initialize git and commit the current changes"

# Web data retrieval
python main.py task "Fetch and summarize the content from example.com"
```

### Execute Tasks with Specific Agents

Skip task analysis and specify agents manually:

```bash
# Use only code_planner
python main.py task "Plan a REST API" --agents code_planner

# Chain multiple agents
python main.py task "Create and commit hello.py" --agents code_editor,git_agent
```

### Auto-Confirm Mode (USE WITH CAUTION)

Skip all confirmation prompts:

```bash
python main.py task "Create hello.py" --auto-confirm
```

### Simple LLM Queries (Phase 1)

```bash
# Single query
python main.py run "What is the meaning of life?"

# With specific model
python main.py run "Explain quantum computing" --model llama2

# Force specific provider
python main.py run "Write a poem" --provider openai

# Interactive mode
python main.py run --interactive
```

### Saved Prompts Management

```bash
# Save a prompt
python main.py prompt-save "code-review" \
  -c "Review the following {{language}} code for best practices" \
  --tags "code,review"

# List prompts
python main.py prompt-list

# Use a prompt with variables
python main.py prompt-use "code-review" --vars "language=Python"

# View prompt details
python main.py prompt-view "code-review"

# Export prompts
python main.py prompt-export my-prompts.json

# Import prompts (including samples)
python main.py prompt-import examples/sample_prompts.json

# View statistics
python main.py prompt-stats
```

See the [Saved Prompts Guide](docs/guides/SAVED_PROMPTS.md) for complete documentation.

## Architecture

### Task Flow with Memory

```
User Input
    ↓
Engine.execute_task()
    ↓
Memory Session Creation
    ↓
TaskAnalyzer (LLM-based)
    ↓
Orchestrator
    ↓
┌──────────────────────────────────────┐
│  [Agent 1] → [Agent 2] → [Agent 3]  │
│     ↓            ↓            ↓       │
│  Memory      Memory       Memory     │
│  Update      Update       Update     │
└──────────────────────────────────────┘
    ↓
Context + Results + Session ID
    ↓
Memory Persistence
```

### Agent Architecture

```python
class Agent(ABC):
    def __init__(
        self,
        name: str,
        description: str,
        llm_router: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[Any] = None  # ✨ NEW
    ):
        self.memory_manager = memory_manager
        # ...
    
    @abstractmethod
    def execute(self, task: str, context: Dict) -> Dict:
        """Execute agent's task with given context"""
        pass
    
    # Memory helper methods
    def _get_memory_context(self, session_id: str) -> List[Dict]:
        """Retrieve conversation history from memory"""
        pass
    
    def _add_to_memory(self, session_id: str, message: str) -> bool:
        """Add agent response to memory"""
        pass
```

Each agent:
- Has access to **LLM router** for AI-powered reasoning
- Can use **tools** from tool registry
- Has access to **memory manager** for conversation history
- Receives **context** from previous agents
- Returns **results** with success status
- Automatically tracks interactions in memory

### Memory System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Memory Manager                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Session Management    │    Message Tracking            │
│  - Create sessions     │    - User messages             │
│  - Session metadata    │    - Agent responses           │
│  - Multi-session       │    - System messages           │
│                        │                                 │
│  Memory Retrieval      │    Context Management          │
│  - History access      │    - Token counting            │
│  - Search messages     │    - Window limits             │
│  - Context for agents  │    - Summarization             │
│                        │                                 │
│  Persistence          │    Advanced Features            │
│  - Auto-save          │    - Memory search              │
│  - JSON storage       │    - Context formatting         │
│  - Load/restore       │    - Cleanup utilities          │
└─────────────────────────────────────────────────────────┘
```

### Tool Architecture

```python
class Tool(ABC):
    @abstractmethod
    def invoke(self, params: Dict) -> Any:
        """Execute tool with given parameters"""
        pass
```

Tools are stateless, reusable components that agents can invoke.

**Available Tools**:
- **FileSystem**: File operations (read, write, delete, list)
- **WebFetch**: HTTP/HTTPS requests with async support
- **Git**: Version control operations
- **OllamaManager**: LLM server management
- **WebScraper**: Advanced web scraping and parsing
- **CodeAnalyzer**: Static code analysis and metrics
- **MCP**: Model Context Protocol integration

## Example: "Plan and commit a hello world script"

### Task Analysis
```
Task: "Plan and commit a hello world Python script"
Selected Agents: [code_planner, code_editor, git_agent]
Reasoning: Need to plan structure, create file, and commit changes
```

### Execution Flow

1. **CodePlannerAgent**
   - Generates project plan
   - Determines file structure
   - Identifies dependencies
   - Result: Plan with file structure

2. **CodeEditorAgent**
   - Uses plan from previous agent
   - Creates `hello.py` file
   - Shows diff/preview
   - Asks for user confirmation
   - Result: File created

3. **GitAgent**
   - Checks git status
   - Stages files (`git add`)
   - Shows commit preview
   - Asks for confirmation
   - Creates commit
   - Result: Changes committed

## Development

### Project Structure

```
ai-agent-console/
├── agents/                      # Agent system (40+ agents)
│   ├── base.py                 # Abstract Agent class with memory support
│   ├── registry.py             # Agent registry with caching
│   ├── code_planner.py         # Project planning agent
│   ├── code_editor*.py         # Code editor agents (base + language-specific)
│   ├── *_debug.py              # Debug agents (7 languages)
│   ├── build_agent_*.py        # Build agents (7 languages)
│   ├── code_tester.py          # Testing agent
│   ├── git_agent.py            # Git operations
│   ├── web_data.py             # Web data retrieval
│   ├── web_search.py           # Web search
│   ├── database.py             # Database operations
│   ├── data_analysis.py        # Data analysis
│   ├── cybersecurity.py        # Security analysis
│   └── windows_admin.py        # Windows administration
├── tools/                       # Tool system
│   ├── base.py                 # Abstract Tool class
│   ├── registry.py             # Tool registry
│   ├── web_fetch.py            # HTTP client
│   ├── git.py                  # Git operations
│   ├── filesystem.py           # File operations
│   ├── web_scraper.py          # Web scraping
│   ├── code_analyzer.py        # Code analysis
│   ├── ollama_manager.py       # Ollama management
│   └── mcp.py                  # MCP integration
├── core/                        # Core infrastructure
│   ├── config.py               # YAML configuration management
│   ├── engine.py               # Main orchestration engine
│   ├── llm_router.py           # LLM provider routing
│   └── memory.py               # ✨ Memory management system
├── docs/                        # Documentation
│   ├── README.md               # Documentation index
│   ├── user_guide.md           # User guide
│   └── MEMORY_SYSTEM.md        # ✨ Memory system documentation
├── memory_storage/              # ✨ Persistent memory storage (auto-created)
│   └── <session-id>.json       # Session files
├── logs/                        # Application logs
│   └── app.log                 # Log file
├── main.py                      # CLI entry point
├── config.yaml                  # ✨ YAML configuration file
└── requirements.txt             # Dependencies
```

### Adding a New Agent

1. Create agent class inheriting from `Agent`
2. Implement required properties and `execute()` method
3. Register in `core/engine.py` `_register_agents()`
4. Add to config.yaml `enabled_agents`

Example:

```python
from agents.base import Agent

class CustomAgent(Agent):
    @property
    def name(self) -> str:
        return "custom_agent"
    
    @property
    def description(self) -> str:
        return "Does custom things"
    
    @property
    def capabilities(self) -> list[str]:
        return ["capability1", "capability2"]
    
    def execute(self, task: str, context: Dict) -> Dict:
        # Implementation
        return {
            'success': True,
            'result': {...},
            'message': 'Task completed'
        }
```

### Adding a New Tool

1. Create tool class inheriting from `Tool`
2. Implement required properties and `invoke()` method
3. Register in `core/engine.py` `_register_tools()`
4. Add to config.yaml `enabled_tools`

Example:

```python
from tools.base import Tool

class CustomTool(Tool):
    @property
    def name(self) -> str:
        return "custom_tool"
    
    @property
    def description(self) -> str:
        return "Does custom operations"
    
    @property
    def parameters_schema(self) -> Dict:
        return {
            'type': 'object',
            'required': ['param1'],
            'properties': {
                'param1': {'type': 'string'}
            }
        }
    
    def invoke(self, params: Dict) -> Any:
        # Implementation
        return result
```

## Security

- **User Confirmations**: All destructive operations require confirmation
- **Sandboxing**: Operations limited to working directory
- **Input Validation**: Pydantic validation for all configs
- **No Root Operations**: System designed to run as regular user
- **Sensitive Data Masking**: API keys masked in logs

## Troubleshooting

### No LLM Providers Available

```bash
# Check Ollama
ollama serve
ollama list

# Or configure OpenAI
export AI_AGENT_OPENAI__API_KEY="sk-..."
```

### Agent System Not Available

```bash
# Verify imports
python -c "from agents import AgentRegistry; print('OK')"

# Check logs
cat logs/app.log
```

### Tool Execution Fails

```bash
# For git tool
git --version

# For web_fetch tool
python -c "import httpx; print('OK')"
```

## Environment Variables

Override any configuration via environment variables:

```bash
export AI_AGENT_OLLAMA__HOST="http://192.168.1.100"
export AI_AGENT_OPENAI__API_KEY="sk-..."
export AI_AGENT_LOGGING__LEVEL="DEBUG"
export AI_AGENT_AGENTS__AUTO_CONFIRM="false"
export AI_AGENT_TOOLS__WEB_TIMEOUT="60"
```

## License

[Your License Here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Memory System

The AI Agent Console includes a comprehensive memory system for conversation history and context management. Key features:

- **Persistent Storage**: Conversations saved automatically to `memory_storage/`
- **Session Management**: Organize conversations into sessions
- **Context Retrieval**: Agents can access previous conversation history
- **Automatic Summarization**: LLM-based summarization when context limits are reached
- **Search Capabilities**: Search through conversation history
- **Token Management**: Automatic token counting and context window management

For detailed documentation, see [Memory System Documentation](./docs/architecture/MEMORY_SYSTEM.md).

### Quick Example

```python
# Memory is automatically managed during task execution
result = engine.execute_task("Create a Python script")
session_id = result.get('session_id')

# Continue conversation with context
context = {'session_id': session_id}
result2 = engine.execute_task("Now add error handling", context=context)
# Agent remembers the previous script and adds error handling
```

## Documentation

📚 **Complete documentation is now organized in the [`/docs/`](./docs/) directory.**

### Quick Links

#### Getting Started
- **[Documentation Index](./docs/README.md)** - Complete documentation overview
- **[User Guide](./docs/guides/user_guide.md)** - Comprehensive usage guide
- **[Windows Installation Guide](./docs/guides/WINDOWS_INSTALLATION.md)** - ⭐ **NEW** Complete Windows setup and troubleshooting
- **[Example Usage](./docs/guides/EXAMPLE_USAGE.md)** - Practical usage examples
- **[Extending Guide](./docs/guides/EXTENDING_GUIDE.md)** - Guide for adding custom agents

#### Reference
- **[Agent Catalog](./docs/reference/AGENT_CATALOG.md)** - Complete catalog of all agents
- **[Agent Inventory](./docs/reference/AGENT_CATALOG.md)** - Detailed agent inventory
- **[Agent-Tool Guide](./docs/reference/AGENT_TOOL_GUIDE.md)** - Tool integration guide
- **[Model Assignments](./docs/reference/MODEL_ASSIGNMENTS.md)** - LLM model assignments

#### Architecture
- **[AI Context](docs/architecture/AI_CONTEXT.md)** - AI agent architecture
- **[Design Principles](./docs/architecture/DESIGN_PRINCIPLES.md)** - Core design principles
- **[Memory System](./docs/architecture/MEMORY_SYSTEM.md)** - Memory system documentation
- **[Vector Database](./docs/architecture/VECTOR_DB.md)** - Vector DB integration
- **[Rich UI Integration](./docs/architecture/RICH_UI_INTEGRATION.md)** - UI features

#### Development
- **[TODO](./docs/TODO.md)** - Current tasks and roadmap
- **[Status](./docs/development/STATUS.md)** - Current project status
- **[Changelog](./docs/development/CHANGELOG.md)** - Version history
- **[Future Improvements](./docs/development/FUTURE_IMPROVEMENTS.md)** - Planned enhancements

### Configuration
- **[Configuration File](./config.yaml)** - Full configuration reference

## Acknowledgments

- Built with Pydantic, Typer, Rich, and modern Python practices
- Supports Ollama (local) and OpenAI (cloud) LLMs
- Model Context Protocol (MCP) integration for tool extensibility
- Persistent memory management for conversation context
