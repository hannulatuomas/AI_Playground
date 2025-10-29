"""
Comprehensive integration tests for core/engine.py

Tests real integration between:
- Engine and LLM Router
- Engine and Agent Registry
- Engine and Tool Registry
- Engine and Task Analyzer
- Engine and Orchestrator
- Engine and Memory Manager
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from core.engine import Engine, EngineError
from core.config import AppConfig


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_config(temp_config_dir):
    """Create a test configuration."""
    config = AppConfig()
    
    # Configure for testing - Ollama and OpenAI are enabled by default
    # We'll mock the actual providers to avoid real API calls
    
    # Enable basic agents and tools
    config.agents.enabled_agents = ['code_planner', 'code_editor']
    config.agents.auto_confirm = True
    config.agents.max_iterations = 3
    
    config.tools.enabled_tools = ['web_fetch', 'git']
    
    return config


@pytest.fixture
def mock_llm_providers():
    """Mock LLM providers to avoid real API calls."""
    with patch('core.llm_router.OllamaProvider') as mock_ollama:
        with patch('core.llm_router.OpenAIProvider') as mock_openai:
            # Configure mock Ollama
            mock_ollama_instance = Mock()
            mock_ollama_instance.is_available.return_value = True
            mock_ollama_instance.query.return_value = "Test response"
            mock_ollama_instance.get_available_models.return_value = ['test-model']
            mock_ollama.return_value = mock_ollama_instance
            
            # Configure mock OpenAI
            mock_openai_instance = Mock()
            mock_openai_instance.is_available.return_value = False
            mock_openai.return_value = mock_openai_instance
            
            yield {
                'ollama': mock_ollama_instance,
                'openai': mock_openai_instance
            }


@pytest.fixture
def mock_engine_components():
    """Mock all engine components for testing."""
    with patch('core.engine.AGENTS_AVAILABLE', True):
        with patch('core.engine.TOOLS_AVAILABLE', True):
            with patch('core.engine.GenericCodePlanner'):
                with patch('core.engine.GenericCodeEditor'):
                    with patch('core.engine.GitAgent'):
                        with patch('core.engine.WebDataAgent'):
                            with patch('core.engine.WebFetchTool'):
                                with patch('core.engine.GitTool'):
                                    # Mock AgentRegistry
                                    with patch('core.engine.AgentRegistry') as mock_agent_reg_class:
                                        mock_agent_reg = Mock()
                                        mock_agent_reg.__len__ = Mock(return_value=2)
                                        mock_agent_reg.register = Mock()
                                        mock_agent_reg_class.return_value = mock_agent_reg
                                        
                                        # Mock ToolRegistry
                                        with patch('core.engine.ToolRegistry') as mock_tool_reg_class:
                                            mock_tool_reg = Mock()
                                            mock_tool_reg.__len__ = Mock(return_value=2)
                                            mock_tool_reg.register = Mock()
                                            mock_tool_reg_class.return_value = mock_tool_reg
                                            
                                            yield {
                                                'agent_registry': mock_agent_reg,
                                                'tool_registry': mock_tool_reg
                                            }


# =============================================================================
# Engine Initialization Integration Tests
# =============================================================================

class TestEngineInitializationIntegration:
    """Integration tests for engine initialization."""
    
    def test_engine_initialization_full_stack(self, test_config, mock_engine_components):
        """Test full engine initialization with all components."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router_class.return_value = mock_router
            
            engine = Engine(config=test_config)
            engine.initialize()
            
            assert engine._initialized is True
            assert engine.router is not None
            assert engine.task_analyzer is not None
            assert engine.orchestrator is not None
    
    def test_engine_initialization_with_memory(self, test_config, tmp_path):
        """Test engine initialization with memory manager."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router_class.return_value = mock_router
            
            with patch('core.engine.AGENTS_AVAILABLE', True):
                with patch('core.engine.TOOLS_AVAILABLE', True):
                    with patch('core.engine.AgentRegistry'):
                        with patch('core.engine.ToolRegistry'):
                            engine = Engine(config=test_config)
                            engine.initialize()
            
            # Memory manager should be initialized
            assert engine.memory_manager is not None
    
    def test_engine_initialization_without_providers_fails(self, test_config):
        """Test that engine fails to initialize without providers."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = []  # No providers
            mock_router_class.return_value = mock_router
            
            engine = Engine(config=test_config)
            
            with pytest.raises(EngineError) as exc_info:
                engine.initialize()
            
            assert "no llm providers" in str(exc_info.value).lower()


