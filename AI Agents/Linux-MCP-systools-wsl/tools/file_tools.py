"""
File operations tools: read, write, delete, copy, move, etc.
"""
import os
import shlex
from typing import Any
from mcp.types import Tool, TextContent
from .shell_tools import execute_shell_command
import logging

logger = logging.getLogger("mcp-file-tools")


def register_file_tools() -> list[Tool]:
    """Register all file operation tools."""
    return [
        Tool(
            name="read_file",
            description="Read and display file contents (cat, head, tail commands). Supports reading entire files or specific portions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to read"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["cat", "head", "tail"],
                        "description": "Read mode: 'cat' (entire file), 'head' (first lines), 'tail' (last lines)",
                        "default": "cat"
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Number of lines to read (for head/tail mode, default: 10)",
                        "default": 10
                    },
                    "follow": {
                        "type": "boolean",
                        "description": "Follow file updates (tail -f mode, use with caution)",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="write_file",
            description="Create or overwrite a file with content. Use with caution as it will overwrite existing files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    },
                    "append": {
                        "type": "boolean",
                        "description": "Append to file instead of overwriting",
                        "default": False
                    },
                    "create_dirs": {
                        "type": "boolean",
                        "description": "Create parent directories if they don't exist",
                        "default": False
                    }
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="delete_file",
            description="Delete files or directories (rm command). Use with caution - deleted files cannot be recovered.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File or directory path to delete"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Recursively delete directories and contents",
                        "default": False
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force deletion without prompts",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="copy_file",
            description="Copy files or directories (cp command). Can copy single files or entire directory trees.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source file or directory path"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination path"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Copy directories recursively",
                        "default": False
                    },
                    "preserve": {
                        "type": "boolean",
                        "description": "Preserve file attributes (permissions, timestamps)",
                        "default": True
                    }
                },
                "required": ["source", "destination"]
            }
        ),
        Tool(
            name="move_file",
            description="Move or rename files and directories (mv command).",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source file or directory path"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination path"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force move, overwriting destination if exists",
                        "default": False
                    }
                },
                "required": ["source", "destination"]
            }
        ),
        Tool(
            name="create_directory",
            description="Create directories (mkdir command). Can create nested directory structures.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to create"
                    },
                    "parents": {
                        "type": "boolean",
                        "description": "Create parent directories as needed",
                        "default": True
                    },
                    "mode": {
                        "type": "string",
                        "description": "Permission mode (e.g., '755', '700')"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="change_permissions",
            description="Change file or directory permissions (chmod command).",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File or directory path"
                    },
                    "mode": {
                        "type": "string",
                        "description": "Permission mode (e.g., '755', '644', 'u+x')"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Apply recursively to directories",
                        "default": False
                    }
                },
                "required": ["path", "mode"]
            }
        ),
        Tool(
            name="create_symlink",
            description="Create symbolic links (ln -s command).",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target file or directory"
                    },
                    "link_name": {
                        "type": "string",
                        "description": "Name/path for the symbolic link"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Remove existing link if it exists",
                        "default": False
                    }
                },
                "required": ["target", "link_name"]
            }
        ),
        Tool(
            name="disk_usage",
            description="Show disk usage statistics (du, df commands).",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to analyze (default: current directory)",
                        "default": "."
                    },
                    "command": {
                        "type": "string",
                        "enum": ["du", "df"],
                        "description": "Command: 'du' (directory usage) or 'df' (filesystem usage)",
                        "default": "du"
                    },
                    "human_readable": {
                        "type": "boolean",
                        "description": "Show sizes in human-readable format",
                        "default": True
                    },
                    "summary": {
                        "type": "boolean",
                        "description": "Show only total (du command)",
                        "default": False
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="compare_files",
            description="Compare files (diff, cmp commands).",
            inputSchema={
                "type": "object",
                "properties": {
                    "file1": {
                        "type": "string",
                        "description": "First file path"
                    },
                    "file2": {
                        "type": "string",
                        "description": "Second file path"
                    },
                    "unified": {
                        "type": "boolean",
                        "description": "Use unified diff format",
                        "default": True
                    },
                    "ignore_whitespace": {
                        "type": "boolean",
                        "description": "Ignore whitespace differences",
                        "default": False
                    },
                    "context_lines": {
                        "type": "integer",
                        "description": "Number of context lines to show",
                        "default": 3
                    }
                },
                "required": ["file1", "file2"]
            }
        ),
    ]


