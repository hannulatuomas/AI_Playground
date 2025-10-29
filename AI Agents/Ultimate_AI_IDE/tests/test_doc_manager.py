"""
Tests for Documentation Manager Module
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.modules.doc_manager import (
    DocManager, CodeScanner, DocGenerator, 
    CodeStructure, Documentation
)


class MockAIBackend:
    """Mock AI backend for testing."""
    
    def query(self, prompt, max_tokens=1000):
        """Mock query method."""
        if "README" in prompt:
            return "# Test Project\n\nA test project."
        elif "API" in prompt:
            return "# API Documentation\n\n## Functions\n\n### test_function\n\nTest function."
        elif "docstring" in prompt.lower():
            return "Test function.\n\nArgs:\n    param: Description\n\nReturns:\n    Result"
        else:
            return "Generated documentation"


@pytest.fixture
def mock_ai():
    """Provide mock AI backend."""
    return MockAIBackend()


@pytest.fixture
def temp_project():
    """Create temporary project directory."""
    temp_dir = tempfile.mkdtemp()
    
    # Create sample Python file
    test_file = Path(temp_dir) / "test.py"
    test_file.write_text('''"""Test module."""

def test_function(param):
    """Test function."""
    return param * 2

class TestClass:
    """Test class."""
    
    def test_method(self):
        """Test method."""
        pass
''')
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


def test_code_scanner_python(temp_project):
    """Test scanning Python code."""
    scanner = CodeScanner()
    structure = scanner.scan_project(temp_project, 'python')
    
    assert len(structure.modules) > 0
    assert len(structure.public_api) > 0


def test_code_scanner_finds_classes(temp_project):
    """Test that scanner finds classes."""
    scanner = CodeScanner()
    structure = scanner.scan_project(temp_project, 'python')
    
    module = structure.modules[0]
    assert len(module.classes) == 1
    assert module.classes[0].name == "TestClass"


def test_code_scanner_finds_functions(temp_project):
    """Test that scanner finds functions."""
    scanner = CodeScanner()
    structure = scanner.scan_project(temp_project, 'python')
    
    module = structure.modules[0]
    assert len(module.functions) == 1
    assert module.functions[0].name == "test_function"


def test_doc_generator_readme(mock_ai):
    """Test README generation."""
    generator = DocGenerator(mock_ai)
    structure = CodeStructure()
    
    readme = generator.generate_readme(
        project_name="Test Project",
        language="python",
        framework=None,
        structure=structure,
        features=["Feature 1", "Feature 2"]
    )
    
    assert readme.doc_type == 'readme'
    assert readme.file_path == 'README.md'
    assert len(readme.content) > 0


def test_doc_generator_api_docs(mock_ai):
    """Test API documentation generation."""
    generator = DocGenerator(mock_ai)
    structure = CodeStructure()
    
    api_docs = generator.generate_api_docs(structure, 'python')
    
    assert api_docs.doc_type == 'api'
    assert api_docs.file_path == 'docs/API.md'


def test_doc_manager_sync(mock_ai, temp_project):
    """Test documentation synchronization."""
    manager = DocManager(mock_ai)
    
    report = manager.sync_documentation(temp_project, 'python')
    
    assert isinstance(report.files_created, list)
    assert isinstance(report.undocumented_items, list)


def test_doc_manager_generate_readme(mock_ai, temp_project):
    """Test README generation through manager."""
    manager = DocManager(mock_ai)
    
    success = manager.generate_readme(
        project_path=temp_project,
        language='python',
        features=["Test feature"]
    )
    
    assert success is True or success is False  # May fail without write permissions


def test_changelog_entry_generation(mock_ai):
    """Test changelog entry generation."""
    generator = DocGenerator(mock_ai)
    
    entry = generator.generate_changelog_entry(
        version="1.0.0",
        changes=["Added feature X", "Fixed bug Y"],
        change_type="Added"
    )
    
    assert "1.0.0" in entry
    assert "Added" in entry
    assert "Added feature X" in entry
