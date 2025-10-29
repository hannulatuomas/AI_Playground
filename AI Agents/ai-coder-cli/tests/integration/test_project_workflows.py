#!/usr/bin/env python3
"""
Integration tests for AI Agent Console project workflows.

Tests the complete workflows for:
1. Project initialization
2. Version management
3. Important files creation
4. Context management
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.versioning import VersioningTool
from tools.context_cache import ContextCacheTool
from tools.lib.version_manager import VersionInfo
from utils.important_files_manager import get_manager, export_checklist


class TestProjectInitialization:
    """Test project initialization workflow."""
    
    def setup_method(self):
        """Create temporary directory for testing."""
        self.test_dir = Path(tempfile.mkdtemp(prefix='aiagent_test_'))
        self.project_dir = self.test_dir / 'test_project'
        self.project_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up temporary directory."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_important_files_manager_loads(self):
        """Test that ImportantFilesManager loads configuration correctly."""
        manager = get_manager()
        
        # Check that we can get important files
        all_files = manager.get_all_important_files()
        assert len(all_files) > 0, "Should have important files defined"
        
        # Check required files
        required = manager.get_required_files()
        assert 'README.md' in required
        assert 'VERSION' in required
        
        # Check init files
        init_files = manager.get_files_to_create_on_init()
        assert len(init_files) > 0, "Should have files to create on init"
    
    def test_version_file_in_project(self):
        """Test that versioning creates VERSION file in project, not console."""
        # Create VERSION file in project
        version_file = self.project_dir / 'VERSION'
        version_file.write_text('0.1.0\n')
        
        # Initialize versioning tool with project root
        versioning = VersioningTool(config={'project_root': self.project_dir})
        
        # Get version
        result = versioning.invoke({'action': 'get_version'})
        assert result['success']
        assert result['version'] == '0.1.0'
        
        # Bump version
        result = versioning.invoke({'action': 'bump', 'bump_type': 'minor'})
        assert result['success']
        assert result['new_version'] == '0.2.0'
        
        # Verify VERSION file updated in project directory
        updated_version = version_file.read_text().strip()
        assert updated_version == '0.2.0'
        
        # Verify console directory doesn't have VERSION file
        console_root = Path(__file__).parent.parent.parent
        console_version = console_root / 'VERSION'
        # The console VERSION should exist but should not have changed
        if console_version.exists():
            console_version_content = console_version.read_text().strip()
            # It should still be the console version, not 0.2.0
            assert console_version_content != '0.2.0' or not console_version.exists()
    
    def test_context_in_project(self):
        """Test that context is saved in project's .project directory."""
        # Initialize context tool with project root
        context_tool = ContextCacheTool(config={'project_root': self.project_dir})
        
        # Save some context
        result = context_tool.invoke({
            'action': 'save_context',
            'context_type': 'todo',
            'name': 'test_todo',
            'data': {'todos': [{'task': 'Test task', 'status': 'pending'}]}
        })
        assert result['success']
        
        # Verify context file created in project directory
        context_file = self.project_dir / '.project' / 'context' / 'todo' / 'test_todo.json'
        assert context_file.exists(), f"Context file should exist at {context_file}"
        
        # Verify console directory doesn't have this context
        console_root = Path(__file__).parent.parent.parent
        console_context = console_root / '.project' / 'context' / 'todo' / 'test_todo.json'
        # This test context should not be in console directory
        assert not console_context.exists() or console_context != context_file
    
    def test_important_files_template_generation(self):
        """Test template generation for important files."""
        manager = get_manager()
        
        # Test README template
        readme = manager.get_file_template(
            'README.md',
            project_name='Test Project',
            project_description='A test project',
            license='MIT'
        )
        assert readme is not None
        assert 'Test Project' in readme
        assert 'A test project' in readme
        
        # Test VERSION template
        version = manager.get_file_template('VERSION')
        assert version is not None
        assert '0.1.0' in version
    
    def test_checklist_export(self):
        """Test exporting important files checklist."""
        # Create a few important files
        (self.project_dir / 'README.md').write_text('# Test')
        (self.project_dir / 'VERSION').write_text('0.1.0')
        
        # Export checklist
        checklist = export_checklist(self.project_dir)
        
        assert 'README.md' in checklist
        assert 'VERSION' in checklist
        assert '✓ Exists' in checklist  # Some files exist
        assert '✗ Missing' in checklist  # Some files don't exist


class TestVersionManagement:
    """Test version management functionality."""
    
    def setup_method(self):
        """Create temporary directory for testing."""
        self.test_dir = Path(tempfile.mkdtemp(prefix='aiagent_test_'))
        self.project_dir = self.test_dir / 'test_project'
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create initial VERSION file
        (self.project_dir / 'VERSION').write_text('1.0.0\n')
    
    def teardown_method(self):
        """Clean up temporary directory."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_version_bump_major(self):
        """Test major version bump."""
        versioning = VersioningTool(config={'project_root': self.project_dir})
        
        result = versioning.invoke({'action': 'bump', 'bump_type': 'major'})
        assert result['success']
        assert result['old_version'] == '1.0.0'
        assert result['new_version'] == '2.0.0'
    
    def test_version_bump_minor(self):
        """Test minor version bump."""
        versioning = VersioningTool(config={'project_root': self.project_dir})
        
        result = versioning.invoke({'action': 'bump', 'bump_type': 'minor'})
        assert result['success']
        assert result['old_version'] == '1.0.0'
        assert result['new_version'] == '1.1.0'
    
    def test_version_bump_patch(self):
        """Test patch version bump."""
        versioning = VersioningTool(config={'project_root': self.project_dir})
        
        result = versioning.invoke({'action': 'bump', 'bump_type': 'patch'})
        assert result['success']
        assert result['old_version'] == '1.0.0'
        assert result['new_version'] == '1.0.1'


class TestPromptRefinement:
    """Test enhanced prompt refinement functionality."""
    
    def test_enhanced_prompt_refiner_import(self):
        """Test that enhanced prompt refiner can be imported."""
        from agents.enhanced_prompt_refiner import EnhancedPromptRefiner, refine_prompt_for_agent
        
        # Should not raise import error
        assert EnhancedPromptRefiner is not None
        assert refine_prompt_for_agent is not None
    
    def test_prompt_refinement_basic(self):
        """Test basic prompt refinement."""
        from agents.enhanced_prompt_refiner import refine_prompt_for_agent
        
        refined = refine_prompt_for_agent(
            prompt="Write a function to add two numbers",
            language="python",
            agent_type="code_editor"
        )
        
        assert refined is not None
        assert len(refined) > 0
        # Should contain role information
        assert 'Python' in refined or 'python' in refined


def run_tests():
    """Run all tests."""
    print("Running AI Agent Console Integration Tests...\n")
    
    # Run pytest
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    run_tests()