async def handle_file_tools(name: str, arguments: dict[str, Any]) -> list[TextContent] | None:
    """Handle file tool execution."""
    handlers = {
        "read_file": read_file,
        "write_file": write_file,
        "delete_file": delete_file,
        "copy_file": copy_file,
        "move_file": move_file,
        "create_directory": create_directory,
        "change_permissions": change_permissions,
        "create_symlink": create_symlink,
        "disk_usage": disk_usage,
        "compare_files": compare_files,
    }
    
    handler = handlers.get(name)
    if handler:
        return await handler(arguments)
    return None


# ============================================================================
# File Operations Implementation
# ============================================================================

async def read_file(arguments: dict[str, Any]) -> list[TextContent]:
    """Read file contents using cat, head, or tail."""
    path = arguments.get("path")
    mode = arguments.get("mode", "cat")
    lines = arguments.get("lines", 10)
    follow = arguments.get("follow", False)
    
    if not path:
        raise ValueError("Path is required")
    
    logger.info(f"Reading file: {path} (mode: {mode})")
    
    if mode == "cat":
        command = f"cat {shlex.quote(path)}"
    elif mode == "head":
        command = f"head -n {lines} {shlex.quote(path)}"
    elif mode == "tail":
        if follow:
            command = f"timeout 5 tail -f -n {lines} {shlex.quote(path)}"
        else:
            command = f"tail -n {lines} {shlex.quote(path)}"
    else:
        raise ValueError(f"Unknown mode: {mode}")
    
    return await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )


async def write_file(arguments: dict[str, Any]) -> list[TextContent]:
    """Write content to a file."""
    path = arguments.get("path")
    content = arguments.get("content")
    append = arguments.get("append", False)
    create_dirs = arguments.get("create_dirs", False)
    
    if not path or content is None:
        raise ValueError("Path and content are required")
    
    logger.info(f"Writing to file: {path} (append: {append})")
    
    commands = []
    if create_dirs:
        dir_path = os.path.dirname(path)
        if dir_path:
            commands.append(f"mkdir -p {shlex.quote(dir_path)}")
    
    operator = ">>" if append else ">"
    commands.append(f"printf %s {shlex.quote(content)} {operator} {shlex.quote(path)}")
    
    command = " && ".join(commands)
    
    result = await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )
    
    if result and result[0].text.startswith("Exit Code: 0"):
        action = "Appended to" if append else "Written to"
        result[0].text += f"\n✓ {action} file successfully: {path}"
    
    return result


async def delete_file(arguments: dict[str, Any]) -> list[TextContent]:
    """Delete files or directories."""
    path = arguments.get("path")
    recursive = arguments.get("recursive", False)
    force = arguments.get("force", False)
    
    if not path:
        raise ValueError("Path is required")
    
    logger.info(f"Deleting: {path} (recursive: {recursive}, force: {force})")
    
    cmd_parts = ["rm"]
    if recursive:
        cmd_parts.append("-r")
    if force:
        cmd_parts.append("-f")
    cmd_parts.append(shlex.quote(path))
    
    command = " ".join(cmd_parts)
    
    result = await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )
    
    if result and result[0].text.startswith("Exit Code: 0"):
        result[0].text += f"\n✓ Deleted successfully: {path}"
    
    return result


async def copy_file(arguments: dict[str, Any]) -> list[TextContent]:
    """Copy files or directories."""
    source = arguments.get("source")
    destination = arguments.get("destination")
    recursive = arguments.get("recursive", False)
    preserve = arguments.get("preserve", True)
    
    if not source or not destination:
        raise ValueError("Source and destination are required")
    
    logger.info(f"Copying {source} to {destination}")
    
    cmd_parts = ["cp"]
    if recursive:
        cmd_parts.append("-r")
    if preserve:
        cmd_parts.append("-p")
    cmd_parts.append(shlex.quote(source))
    cmd_parts.append(shlex.quote(destination))
    
    command = " ".join(cmd_parts)
    
    result = await execute_shell_command(
        {"command": command, "timeout": 60},
        shell="bash"
    )
    
    if result and result[0].text.startswith("Exit Code: 0"):
        result[0].text += f"\n✓ Copied successfully: {source} → {destination}"
    
    return result


async def move_file(arguments: dict[str, Any]) -> list[TextContent]:
    """Move or rename files and directories."""
    source = arguments.get("source")
    destination = arguments.get("destination")
    force = arguments.get("force", False)
    
    if not source or not destination:
        raise ValueError("Source and destination are required")
    
    logger.info(f"Moving {source} to {destination}")
    
    cmd_parts = ["mv"]
    if force:
        cmd_parts.append("-f")
    cmd_parts.append(shlex.quote(source))
    cmd_parts.append(shlex.quote(destination))
    
    command = " ".join(cmd_parts)
    
    result = await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )
    
    if result and result[0].text.startswith("Exit Code: 0"):
        result[0].text += f"\n✓ Moved successfully: {source} → {destination}"
    
    return result


