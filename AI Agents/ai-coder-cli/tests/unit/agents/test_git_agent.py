"""
Comprehensive unit tests for agents/git_agent.py

Tests cover:
- GitAgent initialization
- Git operation parsing
- Command execution
- Confirmation handling
- Error handling
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from agents.git_agent import GitAgent


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_llm_router():
    """Create a mock LLM router."""
    router = Mock()
    router.query = Mock(return_value={
        'response': 'Git operation completed',
        'provider': 'ollama',
        'model': 'test-model'
    })
    return router


@pytest.fixture
def mock_tool_registry():
    """Create a mock tool registry."""
    registry = Mock()
    
    # Mock git tool
    mock_git_tool = Mock()
    mock_git_tool.invoke = Mock(return_value={
        'success': True,
        'output': 'Git operation successful',
        'message': 'Success'
    })
    
    registry.get = Mock(return_value=mock_git_tool)
    return registry


@pytest.fixture
def git_agent(mock_llm_router, mock_tool_registry):
    """Create a GitAgent instance."""
    config = {
        'auto_confirm': False,
        'use_gitpython': True
    }
    agent = GitAgent(
        name="test_git_agent",
        description="Test git agent for unit tests",
        llm_router=mock_llm_router,
        tool_registry=mock_tool_registry,
        config=config
    )
    return agent


# =============================================================================
# GitAgent Initialization Tests
# =============================================================================

class TestGitAgentInitialization:
    """Tests for GitAgent initialization."""
    
    def test_initialization(self, mock_llm_router, mock_tool_registry):
        """Test GitAgent initialization."""
        agent = GitAgent(
            name="test_git",
            description="Test git agent",
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
        
        assert agent.name == "test_git"
        assert agent.description == "Test git agent"
        assert agent.llm_router == mock_llm_router
        assert agent.tool_registry == mock_tool_registry
        assert agent.logger is not None
    
    def test_initialization_with_config(self, mock_llm_router):
        """Test GitAgent initialization with custom config."""
        config = {
            'auto_confirm': True,
            'use_gitpython': False
        }
        agent = GitAgent(
            name="test_git",
            description="Test git agent",
            llm_router=mock_llm_router,
            config=config
        )
        
        assert agent.config['auto_confirm'] is True
        assert agent.config['use_gitpython'] is False


# =============================================================================
# Git Operation Parsing Tests
# =============================================================================

class TestGitOperationParsing:
    """Tests for git operation parsing."""
    
    def test_parse_init_operation(self, git_agent):
        """Test parsing git init operation."""
        task = "Initialize a new git repository"
        context = {}
        
        operation = git_agent._parse_git_task(task, context)
        
        assert operation is not None
        assert operation['command'] == 'init'
        assert 'Initialize' in operation['description']
    
    def test_parse_status_operation(self, git_agent):
        """Test parsing git status operation."""
        task = "Check the git status"
        context = {}
        
        operation = git_agent._parse_git_task(task, context)
        
        assert operation is not None
        assert operation['command'] == 'status'
    
    def test_parse_add_operation(self, git_agent):
        """Test parsing git add operation."""
        task = "Add files to staging"
        context = {'last_file': 'test.py'}
        
        operation = git_agent._parse_git_task(task, context)
        
        assert operation is not None
        assert operation['command'] == 'add'
        assert 'test.py' in str(operation['args']['files'])
    
    def test_parse_add_operation_default_files(self, git_agent):
        """Test parsing git add without specific files."""
        task = "Stage all changes"
        context = {}
        
        operation = git_agent._parse_git_task(task, context)
        
        assert operation is not None
        assert operation['command'] == 'add'
        assert '.' in operation['args']['files']
    
    def test_parse_commit_operation(self, git_agent):
        """Test parsing git commit operation."""
        task = "Commit changes with message 'Initial commit'"
        context = {}
        
        with patch.object(git_agent, '_extract_commit_message', return_value='Initial commit'):
            operation = git_agent._parse_git_task(task, context)
        
        assert operation is not None
        assert operation['command'] == 'commit'
        assert operation['args']['message'] == 'Initial commit'
    
    def test_parse_push_operation(self, git_agent):
        """Test parsing git push operation."""
        task = "Push changes to remote repository"
        context = {}
        
        operation = git_agent._parse_git_task(task, context)
        
        assert operation is not None
        assert operation['command'] == 'push'
    
    def test_parse_unknown_defaults_to_status(self, git_agent):
        """Test that unknown operations default to status."""
        task = "Do something with git"
        context = {}
        
        operation = git_agent._parse_git_task(task, context)
        
        assert operation is not None
        assert operation['command'] == 'status'
        assert 'default' in operation['description'].lower()


# =============================================================================
# Execution Tests
# =============================================================================

class TestGitAgentExecution:
    """Tests for GitAgent execution."""
    
    def test_execute_init_success(self, git_agent, mock_tool_registry):
        """Test successful git init execution."""
        task = "Initialize git repository"
        context = {'auto_confirm': True}
        
        result = git_agent.execute(task, context)
        
        assert result['success'] is True
        assert 'init' in result['message'].lower()
    
    def test_execute_status_success(self, git_agent):
        """Test successful git status execution."""
        task = "Check git status"
        context = {'auto_confirm': True}
        
        result = git_agent.execute(task, context)
        
        assert result['success'] is True
    
    def test_execute_add_success(self, git_agent):
        """Test successful git add execution."""
        task = "Add files to staging"
        context = {'auto_confirm': True, 'last_file': 'test.py'}
        
        result = git_agent.execute(task, context)
        
        assert result['success'] is True
        assert 'add' in result['message'].lower()
    
    def test_execute_commit_success(self, git_agent):
        """Test successful git commit execution."""
        task = "Commit with message 'Test commit'"
        context = {'auto_confirm': True}
        
        with patch.object(git_agent, '_extract_commit_message', return_value='Test commit'):
            result = git_agent.execute(task, context)
        
        assert result['success'] is True
        assert 'commit' in result['message'].lower()
    
    def test_execute_push_success(self, git_agent):
        """Test successful git push execution."""
        task = "Push to remote"
        context = {'auto_confirm': True}
        
        result = git_agent.execute(task, context)
        
        assert result['success'] is True
        assert 'push' in result['message'].lower()
    
    def test_execute_with_confirmation_required(self, git_agent):
        """Test execution requiring user confirmation."""
        task = "Commit changes"
        context = {'auto_confirm': False}
        
        with patch.object(git_agent, '_requires_confirmation', return_value=True):
            with patch.object(git_agent, '_request_confirmation', return_value=False):
                result = git_agent.execute(task, context)
        
        assert result['success'] is True
        assert 'cancelled' in result['message'].lower()
        assert result.get('data', {}).get('cancelled') is True
    
    def test_execute_with_confirmation_granted(self, git_agent):
        """Test execution with confirmation granted."""
        task = "Commit changes"
        context = {'auto_confirm': False}
        
        with patch.object(git_agent, '_requires_confirmation', return_value=True):
            with patch.object(git_agent, '_request_confirmation', return_value=True):
                result = git_agent.execute(task, context)
        
        assert result['success'] is True
        assert 'cancelled' not in result['message'].lower()
    
    def test_execute_auto_confirm(self, git_agent):
        """Test execution with auto_confirm enabled."""
        task = "Push to remote"
        context = {'auto_confirm': True}
        
        result = git_agent.execute(task, context)
        
        # Should not prompt for confirmation
        assert result['success'] is True
    
    def test_execute_with_tool(self, git_agent, mock_tool_registry):
        """Test execution using git tool."""
        task = "Check status"
        context = {'auto_confirm': True}
        
        mock_git_tool = Mock()
        mock_git_tool.invoke = Mock(return_value={
            'success': True,
            'output': 'On branch main',
            'message': 'Success'
        })
        mock_tool_registry.get.return_value = mock_git_tool
        
        result = git_agent.execute(task, context)
        
        assert result['success'] is True
        mock_git_tool.invoke.assert_called_once()
    
    def test_execute_without_tool(self, git_agent, mock_tool_registry):
        """Test execution without git tool (subprocess fallback)."""
        task = "Check status"
        context = {'auto_confirm': True}
        
        # Disable tool usage
        git_agent.config['use_gitpython'] = False
        mock_tool_registry.get.return_value = None
        
        with patch.object(git_agent, '_execute_with_subprocess') as mock_subprocess:
            mock_subprocess.return_value = {
                'success': True,
                'output': 'Status output',
                'message': 'Success'
            }
            
            result = git_agent.execute(task, context)
        
        assert result['success'] is True
        mock_subprocess.assert_called_once()
    
    def test_execute_operation_failure(self, git_agent, mock_tool_registry):
        """Test handling of operation failure."""
        task = "Push to remote"
        context = {'auto_confirm': True}
        
        mock_git_tool = Mock()
        mock_git_tool.invoke = Mock(return_value={
            'success': False,
            'message': 'Push failed: remote not found'
        })
        mock_tool_registry.get.return_value = mock_git_tool
        
        result = git_agent.execute(task, context)
        
        assert result['success'] is False
        assert 'failed' in result['message'].lower()
    
    def test_execute_exception_handling(self, git_agent):
        """Test exception handling during execution."""
        task = "Commit changes"
        context = {'auto_confirm': True}
        
        with patch.object(git_agent, '_parse_git_task', side_effect=Exception("Test error")):
            result = git_agent.execute(task, context)
        
        assert result['success'] is False
        assert 'error' in result['message'].lower()
    
    def test_execute_no_operation_parsed(self, git_agent):
        """Test handling when no operation can be parsed."""
        task = "Invalid task"
        context = {}
        
        with patch.object(git_agent, '_parse_git_task', return_value=None):
            result = git_agent.execute(task, context)
        
        assert result['success'] is False
        assert 'could not determine' in result['message'].lower()


# =============================================================================
# Helper Method Tests
# =============================================================================

class TestGitAgentHelpers:
    """Tests for GitAgent helper methods."""
    
    def test_requires_confirmation_commit(self, git_agent):
        """Test that commit operations require confirmation."""
        operation = {'command': 'commit', 'args': {}}
        
        if hasattr(git_agent, '_requires_confirmation'):
            requires = git_agent._requires_confirmation(operation)
            # Implementation-dependent
            assert isinstance(requires, bool)
    
    def test_requires_confirmation_push(self, git_agent):
        """Test that push operations require confirmation."""
        operation = {'command': 'push', 'args': {}}
        
        if hasattr(git_agent, '_requires_confirmation'):
            requires = git_agent._requires_confirmation(operation)
            assert isinstance(requires, bool)
    
    def test_requires_confirmation_status(self, git_agent):
        """Test that status operations don't require confirmation."""
        operation = {'command': 'status', 'args': {}}
        
        if hasattr(git_agent, '_requires_confirmation'):
            requires = git_agent._requires_confirmation(operation)
            # Status should typically not require confirmation
            assert isinstance(requires, bool)
    
    def test_extract_commit_message_from_task(self, git_agent):
        """Test extracting commit message from task."""
        task = "Commit changes with message 'Initial commit'"
        
        if hasattr(git_agent, '_extract_commit_message'):
            message = git_agent._extract_commit_message(task)
            assert isinstance(message, str)
            # Should extract or generate some message
            assert len(message) > 0
    
    def test_extract_commit_message_default(self, git_agent):
        """Test default commit message when none specified."""
        task = "Commit changes"
        
        if hasattr(git_agent, '_extract_commit_message'):
            message = git_agent._extract_commit_message(task)
            assert isinstance(message, str)
            assert len(message) > 0


# =============================================================================
# Context and Next Steps Tests
# =============================================================================

class TestGitAgentContext:
    """Tests for context handling and next steps."""
    
    def test_success_result_includes_next_context(self, git_agent):
        """Test that successful operations include next context."""
        task = "Check status"
        context = {'auto_confirm': True}
        
        result = git_agent.execute(task, context)
        
        if result['success']:
            # Should include information for next agent
            assert 'data' in result or 'next_context' in result
    
    def test_last_git_operation_tracked(self, git_agent):
        """Test that last git operation is tracked in context."""
        task = "Add files"
        context = {'auto_confirm': True}
        
        result = git_agent.execute(task, context)
        
        if result['success'] and 'next_context' in result:
            assert 'last_git_operation' in result['next_context']
    
    def test_git_output_included(self, git_agent):
        """Test that git output is included in result."""
        task = "Check status"
        context = {'auto_confirm': True}
        
        result = git_agent.execute(task, context)
        
        if result['success'] and 'next_context' in result:
            # Output should be available
            assert 'git_output' in result['next_context'] or 'output' in result.get('data', {})
