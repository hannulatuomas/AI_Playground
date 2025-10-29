# Debug Agents & Ollama Management - Implementation Guide

## Overview

This document describes the **7 language-specific debug agents** and **Ollama management tool** that have been implemented for the AI Agent Console.

## Debug Agents

All debug agents follow a consistent architecture and integrate with the LLM routing system for intelligent debugging assistance.

### 1. Python Debug Agent (`python_debug_agent.py`)

**Purpose**: Debug Python code using pdb/ipdb integration

**Features**:
- Breakpoint management (set, clear, list)
- Step execution (step, next, continue)
- Variable inspection
- Stack trace analysis
- Exception handling and debugging
- Integration with pdb/ipdb

**Operations**:
- `set_breakpoint` - Set breakpoint at file:line
- `clear_breakpoint` - Clear specific or all breakpoints
- `list_breakpoints` - List all breakpoints
- `analyze_stack` - Analyze Python stack traces
- `inspect_variables` - Inspect variable values and types
- `debug_exception` - Debug Python exceptions
- `run_debug_session` - Generate debug script

**Model Assignment**:
- Primary: `qwen3-coder:30b` (deep code understanding)
- Fallback: `codellama:13b` (good Python support)
- Temperature: 0.4 (creative debugging insights)

---

### 2. C# Debug Agent (`csharp_debug_agent.py`)

**Purpose**: Debug C# code with .NET integration

**Features**:
- Breakpoint management for C# projects
- Stack trace analysis for .NET exceptions
- Variable inspection and watch expressions
- Integration with dotnet CLI
- Exception analysis (NullReferenceException, ArgumentException, etc.)
- Memory leak detection guidance
- Performance profiling recommendations

**Operations**:
- `set_breakpoint` - Set C# breakpoint
- `clear_breakpoint` - Clear breakpoints
- `list_breakpoints` - List all breakpoints
- `analyze_stack` - Analyze .NET stack traces
- `inspect_variables` - Inspect C# variables with type info
- `debug_exception` - Debug .NET exceptions
- `memory_analysis` - Analyze memory usage and leaks

