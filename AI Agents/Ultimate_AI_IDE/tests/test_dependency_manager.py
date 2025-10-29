"""
Tests for Dependency Manager Module

Comprehensive tests for dependency management functionality.
"""

import pytest
from pathlib import Path
from src.modules.dependency_manager import DependencyManager, DependencyUpdate, UpdateResult


class TestDependencyManager:
    """Test dependency manager."""
    
    def test_manager_initialization(self, tmp_path):
        """Test manager initializes correctly"""
        manager = DependencyManager(str(tmp_path))
        assert manager.project_path == tmp_path
        assert manager.package_manager in ['pip', 'npm', 'yarn', 'dotnet', 'maven', 'unknown']
    
    def test_detect_pip_project(self, tmp_path):
        """Test detection of pip project"""
        (tmp_path / "requirements.txt").write_text("requests==2.28.0\n")
        
        manager = DependencyManager(str(tmp_path))
        assert manager.package_manager == "pip"
    
    def test_detect_npm_project(self, tmp_path):
        """Test detection of npm project"""
        (tmp_path / "package.json").write_text('{"name": "test"}')
        
        manager = DependencyManager(str(tmp_path))
        assert manager.package_manager == "npm"
    
    def test_detect_yarn_project(self, tmp_path):
        """Test detection of yarn project"""
        (tmp_path / "yarn.lock").write_text("")
        
        manager = DependencyManager(str(tmp_path))
        assert manager.package_manager == "yarn"
    
    def test_check_outdated_pip(self, tmp_path):
        """Test checking outdated pip packages"""
        (tmp_path / "requirements.txt").write_text("requests==2.0.0\n")
        
        manager = DependencyManager(str(tmp_path))
        updates = manager.check_outdated()
        
        assert isinstance(updates, list)
    
    def test_breaking_change_detection(self, tmp_path):
        """Test breaking change detection"""
        manager = DependencyManager(str(tmp_path))
        
        # Major version change is breaking
        assert manager._is_breaking_change("1.0.0", "2.0.0") is True
        
        # Minor version change is not breaking
        assert manager._is_breaking_change("1.0.0", "1.1.0") is False
        
        # Patch version change is not breaking
        assert manager._is_breaking_change("1.0.0", "1.0.1") is False
    
    def test_suggest_safe_updates(self, tmp_path):
        """Test suggesting safe updates"""
        manager = DependencyManager(str(tmp_path))
        safe_updates = manager.suggest_safe_updates()
        
        assert isinstance(safe_updates, list)
        # All suggested updates should be non-breaking
        for update in safe_updates:
            assert update.is_breaking is False
    
    def test_backup_creation(self, tmp_path):
        """Test backup creation"""
        (tmp_path / "requirements.txt").write_text("requests==2.28.0\n")
        
        manager = DependencyManager(str(tmp_path))
        backup_path = manager._create_backup()
        
        assert backup_path is not None
        assert backup_path.exists()
        assert (backup_path / "requirements.txt").exists()
    
    def test_update_with_rollback(self, tmp_path):
        """Test update with rollback on failure"""
        (tmp_path / "requirements.txt").write_text("requests==2.28.0\n")
        
        manager = DependencyManager(str(tmp_path))
        
        # Update with invalid package (should fail)
        result = manager.update_dependencies(
            packages=["nonexistent-package-12345"],
            test_after=False,
            rollback_on_failure=True
        )
        
        assert isinstance(result, UpdateResult)
        assert result.success is False or len(result.failed) > 0


class TestDependencyUpdate:
    """Test DependencyUpdate dataclass."""
    
    def test_dependency_update_creation(self):
        """Test creating dependency update"""
        update = DependencyUpdate(
            name="requests",
            current_version="2.28.0",
            latest_version="2.31.0",
            is_breaking=False
        )
        
        assert update.name == "requests"
        assert update.current_version == "2.28.0"
        assert update.latest_version == "2.31.0"
        assert update.is_breaking is False
        assert update.security_fixes == []
    
    def test_breaking_update(self):
        """Test breaking update"""
        update = DependencyUpdate(
            name="requests",
            current_version="2.28.0",
            latest_version="3.0.0",
            is_breaking=True
        )
        
        assert update.is_breaking is True


class TestUpdateResult:
    """Test UpdateResult dataclass."""
    
    def test_update_result_success(self):
        """Test successful update result"""
        result = UpdateResult(
            success=True,
            updated=["requests", "urllib3"],
            failed=[]
        )
        
        assert result.success is True
        assert len(result.updated) == 2
        assert len(result.failed) == 0
        assert result.rolled_back is False
    
    def test_update_result_failure(self):
        """Test failed update result"""
        result = UpdateResult(
            success=False,
            updated=[],
            failed=["nonexistent-package"],
            rolled_back=True,
            errors=["Package not found"]
        )
        
        assert result.success is False
        assert len(result.failed) == 1
        assert result.rolled_back is True
        assert len(result.errors) == 1


