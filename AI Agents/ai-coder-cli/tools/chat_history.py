"""
Chat History Tool - Manages conversation history and context summaries.

This tool provides chat history management including:
- Saving and loading chat messages
- Context summary generation
- Conversation history tracking
- Session management
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from datetime import datetime, timedelta

from .base import Tool


class ChatHistoryTool(Tool):
    """
    Tool for managing chat history and context summaries.
    
    Capabilities:
    - Save and load chat messages
    - Manage conversation sessions
    - Generate context summaries
    - Track conversation history
    - Prune old messages
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the chat history tool.
        
        Args:
            config: Configuration dictionary with optional:
                - project_root: Root directory of the project (default: current directory)
                - max_messages: Maximum messages to keep per session (default: 1000)
                - max_age_days: Maximum age of messages in days (default: 30)
        """
        super().__init__(
            name='chat_history',
            description='Chat history and context summary management',
            config=config
        )
        
        self.project_root = Path(self.config.get('project_root', '.'))
        self.history_dir = self.project_root / '.project' / 'chat_history'
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_messages = self.config.get('max_messages', 1000)
        self.max_age_days = self.config.get('max_age_days', 30)
        
        self.sessions_file = self.history_dir / 'sessions.json'
        self.summaries_file = self.history_dir / 'summaries.json'
    
    def invoke(self, params: Dict[str, Any]) -> Any:
        """
        Execute chat history operation.
        
        Args:
            params: Dictionary with:
                - action: Operation to perform (save_message, load_history, 
                         create_session, get_session, list_sessions, save_summary,
                         load_summary, prune_history, clear_session)
                - Additional action-specific parameters
                
        Returns:
            Operation result
        """
        self._log_invocation(params)
        
        action = params.get('action')
        if not action:
            raise ValueError("Parameter 'action' is required")
        
        # Route to appropriate method
        if action == 'save_message':
            return self._save_message(
                params.get('session_id'),
                params.get('message')
            )
        elif action == 'load_history':
            return self._load_history(
                params.get('session_id'),
                params.get('limit')
            )
        elif action == 'create_session':
            return self._create_session(
                params.get('session_id'),
                params.get('metadata')
            )
        elif action == 'get_session':
            return self._get_session(params.get('session_id'))
        elif action == 'list_sessions':
            return self._list_sessions()
        elif action == 'save_summary':
            return self._save_summary(
                params.get('session_id'),
                params.get('summary')
            )
        elif action == 'load_summary':
            return self._load_summary(params.get('session_id'))
        elif action == 'prune_history':
            return self._prune_history(params.get('session_id'))
        elif action == 'clear_session':
            return self._clear_session(params.get('session_id'))
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _get_session_file(self, session_id: str) -> Path:
        """Get the path to a session history file."""
        return self.history_dir / f"session_{session_id}.json"
    
    def _save_message(self, session_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Save a chat message to history."""
        if not session_id:
            raise ValueError("Parameter 'session_id' is required")
        if not message:
            raise ValueError("Parameter 'message' is required")
        
        session_file = self._get_session_file(session_id)
        
        # Load existing history
        history = []
        if session_file.exists():
            with open(session_file, 'r') as f:
                data = json.load(f)
                history = data.get('messages', [])
        
        # Add timestamp if not present
        if 'timestamp' not in message:
            message['timestamp'] = datetime.now().isoformat()
        
        # Add message
        history.append(message)
        
        # Limit message count
        if len(history) > self.max_messages:
            history = history[-self.max_messages:]
        
        # Save back
        session_data = {
            'session_id': session_id,
            'messages': history,
            'updated_at': datetime.now().isoformat()
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Update session registry
        self._update_session_registry(session_id)
        
        self.logger.info(f"Saved message to session: {session_id}")
        
        return {
            'success': True,
            'session_id': session_id,
            'message_count': len(history)
        }
    
    def _load_history(self, session_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Load chat history for a session."""
        if not session_id:
            raise ValueError("Parameter 'session_id' is required")
        
        session_file = self._get_session_file(session_id)
        
        if not session_file.exists():
            return {
                'success': False,
                'session_id': session_id,
                'error': 'Session not found'
            }
        
        with open(session_file, 'r') as f:
            data = json.load(f)
        
        messages = data.get('messages', [])
        
        # Apply limit if specified
        if limit and limit > 0:
            messages = messages[-limit:]
        
        return {
            'success': True,
            'session_id': session_id,
            'messages': messages,
            'total_count': len(data.get('messages', [])),
            'updated_at': data.get('updated_at')
        }
    
    def _create_session(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new chat session."""
        if not session_id:
            raise ValueError("Parameter 'session_id' is required")
        
        session_file = self._get_session_file(session_id)
        
        # Check if session already exists
        if session_file.exists():
            return {
                'success': False,
                'session_id': session_id,
                'error': 'Session already exists'
            }
        
        # Create session data
        session_data = {
            'session_id': session_id,
            'messages': [],
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Update session registry
        self._update_session_registry(session_id, metadata)
        
        self.logger.info(f"Created session: {session_id}")
        
        return {
            'success': True,
            'session_id': session_id,
            'created_at': session_data['created_at']
        }
    
    def _get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session information."""
        if not session_id:
            raise ValueError("Parameter 'session_id' is required")
        
        session_file = self._get_session_file(session_id)
        
        if not session_file.exists():
            return {
                'success': False,
                'session_id': session_id,
                'error': 'Session not found'
            }
        
        with open(session_file, 'r') as f:
            data = json.load(f)
        
        return {
            'success': True,
            'session_id': session_id,
            'message_count': len(data.get('messages', [])),
            'metadata': data.get('metadata', {}),
            'created_at': data.get('created_at'),
            'updated_at': data.get('updated_at')
        }
    
    def _list_sessions(self) -> Dict[str, Any]:
        """List all chat sessions."""
        sessions = self._load_session_registry()
        
        session_list = []
        for session_id, session_info in sessions.items():
            session_list.append({
                'session_id': session_id,
                'message_count': session_info.get('message_count', 0),
                'created_at': session_info.get('created_at'),
                'updated_at': session_info.get('updated_at')
            })
        
        # Sort by updated_at descending
        session_list.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        
        return {
            'success': True,
            'sessions': session_list,
            'total_count': len(session_list)
        }
    
    def _update_session_registry(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Update the session registry with session info."""
        sessions = self._load_session_registry()
        
        # Get current message count
        session_file = self._get_session_file(session_id)
        message_count = 0
        created_at = datetime.now().isoformat()
        
        if session_file.exists():
            with open(session_file, 'r') as f:
                data = json.load(f)
                message_count = len(data.get('messages', []))
                created_at = data.get('created_at', created_at)
        
        # Update registry
        if session_id not in sessions:
            sessions[session_id] = {
                'created_at': created_at,
                'metadata': metadata or {}
            }
        
        sessions[session_id].update({
            'message_count': message_count,
            'updated_at': datetime.now().isoformat()
        })
        
        # Save registry
        with open(self.sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
    
    def _load_session_registry(self) -> Dict[str, Any]:
        """Load the session registry."""
        if self.sessions_file.exists():
            with open(self.sessions_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_summary(self, session_id: str, summary: str) -> Dict[str, Any]:
        """Save a context summary for a session."""
        if not session_id:
            raise ValueError("Parameter 'session_id' is required")
        if not summary:
            raise ValueError("Parameter 'summary' is required")
        
        # Load existing summaries
        summaries = self._load_all_summaries()
        
        # Update with new summary
        summaries[session_id] = {
            'summary': summary,
            'updated_at': datetime.now().isoformat()
        }
        
        # Save back
        with open(self.summaries_file, 'w') as f:
            json.dump(summaries, f, indent=2)
        
        self.logger.info(f"Saved summary for session: {session_id}")
        
        return {
            'success': True,
            'session_id': session_id
        }
    
    def _load_summary(self, session_id: str) -> Dict[str, Any]:
        """Load context summary for a session."""
        if not session_id:
            raise ValueError("Parameter 'session_id' is required")
        
        summaries = self._load_all_summaries()
        summary_entry = summaries.get(session_id)
        
        if summary_entry:
            return {
                'success': True,
                'session_id': session_id,
                'summary': summary_entry.get('summary'),
                'updated_at': summary_entry.get('updated_at')
            }
        else:
            return {
                'success': False,
                'session_id': session_id,
                'error': 'Summary not found'
            }
    
    def _load_all_summaries(self) -> Dict[str, Any]:
        """Load all summaries from file."""
        if self.summaries_file.exists():
            with open(self.summaries_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _prune_history(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Prune old messages from history."""
        cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
        
        if session_id:
            # Prune specific session
            result = self._prune_session(session_id, cutoff_date)
            return {
                'success': True,
                'session_id': session_id,
                'pruned_count': result
            }
        else:
            # Prune all sessions
            sessions = self._load_session_registry()
            total_pruned = 0
            
            for sid in sessions.keys():
                pruned = self._prune_session(sid, cutoff_date)
                total_pruned += pruned
            
            return {
                'success': True,
                'pruned_count': total_pruned,
                'sessions_processed': len(sessions)
            }
    
    def _prune_session(self, session_id: str, cutoff_date: datetime) -> int:
        """Prune messages older than cutoff date from a session."""
        session_file = self._get_session_file(session_id)
        
        if not session_file.exists():
            return 0
        
        with open(session_file, 'r') as f:
            data = json.load(f)
        
        messages = data.get('messages', [])
        original_count = len(messages)
        
        # Filter messages
        filtered_messages = []
        for msg in messages:
            msg_date = datetime.fromisoformat(msg.get('timestamp', cutoff_date.isoformat()))
            if msg_date >= cutoff_date:
                filtered_messages.append(msg)
        
        # Save if changed
        if len(filtered_messages) != original_count:
            data['messages'] = filtered_messages
            data['updated_at'] = datetime.now().isoformat()
            
            with open(session_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Update registry
            self._update_session_registry(session_id)
        
        return original_count - len(filtered_messages)
    
    def _clear_session(self, session_id: str) -> Dict[str, Any]:
        """Clear/delete a session."""
        if not session_id:
            raise ValueError("Parameter 'session_id' is required")
        
        session_file = self._get_session_file(session_id)
        
        if session_file.exists():
            session_file.unlink()
            
            # Remove from registry
            sessions = self._load_session_registry()
            if session_id in sessions:
                del sessions[session_id]
                with open(self.sessions_file, 'w') as f:
                    json.dump(sessions, f, indent=2)
            
            self.logger.info(f"Cleared session: {session_id}")
            
            return {
                'success': True,
                'session_id': session_id
            }
        else:
            return {
                'success': False,
                'session_id': session_id,
                'error': 'Session not found'
            }
