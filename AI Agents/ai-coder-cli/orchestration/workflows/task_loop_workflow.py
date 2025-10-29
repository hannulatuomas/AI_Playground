"""
Task Loop Workflow

A specialized workflow that uses the TaskLoopProcessor to independently
process a list of tasks through the complete lifecycle.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base_workflow import BaseWorkflow
from ..task_loop_processor import TaskLoopProcessor, TaskType


logger = logging.getLogger(__name__)


class TaskLoopWorkflow(BaseWorkflow):
    """
    Workflow for processing multiple tasks independently using the task loop system.
    
    This workflow:
    1. Accepts a list of tasks
    2. Processes each task through plan-implement-test-fix-document-validate cycle
    3. Tracks progress and state
    4. Provides comprehensive results
    """
    
    def __init__(
        self,
        tasks_data: List[Dict[str, Any]],
        llm_router: Any,
        agent_registry: Any,
        config: Optional[Dict[str, Any]] = None,
        workflow_id: str = "task_loop_workflow",
        name: str = "Task Loop Processing Workflow",
        description: str = "Independent task processing with full lifecycle management"
    ):
        """
        Initialize task loop workflow.
        
        Args:
            tasks_data: List of task dictionaries
            llm_router: LLM router for AI operations
            agent_registry: Agent registry for task execution
            config: Optional configuration
            workflow_id: Workflow identifier
            name: Workflow name
            description: Workflow description
        """
        # Initialize base workflow
        super().__init__(
            workflow_id=workflow_id,
            name=name,
            description=description,
            version="1.0.0",
            tags=['task-loop', 'automated', 'independent']
        )
        
        # Initialize task loop processor
        self.task_processor = TaskLoopProcessor(
            llm_router=llm_router,
            agent_registry=agent_registry,
            config=config
        )
        
        # Add tasks to processor
        self.task_processor.add_tasks_from_list(tasks_data)
        
        logger.info(f"TaskLoopWorkflow initialized with {len(tasks_data)} tasks")
    
    def _initialize_steps(self):
        """Initialize workflow steps."""
        # This workflow uses the task loop processor instead of traditional steps
        # We still need to define a step for the workflow manager
        self.add_step(
            step_id="process_tasks",
            name="Process all tasks through the task loop",
            agent="task_loop_processor",
            action="process_all_tasks",
            params={},
            on_error="fail"
        )
    
    async def execute(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the task loop workflow.
        
        Args:
            context: Optional execution context
            
        Returns:
            Workflow execution results
        """
        self.status = "running"
        self.started_at = self.created_at
        
        logger.info(f"Executing TaskLoopWorkflow: {self.name}")
        
        try:
            # Process all tasks
            results = await self.task_processor.process_all_tasks()
            
            # Update workflow status
            if results.get('tasks_failed', 0) == 0:
                self.status = "completed"
            else:
                self.status = "completed_with_errors"
            
            # Add task processor state to results
            results['progress'] = self.task_processor.get_progress()
            results['workflow_id'] = self.workflow_id
            results['workflow_name'] = self.name
            
            return results
            
        except Exception as e:
            logger.error(f"TaskLoopWorkflow execution failed: {e}", exc_info=True)
            self.status = "failed"
            
            return {
                'success': False,
                'error': str(e),
                'workflow_id': self.workflow_id,
                'workflow_name': self.name
            }
    
    def get_progress(self) -> Dict[str, Any]:
        """Get workflow progress."""
        base_progress = super().get_progress()
        
        # Add task processor progress
        task_progress = self.task_processor.get_progress()
        
        return {
            **base_progress,
            'task_loop_progress': task_progress
        }
    
    def save_state(self, filepath: Path) -> None:
        """Save workflow state."""
        self.task_processor.save_state(filepath)
        logger.info(f"Saved TaskLoopWorkflow state to {filepath}")
    
    def load_state(self, filepath: Path) -> None:
        """Load workflow state."""
        self.task_processor.load_state(filepath)
        logger.info(f"Loaded TaskLoopWorkflow state from {filepath}")
    
    @classmethod
    def from_task_list(
        cls,
        tasks_file: Path,
        llm_router: Any,
        agent_registry: Any,
        config: Optional[Dict[str, Any]] = None
    ) -> 'TaskLoopWorkflow':
        """
        Create workflow from a task list file.
        
        Args:
            tasks_file: Path to JSON file containing task list
            llm_router: LLM router
            agent_registry: Agent registry
            config: Optional configuration
            
        Returns:
            TaskLoopWorkflow instance
        """
        import json
        
        with open(tasks_file, 'r') as f:
            tasks_data = json.load(f)
        
        # Ensure tasks_data is a list
        if isinstance(tasks_data, dict):
            if 'tasks' in tasks_data:
                tasks_data = tasks_data['tasks']
            else:
                raise ValueError("Task file must contain a 'tasks' key with a list of tasks")
        
        return cls(
            tasks_data=tasks_data,
            llm_router=llm_router,
            agent_registry=agent_registry,
            config=config
        )
