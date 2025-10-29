"""
Archive tools: tar, zip, unzip, gzip, etc.
"""
import shlex
from typing import Any
from mcp.types import Tool, TextContent
from .shell_tools import execute_shell_command
import logging

logger = logging.getLogger("mcp-archive-tools")


def register_archive_tools() -> list[Tool]:
    """Register all archive tools."""
    return [
        Tool(
            name="create_archive",
            description="Create archive files (tar, zip, tar.gz, tar.bz2, tar.xz).",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source file(s) or directory to archive"
                    },
                    "output": {
                        "type": "string",
                        "description": "Output archive filename"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["tar", "tar.gz", "tar.bz2", "tar.xz", "zip"],
                        "description": "Archive format",
                        "default": "tar.gz"
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Verbose output",
                        "default": False
                    },
                    "exclude": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Patterns to exclude from archive"
                    }
                },
                "required": ["source", "output"]
            }
        ),
        Tool(
            name="extract_archive",
            description="Extract archive files (tar, zip, gz, bz2, xz).",
            inputSchema={
                "type": "object",
                "properties": {
                    "archive": {
                        "type": "string",
                        "description": "Archive file to extract"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination directory (default: current directory)",
                        "default": "."
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Verbose output",
                        "default": False
                    },
                    "list_only": {
                        "type": "boolean",
                        "description": "List contents without extracting",
                        "default": False
                    }
                },
                "required": ["archive"]
            }
        ),
        Tool(
            name="list_archive",
            description="List contents of an archive file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "archive": {
                        "type": "string",
                        "description": "Archive file to list"
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Show detailed information",
                        "default": False
                    }
                },
                "required": ["archive"]
            }
        ),
        Tool(
            name="compress_file",
            description="Compress a file using gzip, bzip2, or xz.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "File to compress"
                    },
                    "algorithm": {
                        "type": "string",
                        "enum": ["gzip", "bzip2", "xz"],
                        "description": "Compression algorithm",
                        "default": "gzip"
                    },
                    "keep_original": {
                        "type": "boolean",
                        "description": "Keep original file after compression",
                        "default": True
                    },
                    "level": {
                        "type": "integer",
                        "description": "Compression level (1-9, 9=best)",
                        "default": 6
                    }
                },
                "required": ["file"]
            }
        ),
        Tool(
            name="decompress_file",
            description="Decompress a file (gunzip, bunzip2, unxz).",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "File to decompress"
                    },
                    "keep_original": {
                        "type": "boolean",
                        "description": "Keep original compressed file",
                        "default": False
                    }
                },
                "required": ["file"]
            }
        ),
    ]


async def handle_archive_tools(name: str, arguments: dict[str, Any]) -> list[TextContent] | None:
    """Handle archive tool execution."""
    handlers = {
        "create_archive": create_archive,
        "extract_archive": extract_archive,
        "list_archive": list_archive,
        "compress_file": compress_file,
        "decompress_file": decompress_file,
    }
    
    handler = handlers.get(name)
    if handler:
        return await handler(arguments)
    return None


# ============================================================================
# Archive Tools Implementation
# ============================================================================

async def create_archive(arguments: dict[str, Any]) -> list[TextContent]:
    """Create an archive."""
    source = arguments.get("source")
    output = arguments.get("output")
    format_type = arguments.get("format", "tar.gz")
    verbose = arguments.get("verbose", False)
    exclude = arguments.get("exclude", [])
    
    if not source or not output:
        raise ValueError("Source and output are required")
    
    logger.info(f"Creating {format_type} archive: {output}")
    
    if format_type == "zip":
        cmd_parts = ["zip", "-r"]
        if not verbose:
            cmd_parts.append("-q")
        cmd_parts.append(shlex.quote(output))
        cmd_parts.append(shlex.quote(source))
        for pattern in exclude:
            cmd_parts.extend(["-x", shlex.quote(pattern)])
    else:
        cmd_parts = ["tar"]
        
        if format_type == "tar":
            cmd_parts.append("-cf")
        elif format_type == "tar.gz":
            cmd_parts.append("-czf")
        elif format_type == "tar.bz2":
            cmd_parts.append("-cjf")
        elif format_type == "tar.xz":
            cmd_parts.append("-cJf")
        else:
            raise ValueError(f"Unknown format: {format_type}")
        
        if verbose:
            cmd_parts.append("-v")
        
        cmd_parts.append(shlex.quote(output))
        
        for pattern in exclude:
            cmd_parts.extend(["--exclude", shlex.quote(pattern)])
        
        cmd_parts.append(shlex.quote(source))
    
    command = " ".join(cmd_parts)
    
    result = await execute_shell_command(
        {"command": command, "timeout": 300},
        shell="bash"
    )
    
    if result and result[0].text.startswith("Exit Code: 0"):
        result[0].text += f"\n✓ Archive created: {output}"
    
    return result


