"""
Comprehensive unit tests for orchestration/workflows/workflow_manager.py

Tests cover:
- WorkflowManager initialization
- Workflow loading from YAML
- Workflow selection (keyword-based and LLM-based)
- Workflow execution
- Step execution
- User workflow prompting
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch, mock_open
from pathlib import Path
from datetime import datetime

from orchestration.workflows.workflow_manager import WorkflowManager
from orchestration.workflows.base_workflow import BaseWorkflow, WorkflowStep


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_workflows_dir(tmp_path):
    """Create a temporary workflows directory."""
    workflows_dir = tmp_path / "workflows"
    workflows_dir.mkdir()
    return workflows_dir


@pytest.fixture
def mock_agent_registry():
    """Create a mock agent registry."""
    registry = Mock()
    registry.get_agent = Mock()
    return registry


@pytest.fixture
def mock_llm_router():
    """Create a mock LLM router."""
    router = Mock()
    router.query = Mock(return_value={
        'response': 'new_project_workflow',
        'provider': 'ollama',
        'model': 'test-model'
    })
    return router


@pytest.fixture
def sample_workflow_yaml():
    """Sample workflow YAML content."""
    return """
workflow_id: test_workflow
name: Test Workflow
description: A test workflow
version: 1.0
tags:
  - test
  - demo
steps:
  - step_id: step1
    name: First Step
    agent: code_planner
    params:
      action: plan
    dependencies: []
  - step_id: step2
    name: Second Step
    agent: code_editor
    params:
      action: edit
    dependencies:
      - step1
"""


@pytest.fixture
def mock_workflow():
    """Create a mock workflow."""
    workflow = Mock(spec=BaseWorkflow)
    workflow.workflow_id = 'test_workflow'
    workflow.name = 'Test Workflow'
    workflow.description = 'A test workflow'
    workflow.version = '1.0'
    workflow.tags = ['test']
    workflow.steps = []
    workflow.status = 'pending'
    workflow.context = {}
    workflow.is_complete = Mock(return_value=False)
    workflow.get_ready_steps = Mock(return_value=[])
    workflow.has_failures = Mock(return_value=False)
    workflow.get_progress = Mock(return_value={'completed': 0, 'total': 2})
    workflow.to_dict = Mock(return_value={'workflow_id': 'test_workflow'})
    return workflow


@pytest.fixture
def mock_workflow_step():
    """Create a mock workflow step."""
    step = Mock(spec=WorkflowStep)
    step.step_id = 'step1'
    step.name = 'Test Step'
    step.agent = 'code_planner'
    step.params = {'action': 'plan'}
    step.on_error = 'fail'
    step.mark_started = Mock()
    step.mark_completed = Mock()
    step.mark_failed = Mock()
    return step


# =============================================================================
# WorkflowManager Initialization Tests
# =============================================================================

class TestWorkflowManagerInitialization:
    """Tests for WorkflowManager initialization."""
    
    def test_initialization_default_dir(self):
        """Test initialization with default workflows directory."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager()
        
        assert manager.workflows_dir is not None
        assert manager.workflows == {}
        assert manager.active_workflows == {}
        assert manager.agent_registry is None
        assert manager.llm_router is None
    
    def test_initialization_custom_dir(self, temp_workflows_dir):
        """Test initialization with custom workflows directory."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
        
        assert manager.workflows_dir == temp_workflows_dir
    
    def test_initialization_with_dependencies(self, temp_workflows_dir, 
                                             mock_agent_registry, mock_llm_router):
        """Test initialization with agent registry and LLM router."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(
                workflows_dir=temp_workflows_dir,
                agent_registry=mock_agent_registry,
                llm_router=mock_llm_router
            )
        
        assert manager.agent_registry == mock_agent_registry
        assert manager.llm_router == mock_llm_router
    
    def test_initialization_loads_workflows(self, temp_workflows_dir, sample_workflow_yaml):
        """Test that initialization loads workflows from directory."""
        # Create a sample workflow file
        workflow_file = temp_workflows_dir / "test_workflow.yaml"
        workflow_file.write_text(sample_workflow_yaml)
        
        with patch('orchestration.workflows.base_workflow.BaseWorkflow.from_yaml') as mock_from_yaml:
            mock_workflow = Mock(spec=BaseWorkflow)
            mock_workflow.workflow_id = 'test_workflow'
            mock_workflow.name = 'Test Workflow'
            mock_from_yaml.return_value = mock_workflow
            
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
        
        assert len(manager.workflows) == 1
        assert 'test_workflow' in manager.workflows