async def create_directory(arguments: dict[str, Any]) -> list[TextContent]:
    """Create directories."""
    path = arguments.get("path")
    parents = arguments.get("parents", True)
    mode = arguments.get("mode")
    
    if not path:
        raise ValueError("Path is required")
    
    logger.info(f"Creating directory: {path}")
    
    cmd_parts = ["mkdir"]
    if parents:
        cmd_parts.append("-p")
    if mode:
        cmd_parts.extend(["-m", mode])
    cmd_parts.append(shlex.quote(path))
    
    command = " ".join(cmd_parts)
    
    result = await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )
    
    if result and result[0].text.startswith("Exit Code: 0"):
        result[0].text += f"\n✓ Directory created: {path}"
    
    return result


async def change_permissions(arguments: dict[str, Any]) -> list[TextContent]:
    """Change file or directory permissions."""
    path = arguments.get("path")
    mode = arguments.get("mode")
    recursive = arguments.get("recursive", False)
    
    if not path or not mode:
        raise ValueError("Path and mode are required")
    
    logger.info(f"Changing permissions: {path} to {mode}")
    
    cmd_parts = ["chmod"]
    if recursive:
        cmd_parts.append("-R")
    cmd_parts.append(mode)
    cmd_parts.append(shlex.quote(path))
    
    command = " ".join(cmd_parts)
    
    result = await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )
    
    if result and result[0].text.startswith("Exit Code: 0"):
        result[0].text += f"\n✓ Permissions changed: {path} → {mode}"
    
    return result


async def create_symlink(arguments: dict[str, Any]) -> list[TextContent]:
    """Create symbolic links."""
    target = arguments.get("target")
    link_name = arguments.get("link_name")
    force = arguments.get("force", False)
    
    if not target or not link_name:
        raise ValueError("Target and link_name are required")
    
    logger.info(f"Creating symlink: {link_name} → {target}")
    
    cmd_parts = ["ln", "-s"]
    if force:
        cmd_parts.append("-f")
    cmd_parts.append(shlex.quote(target))
    cmd_parts.append(shlex.quote(link_name))
    
    command = " ".join(cmd_parts)
    
    result = await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )
    
    if result and result[0].text.startswith("Exit Code: 0"):
        result[0].text += f"\n✓ Symlink created: {link_name} → {target}"
    
    return result


async def disk_usage(arguments: dict[str, Any]) -> list[TextContent]:
    """Show disk usage statistics."""
    path = arguments.get("path", ".")
    command_type = arguments.get("command", "du")
    human_readable = arguments.get("human_readable", True)
    summary = arguments.get("summary", False)
    
    logger.info(f"Getting disk usage: {command_type} for {path}")
    
    if command_type == "du":
        cmd_parts = ["du"]
        if human_readable:
            cmd_parts.append("-h")
        if summary:
            cmd_parts.append("-s")
        else:
            cmd_parts.append("-a")
        cmd_parts.append(shlex.quote(path))
        command = " ".join(cmd_parts)
    else:  # df
        cmd_parts = ["df"]
        if human_readable:
            cmd_parts.append("-h")
        if path != ".":
            cmd_parts.append(shlex.quote(path))
        command = " ".join(cmd_parts)
    
    return await execute_shell_command(
        {"command": command, "timeout": 60},
        shell="bash"
    )


async def compare_files(arguments: dict[str, Any]) -> list[TextContent]:
    """Compare two files."""
    file1 = arguments.get("file1")
    file2 = arguments.get("file2")
    unified = arguments.get("unified", True)
    ignore_whitespace = arguments.get("ignore_whitespace", False)
    context_lines = arguments.get("context_lines", 3)
    
    if not file1 or not file2:
        raise ValueError("Both file1 and file2 are required")
    
    logger.info(f"Comparing files: {file1} vs {file2}")
    
    cmd_parts = ["diff"]
    if unified:
        cmd_parts.extend(["-u", f"-U{context_lines}"])
    if ignore_whitespace:
        cmd_parts.append("-w")
    cmd_parts.append(shlex.quote(file1))
    cmd_parts.append(shlex.quote(file2))
    
    command = " ".join(cmd_parts)
    
    result = await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )
    
    if result and result[0].text:
        if "Exit Code: 0" in result[0].text:
            result[0].text += "\n✓ Files are identical"
        elif "Exit Code: 1" in result[0].text:
            result[0].text += "\n⚠ Files differ (see diff above)"
    
    return result
