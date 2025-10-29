# AI Agent Console - Model Assignments

## Overview

This document provides a comprehensive reference for which Large Language Models (LLMs) are assigned to which agents and tools in the AI Agent Console, along with the reasoning behind these assignments.

## Available Models

The following models are available locally via Ollama and llama-cpp and can be used by the system:

### Ollama Models (Server-based)

| Model | Size | Primary Use Case | Speed | Capabilities |
|-------|------|------------------|-------|--------------|
| `deepseek-r1:32b` | 32B | Reasoning & Planning | Medium | Complex reasoning, strategic planning, architecture design |
| `qwen3-coder:30b` | 30B | Code Generation | Medium | Code editing, generation, refactoring |
| `qwen3:30b-a3b` | 30B | Data Analysis | Medium | Complex reasoning, data analysis, statistical work |
| `gemma3:27b` | 27B | General Purpose | Medium | Balanced performance for general tasks |
| `gpt-oss:20b` | 20B | General Purpose | Fast | General tasks, moderate complexity |
| `codellama:13b` | 13B | Code Assistance | Fast | Code understanding, simple code tasks |
| `mistral-nemo:12b` | 12B | Fast Tasks | Fast | Quick responses, lightweight operations |
| `mistral:7b` | 7B | Simple Tasks | Very Fast | Simple operations, administrative tasks |
| `nomic-embed-text:latest` | - | Embeddings | Very Fast | Text embeddings, semantic search |

### Llama-cpp Models (Direct GGUF Loading)

Llama-cpp allows direct loading of GGUF format models without a server. Any GGUF model from Hugging Face can be used:

| Model Format | Example | Primary Use Case | Notes |
|--------------|---------|------------------|-------|
| GGUF (Q4_K_M) | `llama-2-7b-chat.Q4_K_M.gguf` | General purpose | Good balance of quality/size |
| GGUF (Q5_K_M) | `mistral-7b.Q5_K_M.gguf` | Higher quality | Larger size, better quality |
| GGUF (Q2_K) | `tiny-llm.Q2_K.gguf` | Fast inference | Smallest, lowest quality |

**Features:**
- No server required - direct model loading
- GPU acceleration support (CUDA, Metal, OpenBLAS)
- Configurable context windows (2048-8192+ tokens)
- Lower memory footprint than server-based approaches

See [Llama-cpp Integration Guide](../LLAMA_CPP_INTEGRATION.md) for setup and configuration.

## Agent Model Assignments

### Core Planning & Architecture Agents

#### Code Planner Agent (`code_planner`)
- **Assigned Model:** `deepseek-r1:32b`
- **Reasoning:** 
  - Requires deep reasoning for project architecture
  - Needs to understand complex requirements
  - Strategic planning benefits from larger reasoning capacity
  - Can think through multiple implementation approaches
- **Fallback:** `gemma3:27b`

#### Prompt Refiner Agent (`prompt_refiner`)
- **Assigned Model:** `gemma3:27b`
- **Reasoning:**
  - General-purpose model suitable for text refinement
  - Good balance of speed and quality
  - Understands nuanced language requirements
- **Fallback:** `mistral-nemo:12b`

---

### Code Editing & Generation Agents

#### Code Editor Agent (`code_editor`)
- **Assigned Model:** `qwen3-coder:30b`
- **Reasoning:**
  - Specialized for code generation and editing
  - Excellent at multi-language code synthesis
  - Understands code patterns and best practices
- **Fallback:** `codellama:13b`

#### Python Code Editor (`code_editor_python`)
- **Assigned Model:** `qwen3-coder:30b`
- **Reasoning:**
  - Best code generation model available
  - Strong Python understanding and PEP8 compliance
- **Fallback:** `codellama:13b`

#### C# Code Editor (`code_editor_csharp`)
- **Assigned Model:** `qwen3-coder:30b`
- **Reasoning:**
  - Handles .NET ecosystem well
  - Good understanding of C# syntax and patterns
