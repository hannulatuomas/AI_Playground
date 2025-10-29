"""
Context Window Manager

Manages conversation history within token limits.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Message:
    """Conversation message."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    tokens: int


class WindowManager:
    """Manages context window for conversations."""
    
    def __init__(self, max_tokens: int = 4000):
        """
        Initialize window manager.
        
        Args:
            max_tokens: Maximum tokens in window
        """
        self.max_tokens = max_tokens
        self.messages: List[Message] = []
    
    def add_message(self, role: str, content: str):
        """
        Add message to window.
        
        Args:
            role: Message role
            content: Message content
        """
        tokens = self._estimate_tokens(content)
        message = Message(role=role, content=content, tokens=tokens)
        self.messages.append(message)
        
        # Trim if needed
        self._trim_window()
    
    def get_messages(self) -> List[Message]:
        """Get all messages in window."""
        return self.messages.copy()
    
    def get_formatted_history(self) -> str:
        """Get formatted conversation history."""
        formatted = ""
        for msg in self.messages:
            formatted += f"{msg.role.upper()}: {msg.content}\n\n"
        return formatted
    
    def clear(self):
        """Clear all messages."""
        self.messages = []
    
    def get_token_count(self) -> int:
        """Get total tokens in window."""
        return sum(msg.tokens for msg in self.messages)
    
    def _trim_window(self):
        """Trim window to fit within token limit."""
        total_tokens = self.get_token_count()
        
        if total_tokens <= self.max_tokens:
            return
        
        # Keep system messages and recent messages
        system_messages = [m for m in self.messages if m.role == 'system']
        other_messages = [m for m in self.messages if m.role != 'system']
        
        # Calculate tokens for system messages
        system_tokens = sum(m.tokens for m in system_messages)
        available_tokens = self.max_tokens - system_tokens
        
        # Keep most recent messages that fit
        kept_messages = []
        current_tokens = 0
        
        for msg in reversed(other_messages):
            if current_tokens + msg.tokens <= available_tokens:
                kept_messages.insert(0, msg)
                current_tokens += msg.tokens
            else:
                break
        
        # Combine system and kept messages
        self.messages = system_messages + kept_messages
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Rough estimate: 1 token ≈ 4 characters
        For production, use tiktoken or similar
        """
        return len(text) // 4
    
    def summarize_old_messages(self, ai_backend, keep_recent: int = 5) -> str:
        """
        Summarize old messages to save space.
        
        Args:
            ai_backend: AI backend for summarization
            keep_recent: Number of recent messages to keep
            
        Returns:
            Summary of old messages
        """
        if len(self.messages) <= keep_recent:
            return ""
        
        # Get old messages
        old_messages = self.messages[:-keep_recent]
        
        # Create text to summarize
        text = ""
        for msg in old_messages:
            text += f"{msg.role}: {msg.content}\n\n"
        
        # Generate summary
        prompt = f"""Summarize this conversation history concisely:

{text}

Provide a brief summary of the key points and context."""
        
        try:
            summary = ai_backend.query(prompt, max_tokens=300)
            return summary.strip()
        except Exception:
            return "Previous conversation context"
    
    def apply_summary(self, summary: str, keep_recent: int = 5):
        """
        Replace old messages with summary.
        
        Args:
            summary: Summary text
            keep_recent: Number of recent messages to keep
        """
        if len(self.messages) <= keep_recent:
            return
        
        # Keep recent messages
        recent_messages = self.messages[-keep_recent:]
        
        # Create summary message
        summary_tokens = self._estimate_tokens(summary)
        summary_message = Message(
            role='system',
            content=f"Previous context: {summary}",
            tokens=summary_tokens
        )
        
        # Replace messages
        self.messages = [summary_message] + recent_messages
