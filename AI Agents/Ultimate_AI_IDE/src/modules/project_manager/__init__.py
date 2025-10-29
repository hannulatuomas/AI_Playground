"""
Project Manager Module

Handles project scaffolding and maintenance.
Phase 2 implementation.
"""

from .manager import ProjectManager
from .detector import ProjectDetector, ProjectInfo
from .scaffolder import ProjectScaffolder

__all__ = ['ProjectManager', 'ProjectDetector', 'ProjectInfo', 'ProjectScaffolder']