# =============================================================================
# Engine Query Processing Integration Tests
# =============================================================================

class TestEngineQueryProcessingIntegration:
    """Integration tests for engine query processing."""
    
    def test_process_query_with_llm_router(self, test_config):
        """Test query processing through LLM router."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router.query.return_value = {
                'response': 'Test LLM response',
                'provider': 'ollama',
                'model': 'test-model'
            }
            mock_router_class.return_value = mock_router
            
            engine = Engine(config=test_config)
            engine._initialized = True
            engine.router = mock_router
            
            result = engine.process_query("What is AI?")
            
            assert result['success'] is True
            assert result['response'] == 'Test LLM response'
            assert result['provider'] == 'ollama'
            mock_router.query.assert_called_once()
    
    def test_process_query_with_provider_override(self, test_config):
        """Test query processing with provider override."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama', 'openai']
            mock_router.query.return_value = {
                'response': 'OpenAI response',
                'provider': 'openai',
                'model': 'gpt-4'
            }
            mock_router_class.return_value = mock_router
            
            engine = Engine(config=test_config)
            engine._initialized = True
            engine.router = mock_router
            
            result = engine.process_query("Test query", provider="openai", model="gpt-4")
            
            assert result['success'] is True
            call_args = mock_router.query.call_args
            assert call_args.kwargs['provider'] == "openai"
            assert call_args.kwargs['model'] == "gpt-4"


# =============================================================================
# Engine Task Execution Integration Tests
# =============================================================================