# =============================================================================
# Workflow Loading Tests
# =============================================================================

class TestWorkflowLoading:
    """Tests for workflow loading functionality."""
    
    def test_load_workflows_nonexistent_dir(self, tmp_path):
        """Test loading workflows when directory doesn't exist."""
        non_existent_dir = tmp_path / "non_existent"
        
        manager = WorkflowManager(workflows_dir=non_existent_dir)
        
        # Should create directory and have no workflows
        assert non_existent_dir.exists()
        assert len(manager.workflows) == 0
    
    def test_load_workflows_empty_dir(self, temp_workflows_dir):
        """Test loading workflows from empty directory."""
        manager = WorkflowManager(workflows_dir=temp_workflows_dir)
        
        assert len(manager.workflows) == 0
    
    def test_load_workflows_multiple_files(self, temp_workflows_dir):
        """Test loading multiple workflow files."""
        # Create multiple workflow files
        for i in range(3):
            workflow_file = temp_workflows_dir / f"workflow{i}.yaml"
            workflow_file.write_text(f"""
workflow_id: workflow{i}
name: Workflow {i}
description: Test workflow {i}
version: 1.0
tags: []
steps: []
""")
        
        with patch('orchestration.workflows.base_workflow.BaseWorkflow.from_yaml') as mock_from_yaml:
            def create_mock_workflow(yaml_file):
                mock_wf = Mock(spec=BaseWorkflow)
                # Extract workflow ID from filename
                wf_id = yaml_file.stem
                mock_wf.workflow_id = wf_id
                mock_wf.name = f"Workflow {wf_id}"
                return mock_wf
            
            mock_from_yaml.side_effect = create_mock_workflow
            
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
        
        assert len(manager.workflows) == 3
    
    def test_load_workflows_handles_errors(self, temp_workflows_dir):
        """Test that loading continues even if one workflow fails."""
        # Create two workflow files
        (temp_workflows_dir / "good.yaml").write_text("workflow_id: good\nname: Good\nsteps: []")
        (temp_workflows_dir / "bad.yaml").write_text("invalid yaml content")
        
        with patch('orchestration.workflows.base_workflow.BaseWorkflow.from_yaml') as mock_from_yaml:
            def from_yaml_side_effect(yaml_file):
                if 'bad' in str(yaml_file):
                    raise Exception("Invalid YAML")
                mock_wf = Mock(spec=BaseWorkflow)
                mock_wf.workflow_id = 'good'
                mock_wf.name = 'Good'
                return mock_wf
            
            mock_from_yaml.side_effect = from_yaml_side_effect
            
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
        
        # Should have loaded the good workflow and skipped the bad one
        assert len(manager.workflows) == 1
        assert 'good' in manager.workflows


# =============================================================================
# Workflow Retrieval Tests
# =============================================================================

