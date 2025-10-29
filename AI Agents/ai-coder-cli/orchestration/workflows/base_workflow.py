"""
Base Workflow Class

Provides the foundation for workflow definitions that automate common development tasks.
"""

import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import yaml


logger = logging.getLogger(__name__)


class WorkflowStep:
    """
    Represents a single step in a workflow.
    """
    
    def __init__(
        self,
        step_id: str,
        name: str,
        agent: str,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        condition: Optional[str] = None,
        on_error: str = "fail"
    ):
        """
        Initialize a workflow step.
        
        Args:
            step_id: Unique identifier for the step
            name: Human-readable step name
            agent: Agent to execute this step
            action: Action for the agent to perform
            params: Parameters for the action
            dependencies: Step IDs that must complete before this step
            condition: Optional condition for step execution (Python expression)
            on_error: Error handling strategy ("fail", "continue", "retry")
        """
        self.step_id = step_id
        self.name = name
        self.agent = agent
        self.action = action
        self.params = params or {}
        self.dependencies = dependencies or []
        self.condition = condition
        self.on_error = on_error
        self.status = "pending"
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None
    
    def mark_started(self):
        """Mark step as started."""
        self.status = "running"
        self.started_at = datetime.now()
    
    def mark_completed(self, result: Any):
        """Mark step as completed."""
        self.status = "completed"
        self.result = result
        self.completed_at = datetime.now()
    
    def mark_failed(self, error: str):
        """Mark step as failed."""
        self.status = "failed"
        self.error = error
        self.completed_at = datetime.now()
    
    def mark_skipped(self, reason: str):
        """Mark step as skipped."""
        self.status = "skipped"
        self.error = reason
        self.completed_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary."""
        return {
            'step_id': self.step_id,
            'name': self.name,
            'agent': self.agent,
            'action': self.action,
            'params': self.params,
            'dependencies': self.dependencies,
            'condition': self.condition,
            'on_error': self.on_error,
            'status': self.status,
            'result': str(self.result) if self.result else None,
            'error': self.error,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


class BaseWorkflow(ABC):
    """
    Base class for all workflow definitions.
    
    A workflow is a series of coordinated steps that use different agents
    to accomplish a complex development task.
    
    Workflows can be defined in Python (by subclassing) or loaded from YAML files.
    """
    
    def __init__(
        self,
        workflow_id: str,
        name: str,
        description: str,
        version: str = "1.0.0",
        tags: Optional[List[str]] = None
    ):
        """
        Initialize a workflow.
        
        Args:
            workflow_id: Unique identifier for the workflow
            name: Human-readable workflow name
            description: Workflow description
            version: Workflow version
            tags: Tags for categorization and discovery
        """
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.version = version
        self.tags = tags or []
        self.steps: List[WorkflowStep] = []
        self.status = "initialized"
        self.context: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        
        # Initialize workflow steps
        self._initialize_steps()
        
        logger.info(f"Initialized workflow: {self.name} (ID: {self.workflow_id})")
    
    @abstractmethod
    def _initialize_steps(self):
        """
        Initialize workflow steps.
        
        Subclasses should implement this to define their workflow steps.
        """
        pass
    
    def add_step(
        self,
        step_id: str,
        name: str,
        agent: str,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        condition: Optional[str] = None,
        on_error: str = "fail"
    ) -> WorkflowStep:
        """
        Add a step to the workflow.
        
        Args:
            step_id: Unique identifier for the step
            name: Human-readable step name
            agent: Agent to execute this step
            action: Action for the agent to perform
            params: Parameters for the action
            dependencies: Step IDs that must complete before this step
            condition: Optional condition for step execution
            on_error: Error handling strategy
            
        Returns:
            The created WorkflowStep
        """
        step = WorkflowStep(
            step_id=step_id,
            name=name,
            agent=agent,
            action=action,
            params=params,
            dependencies=dependencies,
            condition=condition,
            on_error=on_error
        )
        self.steps.append(step)
        return step
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get a step by ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_ready_steps(self) -> List[WorkflowStep]:
        """
        Get steps that are ready to execute.
        
        A step is ready if:
        - Its status is "pending"
        - All its dependencies are completed
        - Its condition evaluates to True (if present)
        
        Returns:
            List of ready steps
        """
        ready = []
        
        for step in self.steps:
            if step.status != "pending":
                continue
            
            # Check dependencies
            dependencies_met = True
            for dep_id in step.dependencies:
                dep_step = self.get_step(dep_id)
                if not dep_step or dep_step.status != "completed":
                    dependencies_met = False
                    break
            
            if not dependencies_met:
                continue
            
            # Check condition
            if step.condition:
                try:
                    # Evaluate condition in context
                    if not eval(step.condition, {"__builtins__": {}}, self.context):
                        step.mark_skipped(f"Condition not met: {step.condition}")
                        continue
                except Exception as e:
                    logger.warning(f"Failed to evaluate condition for step {step.step_id}: {e}")
                    step.mark_skipped(f"Condition evaluation error: {e}")
                    continue
            
            ready.append(step)
        
        return ready
    
    def is_complete(self) -> bool:
        """Check if all workflow steps are complete or skipped."""
        return all(
            step.status in ["completed", "skipped"]
            for step in self.steps
        )
    
    def has_failures(self) -> bool:
        """Check if any workflow steps have failed."""
        return any(step.status == "failed" for step in self.steps)
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get workflow progress information.
        
        Returns:
            Dictionary with progress metrics
        """
        total = len(self.steps)
        completed = sum(1 for s in self.steps if s.status == "completed")
        failed = sum(1 for s in self.steps if s.status == "failed")
        skipped = sum(1 for s in self.steps if s.status == "skipped")
        running = sum(1 for s in self.steps if s.status == "running")
        pending = sum(1 for s in self.steps if s.status == "pending")
        
        return {
            'total_steps': total,
            'completed': completed,
            'failed': failed,
            'skipped': skipped,
            'running': running,
            'pending': pending,
            'progress_percent': (completed + skipped) / total * 100 if total > 0 else 0,
            'status': self.status
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary."""
        return {
            'workflow_id': self.workflow_id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'tags': self.tags,
            'status': self.status,
            'steps': [step.to_dict() for step in self.steps],
            'context': self.context,
            'progress': self.get_progress(),
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
    
    @classmethod
    def from_yaml(cls, yaml_path: Path) -> 'BaseWorkflow':
        """
        Load a workflow from a YAML file.
        
        Args:
            yaml_path: Path to the YAML file
            
        Returns:
            Workflow instance
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return YAMLWorkflow(
            workflow_id=data['workflow_id'],
            name=data['name'],
            description=data['description'],
            version=data.get('version', '1.0.0'),
            tags=data.get('tags', []),
            steps_data=data.get('steps', [])
        )


class YAMLWorkflow(BaseWorkflow):
    """
    Workflow loaded from a YAML definition file.
    """
    
    def __init__(
        self,
        workflow_id: str,
        name: str,
        description: str,
        steps_data: List[Dict[str, Any]],
        version: str = "1.0.0",
        tags: Optional[List[str]] = None
    ):
        """
        Initialize YAML workflow.
        
        Args:
            workflow_id: Workflow ID
            name: Workflow name
            description: Workflow description
            steps_data: List of step definitions from YAML
            version: Workflow version
            tags: Workflow tags
        """
        self.steps_data = steps_data
        super().__init__(
            workflow_id=workflow_id,
            name=name,
            description=description,
            version=version,
            tags=tags
        )
    
    def _initialize_steps(self):
        """Initialize steps from YAML data."""
        for step_data in self.steps_data:
            self.add_step(
                step_id=step_data['step_id'],
                name=step_data['name'],
                agent=step_data['agent'],
                action=step_data['action'],
                params=step_data.get('params', {}),
                dependencies=step_data.get('dependencies', []),
                condition=step_data.get('condition'),
                on_error=step_data.get('on_error', 'fail')
            )
