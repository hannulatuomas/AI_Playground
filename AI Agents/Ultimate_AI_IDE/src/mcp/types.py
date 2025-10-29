"""
MCP Types

Data structures for MCP protocol.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class MCPServerType(Enum):
    """MCP server connection type."""
    STDIO = "stdio"
    HTTP = "http"
    WEBSOCKET = "websocket"


@dataclass
class MCPServer:
    """MCP server configuration."""
    name: str
    type: MCPServerType
    command: Optional[str] = None  # For stdio servers
    args: List[str] = field(default_factory=list)
    url: Optional[str] = None  # For HTTP/WebSocket servers
    env: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    auto_start: bool = True
    description: str = ""


@dataclass
class MCPTool:
    """MCP tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str


@dataclass
class MCPResource:
    """MCP resource definition."""
    uri: str
    name: str
    description: str
    mime_type: Optional[str] = None
    server_name: str = ""


@dataclass
class MCPPrompt:
    """MCP prompt template."""
    name: str
    description: str
    arguments: List[Dict[str, Any]] = field(default_factory=list)
    server_name: str = ""


@dataclass
class MCPToolCall:
    """MCP tool call request."""
    tool_name: str
    arguments: Dict[str, Any]
    server_name: str


@dataclass
class MCPToolResult:
    """MCP tool call result."""
    success: bool
    content: Any
    error: Optional[str] = None
    is_error: bool = False
