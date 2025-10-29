"""
Important Files Manager

This module provides utilities for managing important project documentation files
that should be kept up-to-date across all code projects managed by the AI Agent Console.

It loads the configuration from important_project_files.yaml and provides helper
methods for agents to:
- Check which files should exist in a project
- Get file templates
- Determine when files need updating
- Get list of files by category or priority
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class ImportantFilesManager:
    """
    Manager for important project documentation files.
    
    This class loads and provides access to the configuration of important
    files that should be maintained in all code projects.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the important files manager.
        
        Args:
            config_path: Path to important_project_files.yaml (default: auto-detect)
        """
        if config_path is None:
            # Auto-detect config path
            console_root = Path(__file__).parent.parent
            config_path = console_root / "config" / "important_project_files.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"Loaded important files configuration from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load important files config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if file loading fails."""
        return {
            'core_documentation': [
                {'name': 'README.md', 'required': True, 'location': 'root'},
                {'name': 'CHANGELOG.md', 'required': True, 'location': 'root'},
                {'name': 'VERSION', 'required': True, 'location': 'root'},
            ],
            'auto_update_settings': {
                'create_on_init': ['README.md', 'VERSION', 'TODO.md'],
                'update_priorities': {
                    'critical': ['README.md', 'CHANGELOG.md', 'VERSION']
                }
            }
        }
    
    def get_all_important_files(self) -> List[Dict[str, Any]]:
        """
        Get list of all important files across all categories.
        
        Returns:
            List of file definitions with name, description, required, location, etc.
        """
        all_files = []
        
        # Iterate through all category keys
        for key, value in self.config.items():
            if isinstance(value, list):
                # This is a category of files
                for file_def in value:
                    if isinstance(file_def, dict) and 'name' in file_def:
                        file_def['category'] = key
                        all_files.append(file_def)
        
        return all_files
    
    def get_required_files(self) -> List[str]:
        """
        Get list of required file names.
        
        Returns:
            List of file names that are marked as required
        """
        all_files = self.get_all_important_files()
        return [f['name'] for f in all_files if f.get('required', False)]
    
    def get_files_to_create_on_init(self) -> List[str]:
        """
        Get list of files that should be created on project initialization.
        
        Returns:
            List of file names to create
        """
        settings = self.config.get('auto_update_settings', {})
        return settings.get('create_on_init', [])
    
    def get_files_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get files in a specific category.
        
        Args:
            category: Category name (e.g., 'core_documentation', 'planning_files')
            
        Returns:
            List of file definitions in the category
        """
        return self.config.get(category, [])
    
    def get_files_by_priority(self, priority: str) -> List[str]:
        """
        Get files by update priority.
        
        Args:
            priority: Priority level ('critical', 'high', 'medium', 'low')
            
        Returns:
            List of file names with the specified priority
        """
        settings = self.config.get('auto_update_settings', {})
        priorities = settings.get('update_priorities', {})
        return priorities.get(priority, [])
    
    def get_critical_files(self) -> List[str]:
        """Get list of critical files that must always be up-to-date."""
        return self.get_files_by_priority('critical')
    
    def get_file_template(self, filename: str, **template_vars) -> Optional[str]:
        """
        Get template content for a file.
        
        Args:
            filename: Name of the file
            **template_vars: Variables to substitute in template
            
        Returns:
            Template content with variables substituted, or None if no template
        """
        templates = self.config.get('minimal_templates', {})
        template = templates.get(filename)
        
        if template:
            # Simple template variable substitution
            for key, value in template_vars.items():
                placeholder = f"{{{{{key}}}}}"
                template = template.replace(placeholder, str(value))
            
            # Replace date if not provided
            if '{{date}}' in template:
                template = template.replace('{{date}}', datetime.now().strftime('%Y-%m-%d'))
        
        return template
    
    def get_file_location(self, filename: str) -> Optional[str]:
        """
        Get the expected location for a file.
        
        Args:
            filename: Name of the file
            
        Returns:
            Location string ('root', 'docs', '.project_ai') or None
        """
        all_files = self.get_all_important_files()
        for file_def in all_files:
            if file_def['name'] == filename:
                return file_def.get('location', 'root')
        return None
    
    def get_file_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get complete information about a file.
        
        Args:
            filename: Name of the file
            
        Returns:
            File definition dictionary or None if not found
        """
        all_files = self.get_all_important_files()
        for file_def in all_files:
            if file_def['name'] == filename:
                return file_def
        return None
    
    def should_update_file(self, filename: str, last_update: datetime, 
                          trigger_event: str) -> bool:
        """
        Determine if a file should be updated based on frequency and trigger event.
        
        Args:
            filename: Name of the file
            last_update: When the file was last updated
            trigger_event: Event that might trigger an update
            
        Returns:
            True if file should be updated
        """
        file_info = self.get_file_info(filename)
        if not file_info:
            return False
        
        # Check if trigger event matches update frequency
        update_freq = file_info.get('update_frequency', 'as_needed')
        
        settings = self.config.get('auto_update_settings', {})
        trigger_events = settings.get('trigger_events', [])
        
        # If the event is in our trigger list, check frequency requirements
        if trigger_event not in trigger_events:
            return False
        
        # Map trigger events to frequencies
        event_frequency_map = {
            'project_initialization': ['every_major_change', 'every_version', 
                                      'every_feature_release', 'as_needed'],
            'major_feature_addition': ['every_major_change', 'every_feature_release', 'as_needed'],
            'version_bump': ['every_version', 'as_needed'],
            'architecture_change': ['when_architecture_changes', 'when_structure_changes', 'as_needed'],
            'before_commit': ['daily', 'as_needed']
        }
        
        matching_frequencies = event_frequency_map.get(trigger_event, [])
        return update_freq in matching_frequencies
    
    def get_responsible_agents(self) -> List[str]:
        """
        Get list of agents responsible for updating important files.
        
        Returns:
            List of agent names
        """
        settings = self.config.get('auto_update_settings', {})
        return settings.get('responsible_agents', [])
    
    def export_checklist(self, project_path: Path) -> str:
        """
        Generate a checklist of important files for a project.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Markdown checklist of files
        """
        all_files = self.get_all_important_files()
        checklist = ["# Important Project Files Checklist\n\n"]
        checklist.append(f"Project: {project_path}\n")
        checklist.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Group by category
        categories = {}
        for file_def in all_files:
            category = file_def.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append(file_def)
        
        for category, files in categories.items():
            checklist.append(f"## {category.replace('_', ' ').title()}\n\n")
            
            for file_def in files:
                filename = file_def['name']
                location = file_def.get('location', 'root')
                required = file_def.get('required', False)
                
                # Check if file exists
                file_path = project_path / location / filename
                if location == 'root':
                    file_path = project_path / filename
                elif location == 'docs':
                    file_path = project_path / 'docs' / filename
                elif location == '.project_ai':
                    file_path = project_path / '.project_ai' / filename
                
                exists = file_path.exists()
                checkbox = "[x]" if exists else "[ ]"
                req_marker = "**[REQUIRED]**" if required else ""
                
                checklist.append(f"- {checkbox} {filename} {req_marker}\n")
                checklist.append(f"  - Description: {file_def.get('description', 'N/A')}\n")
                checklist.append(f"  - Location: `{location}/`\n")
                checklist.append(f"  - Status: {'✓ Exists' if exists else '✗ Missing'}\n\n")
        
        return ''.join(checklist)


# Singleton instance for convenience
_manager_instance = None


def get_manager() -> ImportantFilesManager:
    """Get singleton instance of ImportantFilesManager."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ImportantFilesManager()
    return _manager_instance


# Convenience functions
def get_important_files() -> List[Dict[str, Any]]:
    """Get list of all important files."""
    return get_manager().get_all_important_files()


def get_required_files() -> List[str]:
    """Get list of required file names."""
    return get_manager().get_required_files()


def get_init_files() -> List[str]:
    """Get files to create on initialization."""
    return get_manager().get_files_to_create_on_init()


def get_file_template(filename: str, **kwargs) -> Optional[str]:
    """Get template for a file."""
    return get_manager().get_file_template(filename, **kwargs)


def export_checklist(project_path: Path) -> str:
    """Export checklist for a project."""
    return get_manager().export_checklist(project_path)
