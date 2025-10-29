"""
Project Management Tool - Manages project state, global memory, and TODO tracking.

This tool provides project-level context management including:
- Global memory and state tracking
- TODO list management
- Project structure tracking
- Preference management
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from datetime import datetime

from .base import Tool


class ProjectManagementTool(Tool):
    """
    Tool for managing project-level state and memory.
    
    Capabilities:
    - Save and load project memory
    - Manage TODO lists
    - Track project structure
    - Store user preferences
    - Maintain global project state
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the project management tool.
        
        Args:
            config: Configuration dictionary with optional:
                - project_root: Root directory of the project (default: current directory)
                - memory_file: Path to global memory file
        """
        super().__init__(
            name='project_management',
            description='Project-level state and memory management',
            config=config
        )
        
        self.project_root = Path(self.config.get('project_root', '.'))
        self.memory_dir = self.project_root / '.project' / 'memory'
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.global_memory_file = self.memory_dir / 'global_memory.json'
        self.todos_file = self.memory_dir / 'todos.json'
        self.preferences_file = self.memory_dir / 'preferences.json'
        self.structure_file = self.memory_dir / 'project_structure.json'
    
    def invoke(self, params: Dict[str, Any]) -> Any:
        """
        Execute project management operation.
        
        Args:
            params: Dictionary with:
                - action: Operation to perform (save_memory, load_memory, save_todo,
                         load_todo, save_preference, load_preference, save_structure,
                         load_structure, list_todos, clear_memory)
                - Additional action-specific parameters
                
        Returns:
            Operation result
        """
        self._log_invocation(params)
        
        action = params.get('action')
        if not action:
            raise ValueError("Parameter 'action' is required")
        
        # Route to appropriate method
        if action == 'save_memory':
            return self._save_memory(
                params.get('key'),
                params.get('data')
            )
        elif action == 'load_memory':
            return self._load_memory(params.get('key'))
        elif action == 'save_todo':
            return self._save_todo(
                params.get('name'),
                params.get('todos')
            )
        elif action == 'load_todo':
            return self._load_todo(params.get('name'))
        elif action == 'list_todos':
            return self._list_todos()
        elif action == 'save_preference':
            return self._save_preference(
                params.get('key'),
                params.get('value')
            )
        elif action == 'load_preference':
            return self._load_preference(params.get('key'))
        elif action == 'save_structure':
            return self._save_structure(params.get('structure'))
        elif action == 'load_structure':
            return self._load_structure()
        elif action == 'clear_memory':
            return self._clear_memory(params.get('key'))
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _save_memory(self, key: str, data: Any) -> Dict[str, Any]:
        """Save data to global memory."""
        if not key:
            raise ValueError("Parameter 'key' is required for save_memory")
        
        # Load existing memory
        memory = self._load_global_memory()
        
        # Update with new data
        memory[key] = {
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Save back
        with open(self.global_memory_file, 'w') as f:
            json.dump(memory, f, indent=2)
        
        self.logger.info(f"Saved memory for key: {key}")
        
        return {
            'success': True,
            'key': key,
            'timestamp': memory[key]['timestamp']
        }
    
    def _load_memory(self, key: Optional[str] = None) -> Any:
        """Load data from global memory."""
        memory = self._load_global_memory()
        
        if key:
            entry = memory.get(key)
            if entry:
                return {
                    'success': True,
                    'key': key,
                    'data': entry.get('data'),
                    'timestamp': entry.get('timestamp')
                }
            else:
                return {
                    'success': False,
                    'key': key,
                    'error': 'Key not found'
                }
        else:
            # Return all memory
            return {
                'success': True,
                'memory': memory
            }
    
    def _load_global_memory(self) -> Dict[str, Any]:
        """Load the entire global memory file."""
        if self.global_memory_file.exists():
            with open(self.global_memory_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_todo(self, name: str, todos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Save TODO list."""
        if not name:
            raise ValueError("Parameter 'name' is required for save_todo")
        if not todos:
            raise ValueError("Parameter 'todos' is required for save_todo")
        
        # Load existing todos
        all_todos = self._load_all_todos()
        
        # Update with new todos
        all_todos[name] = {
            'todos': todos,
            'updated_at': datetime.now().isoformat()
        }
        
        # Save back
        with open(self.todos_file, 'w') as f:
            json.dump(all_todos, f, indent=2)
        
        self.logger.info(f"Saved TODO list: {name}")
        
        return {
            'success': True,
            'name': name,
            'count': len(todos)
        }
    
    def _load_todo(self, name: str) -> Any:
        """Load TODO list by name."""
        if not name:
            raise ValueError("Parameter 'name' is required for load_todo")
        
        all_todos = self._load_all_todos()
        todo_entry = all_todos.get(name)
        
        if todo_entry:
            return {
                'success': True,
                'name': name,
                'todos': todo_entry.get('todos', []),
                'updated_at': todo_entry.get('updated_at')
            }
        else:
            return {
                'success': False,
                'name': name,
                'error': 'TODO list not found'
            }
    
    def _list_todos(self) -> Dict[str, Any]:
        """List all TODO lists."""
        all_todos = self._load_all_todos()
        
        todo_list = []
        for name, entry in all_todos.items():
            todo_list.append({
                'name': name,
                'count': len(entry.get('todos', [])),
                'updated_at': entry.get('updated_at')
            })
        
        return {
            'success': True,
            'todos': todo_list
        }
    
    def _load_all_todos(self) -> Dict[str, Any]:
        """Load all TODO lists from file."""
        if self.todos_file.exists():
            with open(self.todos_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_preference(self, key: str, value: Any) -> Dict[str, Any]:
        """Save user preference."""
        if not key:
            raise ValueError("Parameter 'key' is required for save_preference")
        
        # Load existing preferences
        preferences = self._load_all_preferences()
        
        # Update with new preference
        preferences[key] = {
            'value': value,
            'updated_at': datetime.now().isoformat()
        }
        
        # Save back
        with open(self.preferences_file, 'w') as f:
            json.dump(preferences, f, indent=2)
        
        self.logger.info(f"Saved preference: {key}")
        
        return {
            'success': True,
            'key': key
        }
    
    def _load_preference(self, key: str) -> Any:
        """Load user preference."""
        if not key:
            raise ValueError("Parameter 'key' is required for load_preference")
        
        preferences = self._load_all_preferences()
        pref_entry = preferences.get(key)
        
        if pref_entry:
            return {
                'success': True,
                'key': key,
                'value': pref_entry.get('value'),
                'updated_at': pref_entry.get('updated_at')
            }
        else:
            return {
                'success': False,
                'key': key,
                'error': 'Preference not found'
            }
    
    def _load_all_preferences(self) -> Dict[str, Any]:
        """Load all preferences from file."""
        if self.preferences_file.exists():
            with open(self.preferences_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_structure(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Save project structure information."""
        if not structure:
            raise ValueError("Parameter 'structure' is required for save_structure")
        
        structure_data = {
            'structure': structure,
            'updated_at': datetime.now().isoformat()
        }
        
        with open(self.structure_file, 'w') as f:
            json.dump(structure_data, f, indent=2)
        
        self.logger.info("Saved project structure")
        
        return {
            'success': True,
            'updated_at': structure_data['updated_at']
        }
    
    def _load_structure(self) -> Dict[str, Any]:
        """Load project structure information."""
        if self.structure_file.exists():
            with open(self.structure_file, 'r') as f:
                data = json.load(f)
                return {
                    'success': True,
                    'structure': data.get('structure', {}),
                    'updated_at': data.get('updated_at')
                }
        else:
            return {
                'success': False,
                'error': 'Project structure not found'
            }
    
    def _clear_memory(self, key: Optional[str] = None) -> Dict[str, Any]:
        """Clear memory entry or entire memory."""
        if key:
            # Clear specific key
            memory = self._load_global_memory()
            if key in memory:
                del memory[key]
                with open(self.global_memory_file, 'w') as f:
                    json.dump(memory, f, indent=2)
                self.logger.info(f"Cleared memory for key: {key}")
                return {'success': True, 'key': key}
            else:
                return {'success': False, 'key': key, 'error': 'Key not found'}
        else:
            # Clear all memory
            with open(self.global_memory_file, 'w') as f:
                json.dump({}, f, indent=2)
            self.logger.info("Cleared all memory")
            return {'success': True, 'cleared': 'all'}