**Model Assignment**:
- Primary: `qwen3-coder:30b` (strong C#/.NET knowledge)
- Fallback: `codellama:13b` (reasonable C# support)
- Temperature: 0.4

---

### 3. C++ Debug Agent (`cpp_debug_agent.py`)

**Purpose**: Debug C++ code using GDB/LLDB

**Features**:
- Breakpoint management for C++ code
- GDB/LLDB integration and command generation
- Core dump analysis
- Memory debugging (valgrind, sanitizers)
- Stack trace analysis for C++ exceptions
- Segfault debugging
- Memory leak detection

**Operations**:
- `set_breakpoint` - Set C++ breakpoint (generates GDB/LLDB commands)
- `clear_breakpoint` - Clear breakpoints
- `list_breakpoints` - List all breakpoints
- `analyze_stack` - Analyze C++ stack traces/backtraces
- `analyze_coredump` - Analyze core dump files
- `memory_debug` - Debug memory issues (leaks, overflows)
- `segfault_debug` - Debug segmentation faults

**Model Assignment**:
- Primary: `qwen3-coder:30b` (complex memory debugging)
- Fallback: `codellama:13b` (good C++ understanding)
- Temperature: 0.4

---

### 4. Shell Debug Agent (`shell_debug_agent.py`)

**Purpose**: Debug shell scripts (bash/zsh/sh)

**Features**:
- Bash/Zsh/Sh debugging support
- Script trace analysis (set -x)
- Variable inspection ($VAR expansion)
- Exit code debugging
- Shellcheck integration recommendations
- Common shell script pitfalls

**Operations**:
- `analyze_error` - Analyze shell script errors
- `inspect_variables` - Inspect shell variables and expansion
- `validate_syntax` - Validate syntax (integrates with shellcheck)
- `debug_exit_code` - Debug exit codes and $?
- `trace_execution` - Provide execution tracing guidance

**Model Assignment**:
- Primary: `qwen3-coder:30b` (shell script intricacies)
- Fallback: `mistral-nemo:12b` (fast for simpler debugging)
- Temperature: 0.3

---

### 5. PowerShell Debug Agent (`powershell_debug_agent.py`)

**Purpose**: Debug PowerShell scripts

**Features**:
- Breakpoint management for PowerShell
- Stack trace analysis for PowerShell errors
- Variable inspection and watch expressions
- Exception debugging (ErrorRecord, Exception)
- Cmdlet parameter validation
- Pipeline debugging

**Operations**:
- `set_breakpoint` - Set PowerShell breakpoint
- `clear_breakpoint` - Clear breakpoints
- `list_breakpoints` - List all breakpoints
- `analyze_error` - Analyze PowerShell errors and ErrorRecords
- `inspect_variables` - Inspect PowerShell variables and scopes
- `debug_pipeline` - Debug PowerShell pipelines

**Model Assignment**:
- Primary: `qwen3-coder:30b` (PowerShell-specific knowledge)
- Fallback: `mistral-nemo:12b` (fast fallback)
- Temperature: 0.3

---

### 6. Batch Debug Agent (`batch_debug_agent.py`)

**Purpose**: Debug Windows Batch scripts (.bat/.cmd)

**Features**:
- Batch script error analysis
- Command echo debugging (@ECHO ON)
- Variable value inspection (%VAR% and !VAR!)
- Exit code analysis (ERRORLEVEL)
- Syntax validation
- Common batch script errors

**Operations**:
- `analyze_error` - Analyze batch script errors
- `inspect_variables` - Inspect batch variables and expansion
- `validate_syntax` - Validate batch syntax
- `debug_exit_code` - Debug ERRORLEVEL and exit codes

**Model Assignment**:
- Primary: `mistral-nemo:12b` (fast for batch script debugging)
- Fallback: `mistral:7b` (very fast fallback)
- Temperature: 0.3

---

### 7. WebDev Debug Agent (`webdev_debug_agent.py`)

**Purpose**: Debug web development (JavaScript, TypeScript, HTML, CSS)

**Features**:
- JavaScript/TypeScript debugging (Chrome DevTools, Node.js debugger)
- React/Vue/Angular component debugging
- Browser console error analysis
- Network request debugging (fetch, AJAX, API calls)
- CSS layout debugging (Flexbox, Grid)
- HTML validation
- Frontend build error analysis

**Operations**:
- `set_breakpoint` - Set JS/TS breakpoint
- `clear_breakpoint` - Clear breakpoints
- `list_breakpoints` - List all breakpoints
- `analyze_console_error` - Analyze browser console errors
- `debug_network` - Debug network requests (CORS, 404, 500, etc.)
- `debug_css` - Debug CSS layout issues
- `debug_react` - Debug React component issues
- `validate_html` - Validate HTML markup

**Model Assignment**:
- Primary: `qwen3-coder:30b` (complex web stack debugging)
- Fallback: `codellama:13b` (good web technologies support)
- Temperature: 0.4

---

## Ollama Management Tool

### Tool: `ollama_manager.py`

**Purpose**: Manage Ollama LLM server lifecycle and health

**Features**:
- Start/stop Ollama server
- Health check before LLM connections
- List running models
- List available models
- Pull/download models from registry
- Check model status
- Server status monitoring
- Auto-start capability

**Operations**:

#### `health_check(auto_start=True)`
- Checks if Ollama server is running
- Automatically starts server if not running (when auto_start=True)
- Returns server status and available models

#### `start_server()`
- Starts Ollama server in background
- Waits for server initialization
- Returns success status and PID

#### `stop_server()`
- Stops Ollama server
- Verifies server stopped
- Returns status

#### `server_status()`
- Gets current server status
- Lists available models
- Returns connection information

#### `list_models()`
- Lists all downloaded models
- Shows model size, modified date, digest
- Returns model count

#### `list_running_models()`
- Lists currently loaded/running models
- Shows expiration time
- Returns running model count

#### `pull_model(model_name)`
- Downloads model from Ollama registry
- Shows progress output
- Timeout: 10 minutes

#### `get_model_info(model_name)`
- Gets detailed model information
- Shows modelfile, parameters, template
- Returns model details

**Configuration**:
```yaml
ollama:
  host: "http://localhost"
  port: 11434
  timeout: 120
```

**Integration with LLM Router**:

The LLM router now includes:
1. **Health check on initialization** - Automatically checks Ollama health when creating the provider
2. **Auto-start capability** - Attempts to start Ollama if not running
3. **Lazy-loaded Ollama manager** - Avoids circular imports
4. **Fallback health check** - Works even without Ollama manager

**Updated LLM Router Methods**:
- `OllamaProvider.__init__(auto_start=True)` - Accepts auto_start parameter
- `OllamaProvider.health_check(auto_start=True)` - Performs health check with optional auto-start
- `OllamaProvider.is_available()` - Now attempts auto-start if enabled

---

## Usage Examples

### Using Debug Agents

```python
from agents.python_debug_agent import PythonDebugAgent
from core.config import AppConfig

# Initialize
config = AppConfig.load()
debug_agent = PythonDebugAgent(config=config.to_dict())

# Set breakpoint
result = debug_agent.execute(
    "Set breakpoint at line 42",
    {
        'operation': 'set_breakpoint',
        'file_path': '/path/to/script.py',
        'line_number': 42
    }
)

# Analyze stack trace
result = debug_agent.execute(
    "Analyze this stack trace",
    {
        'operation': 'analyze_stack',
        'stack_trace': """Traceback (most recent call last):
  File "script.py", line 10, in <module>
    result = divide(10, 0)
ZeroDivisionError: division by zero"""
    }
)
```

### Using Ollama Manager

```python
from tools.ollama_manager import OllamaManager
from core.config import AppConfig

# Initialize
config = AppConfig.load()
manager = OllamaManager(config=config.to_dict())

# Health check with auto-start
result = manager.health_check(auto_start=True)
print(result)
# Output: {'success': True, 'message': 'Ollama server is healthy', ...}

# List available models
result = manager.list_models()
print(result['data']['models'])

# Pull a new model
result = manager.pull_model('llama2')
print(result['message'])

# Check running models
result = manager.list_running_models()
print(result['data']['models'])
```

### LLM Router with Health Check

```python
from core.llm_router import LLMRouter
from core.config import AppConfig

# Initialize (automatically performs health check and auto-starts Ollama)
config = AppConfig.load()
router = LLMRouter(config)

# Query will auto-start Ollama if needed
result = router.query("Explain Python decorators", provider="ollama")
print(result['response'])
```

---

## Configuration in config.yaml

All debug agents and the Ollama manager are configured in `config.yaml`:

```yaml
agents:
  model_assignments:
    # Debug Agents
    python_debug:
      primary: "qwen3-coder:30b"
      fallback: "codellama:13b"
      temperature: 0.4
    
    csharp_debug:
      primary: "qwen3-coder:30b"
      fallback: "codellama:13b"
      temperature: 0.4
    
    # ... (other debug agents)

tools:
  enabled_tools:
    - "web_fetch"
    - "git"
    - "ollama_manager"  # Added
```

---

## File Structure

```
ai-agent-console/
├── agents/
│   ├── python_debug_agent.py      # Python debugging
│   ├── csharp_debug_agent.py      # C# debugging
│   ├── cpp_debug_agent.py         # C++ debugging
│   ├── shell_debug_agent.py       # Shell script debugging
│   ├── powershell_debug_agent.py  # PowerShell debugging
│   ├── batch_debug_agent.py       # Batch script debugging
│   └── webdev_debug_agent.py      # Web development debugging
├── tools/
│   └── ollama_manager.py          # Ollama management tool
├── core/
│   └── llm_router.py              # Updated with health check
└── config.yaml                     # Configuration with model assignments
```

---

## Testing

To test the implementations:

```bash
# Test Ollama manager
python -c "
from tools.ollama_manager import OllamaManager
from core.config import AppConfig
config = AppConfig.load()
manager = OllamaManager(config=config.to_dict())
print(manager.health_check(auto_start=True))
"

# Test Python debug agent
python -c "
from agents.python_debug_agent import PythonDebugAgent
from core.config import AppConfig
config = AppConfig.load()
agent = PythonDebugAgent(config=config.to_dict())
result = agent.execute('List breakpoints', {'operation': 'list_breakpoints'})
print(result)
"
```

---

## Summary

✅ **7 Debug Agents Created**:
- Python, C#, C++, Shell, PowerShell, Batch, WebDev

✅ **Ollama Manager Tool Created**:
- Health check, start/stop, model management

✅ **LLM Router Updated**:
- Health check integration
- Auto-start capability
- Lazy-loaded manager

✅ **Configuration Updated**:
- Model assignments for all debug agents
- Ollama manager enabled in tools

✅ **Consistent Architecture**:
- All agents follow base agent pattern
- LLM-assisted debugging
- Error handling and logging
- Context-aware operations

---

## Next Steps

1. **Test each debug agent** with real-world debugging scenarios
2. **Verify Ollama auto-start** works on your system
3. **Pull required models** using the Ollama manager
4. **Integrate debug agents** into your workflow
5. **Customize model assignments** based on your available models

For questions or issues, refer to the individual agent files or the main README.md.
