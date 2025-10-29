# AI Agent Console - Agent & Tool System Guide

## Overview

The AI Agent Console now includes a complete **Agent and Tool system** for orchestrating complex tasks through autonomous agents. This guide explains how to use the new capabilities.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Available Agents](#available-agents)
3. [Available Tools](#available-tools)
4. [CLI Commands](#cli-commands)
5. [Usage Examples](#usage-examples)
6. [Extending the System](#extending-the-system)
7. [Configuration](#configuration)

---

## Architecture

### Agent System

**Agents** are autonomous components that perform specific high-level tasks:

```
User Task → TaskAnalyzer → Orchestrator → Agent Chain → Results
                  ↓              ↓
             (LLM-based)    (Context passing)
```

- **TaskAnalyzer**: Uses LLM to analyze tasks and select appropriate agents
- **Orchestrator**: Chains agents together and passes context between them
- **AgentRegistry**: Manages agent discovery and instantiation

### Tool System

**Tools** provide low-level utilities that agents can use:

```
Agent → ToolRegistry → Tool → Operation → Result
           ↓
    (Dynamic lookup)
```

- **ToolRegistry**: Singleton registry for all available tools
- **Tools**: Concrete implementations (web_fetch, git, mcp)

---

## Available Agents

### 1. **CodePlannerAgent** (`code_planner`)

Generates project structures and implementation plans using LLM.

**Capabilities:**
- Analyze project requirements
- Generate file structures
- Suggest technology stacks
- Create step-by-step implementation plans
- Recommend best practices

**Example Output:**
```json
{
  "overview": "Simple Python web scraper",
  "tech_stack": {
    "language": "python",
    "frameworks": ["requests", "beautifulsoup4"]
  },
  "files": [
    {
      "path": "scraper.py",
      "purpose": "Main scraping logic",
      "priority": "high"
    }
  ],
  "dependencies": [...],
  "steps": [...]
}
```

---

### 2. **CodeEditorAgent** (`code_editor`)

Creates and modifies code files with user confirmation.

**Capabilities:**
- Create new files
- Modify existing files
- Generate code using LLM
- Support multiple programming languages
- Security: File path validation and confirmation prompts

**Configuration:**
- `require_file_confirmation`: Ask before file operations (default: true)
- `allowed_file_extensions`: Whitelist of allowed extensions
- `blocked_paths`: System paths to protect

---

### 3. **GitAgent** (`git_agent`)

Handles Git version control operations.

**Capabilities:**
- Initialize repositories (`git init`)
- Stage files (`git add`)
- Create commits (`git commit`)
- Push to remote (`git push`)
- Check status (`git status`)

**Configuration:**
- `require_git_confirmation`: Ask before git operations (default: true)
- `use_gitpython`: Use gitpython library vs subprocess (default: true)

**Security:** Confirmations for destructive operations (commit, push, reset)

---

### 4. **WebDataAgent** (`web_data`)

Fetches and processes web content.

**Capabilities:**
- Fetch data from URLs
- Parse HTML with BeautifulSoup
- Extract structured data
- Handle various content types (HTML, JSON, text)
- Timeout and retry support

**Example Usage:**
```python
# Fetches web data, extracts text and links
result = web_data_agent.execute(
    task="Fetch data from https://example.com",
    context={}
)
```

---

## Available Tools

### 1. **WebFetchTool** (`web_fetch`)

Async HTTP requests using httpx with HTML parsing.

**Actions:**
- `fetch`: Fetch URL content with optional parsing
- `parse`: Parse HTML content

**Parameters:**
```python
{
    "action": "fetch",
    "url": "https://example.com",
    "parse": True,          # Parse HTML with BeautifulSoup
    "extract_text": True    # Extract text content
}
```

**Configuration:**
- `web_timeout`: Request timeout in seconds (default: 30)
- `user_agent`: Custom user agent string

---

### 2. **GitTool** (`git`)

Git operations using gitpython library.

**Actions:**
- `init`: Initialize repository
- `status`: Get repository status
- `add`: Stage files
- `commit`: Create commit
- `push`: Push to remote

**Parameters:**
```python
{
    "action": "commit",
    "path": ".",
    "message": "Update files"
}
```

**Configuration:**
- `enable_sandboxing`: Enable path validation (default: true)
- `sandbox_working_directory`: Restrict operations to directory

---

### 3. **MCPClientTool** (`mcp`)

Model Context Protocol client for external tool integration.

**Transports:**
- **stdio**: Spawn subprocess
- **sse**: Server-Sent Events
- **http**: HTTP REST API

**Actions:**
- `connect`: Connect to MCP server
- `discover`: Discover available tools
- `invoke_tool`: Invoke remote tool
- `disconnect`: Disconnect from server

**Example Configuration (config.yaml):**
```yaml
mcp:
  enabled: true
  servers:
    - server_id: "local_tools"
      transport: "stdio"
      endpoint: "/usr/local/bin/mcp-server"
      auto_connect: true
      timeout: 30
```

---

## CLI Commands

### 1. List Available Agents

```bash
# Simple list
python main.py agents

# Detailed information
python main.py agents --verbose
```

**Output:**
```
Available Agents (4):
═══════════════════════════════════════════════════════════
  • code_planner
  • code_editor
  • git_agent
  • web_data
```

---

### 2. List Available Tools

```bash
# Simple list
python main.py tools

# Detailed information
python main.py tools --verbose
```

**Output:**
```
Available Tools (2):
═══════════════════════════════════════════════════════════
  • web_fetch
  • git
```

---

### 3. Execute Task (Agent Orchestration)

```bash
# Automatic agent selection
python main.py task "Plan and create a hello world Python script"

# Manual agent specification
python main.py task "Create README.md" --agents code_editor

# Auto-confirm all actions (USE WITH CAUTION!)
python main.py task "Commit changes" --auto-confirm
```

**Task Execution Flow:**
1. **Task Analysis**: LLM analyzes task and selects agents
2. **Orchestration**: Agents execute in sequence
3. **Context Passing**: Results flow between agents
4. **Confirmation**: User confirms file/git operations (unless auto-confirm)

---

### 4. Check System Status

```bash
python main.py status
```

**Output:**
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

---

## Usage Examples

### Example 1: Plan and Implement a Feature

```bash
python main.py task "Plan and create a Python calculator with add, subtract, multiply, divide functions"
```

**What Happens:**
1. TaskAnalyzer selects: `code_planner` → `code_editor`
2. CodePlannerAgent creates implementation plan
3. CodeEditorAgent generates `calculator.py` (with confirmation)
4. Results displayed to user

---

### Example 2: Web Scraping Task

```bash
python main.py task "Fetch and summarize content from https://example.com"
```

**Agent Chain:**
- `web_data`: Fetches URL content
- `code_planner` (optional): Analyzes content structure

---

### Example 3: Complete Git Workflow

```bash
# Step 1: Create files
python main.py task "Create a README.md file"

# Step 2: Initialize git and commit
python main.py task "Initialize git repository and commit all changes with message 'Initial commit'"
```

**Agent Chain:**
- `code_editor`: Creates README.md
- `git_agent`: Runs git init, add, commit

---

## Extending the System

### Creating a New Agent

```python
# agents/my_agent.py
from agents.base import Agent
from typing import Dict, Any

class MyCustomAgent(Agent):
    """Custom agent that does something special."""
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom logic."""
        self._log_action("Starting custom task", task[:100])
        
        try:
            # Your agent logic here
            result = self._perform_task(task, context)
            
            return self._build_success_result(
                message="Task completed successfully",
                data=result,
                next_context={'custom_data': result}
            )
            
        except Exception as e:
            return self._build_error_result(f"Task failed: {e}", e)
    
    def _perform_task(self, task: str, context: Dict[str, Any]) -> Any:
        """Implement your agent's core functionality."""
        # Use self._get_llm_response() for LLM queries
        # Use self._get_tool() to access tools
        pass
```

**Registration:**
```python
# core/engine.py
from agents.my_agent import MyCustomAgent

# In _register_agents():
agent_classes = {
    'my_custom': MyCustomAgent,
    # ... existing agents
}
```

---

### Creating a New Tool

```python
# tools/my_tool.py
from tools.base import Tool
from typing import Dict, Any

class MyCustomTool(Tool):
    """Custom tool for specific operations."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name='my_tool',
            description='Does something useful',
            config=config
        )
    
    def invoke(self, params: Dict[str, Any]) -> Any:
        """Execute tool operation."""
        self._log_invocation(params)
        self.validate_params(params, ['required_param'])
        
        try:
            # Your tool logic here
            result = self._do_operation(params)
            return result
            
        except Exception as e:
            self.logger.error(f"Tool invocation failed: {e}")
            raise
```

**Registration:**
```python
# core/engine.py
from tools.my_tool import MyCustomTool

# In _register_tools():
if tool_name == 'my_tool':
    self.tool_registry.register(MyCustomTool(config=tool_config))
```

---

## Configuration

### Agent Settings (config.yaml)

```yaml
agents:
  # List of enabled agents
  enabled_agents:
    - "code_planner"
    - "code_editor"
    - "git_agent"
    - "web_data"
  
  # Auto-confirm all actions (USE WITH CAUTION!)
  auto_confirm: false
  
  # Maximum iterations for agent orchestration
  max_iterations: 10
  
  # Language-specific editor agents
  language_editors:
    python_editor: "code_editor"
    javascript_editor: "code_editor"
```

---

### Tool Settings (config.yaml)

```yaml
tools:
  # List of enabled tools
  enabled_tools:
    - "web_fetch"
    - "git"
  
  # Use gitpython library (vs subprocess)
  use_gitpython: true
  
  # Web request timeout in seconds
  web_timeout: 30
  
  # Enable sandboxing for tool execution
  enable_sandboxing: true
  
  # Maximum file size for file operations (bytes)
  max_file_size: 104857600  # 100 MB
```

---

### Security Settings (config.yaml)

```yaml
security:
  # Require confirmation before file operations
  require_file_confirmation: true
  
  # Require confirmation before git operations
  require_git_confirmation: true
  
  # Sandboxing level: "none", "basic", "strict"
  sandboxing_level: "basic"
  
  # Allowed file extensions
  allowed_file_extensions:
    - ".py"
    - ".js"
    - ".json"
    - ".md"
  
  # Blocked system paths
  blocked_paths:
    - "/etc"
    - "/sys"
    - "/proc"
```

---

## Testing the System

### Python Integration Test

```python
from core import Engine

# Initialize engine
engine = Engine()
engine.initialize()

# Check status
status = engine.get_status()
print(f"Agents: {status['registered_agents']}")
print(f"Tools: {status['registered_tools']}")

# Execute a task
result = engine.execute_task(
    task="Plan a simple web scraper",
    context={},
    agent_override=['code_planner']  # Optional: specify agents
)

print(f"Success: {result['success']}")
print(f"Analysis: {result['analysis']}")
```

---

## Troubleshooting

### No LLM Providers Available

**Issue:** Engine fails to initialize due to missing LLM providers

**Solution:**
1. Start Ollama: `ollama serve`
2. Or configure OpenAI API key in `config.yaml`

---

### Import Errors

**Issue:** `ModuleNotFoundError` for agents or tools

**Solution:**
```bash
# Ensure you're in the project directory
cd /home/ubuntu/ai-agent-console

# Run Python from the project root
python main.py status
```

---

### Agent/Tool Not Found

**Issue:** Agent or tool not registered

**Solution:**
1. Check `config.yaml` - ensure agent/tool is in `enabled_agents`/`enabled_tools`
2. Verify imports in `core/engine.py`
3. Check logs: `logs/app.log`

---

## Next Steps

1. **Configure LLM Provider**: Set up Ollama or OpenAI
2. **Test Basic Commands**: Run `python main.py status`
3. **Try Simple Tasks**: Execute `python main.py task "Create a hello world script"`
4. **Explore Agents**: List agents with `python main.py agents --verbose`
5. **Extend the System**: Create custom agents and tools

---

## Additional Resources

- **Configuration Guide**: See `config.yaml` for all settings
- **API Documentation**: Check docstrings in source files
- **Logs**: Monitor `logs/app.log` for detailed execution logs

---

**Happy Agent Orchestrating! 🤖**
