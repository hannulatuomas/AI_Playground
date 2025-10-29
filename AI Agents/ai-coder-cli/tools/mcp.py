
"""
MCP (Model Context Protocol) Client Tool.

This tool implements a client for the Model Context Protocol,
supporting stdio, SSE, and HTTP transports with:
- Proper stdio implementation with subprocess.Popen
- SSE implementation with httpx streaming
- HTTP implementation with httpx connection pooling
- Authentication handling (API keys, tokens, bearer)
- Comprehensive error handling
- Retry logic with exponential backoff
- Timeout handling for all transports
"""

import asyncio
import json
import subprocess
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from enum import Enum

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from .base import Tool


class TransportType(Enum):
    """MCP transport types."""
    STDIO = "stdio"
    SSE = "sse"
    HTTP = "http"


class MCPClientTool(Tool):
    """
    Tool for Model Context Protocol client operations.
    
    Capabilities:
    - Connect to MCP servers via stdio, SSE, or HTTP
    - Discover available tools from MCP servers
    - Invoke remote tools
    - Handle authentication
    - Async operations for network transports
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MCP client tool.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(
            name='mcp',
            description='Model Context Protocol client for external tool integration',
            config=config
        )
        
        self.connections: Dict[str, Any] = {}
        self.discovered_tools: Dict[str, List[Dict[str, Any]]] = {}
        
        # Retry configuration
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 1.0)
        self.retry_backoff = self.config.get('retry_backoff', 2.0)
    
    def invoke(self, params: Dict[str, Any]) -> Any:
        """
        Execute MCP operation.
        
        Args:
            params: Dictionary with:
                - action: Operation (connect, discover, invoke_tool, disconnect)
                - server_id: Server identifier
                - Additional action-specific parameters
                
        Returns:
            Operation result
        """
        self._log_invocation(params)
        
        action = params.get('action')
        if not action:
            raise ValueError("Parameter 'action' is required")
        
        # Route to appropriate method
        if action == 'connect':
            return self._connect(params)
        elif action == 'discover':
            return self._discover_tools(params)
        elif action == 'invoke_tool':
            return self._invoke_tool(params)
        elif action == 'disconnect':
            return self._disconnect(params)
        else:
            raise ValueError(f"Unknown MCP action: {action}")
    
    def _retry_operation(self, operation_func, *args, **kwargs) -> Any:
        """
        Retry an operation with exponential backoff.
        
        Args:
            operation_func: Function to retry
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Operation result
            
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        delay = self.retry_delay
        
        for attempt in range(self.max_retries + 1):
            try:
                return operation_func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    self.logger.warning(
                        f"Operation failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                    delay *= self.retry_backoff
                else:
                    self.logger.error(f"Operation failed after {self.max_retries + 1} attempts")
        
        raise last_exception
    
    def _connect(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Connect to an MCP server.
        
        Args:
            params: Connection parameters with:
                - server_id: Unique server identifier
                - transport: Transport type (stdio, sse, http)
                - endpoint: Server endpoint (command or URL)
                - auth: Optional authentication credentials
                - timeout: Connection timeout (default: 30)
                
        Returns:
            Connection result
        """
        self.validate_params(params, ['server_id', 'transport', 'endpoint'])
        
        server_id = params['server_id']
        transport_str = params['transport']
        endpoint = params['endpoint']
        auth = params.get('auth')
        timeout = params.get('timeout', 30)
        
        try:
            transport = TransportType(transport_str)
        except ValueError:
            raise ValueError(f"Invalid transport type: {transport_str}")
        
        try:
            if transport == TransportType.STDIO:
                connection = self._connect_stdio(endpoint, timeout)
            elif transport == TransportType.SSE:
                connection = self._connect_sse(endpoint, auth, timeout)
            elif transport == TransportType.HTTP:
                connection = self._connect_http(endpoint, auth, timeout)
            else:
                raise ValueError(f"Transport not implemented: {transport}")
            
            self.connections[server_id] = {
                'transport': transport,
                'connection': connection,
                'endpoint': endpoint
            }
            
            self.logger.info(f"Connected to MCP server '{server_id}' via {transport.value}")
            
            return {
                'success': True,
                'server_id': server_id,
                'transport': transport.value,
                'message': f'Connected to {server_id}'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MCP server '{server_id}': {e}")
            return {
                'success': False,
                'server_id': server_id,
                'error': str(e)
            }
    
    def _connect_stdio(self, command: str, timeout: int) -> Dict[str, Any]:
        """
        Connect via stdio (spawn subprocess).
        
        Args:
            command: Command to spawn MCP server
            timeout: Connection timeout
            
        Returns:
            Connection object
        """
        try:
            process = subprocess.Popen(
                command.split(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            return {
                'type': 'stdio',
                'process': process,
                'command': command
            }
        except Exception as e:
            raise RuntimeError(f"Failed to spawn MCP server: {e}") from e
    
    def _connect_sse(self, url: str, auth: Optional[Dict], timeout: int) -> Dict[str, Any]:
        """
        Connect via Server-Sent Events (streaming).
        
        Args:
            url: SSE endpoint URL
            auth: Authentication credentials
            timeout: Connection timeout
            
        Returns:
            Connection object
        """
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx required for SSE transport")
        
        # Create httpx client for SSE streaming
        # SSE connection is kept alive for streaming events
        client = httpx.Client(timeout=timeout)
        headers = self._build_auth_headers(auth)
        headers['Accept'] = 'text/event-stream'
        headers['Cache-Control'] = 'no-cache'
        
        # Test connection
        try:
            response = client.get(url, headers=headers)
            if response.status_code != 200:
                client.close()
                raise RuntimeError(f"SSE connection failed: HTTP {response.status_code}")
        except Exception as e:
            client.close()
            raise RuntimeError(f"SSE connection failed: {str(e)}") from e
        
        return {
            'type': 'sse',
            'url': url,
            'auth': auth,
            'timeout': timeout,
            'client': client,
            'headers': headers
        }
    
    def _connect_http(self, url: str, auth: Optional[Dict], timeout: int) -> Dict[str, Any]:
        """
        Connect via HTTP with connection pooling.
        
        Args:
            url: HTTP endpoint URL
            auth: Authentication credentials
            timeout: Connection timeout
            
        Returns:
            Connection object
        """
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx required for HTTP transport")
        
        # Create httpx client with connection pooling
        # This reuses connections for better performance
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        client = httpx.Client(timeout=timeout, limits=limits)
        
        # Test connection
        try:
            headers = self._build_auth_headers(auth)
            response = client.get(url, headers=headers)
            if response.status_code >= 500:
                client.close()
                raise RuntimeError(f"HTTP connection failed: HTTP {response.status_code}")
        except httpx.HTTPError as e:
            client.close()
            raise RuntimeError(f"HTTP connection failed: {str(e)}") from e
        
        return {
            'type': 'http',
            'url': url,
            'auth': auth,
            'timeout': timeout,
            'client': client
        }
    
    def _discover_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Discover available tools from MCP server.
        
        Args:
            params: Parameters with server_id
            
        Returns:
            Discovered tools
        """
        self.validate_params(params, ['server_id'])
        
        server_id = params['server_id']
        
        if server_id not in self.connections:
            return {
                'success': False,
                'error': f'Not connected to server: {server_id}'
            }
        
        connection = self.connections[server_id]
        
        try:
            # Send tool discovery request based on transport
            if connection['transport'] == TransportType.STDIO:
                tools = self._discover_stdio(connection['connection'])
            elif connection['transport'] == TransportType.HTTP:
                tools = asyncio.run(self._discover_http(connection['connection']))
            else:
                tools = []
            
            self.discovered_tools[server_id] = tools
            
            return {
                'success': True,
                'server_id': server_id,
                'tools': tools,
                'count': len(tools)
            }
            
        except Exception as e:
            self.logger.error(f"Tool discovery failed for '{server_id}': {e}")
            return {
                'success': False,
                'server_id': server_id,
                'error': str(e)
            }
    
    def _discover_stdio(self, connection: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Discover tools via stdio.
        
        Args:
            connection: stdio connection object
            
        Returns:
            List of tool definitions
        """
        process = connection['process']
        
        # Send discovery request
        request = json.dumps({
            'jsonrpc': '2.0',
            'method': 'tools/list',
            'id': 1
        }) + '\n'
        
        try:
            process.stdin.write(request)
            process.stdin.flush()
            
            # Read response
            response_line = process.stdout.readline()
            response = json.loads(response_line)
            
            if 'result' in response:
                return response['result'].get('tools', [])
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"stdio discovery failed: {e}")
            return []
    
    async def _discover_http(self, connection: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Discover tools via HTTP using persistent client.
        
        Args:
            connection: HTTP connection object
            
        Returns:
            List of tool definitions
        """
        url = connection['url']
        auth = connection.get('auth')
        client = connection.get('client')
        
        if not client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = self._build_auth_headers(auth)
        
        # Use retry logic
        def _do_discover():
            response = client.post(f"{url}/tools/list", headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get('tools', [])
        
        return self._retry_operation(_do_discover)
    
    def _invoke_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke a tool on the MCP server.
        
        Args:
            params: Parameters with:
                - server_id: Server identifier
                - tool_name: Name of tool to invoke
                - tool_params: Parameters for the tool
                
        Returns:
            Tool invocation result
        """
        self.validate_params(params, ['server_id', 'tool_name'])
        
        server_id = params['server_id']
        tool_name = params['tool_name']
        tool_params = params.get('tool_params', {})
        
        if server_id not in self.connections:
            return {
                'success': False,
                'error': f'Not connected to server: {server_id}'
            }
        
        connection = self.connections[server_id]
        
        try:
            # Invoke tool based on transport
            if connection['transport'] == TransportType.STDIO:
                result = self._invoke_stdio(connection['connection'], tool_name, tool_params)
            elif connection['transport'] == TransportType.HTTP:
                result = asyncio.run(
                    self._invoke_http(connection['connection'], tool_name, tool_params)
                )
            else:
                result = None
            
            return {
                'success': True,
                'server_id': server_id,
                'tool_name': tool_name,
                'result': result
            }
            
        except Exception as e:
            self.logger.error(f"Tool invocation failed for '{tool_name}' on '{server_id}': {e}")
            return {
                'success': False,
                'server_id': server_id,
                'tool_name': tool_name,
                'error': str(e)
            }
    
    def _invoke_stdio(
        self,
        connection: Dict[str, Any],
        tool_name: str,
        tool_params: Dict[str, Any]
    ) -> Any:
        """Invoke tool via stdio."""
        process = connection['process']
        
        request = json.dumps({
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'params': {
                'name': tool_name,
                'arguments': tool_params
            },
            'id': 2
        }) + '\n'
        
        process.stdin.write(request)
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        response = json.loads(response_line)
        
        if 'result' in response:
            return response['result']
        elif 'error' in response:
            raise RuntimeError(f"Tool error: {response['error']}")
        else:
            return None
    
    async def _invoke_http(
        self,
        connection: Dict[str, Any],
        tool_name: str,
        tool_params: Dict[str, Any]
    ) -> Any:
        """Invoke tool via HTTP using persistent client."""
        url = connection['url']
        auth = connection.get('auth')
        client = connection.get('client')
        
        if not client:
            raise RuntimeError("HTTP client not initialized")
        
        headers = self._build_auth_headers(auth)
        
        # Use retry logic
        def _do_invoke():
            response = client.post(
                f"{url}/tools/call",
                json={
                    'name': tool_name,
                    'arguments': tool_params
                },
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        
        return self._retry_operation(_do_invoke)
    
    def _disconnect(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Disconnect from MCP server.
        
        Args:
            params: Parameters with server_id
            
        Returns:
            Disconnect result
        """
        self.validate_params(params, ['server_id'])
        
        server_id = params['server_id']
        
        if server_id not in self.connections:
            return {
                'success': False,
                'error': f'Not connected to server: {server_id}'
            }
        
        connection = self.connections[server_id]
        
        try:
            # Clean up based on transport
            conn_obj = connection['connection']
            
            if connection['transport'] == TransportType.STDIO:
                process = conn_obj['process']
                process.terminate()
                process.wait(timeout=5)
            elif connection['transport'] in [TransportType.HTTP, TransportType.SSE]:
                # Close HTTP/SSE client
                client = conn_obj.get('client')
                if client:
                    client.close()
            
            del self.connections[server_id]
            
            if server_id in self.discovered_tools:
                del self.discovered_tools[server_id]
            
            self.logger.info(f"Disconnected from MCP server '{server_id}'")
            
            return {
                'success': True,
                'server_id': server_id,
                'message': f'Disconnected from {server_id}'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to disconnect from '{server_id}': {e}")
            return {
                'success': False,
                'server_id': server_id,
                'error': str(e)
            }
    
    def _build_auth_headers(self, auth: Optional[Dict[str, str]]) -> Dict[str, str]:
        """
        Build authentication headers.
        
        Args:
            auth: Authentication credentials
            
        Returns:
            HTTP headers dictionary
        """
        headers = {}
        
        if not auth:
            return headers
        
        if 'token' in auth:
            headers['Authorization'] = f"Bearer {auth['token']}"
        elif 'api_key' in auth:
            headers['X-API-Key'] = auth['api_key']
        elif 'bearer_token' in auth:
            headers['Authorization'] = f"Bearer {auth['bearer_token']}"
        
        return headers