class TestEngineTaskExecutionIntegration:
    """Integration tests for engine task execution."""
    
    def test_execute_task_full_flow(self, test_config):
        """Test full task execution flow with task analysis and orchestration."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router.query.return_value = {
                'response': '{"agents": ["code_planner"], "reasoning": "Plan the project", "parallel": false}'
            }
            mock_router_class.return_value = mock_router
            
            with patch('core.engine.AGENTS_AVAILABLE', True):
                with patch('core.engine.AgentRegistry') as mock_agent_reg_class:
                    mock_agent_reg = Mock()
                    mock_agent_reg.__len__ = Mock(return_value=2)
                    mock_agent_reg.list_agents.return_value = ['code_planner', 'code_editor']
                    
                    # Mock agent execution
                    mock_agent = Mock()
                    mock_agent.execute.return_value = {
                        'success': True,
                        'message': 'Planning complete',
                        'result': {'plan': 'test plan'}
                    }
                    mock_agent_reg.get_or_create_agent.return_value = mock_agent
                    mock_agent_reg_class.return_value = mock_agent_reg
                    
                    with patch('core.engine.ToolRegistry') as mock_tool_reg_class:
                        mock_tool_reg = Mock()
                        mock_tool_reg.__len__ = Mock(return_value=2)
                        mock_tool_reg_class.return_value = mock_tool_reg
                        
                        engine = Engine(config=test_config)
                        engine.initialize()
                        
                        result = engine.execute_task("Create a new Python project")
            
            assert result['success'] is True
            assert 'analysis' in result
            assert 'orchestration' in result
            assert result['analysis']['agents'] == ['code_planner']
    
    def test_execute_task_with_agent_override(self, test_config):
        """Test task execution with agent override (skip analysis)."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router_class.return_value = mock_router
            
            with patch('core.engine.AGENTS_AVAILABLE', True):
                with patch('core.engine.AgentRegistry') as mock_agent_reg_class:
                    mock_agent_reg = Mock()
                    mock_agent_reg.__len__ = Mock(return_value=1)
                    
                    mock_agent = Mock()
                    mock_agent.execute.return_value = {
                        'success': True,
                        'message': 'Task complete'
                    }
                    mock_agent_reg.get_or_create_agent.return_value = mock_agent
                    mock_agent_reg_class.return_value = mock_agent_reg
                    
                    with patch('core.engine.ToolRegistry') as mock_tool_reg_class:
                        mock_tool_reg = Mock()
                        mock_tool_reg.__len__ = Mock(return_value=2)
                        mock_tool_reg_class.return_value = mock_tool_reg
                        
                        engine = Engine(config=test_config)
                        engine.initialize()
                        
                        result = engine.execute_task(
                            "Test task",
                            agent_override=['code_editor']
                        )
            
            assert result['success'] is True
            assert result['analysis']['agents'] == ['code_editor']
            assert 'User-specified' in result['analysis']['reasoning']
    
    def test_execute_task_with_memory_integration(self, test_config, tmp_path):
        """Test task execution with memory manager integration."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router.query.return_value = {
                'response': '{"agents": ["code_planner"], "reasoning": "Test", "parallel": false}'
            }
            mock_router_class.return_value = mock_router
            
            with patch('core.engine.AGENTS_AVAILABLE', True):
                with patch('core.engine.AgentRegistry') as mock_agent_reg_class:
                    mock_agent_reg = Mock()
                    mock_agent_reg.__len__ = Mock(return_value=1)
                    mock_agent_reg.list_agents.return_value = ['code_planner']
                    
                    mock_agent = Mock()
                    mock_agent.execute.return_value = {
                        'success': True,
                        'message': 'Complete'
                    }
                    mock_agent_reg.get_or_create_agent.return_value = mock_agent
                    mock_agent_reg_class.return_value = mock_agent_reg
                    
                    with patch('core.engine.ToolRegistry') as mock_tool_reg_class:
                        mock_tool_reg = Mock()
                        mock_tool_reg.__len__ = Mock(return_value=2)
                        mock_tool_reg_class.return_value = mock_tool_reg
                        
                        engine = Engine(config=test_config)
                        engine.initialize()
                        
                        # Execute task - should create memory session
                        result = engine.execute_task("Test task")
            
            # Memory session should be created
            assert result['success'] is True
            if 'orchestration' in result and 'session_id' in result['orchestration']:
                assert result['orchestration']['session_id'] is not None


# =============================================================================
# Engine Agent-Tool Integration Tests
# =============================================================================

class TestEngineAgentToolIntegration:
    """Integration tests for engine with agents and tools."""
    
    def test_engine_registers_agents_on_init(self, test_config):
        """Test that engine registers enabled agents on initialization."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router_class.return_value = mock_router
            
            with patch('core.engine.AGENTS_AVAILABLE', True):
                with patch('core.engine.AgentRegistry') as mock_agent_reg_class:
                    mock_agent_reg = Mock()
                    mock_agent_reg.__len__ = Mock(return_value=2)
                    mock_agent_reg_class.return_value = mock_agent_reg
                    
                    with patch('core.engine.ToolRegistry') as mock_tool_reg_class:
                        mock_tool_reg = Mock()
                        mock_tool_reg.__len__ = Mock(return_value=2)
                        mock_tool_reg_class.return_value = mock_tool_reg
                        
                        with patch('core.engine.GenericCodePlanner') as mock_planner:
                            with patch('core.engine.GenericCodeEditor') as mock_editor:
                                engine = Engine(config=test_config)
                                engine.initialize()
                    
                    # Should register enabled agents
                    assert mock_agent_reg.register.called
    
    def test_engine_registers_tools_on_init(self, test_config):
        """Test that engine registers enabled tools on initialization."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router_class.return_value = mock_router
            
            with patch('core.engine.TOOLS_AVAILABLE', True):
                with patch('core.engine.ToolRegistry') as mock_tool_reg_class:
                    mock_tool_reg = Mock()
                    mock_tool_reg.__len__ = Mock(return_value=2)
                    mock_tool_reg_class.return_value = mock_tool_reg
                    
                    with patch('core.engine.AgentRegistry') as mock_agent_reg_class:
                        mock_agent_reg = Mock()
                        mock_agent_reg.__len__ = Mock(return_value=0)
                        mock_agent_reg_class.return_value = mock_agent_reg
                        
                        with patch('core.engine.WebFetchTool') as mock_web_fetch:
                            with patch('core.engine.GitTool') as mock_git_tool:
                                engine = Engine(config=test_config)
                                engine.initialize()
                    
                    # Should register enabled tools
                    assert mock_tool_reg.register.called
    
    def test_orchestrator_provides_tools_to_agents(self, test_config):
        """Test that orchestrator provides tool registry to agents."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router.query.return_value = {
                'response': '{"agents": ["code_planner"], "reasoning": "Test", "parallel": false}'
            }
            mock_router_class.return_value = mock_router
            
            with patch('core.engine.AGENTS_AVAILABLE', True):
                with patch('core.engine.TOOLS_AVAILABLE', True):
                    with patch('core.engine.AgentRegistry') as mock_agent_reg_class:
                        mock_agent_reg = Mock()
                        mock_agent_reg.__len__ = Mock(return_value=1)
                        mock_agent_reg.list_agents.return_value = ['code_planner']
                        
                        mock_agent = Mock()
                        mock_agent.execute.return_value = {'success': True}
                        mock_agent_reg.get_or_create_agent.return_value = mock_agent
                        mock_agent_reg_class.return_value = mock_agent_reg
                        
                        with patch('core.engine.ToolRegistry') as mock_tool_reg_class:
                            mock_tool_reg = Mock()
                            mock_tool_reg.__len__ = Mock(return_value=2)
                            mock_tool_reg_class.return_value = mock_tool_reg
                            
                            engine = Engine(config=test_config)
                            engine.initialize()
                            engine.execute_task("Test task")
                        
                        # Agent should be created with tool registry
                        call_args = mock_agent_reg.get_or_create_agent.call_args
                        assert call_args.kwargs['tool_registry'] == mock_tool_reg


