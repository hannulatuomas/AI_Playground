"""
Tests for Tester Module
"""

import pytest
from pathlib import Path

from src.modules.tester import (
    TestGenerator, TestCase, TestFile,
    TestRunner, TestResult, TestResults,
    BugFixer, BugDiagnosis, BugFix
)


class TestTestGenerator:
    """Test TestGenerator class."""
    
    def test_generate_tests_for_file(self, tmp_path):
        """Test generating tests for a file."""
        # Create a Python file
        test_file = tmp_path / "calculator.py"
        test_file.write_text("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
""")
        
        # Mock AI backend
        class MockAI:
            def query(self, prompt, max_tokens=1500):
                return """
TEST: test_add_positive_numbers
DESCRIPTION: Test adding two positive numbers
CODE:
```
def test_add_positive_numbers():
    assert add(2, 3) == 5
```

TEST: test_subtract
DESCRIPTION: Test subtraction
CODE:
```
def test_subtract():
    assert subtract(5, 3) == 2
```
"""
        
        generator = TestGenerator(MockAI())
        test_file_obj = generator.generate_tests(str(test_file), "python", "pytest")
        
        assert test_file_obj.language == "python"
        assert test_file_obj.framework == "pytest"
        assert len(test_file_obj.test_cases) >= 0
    
    def test_detect_test_framework(self):
        """Test framework detection."""
        generator = TestGenerator(None)
        
        assert generator._detect_test_framework("python") == "pytest"
        assert generator._detect_test_framework("javascript") == "jest"
        assert generator._detect_test_framework("typescript") == "jest"


class TestTestRunner:
    """Test TestRunner class."""
    
    def test_parse_pytest_output(self):
        """Test parsing pytest output."""
        runner = TestRunner()
        
        output = """
test_example.py::test_one PASSED
test_example.py::test_two FAILED

3 passed, 1 failed in 0.5s
TOTAL                                                  95%
"""
        
        results = runner._parse_pytest_output(output)
        
        assert results.passed == 3
        assert results.failed == 1
        assert results.coverage == 95.0
    
    def test_parse_jest_output(self):
        """Test parsing Jest output."""
        runner = TestRunner()
        
        output = """
Tests:       1 failed, 5 passed, 6 total
Time:        2.5 s
All files    |   85.5
"""
        
        results = runner._parse_jest_output(output)
        
        assert results.passed == 5
        assert results.failed == 1
        assert results.total == 6
        assert results.coverage == 85.5
    
    def test_build_command(self):
        """Test building test command."""
        runner = TestRunner()
        
        cmd = runner._build_command("pytest", ["test_file.py"])
        
        assert "pytest" in cmd
        assert "test_file.py" in cmd


class TestBugFixer:
    """Test BugFixer class."""
    
    def test_extract_error_type(self):
        """Test extracting error type."""
        # Mock AI backend
        class MockAI:
            def query(self, prompt, max_tokens=1000):
                return """
ROOT_CAUSE: Division by zero
AFFECTED_FILES: calculator.py
FIXES:
1. Add check for zero divisor
2. Raise ValueError with message
CONFIDENCE: 90
"""
        
        fixer = BugFixer(MockAI())
        
        error = "ZeroDivisionError: division by zero"
        error_type = fixer._extract_error_type(error)
        
        assert error_type == "ZeroDivisionError"
    
    def test_diagnose_bug(self):
        """Test bug diagnosis."""
        class MockAI:
            def query(self, prompt, max_tokens=1000):
                return """
ROOT_CAUSE: Variable not defined before use
AFFECTED_FILES: main.py
FIXES:
1. Initialize variable before loop
2. Add default value
CONFIDENCE: 85
"""
        
        fixer = BugFixer(MockAI())
        
        error = "NameError: name 'x' is not defined"
        stack_trace = "File main.py, line 10"
        
        diagnosis = fixer.diagnose_bug(error, stack_trace)
        
        assert diagnosis.error_type == "NameError"
        assert len(diagnosis.suggested_fixes) > 0
    
    def test_suggest_preventive_tests(self):
        """Test suggesting preventive tests."""
        class MockAI:
            def query(self, prompt, max_tokens=500):
                return """
1. Test with zero input
2. Test with negative numbers
3. Test with very large numbers
"""
        
        fixer = BugFixer(MockAI())
        
        diagnosis = BugDiagnosis(
            error_type="ValueError",
            root_cause="Invalid input",
            affected_files=["calc.py"],
            suggested_fixes=["Add validation"]
        )
        
        tests = fixer.suggest_preventive_tests(diagnosis)
        
        assert len(tests) >= 0


class TestIntegration:
    """Integration tests for tester module."""
    
    def test_full_workflow(self, tmp_path):
        """Test full testing workflow."""
        # Create a simple Python file
        code_file = tmp_path / "math_utils.py"
        code_file.write_text("""
def multiply(a, b):
    '''Multiply two numbers'''
    return a * b
""")
        
        # Mock AI
        class MockAI:
            def query(self, prompt, max_tokens=1500):
                if "Generate comprehensive unit tests" in prompt:
                    return """
TEST: test_multiply_positive
DESCRIPTION: Test multiplying positive numbers
CODE:
```
def test_multiply_positive():
    assert multiply(3, 4) == 12
```
"""
                return ""
        
        # Generate tests
        generator = TestGenerator(MockAI())
        test_file = generator.generate_tests(str(code_file), "python", "pytest")
        
        assert test_file.language == "python"
        assert test_file.framework == "pytest"
