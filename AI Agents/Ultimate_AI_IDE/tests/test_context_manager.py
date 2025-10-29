"""
Tests for Context Manager Module
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.modules.context_manager import (
    ContextManager, CodeSummarizer, CodeEmbedder,
    ContextRetriever, WindowManager, Message
)


class MockAIBackend:
    """Mock AI backend for testing."""
    
    def query(self, prompt, max_tokens=1000):
        """Mock query method."""
        if "summarize" in prompt.lower():
            return "This is a test module for testing purposes."
        return "AI response"


@pytest.fixture
def mock_ai():
    """Provide mock AI backend."""
    return MockAIBackend()


@pytest.fixture
def temp_project():
    """Create temporary project with code files."""
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
    shutil.rmtree(temp_dir)


def test_code_summarizer(mock_ai, temp_project):
    """Test code summarizer."""
    summarizer = CodeSummarizer(mock_ai)
    
    test_file = Path(temp_project) / "test.py"
    summary = summarizer.summarize_file(str(test_file), 'python')
    
    assert summary.language == 'python'
    assert len(summary.functions) > 0
    assert len(summary.classes) > 0


def test_code_embedder():
    """Test code embedder."""
    embedder = CodeEmbedder()
    
    text = "def test_function(): pass"
    embedding = embedder.generate_embedding(text)
    
    assert len(embedding) == 384
    assert all(isinstance(x, float) for x in embedding)


def test_embedding_similarity():
    """Test cosine similarity calculation."""
    embedder = CodeEmbedder()
    
    vec1 = embedder.generate_embedding("test function")
    vec2 = embedder.generate_embedding("test function")
    vec3 = embedder.generate_embedding("completely different")
    
    sim_same = embedder.cosine_similarity(vec1, vec2)
    sim_diff = embedder.cosine_similarity(vec1, vec3)
    
    assert sim_same > sim_diff


def test_window_manager():
    """Test window manager."""
    manager = WindowManager(max_tokens=1000)
    
    manager.add_message('user', 'Hello')
    manager.add_message('assistant', 'Hi there!')
    
    assert len(manager.messages) == 2
    assert manager.get_token_count() > 0


def test_window_trimming():
    """Test window trimming."""
    manager = WindowManager(max_tokens=100)
    
    # Add many messages to exceed limit
    for i in range(20):
        manager.add_message('user', f'Message {i}' * 10)
    
    # Should be trimmed
    assert manager.get_token_count() <= 100


def test_context_manager_initialization(mock_ai):
    """Test context manager initialization."""
    manager = ContextManager(mock_ai)
    
    assert manager.ai_backend == mock_ai
    assert manager.summarizer is not None
    assert manager.retriever is not None


def test_context_manager_conversation(mock_ai):
    """Test conversation management."""
    manager = ContextManager(mock_ai)
    
    manager.add_to_conversation('user', 'Test message')
    history = manager.get_conversation_history()
    
    assert 'Test message' in history


def test_context_manager_stats(mock_ai):
    """Test getting statistics."""
    manager = ContextManager(mock_ai)
    
    stats = manager.get_stats()
    
    assert 'indexed_projects' in stats
    assert 'conversation_tokens' in stats
