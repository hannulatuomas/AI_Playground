"""
MCP Server Manager

Manages multiple MCP server connections.
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

from .client import MCPClient
from .types import (
    MCPServer, MCPTool, MCPResource, MCPPrompt,
    MCPToolCall, MCPToolResult, MCPServerType
)

logger = logging.getLogger(__name__)


class MCPServerManager:
    """Manages MCP server connections."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize MCP server manager.
        
        Args:
            config_path: Path to MCP configuration file
        """
        self.config_path = config_path or "mcp_servers.json"
        self.servers: Dict[str, MCPServer] = {}
        self.clients: Dict[str, MCPClient] = {}
        self.load_config()
    
    def load_config(self):
        """Load MCP server configurations from file."""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            logger.info("No MCP config found, using defaults")
            self._create_default_config()
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            for server_name, server_data in config_data.get("servers", {}).items():
                server = MCPServer(
                    name=server_name,
                    type=MCPServerType(server_data.get("type", "stdio")),
                    command=server_data.get("command"),
                    args=server_data.get("args", []),
                    url=server_data.get("url"),
                    env=server_data.get("env", {}),
                    enabled=server_data.get("enabled", True),
                    auto_start=server_data.get("auto_start", True),
                    description=server_data.get("description", "")
                )
                self.servers[server_name] = server
            
            logger.info(f"Loaded {len(self.servers)} MCP server configurations")
            
        except Exception as e:
            logger.error(f"Failed to load MCP config: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default MCP configuration."""
        default_servers = {
            "filesystem": MCPServer(
                name="filesystem",
                type=MCPServerType.STDIO,
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "."],
                description="File system access MCP server",
                enabled=False,  # Disabled by default for security
                auto_start=False
            ),
            "github": MCPServer(
                name="github",
                type=MCPServerType.STDIO,
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={"GITHUB_PERSONAL_ACCESS_TOKEN": ""},
                description="GitHub API MCP server",
                enabled=False,
                auto_start=False
            ),
            "brave-search": MCPServer(
                name="brave-search",
                type=MCPServerType.STDIO,
                command="npx",
                args=["-y", "@modelcontextprotocol/server-brave-search"],
                env={"BRAVE_API_KEY": ""},
                description="Brave Search API MCP server",
                enabled=False,
                auto_start=False
            ),
        }
        
        self.servers = default_servers
        self.save_config()
    
    def save_config(self):
        """Save MCP server configurations to file."""
        try:
            config_data = {
                "servers": {
                    name: {
                        "type": server.type.value,
                        "command": server.command,
                        "args": server.args,
                        "url": server.url,
                        "env": server.env,
                        "enabled": server.enabled,
                        "auto_start": server.auto_start,
                        "description": server.description
                    }
                    for name, server in self.servers.items()
                }
            }
            
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Saved MCP configuration to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save MCP config: {e}")
    
    def start_server(self, server_name: str) -> bool:
        """
        Start an MCP server.
        
        Args:
            server_name: Name of server to start
            
        Returns:
            True if started successfully
        """
        if server_name not in self.servers:
            logger.error(f"Server '{server_name}' not found")
            return False
        
        if server_name in self.clients:
            logger.warning(f"Server '{server_name}' already running")
            return True
        
        server = self.servers[server_name]
        
        if not server.enabled:
            logger.warning(f"Server '{server_name}' is disabled")
            return False
        
        try:
            client = MCPClient(server)
            if client.connect():
                self.clients[server_name] = client
                logger.info(f"Started MCP server: {server_name}")
                return True
            else:
                logger.error(f"Failed to start server: {server_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting server {server_name}: {e}")
            return False
    
    def stop_server(self, server_name: str):
        """
        Stop an MCP server.
        
        Args:
            server_name: Name of server to stop
        """
        if server_name in self.clients:
            self.clients[server_name].disconnect()
            del self.clients[server_name]
            logger.info(f"Stopped MCP server: {server_name}")
    
    def start_all(self):
        """Start all enabled servers with auto_start."""
        for name, server in self.servers.items():
            if server.enabled and server.auto_start:
                self.start_server(name)
    
    def stop_all(self):
        """Stop all running servers."""
        for name in list(self.clients.keys()):
            self.stop_server(name)
    
    def get_all_tools(self) -> List[MCPTool]:
        """Get all tools from all connected servers."""
        tools = []
        for client in self.clients.values():
            tools.extend(client.tools)
        return tools
    
    def get_all_resources(self) -> List[MCPResource]:
        """Get all resources from all connected servers."""
        resources = []
        for client in self.clients.values():
            resources.extend(client.resources)
        return resources
    
    def get_all_prompts(self) -> List[MCPPrompt]:
        """Get all prompts from all connected servers."""
        prompts = []
        for client in self.clients.values():
            prompts.extend(client.prompts)
        return prompts
    
    def call_tool(self, tool_call: MCPToolCall) -> MCPToolResult:
        """
        Call a tool on the appropriate server.
        
        Args:
            tool_call: Tool call request
            
        Returns:
            Tool call result
        """
        if tool_call.server_name not in self.clients:
            return MCPToolResult(
                success=False,
                content=None,
                error=f"Server '{tool_call.server_name}' not connected",
                is_error=True
            )
        
        client = self.clients[tool_call.server_name]
        return client.call_tool(tool_call)
    
    def read_resource(self, server_name: str, uri: str) -> Optional[Dict]:
        """
        Read a resource from a server.
        
        Args:
            server_name: Server name
            uri: Resource URI
            
        Returns:
            Resource content or None
        """
        if server_name not in self.clients:
            logger.error(f"Server '{server_name}' not connected")
            return None
        
        client = self.clients[server_name]
        return client.read_resource(uri)
    
    def get_prompt(self, server_name: str, name: str, 
                   arguments: Dict = None) -> Optional[str]:
        """
        Get a prompt from a server.
        
        Args:
            server_name: Server name
            name: Prompt name
            arguments: Prompt arguments
            
        Returns:
            Prompt text or None
        """
        if server_name not in self.clients:
            logger.error(f"Server '{server_name}' not connected")
            return None
        
        client = self.clients[server_name]
        return client.get_prompt(name, arguments)
    
    def add_server(self, server: MCPServer):
        """Add a new server configuration."""
        self.servers[server.name] = server
        self.save_config()
    
    def remove_server(self, server_name: str):
        """Remove a server configuration."""
        if server_name in self.clients:
            self.stop_server(server_name)
        
        if server_name in self.servers:
            del self.servers[server_name]
            self.save_config()
    
    def get_server_status(self) -> Dict[str, Dict]:
        """Get status of all servers."""
        status = {}
        for name, server in self.servers.items():
            status[name] = {
                "enabled": server.enabled,
                "connected": name in self.clients,
                "tools": len(self.clients[name].tools) if name in self.clients else 0,
                "resources": len(self.clients[name].resources) if name in self.clients else 0,
                "prompts": len(self.clients[name].prompts) if name in self.clients else 0,
                "description": server.description
            }
        return status
    
    def __del__(self):
        """Cleanup on deletion."""
        self.stop_all()
