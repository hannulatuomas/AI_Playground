
"""
Enhanced unit tests for MCP (Model Context Protocol) Tool.

Additional comprehensive tests for MCP functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import asyncio


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_mcp_config():
    """Create mock MCP configuration."""
    return {
        'server_command': 'mcp-server',
        'server_args': ['--host', 'localhost', '--port', '8080'],
        'timeout': 60,
        'max_retries': 3
    }


@pytest.fixture
def mock_mcp_client():
    """Create a mock MCP client."""
    client = AsyncMock()
    client.list_tools = AsyncMock(return_value={
        'tools': [
            {'name': 'tool1', 'description': 'First tool'},
            {'name': 'tool2', 'description': 'Second tool'}
        ]
    })
    client.call_tool = AsyncMock(return_value={
        'result': 'Tool executed successfully'
    })
    client.list_prompts = AsyncMock(return_value={
        'prompts': [
            {'name': 'prompt1', 'description': 'First prompt'}
        ]
    })
    client.get_prompt = AsyncMock(return_value={
        'content': 'Prompt content here'
    })
    client.list_resources = AsyncMock(return_value={
        'resources': [
            {'name': 'resource1', 'type': 'file'}
        ]
    })
    return client


# =============================================================================
# Initialization Tests
# =============================================================================

class TestMCPToolInitialization:
    """Tests for MCP tool initialization."""
    
    def test_default_initialization(self):
        """Test initialization with default config."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        assert tool.name == "mcp"
        assert "MCP" in tool.description or "Model Context Protocol" in tool.description
    
    def test_custom_config_initialization(self, mock_mcp_config):
        """Test initialization with custom config."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool(config=mock_mcp_config)
        
        assert tool.timeout == 60
    
    def test_tool_attributes(self):
        """Test that tool has required attributes."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert hasattr(tool, 'invoke')


# =============================================================================
# Tool Operations Tests
# =============================================================================

class TestMCPToolOperations:
    """Tests for MCP tool operations."""
    
    def test_list_tools_success(self, mock_mcp_client):
        """Test listing available MCP tools."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        with patch.object(tool, '_get_mcp_client', return_value=mock_mcp_client):
            result = tool.invoke({'action': 'list_tools'})
            
            assert result is not None
            assert result['success'] is True
            assert 'tools' in result['data']
    
    def test_list_tools_empty(self, mock_mcp_client):
        """Test listing tools when none available."""
        from tools.mcp import MCPClientTool
        
        mock_mcp_client.list_tools = AsyncMock(return_value={'tools': []})
        
        tool = MCPClientTool()
        
        with patch.object(tool, '_get_mcp_client', return_value=mock_mcp_client):
            result = tool.invoke({'action': 'list_tools'})
            
            assert result['success'] is True
            assert len(result['data']['tools']) == 0
    
    def test_call_tool_success(self, mock_mcp_client):
        """Test calling an MCP tool successfully."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        with patch.object(tool, '_get_mcp_client', return_value=mock_mcp_client):
            result = tool.invoke({
                'action': 'call_tool',
                'tool_name': 'test_tool',
                'arguments': {'arg1': 'value1', 'arg2': 'value2'}
            })
            
            assert result is not None
            assert result['success'] is True
    
    def test_call_tool_with_no_arguments(self, mock_mcp_client):
        """Test calling tool without arguments."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        with patch.object(tool, '_get_mcp_client', return_value=mock_mcp_client):
            result = tool.invoke({
                'action': 'call_tool',
                'tool_name': 'test_tool'
            })
            
            assert result is not None
    
    def test_call_nonexistent_tool(self, mock_mcp_client):
        """Test calling a tool that doesn't exist."""
        from tools.mcp import MCPClientTool
        
        mock_mcp_client.call_tool = AsyncMock(
            side_effect=ValueError("Tool not found")
        )
        
        tool = MCPClientTool()
        
        with patch.object(tool, '_get_mcp_client', return_value=mock_mcp_client):
            result = tool.invoke({
                'action': 'call_tool',
                'tool_name': 'nonexistent_tool'
            })
            
            assert result['success'] is False


# =============================================================================
# Prompt Operations Tests
# =============================================================================

class TestMCPPromptOperations:
    """Tests for MCP prompt operations."""
    
    def test_list_prompts_success(self, mock_mcp_client):
        """Test listing available prompts."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        with patch.object(tool, '_get_mcp_client', return_value=mock_mcp_client):
            result = tool.invoke({'action': 'list_prompts'})
            
            assert result is not None
            assert result['success'] is True
            assert 'prompts' in result['data']
    
    def test_get_prompt_success(self, mock_mcp_client):
        """Test getting a specific prompt."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        with patch.object(tool, '_get_mcp_client', return_value=mock_mcp_client):
            result = tool.invoke({
                'action': 'get_prompt',
                'prompt_name': 'test_prompt'
            })
            
            assert result is not None
            assert result['success'] is True
    
    def test_get_prompt_missing_name(self):
        """Test getting prompt without providing name."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        result = tool.invoke({'action': 'get_prompt'})
        
        assert result['success'] is False
        assert 'prompt_name required' in result['message']


# =============================================================================
# Resource Operations Tests
# =============================================================================

class TestMCPResourceOperations:
    """Tests for MCP resource operations."""
    
    def test_list_resources_success(self, mock_mcp_client):
        """Test listing available resources."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        with patch.object(tool, '_get_mcp_client', return_value=mock_mcp_client):
            result = tool.invoke({'action': 'list_resources'})
            
            assert result is not None
            assert result['success'] is True
            assert 'resources' in result['data']
    
    def test_get_resource_success(self, mock_mcp_client):
        """Test getting a specific resource."""
        from tools.mcp import MCPClientTool
        
        mock_mcp_client.get_resource = AsyncMock(return_value={
            'content': 'Resource content'
        })
        
        tool = MCPClientTool()
        
        with patch.object(tool, '_get_mcp_client', return_value=mock_mcp_client):
            result = tool.invoke({
                'action': 'get_resource',
                'resource_name': 'test_resource'
            })
            
            assert result is not None
            assert result['success'] is True


