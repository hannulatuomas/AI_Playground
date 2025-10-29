"""
Task Executor

Executes task plans.
"""

from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from .decomposer import SubTask
from .planner import ExecutionPlan


@dataclass
class ExecutionResult:
    """Task execution result."""
    plan: ExecutionPlan
    completed_tasks: List[int]
    failed_tasks: List[int]
    total_time: float  # seconds
    success: bool
    errors: List[str]


class TaskExecutor:
    """Executes task plans."""
    
    def __init__(self):
        """Initialize task executor."""
        self.task_handlers: Dict[str, Callable] = {}
    
    def register_handler(self, task_type: str, handler: Callable):
        """
        Register handler for task type.
        
        Args:
            task_type: Type of task (e.g., 'code_generation', 'testing')
            handler: Handler function
        """
        self.task_handlers[task_type] = handler
    
    def execute_plan(self, plan: ExecutionPlan,
                    on_task_complete: Optional[Callable] = None,
                    on_checkpoint: Optional[Callable] = None) -> ExecutionResult:
        """
        Execute task plan.
        
        Args:
            plan: Execution plan
            on_task_complete: Callback after each task
            on_checkpoint: Callback at checkpoints
            
        Returns:
            ExecutionResult
        """
        import time
        
        start_time = time.time()
        completed = []
        failed = []
        errors = []
        
        # Execute tasks in order
        for task_id in plan.execution_order:
            task = next(t for t in plan.subtasks if t.id == task_id)
            
            print(f"Executing task {task_id}: {task.description}")
            
            # Check dependencies
            if not all(dep_id in completed for dep_id in task.dependencies):
                error = f"Task {task_id}: Dependencies not met"
                errors.append(error)
                failed.append(task_id)
                task.status = 'failed'
                task.error = error
                continue
            
            # Execute task
            try:
                task.status = 'in_progress'
                
                # Determine task type and execute
                success, result, error = self._execute_task(task)
                
                if success:
                    task.status = 'completed'
                    task.result = result
                    completed.append(task_id)
                    
                    if on_task_complete:
                        on_task_complete(task)
                else:
                    task.status = 'failed'
                    task.error = error
                    failed.append(task_id)
                    errors.append(f"Task {task_id}: {error}")
                
                # Check if checkpoint
                if task_id in plan.checkpoints:
                    if on_checkpoint:
                        should_continue = on_checkpoint(task, completed, failed)
                        if not should_continue:
                            break
                
            except Exception as e:
                task.status = 'failed'
                task.error = str(e)
                failed.append(task_id)
                errors.append(f"Task {task_id}: {str(e)}")
        
        total_time = time.time() - start_time
        success = len(failed) == 0 and len(completed) == len(plan.subtasks)
        
        return ExecutionResult(
            plan=plan,
            completed_tasks=completed,
            failed_tasks=failed,
            total_time=total_time,
            success=success,
            errors=errors
        )
    
    def _execute_task(self, task: SubTask) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Execute a single task.
        
        Returns:
            (success, result, error)
        """
        # Determine task type from description
        desc_lower = task.description.lower()
        
        task_type = None
        if 'implement' in desc_lower or 'create' in desc_lower or 'generate' in desc_lower:
            task_type = 'code_generation'
        elif 'test' in desc_lower:
            task_type = 'testing'
        elif 'document' in desc_lower:
            task_type = 'documentation'
        elif 'refactor' in desc_lower:
            task_type = 'refactoring'
        
        # Execute with registered handler if available
        if task_type and task_type in self.task_handlers:
            try:
                result = self.task_handlers[task_type](task)
                return (True, result, None)
            except Exception as e:
                return (False, None, str(e))
        
        # Default: mark as completed (manual execution)
        return (True, f"Task marked for manual execution: {task.description}", None)
    
    def execute_single_task(self, task: SubTask) -> bool:
        """
        Execute a single task.
        
        Args:
            task: Task to execute
            
        Returns:
            True if successful
        """
        success, result, error = self._execute_task(task)
        
        if success:
            task.status = 'completed'
            task.result = result
        else:
            task.status = 'failed'
            task.error = error
        
        return success
    
    def retry_failed_tasks(self, result: ExecutionResult) -> ExecutionResult:
        """
        Retry failed tasks.
        
        Args:
            result: Previous execution result
            
        Returns:
            New ExecutionResult
        """
        # Create new plan with only failed tasks
        failed_tasks = [t for t in result.plan.subtasks if t.id in result.failed_tasks]
        
        for task in failed_tasks:
            task.status = 'pending'
            task.error = None
        
        # Re-execute
        return self.execute_plan(result.plan)
