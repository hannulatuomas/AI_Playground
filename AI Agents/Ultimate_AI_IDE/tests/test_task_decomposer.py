"""
Tests for Task Decomposer Module
"""

import pytest
from src.modules.task_decomposer import (
    TaskDecomposer, SubTask, TaskPlanner,
    TaskExecutor, TaskTracker
)


class MockAIBackend:
    """Mock AI backend for testing."""
    
    def query(self, prompt, max_tokens=1000):
        """Mock query method."""
        return '''[
  {
    "id": 1,
    "description": "Create user model",
    "dependencies": [],
    "estimated_time": "10 min"
  },
  {
    "id": 2,
    "description": "Create authentication endpoint",
    "dependencies": [1],
    "estimated_time": "15 min"
  }
]'''


@pytest.fixture
def mock_ai():
    """Provide mock AI backend."""
    return MockAIBackend()


def test_task_decomposer_analyze(mock_ai):
    """Test task analysis."""
    decomposer = TaskDecomposer(mock_ai)
    
    analysis = decomposer.analyze_task("Create a simple function")
    
    assert analysis.complexity in ['simple', 'moderate', 'complex']
    assert analysis.estimated_subtasks > 0


def test_task_decomposer_decompose(mock_ai):
    """Test task decomposition."""
    decomposer = TaskDecomposer(mock_ai)
    
    subtasks = decomposer.decompose_task("Create user authentication", 'python')
    
    assert len(subtasks) > 0
    assert all(isinstance(task, SubTask) for task in subtasks)


def test_task_decomposer_validate_dependencies(mock_ai):
    """Test dependency validation."""
    decomposer = TaskDecomposer(mock_ai)
    
    subtasks = [
        SubTask(id=1, description="Task 1", dependencies=[]),
        SubTask(id=2, description="Task 2", dependencies=[1])
    ]
    
    assert decomposer.validate_dependencies(subtasks) is True


def test_task_planner():
    """Test task planner."""
    planner = TaskPlanner()
    
    subtasks = [
        SubTask(id=1, description="Task 1", dependencies=[]),
        SubTask(id=2, description="Task 2", dependencies=[1]),
        SubTask(id=3, description="Task 3", dependencies=[1, 2])
    ]
    
    plan = planner.create_plan("Test task", subtasks)
    
    assert len(plan.execution_order) == 3
    assert plan.execution_order[0] == 1  # No dependencies first


def test_task_executor():
    """Test task executor."""
    executor = TaskExecutor()
    
    task = SubTask(id=1, description="Test task", dependencies=[])
    success = executor.execute_single_task(task)
    
    assert task.status in ['completed', 'failed']


def test_task_tracker():
    """Test task tracker."""
    tracker = TaskTracker()
    
    subtasks = [
        SubTask(id=1, description="Task 1", dependencies=[], status='completed'),
        SubTask(id=2, description="Task 2", dependencies=[], status='pending')
    ]
    
    from src.modules.task_decomposer.planner import ExecutionPlan
    plan = ExecutionPlan(
        task_description="Test",
        subtasks=subtasks,
        execution_order=[1, 2],
        checkpoints=[2],
        estimated_duration="20 min",
        success_criteria=[]
    )
    
    progress = tracker.track_progress(plan)
    
    assert progress.total_tasks == 2
    assert progress.completed_tasks == 1
    assert progress.completion_percentage == 50.0


def test_get_ready_tasks(mock_ai):
    """Test getting ready tasks."""
    decomposer = TaskDecomposer(mock_ai)
    
    subtasks = [
        SubTask(id=1, description="Task 1", dependencies=[], status='completed'),
        SubTask(id=2, description="Task 2", dependencies=[1], status='pending'),
        SubTask(id=3, description="Task 3", dependencies=[2], status='pending')
    ]
    
    ready = decomposer.get_ready_tasks(subtasks)
    
    assert len(ready) == 1
    assert ready[0].id == 2