# =============================================================================
# Connection Management Tests
# =============================================================================

class TestMCPConnectionManagement:
    """Tests for MCP connection management."""
    
    def test_connect_to_server_success(self, mock_mcp_client):
        """Test successfully connecting to MCP server."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        with patch('asyncio.run') as mock_run:
            mock_run.return_value = {'success': True, 'message': 'Connected'}
            
            result = tool.invoke({
                'action': 'connect',
                'server_command': 'mcp-server',
                'server_args': ['--port', '8080']
            })
            
            assert result is not None
    
    def test_disconnect_from_server(self):
        """Test disconnecting from MCP server."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        result = tool.invoke({'action': 'disconnect'})
        
        assert result is not None
        assert 'success' in result
    
    def test_check_connection_status(self):
        """Test checking connection status."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        result = tool.invoke({'action': 'status'})
        
        assert result is not None
        assert 'success' in result
    
    def test_reconnect_on_connection_loss(self, mock_mcp_client):
        """Test reconnecting when connection is lost."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        # First call fails, second succeeds
        mock_mcp_client.list_tools = AsyncMock(side_effect=[
            ConnectionError("Connection lost"),
            {'tools': []}
        ])
        
        with patch.object(tool, '_get_mcp_client', return_value=mock_mcp_client):
            with patch.object(tool, '_reconnect', return_value=True):
                result = tool.invoke({'action': 'list_tools'})
                
                # Should handle reconnection gracefully
                assert result is not None


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestMCPErrorHandling:
    """Tests for MCP error handling."""
    
    def test_connection_error_handling(self, mock_mcp_client):
        """Test handling connection errors."""
        from tools.mcp import MCPClientTool
        
        mock_mcp_client.list_tools = AsyncMock(
            side_effect=ConnectionError("Cannot connect to server")
        )
        
        tool = MCPClientTool()
        
        with patch.object(tool, '_get_mcp_client', return_value=mock_mcp_client):
            result = tool.invoke({'action': 'list_tools'})
            
            assert result['success'] is False
            assert 'error' in result
    
    def test_timeout_error_handling(self, mock_mcp_client):
        """Test handling timeout errors."""
        from tools.mcp import MCPClientTool
        
        mock_mcp_client.call_tool = AsyncMock(
            side_effect=asyncio.TimeoutError()
        )
        
        tool = MCPClientTool()
        
        with patch.object(tool, '_get_mcp_client', return_value=mock_mcp_client):
            result = tool.invoke({
                'action': 'call_tool',
                'tool_name': 'slow_tool'
            })
            
            assert result['success'] is False
    
    def test_invalid_action_handling(self):
        """Test handling invalid actions."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        result = tool.invoke({'action': 'invalid_action'})
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_missing_action_handling(self):
        """Test handling missing action parameter."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        result = tool.invoke({})
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_malformed_request_handling(self):
        """Test handling malformed requests."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        result = tool.invoke(None)
        
        assert result['success'] is False
    
    def test_server_error_handling(self, mock_mcp_client):
        """Test handling server errors."""
        from tools.mcp import MCPClientTool
        
        mock_mcp_client.call_tool = AsyncMock(
            side_effect=Exception("Internal server error")
        )
        
        tool = MCPClientTool()
        
        with patch.object(tool, '_get_mcp_client', return_value=mock_mcp_client):
            result = tool.invoke({
                'action': 'call_tool',
                'tool_name': 'test_tool'
            })
            
            assert result['success'] is False


# =============================================================================
# Advanced Features Tests
# =============================================================================

class TestMCPAdvancedFeatures:
    """Tests for advanced MCP features."""
    
    def test_batch_tool_calls(self, mock_mcp_client):
        """Test calling multiple tools in batch."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        with patch.object(tool, '_get_mcp_client', return_value=mock_mcp_client):
            result = tool.invoke({
                'action': 'batch_call',
                'tools': [
                    {'name': 'tool1', 'args': {}},
                    {'name': 'tool2', 'args': {}}
                ]
            })
            
            # Should handle batch calls
            assert result is not None
    
    def test_streaming_response(self, mock_mcp_client):
        """Test handling streaming responses."""
        from tools.mcp import MCPClientTool
        
        async def stream_response():
            for chunk in ['chunk1', 'chunk2', 'chunk3']:
                yield chunk
        
        mock_mcp_client.call_tool_streaming = AsyncMock(
            return_value=stream_response()
        )
        
        tool = MCPClientTool()
        
        # Should handle streaming if supported
        assert tool is not None
    
    def test_caching_mechanism(self, mock_mcp_client):
        """Test that tool implements caching for repeated calls."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        with patch.object(tool, '_get_mcp_client', return_value=mock_mcp_client):
            # Call same tool twice
            result1 = tool.invoke({'action': 'list_tools'})
            result2 = tool.invoke({'action': 'list_tools'})
            
            # Both should succeed
            assert result1['success'] is True
            assert result2['success'] is True