class TestIntegration:
    """Integration tests for dependency manager."""
    
    def test_full_workflow_pip(self, tmp_path):
        """Test complete workflow for pip project"""
        # Create pip project
        (tmp_path / "requirements.txt").write_text("requests==2.0.0\n")
        
        manager = DependencyManager(str(tmp_path))
        
        # Check outdated
        updates = manager.check_outdated()
        assert isinstance(updates, list)
        
        # Get safe updates
        safe_updates = manager.suggest_safe_updates()
        assert isinstance(safe_updates, list)
        
        # Verify all safe updates are non-breaking
        for update in safe_updates:
            assert update.is_breaking is False
    
    def test_full_workflow_npm(self, tmp_path):
        """Test complete workflow for npm project"""
        # Create npm project
        (tmp_path / "package.json").write_text('''
{
  "name": "test-project",
  "version": "1.0.0",
  "dependencies": {
    "express": "4.0.0"
  }
}
''')
        
        manager = DependencyManager(str(tmp_path))
        
        # Check outdated
        updates = manager.check_outdated()
        assert isinstance(updates, list)
    
    def test_backup_and_rollback(self, tmp_path):
        """Test backup and rollback functionality"""
        # Create project
        req_file = tmp_path / "requirements.txt"
        original_content = "requests==2.28.0\n"
        req_file.write_text(original_content)
        
        manager = DependencyManager(str(tmp_path))
        
        # Create backup
        backup_path = manager._create_backup()
        assert backup_path.exists()
        
        # Modify file
        req_file.write_text("requests==2.31.0\n")
        assert req_file.read_text() != original_content
        
        # Rollback
        manager._rollback(backup_path)
        assert req_file.read_text() == original_content
    
    def test_version_comparison(self, tmp_path):
        """Test semantic version comparison"""
        manager = DependencyManager(str(tmp_path))
        
        # Test various version comparisons
        test_cases = [
            ("1.0.0", "2.0.0", True),   # Major bump - breaking
            ("1.0.0", "1.1.0", False),  # Minor bump - safe
            ("1.0.0", "1.0.1", False),  # Patch bump - safe
            ("2.5.3", "3.0.0", True),   # Major bump - breaking
            ("2.5.3", "2.6.0", False),  # Minor bump - safe
        ]
        
        for current, latest, expected_breaking in test_cases:
            result = manager._is_breaking_change(current, latest)
            assert result == expected_breaking, f"Failed for {current} -> {latest}"
    
    def test_multiple_package_managers(self, tmp_path):
        """Test detection of different package managers"""
        # Test pip
        (tmp_path / "requirements.txt").write_text("requests==2.0.0\n")
        manager1 = DependencyManager(str(tmp_path))
        assert manager1.package_manager == "pip"
        
        # Clean up
        (tmp_path / "requirements.txt").unlink()
        
        # Test npm
        (tmp_path / "package.json").write_text('{"name": "test"}')
        manager2 = DependencyManager(str(tmp_path))
        assert manager2.package_manager == "npm"
    
    def test_backup_directory_creation(self, tmp_path):
        """Test backup directory is created properly"""
        (tmp_path / "requirements.txt").write_text("requests==2.0.0\n")
        
        manager = DependencyManager(str(tmp_path))
        backup_path = manager._create_backup()
        
        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.parent == manager.backup_dir
        assert manager.backup_dir.exists()
    
    def test_multiple_backups(self, tmp_path):
        """Test creating multiple backups"""
        (tmp_path / "requirements.txt").write_text("requests==2.0.0\n")
        
        manager = DependencyManager(str(tmp_path))
        
        # Create multiple backups with delay to ensure different timestamps
        import time
        backup1 = manager._create_backup()
        time.sleep(1)  # Wait 1 second to get different timestamp
        backup2 = manager._create_backup()
        
        assert backup1 is not None
        assert backup2 is not None
        if backup1 and backup2:
            assert backup1 != backup2
            assert backup1.exists()
            assert backup2.exists()
    
    def test_update_with_test_failure(self, tmp_path):
        """Test rollback when tests fail"""
        (tmp_path / "requirements.txt").write_text("requests==2.28.0\n")
        
        manager = DependencyManager(str(tmp_path))
        
        # Mock test failure by updating non-existent package
        result = manager.update_dependencies(
            packages=["nonexistent-package-xyz"],
            test_after=False,
            rollback_on_failure=True
        )
        
        # Should handle failure gracefully
        assert isinstance(result, UpdateResult)
    
    def test_safe_update_filtering(self, tmp_path):
        """Test that safe updates exclude breaking changes"""
        manager = DependencyManager(str(tmp_path))
        
        # Mock some updates
        all_updates = manager.check_outdated()
        safe_updates = manager.suggest_safe_updates()
        
        # All safe updates should be non-breaking
        for update in safe_updates:
            assert update.is_breaking is False
    
    def test_empty_project(self, tmp_path):
        """Test handling of project with no dependencies"""
        manager = DependencyManager(str(tmp_path))
        
        updates = manager.check_outdated()
        assert isinstance(updates, list)
        assert len(updates) == 0
    
    def test_package_manager_unknown(self, tmp_path):
        """Test handling of unknown package manager"""
        # Empty directory with no package files
        manager = DependencyManager(str(tmp_path))
        assert manager.package_manager == "unknown"
        
        updates = manager.check_outdated()
        assert isinstance(updates, list)
        assert len(updates) == 0
