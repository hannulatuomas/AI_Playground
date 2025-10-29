"""
Workflow Executor

Executes workflow steps with dependency resolution and error handling.
"""

import time
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import logging


class StepStatus(Enum):
    """Step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowExecutor:
    """Execute workflows with dependency management"""
    
    def __init__(self, action_handlers: Optional[Dict[str, Callable]] = None):
        """
        Initialize workflow executor
        
        Args:
            action_handlers: Dictionary mapping action names to handler functions
        """
        self.action_handlers = action_handlers or {}
        self.logger = logging.getLogger(__name__)
        self.execution_log = []
        self.step_results = {}
        self.variables = {}
    
    def register_action(self, action_name: str, handler: Callable):
        """
        Register an action handler
        
        Args:
            action_name: Name of the action
            handler: Function to handle the action
        """
        self.action_handlers[action_name] = handler
    
    def execute(self, workflow: Dict[str, Any], 
                progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Execute a workflow
        
        Args:
            workflow: Workflow dictionary
            progress_callback: Optional callback for progress updates
            
        Returns:
            Execution results
        """
        self.execution_log = []
        self.step_results = {}
        self.variables = workflow.get('variables', {}).copy()
        
        start_time = time.time()
        
        try:
            # Get execution order
            execution_order = self._get_execution_order(workflow)
            
            # Execute steps in order
            for step_name in execution_order:
                step = self._get_step_by_name(workflow, step_name)
                
                if progress_callback:
                    progress_callback(step_name, StepStatus.RUNNING)
                
                result = self._execute_step(step, workflow)
                
                if result['status'] == StepStatus.FAILED:
                    self._handle_failure(step, workflow, result)
                    if workflow.get('on_error', 'stop') == 'stop':
                        break
                
                if progress_callback:
                    progress_callback(step_name, result['status'])
            
            end_time = time.time()
            
            return {
                'success': self._all_steps_successful(),
                'duration': end_time - start_time,
                'steps': self.step_results,
                'log': self.execution_log,
                'variables': self.variables
            }
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'steps': self.step_results,
                'log': self.execution_log
            }
    
    def _execute_step(self, step: Dict[str, Any], 
                      workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step"""
        step_name = step['name']
        action = step['action']
        params = step.get('params', {})
        
        self.logger.info(f"Executing step: {step_name} (action: {action})")
        
        start_time = time.time()
        retry_count = 0
        max_retries = step.get('retry_count', 0)
        
        while retry_count <= max_retries:
            try:
                # Check dependencies
                if not self._dependencies_met(step):
                    result = {
                        'status': StepStatus.SKIPPED,
                        'message': 'Dependencies not met',
                        'duration': 0
                    }
                    self.step_results[step_name] = result
                    self._log_step(step_name, result)
                    return result
                
                # Resolve parameters with variables
                resolved_params = self._resolve_params(params)
                
                # Execute action
                if action not in self.action_handlers:
                    raise ValueError(f"No handler for action: {action}")
                
                handler = self.action_handlers[action]
                output = handler(resolved_params, self.variables)
                
                # Store result
                result = {
                    'status': StepStatus.COMPLETED,
                    'output': output,
                    'duration': time.time() - start_time
                }
                
                self.step_results[step_name] = result
                self._log_step(step_name, result)
                
                return result
                
            except Exception as e:
                retry_count += 1
                self.logger.warning(f"Step {step_name} failed (attempt {retry_count}): {e}")
                
                if retry_count > max_retries:
                    result = {
                        'status': StepStatus.FAILED,
                        'error': str(e),
                        'duration': time.time() - start_time
                    }
                    self.step_results[step_name] = result
                    self._log_step(step_name, result)
                    return result
    
    def _get_execution_order(self, workflow: Dict[str, Any]) -> List[str]:
        """Get execution order using topological sort"""
        steps = workflow['steps']
        dependencies = {}
        in_degree = {}
        
        # Build dependency graph
        for step in steps:
            step_name = step['name']
            deps = step.get('depends_on', [])
            if isinstance(deps, str):
                deps = [deps]
            dependencies[step_name] = deps
            in_degree[step_name] = len(deps)
        
        # Topological sort (Kahn's algorithm)
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Reduce in-degree for dependent steps
            for step_name, deps in dependencies.items():
                if current in deps:
                    in_degree[step_name] -= 1
                    if in_degree[step_name] == 0:
                        queue.append(step_name)
        
        if len(result) != len(steps):
            raise ValueError("Circular dependency detected in workflow")
        
        return result
    
    def _get_step_by_name(self, workflow: Dict[str, Any], name: str) -> Dict[str, Any]:
        """Get step by name"""
        for step in workflow['steps']:
            if step['name'] == name:
                return step
        raise ValueError(f"Step not found: {name}")
    
    def _dependencies_met(self, step: Dict[str, Any]) -> bool:
        """Check if step dependencies are met"""
        depends_on = step.get('depends_on', [])
        if isinstance(depends_on, str):
            depends_on = [depends_on]
        
        for dep in depends_on:
            if dep not in self.step_results:
                return False
            if self.step_results[dep]['status'] != StepStatus.COMPLETED:
                return False
        
        return True
    
    def _resolve_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameters with variables"""
        resolved = {}
        
        for key, value in params.items():
            if isinstance(value, str) and value.startswith('$'):
                var_name = value[1:]
                resolved[key] = self.variables.get(var_name, value)
            else:
                resolved[key] = value
        
        return resolved
    
    def _handle_failure(self, step: Dict[str, Any], 
                       workflow: Dict[str, Any], 
                       result: Dict[str, Any]):
        """Handle step failure"""
        on_failure = step.get('on_failure', 'stop')
        
        if on_failure == 'rollback':
            self._rollback(workflow)
        elif on_failure == 'continue':
            self.logger.warning(f"Step {step['name']} failed, continuing...")
    
    def _rollback(self, workflow: Dict[str, Any]):
        """Rollback executed steps"""
        self.logger.info("Rolling back workflow...")
        
        # Execute rollback in reverse order
        completed_steps = [
            name for name, result in self.step_results.items()
            if result['status'] == StepStatus.COMPLETED
        ]
        
        for step_name in reversed(completed_steps):
            step = self._get_step_by_name(workflow, step_name)
            rollback_action = step.get('rollback_action')
            
            if rollback_action and rollback_action in self.action_handlers:
                try:
                    handler = self.action_handlers[rollback_action]
                    handler(step.get('params', {}), self.variables)
                    self.logger.info(f"Rolled back step: {step_name}")
                except Exception as e:
                    self.logger.error(f"Rollback failed for {step_name}: {e}")
    
    def _all_steps_successful(self) -> bool:
        """Check if all steps completed successfully"""
        return all(
            result['status'] in [StepStatus.COMPLETED, StepStatus.SKIPPED]
            for result in self.step_results.values()
        )
    
    def _log_step(self, step_name: str, result: Dict[str, Any]):
        """Log step execution"""
        self.execution_log.append({
            'step': step_name,
            'status': result['status'].value if isinstance(result['status'], StepStatus) else result['status'],
            'timestamp': time.time(),
            'duration': result.get('duration', 0)
        })