async def extract_archive(arguments: dict[str, Any]) -> list[TextContent]:
    """Extract an archive."""
    archive = arguments.get("archive")
    destination = arguments.get("destination", ".")
    verbose = arguments.get("verbose", False)
    list_only = arguments.get("list_only", False)
    
    if not archive:
        raise ValueError("Archive is required")
    
    logger.info(f"Extracting archive: {archive}")
    
    if archive.endswith(".zip"):
        if list_only:
            command = f"unzip -l {shlex.quote(archive)}"
        else:
            cmd_parts = ["unzip"]
            if not verbose:
                cmd_parts.append("-q")
            cmd_parts.append(shlex.quote(archive))
            cmd_parts.extend(["-d", shlex.quote(destination)])
            command = " ".join(cmd_parts)
    elif any(archive.endswith(ext) for ext in [".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tar.xz"]):
        cmd_parts = ["tar"]
        
        if list_only:
            cmd_parts.append("-tf")
        else:
            cmd_parts.append("-xf")
        
        if verbose and not list_only:
            cmd_parts.append("-v")
        
        cmd_parts.append(shlex.quote(archive))
        
        if not list_only:
            cmd_parts.extend(["-C", shlex.quote(destination)])
        
        command = " ".join(cmd_parts)
    elif archive.endswith(".gz"):
        command = f"gunzip -c {shlex.quote(archive)} > {shlex.quote(destination)}/$(basename {shlex.quote(archive)} .gz)"
    elif archive.endswith(".bz2"):
        command = f"bunzip2 -c {shlex.quote(archive)} > {shlex.quote(destination)}/$(basename {shlex.quote(archive)} .bz2)"
    elif archive.endswith(".xz"):
        command = f"unxz -c {shlex.quote(archive)} > {shlex.quote(destination)}/$(basename {shlex.quote(archive)} .xz)"
    else:
        raise ValueError("Unsupported archive format")
    
    result = await execute_shell_command(
        {"command": command, "timeout": 300},
        shell="bash"
    )
    
    if result and result[0].text.startswith("Exit Code: 0") and not list_only:
        result[0].text += f"\n✓ Archive extracted to: {destination}"
    
    return result


async def list_archive(arguments: dict[str, Any]) -> list[TextContent]:
    """List archive contents."""
    archive = arguments.get("archive")
    verbose = arguments.get("verbose", False)
    
    if not archive:
        raise ValueError("Archive is required")
    
    logger.info(f"Listing archive: {archive}")
    
    if archive.endswith(".zip"):
        command = f"unzip -{'l' if verbose else 'Z'} {shlex.quote(archive)}"
    elif any(archive.endswith(ext) for ext in [".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tar.xz"]):
        cmd_parts = ["tar", "-tf"]
        if verbose:
            cmd_parts.append("-v")
        cmd_parts.append(shlex.quote(archive))
        command = " ".join(cmd_parts)
    else:
        raise ValueError("Unsupported archive format")
    
    return await execute_shell_command(
        {"command": command, "timeout": 60},
        shell="bash"
    )


async def compress_file(arguments: dict[str, Any]) -> list[TextContent]:
    """Compress a file."""
    file = arguments.get("file")
    algorithm = arguments.get("algorithm", "gzip")
    keep_original = arguments.get("keep_original", True)
    level = arguments.get("level", 6)
    
    if not file:
        raise ValueError("File is required")
    
    logger.info(f"Compressing file: {file} with {algorithm}")
    
    cmd_parts = []
    
    if algorithm == "gzip":
        cmd_parts = ["gzip", f"-{level}"]
        if keep_original:
            cmd_parts.append("-c")
            cmd_parts.append(shlex.quote(file))
            cmd_parts.append(">")
            cmd_parts.append(f"{shlex.quote(file)}.gz")
        else:
            cmd_parts.append(shlex.quote(file))
    elif algorithm == "bzip2":
        cmd_parts = ["bzip2", f"-{level}"]
        if keep_original:
            cmd_parts.append("-c")
            cmd_parts.append(shlex.quote(file))
            cmd_parts.append(">")
            cmd_parts.append(f"{shlex.quote(file)}.bz2")
        else:
            cmd_parts.append(shlex.quote(file))
    elif algorithm == "xz":
        cmd_parts = ["xz", f"-{level}"]
        if keep_original:
            cmd_parts.append("-c")
            cmd_parts.append(shlex.quote(file))
            cmd_parts.append(">")
            cmd_parts.append(f"{shlex.quote(file)}.xz")
        else:
            cmd_parts.append(shlex.quote(file))
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    command = " ".join(cmd_parts)
    
    result = await execute_shell_command(
        {"command": command, "timeout": 300},
        shell="bash"
    )
    
    if result and result[0].text.startswith("Exit Code: 0"):
        result[0].text += f"\n✓ File compressed with {algorithm}"
    
    return result


async def decompress_file(arguments: dict[str, Any]) -> list[TextContent]:
    """Decompress a file."""
    file = arguments.get("file")
    keep_original = arguments.get("keep_original", False)
    
    if not file:
        raise ValueError("File is required")
    
    logger.info(f"Decompressing file: {file}")
    
    if file.endswith(".gz"):
        cmd = "gunzip"
    elif file.endswith(".bz2"):
        cmd = "bunzip2"
    elif file.endswith(".xz"):
        cmd = "unxz"
    else:
        raise ValueError("Unsupported compressed file format")
    
    cmd_parts = [cmd]
    if keep_original:
        cmd_parts.append("-k")
    cmd_parts.append(shlex.quote(file))
    
    command = " ".join(cmd_parts)
    
    result = await execute_shell_command(
        {"command": command, "timeout": 300},
        shell="bash"
    )
    
    if result and result[0].text.startswith("Exit Code: 0"):
        result[0].text += f"\n✓ File decompressed"
    
    return result
