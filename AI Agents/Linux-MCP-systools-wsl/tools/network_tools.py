"""
Network tools: curl, wget, ping, netstat, etc.
"""
import shlex
from typing import Any
from mcp.types import Tool, TextContent
from .shell_tools import execute_shell_command
import logging

logger = logging.getLogger("mcp-network-tools")


def register_network_tools() -> list[Tool]:
    """Register all network tools."""
    return [
        Tool(
            name="http_request",
            description="Make HTTP requests using curl. Supports GET, POST, PUT, DELETE with headers and data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to request"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"],
                        "description": "HTTP method",
                        "default": "GET"
                    },
                    "headers": {
                        "type": "object",
                        "description": "HTTP headers as key-value pairs"
                    },
                    "data": {
                        "type": "string",
                        "description": "Request body data"
                    },
                    "follow_redirects": {
                        "type": "boolean",
                        "description": "Follow HTTP redirects",
                        "default": True
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Request timeout in seconds",
                        "default": 30
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Save response to file"
                    },
                    "show_headers": {
                        "type": "boolean",
                        "description": "Include response headers in output",
                        "default": False
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="download_file",
            description="Download files from the internet using wget or curl.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to download"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Output file path (default: current directory with original filename)"
                    },
                    "resume": {
                        "type": "boolean",
                        "description": "Resume partial downloads",
                        "default": False
                    },
                    "quiet": {
                        "type": "boolean",
                        "description": "Quiet mode (less output)",
                        "default": False
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="ping_host",
            description="Ping a host to check connectivity and measure latency.",
            inputSchema={
                "type": "object",
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "Hostname or IP address to ping"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of ping packets to send",
                        "default": 4
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds",
                        "default": 5
                    }
                },
                "required": ["host"]
            }
        ),
        Tool(
            name="network_info",
            description="Get network information (ifconfig, ip, netstat commands).",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "enum": ["interfaces", "routes", "connections", "listening"],
                        "description": "Type of network info: 'interfaces' (ip/ifconfig), 'routes' (ip route), 'connections' (netstat active), 'listening' (netstat listening ports)",
                        "default": "interfaces"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="dns_lookup",
            description="Perform DNS lookups (dig, nslookup, host commands).",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain name to lookup"
                    },
                    "record_type": {
                        "type": "string",
                        "enum": ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "ANY"],
                        "description": "DNS record type",
                        "default": "A"
                    },
                    "nameserver": {
                        "type": "string",
                        "description": "Specific nameserver to query (optional)"
                    }
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="port_scan",
            description="Scan ports on a host using nc (netcat) or nmap.",
            inputSchema={
                "type": "object",
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "Target host"
                    },
                    "ports": {
                        "type": "string",
                        "description": "Port(s) to scan (e.g., '80', '1-1000', '80,443,8080')",
                        "default": "1-1000"
                    },
                    "use_nmap": {
                        "type": "boolean",
                        "description": "Use nmap if available (more detailed)",
                        "default": False
                    }
                },
                "required": ["host"]
            }
        ),
    ]


async def handle_network_tools(name: str, arguments: dict[str, Any]) -> list[TextContent] | None:
    """Handle network tool execution."""
    handlers = {
        "http_request": http_request,
        "download_file": download_file,
        "ping_host": ping_host,
        "network_info": network_info,
        "dns_lookup": dns_lookup,
        "port_scan": port_scan,
    }
    
    handler = handlers.get(name)
    if handler:
        return await handler(arguments)
    return None


# ============================================================================
# Network Tools Implementation
# ============================================================================

async def http_request(arguments: dict[str, Any]) -> list[TextContent]:
    """Make HTTP requests using curl."""
    url = arguments.get("url")
    method = arguments.get("method", "GET")
    headers = arguments.get("headers", {})
    data = arguments.get("data")
    follow_redirects = arguments.get("follow_redirects", True)
    timeout = arguments.get("timeout", 30)
    output_file = arguments.get("output_file")
    show_headers = arguments.get("show_headers", False)
    
    if not url:
        raise ValueError("URL is required")
    
    logger.info(f"HTTP {method} request to {url}")
    
    cmd_parts = ["curl", "-X", method]
    
    if follow_redirects:
        cmd_parts.append("-L")
    
    if show_headers:
        cmd_parts.append("-i")
    
    cmd_parts.extend(["--max-time", str(timeout)])
    
    for key, value in headers.items():
        cmd_parts.extend(["-H", shlex.quote(f"{key}: {value}")])
    
    if data:
        cmd_parts.extend(["-d", shlex.quote(data)])
    
    if output_file:
        cmd_parts.extend(["-o", shlex.quote(output_file)])
    
    cmd_parts.append(shlex.quote(url))
    
    command = " ".join(cmd_parts)
    
    return await execute_shell_command(
        {"command": command, "timeout": timeout + 5},
        shell="bash"
    )


