
"""
Tool system for AI Agent Console.

This package provides the tool infrastructure including base classes,
registry, and concrete tool implementations.
"""

from .base import Tool
from .registry import ToolRegistry
from .web_fetch import WebFetchTool
from .git import GitTool
from .mcp import MCPClientTool
from .file_io import FileIOTool
from .shell_exec import ShellExecTool
from .file_operations import FileOperationsTool
from .vector_db import VectorDBTool, ChromaVectorDB
from .project_management import ProjectManagementTool
from .chat_history import ChatHistoryTool
from .dependency_tracking import DependencyTrackingTool
from .context_cache import ContextCacheTool
from .git_commit_enhanced import GitCommitEnhancedTool
from .versioning import VersioningTool
from .ollama_manager import OllamaManager
from .llamacpp_manager import LlamaCppManager


__all__ = [
    'Tool',
    'ToolRegistry',
    'WebFetchTool',
    'GitTool',
    'MCPClientTool',
    'FileIOTool',
    'ShellExecTool',
    'FileOperationsTool',
    'VectorDBTool',
    'ChromaVectorDB',
    'ProjectManagementTool',
    'ChatHistoryTool',
    'DependencyTrackingTool',
    'ContextCacheTool',
    'GitCommitEnhancedTool',
    'VersioningTool',
    'OllamaManager',
    'LlamaCppManager',
]
