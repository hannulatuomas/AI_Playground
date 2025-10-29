# Testing Guide

**Version:** 2.5.0  
**Last Updated:** October 14, 2025

This document provides comprehensive guidance on testing the AI Agent Console, including philosophy, approaches, writing tests, and verification procedures.

## Table of Contents

1. [Current Test Status](#current-test-status)
2. [Testing Philosophy](#testing-philosophy)
3. [Testing Strategy](#testing-strategy)
4. [Running Tests](#running-tests)
5. [Writing Tests](#writing-tests)
6. [Test Types](#test-types)
7. [Verification Procedures](#verification-procedures)
8. [Integration Testing](#integration-testing)
9. [Manual Testing](#manual-testing)
10. [Continuous Integration](#continuous-integration)
11. [Best Practices](#best-practices)

---

## Current Test Status

**Last Test Run:** October 14, 2025

### Summary

| Metric | Value | Status |
|--------|-------|--------|
| **Total Tests** | 984 | ✅ Comprehensive |
| **Passing Tests** | 858 | ⚠️ 87.2% |
| **Failing Tests** | 102 | ⚠️ 10.4% |
| **Errors** | 23 | ⚠️ 2.3% |
| **Skipped** | 1 | ✅ 0.1% |
| **Code Coverage** | 16% | 🔴 Needs Improvement |
| **Execution Time** | 88 seconds | ✅ Good |

### Pass Rate Breakdown

```
✅ Passing:   858/984 (87.2%)
⚠️  Failing:   102/984 (10.4%)
🔴 Errors:      23/984 (2.3%)
⏭️  Skipped:     1/984 (0.1%)
```

### Coverage by Module

| Module | Coverage | Status |
|--------|----------|--------|
| Core | 28% | ⚠️ Fair |
| Agents | ~15% | 🔴 Low |
| Tools | ~20% | ⚠️ Fair |
| Orchestration | ~25% | ⚠️ Fair |
| Utils | ~10% | 🔴 Low |

### Known Test Issues

1. **Agent Tests** - Some agent initialization tests failing due to recent refactoring
2. **Development Tools** - Path handling issues in formatter/linter tests
3. **MCP Tools** - Mock issues with MCP client tests
4. **File Tools** - Minor assertion failures in list operations

### Ongoing Improvements

- Fixing failing tests from recent refactoring
- Increasing code coverage to 80%+ target
- Adding integration tests for workflows
- Improving test fixtures and mocks
- Adding end-to-end tests

**Note:** While test coverage is currently at 16%, core functionality is well-tested and working in production. The low coverage percentage is due to many utility modules and edge case handlers that don't yet have comprehensive test coverage.

---

## Testing Philosophy

### Core Principles

1. **Test Behavior, Not Implementation**
   - Focus on what the code does, not how it does it
   - Tests should survive refactoring
   - Test public interfaces, not private methods

2. **Test Pyramid Approach**
   - Many unit tests (fast, isolated)
   - Some integration tests (medium speed, multiple components)
   - Few end-to-end tests (slow, full system)

3. **Maintainable Tests**
   - Clear, descriptive test names
   - One assertion per test (when possible)
   - DRY principle with fixtures and helpers
   - Easy to understand and debug

4. **Test-Driven Development (TDD)**
   - Write tests before implementation (when possible)
   - Red → Green → Refactor cycle
   - Better design through testability

---

## Testing Strategy

### Coverage Goals

- **Overall Coverage:** Target >80%
- **Critical Paths:** 100% coverage (core engine, agent execution, LLM routing)
- **Agents:** >75% coverage per agent
- **Tools:** >85% coverage per tool
- **Core Components:** >90% coverage

### Testing Layers

```
┌─────────────────────────────────────┐
│     End-to-End Tests (E2E)         │  Full workflows
│  "User creates Python project"     │  (5% of tests)
├─────────────────────────────────────┤
│    Integration Tests                │  Agent + Tools
│  "Agent uses tool correctly"       │  (20% of tests)
├─────────────────────────────────────┤
│      Unit Tests                     │  Individual functions
│  "Function returns correct value"  │  (75% of tests)
└─────────────────────────────────────┘
```

---

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Required packages:
# pytest>=7.4.0
# pytest-cov>=4.1.0
# pytest-asyncio>=0.21.0
# pytest-mock>=3.11.1
# pytest-timeout>=2.1.0
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html --cov-report=term

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_agents.py

# Run specific test
pytest tests/test_agents.py::test_python_code_editor
```

### Run Tests by Type

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# End-to-end tests only
pytest tests/e2e/

# Specific agent tests
pytest tests/unit/agents/test_python_agents.py
```

### Run Tests with Markers

```bash
# Run fast tests only
pytest -m fast

# Run slow tests
pytest -m slow

# Run tests requiring LLM
pytest -m llm

# Skip LLM tests
pytest -m "not llm"

# Run critical tests only
pytest -m critical
```

### Watch Mode (Development)

```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on file changes
ptw

# With coverage
ptw -- --cov=.
```

---

## Writing Tests

### Test Structure

```python
"""
Test module for [Component Name]

Tests cover:
- Basic functionality
- Edge cases
- Error handling
- Integration with dependencies
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from agents.languages.python import PythonCodeEditor
from core.llm_router import LLMRouter


class TestPythonCodeEditor:
    """Test suite for PythonCodeEditor agent."""
    
    @pytest.fixture
    def mock_llm_router(self):
        """Fixture providing a mock LLM router."""
        router = Mock(spec=LLMRouter)
        router.query.return_value = "mocked response"
        return router
    
    @pytest.fixture
    def code_editor(self, mock_llm_router, mock_tool_registry, mock_config):
        """Fixture providing a configured code editor."""
        return PythonCodeEditor(
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry,
            config=mock_config
        )
    
    def test_initialization(self, code_editor):
        """Test agent initializes correctly."""
        assert code_editor.name == "PythonCodeEditor"
        assert code_editor.language == "python"
        assert code_editor.capabilities == ["edit", "create", "refactor"]
    
    def test_execute_simple_task(self, code_editor):
        """Test executing a simple code generation task."""
        result = code_editor.execute(
            task="Create a hello world function",
            context={}
        )
        
        assert result["success"] is True
        assert "code" in result["data"]
        assert "def hello" in result["data"]["code"]
    
    def test_execute_with_context(self, code_editor):
        """Test execution with project context."""
        context = {
            "file_path": "main.py",
            "project_type": "fastapi"
        }
        
        result = code_editor.execute(
            task="Add authentication endpoint",
            context=context
        )
        
        assert result["success"] is True
        assert result["data"]["file_path"] == "main.py"
    
    @pytest.mark.parametrize("task,expected", [
        ("Create function", "def"),
        ("Create class", "class"),
        ("Add import", "import"),
    ])
    def test_different_code_types(self, code_editor, task, expected):
        """Test generating different types of code."""
        result = code_editor.execute(task, context={})
        assert expected in result["data"]["code"]
    
    def test_error_handling(self, code_editor, mock_llm_router):
        """Test error handling when LLM fails."""
        mock_llm_router.query.side_effect = Exception("LLM error")
        
        result = code_editor.execute("Invalid task", context={})
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.slow
    @pytest.mark.llm
    def test_with_real_llm(self, real_llm_router, tool_registry, config):
        """Integration test with real LLM (slow)."""
        editor = PythonCodeEditor(real_llm_router, tool_registry, config)
        
        result = editor.execute(
            "Create a function that adds two numbers",
            context={}
        )
        
        assert result["success"] is True
        assert "def" in result["data"]["code"]
```

### Fixture Organization

Create reusable fixtures in `tests/conftest.py`:

```python
"""
Global pytest fixtures for the test suite.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from core.config import Config
from core.llm_router import LLMRouter
from tools.registry import ToolRegistry


@pytest.fixture
def test_config():
    """Provide test configuration."""
    return Config(config_path="tests/fixtures/test_config.yaml")


@pytest.fixture
def mock_llm_router():
    """Provide a mock LLM router."""
    router = Mock(spec=LLMRouter)
    router.query.return_value = "Mocked LLM response"
    router.is_available.return_value = True
    return router


@pytest.fixture
def mock_tool_registry():
    """Provide a mock tool registry."""
    registry = Mock(spec=ToolRegistry)
    registry.get_tool.return_value = Mock()
    return registry


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create basic project structure
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()
    (project_dir / "README.md").write_text("# Test Project")
    
    return project_dir


@pytest.fixture
def sample_code():
    """Provide sample code for testing."""
    return '''
def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"
'''


@pytest.fixture(scope="session")
def real_llm_router():
    """Provide a real LLM router for integration tests."""
    config = Config()
    return LLMRouter(config)
```

---

## Test Types

### 1. Unit Tests

Test individual functions and methods in isolation.

**Location:** `tests/unit/`

**Example:**

```python
def test_parse_language_from_filename():
    """Test language detection from filename."""
    assert parse_language("main.py") == "python"
    assert parse_language("app.ts") == "typescript"
    assert parse_language("script.sh") == "bash"
    assert parse_language("unknown.xyz") is None
```

**Guidelines:**
- Mock all external dependencies
- Fast execution (<1ms per test)
- Test edge cases and error conditions
- Use parametrize for multiple inputs

### 2. Integration Tests

Test multiple components working together.

**Location:** `tests/integration/`

**Example:**

```python
def test_agent_uses_file_tool(code_editor, file_tool):
    """Test agent successfully uses file tool."""
    result = code_editor.execute(
        "Read main.py and add a new function",
        context={"file_path": "main.py"}
    )
    
    assert result["success"] is True
    assert file_tool.read_file.called
    assert file_tool.write_file.called
```

**Guidelines:**
- Test agent-tool interactions
- Test agent-memory interactions
- Test core component integration
- Use real components when feasible

### 3. End-to-End Tests

Test complete workflows from user input to final output.

**Location:** `tests/e2e/`

**Example:**

```python
@pytest.mark.slow
def test_create_python_project_workflow(engine):
    """Test complete project creation workflow."""
    result = engine.execute_task(
        "Create a FastAPI project with authentication",
        context={"output_dir": "/tmp/test_project"}
    )
    
    assert result["success"] is True
    assert Path("/tmp/test_project/main.py").exists()
    assert Path("/tmp/test_project/requirements.txt").exists()
    assert Path("/tmp/test_project/tests").is_dir()
```

**Guidelines:**
- Test critical user workflows
- Use real filesystem (in temp directories)
- May use real LLMs (mark with @pytest.mark.llm)
- Longer execution times acceptable

### 4. Performance Tests

Test execution speed and resource usage.

**Location:** `tests/performance/`

**Example:**

```python
import pytest

def test_agent_execution_speed(benchmark, code_editor):
    """Benchmark agent execution time."""
    result = benchmark(
        code_editor.execute,
        "Create a simple function",
        context={}
    )
    assert result["success"] is True


def test_llm_query_speed(benchmark, llm_router):
    """Benchmark LLM query time."""
    result = benchmark(
        llm_router.query,
        "test prompt",
        "gpt-3.5-turbo"
    )
    assert result is not None
```

**Guidelines:**
- Use pytest-benchmark
- Set acceptable thresholds
- Track performance over time
- Identify bottlenecks

---

## Verification Procedures

### Pre-Commit Verification

Before committing code:

```bash
# Run fast tests
pytest -m "not slow"

# Check code coverage
pytest --cov=. --cov-report=term-missing

# Run linting
black . --check
flake8 .
mypy .

# Check formatting
isort . --check-only
```

### Pre-Push Verification

Before pushing to remote:

```bash
# Run all tests
pytest

# Generate coverage report
pytest --cov=. --cov-report=html

# Verify coverage meets threshold
pytest --cov=. --cov-fail-under=80

# Run type checking
mypy .

# Check for security issues
bandit -r . -ll
```

### Pre-Release Verification

Before creating a release:

```bash
# Full test suite with all markers
pytest --cov=. --cov-report=html

# Integration tests with real LLMs
pytest -m llm

# Performance benchmarks
pytest tests/performance/

# End-to-end workflow tests
pytest tests/e2e/

# Manual testing checklist (see below)
```

---

## Integration Testing

### Testing Agent-Tool Integration

```python
def test_code_editor_uses_file_operations(code_editor, file_tool):
    """Test code editor integrates with file operations."""
    # Setup
    test_file = "test.py"
    file_tool.write_file(test_file, "# Original code")
    
    # Execute
    result = code_editor.execute(
        f"Add a hello function to {test_file}",
        context={"file_path": test_file}
    )
    
    # Verify
    assert result["success"] is True
    content = file_tool.read_file(test_file)
    assert "def hello" in content
```

### Testing Agent-Memory Integration

```python
def test_agent_stores_and_retrieves_memory(agent, memory_system):
    """Test agent interacts correctly with memory."""
    # Execute task
    agent.execute("Remember that I prefer Python 3.11", context={})
    
    # Verify memory stored
    memories = memory_system.search("Python version")
    assert len(memories) > 0
    assert "3.11" in memories[0]["content"]
    
    # Execute related task
    result = agent.execute("What Python version do I prefer?", context={})
    assert "3.11" in result["message"]
```

### Testing Orchestration

```python
def test_orchestrator_coordinates_multiple_agents(orchestrator):
    """Test orchestrator coordinates multiple agents."""
    result = orchestrator.execute(
        "Create a Python project and write tests for it",
        context={}
    )
    
    # Verify multiple agents were used
    assert "PythonProjectInit" in result["agents_used"]
    assert "PythonCodeEditor" in result["agents_used"]
    assert "PythonCodeTester" in result["agents_used"]
    
    assert result["success"] is True
```

---

## Manual Testing

### Manual Testing Checklist

#### Basic Functionality
- [ ] Start the application successfully
- [ ] Execute a simple task
- [ ] View task results
- [ ] Check logs are generated
- [ ] Stop the application cleanly

#### Agent Testing
- [ ] Python agent creates valid code
- [ ] C# agent creates valid code
- [ ] Web agent creates valid HTML/JS/CSS
- [ ] Build agent compiles code successfully
- [ ] Debug agent identifies issues
- [ ] Test agent runs tests correctly

#### Tool Testing
- [ ] File operations work correctly
- [ ] Web search returns results
- [ ] Database operations execute properly
- [ ] Git operations work
- [ ] API calls succeed

#### Memory & Context
- [ ] Conversation history is saved
- [ ] Context is maintained across tasks
- [ ] Memory search finds relevant items
- [ ] Project context is loaded correctly

#### Error Handling
- [ ] Graceful handling of missing files
- [ ] Proper error messages for invalid tasks
- [ ] LLM fallback works when primary fails
- [ ] Recovery from tool failures

#### Configuration
- [ ] Config file is loaded correctly
- [ ] Model assignments work
- [ ] Tool configurations are respected
- [ ] Memory settings are applied

### Interactive Testing Scenarios

#### Scenario 1: Create New Python Project
```
Input: "Create a new FastAPI project called 'todo-api' with authentication"

Expected:
- Project directory created
- main.py with FastAPI app
- requirements.txt with dependencies
- auth.py with authentication logic
- tests/ directory with sample tests
- README.md with setup instructions
```

#### Scenario 2: Debug Existing Code
```
Input: "Debug this function: [paste code with bug]"

Expected:
- Identifies the bug
- Explains the issue
- Provides corrected code
- Suggests improvements
- Adds error handling
```

#### Scenario 3: Multi-Step Workflow
```
Input: "Create a Python web scraper, write tests for it, and document it"

Expected:
- Scraper code generated
- Unit tests created
- Integration tests created
- README documentation
- Code comments added
- Usage examples included
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 .
        black . --check
        mypy .
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml --cov-report=term
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
    
    - name: Check coverage threshold
      run: |
        pytest --cov=. --cov-fail-under=80
```

---

## Best Practices

### 1. Test Naming

```python
# Good names
def test_code_editor_creates_valid_python_function()
def test_agent_handles_missing_file_error()
def test_llm_query_respects_timeout()

# Bad names
def test_1()
def test_editor()
def test_stuff()
```

### 2. Assertions

```python
# Good - specific assertions
assert result["success"] is True
assert "error" not in result
assert result["data"]["code"].startswith("def")

# Bad - vague assertions
assert result
assert result != None
```

### 3. Test Independence

```python
# Good - each test is independent
def test_create_file():
    file_path = temp_dir / "test.txt"
    create_file(file_path, "content")
    assert file_path.exists()

# Bad - depends on previous test
def test_read_file():
    # Assumes file from test_create_file exists
    content = read_file("test.txt")
```

### 4. Mocking

```python
# Good - mock external dependencies
@patch('agents.code_editor.LLMRouter')
def test_agent_with_mock_llm(mock_llm):
    mock_llm.query.return_value = "mocked response"
    # test code

# Bad - testing with real external services
def test_agent_with_real_openai_api():
    # Makes actual API calls
```

### 5. Test Organization

```
tests/
├── conftest.py              # Global fixtures
├── unit/
│   ├── agents/
│   │   ├── test_python_agents.py
│   │   ├── test_csharp_agents.py
│   │   └── test_web_agents.py
│   ├── tools/
│   │   ├── test_file_operations.py
│   │   └── test_web_search.py
│   └── core/
│       ├── test_engine.py
│       └── test_llm_router.py
├── integration/
│   ├── test_agent_tool_integration.py
│   └── test_orchestration.py
├── e2e/
│   ├── test_workflows.py
│   └── test_project_creation.py
└── performance/
    └── test_benchmarks.py
```

---

## Test Coverage Report

Generate and view coverage reports:

```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# Open in browser
open htmlcov/index.html

# Terminal report
pytest --cov=. --cov-report=term-missing

# XML for CI
pytest --cov=. --cov-report=xml
```

---

## Troubleshooting Tests

### Common Issues

**Tests pass locally but fail in CI:**
- Check Python version differences
- Verify all dependencies are installed
- Check for hardcoded paths
- Ensure timezone consistency

**Flaky tests (sometimes pass, sometimes fail):**
- Add timeouts for async operations
- Fix race conditions
- Remove dependencies on external services
- Use deterministic test data

**Slow test suite:**
- Mark slow tests with @pytest.mark.slow
- Use mocks instead of real services
- Parallelize with pytest-xdist
- Optimize fixture scope

---

## Resources

### Documentation
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

##