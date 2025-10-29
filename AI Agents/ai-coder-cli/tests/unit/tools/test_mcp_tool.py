"""
Unit tests for MCP (Model Context Protocol) tool.

Tests for MCP client functionality, transport operations, and tool invocations.
Validates:
- Tool initialization and configuration
- Connection management (stdio, SSE, HTTP transports)
- Tool discovery and invocation
- Error handling and retry logic
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import asyncio


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_config():
    """Create mock MCP configuration."""
    return {
        'max_retries': 3,
        'retry_delay': 1.0,
        'retry_backoff': 2.0
    }


@pytest.fixture
def mcp_tool(mock_config):
    """Create MCP tool instance for testing."""
    from tools.mcp import MCPClientTool
    return MCPClientTool(config=mock_config)


# =============================================================================
# MCPClientTool Initialization Tests
# =============================================================================

class TestMCPClientToolInitialization:
    """Tests for MCPClientTool initialization."""
    
    def test_initialization(self):
        """Test MCP tool initialization with defaults."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool()
        
        assert tool.name == "mcp"
        assert "Model Context Protocol" in tool.description or "MCP" in tool.description
        assert hasattr(tool, 'invoke')
        assert hasattr(tool, 'connections')
        assert hasattr(tool, 'discovered_tools')
        assert tool.connections == {}
        assert tool.discovered_tools == {}
    
    def test_initialization_with_config(self, mock_config):
        """Test initialization with custom config."""
        from tools.mcp import MCPClientTool
        
        tool = MCPClientTool(config=mock_config)
        
        assert tool.name == "mcp"
        assert tool.max_retries == 3
        assert tool.retry_delay == 1.0
        assert tool.retry_backoff == 2.0


# =============================================================================
# MCPClientTool Operation Tests
# =============================================================================

class TestMCPClientToolOperations:
    """Tests for MCP tool operations."""
    
    def test_invoke_connect_stdio(self, mcp_tool):
        """Test connecting to MCP server via stdio."""
        with patch.object(mcp_tool, '_connect_stdio') as mock_connect:
            mock_connect.return_value = {'process': Mock(), 'status': 'connected'}
            
            result = mcp_tool.invoke({
                'action': 'connect',
                'server_id': 'test-server',
                'transport': 'stdio',
                'endpoint': 'test-mcp-server'
            })
            
            assert result is not None
            assert result['success'] is True
            assert result['server_id'] == 'test-server'
            assert 'test-server' in mcp_tool.connections
    
    def test_invoke_discover_tools(self, mcp_tool):
        """Test discovering tools from connected server."""
        # First connect
        mcp_tool.connections['test-server'] = {
            'transport': Mock(),
            'connection': {'status': 'connected'},
            'endpoint': 'test-endpoint'
        }
        
        with patch.object(mcp_tool, '_discover_stdio') as mock_discover:
            mock_discover.return_value = [
                {'name': 'tool1', 'description': 'Tool 1'},
                {'name': 'tool2', 'description': 'Tool 2'}
            ]
            
            result = mcp_tool.invoke({
                'action': 'discover',
                'server_id': 'test-server'
            })
            
            assert result is not None
            assert result['success'] is True
            assert 'tools' in result
            assert len(result['tools']) == 2
    
    def test_invoke_tool_execution(self, mcp_tool):
        """Test invoking a remote tool."""
        # Setup connected server with discovered tools
        mcp_tool.connections['test-server'] = {
            'transport': Mock(),
            'connection': {'status': 'connected'},
            'endpoint': 'test-endpoint'
        }
        mcp_tool.discovered_tools['test-server'] = [
            {'name': 'test_tool', 'description': 'Test Tool'}
        ]
        
        with patch.object(mcp_tool, '_invoke_stdio') as mock_invoke:
            mock_invoke.return_value = {
                'result': 'Tool executed successfully',
                'data': {'output': 'test output'}
            }
            
            result = mcp_tool.invoke({
                'action': 'invoke_tool',
                'server_id': 'test-server',
                'tool_name': 'test_tool',
                'arguments': {'arg1': 'value1'}
            })
            
            assert result is not None
            assert result['success'] is True
            assert 'result' in result
    
    def test_invoke_disconnect(self, mcp_tool):
        """Test disconnecting from MCP server."""
        # Setup a connection first
        mock_connection = {'process': Mock(), 'status': 'connected'}
        mcp_tool.connections['test-server'] = {
            'transport': Mock(),
            'connection': mock_connection,
            'endpoint': 'test-endpoint'
        }
        
        result = mcp_tool.invoke({
            'action': 'disconnect',
            'server_id': 'test-server'
        })
        
        assert result is not None
        assert result['success'] is True
        assert 'test-server' not in mcp_tool.connections
    
    def test_invoke_invalid_action(self, mcp_tool):
        """Test handling of invalid action."""
        with pytest.raises(ValueError) as exc_info:
            mcp_tool.invoke({'action': 'invalid_action'})
        
        assert 'Unknown MCP action' in str(exc_info.value)
    
    def test_invoke_missing_action(self, mcp_tool):
        """Test handling of missing action parameter."""
        with pytest.raises(ValueError) as exc_info:
            mcp_tool.invoke({})
        
        assert "action' is required" in str(exc_info.value)
    
    def test_invoke_missing_required_params(self, mcp_tool):
        """Test handling of missing required parameters."""
        with pytest.raises(Exception):  # Will raise validation error
            mcp_tool.invoke({
                'action': 'connect'
                # Missing server_id, transport, endpoint
            })


