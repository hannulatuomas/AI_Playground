
"""
Project Management System

This module provides a comprehensive project management system for the AI Agent Console.
It allows users to create, manage, and switch between different projects, each with its own
isolated memory space and context.

Features:
- Create projects with unique identifiers and metadata
- List all available projects
- Switch between projects (set active project)
- Delete projects
- Persist project data to disk (JSON format)
- Project-scoped memory and chat history
- Automatic project initialization and setup

The ProjectManager integrates with the MemoryManager to provide project-scoped memory
that persists across sessions.
"""

import logging
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


logger = logging.getLogger(__name__)


@dataclass
class Project:
    """
    Represents a project with its metadata.
    
    Attributes:
        project_id: Unique identifier for the project
        name: Human-readable project name
        description: Project description
        created_at: Project creation timestamp
        updated_at: Last update timestamp
        metadata: Additional project metadata
        memory_session_id: Associated memory session ID
        is_active: Whether this is the currently active project
    """
    project_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Project"
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    memory_session_id: Optional[str] = None
    is_active: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary for serialization."""
        return {
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata,
            'memory_session_id': self.memory_session_id,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create project from dictionary."""
        return cls(
            project_id=data['project_id'],
            name=data['name'],
            description=data.get('description', ''),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            metadata=data.get('metadata', {}),
            memory_session_id=data.get('memory_session_id'),
            is_active=data.get('is_active', False)
        )
    
    def __repr__(self) -> str:
        """String representation of project."""
        active_marker = " [ACTIVE]" if self.is_active else ""
        return f"<Project id={self.project_id[:8]} name='{self.name}'{active_marker}>"


