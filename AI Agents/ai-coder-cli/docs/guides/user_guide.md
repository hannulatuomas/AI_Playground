# AI Agent Console - User Guide

Comprehensive guide to using the AI Agent Console.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Agents Overview](#agents-overview)
3. [Tools Overview](#tools-overview)
4. [Configuration](#configuration)
5. [Examples](#examples)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) Ollama for local LLM
- (Optional) OpenAI API key for cloud LLM

### Installation

```bash
pip install -r requirements.txt
```

### First Run

```bash
python main.py "Hello, what can you do?"
```

## Agents Overview

### Language-Specific Code Editors

#### Python Editor (`code_editor_python`)
- **Features**: PEP 8 compliance, syntax validation, pytest/unittest support
- **Use for**: Python scripts, modules, test files
- **Example**: `"Create a Python REST API with FastAPI"`

#### C# Editor (`code_editor_csharp`)
- **Features**: .NET awareness, NuGet packages, ASP.NET Core patterns
- **Use for**: C# classes, ASP.NET controllers, .csproj files
- **Example**: `"Create a C# web API controller for user management"`

#### Shell Script Editor (`code_editor_shell`)
- **Features**: Bash/Sh/Zsh support, shebang handling, executable permissions
- **Use for**: Shell scripts, automation tasks
- **Example**: `"Create a backup script for /data directory"`

#### Web Dev Editor (`code_editor_webdev`)
- **Features**: React/Next.js patterns, package.json, modern ES6+
- **Use for**: HTML, CSS, JavaScript, TypeScript, React components
- **Example**: `"Create a Next.js landing page with hero section"`

#### PowerShell Editor (`code_editor_powershell`)
- **Features**: Cmdlet patterns, module support, comment-based help
- **Use for**: PowerShell scripts, modules, manifests
- **Example**: `"Create a PowerShell script to monitor services"`

#### Batch File Editor (`code_editor_batch`)
- **Features**: Windows CMD syntax, error level handling
- **Use for**: Windows batch files, automation
- **Example**: `"Create a batch file to clean temp directories"`

#### C++ Editor (`code_editor_cpp`)
- **Features**: Modern C++ (C++17/20), CMake support, header guards
- **Use for**: C++ source/header files, CMakeLists.txt
- **Example**: `"Create a C++ class for binary search tree"`

### Specialized Agents

#### Code Tester (`code_tester`)
- **Supports**: pytest, unittest, jest, mocha, vitest, nunit, xunit
- **Features**: Auto-detect framework, parse results, detailed failures
- **Example**: `"Run tests in tests/ directory"`

#### Prompt Refiner (`prompt_refiner`)
- **Techniques**: Chain-of-Thought, few-shot, structured formatting
- **Use for**: Optimizing prompts before LLM queries
- **Example**: `"Refine this prompt: Write a sorting algorithm"`

#### Linux Admin (`linux_admin`)
- **Features**: Package management, service control, system info, log inspection
- **Safety**: Command validation, no destructive operations without confirmation
- **Example**: `"Check disk usage and list largest directories"`

### Extensibility Examples (Stubs)

#### Data Analysis (`data_analysis`)
- **Status**: Stub implementation with guidance
- **Would support**: pandas, numpy, matplotlib, statistical analysis
- **Use for**: Learning to extend the system

#### Windows Admin (`windows_admin`)
- **Status**: Stub with PowerShell integration guide
- **Would support**: Service management, registry access, event logs
- **Requires**: Windows OS, pywin32

#### Cybersecurity (`cybersecurity`)
- **Status**: Stub with ethical guidelines
- **Includes**: Password strength checker (implemented as example)
- **Would support**: Vulnerability scanning, port scanning (with authorization)

## Tools Overview

### Web Fetch Tool (`web_fetch`)
- **Purpose**: Fetch data from URLs
- **Features**: HTTP/HTTPS, timeout handling, retry logic
- **Usage**: Used by web_data agent

### Git Tool (`git`)
- **Purpose**: Git operations
- **Features**: Init, add, commit, push, pull, status
- **Usage**: Used by git_agent

### MCP Tool (`mcp`)
- **Purpose**: Model Context Protocol client
- **Transports**: stdio, HTTP, SSE
- **Features**: Tool discovery, remote tool invocation, authentication
- **Usage**: Connect to external tool servers

### File I/O Tool (`file_io`)
- **Purpose**: Sandboxed file operations
- **Operations**: read, write, append, delete, list, mkdir
- **Safety**: Path validation, size limits, extension whitelisting
- **Usage**: Safe file manipulation

### Shell Exec Tool (`shell_exec`)
- **Purpose**: Safe command execution
- **Features**: Command whitelisting, timeout, output limits
- **Safety**: Dangerous command blocking, non-root enforcement
- **Usage**: Execute system commands safely

## Configuration

### Key Settings

```yaml
# LLM Providers
ollama:
  host: "http://localhost"
  port: 11434

openai:
  api_key: "your-key-here"

# Security
security:
  require_file_confirmation: true
  sandboxing_level: "basic"
  blocked_paths:
    - "/etc"
    - "/sys"

# Agents
agents:
  language_editors:
    python: "code_editor_python"
    javascript: "code_editor_webdev"

# Testing
testing:
  auto_detect_framework: true
  test_timeout: 300
```

## Examples

### Example 1: Create Python Web Scraper

```bash
python main.py "Create a Python web scraper for news articles"
```

**What happens:**
1. Task analyzed
2. `code_editor_python` agent selected
3. Code generated with requests/BeautifulSoup
4. File created with proper structure

### Example 2: Run Tests

```bash
python main.py "Run tests and show results"
```

**What happens:**
1. `code_tester` agent activated
2. Test framework detected (e.g., pytest)
3. Tests executed
4. Results parsed and displayed

### Example 3: System Administration

```bash
python main.py "Show disk usage and system uptime"
```

**What happens:**
1. `linux_admin` agent selected
2. Commands validated for safety
3. `df -h` and `uptime` executed
4. Results formatted and displayed

## Troubleshooting

### Issue: LLM Not Responding

**Solution:**
- Check Ollama is running: `ollama serve`
- Verify OpenAI API key if using OpenAI
- Check network connectivity

### Issue: Import Errors

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Permission Denied

**Solution:**
- Adjust `blocked_paths` in config.yaml
- Check file permissions
- Use appropriate agent (e.g., linux_admin for system ops)

### Issue: Agent Not Found

**Solution:**
- Check agent is enabled in config.yaml
- Verify agent imports in agents/__init__.py
- Check for syntax errors in agent file

## Advanced Usage

### Custom Agent Development

1. Create new agent file in `agents/`
2. Inherit from `Agent` base class
3. Implement `execute()` method
4. Add to `agents/__init__.py`
5. Register in config.yaml

### Custom Tool Development

1. Create new tool file in `tools/`
2. Inherit from `Tool` base class
3. Implement `invoke()` method
4. Add to `tools/__init__.py`
5. Configure in config.yaml

## Best Practices

1. **Start Simple**: Test with basic tasks before complex workflows
2. **Review Output**: Always review generated code before execution
3. **Use Confirmations**: Keep security confirmations enabled
4. **Check Logs**: Review logs/ directory for debugging
5. **Update Config**: Customize config.yaml for your workflow

## FAQ

**Q: Can I use only local LLMs?**
A: Yes, configure Ollama and disable OpenAI fallback in config.yaml.

**Q: How do I add a new programming language?**
A: Create a new code_editor_<lang>.py agent following existing patterns.

**Q: Is it safe to run automatically?**
A: With confirmations enabled, yes. Disable auto_confirm for production.

**Q: Can I extend with custom agents?**
A: Yes! See "Custom Agent Development" above.

**Q: What's the difference between agents and tools?**
A: Agents use LLMs for decision-making. Tools are utilities agents can call.

## Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@example.com

## Next Steps

- Read [API Reference](../reference/AGENT_TOOL_GUIDE.md) for code documentation
- See [Examples](examples/) for more use cases
- Check [Contributing](../../CONTRIBUTING.md) to help improve the project
