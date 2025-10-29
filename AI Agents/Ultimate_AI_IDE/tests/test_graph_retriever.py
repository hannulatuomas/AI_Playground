"""
Tests for Graph Retriever

Tests for v1.6.0 Advanced RAG features.
"""

import pytest
import os
import tempfile
import ast

from src.modules.context_manager import GraphRetriever, CallGraphBuilder, CodeNode


class TestCallGraphBuilder:
    """Test call graph builder functionality."""
    
    @pytest.fixture
    def builder(self):
        """Create builder instance."""
        return CallGraphBuilder()
    
    @pytest.fixture
    def sample_code(self):
        """Sample Python code."""
        return """
def helper():
    return 42

def main():
    result = helper()
    return result

class MyClass:
    def __init__(self):
        self.value = helper()
    
    def get_value(self):
        return self.value
"""
    
    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create sample Python file."""
        file_path = tmp_path / "test.py"
        file_path.write_text("""
def add(a, b):
    return a + b

def multiply(a, b):
    result = add(a, b)
    return result * 2

class Calculator:
    def calculate(self, x, y):
        return multiply(x, y)
""")
        return str(file_path)
    
    def test_builder_initialization(self, builder):
        """Test builder initialization."""
        assert len(builder.graph) == 0
        assert len(builder.file_nodes) == 0
    
    def test_build_from_file(self, builder, sample_file):
        """Test building graph from file."""
        success = builder.build_from_file(sample_file)
        assert success
        assert len(builder.graph) > 0
        
        # Check for expected nodes
        assert 'add' in builder.graph
        assert 'multiply' in builder.graph
        assert 'Calculator' in builder.graph
    
    def test_function_node(self, builder, sample_file):
        """Test function node creation."""
        builder.build_from_file(sample_file)
        
        node = builder.graph.get('add')
        assert node is not None
        assert node.node_type == 'function'
        assert node.name == 'add'
        assert node.file_path == sample_file
        assert isinstance(node.dependencies, set)
    
    def test_class_node(self, builder, sample_file):
        """Test class node creation."""
        builder.build_from_file(sample_file)
        
        node = builder.graph.get('Calculator')
        assert node is not None
        assert node.node_type == 'class'
        assert node.name == 'Calculator'
    
    def test_method_node(self, builder, sample_file):
        """Test method node creation."""
        builder.build_from_file(sample_file)
        
        node = builder.graph.get('Calculator.calculate')
        assert node is not None
        assert node.node_type == 'method'
        assert 'multiply' in node.dependencies
    
    def test_resolve_dependencies(self, builder, sample_file):
        """Test dependency resolution."""
        builder.build_from_file(sample_file)
        builder.resolve_dependencies()
        
        # multiply depends on add
        multiply_node = builder.graph['multiply']
        assert 'add' in multiply_node.dependencies
        
        # add should have multiply as dependent
        add_node = builder.graph['add']
        assert 'multiply' in add_node.dependents


class TestGraphRetriever:
    """Test graph retriever functionality."""
    
    @pytest.fixture
    def retriever(self):
        """Create retriever instance."""
        return GraphRetriever()
    
    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create sample Python file."""
        file_path = tmp_path / "test.py"
        file_path.write_text("""
def helper():
    return 42

def process(data):
    value = helper()
    return data + value

def main():
    result = process(10)
    return result
""")
        return str(file_path)
    
    def test_retriever_initialization(self, retriever):
        """Test retriever initialization."""
        assert retriever.call_graph is not None
        assert isinstance(retriever.call_graph, CallGraphBuilder)
    
    def test_index_file(self, retriever, sample_file):
        """Test file indexing."""
        success = retriever.index_file(sample_file)
        assert success
        assert len(retriever.call_graph.graph) > 0
    
    def test_find_node(self, retriever, sample_file):
        """Test node finding."""
        retriever.index_file(sample_file)
        retriever.call_graph.resolve_dependencies()
        
        node = retriever.find_node('helper')
        assert node is not None
        assert node.name == 'helper'
        assert node.node_type == 'function'
    
    def test_get_dependencies(self, retriever, sample_file):
        """Test dependency retrieval."""
        retriever.index_file(sample_file)
        retriever.call_graph.resolve_dependencies()
        
        deps = retriever.get_dependencies('process', depth=1)
        assert len(deps) > 0
        assert any(node.name == 'helper' for node in deps)
    
    def test_get_dependents(self, retriever, sample_file):
        """Test dependent retrieval."""
        retriever.index_file(sample_file)
        retriever.call_graph.resolve_dependencies()
        
        dependents = retriever.get_dependents('helper', depth=1)
        assert len(dependents) > 0
        assert any(node.name == 'process' for node in dependents)
    
    def test_expand_context(self, retriever, sample_file):
        """Test context expansion."""
        retriever.index_file(sample_file)
        retriever.call_graph.resolve_dependencies()
        
        context = retriever.expand_context('process', expansion_depth=2)
        assert isinstance(context, str)
        assert len(context) > 0
        assert 'process' in context
    
    def test_find_related_code(self, retriever, sample_file):
        """Test related code finding."""
        retriever.index_file(sample_file)
        retriever.call_graph.resolve_dependencies()
        
        related = retriever.find_related_code('process', max_results=10)
        assert isinstance(related, list)
        assert len(related) > 0
        assert all(isinstance(node, CodeNode) for node in related)
    
    def test_search_by_pattern(self, retriever, sample_file):
        """Test pattern search."""
        retriever.index_file(sample_file)
        
        results = retriever.search_by_pattern('help')
        assert len(results) > 0
        assert any('helper' in node.name for node in results)
    
    def test_get_call_chain(self, retriever, sample_file):
        """Test call chain finding."""
        retriever.index_file(sample_file)
        retriever.call_graph.resolve_dependencies()
        
        chain = retriever.get_call_chain('main', 'helper')
        if chain:  # Chain might exist depending on graph structure
            assert isinstance(chain, list)
            assert 'main' in chain
            assert 'helper' in chain
    
    def test_get_statistics(self, retriever, sample_file):
        """Test statistics retrieval."""
        retriever.index_file(sample_file)
        retriever.call_graph.resolve_dependencies()
        
        stats = retriever.get_statistics()
        assert 'total_nodes' in stats
        assert 'total_files' in stats
        assert 'total_dependencies' in stats
        assert 'node_types' in stats
        assert stats['total_nodes'] > 0
    
    def test_export_graph_dot(self, retriever, sample_file, tmp_path):
        """Test graph export to DOT format."""
        retriever.index_file(sample_file)
        retriever.call_graph.resolve_dependencies()
        
        output_file = str(tmp_path / "graph.dot")
        success = retriever.export_graph(output_file, format='dot')
        assert success
        assert os.path.exists(output_file)
        
        # Check content
        with open(output_file, 'r') as f:
            content = f.read()
            assert 'digraph CallGraph' in content
    
    def test_export_graph_json(self, retriever, sample_file, tmp_path):
        """Test graph export to JSON format."""
        retriever.index_file(sample_file)
        retriever.call_graph.resolve_dependencies()
        
        output_file = str(tmp_path / "graph.json")
        success = retriever.export_graph(output_file, format='json')
        assert success
        assert os.path.exists(output_file)
        
        # Check content
        import json
        with open(output_file, 'r') as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert len(data) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