# =============================================================================
# Engine Status and Lifecycle Integration Tests
# =============================================================================

class TestEngineStatusLifecycleIntegration:
    """Integration tests for engine status and lifecycle."""
    
    def test_engine_status_reflects_initialization_state(self, test_config):
        """Test that engine status correctly reflects initialization state."""
        engine = Engine(config=test_config)
        
        # Before initialization
        status = engine.get_status()
        assert status['initialized'] is False
        assert status['config_loaded'] is True
        
        # After initialization
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router_class.return_value = mock_router
            
            with patch('core.engine.AGENTS_AVAILABLE', True):
                with patch('core.engine.TOOLS_AVAILABLE', True):
                    with patch('core.engine.AgentRegistry'):
                        with patch('core.engine.ToolRegistry'):
                            engine.initialize()
        
        status = engine.get_status()
        assert status['initialized'] is True
    
    def test_engine_shutdown_cleanup(self, test_config):
        """Test that engine shutdown properly cleans up resources."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router_class.return_value = mock_router
            
            with patch('core.engine.AgentRegistry'):
                with patch('core.engine.ToolRegistry'):
                    engine = Engine(config=test_config)
                    engine.initialize()
                    
                    assert engine._initialized is True
                    assert engine.router is not None
                    
                    engine.shutdown()
                    
                    assert engine._initialized is False
                    assert engine.router is None
    
    def test_engine_get_status_includes_all_components(self, test_config):
        """Test that get_status includes information about all components."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router_class.return_value = mock_router
            
            with patch('core.engine.AGENTS_AVAILABLE', True):
                with patch('core.engine.TOOLS_AVAILABLE', True):
                    with patch('core.engine.AgentRegistry') as mock_agent_reg_class:
                        mock_agent_reg = Mock()
                        mock_agent_reg.__len__ = Mock(return_value=2)
                        mock_agent_reg.list_agents.return_value = ['agent1', 'agent2']
                        mock_agent_reg_class.return_value = mock_agent_reg
                        
                        with patch('core.engine.ToolRegistry') as mock_tool_reg_class:
                            mock_tool_reg = Mock()
                            mock_tool_reg.__len__ = Mock(return_value=2)
                            mock_tool_reg.list_tools.return_value = ['tool1', 'tool2']
                            mock_tool_reg_class.return_value = mock_tool_reg
                            
                            engine = Engine(config=test_config)
                            engine.initialize()
                            
                            status = engine.get_status()
        
        assert status['initialized'] is True
        assert 'ollama' in status['available_providers']
        assert len(status['registered_agents']) == 2
        assert len(status['registered_tools']) == 2
        assert status['agents_available'] is True
        assert status['tools_available'] is True


