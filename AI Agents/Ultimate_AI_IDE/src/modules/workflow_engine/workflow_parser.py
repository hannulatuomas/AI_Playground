"""
Workflow Parser

Parses workflow definitions from YAML and JSON formats.
"""

import yaml
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class WorkflowParser:
    """Parse workflow definitions from YAML/JSON"""
    
    def __init__(self):
        """Initialize workflow parser"""
        self.supported_formats = ['.yaml', '.yml', '.json']
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse workflow from file
        
        Args:
            file_path: Path to workflow file
            
        Returns:
            Parsed workflow dictionary
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Workflow file not found: {file_path}")
        
        if path.suffix not in self.supported_formats:
            raise ValueError(f"Unsupported format: {path.suffix}")
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                return self._parse_yaml(f.read())
            elif path.suffix == '.json':
                return self._parse_json(f.read())
    
    def parse_string(self, content: str, format: str = 'yaml') -> Dict[str, Any]:
        """
        Parse workflow from string
        
        Args:
            content: Workflow content
            format: Format (yaml or json)
            
        Returns:
            Parsed workflow dictionary
        """
        if format.lower() in ['yaml', 'yml']:
            return self._parse_yaml(content)
        elif format.lower() == 'json':
            return self._parse_json(content)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _parse_yaml(self, content: str) -> Dict[str, Any]:
        """Parse YAML content"""
        try:
            workflow = yaml.safe_load(content)
            return self._validate_workflow(workflow)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")
    
    def _parse_json(self, content: str) -> Dict[str, Any]:
        """Parse JSON content"""
        try:
            workflow = json.loads(content)
            return self._validate_workflow(workflow)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    
    def _validate_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate workflow structure
        
        Args:
            workflow: Workflow dictionary
            
        Returns:
            Validated workflow
        """
        required_fields = ['name', 'steps']
        
        for field in required_fields:
            if field not in workflow:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(workflow['steps'], list):
            raise ValueError("Steps must be a list")
        
        if not workflow['steps']:
            raise ValueError("Workflow must have at least one step")
        
        # Validate each step
        for i, step in enumerate(workflow['steps']):
            self._validate_step(step, i)
        
        # Set defaults
        workflow.setdefault('description', '')
        workflow.setdefault('version', '1.0')
        workflow.setdefault('on_error', 'stop')  # stop, continue, rollback
        workflow.setdefault('variables', {})
        
        return workflow
    
    def _validate_step(self, step: Dict[str, Any], index: int):
        """Validate individual step"""
        if not isinstance(step, dict):
            raise ValueError(f"Step {index} must be a dictionary")
        
        if 'action' not in step:
            raise ValueError(f"Step {index} missing 'action' field")
        
        # Set step defaults
        step.setdefault('name', f"Step {index + 1}")
        step.setdefault('description', '')
        step.setdefault('depends_on', [])
        step.setdefault('on_failure', 'stop')  # stop, continue, retry
        step.setdefault('retry_count', 0)
        step.setdefault('timeout', None)
        step.setdefault('params', {})
    
    def get_dependencies(self, workflow: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Extract dependency graph from workflow
        
        Args:
            workflow: Workflow dictionary
            
        Returns:
            Dictionary mapping step names to their dependencies
        """
        dependencies = {}
        
        for step in workflow['steps']:
            step_name = step['name']
            depends_on = step.get('depends_on', [])
            dependencies[step_name] = depends_on if isinstance(depends_on, list) else [depends_on]
        
        return dependencies
    
    def validate_dependencies(self, workflow: Dict[str, Any]) -> bool:
        """
        Validate that all dependencies exist and there are no cycles
        
        Args:
            workflow: Workflow dictionary
            
        Returns:
            True if valid
        """
        dependencies = self.get_dependencies(workflow)
        step_names = set(dependencies.keys())
        
        # Check all dependencies exist
        for step_name, deps in dependencies.items():
            for dep in deps:
                if dep not in step_names:
                    raise ValueError(f"Step '{step_name}' depends on non-existent step '{dep}'")
        
        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for dep in dependencies.get(node, []):
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for step_name in step_names:
            if step_name not in visited:
                if has_cycle(step_name):
                    raise ValueError(f"Circular dependency detected involving '{step_name}'")
        
        return True
