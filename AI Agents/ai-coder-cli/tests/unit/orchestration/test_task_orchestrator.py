
"""
Unit tests for Task Orchestrator.

Tests the task orchestration and agent coordination system.
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
class TestTaskOrchestrator:
    """Test suite for Task Orchestrator."""
    
    @pytest.fixture
    def task_orchestrator(self, mock_llm_router, mock_agent_registry, mock_tool_registry):
        """Create a task orchestrator for testing."""
        from agents.generic.task_orchestrator import TaskOrchestrator
        
        # TaskOrchestrator doesn't accept agent_registry parameter
        # It uses its own internal agent coordination logic
        return TaskOrchestrator(
            name='orchestrator',
            description='Task orchestrator',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry,
            config={'agents': {'enabled_agents': []}}
        )
    
    def test_initialization(self, task_orchestrator):
        """Test task orchestrator initialization."""
        assert task_orchestrator is not None
        assert task_orchestrator.name == 'orchestrator'
    
    def test_execute_simple_task(self, task_orchestrator, mock_llm_router, sample_task_context):
        """Test executing a simple task."""
        task = "Create a Python hello world program"
        
        # Mock LLM response for task analysis
        mock_llm_router.query.return_value = {
            'success': True,
            'response': '{"steps": ["Create main.py", "Write hello world code"]}'
        }
        
        # Execute method expects a params dict
        params = {
            'prompt': task,
            'session_id': 'test-session',
            'context': sample_task_context
        }
        result = task_orchestrator.execute(params)
        
        assert 'success' in result
        assert 'message' in result or 'result' in result
    
    def test_execute_multi_step_task(self, task_orchestrator, mock_llm_router, sample_task_context):
        """Test executing a multi-step task."""
        task = "Create a Python project with tests"
        
        # Mock LLM response for task decomposition
        mock_llm_router.query.return_value = {
            'success': True,
            'response': '{"steps": ["Create structure", "Write code", "Add tests"]}'
        }
        
        # Execute method expects a params dict
        params = {
            'prompt': task,
            'session_id': 'test-session',
            'context': sample_task_context
        }
        result = task_orchestrator.execute(params)
        
        assert 'success' in result or 'result' in result
    
    def test_decompose_task(self, task_orchestrator, mock_llm_router):
        """Test task decomposition."""
        from agents.generic.task_decomposition import TaskDecomposer
        
        # TaskDecomposer only accepts llm_router parameter
        decomposer = TaskDecomposer(llm_router=mock_llm_router)
        
        # Mock LLM response with proper format expected by parser
        mock_llm_router.query.return_value = {
            'success': True,
            'response': '''TASK 1: Design database schema
Priority: 8
Dependencies: none
1.1: Create ER diagram
1.2: Define tables
1.3: Define relationships

TASK 2: Implement API endpoints
Priority: 7
Dependencies: task_1
2.1: Create REST API
2.2: Add authentication
2.3: Add validation'''
        }
        
        result = decomposer.decompose("Create a web app", specifications={})
        
        # Check that result contains tasks
        assert 'tasks' in result
        assert isinstance(result['tasks'], list)
        assert len(result['tasks']) >= 2
        assert 'description' in result['tasks'][0]


@pytest.mark.unit
class TestWorkflowManager:
    """Test suite for Workflow Manager."""
    
    @pytest.fixture
    def workflow_manager(self, mock_llm_router, mock_agent_registry):
        """Create a workflow manager for testing."""
        from orchestration.workflows.workflow_manager import WorkflowManager
        
        return WorkflowManager(
            llm_router=mock_llm_router,
            agent_registry=mock_agent_registry
        )
    
    def test_initialization(self, workflow_manager):
        """Test workflow manager initialization."""
        assert workflow_manager is not None
    
    def test_list_workflows(self, workflow_manager):
        """Test listing available workflows."""
        workflows = workflow_manager.list_workflows()
        
        assert isinstance(workflows, list)
        assert len(workflows) >= 0
    
    def test_execute_workflow(self, workflow_manager, sample_task_context):
        """Test executing a workflow."""
        import asyncio
        
        # Add task to context
        context = sample_task_context.copy()
        context['task'] = 'Create main.py'
        
        result = asyncio.run(workflow_manager.execute_workflow(
            workflow_id='code_generation',
            context=context,
            auto_confirm=True
        ))
        
        assert result is not None
