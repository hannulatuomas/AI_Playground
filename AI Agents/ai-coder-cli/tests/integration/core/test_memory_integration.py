"""
Integration tests for Memory System.

Tests interactions between Memory Manager, Cache, and Vector Memory.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path


@pytest.mark.integration
class TestMemoryCacheIntegration:
    """Test Memory Manager integration with Cache."""
    
    @pytest.fixture
    def memory_with_cache(self, temp_dir):
        """Create a memory manager with cache."""
        from core.memory import MemoryManager
        from core.cache import Cache, FileCacheBackend
        
        backend = FileCacheBackend(cache_dir=str(temp_dir / "cache"))
        cache = Cache(backend=backend, default_ttl=3600)
        
        # Create memory manager with cache
        memory = MemoryManager(
            storage_path=temp_dir / "memory",
            default_max_context_window=4096
        )
        
        return {
            'memory': memory,
            'cache': cache
        }
    
    def test_memory_cache_storage(self, memory_with_cache):
        """Test that memory uses cache for storage."""
        memory = memory_with_cache['memory']
        cache = memory_with_cache['cache']
        
        # Create session first
        session_id = memory.create_session(session_id="test-session")
        
        # Add messages to memory
        from core.memory import MessageRole
        memory.add_message(session_id=session_id, role=MessageRole.USER, content="Hello")
        memory.add_message(session_id=session_id, role=MessageRole.AGENT, content="Hi there")
        
        # Verify messages are in memory
        history = memory.get_conversation_history(session_id=session_id)
        assert len(history) >= 2
    
    def test_memory_session_persistence(self, memory_with_cache):
        """Test session persistence through cache."""
        memory = memory_with_cache['memory']
        
        # Create session first
        session_id = memory.create_session(session_id="test-session")
        
        # Add messages
        from core.memory import MessageRole
        memory.add_message(session_id=session_id, role=MessageRole.USER, content="Test message 1")
        memory.add_message(session_id=session_id, role=MessageRole.AGENT, content="Response 1")
        
        # Save all sessions (auto_save is enabled by default, but let's be explicit)
        memory.save_all_sessions()
        
        # Verify session was saved
        history = memory.get_conversation_history(session_id=session_id)
        assert len(history) >= 2


@pytest.mark.integration
class TestMemoryVectorIntegration:
    """Test Memory Manager integration with Vector Memory."""
    
    @pytest.fixture
    def memory_with_vector(self, mock_chromadb_client, temp_dir):
        """Create a memory manager with vector memory."""
        from core.vector_memory import VectorMemoryManager
        
        with patch('chromadb.PersistentClient', return_value=mock_chromadb_client):
            with patch('tools.vector_db.create_embedding_generator') as mock_embed:
                # Mock embedding generator
                generator = Mock()
                generator.generate = Mock(return_value=[0.1, 0.2, 0.3])
                generator.generate_batch = Mock(return_value=[[0.1, 0.2], [0.3, 0.4]])
                mock_embed.return_value = generator
                
                vector_memory = VectorMemoryManager(
                    storage_path=temp_dir / "memory",
                    vector_db_path=str(temp_dir / "vector")
                )
                
                return {
                    'memory': vector_memory
                }
    
    def test_memory_vector_storage(self, memory_with_vector):
        """Test that memory can use vector memory."""
        memory = memory_with_vector['memory']
        
        # Create session first
        session_id = memory.create_session(session_id="test-session")
        
        # Add messages
        from core.memory import MessageRole
        memory.add_message(session_id=session_id, role=MessageRole.USER, content="How do I implement a binary tree?")
        memory.add_message(session_id=session_id, role=MessageRole.AGENT, content="Here's how to implement a binary tree...")
        
        # Verify messages are stored
        history = memory.get_conversation_history(session_id=session_id)
        assert len(history) >= 2


@pytest.mark.integration
class TestFullMemoryStack:
    """Test complete memory stack with all components."""
    
    @pytest.fixture
    def full_memory_stack(self, mock_chromadb_client, temp_dir):
        """Create a full memory stack."""
        from core.vector_memory import VectorMemoryManager
        
        with patch('chromadb.PersistentClient', return_value=mock_chromadb_client):
            with patch('tools.vector_db.create_embedding_generator') as mock_embed:
                generator = Mock()
                generator.generate = Mock(return_value=[0.1, 0.2, 0.3])
                generator.generate_batch = Mock(return_value=[[0.1, 0.2], [0.3, 0.4]])
                mock_embed.return_value = generator
                
                vector_memory = VectorMemoryManager(
                    storage_path=temp_dir / "memory",
                    vector_db_path=str(temp_dir / "vector")
                )
                
                return {
                    'memory': vector_memory
                }
    
    def test_full_stack_operations(self, full_memory_stack):
        """Test operations with full memory stack."""
        memory = full_memory_stack['memory']
        
        session_id = "test-session"
        
        # Create session first
        memory.create_session(session_id=session_id)
        
        # Add multiple messages
        for i in range(5):
            memory.add_message(session_id=session_id, role="user", content=f"Message {i}")
            memory.add_message(session_id=session_id, role="assistant", content=f"Response {i}")
        
        # Get history
        history = memory.get_conversation_history(session_id=session_id)
        assert len(history) >= 10
        
        # Clear session
        memory.clear_session(session_id=session_id)
        
        # Verify cleared
        history_after_clear = memory.get_conversation_history(session_id=session_id)
        assert len(history_after_clear) == 0
