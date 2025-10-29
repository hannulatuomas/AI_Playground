"""Tests for project templates system."""

import sys
import json
import pytest
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.features.project_lifecycle.templates import TemplateManager


class TestTemplateManager:
    """Test TemplateManager functionality."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        builtin_dir = Path(tempfile.mkdtemp())
        custom_dir = Path(tempfile.mkdtemp())
        
        yield builtin_dir, custom_dir
        
        # Cleanup
        shutil.rmtree(builtin_dir, ignore_errors=True)
        shutil.rmtree(custom_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_template(self):
        """Create a sample template."""
        return {
            "name": "test-template",
            "description": "A test template",
            "version": "1.0.0",
            "variables": {
                "PROJECT_NAME": {
                    "type": "string",
                    "required": True
                },
                "AUTHOR": {
                    "type": "string",
                    "default": "Test Author"
                }
            },
            "files": {
                "README.md": "# {{PROJECT_NAME}}\n\nBy {{AUTHOR}}",
                "src/main.py": "print('{{PROJECT_NAME}}')"
            },
            "commands": ["pip install -r requirements.txt"]
        }
    
    def test_init(self, temp_dirs):
        """Test TemplateManager initialization."""
        builtin_dir, custom_dir = temp_dirs
        manager = TemplateManager(builtin_dir=builtin_dir, custom_dir=custom_dir)
        
        assert manager.builtin_dir == builtin_dir
        assert manager.custom_dir == custom_dir
        assert custom_dir.exists()
    
    def test_validate_template_valid(self, sample_template):
        """Test template validation with valid template."""
        manager = TemplateManager()
        is_valid, errors = manager.validate_template(sample_template)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_template_missing_name(self, sample_template):
        """Test template validation without name."""
        manager = TemplateManager()
        del sample_template["name"]
        
        is_valid, errors = manager.validate_template(sample_template)
        
        assert is_valid is False
        assert any("name" in error.lower() for error in errors)
    
    def test_validate_template_missing_files(self, sample_template):
        """Test template validation without files."""
        manager = TemplateManager()
        del sample_template["files"]
        
        is_valid, errors = manager.validate_template(sample_template)
        
        assert is_valid is False
        assert any("files" in error.lower() for error in errors)
    
    def test_validate_template_invalid_path(self, sample_template):
        """Test template validation with backslashes in path."""
        manager = TemplateManager()
        sample_template["files"]["src\\test.py"] = "content"
        
        is_valid, errors = manager.validate_template(sample_template)
        
        assert is_valid is False
        assert any("forward slashes" in error.lower() for error in errors)
    
    def test_is_valid_project_name(self):
        """Test project name validation."""
        manager = TemplateManager()
        
        # Valid names
        assert manager._is_valid_project_name("my-project") is True
        assert manager._is_valid_project_name("my_project") is True
        assert manager._is_valid_project_name("MyProject123") is True
        
        # Invalid names
        assert manager._is_valid_project_name("") is False
        assert manager._is_valid_project_name("my project") is False
        assert manager._is_valid_project_name("my@project") is False
        assert manager._is_valid_project_name("my.project") is False
    
    def test_substitute_variables(self):
        """Test variable substitution."""
        manager = TemplateManager()
        
        content = "Hello {{NAME}}, welcome to {{PROJECT}}!"
        variables = {"NAME": "Alice", "PROJECT": "TestApp"}
        
        result = manager._substitute_variables(content, variables)
        
        assert result == "Hello Alice, welcome to TestApp!"
    
    def test_add_custom_template(self, temp_dirs, sample_template):
        """Test adding custom template."""
        builtin_dir, custom_dir = temp_dirs
        manager = TemplateManager(builtin_dir=builtin_dir, custom_dir=custom_dir)
        
        # Create template file
        template_path = builtin_dir / "test-template.json"
        with open(template_path, 'w') as f:
            json.dump(sample_template, f)
        
        # Add template
        success, message = manager.add_custom_template(template_path)
        
        assert success is True
        assert "successfully" in message.lower()
        assert (custom_dir / "test-template.json").exists()
    
    def test_list_templates(self, temp_dirs, sample_template):
        """Test listing templates."""
        builtin_dir, custom_dir = temp_dirs
        manager = TemplateManager(builtin_dir=builtin_dir, custom_dir=custom_dir)
        
        # Create builtin template
        builtin_template_path = builtin_dir / "builtin-template.json"
        with open(builtin_template_path, 'w') as f:
            json.dump(sample_template, f)
        
        # Create custom template
        custom_template = sample_template.copy()
        custom_template["name"] = "custom-template"
        custom_template_path = custom_dir / "custom-template.json"
        with open(custom_template_path, 'w') as f:
            json.dump(custom_template, f)
        
        # List templates
        templates = manager.list_templates()
        
        assert len(templates) == 2
        assert any(t["source"] == "builtin" for t in templates)
        assert any(t["source"] == "custom" for t in templates)
    
    def test_get_template(self, temp_dirs, sample_template):
        """Test getting template by name."""
        builtin_dir, custom_dir = temp_dirs
        manager = TemplateManager(builtin_dir=builtin_dir, custom_dir=custom_dir)
        
        # Create template
        template_path = builtin_dir / "test-template.json"
        with open(template_path, 'w') as f:
            json.dump(sample_template, f)
        
        # Get template
        template = manager.get_template("test-template")
        
        assert template is not None
        assert template["name"] == "test-template"
        assert template["description"] == "A test template"
    
    def test_get_template_not_found(self, temp_dirs):
        """Test getting non-existent template."""
        builtin_dir, custom_dir = temp_dirs
        manager = TemplateManager(builtin_dir=builtin_dir, custom_dir=custom_dir)
        
        template = manager.get_template("nonexistent")
        
        assert template is None
    
    def test_create_from_template(self, temp_dirs, sample_template):
        """Test creating project from template."""
        builtin_dir, custom_dir = temp_dirs
        manager = TemplateManager(builtin_dir=builtin_dir, custom_dir=custom_dir)
        
        # Create template
        template_path = builtin_dir / "test-template.json"
        with open(template_path, 'w') as f:
            json.dump(sample_template, f)
        
        # Create project
        dest = Path(tempfile.mkdtemp()) / "test-project"
        config = {
            "PROJECT_NAME": "test-project",
            "AUTHOR": "John Doe"
        }
        
        try:
            success, message = manager.create_from_template(
                "test-template",
                dest,
                config
            )
            
            assert success is True
            assert dest.exists()
            assert (dest / "README.md").exists()
            assert (dest / "src" / "main.py").exists()
            
            # Check variable substitution
            readme_content = (dest / "README.md").read_text()
            assert "test-project" in readme_content
            assert "John Doe" in readme_content
            
        finally:
            # Cleanup
            if dest.exists():
                shutil.rmtree(dest.parent, ignore_errors=True)
    
    def test_create_from_template_with_defaults(self, temp_dirs, sample_template):
        """Test creating project with default variable values."""
        builtin_dir, custom_dir = temp_dirs
        manager = TemplateManager(builtin_dir=builtin_dir, custom_dir=custom_dir)
        
        # Create template
        template_path = builtin_dir / "test-template.json"
        with open(template_path, 'w') as f:
            json.dump(sample_template, f)
        
        # Create project with minimal config
        dest = Path(tempfile.mkdtemp()) / "test-project"
        config = {
            "PROJECT_NAME": "test-project"
            # AUTHOR not provided, should use default
        }
        
        try:
            success, message = manager.create_from_template(
                "test-template",
                dest,
                config
            )
            
            assert success is True
            
            # Check default value was used
            readme_content = (dest / "README.md").read_text()
            assert "Test Author" in readme_content
            
        finally:
            # Cleanup
            if dest.exists():
                shutil.rmtree(dest.parent, ignore_errors=True)
    
    def test_create_from_template_invalid_name(self, temp_dirs, sample_template):
        """Test creating project with invalid name."""
        builtin_dir, custom_dir = temp_dirs
        manager = TemplateManager(builtin_dir=builtin_dir, custom_dir=custom_dir)
        
        # Create template
        template_path = builtin_dir / "test-template.json"
        with open(template_path, 'w') as f:
            json.dump(sample_template, f)
        
        # Try to create project with invalid name
        dest = Path(tempfile.mkdtemp()) / "test project"  # Space in name
        config = {
            "PROJECT_NAME": "test project",
            "AUTHOR": "John Doe"
        }
        
        success, message = manager.create_from_template(
            "test-template",
            dest,
            config
        )
        
        assert success is False
        assert "invalid" in message.lower()
    
    def test_create_from_template_already_exists(self, temp_dirs, sample_template):
        """Test creating project in existing directory."""
        builtin_dir, custom_dir = temp_dirs
        manager = TemplateManager(builtin_dir=builtin_dir, custom_dir=custom_dir)
        
        # Create template
        template_path = builtin_dir / "test-template.json"
        with open(template_path, 'w') as f:
            json.dump(sample_template, f)
        
        # Create destination directory
        dest = Path(tempfile.mkdtemp())
        
        try:
            config = {
                "PROJECT_NAME": "test-project",
                "AUTHOR": "John Doe"
            }
            
            success, message = manager.create_from_template(
                "test-template",
                dest,
                config
            )
            
            assert success is False
            assert "already exists" in message.lower()
            
        finally:
            # Cleanup
            if dest.exists():
                shutil.rmtree(dest, ignore_errors=True)
    
    def test_merge_config_with_defaults(self, sample_template):
        """Test merging user config with template defaults."""
        manager = TemplateManager()
        
        config = {"PROJECT_NAME": "my-app"}
        
        merged = manager._merge_config_with_defaults(sample_template, config)
        
        assert merged["PROJECT_NAME"] == "my-app"
        assert merged["AUTHOR"] == "Test Author"  # Default value
    
    def test_is_binary_content(self):
        """Test binary content detection."""
        manager = TemplateManager()
        
        # Text content
        assert manager._is_binary_content("Hello World") is False
        assert manager._is_binary_content("print('test')") is False
        
        # Binary-like content (null bytes)
        assert manager._is_binary_content("Hello\x00World") is True
        
        # Mostly non-printable
        binary_like = "\x01\x02\x03\x04\x05"
        assert manager._is_binary_content(binary_like) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
