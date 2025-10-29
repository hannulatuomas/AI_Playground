"""
MCP (Model Context Protocol) Commands

Commands for managing MCP servers, tools, and resources.
"""

import click
import json


@click.group()
def mcp():
    """MCP (Model Context Protocol) server management"""
    pass


@mcp.command('list')
def mcp_list():
    """List all MCP servers and their status"""
    from ...core.orchestrator import UAIDE
    
    try:
        uaide = UAIDE()
        status = uaide.mcp_manager.get_server_status()
        
        if not status:
            click.echo("No MCP servers configured")
            return
        
        click.echo("\n=== MCP Servers ===\n")
        for name, info in status.items():
            status_icon = "✓" if info['connected'] else "✗"
            enabled_text = "enabled" if info['enabled'] else "disabled"
            
            click.echo(f"{status_icon} {name} ({enabled_text})")
            click.echo(f"  Description: {info['description']}")
            if info['connected']:
                click.echo(f"  Tools: {info['tools']}, Resources: {info['resources']}, Prompts: {info['prompts']}")
            click.echo()
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@mcp.command('start')
@click.argument('server_name')
def mcp_start(server_name):
    """Start an MCP server"""
    from ...core.orchestrator import UAIDE
    
    try:
        uaide = UAIDE()
        if uaide.mcp_manager.start_server(server_name):
            click.echo(f"✓ Started server: {server_name}")
        else:
            click.echo(f"✗ Failed to start server: {server_name}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@mcp.command('stop')
@click.argument('server_name')
def mcp_stop(server_name):
    """Stop an MCP server"""
    from ...core.orchestrator import UAIDE
    
    try:
        uaide = UAIDE()
        uaide.mcp_manager.stop_server(server_name)
        click.echo(f"✓ Stopped server: {server_name}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@mcp.command('tools')
@click.option('--server', help='Filter by server name')
def mcp_tools(server):
    """List all available MCP tools"""
    from ...core.orchestrator import UAIDE
    
    try:
        uaide = UAIDE()
        tools = uaide.mcp_manager.get_all_tools()
        
        if server:
            tools = [t for t in tools if t.server_name == server]
        
        if not tools:
            click.echo("No tools available")
            return
        
        click.echo(f"\n=== MCP Tools ({len(tools)}) ===\n")
        for tool in tools:
            click.echo(f"• {tool.name} ({tool.server_name})")
            click.echo(f"  {tool.description}")
            click.echo()
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@mcp.command('call')
@click.argument('tool_name')
@click.argument('server_name')
@click.option('--args', '-a', help='Tool arguments as JSON')
def mcp_call(tool_name, server_name, args):
    """Call an MCP tool"""
    from ...core.orchestrator import UAIDE
    from ...mcp.types import MCPToolCall
    
    try:
        uaide = UAIDE()
        
        # Parse arguments
        arguments = json.loads(args) if args else {}
        
        # Call tool
        result = uaide.mcp_manager.call_tool(MCPToolCall(
            tool_name=tool_name,
            arguments=arguments,
            server_name=server_name
        ))
        
        if result.success:
            click.echo(f"✓ Tool call successful")
            click.echo(f"Result: {result.content}")
        else:
            click.echo(f"✗ Tool call failed: {result.error}", err=True)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@mcp.command('resources')
@click.option('--server', help='Filter by server name')
def mcp_resources(server):
    """List all available MCP resources"""
    from ...core.orchestrator import UAIDE
    
    try:
        uaide = UAIDE()
        resources = uaide.mcp_manager.get_all_resources()
        
        if server:
            resources = [r for r in resources if r.server_name == server]
        
        if not resources:
            click.echo("No resources available")
            return
        
        click.echo(f"\n=== MCP Resources ({len(resources)}) ===\n")
        for resource in resources:
            click.echo(f"• {resource.name} ({resource.server_name})")
            click.echo(f"  URI: {resource.uri}")
            click.echo(f"  {resource.description}")
            click.echo()
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
