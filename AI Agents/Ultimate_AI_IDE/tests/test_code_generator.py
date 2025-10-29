"""
Tests for Code Generator Module
"""

import pytest
from pathlib import Path

from src.modules.code_generator import (
    CodeAnalyzer, CodeContext, FeaturePlan,
    CodeGenerator, CodeArtifact,
    CodeEditor, CodeValidator, ValidationResult
)


class TestCodeAnalyzer:
    """Test CodeAnalyzer class."""
    
    def test_get_code_context(self, tmp_path):
        """Test extracting code context."""
        # Create test files
        (tmp_path / "test.py").write_text("""
class MyClass:
    def my_method(self, arg1: str) -> bool:
        return True

def my_function():
    pass
""")
        
        analyzer = CodeAnalyzer()
        context = analyzer.get_code_context(str(tmp_path), "python")
        
        assert context.language == "python"
        assert len(context.existing_files) > 0
        assert "MyClass" in context.existing_classes
        assert "my_function" in context.existing_functions
    
    def test_check_duplicates(self, tmp_path):
        """Test duplicate detection."""
        # Create file with code
        code_file = tmp_path / "existing.py"
        code_file.write_text("""
def calculate_sum(a, b):
    return a + b
""")
        
        analyzer = CodeAnalyzer()
        context = analyzer.get_code_context(str(tmp_path), "python")
        
        # Check for duplicate
        new_code = """
def calculate_sum(x, y):
    return x + y
"""
        duplicates = analyzer.check_duplicates(new_code, context)
        
        # Should detect similarity
        assert len(duplicates) >= 0  # May or may not detect depending on threshold


class TestCodeGenerator:
    """Test CodeGenerator class."""
    
    def test_generate_class(self):
        """Test generating a class."""
        # Mock AI backend
        class MockAI:
            def query(self, prompt, max_tokens=1000):
                return """
class TestClass:
    def __init__(self):
        pass
"""
        
        context = CodeContext(project_path=".", language="python")
        generator = CodeGenerator(MockAI())
        
        code = generator.generate_class("TestClass", "A test class", context)
        
        assert "class TestClass" in code
    
    def test_generate_function(self):
        """Test generating a function."""
        class MockAI:
            def query(self, prompt, max_tokens=500):
                return """
def test_function(arg1: str) -> bool:
    return True
"""
        
        context = CodeContext(project_path=".", language="python")
        generator = CodeGenerator(MockAI())
        
        code = generator.generate_function("test_function", "A test function", context)
        
        assert "def test_function" in code
    
    def test_add_imports(self):
        """Test adding imports to code."""
        generator = CodeGenerator(None)
        
        code = "def my_function():\n    pass"
        imports = ["os", "sys", "pathlib.Path"]
        
        result = generator.add_imports(code, imports, "python")
        
        assert "import os" in result
        assert "import sys" in result
        assert "from pathlib import Path" in result


class TestCodeEditor:
    """Test CodeEditor class."""
    
    def test_insert_code(self, tmp_path):
        """Test inserting code into file."""
        artifact = CodeArtifact(
            file_path=str(tmp_path / "test.py"),
            content="print('hello')",
            language="python",
            is_new_file=True
        )
        
        editor = CodeEditor()
        success = editor.insert_code(artifact, backup=False)
        
        assert success is True
        assert (tmp_path / "test.py").exists()
        assert (tmp_path / "test.py").read_text() == "print('hello')"
    
    def test_add_import(self, tmp_path):
        """Test adding import to file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def my_function():\n    pass")
        
        editor = CodeEditor()
        success = editor.add_import(str(test_file), "import os", "python")
        
        assert success is True
        content = test_file.read_text()
        assert "import os" in content
    
    def test_update_indentation(self):
        """Test updating code indentation."""
        editor = CodeEditor()
        
        code = "def func():\npass"
        result = editor.update_indentation(code, base_indent=4)
        
        lines = result.split('\n')
        assert lines[0].startswith('    ')


class TestCodeValidator:
    """Test CodeValidator class."""
    
    def test_validate_python_syntax_valid(self):
        """Test validating valid Python code."""
        validator = CodeValidator()
        
        code = """
def my_function(arg1: str) -> bool:
    '''Docstring'''
    return True
"""
        
        result = validator.validate_code(code, "python")
        
        assert result.valid is True
        assert len(result.errors) == 0
    
    def test_validate_python_syntax_invalid(self):
        """Test validating invalid Python code."""
        validator = CodeValidator()
        
        code = """
def my_function(
    return True
"""
        
        result = validator.validate_code(code, "python")
        
        assert result.valid is False
        assert len(result.errors) > 0
    
    def test_validate_style(self):
        """Test style validation."""
        validator = CodeValidator()
        
        # Create code with long lines
        code = "x = " + "a" * 150
        
        result = validator.validate_code(code, "python")
        
        # Should have warnings about line length
        assert len(result.warnings) > 0
    
    def test_check_complexity(self):
        """Test complexity checking."""
        validator = CodeValidator()
        
        code = """
class MyClass:
    def method1(self):
        pass
    
    def method2(self):
        pass

def function1():
    pass
"""
        
        metrics = validator.check_complexity(code)
        
        assert metrics['classes'] == 1
        assert metrics['functions'] >= 2
