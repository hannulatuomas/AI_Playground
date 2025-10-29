
"""
Generic fallback agents for unsupported languages.

This package provides default implementations of code editor, build,
debug, project initialization, and task orchestration agents that can 
handle any language using LLM-based approaches.
"""

from .generic_code_editor import GenericCodeEditor
from .generic_build_agent import GenericBuildAgent
from .generic_debug_agent import GenericDebugAgent
from .generic_project_init import GenericProjectInitAgent
from .generic_code_tester import GenericCodeTester
from .generic_code_planner import GenericCodePlanner
from .generic_code_analyzer import GenericCodeAnalyzer
from .task_orchestrator import TaskOrchestrator

__all__ = [
    'GenericCodeEditor',
    'GenericBuildAgent',
    'GenericDebugAgent',
    'GenericProjectInitAgent',
    'GenericCodeTester',
    'GenericCodePlanner',
    'GenericCodeAnalyzer',
    'TaskOrchestrator',
]
