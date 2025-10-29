"""
Comprehensive unit tests for core/engine.py

Tests cover:
- EngineError exception
- TaskAnalyzer class
- Orchestrator class
- Engine class
- Rich UI helper functions
"""

import pytest
import logging
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
from typing import Dict, Any, List

from core.engine import (
    EngineError,
    TaskAnalyzer,
    Orchestrator,
    Engine,
    _print_engine_status,
    _create_task_summary_panel,
    _create_orchestration_table,
)
from core.config import AppConfig
from core.llm_router import LLMRouter
from core.memory import MemoryManager


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_config():
    """Create a mock AppConfig."""
    config = Mock(spec=AppConfig)
    config.agents = Mock()
    config.agents.auto_confirm = True
    config.agents.max_iterations = 10
    config.agents.enabled_agents = ['code_planner', 'code_editor', 'git_agent', 'web_data']
    config.agents.model_dump = Mock(return_value={'auto_confirm': True})
    config.tools = Mock()
    config.tools.enabled_tools = ['web_fetch', 'git']
    config.tools.model_dump = Mock(return_value={})
    config.mask_sensitive_data = Mock(return_value={'masked': True})
    return config


@pytest.fixture
def mock_llm_router():
    """Create a mock LLMRouter."""
    router = Mock(spec=LLMRouter)
    router.query = Mock(return_value={
        'response': '{"agents": ["code_planner"], "reasoning": "Test", "parallel": false}',
        'provider': 'ollama',
        'model': 'test-model'
    })
    router.get_available_providers = Mock(return_value=['ollama'])
    return router


@pytest.fixture
def mock_agent_registry():
    """Create a mock AgentRegistry."""
    registry = Mock()
    registry.list_agents = Mock(return_value=['code_planner', 'code_editor', 'git_agent'])
    registry.get_or_create_agent = Mock()
    registry.__len__ = Mock(return_value=3)
    return registry


@pytest.fixture
def mock_tool_registry():
    """Create a mock ToolRegistry."""
    registry = Mock()
    registry.list_tools = Mock(return_value=['web_fetch', 'git'])
    registry.__len__ = Mock(return_value=2)
    return registry


@pytest.fixture
def mock_memory_manager():
    """Create a mock MemoryManager."""
    manager = Mock(spec=MemoryManager)
    manager.create_session = Mock(return_value='test-session-123')
    manager.add_user_message = Mock()
    manager.add_agent_message = Mock()
    return manager


@pytest.fixture
def task_analyzer(mock_llm_router):
    """Create a TaskAnalyzer instance."""
    return TaskAnalyzer(mock_llm_router)


@pytest.fixture
def orchestrator(mock_agent_registry, mock_tool_registry, mock_llm_router, 
                mock_config, mock_memory_manager):
    """Create an Orchestrator instance."""
    return Orchestrator(
        agent_registry=mock_agent_registry,
        tool_registry=mock_tool_registry,
        llm_router=mock_llm_router,
        config=mock_config,
        memory_manager=mock_memory_manager
    )


# =============================================================================
# EngineError Tests
# =============================================================================

class TestEngineError:
    """Tests for EngineError exception."""
    
    def test_engine_error_is_exception(self):
        """Test that EngineError is an Exception."""
        assert issubclass(EngineError, Exception)
    
    def test_engine_error_can_be_raised(self):
        """Test that EngineError can be raised with a message."""
        with pytest.raises(EngineError) as exc_info:
            raise EngineError("Test error message")
        
        assert str(exc_info.value) == "Test error message"
    
    def test_engine_error_with_empty_message(self):
        """Test EngineError with empty message."""
        with pytest.raises(EngineError) as exc_info:
            raise EngineError("")
        
        assert str(exc_info.value) == ""


# =============================================================================
# TaskAnalyzer Tests
# =============================================================================