# =============================================================================
# MCP Transport Tests
# =============================================================================

class TestMCPTransports:
    """Tests for different MCP transport types."""
    
    def test_connect_stdio_transport(self, mcp_tool):
        """Test stdio transport connection."""
        with patch('tools.mcp.subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.poll.return_value = None  # Process is running
            mock_popen.return_value = mock_process
            
            result = mcp_tool._connect_stdio('test-server', timeout=30)
            
            assert result is not None
            assert 'process' in result
            mock_popen.assert_called_once()
    
    def test_connect_http_transport(self, mcp_tool):
        """Test HTTP transport connection."""
        if not hasattr(mcp_tool, '_connect_http'):
            pytest.skip("HTTP transport not available")
        
        with patch('tools.mcp.httpx') as mock_httpx:
            mock_client = Mock()
            mock_httpx.Client.return_value = mock_client
            
            result = mcp_tool._connect_http('http://localhost:8000', auth=None, timeout=30)
            
            assert result is not None
    
    def test_connect_invalid_transport(self, mcp_tool):
        """Test handling of invalid transport type."""
        with pytest.raises(ValueError) as exc_info:
            mcp_tool.invoke({
                'action': 'connect',
                'server_id': 'test',
                'transport': 'invalid_transport',
                'endpoint': 'test'
            })
        
        assert 'Invalid transport type' in str(exc_info.value)


# =============================================================================
# MCP Error Handling Tests
# =============================================================================

class TestMCPErrorHandling:
    """Tests for MCP error handling."""
    
    def test_connection_error_handling(self, mcp_tool):
        """Test handling connection errors gracefully."""
        with patch.object(mcp_tool, '_connect_stdio') as mock_connect:
            mock_connect.side_effect = ConnectionError("Cannot connect to server")
            
            result = mcp_tool.invoke({
                'action': 'connect',
                'server_id': 'test',
                'transport': 'stdio',
                'endpoint': 'failing-server'
            })
            
            assert result is not None
            assert result['success'] is False
            assert 'error' in result
    
    def test_discover_on_disconnected_server(self, mcp_tool):
        """Test discovering tools on non-existent server."""
        with pytest.raises(Exception):  # Will raise key error or validation error
            mcp_tool.invoke({
                'action': 'discover',
                'server_id': 'nonexistent-server'
            })
    
    def test_invoke_tool_on_disconnected_server(self, mcp_tool):
        """Test invoking tool on non-existent server."""
        with pytest.raises(Exception):
            mcp_tool.invoke({
                'action': 'invoke_tool',
                'server_id': 'nonexistent-server',
                'tool_name': 'test_tool',
                'arguments': {}
            })
    
    def test_retry_logic_on_transient_errors(self, mcp_tool):
        """Test retry logic with exponential backoff."""
        attempt_count = [0]
        
        def failing_operation():
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                raise Exception("Transient error")
            return "Success"
        
        with patch.object(mcp_tool, 'max_retries', 3):
            result = mcp_tool._retry_operation(failing_operation)
            
            assert result == "Success"
            assert attempt_count[0] == 3


# =============================================================================
# MCP Workflow Tests
# =============================================================================

class TestMCPWorkflows:
    """Tests for complete MCP workflows."""
    
    def test_full_workflow_connect_discover_invoke(self, mcp_tool):
        """Test complete workflow: connect -> discover -> invoke."""
        with patch.object(mcp_tool, '_connect_stdio') as mock_connect, \
             patch.object(mcp_tool, '_discover_stdio') as mock_discover, \
             patch.object(mcp_tool, '_invoke_stdio') as mock_invoke:
            
            # Step 1: Connect
            mock_connect.return_value = {'process': Mock(), 'status': 'connected'}
            connect_result = mcp_tool.invoke({
                'action': 'connect',
                'server_id': 'workflow-server',
                'transport': 'stdio',
                'endpoint': 'test-server'
            })
            assert connect_result['success'] is True
            
            # Step 2: Discover tools
            mock_discover.return_value = [
                {'name': 'calculate', 'description': 'Calculate something'}
            ]
            discover_result = mcp_tool.invoke({
                'action': 'discover',
                'server_id': 'workflow-server'
            })
            assert discover_result['success'] is True
            assert len(discover_result['tools']) == 1
            
            # Step 3: Invoke tool
            mock_invoke.return_value = {'result': 'calculated', 'value': 42}
            invoke_result = mcp_tool.invoke({
                'action': 'invoke_tool',
                'server_id': 'workflow-server',
                'tool_name': 'calculate',
                'arguments': {'x': 6, 'y': 7}
            })
            assert invoke_result['success'] is True
    
    def test_connection_state_management(self, mcp_tool):
        """Test connection state is properly managed."""
        with patch.object(mcp_tool, '_connect_stdio') as mock_connect:
            mock_connect.return_value = {'process': Mock()}
            
            # Connect to server
            mcp_tool.invoke({
                'action': 'connect',
                'server_id': 'state-test',
                'transport': 'stdio',
                'endpoint': 'test'
            })
            
            assert 'state-test' in mcp_tool.connections
            
            # Disconnect
            mcp_tool.invoke({
                'action': 'disconnect',
                'server_id': 'state-test'
            })
            
            assert 'state-test' not in mcp_tool.connections
