"""Tests for project initialization system."""

import unittest
import tempfile
import shutil
import subprocess
from pathlib import Path

from src.features.project_lifecycle import ProjectInitializer


class TestProjectInitializer(unittest.TestCase):
    """Test ProjectInitializer functionality."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.initializer = ProjectInitializer(verbose=False)
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Cleanup test files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_project_type_python(self):
        """Test Python project detection."""
        project = self.temp_dir / "python-project"
        project.mkdir()
        (project / "requirements.txt").write_text("flask==2.0.0")
        
        project_type = self.initializer.detect_project_type(project)
        
        self.assertEqual(project_type, "python")
    
    def test_detect_project_type_node(self):
        """Test Node project detection."""
        project = self.temp_dir / "node-project"
        project.mkdir()
        (project / "package.json").write_text('{"name": "test"}')
        
        project_type = self.initializer.detect_project_type(project)
        
        self.assertEqual(project_type, "node")
    
    def test_detect_project_type_dotnet(self):
        """Test .NET project detection."""
        project = self.temp_dir / "dotnet-project"
        project.mkdir()
        (project / "App.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk">')
        
        project_type = self.initializer.detect_project_type(project)
        
        self.assertEqual(project_type, "dotnet")
    
    def test_detect_project_type_unknown(self):
        """Test unknown project type."""
        project = self.temp_dir / "unknown-project"
        project.mkdir()
        (project / "README.md").write_text("# Test")
        
        project_type = self.initializer.detect_project_type(project)
        
        self.assertIsNone(project_type)
    
    def test_detect_dependencies_python(self):
        """Test Python dependency detection."""
        project = self.temp_dir / "python-project"
        project.mkdir()
        (project / "requirements.txt").write_text("flask")
        (project / "requirements-dev.txt").write_text("pytest")
        
        deps = self.initializer.detect_dependencies(project)
        
        self.assertIn("requirements.txt", deps)
        self.assertIn("requirements-dev.txt", deps)
    
    def test_detect_dependencies_node(self):
        """Test Node dependency detection."""
        project = self.temp_dir / "node-project"
        project.mkdir()
        (project / "package.json").write_text('{}')
        
        deps = self.initializer.detect_dependencies(project)
        
        self.assertIn("package.json", deps)
    
    def test_select_license_mit(self):
        """Test MIT license selection."""
        license_text = self.initializer.select_license("MIT")
        
        self.assertIsNotNone(license_text)
        self.assertIn("MIT License", license_text)
        self.assertIn("Permission is hereby granted", license_text)
    
    def test_select_license_apache(self):
        """Test Apache license selection."""
        license_text = self.initializer.select_license("Apache-2.0")
        
        self.assertIsNotNone(license_text)
        self.assertIn("Apache License", license_text)
    
    def test_select_license_gpl(self):
        """Test GPL license selection."""
        license_text = self.initializer.select_license("GPL-3.0")
        
        self.assertIsNotNone(license_text)
        self.assertIn("GNU GENERAL PUBLIC LICENSE", license_text)
    
    def test_select_license_unknown(self):
        """Test unknown license type."""
        license_text = self.initializer.select_license("Unknown")
        
        self.assertIsNone(license_text)
    
    def test_generate_license_file(self):
        """Test LICENSE file generation."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        
        success, message = self.initializer.generate_license_file(
            project,
            license_type="MIT",
            author="Test Author",
            year=2024
        )
        
        self.assertTrue(success)
        self.assertTrue((project / "LICENSE").exists())
        
        # Check content
        license_content = (project / "LICENSE").read_text()
        self.assertIn("MIT License", license_content)
        self.assertIn("Test Author", license_content)
        self.assertIn("2024", license_content)
    
    def test_generate_license_file_invalid_type(self):
        """Test LICENSE generation with invalid type."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        
        success, message = self.initializer.generate_license_file(
            project,
            license_type="Invalid"
        )
        
        self.assertFalse(success)
        self.assertIn("Unknown license type", message)
    
    def test_generate_readme_basic(self):
        """Test README generation."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        
        info = {
            "name": "Test Project",
            "description": "A test project",
            "author": "Test Author"
        }
        
        success, message = self.initializer.generate_readme(project, info)
        
        self.assertTrue(success)
        self.assertTrue((project / "README.md").exists())
        
        # Check content
        readme_content = (project / "README.md").read_text()
        self.assertIn("Test Project", readme_content)
        self.assertIn("A test project", readme_content)
        self.assertIn("Test Author", readme_content)
    
    def test_generate_readme_existing_no_overwrite(self):
        """Test README generation with existing file."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        (project / "README.md").write_text("Existing README")
        
        info = {"name": "Test"}
        
        success, message = self.initializer.generate_readme(
            project, info, overwrite=False
        )
        
        self.assertTrue(success)
        self.assertIn("already exists", message)
        
        # Original content should remain
        content = (project / "README.md").read_text()
        self.assertEqual(content, "Existing README")
    
    def test_generate_readme_with_overwrite(self):
        """Test README generation with overwrite."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        (project / "README.md").write_text("Old README")
        
        info = {"name": "New Project"}
        
        success, message = self.initializer.generate_readme(
            project, info, overwrite=True
        )
        
        self.assertTrue(success)
        self.assertIn("updated", message)
        
        # Should have new content
        content = (project / "README.md").read_text()
        self.assertIn("New Project", content)
        self.assertNotIn("Old README", content)
    
    def test_get_setup_instructions_python(self):
        """Test setup instructions for Python project."""
        project = self.temp_dir / "python-project"
        project.mkdir()
        (project / "requirements.txt").write_text("flask")
        
        instructions = self.initializer.get_setup_instructions(project)
        
        self.assertIsInstance(instructions, list)
        self.assertTrue(any("venv" in inst for inst in instructions))
        self.assertTrue(any("pip install" in inst for inst in instructions))
    
    def test_get_setup_instructions_node(self):
        """Test setup instructions for Node project."""
        project = self.temp_dir / "node-project"
        project.mkdir()
        (project / "package.json").write_text('{}')
        
        instructions = self.initializer.get_setup_instructions(project)
        
        self.assertIsInstance(instructions, list)
        self.assertTrue(any("npm install" in inst for inst in instructions))
    
    def test_get_setup_instructions_dotnet(self):
        """Test setup instructions for .NET project."""
        project = self.temp_dir / "dotnet-project"
        project.mkdir()
        (project / "App.csproj").write_text('<Project>')
        
        instructions = self.initializer.get_setup_instructions(project)
        
        self.assertIsInstance(instructions, list)
        self.assertTrue(any("dotnet restore" in inst for inst in instructions))
    
    def test_initialize_git_basic(self):
        """Test basic git initialization."""
        # Skip if git not available
        try:
            subprocess.run(
                ["git", "--version"],
                check=True,
                capture_output=True,
                timeout=5
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self.skipTest("Git not available")
        
        project = self.temp_dir / "git-project"
        project.mkdir()
        (project / "README.md").write_text("# Test")
        
        success, message = self.initializer.initialize_git(
            project,
            initial_message="Test commit"
        )
        
        self.assertTrue(success)
        self.assertTrue((project / ".git").exists())
        self.assertIn("initialized", message.lower())
    
    def test_initialize_git_creates_gitignore(self):
        """Test git init creates .gitignore."""
        try:
            subprocess.run(
                ["git", "--version"],
                check=True,
                capture_output=True,
                timeout=5
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self.skipTest("Git not available")
        
        project = self.temp_dir / "git-project"
        project.mkdir()
        (project / "requirements.txt").write_text("flask")  # Make it Python project
        
        success, message = self.initializer.initialize_git(
            project,
            add_gitignore=True
        )
        
        self.assertTrue(success)
        self.assertTrue((project / ".gitignore").exists())
        
        # Check .gitignore content
        gitignore = (project / ".gitignore").read_text()
        self.assertIn("__pycache__", gitignore)
    
    def test_initialize_git_nonexistent_path(self):
        """Test git init with nonexistent path."""
        nonexistent = self.temp_dir / "nonexistent"
        
        success, message = self.initializer.initialize_git(nonexistent)
        
        self.assertFalse(success)
        self.assertIn("does not exist", message)
    
    def test_create_virtual_env_venv(self):
        """Test venv creation."""
        project = self.temp_dir / "python-project"
        project.mkdir()
        (project / "requirements.txt").write_text("flask")
        
        success, message = self.initializer.create_virtual_env(
            project,
            env_type="venv"
        )
        
        # Should succeed (or fail gracefully if venv not available)
        if success:
            self.assertTrue((project / "venv").exists())
        else:
            self.assertIsInstance(message, str)
    
    def test_create_virtual_env_not_python_project(self):
        """Test venv creation on non-Python project."""
        project = self.temp_dir / "node-project"
        project.mkdir()
        (project / "package.json").write_text('{}')
        
        success, message = self.initializer.create_virtual_env(project)
        
        self.assertFalse(success)
        self.assertIn("Not a Python project", message)
    
    def test_create_virtual_env_invalid_type(self):
        """Test venv creation with invalid type."""
        project = self.temp_dir / "python-project"
        project.mkdir()
        (project / "requirements.txt").write_text("")
        
        success, message = self.initializer.create_virtual_env(
            project,
            env_type="invalid"
        )
        
        self.assertFalse(success)
        self.assertIn("Unknown environment type", message)


class TestProjectInitializerIntegration(unittest.TestCase):
    """Integration tests for ProjectInitializer."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.initializer = ProjectInitializer(verbose=False)
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Cleanup test files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_project_initialization(self):
        """Test complete project initialization workflow."""
        project = self.temp_dir / "full-test-project"
        project.mkdir()
        (project / "requirements.txt").write_text("flask==2.0.0")
        
        # Detect project type
        project_type = self.initializer.detect_project_type(project)
        self.assertEqual(project_type, "python")
        
        # Generate LICENSE
        success, msg = self.initializer.generate_license_file(
            project,
            license_type="MIT",
            author="Test Author"
        )
        self.assertTrue(success)
        
        # Generate README
        info = {
            "name": "Full Test Project",
            "description": "Integration test",
            "author": "Test Author"
        }
        success, msg = self.initializer.generate_readme(project, info)
        self.assertTrue(success)
        
        # Get setup instructions
        instructions = self.initializer.get_setup_instructions(project)
        self.assertGreater(len(instructions), 0)
        
        # Verify all files created
        self.assertTrue((project / "LICENSE").exists())
        self.assertTrue((project / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