class TestWorkflowRetrieval:
    """Tests for workflow retrieval methods."""
    
    def test_get_workflow_existing(self, temp_workflows_dir, mock_workflow):
        """Test getting an existing workflow."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            manager.workflows['test_workflow'] = mock_workflow
        
        result = manager.get_workflow('test_workflow')
        
        assert result == mock_workflow
    
    def test_get_workflow_nonexistent(self, temp_workflows_dir):
        """Test getting a non-existent workflow returns None."""
        manager = WorkflowManager(workflows_dir=temp_workflows_dir)
        
        result = manager.get_workflow('nonexistent')
        
        assert result is None
    
    def test_list_workflows_all(self, temp_workflows_dir):
        """Test listing all workflows."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            
            # Add mock workflows
            for i in range(3):
                mock_wf = Mock(spec=BaseWorkflow)
                mock_wf.workflow_id = f'workflow{i}'
                mock_wf.name = f'Workflow {i}'
                mock_wf.description = f'Description {i}'
                mock_wf.version = '1.0'
                mock_wf.tags = ['tag1', 'tag2']
                mock_wf.steps = [Mock(), Mock()]
                manager.workflows[f'workflow{i}'] = mock_wf
        
        result = manager.list_workflows()
        
        assert len(result) == 3
        assert all('workflow_id' in wf for wf in result)
        assert all('name' in wf for wf in result)
        assert all('num_steps' in wf for wf in result)
    
    def test_list_workflows_filtered_by_tags(self, temp_workflows_dir):
        """Test listing workflows filtered by tags."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            
            # Add workflows with different tags
            wf1 = Mock(spec=BaseWorkflow)
            wf1.workflow_id = 'wf1'
            wf1.name = 'WF1'
            wf1.description = 'Desc1'
            wf1.version = '1.0'
            wf1.tags = ['python', 'backend']
            wf1.steps = []
            
            wf2 = Mock(spec=BaseWorkflow)
            wf2.workflow_id = 'wf2'
            wf2.name = 'WF2'
            wf2.description = 'Desc2'
            wf2.version = '1.0'
            wf2.tags = ['javascript', 'frontend']
            wf2.steps = []
            
            manager.workflows['wf1'] = wf1
            manager.workflows['wf2'] = wf2
        
        result = manager.list_workflows(tags=['python'])
        
        assert len(result) == 1
        assert result[0]['workflow_id'] == 'wf1'


# =============================================================================
# Workflow Selection Tests
# =============================================================================

class TestWorkflowSelection:
    """Tests for workflow selection functionality."""
    
    def test_select_workflow_new_project_keywords(self, temp_workflows_dir, mock_workflow):
        """Test selecting workflow using new project keywords."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            mock_workflow.workflow_id = 'new_project_workflow'
            manager.workflows['new_project_workflow'] = mock_workflow
        
        result = manager.select_workflow("Create a new project")
        
        assert result == 'new_project_workflow'
    
    def test_select_workflow_new_feature_keywords(self, temp_workflows_dir, mock_workflow):
        """Test selecting workflow using new feature keywords."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            mock_workflow.workflow_id = 'new_feature_workflow'
            manager.workflows['new_feature_workflow'] = mock_workflow
        
        result = manager.select_workflow("Add a new feature to the app")
        
        assert result == 'new_feature_workflow'
    
    def test_select_workflow_refactor_keywords(self, temp_workflows_dir, mock_workflow):
        """Test selecting workflow using refactor keywords."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            mock_workflow.workflow_id = 'refactor_workflow'
            manager.workflows['refactor_workflow'] = mock_workflow
        
        result = manager.select_workflow("Refactor the code structure")
        
        assert result == 'refactor_workflow'
    
    def test_select_workflow_debug_keywords(self, temp_workflows_dir, mock_workflow):
        """Test selecting workflow using debug keywords."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            mock_workflow.workflow_id = 'debug_workflow'
            manager.workflows['debug_workflow'] = mock_workflow
        
        result = manager.select_workflow("Fix bug in the application")
        
        assert result == 'debug_workflow'
    
    def test_select_workflow_test_keywords(self, temp_workflows_dir, mock_workflow):
        """Test selecting workflow using test keywords."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            mock_workflow.workflow_id = 'test_workflow'
            manager.workflows['test_workflow'] = mock_workflow
        
        result = manager.select_workflow("Write unit tests")
        
        assert result == 'test_workflow'
    
    def test_select_workflow_ambiguous_returns_none(self, temp_workflows_dir):
        """Test that ambiguous workflow selection returns None."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            
            # Add multiple workflows that could match
            wf1 = Mock(spec=BaseWorkflow)
            wf1.workflow_id = 'new_project_workflow'
            wf2 = Mock(spec=BaseWorkflow)
            wf2.workflow_id = 'new_feature_workflow'
            
            manager.workflows['new_project_workflow'] = wf1
            manager.workflows['new_feature_workflow'] = wf2
        
        # "new" keyword matches both workflows equally
        result = manager.select_workflow("new something")
        
        # Should return None due to ambiguity
        assert result is None
    
    def test_select_workflow_no_match_tries_llm(self, temp_workflows_dir, mock_llm_router):
        """Test that no keyword match triggers LLM selection."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(
                workflows_dir=temp_workflows_dir,
                llm_router=mock_llm_router
            )
            
            mock_wf = Mock(spec=BaseWorkflow)
            mock_wf.workflow_id = 'test_workflow'
            mock_wf.description = 'Test workflow'
            manager.workflows['test_workflow'] = mock_wf
            
            mock_llm_router.query.return_value = {
                'response': 'test_workflow',
                'provider': 'ollama'
            }
        
        result = manager.select_workflow("some random task with no keywords")
        
        # Should have called LLM
        mock_llm_router.query.assert_called_once()
        assert result == 'test_workflow'
    
    def test_select_workflow_no_llm_router(self, temp_workflows_dir):
        """Test workflow selection when LLM router not available."""
        manager = WorkflowManager(workflows_dir=temp_workflows_dir, llm_router=None)
        
        result = manager.select_workflow("random task")
        
        # Should return None if no keywords match and no LLM
        assert result is None
    
    def test_llm_select_workflow_success(self, temp_workflows_dir, mock_llm_router):
        """Test successful LLM-based workflow selection."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(
                workflows_dir=temp_workflows_dir,
                llm_router=mock_llm_router
            )
            
            mock_wf = Mock(spec=BaseWorkflow)
            mock_wf.workflow_id = 'selected_workflow'
            mock_wf.description = 'Selected workflow'
            manager.workflows['selected_workflow'] = mock_wf
            
            mock_llm_router.query.return_value = {
                'response': 'selected_workflow',
                'provider': 'ollama'
            }
        
        result = manager._llm_select_workflow("task description", {})
        
        assert result == 'selected_workflow'
    
    def test_llm_select_workflow_case_insensitive(self, temp_workflows_dir, mock_llm_router):
        """Test LLM selection is case-insensitive."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(
                workflows_dir=temp_workflows_dir,
                llm_router=mock_llm_router
            )
            
            mock_wf = Mock(spec=BaseWorkflow)
            mock_wf.workflow_id = 'test_workflow'
            manager.workflows['test_workflow'] = mock_wf
            
            mock_llm_router.query.return_value = {
                'response': 'TEST_WORKFLOW',  # Different case
                'provider': 'ollama'
            }
        
        result = manager._llm_select_workflow("task", {})
        
        assert result == 'test_workflow'
    
    def test_llm_select_workflow_invalid_response(self, temp_workflows_dir, mock_llm_router):
        """Test LLM selection with invalid response."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(
                workflows_dir=temp_workflows_dir,
                llm_router=mock_llm_router
            )
            
            mock_llm_router.query.return_value = {
                'response': 'INVALID_WORKFLOW',
                'provider': 'ollama'
            }
        
        result = manager._llm_select_workflow("task", {})
        
        assert result is None
    
    def test_llm_select_workflow_handles_exception(self, temp_workflows_dir, mock_llm_router):
        """Test LLM selection handles exceptions gracefully."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(
                workflows_dir=temp_workflows_dir,
                llm_router=mock_llm_router
            )
            
            mock_llm_router.query.side_effect = Exception("LLM error")
        
        result = manager._llm_select_workflow("task", {})
        
        assert result is None


