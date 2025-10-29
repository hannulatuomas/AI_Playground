"""
Core modules for AI Coding Assistant.

This package contains the fundamental components:
- llm_interface: Integration with llama.cpp
- prompt_engine: Prompt template management
- learning_db: SQLite-based learning system
- project_manager: Project-level operations
"""

from .llm_interface import LLMInterface, LLMConfig, load_config_from_file, save_config_to_file
from .prompt_engine import PromptEngine
from .learning_db import LearningDB
from .project_manager import ProjectManager
from .model_manager import ModelManager, ModelInfo

__all__ = [
    'LLMInterface',
    'LLMConfig',
    'load_config_from_file',
    'save_config_to_file',
    'PromptEngine',
    'LearningDB',
    'ProjectManager',
    'ModelManager',
    'ModelInfo',
]

__version__ = '1.7.0'
