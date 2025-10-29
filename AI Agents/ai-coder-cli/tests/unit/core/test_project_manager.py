
"""
Unit tests for ProjectManager.

Tests the project management system including CRUD operations,
persistence, and project-scoped functionality.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from core.project_manager import ProjectManager, Project


class TestProject:
    """Tests for the Project dataclass."""
    
    def test_project_creation(self):
        """Test creating a project with default values."""
        project = Project(name="Test Project")
        
        assert project.name == "Test Project"
        assert project.description == ""
        assert isinstance(project.project_id, str)
        assert len(project.project_id) > 0
        assert isinstance(project.created_at, datetime)
        assert isinstance(project.updated_at, datetime)
        assert project.metadata == {}
        assert project.memory_session_id is None
        assert project.is_active is False
    
    def test_project_with_custom_values(self):
        """Test creating a project with custom values."""
        project = Project(
            project_id="custom-id",
            name="Custom Project",
            description="Test description",
            is_active=True,
            metadata={"key": "value"}
        )
        
        assert project.project_id == "custom-id"
        assert project.name == "Custom Project"
        assert project.description == "Test description"
        assert project.is_active is True
        assert project.metadata == {"key": "value"}
    
    def test_project_to_dict(self):
        """Test converting project to dictionary."""
        project = Project(
            name="Test Project",
            description="Test description"
        )
        
        data = project.to_dict()
        
        assert isinstance(data, dict)
        assert data['name'] == "Test Project"
        assert data['description'] == "Test description"
        assert 'project_id' in data
        assert 'created_at' in data
        assert 'updated_at' in data
        assert 'metadata' in data
        assert 'memory_session_id' in data
        assert 'is_active' in data
    
    def test_project_from_dict(self):
        """Test creating project from dictionary."""
        data = {
            'project_id': 'test-id',
            'name': 'Test Project',
            'description': 'Test description',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'metadata': {'key': 'value'},
            'memory_session_id': 'session-123',
            'is_active': True
        }
        
        project = Project.from_dict(data)
        
        assert project.project_id == 'test-id'
        assert project.name == 'Test Project'
        assert project.description == 'Test description'
        assert project.metadata == {'key': 'value'}
        assert project.memory_session_id == 'session-123'
        assert project.is_active is True


class TestProjectManager:
    """Tests for the ProjectManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        # Cleanup
        if temp_path.exists():
            shutil.rmtree(temp_path)
    
    @pytest.fixture
    def manager(self, temp_dir):
        """Create a ProjectManager instance for testing."""
        return ProjectManager(
            storage_path=temp_dir,
            auto_save=True,
            create_default_project=False  # Don't create default for tests
        )
    
    def test_manager_initialization(self, manager, temp_dir):
        """Test ProjectManager initialization."""
        assert manager.storage_path == temp_dir
        assert manager.auto_save is True
        assert isinstance(manager.projects, dict)
        assert manager.active_project_id is None
    
    def test_create_project(self, manager):
        """Test creating a new project."""
        project_id = manager.create_project(
            name="Test Project",
            description="Test description"
        )
        
        assert isinstance(project_id, str)
        assert len(project_id) > 0
        assert project_id in manager.projects
        
        project = manager.projects[project_id]
        assert project.name == "Test Project"
        assert project.description == "Test description"
    
    def test_create_project_with_custom_id(self, manager):
        """Test creating a project with custom ID."""
        custom_id = "custom-project-id"
        project_id = manager.create_project(
            name="Test Project",
            project_id=custom_id
        )
        
        assert project_id == custom_id
        assert custom_id in manager.projects
    
    def test_get_project(self, manager):
        """Test getting a project by ID."""
        project_id = manager.create_project(name="Test Project")
        
        project = manager.get_project(project_id)
        
        assert project is not None
        assert project.project_id == project_id
        assert project.name == "Test Project"
    
    def test_get_nonexistent_project(self, manager):
        """Test getting a project that doesn't exist."""
        project = manager.get_project("nonexistent-id")
        assert project is None
    
    def test_update_project(self, manager):
        """Test updating project information."""
        project_id = manager.create_project(name="Original Name")
        
        success = manager.update_project(
            project_id=project_id,
            name="Updated Name",
            description="New description",
            metadata={"key": "value"}
        )
        
        assert success is True
        
        project = manager.get_project(project_id)
        assert project.name == "Updated Name"
        assert project.description == "New description"
        assert project.metadata["key"] == "value"
    
    def test_update_nonexistent_project(self, manager):
        """Test updating a project that doesn't exist."""
        success = manager.update_project(
            project_id="nonexistent-id",
            name="New Name"
        )
        
        assert success is False
    
    def test_delete_project(self, manager):
        """Test deleting a project."""
        project_id = manager.create_project(name="Test Project")
        
        assert project_id in manager.projects
        
        success = manager.delete_project(project_id)
        
        assert success is True
        assert project_id not in manager.projects
    
    def test_delete_nonexistent_project(self, manager):
        """Test deleting a project that doesn't exist."""
        success = manager.delete_project("nonexistent-id")
        assert success is False
    
    def test_list_projects(self, manager):
        """Test listing all projects."""
        # Create some projects
        id1 = manager.create_project(name="Project 1")
        id2 = manager.create_project(name="Project 2")
        id3 = manager.create_project(name="Project 3")
        
        projects = manager.list_projects()
        
        assert len(projects) == 3
        assert all(isinstance(p, dict) for p in projects)
        
        project_names = [p['name'] for p in projects]
        assert "Project 1" in project_names
        assert "Project 2" in project_names
        assert "Project 3" in project_names
    
    def test_set_active_project(self, manager):
        """Test setting the active project."""
        project_id = manager.create_project(name="Test Project")
        
        success = manager.set_active_project(project_id)
        
        assert success is True
        assert manager.active_project_id == project_id
        
        project = manager.get_project(project_id)
        assert project.is_active is True
    
    def test_set_active_project_clears_previous(self, manager):
        """Test that setting active project clears previous active status."""
        id1 = manager.create_project(name="Project 1")
        id2 = manager.create_project(name="Project 2")
        
        manager.set_active_project(id1)
        assert manager.get_project(id1).is_active is True
        
        manager.set_active_project(id2)
        assert manager.get_project(id1).is_active is False
        assert manager.get_project(id2).is_active is True
    
    def test_get_active_project(self, manager):
        """Test getting the active project."""
        project_id = manager.create_project(name="Test Project")
        manager.set_active_project(project_id)
        
        active = manager.get_active_project()
        
        assert active is not None
        assert active.project_id == project_id
        assert active.is_active is True
    
    def test_get_active_project_when_none(self, manager):
        """Test getting active project when none is set."""
        active = manager.get_active_project()
        assert active is None
    
    def test_delete_active_project_switches_to_another(self, manager):
        """Test that deleting active project switches to another."""
        id1 = manager.create_project(name="Project 1")
        id2 = manager.create_project(name="Project 2")
        
        manager.set_active_project(id1)
        manager.delete_project(id1)
        
        # Should have switched to project 2
        assert manager.active_project_id == id2
        assert manager.get_project(id2).is_active is True
    
    def test_get_project_count(self, manager):
        """Test getting the project count."""
        assert manager.get_project_count() == 0
        
        manager.create_project(name="Project 1")
        assert manager.get_project_count() == 1
        
        manager.create_project(name="Project 2")
        assert manager.get_project_count() == 2
    
    def test_find_projects_by_name(self, manager):
        """Test finding projects by name."""
        manager.create_project(name="AI Project 1")
        manager.create_project(name="AI Project 2")
        manager.create_project(name="Web Project")
        
        ai_projects = manager.find_projects_by_name("AI")
        assert len(ai_projects) == 2
        
        web_projects = manager.find_projects_by_name("Web")
        assert len(web_projects) == 1
        
        all_projects = manager.find_projects_by_name("Project")
        assert len(all_projects) == 3
    
    def test_memory_session_integration(self, manager):
        """Test memory session ID management."""
        project_id = manager.create_project(name="Test Project")
        
        # Set memory session ID
        session_id = "test-session-123"
        success = manager.set_project_memory_session_id(project_id, session_id)
        
        assert success is True
        
        # Get memory session ID
        retrieved_session_id = manager.get_project_memory_session_id(project_id)
        assert retrieved_session_id == session_id
    
    def test_get_project_storage_path(self, manager):
        """Test getting project storage path."""
        project_id = manager.create_project(name="Test Project")
        
        storage_path = manager.get_project_storage_path(project_id)
        
        assert storage_path is not None
        assert isinstance(storage_path, Path)
        assert storage_path.exists()
        assert storage_path.is_dir()
    
    def test_persistence_save_and_load(self, manager, temp_dir):
        """Test saving and loading projects."""
        # Create a project
        project_id = manager.create_project(
            name="Test Project",
            description="Test description"
        )
        manager.set_active_project(project_id)
        
        # Verify file was created
        project_file = temp_dir / f"{project_id}.json"
        assert project_file.exists()
        
        # Create new manager and load
        new_manager = ProjectManager(
            storage_path=temp_dir,
            auto_save=False,
            create_default_project=False
        )
        
        # Should have loaded the project
        assert len(new_manager.projects) == 1
        assert project_id in new_manager.projects
        
        loaded_project = new_manager.get_project(project_id)
        assert loaded_project.name == "Test Project"
        assert loaded_project.description == "Test description"
        assert loaded_project.is_active is True
        assert new_manager.active_project_id == project_id
    
    def test_export_project(self, manager, temp_dir):
        """Test exporting a project."""
        project_id = manager.create_project(name="Test Project")
        export_path = temp_dir / "export.json"
        
        success = manager.export_project(project_id, export_path)
        
        assert success is True
        assert export_path.exists()
        
        # Verify export content
        with open(export_path, 'r') as f:
            data = json.load(f)
        
        assert data['project_id'] == project_id
        assert data['name'] == "Test Project"
    
    def test_import_project(self, manager, temp_dir):
        """Test importing a project."""
        # Create an export file
        export_data = {
            'project_id': 'imported-id',
            'name': 'Imported Project',
            'description': 'Imported from file',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'metadata': {'source': 'import'},
            'memory_session_id': None,
            'is_active': False
        }
        
        import_path = temp_dir / "import.json"
        with open(import_path, 'w') as f:
            json.dump(export_data, f)
        
        # Import the project
        project_id = manager.import_project(import_path)
        
        assert project_id is not None
        assert project_id in manager.projects
        
        project = manager.get_project(project_id)
        assert project.name == 'Imported Project'
        assert project.description == 'Imported from file'
        assert project.metadata == {'source': 'import'}
        assert project.is_active is False  # Should not be active on import
    
    def test_import_project_with_id_conflict(self, manager, temp_dir):
        """Test importing a project when ID already exists."""
        # Create a project
        existing_id = manager.create_project(name="Existing Project")
        
        # Try to import with same ID
        export_data = {
            'project_id': existing_id,
            'name': 'Conflicting Project',
            'description': 'Should get new ID',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'metadata': {},
            'memory_session_id': None,
            'is_active': False
        }
        
        import_path = temp_dir / "conflict.json"
        with open(import_path, 'w') as f:
            json.dump(export_data, f)
        
        # Import should succeed with new ID
        imported_id = manager.import_project(import_path)
        
        assert imported_id is not None
        assert imported_id != existing_id  # Should have generated new ID
        assert len(manager.projects) == 2
    
    def test_default_project_creation(self, temp_dir):
        """Test that default project is created if none exist."""
        manager = ProjectManager(
            storage_path=temp_dir,
            auto_save=False,
            create_default_project=True
        )
        
        assert len(manager.projects) == 1
        assert manager.active_project_id is not None
        
        active = manager.get_active_project()
        assert active is not None
        assert "Default Project" in active.name
    
    def test_len_and_repr(self, manager):
        """Test __len__ and __repr__ methods."""
        assert len(manager) == 0
        
        manager.create_project(name="Project 1")
        assert len(manager) == 1
        
        manager.create_project(name="Project 2")
        assert len(manager) == 2
        
        # Test repr
        repr_str = repr(manager)
        assert "ProjectManager" in repr_str
        assert "projects=2" in repr_str