# =============================================================================
# User Prompting Tests
# =============================================================================

class TestUserPrompting:
    """Tests for user workflow prompting."""
    
    def test_prompt_user_with_candidates(self, temp_workflows_dir):
        """Test prompting user with candidate workflows."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            
            # Add mock workflows
            wf1 = Mock(spec=BaseWorkflow)
            wf1.workflow_id = 'wf1'
            wf1.name = 'Workflow 1'
            wf1.description = 'First workflow'
            wf1.steps = [Mock(), Mock()]
            
            wf2 = Mock(spec=BaseWorkflow)
            wf2.workflow_id = 'wf2'
            wf2.name = 'Workflow 2'
            wf2.description = 'Second workflow'
            wf2.steps = [Mock()]
            
            manager.workflows['wf1'] = wf1
            manager.workflows['wf2'] = wf2
        
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print'):
                result = manager.prompt_user_for_workflow("test task", ['wf1', 'wf2'])
        
        assert result == 'wf1'
    
    def test_prompt_user_select_none(self, temp_workflows_dir):
        """Test user selecting 'None' option."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            
            wf1 = Mock(spec=BaseWorkflow)
            wf1.workflow_id = 'wf1'
            wf1.name = 'Workflow 1'
            wf1.description = 'First workflow'
            wf1.steps = []
            manager.workflows['wf1'] = wf1
        
        with patch('builtins.input', return_value='2'):  # Select "None" option
            with patch('builtins.print'):
                result = manager.prompt_user_for_workflow("test task", ['wf1'])
        
        assert result is None
    
    def test_prompt_user_invalid_input(self, temp_workflows_dir):
        """Test user providing invalid input."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            
            wf1 = Mock(spec=BaseWorkflow)
            wf1.workflow_id = 'wf1'
            wf1.name = 'Workflow 1'
            wf1.description = 'First workflow'
            wf1.steps = []
            manager.workflows['wf1'] = wf1
        
        with patch('builtins.input', return_value='invalid'):
            with patch('builtins.print'):
                result = manager.prompt_user_for_workflow("test task", ['wf1'])
        
        assert result is None
    
    def test_prompt_user_keyboard_interrupt(self, temp_workflows_dir):
        """Test handling keyboard interrupt during prompt."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            
            wf1 = Mock(spec=BaseWorkflow)
            wf1.workflow_id = 'wf1'
            wf1.name = 'Workflow 1'
            wf1.description = 'First workflow'
            wf1.steps = []
            manager.workflows['wf1'] = wf1
        
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with patch('builtins.print'):
                result = manager.prompt_user_for_workflow("test task", ['wf1'])
        
        assert result is None


