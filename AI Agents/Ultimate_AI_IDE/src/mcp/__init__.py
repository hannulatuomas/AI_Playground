"""
MCP (Model Context Protocol) Module

Provides MCP client functionality for connecting to external tools and data sources.
"""

from .client import MCPClient
from .manager import MCPServerManager
from .types import MCPServer, MCPTool, MCPResource, MCPPrompt

__all__ = [
    "MCPClient",
    "MCPServerManager",
    "MCPServer",
    "MCPTool",
    "MCPResource",
    "MCPPrompt",
]
