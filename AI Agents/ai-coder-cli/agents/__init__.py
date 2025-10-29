
"""
Agent system for AI Agent Console.

This package provides the agent infrastructure including base classes,
registry, and concrete agent implementations.

New Architecture:
- base/: Base classes for all agent types
- generic/: Generic fallback agents for unsupported languages
- languages/: Language-specific agent implementations organized by language
"""

# Base classes
from .base import Agent, CodeEditorBase, BuildAgentBase, DebugAgentBase
from .registry import AgentRegistry

# Core agents (not language-specific)
from .git_agent import GitAgent
from .web_data import WebDataAgent

# Specialized agents
from .prompt_refiner import PromptRefinerAgent
from .linux_admin import LinuxAdminAgent

# Extensibility examples (stubs)
from .data_analysis import DataAnalysisAgent
from .windows_admin import WindowsAdminAgent
from .cybersecurity import CybersecurityAgent

# New agents
from .web_search import WebSearchAgent
from .database import DatabaseAgent
from .api_agent import APIAgent

# Generic fallback agents
from .generic import GenericCodeEditor, GenericBuildAgent, GenericDebugAgent, GenericProjectInitAgent, TaskOrchestrator

# Language-specific agents (new structure)
from .languages.python import (
    PythonCodeEditorAgent,
    PythonBuildAgent,
    PythonDebugAgent,
    PythonProjectInitAgent,
)

from .languages.csharp import (
    CSharpCodeEditorAgent,
    CSharpBuildAgent,
    CSharpDebugAgent,
    CSharpProjectInitAgent,
)

from .languages.cpp import (
    CPPCodeEditorAgent,
    CPPBuildAgent,
    CPPDebugAgent,
    CPPProjectInitAgent,
)

from .languages.web import (
    WebJSTSCodeEditorAgent,
    WebJSTSBuildAgent,
    WebJSTSDebugAgent,
    WebJSTSProjectInitAgent,
)

from .languages.shell import (
    ShellCodeEditorAgent,
    ShellBuildAgent,
    ShellDebugAgent,
    ShellProjectInitAgent,
)

from .languages.powershell import (
    PowerShellCodeEditorAgent,
    PowerShellBuildAgent,
    PowerShellDebugAgent,
    PowerShellProjectInitAgent,
)

from .languages.batch import (
    BatchCodeEditorAgent,
    BatchBuildAgent,
    BatchDebugAgent,
    BatchProjectInitAgent,
)


__all__ = [
    # Base classes
    'Agent',
    'CodeEditorBase',
    'BuildAgentBase',
    'DebugAgentBase',
    'AgentRegistry',
    
    # Core agents
    'GitAgent',
    'WebDataAgent',
    
    # Specialized agents
    'PromptRefinerAgent',
    'LinuxAdminAgent',
    
    # Extensibility examples
    'DataAnalysisAgent',
    'WindowsAdminAgent',
    'CybersecurityAgent',
    
    # New agents
    'WebSearchAgent',
    'DatabaseAgent',
    'APIAgent',
    
    # Generic agents
    'GenericCodeEditor',
    'GenericBuildAgent',
    'GenericDebugAgent',
    'GenericProjectInitAgent',
    'TaskOrchestrator',
    
    # Python agents
    'PythonCodeEditorAgent',
    'PythonBuildAgent',
    'PythonDebugAgent',
    
    # C# agents
    'CSharpCodeEditorAgent',
    'CSharpBuildAgent',
    'CSharpDebugAgent',
    
    # C++ agents
    'CPPCodeEditorAgent',
    'CPPBuildAgent',
    'CPPDebugAgent',
    
    # Web development agents
    'WebJSTSCodeEditorAgent',
    'WebJSTSBuildAgent',
    'WebJSTSDebugAgent',
    
    # Shell agents (bash/zsh/sh)
    'ShellCodeEditorAgent',
    'ShellBuildAgent',
    'ShellDebugAgent',
    
    # PowerShell agents
    'PowerShellCodeEditorAgent',
    'PowerShellBuildAgent',
    'PowerShellDebugAgent',
    
    # Batch agents
    'BatchCodeEditorAgent',
    'BatchBuildAgent',
    'BatchDebugAgent',
]