class ProjectManager:
    """
    Manages projects and their lifecycle.
    
    Features:
    - CRUD operations for projects
    - Project persistence to disk
    - Active project management
    - Project-scoped memory integration
    - Automatic project initialization
    
    Example:
        >>> manager = ProjectManager()
        >>> project_id = manager.create_project("My AI Project", "Working on AI features")
        >>> manager.set_active_project(project_id)
        >>> active = manager.get_active_project()
        >>> projects = manager.list_projects()
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        auto_save: bool = True,
        create_default_project: bool = True
    ):
        """
        Initialize the project manager.
        
        Args:
            storage_path: Path to store project files (default: ./projects/)
            auto_save: Automatically save projects after updates
            create_default_project: Create a default project if none exist
        """
        self.storage_path = storage_path or Path("./projects")
        self.auto_save = auto_save
        
        self.projects: Dict[str, Project] = {}
        self.active_project_id: Optional[str] = None
        self.logger = logging.getLogger(f"{__name__}.ProjectManager")
        
        # Create storage directory if needed
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Project storage initialized at: {self.storage_path}")
        
        # Load existing projects
        self._load_all_projects()
        
        # Create default project if none exist
        if create_default_project and not self.projects:
            self.logger.info("No projects found, creating default project")
            default_id = self.create_project(
                name="Default Project",
                description="Default project for AI Agent Console"
            )
            self.set_active_project(default_id)
        
        # Ensure we have an active project
        if not self.active_project_id and self.projects:
            # Set first project as active
            first_project_id = next(iter(self.projects.keys()))
            self.set_active_project(first_project_id)
        
        self.logger.info(f"ProjectManager initialized with {len(self.projects)} projects")
    
    # ========================================================================
    # Project CRUD Operations
    # ========================================================================
    
    def create_project(
        self,
        name: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None
    ) -> str:
        """
        Create a new project.
        
        Args:
            name: Project name
            description: Project description
            metadata: Optional project metadata
            project_id: Optional custom project ID (auto-generated if None)
            
        Returns:
            Project ID
        """
        project = Project(
            project_id=project_id or str(uuid.uuid4()),
            name=name,
            description=description,
            metadata=metadata or {},
            # Memory session will be created when needed
            memory_session_id=None
        )
        
        self.projects[project.project_id] = project
        self.logger.info(f"Created project: {project.name} ({project.project_id[:8]})")
        
        if self.auto_save:
            self._save_project(project.project_id)
        
        return project.project_id
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """
        Get a project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project or None if not found
        """
        project = self.projects.get(project_id)
        
        if project is None:
            # Try to load from storage if not in memory
            try:
                loaded_project = self._load_project(project_id)
                if loaded_project:
                    self.projects[project_id] = loaded_project
                    return loaded_project
            except Exception as e:
                self.logger.debug(f"Could not load project from storage: {e}")
        
        return project
    
    def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update project information.
        
        Args:
            project_id: Project ID
            name: New project name (optional)
            description: New project description (optional)
            metadata: New metadata (optional, will be merged)
            
        Returns:
            True if updated, False if project not found
        """
        project = self.get_project(project_id)
        if project is None:
            self.logger.error(f"Cannot update project: not found: {project_id}")
            return False
        
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if metadata is not None:
            project.metadata.update(metadata)
        
        project.updated_at = datetime.now()
        
        if self.auto_save:
            self._save_project(project_id)
        
        self.logger.info(f"Updated project: {project.name} ({project_id[:8]})")
        return True
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if deleted, False if not found
        """
        if project_id not in self.projects:
            self.logger.warning(f"Cannot delete project: not found: {project_id}")
            return False
        
        project = self.projects[project_id]
        project_name = project.name
        
        # If this is the active project, clear active status
        if self.active_project_id == project_id:
            self.active_project_id = None
            
            # Set another project as active if available
            remaining_projects = [pid for pid in self.projects.keys() if pid != project_id]
            if remaining_projects:
                self.set_active_project(remaining_projects[0])
        
        # Delete from memory
        del self.projects[project_id]
        
        # Delete from storage
        project_file = self.storage_path / f"{project_id}.json"
        if project_file.exists():
            project_file.unlink()
        
        # Delete project-specific directories (memory, chat history, etc.)
        project_dir = self.storage_path / project_id
        if project_dir.exists() and project_dir.is_dir():
            import shutil
            shutil.rmtree(project_dir)
        
        self.logger.info(f"Deleted project: {project_name} ({project_id[:8]})")
        return True
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects.
        
        Returns:
            List of project dictionaries
        """
        return [project.to_dict() for project in self.projects.values()]
    
    def get_project_info(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project information.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary with project info or None
        """
        project = self.get_project(project_id)
        if project is None:
            return None
        
        return project.to_dict()
    
    # ========================================================================
    # Active Project Management
    # ========================================================================
    
    def set_active_project(self, project_id: str) -> bool:
        """
        Set the active project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if set successfully, False if project not found
        """
        project = self.get_project(project_id)
        if project is None:
            self.logger.error(f"Cannot set active project: not found: {project_id}")
            return False
        
        # Clear active status from all projects
        for proj in self.projects.values():
            proj.is_active = False
        
        # Set new active project
        project.is_active = True
        self.active_project_id = project_id
        
        if self.auto_save:
            # Save all projects to persist active status
            self.save_all_projects()
        
        self.logger.info(f"Active project set to: {project.name} ({project_id[:8]})")
        return True
    
    def get_active_project(self) -> Optional[Project]:
        """
        Get the currently active project.
        
        Returns:
            Active Project or None if no active project
        """
        if self.active_project_id:
            return self.get_project(self.active_project_id)
        return None
    
    def get_active_project_id(self) -> Optional[str]:
        """
        Get the active project ID.
        
        Returns:
            Active project ID or None
        """
        return self.active_project_id
    
    # ========================================================================
    # Memory Integration
    # ========================================================================
    
    def get_project_memory_session_id(self, project_id: str) -> Optional[str]:
        """
        Get the memory session ID for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Memory session ID or None
        """
        project = self.get_project(project_id)
        if project is None:
            return None
        return project.memory_session_id
    
    def set_project_memory_session_id(
        self,
        project_id: str,
        memory_session_id: str
    ) -> bool:
        """
        Set the memory session ID for a project.
        
        Args:
            project_id: Project ID
            memory_session_id: Memory session ID
            
        Returns:
            True if set successfully, False if project not found
        """
        project = self.get_project(project_id)
        if project is None:
            self.logger.error(f"Cannot set memory session: project not found: {project_id}")
            return False
        
        project.memory_session_id = memory_session_id
        project.updated_at = datetime.now()
        
        if self.auto_save:
            self._save_project(project_id)
        
        self.logger.debug(f"Set memory session for project {project_id[:8]}: {memory_session_id[:8]}")
        return True
    
    def get_project_storage_path(self, project_id: str) -> Optional[Path]:
        """
        Get the storage path for a specific project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Path to project storage directory or None
        """
        project = self.get_project(project_id)
        if project is None:
            return None
        
        project_path = self.storage_path / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        return project_path
    
    # ========================================================================
    # Persistence
    # ========================================================================
    
    def _save_project(self, project_id: str) -> bool:
        """
        Save a project to storage.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if saved successfully
        """
        project = self.projects.get(project_id)
        if project is None:
            return False
        
        try:
            project_file = self.storage_path / f"{project_id}.json"
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved project: {project_id[:8]}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save project {project_id[:8]}: {e}")
            return False
    
    def _load_project(self, project_id: str) -> Optional[Project]:
        """
        Load a project from storage.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project or None if not found
        """
        try:
            project_file = self.storage_path / f"{project_id}.json"
            if not project_file.exists():
                return None
            
            with open(project_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            project = Project.from_dict(data)
            self.logger.debug(f"Loaded project: {project_id[:8]}")
            return project
            
        except Exception as e:
            self.logger.error(f"Failed to load project {project_id[:8]}: {e}")
            return None
    
    def _load_all_projects(self) -> int:
        """
        Load all projects from storage.
        
        Returns:
            Number of projects loaded
        """
        count = 0
        
        # Load all project files
        for project_file in self.storage_path.glob("*.json"):
            project_id = project_file.stem
            project = self._load_project(project_id)
            if project:
                self.projects[project_id] = project
                
                # Track active project
                if project.is_active:
                    self.active_project_id = project_id
                
                count += 1
        
        self.logger.info(f"Loaded {count} projects from storage")
        return count
    
    def save_all_projects(self) -> int:
        """
        Save all projects to storage.
        
        Returns:
            Number of projects saved
        """
        count = 0
        for project_id in self.projects.keys():
            if self._save_project(project_id):
                count += 1
        
        self.logger.info(f"Saved {count} projects")
        return count
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def find_projects_by_name(self, name: str) -> List[Project]:
        """
        Find projects by name (case-insensitive substring match).
        
        Args:
            name: Project name to search for
            
        Returns:
            List of matching projects
        """
        name_lower = name.lower()
        return [
            project for project in self.projects.values()
            if name_lower in project.name.lower()
        ]
    
    def get_project_count(self) -> int:
        """
        Get the total number of projects.
        
        Returns:
            Number of projects
        """
        return len(self.projects)
    
    def export_project(self, project_id: str, export_path: Path) -> bool:
        """
        Export a project to a specific path.
        
        Args:
            project_id: Project ID
            export_path: Path to export the project to
            
        Returns:
            True if exported successfully
        """
        project = self.get_project(project_id)
        if project is None:
            self.logger.error(f"Cannot export project: not found: {project_id}")
            return False
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(project.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported project {project.name} to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export project {project_id[:8]}: {e}")
            return False
    
    def import_project(self, import_path: Path) -> Optional[str]:
        """
        Import a project from a file.
        
        Args:
            import_path: Path to import the project from
            
        Returns:
            Project ID if imported successfully, None otherwise
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            project = Project.from_dict(data)
            
            # Ensure unique project ID
            if project.project_id in self.projects:
                project.project_id = str(uuid.uuid4())
                self.logger.info(f"Project ID conflict, generated new ID: {project.project_id[:8]}")
            
            # Don't set as active on import
            project.is_active = False
            
            self.projects[project.project_id] = project
            
            if self.auto_save:
                self._save_project(project.project_id)
            
            self.logger.info(f"Imported project: {project.name} ({project.project_id[:8]})")
            return project.project_id
            
        except Exception as e:
            self.logger.error(f"Failed to import project from {import_path}: {e}")
            return None
    
    def __len__(self) -> int:
        """Return number of projects."""
        return len(self.projects)
    
    def __repr__(self) -> str:
        """String representation of project manager."""
        active = f" active={self.active_project_id[:8] if self.active_project_id else None}"
        return f"<ProjectManager projects={len(self.projects)}{active}>"
