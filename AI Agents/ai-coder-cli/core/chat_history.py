
"""
Chat History and Context Summary System

This module provides comprehensive chat history management with intelligent summarization
capabilities. It tracks conversations, persists them to disk, and can generate summaries
to compress long conversations while preserving important context.

Features:
- Write and read chat messages for each project/session
- Intelligent summarization to compress chat history
- Configurable summarization strategies
- Multiple summarization triggers (message count, token count, time-based)
- Store summaries alongside full history
- Quick context loading with summaries
- Project-scoped chat history
- Session continuity across restarts

The ChatHistoryManager integrates with the LLM system to generate high-quality summaries
and works seamlessly with the ProjectManager for project-scoped history.
"""

import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class SummarizationStrategy(Enum):
    """Strategies for when to trigger summarization."""
    MESSAGE_COUNT = "message_count"  # After N messages
    TOKEN_COUNT = "token_count"      # After N tokens
    TIME_BASED = "time_based"        # After N minutes/hours
    MANUAL = "manual"                # Only when explicitly requested


@dataclass
class ChatMessage:
    """
    Represents a single chat message.
    
    Attributes:
        role: Message role (user/assistant/system)
        content: Message content
        timestamp: When the message was created
        metadata: Additional metadata
        tokens: Estimated token count
    """
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tokens: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'tokens': self.tokens
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Create message from dictionary."""
        return cls(
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {}),
            tokens=data.get('tokens')
        )


@dataclass
class ChatSummary:
    """
    Represents a summary of chat messages.
    
    Attributes:
        summary_text: The summary content
        original_message_count: Number of messages summarized
        original_token_count: Total tokens in original messages
        created_at: When the summary was created
        strategy_used: Summarization strategy used
        metadata: Additional summary metadata
    """
    summary_text: str
    original_message_count: int
    original_token_count: int
    created_at: datetime = field(default_factory=datetime.now)
    strategy_used: str = "manual"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert summary to dictionary."""
        return {
            'summary_text': self.summary_text,
            'original_message_count': self.original_message_count,
            'original_token_count': self.original_token_count,
            'created_at': self.created_at.isoformat(),
            'strategy_used': self.strategy_used,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSummary':
        """Create summary from dictionary."""
        return cls(
            summary_text=data['summary_text'],
            original_message_count=data['original_message_count'],
            original_token_count=data['original_token_count'],
            created_at=datetime.fromisoformat(data['created_at']),
            strategy_used=data.get('strategy_used', 'manual'),
            metadata=data.get('metadata', {})
        )


@dataclass
class ChatHistory:
    """
    Represents a complete chat history with messages and summaries.
    
    Attributes:
        history_id: Unique identifier for this history
        project_id: Associated project ID
        messages: List of chat messages
        summaries: List of chat summaries
        created_at: When the history was created
        updated_at: Last update timestamp
        metadata: Additional history metadata
    """
    history_id: str
    project_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    summaries: List[ChatSummary] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: ChatMessage) -> None:
        """Add a message to the history."""
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def add_summary(self, summary: ChatSummary) -> None:
        """Add a summary to the history."""
        self.summaries.append(summary)
        self.updated_at = datetime.now()
    
    def get_total_tokens(self) -> int:
        """Calculate total tokens in all messages."""
        return sum(msg.tokens or self._estimate_tokens(msg.content) for msg in self.messages)
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        Simple heuristic: ~4 characters per token.
        """
        return len(text) // 4
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert history to dictionary."""
        return {
            'history_id': self.history_id,
            'project_id': self.project_id,
            'messages': [msg.to_dict() for msg in self.messages],
            'summaries': [summary.to_dict() for summary in self.summaries],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatHistory':
        """Create history from dictionary."""
        return cls(
            history_id=data['history_id'],
            project_id=data['project_id'],
            messages=[ChatMessage.from_dict(msg) for msg in data.get('messages', [])],
            summaries=[ChatSummary.from_dict(s) for s in data.get('summaries', [])],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            metadata=data.get('metadata', {})
        )


class ChatHistoryManager:
    """
    Manages chat history with intelligent summarization.
    
    Features:
    - Project-scoped chat history
    - Automatic and manual summarization
    - Multiple summarization strategies
    - History persistence
    - Context loading and reconstruction
    - Summary management
    
    Example:
        >>> manager = ChatHistoryManager(llm_router=llm_router)
        >>> history_id = manager.create_history(project_id="proj123")
        >>> manager.add_user_message(history_id, "Hello!")
        >>> manager.add_assistant_message(history_id, "Hi! How can I help?")
        >>> summary = manager.summarize_history(history_id)
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        llm_router: Optional[Any] = None,
        auto_save: bool = True,
        summarization_strategy: SummarizationStrategy = SummarizationStrategy.MESSAGE_COUNT,
        summarize_after_messages: int = 20,
        summarize_after_tokens: int = 8000,
        keep_recent_messages: int = 10,
        enable_auto_summarization: bool = True
    ):
        """
        Initialize the chat history manager.
        
        Args:
            storage_path: Path to store chat history files
            llm_router: LLM router for generating summaries
            auto_save: Automatically save history after updates
            summarization_strategy: When to trigger summarization
            summarize_after_messages: Message count threshold for summarization
            summarize_after_tokens: Token count threshold for summarization
            keep_recent_messages: Number of recent messages to keep after summarization
            enable_auto_summarization: Enable automatic summarization
        """
        self.storage_path = storage_path or Path("./chat_history")
        self.llm_router = llm_router
        self.auto_save = auto_save
        self.summarization_strategy = summarization_strategy
        self.summarize_after_messages = summarize_after_messages
        self.summarize_after_tokens = summarize_after_tokens
        self.keep_recent_messages = keep_recent_messages
        self.enable_auto_summarization = enable_auto_summarization
        
        self.histories: Dict[str, ChatHistory] = {}
        self.logger = logging.getLogger(f"{__name__}.ChatHistoryManager")
        
        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Chat history storage initialized at: {self.storage_path}")
        
        self.logger.info("ChatHistoryManager initialized")
    
    # ========================================================================
    # History Management
    # ========================================================================
    
    def create_history(
        self,
        project_id: str,
        history_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new chat history for a project.
        
        Args:
            project_id: Project ID
            history_id: Optional custom history ID
            metadata: Optional history metadata
            
        Returns:
            History ID
        """
        import uuid
        
        history = ChatHistory(
            history_id=history_id or str(uuid.uuid4()),
            project_id=project_id,
            metadata=metadata or {}
        )
        
        self.histories[history.history_id] = history
        self.logger.info(f"Created chat history: {history.history_id[:8]} for project {project_id[:8]}")
        
        if self.auto_save:
            self._save_history(history.history_id)
        
        return history.history_id
    
    def get_history(self, history_id: str) -> Optional[ChatHistory]:
        """
        Get a chat history by ID.
        
        Args:
            history_id: History ID
            
        Returns:
            ChatHistory or None if not found
        """
        # Check in-memory histories first
        if history_id in self.histories:
            return self.histories[history_id]
        
        # Try to load from storage
        loaded_history = self._load_history(history_id)
        if loaded_history:
            self.histories[history_id] = loaded_history
            return loaded_history
        
        return None
    
    def get_history_by_project(self, project_id: str) -> Optional[ChatHistory]:
        """
        Get the chat history for a specific project.
        
        Args:
            project_id: Project ID
            
        Returns:
            ChatHistory or None if not found
        """
        # Check in-memory histories
        for history in self.histories.values():
            if history.project_id == project_id:
                return history
        
        # Try to load from storage
        history_file = self.storage_path / f"project_{project_id}.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                history = ChatHistory.from_dict(data)
                self.histories[history.history_id] = history
                return history
            except Exception as e:
                self.logger.error(f"Failed to load history for project {project_id[:8]}: {e}")
        
        return None
    
    def delete_history(self, history_id: str) -> bool:
        """
        Delete a chat history.
        
        Args:
            history_id: History ID
            
        Returns:
            True if deleted, False if not found
        """
        if history_id not in self.histories:
            return False
        
        history = self.histories[history_id]
        project_id = history.project_id
        
        # Delete from memory
        del self.histories[history_id]
        
        # Delete from storage
        history_file = self.storage_path / f"project_{project_id}.json"
        if history_file.exists():
            history_file.unlink()
        
        self.logger.info(f"Deleted chat history: {history_id[:8]}")
        return True
    
    # ========================================================================
    # Message Management
    # ========================================================================
    
    def add_message(
        self,
        history_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a message to a chat history.
        
        Args:
            history_id: History ID
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            True if added, False if history not found
        """
        history = self.get_history(history_id)
        if history is None:
            self.logger.error(f"Cannot add message: history not found: {history_id}")
            return False
        
        message = ChatMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        history.add_message(message)
        
        # Check if summarization is needed
        if self.enable_auto_summarization:
            if self._should_summarize(history):
                self.logger.info(f"Auto-summarization triggered for history {history_id[:8]}")
                self.summarize_history(history_id)
        
        if self.auto_save:
            self._save_history(history_id)
        
        return True
    
    def add_user_message(
        self,
        history_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a user message."""
        return self.add_message(history_id, "user", content, metadata)
    
    def add_assistant_message(
        self,
        history_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add an assistant message."""
        return self.add_message(history_id, "assistant", content, metadata)
    
    def add_system_message(
        self,
        history_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a system message."""
        return self.add_message(history_id, "system", content, metadata)
    
    # ========================================================================
    # History Retrieval
    # ========================================================================
    
    def get_messages(
        self,
        history_id: str,
        limit: Optional[int] = None,
        include_summaries: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a chat history.
        
        Args:
            history_id: History ID
            limit: Optional limit on number of messages
            include_summaries: Whether to include summary as a message
            
        Returns:
            List of message dictionaries
        """
        history = self.get_history(history_id)
        if history is None:
            return []
        
        messages = []
        
        # Add latest summary if requested
        if include_summaries and history.summaries:
            latest_summary = history.summaries[-1]
            messages.append({
                'role': 'system',
                'content': f"[Previous conversation summary ({latest_summary.original_message_count} messages)]: {latest_summary.summary_text}",
                'timestamp': latest_summary.created_at.isoformat(),
                'metadata': {'type': 'summary'}
            })
        
        # Add messages
        msg_list = history.messages
        if limit:
            msg_list = msg_list[-limit:]
        
        messages.extend([msg.to_dict() for msg in msg_list])
        
        return messages
    
    def get_full_context(self, history_id: str) -> List[Dict[str, Any]]:
        """
        Get full context including summaries for LLM consumption.
        
        Args:
            history_id: History ID
            
        Returns:
            List of context messages
        """
        return self.get_messages(history_id, include_summaries=True)
    
    def get_recent_messages(
        self,
        history_id: str,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get the most recent messages.
        
        Args:
            history_id: History ID
            count: Number of recent messages
            
        Returns:
            List of message dictionaries
        """
        return self.get_messages(history_id, limit=count, include_summaries=False)
    
    # ========================================================================
    # Summarization
    # ========================================================================
    
    def _should_summarize(self, history: ChatHistory) -> bool:
        """
        Check if summarization should be triggered.
        
        Args:
            history: ChatHistory to check
            
        Returns:
            True if summarization should be triggered
        """
        if not self.enable_auto_summarization:
            return False
        
        if self.summarization_strategy == SummarizationStrategy.MANUAL:
            return False
        
        if self.summarization_strategy == SummarizationStrategy.MESSAGE_COUNT:
            return len(history.messages) >= self.summarize_after_messages
        
        if self.summarization_strategy == SummarizationStrategy.TOKEN_COUNT:
            return history.get_total_tokens() >= self.summarize_after_tokens
        
        if self.summarization_strategy == SummarizationStrategy.TIME_BASED:
            # Check if last summary was more than 1 hour ago
            if history.summaries:
                last_summary_time = history.summaries[-1].created_at
                return (datetime.now() - last_summary_time) > timedelta(hours=1)
            # Or if no summaries and messages are old
            if history.messages:
                first_message_time = history.messages[0].timestamp
                return (datetime.now() - first_message_time) > timedelta(hours=1)
        
        return False
    
    def summarize_history(
        self,
        history_id: str,
        keep_recent: Optional[int] = None
    ) -> Optional[str]:
        """
        Summarize a chat history.
        
        Args:
            history_id: History ID
            keep_recent: Number of recent messages to keep (uses default if None)
            
        Returns:
            Summary text or None if failed
        """
        if not self.llm_router:
            self.logger.warning("Cannot summarize: LLM router not available")
            return None
        
        history = self.get_history(history_id)
        if history is None:
            self.logger.error(f"Cannot summarize: history not found: {history_id}")
            return None
        
        keep_count = keep_recent or self.keep_recent_messages
        
        # Determine messages to summarize
        if len(history.messages) <= keep_count:
            self.logger.info(f"History {history_id[:8]} has too few messages to summarize")
            return None
        
        messages_to_summarize = history.messages[:-keep_count]
        
        try:
            # Build summarization prompt
            prompt = self._build_summarization_prompt(messages_to_summarize, history.summaries)
            
            # Get summary from LLM
            self.logger.info(f"Summarizing {len(messages_to_summarize)} messages for history {history_id[:8]}")
            response = self.llm_router.query(prompt=prompt, temperature=0.3)
            summary_text = response.get('response', '').strip()
            
            if summary_text:
                # Create summary object
                summary = ChatSummary(
                    summary_text=summary_text,
                    original_message_count=len(messages_to_summarize),
                    original_token_count=sum(
                        msg.tokens or history._estimate_tokens(msg.content)
                        for msg in messages_to_summarize
                    ),
                    strategy_used=self.summarization_strategy.value
                )
                
                history.add_summary(summary)
                
                # Remove summarized messages, keep recent ones
                history.messages = history.messages[-keep_count:]
                
                self.logger.info(f"History {history_id[:8]} summarized successfully")
                
                if self.auto_save:
                    self._save_history(history_id)
                
                return summary_text
            
        except Exception as e:
            self.logger.error(f"Summarization failed for history {history_id[:8]}: {e}")
        
        return None
    
    def _build_summarization_prompt(
        self,
        messages: List[ChatMessage],
        previous_summaries: List[ChatSummary]
    ) -> str:
        """
        Build prompt for chat history summarization.
        
        Args:
            messages: Messages to summarize
            previous_summaries: Previous summaries for context
            
        Returns:
            Prompt string
        """
        prompt_parts = []
        
        # Add previous summary context if available
        if previous_summaries:
            latest_summary = previous_summaries[-1]
            prompt_parts.append("Previous conversation summary:")
            prompt_parts.append(latest_summary.summary_text)
            prompt_parts.append("\nNew messages to incorporate:")
        else:
            prompt_parts.append("Conversation to summarize:")
        
        # Add messages
        for msg in messages:
            prompt_parts.append(f"\n{msg.role.upper()}: {msg.content}")
        
        # Add instructions
        prompt_parts.append("\n\nProvide a comprehensive but concise summary that:")
        prompt_parts.append("1. Captures key topics discussed")
        prompt_parts.append("2. Preserves important decisions and conclusions")
        prompt_parts.append("3. Maintains context for future conversation")
        prompt_parts.append("4. Highlights any action items or pending questions")
        
        if previous_summaries:
            prompt_parts.append("5. Integrates with the previous summary to create a cohesive narrative")
        
        prompt_parts.append("\nSummary (2-4 paragraphs):")
        
        return "\n".join(prompt_parts)
    
    def get_summaries(self, history_id: str) -> List[Dict[str, Any]]:
        """
        Get all summaries for a history.
        
        Args:
            history_id: History ID
            
        Returns:
            List of summary dictionaries
        """
        history = self.get_history(history_id)
        if history is None:
            return []
        
        return [summary.to_dict() for summary in history.summaries]
    
    # ========================================================================
    # Persistence
    # ========================================================================
    
    def _save_history(self, history_id: str) -> bool:
        """
        Save a chat history to storage.
        
        Args:
            history_id: History ID
            
        Returns:
            True if saved successfully
        """
        history = self.histories.get(history_id)
        if history is None:
            return False
        
        try:
            # Save using project_id as filename for easy lookup
            history_file = self.storage_path / f"project_{history.project_id}.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved chat history: {history_id[:8]}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save chat history {history_id[:8]}: {e}")
            return False
    
    def _load_history(self, history_id: str) -> Optional[ChatHistory]:
        """
        Load a chat history from storage.
        
        Args:
            history_id: History ID
            
        Returns:
            ChatHistory or None if not found
        """
        try:
            # Try to find by history_id in all files
            for history_file in self.storage_path.glob("*.json"):
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('history_id') == history_id:
                    history = ChatHistory.from_dict(data)
                    self.logger.debug(f"Loaded chat history: {history_id[:8]}")
                    return history
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to load chat history {history_id[:8]}: {e}")
            return None
    
    def save_all_histories(self) -> int:
        """
        Save all histories to storage.
        
        Returns:
            Number of histories saved
        """
        count = 0
        for history_id in self.histories.keys():
            if self._save_history(history_id):
                count += 1
        
        self.logger.info(f"Saved {count} chat histories")
        return count
    
    def load_all_histories(self) -> int:
        """
        Load all histories from storage.
        
        Returns:
            Number of histories loaded
        """
        count = 0
        for history_file in self.storage_path.glob("*.json"):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                history = ChatHistory.from_dict(data)
                self.histories[history.history_id] = history
                count += 1
            except Exception as e:
                self.logger.error(f"Failed to load history from {history_file}: {e}")
        
        self.logger.info(f"Loaded {count} chat histories")
        return count
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def get_history_stats(self, history_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a chat history.
        
        Args:
            history_id: History ID
            
        Returns:
            Dictionary with statistics or None
        """
        history = self.get_history(history_id)
        if history is None:
            return None
        
        return {
            'history_id': history.history_id,
            'project_id': history.project_id,
            'message_count': len(history.messages),
            'summary_count': len(history.summaries),
            'total_tokens': history.get_total_tokens(),
            'created_at': history.created_at.isoformat(),
            'updated_at': history.updated_at.isoformat(),
            'metadata': history.metadata
        }
    
    def clear_history(self, history_id: str) -> bool:
        """
        Clear all messages from a history without deleting it.
        
        Args:
            history_id: History ID
            
        Returns:
            True if cleared, False if history not found
        """
        history = self.get_history(history_id)
        if history is None:
            return False
        
        history.messages = []
        history.summaries = []
        history.updated_at = datetime.now()
        
        if self.auto_save:
            self._save_history(history_id)
        
        self.logger.info(f"Cleared chat history: {history_id[:8]}")
        return True
    
    def export_history(self, history_id: str, export_path: Path) -> bool:
        """
        Export a chat history to a file.
        
        Args:
            history_id: History ID
            export_path: Path to export to
            
        Returns:
            True if exported successfully
        """
        history = self.get_history(history_id)
        if history is None:
            return False
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(history.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported chat history {history_id[:8]} to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export history {history_id[:8]}: {e}")
            return False
    
    def __len__(self) -> int:
        """Return number of histories."""
        return len(self.histories)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<ChatHistoryManager histories={len(self.histories)} storage={self.storage_path}>"
