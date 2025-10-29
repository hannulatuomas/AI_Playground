#!/usr/bin/env python3
"""
MCP Server for Kali Linux - Complete Edition
Provides comprehensive Linux system management capabilities.
"""
import asyncio
from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent
import logging

# Import tool modules
from tools import (
    register_shell_tools,
    handle_shell_tools,
    register_file_tools,
    handle_file_tools,
    register_filesystem_tools,
    handle_filesystem_tools,
    register_text_tools,
    handle_text_tools,
    register_network_tools,
    handle_network_tools,
    register_archive_tools,
    handle_archive_tools,
    register_system_tools,
    handle_system_tools,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-kali-server")

# Create server instance
server = Server("kali-linux-tools")


@server.list_tools()
async def handle_list_tools():
    """List all available tools from all modules."""
    tools = []
    
    # Collect tools from all modules
    tools.extend(register_shell_tools())
    tools.extend(register_file_tools())
    tools.extend(register_filesystem_tools())
    tools.extend(register_text_tools())
    tools.extend(register_network_tools())
    tools.extend(register_archive_tools())
    tools.extend(register_system_tools())
    
    logger.info(f"Registered {len(tools)} tools")
    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Route tool calls to appropriate handler."""
    logger.info(f"Tool called: {name}")
    
    # Try each module's handler
    result = await handle_shell_tools(name, arguments)
    if result is not None:
        return result
    
    result = await handle_file_tools(name, arguments)
    if result is not None:
        return result
    
    result = await handle_filesystem_tools(name, arguments)
    if result is not None:
        return result
    
    result = await handle_text_tools(name, arguments)
    if result is not None:
        return result
    
    result = await handle_network_tools(name, arguments)
    if result is not None:
        return result
    
    result = await handle_archive_tools(name, arguments)
    if result is not None:
        return result
    
    result = await handle_system_tools(name, arguments)
    if result is not None:
        return result
    
    # Tool not found
    raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server."""
    logger.info("=" * 70)
    logger.info("Starting Kali Linux MCP Server - Complete Edition")
    logger.info("=" * 70)
    logger.info("Categories:")
    logger.info("  • Shell Execution (bash/zsh/python)")
    logger.info("  • File Operations (read/write/copy/move/delete)")
    logger.info("  • Filesystem Tools (ls/find/stat)")
    logger.info("  • Text Processing (grep/sed/awk/sort)")
    logger.info("  • Network Tools (curl/wget/ping/dns)")
    logger.info("  • Archive Tools (tar/zip/gzip)")
    logger.info("  • System Tools (ps/kill/systemctl/resources)")
    logger.info("=" * 70)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="kali-linux-tools",
                server_version="4.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
