# Testing Guide - UAIDE

Complete guide for running and writing tests in UAIDE.

---

## 🧪 Running Tests

### Quick Start

```bash
# Run all tests
.\scripts\run_tests.bat

# Show test summary
.\scripts\test_summary.bat
```

### Manual Test Execution

```bash
# Activate virtual environment first
call venv\Scripts\activate.bat

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_bloat_detector.py -v

# Run specific test
pytest tests/test_bloat_detector.py::TestBloatDetector::test_detect_all -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

---

## 📊 Test Coverage

### Current Test Files

**Phase 1-5 Tests (Existing):**
- `test_config.py` - Configuration management
- `test_database.py` - Database operations
- `test_utils.py` - Utility functions
- `test_project_manager.py` - Project management
- `test_code_generator.py` - Code generation
- `test_tester.py` - Test generation and execution
- `test_doc_manager.py` - Documentation
- `test_code_refactorer.py` - Refactoring
- `test_api_generator.py` - API generation
- `test_database_tools.py` - Database tools
- `test_context_manager.py` - Context management
- `test_rule_manager.py` - Rule management
- `test_task_decomposer.py` - Task decomposition
- `test_orchestrator.py` - Core orchestrator
- `test_event_bus.py` - Event system

**v1.3.0 Tests (New):**
- `test_bloat_detector.py` - Bloat detection (25 tests)
- `test_quality_monitor.py` - Quality monitoring (20 tests)
- `test_context_pruner.py` - Context pruning (22 tests)
- `test_codebase_indexer.py` - Codebase indexing (23 tests)

**Total: 19 test files, 160+ tests**

---

## ✅ Test Organization

### Test Structure

```
tests/
├── test_*.py           # Test files (auto-discovered by pytest)
├── conftest.py         # Shared fixtures (if needed)
└── fixtures/           # Test data and fixtures
```

### Naming Conventions

- **Test Files**: `test_<module_name>.py`
- **Test Classes**: `Test<ClassName>`
- **Test Functions**: `test_<functionality>`
- **Fixtures**: Descriptive names (e.g., `temp_project`, `pruner_with_items`)

---

## 🔧 Writing Tests

### Basic Test Template

```python
"""
Tests for MyModule
"""

import pytest
from src.modules.my_module import MyClass


@pytest.fixture
def my_fixture():
    """Create test fixture."""
    # Setup
    obj = MyClass()
    yield obj
    # Teardown (if needed)


class TestMyClass:
    """Test MyClass functionality."""
    
    def test_basic_functionality(self, my_fixture):
        """Test basic functionality."""
        result = my_fixture.do_something()
        assert result is not None
    
    def test_edge_case(self):
        """Test edge case."""
        obj = MyClass()
        with pytest.raises(ValueError):
            obj.invalid_operation()
```

### Test Best Practices

1. **One Concept Per Test**
   - Each test should test one specific behavior
   - Keep tests focused and simple

2. **Use Descriptive Names**
   - Test names should describe what they test
   - Use `test_<action>_<expected_result>` pattern

3. **Arrange-Act-Assert Pattern**
   ```python
   def test_something():
       # Arrange: Set up test data
       data = create_test_data()
       
       # Act: Execute the functionality
       result = process(data)
       
       # Assert: Verify the result
       assert result == expected_value
   ```

4. **Use Fixtures for Setup**
   - Avoid code duplication
   - Use pytest fixtures for common setup
   - Use `@pytest.fixture` decorator

5. **Test Edge Cases**
   - Empty inputs
   - Invalid inputs
   - Boundary conditions
   - Error conditions

6. **Mock External Dependencies**
   ```python
   from unittest.mock import Mock, patch
   
   def test_with_mock():
       with patch('module.external_call') as mock_call:
           mock_call.return_value = 'mocked'
           result = function_that_calls_external()
           assert result == 'mocked'
   ```

---

## 📈 Coverage Goals

### Target Coverage

- **Overall**: >85%
- **Core Modules**: >90%
- **New Features**: >85%
- **Critical Paths**: 100%

### Checking Coverage

```bash
# Terminal report
pytest tests/ --cov=src --cov-report=term-missing

