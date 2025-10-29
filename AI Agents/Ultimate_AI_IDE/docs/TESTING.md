# Testing Guide - UAIDE

Complete guide for testing the Ultimate AI-Powered IDE.

---

## 🚀 Quick Start

### Run All Tests
```bash
scripts\run_tests.bat
```

### Run Phase 2 Tests Only (Faster)
```bash
scripts\quick_test_phase2.bat
```

### Run with Coverage
```bash
scripts\run_tests_coverage.bat
```

### Demo Phase 2 Features
```bash
scripts\demo_phase2.bat
```

---

## 📊 Test Coverage

### Phase 1: Core Infrastructure
| Module | Test File | Coverage | Status |
|--------|-----------|----------|--------|
| Config | test_config.py | ~90% | ✅ |
| Database | test_database.py | ~85% | ✅ |
| Utils | test_utils.py | ~80% | ✅ |

### Phase 2: Basic Features
| Module | Test File | Coverage | Status |
|--------|-----------|----------|--------|
| Project Manager | test_project_manager.py | ~85% | ✅ |
| Code Generator | test_code_generator.py | ~80% | ✅ |
| Tester | test_tester.py | ~75% | ✅ |

**Overall Coverage**: ~80%+

---

## 🧪 Test Structure

### Test Files
```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── test_config.py           # Config system tests
├── test_database.py         # Database tests
├── test_utils.py            # Utility function tests
├── test_project_manager.py  # Project Manager tests (Phase 2)
├── test_code_generator.py   # Code Generator tests (Phase 2)
└── test_tester.py           # Tester module tests (Phase 2)
```

### Test Categories

**Unit Tests**: Test individual functions/classes
- Fast execution
- Isolated components
- Mock external dependencies

**Integration Tests**: Test module interactions
- Real workflows
- Multiple components
- End-to-end scenarios

**Mock Tests**: Use mock AI backend
- No actual AI model needed
- Predictable results
- Fast and reliable

---

## 🎯 Running Tests

### All Tests
```bash
# Using script (recommended)
scripts\run_tests.bat

# Manual (if venv activated)
pytest tests/ -v
```

### Specific Test File
```bash
pytest tests/test_project_manager.py -v
```

### Specific Test Class
```bash
pytest tests/test_project_manager.py::TestProjectDetector -v
```

### Specific Test Method
```bash
pytest tests/test_project_manager.py::TestProjectDetector::test_detect_python_project -v
```

### With Coverage
```bash
# Using script (recommended)
scripts\run_tests_coverage.bat

# Manual
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

### Watch Mode (Re-run on changes)
```bash
pytest-watch tests/
```

---

## 📝 Writing Tests

### Test Template
```python
"""
Tests for MyModule
"""

import pytest
from src.modules.my_module import MyClass


class TestMyClass:
    """Test MyClass functionality."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        obj = MyClass()
        result = obj.do_something()
        
        assert result is not None
        assert result.success is True
    
    def test_error_handling(self):
        """Test error handling."""
        obj = MyClass()
        
        with pytest.raises(ValueError):
            obj.do_something_invalid()
    
    def test_with_fixture(self, tmp_path):
        """Test using pytest fixture."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        obj = MyClass()
        result = obj.process_file(str(test_file))
        
        assert result is True
```

### Using Fixtures
```python
@pytest.fixture
def mock_ai():
    """Mock AI backend."""
    class MockAI:
        def query(self, prompt, max_tokens=1000):
            return "Mock response"
    return MockAI()

def test_with_mock_ai(mock_ai):
    """Test using mock AI."""
    generator = CodeGenerator(mock_ai)
    result = generator.generate_class("Test", "A test class", context)
    assert "class Test" in result
```

### Using tmp_path
```python
def test_file_operations(tmp_path):
    """Test file operations with temporary directory."""
    # tmp_path is automatically created and cleaned up
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')")
    
    # Do your tests
    assert test_file.exists()
    # Cleanup is automatic!
```

---

## 🔍 Test Best Practices

### ✅ Do
- Use descriptive test names
- Test one thing per test
- Use fixtures for setup
- Mock external dependencies
- Clean up resources
- Add docstrings
- Test edge cases
- Test error conditions

### ❌ Don't
- Test multiple things in one test
- Depend on test execution order
- Use hard-coded paths
- Leave files/directories behind
- Skip error testing
- Write tests without assertions
- Ignore warnings

---

## 🐛 Debugging Tests

### Run with More Detail
```bash
pytest tests/ -vv --tb=long
```

### Run with Print Statements
```bash
pytest tests/ -s
```

### Run with Debugger
```bash
pytest tests/ --pdb
```

### Run Failed Tests Only
```bash
pytest tests/ --lf
```

### Run Last Failed First
```bash
pytest tests/ --ff
```

---

## 📈 Coverage Reports

### Generate HTML Report
```bash
scripts\run_tests_coverage.bat
# Opens htmlcov/index.html in browser
```

### View in Terminal
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Coverage Thresholds
```bash
pytest tests/ --cov=src --cov-fail-under=80
```

---

## 🚦 CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    
    - name: Run tests
      run: scripts\run_tests.bat
    
    - name: Run coverage
      run: scripts\run_tests_coverage.bat
```

---

## 📊 Test Metrics

### Current Statistics
- **Total Test Files**: 8
- **Total Test Classes**: 20+
- **Total Test Methods**: 60+
- **Overall Coverage**: ~80%
- **Test Execution Time**: ~10 seconds
- **Lines of Test Code**: ~1,500

### Coverage Goals
- **Target**: 90%+ coverage
- **Minimum**: 80% coverage
- **Critical Paths**: 100% coverage

---

## 🛠️ Troubleshooting

### Tests Won't Run
```bash
# Ensure venv is set up
scripts\setup_venv.bat

# Try running tests again
scripts\run_tests.bat
```

### Import Errors
```bash
# Ensure PYTHONPATH includes src/
set PYTHONPATH=%PYTHONPATH%;src

# Or use pytest with proper path
pytest tests/ --import-mode=importlib
```

### Slow Tests
```bash
# Run only fast tests
pytest tests/ -m "not slow"

# Run Phase 2 tests only
scripts\quick_test_phase2.bat
```

### Coverage Not Working
```bash
# Install coverage
pip install pytest-cov

# Run with coverage
pytest tests/ --cov=src
```

---

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

## 🎯 Next Steps

1. **Run Tests**: `scripts\run_tests.bat`
2. **Check Coverage**: `scripts\run_tests_coverage.bat`
3. **Try Demo**: `scripts\demo_phase2.bat`
4. **Write More Tests**: Follow templates above
5. **Improve Coverage**: Target 90%+

---

**Happy Testing!** 🧪✨
