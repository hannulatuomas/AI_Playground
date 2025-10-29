"""
Orchestration Module

Provides workflow automation and management capabilities for the AI Agent Console.
"""

from .workflows.base_workflow import BaseWorkflow
from .workflows.workflow_manager import WorkflowManager

__all__ = ['BaseWorkflow', 'WorkflowManager']