- **Fallback:** `codellama:13b`

#### Shell Script Editor (`code_editor_shell`)
- **Assigned Model:** `qwen3-coder:30b`
- **Reasoning:**
  - Strong bash/shell scripting capabilities
  - Understands Linux/Unix command patterns
- **Fallback:** `mistral-nemo:12b`

#### Web Development Editor (`code_editor_webdev`)
- **Assigned Model:** `qwen3-coder:30b`
- **Reasoning:**
  - Excellent at JavaScript/TypeScript/HTML/CSS
  - Understands modern web frameworks
- **Fallback:** `codellama:13b`

#### PowerShell Editor (`code_editor_powershell`)
- **Assigned Model:** `qwen3-coder:30b`
- **Reasoning:**
  - Good Windows PowerShell knowledge
  - Handles cmdlet syntax well
- **Fallback:** `mistral-nemo:12b`

#### Batch Script Editor (`code_editor_batch`)
- **Assigned Model:** `mistral-nemo:12b`
- **Reasoning:**
  - Batch scripts are simpler, don't need large model
  - Fast generation for simple administrative scripts
- **Fallback:** `mistral:7b`

#### C++ Code Editor (`code_editor_cpp`)
- **Assigned Model:** `qwen3-coder:30b`
- **Reasoning:**
  - C++ complexity requires sophisticated model
  - Good understanding of memory management, templates
- **Fallback:** `codellama:13b`

---

### Testing & Quality Agents

#### Code Tester Agent (`code_tester`)
- **Assigned Model:** `qwen3-coder:30b`
- **Reasoning:**
  - Needs to understand code deeply to write tests
  - Must generate valid test cases
  - Understands various testing frameworks
- **Fallback:** `codellama:13b`

---

### Security & Administration Agents

#### Cybersecurity Agent (`cybersecurity`)
- **Assigned Model:** `deepseek-r1:32b`
- **Reasoning:**
  - Security analysis requires deep reasoning
  - Needs to think through attack vectors
  - Must understand complex security patterns
  - Strategic threat assessment benefits from reasoning capacity
- **Fallback:** `gemma3:27b`

#### Windows Admin Agent (`windows_admin`)
- **Assigned Model:** `mistral-nemo:12b`
- **Reasoning:**
  - Administrative tasks are generally straightforward
  - Fast responses for system operations
  - Good understanding of Windows commands
- **Fallback:** `mistral:7b`

#### Linux Admin Agent (`linux_admin`)
- **Assigned Model:** `mistral-nemo:12b`
- **Reasoning:**
  - Similar to Windows admin - mostly straightforward tasks
  - Fast execution for system commands
  - Good Linux command knowledge
- **Fallback:** `mistral:7b`

---

### Data & Analysis Agents

#### Data Analysis Agent (`data_analysis`)
- **Assigned Model:** `qwen3:30b-a3b`
- **Reasoning:**
  - Specialized for data analysis and statistical reasoning
  - Understands pandas, numpy operations
  - Can handle complex data transformations
  - Good at statistical interpretation
- **Fallback:** `gemma3:27b`

---

### Web & Search Agents

#### Web Data Agent (`web_data`)
- **Assigned Model:** `gemma3:27b`
- **Reasoning:**
  - General-purpose model for web scraping and parsing
  - Good at understanding HTML structure
  - Balanced speed for web operations
- **Fallback:** `mistral-nemo:12b`

#### Web Search Agent (`web_search`) *NEW*
- **Assigned Model:** `mistral-nemo:12b`
- **Reasoning:**
  - Search query formulation doesn't need large model
  - Fast responses for search operations
  - Efficient at parsing search results
- **Fallback:** `mistral:7b`

---

### Database Agents

#### Database Agent (`database`) *NEW*
- **Assigned Model:** `qwen3:30b-a3b`
- **Reasoning:**
  - SQL and query generation requires strong reasoning
  - Needs to understand complex data relationships
  - Must generate safe, efficient queries
  - Good at understanding different database dialects
