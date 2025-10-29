"""
Project Template Management System

Provides template-based project scaffolding for creating new projects
from predefined templates. Supports variable substitution, custom templates,
and cross-platform compatibility.
"""

import json
import os
import re
import shutil
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from string import Template


class TemplateManager:
    """
    Manages project templates for scaffolding new projects.
    
    Features:
    - List and retrieve built-in and custom templates
    - Create projects from templates with variable substitution
    - Add custom user templates
    - Validate template structure
    - Cross-platform support
    
    Example:
        >>> manager = TemplateManager()
        >>> templates = manager.list_templates()
        >>> config = {
        ...     "PROJECT_NAME": "my-app",
        ...     "AUTHOR": "John Doe",
        ...     "DESCRIPTION": "My awesome app"
        ... }
        >>> success = manager.create_from_template(
        ...     "web-react",
        ...     Path("./my-app"),
        ...     config
        ... )
    """
    
    def __init__(self, builtin_dir: Optional[Path] = None, custom_dir: Optional[Path] = None):
        """
        Initialize the template manager.
        
        Args:
            builtin_dir: Path to built-in templates (defaults to package templates/)
            custom_dir: Path to custom templates (defaults to data/project_templates/)
        """
        # Set default directories
        if builtin_dir is None:
            self.builtin_dir = Path(__file__).parent / "templates"
        else:
            self.builtin_dir = builtin_dir
            
        if custom_dir is None:
            # Assume project root is 3 levels up from this file
            project_root = Path(__file__).parent.parent.parent.parent
            self.custom_dir = project_root / "data" / "project_templates"
        else:
            self.custom_dir = custom_dir
        
        # Create custom directory if it doesn't exist
        self.custom_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache for loaded templates
        self._template_cache: Dict[str, Dict] = {}
        
        # Initialize mimetypes for binary detection
        mimetypes.init()
    
    def list_templates(self) -> List[Dict]:
        """
        List all available templates (built-in and custom).
        
        Returns:
            List of template info dictionaries with keys:
            - name: Template name
            - description: Template description
            - version: Template version
            - source: 'builtin' or 'custom'
            - path: Path to template file
        
        Example:
            >>> manager = TemplateManager()
            >>> templates = manager.list_templates()
            >>> for t in templates:
            ...     print(f"{t['name']}: {t['description']}")
        """
        templates = []
        
        # Load built-in templates
        if self.builtin_dir.exists():
            for template_file in self.builtin_dir.glob("*.json"):
                try:
                    template = self._load_template_file(template_file)
                    templates.append({
                        "name": template.get("name", template_file.stem),
                        "description": template.get("description", ""),
                        "version": template.get("version", "1.0.0"),
                        "source": "builtin",
                        "path": str(template_file)
                    })
                except Exception as e:
                    print(f"Warning: Failed to load template {template_file}: {e}")
        
        # Load custom templates
        if self.custom_dir.exists():
            for template_file in self.custom_dir.glob("*.json"):
                try:
                    template = self._load_template_file(template_file)
                    templates.append({
                        "name": template.get("name", template_file.stem),
                        "description": template.get("description", ""),
                        "version": template.get("version", "1.0.0"),
                        "source": "custom",
                        "path": str(template_file)
                    })
                except Exception as e:
                    print(f"Warning: Failed to load template {template_file}: {e}")
        
        return templates
    
    def get_template(self, name: str) -> Optional[Dict]:
        """
        Get a template by name.
        
        Args:
            name: Template name (without .json extension)
        
        Returns:
            Template dictionary or None if not found
        
        Example:
            >>> manager = TemplateManager()
            >>> template = manager.get_template("web-react")
            >>> print(template['description'])
        """
        # Check cache first
        if name in self._template_cache:
            return self._template_cache[name]
        
        # Search in built-in templates
        builtin_path = self.builtin_dir / f"{name}.json"
        if builtin_path.exists():
            template = self._load_template_file(builtin_path)
            self._template_cache[name] = template
            return template
        
        # Search in custom templates
        custom_path = self.custom_dir / f"{name}.json"
        if custom_path.exists():
            template = self._load_template_file(custom_path)
            self._template_cache[name] = template
            return template
        
        return None
    
    def create_from_template(
        self, 
        name: str, 
        dest: Path, 
        config: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Create a new project from a template.
        
        Args:
            name: Template name
            dest: Destination directory for the new project
            config: Variable values for template substitution
        
        Returns:
            Tuple of (success: bool, message: str)
        
        Example:
            >>> manager = TemplateManager()
            >>> success, msg = manager.create_from_template(
            ...     "web-react",
            ...     Path("./my-app"),
            ...     {"PROJECT_NAME": "my-app", "AUTHOR": "John"}
            ... )
            >>> if success:
            ...     print("Project created successfully!")
        """
        # Get template
        template = self.get_template(name)
        if template is None:
            return False, f"Template '{name}' not found"
        
        # Validate template
        is_valid, errors = self.validate_template(template)
        if not is_valid:
            return False, f"Invalid template: {', '.join(errors)}"
        
        # Validate project name
        project_name = config.get("PROJECT_NAME", "")
        if not self._is_valid_project_name(project_name):
            return False, "Invalid project name. Use only alphanumeric characters, hyphens, and underscores."
        
        # Check if destination exists
        if dest.exists():
            return False, f"Destination '{dest}' already exists"
        
        try:
            # Create destination directory
            dest.mkdir(parents=True, exist_ok=True)
            
            # Merge config with template defaults
            variables = self._merge_config_with_defaults(template, config)
            
            # Create files from template
            files = template.get("files", {})
            for rel_path, content in files.items():
                file_path = dest / rel_path
                
                # Create parent directories
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Substitute variables in path
                file_path_str = str(file_path)
                for var_name, var_value in variables.items():
                    file_path_str = file_path_str.replace(f"{{{{{var_name}}}}}", str(var_value))
                file_path = Path(file_path_str)
                
                # Check if content should be treated as binary
                if self._is_binary_content(content):
                    # Write as binary
                    file_path.write_bytes(content.encode('latin-1'))
                else:
                    # Substitute variables in content
                    substituted_content = self._substitute_variables(content, variables)
                    
                    # Write file
                    file_path.write_text(substituted_content, encoding='utf-8')
            
            # Execute post-creation commands if any
            commands = template.get("commands", [])
            if commands:
                print(f"\nPost-creation commands for '{name}':")
                for cmd in commands:
                    print(f"  - {cmd}")
                print("\nNote: Please run these commands manually in your project directory.")
            
            return True, f"Project created successfully at {dest}"
            
        except Exception as e:
            # Rollback on failure
            if dest.exists():
                shutil.rmtree(dest, ignore_errors=True)
            return False, f"Failed to create project: {str(e)}"
    
    def add_custom_template(self, template_path: Path) -> Tuple[bool, str]:
        """
        Add a custom template from a file.
        
        Args:
            template_path: Path to the template JSON file
        
        Returns:
            Tuple of (success: bool, message: str)
        
        Example:
            >>> manager = TemplateManager()
            >>> success, msg = manager.add_custom_template(
            ...     Path("./my-template.json")
            ... )
        """
        if not template_path.exists():
            return False, f"Template file '{template_path}' not found"
        
        try:
            # Load and validate template
            template = self._load_template_file(template_path)
            is_valid, errors = self.validate_template(template)
            
            if not is_valid:
                return False, f"Invalid template: {', '.join(errors)}"
            
            # Copy to custom templates directory
            template_name = template.get("name", template_path.stem)
            dest_path = self.custom_dir / f"{template_name}.json"
            
            shutil.copy2(template_path, dest_path)
            
            # Clear cache
            if template_name in self._template_cache:
                del self._template_cache[template_name]
            
            return True, f"Template '{template_name}' added successfully"
            
        except Exception as e:
            return False, f"Failed to add template: {str(e)}"
    
    def validate_template(self, template: Dict) -> Tuple[bool, List[str]]:
        """
        Validate template structure.
        
        Args:
            template: Template dictionary to validate
        
        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        
        Example:
            >>> manager = TemplateManager()
            >>> template = {"name": "test", "files": {}}
            >>> is_valid, errors = manager.validate_template(template)
            >>> if not is_valid:
            ...     print("Errors:", errors)
        """
        errors = []
        
        # Check required fields
        if "name" not in template:
            errors.append("Missing required field: 'name'")
        elif not isinstance(template["name"], str):
            errors.append("'name' must be a string")
        
        if "files" not in template:
            errors.append("Missing required field: 'files'")
        elif not isinstance(template["files"], dict):
            errors.append("'files' must be a dictionary")
        
        # Check optional fields
        if "variables" in template:
            if not isinstance(template["variables"], dict):
                errors.append("'variables' must be a dictionary")
            else:
                # Validate variable definitions
                for var_name, var_def in template["variables"].items():
                    if not isinstance(var_def, dict):
                        errors.append(f"Variable '{var_name}' definition must be a dictionary")
                    else:
                        if "type" not in var_def:
                            errors.append(f"Variable '{var_name}' missing 'type' field")
        
        if "commands" in template:
            if not isinstance(template["commands"], list):
                errors.append("'commands' must be a list")
            else:
                for i, cmd in enumerate(template["commands"]):
                    if not isinstance(cmd, str):
                        errors.append(f"Command at index {i} must be a string")
        
        # Check file paths
        if "files" in template and isinstance(template["files"], dict):
            for file_path in template["files"].keys():
                # Check for invalid characters
                if "\\" in file_path:
                    errors.append(f"File path '{file_path}' should use forward slashes")
                
                # Check for absolute paths
                if file_path.startswith("/") or (len(file_path) > 1 and file_path[1] == ":"):
                    errors.append(f"File path '{file_path}' should be relative")
        
        return len(errors) == 0, errors
    
    def _load_template_file(self, path: Path) -> Dict:
        """Load a template from a JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _is_valid_project_name(self, name: str) -> bool:
        """
        Check if project name is valid.
        
        Valid names contain only:
        - Alphanumeric characters
        - Hyphens (-)
        - Underscores (_)
        """
        if not name:
            return False
        
        # Check pattern
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, name))
    
    def _merge_config_with_defaults(self, template: Dict, config: Dict) -> Dict:
        """
        Merge user config with template variable defaults.
        
        Args:
            template: Template dictionary
            config: User configuration
        
        Returns:
            Merged variables dictionary
        """
        variables = {}
        template_vars = template.get("variables", {})
        
        # Process each template variable
        for var_name, var_def in template_vars.items():
            if var_name in config:
                variables[var_name] = config[var_name]
            elif "default" in var_def:
                variables[var_name] = var_def["default"]
            elif var_def.get("required", False):
                raise ValueError(f"Required variable '{var_name}' not provided")
            else:
                variables[var_name] = ""
        
        # Add any extra config variables not in template
        for var_name, var_value in config.items():
            if var_name not in variables:
                variables[var_name] = var_value
        
        return variables
    
    def _substitute_variables(self, content: str, variables: Dict) -> str:
        """
        Substitute variables in content using {{VARIABLE}} syntax.
        
        Args:
            content: Content with variable placeholders
            variables: Dictionary of variable values
        
        Returns:
            Content with substituted variables
        """
        result = content
        for var_name, var_value in variables.items():
            # Replace {{VARIABLE}} with value
            result = result.replace(f"{{{{{var_name}}}}}", str(var_value))
        
        return result
    
    def _is_binary_content(self, content: str) -> bool:
        """
        Check if content should be treated as binary.
        
        This is a simple heuristic - if content contains null bytes
        or many non-printable characters, treat as binary.
        """
        if not content:
            return False
        
        # Check for null bytes
        if '\x00' in content:
            return True
        
        # Check ratio of printable characters
        printable_chars = sum(1 for c in content if c.isprintable() or c in '\n\r\t')
        total_chars = len(content)
        
        if total_chars == 0:
            return False
        
        printable_ratio = printable_chars / total_chars
        
        # If less than 95% printable, consider binary
        return printable_ratio < 0.95


# Example usage and testing
if __name__ == "__main__":
    # Create template manager
    manager = TemplateManager()
    
    # List templates
    print("Available templates:")
    for template in manager.list_templates():
        print(f"  - {template['name']}: {template['description']} ({template['source']})")
    
    # Example: Create project from template
    # config = {
    #     "PROJECT_NAME": "my-awesome-app",
    #     "AUTHOR": "John Doe",
    #     "DESCRIPTION": "A test application"
    # }
    # success, message = manager.create_from_template("web-react", Path("./test-project"), config)
    # print(f"\nCreate project: {message}")
