"""
Project Scaffolding System

Handles the creation of projects from templates with variable substitution,
file generation, and initialization command execution. Follows Zero-Bloat
principles by delegating template management to TemplateManager.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ProjectScaffolder:
    """
    Scaffolds projects from templates with zero bloat.
    
    Delegates template management to TemplateManager and focuses solely on:
    - Creating directory structures
    - Generating files with variable substitution
    - Running initialization commands
    - Error handling and rollback
    
    Example:
        >>> from src.features.project_lifecycle import TemplateManager, ProjectScaffolder
        >>> 
        >>> manager = TemplateManager()
        >>> scaffolder = ProjectScaffolder()
        >>> 
        >>> template = manager.get_template("web-react")
        >>> config = {"PROJECT_NAME": "my-app", "AUTHOR": "John Doe"}
        >>> 
        >>> success, message = scaffolder.scaffold_project(
        ...     template, Path("./my-app"), config
        ... )
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the scaffolder.
        
        Args:
            verbose: Enable verbose logging output
        """
        self.verbose = verbose
        self._created_paths: List[Path] = []  # Track for rollback
    
    def scaffold_project(
        self,
        template: Dict[str, Any],
        dest: Path,
        config: Dict[str, Any],
        overwrite: bool = False
    ) -> Tuple[bool, str]:
        """
        Scaffold a complete project from a template.
        
        Args:
            template: Template dictionary (from TemplateManager)
            dest: Destination directory path
            config: Variable configuration dictionary
            overwrite: Allow overwriting existing directory
        
        Returns:
            Tuple of (success: bool, message: str)
        
        Example:
            >>> template = {"name": "example", "files": {...}, "variables": {...}}
            >>> success, msg = scaffolder.scaffold_project(
            ...     template, Path("./my-project"), {"PROJECT_NAME": "my-project"}
            ... )
        """
        self._created_paths = []  # Reset tracking
        
        try:
            # Step 1: Validate inputs
            if not self._validate_inputs(template, dest, config, overwrite):
                return False, "Validation failed"
            
            # Step 2: Merge config with defaults
            variables = self._merge_config_with_defaults(template, config)
            
            # Step 3: Validate required variables
            is_valid, missing = self._validate_required_variables(template, variables)
            if not is_valid:
                return False, f"Missing required variables: {', '.join(missing)}"
            
            # Step 4: Create destination directory
            if not self._create_destination(dest, overwrite):
                return False, f"Failed to create destination: {dest}"
            
            # Step 5: Create files from template
            files = template.get("files", {})
            if not self._create_files(files, dest, variables):
                self._rollback(dest)
                return False, "Failed to create files"
            
            # Step 6: Run initialization commands (optional)
            commands = template.get("commands", [])
            if commands:
                success, cmd_message = self._run_init_commands(commands, dest)
                if not success:
                    # Commands are optional, so just warn
                    logger.warning(f"Some commands failed: {cmd_message}")
            
            return True, f"Project scaffolded successfully at {dest}"
            
        except Exception as e:
            logger.error(f"Scaffolding error: {e}", exc_info=True)
            self._rollback(dest)
            return False, f"Scaffolding failed: {str(e)}"
    
    def replace_variables(
        self,
        content: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        Replace {{VARIABLE}} placeholders with actual values.
        
        Args:
            content: Content with variable placeholders
            variables: Dictionary of variable values
        
        Returns:
            Content with variables replaced
        
        Example:
            >>> content = "Project: {{PROJECT_NAME}}, Author: {{AUTHOR}}"
            >>> variables = {"PROJECT_NAME": "my-app", "AUTHOR": "John"}
            >>> result = scaffolder.replace_variables(content, variables)
            >>> print(result)
            Project: my-app, Author: John
        """
        result = content
        
        # Replace all {{VARIABLE}} occurrences
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            result = result.replace(placeholder, str(var_value))
        
        return result
    
    def create_files(
        self,
        files: Dict[str, str],
        dest: Path,
        variables: Dict[str, Any]
    ) -> bool:
        """
        Create all files from the template.
        
        Args:
            files: Dictionary of {relative_path: content}
            dest: Destination directory
            variables: Variables for substitution
        
        Returns:
            True if successful, False otherwise
        
        Example:
            >>> files = {"README.md": "# {{PROJECT_NAME}}"}
            >>> variables = {"PROJECT_NAME": "my-app"}
            >>> success = scaffolder.create_files(files, Path("./project"), variables)
        """
        return self._create_files(files, dest, variables)
    
    def run_init_commands(
        self,
        commands: List[str],
        cwd: Path
    ) -> Tuple[bool, str]:
        """
        Run initialization commands in the project directory.
        
        Args:
            commands: List of commands to execute
            cwd: Working directory for command execution
        
        Returns:
            Tuple of (success: bool, message: str)
        
        Example:
            >>> commands = ["npm install", "git init"]
            >>> success, msg = scaffolder.run_init_commands(commands, Path("./my-app"))
        """
        return self._run_init_commands(commands, cwd)
    
    def rollback(self, dest: Path) -> bool:
        """
        Rollback project creation by removing all created files/directories.
        
        Args:
            dest: Project directory to remove
        
        Returns:
            True if rollback successful, False otherwise
        
        Example:
            >>> scaffolder.rollback(Path("./failed-project"))
        """
        return self._rollback(dest)
    
    # Private methods
    
    def _validate_inputs(
        self,
        template: Dict[str, Any],
        dest: Path,
        config: Dict[str, Any],
        overwrite: bool
    ) -> bool:
        """Validate all inputs before scaffolding."""
        # Check template has required fields
        if not isinstance(template, dict):
            logger.error("Template must be a dictionary")
            return False
        
        if "files" not in template:
            logger.error("Template missing 'files' field")
            return False
        
        # Check destination
        if dest.exists() and not overwrite:
            logger.error(f"Destination {dest} already exists. Use overwrite=True to replace.")
            return False
        
        # Check config is dict
        if not isinstance(config, dict):
            logger.error("Config must be a dictionary")
            return False
        
        return True
    
    def _merge_config_with_defaults(
        self,
        template: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge user config with template variable defaults."""
        variables = {}
        template_vars = template.get("variables", {})
        
        # Process each template variable
        for var_name, var_def in template_vars.items():
            if var_name in config:
                # Use user-provided value
                variables[var_name] = config[var_name]
            elif "default" in var_def:
                # Use default value
                variables[var_name] = var_def["default"]
            elif var_def.get("required", False):
                # Required but not provided - will be caught in validation
                pass
            else:
                # Optional with no default - use empty string
                variables[var_name] = ""
        
        # Add any extra variables from config not in template
        for var_name, var_value in config.items():
            if var_name not in variables:
                variables[var_name] = var_value
        
        return variables
    
    def _validate_required_variables(
        self,
        template: Dict[str, Any],
        variables: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Check all required variables are provided."""
        missing = []
        template_vars = template.get("variables", {})
        
        for var_name, var_def in template_vars.items():
            if var_def.get("required", False):
                if var_name not in variables or not variables[var_name]:
                    missing.append(var_name)
        
        return len(missing) == 0, missing
    
    def _create_destination(self, dest: Path, overwrite: bool) -> bool:
        """Create destination directory."""
        try:
            if dest.exists():
                if overwrite:
                    if self.verbose:
                        logger.info(f"Removing existing directory: {dest}")
                    shutil.rmtree(dest)
                else:
                    logger.error(f"Destination exists: {dest}")
                    return False
            
            dest.mkdir(parents=True, exist_ok=True)
            self._created_paths.append(dest)
            
            if self.verbose:
                logger.info(f"Created destination: {dest}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create destination: {e}")
            return False
    
    def _create_files(
        self,
        files: Dict[str, str],
        dest: Path,
        variables: Dict[str, Any]
    ) -> bool:
        """Create all files from template."""
        try:
            for rel_path, content in files.items():
                # Replace variables in file path
                file_path_str = self.replace_variables(str(rel_path), variables)
                file_path = dest / file_path_str
                
                # Create parent directories
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Track created directory
                if file_path.parent not in self._created_paths:
                    self._created_paths.append(file_path.parent)
                
                # Replace variables in content
                file_content = self.replace_variables(content, variables)
                
                # Write file
                file_path.write_text(file_content, encoding='utf-8')
                self._created_paths.append(file_path)
                
                if self.verbose:
                    logger.info(f"Created file: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create files: {e}", exc_info=True)
            return False
    
    def _run_init_commands(
        self,
        commands: List[str],
        cwd: Path
    ) -> Tuple[bool, str]:
        """
        Run initialization commands.
        
        NOTE: Commands are shown to user but NOT executed automatically
        for security reasons. This follows Zero-Bloat principles.
        """
        if not commands:
            return True, "No commands to run"
        
        # Don't execute commands automatically - security risk
        # Instead, inform user what to run
        messages = []
        messages.append(f"\nTo complete setup, run these commands in {cwd}:")
        
        for i, cmd in enumerate(commands, 1):
            # Replace variables in command
            # (Note: TemplateManager already does this, but for safety)
            messages.append(f"  {i}. {cmd}")
        
        message = "\n".join(messages)
        
        if self.verbose:
            logger.info("Initialization commands listed for user")
        
        return True, message
    
    def _rollback(self, dest: Path) -> bool:
        """Rollback by removing created files and directories."""
        try:
            if dest.exists():
                if self.verbose:
                    logger.info(f"Rolling back: removing {dest}")
                
                shutil.rmtree(dest, ignore_errors=True)
            
            self._created_paths = []
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False


# Convenience function for direct use
def scaffold_from_template(
    template_name: str,
    dest: Path,
    config: Dict[str, Any],
    overwrite: bool = False,
    verbose: bool = False
) -> Tuple[bool, str]:
    """
    Convenience function to scaffold a project from a template name.
    
    This combines TemplateManager and ProjectScaffolder for easy use.
    
    Args:
        template_name: Name of the template to use
        dest: Destination directory
        config: Variable configuration
        overwrite: Allow overwriting existing directory
        verbose: Enable verbose output
    
    Returns:
        Tuple of (success: bool, message: str)
    
    Example:
        >>> from src.features.project_lifecycle.scaffolding import scaffold_from_template
        >>> 
        >>> success, msg = scaffold_from_template(
        ...     "web-react",
        ...     Path("./my-app"),
        ...     {"PROJECT_NAME": "my-app", "AUTHOR": "John Doe"}
        ... )
        >>> print(msg)
    """
    from .templates import TemplateManager
    
    # Get template
    manager = TemplateManager()
    template = manager.get_template(template_name)
    
    if template is None:
        return False, f"Template '{template_name}' not found"
    
    # Validate template
    is_valid, errors = manager.validate_template(template)
    if not is_valid:
        return False, f"Invalid template: {', '.join(errors)}"
    
    # Scaffold project
    scaffolder = ProjectScaffolder(verbose=verbose)
    return scaffolder.scaffold_project(template, dest, config, overwrite)


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    # Example 1: Using ProjectScaffolder directly
    print("Example 1: Direct scaffolding")
    print("-" * 60)
    
    from .templates import TemplateManager
    
    manager = TemplateManager()
    scaffolder = ProjectScaffolder(verbose=True)
    
    template = manager.get_template("web-react")
    if template:
        config = {
            "PROJECT_NAME": "example-app",
            "AUTHOR": "Example Author",
            "DESCRIPTION": "An example application"
        }
        
        success, message = scaffolder.scaffold_project(
            template,
            Path("./example-app"),
            config
        )
        
        print(f"\nResult: {message}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Example 2: Using convenience function
    print("Example 2: Convenience function")
    print("-" * 60)
    
    success, message = scaffold_from_template(
        "cli-python",
        Path("./example-cli"),
        {
            "PROJECT_NAME": "example_cli",
            "AUTHOR": "Example Author",
            "EMAIL": "[email protected]"
        },
        verbose=True
    )
    
    print(f"\nResult: {message}")
