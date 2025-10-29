# Agent Catalog

**Version:** 2.5.0  
**Last Updated:** October 14, 2025

This document provides a comprehensive catalog of all available agents in the AI Agent Console.

## Table of Contents

1. [Overview](#overview)
2. [Base Agent Classes](#base-agent-classes)
3. [Generic Agents](#generic-agents)
4. [Language-Specific Agents](#language-specific-agents)
5. [Specialized Agents](#specialized-agents)
6. [Usage Examples](#usage-examples)
7. [Agent Selection](#agent-selection)

---

## Overview

The AI Agent Console includes **86 specialized agents** across multiple categories:

- **Base Classes** (9): Abstract base classes for agent types
- **Generic Agents** (11): Language-agnostic implementations
- **Language-Specific Agents** (56): 8 agents for each of 7 languages
- **Specialized Agents** (10): Domain-specific task automation

---

## Base Agent Classes

Base classes define interfaces and common functionality for specialized agents.

| Base Class | Purpose | Location |
|------------|---------|----------|
| `Agent` | Abstract base for all agents | `agents/base/agent_base.py` |
| `CodeEditorBase` | Code editing agents | `agents/base/code_editor_base.py` |
| `BuildAgentBase` | Build and compilation agents | `agents/base/build_agent_base.py` |
| `DebugAgentBase` | Debugging agents | `agents/base/debug_agent_base.py` |
| `DocumentationAgentBase` | Documentation agents | `agents/base/documentation_agent.py` |
| `ProjectInitBase` | Project initialization agents | `agents/base/project_init_base.py` |
| `CodeTesterBase` | Code testing agents | `agents/base/code_tester_base.py` |
| `CodePlannerBase` | Code planning agents | `agents/base/code_planner_base.py` |
| `CodeAnalyzerBase` | Code analysis agents | `agents/base/code_analyzer_base.py` |

---

## Generic Agents

Language-agnostic agents that work across all languages and scenarios.

| Agent | Purpose | Location |
|-------|---------|----------|
| `GenericCodeEditor` | LLM-based code generation for any language | `agents/generic/generic_code_editor.py` |
| `GenericCodeTester` | Generic test pattern execution | `agents/generic/generic_code_tester.py` |
| `GenericCodePlanner` | SOLID principles & design patterns | `agents/generic/generic_code_planner.py` |
| `GenericCodeAnalyzer` | Quality, complexity, security analysis | `agents/generic/generic_code_analyzer.py` |
| `GenericBuildAgent` | Generic build command execution | `agents/generic/generic_build_agent.py` |
| `GenericDebugAgent` | Generic debugging assistance | `agents/generic/generic_debug_agent.py` |
| `GenericDocumentation` | Documentation generation | `agents/generic/generic_documentation.py` |
| `GenericProjectInit` | Project scaffolding | `agents/generic/generic_project_init.py` |
| `TaskOrchestrator` | Multi-agent task coordination | `agents/generic/task_orchestrator.py` |
| `ContextManager` | Context extraction and management | `agents/generic/context_manager.py` |
| `SpecificationExtraction` | Extract requirements from text | `agents/generic/specification_extraction.py` |
| `TaskDecomposition` | Break down complex tasks | `agents/generic/task_decomposition.py` |

---

## Language-Specific Agents

All 7 supported languages have complete agent implementations with 8 specialized agents each (56 total).

### Python Agents

| Agent | Purpose | Specialization |
|-------|---------|----------------|
| `PythonCodeEditor` | Code editing | PEP8, type hints, AST validation |
| `PythonCodeTester` | Testing | pytest, unittest, nose |
| `PythonCodePlanner` | Planning | Django, Flask, FastAPI |
| `PythonCodeAnalyzer` | Analysis | AST analysis, PEP8, bandit |
| `PythonBuildAgent` | Building | pip, poetry, setuptools |
| `PythonDebugAgent` | Debugging | pdb, pytest debugging |
| `PythonDocumentation` | Documentation | Sphinx, docstrings |
| `PythonProjectInit` | Initialization | Project templates |

**Location:** `agents/languages/python/`

### C# Agents

| Agent | Purpose | Specialization |
|-------|---------|----------------|
| `CSharpCodeEditor` | Code editing | .NET conventions, LINQ |
| `CSharpCodeTester` | Testing | xUnit, NUnit, MSTest |
| `CSharpCodePlanner` | Planning | ASP.NET, Entity Framework |
| `CSharpCodeAnalyzer` | Analysis | FxCop, StyleCop patterns |
| `CSharpBuildAgent` | Building | dotnet, MSBuild |
| `CSharpDebugAgent` | Debugging | Visual Studio debugger |
| `CSharpDocumentation` | Documentation | XML docs, DocFX |
| `CSharpProjectInit` | Initialization | .NET project templates |

**Location:** `agents/languages/csharp/`

### C++ Agents

| Agent | Purpose | Specialization |
|-------|---------|----------------|
| `CppCodeEditor` | Code editing | Modern C++, RAII patterns |
| `CppCodeTester` | Testing | Google Test, Catch2 |
| `CppCodePlanner` | Planning | CMake, vcpkg |
| `CppCodeAnalyzer` | Analysis | Static analysis, memory safety |
| `CppBuildAgent` | Building | CMake, Make, ninja |
| `CppDebugAgent` | Debugging | gdb, lldb |
| `CppDocumentation` | Documentation | Doxygen |
| `CppProjectInit` | Initialization | CMake project setup |

**Location:** `agents/languages/cpp/`

### Web (JavaScript/TypeScript) Agents

| Agent | Purpose | Specialization |
|-------|---------|----------------|
| `WebCodeEditor` | Code editing | React, Vue, Angular support |
| `WebCodeTester` | Testing | Jest, Mocha, Vitest |
| `WebCodePlanner` | Planning | React, Vue, Node.js |
| `WebCodeAnalyzer` | Analysis | ESLint, security patterns |
| `WebBuildAgent` | Building | npm, webpack, vite |
| `WebDebugAgent` | Debugging | Chrome DevTools, Node debugger |
| `WebDocumentation` | Documentation | JSDoc, TypeDoc |
| `WebProjectInit` | Initialization | React, Next.js, Vue templates |

**Location:** `agents/languages/web/`

### Bash Agents

| Agent | Purpose | Specialization |
|-------|---------|----------------|
| `BashCodeEditor` | Code editing | ShellCheck integration |
| `BashCodeTester` | Testing | bats, shunit2 |
| `BashCodePlanner` | Planning | Shell scripting patterns |
| `BashCodeAnalyzer` | Analysis | ShellCheck integration |
| `ShellBuildAgent` | Building | Shell scripts |
| `ShellDebugAgent` | Debugging | bash -x, shellcheck |
| `BashDocumentation` | Documentation | Man pages, comments |
| `BashProjectInit` | Initialization | Script templates |

**Location:** `agents/languages/shell/`

### PowerShell Agents

| Agent | Purpose | Specialization |
|-------|---------|----------------|
| `PowerShellCodeEditor` | Code editing | PSScriptAnalyzer |
| `PowerShellCodeTester` | Testing | Pester |
| `PowerShellCodePlanner` | Planning | Module development |
| `PowerShellCodeAnalyzer` | Analysis | PSScriptAnalyzer |
| `PowerShellBuildAgent` | Building | PSake, Invoke-Build |
| `PowerShellDebugAgent` | Debugging | PS debugger |
| `PowerShellDocumentation` | Documentation | Comment-based help |
| `PowerShellProjectInit` | Initialization | Module templates |

**Location:** `agents/languages/powershell/`

### Batch Agents

| Agent | Purpose | Specialization |
|-------|---------|----------------|
| `BatchCodeEditor` | Code editing | Windows scripting |
| `BatchCodeTester` | Testing | Custom scripts |
| `BatchCodePlanner` | Planning | Batch scripting patterns |
| `BatchCodeAnalyzer` | Analysis | Batch best practices |
| `BatchBuildAgent` | Building | Batch scripts |
| `BatchDebugAgent` | Debugging | echo debugging |
| `BatchDocumentation` | Documentation | REM comments |
| `BatchProjectInit` | Initialization | Batch templates |

**Location:** `agents/languages/batch/`

---

## Specialized Agents

Domain-specific agents for various tasks.

| Agent | Purpose | Location |
|-------|---------|----------|
| `APIAgent` | REST API interactions | `agents/api_agent.py` |
| `GitAgent` | Git version control operations | `agents/git_agent.py` |
| `WebSearchAgent` | Multi-engine web search | `agents/web_search.py` |
| `WebDataAgent` | Web scraping and data extraction | `agents/web_data.py` |
| `DatabaseAgent` | SQL and NoSQL database operations | `agents/database.py` |
| `DataAnalysisAgent` | Data analysis with pandas | `agents/data_analysis.py` |
| `CybersecurityAgent` | Security analysis and testing | `agents/cybersecurity.py` |
| `LinuxAdminAgent` | Linux system administration | `agents/linux_admin.py` |
| `WindowsAdminAgent` | Windows system administration | `agents/windows_admin.py` |
| `PromptRefinerAgent` | Refine and optimize prompts | `agents/prompt_refiner.py` |

---

## Usage Examples

### Using a Code Editor

```python
from agents.languages.python import PythonCodeEditor

editor = PythonCodeEditor()
result = editor.execute(
    "Create a FastAPI REST API with user authentication",
    context={'output_dir': '/path/to/project'}
)
```

### Using a Code Tester

```python
from agents.languages.python import PythonCodeTester

tester = PythonCodeTester()
result = tester.execute(
    "Run tests in tests/ directory",
    context={'working_dir': '/path/to/project'}
)
```

### Using a Code Planner

```python
from agents.languages.python import PythonCodePlanner

planner = PythonCodePlanner()
result = planner.execute(
    "Create a REST API with FastAPI",
    context={}
)
```

### Using a Code Analyzer

```python
from agents.languages.python import PythonCodeAnalyzer

analyzer = PythonCodeAnalyzer()
result = analyzer.execute(
    "Analyze code quality and security",
    context={'file_path': 'main.py'}
)
```

### Using a Specialized Agent

```python
from agents import GitAgent

git = GitAgent()
result = git.execute(
    "Create a new feature branch and commit changes",
    context={'branch_name': 'feature/new-api'}
)
```

---

## Agent Selection

The Engine automatically selects appropriate agents based on:
- **Task description:** Keywords and intent analysis
- **File extensions:** Determines language-specific agents
- **Project context:** Project structure and configuration
- **Agent capabilities:** Matches task requirements to agent skills

You can also explicitly specify agents using context parameters:
```python
result = engine.execute_task(
    "Write unit tests",
    context={'agent_type': 'PythonCodeTester'}
)
```

---

## Agent Architecture

### Inheritance Hierarchy

```
Agent (base)
├── CodeEditorBase → Generic + Language-Specific (7×)
├── CodeTesterBase → Generic + Language-Specific (7×)
├── CodePlannerBase → Generic + Language-Specific (7×)
├── CodeAnalyzerBase → Generic + Language-Specific (7×)
├── BuildAgentBase → Generic + Language-Specific (7×)
├── DebugAgentBase → Generic + Language-Specific (7×)
├── DocumentationAgentBase → Generic + Language-Specific (7×)
├── ProjectInitBase → Generic + Language-Specific (7×)
└── Specialized Agents (10)
```

### Common Features

All agents inherit from the base `Agent` class and provide:

1. **LLM Integration**
   - Model selection from configuration
   - Primary and fallback model support
   - Temperature control
   - Streaming support

2. **Error Handling**
   - Standardized error results
   - Exception logging
   - Graceful degradation

3. **Logging**
   - Action logging
   - Debug information
   - Performance tracking

4. **Tool Integration**
   - Tool registry access
   - Tool invocation
   - Result processing

5. **Memory & Context**
   - Vector database integration
   - Context awareness
   - Memory persistence

---

## Language Coverage Summary

| Language | Code Editor | Tester | Planner | Analyzer | Build | Debug | Docs | Init | Total |
|----------|------------|--------|---------|----------|-------|-------|------|------|-------|
| Python | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 8 |
| C# | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 8 |
| C++ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 8 |
| Web (JS/TS) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 8 |
| Bash | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 8 |
| PowerShell | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 8 |
| Batch | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 8 |

**Complete Coverage:** 7 languages × 8 agent types = **56 language-specific agents**

---

## Version History

- **v2.5.0** - October 13, 2025
  - 📝 Updated version to match project version (v2.5)
  - ℹ️ No new agents added (v2.5 focused on llama-cpp integration and task loop processing)

- **v2.3.0** - October 12, 2025
  - ✨ Updated to reflect complete agent inventory (86 agents)
  - ✨ Added documentation and project init agents for all languages
  - 📝 Consolidated AGENT_INVENTORY.md into AGENT_CATALOG.md
  - 📝 Improved organization and clarity

- **v2.2.0** - October 12, 2025
  - ✨ Added Code Tester, Code Planner, and Code Analyzer agents
  - 📝 Expanded language coverage

- **v2.1.0** - October 10, 2025
  - ✨ Added Build Agents for all languages
  - 📝 Enhanced documentation

---

**Version:** 2.5.0  
**Total Agents:** 86  
**Last Updated:** October 13, 2025

---

**For more information, see:**
- [README.md](../../README.md) - Project overview
- [EXTENDING_GUIDE.md](../guides/EXTENDING_GUIDE.md) - Adding new agents
- [MODEL_ASSIGNMENTS.md](MODEL_ASSIGNMENTS.md) - LLM model configuration
