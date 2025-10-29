"""
Process and system tools: ps, kill, top, uptime, free, etc.
"""
import shlex
from typing import Any
from mcp.types import Tool, TextContent
from .shell_tools import execute_shell_command
import logging

logger = logging.getLogger("mcp-system-tools")


def register_system_tools() -> list[Tool]:
    """Register all process and system tools."""
    return [
        Tool(
            name="list_processes",
            description="List running processes (ps command) with various filtering options.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_type": {
                        "type": "string",
                        "enum": ["all", "user", "tree", "top_cpu", "top_mem"],
                        "description": "'all' (all processes), 'user' (current user), 'tree' (process tree), 'top_cpu' (highest CPU), 'top_mem' (highest memory)",
                        "default": "user"
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["cpu", "mem", "pid", "time"],
                        "description": "Sort processes by field",
                        "default": "cpu"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Limit number of results",
                        "default": 20
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="kill_process",
            description="Kill a process by PID or name. Use with caution.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pid": {
                        "type": "integer",
                        "description": "Process ID to kill"
                    },
                    "name": {
                        "type": "string",
                        "description": "Process name to kill (kills all matching)"
                    },
                    "signal": {
                        "type": "string",
                        "enum": ["TERM", "KILL", "HUP", "INT", "QUIT"],
                        "description": "Signal to send (default: TERM)",
                        "default": "TERM"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force kill (SIGKILL)",
                        "default": False
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="system_info",
            description="Get system information (uname, hostname, kernel, etc.).",
            inputSchema={
                "type": "object",
                "properties": {
                    "info_type": {
                        "type": "string",
                        "enum": ["basic", "kernel", "hardware", "os", "all"],
                        "description": "Type of system info to retrieve",
                        "default": "all"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="system_resources",
            description="Show system resource usage (CPU, memory, disk, uptime).",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "enum": ["cpu", "memory", "disk", "uptime", "all"],
                        "description": "Resource type to check",
                        "default": "all"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="monitor_system",
            description="Monitor system resources in real-time (top/htop snapshot).",
            inputSchema={
                "type": "object",
                "properties": {
                    "duration": {
                        "type": "integer",
                        "description": "Monitoring duration in seconds",
                        "default": 5
                    },
                    "use_htop": {
                        "type": "boolean",
                        "description": "Use htop if available",
                        "default": False
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="service_control",
            description="Control system services (systemctl).",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service name"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["status", "start", "stop", "restart", "enable", "disable", "list"],
                        "description": "Action to perform",
                        "default": "status"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="environment_info",
            description="Get environment variables and shell information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "show_all": {
                        "type": "boolean",
                        "description": "Show all environment variables",
                        "default": False
                    },
                    "variable": {
                        "type": "string",
                        "description": "Specific variable to query"
                    }
                },
                "required": []
            }
        ),
    ]


async def handle_system_tools(name: str, arguments: dict[str, Any]) -> list[TextContent] | None:
    """Handle system tool execution."""
    handlers = {
        "list_processes": list_processes,
        "kill_process": kill_process,
        "system_info": system_info,
        "system_resources": system_resources,
        "monitor_system": monitor_system,
        "service_control": service_control,
        "environment_info": environment_info,
    }
    
    handler = handlers.get(name)
    if handler:
        return await handler(arguments)
    return None


# ============================================================================
# System Tools Implementation
# ============================================================================

async def list_processes(arguments: dict[str, Any]) -> list[TextContent]:
    """List running processes."""
    filter_type = arguments.get("filter_type", "user")
    sort_by = arguments.get("sort_by", "cpu")
    limit = arguments.get("limit", 20)
    
    logger.info(f"Listing processes: {filter_type}")
    
    if filter_type == "all":
        command = f"ps aux --sort=-%{sort_by} | head -n {limit + 1}"
    elif filter_type == "user":
        command = f"ps u --sort=-%{sort_by} | head -n {limit + 1}"
    elif filter_type == "tree":
        command = "ps auxf | head -n 50"
    elif filter_type == "top_cpu":
        command = f"ps aux --sort=-%cpu | head -n {limit + 1}"
    elif filter_type == "top_mem":
        command = f"ps aux --sort=-%mem | head -n {limit + 1}"
    else:
        raise ValueError(f"Unknown filter type: {filter_type}")
    
    return await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )


async def kill_process(arguments: dict[str, Any]) -> list[TextContent]:
    """Kill a process."""
    pid = arguments.get("pid")
    name = arguments.get("name")
    signal = arguments.get("signal", "TERM")
    force = arguments.get("force", False)
    
    if not pid and not name:
        raise ValueError("Either pid or name is required")
    
    if force:
        signal = "KILL"
    
    logger.info(f"Killing process (signal: {signal})")
    
    if pid:
        command = f"kill -{signal} {pid}"
    else:
        command = f"pkill -{signal} {shlex.quote(name)}"
    
    result = await execute_shell_command(
        {"command": command, "timeout": 10},
        shell="bash"
    )
    
    if result and result[0].text.startswith("Exit Code: 0"):
        target = f"PID {pid}" if pid else f"process '{name}'"
        result[0].text += f"\n✓ Sent {signal} signal to {target}"
    
    return result


async def system_info(arguments: dict[str, Any]) -> list[TextContent]:
    """Get system information."""
    info_type = arguments.get("info_type", "all")
    
    logger.info(f"Getting system info: {info_type}")
    
    commands = []
    
    if info_type in ["basic", "all"]:
        commands.append("echo '=== Basic Info ===' && hostname && uname -a")
    
    if info_type in ["kernel", "all"]:
        commands.append("echo '=== Kernel ===' && uname -r && cat /proc/version 2>/dev/null || true")
    
    if info_type in ["hardware", "all"]:
        commands.append("echo '=== Hardware ===' && lscpu 2>/dev/null | head -20 || true")
        commands.append("echo '=== Memory ===' && free -h")
    
    if info_type in ["os", "all"]:
        commands.append("echo '=== OS Info ===' && cat /etc/os-release 2>/dev/null || cat /etc/*release 2>/dev/null | head -10 || true")
    
    command = " && ".join(commands)
    
    return await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )


async def system_resources(arguments: dict[str, Any]) -> list[TextContent]:
    """Show system resources."""
    resource = arguments.get("resource", "all")
    
    logger.info(f"Checking system resources: {resource}")
    
    commands = []
    
    if resource in ["cpu", "all"]:
        commands.append("echo '=== CPU Usage ===' && top -bn1 | grep 'Cpu(s)' || mpstat 1 1 2>/dev/null || true")
    
    if resource in ["memory", "all"]:
        commands.append("echo '=== Memory Usage ===' && free -h")
    
    if resource in ["disk", "all"]:
        commands.append("echo '=== Disk Usage ===' && df -h | head -20")
    
    if resource in ["uptime", "all"]:
        commands.append("echo '=== Uptime & Load ===' && uptime")
        commands.append("echo '=== Load Average ===' && cat /proc/loadavg 2>/dev/null || true")
    
    command = " && ".join(commands)
    
    return await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )


async def monitor_system(arguments: dict[str, Any]) -> list[TextContent]:
    """Monitor system in real-time."""
    duration = arguments.get("duration", 5)
    use_htop = arguments.get("use_htop", False)
    
    logger.info(f"Monitoring system for {duration} seconds")
    
    if use_htop:
        command = f"timeout {duration} htop --no-mouse 2>/dev/null || timeout {duration} top -b -n {duration}"
    else:
        command = f"top -b -n {duration} -d 1"
    
    return await execute_shell_command(
        {"command": command, "timeout": duration + 5},
        shell="bash"
    )


async def service_control(arguments: dict[str, Any]) -> list[TextContent]:
    """Control system services."""
    service = arguments.get("service")
    action = arguments.get("action", "status")
    
    logger.info(f"Service control: {action} {service if service else 'all'}")
    
    if action == "list":
        command = "systemctl list-units --type=service --all | head -50"
    else:
        if not service:
            raise ValueError("Service name is required for this action")
        command = f"systemctl {action} {shlex.quote(service)}"
    
    result = await execute_shell_command(
        {"command": command, "timeout": 60},
        shell="bash"
    )
    
    if result and result[0].text.startswith("Exit Code: 0") and action != "status":
        result[0].text += f"\n✓ Service {action} completed: {service}"
    
    return result


async def environment_info(arguments: dict[str, Any]) -> list[TextContent]:
    """Get environment information."""
    show_all = arguments.get("show_all", False)
    variable = arguments.get("variable")
    
    logger.info("Getting environment info")
    
    if variable:
        command = f"echo ${shlex.quote(variable)}"
    elif show_all:
        command = "env | sort"
    else:
        command = "echo '=== Shell ===' && echo $SHELL && echo '=== User ===' && whoami && echo '=== Path ===' && echo $PATH && echo '=== Home ===' && echo $HOME"
    
    return await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )
