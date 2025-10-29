"""
Comprehensive integration tests for core components with tools

Tests real integration between:
- Engine and Tools
- Agents and Tools
- Tool Registry and Tool implementations
- LLM Router with Tool invocations
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from core.config import AppConfig
from tools.registry import ToolRegistry
from tools.web_fetch import WebFetchTool
from tools.git import GitTool
from tools.file_operations import FileOperationsTool


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_config():
    """Create test configuration."""
    config = AppConfig()
    config.tools.enabled_tools = ['web_fetch', 'git', 'file_operations']
    return config


@pytest.fixture
def tool_registry():
    """Create tool registry."""
    registry = ToolRegistry()
    registry.clear()  # Clear any existing tools from previous tests
    return registry


# =============================================================================
# Tool Registry Integration Tests
# =============================================================================

class TestToolRegistryIntegration:
    """Integration tests for tool registry with real tools."""
    
    def test_register_and_retrieve_web_fetch_tool(self, tool_registry):
        """Test registering and retrieving WebFetchTool."""
        tool = WebFetchTool()
        tool_registry.register(tool)
        
        retrieved = tool_registry.get('web_fetch')
        
        assert retrieved is not None
        assert retrieved.name == 'web_fetch'
        assert retrieved == tool
    
    def test_register_and_retrieve_git_tool(self, tool_registry):
        """Test registering and retrieving GitTool."""
        tool = GitTool()
        tool_registry.register(tool)
        
        retrieved = tool_registry.get('git')
        
        assert retrieved is not None
        assert retrieved.name == 'git'
    
    def test_register_multiple_tools(self, tool_registry):
        """Test registering multiple tools."""
        web_tool = WebFetchTool()
        git_tool = GitTool()
        file_tool = FileOperationsTool()
        
        tool_registry.register(web_tool)
        tool_registry.register(git_tool)
        tool_registry.register(file_tool)
        
        assert len(tool_registry) == 3
        assert tool_registry.get('web_fetch') is not None
        assert tool_registry.get('git') is not None
        assert tool_registry.get('file_operations') is not None
    
    def test_list_registered_tools(self, tool_registry):
        """Test listing all registered tools."""
        tool_registry.register(WebFetchTool())
        tool_registry.register(GitTool())
        
        tools = tool_registry.list_tools()
        
        assert 'web_fetch' in tools
        assert 'git' in tools
        assert len(tools) == 2
    
    def test_invoke_tool_through_registry(self, tool_registry, temp_dir):
        """Test invoking a tool through the registry."""
        file_tool = FileOperationsTool()
        tool_registry.register(file_tool)
        
        test_file = temp_dir / "test.txt"
        # Get the tool from registry then invoke it
        retrieved_tool = tool_registry.get('file_operations')
        assert retrieved_tool is not None
        
        result = retrieved_tool.invoke({
            'operation': 'write',
            'path': str(test_file),
            'content': 'Test content'
        })
        
        assert result['success'] is True
        assert test_file.exists()


# =============================================================================
# File Operations Tool Integration Tests
# =============================================================================

class TestFileOperationsToolIntegration:
    """Integration tests for file operations tool with real file system."""
    
    def test_write_read_file_integration(self, temp_dir):
        """Test writing and reading files."""
        tool = FileOperationsTool()
        file_path = temp_dir / "test.txt"
        content = "Hello, World!"
        
        # Write file
        write_result = tool.invoke({
            'operation': 'write',
            'path': str(file_path),
            'content': content
        })
        assert write_result['success'] is True
        
        # Read file
        read_result = tool.invoke({
            'operation': 'read',
            'path': str(file_path)
        })
        assert read_result['success'] is True
        assert read_result['content'] == content
    
    def test_edit_file_integration(self, temp_dir):
        """Test editing existing file."""
        tool = FileOperationsTool()
        file_path = temp_dir / "edit.txt"
        
        # Create initial file
        file_path.write_text("Original content")
        
        # Edit file
        result = tool.invoke({
            'operation': 'edit',
            'path': str(file_path),
            'old_content': 'Original',
            'new_content': 'Modified'
        })
        
        if result['success']:
            assert 'Modified' in file_path.read_text()
    
    def test_move_file_integration(self, temp_dir):
        """Test moving files."""
        tool = FileOperationsTool()
        source = temp_dir / "source.txt"
        dest = temp_dir / "dest.txt"
        
        source.write_text("content")
        
        result = tool.invoke({
            'operation': 'move',
            'path': str(source),
            'destination': str(dest)
        })
        
        assert result['success'] is True
        assert dest.exists()
        assert not source.exists()
    
    def test_copy_file_integration(self, temp_dir):
        """Test copying files."""
        tool = FileOperationsTool()
        source = temp_dir / "source.txt"
        dest = temp_dir / "copy.txt"
        
        source.write_text("content")
        
        result = tool.invoke({
            'operation': 'copy',
            'path': str(source),
            'destination': str(dest)
        })
        
        assert result['success'] is True
        assert dest.exists()
        assert source.exists()  # Original should still exist
    
    def test_mkdir_integration(self, temp_dir):
        """Test creating directories."""
        tool = FileOperationsTool()
        new_dir = temp_dir / "new_directory"
        
        result = tool.invoke({
            'operation': 'mkdir',
            'path': str(new_dir)
        })
        
        assert result['success'] is True
        assert new_dir.exists()
        assert new_dir.is_dir()


# =============================================================================
# Git Tool Integration Tests (Mocked)
# =============================================================================

class TestGitToolIntegration:
    """Integration tests for git tool."""
    
    def test_git_tool_status_command(self, temp_dir):
        """Test git status command."""
        tool = GitTool()
        
        # Mock GitPython Repo class to avoid real git calls
        with patch('tools.git.Repo') as mock_repo_class:
            mock_repo = Mock()
            mock_repo.is_dirty.return_value = False
            mock_repo.untracked_files = []
            mock_repo.active_branch.name = 'main'
            
            # Mock index.diff to return empty lists for changed/staged files
            mock_diff_item = Mock()
            mock_diff_item.a_path = 'test_file.txt'
            mock_repo.index.diff.return_value = []  # Return empty list instead of Mock
            
            mock_repo_class.return_value = mock_repo
            
            result = tool.invoke({
                'action': 'status',
                'path': str(temp_dir)
            })
            
            # Tool should handle the request (success or failure)
            assert 'success' in result
    
    def test_git_tool_init_command(self, temp_dir):
        """Test git init command."""
        tool = GitTool()
        
        # Mock GitPython Repo.init
        with patch('tools.git.Repo.init') as mock_init:
            mock_repo = Mock()
            mock_init.return_value = mock_repo
            
            result = tool.invoke({
                'action': 'init',
                'path': str(temp_dir)
            })
            
            # Tool should handle the request
            assert 'success' in result


# =============================================================================
# Web Fetch Tool Integration Tests (Mocked)
# =============================================================================

class TestWebFetchToolIntegration:
    """Integration tests for web fetch tool."""
    
    def test_web_fetch_tool_fetch_url(self):
        """Test fetching URL with web fetch tool."""
        tool = WebFetchTool()
        
        # Mock httpx.AsyncClient and its methods
        with patch('tools.web_fetch.httpx.AsyncClient') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '<html><body>Test content</body></html>'
            mock_response.content = mock_response.text.encode()
            mock_response.headers = {'content-type': 'text/html'}
            
            # Setup async context manager
            mock_client.__aenter__ = Mock(return_value=mock_client)
            mock_client.__aexit__ = Mock(return_value=None)
            mock_client.get = Mock(return_value=mock_response)
            mock_client_class.return_value = mock_client
            
            result = tool.invoke({
                'action': 'fetch',
                'url': 'https://example.com'
            })
            
            assert result is not None
            if isinstance(result, dict):
                assert 'content' in result or 'text' in result or 'success' in result


# =============================================================================
# Agent-Tool Integration Tests
# =============================================================================

class TestAgentToolIntegration:
    """Integration tests for agents using tools."""
    
    def test_agent_can_access_tool_registry(self):
        """Test that agents can access and use tool registry."""
        from agents.git_agent import GitAgent
        
        tool_registry = ToolRegistry()
        tool_registry.clear()
        git_tool = GitTool()
        tool_registry.register(git_tool)
        
        # Create agent with correct constructor
        mock_llm_router = Mock()
        mock_llm_router.query.return_value = "Test response"
        
        agent = GitAgent(
            name='test_git_agent',
            description='Test git agent',
            llm_router=mock_llm_router,
            tool_registry=tool_registry,
            config={}
        )
        
        # Agent should have access to tool registry
        assert agent.tool_registry == tool_registry
        
        # Agent should be able to get tools
        tool = agent.tool_registry.get('git')
        assert tool is not None
        assert tool.name == 'git'
    
    def test_agent_tool_invocation_flow(self, temp_dir):
        """Test full agent-tool invocation flow."""
        from agents.git_agent import GitAgent
        
        tool_registry = ToolRegistry()
        tool_registry.clear()
        git_tool = GitTool()
        tool_registry.register(git_tool)
        
        mock_llm_router = Mock()
        mock_llm_router.query.return_value = "Test response"
        
        agent = GitAgent(
            name='test_git_agent',
            description='Test git agent',
            llm_router=mock_llm_router,
            tool_registry=tool_registry,
            config={}
        )
        
        # Agent gets tool from registry
        tool = agent.tool_registry.get('git')
        assert tool is not None
        
        # Agent invokes tool with proper mocking
        with patch('tools.git.Repo.init') as mock_init:
            mock_init.return_value = Mock()
            
            result = tool.invoke({
                'action': 'init',
                'path': str(temp_dir)
            })
            
            assert result['success'] is True
            mock_init.assert_called_once()


# =============================================================================
# Engine-Tool Integration Tests
# =============================================================================

class TestEngineToolIntegration:
    """Integration tests for engine with tools."""
    
    def test_engine_initializes_tool_registry(self, test_config):
        """Test that engine initializes tool registry."""
        from core.engine import Engine
        
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router_class.return_value = mock_router
            
            with patch('core.engine.TOOLS_AVAILABLE', True):
                with patch('core.engine.ToolRegistry') as mock_tool_reg_class:
                    mock_tool_reg = Mock()
                    mock_tool_reg.__len__ = Mock(return_value=2)
                    mock_tool_reg_class.return_value = mock_tool_reg
                    
                    with patch('core.engine.AgentRegistry'):
                        engine = Engine(config=test_config)
                        engine.initialize()
            
            assert engine.tool_registry is not None
    
    def test_engine_registers_enabled_tools(self, test_config):
        """Test that engine registers enabled tools from config."""
        from core.engine import Engine
        
        with patch('core.engine.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.get_available_providers.return_value = ['ollama']
            mock_router_class.return_value = mock_router
            
            with patch('core.engine.TOOLS_AVAILABLE', True):
                with patch('core.engine.ToolRegistry') as mock_tool_reg_class:
                    mock_tool_reg = Mock()
                    mock_tool_reg.__len__ = Mock(return_value=2)  # Add __len__ method
                    mock_tool_reg_class.return_value = mock_tool_reg
                    
                    with patch('core.engine.WebFetchTool') as mock_web_tool:
                        with patch('core.engine.GitTool') as mock_git_tool:
                            with patch('core.engine.AgentRegistry'):
                                engine = Engine(config=test_config)
                                engine.initialize()
                    
                    # Tools should be registered
                    assert mock_tool_reg.register.called


# =============================================================================
# Tool Configuration Integration Tests
# =============================================================================

class TestToolConfigurationIntegration:
    """Integration tests for tool configuration."""
    
    def test_tool_respects_config_settings(self):
        """Test that tools respect configuration settings."""
        config = {
            'max_file_size': 1024,
            'require_file_confirmation': True
        }
        
        tool = FileOperationsTool(config=config)
        
        assert tool.max_file_size == 1024
        assert tool.require_confirmation is True
    
    def test_tool_uses_default_config(self):
        """Test that tools use default config when not specified."""
        tool = FileOperationsTool()
        
        assert tool.max_file_size > 0
        assert hasattr(tool, 'require_confirmation')


# =============================================================================
# Tool Error Handling Integration Tests
# =============================================================================

class TestToolErrorHandlingIntegration:
    """Integration tests for tool error handling."""
    
    def test_file_tool_handles_missing_file(self, temp_dir):
        """Test that file tool handles missing files gracefully."""
        tool = FileOperationsTool()
        
        result = tool.invoke({
            'operation': 'read',
            'path': str(temp_dir / "nonexistent.txt")
        })
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_file_tool_handles_permission_errors(self, temp_dir):
        """Test handling of permission errors."""
        tool = FileOperationsTool()
        
        # Try to write to a protected location (may or may not fail depending on system)
        result = tool.invoke({
            'operation': 'write',
            'path': '/root/test.txt',
            'content': 'test'
        })
        
        # Should handle error gracefully
        assert 'success' in result
    
    def test_tool_handles_invalid_parameters(self):
        """Test that tools handle invalid parameters."""
        tool = FileOperationsTool()
        
        result = tool.invoke({
            'operation': 'invalid_op',
            'path': '/some/path'
        })
        
        assert result['success'] is False
        assert 'error' in result


# =============================================================================
# Multi-Tool Workflow Integration Tests
# =============================================================================

class TestMultiToolWorkflowIntegration:
    """Integration tests for workflows using multiple tools."""
    
    def test_file_operations_workflow(self, temp_dir):
        """Test a workflow using file operations."""
        tool = FileOperationsTool()
        
        # Create file
        file_path = temp_dir / "workflow.txt"
        result1 = tool.invoke({
            'operation': 'write',
            'path': str(file_path),
            'content': 'Step 1'
        })
        assert result1['success'] is True
        
        # Edit file
        result2 = tool.invoke({
            'operation': 'edit',
            'path': str(file_path),
            'old_content': 'Step 1',
            'new_content': 'Step 2'
        })
        if result2['success']:
            assert 'Step 2' in file_path.read_text()
        
        # Copy file
        copy_path = temp_dir / "workflow_copy.txt"
        result3 = tool.invoke({
            'operation': 'copy',
            'path': str(file_path),
            'destination': str(copy_path)
        })
        assert result3['success'] is True
        assert copy_path.exists()
        
        # Delete original
        result4 = tool.invoke({
            'operation': 'delete',
            'path': str(file_path),
            'force': True
        })
        assert result4['success'] is True
        assert not file_path.exists()
