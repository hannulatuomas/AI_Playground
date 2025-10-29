# Getting Started with AI Agent Console

**Version:** 2.0.0  
**Last Updated:** October 13, 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Basic Usage Examples](#basic-usage-examples)
5. [Advanced Features](#advanced-features)
6. [Configuration Guide](#configuration-guide)
7. [Common Workflows](#common-workflows)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

The AI Agent Console is a comprehensive AI-powered development assistant featuring 80+ specialized agents for software development across 7 programming languages. This guide will help you get started quickly.

### What Can You Do?

- 🚀 **Initialize Projects**: Automatically set up new projects with proper structure
- ✏️ **Code Editing**: AI-assisted code creation and modification
- 🧪 **Testing**: Automated test generation and execution
- 🐛 **Debugging**: Intelligent error detection and fixing
- 📚 **Documentation**: Automatic documentation generation
- 🔍 **Code Analysis**: Quality checks and best practice enforcement
- 🏗️ **Building**: Project building and packaging
- 🔄 **Version Control**: AI-enhanced Git operations

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control features)

### Option 1: Install with Ollama (Recommended for Local Use)

```bash
# 1. Install Ollama (if not already installed)
# Visit: https://ollama.ai/download

# 2. Pull a model
ollama pull llama2

# 3. Clone the repository
git clone https://github.com/yourusername/ai-agent-console.git
cd ai-agent-console

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the console
python main.py
```

### Option 2: Install with OpenAI

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ai-agent-console.git
cd ai-agent-console

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your OpenAI API key
export AI_AGENT_OPENAI__API_KEY="your-api-key-here"

# 4. Configure to use OpenAI
# Edit config.yaml and set:
#   fallback.primary_provider: "openai"

# 5. Run the console
python main.py
```

### Option 3: Use Both (Fallback Configuration)

```bash
# Set up both Ollama and OpenAI for automatic fallback
# This gives you the best of both worlds:
# - Fast local inference with Ollama
# - Fallback to OpenAI if Ollama is unavailable

# 1. Install and configure Ollama (see Option 1)
# 2. Set OpenAI API key (see Option 2)
# 3. Configure fallback in config.yaml:
#   fallback.enabled: true
#   fallback.primary_provider: "ollama"
#   fallback.fallback_provider: "openai"
```

---

## Quick Start

### Your First Interaction

```bash
# Start the console
python main.py

# You'll see the welcome banner:
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║        🤖 AI Agent Console 🚀                        ║
║        Intelligent Development Assistant              ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

# Try a simple command
You: Create a Python function to calculate fibonacci numbers

# The agent will respond with code
```

### Example Session

```
You: I want to create a new Python web application

Agent: I'll help you create a new Python web application. Let me gather
some information first:

1. What type of web framework would you like to use?
   - Flask (lightweight, simple)
   - FastAPI (modern, async, with automatic API docs)
   - Django (full-featured, batteries included)

2. What will this application do?

3. Do you need database support? If yes, which database?

You: Let's use FastAPI. I want to create a REST API for a todo list
application. Use SQLite for now.

Agent: Perfect! I'll create a FastAPI todo list application with SQLite.
Let me set up the project structure...

[Agent proceeds to create project files, install dependencies, and
provide usage instructions]
```

---

## Basic Usage Examples

### Example 1: Create a New Python Project

```
You: Create a new Python CLI tool project called "file-organizer"

Agent: I'll create a new Python CLI tool project. The project will include:
- Proper directory structure
- setup.py for packaging
- requirements.txt for dependencies
- README.md with documentation
- Example CLI code with argparse
- Tests directory with sample tests

[Agent creates the project structure]

Your new project structure:
file-organizer/
├── file_organizer/
│   ├── __init__.py
│   ├── cli.py
│   ├── core.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_core.py
├── setup.py
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── .gitignore
└── LICENSE

To get started:
1. cd file-organizer
2. pip install -r requirements.txt
3. python -m file_organizer --help
```

### Example 2: Add a Feature to Existing Code

```
You: I have a Python file calculator.py with basic arithmetic functions.
Add support for scientific operations like square root, power, and logarithm.

Agent: I'll analyze your calculator.py file and add scientific operations.
Let me check the current structure first...

[Agent reads the file]

I'll add the following functions:
- sqrt(x): Square root
- power(x, y): x raised to the power y
- log(x, base=10): Logarithm with configurable base
- ln(x): Natural logarithm

I'll also add proper error handling and input validation.

[Agent modifies the file and shows the changes]

Would you like me to also:
1. Generate tests for the new functions?
2. Update the README with usage examples?
3. Add type hints for better code quality?
```

### Example 3: Debug Code with Errors

```
You: My Python script is throwing an error. Here's the code:
[paste your code]

Error message:
AttributeError: 'NoneType' object has no attribute 'split'

Agent: I've analyzed your code and found the issue. The error occurs on
line 15 where you're calling .split() on the result of file.read().

The problem is that when the file is empty, read() returns an empty
string, but your code doesn't handle this case.

Here's the fix:

[Agent shows before/after code with explanation]

The corrected code includes:
1. Check if content is not None before calling split()
2. Handle empty file case gracefully
3. Added try-except block for better error handling

Would you like me to:
1. Add more robust error handling?
2. Add logging for debugging?
3. Create unit tests to prevent this issue?
```

### Example 4: Generate Tests

```
You: Generate pytest tests for my calculator.py file

Agent: I'll create comprehensive pytest tests for your calculator.py.
The test suite will include:
- Test for each function
- Edge cases (division by zero, negative numbers, etc.)
- Parametrized tests for multiple inputs
- Fixtures for common test data

[Agent creates test_calculator.py]

Test coverage includes:
✓ Basic arithmetic operations
✓ Scientific operations
✓ Edge cases and error conditions
✓ Input validation

To run the tests:
pytest test_calculator.py -v

To check coverage:
pytest --cov=calculator test_calculator.py
```

### Example 5: Create Documentation

```
You: Generate documentation for my Python project

Agent: I'll create comprehensive documentation for your project. This
will include:
1. README.md with overview and quick start
2. API.md with detailed API reference
3. CONTRIBUTING.md for contributors
4. Updated docstrings in all Python files

[Agent analyzes project and generates documentation]

Documentation created:
✓ README.md - Project overview, installation, usage
✓ docs/API.md - Complete API reference
✓ docs/EXAMPLES.md - Usage examples
✓ docs/CONTRIBUTING.md - Contribution guidelines
✓ All Python files updated with proper docstrings

The documentation follows Google-style docstring format and includes:
- Function signatures with type hints
- Parameter descriptions
- Return value descriptions
- Usage examples
- Exception documentation
```

---

## Advanced Features

### 1. Multi-Language Support

Work with multiple programming languages in the same session:

```
You: Create a web application with:
- Python FastAPI backend
- React TypeScript frontend
- Shell deployment scripts

Agent: I'll create a full-stack web application with the following
structure:

backend/ (Python FastAPI)
  ├── app/
  │   ├── main.py
  │   ├── api/
  │   ├── models/
  │   └── services/
  └── tests/

frontend/ (React TypeScript)
  ├── src/
  │   ├── components/
  │   ├── pages/
  │   └── App.tsx
  └── package.json

scripts/ (Shell)
  ├── deploy.sh
  ├── setup-dev.sh
  └── run-tests.sh

[Agent creates all files with appropriate code for each language]
```

### 2. Task Loop Processing

For complex tasks that need iterative refinement:

```
You: Build a complete REST API for a blog application with authentication,
post management, and comment system. Make sure it follows best practices.

Agent: This is a complex task. I'll use task loop processing to:
1. Create initial implementation
2. Run tests and validation
3. Check for security issues
4. Verify best practices
5. Refine based on feedback

[Phase 1: Initial Implementation]
Creating project structure...
✓ Project structure created

[Phase 2: Implementation]
Creating authentication system...
Creating post management API...
Creating comment system...
✓ Core functionality implemented

[Phase 3: Testing]
Running tests...
⚠ Found 3 issues in authentication
✓ Fixed authentication issues
✓ All tests passing

[Phase 4: Security Check]
Running security analysis...
✓ No security vulnerabilities found

[Phase 5: Best Practices]
Checking code quality...
✓ Code follows PEP 8
✓ All functions have docstrings
✓ Type hints present

[Phase 6: Final Review]
✓ All components working
✓ Tests passing
✓ Documentation complete
✓ Ready for deployment
```

### 3. Semantic Code Search

Use vector database for intelligent code search:

```
You: Find all functions in my codebase that handle user authentication

Agent: Searching codebase semantically for authentication-related code...

Found 5 relevant functions:

1. authenticate_user() in auth/users.py
   Purpose: Validates user credentials against database
   Lines: 45-67

2. verify_token() in auth/jwt.py
   Purpose: Verifies JWT token validity
   Lines: 23-35

3. check_permissions() in auth/permissions.py
   Purpose: Checks if user has required permissions
   Lines: 15-28

[Shows code snippets for each function]

Would you like me to:
1. Explain how these functions work together?
2. Identify any security issues?
3. Suggest improvements?
```

### 4. AI-Enhanced Git Commits

Generate intelligent commit messages:

```bash
# Make some changes to your code
vim calculator.py

# Use AI-enhanced commit
python main.py --git-commit

Agent: Analyzing changes...

Changes detected:
- Modified calculator.py:
  - Added error handling for division by zero
  - Added input validation
  - Improved error messages

Suggested commit message:
---
feat(calculator): enhance error handling and validation

- Add division by zero check with clear error message
- Add input type validation for all operations
- Improve error messages for better user experience

This change improves robustness and user feedback.
---

Would you like to:
1. Use this commit message
2. Edit the message
3. See a different suggestion
```

### 5. Codebase Awareness

The agent understands your entire codebase:

```
You: Where is the user authentication implemented?

Agent: I've analyzed your codebase. User authentication is implemented
across several files:

Core implementation:
- backend/app/auth/authentication.py (main logic)
- backend/app/auth/jwt.py (token handling)
- backend/app/models/user.py (user model)

API endpoints:
- backend/app/api/v1/endpoints/auth.py (login, logout, register)

Database:
- backend/app/db/repositories/user_repository.py (user CRUD)

Configuration:
- backend/app/core/config.py (auth settings)

Tests:
- backend/tests/auth/test_authentication.py

The authentication flow works as follows:
1. User submits credentials to /api/v1/auth/login
2. authentication.py validates credentials
3. jwt.py generates access and refresh tokens
4. Tokens are returned to client

Would you like me to explain any specific part in detail?
```

---

## Configuration Guide

### Basic Configuration (config.yaml)

```yaml
# Choose your primary LLM provider
ollama:
  host: "http://localhost"
  port: 11434

openai:
  api_key: "your-key-here"  # or use environment variable

# Select primary provider
fallback:
  enabled: true
  primary_provider: "ollama"      # or "openai"
  fallback_provider: "openai"     # or "ollama"

# Configure models
models:
  ollama_default: "llama2"        # or llama3, mistral, codellama
  openai_default: "gpt-3.5-turbo" # or gpt-4, gpt-4-turbo
  temperature: 0.7                # 0.0-2.0, higher = more creative

# Memory settings
memory:
  enabled: true
  use_vector_memory: true
  default_max_context_window: 4096

# Enable/disable features
vector_db:
  enabled: true

development_tools:
  enabled: true
  linter:
    auto_lint: false
  formatter:
    auto_format: false
```

### Environment Variables

You can override any configuration with environment variables:

```bash
# LLM settings
export AI_AGENT_OLLAMA__HOST="http://192.168.1.100"
export AI_AGENT_OPENAI__API_KEY="sk-..."

# Model selection
export AI_AGENT_MODELS__OLLAMA_DEFAULT="llama3"
export AI_AGENT_MODELS__TEMPERATURE="0.5"

# Feature toggles
export AI_AGENT_VECTOR_DB__ENABLED="true"
export AI_AGENT_MEMORY__USE_VECTOR_MEMORY="true"
```

---

## Common Workflows

### Workflow 1: New Project from Scratch

```
1. Start console: python main.py

2. Initialize project:
   You: Create a new Python web application project called "my-api"
        using FastAPI framework

3. Add features:
   You: Add user authentication with JWT
   You: Add CRUD endpoints for managing posts
   You: Add database models for users and posts

4. Generate tests:
   You: Generate pytest tests for all endpoints

5. Create documentation:
   You: Generate API documentation

6. Run tests:
   You: Run all tests and fix any issues

7. Done! Your project is ready for deployment.
```

### Workflow 2: Debug Existing Code

```
1. Describe the problem:
   You: My application is throwing a database connection error

2. Agent analyzes and diagnoses:
   Agent: [Analyzes logs, checks configuration, identifies issue]

3. Agent suggests fixes:
   Agent: The issue is in your database URL configuration...

4. Apply fix:
   You: Apply the suggested fix

5. Verify:
   Agent: [Runs tests to verify fix works]
```

### Workflow 3: Code Review and Improvement

```
1. Request review:
   You: Review my code and suggest improvements

2. Agent analyzes:
   Agent: [Checks code quality, security, best practices]

3. Agent provides feedback:
   - Security issues found
   - Performance improvements suggested
   - Code style recommendations

4. Apply improvements:
   You: Apply all suggested improvements

5. Verify improvements:
   Agent: [Runs tests and validates changes]
```

---

## Troubleshooting

### Issue: "Connection to Ollama failed"

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve

# Or configure fallback to OpenAI in config.yaml
```

### Issue: "No module named 'xxxx'"

**Solution:**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Or install specific package
pip install xxxx
```

### Issue: "Out of memory" errors

**Solution:**
```yaml
# In config.yaml, reduce context window:
memory:
  default_max_context_window: 2048  # Reduce from 4096
```

### Issue: Agent responses are too slow

**Solution:**
```yaml
# Use a faster model:
models:
  ollama_default: "llama2"  # Faster than llama3
  # Or use smaller models:
  ollama_default: "phi3"    # Very fast, smaller model
```

### Issue: Agent doesn't understand my codebase

**Solution:**
```
# Ensure codebase indexing is enabled:
You: Index my codebase

# Or ask for specific analysis:
You: Analyze the project structure and remember the key components
```

---

## Next Steps

### Learn More

- **[Complete Feature Inventory](COMPLETE_FEATURE_INVENTORY.md)** - All features and capabilities
- **[User Guide](guides/user_guide.md)** - Comprehensive user documentation
- **[Extending Guide](guides/EXTENDING_GUIDE.md)** - How to extend the console
- **[Agent Catalog](reference/AGENT_CATALOG.md)** - All available agents
- **[API Reference](reference/AGENT_TOOL_GUIDE.md)** - Tool and API documentation

### Join the Community

- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share tips
- Contributing: See CONTRIBUTING.md for guidelines

### Tips for Best Results

1. **Be specific**: Clear, detailed requests get better results
2. **Iterate**: Use follow-up questions to refine results
3. **Use examples**: Show examples of what you want
4. **Provide context**: Explain your project and goals
5. **Review suggestions**: Always review AI-generated code before using

---

**Happy coding with AI Agent Console! 🚀**

For more help, type `help` in the console or visit the documentation.
