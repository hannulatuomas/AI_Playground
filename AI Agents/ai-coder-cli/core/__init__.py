
"""
Core module for AI Agent Console.

This package contains the core infrastructure for:
- Configuration management (config.py)
- LLM provider routing (llm_router.py)
- Main orchestration engine (engine.py)
- Memory management (memory.py, vector_memory.py)
- Project management (project_manager.py)
- Chat history management (chat_history.py)
"""

from .config import AppConfig, setup_logging
from .engine import Engine, EngineError
from .llm_router import (
    LLMRouter,
    BaseLLMProvider,
    OllamaProvider,
    OpenAIProvider,
    LLMProviderError,
    ConnectionError,
    AuthenticationError,
    RateLimitError,
    ProviderType
)
from .memory import MemoryManager, MemorySession, Message, MessageRole
from .vector_memory import VectorMemoryManager, create_vector_memory_manager
from .project_manager import ProjectManager, Project
from .chat_history import (
    ChatHistoryManager,
    ChatHistory,
    ChatMessage,
    ChatSummary,
    SummarizationStrategy
)
from .prompt_manager import (
    PromptManager,
    Prompt,
    PromptScope,
    PromptType,
    create_prompt_manager
)

__all__ = [
    # Configuration
    'AppConfig',
    'setup_logging',
    
    # Engine
    'Engine',
    'EngineError',
    
    # LLM Routing
    'LLMRouter',
    'BaseLLMProvider',
    'OllamaProvider',
    'OpenAIProvider',
    'LLMProviderError',
    'ConnectionError',
    'AuthenticationError',
    'RateLimitError',
    'ProviderType',
    
    # Memory Management
    'MemoryManager',
    'MemorySession',
    'Message',
    'MessageRole',
    'VectorMemoryManager',
    'create_vector_memory_manager',
    
    # Project Management
    'ProjectManager',
    'Project',
    
    # Chat History Management
    'ChatHistoryManager',
    'ChatHistory',
    'ChatMessage',
    'ChatSummary',
    'SummarizationStrategy',
    
    # Prompt Management
    'PromptManager',
    'Prompt',
    'PromptScope',
    'PromptType',
    'create_prompt_manager',
]

# Read version from VERSION file
import os
_version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'VERSION')
try:
    with open(_version_file, 'r') as f:
        __version__ = f.read().strip()
except Exception:
    __version__ = '0.1.0'  # Fallback version