class TestTaskAnalyzer:
    """Tests for TaskAnalyzer class."""
    
    def test_initialization(self, mock_llm_router):
        """Test TaskAnalyzer initialization."""
        analyzer = TaskAnalyzer(mock_llm_router)
        
        assert analyzer.llm_router == mock_llm_router
        assert analyzer.logger is not None
        assert isinstance(analyzer.logger, logging.Logger)
    
    def test_analyze_task_success(self, task_analyzer, mock_llm_router):
        """Test successful task analysis."""
        task = "Create a new Python project"
        available_agents = ['code_planner', 'code_editor']
        
        mock_llm_router.query.return_value = {
            'response': '{"agents": ["code_planner", "code_editor"], "reasoning": "Need to plan and create", "parallel": false}'
        }
        
        result = task_analyzer.analyze_task(task, available_agents)
        
        assert result['agents'] == ['code_planner', 'code_editor']
        assert result['reasoning'] == 'Need to plan and create'
        assert result['parallel'] is False
        
        # Verify LLM was called
        mock_llm_router.query.assert_called_once()
        call_args = mock_llm_router.query.call_args
        assert 'prompt' in call_args.kwargs or len(call_args.args) > 0
        assert 'temperature' in call_args.kwargs
    
    def test_analyze_task_with_llm_failure(self, task_analyzer, mock_llm_router):
        """Test task analysis with LLM failure falls back to keyword matching."""
        task = "Create a new Python project with git"
        available_agents = ['code_planner', 'code_editor', 'git_agent']
        
        # Make LLM query fail
        mock_llm_router.query.side_effect = Exception("LLM error")
        
        result = task_analyzer.analyze_task(task, available_agents)
        
        # Should fallback to keyword-based analysis
        assert 'agents' in result
        assert 'reasoning' in result
        assert result['reasoning'] == 'Fallback analysis based on keywords'
        assert isinstance(result['agents'], list)
    
    def test_parse_analysis_valid_json(self, task_analyzer):
        """Test parsing valid JSON analysis response."""
        response = '{"agents": ["code_planner"], "reasoning": "Test reasoning", "parallel": true}'
        
        result = task_analyzer._parse_analysis(response)
        
        assert result['agents'] == ['code_planner']
        assert result['reasoning'] == 'Test reasoning'
        assert result['parallel'] is True
    
    def test_parse_analysis_json_with_extra_text(self, task_analyzer):
        """Test parsing JSON with surrounding text."""
        response = 'Here is the analysis: {"agents": ["code_editor"], "reasoning": "Edit files"} Done!'
        
        result = task_analyzer._parse_analysis(response)
        
        assert result['agents'] == ['code_editor']
        assert result['reasoning'] == 'Edit files'
    
    def test_parse_analysis_missing_fields(self, task_analyzer):
        """Test parsing JSON with missing fields adds defaults."""
        response = '{"agents": ["code_planner"]}'
        
        result = task_analyzer._parse_analysis(response)
        
        assert result['agents'] == ['code_planner']
        assert result['reasoning'] == 'No reasoning provided'
        assert result['parallel'] is False
    
    def test_parse_analysis_invalid_json(self, task_analyzer):
        """Test parsing invalid JSON raises exception."""
        response = 'This is not JSON'
        
        with pytest.raises(Exception):
            task_analyzer._parse_analysis(response)
    
    def test_fallback_analysis_plan_keywords(self, task_analyzer):
        """Test fallback analysis detects planning keywords."""
        task = "Plan and design a new architecture"
        available_agents = ['code_planner', 'code_editor']
        
        result = task_analyzer._fallback_analysis(task, available_agents)
        
        assert 'code_planner' in result['agents']
        assert result['parallel'] is False
    
    def test_fallback_analysis_create_keywords(self, task_analyzer):
        """Test fallback analysis detects creation keywords."""
        task = "Create and write new files"
        available_agents = ['code_planner', 'code_editor']
        
        result = task_analyzer._fallback_analysis(task, available_agents)
        
        assert 'code_editor' in result['agents']
    
    def test_fallback_analysis_git_keywords(self, task_analyzer):
        """Test fallback analysis detects git keywords."""
        task = "Commit and push changes to git"
        available_agents = ['code_planner', 'git_agent']
        
        result = task_analyzer._fallback_analysis(task, available_agents)
        
        assert 'git_agent' in result['agents']
    
    def test_fallback_analysis_web_keywords(self, task_analyzer):
        """Test fallback analysis detects web keywords."""
        task = "Fetch and scrape data from URL"
        available_agents = ['web_data', 'code_editor']
        
        result = task_analyzer._fallback_analysis(task, available_agents)
        
        assert 'web_data' in result['agents']
    
    def test_fallback_analysis_no_keywords_defaults_to_planner(self, task_analyzer):
        """Test fallback analysis defaults to planner when no keywords match."""
        task = "Some random task"
        available_agents = ['code_planner', 'code_editor']
        
        result = task_analyzer._fallback_analysis(task, available_agents)
        
        assert result['agents'] == ['code_planner']
    
    def test_build_analysis_prompt(self, task_analyzer):
        """Test building the analysis prompt."""
        task = "Create a Python project"
        available_agents = ['code_planner', 'code_editor']
        
        prompt = task_analyzer._build_analysis_prompt(task, available_agents)
        
        assert task in prompt
        assert 'code_planner' in prompt
        assert 'code_editor' in prompt
        assert 'JSON' in prompt
        assert '"agents"' in prompt


