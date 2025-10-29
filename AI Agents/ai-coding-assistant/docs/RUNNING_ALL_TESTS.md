# Running All Tests - Quick Guide

## 🧪 Test Runners Available

We provide multiple ways to run all tests in the project:

### Option 1: Simple Batch File (Windows)
```batch
run_all_tests.bat
```

### Option 2: Full Script (Windows)
```batch
scripts\run_all_tests.bat
```

### Option 3: Python Script (Cross-Platform)
```bash
# Basic usage
python run_all_tests.py

# Verbose output
python run_all_tests.py --verbose

# Stop on first failure
python run_all_tests.py --stop-on-fail
```

---

## 📋 Test Suites Included

The test runner executes all test suites in sequence:

1. **Core Tests** (`scripts/run_tests.bat`)
   - Core functionality tests
   - Basic feature verification

2. **RAG Tests** (`scripts/run_rag_tests.bat`)
   - Phase 8 RAG system tests
   - Vector search and indexing

3. **Advanced RAG Tests** (`scripts/run_advanced_rag_tests.bat`)
   - Phase 9.1 features (query expansion, feedback, graph)

4. **Phase 9.2 Tests** (`scripts/run_phase_92_tests.bat`)
   - CodeBERT embeddings
   - Multi-modal retrieval

5. **Phase 9.3 Tests** (`scripts/run_phase_93_tests.bat`)
   - Cross-encoder reranking
   - Hybrid search
   - Query understanding

6. **Project Lifecycle Tests** (`scripts/run_project_lifecycle_tests.bat`)
   - Phase 10 features
   - Templates, scaffolding, maintenance, archiving

7. **Automated Testing Tests** (`test_automated_testing.py`)
   - Phase 11.1 features
   - Test generation, code analysis

---

## 📊 Output Format

### Summary Example
```
============================================================
AI Coding Assistant - Complete Test Suite
Version: 2.1.0
============================================================

[1/7] Running Core Tests...
[PASS] Core Tests

[2/7] Running RAG Tests...
[PASS] RAG Tests

[3/7] Running Advanced RAG Tests...
[PASS] Advanced RAG Tests

[4/7] Running Phase 9.2 Tests...
[PASS] Phase 9.2 Tests

[5/7] Running Phase 9.3 Tests...
[PASS] Phase 9.3 Tests

[6/7] Running Project Lifecycle Tests...
[PASS] Project Lifecycle Tests

[7/7] Running Automated Testing Tests...
[PASS] Automated Testing Tests

============================================================
Test Execution Complete
============================================================

Duration: 45.23 seconds

============================================================
Test Summary
============================================================
Total Test Suites: 7
Passed:            7
Failed:            0

Result: ALL TESTS PASSED!
Status: ✓ SUCCESS
============================================================
```

---

## 🎯 Quick Commands

### Run All Tests (Windows)
```batch
run_all_tests.bat
```

### Run All Tests (Any Platform)
```bash
python run_all_tests.py
```

### Run with Verbose Output
```bash
python run_all_tests.py -v
```

### Stop on First Failure
```bash
python run_all_tests.py --stop-on-fail
```

---

## ⚠️ Troubleshooting

### Issue: Tests Not Found
**Solution**: Run from project root directory
```bash
cd C:\Users\Coder\Downloads\ClaudeDesktop\ai-coding-assistant
python run_all_tests.py
```

### Issue: Python Not Found
**Solution**: Ensure Python 3.12+ is in PATH
```bash
python --version
```

### Issue: Some Tests Fail
**Solution**: 
1. Check individual test output
2. Run specific test suite: `scripts\run_<test_name>.bat`
3. Review error messages

### Issue: .bat Files Don't Run (Non-Windows)
**Solution**: Use Python runner instead
```bash
python run_all_tests.py
```

---

## 📈 Exit Codes

- **0**: All tests passed
- **1**: One or more tests failed

### Use in CI/CD
```bash
python run_all_tests.py
if [ $? -eq 0 ]; then
    echo "All tests passed"
else
    echo "Tests failed"
    exit 1
fi
```

---

## 🔧 Individual Test Suites

If you want to run specific test suites:

```batch
REM Core tests
scripts\run_tests.bat

REM RAG tests
scripts\run_rag_tests.bat

REM Advanced RAG tests
scripts\run_advanced_rag_tests.bat

REM Phase 9.2 tests
scripts\run_phase_92_tests.bat

REM Phase 9.3 tests
scripts\run_phase_93_tests.bat

REM Project lifecycle tests
scripts\run_project_lifecycle_tests.bat

REM Automated testing tests
python test_automated_testing.py
```

---

## 📝 Adding New Tests

To add a new test suite to the runner:

### In `scripts/run_all_tests.bat`
Add a new section:
```batch
REM Test X: New Test Suite
echo.
echo [X/Y] Running New Test Suite...
echo ============================================================
if exist "scripts\run_new_tests.bat" (
    call scripts\run_new_tests.bat
    if %ERRORLEVEL% EQU 0 (
        echo [PASS] New Test Suite
        set /a PASSED_TESTS+=1
    ) else (
        echo [FAIL] New Test Suite
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
) else (
    echo [SKIP] New Test Suite - script not found
)
```

### In `run_all_tests.py`
Add to the `test_suites` list:
```python
test_suites = [
    # ... existing tests ...
    ("New Test Suite", Path("scripts/run_new_tests.bat")),
]
```

---

## 🎉 Best Practices

1. **Run Before Committing**: Always run all tests before committing
2. **CI/CD Integration**: Use in continuous integration
3. **Regular Testing**: Run daily to catch regressions
4. **Verbose When Debugging**: Use `-v` flag to see detailed output
5. **Individual Suites for Speed**: Run specific suites during development

---

## 📞 Support

- **Documentation**: `docs/` folder
- **Test Files**: `tests/` folder
- **Scripts**: `scripts/` folder

---

**Version**: 2.1.0  
**Last Updated**: January 2025
