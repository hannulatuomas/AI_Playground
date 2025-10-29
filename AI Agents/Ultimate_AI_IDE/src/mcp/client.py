"""
MCP Client

Core MCP client for communicating with MCP servers.
"""

import json
import subprocess
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from .types import (
    MCPServer, MCPTool, MCPResource, MCPPrompt,
    MCPToolCall, MCPToolResult, MCPServerType
)

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP protocol client."""
    
    def __init__(self, server: MCPServer):
        """
        Initialize MCP client.
        
        Args:
            server: MCP server configuration
        """
        self.server = server
        self.process: Optional[subprocess.Popen] = None
        self.tools: List[MCPTool] = []
        self.resources: List[MCPResource] = []
        self.prompts: List[MCPPrompt] = []
        self.connected = False
    
    def connect(self) -> bool:
        """
        Connect to MCP server.
        
        Returns:
            True if connection successful
        """
        try:
            if self.server.type == MCPServerType.STDIO:
                return self._connect_stdio()
            elif self.server.type == MCPServerType.HTTP:
                return self._connect_http()
            elif self.server.type == MCPServerType.WEBSOCKET:
                return self._connect_websocket()
            else:
                logger.error(f"Unsupported server type: {self.server.type}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to {self.server.name}: {e}")
            return False
    
    def _connect_stdio(self) -> bool:
        """Connect to stdio-based MCP server."""
        if not self.server.command:
            logger.error("No command specified for stdio server")
            return False
        
        try:
            # Start the server process
            self.process = subprocess.Popen(
                [self.server.command] + self.server.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**subprocess.os.environ, **self.server.env}
            )
            
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "clientInfo": {
                        "name": "UAIDE",
                        "version": "1.2.0"
                    }
                }
            }
            
            self._send_request(init_request)
            response = self._receive_response()
            
            if response and "result" in response:
                self.connected = True
                logger.info(f"Connected to {self.server.name}")
                
                # Discover capabilities
                self._discover_capabilities()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to connect stdio server: {e}")
            return False
    
    def _connect_http(self) -> bool:
        """Connect to HTTP-based MCP server."""
        # TODO: Implement HTTP connection
        logger.warning("HTTP MCP servers not yet implemented")
        return False
    
    def _connect_websocket(self) -> bool:
        """Connect to WebSocket-based MCP server."""
        # TODO: Implement WebSocket connection
        logger.warning("WebSocket MCP servers not yet implemented")
        return False
    
    def _discover_capabilities(self):
        """Discover server capabilities (tools, resources, prompts)."""
        try:
            # List tools
            tools_response = self._send_request({
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            })
            
            if tools_response and "result" in tools_response:
                for tool_data in tools_response["result"].get("tools", []):
                    tool = MCPTool(
                        name=tool_data["name"],
                        description=tool_data.get("description", ""),
                        input_schema=tool_data.get("inputSchema", {}),
                        server_name=self.server.name
                    )
                    self.tools.append(tool)
            
            # List resources
            resources_response = self._send_request({
                "jsonrpc": "2.0",
                "id": 3,
                "method": "resources/list",
                "params": {}
            })
            
            if resources_response and "result" in resources_response:
                for res_data in resources_response["result"].get("resources", []):
                    resource = MCPResource(
                        uri=res_data["uri"],
                        name=res_data["name"],
                        description=res_data.get("description", ""),
                        mime_type=res_data.get("mimeType"),
                        server_name=self.server.name
                    )
                    self.resources.append(resource)
            
            # List prompts
            prompts_response = self._send_request({
                "jsonrpc": "2.0",
                "id": 4,
                "method": "prompts/list",
                "params": {}
            })
            
            if prompts_response and "result" in prompts_response:
                for prompt_data in prompts_response["result"].get("prompts", []):
                    prompt = MCPPrompt(
                        name=prompt_data["name"],
                        description=prompt_data.get("description", ""),
                        arguments=prompt_data.get("arguments", []),
                        server_name=self.server.name
                    )
                    self.prompts.append(prompt)
            
            logger.info(
                f"Discovered {len(self.tools)} tools, "
                f"{len(self.resources)} resources, "
                f"{len(self.prompts)} prompts from {self.server.name}"
            )
            
        except Exception as e:
            logger.error(f"Failed to discover capabilities: {e}")
    
    def call_tool(self, tool_call: MCPToolCall) -> MCPToolResult:
        """
        Call an MCP tool.
        
        Args:
            tool_call: Tool call request
            
        Returns:
            Tool call result
        """
        if not self.connected:
            return MCPToolResult(
                success=False,
                content=None,
                error="Not connected to server",
                is_error=True
            )
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 100,  # TODO: Implement proper ID management
                "method": "tools/call",
                "params": {
                    "name": tool_call.tool_name,
                    "arguments": tool_call.arguments
                }
            }
            
            response = self._send_request(request)
            
            if response and "result" in response:
                return MCPToolResult(
                    success=True,
                    content=response["result"].get("content", []),
                    is_error=False
                )
            elif response and "error" in response:
                return MCPToolResult(
                    success=False,
                    content=None,
                    error=response["error"].get("message", "Unknown error"),
                    is_error=True
                )
            else:
                return MCPToolResult(
                    success=False,
                    content=None,
                    error="Invalid response from server",
                    is_error=True
                )
                
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return MCPToolResult(
                success=False,
                content=None,
                error=str(e),
                is_error=True
            )
    
    def read_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """
        Read an MCP resource.
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content or None
        """
        if not self.connected:
            return None
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 200,
                "method": "resources/read",
                "params": {"uri": uri}
            }
            
            response = self._send_request(request)
            
            if response and "result" in response:
                return response["result"]
            
            return None
            
        except Exception as e:
            logger.error(f"Resource read failed: {e}")
            return None
    
    def get_prompt(self, name: str, arguments: Dict[str, Any] = None) -> Optional[str]:
        """
        Get an MCP prompt.
        
        Args:
            name: Prompt name
            arguments: Prompt arguments
            
        Returns:
            Prompt text or None
        """
        if not self.connected:
            return None
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 300,
                "method": "prompts/get",
                "params": {
                    "name": name,
                    "arguments": arguments or {}
                }
            }
            
            response = self._send_request(request)
            
            if response and "result" in response:
                messages = response["result"].get("messages", [])
                if messages:
                    return messages[0].get("content", {}).get("text", "")
            
            return None
            
        except Exception as e:
            logger.error(f"Prompt get failed: {e}")
            return None
    
    def _send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send JSON-RPC request to server."""
        if not self.process or not self.process.stdin:
            return None
        
        try:
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            return self._receive_response()
            
        except Exception as e:
            logger.error(f"Failed to send request: {e}")
            return None
    
    def _receive_response(self) -> Optional[Dict[str, Any]]:
        """Receive JSON-RPC response from server."""
        if not self.process or not self.process.stdout:
            return None
        
        try:
            response_line = self.process.stdout.readline()
            if response_line:
                return json.loads(response_line)
            return None
            
        except Exception as e:
            logger.error(f"Failed to receive response: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from MCP server."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
            finally:
                self.process = None
                self.connected = False
                logger.info(f"Disconnected from {self.server.name}")
    
    def __del__(self):
        """Cleanup on deletion."""
        self.disconnect()