# HTML report (detailed)
pytest tests/ --cov=src --cov-report=html
start htmlcov/index.html

# XML report (for CI/CD)
pytest tests/ --cov=src --cov-report=xml
```

### Coverage Report Example

```
Name                                 Stmts   Miss  Cover   Missing
------------------------------------------------------------------
src/modules/bloat_detector.py         250      15    94%   45-47, 89
src/modules/quality_monitor.py        230      12    95%   123-125
src/modules/context_pruner.py         240      18    93%   67-69, 145
src/modules/codebase_indexer.py       245      20    92%   234-238
------------------------------------------------------------------
TOTAL                                 965      65    93%
```

---

## 🚀 Continuous Testing

### Pre-Commit Testing

Run tests before committing:

```bash
# Quick test
pytest tests/ -v --tb=short

# Full test with coverage
.\scripts\run_tests.bat
```

### Test-Driven Development (TDD)

1. Write failing test
2. Implement minimal code to pass
3. Refactor while keeping tests green
4. Repeat

### Regression Testing

- Run full test suite after changes
- Ensure no existing tests break
- Add tests for bug fixes

---

## 🐛 Debugging Tests

### Running Failed Tests Only

```bash
# Run only failed tests from last run
pytest --lf

# Run failed tests first, then others
pytest --ff
```

### Verbose Output

```bash
# Show print statements
pytest tests/ -v -s

# Show full traceback
pytest tests/ -v --tb=long

# Stop at first failure
pytest tests/ -x
```

### Using Debugger

```python
def test_with_debugger():
    import pdb; pdb.set_trace()
    # Test code here
```

Or use pytest's built-in debugger:

```bash
pytest tests/ --pdb  # Drop into debugger on failure
```

---

## 📝 Test Documentation

### Docstrings

Every test should have a docstring:

```python
def test_bloat_detection():
    """
    Test that BloatDetector correctly identifies all types of bloat.
    
    This test creates a project with various bloat types and verifies
    that the detector finds them all.
    """
    # Test implementation
```

### Test Comments

Use comments for complex test logic:

```python
def test_complex_scenario():
    """Test complex scenario."""
    # Setup: Create project with circular dependencies
    create_circular_deps()
    
    # Act: Run detection
    result = detector.detect_circular()
    
    # Assert: Should find the cycle
    assert len(result) > 0  # At least one cycle found
    assert 'a.py' in result[0]  # Contains expected file
```

---

## 🔄 Test Maintenance

### Updating Tests

When code changes:
1. Update affected tests
2. Add tests for new functionality
3. Remove obsolete tests
4. Refactor duplicate test code

### Test Refactoring

- Extract common setup to fixtures
- Remove duplicate assertions
- Simplify complex tests
- Keep tests maintainable

---

## 📊 Test Metrics

### Key Metrics

- **Test Count**: 160+ tests
- **Coverage**: >85%
- **Pass Rate**: 100%
- **Execution Time**: <30 seconds

### Monitoring

```bash
# Count tests
pytest tests/ --collect-only | grep "test session starts"

# Show slowest tests
pytest tests/ --durations=10

# Show test execution time
pytest tests/ -v --durations=0
```

---

## 🎯 Testing Checklist

### For New Features

- [ ] Unit tests for all public methods
- [ ] Integration tests for workflows
- [ ] Edge case tests
- [ ] Error handling tests
- [ ] Performance tests (if applicable)
- [ ] Documentation tests (docstrings)

### For Bug Fixes

- [ ] Add test that reproduces the bug
- [ ] Verify test fails before fix
- [ ] Implement fix
- [ ] Verify test passes after fix
- [ ] Add regression test

---

## 🔗 Related Documentation

- [TESTING.md](../TESTING.md) - Testing overview
- [API.md](API.md) - API documentation
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines

---

## 📞 Support

If tests fail:
1. Check error messages carefully
2. Run with verbose output (`-v`)
3. Check if dependencies are installed
4. Verify virtual environment is activated
5. Review test documentation

---

**Happy Testing!** 🧪✨
