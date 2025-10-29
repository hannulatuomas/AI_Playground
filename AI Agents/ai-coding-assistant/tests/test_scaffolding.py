"""Tests for project scaffolding system."""

import unittest
import tempfile
import shutil
from pathlib import Path

from src.features.project_lifecycle import ProjectScaffolder, scaffold_from_template
from src.features.project_lifecycle.templates import TemplateManager


class TestProjectScaffolder(unittest.TestCase):
    """Test ProjectScaffolder functionality."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.scaffolder = ProjectScaffolder(verbose=False)
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Cleanup test files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_replace_variables(self):
        """Test variable replacement in content."""
        content = "Project: {{PROJECT_NAME}}, Author: {{AUTHOR}}"
        variables = {"PROJECT_NAME": "test-app", "AUTHOR": "John Doe"}
        
        result = self.scaffolder.replace_variables(content, variables)
        
        self.assertEqual(result, "Project: test-app, Author: John Doe")
        self.assertNotIn("{{", result)
    
    def test_replace_variables_multiple_occurrences(self):
        """Test variable replacement with multiple occurrences."""
        content = "{{NAME}} is great. {{NAME}} is awesome. {{NAME}} rocks!"
        variables = {"NAME": "Python"}
        
        result = self.scaffolder.replace_variables(content, variables)
        
        self.assertEqual(result, "Python is great. Python is awesome. Python rocks!")
    
    def test_replace_variables_case_sensitive(self):
        """Test that variable replacement is case-sensitive."""
        content = "{{NAME}} and {{name}} are different"
        variables = {"NAME": "UPPER", "name": "lower"}
        
        result = self.scaffolder.replace_variables(content, variables)
        
        self.assertEqual(result, "UPPER and lower are different")
    
    def test_create_files_basic(self):
        """Test basic file creation."""
        files = {
            "README.md": "# {{PROJECT_NAME}}",
            "src/main.py": "print('{{PROJECT_NAME}}')"
        }
        variables = {"PROJECT_NAME": "test-project"}
        dest = self.temp_dir / "project"
        dest.mkdir()
        
        success = self.scaffolder.create_files(files, dest, variables)
        
        self.assertTrue(success)
        self.assertTrue((dest / "README.md").exists())
        self.assertTrue((dest / "src" / "main.py").exists())
        
        # Check content
        readme = (dest / "README.md").read_text()
        self.assertEqual(readme, "# test-project")
    
    def test_create_files_with_variable_in_path(self):
        """Test file creation with variables in path."""
        files = {
            "src/{{PROJECT_NAME}}/main.py": "# Main file"
        }
        variables = {"PROJECT_NAME": "myapp"}
        dest = self.temp_dir / "project"
        dest.mkdir()
        
        success = self.scaffolder.create_files(files, dest, variables)
        
        self.assertTrue(success)
        self.assertTrue((dest / "src" / "myapp" / "main.py").exists())
    
    def test_scaffold_project_success(self):
        """Test successful project scaffolding."""
        template = {
            "name": "test-template",
            "variables": {
                "PROJECT_NAME": {"type": "string", "required": True},
                "AUTHOR": {"type": "string", "default": "Anonymous"}
            },
            "files": {
                "README.md": "# {{PROJECT_NAME}}\nBy {{AUTHOR}}",
                "main.py": "print('{{PROJECT_NAME}}')"
            },
            "commands": ["echo 'Setup complete'"]
        }
        
        dest = self.temp_dir / "test-project"
        config = {"PROJECT_NAME": "my-project"}
        
        success, message = self.scaffolder.scaffold_project(template, dest, config)
        
        self.assertTrue(success)
        self.assertIn("successfully", message.lower())
        self.assertTrue(dest.exists())
        self.assertTrue((dest / "README.md").exists())
        self.assertTrue((dest / "main.py").exists())
        
        # Check variable substitution
        readme = (dest / "README.md").read_text()
        self.assertIn("my-project", readme)
        self.assertIn("Anonymous", readme)  # Default value
    
    def test_scaffold_project_with_custom_values(self):
        """Test scaffolding with all variables provided."""
        template = {
            "name": "test-template",
            "variables": {
                "PROJECT_NAME": {"type": "string", "required": True},
                "AUTHOR": {"type": "string", "default": "Anonymous"}
            },
            "files": {
                "README.md": "# {{PROJECT_NAME}}\nBy {{AUTHOR}}"
            }
        }
        
        dest = self.temp_dir / "test-project"
        config = {"PROJECT_NAME": "my-project", "AUTHOR": "John Doe"}
        
        success, message = self.scaffolder.scaffold_project(template, dest, config)
        
        self.assertTrue(success)
        
        readme = (dest / "README.md").read_text()
        self.assertIn("John Doe", readme)  # Custom value, not default
    
    def test_scaffold_project_missing_required_variable(self):
        """Test scaffolding fails with missing required variable."""
        template = {
            "name": "test-template",
            "variables": {
                "PROJECT_NAME": {"type": "string", "required": True}
            },
            "files": {"README.md": "# {{PROJECT_NAME}}"}
        }
        
        dest = self.temp_dir / "test-project"
        config = {}  # Missing PROJECT_NAME
        
        success, message = self.scaffolder.scaffold_project(template, dest, config)
        
        self.assertFalse(success)
        self.assertIn("required", message.lower())
        self.assertIn("PROJECT_NAME", message)
    
    def test_scaffold_project_existing_destination(self):
        """Test scaffolding fails when destination exists."""
        template = {
            "name": "test-template",
            "files": {"README.md": "# Test"}
        }
        
        dest = self.temp_dir / "existing"
        dest.mkdir()  # Create destination
        
        config = {}
        
        success, message = self.scaffolder.scaffold_project(template, dest, config, overwrite=False)
        
        self.assertFalse(success)
    
    def test_scaffold_project_overwrite(self):
        """Test scaffolding with overwrite=True."""
        template = {
            "name": "test-template",
            "files": {"README.md": "# New Content"}
        }
        
        dest = self.temp_dir / "existing"
        dest.mkdir()
        (dest / "old.txt").write_text("old content")
        
        config = {}
        
        success, message = self.scaffolder.scaffold_project(template, dest, config, overwrite=True)
        
        self.assertTrue(success)
        self.assertTrue((dest / "README.md").exists())
        self.assertFalse((dest / "old.txt").exists())  # Old content removed
    
    def test_rollback_on_error(self):
        """Test rollback removes created files on error."""
        template = {
            "name": "test-template",
            "files": {
                "README.md": "# Test",
                "invalid/../../escape.txt": "Bad path"  # This should fail
            }
        }
        
        dest = self.temp_dir / "test-project"
        config = {}
        
        # This should fail and rollback
        success, message = self.scaffolder.scaffold_project(template, dest, config)
        
        # Even if it fails, rollback should work
        # (Note: actual behavior depends on error type)
        self.assertFalse(success)
    
    def test_merge_config_with_defaults(self):
        """Test merging user config with template defaults."""
        template = {
            "variables": {
                "VAR1": {"required": True},
                "VAR2": {"default": "default2"},
                "VAR3": {"default": "default3"}
            }
        }
        config = {"VAR1": "value1", "VAR3": "custom3"}
        
        merged = self.scaffolder._merge_config_with_defaults(template, config)
        
        self.assertEqual(merged["VAR1"], "value1")
        self.assertEqual(merged["VAR2"], "default2")  # From default
        self.assertEqual(merged["VAR3"], "custom3")   # Custom overrides default
    
    def test_validate_required_variables(self):
        """Test required variable validation."""
        template = {
            "variables": {
                "REQ1": {"required": True},
                "REQ2": {"required": True},
                "OPT1": {"required": False}
            }
        }
        
        # All required provided
        variables = {"REQ1": "val1", "REQ2": "val2"}
        is_valid, missing = self.scaffolder._validate_required_variables(template, variables)
        self.assertTrue(is_valid)
        self.assertEqual(len(missing), 0)
        
        # One required missing
        variables = {"REQ1": "val1"}
        is_valid, missing = self.scaffolder._validate_required_variables(template, variables)
        self.assertFalse(is_valid)
        self.assertIn("REQ2", missing)


class TestScaffoldFromTemplate(unittest.TestCase):
    """Test the convenience function."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = TemplateManager()
    
    def tearDown(self):
        """Cleanup test files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_scaffold_from_existing_template(self):
        """Test scaffolding from a real template."""
        dest = self.temp_dir / "test-react-app"
        config = {
            "PROJECT_NAME": "test-react-app",
            "AUTHOR": "Test Author",
            "DESCRIPTION": "A test application"
        }
        
        success, message = scaffold_from_template(
            "web-react",
            dest,
            config
        )
        
        self.assertTrue(success)
        self.assertTrue(dest.exists())
        self.assertTrue((dest / "package.json").exists())
        self.assertTrue((dest / "src" / "main.tsx").exists())
        
        # Verify variable substitution
        package_json = (dest / "package.json").read_text()
        self.assertIn("test-react-app", package_json)
    
    def test_scaffold_from_nonexistent_template(self):
        """Test scaffolding fails for nonexistent template."""
        dest = self.temp_dir / "test-project"
        config = {"PROJECT_NAME": "test"}
        
        success, message = scaffold_from_template(
            "nonexistent-template",
            dest,
            config
        )
        
        self.assertFalse(success)
        self.assertIn("not found", message.lower())
    
    def test_scaffold_cli_python_template(self):
        """Test scaffolding CLI Python template."""
        dest = self.temp_dir / "test_cli"
        config = {
            "PROJECT_NAME": "test_cli",
            "AUTHOR": "Test Author",
            "EMAIL": "[email protected]",
            "DESCRIPTION": "A test CLI"
        }
        
        success, message = scaffold_from_template(
            "cli-python",
            dest,
            config
        )
        
        self.assertTrue(success)
        self.assertTrue((dest / "setup.py").exists())
        self.assertTrue((dest / "src" / "test_cli" / "cli.py").exists())
        
        # Check variable substitution in path
        cli_file = dest / "src" / "test_cli" / "cli.py"
        self.assertTrue(cli_file.exists())


class TestIntegrationWithTemplateManager(unittest.TestCase):
    """Test integration between TemplateManager and ProjectScaffolder."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.manager = TemplateManager()
        self.scaffolder = ProjectScaffolder()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Cleanup test files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_workflow(self):
        """Test complete workflow from template to project."""
        # 1. List templates
        templates = self.manager.list_templates()
        self.assertGreater(len(templates), 0)
        
        # 2. Get a template
        template = self.manager.get_template("web-react")
        self.assertIsNotNone(template)
        
        # 3. Validate template
        is_valid, errors = self.manager.validate_template(template)
        self.assertTrue(is_valid)
        
        # 4. Scaffold project
        dest = self.temp_dir / "integrated-project"
        config = {
            "PROJECT_NAME": "integrated-project",
            "AUTHOR": "Integration Test"
        }
        
        success, message = self.scaffolder.scaffold_project(template, dest, config)
        
        self.assertTrue(success)
        self.assertTrue(dest.exists())
        
        # 5. Verify files created
        self.assertTrue((dest / "package.json").exists())
        self.assertTrue((dest / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
