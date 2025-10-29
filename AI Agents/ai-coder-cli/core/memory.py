
"""
Agent Memory System

This module provides a robust memory and conversation history management system
for AI agents. It supports:
- Conversation history tracking (user messages and agent responses)
- Context persistence across interactions
- Memory retrieval capabilities
- Memory management (context window limits, summarization)
- Session management
- Memory search and query capabilities

The memory system integrates seamlessly with the existing agent architecture.
"""

import logging
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum


logger = logging.getLogger(__name__)


class MessageRole(Enum):
    """Enum for message roles in conversation history."""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


@dataclass
class Message:
    """
    Represents a single message in conversation history.
    
    Attributes:
        role: Message role (user, agent, system)
        content: Message content
        agent_name: Name of agent that generated this message (if role=agent)
        timestamp: When the message was created
        metadata: Additional metadata about the message
        tokens: Estimated token count for the message
    """
    role: MessageRole
    content: str
    agent_name: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tokens: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            'role': self.role.value,
            'content': self.content,
            'agent_name': self.agent_name,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'tokens': self.tokens
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        return cls(
            role=MessageRole(data['role']),
            content=data['content'],
            agent_name=data.get('agent_name'),
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {}),
            tokens=data.get('tokens')
        )
    
    def __repr__(self) -> str:
        """String representation of message."""
        agent_info = f" ({self.agent_name})" if self.agent_name else ""
        return f"<Message role={self.role.value}{agent_info} len={len(self.content)} ts={self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}>"


