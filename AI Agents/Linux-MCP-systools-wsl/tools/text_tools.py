"""
Text processing tools: grep, sed, awk, cut, sort, etc.
"""
import shlex
from typing import Any
from mcp.types import Tool, TextContent
from .shell_tools import execute_shell_command
import logging

logger = logging.getLogger("mcp-text-tools")


def register_text_tools() -> list[Tool]:
    """Register all text processing tools."""
    return [
        Tool(
            name="grep_search",
            description="Search for patterns in files (grep command). Supports regular expressions and various search options.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Search pattern (supports regular expressions)"
                    },
                    "path": {
                        "type": "string",
                        "description": "File or directory to search in"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Search recursively in directories",
                        "default": False
                    },
                    "ignore_case": {
                        "type": "boolean",
                        "description": "Case-insensitive search",
                        "default": False
                    },
                    "line_numbers": {
                        "type": "boolean",
                        "description": "Show line numbers in output",
                        "default": True
                    },
                    "count_only": {
                        "type": "boolean",
                        "description": "Only show count of matching lines",
                        "default": False
                    },
                    "invert_match": {
                        "type": "boolean",
                        "description": "Select non-matching lines",
                        "default": False
                    },
                    "context_lines": {
                        "type": "integer",
                        "description": "Number of context lines to show around matches"
                    }
                },
                "required": ["pattern", "path"]
            }
        ),
        Tool(
            name="text_transform",
            description="Transform text using sed, awk, cut, or tr commands. Supports pattern replacement, field extraction, and character translation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Input file path (or use input_text for string input)"
                    },
                    "input_text": {
                        "type": "string",
                        "description": "Direct text input (alternative to input_path)"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["sed", "awk", "cut", "tr"],
                        "description": "Text processing operation to perform"
                    },
                    "sed_pattern": {
                        "type": "string",
                        "description": "Sed pattern (e.g., 's/old/new/g' for replacement)"
                    },
                    "awk_script": {
                        "type": "string",
                        "description": "Awk script or pattern (e.g., '{print $1}' to print first field)"
                    },
                    "cut_fields": {
                        "type": "string",
                        "description": "Fields to extract (e.g., '1,3' or '1-5')"
                    },
                    "cut_delimiter": {
                        "type": "string",
                        "description": "Field delimiter for cut (default: tab)",
                        "default": "\t"
                    },
                    "tr_from": {
                        "type": "string",
                        "description": "Characters to translate from"
                    },
                    "tr_to": {
                        "type": "string",
                        "description": "Characters to translate to"
                    }
                },
                "required": ["operation"]
            }
        ),
        Tool(
            name="sort_text",
            description="Sort lines of text files. Supports various sorting options including numeric, reverse, and unique.",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Input file path (or use input_text)"
                    },
                    "input_text": {
                        "type": "string",
                        "description": "Direct text input"
                    },
                    "numeric": {
                        "type": "boolean",
                        "description": "Sort numerically",
                        "default": False
                    },
                    "reverse": {
                        "type": "boolean",
                        "description": "Sort in reverse order",
                        "default": False
                    },
                    "unique": {
                        "type": "boolean",
                        "description": "Remove duplicate lines",
                        "default": False
                    },
                    "ignore_case": {
                        "type": "boolean",
                        "description": "Ignore case when sorting",
                        "default": False
                    },
                    "field": {
                        "type": "integer",
                        "description": "Sort by specific field number (space-delimited)"
                    }
                },
                "required": []
            }
        ),
    ]


async def handle_text_tools(name: str, arguments: dict[str, Any]) -> list[TextContent] | None:
    """Handle text processing tool execution."""
    handlers = {
        "grep_search": grep_search,
        "text_transform": text_transform,
        "sort_text": sort_text,
    }
    
    handler = handlers.get(name)
    if handler:
        return await handler(arguments)
    return None


# ============================================================================
# Text Processing Tools Implementation
# ============================================================================

