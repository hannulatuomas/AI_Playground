"""
Filesystem tools: ls, find, file info, etc.
"""
import shlex
from typing import Any
from mcp.types import Tool, TextContent
from .shell_tools import execute_shell_command
import logging

logger = logging.getLogger("mcp-filesystem-tools")


def register_filesystem_tools() -> list[Tool]:
    """Register all filesystem tools."""
    return [
        Tool(
            name="list_directory",
            description="List contents of a directory (ls command). Returns detailed file information including permissions, size, and modification time.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list (default: current directory)",
                        "default": "."
                    },
                    "show_hidden": {
                        "type": "boolean",
                        "description": "Show hidden files (files starting with .)",
                        "default": False
                    },
                    "long_format": {
                        "type": "boolean",
                        "description": "Use long listing format with details",
                        "default": True
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "List subdirectories recursively",
                        "default": False
                    },
                    "human_readable": {
                        "type": "boolean",
                        "description": "Print sizes in human readable format (e.g., 1K, 234M, 2G)",
                        "default": True
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="find_files",
            description="Search for files and directories (find command). Supports various search criteria like name patterns, type, size, and modification time.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Starting directory for search",
                        "default": "."
                    },
                    "name_pattern": {
                        "type": "string",
                        "description": "File name pattern (supports wildcards like *.txt)"
                    },
                    "file_type": {
                        "type": "string",
                        "enum": ["f", "d", "l"],
                        "description": "File type: 'f' (regular file), 'd' (directory), 'l' (symbolic link)"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum directory depth to search"
                    },
                    "modified_within": {
                        "type": "string",
                        "description": "Find files modified within time period (e.g., '1' for 1 day, '24h', '7d')"
                    },
                    "size": {
                        "type": "string",
                        "description": "File size criteria (e.g., '+10M' larger than 10MB, '-1G' smaller than 1GB)"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="file_info",
            description="Get detailed file or directory information (stat, file commands). Shows size, permissions, timestamps, and file type.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File or directory path"
                    },
                    "follow_symlinks": {
                        "type": "boolean",
                        "description": "Follow symbolic links",
                        "default": True
                    }
                },
                "required": ["path"]
            }
        ),
    ]


async def handle_filesystem_tools(name: str, arguments: dict[str, Any]) -> list[TextContent] | None:
    """Handle filesystem tool execution."""
    handlers = {
        "list_directory": list_directory,
        "find_files": find_files,
        "file_info": file_info,
    }
    
    handler = handlers.get(name)
    if handler:
        return await handler(arguments)
    return None


# ============================================================================
# Filesystem Tools Implementation
# ============================================================================

async def list_directory(arguments: dict[str, Any]) -> list[TextContent]:
    """List directory contents using ls command."""
    path = arguments.get("path", ".")
    show_hidden = arguments.get("show_hidden", False)
    long_format = arguments.get("long_format", True)
    recursive = arguments.get("recursive", False)
    human_readable = arguments.get("human_readable", True)
    
    logger.info(f"Listing directory: {path}")
    
    cmd_parts = ["ls"]
    if long_format:
        cmd_parts.append("-l")
    if show_hidden:
        cmd_parts.append("-a")
    if recursive:
        cmd_parts.append("-R")
    if human_readable and long_format:
        cmd_parts.append("-h")
    cmd_parts.append(shlex.quote(path))
    
    command = " ".join(cmd_parts)
    
    return await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )


async def find_files(arguments: dict[str, Any]) -> list[TextContent]:
    """Search for files using find command."""
    path = arguments.get("path", ".")
    name_pattern = arguments.get("name_pattern")
    file_type = arguments.get("file_type")
    max_depth = arguments.get("max_depth")
    modified_within = arguments.get("modified_within")
    size = arguments.get("size")
    
    logger.info(f"Finding files in: {path}")
    
    cmd_parts = ["find", shlex.quote(path)]
    
    if max_depth is not None:
        cmd_parts.extend(["-maxdepth", str(max_depth)])
    if name_pattern:
        cmd_parts.extend(["-name", shlex.quote(name_pattern)])
    if file_type:
        cmd_parts.extend(["-type", file_type])
    if modified_within:
        cmd_parts.extend(["-mtime", f"-{modified_within}"])
    if size:
        cmd_parts.extend(["-size", shlex.quote(size)])
    
    command = " ".join(cmd_parts)
    
    return await execute_shell_command(
        {"command": command, "timeout": 60},
        shell="bash"
    )


async def file_info(arguments: dict[str, Any]) -> list[TextContent]:
    """Get detailed file information."""
    path = arguments.get("path")
    follow_symlinks = arguments.get("follow_symlinks", True)
    
    if not path:
        raise ValueError("Path is required")
    
    logger.info(f"Getting info for: {path}")
    
    stat_flag = "" if follow_symlinks else "-L"
    commands = [
        f"file {shlex.quote(path)}",
        f"stat {stat_flag} {shlex.quote(path)}",
        f"ls -lhd {shlex.quote(path)}"
    ]
    
    command = " && echo '---' && ".join(commands)
    
    return await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )
