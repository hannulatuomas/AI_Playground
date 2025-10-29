"""
Context Manager

Main interface for context management operations.
"""

from typing import List, Dict, Optional
from pathlib import Path
from .summarizer import CodeSummarizer, CodeSummary
from .embedder import CodeEmbedder, EmbeddingIndex
from .retriever import ContextRetriever, RetrievedContext
from .window_manager import WindowManager, Message


class ContextManager:
    """Manages code context for AI operations."""
    
    def __init__(self, ai_backend, max_window_tokens: int = 4000):
        """
        Initialize context manager.
        
        Args:
            ai_backend: AI backend
            max_window_tokens: Maximum tokens in conversation window
        """
        self.ai_backend = ai_backend
        self.summarizer = CodeSummarizer(ai_backend)
        self.embedder = CodeEmbedder()
        self.retriever = ContextRetriever(ai_backend)
        self.window_manager = WindowManager(max_window_tokens)
        self.indexed_projects: Dict[str, bool] = {}
    
    def index_project(self, project_path: str, language: str = 'python',
                     force_reindex: bool = False):
        """
        Index a project for context retrieval.
        
        Args:
            project_path: Root path of project
            language: Programming language
            force_reindex: Force re-indexing if already indexed
        """
        if project_path in self.indexed_projects and not force_reindex:
            print(f"Project already indexed: {project_path}")
            return
        
        print(f"Indexing project: {project_path}")
        self.retriever.index_project(project_path, language)
        self.indexed_projects[project_path] = True
        
        stats = self.retriever.get_stats()
        print(f"Indexed {stats['indexed_files']} files")
    
    def get_context_for_task(self, task_description: str,
                            max_tokens: int = 2000) -> str:
        """
        Get relevant context for a task.
        
        Args:
            task_description: Description of task
            max_tokens: Maximum tokens to return
            
        Returns:
            Formatted context string
        """
        return self.retriever.get_context_for_task(task_description, max_tokens)
    
    def add_to_conversation(self, role: str, content: str):
        """
        Add message to conversation history.
        
        Args:
            role: Message role ('user', 'assistant', 'system')
            content: Message content
        """
        self.window_manager.add_message(role, content)
    
    def get_conversation_history(self) -> str:
        """Get formatted conversation history."""
        return self.window_manager.get_formatted_history()
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.window_manager.clear()
    
    def summarize_file(self, file_path: str, language: str = 'python') -> CodeSummary:
        """
        Summarize a code file.
        
        Args:
            file_path: Path to file
            language: Programming language
            
        Returns:
            CodeSummary object
        """
        return self.summarizer.summarize_file(file_path, language)
    
    def build_prompt_with_context(self, user_request: str,
                                  include_project_context: bool = True,
                                  include_conversation: bool = True,
                                  max_context_tokens: int = 2000) -> str:
        """
        Build complete prompt with context.
        
        Args:
            user_request: User's request
            include_project_context: Include relevant project code
            include_conversation: Include conversation history
            max_context_tokens: Maximum tokens for context
            
        Returns:
            Complete prompt string
        """
        prompt_parts = []
        
        # Add conversation history if requested
        if include_conversation:
            history = self.get_conversation_history()
            if history:
                prompt_parts.append("Conversation History:")
                prompt_parts.append(history)
                prompt_parts.append("---")
        
        # Add project context if requested
        if include_project_context:
            context = self.get_context_for_task(user_request, max_context_tokens)
            if context and context != "No relevant context found.":
                prompt_parts.append(context)
                prompt_parts.append("---")
        
        # Add current request
        prompt_parts.append("Current Request:")
        prompt_parts.append(user_request)
        
        return "\n\n".join(prompt_parts)
    
    def manage_conversation_window(self):
        """Manage conversation window to prevent overflow."""
        token_count = self.window_manager.get_token_count()
        max_tokens = self.window_manager.max_tokens
        
        if token_count > max_tokens * 0.8:  # 80% threshold
            # Summarize old messages
            summary = self.window_manager.summarize_old_messages(
                self.ai_backend, 
                keep_recent=5
            )
            
            if summary:
                self.window_manager.apply_summary(summary, keep_recent=5)
                print("Conversation history summarized to save space")
    
    def get_stats(self) -> Dict[str, any]:
        """Get context manager statistics."""
        retriever_stats = self.retriever.get_stats()
        
        return {
            'indexed_projects': len(self.indexed_projects),
            'indexed_files': retriever_stats['indexed_files'],
            'conversation_tokens': self.window_manager.get_token_count(),
            'conversation_messages': len(self.window_manager.messages),
            'max_window_tokens': self.window_manager.max_tokens
        }
    
    def clear_all(self):
        """Clear all context."""
        self.retriever.clear_index()
        self.window_manager.clear()
        self.indexed_projects.clear()
    
    def export_context(self, output_file: str):
        """
        Export context to file.
        
        Args:
            output_file: Path to output file
        """
        import json
        
        data = {
            'indexed_projects': list(self.indexed_projects.keys()),
            'stats': self.get_stats(),
            'conversation': [
                {'role': msg.role, 'content': msg.content}
                for msg in self.window_manager.messages
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"Context exported to {output_file}")