async def grep_search(arguments: dict[str, Any]) -> list[TextContent]:
    """Search for patterns in files using grep."""
    pattern = arguments.get("pattern")
    path = arguments.get("path")
    recursive = arguments.get("recursive", False)
    ignore_case = arguments.get("ignore_case", False)
    line_numbers = arguments.get("line_numbers", True)
    count_only = arguments.get("count_only", False)
    invert_match = arguments.get("invert_match", False)
    context_lines = arguments.get("context_lines")
    
    if not pattern or not path:
        raise ValueError("Pattern and path are required")
    
    logger.info(f"Searching for pattern '{pattern}' in {path}")
    
    cmd_parts = ["grep"]
    if recursive:
        cmd_parts.append("-r")
    if ignore_case:
        cmd_parts.append("-i")
    if line_numbers and not count_only:
        cmd_parts.append("-n")
    if count_only:
        cmd_parts.append("-c")
    if invert_match:
        cmd_parts.append("-v")
    if context_lines is not None:
        cmd_parts.extend(["-C", str(context_lines)])
    
    cmd_parts.append(shlex.quote(pattern))
    cmd_parts.append(shlex.quote(path))
    
    command = " ".join(cmd_parts)
    
    return await execute_shell_command(
        {"command": command, "timeout": 60},
        shell="bash"
    )


async def text_transform(arguments: dict[str, Any]) -> list[TextContent]:
    """Transform text using sed, awk, cut, or tr."""
    input_path = arguments.get("input_path")
    input_text = arguments.get("input_text")
    operation = arguments.get("operation")
    
    if not operation:
        raise ValueError("Operation is required")
    
    if not input_path and not input_text:
        raise ValueError("Either input_path or input_text is required")
    
    logger.info(f"Performing {operation} operation")
    
    # Build command based on operation
    if operation == "sed":
        sed_pattern = arguments.get("sed_pattern")
        if not sed_pattern:
            raise ValueError("sed_pattern is required for sed operation")
        
        if input_text:
            command = f"echo {shlex.quote(input_text)} | sed {shlex.quote(sed_pattern)}"
        else:
            command = f"sed {shlex.quote(sed_pattern)} {shlex.quote(input_path)}"
    
    elif operation == "awk":
        awk_script = arguments.get("awk_script")
        if not awk_script:
            raise ValueError("awk_script is required for awk operation")
        
        if input_text:
            command = f"echo {shlex.quote(input_text)} | awk {shlex.quote(awk_script)}"
        else:
            command = f"awk {shlex.quote(awk_script)} {shlex.quote(input_path)}"
    
    elif operation == "cut":
        cut_fields = arguments.get("cut_fields")
        cut_delimiter = arguments.get("cut_delimiter", "\t")
        
        if not cut_fields:
            raise ValueError("cut_fields is required for cut operation")
        
        cmd_parts = ["cut", "-f", cut_fields]
        if cut_delimiter != "\t":
            cmd_parts.extend(["-d", shlex.quote(cut_delimiter)])
        
        if input_text:
            command = f"echo {shlex.quote(input_text)} | {' '.join(cmd_parts)}"
        else:
            command = f"{' '.join(cmd_parts)} {shlex.quote(input_path)}"
    
    elif operation == "tr":
        tr_from = arguments.get("tr_from")
        tr_to = arguments.get("tr_to")
        
        if not tr_from or not tr_to:
            raise ValueError("tr_from and tr_to are required for tr operation")
        
        if input_text:
            command = f"echo {shlex.quote(input_text)} | tr {shlex.quote(tr_from)} {shlex.quote(tr_to)}"
        else:
            command = f"tr {shlex.quote(tr_from)} {shlex.quote(tr_to)} < {shlex.quote(input_path)}"
    
    else:
        raise ValueError(f"Unknown operation: {operation}")
    
    return await execute_shell_command(
        {"command": command, "timeout": 60},
        shell="bash"
    )


async def sort_text(arguments: dict[str, Any]) -> list[TextContent]:
    """Sort lines of text."""
    input_path = arguments.get("input_path")
    input_text = arguments.get("input_text")
    numeric = arguments.get("numeric", False)
    reverse = arguments.get("reverse", False)
    unique = arguments.get("unique", False)
    ignore_case = arguments.get("ignore_case", False)
    field = arguments.get("field")
    
    if not input_path and not input_text:
        raise ValueError("Either input_path or input_text is required")
    
    logger.info("Sorting text")
    
    cmd_parts = ["sort"]
    if numeric:
        cmd_parts.append("-n")
    if reverse:
        cmd_parts.append("-r")
    if unique:
        cmd_parts.append("-u")
    if ignore_case:
        cmd_parts.append("-f")
    if field is not None:
        cmd_parts.extend(["-k", str(field)])
    
    if input_text:
        command = f"echo {shlex.quote(input_text)} | {' '.join(cmd_parts)}"
    else:
        cmd_parts.append(shlex.quote(input_path))
        command = " ".join(cmd_parts)
    
    return await execute_shell_command(
        {"command": command, "timeout": 60},
        shell="bash"
    )