- **Fallback:** `qwen3-coder:30b`

---

### Version Control Agents

#### Git Agent (`git_agent`)
- **Assigned Model:** `mistral-nemo:12b`
- **Reasoning:**
  - Git operations are relatively straightforward
  - Fast responses for version control tasks
  - Good understanding of git commands
- **Fallback:** `mistral:7b`

---

### API Integration Agent

#### API Agent (`api_agent`)
- **Assigned Model:** `gemma3:27b`
- **Reasoning:**
  - Good understanding of API concepts and patterns
  - Can handle REST, SOAP, and GraphQL operations
  - Balanced performance for API testing and integration
  - Can parse and format various API response types
- **Fallback:** `mistral-nemo:12b`

---

### Project Initialization Agents

#### General Project Init (`project_init`)
- **Assigned Model:** `qwen3-coder:30b`
- **Reasoning:**
  - Needs to understand project structures across languages
  - Creates comprehensive project scaffolding
  - Generates configuration files and documentation
  - Benefits from larger model's architectural understanding
- **Fallback:** `gemma3:27b`

#### Python Project Init (`project_init_python`)
- **Assigned Model:** `qwen3-coder:30b`
- **Reasoning:**
  - Excellent understanding of Python project structures
  - Knows setuptools, poetry, pip, virtual environments
  - Generates proper pyproject.toml and setup.py
  - Understands Python packaging best practices
- **Fallback:** `codellama:13b`

#### C# Project Init (`project_init_csharp`)
- **Assigned Model:** `qwen3-coder:30b`
- **Reasoning:**
  - Strong .NET and MSBuild knowledge
  - Generates proper .csproj and .sln files
  - Understands NuGet package management
  - Handles various C# project types (console, library, web, etc.)
- **Fallback:** `codellama:13b`

#### Web Development Project Init (`project_init_webdev`)
- **Assigned Model:** `qwen3-coder:30b`
- **Reasoning:**
  - Excellent at web project structures
  - Understands npm, yarn, webpack, vite
  - Generates package.json, tsconfig.json properly
  - Knows React, Vue, Angular, and other frameworks
- **Fallback:** `codellama:13b`

#### Bash Project Init (`project_init_bash`)
- **Assigned Model:** `qwen3-coder:30b`
- **Reasoning:**
  - Good understanding of shell script project organization
  - Generates proper shebang and script structure
  - Understands shell library patterns
- **Fallback:** `mistral-nemo:12b`

#### PowerShell Project Init (`project_init_powershell`)
- **Assigned Model:** `qwen3-coder:30b`
- **Reasoning:**
  - Knows PowerShell module structure
  - Generates .psd1 and .psm1 files correctly
  - Understands PowerShell Gallery conventions
- **Fallback:** `mistral-nemo:12b`

#### C++ Project Init (`project_init_cpp`)
- **Assigned Model:** `qwen3-coder:30b`
- **Reasoning:**
  - Handles complex C++ build systems
  - Generates CMakeLists.txt properly
  - Understands include guards, headers, compilation
  - Large model needed for C++ complexity
- **Fallback:** `codellama:13b`

#### Batch Project Init (`project_init_batch`)
- **Assigned Model:** `mistral-nemo:12b`
- **Reasoning:**
  - Batch scripts are simpler
  - Fast generation for Windows batch projects
  - Adequate understanding of .bat file structure
- **Fallback:** `mistral:7b`

---

## Tool Model Assignments

Most tools don't directly use LLMs as they perform concrete operations (file I/O, git commands, etc.). However, some tools may use LLMs for specialized tasks:

### File Operations Tool (`file_operations`)
- **Model:** None (Direct file operations)
- **Reasoning:** 
  - Performs direct file system operations
  - No LLM needed for read, write, edit, move, delete operations
  - Provides comprehensive file handling for agents

### File Tool (Legacy)
- **Model:** None (Direct file operations)
- **Reasoning:** No LLM needed for file I/O

