"""
Project Lifecycle GUI - Modular Structure

This package contains the Project Lifecycle GUI split into manageable modules:
- new_project_tab.py: New project creation interface
- maintenance_tab.py: Dependency and health management
- archiving_tab.py: Version control and archiving
"""

from .new_project_tab import NewProjectTab
from .maintenance_tab import MaintenanceTab
from .archiving_tab import ArchivingTab

__all__ = ['NewProjectTab', 'MaintenanceTab', 'ArchivingTab']
