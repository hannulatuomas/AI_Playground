"""
Unit tests for ImportantFilesManager.

Tests for managing important project documentation files.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch
import yaml

from utils.important_files_manager import (
    ImportantFilesManager,
    get_manager,
    get_important_files,
    get_required_files,
    get_init_files,
    get_file_template,
    export_checklist
)


class TestImportantFilesManagerInitialization:
    """Tests for ImportantFilesManager initialization."""
    
    @pytest.fixture
    def temp_config(self):
        """Create a temporary config file."""
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "important_project_files.yaml"
        
        config_data = {
            'core_documentation': [
                {
                    'name': 'README.md',
                    'description': 'Project overview',
                    'required': True,
                    'location': 'root'
                },
                {
                    'name': 'VERSION',
                    'description': 'Version file',
                    'required': True,
                    'location': 'root'
                }
            ],
            'auto_update_settings': {
                'create_on_init': ['README.md', 'VERSION'],
                'update_priorities': {
                    'critical': ['README.md', 'VERSION']
                }
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        yield config_path
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_initialization_with_config_path(self, temp_config):
        """Test initialization with explicit config path."""
        manager = ImportantFilesManager(config_path=temp_config)
        
        assert manager.config_path == temp_config
        assert manager.config is not None
        assert 'core_documentation' in manager.config
    
    def test_initialization_default_config(self):
        """Test initialization with auto-detected config path."""
        manager = ImportantFilesManager()
        
        assert manager.config is not None
        # Should have loaded default config or actual config
        assert isinstance(manager.config, dict)
    
    def test_load_config_success(self, temp_config):
        """Test successful config loading."""
        manager = ImportantFilesManager(config_path=temp_config)
        
        assert 'core_documentation' in manager.config
        assert len(manager.config['core_documentation']) == 2
    
    def test_load_config_failure_uses_default(self):
        """Test that default config is used when loading fails."""
        invalid_path = Path("/nonexistent/config.yaml")
        manager = ImportantFilesManager(config_path=invalid_path)
        
        # Should use default config
        assert manager.config is not None
        assert 'core_documentation' in manager.config


class TestGetAllImportantFiles:
    """Tests for get_all_important_files method."""
    
    @pytest.fixture
    def manager(self, temp_config):
        """Create a manager instance."""
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "config.yaml"
        
        config_data = {
            'core_documentation': [
                {'name': 'README.md', 'required': True, 'location': 'root'},
                {'name': 'CHANGELOG.md', 'required': True, 'location': 'root'}
            ],
            'planning_files': [
                {'name': 'TODO.md', 'required': False, 'location': 'root'}
            ]
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ImportantFilesManager(config_path=config_path)
        yield manager
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_all_files(self, manager):
        """Test getting all important files."""
        files = manager.get_all_important_files()
        
        assert len(files) == 3
        assert all('category' in f for f in files)
        
        file_names = [f['name'] for f in files]
        assert 'README.md' in file_names
        assert 'CHANGELOG.md' in file_names
        assert 'TODO.md' in file_names
    
    def test_files_have_category(self, manager):
        """Test that files have category assigned."""
        files = manager.get_all_important_files()
        
        for file_def in files:
            assert 'category' in file_def
            assert file_def['category'] in ['core_documentation', 'planning_files']


class TestGetRequiredFiles:
    """Tests for get_required_files method."""
    
    @pytest.fixture
    def manager(self):
        """Create a manager instance."""
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "config.yaml"
        
        config_data = {
            'core_documentation': [
                {'name': 'README.md', 'required': True},
                {'name': 'VERSION', 'required': True},
                {'name': 'TODO.md', 'required': False}
            ]
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ImportantFilesManager(config_path=config_path)
        yield manager
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_required_files_only(self, manager):
        """Test getting only required files."""
        required = manager.get_required_files()
        
        assert len(required) == 2
        assert 'README.md' in required
        assert 'VERSION' in required
        assert 'TODO.md' not in required


class TestGetFilesToCreateOnInit:
    """Tests for get_files_to_create_on_init method."""
    
    @pytest.fixture
    def manager(self):
        """Create a manager instance."""
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "config.yaml"
        
        config_data = {
            'auto_update_settings': {
                'create_on_init': ['README.md', 'VERSION', 'TODO.md']
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ImportantFilesManager(config_path=config_path)
        yield manager
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_init_files(self, manager):
        """Test getting files to create on init."""
        init_files = manager.get_files_to_create_on_init()
        
        assert len(init_files) == 3
        assert 'README.md' in init_files
        assert 'VERSION' in init_files
        assert 'TODO.md' in init_files


class TestGetFilesByCategory:
    """Tests for get_files_by_category method."""
    
    @pytest.fixture
    def manager(self):
        """Create a manager instance."""
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "config.yaml"
        
        config_data = {
            'core_documentation': [
                {'name': 'README.md'},
                {'name': 'CHANGELOG.md'}
            ],
            'planning_files': [
                {'name': 'TODO.md'}
            ]
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ImportantFilesManager(config_path=config_path)
        yield manager
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_core_documentation_files(self, manager):
        """Test getting core documentation files."""
        files = manager.get_files_by_category('core_documentation')
        
        assert len(files) == 2
        assert files[0]['name'] == 'README.md'
        assert files[1]['name'] == 'CHANGELOG.md'
    
    def test_get_planning_files(self, manager):
        """Test getting planning files."""
        files = manager.get_files_by_category('planning_files')
        
        assert len(files) == 1
        assert files[0]['name'] == 'TODO.md'
    
    def test_get_nonexistent_category(self, manager):
        """Test getting files from nonexistent category."""
        files = manager.get_files_by_category('nonexistent')
        
        assert files == []


class TestGetFilesByPriority:
    """Tests for get_files_by_priority method."""
    
    @pytest.fixture
    def manager(self):
        """Create a manager instance."""
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "config.yaml"
        
        config_data = {
            'auto_update_settings': {
                'update_priorities': {
                    'critical': ['README.md', 'VERSION'],
                    'high': ['CHANGELOG.md'],
                    'medium': ['TODO.md']
                }
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ImportantFilesManager(config_path=config_path)
        yield manager
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_critical_files(self, manager):
        """Test getting critical priority files."""
        critical = manager.get_files_by_priority('critical')
        
        assert len(critical) == 2
        assert 'README.md' in critical
        assert 'VERSION' in critical
    
    def test_get_high_priority_files(self, manager):
        """Test getting high priority files."""
        high = manager.get_files_by_priority('high')
        
        assert len(high) == 1
        assert 'CHANGELOG.md' in high
    
    def test_get_nonexistent_priority(self, manager):
        """Test getting files with nonexistent priority."""
        files = manager.get_files_by_priority('nonexistent')
        
        assert files == []
    
    def test_get_critical_files_helper(self, manager):
        """Test get_critical_files helper method."""
        critical = manager.get_critical_files()
        
        assert len(critical) == 2
        assert 'README.md' in critical


class TestGetFileTemplate:
    """Tests for get_file_template method."""
    
    @pytest.fixture
    def manager(self):
        """Create a manager instance."""
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "config.yaml"
        
        config_data = {
            'minimal_templates': {
                'README.md': '# {{project_name}}\n\nCreated: {{date}}',
                'VERSION': '{{version}}'
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ImportantFilesManager(config_path=config_path)
        yield manager
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_template_with_substitution(self, manager):
        """Test getting template with variable substitution."""
        template = manager.get_file_template(
            'README.md',
            project_name='My Project'
        )
        
        assert 'My Project' in template
        assert '{{project_name}}' not in template
        # Date should be auto-substituted
        assert '{{date}}' not in template
    
    def test_get_template_with_version(self, manager):
        """Test getting VERSION template."""
        template = manager.get_file_template('VERSION', version='1.0.0')
        
        assert template == '1.0.0'
    
    def test_get_nonexistent_template(self, manager):
        """Test getting template for file without template."""
        template = manager.get_file_template('NONEXISTENT.md')
        
        assert template is None


class TestGetFileLocation:
    """Tests for get_file_location method."""
    
    @pytest.fixture
    def manager(self):
        """Create a manager instance."""
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "config.yaml"
        
        config_data = {
            'core_documentation': [
                {'name': 'README.md', 'location': 'root'},
                {'name': 'ARCHITECTURE.md', 'location': 'docs'}
            ]
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ImportantFilesManager(config_path=config_path)
        yield manager
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_root_location(self, manager):
        """Test getting location for root file."""
        location = manager.get_file_location('README.md')
        
        assert location == 'root'
    
    def test_get_docs_location(self, manager):
        """Test getting location for docs file."""
        location = manager.get_file_location('ARCHITECTURE.md')
        
        assert location == 'docs'
    
    def test_get_location_nonexistent_file(self, manager):
        """Test getting location for nonexistent file."""
        location = manager.get_file_location('NONEXISTENT.md')
        
        assert location is None


class TestGetFileInfo:
    """Tests for get_file_info method."""
    
    @pytest.fixture
    def manager(self):
        """Create a manager instance."""
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "config.yaml"
        
        config_data = {
            'core_documentation': [
                {
                    'name': 'README.md',
                    'description': 'Project overview',
                    'required': True,
                    'location': 'root',
                    'update_frequency': 'as_needed'
                }
            ]
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ImportantFilesManager(config_path=config_path)
        yield manager
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_file_info_complete(self, manager):
        """Test getting complete file info."""
        info = manager.get_file_info('README.md')
        
        assert info is not None
        assert info['name'] == 'README.md'
        assert info['description'] == 'Project overview'
        assert info['required'] is True
        assert info['location'] == 'root'
        assert info['update_frequency'] == 'as_needed'
    
    def test_get_file_info_nonexistent(self, manager):
        """Test getting info for nonexistent file."""
        info = manager.get_file_info('NONEXISTENT.md')
        
        assert info is None


class TestShouldUpdateFile:
    """Tests for should_update_file method."""
    
    @pytest.fixture
    def manager(self):
        """Create a manager instance."""
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "config.yaml"
        
        config_data = {
            'core_documentation': [
                {'name': 'README.md', 'update_frequency': 'every_major_change'},
                {'name': 'CHANGELOG.md', 'update_frequency': 'every_version'},
                {'name': 'TODO.md', 'update_frequency': 'as_needed'}
            ],
            'auto_update_settings': {
                'trigger_events': [
                    'project_initialization',
                    'major_feature_addition',
                    'version_bump',
                    'architecture_change'
                ]
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ImportantFilesManager(config_path=config_path)
        yield manager
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_should_update_on_major_change(self, manager):
        """Test file should update on major change."""
        last_update = datetime.now()
        should_update = manager.should_update_file(
            'README.md',
            last_update,
            'major_feature_addition'
        )
        
        assert should_update is True
    
    def test_should_update_on_version_bump(self, manager):
        """Test file should update on version bump."""
        last_update = datetime.now()
        should_update = manager.should_update_file(
            'CHANGELOG.md',
            last_update,
            'version_bump'
        )
        
        assert should_update is True
    
    def test_should_not_update_wrong_event(self, manager):
        """Test file should not update on wrong event."""
        last_update = datetime.now()
        should_update = manager.should_update_file(
            'CHANGELOG.md',
            last_update,
            'nonexistent_event'
        )
        
        assert should_update is False


class TestGetResponsibleAgents:
    """Tests for get_responsible_agents method."""
    
    @pytest.fixture
    def manager(self):
        """Create a manager instance."""
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "config.yaml"
        
        config_data = {
            'auto_update_settings': {
                'responsible_agents': [
                    'documentation_agent',
                    'project_init_agent'
                ]
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ImportantFilesManager(config_path=config_path)
        yield manager
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_responsible_agents(self, manager):
        """Test getting responsible agents."""
        agents = manager.get_responsible_agents()
        
        assert len(agents) == 2
        assert 'documentation_agent' in agents
        assert 'project_init_agent' in agents


class TestExportChecklist:
    """Tests for export_checklist method."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        
        # Create some files
        (Path(temp_dir) / 'README.md').write_text('# Test')
        (Path(temp_dir) / 'docs').mkdir()
        (Path(temp_dir) / 'docs' / 'ARCHITECTURE.md').write_text('# Architecture')
        
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def manager(self):
        """Create a manager instance."""
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "config.yaml"
        
        config_data = {
            'core_documentation': [
                {
                    'name': 'README.md',
                    'description': 'Project overview',
                    'required': True,
                    'location': 'root'
                },
                {
                    'name': 'VERSION',
                    'description': 'Version file',
                    'required': True,
                    'location': 'root'
                }
            ],
            'technical_documentation': [
                {
                    'name': 'ARCHITECTURE.md',
                    'description': 'Architecture overview',
                    'required': False,
                    'location': 'docs'
                }
            ]
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        manager = ImportantFilesManager(config_path=config_path)
        yield manager
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_export_checklist_format(self, manager, temp_project):
        """Test checklist export format."""
        checklist = manager.export_checklist(Path(temp_project))
        
        assert '# Important Project Files Checklist' in checklist
        assert 'Project:' in checklist
        assert 'Generated:' in checklist
    
    def test_export_checklist_shows_existing_files(self, manager, temp_project):
        """Test checklist shows existing files."""
        checklist = manager.export_checklist(Path(temp_project))
        
        # README.md exists
        assert '[x] README.md' in checklist
        # VERSION doesn't exist
        assert '[ ] VERSION' in checklist
    
    def test_export_checklist_shows_required_marker(self, manager, temp_project):
        """Test checklist shows required marker."""
        checklist = manager.export_checklist(Path(temp_project))
        
        assert '**[REQUIRED]**' in checklist


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_get_manager_singleton(self):
        """Test that get_manager returns singleton."""
        manager1 = get_manager()
        manager2 = get_manager()
        
        assert manager1 is manager2
    
    def test_get_important_files_convenience(self):
        """Test get_important_files convenience function."""
        files = get_important_files()
        
        assert isinstance(files, list)
    
    def test_get_required_files_convenience(self):
        """Test get_required_files convenience function."""
        required = get_required_files()
        
        assert isinstance(required, list)
    
    def test_get_init_files_convenience(self):
        """Test get_init_files convenience function."""
        init_files = get_init_files()
        
        assert isinstance(init_files, list)
    
    def test_get_file_template_convenience(self):
        """Test get_file_template convenience function."""
        # May return None if template doesn't exist
        template = get_file_template('README.md', project_name='Test')
        
        # Just check it doesn't raise an error
        assert template is None or isinstance(template, str)
    
    def test_export_checklist_convenience(self):
        """Test export_checklist convenience function."""
        temp_dir = tempfile.mkdtemp()
        try:
            checklist = export_checklist(Path(temp_dir))
            
            assert isinstance(checklist, str)
            assert '# Important Project Files Checklist' in checklist
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_config(self):
        """Test handling of empty config."""
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "config.yaml"
        
        with open(config_path, 'w') as f:
            f.write('')
        
        try:
            manager = ImportantFilesManager(config_path=config_path)
            
            # Should use default config
            assert manager.config is not None
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_malformed_config(self):
        """Test handling of malformed config."""
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "config.yaml"
        
        with open(config_path, 'w') as f:
            f.write('invalid: yaml: content: [')
        
        try:
            manager = ImportantFilesManager(config_path=config_path)
            
            # Should use default config
            assert manager.config is not None
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
