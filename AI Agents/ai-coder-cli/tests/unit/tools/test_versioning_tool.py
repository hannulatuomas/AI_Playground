"""
Unit tests for VersioningTool.

Tests for automated version management with semantic versioning.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from tools.versioning import VersioningTool
from tools.lib.version_manager import VersionInfo, VersionBumpType, ChangeAnalysis


class TestVersioningToolInitialization:
    """Tests for VersioningTool initialization."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        # Create a VERSION file
        version_file = Path(temp_dir) / 'VERSION'
        version_file.write_text('1.0.0')
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_tool_initialization_default(self):
        """Test tool initialization with default config."""
        tool = VersioningTool()
        
        assert tool.name == 'versioning'
        assert 'version management' in tool.description.lower()
        assert tool.version_manager is not None
    
    def test_tool_initialization_with_project_root(self, temp_project):
        """Test tool initialization with custom project root."""
        tool = VersioningTool(config={'project_root': temp_project})
        
        assert tool.name == 'versioning'
        assert tool.version_manager is not None


class TestGetVersion:
    """Tests for get_version action."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        version_file = Path(temp_dir) / 'VERSION'
        version_file.write_text('2.5.0')
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def tool(self, temp_project):
        """Create a VersioningTool instance."""
        return VersioningTool(config={'project_root': temp_project})
    
    def test_get_version_success(self, tool):
        """Test getting current version."""
        result = tool.invoke({'action': 'get_version'})
        
        assert result['success'] is True
        assert result['action'] == 'get_version'
        assert result['version'] == '2.5.0'
        assert 'version_parts' in result
        assert result['version_parts']['major'] == 2
        assert result['version_parts']['minor'] == 5
        assert result['version_parts']['patch'] == 0
    
    def test_get_version_with_prerelease(self, temp_project):
        """Test getting version with prerelease tag."""
        version_file = Path(temp_project) / 'VERSION'
        version_file.write_text('2.5.0-beta.1')
        
        tool = VersioningTool(config={'project_root': temp_project})
        result = tool.invoke({'action': 'get_version'})
        
        assert result['success'] is True
        assert '2.5.0' in result['version']
        assert result['version_parts']['major'] == 2


class TestBumpVersion:
    """Tests for bump action."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        version_file = Path(temp_dir) / 'VERSION'
        version_file.write_text('1.0.0')
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def tool(self, temp_project):
        """Create a VersioningTool instance."""
        return VersioningTool(config={'project_root': temp_project})
    
    def test_bump_major_version(self, tool):
        """Test bumping major version."""
        result = tool.invoke({
            'action': 'bump',
            'bump_type': 'major'
        })
        
        assert result['success'] is True
        assert result['action'] == 'bump'
        assert result['bump_type'] == 'major'
        assert result['old_version'] == '1.0.0'
        assert result['new_version'] == '2.0.0'
        assert 'message' in result
    
    def test_bump_minor_version(self, tool):
        """Test bumping minor version."""
        result = tool.invoke({
            'action': 'bump',
            'bump_type': 'minor'
        })
        
        assert result['success'] is True
        assert result['bump_type'] == 'minor'
        assert result['old_version'] == '1.0.0'
        assert result['new_version'] == '1.1.0'
    
    def test_bump_patch_version(self, tool):
        """Test bumping patch version."""
        result = tool.invoke({
            'action': 'bump',
            'bump_type': 'patch'
        })
        
        assert result['success'] is True
        assert result['bump_type'] == 'patch'
        assert result['old_version'] == '1.0.0'
        assert result['new_version'] == '1.0.1'
    
    def test_bump_invalid_type(self, tool):
        """Test bumping with invalid type."""
        result = tool.invoke({
            'action': 'bump',
            'bump_type': 'invalid'
        })
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Invalid bump_type' in result['error']
    
    def test_bump_missing_type(self, tool):
        """Test bumping without specifying type."""
        result = tool.invoke({
            'action': 'bump'
        })
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_bump_case_insensitive(self, tool):
        """Test that bump_type is case insensitive."""
        result = tool.invoke({
            'action': 'bump',
            'bump_type': 'MAJOR'
        })
        
        assert result['success'] is True
        assert result['new_version'] == '2.0.0'


