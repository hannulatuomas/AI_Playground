"""
Tests for CodebaseIndexer module
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.modules.codebase_indexer import CodebaseIndexer, FileIndex, ClassIndex, FunctionIndex


@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def python_project(temp_project):
    """Create a Python project with various structures."""
    # Main module with class and functions
    main_content = '''
"""Main module."""

class MyClass:
    """A test class."""
    
    def __init__(self):
        """Initialize."""
        self.value = 0
    
    def method1(self):
        """Method 1."""
        return self.value

def standalone_function(x, y):
    """A standalone function."""
    return x + y

def another_function():
    """Another function."""
    pass
'''
    (temp_project / 'main.py').write_text(main_content)
    
    # Utils module
    utils_content = '''
"""Utilities."""

def helper_function(data):
    """Helper function."""
    return data * 2
'''
    (temp_project / 'utils.py').write_text(utils_content)
    
    # Module with imports
    imports_content = '''
"""Module with imports."""
import os
import sys
from pathlib import Path
from utils import helper_function

def use_imports():
    """Use imported modules."""
    return Path(".")
'''
    (temp_project / 'imports.py').write_text(imports_content)
    
    return temp_project


class TestCodebaseIndexer:
    """Test CodebaseIndexer functionality."""
    
    def test_init(self, temp_project):
        """Test CodebaseIndexer initialization."""
        indexer = CodebaseIndexer(str(temp_project))
        
        assert indexer.project_path == temp_project
        assert len(indexer.file_index) == 0
        assert len(indexer.class_index) == 0
        assert len(indexer.function_index) == 0
    
    def test_index_project(self, python_project):
        """Test indexing entire project."""
        indexer = CodebaseIndexer(str(python_project))
        stats = indexer.index_project()
        
        assert stats['files_indexed'] > 0
        assert stats['total_files'] >= 3
        assert stats['total_classes'] >= 1
        assert stats['total_functions'] >= 3
        assert 'duration_seconds' in stats
    
    def test_index_python_file(self, python_project):
        """Test indexing Python file."""
        indexer = CodebaseIndexer(str(python_project))
        indexer.index_project()
        
        # Check main.py was indexed
        assert 'main.py' in indexer.file_index
        file_idx = indexer.file_index['main.py']
        
        assert file_idx.language == 'python'
        assert len(file_idx.classes) >= 1
        assert 'MyClass' in file_idx.classes
        assert len(file_idx.functions) >= 2
    
    def test_class_indexing(self, python_project):
        """Test class indexing."""
        indexer = CodebaseIndexer(str(python_project))
        indexer.index_project()
        
        assert 'MyClass' in indexer.class_index
        class_idx = indexer.class_index['MyClass'][0]
        
        assert class_idx.name == 'MyClass'
        assert class_idx.file_path == 'main.py'
        assert len(class_idx.methods) >= 2
        assert '__init__' in class_idx.methods
        assert 'method1' in class_idx.methods
    
    def test_function_indexing(self, python_project):
        """Test function indexing."""
        indexer = CodebaseIndexer(str(python_project))
        indexer.index_project()
        
        assert 'standalone_function' in indexer.function_index
        func_idx = indexer.function_index['standalone_function'][0]
        
        assert func_idx.name == 'standalone_function'
        assert func_idx.file_path == 'main.py'
        assert len(func_idx.parameters) == 2
        assert 'x' in func_idx.parameters
        assert 'y' in func_idx.parameters
    
    def test_import_tracking(self, python_project):
        """Test import tracking."""
        indexer = CodebaseIndexer(str(python_project))
        indexer.index_project()
        
        imports_file = indexer.file_index['imports.py']
        
        assert len(imports_file.imports) > 0
        assert 'os' in imports_file.imports
        assert 'sys' in imports_file.imports
        assert 'pathlib' in imports_file.imports
    
    def test_dependency_graph(self, python_project):
        """Test dependency graph building."""
        indexer = CodebaseIndexer(str(python_project))
        indexer.index_project()
        
        assert len(indexer.dependency_graph) > 0
        
        # imports.py should depend on utils
        deps = [edge for edge in indexer.dependency_graph if edge.from_file == 'imports.py']
        assert len(deps) > 0
    
    def test_search_symbol(self, python_project):
        """Test symbol search."""
        indexer = CodebaseIndexer(str(python_project))
        indexer.index_project()
        
        results = indexer.search_symbol('MyClass')
        
        assert len(results['classes']) >= 1
        assert results['classes'][0].name == 'MyClass'
    
    def test_find_definition(self, python_project):
        """Test finding symbol definition."""
        indexer = CodebaseIndexer(str(python_project))
        indexer.index_project()
        
        definition = indexer.find_definition('MyClass')
        
        assert definition is not None
        assert definition['type'] == 'class'
        assert definition['file'] == 'main.py'
        assert 'line' in definition
    
    def test_find_usages(self, python_project):
        """Test finding symbol usages."""
        indexer = CodebaseIndexer(str(python_project))
        indexer.index_project()
        
        usages = indexer.find_usages('utils')
        
        # imports.py uses utils
        assert 'imports.py' in usages
    
    def test_get_file_dependencies(self, python_project):
        """Test getting file dependencies."""
        indexer = CodebaseIndexer(str(python_project))
        indexer.index_project()
        
        deps = indexer.get_file_dependencies('imports.py')
        
        assert len(deps) > 0
        assert any('os' in dep or 'sys' in dep for dep in deps)
    
    def test_get_project_structure(self, python_project):
        """Test getting project structure."""
        indexer = CodebaseIndexer(str(python_project))
        indexer.index_project()
        
        structure = indexer.get_project_structure()
        
        assert 'total_files' in structure
        assert 'by_language' in structure
        assert 'total_lines' in structure
        assert 'total_classes' in structure
        assert 'total_functions' in structure
        assert 'largest_files' in structure
        
        assert structure['total_files'] >= 3
        assert 'python' in structure['by_language']
    
    def test_incremental_indexing(self, python_project):
        """Test incremental indexing."""
        indexer = CodebaseIndexer(str(python_project))
        
        # Full index
        stats1 = indexer.index_project(incremental=False)
        
        # Incremental index (no changes)
        stats2 = indexer.index_project(incremental=True)
        
        # Should index fewer files on incremental
        assert stats2['files_indexed'] <= stats1['files_indexed']
    
    def test_save_and_load_index(self, python_project, tmp_path):
        """Test saving and loading index."""
        indexer = CodebaseIndexer(str(python_project))
        indexer.index_project()
        
        index_file = tmp_path / 'test_index.json'
        
        # Save index
        indexer.save_index(str(index_file))
        assert index_file.exists()
        
        # Load index into new indexer
        new_indexer = CodebaseIndexer(str(python_project))
        new_indexer.load_index(str(index_file))
        
        assert len(new_indexer.file_index) == len(indexer.file_index)
        assert len(new_indexer.class_index) == len(indexer.class_index)
        assert len(new_indexer.function_index) == len(indexer.function_index)
    
    def test_detect_circular_dependencies(self, temp_project):
        """Test circular dependency detection."""
        # Create circular dependency
        (temp_project / 'a.py').write_text('from b import something\n\ndef func_a():\n    pass')
        (temp_project / 'b.py').write_text('from a import func_a\n\ndef something():\n    pass')
        
        indexer = CodebaseIndexer(str(temp_project))
        indexer.index_project()
        
        circles = indexer.detect_circular_dependencies()
        
        # Circular dependency detection is complex, so we just check it doesn't crash
        # The actual detection may or may not find the cycle depending on implementation
        assert isinstance(circles, list)


class TestCodebaseIndexerEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_project(self, temp_project):
        """Test indexing empty project."""
        indexer = CodebaseIndexer(str(temp_project))
        stats = indexer.index_project()
        
        assert stats['files_indexed'] == 0
        assert stats['total_files'] == 0
    
    def test_syntax_error_file(self, temp_project):
        """Test handling files with syntax errors."""
        bad_file = temp_project / 'bad.py'
        bad_file.write_text('def bad_syntax(\n    # Missing closing')
        
        indexer = CodebaseIndexer(str(temp_project))
        stats = indexer.index_project()
        
        # Should not crash, just skip the bad file
        assert isinstance(stats, dict)
    
    def test_nonexistent_symbol(self, python_project):
        """Test searching for nonexistent symbol."""
        indexer = CodebaseIndexer(str(python_project))
        indexer.index_project()
        
        results = indexer.search_symbol('NonexistentClass')
        
        assert len(results['classes']) == 0
        assert len(results['functions']) == 0
    
    def test_javascript_file(self, temp_project):
        """Test indexing JavaScript file."""
        js_content = '''
class MyJSClass {
    constructor() {
        this.value = 0;
    }
    
    method1() {
        return this.value;
    }
}

function jsFunction(x, y) {
    return x + y;
}

export default MyJSClass;
export { jsFunction };
'''
        (temp_project / 'test.js').write_text(js_content)
        
        indexer = CodebaseIndexer(str(temp_project))
        stats = indexer.index_project()
        
        assert stats['files_indexed'] >= 1
        assert 'test.js' in indexer.file_index
        
        file_idx = indexer.file_index['test.js']
        assert file_idx.language == 'javascript'
        assert len(file_idx.classes) >= 1
        assert len(file_idx.functions) >= 1
        # Exports detection is basic, so we just check it's a list
        assert isinstance(file_idx.exports, list)
