"""
Features modules for AI Coding Assistant.

This package contains high-level features built on core modules:
- code_gen: Code generation from natural language
- debugger: Code debugging and error correction
- lang_support: Language-specific utilities and templates
- project_nav: Project navigation, search, and file editing (v1.2.0)
- context_manager: Context and memory management (v1.3.0)
- task_manager: Task decomposition and execution (v1.4.0)
- rule_enforcer: Rule enforcement and best practices (v1.5.0)
- tool_integrator: Git, testing, and documentation integration (v1.6.0)
- rag_indexer: RAG indexing for semantic search (v1.8.0)
- rag_retriever: RAG retrieval for context enhancement (v1.8.0)
"""

from .code_gen import CodeGenerator
from .debugger import Debugger
from .lang_support import LanguageSupport
from .project_nav import ProjectNavigator
from .context_manager import ContextManager
from .task_manager import TaskManager
from .rule_enforcer import RuleEnforcer
from .tool_integrator import ToolIntegrator

# RAG modules (optional dependencies)
try:
    from .rag_indexer import RAGIndexer
    from .rag_retriever import RAGRetriever
    RAG_AVAILABLE = True
except (ImportError, Exception):
    RAGIndexer = None
    RAGRetriever = None
    RAG_AVAILABLE = False

__all__ = [
    'CodeGenerator',
    'Debugger',
    'LanguageSupport',
    'ProjectNavigator',
    'ContextManager',
    'TaskManager',
    'RuleEnforcer',
    'ToolIntegrator',
    'RAGIndexer',
    'RAGRetriever',
    'RAG_AVAILABLE',
]

__version__ = '1.8.0'
