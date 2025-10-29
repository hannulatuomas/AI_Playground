
"""
Shell language agents.

This package provides Shell-specific agents supporting bash, zsh, and sh.
"""

from .code_editor import ShellCodeEditorAgent
from .build_agent import ShellBuildAgent
from .debug_agent import ShellDebugAgent
from .code_tester import ShellCodeTesterAgent
from .code_planner import ShellCodePlannerAgent
from .code_analyzer import ShellCodeAnalyzerAgent
from .project_init_agent import ShellProjectInitAgent
from .documentation_agent import ShellDocumentationAgent

__all__ = [
    'ShellCodeEditorAgent',
    'ShellBuildAgent',
    'ShellDebugAgent',
    'ShellCodeTesterAgent',
    'ShellCodePlannerAgent',
    'ShellCodeAnalyzerAgent',
    'ShellProjectInitAgent',
    'ShellDocumentationAgent',
]
