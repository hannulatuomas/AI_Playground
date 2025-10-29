
"""
Unit tests for ChatHistoryManager.

Tests the chat history management system including message handling,
summarization, and persistence.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock

from core.chat_history import (
    ChatHistoryManager,
    ChatHistory,
    ChatMessage,
    ChatSummary,
    SummarizationStrategy
)


class TestChatMessage:
    """Tests for the ChatMessage dataclass."""
    
    def test_message_creation(self):
        """Test creating a chat message."""
        message = ChatMessage(role="user", content="Hello!")
        
        assert message.role == "user"
        assert message.content == "Hello!"
        assert isinstance(message.timestamp, datetime)
        assert message.metadata == {}
        assert message.tokens is None
    
    def test_message_to_dict(self):
        """Test converting message to dictionary."""
        message = ChatMessage(
            role="assistant",
            content="Hi there!",
            metadata={"key": "value"}
        )
        
        data = message.to_dict()
        
        assert isinstance(data, dict)
        assert data['role'] == "assistant"
        assert data['content'] == "Hi there!"
        assert 'timestamp' in data
        assert data['metadata'] == {"key": "value"}
    
    def test_message_from_dict(self):
        """Test creating message from dictionary."""
        data = {
            'role': 'user',
            'content': 'Test message',
            'timestamp': datetime.now().isoformat(),
            'metadata': {'source': 'test'},
            'tokens': 10
        }
        
        message = ChatMessage.from_dict(data)
        
        assert message.role == 'user'
        assert message.content == 'Test message'
        assert message.metadata == {'source': 'test'}
        assert message.tokens == 10


class TestChatSummary:
    """Tests for the ChatSummary dataclass."""
    
    def test_summary_creation(self):
        """Test creating a chat summary."""
        summary = ChatSummary(
            summary_text="This is a summary",
            original_message_count=10,
            original_token_count=500
        )
        
        assert summary.summary_text == "This is a summary"
        assert summary.original_message_count == 10
        assert summary.original_token_count == 500
        assert isinstance(summary.created_at, datetime)
        assert summary.strategy_used == "manual"
    
    def test_summary_to_dict(self):
        """Test converting summary to dictionary."""
        summary = ChatSummary(
            summary_text="Summary text",
            original_message_count=5,
            original_token_count=250
        )
        
        data = summary.to_dict()
        
        assert isinstance(data, dict)
        assert data['summary_text'] == "Summary text"
        assert data['original_message_count'] == 5
        assert data['original_token_count'] == 250
        assert 'created_at' in data


class TestChatHistory:
    """Tests for the ChatHistory dataclass."""
    
    def test_history_creation(self):
        """Test creating a chat history."""
        history = ChatHistory(
            history_id="test-hist-123",
            project_id="test-proj-456"
        )
        
        assert history.history_id == "test-hist-123"
        assert history.project_id == "test-proj-456"
        assert history.messages == []
        assert history.summaries == []
        assert isinstance(history.created_at, datetime)
    
    def test_add_message(self):
        """Test adding a message to history."""
        history = ChatHistory(
            history_id="test-id",
            project_id="proj-id"
        )
        
        message = ChatMessage(role="user", content="Hello")
        history.add_message(message)
        
        assert len(history.messages) == 1
        assert history.messages[0] == message
    
    def test_add_summary(self):
        """Test adding a summary to history."""
        history = ChatHistory(
            history_id="test-id",
            project_id="proj-id"
        )
        
        summary = ChatSummary(
            summary_text="Summary",
            original_message_count=5,
            original_token_count=200
        )
        history.add_summary(summary)
        
        assert len(history.summaries) == 1
        assert history.summaries[0] == summary
    
    def test_get_total_tokens(self):
        """Test calculating total tokens."""
        history = ChatHistory(
            history_id="test-id",
            project_id="proj-id"
        )
        
        msg1 = ChatMessage(role="user", content="Hello", tokens=5)
        msg2 = ChatMessage(role="assistant", content="Hi there", tokens=10)
        
        history.add_message(msg1)
        history.add_message(msg2)
        
        assert history.get_total_tokens() == 15


class TestChatHistoryManager:
    """Tests for the ChatHistoryManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        # Cleanup
        if temp_path.exists():
            shutil.rmtree(temp_path)
    
    @pytest.fixture
    def mock_llm_router(self):
        """Create a mock LLM router."""
        mock = Mock()
        mock.query = Mock(return_value={'response': 'This is a test summary.'})
        return mock
    
    @pytest.fixture
    def manager(self, temp_dir, mock_llm_router):
        """Create a ChatHistoryManager instance for testing."""
        return ChatHistoryManager(
            storage_path=temp_dir,
            llm_router=mock_llm_router,
            auto_save=True,
            enable_auto_summarization=False  # Disable for most tests
        )
    
    def test_manager_initialization(self, manager, temp_dir):
        """Test ChatHistoryManager initialization."""
        assert manager.storage_path == temp_dir
        assert manager.auto_save is True
        assert isinstance(manager.histories, dict)
    
    def test_create_history(self, manager):
        """Test creating a new chat history."""
        history_id = manager.create_history(project_id="proj-123")
        
        assert isinstance(history_id, str)
        assert len(history_id) > 0
        assert history_id in manager.histories
        
        history = manager.histories[history_id]
        assert history.project_id == "proj-123"
        assert len(history.messages) == 0
    
    def test_get_history(self, manager):
        """Test getting a history by ID."""
        history_id = manager.create_history(project_id="proj-123")
        
        history = manager.get_history(history_id)
        
        assert history is not None
        assert history.history_id == history_id
        assert history.project_id == "proj-123"
    
    def test_get_nonexistent_history(self, manager):
        """Test getting a history that doesn't exist."""
        history = manager.get_history("nonexistent-id")
        assert history is None
    
    def test_get_history_by_project(self, manager):
        """Test getting history by project ID."""
        project_id = "proj-123"
        history_id = manager.create_history(project_id=project_id)
        
        history = manager.get_history_by_project(project_id)
        
        assert history is not None
        assert history.history_id == history_id
        assert history.project_id == project_id
    
    def test_delete_history(self, manager):
        """Test deleting a history."""
        history_id = manager.create_history(project_id="proj-123")
        
        assert history_id in manager.histories
        
        success = manager.delete_history(history_id)
        
        assert success is True
        assert history_id not in manager.histories
    
    def test_add_message(self, manager):
        """Test adding a message to history."""
        history_id = manager.create_history(project_id="proj-123")
        
        success = manager.add_message(
            history_id=history_id,
            role="user",
            content="Hello, AI!"
        )
        
        assert success is True
        
        history = manager.get_history(history_id)
        assert len(history.messages) == 1
        assert history.messages[0].role == "user"
        assert history.messages[0].content == "Hello, AI!"
    
    def test_add_user_message(self, manager):
        """Test adding a user message."""
        history_id = manager.create_history(project_id="proj-123")
        
        success = manager.add_user_message(history_id, "User message")
        
        assert success is True
        
        history = manager.get_history(history_id)
        assert len(history.messages) == 1
        assert history.messages[0].role == "user"
    
    def test_add_assistant_message(self, manager):
        """Test adding an assistant message."""
        history_id = manager.create_history(project_id="proj-123")
        
        success = manager.add_assistant_message(history_id, "Assistant response")
        
        assert success is True
        
        history = manager.get_history(history_id)
        assert len(history.messages) == 1
        assert history.messages[0].role == "assistant"
    
    def test_add_system_message(self, manager):
        """Test adding a system message."""
        history_id = manager.create_history(project_id="proj-123")
        
        success = manager.add_system_message(history_id, "System message")
        
        assert success is True
        
        history = manager.get_history(history_id)
        assert len(history.messages) == 1
        assert history.messages[0].role == "system"
    
    def test_get_messages(self, manager):
        """Test getting messages from history."""
        history_id = manager.create_history(project_id="proj-123")
        
        manager.add_user_message(history_id, "Message 1")
        manager.add_assistant_message(history_id, "Message 2")
        manager.add_user_message(history_id, "Message 3")
        
        messages = manager.get_messages(history_id)
        
        assert len(messages) == 3
        assert messages[0]['content'] == "Message 1"
        assert messages[1]['content'] == "Message 2"
        assert messages[2]['content'] == "Message 3"
    
    def test_get_messages_with_limit(self, manager):
        """Test getting messages with a limit."""
        history_id = manager.create_history(project_id="proj-123")
        
        for i in range(10):
            manager.add_user_message(history_id, f"Message {i}")
        
        messages = manager.get_messages(history_id, limit=5)
        
        # Should get the most recent 5 messages
        assert len(messages) == 5
        assert messages[0]['content'] == "Message 5"
        assert messages[4]['content'] == "Message 9"
    
    def test_get_recent_messages(self, manager):
        """Test getting recent messages."""
        history_id = manager.create_history(project_id="proj-123")
        
        for i in range(10):
            manager.add_user_message(history_id, f"Message {i}")
        
        recent = manager.get_recent_messages(history_id, count=3)
        
        assert len(recent) == 3
        assert recent[0]['content'] == "Message 7"
        assert recent[2]['content'] == "Message 9"
    
    def test_summarize_history(self, manager):
        """Test summarizing a history."""
        history_id = manager.create_history(project_id="proj-123")
        
        # Add many messages
        for i in range(15):
            manager.add_user_message(history_id, f"Message {i}")
        
        summary_text = manager.summarize_history(history_id, keep_recent=5)
        
        assert summary_text is not None
        assert isinstance(summary_text, str)
        assert len(summary_text) > 0
        
        # Check that history was compressed
        history = manager.get_history(history_id)
        assert len(history.messages) == 5  # Only recent messages kept
        assert len(history.summaries) == 1  # Summary was added
    
    def test_summarize_history_too_few_messages(self, manager):
        """Test summarization with too few messages."""
        history_id = manager.create_history(project_id="proj-123")
        
        # Add only a few messages
        manager.add_user_message(history_id, "Message 1")
        manager.add_user_message(history_id, "Message 2")
        
        summary_text = manager.summarize_history(history_id, keep_recent=5)
        
        # Should not summarize (too few messages)
        assert summary_text is None
        
        history = manager.get_history(history_id)
        assert len(history.messages) == 2  # Messages unchanged
        assert len(history.summaries) == 0  # No summary added
    
    def test_get_summaries(self, manager):
        """Test getting all summaries for a history."""
        history_id = manager.create_history(project_id="proj-123")
        
        # Add messages and create summary
        for i in range(15):
            manager.add_user_message(history_id, f"Message {i}")
        
        manager.summarize_history(history_id)
        
        summaries = manager.get_summaries(history_id)
        
        assert len(summaries) == 1
        assert isinstance(summaries[0], dict)
        assert 'summary_text' in summaries[0]
    
    def test_clear_history(self, manager):
        """Test clearing all messages from history."""
        history_id = manager.create_history(project_id="proj-123")
        
        manager.add_user_message(history_id, "Message 1")
        manager.add_user_message(history_id, "Message 2")
        
        success = manager.clear_history(history_id)
        
        assert success is True
        
        history = manager.get_history(history_id)
        assert len(history.messages) == 0
        assert len(history.summaries) == 0
    
    def test_get_history_stats(self, manager):
        """Test getting history statistics."""
        history_id = manager.create_history(project_id="proj-123")
        
        manager.add_user_message(history_id, "Message 1")
        manager.add_assistant_message(history_id, "Message 2")
        
        stats = manager.get_history_stats(history_id)
        
        assert stats is not None
        assert stats['history_id'] == history_id
        assert stats['project_id'] == "proj-123"
        assert stats['message_count'] == 2
        assert stats['summary_count'] == 0
        assert 'total_tokens' in stats
    
    def test_persistence_save_and_load(self, manager, temp_dir):
        """Test saving and loading histories."""
        # Create a history with messages
        history_id = manager.create_history(project_id="proj-123")
        manager.add_user_message(history_id, "Hello")
        manager.add_assistant_message(history_id, "Hi there")
        
        # Verify file was created
        history_file = temp_dir / "project_proj-123.json"
        assert history_file.exists()
        
        # Create new manager and load
        new_manager = ChatHistoryManager(
            storage_path=temp_dir,
            llm_router=manager.llm_router,
            auto_save=False
        )
        
        # Load the history
        loaded_history = new_manager.get_history_by_project("proj-123")
        
        assert loaded_history is not None
        assert loaded_history.history_id == history_id
        assert len(loaded_history.messages) == 2
        assert loaded_history.messages[0].content == "Hello"
        assert loaded_history.messages[1].content == "Hi there"
    
    def test_export_history(self, manager, temp_dir):
        """Test exporting a history."""
        history_id = manager.create_history(project_id="proj-123")
        manager.add_user_message(history_id, "Test message")
        
        export_path = temp_dir / "export_history.json"
        success = manager.export_history(history_id, export_path)
        
        assert success is True
        assert export_path.exists()
    
    def test_auto_summarization_trigger(self, temp_dir, mock_llm_router):
        """Test that summarization is triggered automatically."""
        manager = ChatHistoryManager(
            storage_path=temp_dir,
            llm_router=mock_llm_router,
            auto_save=False,
            enable_auto_summarization=True,
            summarization_strategy=SummarizationStrategy.MESSAGE_COUNT,
            summarize_after_messages=10,
            keep_recent_messages=3
        )
        
        history_id = manager.create_history(project_id="proj-123")
        
        # Add messages up to threshold
        for i in range(10):
            manager.add_user_message(history_id, f"Message {i}")
        
        # Should have triggered summarization
        history = manager.get_history(history_id)
        assert len(history.summaries) >= 1  # At least one summary created
        assert len(history.messages) == 3   # Only recent messages kept
    
    def test_len_and_repr(self, manager):
        """Test __len__ and __repr__ methods."""
        assert len(manager) == 0
        
        manager.create_history(project_id="proj-1")
        assert len(manager) == 1
        
        manager.create_history(project_id="proj-2")
        assert len(manager) == 2
        
        # Test repr
        repr_str = repr(manager)
        assert "ChatHistoryManager" in repr_str
        assert "histories=2" in repr_str
    
    def test_get_full_context_with_summary(self, manager):
        """Test getting full context including summary."""
        history_id = manager.create_history(project_id="proj-123")
        
        # Add messages and summarize
        for i in range(15):
            manager.add_user_message(history_id, f"Message {i}")
        
        manager.summarize_history(history_id, keep_recent=3)
        
        # Get full context
        context = manager.get_full_context(history_id)
        
        # Should have summary as first message + recent messages
        assert len(context) > 3  # At least summary + 3 messages
        assert context[0]['role'] == 'system'  # Summary as system message
        assert '[Previous conversation summary' in context[0]['content']
