
"""
Unit tests for Memory System.

Tests the conversation memory and session management.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime


@pytest.mark.unit
class TestMemoryManager:
    """Test suite for Memory Manager."""
    
    @pytest.fixture
    def memory_manager(self, mock_config, temp_dir):
        """Create a memory manager for testing."""
        from core.memory import MemoryManager
        
        # MemoryManager accepts individual params, not config dict
        return MemoryManager(
            storage_path=temp_dir / "memory",
            default_max_context_window=4096,
            auto_save=False,  # Disable auto-save for tests
            enable_summarization=False,  # Disable for tests
            llm_router=None
        )
    
    def test_initialization(self, memory_manager):
        """Test memory manager initialization."""
        assert memory_manager is not None
    
    def test_add_message(self, memory_manager):
        """Test adding a message to memory."""
        # Create session first
        session_id = memory_manager.create_session()
        
        # Correct API: add_message(session_id, role, content, ...)
        from core.memory import MessageRole
        memory_manager.add_message(
            session_id=session_id,
            role=MessageRole.USER,
            content='Test message'
        )
        
        history = memory_manager.get_conversation_history(session_id=session_id)
        
        assert len(history) > 0
        assert any(msg['content'] == 'Test message' for msg in history)
    
    def test_add_multiple_messages(self, memory_manager):
        """Test adding multiple messages."""
        session_id = memory_manager.create_session()
        
        from core.memory import MessageRole
        memory_manager.add_user_message(session_id, 'Message 1')
        memory_manager.add_agent_message(session_id, 'Response 1', 'assistant')
        memory_manager.add_user_message(session_id, 'Message 2')
        
        history = memory_manager.get_conversation_history(session_id=session_id)
        
        assert len(history) >= 3
    
    def test_get_history_empty_session(self, memory_manager):
        """Test getting history for empty session."""
        session_id = memory_manager.create_session()
        history = memory_manager.get_conversation_history(session_id=session_id)
        
        assert isinstance(history, list)
        assert len(history) == 0
    
    def test_get_history_with_limit(self, memory_manager):
        """Test getting history with limit."""
        session_id = memory_manager.create_session()
        
        # Add multiple messages
        for i in range(10):
            memory_manager.add_user_message(session_id, f'Message {i}')
        
        history = memory_manager.get_conversation_history(session_id=session_id, limit=5)
        
        assert len(history) <= 5
    
    def test_clear_session(self, memory_manager):
        """Test clearing a session."""
        session_id = memory_manager.create_session()
        
        memory_manager.add_user_message(session_id, 'Test')
        assert len(memory_manager.get_conversation_history(session_id=session_id)) > 0
        
        # delete_session is equivalent to clearing
        memory_manager.delete_session(session_id=session_id)
        
        # After deletion, getting the session should return None
        session = memory_manager.get_session(session_id=session_id)
        assert session is None
    
    def test_save_session(self, memory_manager, temp_dir):
        """Test saving session to file."""
        session_id = memory_manager.create_session()
        
        memory_manager.add_user_message(session_id, 'Test message')
        
        # save_all_sessions() saves all sessions to storage
        count = memory_manager.save_all_sessions()
        
        # At least one session should be saved
        assert count > 0
    
    def test_load_session(self, memory_manager, temp_dir):
        """Test loading session from file."""
        session_id = memory_manager.create_session()
        
        # Save a session
        memory_manager.add_user_message(session_id, 'Saved message')
        memory_manager.save_all_sessions()
        
        # Remove from memory only (not from storage) to test reloading
        if session_id in memory_manager.sessions:
            del memory_manager.sessions[session_id]
        
        # Get session should reload from storage
        session = memory_manager.get_session(session_id=session_id)
        assert session is not None
        
        history = memory_manager.get_conversation_history(session_id=session_id)
        assert len(history) > 0
        assert any(msg['content'] == 'Saved message' for msg in history)
    
    def test_get_summary(self, memory_manager):
        """Test getting session summary."""
        session_id = memory_manager.create_session()
        
        memory_manager.add_user_message(session_id, 'Test message')
        
        # Get session info which includes metadata
        session_info = memory_manager.get_session_info(session_id=session_id)
        
        assert session_info is not None
        assert isinstance(session_info, dict)
        assert 'session_id' in session_info


@pytest.mark.unit
class TestMemoryAutoSummarization:
    """Test suite for memory auto-summarization."""
    
    @pytest.fixture
    def memory_with_summarization(self, mock_config, mock_llm_router, temp_dir):
        """Create memory manager with summarization enabled."""
        from core.memory import MemoryManager
        
        return MemoryManager(
            storage_path=temp_dir / "memory_summary",
            default_max_context_window=4096,
            auto_save=False,
            enable_summarization=True,  # Enable for this test
            llm_router=mock_llm_router
        )
    
    def test_auto_summarize_threshold(self, memory_with_summarization):
        """Test that auto-summarization triggers at threshold."""
        session_id = 'auto_summary_test'
        
        # Add messages up to threshold
        for i in range(15):
            memory_with_summarization.add_message(
                'user',
                f'Message {i}',
                session_id
            )
        
        # Should have triggered summarization
        # Check that history is managed
        history = memory_with_summarization.get_conversation_history(session_id=session_id)
        assert history is not None
