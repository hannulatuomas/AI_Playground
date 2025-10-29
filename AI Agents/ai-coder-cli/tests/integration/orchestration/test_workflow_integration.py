
"""
Integration tests for Workflow System.

Tests complete workflows with multiple agents and tools.
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.integration
class TestCodeGenerationWorkflow:
    """Test complete code generation workflow."""
    
    @pytest.fixture
    def workflow_setup(self, mock_llm_router, mock_agent_registry, mock_tool_registry, temp_project_dir):
        """Set up workflow components."""
        from orchestration.workflows.workflow_manager import WorkflowManager
        
        manager = WorkflowManager(
            llm_router=mock_llm_router,
            agent_registry=mock_agent_registry
        )
        
        return {
            'manager': manager,
            'project_dir': temp_project_dir
        }
    
    def test_full_code_generation_workflow(self, workflow_setup, mock_llm_router):
        """Test full code generation workflow from planning to implementation."""
        import asyncio
        
        manager = workflow_setup['manager']
        project_dir = workflow_setup['project_dir']
        
        # Mock LLM responses for different stages
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Workflow completed successfully'
        }
        
        context = {
            'task': 'Create a simple REST API',
            'project_path': str(project_dir),
            'language': 'python'
        }
        
        # execute_workflow is async, need to run it in event loop
        result = asyncio.run(manager.execute_workflow(
            workflow_id='code_generation',
            context=context,
            auto_confirm=True
        ))
        
        assert result is not None


@pytest.mark.integration
@pytest.mark.slow
class TestProjectInitWorkflow:
    """Test project initialization workflow."""
    
    @pytest.mark.parametrize('language', ['python', 'javascript', 'java'])
    def test_init_project_workflow(self, language, mock_llm_router, mock_agent_registry, temp_dir):
        """Test initializing projects in different languages."""
        import asyncio
        from orchestration.workflows.workflow_manager import WorkflowManager
        
        manager = WorkflowManager(
            llm_router=mock_llm_router,
            agent_registry=mock_agent_registry
        )
        
        # Mock LLM response
        mock_llm_router.query.return_value = {
            'success': True,
            'response': f'Project initialized for {language}'
        }
        
        project_dir = temp_dir / f"test_{language}_project"
        
        context = {
            'task': f'Initialize a new {language} project',
            'project_path': str(project_dir),
            'language': language
        }
        
        # execute_workflow is async
        result = asyncio.run(manager.execute_workflow(
            workflow_id='project_init',
            context=context,
            auto_confirm=True
        ))
        
        assert result is not None