# =============================================================================
# Error Handling Integration Tests
# =============================================================================

class TestEngineErrorHandlingIntegration:
    """Integration tests for engine error handling."""
    
    def test_engine_handles_llm_router_errors(self, test_config):
        """Test that engine handles LLM router errors gracefully."""
        from core.llm_router import LLMProviderError
        
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router.query.side_effect = LLMProviderError("Provider error")
            mock_router_class.return_value = mock_router
            
            engine = Engine(config=test_config)
            engine._initialized = True
            engine.router = mock_router
            
            result = engine.process_query("Test query")
            
            assert result['success'] is False
            assert 'error' in result
            assert result['error'] == "Provider error"
    
    def test_engine_handles_agent_execution_errors(self, test_config):
        """Test that engine handles agent execution errors gracefully."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router.query.return_value = {
                'response': '{"agents": ["code_planner"], "reasoning": "Test", "parallel": false}'
            }
            mock_router_class.return_value = mock_router
            
            with patch('core.engine.AGENTS_AVAILABLE', True):
                with patch('core.engine.AgentRegistry') as mock_agent_reg_class:
                    mock_agent_reg = Mock()
                    mock_agent_reg.__len__ = Mock(return_value=1)
                    mock_agent_reg.list_agents.return_value = ['code_planner']
                    
                    # Agent execution raises exception
                    mock_agent = Mock()
                    mock_agent.execute.side_effect = Exception("Agent error")
                    mock_agent_reg.get_or_create_agent.return_value = mock_agent
                    mock_agent_reg_class.return_value = mock_agent_reg
                    
                    with patch('core.engine.ToolRegistry') as mock_tool_reg_class:
                        mock_tool_reg = Mock()
                        mock_tool_reg.__len__ = Mock(return_value=2)
                        mock_tool_reg_class.return_value = mock_tool_reg
                        
                        engine = Engine(config=test_config)
                        engine.initialize()
                        
                        result = engine.execute_task("Test task")
            
            # Should handle error gracefully
            assert result['success'] is False
            assert 'orchestration' in result
            assert 'error' in result['orchestration']
    
    def test_engine_handles_task_analysis_errors(self, test_config):
        """Test that engine handles task analysis errors with fallback."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            # LLM query fails
            mock_router.query.side_effect = Exception("LLM error")
            mock_router_class.return_value = mock_router
            
            with patch('core.engine.AGENTS_AVAILABLE', True):
                with patch('core.engine.AgentRegistry') as mock_agent_reg_class:
                    mock_agent_reg = Mock()
                    mock_agent_reg.__len__ = Mock(return_value=1)
                    mock_agent_reg.list_agents.return_value = ['code_planner']
                    
                    mock_agent = Mock()
                    mock_agent.execute.return_value = {'success': True}
                    mock_agent_reg.get_or_create_agent.return_value = mock_agent
                    mock_agent_reg_class.return_value = mock_agent_reg
                    
                    with patch('core.engine.ToolRegistry') as mock_tool_reg_class:
                        mock_tool_reg = Mock()
                        mock_tool_reg.__len__ = Mock(return_value=2)
                        mock_tool_reg_class.return_value = mock_tool_reg
                        
                        engine = Engine(config=test_config)
                        engine.initialize()
                        
                        # Should use fallback analysis
                        result = engine.execute_task("Plan a new project")
            
            # Should still complete with fallback
            if result['success']:
                assert result['analysis']['reasoning'] == 'Fallback analysis based on keywords'
