
"""
Unit tests for Agent Base Class.

Tests the abstract base agent class and its core functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock
from agents.base.agent_base import Agent


class ConcreteAgent(Agent):
    """Concrete agent implementation for testing."""
    
    def execute(self, task, context):
        """Implementation of execute method."""
        return {
            'success': True,
            'message': f'Executed: {task}',
            'data': {'context': context}
        }


@pytest.mark.unit
class TestAgentBase:
    """Test suite for Agent base class."""
    
    def test_agent_initialization(self, mock_llm_router, mock_tool_registry, mock_memory_manager):
        """Test agent initialization with all parameters."""
        config = {'test_param': 'value'}
        
        agent = ConcreteAgent(
            name='test_agent',
            description='Test agent description',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry,
            config=config,
            memory_manager=mock_memory_manager
        )
        
        assert agent.name == 'test_agent'
        assert agent.description == 'Test agent description'
        assert agent.llm_router is mock_llm_router
        assert agent.tool_registry is mock_tool_registry
        assert agent.config == config
        assert agent.memory_manager is mock_memory_manager
        assert agent.logger is not None
    
    def test_agent_initialization_without_optional_params(self):
        """Test agent initialization with minimal parameters."""
        agent = ConcreteAgent(
            name='minimal_agent',
            description='Minimal agent'
        )
        
        assert agent.name == 'minimal_agent'
        assert agent.description == 'Minimal agent'
        assert agent.llm_router is None
        assert agent.tool_registry is None
        assert agent.config == {}
        assert agent.memory_manager is None
    
    def test_execute_method(self):
        """Test execute method implementation."""
        agent = ConcreteAgent(
            name='exec_agent',
            description='Test execute'
        )
        
        result = agent.execute('test task', {'key': 'value'})
        
        assert result['success'] is True
        assert 'test task' in result['message']
        assert 'context' in result['data']
    
    def test_abstract_execute_method(self):
        """Test that Agent class is abstract and requires execute implementation."""
        # Cannot instantiate Agent directly without implementing execute
        with pytest.raises(TypeError):
            Agent(name='abstract', description='test')
    
    def test_get_llm_response_helper(self, mock_llm_router):
        """Test _get_llm_response helper method."""
        agent = ConcreteAgent(
            name='llm_agent',
            description='LLM test agent',
            llm_router=mock_llm_router
        )
        
        # Mock the response
        mock_llm_router.query.return_value = {
            'success': True,
            'response': 'Test response'
        }
        
        response = agent._get_llm_response('Test prompt')
        
        assert response['success'] is True
        assert response['response'] == 'Test response'
        mock_llm_router.query.assert_called_once()
    
    def test_agent_logging(self, caplog):
        """Test that agent initialization logs correctly."""
        agent = ConcreteAgent(
            name='log_test_agent',
            description='Logging test'
        )
        
        assert 'initialized' in caplog.text.lower()
        assert 'log_test_agent' in caplog.text