async def download_file(arguments: dict[str, Any]) -> list[TextContent]:
    """Download files using wget."""
    url = arguments.get("url")
    output_path = arguments.get("output_path")
    resume = arguments.get("resume", False)
    quiet = arguments.get("quiet", False)
    
    if not url:
        raise ValueError("URL is required")
    
    logger.info(f"Downloading file from {url}")
    
    cmd_parts = ["wget"]
    
    if resume:
        cmd_parts.append("-c")
    
    if quiet:
        cmd_parts.append("-q")
    else:
        cmd_parts.append("--progress=bar:force")
    
    if output_path:
        cmd_parts.extend(["-O", shlex.quote(output_path)])
    
    cmd_parts.append(shlex.quote(url))
    
    command = " ".join(cmd_parts)
    
    return await execute_shell_command(
        {"command": command, "timeout": 300},
        shell="bash"
    )


async def ping_host(arguments: dict[str, Any]) -> list[TextContent]:
    """Ping a host."""
    host = arguments.get("host")
    count = arguments.get("count", 4)
    timeout = arguments.get("timeout", 5)
    
    if not host:
        raise ValueError("Host is required")
    
    logger.info(f"Pinging {host}")
    
    command = f"ping -c {count} -W {timeout} {shlex.quote(host)}"
    
    return await execute_shell_command(
        {"command": command, "timeout": timeout * count + 5},
        shell="bash"
    )


async def network_info(arguments: dict[str, Any]) -> list[TextContent]:
    """Get network information."""
    info_type = arguments.get("command", "interfaces")
    
    logger.info(f"Getting network info: {info_type}")
    
    if info_type == "interfaces":
        command = "ip addr show || ifconfig"
    elif info_type == "routes":
        command = "ip route show || route -n"
    elif info_type == "connections":
        command = "ss -tunapl || netstat -tunap"
    elif info_type == "listening":
        command = "ss -tunapl | grep LISTEN || netstat -tunlp"
    else:
        raise ValueError(f"Unknown command type: {info_type}")
    
    return await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )


async def dns_lookup(arguments: dict[str, Any]) -> list[TextContent]:
    """Perform DNS lookup."""
    domain = arguments.get("domain")
    record_type = arguments.get("record_type", "A")
    nameserver = arguments.get("nameserver")
    
    if not domain:
        raise ValueError("Domain is required")
    
    logger.info(f"DNS lookup for {domain} ({record_type})")
    
    if nameserver:
        command = f"dig @{shlex.quote(nameserver)} {shlex.quote(domain)} {record_type} +short || nslookup -type={record_type} {shlex.quote(domain)} {shlex.quote(nameserver)}"
    else:
        command = f"dig {shlex.quote(domain)} {record_type} +short || nslookup -type={record_type} {shlex.quote(domain)}"
    
    return await execute_shell_command(
        {"command": command, "timeout": 30},
        shell="bash"
    )


async def port_scan(arguments: dict[str, Any]) -> list[TextContent]:
    """Scan ports on a host."""
    host = arguments.get("host")
    ports = arguments.get("ports", "1-1000")
    use_nmap = arguments.get("use_nmap", False)
    
    if not host:
        raise ValueError("Host is required")
    
    logger.info(f"Scanning ports on {host}: {ports}")
    
    if use_nmap:
        command = f"nmap -p {shlex.quote(ports)} {shlex.quote(host)} || echo 'nmap not available, falling back to nc'"
    else:
        # Use netcat for basic scan
        command = f"nc -zv {shlex.quote(host)} {shlex.quote(ports)} 2>&1"
    
    return await execute_shell_command(
        {"command": command, "timeout": 120},
        shell="bash"
    )
