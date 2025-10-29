
"""
CSharp language agents.

This package provides CSharp-specific agents.
"""

from .code_editor import CSharpCodeEditorAgent
from .build_agent import CSharpBuildAgent
from .debug_agent import CSharpDebugAgent
from .code_tester import CSharpCodeTesterAgent
from .code_planner import CSharpCodePlannerAgent
from .code_analyzer import CSharpCodeAnalyzerAgent
from .project_init_agent import CSharpProjectInitAgent
from .documentation_agent import CSharpDocumentationAgent

__all__ = [
    'CSharpCodeEditorAgent',
    'CSharpBuildAgent',
    'CSharpDebugAgent',
    'CSharpCodeTesterAgent',
    'CSharpCodePlannerAgent',
    'CSharpCodeAnalyzerAgent',
    'CSharpProjectInitAgent',
    'CSharpDocumentationAgent',
]
