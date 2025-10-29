"""
Task Planner

Creates execution plans for tasks.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from .decomposer import SubTask


@dataclass
class ExecutionPlan:
    """Task execution plan."""
    task_description: str
    subtasks: List[SubTask]
    execution_order: List[int]
    checkpoints: List[int]  # Task IDs where to pause/verify
    estimated_duration: str
    success_criteria: List[str]


class TaskPlanner:
    """Creates execution plans for tasks."""
    
    def __init__(self):
        """Initialize task planner."""
        pass
    
    def create_plan(self, task_description: str, 
                   subtasks: List[SubTask]) -> ExecutionPlan:
        """
        Create execution plan from subtasks.
        
        Args:
            task_description: Original task description
            subtasks: List of subtasks
            
        Returns:
            ExecutionPlan object
        """
        # Determine execution order (topological sort)
        execution_order = self._topological_sort(subtasks)
        
        # Identify checkpoints (after major milestones)
        checkpoints = self._identify_checkpoints(subtasks, execution_order)
        
        # Estimate duration
        estimated_duration = self._estimate_duration(subtasks)
        
        # Define success criteria
        success_criteria = self._define_success_criteria(subtasks)
        
        return ExecutionPlan(
            task_description=task_description,
            subtasks=subtasks,
            execution_order=execution_order,
            checkpoints=checkpoints,
            estimated_duration=estimated_duration,
            success_criteria=success_criteria
        )
    
    def _topological_sort(self, subtasks: List[SubTask]) -> List[int]:
        """
        Sort tasks by dependencies (topological sort).
        
        Args:
            subtasks: List of subtasks
            
        Returns:
            List of task IDs in execution order
        """
        # Build adjacency list
        graph: Dict[int, List[int]] = {task.id: [] for task in subtasks}
        in_degree: Dict[int, int] = {task.id: 0 for task in subtasks}
        
        for task in subtasks:
            for dep_id in task.dependencies:
                if dep_id in graph:
                    graph[dep_id].append(task.id)
                    in_degree[task.id] += 1
        
        # Kahn's algorithm
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            task_id = queue.pop(0)
            result.append(task_id)
            
            for neighbor in graph[task_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def _identify_checkpoints(self, subtasks: List[SubTask],
                             execution_order: List[int]) -> List[int]:
        """Identify checkpoint tasks."""
        checkpoints = []
        
        # Add checkpoint after every 3 tasks
        for i in range(2, len(execution_order), 3):
            checkpoints.append(execution_order[i])
        
        # Always checkpoint at the last task
        if execution_order and execution_order[-1] not in checkpoints:
            checkpoints.append(execution_order[-1])
        
        return checkpoints
    
    def _estimate_duration(self, subtasks: List[SubTask]) -> str:
        """Estimate total duration."""
        total_minutes = 0
        
        for task in subtasks:
            time_str = task.estimated_time.lower()
            
            if 'min' in time_str:
                minutes = int(''.join(filter(str.isdigit, time_str)) or '10')
                total_minutes += minutes
            elif 'hour' in time_str:
                hours = int(''.join(filter(str.isdigit, time_str)) or '1')
                total_minutes += hours * 60
        
        if total_minutes < 60:
            return f"{total_minutes} minutes"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
    
    def _define_success_criteria(self, subtasks: List[SubTask]) -> List[str]:
        """Define success criteria."""
        criteria = [
            "All subtasks completed successfully",
            "Code passes all tests",
            "No errors or warnings",
            "Documentation updated"
        ]
        
        # Add specific criteria based on task types
        descriptions = ' '.join(task.description.lower() for task in subtasks)
        
        if 'test' in descriptions:
            criteria.append("Test coverage >80%")
        
        if 'api' in descriptions:
            criteria.append("API endpoints respond correctly")
        
        if 'database' in descriptions:
            criteria.append("Database migrations applied successfully")
        
        return criteria
    
    def format_plan(self, plan: ExecutionPlan) -> str:
        """Format plan as readable text."""
        text = f"Execution Plan: {plan.task_description}\n"
        text += f"Estimated Duration: {plan.estimated_duration}\n"
        text += f"Total Subtasks: {len(plan.subtasks)}\n\n"
        
        text += "Execution Order:\n"
        for i, task_id in enumerate(plan.execution_order):
            task = next(t for t in plan.subtasks if t.id == task_id)
            checkpoint = " [CHECKPOINT]" if task_id in plan.checkpoints else ""
            text += f"  {i+1}. Task {task_id}: {task.description}{checkpoint}\n"
            text += f"     Time: {task.estimated_time}\n"
            if task.dependencies:
                text += f"     Depends on: {task.dependencies}\n"
        
        text += "\nSuccess Criteria:\n"
        for criterion in plan.success_criteria:
            text += f"  ✓ {criterion}\n"
        
        return text
