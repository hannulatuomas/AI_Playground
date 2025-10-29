# AI Agent Console - Example Usage

This document provides comprehensive examples of using the AI Agent Console.

## Table of Contents
1. [Basic Setup](#basic-setup)
2. [Status Checks](#status-checks)
3. [Simple LLM Queries](#simple-llm-queries)
4. [Task Orchestration Examples](#task-orchestration-examples)
5. [Agent-Specific Examples](#agent-specific-examples)
6. [Tool Usage](#tool-usage)
7. [MCP Integration](#mcp-integration)

## Basic Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure LLM Provider

**Using Ollama (Recommended for local development):**

```bash
# Install Ollama from https://ollama.ai/
ollama serve

# Pull a model
ollama pull llama2
# or
ollama pull mistral
```

**Using OpenAI:**

Edit `config.yaml`:
```yaml
openai:
  api_key: "sk-your-api-key-here"
```

Or set environment variable:
```bash
export AI_AGENT_OPENAI__API_KEY="sk-your-api-key-here"
```

### 3. Verify Installation

```bash
python main.py status
```

## Status Checks

### Check System Status

```bash
python main.py status
```

**Expected Output:**
```
🔍 Checking system status...

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

### View Configuration

```bash
python main.py config --show
```

### Validate Configuration

```bash
python main.py config --validate
```

## Simple LLM Queries

### Single Query

```bash
python main.py run "Explain the difference between Python lists and tuples"
```

### Interactive Mode

```bash
python main.py run --interactive
```

Then type your queries:
```
You: What is machine learning?
[ollama:llama2]
Machine learning is...

You: Give me a Python example
[ollama:llama2]
Here's an example...

You: exit
```

### Specify Model

```bash
python main.py run "Write a haiku about programming" --model mistral
```

### Force Provider

```bash
python main.py run "Explain quantum entanglement" --provider openai --model gpt-4
```

## Task Orchestration Examples

### Example 1: Plan and Create Python Script

**Command:**
```bash
python main.py task "Plan and create a hello world Python script with proper structure"
```

**What Happens:**
1. **Task Analysis**: System analyzes the task
   - Identifies needed agents: code_planner, code_editor
   
2. **CodePlannerAgent Executes**:
   - Generates project plan
   - Determines file structure
   - Creates implementation steps
   
3. **CodeEditorAgent Executes**:
   - Uses plan from previous agent
   - Creates `hello.py` file
   - Shows preview:
     ```python
     ════════════════════════════════════════════════════
     Creating: hello.py
     ════════════════════════════════════════════════════
     #!/usr/bin/env python3
     """
     Simple Hello World script
     """
     
     def main():
         print("Hello, World!")
     
     if __name__ == "__main__":
         main()
     ════════════════════════════════════════════════════
     ```
   - Asks: `Create file hello.py? (y/n):`
   - If yes: Creates file
   
4. **Result**:
   ```
   ✓ Task Analysis:
     Agents: code_planner, code_editor
     Reasoning: Need to plan structure and create file
   
   ✓ Execution Results (2 agents):
   ────────────────────────────────────────────────────────
   
   1. ✓ code_planner
      Message: Project plan generated successfully
   
   2. ✓ code_editor
      Message: File operation completed: create
   ────────────────────────────────────────────────────────
   
   ✓ Task completed successfully!
   ```

### Example 2: Git Operations

**Command:**
```bash
python main.py task "Initialize git repository and commit all changes"
```

**What Happens:**
1. **Task Analysis**: Identifies git_agent
2. **GitAgent Executes**:
   - Initializes git repo (if needed)
   - Shows status
   - Asks: `Create commit? (y/n):`
   - Creates commit with descriptive message

### Example 3: Web Data Retrieval

**Command:**
```bash
python main.py task "Fetch and summarize the latest news from example.com/news"
```

**What Happens:**
1. **Task Analysis**: Identifies web_data agent
2. **WebDataAgent Executes**:
   - Uses web_fetch tool to retrieve content
   - Parses HTML with BeautifulSoup
   - Uses LLM to summarize content
   - Returns structured summary

### Example 4: Complex Multi-Agent Task

**Command:**
```bash
python main.py task "Create a REST API plan, implement hello endpoint, and commit to git"
```

**What Happens:**
1. **Task Analysis**: code_planner → code_editor → git_agent
2. **Execution**:
   - **code_planner**: Generates API structure plan
   - **code_editor**: Creates `api.py` with hello endpoint
   - **git_agent**: Commits the new file

## Agent-Specific Examples

### Using Specific Agents

You can skip task analysis and specify agents manually:

#### Code Planner Only

```bash
python main.py task "Plan a microservices architecture for e-commerce" --agents code_planner
```

#### Code Editor Only

```bash
python main.py task "Create a README.md file" --agents code_editor
```

This will:
1. Use LLM to generate README content
2. Show preview
3. Ask for confirmation
4. Create file

#### Git Agent Only

```bash
python main.py task "Check git status and commit changes" --agents git_agent
```

#### Multiple Agents (Manual Chain)

```bash
python main.py task "Create config.py and commit it" --agents code_editor,git_agent
```

## Advanced Usage

### Auto-Confirm Mode

**⚠️  WARNING: This skips ALL confirmations. Use with extreme caution!**

```bash
python main.py task "Create test.py" --auto-confirm
```

Or in config.yaml:
```yaml
agents:
  auto_confirm: true  # ⚠️  Dangerous!
```

### Custom Configuration File

```bash
python main.py task "Create script" --config my_custom_config.yaml
```

### Environment Variable Override

```bash
AI_AGENT_AGENTS__AUTO_CONFIRM=false \
AI_AGENT_LOGGING__LEVEL=DEBUG \
python main.py task "Create file"
```

## Tool Usage

Tools are used internally by agents, but you can understand their capabilities:

### Web Fetch Tool

Used by `web_data` agent. Capabilities:
- HTTP/HTTPS requests
- Custom headers and auth
- Async operations (httpx)
- Timeout configuration

Example task that uses web_fetch:
```bash
python main.py task "Download and analyze data from api.example.com/data" --agents web_data
```

### Git Tool

Used by `git_agent`. Capabilities:
- Repository initialization
- Status checks
- File staging
- Commits
- Branch operations

Example task:
```bash
python main.py task "Initialize git and create initial commit" --agents git_agent
```

## MCP Integration

### Enable MCP

Edit `config.yaml`:
```yaml
mcp:
  enabled: true
  servers:
    - server_id: "local_tools"
      transport: "stdio"
      endpoint: "/usr/local/bin/mcp-server"
      auto_connect: true
```

### MCP Server Types

#### 1. stdio (subprocess)
```toml
[[mcp.servers]]
server_id = "local_tools"
transport = "stdio"
endpoint = "python /path/to/mcp_server.py"
auto_connect = true
```

#### 2. HTTP
```toml
[[mcp.servers]]
server_id = "remote_api"
transport = "http"
endpoint = "https://api.example.com/mcp"
auto_connect = false

[mcp.servers.auth]
token = "your-auth-token"
```

#### 3. SSE (Server-Sent Events)
```toml
[[mcp.servers]]
server_id = "sse_server"
transport = "sse"
endpoint = "https://sse.example.com/events"
auto_connect = true

[mcp.servers.auth]
api_key = "your-api-key"
```

## Real-World Workflows

### Workflow 1: Start New Python Project

```bash
# 1. Plan project structure
python main.py task "Plan a Python CLI application with typer"

# 2. Create initial files
python main.py task "Create main.py, requirements.txt, and README.md based on the plan"

# 3. Initialize git
python main.py task "Initialize git repository and create initial commit"
```

### Workflow 2: Research and Document

```bash
# 1. Fetch information
python main.py task "Fetch and summarize Python best practices from python.org"

# 2. Create documentation
python main.py task "Create BEST_PRACTICES.md with the summarized information"

# 3. Commit
python main.py task "Commit the documentation"
```

### Workflow 3: Code Generation and Testing

```bash
# 1. Plan implementation
python main.py task "Plan a calculator module with add, subtract, multiply, divide functions"

# 2. Generate code
python main.py task "Implement the calculator module based on the plan"

# 3. Generate tests
python main.py task "Create test_calculator.py with pytest tests"

# 4. Commit everything
python main.py task "Commit all calculator files with descriptive message"
```

## Error Handling

### No LLM Provider Available

```
❌ Engine Error: No LLM providers are available.

Troubleshooting:
  • Ensure Ollama is running (ollama serve)
  • Or configure OpenAI API key in config.yaml
  • Check logs/app.log for detailed information
```

**Solution:**
```bash
# Start Ollama
ollama serve

# Or configure OpenAI
export AI_AGENT_OPENAI__API_KEY="sk-..."
```

### Agent Execution Failed

If an agent fails, the system continues with remaining agents but marks the failure:

```
✓ Execution Results (3 agents):
────────────────────────────────────────────────────────────

1. ✓ code_planner
   Message: Project plan generated successfully

2. ✗ code_editor
   Message: File operation failed: Permission denied

3. ✓ git_agent
   Message: Git operation completed successfully
────────────────────────────────────────────────────────────
```

### User Cancellation

You can cancel at any confirmation prompt:

```
Create file hello.py? (y/n): n

Result: Operation cancelled by user
```

Or interrupt with Ctrl+C:

```
^C

👋 Interrupted by user
```

## Tips and Best Practices

### 1. Start with Task Analysis

Let the system select agents automatically:
```bash
python main.py task "Your task description"
```

### 2. Review Before Confirming

Always review diffs and changes before confirming.

### 3. Use Specific Agents for Simple Tasks

For straightforward tasks, specify agents:
```bash
python main.py task "Create README" --agents code_editor
```

### 4. Check Logs for Details

```bash
cat logs/app.log
```

### 5. Test with Ollama First

Ollama is free and runs locally - perfect for testing.

### 6. Use Auto-Confirm Sparingly

Only use `--auto-confirm` when you're certain about the operations.

### 7. Backup Before Major Operations

The system is safe, but backups are always good practice.

## Next Steps

1. Read the [README.md](README.md) for architecture details
2. Explore the [agents/](agents/) and [tools/](tools/) directories
3. Create custom agents for your specific needs
4. Integrate with MCP servers for extended functionality
5. Build workflows that chain multiple tasks together
