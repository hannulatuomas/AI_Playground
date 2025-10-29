"""
Workflow Engine

Main interface for workflow management and execution.
"""

import json
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import logging

from .workflow_parser import WorkflowParser
from .workflow_executor import WorkflowExecutor, StepStatus
from .workflow_templates import WorkflowTemplates


class WorkflowEngine:
    """Main workflow engine interface"""
    
    def __init__(self, action_handlers: Optional[Dict[str, Callable]] = None):
        """
        Initialize workflow engine
        
        Args:
            action_handlers: Dictionary mapping action names to handler functions
        """
        self.parser = WorkflowParser()
        self.executor = WorkflowExecutor(action_handlers)
        self.templates = WorkflowTemplates()
        self.logger = logging.getLogger(__name__)
        self.workflows = {}  # Cache loaded workflows
    
    def load_workflow(self, file_path: str) -> str:
        """
        Load workflow from file
        
        Args:
            file_path: Path to workflow file
            
        Returns:
            Workflow ID
        """
        workflow = self.parser.parse_file(file_path)
        workflow_id = workflow['name']
        self.workflows[workflow_id] = workflow
        self.logger.info(f"Loaded workflow: {workflow_id}")
        return workflow_id
    
    def load_workflow_string(self, content: str, format: str = 'yaml') -> str:
        """
        Load workflow from string
        
        Args:
            content: Workflow content
            format: Format (yaml or json)
            
        Returns:
            Workflow ID
        """
        workflow = self.parser.parse_string(content, format)
        workflow_id = workflow['name']
        self.workflows[workflow_id] = workflow
        self.logger.info(f"Loaded workflow: {workflow_id}")
        return workflow_id
    
    def load_template(self, template_name: str) -> str:
        """
        Load workflow from template
        
        Args:
            template_name: Template name
            
        Returns:
            Workflow ID
        """
        workflow = self.templates.get_template(template_name)
        workflow_id = workflow['name']
        self.workflows[workflow_id] = workflow
        self.logger.info(f"Loaded template: {template_name}")
        return workflow_id
    
    def list_templates(self) -> Dict[str, str]:
        """List available templates"""
        return self.templates.list_templates()
    
    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow by ID"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        return self.workflows[workflow_id]
    
    def execute_workflow(self, workflow_id: str, 
                        variables: Optional[Dict[str, Any]] = None,
                        progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Execute a workflow
        
        Args:
            workflow_id: Workflow ID
            variables: Variables to override
            progress_callback: Optional callback for progress updates
            
        Returns:
            Execution results
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow = self.workflows[workflow_id].copy()
        
        # Override variables
        if variables:
            workflow['variables'].update(variables)
        
        # Validate dependencies
        self.parser.validate_dependencies(workflow)
        
        # Execute
        self.logger.info(f"Executing workflow: {workflow_id}")
        result = self.executor.execute(workflow, progress_callback)
        
        if result['success']:
            self.logger.info(f"Workflow completed successfully: {workflow_id}")
        else:
            self.logger.error(f"Workflow failed: {workflow_id}")
        
        return result
    
    def execute_template(self, template_name: str,
                        variables: Optional[Dict[str, Any]] = None,
                        progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Execute a workflow template
        
        Args:
            template_name: Template name
            variables: Variables to provide
            progress_callback: Optional callback for progress updates
            
        Returns:
            Execution results
        """
        workflow_id = self.load_template(template_name)
        return self.execute_workflow(workflow_id, variables, progress_callback)
    
    def register_action(self, action_name: str, handler: Callable):
        """
        Register an action handler
        
        Args:
            action_name: Name of the action
            handler: Function to handle the action
        """
        self.executor.register_action(action_name, handler)
        self.logger.info(f"Registered action: {action_name}")
    
    def validate_workflow(self, workflow_id: str) -> bool:
        """
        Validate a workflow
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            True if valid
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        try:
            self.parser.validate_dependencies(workflow)
            return True
        except Exception as e:
            self.logger.error(f"Workflow validation failed: {e}")
            return False
    
    def save_workflow(self, workflow_id: str, file_path: str, format: str = 'yaml'):
        """
        Save workflow to file
        
        Args:
            workflow_id: Workflow ID
            file_path: Output file path
            format: Format (yaml or json)
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        path = Path(file_path)
        
        with open(path, 'w', encoding='utf-8') as f:
            if format.lower() in ['yaml', 'yml']:
                import yaml
                yaml.dump(workflow, f, default_flow_style=False)
            elif format.lower() == 'json':
                json.dump(workflow, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
        
        self.logger.info(f"Saved workflow to: {file_path}")
    
    def get_execution_plan(self, workflow_id: str) -> List[str]:
        """
        Get execution plan (order of steps)
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            List of step names in execution order
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        return self.executor._get_execution_order(workflow)
    
    def get_workflow_info(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get workflow information
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow information
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        return {
            'name': workflow['name'],
            'description': workflow.get('description', ''),
            'version': workflow.get('version', '1.0'),
            'step_count': len(workflow['steps']),
            'variables': list(workflow.get('variables', {}).keys()),
            'execution_order': self.get_execution_plan(workflow_id)
        }
    
    def list_workflows(self) -> List[str]:
        """List loaded workflows"""
        return list(self.workflows.keys())
    
    def remove_workflow(self, workflow_id: str):
        """Remove workflow from cache"""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            self.logger.info(f"Removed workflow: {workflow_id}")