# =============================================================================
# Workflow Execution Tests
# =============================================================================

class TestWorkflowExecution:
    """Tests for workflow execution."""
    
    @pytest.mark.asyncio
    async def test_execute_workflow_not_found(self, temp_workflows_dir):
        """Test executing non-existent workflow."""
        manager = WorkflowManager(workflows_dir=temp_workflows_dir)
        
        result = await manager.execute_workflow('nonexistent')
        
        assert result['success'] is False
        assert 'not found' in result['error'].lower()
    
    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, temp_workflows_dir, mock_workflow, 
                                           mock_workflow_step, mock_agent_registry):
        """Test successful workflow execution."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(
                workflows_dir=temp_workflows_dir,
                agent_registry=mock_agent_registry
            )
            
            # Setup mock workflow
            mock_workflow.is_complete.side_effect = [False, True]  # Complete after one step
            mock_workflow.get_ready_steps.return_value = [mock_workflow_step]
            manager.workflows['test_workflow'] = mock_workflow
            
            # Setup mock agent
            mock_agent = Mock()
            mock_agent.execute = Mock(return_value={'success': True, 'data': 'result'})
            mock_agent_registry.get_agent.return_value = mock_agent
        
        result = await manager.execute_workflow('test_workflow', auto_confirm=True)
        
        assert result['workflow_id'] == 'test_workflow'
        assert result['workflow_name'] == 'Test Workflow'
        assert 'started_at' in result
        assert len(result['steps']) == 1
    
    @pytest.mark.asyncio
    async def test_execute_workflow_with_context(self, temp_workflows_dir, mock_workflow,
                                                mock_agent_registry):
        """Test workflow execution with initial context."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(
                workflows_dir=temp_workflows_dir,
                agent_registry=mock_agent_registry
            )
            
            mock_workflow.is_complete.return_value = True
            mock_workflow.get_ready_steps.return_value = []
            manager.workflows['test_workflow'] = mock_workflow
        
        context = {'key': 'value', 'task': 'test'}
        result = await manager.execute_workflow('test_workflow', context=context)
        
        # Context should be updated in workflow
        assert 'key' in mock_workflow.context
        assert mock_workflow.context['key'] == 'value'
    
    @pytest.mark.asyncio
    async def test_execute_workflow_marks_active(self, temp_workflows_dir, mock_workflow):
        """Test that workflow is marked as active during execution."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            
            mock_workflow.is_complete.return_value = True
            mock_workflow.get_ready_steps.return_value = []
            manager.workflows['test_workflow'] = mock_workflow
        
        # Before execution
        assert 'test_workflow' not in manager.active_workflows
        
        result = await manager.execute_workflow('test_workflow')
        
        # After execution - should be removed from active
        assert 'test_workflow' not in manager.active_workflows
    
    @pytest.mark.asyncio
    async def test_execute_workflow_handles_exception(self, temp_workflows_dir, mock_workflow):
        """Test workflow execution handles exceptions."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            
            mock_workflow.is_complete.side_effect = Exception("Test error")
            manager.workflows['test_workflow'] = mock_workflow
        
        result = await manager.execute_workflow('test_workflow')
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Test error' in result['error']
    
    @pytest.mark.asyncio
    async def test_execute_step_success(self, temp_workflows_dir, mock_workflow,
                                       mock_workflow_step, mock_agent_registry):
        """Test successful step execution."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(
                workflows_dir=temp_workflows_dir,
                agent_registry=mock_agent_registry
            )
            
            mock_agent = Mock()
            mock_agent.execute = Mock(return_value={'success': True, 'data': 'result'})
            mock_agent_registry.get_agent.return_value = mock_agent
        
        result = await manager._execute_step(mock_workflow_step, mock_workflow, auto_confirm=True)
        
        assert result['step_id'] == 'step1'
        assert result['name'] == 'Test Step'
        assert result['status'] == 'completed'
        
        # Verify step was marked appropriately
        mock_workflow_step.mark_started.assert_called_once()
        mock_workflow_step.mark_completed.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_step_agent_not_found(self, temp_workflows_dir, mock_workflow,
                                               mock_workflow_step, mock_agent_registry):
        """Test step execution when agent not found."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(
                workflows_dir=temp_workflows_dir,
                agent_registry=mock_agent_registry
            )
            
            mock_agent_registry.get_agent.return_value = None
        
        result = await manager._execute_step(mock_workflow_step, mock_workflow, auto_confirm=True)
        
        assert result['status'] == 'failed'
        assert 'not found' in result['error'].lower()
    
    @pytest.mark.asyncio
    async def test_execute_step_no_agent_registry(self, temp_workflows_dir, mock_workflow,
                                                  mock_workflow_step):
        """Test step execution without agent registry."""
        manager = WorkflowManager(workflows_dir=temp_workflows_dir, agent_registry=None)
        
        result = await manager._execute_step(mock_workflow_step, mock_workflow, auto_confirm=True)
        
        assert result['status'] == 'failed'
        assert 'not available' in result['error'].lower()
    
    @pytest.mark.asyncio
    async def test_execute_step_on_error_continue(self, temp_workflows_dir, mock_workflow,
                                                  mock_agent_registry):
        """Test step execution with on_error=continue."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(
                workflows_dir=temp_workflows_dir,
                agent_registry=mock_agent_registry
            )
            
            step = Mock(spec=WorkflowStep)
            step.step_id = 'step1'
            step.name = 'Test Step'
            step.agent = 'code_planner'
            step.params = {}
            step.on_error = 'continue'
            step.mark_started = Mock()
            step.mark_completed = Mock()
            
            mock_agent = Mock()
            mock_agent.execute = Mock(side_effect=Exception("Test error"))
            mock_agent_registry.get_agent.return_value = mock_agent
        
        result = await manager._execute_step(step, mock_workflow, auto_confirm=True)
        
        assert result['status'] == 'completed_with_error'
        assert 'error' in result
        step.mark_completed.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_step_on_error_fail(self, temp_workflows_dir, mock_workflow,
                                              mock_agent_registry):
        """Test step execution with on_error=fail."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(
                workflows_dir=temp_workflows_dir,
                agent_registry=mock_agent_registry
            )
            
            step = Mock(spec=WorkflowStep)
            step.step_id = 'step1'
            step.name = 'Test Step'
            step.agent = 'code_planner'
            step.params = {}
            step.on_error = 'fail'
            step.mark_started = Mock()
            step.mark_failed = Mock()
            
            mock_agent = Mock()
            mock_agent.execute = Mock(side_effect=Exception("Test error"))
            mock_agent_registry.get_agent.return_value = mock_agent
        
        result = await manager._execute_step(step, mock_workflow, auto_confirm=True)
        
        assert result['status'] == 'failed'
        assert 'error' in result
        step.mark_failed.assert_called_once()


# =============================================================================
# Workflow Status Tests
# =============================================================================

class TestWorkflowStatus:
    """Tests for workflow status retrieval."""
    
    def test_get_workflow_status_active(self, temp_workflows_dir, mock_workflow):
        """Test getting status of active workflow."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            manager.active_workflows['test_workflow'] = mock_workflow
        
        status = manager.get_workflow_status('test_workflow')
        
        assert status is not None
        assert status['workflow_id'] == 'test_workflow'
    
    def test_get_workflow_status_inactive(self, temp_workflows_dir, mock_workflow):
        """Test getting status of inactive workflow."""
        with patch.object(WorkflowManager, '_load_workflows'):
            manager = WorkflowManager(workflows_dir=temp_workflows_dir)
            manager.workflows['test_workflow'] = mock_workflow
        
        status = manager.get_workflow_status('test_workflow')
        
        assert status is not None
        assert status['workflow_id'] == 'test_workflow'
    
    def test_get_workflow_status_not_found(self, temp_workflows_dir):
        """Test getting status of non-existent workflow."""
        manager = WorkflowManager(workflows_dir=temp_workflows_dir)
        
        status = manager.get_workflow_status('nonexistent')
        
        assert status is None