# =============================================================================
# Orchestrator Tests
# =============================================================================

class TestOrchestrator:
    """Tests for Orchestrator class."""
    
    def test_initialization(self, mock_agent_registry, mock_tool_registry, 
                          mock_llm_router, mock_config, mock_memory_manager):
        """Test Orchestrator initialization."""
        orch = Orchestrator(
            agent_registry=mock_agent_registry,
            tool_registry=mock_tool_registry,
            llm_router=mock_llm_router,
            config=mock_config,
            memory_manager=mock_memory_manager
        )
        
        assert orch.agent_registry == mock_agent_registry
        assert orch.tool_registry == mock_tool_registry
        assert orch.llm_router == mock_llm_router
        assert orch.config == mock_config
        assert orch.memory_manager == mock_memory_manager
        assert orch.logger is not None
    
    def test_execute_task_single_agent_success(self, orchestrator, mock_agent_registry,
                                              mock_memory_manager):
        """Test executing task with single agent successfully."""
        task = "Test task"
        agent_sequence = ['code_planner']
        
        # Mock agent execution
        mock_agent = Mock()
        mock_agent.execute = Mock(return_value={
            'success': True,
            'message': 'Task completed',
            'result': 'test result'
        })
        mock_agent_registry.get_or_create_agent.return_value = mock_agent
        
        result = orchestrator.execute_task(task, agent_sequence)
        
        assert result['success'] is True
        assert len(result['results']) == 1
        assert result['results'][0]['agent'] == 'code_planner'
        assert result['final_result']['success'] is True
        assert 'session_id' in result
        
        # Verify memory operations
        mock_memory_manager.create_session.assert_called_once()
        mock_memory_manager.add_user_message.assert_called_once()
        mock_memory_manager.add_agent_message.assert_called_once()
    
    def test_execute_task_multiple_agents(self, orchestrator, mock_agent_registry,
                                         mock_memory_manager):
        """Test executing task with multiple agents."""
        task = "Complex task"
        agent_sequence = ['code_planner', 'code_editor', 'git_agent']
        
        # Mock agent execution
        mock_agent = Mock()
        mock_agent.execute = Mock(return_value={
            'success': True,
            'message': 'Step completed',
            'result': 'step result'
        })
        mock_agent_registry.get_or_create_agent.return_value = mock_agent
        
        result = orchestrator.execute_task(task, agent_sequence)
        
        assert result['success'] is True
        assert len(result['results']) == 3
        assert result['results'][0]['agent'] == 'code_planner'
        assert result['results'][1]['agent'] == 'code_editor'
        assert result['results'][2]['agent'] == 'git_agent'
        
        # Verify all agents were executed
        assert mock_agent_registry.get_or_create_agent.call_count == 3
        assert mock_agent.execute.call_count == 3
    
    def test_execute_task_agent_failure(self, orchestrator, mock_agent_registry):
        """Test executing task when an agent fails."""
        task = "Test task"
        agent_sequence = ['code_planner', 'code_editor']
        
        # First agent succeeds, second fails
        mock_agent1 = Mock()
        mock_agent1.execute = Mock(return_value={
            'success': True,
            'message': 'Success'
        })
        
        mock_agent2 = Mock()
        mock_agent2.execute = Mock(return_value={
            'success': False,
            'message': 'Failed'
        })
        
        mock_agent_registry.get_or_create_agent.side_effect = [mock_agent1, mock_agent2]
        
        result = orchestrator.execute_task(task, agent_sequence)
        
        assert result['success'] is False  # Overall failure
        assert len(result['results']) == 2
        assert result['results'][0]['result']['success'] is True
        assert result['results'][1]['result']['success'] is False
    
    def test_execute_task_with_existing_session(self, orchestrator, mock_agent_registry,
                                               mock_memory_manager):
        """Test executing task with existing session ID."""
        task = "Test task"
        agent_sequence = ['code_planner']
        context = {'session_id': 'existing-session-123'}
        
        mock_agent = Mock()
        mock_agent.execute = Mock(return_value={'success': True, 'message': 'Done'})
        mock_agent_registry.get_or_create_agent.return_value = mock_agent
        
        result = orchestrator.execute_task(task, agent_sequence, context)
        
        # Should not create new session
        mock_memory_manager.create_session.assert_not_called()
        
        # But should add messages to existing session
        mock_memory_manager.add_user_message.assert_called_once()
        assert 'existing-session-123' in str(mock_memory_manager.add_user_message.call_args)
    
    def test_execute_task_max_iterations(self, orchestrator, mock_agent_registry, mock_config):
        """Test that max iterations limit is respected."""
        task = "Test task"
        # Create sequence longer than max iterations
        agent_sequence = ['agent' + str(i) for i in range(20)]
        mock_config.agents.max_iterations = 5
        
        mock_agent = Mock()
        mock_agent.execute = Mock(return_value={'success': True, 'message': 'Done'})
        mock_agent_registry.get_or_create_agent.return_value = mock_agent
        
        result = orchestrator.execute_task(task, agent_sequence)
        
        # Should stop at max iterations
        assert len(result['results']) <= 6  # max_iterations + 1 (starts at 0)
    
    def test_execute_task_exception_handling(self, orchestrator, mock_agent_registry):
        """Test that exceptions during execution are handled."""
        task = "Test task"
        agent_sequence = ['code_planner']
        
        # Make agent execution raise exception
        mock_agent = Mock()
        mock_agent.execute = Mock(side_effect=Exception("Test error"))
        mock_agent_registry.get_or_create_agent.return_value = mock_agent
        
        result = orchestrator.execute_task(task, agent_sequence)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Test error' in result['message']
    
    def test_execute_task_no_memory_manager(self, mock_agent_registry, mock_tool_registry,
                                           mock_llm_router, mock_config):
        """Test executing task without memory manager."""
        orch = Orchestrator(
            agent_registry=mock_agent_registry,
            tool_registry=mock_tool_registry,
            llm_router=mock_llm_router,
            config=mock_config,
            memory_manager=None
        )
        
        task = "Test task"
        agent_sequence = ['code_planner']
        
        mock_agent = Mock()
        mock_agent.execute = Mock(return_value={'success': True, 'message': 'Done'})
        mock_agent_registry.get_or_create_agent.return_value = mock_agent
        
        result = orch.execute_task(task, agent_sequence)
        
        # Should work without memory
        assert result['success'] is True
        assert 'session_id' not in result