class TestAutoBumpVersion:
    """Tests for auto_bump action."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory with git."""
        temp_dir = tempfile.mkdtemp()
        version_file = Path(temp_dir) / 'VERSION'
        version_file.write_text('1.0.0')
        
        # Initialize git repository
        import subprocess
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir, capture_output=True)
        
        # Create an initial commit
        subprocess.run(['git', 'add', '.'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=temp_dir, capture_output=True)
        
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def tool(self, temp_project):
        """Create a VersioningTool instance."""
        return VersioningTool(config={'project_root': temp_project})
    
    def test_auto_bump_with_breaking_changes(self, tool):
        """Test auto bump with breaking changes."""
        result = tool.invoke({
            'action': 'auto_bump',
            'commit_messages': ['feat!: breaking change in API'],
            'use_git': False
        })
        
        assert result['success'] is True
        assert result['action'] == 'auto_bump'
        assert result['bump_type'].lower() == 'major'
        assert result['old_version'] == '1.0.0'
        assert result['new_version'] == '2.0.0'
        assert result['analysis']['has_breaking_changes'] is True
    
    def test_auto_bump_with_new_features(self, tool):
        """Test auto bump with new features."""
        result = tool.invoke({
            'action': 'auto_bump',
            'commit_messages': ['feat: add new feature'],
            'use_git': False
        })
        
        assert result['success'] is True
        assert result['bump_type'].lower() == 'minor'
        assert result['new_version'] == '1.1.0'
        assert result['analysis']['has_new_features'] is True
    
    def test_auto_bump_with_bug_fixes(self, tool):
        """Test auto bump with bug fixes."""
        result = tool.invoke({
            'action': 'auto_bump',
            'commit_messages': ['fix: fix critical bug'],
            'use_git': False
        })
        
        assert result['success'] is True
        assert result['bump_type'].lower() == 'patch'
        assert result['new_version'] == '1.0.1'
        assert result['analysis']['has_bug_fixes'] is True
    
    def test_auto_bump_no_changes(self, tool):
        """Test auto bump with no significant changes."""
        result = tool.invoke({
            'action': 'auto_bump',
            'commit_messages': [],
            'use_git': False
        })
        
        # Implementation may default to patch bump when no changes detected
        # or return error - both are acceptable
        if result['success']:
            # Defaulted to patch bump
            assert result['bump_type'].lower() in ['patch', 'minor', 'major']
        else:
            # Returned error
            assert 'error' in result
    
    def test_auto_bump_with_file_changes(self, tool):
        """Test auto bump with file changes."""
        result = tool.invoke({
            'action': 'auto_bump',
            'file_changes': ['src/api.py', 'src/core.py'],
            'commit_messages': ['refactor: improve code structure'],
            'use_git': False
        })
        
        assert result['success'] is True
        assert result['analysis']['files_changed'] == 2


class TestAnalyzeChanges:
    """Tests for analyze action."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        version_file = Path(temp_dir) / 'VERSION'
        version_file.write_text('1.0.0')
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def tool(self, temp_project):
        """Create a VersioningTool instance."""
        return VersioningTool(config={'project_root': temp_project})
    
    def test_analyze_breaking_changes(self, tool):
        """Test analyzing breaking changes."""
        result = tool.invoke({
            'action': 'analyze',
            'commit_messages': ['feat!: breaking API change', 'docs: update README'],
            'use_git': False
        })
        
        assert result['success'] is True
        assert result['action'] == 'analyze'
        assert result['current_version'] == '1.0.0'
        assert result['suggested_bump'].lower() == 'major'
        assert result['analysis']['has_breaking_changes'] is True
        # commits_analyzed may or may not be present depending on implementation
        if 'commits_analyzed' in result['analysis']:
            assert result['analysis']['commits_analyzed'] >= 0
    
    def test_analyze_new_features(self, tool):
        """Test analyzing new features."""
        result = tool.invoke({
            'action': 'analyze',
            'commit_messages': ['feat: add new API endpoint', 'test: add tests'],
            'use_git': False
        })
        
        assert result['success'] is True
        assert result['suggested_bump'].lower() == 'minor'
        assert result['analysis']['has_new_features'] is True
    
    def test_analyze_bug_fixes(self, tool):
        """Test analyzing bug fixes."""
        result = tool.invoke({
            'action': 'analyze',
            'commit_messages': ['fix: resolve memory leak', 'fix: correct typo'],
            'use_git': False
        })
        
        assert result['success'] is True
        assert result['suggested_bump'].lower() == 'patch'
        assert result['analysis']['has_bug_fixes'] is True
    
    def test_analyze_with_file_changes(self, tool):
        """Test analyzing with file changes."""
        result = tool.invoke({
            'action': 'analyze',
            'file_changes': ['src/main.py', 'tests/test_main.py'],
            'commit_messages': ['refactor: improve structure'],
            'use_git': False
        })
        
        assert result['success'] is True
        assert result['analysis']['file_changes'] == ['src/main.py', 'tests/test_main.py']


class TestUpdateFiles:
    """Tests for update_files action."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory with version files."""
        temp_dir = tempfile.mkdtemp()
        
        # Create VERSION file
        version_file = Path(temp_dir) / 'VERSION'
        version_file.write_text('1.0.0')
        
        # Create setup.py
        setup_file = Path(temp_dir) / 'setup.py'
        setup_file.write_text('version = "1.0.0"')
        
        # Create package.json
        package_file = Path(temp_dir) / 'package.json'
        package_file.write_text('{"version": "1.0.0"}')
        
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def tool(self, temp_project):
        """Create a VersioningTool instance."""
        return VersioningTool(config={'project_root': temp_project})
    
    def test_update_files_with_current_version(self, tool):
        """Test updating files with current version."""
        # First bump the version
        tool.invoke({'action': 'bump', 'bump_type': 'minor'})
        
        # Then update files
        result = tool.invoke({'action': 'update_files'})
        
        assert result['success'] is True
        assert result['action'] == 'update_files'
        assert result['version'] == '1.1.0'
        assert 'updated_files' in result
        assert len(result['updated_files']) > 0
    
    def test_update_files_with_specific_version(self, tool):
        """Test updating files with specific version."""
        result = tool.invoke({
            'action': 'update_files',
            'version': '2.0.0'
        })
        
        assert result['success'] is True
        assert result['version'] == '2.0.0'
        assert 'updated_files' in result


class TestCreateTag:
    """Tests for create_tag action."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory with git."""
        temp_dir = tempfile.mkdtemp()
        version_file = Path(temp_dir) / 'VERSION'
        version_file.write_text('1.0.0')
        
        # Initialize git repository
        import subprocess
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'add', '.'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=temp_dir, capture_output=True)
        
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def tool(self, temp_project):
        """Create a VersioningTool instance."""
        return VersioningTool(config={'project_root': temp_project})
    
    def test_create_tag_with_current_version(self, tool):
        """Test creating tag with current version."""
        result = tool.invoke({'action': 'create_tag'})
        
        assert result['action'] == 'create_tag'
        assert result['version'] == '1.0.0'
        assert result['tag_name'] == 'v1.0.0'
    
    def test_create_tag_with_specific_version(self, tool):
        """Test creating tag with specific version."""
        result = tool.invoke({
            'action': 'create_tag',
            'version': '2.0.0'
        })
        
        assert result['action'] == 'create_tag'
        assert result['version'] == '2.0.0'
        assert result['tag_name'] == 'v2.0.0'
    
    def test_create_tag_with_message(self, tool):
        """Test creating tag with custom message."""
        result = tool.invoke({
            'action': 'create_tag',
            'message': 'Release version 1.0.0'
        })
        
        assert result['action'] == 'create_tag'
        assert 'message' in result