### Shell Tool
- **Model:** None (Direct command execution)
- **Reasoning:** No LLM needed for shell execution

### Git Tool
- **Model:** None (Direct git operations)
- **Reasoning:** No LLM needed for git commands

### MCP Tool
- **Model:** Context-dependent (uses agent's model)
- **Reasoning:** MCP tools may need LLM for parsing responses

---

## Performance Considerations

### Speed vs Quality Trade-offs

1. **Large Models (30B+):** Use for complex reasoning, code generation, data analysis
   - Examples: `deepseek-r1:32b`, `qwen3-coder:30b`, `qwen3:30b-a3b`
   - Trade-off: Better quality, slower responses

2. **Medium Models (12B-27B):** Use for general tasks, administrative work
   - Examples: `gemma3:27b`, `mistral-nemo:12b`
   - Trade-off: Good balance of speed and quality

3. **Small Models (7B-13B):** Use for simple tasks, quick operations
   - Examples: `mistral:7b`, `codellama:13b`
   - Trade-off: Fast responses, adequate for simple tasks

---

## Configuration Override

All model assignments can be overridden in `config.yaml` under the `agents.model_assignments` section. This allows for:

1. **Testing different models** for specific agents
2. **Performance tuning** based on your hardware
3. **Fallback configuration** when models are unavailable
4. **Custom model preferences** per agent

Example override in `config.yaml`:
```yaml
agents:
  model_assignments:
    code_planner:
      primary: "deepseek-r1:32b"
      fallback: "gemma3:27b"
      temperature: 0.7
    code_editor:
      primary: "qwen3-coder:30b"
      fallback: "codellama:13b"
      temperature: 0.3
```

---

## Model Selection Strategy

The system uses the following strategy for model selection:

1. **Check agent-specific assignment** in config.yaml
2. **Use default assignment** from this document
3. **Check model availability** via Ollama
4. **Fallback to secondary model** if primary unavailable
5. **Use global default** as last resort

---

## RouteLLM API Integration

For cloud-based fallback or when local models are unavailable, the system can use RouteLLM API:

- **Use Case:** When local GPU resources are constrained
- **Routing:** RouteLLM can intelligently route requests to appropriate cloud models
- **Configuration:** Set in `config.yaml` under `openai` section with RouteLLM endpoint

---

## Benchmarks & Performance

### Typical Response Times (on Lenovo Thinkpad T14s)

| Model | Simple Task | Code Generation | Complex Reasoning |
|-------|-------------|-----------------|-------------------|
| `mistral:7b` | 1-2s | 3-5s | 5-8s |
| `mistral-nemo:12b` | 2-3s | 5-8s | 8-12s |
| `codellama:13b` | 2-3s | 4-7s | 8-12s |
| `gemma3:27b` | 4-6s | 10-15s | 15-25s |
| `qwen3-coder:30b` | 5-7s | 12-18s | 18-30s |
| `qwen3:30b-a3b` | 5-7s | 12-18s | 18-30s |
| `deepseek-r1:32b` | 6-10s | 15-25s | 25-45s |

*Note: Times are approximate and depend on prompt complexity, context length, and system load*

---

## Best Practices

1. **Use the right model for the job:** Don't use a 32B model for simple tasks
2. **Monitor performance:** Track response times and adjust assignments
3. **Configure fallbacks:** Always have a fallback model configured
4. **Test model quality:** Validate that assigned models produce good results
5. **Consider temperature:** Lower temperature (0.1-0.3) for code, higher (0.7-1.0) for creative tasks
6. **Resource management:** Don't run too many large models simultaneously
7. **Update regularly:** As new models become available, evaluate and update assignments

---

## Maintenance

This document should be updated when:
- New agents are added to the system
- New models become available locally
- Performance characteristics change
- User requirements or preferences change
- Agent capabilities are enhanced

**Last Updated:** October 14, 2025  
**Version:** 2.5.0