# =============================================================================
# Engine Tests
# =============================================================================

class TestEngine:
    """Tests for Engine class."""
    
    def test_initialization_with_config(self, mock_config):
        """Test Engine initialization with provided config."""
        with patch('core.engine.setup_logging'):
            engine = Engine(config=mock_config)
        
        assert engine.config == mock_config
        assert engine.router is None
        assert engine.agent_registry is None
        assert engine.tool_registry is None
        assert engine._initialized is False
    
    def test_initialization_without_config(self):
        """Test Engine initialization without config loads default."""
        with patch('core.engine.AppConfig.load') as mock_load:
            with patch('core.engine.setup_logging'):
                mock_load.return_value = Mock(spec=AppConfig)
                engine = Engine()
            
            mock_load.assert_called_once()
            assert engine.config is not None
    
    @patch('core.engine.AGENTS_AVAILABLE', True)
    @patch('core.engine.TOOLS_AVAILABLE', True)
    @patch('core.engine.WORKFLOWS_AVAILABLE', False)
    @patch('core.engine.AgentRegistry')
    @patch('core.engine.ToolRegistry')
    @patch('core.engine.LLMRouter')
    @patch('core.engine.MemoryManager')
    @patch('core.engine.TaskAnalyzer')
    @patch('core.engine.Orchestrator')
    def test_initialize_success(self, mock_orch_class, mock_ta_class, mock_mem_class,
                               mock_router_class, mock_tool_reg_class, 
                               mock_agent_reg_class, mock_config):
        """Test successful engine initialization."""
        # Setup mocks
        mock_router = Mock()
        mock_router.get_available_providers.return_value = ['ollama']
        mock_router_class.return_value = mock_router
        
        mock_agent_reg = Mock()
        mock_agent_reg.__len__ = Mock(return_value=3)
        mock_agent_reg_class.return_value = mock_agent_reg
        
        mock_tool_reg = Mock()
        mock_tool_reg.__len__ = Mock(return_value=2)
        mock_tool_reg_class.return_value = mock_tool_reg
        
        with patch('core.engine.setup_logging'):
            engine = Engine(config=mock_config)
            engine.initialize()
        
        assert engine._initialized is True
        assert engine.router is not None
        assert engine.agent_registry is not None
        assert engine.tool_registry is not None
        assert engine.task_analyzer is not None
        assert engine.orchestrator is not None
    
    def test_initialize_no_providers_raises_error(self, mock_config):
        """Test that initialization fails with no available providers."""
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = []
            mock_router_class.return_value = mock_router
            
            with patch('core.engine.setup_logging'):
                engine = Engine(config=mock_config)
            
            with pytest.raises(EngineError) as exc_info:
                engine.initialize()
            
            assert "No LLM providers are available" in str(exc_info.value)
    
    def test_process_query_not_initialized_raises_error(self, mock_config):
        """Test that process_query raises error if not initialized."""
        with patch('core.engine.setup_logging'):
            engine = Engine(config=mock_config)
        
        with pytest.raises(EngineError) as exc_info:
            engine.process_query("test query")
        
        assert "not initialized" in str(exc_info.value)
    
    def test_process_query_success(self, mock_config, mock_llm_router):
        """Test successful query processing."""
        with patch('core.engine.setup_logging'):
            engine = Engine(config=mock_config)
            engine._initialized = True
            engine.router = mock_llm_router
        
        mock_llm_router.query.return_value = {
            'response': 'Test response',
            'provider': 'ollama',
            'model': 'test-model'
        }
        
        result = engine.process_query("test query")
        
        assert result['success'] is True
        assert result['response'] == 'Test response'
        assert result['provider'] == 'ollama'
        assert result['model'] == 'test-model'
        assert result['error'] is None
        
        mock_llm_router.query.assert_called_once()
    
    def test_process_query_with_provider_override(self, mock_config, mock_llm_router):
        """Test query processing with provider override."""
        with patch('core.engine.setup_logging'):
            engine = Engine(config=mock_config)
            engine._initialized = True
            engine.router = mock_llm_router
        
        engine.process_query("test query", provider="openai", model="gpt-4")
        
        call_args = mock_llm_router.query.call_args
        assert call_args.kwargs['provider'] == "openai"
        assert call_args.kwargs['model'] == "gpt-4"
    
    def test_process_query_handles_llm_error(self, mock_config, mock_llm_router):
        """Test that process_query handles LLM errors gracefully."""
        from core.llm_router import LLMProviderError
        
        with patch('core.engine.setup_logging'):
            engine = Engine(config=mock_config)
            engine._initialized = True
            engine.router = mock_llm_router
        
        mock_llm_router.query.side_effect = LLMProviderError("Test error")
        
        result = engine.process_query("test query")
        
        assert result['success'] is False
        assert result['error'] == "Test error"
        assert result['response'] is None
    
    def test_execute_task_not_initialized_raises_error(self, mock_config):
        """Test that execute_task raises error if not initialized."""
        with patch('core.engine.setup_logging'):
            engine = Engine(config=mock_config)
        
        with pytest.raises(EngineError) as exc_info:
            engine.execute_task("test task")
        
        assert "not initialized" in str(exc_info.value)
    
    def test_execute_task_no_orchestrator_raises_error(self, mock_config):
        """Test that execute_task raises error if orchestrator not available."""
        with patch('core.engine.setup_logging'):
            engine = Engine(config=mock_config)
            engine._initialized = True
            engine.orchestrator = None
        
        with pytest.raises(EngineError) as exc_info:
            engine.execute_task("test task")
        
        assert "Orchestrator not available" in str(exc_info.value)
    
    def test_execute_task_with_agent_override(self, mock_config):
        """Test execute_task with agent override skips analysis."""
        with patch('core.engine.setup_logging'):
            engine = Engine(config=mock_config)
            engine._initialized = True
            
            mock_orchestrator = Mock()
            mock_orchestrator.execute_task.return_value = {
                'success': True,
                'results': [],
                'final_result': None
            }
            engine.orchestrator = mock_orchestrator
            
            mock_task_analyzer = Mock()
            engine.task_analyzer = mock_task_analyzer
        
        result = engine.execute_task("test task", agent_override=['code_planner'])
        
        # Task analyzer should not be called
        mock_task_analyzer.analyze_task.assert_not_called()
        
        # Orchestrator should be called with override
        mock_orchestrator.execute_task.assert_called_once()
        call_args = mock_orchestrator.execute_task.call_args
        assert call_args.kwargs['agent_sequence'] == ['code_planner']
    
    def test_execute_task_with_analysis(self, mock_config):
        """Test execute_task performs task analysis."""
        with patch('core.engine.setup_logging'):
            engine = Engine(config=mock_config)
            engine._initialized = True
            
            mock_agent_registry = Mock()
            mock_agent_registry.list_agents.return_value = ['code_planner', 'code_editor']
            engine.agent_registry = mock_agent_registry
            
            mock_task_analyzer = Mock()
            mock_task_analyzer.analyze_task.return_value = {
                'agents': ['code_planner'],
                'reasoning': 'Test reasoning',
                'parallel': False
            }
            engine.task_analyzer = mock_task_analyzer
            
            mock_orchestrator = Mock()
            mock_orchestrator.execute_task.return_value = {
                'success': True,
                'results': [],
                'final_result': None
            }
            engine.orchestrator = mock_orchestrator
        
        result = engine.execute_task("create a project")
        
        # Task analyzer should be called
        mock_task_analyzer.analyze_task.assert_called_once()
        
        # Result should include analysis
        assert 'analysis' in result
        assert result['analysis']['agents'] == ['code_planner']
    
    def test_execute_task_handles_exceptions(self, mock_config):
        """Test that execute_task handles exceptions gracefully."""
        with patch('core.engine.setup_logging'):
            engine = Engine(config=mock_config)
            engine._initialized = True
            
            mock_orchestrator = Mock()
            mock_orchestrator.execute_task.side_effect = Exception("Test error")
            engine.orchestrator = mock_orchestrator
            
            mock_agent_registry = Mock()
            mock_agent_registry.list_agents.return_value = []
            engine.agent_registry = mock_agent_registry
            
            mock_task_analyzer = Mock()
            mock_task_analyzer.analyze_task.return_value = {
                'agents': [],
                'reasoning': 'Test',
                'parallel': False
            }
            engine.task_analyzer = mock_task_analyzer
        
        result = engine.execute_task("test task")
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Test error' in result['message']
    
    def test_get_status_not_initialized(self, mock_config):
        """Test get_status returns correct info when not initialized."""
        with patch('core.engine.setup_logging'):
            engine = Engine(config=mock_config)
        
        status = engine.get_status()
        
        assert status['initialized'] is False
        assert status['config_loaded'] is True
        assert status['available_providers'] == []
        assert status['registered_agents'] == []
        assert status['registered_tools'] == []
    
    def test_get_status_initialized(self, mock_config, mock_llm_router, 
                                   mock_agent_registry, mock_tool_registry):
        """Test get_status returns correct info when initialized."""
        with patch('core.engine.setup_logging'):
            engine = Engine(config=mock_config)
            engine._initialized = True
            engine.router = mock_llm_router
            engine.agent_registry = mock_agent_registry
            engine.tool_registry = mock_tool_registry
        
        status = engine.get_status()
        
        assert status['initialized'] is True
        assert 'ollama' in status['available_providers']
        assert len(status['registered_agents']) > 0
        assert len(status['registered_tools']) > 0
    
    def test_shutdown(self, mock_config):
        """Test engine shutdown."""
        with patch('core.engine.setup_logging'):
            engine = Engine(config=mock_config)
            engine._initialized = True
            engine.router = Mock()
        
        engine.shutdown()
        
        assert engine._initialized is False
        assert engine.router is None