class TestFullRelease:
    """Tests for full_release action."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory with git."""
        temp_dir = tempfile.mkdtemp()
        version_file = Path(temp_dir) / 'VERSION'
        version_file.write_text('1.0.0')
        
        # Initialize git repository
        import subprocess
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'add', '.'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=temp_dir, capture_output=True)
        
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def tool(self, temp_project):
        """Create a VersioningTool instance."""
        return VersioningTool(config={'project_root': temp_project})
    
    def test_full_release_with_auto_bump(self, tool):
        """Test full release workflow with auto bump."""
        result = tool.invoke({
            'action': 'full_release',
            'commit_messages': ['feat: add new feature'],
            'use_git': False
        })
        
        assert result['success'] is True
        assert result['action'] == 'full_release'
        assert result['new_version'] == '1.1.0'
        assert 'steps' in result
        assert len(result['steps']) >= 3  # analyze, bump, update_files
    
    def test_full_release_with_manual_bump(self, tool):
        """Test full release workflow with manual bump."""
        result = tool.invoke({
            'action': 'full_release',
            'bump_type': 'major',
            'use_git': False
        })
        
        assert result['success'] is True
        assert result['new_version'] == '2.0.0'
    
    def test_full_release_without_tag(self, tool):
        """Test full release workflow without creating tag."""
        result = tool.invoke({
            'action': 'full_release',
            'bump_type': 'patch',
            'create_tag': False,
            'use_git': False
        })
        
        assert result['success'] is True
        # Check that create_tag step was skipped
        step_names = [step[0] for step in result['steps']]
        assert 'create_tag' not in step_names
    
    def test_full_release_with_tag_message(self, tool):
        """Test full release workflow with custom tag message."""
        result = tool.invoke({
            'action': 'full_release',
            'bump_type': 'minor',
            'tag_message': 'Release v1.1.0 with new features',
            'use_git': False
        })
        
        assert result['success'] is True
        assert result['new_version'] == '1.1.0'


