"""
Shell execution tools: bash, zsh, and Python.
"""
import asyncio
import os
import tempfile
import shlex
from pathlib import Path
from typing import Any
from mcp.types import Tool, TextContent
import logging

logger = logging.getLogger("mcp-shell-tools")


def register_shell_tools() -> list[Tool]:
    """Register all shell execution tools."""
    return [
        Tool(
            name="execute_bash",
            description="Execute a bash command in the WSL environment. Returns stdout, stderr, and exit code. Use with caution as commands are executed with current user permissions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Optional working directory for command execution (defaults to home directory)"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Command timeout in seconds (default: 30)",
                        "default": 30
                    }
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="execute_zsh",
            description="Execute a zsh command in the WSL environment. Returns stdout, stderr, and exit code. Useful for zsh-specific features and plugins. Use with caution as commands are executed with current user permissions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The zsh command to execute"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Optional working directory for command execution (defaults to home directory)"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Command timeout in seconds (default: 30)",
                        "default": 30
                    },
                    "use_login_shell": {
                        "type": "boolean",
                        "description": "If true, executes as a login shell (loads ~/.zshrc). Default: false",
                        "default": False
                    }
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="execute_python",
            description="Execute Python3 code with optional virtual environment support. Can run inline code or scripts, install packages, and manage virtual environments. Returns stdout, stderr, and exit code.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute (inline code or script content)"
                    },
                    "venv_path": {
                        "type": "string",
                        "description": "Path to virtual environment. If provided and doesn't exist, it will be created. If not provided, uses system Python."
                    },
                    "packages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of packages to install via pip before executing code (e.g., ['requests', 'numpy'])"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory for code execution (defaults to temp directory)"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Execution timeout in seconds (default: 60)",
                        "default": 60
                    },
                    "script_mode": {
                        "type": "boolean",
                        "description": "If true, saves code to a temporary file and executes it. If false, uses python -c (default: true for multi-line code)",
                        "default": True
                    }
                },
                "required": ["code"]
            }
        )
    ]


async def handle_shell_tools(name: str, arguments: dict[str, Any]) -> list[TextContent] | None:
    """Handle shell tool execution."""
    if name == "execute_bash":
        return await execute_bash_command(arguments)
    elif name == "execute_zsh":
        return await execute_zsh_command(arguments)
    elif name == "execute_python":
        return await execute_python_code(arguments)
    return None


# ============================================================================
# Shell Execution Implementation
# ============================================================================

async def execute_shell_command(arguments: dict[str, Any], shell: str = "bash") -> list[TextContent]:
    """Execute a shell command (bash or zsh)."""
    command = arguments.get("command")
    working_dir = arguments.get("working_directory")
    timeout = arguments.get("timeout", 30)
    use_login_shell = arguments.get("use_login_shell", False)
    
    if not command:
        raise ValueError("Command is required")
    
    logger.info(f"Executing {shell} command: {command}")
    
    try:
        # Determine shell executable
        if shell == "zsh":
            if use_login_shell:
                shell_cmd = f"zsh -l -c {shlex.quote(command)}"
            else:
                shell_cmd = f"zsh -c {shlex.quote(command)}"
        else:  # bash
            shell_cmd = command
        
        # Execute command
        process = await asyncio.create_subprocess_shell(
            shell_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_dir,
            executable="/bin/zsh" if shell == "zsh" else "/bin/bash"
        )
        
        # Wait for completion with timeout
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )
        
        # Decode output
        stdout_text = stdout.decode('utf-8', errors='replace')
        stderr_text = stderr.decode('utf-8', errors='replace')
        exit_code = process.returncode
        
        # Format response
        response = f"Exit Code: {exit_code}\n\n"
        
        if stdout_text:
            response += f"STDOUT:\n{stdout_text}\n"
        
        if stderr_text:
            response += f"STDERR:\n{stderr_text}\n"
        
        if exit_code == 0:
            logger.info(f"{shell.upper()} command executed successfully")
        else:
            logger.warning(f"{shell.upper()} command failed with exit code {exit_code}")
        
        return [TextContent(type="text", text=response)]
        
    except asyncio.TimeoutError:
        logger.error(f"Command timed out after {timeout} seconds")
        return [TextContent(
            type="text",
            text=f"Error: Command timed out after {timeout} seconds"
        )]
    
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Error executing command: {str(e)}"
        )]


