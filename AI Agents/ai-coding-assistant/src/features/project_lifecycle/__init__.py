"""
Project Lifecycle Management

Provides functionality for managing the full lifecycle of software projects:
- Creating projects from templates (TemplateManager)
- Scaffolding project structures (ProjectScaffolder)
- Initializing projects (ProjectInitializer)
- Maintaining projects (ProjectMaintainer)
- Archiving projects (ProjectArchiver)
- Managing project dependencies
- Version control integration
- Deployment and distribution
"""

from .templates import TemplateManager
from .scaffolding import ProjectScaffolder, scaffold_from_template
from .initializer import ProjectInitializer
from .maintenance import ProjectMaintainer
from .archiving import ProjectArchiver

__all__ = [
    'TemplateManager',
    'ProjectScaffolder',
    'scaffold_from_template',
    'ProjectInitializer',
    'ProjectMaintainer',
    'ProjectArchiver',
]