@dataclass
class MemorySession:
    """
    Represents a conversation session with its own message history.
    
    Attributes:
        session_id: Unique identifier for the session
        messages: List of messages in this session
        created_at: When the session was created
        updated_at: Last update timestamp
        metadata: Session-level metadata
        max_context_window: Maximum number of tokens in context
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    max_context_window: int = 4096  # Default context window size
    
    def add_message(self, message: Message) -> None:
        """Add a message to the session."""
        self.messages.append(message)
        self.updated_at = datetime.now()
        # Handle both string and enum for role
        role_str = message.role.value if isinstance(message.role, MessageRole) else str(message.role)
        logger.debug(f"Added message to session {self.session_id[:8]}: {role_str}")
    
    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Get the most recent N messages."""
        return self.messages[-count:] if len(self.messages) > count else self.messages
    
    def get_messages_by_role(self, role: MessageRole) -> List[Message]:
        """Get all messages with a specific role."""
        return [msg for msg in self.messages if msg.role == role]
    
    def get_messages_by_agent(self, agent_name: str) -> List[Message]:
        """Get all messages from a specific agent."""
        return [msg for msg in self.messages if msg.agent_name == agent_name]
    
    def get_total_tokens(self) -> int:
        """Calculate total tokens in session."""
        return sum(msg.tokens or self._estimate_tokens(msg.content) for msg in self.messages)
    
    def is_context_window_exceeded(self) -> bool:
        """Check if context window is exceeded."""
        return self.get_total_tokens() > self.max_context_window
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Simple heuristic: ~4 characters per token for English text.
        This is approximate; for accurate counts, use a tokenizer.
        """
        return len(text) // 4
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            'session_id': self.session_id,
            'messages': [msg.to_dict() for msg in self.messages],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata,
            'max_context_window': self.max_context_window
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemorySession':
        """Create session from dictionary."""
        session = cls(
            session_id=data['session_id'],
            messages=[Message.from_dict(msg_data) for msg_data in data['messages']],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            metadata=data.get('metadata', {}),
            max_context_window=data.get('max_context_window', 4096)
        )
        return session
    
    def __len__(self) -> int:
        """Return number of messages in session."""
        return len(self.messages)
    
    def __repr__(self) -> str:
        """String representation of session."""
        return f"<MemorySession id={self.session_id[:8]} messages={len(self.messages)} tokens={self.get_total_tokens()}>"


class MemoryManager:
    """
    Manages agent memory across sessions.
    
    Features:
    - Session management (create, get, delete)
    - Conversation history tracking
    - Context window management
    - Memory persistence (save/load)
    - Memory search and retrieval
    - Automatic memory summarization
    
    Example:
        >>> manager = MemoryManager()
        >>> session_id = manager.create_session()
        >>> manager.add_user_message(session_id, "Hello, agent!")
        >>> manager.add_agent_message(session_id, "Hi! How can I help?", "code_editor")
        >>> history = manager.get_conversation_history(session_id)
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        default_max_context_window: int = 4096,
        auto_save: bool = True,
        enable_summarization: bool = True,
        llm_router: Optional[Any] = None,
        project_scoped: bool = True
    ):
        """
        Initialize the memory manager.
        
        Args:
            storage_path: Path to store memory files (None = no persistence)
            default_max_context_window: Default context window size in tokens
            auto_save: Automatically save sessions after updates
            enable_summarization: Enable automatic memory summarization
            llm_router: LLM router for memory summarization (required if enable_summarization=True)
            project_scoped: Enable project-scoped memory (recommended)
        """
        self.storage_path = storage_path
        self.default_max_context_window = default_max_context_window
        self.auto_save = auto_save
        self.enable_summarization = enable_summarization
        self.llm_router = llm_router
        self.project_scoped = project_scoped
        
        self.sessions: Dict[str, MemorySession] = {}
        self.project_sessions: Dict[str, str] = {}  # project_id -> session_id mapping
        self.current_project_id: Optional[str] = None
        self.logger = logging.getLogger(f"{__name__}.MemoryManager")
        
        # Create storage directory if needed
        if self.storage_path:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Memory storage initialized at: {self.storage_path}")
        
        self.logger.info(f"MemoryManager initialized (project_scoped={project_scoped})")
    
    # ========================================================================
    # Session Management
    # ========================================================================
    
    def create_session(
        self,
        session_id: Optional[str] = None,
        max_context_window: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new memory session.
        
        Args:
            session_id: Optional custom session ID (auto-generated if None)
            max_context_window: Optional custom context window size
            metadata: Optional session metadata
            
        Returns:
            Session ID
        """
        session = MemorySession(
            session_id=session_id or str(uuid.uuid4()),
            max_context_window=max_context_window or self.default_max_context_window,
            metadata=metadata or {}
        )
        
        self.sessions[session.session_id] = session
        self.logger.info(f"Created session: {session.session_id[:8]}")
        
        if self.auto_save:
            self._save_session(session.session_id)
        
        return session.session_id
    
    def get_session(self, session_id: str) -> Optional[MemorySession]:
        """
        Get a session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            MemorySession or None if not found
        """
        # Check in-memory sessions first
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        # Try to load from storage if not in memory
        if self.storage_path:
            try:
                loaded_session = self._load_session(session_id)
                if loaded_session:
                    self.sessions[session_id] = loaded_session
                    return loaded_session
            except Exception as e:
                self.logger.debug(f"Could not load session from storage: {e}")
        
        self.logger.warning(f"Session not found: {session_id}")
        return None
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            
            # Delete from storage
            if self.storage_path:
                session_file = self.storage_path / f"{session_id}.json"
                if session_file.exists():
                    session_file.unlink()
            
            self.logger.info(f"Deleted session: {session_id[:8]}")
            return True
        
        return False
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear all messages from a session without deleting the session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if cleared, False if session not found
        """
        session = self.get_session(session_id)
        if session is None:
            self.logger.error(f"Cannot clear session: not found: {session_id}")
            return False
        
        session.messages = []
        session.updated_at = datetime.now()
        
        if self.auto_save:
            self._save_session(session_id)
        
        self.logger.info(f"Cleared session: {session_id[:8]}")
        return True
    
    def list_sessions(self) -> List[str]:
        """
        List all session IDs.
        
        Returns:
            List of session IDs
        """
        session_ids = set(self.sessions.keys())
        
        # Add sessions from storage
        if self.storage_path:
            for session_file in self.storage_path.glob("*.json"):
                session_ids.add(session_file.stem)
        
        return sorted(session_ids)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information without loading all messages.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dictionary with session info or None
        """
        session = self.get_session(session_id)
        if session is None:
            return None
        
        return {
            'session_id': session.session_id,
            'message_count': len(session.messages),
            'total_tokens': session.get_total_tokens(),
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat(),
            'metadata': session.metadata,
            'max_context_window': session.max_context_window,
            'context_exceeded': session.is_context_window_exceeded()
        }
    
    # ========================================================================
    # Message Management
    # ========================================================================
    
    def add_message(
        self,
        session_id: str,
        role: Union[MessageRole, str],
        content: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a message to a session.
        
        Args:
            session_id: Session ID
            role: Message role (can be MessageRole enum or string)
            content: Message content
            agent_name: Agent name (for agent messages)
            metadata: Optional message metadata
            
        Returns:
            True if added, False if session not found
        """
        session = self.get_session(session_id)
        if session is None:
            self.logger.error(f"Cannot add message: session not found: {session_id}")
            return False
        
        # Convert string role to MessageRole enum if needed
        if isinstance(role, str):
            # Handle common string aliases
            role_map = {
                'user': MessageRole.USER,
                'agent': MessageRole.AGENT,
                'assistant': MessageRole.AGENT,  # Common alias for agent
                'system': MessageRole.SYSTEM
            }
            role_lower = role.lower()
            if role_lower in role_map:
                role = role_map[role_lower]
            else:
                try:
                    role = MessageRole(role)
                except ValueError:
                    self.logger.warning(f"Invalid role '{role}', defaulting to USER")
                    role = MessageRole.USER
        
        message = Message(
            role=role,
            content=content,
            agent_name=agent_name,
            metadata=metadata or {}
        )
        
        session.add_message(message)
        
        # Check context window and summarize if needed
        if self.enable_summarization and session.is_context_window_exceeded():
            self.logger.info(f"Context window exceeded for session {session_id[:8]}, triggering summarization")
            self._summarize_session(session_id)
        
        if self.auto_save:
            self._save_session(session_id)
        
        return True
    
    def add_user_message(
        self,
        session_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a user message to a session.
        
        Args:
            session_id: Session ID
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            True if added, False if session not found
        """
        return self.add_message(session_id, MessageRole.USER, content, metadata=metadata)
    
    def add_agent_message(
        self,
        session_id: str,
        content: str,
        agent_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add an agent message to a session.
        
        Args:
            session_id: Session ID
            content: Message content
            agent_name: Name of the agent
            metadata: Optional message metadata
            
        Returns:
            True if added, False if session not found
        """
        return self.add_message(
            session_id,
            MessageRole.AGENT,
            content,
            agent_name=agent_name,
            metadata=metadata
        )
    
    def add_system_message(
        self,
        session_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a system message to a session.
        
        Args:
            session_id: Session ID
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            True if added, False if session not found
        """
        return self.add_message(session_id, MessageRole.SYSTEM, content, metadata=metadata)
    
    # ========================================================================
    # Memory Retrieval
    # ========================================================================
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None,
        include_system: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session ID
            limit: Optional limit on number of messages (most recent)
            include_system: Whether to include system messages
            
        Returns:
            List of message dictionaries
        """
        session = self.get_session(session_id)
        if session is None:
            return []
        
        messages = session.messages
        
        if not include_system:
            messages = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
        
        if limit:
            messages = messages[-limit:]
        
        return [msg.to_dict() for msg in messages]
    
    def get_context_for_agent(
        self,
        session_id: str,
        agent_name: str,
        max_messages: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get relevant context for an agent execution.
        
        Args:
            session_id: Session ID
            agent_name: Name of the agent requesting context
            max_messages: Maximum number of messages to include
            
        Returns:
            List of message dictionaries
        """
        session = self.get_session(session_id)
        if session is None:
            return []
        
        # Get recent messages
        recent_messages = session.get_recent_messages(max_messages)
        
        # Include summary if available
        context = []
        if 'summary' in session.metadata:
            context.append({
                'role': 'system',
                'content': f"Previous conversation summary: {session.metadata['summary']}",
                'agent_name': None,
                'timestamp': session.updated_at.isoformat(),
                'metadata': {'type': 'summary'},
                'tokens': None
            })
        
        # Add recent messages
        context.extend([msg.to_dict() for msg in recent_messages])
        
        return context
    
    def search_messages(
        self,
        session_id: str,
        query: str,
        role: Optional[MessageRole] = None,
        agent_name: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search messages in a session.
        
        Args:
            session_id: Session ID
            query: Search query (case-insensitive substring match)
            role: Optional role filter
            agent_name: Optional agent name filter
            limit: Maximum number of results
            
        Returns:
            List of matching message dictionaries
        """
        session = self.get_session(session_id)
        if session is None:
            return []
        
        query_lower = query.lower()
        results = []
        
        for msg in session.messages:
            # Apply filters
            if role and msg.role != role:
                continue
            if agent_name and msg.agent_name != agent_name:
                continue
            
            # Search in content
            if query_lower in msg.content.lower():
                results.append(msg.to_dict())
                
                if len(results) >= limit:
                    break
        
        return results
    
    # ========================================================================
    # Memory Summarization
    # ========================================================================
    
    def _summarize_session(self, session_id: str) -> bool:
        """
        Summarize old messages in a session to reduce context size.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if summarized successfully
        """
        if not self.llm_router:
            self.logger.warning("Cannot summarize: LLM router not available")
            return False
        
        session = self.get_session(session_id)
        if session is None:
            return False
        
        try:
            # Keep recent messages, summarize older ones
            keep_count = 5
            messages_to_summarize = session.messages[:-keep_count] if len(session.messages) > keep_count else []
            
            if not messages_to_summarize:
                return True  # Nothing to summarize
            
            # Build summarization prompt
            prompt = self._build_summarization_prompt(messages_to_summarize)
            
            # Get summary from LLM
            self.logger.info(f"Summarizing {len(messages_to_summarize)} messages for session {session_id[:8]}")
            response = self.llm_router.query(prompt=prompt, temperature=0.3)
            summary = response.get('response', '').strip()
            
            if summary:
                # Store summary in session metadata
                session.metadata['summary'] = summary
                session.metadata['summarized_at'] = datetime.now().isoformat()
                session.metadata['summarized_message_count'] = len(messages_to_summarize)
                
                # Remove summarized messages, keep a system message with the summary
                session.messages = [
                    Message(
                        role=MessageRole.SYSTEM,
                        content=f"Summary of previous conversation ({len(messages_to_summarize)} messages): {summary}",
                        metadata={'type': 'summary', 'original_message_count': len(messages_to_summarize)}
                    )
                ] + session.messages[-keep_count:]
                
                self.logger.info(f"Session {session_id[:8]} summarized successfully")
                
                if self.auto_save:
                    self._save_session(session_id)
                
                return True
            
        except Exception as e:
            self.logger.error(f"Summarization failed for session {session_id[:8]}: {e}")
        
        return False
    
    def _build_summarization_prompt(self, messages: List[Message]) -> str:
        """
        Build prompt for message summarization.
        
        Args:
            messages: Messages to summarize
            
        Returns:
            Prompt string
        """
        conversation = "\n\n".join([
            f"{msg.role.value.upper()}{f' ({msg.agent_name})' if msg.agent_name else ''}: {msg.content}"
            for msg in messages
        ])
        
        return f"""Summarize the following conversation concisely, preserving key information, decisions, and context:

{conversation}

Provide a concise summary in 2-3 sentences that captures the essential points and outcomes."""
    
    # ========================================================================
    # Persistence
    # ========================================================================
    
    def _save_session(self, session_id: str) -> bool:
        """
        Save a session to storage.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if saved successfully
        """
        if not self.storage_path:
            return False
        
        session = self.sessions.get(session_id)
        if session is None:
            return False
        
        try:
            session_file = self.storage_path / f"{session_id}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved session: {session_id[:8]}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save session {session_id[:8]}: {e}")
            return False
    
    def _load_session(self, session_id: str) -> Optional[MemorySession]:
        """
        Load a session from storage.
        
        Args:
            session_id: Session ID
            
        Returns:
            MemorySession or None if not found
        """
        if not self.storage_path:
            return None
        
        try:
            session_file = self.storage_path / f"{session_id}.json"
            if not session_file.exists():
                return None
            
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session = MemorySession.from_dict(data)
            self.logger.debug(f"Loaded session: {session_id[:8]}")
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to load session {session_id[:8]}: {e}")
            return None
    
    def save_all_sessions(self) -> int:
        """
        Save all sessions to storage.
        
        Returns:
            Number of sessions saved
        """
        if not self.storage_path:
            return 0
        
        count = 0
        for session_id in self.sessions.keys():
            if self._save_session(session_id):
                count += 1
        
        self.logger.info(f"Saved {count} sessions")
        return count
    
    def load_all_sessions(self) -> int:
        """
        Load all sessions from storage.
        
        Returns:
            Number of sessions loaded
        """
        if not self.storage_path:
            return 0
        
        count = 0
        for session_file in self.storage_path.glob("*.json"):
            session_id = session_file.stem
            session = self._load_session(session_id)
            if session:
                self.sessions[session_id] = session
                count += 1
        
        self.logger.info(f"Loaded {count} sessions")
        return count
    
    # ========================================================================
    # Cleanup
    # ========================================================================
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        Delete sessions older than specified days.
        
        Args:
            days: Delete sessions older than this many days
            
        Returns:
            Number of sessions deleted
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for session_id in list(self.sessions.keys()):
            session = self.sessions[session_id]
            if session.updated_at < cutoff_date:
                if self.delete_session(session_id):
                    deleted_count += 1
        
        self.logger.info(f"Cleaned up {deleted_count} old sessions (older than {days} days)")
        return deleted_count
    
    # ========================================================================
    # Project-Scoped Memory
    # ========================================================================
    
    def set_project_context(self, project_id: str) -> bool:
        """
        Set the current project context for memory operations.
        
        Args:
            project_id: Project ID to set as current context
            
        Returns:
            True if set successfully
        """
        if not self.project_scoped:
            self.logger.warning("Project scoping is disabled")
            return False
        
        self.current_project_id = project_id
        self.logger.info(f"Project context set to: {project_id[:8]}")
        return True
    
    def get_project_context(self) -> Optional[str]:
        """
        Get the current project context.
        
        Returns:
            Current project ID or None
        """
        return self.current_project_id
    
    def create_project_session(
        self,
        project_id: str,
        max_context_window: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create or get a memory session for a specific project.
        
        Args:
            project_id: Project ID
            max_context_window: Optional custom context window size
            metadata: Optional session metadata
            
        Returns:
            Session ID
        """
        # Check if project already has a session
        if project_id in self.project_sessions:
            existing_session_id = self.project_sessions[project_id]
            if existing_session_id in self.sessions:
                self.logger.debug(f"Using existing session for project {project_id[:8]}")
                return existing_session_id
        
        # Create new session for project
        session_id = self.create_session(
            max_context_window=max_context_window,
            metadata={**(metadata or {}), 'project_id': project_id}
        )
        
        # Map project to session
        self.project_sessions[project_id] = session_id
        
        # Store project session in project-specific directory if storage is enabled
        if self.storage_path:
            project_dir = self.storage_path / "projects" / project_id
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a symlink or reference file
            project_session_file = project_dir / "session_id.txt"
            with open(project_session_file, 'w') as f:
                f.write(session_id)
        
        self.logger.info(f"Created session {session_id[:8]} for project {project_id[:8]}")
        return session_id
    
    def get_project_session_id(self, project_id: str) -> Optional[str]:
        """
        Get the session ID for a specific project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Session ID or None if not found
        """
        # Check in-memory mapping first
        if project_id in self.project_sessions:
            return self.project_sessions[project_id]
        
        # Try to load from storage
        if self.storage_path:
            project_session_file = self.storage_path / "projects" / project_id / "session_id.txt"
            if project_session_file.exists():
                try:
                    with open(project_session_file, 'r') as f:
                        session_id = f.read().strip()
                    
                    # Update in-memory mapping
                    self.project_sessions[project_id] = session_id
                    return session_id
                except Exception as e:
                    self.logger.error(f"Failed to load project session ID: {e}")
        
        return None
    
    def get_project_session(self, project_id: str) -> Optional[MemorySession]:
        """
        Get the memory session for a specific project.
        
        Args:
            project_id: Project ID
            
        Returns:
            MemorySession or None if not found
        """
        session_id = self.get_project_session_id(project_id)
        if session_id:
            return self.get_session(session_id)
        return None
    
    def switch_project_context(self, project_id: str) -> bool:
        """
        Switch to a different project's memory context.
        
        Args:
            project_id: Project ID to switch to
            
        Returns:
            True if switched successfully
        """
        if not self.project_scoped:
            self.logger.warning("Project scoping is disabled")
            return False
        
        # Get or create session for this project
        session_id = self.get_project_session_id(project_id)
        if not session_id:
            session_id = self.create_project_session(project_id)
        
        # Set as current context
        self.current_project_id = project_id
        
        self.logger.info(f"Switched to project {project_id[:8]} (session: {session_id[:8]})")
        return True
    
    def get_current_session_id(self) -> Optional[str]:
        """
        Get the session ID for the current project context.
        
        Returns:
            Session ID or None if no project context is set
        """
        if not self.project_scoped or not self.current_project_id:
            # Return a default session if not project-scoped
            if self.sessions:
                return next(iter(self.sessions.keys()))
            return None
        
        return self.get_project_session_id(self.current_project_id)
    
    def delete_project_memory(self, project_id: str) -> bool:
        """
        Delete all memory for a specific project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if deleted successfully
        """
        session_id = self.get_project_session_id(project_id)
        if session_id:
            # Delete the session
            self.delete_session(session_id)
        
        # Remove from project mapping
        if project_id in self.project_sessions:
            del self.project_sessions[project_id]
        
        # Delete project directory
        if self.storage_path:
            project_dir = self.storage_path / "projects" / project_id
            if project_dir.exists():
                import shutil
                shutil.rmtree(project_dir)
        
        self.logger.info(f"Deleted memory for project {project_id[:8]}")
        return True
    
    def list_project_sessions(self) -> Dict[str, str]:
        """
        List all project-to-session mappings.
        
        Returns:
            Dictionary of project_id -> session_id
        """
        return self.project_sessions.copy()
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def __len__(self) -> int:
        """Return number of active sessions."""
        return len(self.sessions)
    
    def __repr__(self) -> str:
        """String representation of memory manager."""
        project_info = f" current_project={self.current_project_id[:8] if self.current_project_id else None}" if self.project_scoped else ""
        return f"<MemoryManager sessions={len(self.sessions)}{project_info} storage={self.storage_path}>"