async def execute_bash_command(arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a bash command."""
    return await execute_shell_command(arguments, shell="bash")


async def execute_zsh_command(arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a zsh command."""
    return await execute_shell_command(arguments, shell="zsh")


# ============================================================================
# Python Execution Implementation
# ============================================================================

async def ensure_venv(venv_path: str) -> tuple[bool, str]:
    """Ensure virtual environment exists, create if it doesn't."""
    venv_path = Path(venv_path).expanduser()
    
    if venv_path.exists():
        python_bin = venv_path / "bin" / "python3"
        if python_bin.exists():
            logger.info(f"Using existing venv at {venv_path}")
            return True, f"Using existing virtual environment at {venv_path}"
    
    logger.info(f"Creating new venv at {venv_path}")
    try:
        process = await asyncio.create_subprocess_exec(
            "python3", "-m", "venv", str(venv_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
        
        if process.returncode == 0:
            logger.info(f"Successfully created venv at {venv_path}")
            return True, f"Created new virtual environment at {venv_path}"
        else:
            error_msg = stderr.decode('utf-8', errors='replace')
            logger.error(f"Failed to create venv: {error_msg}")
            return False, f"Failed to create venv: {error_msg}"
            
    except Exception as e:
        logger.error(f"Error creating venv: {str(e)}")
        return False, f"Error creating venv: {str(e)}"


async def install_packages(venv_path: str | None, packages: list[str]) -> tuple[bool, str]:
    """Install packages using pip."""
    if not packages:
        return True, ""
    
    if venv_path:
        venv_path = Path(venv_path).expanduser()
        pip_cmd = str(venv_path / "bin" / "pip")
    else:
        pip_cmd = "pip3"
    
    logger.info(f"Installing packages: {', '.join(packages)}")
    
    try:
        process = await asyncio.create_subprocess_exec(
            pip_cmd, "install", *packages,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
        
        stdout_text = stdout.decode('utf-8', errors='replace')
        stderr_text = stderr.decode('utf-8', errors='replace')
        
        if process.returncode == 0:
            logger.info(f"Successfully installed packages")
            return True, f"Installed packages: {', '.join(packages)}\n{stdout_text}"
        else:
            logger.error(f"Failed to install packages: {stderr_text}")
            return False, f"Failed to install packages:\n{stderr_text}"
            
    except Exception as e:
        logger.error(f"Error installing packages: {str(e)}")
        return False, f"Error installing packages: {str(e)}"


async def execute_python_code(arguments: dict[str, Any]) -> list[TextContent]:
    """Execute Python code with optional venv support."""
    code = arguments.get("code")
    venv_path = arguments.get("venv_path")
    packages = arguments.get("packages", [])
    working_dir = arguments.get("working_directory")
    timeout = arguments.get("timeout", 60)
    script_mode = arguments.get("script_mode", True)
    
    if not code:
        raise ValueError("Code is required")
    
    logger.info(f"Executing Python code (venv: {venv_path or 'system'})")
    
    response_parts = []
    
    try:
        # Setup venv if requested
        if venv_path:
            success, msg = await ensure_venv(venv_path)
            response_parts.append(msg)
            if not success:
                return [TextContent(type="text", text="\n".join(response_parts))]
            
            python_cmd = str(Path(venv_path).expanduser() / "bin" / "python3")
        else:
            python_cmd = "python3"
        
        # Install packages if requested
        if packages:
            success, msg = await install_packages(venv_path, packages)
            response_parts.append(msg)
            if not success:
                return [TextContent(type="text", text="\n".join(response_parts))]
        
        # Execute code
        if script_mode or "\n" in code:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                script_path = f.name
            
            try:
                process = await asyncio.create_subprocess_exec(
                    python_cmd, script_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=working_dir
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            finally:
                try:
                    os.unlink(script_path)
                except Exception:
                    pass
        else:
            process = await asyncio.create_subprocess_exec(
                python_cmd, "-c", code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
        
        # Decode output
        stdout_text = stdout.decode('utf-8', errors='replace')
        stderr_text = stderr.decode('utf-8', errors='replace')
        exit_code = process.returncode
        
        # Format response
        response_parts.append(f"\n{'='*50}")
        response_parts.append(f"Python Execution Result")
        response_parts.append(f"{'='*50}")
        response_parts.append(f"Exit Code: {exit_code}\n")
        
        if stdout_text:
            response_parts.append(f"STDOUT:\n{stdout_text}")
        
        if stderr_text:
            response_parts.append(f"STDERR:\n{stderr_text}")
        
        if exit_code == 0:
            logger.info(f"Python code executed successfully")
        else:
            logger.warning(f"Python code failed with exit code {exit_code}")
        
        return [TextContent(type="text", text="\n".join(response_parts))]
        
    except asyncio.TimeoutError:
        logger.error(f"Python execution timed out after {timeout} seconds")
        response_parts.append(f"\nError: Execution timed out after {timeout} seconds")
        return [TextContent(type="text", text="\n".join(response_parts))]
    
    except Exception as e:
        logger.error(f"Error executing Python code: {str(e)}")
        response_parts.append(f"\nError executing Python code: {str(e)}")
        return [TextContent(type="text", text="\n".join(response_parts))]