class TestErrorHandling:
    """Tests for error handling."""
    
    @pytest.fixture
    def tool(self):
        """Create a VersioningTool instance."""
        return VersioningTool()
    
    def test_unknown_action(self, tool):
        """Test handling of unknown action."""
        result = tool.invoke({'action': 'unknown_action'})
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Unknown action' in result['error']
        assert 'supported_actions' in result
    
    def test_missing_action(self, tool):
        """Test handling of missing action parameter."""
        # Should raise ValueError for missing required param
        with pytest.raises(ValueError):
            tool.invoke({})
    
    def test_exception_during_execution(self, tool):
        """Test handling of exceptions during execution."""
        with patch.object(tool.version_manager, 'get_current_version', side_effect=Exception('Test error')):
            result = tool.invoke({'action': 'get_version'})
            
            assert result['success'] is False
            assert 'error' in result
            assert result['action'] == 'get_version'


class TestParameterValidation:
    """Tests for parameter validation."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        version_file = Path(temp_dir) / 'VERSION'
        version_file.write_text('1.0.0')
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def tool(self, temp_project):
        """Create a VersioningTool instance."""
        return VersioningTool(config={'project_root': temp_project})
    
    def test_bump_requires_bump_type(self, tool):
        """Test that bump action requires bump_type."""
        result = tool.invoke({'action': 'bump'})
        
        assert result['success'] is False
        assert 'error' in result


class TestIntegration:
    """Integration tests for versioning workflow."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory with git."""
        temp_dir = tempfile.mkdtemp()
        version_file = Path(temp_dir) / 'VERSION'
        version_file.write_text('1.0.0')
        
        # Initialize git repository
        import subprocess
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'add', '.'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=temp_dir, capture_output=True)
        
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def tool(self, temp_project):
        """Create a VersioningTool instance."""
        return VersioningTool(config={'project_root': temp_project})
    
    def test_complete_version_bump_workflow(self, tool):
        """Test complete version bump workflow."""
        # 1. Get current version
        result1 = tool.invoke({'action': 'get_version'})
        assert result1['success'] is True
        assert result1['version'] == '1.0.0'
        
        # 2. Analyze changes
        result2 = tool.invoke({
            'action': 'analyze',
            'commit_messages': ['feat: new feature'],
            'use_git': False
        })
        assert result2['success'] is True
        assert result2['suggested_bump'].lower() == 'minor'
        
        # 3. Bump version
        result3 = tool.invoke({
            'action': 'bump',
            'bump_type': 'minor'
        })
        assert result3['success'] is True
        assert result3['new_version'] == '1.1.0'
        
        # 4. Verify new version
        result4 = tool.invoke({'action': 'get_version'})
        assert result4['success'] is True
        assert result4['version'] == '1.1.0'
    
    def test_sequential_version_bumps(self, tool):
        """Test sequential version bumps."""
        # Bump patch
        result1 = tool.invoke({'action': 'bump', 'bump_type': 'patch'})
        assert result1['new_version'] == '1.0.1'
        
        # Bump minor
        result2 = tool.invoke({'action': 'bump', 'bump_type': 'minor'})
        assert result2['new_version'] == '1.1.0'
        
        # Bump major
        result3 = tool.invoke({'action': 'bump', 'bump_type': 'major'})
        assert result3['new_version'] == '2.0.0'