# =============================================================================
# Rich UI Helper Functions Tests
# =============================================================================

class TestRichUIHelpers:
    """Tests for Rich UI helper functions."""
    
    def test_print_engine_status_success(self):
        """Test printing success status."""
        with patch('core.engine._console.print') as mock_print:
            _print_engine_status("Test message", "success")
            mock_print.assert_called_once()
            call_args = str(mock_print.call_args)
            assert "Test message" in call_args
    
    def test_print_engine_status_error(self):
        """Test printing error status."""
        with patch('core.engine._console.print') as mock_print:
            _print_engine_status("Error message", "error")
            mock_print.assert_called_once()
            call_args = str(mock_print.call_args)
            assert "Error message" in call_args
    
    def test_print_engine_status_warning(self):
        """Test printing warning status."""
        with patch('core.engine._console.print') as mock_print:
            _print_engine_status("Warning message", "warning")
            mock_print.assert_called_once()
            call_args = str(mock_print.call_args)
            assert "Warning message" in call_args
    
    def test_print_engine_status_info(self):
        """Test printing info status."""
        with patch('core.engine._console.print') as mock_print:
            _print_engine_status("Info message", "info")
            mock_print.assert_called_once()
            call_args = str(mock_print.call_args)
            assert "Info message" in call_args
    
    def test_create_task_summary_panel(self):
        """Test creating task summary panel."""
        task = "Test task"
        analysis = {
            'agents': ['code_planner', 'code_editor'],
            'reasoning': 'Need both planning and editing'
        }
        
        panel = _create_task_summary_panel(task, analysis)
        
        from rich.panel import Panel
        assert isinstance(panel, Panel)
    
    def test_create_orchestration_table(self):
        """Test creating orchestration results table."""
        results = [
            {
                'agent': 'code_planner',
                'result': {
                    'success': True,
                    'message': 'Planning complete'
                }
            },
            {
                'agent': 'code_editor',
                'result': {
                    'success': False,
                    'message': 'Edit failed'
                }
            }
        ]
        
        table = _create_orchestration_table(results)
        
        from rich.table import Table
        assert isinstance(table, Table)
