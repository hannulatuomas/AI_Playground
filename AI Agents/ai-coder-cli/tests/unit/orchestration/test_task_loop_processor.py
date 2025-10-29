"""
Unit tests for Task Loop Processor.

Tests the task loop processing system for independent task management.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from orchestration.task_loop_processor import (
    TaskLoopProcessor,
    Task,
    TaskType,
    TaskStatus
)


@pytest.mark.unit
class TestTask:
    """Test suite for Task class."""
    
    def test_task_creation(self):
        """Test creating a task."""
        task = Task(
            task_id="task_001",
            title="Test Task",
            description="Test description",
            task_type=TaskType.FEATURE,
            priority=5
        )
        
        assert task.task_id == "task_001"
        assert task.title == "Test Task"
        assert task.task_type == TaskType.FEATURE
        assert task.status == TaskStatus.PENDING
        assert task.priority == 5
    
    def test_task_mark_started(self):
        """Test marking task as started."""
        task = Task(
            task_id="task_001",
            title="Test Task",
            description="Test",
            task_type=TaskType.FEATURE
        )
        
        task.mark_started()
        
        assert task.started_at is not None
        assert isinstance(task.started_at, datetime)
    
    def test_task_mark_completed(self):
        """Test marking task as completed."""
        task = Task(
            task_id="task_001",
            title="Test Task",
            description="Test",
            task_type=TaskType.FEATURE
        )
        
        task.mark_completed()
        
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
    
    def test_task_mark_failed(self):
        """Test marking task as failed."""
        task = Task(
            task_id="task_001",
            title="Test Task",
            description="Test",
            task_type=TaskType.FEATURE
        )
        
        task.mark_failed("Test error")
        
        assert task.status == TaskStatus.FAILED
        assert task.error_message == "Test error"
        assert task.completed_at is not None
    
    def test_task_to_dict(self):
        """Test converting task to dictionary."""
        task = Task(
            task_id="task_001",
            title="Test Task",
            description="Test",
            task_type=TaskType.FEATURE,
            priority=3,
            tags=["test", "feature"],
            dependencies=["task_000"]
        )
        
        task_dict = task.to_dict()
        
        assert task_dict['task_id'] == "task_001"
        assert task_dict['title'] == "Test Task"
        assert task_dict['task_type'] == "feature"
        assert task_dict['priority'] == 3
        assert task_dict['tags'] == ["test", "feature"]
        assert task_dict['dependencies'] == ["task_000"]
    
    def test_task_from_dict(self):
        """Test creating task from dictionary."""
        task_dict = {
            'task_id': "task_001",
            'title': "Test Task",
            'description': "Test",
            'task_type': "bug",
            'priority': 2,
            'status': "pending"
        }
        
        task = Task.from_dict(task_dict)
        
        assert task.task_id == "task_001"
        assert task.title == "Test Task"
        assert task.task_type == TaskType.BUG
        assert task.priority == 2
        assert task.status == TaskStatus.PENDING


@pytest.mark.unit
class TestTaskLoopProcessor:
    """Test suite for TaskLoopProcessor."""
    
    @pytest.fixture
    def mock_llm_router(self):
        """Mock LLM router."""
        router = Mock()
        router.query.return_value = {
            'response': 'Mock plan/documentation response',
            'provider': 'ollama'
        }
        return router
    
    @pytest.fixture
    def mock_agent_registry(self):
        """Mock agent registry."""
        registry = Mock()
        
        # Mock agents
        mock_agent = Mock()
        mock_agent.execute.return_value = {
            'success': True,
            'message': 'Task executed successfully',
            'data': {}
        }
        
        registry.get_agent.return_value = mock_agent
        
        return registry
    
    @pytest.fixture
    def task_processor(self, mock_llm_router, mock_agent_registry):
        """Create a task loop processor for testing."""
        return TaskLoopProcessor(
            llm_router=mock_llm_router,
            agent_registry=mock_agent_registry
        )
    
    def test_processor_initialization(self, task_processor):
        """Test task processor initialization."""
        assert task_processor is not None
        assert task_processor.tasks == []
        assert task_processor.completed_tasks == []
        assert task_processor.failed_tasks == []
    
    def test_add_task(self, task_processor):
        """Test adding a task to the processor."""
        task = task_processor.add_task(
            task_id="task_001",
            title="Test Task",
            description="Test description",
            task_type=TaskType.FEATURE,
            priority=5
        )
        
        assert task is not None
        assert len(task_processor.tasks) == 1
        assert task_processor.tasks[0] == task
    
    def test_add_multiple_tasks(self, task_processor):
        """Test adding multiple tasks."""
        tasks_data = [
            {
                'task_id': 'task_001',
                'title': 'Task 1',
                'description': 'Description 1',
                'task_type': 'feature',
                'priority': 1
            },
            {
                'task_id': 'task_002',
                'title': 'Task 2',
                'description': 'Description 2',
                'task_type': 'bug',
                'priority': 2
            }
        ]
        
        tasks = task_processor.add_tasks_from_list(tasks_data)
        
        assert len(tasks) == 2
        assert len(task_processor.tasks) == 2
    
    def test_get_next_task_by_priority(self, task_processor):
        """Test getting next task respects priority."""
        # Add tasks with different priorities
        task_processor.add_task(
            task_id="task_001",
            title="Low Priority",
            description="Test",
            task_type=TaskType.FEATURE,
            priority=10
        )
        
        task_processor.add_task(
            task_id="task_002",
            title="High Priority",
            description="Test",
            task_type=TaskType.BUG,
            priority=1
        )
        
        next_task = task_processor.get_next_task()
        
        assert next_task is not None
        assert next_task.task_id == "task_002"  # Higher priority (lower number)
        assert next_task.priority == 1
    
    def test_get_next_task_with_dependencies(self, task_processor):
        """Test getting next task respects dependencies."""
        # Add task with dependency
        task_processor.add_task(
            task_id="task_001",
            title="Independent Task",
            description="Test",
            task_type=TaskType.FEATURE,
            priority=1
        )
        
        task_processor.add_task(
            task_id="task_002",
            title="Dependent Task",
            description="Test",
            task_type=TaskType.FEATURE,
            priority=1,
            dependencies=["task_001"]
        )
        
        next_task = task_processor.get_next_task()
        
        # Should get task_001 first (no dependencies)
        assert next_task is not None
        assert next_task.task_id == "task_001"
    
    def test_get_task_by_id(self, task_processor):
        """Test getting a task by ID."""
        task_processor.add_task(
            task_id="task_001",
            title="Test Task",
            description="Test",
            task_type=TaskType.FEATURE
        )
        
        task = task_processor.get_task("task_001")
        
        assert task is not None
        assert task.task_id == "task_001"
    
    @pytest.mark.asyncio
    async def test_plan_task(self, task_processor):
        """Test planning a task."""
        task = task_processor.add_task(
            task_id="task_001",
            title="Test Task",
            description="Test description",
            task_type=TaskType.FEATURE
        )
        
        result = await task_processor._plan_task(task)
        
        assert result['success'] is True
        assert 'plan' in result
        assert task.plan is not None
    
    @pytest.mark.asyncio
    async def test_implement_task(self, task_processor):
        """Test implementing a task."""
        task = task_processor.add_task(
            task_id="task_001",
            title="Test Task",
            description="Test description",
            task_type=TaskType.FEATURE
        )
        task.plan = "Test plan"
        
        result = await task_processor._implement_task(task)
        
        assert 'success' in result
        assert result['success'] is True
    
    @pytest.mark.asyncio
    async def test_test_task(self, task_processor, mock_agent_registry):
        """Test running tests for a task."""
        # Mock test agent
        test_agent = Mock()
        test_agent.execute.return_value = {
            'success': True,
            'failures': []
        }
        
        mock_agent_registry.get_agent.return_value = test_agent
        
        task = task_processor.add_task(
            task_id="task_001",
            title="Test Task",
            description="Test",
            task_type=TaskType.FEATURE
        )
        
        result = await task_processor._test_task(task)
        
        assert result['success'] is True
    
    @pytest.mark.asyncio
    async def test_document_task(self, task_processor):
        """Test documenting a task."""
        task = task_processor.add_task(
            task_id="task_001",
            title="Test Task",
            description="Test",
            task_type=TaskType.FEATURE
        )
        task.plan = "Test plan"
        
        result = await task_processor._document_task(task)
        
        assert result['success'] is True
        assert task.documentation is not None
    
    @pytest.mark.asyncio
    async def test_validate_task(self, task_processor):
        """Test validating a task."""
        task = task_processor.add_task(
            task_id="task_001",
            title="Test Task",
            description="Test",
            task_type=TaskType.FEATURE
        )
        
        # Set required fields
        task.plan = "Test plan"
        task.implementation_result = {'success': True}
        task.test_results = {'success': True}
        task.documentation = "Test documentation"
        
        result = await task_processor._validate_task(task)
        
        assert result['success'] is True
        assert result['checks']['has_plan'] is True
        assert result['checks']['has_implementation'] is True
        assert result['checks']['tests_passed'] is True
        assert result['checks']['has_documentation'] is True
    
    @pytest.mark.asyncio
    async def test_process_single_task(self, task_processor):
        """Test processing a single task through the complete cycle."""
        task = task_processor.add_task(
            task_id="task_001",
            title="Test Task",
            description="Test description",
            task_type=TaskType.FEATURE
        )
        
        result = await task_processor.process_task(task)
        
        assert result is not None
        assert 'task_id' in result
        assert 'stages' in result
        assert 'planning' in result['stages']
        assert 'implementation' in result['stages']
    
    def test_get_progress(self, task_processor):
        """Test getting progress information."""
        # Add some tasks
        task_processor.add_task(
            task_id="task_001",
            title="Task 1",
            description="Test",
            task_type=TaskType.FEATURE
        )
        
        task_processor.add_task(
            task_id="task_002",
            title="Task 2",
            description="Test",
            task_type=TaskType.BUG
        )
        
        progress = task_processor.get_progress()
        
        assert progress is not None
        assert progress['total_tasks'] == 2
        assert progress['pending'] == 2
        assert progress['completed'] == 0
        assert progress['failed'] == 0
    
    def test_save_and_load_state(self, task_processor, tmp_path):
        """Test saving and loading processor state."""
        # Add tasks
        task_processor.add_task(
            task_id="task_001",
            title="Test Task",
            description="Test",
            task_type=TaskType.FEATURE
        )
        
        # Save state
        state_file = tmp_path / "task_processor_state.json"
        task_processor.save_state(state_file)
        
        assert state_file.exists()
        
        # Create new processor and load state
        new_processor = TaskLoopProcessor(
            llm_router=Mock(),
            agent_registry=Mock()
        )
        
        new_processor.load_state(state_file)
        
        assert len(new_processor.tasks) == 1
        assert new_processor.tasks[0].task_id == "task_001"


@pytest.mark.unit
class TestTaskLoopWorkflow:
    """Test suite for TaskLoopWorkflow."""
    
    @pytest.fixture
    def mock_llm_router(self):
        """Mock LLM router."""
        router = Mock()
        router.query.return_value = {
            'response': 'Mock response',
            'provider': 'ollama'
        }
        return router
    
    @pytest.fixture
    def mock_agent_registry(self):
        """Mock agent registry."""
        registry = Mock()
        
        mock_agent = Mock()
        mock_agent.execute.return_value = {
            'success': True,
            'message': 'Success'
        }
        
        registry.get_agent.return_value = mock_agent
        
        return registry
    
    @pytest.fixture
    def tasks_data(self):
        """Sample tasks data."""
        return [
            {
                'task_id': 'task_001',
                'title': 'Implement Feature A',
                'description': 'Add new feature A to the codebase',
                'task_type': 'feature',
                'priority': 1
            },
            {
                'task_id': 'task_002',
                'title': 'Fix Bug B',
                'description': 'Fix the bug in module B',
                'task_type': 'bug',
                'priority': 2
            }
        ]
    
    def test_workflow_initialization(self, tasks_data, mock_llm_router, mock_agent_registry):
        """Test task loop workflow initialization."""
        from orchestration.workflows.task_loop_workflow import TaskLoopWorkflow
        
        workflow = TaskLoopWorkflow(
            tasks_data=tasks_data,
            llm_router=mock_llm_router,
            agent_registry=mock_agent_registry
        )
        
        assert workflow is not None
        assert workflow.task_processor is not None
        assert len(workflow.task_processor.tasks) == 2
    
    @pytest.mark.asyncio
    async def test_workflow_execution(self, tasks_data, mock_llm_router, mock_agent_registry):
        """Test executing the task loop workflow."""
        from orchestration.workflows.task_loop_workflow import TaskLoopWorkflow
        
        workflow = TaskLoopWorkflow(
            tasks_data=tasks_data,
            llm_router=mock_llm_router,
            agent_registry=mock_agent_registry
        )
        
        # Mock process_all_tasks to return quickly
        workflow.task_processor.process_all_tasks = AsyncMock(return_value={
            'tasks_processed': 2,
            'tasks_completed': 2,
            'tasks_failed': 0,
            'task_results': []
        })
        
        result = await workflow.execute()
        
        assert result is not None
        assert 'tasks_processed' in result
        assert result['tasks_processed'] == 2
    
    def test_workflow_progress(self, tasks_data, mock_llm_router, mock_agent_registry):
        """Test getting workflow progress."""
        from orchestration.workflows.task_loop_workflow import TaskLoopWorkflow
        
        workflow = TaskLoopWorkflow(
            tasks_data=tasks_data,
            llm_router=mock_llm_router,
            agent_registry=mock_agent_registry
        )
        
        progress = workflow.get_progress()
        
        assert progress is not None
        assert 'task_loop_progress' in progress
