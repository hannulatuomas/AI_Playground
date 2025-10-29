"""
Task Tracker

Tracks progress of task execution.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from .decomposer import SubTask
from .planner import ExecutionPlan


@dataclass
class Progress:
    """Task progress information."""
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    in_progress_tasks: int
    pending_tasks: int
    completion_percentage: float
    estimated_remaining_time: str
    current_task: Optional[SubTask]


class TaskTracker:
    """Tracks task execution progress."""
    
    def __init__(self):
        """Initialize task tracker."""
        self.start_time: Optional[datetime] = None
        self.task_times: Dict[int, float] = {}
    
    def start_tracking(self):
        """Start tracking time."""
        self.start_time = datetime.now()
    
    def track_progress(self, plan: ExecutionPlan) -> Progress:
        """
        Track progress of task execution.
        
        Args:
            plan: Execution plan
            
        Returns:
            Progress object
        """
        total = len(plan.subtasks)
        completed = sum(1 for t in plan.subtasks if t.status == 'completed')
        failed = sum(1 for t in plan.subtasks if t.status == 'failed')
        in_progress = sum(1 for t in plan.subtasks if t.status == 'in_progress')
        pending = sum(1 for t in plan.subtasks if t.status == 'pending')
        
        completion_pct = (completed / total * 100) if total > 0 else 0
        
        # Find current task
        current_task = None
        for task_id in plan.execution_order:
            task = next(t for t in plan.subtasks if t.id == task_id)
            if task.status == 'in_progress':
                current_task = task
                break
        
        # Estimate remaining time
        remaining_time = self._estimate_remaining_time(plan, completed, total)
        
        return Progress(
            total_tasks=total,
            completed_tasks=completed,
            failed_tasks=failed,
            in_progress_tasks=in_progress,
            pending_tasks=pending,
            completion_percentage=completion_pct,
            estimated_remaining_time=remaining_time,
            current_task=current_task
        )
    
    def _estimate_remaining_time(self, plan: ExecutionPlan, 
                                completed: int, total: int) -> str:
        """Estimate remaining time."""
        if completed == 0:
            return plan.estimated_duration
        
        # Calculate average time per task
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            avg_time_per_task = elapsed / completed
            remaining_tasks = total - completed
            remaining_seconds = avg_time_per_task * remaining_tasks
            
            minutes = int(remaining_seconds // 60)
            if minutes < 60:
                return f"{minutes} minutes"
            else:
                hours = minutes // 60
                mins = minutes % 60
                return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
        
        return "Unknown"
    
    def format_progress(self, progress: Progress) -> str:
        """Format progress as readable text."""
        text = "Task Progress:\n"
        text += f"  Completed: {progress.completed_tasks}/{progress.total_tasks} "
        text += f"({progress.completion_percentage:.1f}%)\n"
        
        if progress.failed_tasks > 0:
            text += f"  Failed: {progress.failed_tasks}\n"
        
        if progress.in_progress_tasks > 0:
            text += f"  In Progress: {progress.in_progress_tasks}\n"
        
        if progress.pending_tasks > 0:
            text += f"  Pending: {progress.pending_tasks}\n"
        
        if progress.current_task:
            text += f"\nCurrent Task: {progress.current_task.description}\n"
        
        text += f"Estimated Remaining: {progress.estimated_remaining_time}\n"
        
        # Progress bar
        bar_length = 30
        filled = int(bar_length * progress.completion_percentage / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        text += f"\n[{bar}] {progress.completion_percentage:.1f}%\n"
        
        return text
    
    def get_task_summary(self, plan: ExecutionPlan) -> Dict[str, any]:
        """Get summary of task execution."""
        progress = self.track_progress(plan)
        
        return {
            'total_tasks': progress.total_tasks,
            'completed': progress.completed_tasks,
            'failed': progress.failed_tasks,
            'completion_percentage': progress.completion_percentage,
            'status': self._get_overall_status(progress),
            'current_task': progress.current_task.description if progress.current_task else None
        }
    
    def _get_overall_status(self, progress: Progress) -> str:
        """Get overall status."""
        if progress.failed_tasks > 0:
            return 'failed'
        elif progress.completion_percentage == 100:
            return 'completed'
        elif progress.in_progress_tasks > 0:
            return 'in_progress'
        else:
            return 'pending'
