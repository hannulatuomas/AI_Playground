
"""
Unit tests for Generic Agents.

Tests generic agent implementations (code editor, planner, build, etc.)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


@pytest.mark.unit
class TestGenericCodeEditor:
    """Test suite for Generic Code Editor Agent."""
    
    @pytest.fixture
    def code_editor_agent(self, mock_llm_router, mock_tool_registry):
        """Create a code editor agent for testing."""
        from agents.generic.generic_code_editor import GenericCodeEditor
        
        return GenericCodeEditor(
            name='code_editor',
            description='Generic code editor',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
    
    def test_initialization(self, code_editor_agent):
        """Test code editor initialization."""
        assert code_editor_agent.name == 'code_editor'
        assert code_editor_agent.description == 'Generic code editor'
    
    def test_execute_create_file(self, code_editor_agent, mock_llm_router, sample_task_context):
        """Test creating a new file."""
        task = "Create a new Python file: main.py"
        
        # Mock LLM response
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'File created successfully'
        }
        
        result = code_editor_agent.execute(task, sample_task_context)
        
        assert 'success' in result
        assert 'message' in result


@pytest.mark.unit
class TestGenericCodePlanner:
    """Test suite for Generic Code Planner Agent."""
    
    @pytest.fixture
    def code_planner_agent(self, mock_llm_router, mock_tool_registry):
        """Create a code planner agent for testing."""
        from agents.generic.generic_code_planner import GenericCodePlanner
        
        return GenericCodePlanner(
            name='code_planner',
            description='Generic code planner',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
    
    def test_initialization(self, code_planner_agent):
        """Test code planner initialization."""
        assert code_planner_agent.name == 'code_planner'
    
    def test_execute_planning(self, code_planner_agent, mock_llm_router, sample_task_context):
        """Test planning a coding task."""
        task = "Plan a REST API for user management"
        
        # Mock LLM response
        mock_llm_router.query.return_value = {
            'success': True,
            'response': '1. Define models\n2. Create routes\n3. Implement handlers'
        }
        
        result = code_planner_agent.execute(task, sample_task_context)
        
        assert 'success' in result
        assert 'message' in result


@pytest.mark.unit
class TestGenericBuildAgent:
    """Test suite for Generic Build Agent."""
    
    @pytest.fixture
    def build_agent(self, mock_llm_router, mock_tool_registry):
        """Create a build agent for testing."""
        from agents.generic.generic_build_agent import GenericBuildAgent
        
        return GenericBuildAgent(
            name='build_agent',
            description='Generic build agent',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
    
    def test_initialization(self, build_agent):
        """Test build agent initialization."""
        assert build_agent.name == 'build_agent'
    
    def test_execute_build(self, build_agent, mock_llm_router, sample_task_context):
        """Test building a project."""
        task = "Build the Python project"
        
        # Mock LLM response
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Build completed successfully'
        }
        
        result = build_agent.execute(task, sample_task_context)
        
        assert 'success' in result


@pytest.mark.unit
class TestGenericDebugAgent:
    """Test suite for Generic Debug Agent."""
    
    @pytest.fixture
    def debug_agent(self, mock_llm_router, mock_tool_registry):
        """Create a debug agent for testing."""
        from agents.generic.generic_debug_agent import GenericDebugAgent
        
        return GenericDebugAgent(
            name='debug_agent',
            description='Generic debug agent',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
    
    def test_initialization(self, debug_agent):
        """Test debug agent initialization."""
        assert debug_agent.name == 'debug_agent'
    
    def test_execute_debug(self, debug_agent, mock_llm_router, sample_task_context):
        """Test debugging code."""
        task = "Debug the error in main.py"
        context = {**sample_task_context, 'error': 'NameError: name x is not defined'}
        
        # Mock LLM response
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Error fixed: variable x was not initialized'
        }
        
        result = debug_agent.execute(task, context)
        
        assert 'success' in result


@pytest.mark.unit
class TestGenericDocumentationAgent:
    """Test suite for Generic Documentation Agent."""
    
    @pytest.fixture
    def doc_agent(self, mock_llm_router, mock_tool_registry):
        """Create a documentation agent for testing."""
        from agents.generic.generic_documentation import GenericDocumentationAgent
        
        return GenericDocumentationAgent(
            name='doc_agent',
            description='Generic documentation agent',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
    
    def test_initialization(self, doc_agent):
        """Test documentation agent initialization."""
        assert doc_agent.name == 'doc_agent'
    
    def test_execute_documentation(self, doc_agent, mock_llm_router, sample_task_context):
        """Test generating documentation."""
        task = "Generate documentation for main.py"
        
        # Mock LLM response
        mock_llm_router.query.return_value = {
            'success': True,
            'response': '# Main Module\n\nThis module contains the main function.'
        }
        
        result = doc_agent.execute(task, sample_task_context)
        
        assert 'success' in result
