
"""
CLI entry point for AI Agent Console.

This module provides the command-line interface using Typer for interacting
with the AI agent system with Rich UI components for beautiful console output.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

# Rich imports for beautiful console UI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.json import JSON
from rich.text import Text
from rich import box
from rich.logging import RichHandler

from core import Engine, EngineError, AppConfig


# Initialize Rich Console (singleton)
console = Console()

# Initialize Typer app
app = typer.Typer(
    name="ai-agent-console",
    help="AI Agent Console - LLM-powered agent management system",
    add_completion=False
)

logger = logging.getLogger(__name__)


# ============================================================================
# Rich UI Helper Functions
# ============================================================================

def show_banner() -> None:
    """Display a beautiful banner for the AI Agent Console."""
    banner_text = Text()
    banner_text.append("╔═══════════════════════════════════════════════════════╗\n", style="bold cyan")
    banner_text.append("║                                                       ║\n", style="bold cyan")
    banner_text.append("║        ", style="bold cyan")
    banner_text.append("🤖 AI AGENT CONSOLE 🤖", style="bold magenta")
    banner_text.append("             ║\n", style="bold cyan")
    banner_text.append("║                                                       ║\n", style="bold cyan")
    banner_text.append("║     ", style="bold cyan")
    banner_text.append("LLM-Powered Agent Management System", style="bold white")
    banner_text.append("       ║\n", style="bold cyan")
    banner_text.append("║                                                       ║\n", style="bold cyan")
    banner_text.append("╚═══════════════════════════════════════════════════════╝", style="bold cyan")
    
    console.print(banner_text)
    console.print()


def print_success(message: str, prefix: str = "✓") -> None:
    """
    Print a success message with green color and checkmark.
    
    Args:
        message: Message to display
        prefix: Prefix symbol (default: ✓)
    """
    console.print(f"[bold green]{prefix}[/bold green] {message}")


def print_error(message: str, prefix: str = "✗") -> None:
    """
    Print an error message with red color and cross mark.
    
    Args:
        message: Message to display
        prefix: Prefix symbol (default: ✗)
    """
    console.print(f"[bold red]{prefix}[/bold red] {message}", style="red")


def print_warning(message: str, prefix: str = "⚠") -> None:
    """
    Print a warning message with yellow color and warning symbol.
    
    Args:
        message: Message to display
        prefix: Prefix symbol (default: ⚠)
    """
    console.print(f"[bold yellow]{prefix}[/bold yellow] {message}", style="yellow")


def print_info(message: str, prefix: str = "ℹ") -> None:
    """
    Print an info message with blue color and info symbol.
    
    Args:
        message: Message to display
        prefix: Prefix symbol (default: ℹ)
    """
    console.print(f"[bold blue]{prefix}[/bold blue] {message}", style="blue")


def create_status_table(status_data: dict) -> Table:
    """
    Create a Rich table for displaying status information.
    
    Args:
        status_data: Dictionary containing status information
        
    Returns:
        Rich Table object
    """
    table = Table(title="System Status", box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Component", style="cyan", width=25)
    table.add_column("Status", style="green", width=30)
    
    for key, value in status_data.items():
        table.add_row(key, str(value))
    
    return table


def create_agents_table(agents: list, verbose: bool = False, agent_info: dict = None) -> Table:
    """
    Create a Rich table for displaying agent information.
    
    Args:
        agents: List of agent names
        verbose: Show detailed information
        agent_info: Dictionary containing detailed agent info (for verbose mode)
        
    Returns:
        Rich Table object
    """
    table = Table(title="🤖 Available Agents", box=box.DOUBLE, show_header=True, header_style="bold magenta")
    
    if verbose and agent_info:
        table.add_column("Name", style="cyan", width=20)
        table.add_column("Class", style="green", width=25)
        table.add_column("Description", style="white", width=40)
        table.add_column("Cached", style="yellow", width=10)
        
        for agent_name in agents:
            info = agent_info.get(agent_name, {})
            table.add_row(
                agent_name,
                info.get('class_name', 'N/A'),
                info.get('description', 'No description')[:40],
                "Yes" if info.get('instance_cached') else "No"
            )
    else:
        table.add_column("Agent Name", style="cyan", width=30)
        table.add_column("Status", style="green", width=20)
        
        for agent_name in agents:
            table.add_row(agent_name, "✓ Available")
    
    return table


def create_tools_table(tools: list, verbose: bool = False, tool_info: dict = None) -> Table:
    """
    Create a Rich table for displaying tool information.
    
    Args:
        tools: List of tool names
        verbose: Show detailed information
        tool_info: Dictionary containing detailed tool info (for verbose mode)
        
    Returns:
        Rich Table object
    """
    table = Table(title="🔧 Available Tools", box=box.DOUBLE, show_header=True, header_style="bold blue")
    
    if verbose and tool_info:
        table.add_column("Name", style="cyan", width=20)
        table.add_column("Class", style="green", width=25)
        table.add_column("Description", style="white", width=45)
        
        for tool_name in tools:
            info = tool_info.get(tool_name, {})
            table.add_row(
                tool_name,
                info.get('class_name', 'N/A'),
                info.get('description', 'No description')[:45]
            )
    else:
        table.add_column("Tool Name", style="cyan", width=30)
        table.add_column("Status", style="green", width=20)
        
        for tool_name in tools:
            table.add_row(tool_name, "✓ Available")
    
    return table


def version_callback(value: bool):
    """Display version information."""
    if value:
        from core import __version__
        version_panel = Panel(
            f"[bold cyan]AI Agent Console[/bold cyan]\n[bold white]Version: {__version__}[/bold white]",
            title="Version Info",
            border_style="cyan"
        )
        console.print(version_panel)
        raise typer.Exit()


@app.callback()
def main():
    """AI Agent Console - LLM-powered agent management system."""
    pass


@app.command()
def run(
    query: Annotated[
        str,
        typer.Option(
            "--query",
            "-q",
            help="Query to process"
        )
    ] = "",
    config_file: Annotated[
        Optional[Path],
        typer.Option(
            "--config",
            "-c",
            help="Path to configuration file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True
        )
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option(
            "--model",
            "-m",
            help="Override default model"
        )
    ] = None,
    provider: Annotated[
        Optional[str],
        typer.Option(
            "--provider",
            "-p",
            help="Force specific provider (ollama or openai)"
        )
    ] = None,
    interactive: Annotated[
        bool,
        typer.Option(
            "--interactive",
            "-i",
            help="Start interactive mode"
        )
    ] = False,
):
    """
    Run a query through the AI agent system.
    
    Examples:
    
        # Single query
        python main.py run "What is the meaning of life?"
        
        # With specific model
        python main.py run "Explain quantum computing" --model llama2
        
        # Force OpenAI provider
        python main.py run "Write a poem" --provider openai
        
        # Interactive mode
        python main.py run --interactive
    """
    engine = None
    
    try:
        # Show banner
        show_banner()
        
        # Initialize engine with progress indicator
        with console.status("[bold cyan]Starting AI Agent Console...", spinner="dots"):
            engine = Engine(config_path=config_file)
            engine.initialize()
        
        # Show available providers
        status = engine.get_status()
        print_success(f"Available providers: {', '.join(status['available_providers'])}")
        console.print()
        
        # Interactive mode
        if interactive or not query or query == "":
            engine.run_interactive_loop()
            return
        
        # Single query mode
        query_panel = Panel(
            query,
            title="[bold cyan]📝 Query",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(query_panel)
        console.print()
        
        # Process with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Processing query...", total=100)
            
            # Simulate progress steps
            progress.update(task, advance=30)
            result = engine.process_query(
                query=query,
                model=model,
                provider=provider
            )
            progress.update(task, advance=70)
        
        console.print()
        
        if result['success']:
            # Show metadata
            metadata_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
            metadata_table.add_column("Key", style="cyan")
            metadata_table.add_column("Value", style="white")
            metadata_table.add_row("Provider", f"[bold green]{result['provider']}[/bold green]")
            metadata_table.add_row("Model", f"[bold green]{result['model']}[/bold green]")
            console.print(metadata_table)
            console.print()
            
            # Show response in a panel
            response_panel = Panel(
                result['response'],
                title="[bold cyan]📄 Response",
                border_style="green",
                padding=(1, 2)
            )
            console.print(response_panel)
            
        else:
            print_error(f"Error: {result['error']}")
            raise typer.Exit(code=1)
            
    except EngineError as e:
        console.print()
        print_error(f"Engine Error: {e}")
        
        # Show troubleshooting panel
        troubleshooting = Panel(
            "[yellow]• Ensure Ollama is running (ollama serve)\n"
            "• Or configure OpenAI API key in config.yaml\n"
            "• Check logs/app.log for detailed information[/yellow]",
            title="[bold yellow]⚠ Troubleshooting",
            border_style="yellow"
        )
        console.print(troubleshooting)
        raise typer.Exit(code=1)
        
    except KeyboardInterrupt:
        console.print("\n")
        print_info("👋 Interrupted by user")
        raise typer.Exit(code=0)
        
    except Exception as e:
        logger.exception("Unexpected error")
        console.print()
        print_error(f"Unexpected error: {e}")
        print_info("Check logs/app.log for details")
        raise typer.Exit(code=1)
        
    finally:
        if engine:
            engine.shutdown()


@app.command()
def task(
    task_description: Annotated[
        str,
        typer.Argument(
            help="Task description for agent execution"
        )
    ],
    config_file: Annotated[
        Optional[Path],
        typer.Option(
            "--config",
            "-c",
            help="Path to configuration file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True
        )
    ] = None,
    agents: Annotated[
        Optional[str],
        typer.Option(
            "--agents",
            "-a",
            help="Comma-separated list of agents to use (skips auto-selection)"
        )
    ] = None,
    auto_confirm: Annotated[
        bool,
        typer.Option(
            "--auto-confirm",
            help="Auto-confirm all agent actions (USE WITH CAUTION)"
        )
    ] = False,
):
    """
    Execute a task using agent orchestration.
    
    This command uses LLM-based task analysis to automatically select and
    chain the appropriate agents to accomplish the task.
    
    Examples:
    
        # Let the system analyze and execute
        python main.py task "Plan and create a hello world Python script"
        
        # Specify agents manually
        python main.py task "Create README.md" --agents code_editor
        
        # Auto-confirm all actions (dangerous!)
        python main.py task "Commit changes" --auto-confirm
    """
    engine = None
    
    try:
        # Show banner
        show_banner()
        
        # Initialize engine with spinner
        with console.status("[bold cyan]Starting AI Agent Console with Orchestration...", spinner="dots"):
            engine = Engine(config_path=config_file)
            engine.initialize()
        
        # Show status in a table
        status = engine.get_status()
        status_table = Table(show_header=False, box=box.ROUNDED, padding=(0, 2))
        status_table.add_column("Component", style="cyan", width=20)
        status_table.add_column("Value", style="white")
        status_table.add_row("Providers", ', '.join(status['available_providers']))
        status_table.add_row("Agents", ', '.join(status['registered_agents']))
        status_table.add_row("Tools", ', '.join(status['registered_tools']))
        console.print(status_table)
        console.print()
        
        if not status['registered_agents']:
            print_error("No agents available. Agent system may not be loaded.")
            raise typer.Exit(code=1)
        
        # Parse agent override if provided
        agent_override = None
        if agents:
            agent_override = [a.strip() for a in agents.split(',')]
            print_info(f"Using specified agents: {', '.join(agent_override)}")
            console.print()
        
        # Prepare context
        context = {
            'auto_confirm': auto_confirm
        }
        
        if auto_confirm:
            print_warning("AUTO-CONFIRM ENABLED - All actions will proceed without confirmation!")
            # Ask for confirmation before proceeding with auto-confirm
            if not Confirm.ask("[yellow]Are you sure you want to continue with auto-confirm?[/yellow]", default=False):
                print_info("Operation cancelled by user")
                raise typer.Exit(code=0)
            console.print()
        
        # Show task in a panel
        task_panel = Panel(
            task_description,
            title="[bold magenta]📝 Task",
            border_style="magenta",
            padding=(1, 2)
        )
        console.print(task_panel)
        console.print()
        
        # Execute task with progress
        with console.status("[bold cyan]Analyzing and executing task...", spinner="dots"):
            result = engine.execute_task(
                task=task_description,
                context=context,
                agent_override=agent_override
            )
        
        console.print()
        
        if result['success']:
            # Show analysis in a panel
            analysis = result.get('analysis', {})
            analysis_content = f"[cyan]Agents:[/cyan] {', '.join(analysis.get('agents', []))}\n"
            analysis_content += f"[cyan]Reasoning:[/cyan] {analysis.get('reasoning', 'N/A')}"
            
            analysis_panel = Panel(
                analysis_content,
                title="[bold green]✓ Task Analysis",
                border_style="green",
                padding=(1, 2)
            )
            console.print(analysis_panel)
            console.print()
            
            # Show orchestration results in a table
            orchestration = result.get('orchestration', {})
            agent_results = orchestration.get('results', [])
            
            results_table = Table(
                title=f"🎯 Execution Results ({len(agent_results)} agents)",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan"
            )
            results_table.add_column("№", style="cyan", width=5)
            results_table.add_column("Agent", style="magenta", width=20)
            results_table.add_column("Status", style="white", width=10)
            results_table.add_column("Message", style="white", width=50)
            
            for i, agent_result in enumerate(agent_results, 1):
                agent_name = agent_result.get('agent', 'unknown')
                agent_data = agent_result.get('result', {})
                success = agent_data.get('success', False)
                message = agent_data.get('message', 'No message')
                
                status_text = "[bold green]✓ Success[/bold green]" if success else "[bold red]✗ Failed[/bold red]"
                results_table.add_row(str(i), agent_name, status_text, message[:50])
            
            console.print(results_table)
            console.print()
            print_success("Task completed successfully!", prefix="🎉")
            
        else:
            print_error(f"Task execution failed: {result.get('message')}")
            if 'error' in result:
                console.print(f"   [red]Error: {result['error']}[/red]")
            raise typer.Exit(code=1)
            
    except EngineError as e:
        console.print()
        print_error(f"Engine Error: {e}")
        raise typer.Exit(code=1)
        
    except KeyboardInterrupt:
        console.print("\n")
        print_info("👋 Interrupted by user")
        raise typer.Exit(code=0)
        
    except Exception as e:
        logger.exception("Unexpected error")
        console.print()
        print_error(f"Unexpected error: {e}")
        print_info("Check logs/app.log for details")
        raise typer.Exit(code=1)
        
    finally:
        if engine:
            engine.shutdown()


@app.command()
def config(
    show: Annotated[
        bool,
        typer.Option(
            "--show",
            "-s",
            help="Display current configuration"
        )
    ] = False,
    validate: Annotated[
        bool,
        typer.Option(
            "--validate",
            help="Validate configuration file"
        )
    ] = False,
    config_file: Annotated[
        Optional[Path],
        typer.Option(
            "--config",
            "-c",
            help="Path to configuration file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True
        )
    ] = None,
):
    """
    Manage configuration settings.
    
    Examples:
    
        # Show current configuration
        python main.py config --show
        
        # Validate a specific config file
        python main.py config --validate --config my_config.yaml
    """
    try:
        if show or validate:
            # Load configuration with spinner
            with console.status("[bold cyan]Loading configuration...", spinner="dots"):
                cfg = AppConfig.load(config_file)
            
            if validate:
                print_success("Configuration is valid")
                console.print()
            
            if show:
                import json
                masked_config = cfg.mask_sensitive_data()
                
                # Display configuration as formatted JSON
                config_json = JSON(json.dumps(masked_config, indent=2))
                config_panel = Panel(
                    config_json,
                    title="[bold cyan]⚙️ Current Configuration",
                    border_style="cyan",
                    padding=(1, 2)
                )
                console.print(config_panel)
        else:
            print_info("Use --show to display configuration or --validate to check it")
            
    except Exception as e:
        print_error(f"Configuration error: {e}")
        raise typer.Exit(code=1)


@app.command()
def agents(
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Show detailed agent information"
        )
    ] = False,
):
    """
    List all available agents.
    
    Examples:
    
        # List all agents
        python main.py agents
        
        # Show detailed agent information
        python main.py agents --verbose
    """
    try:
        # Initialize engine with spinner
        with console.status("[bold cyan]🤖 Loading agent registry...", spinner="dots"):
            engine = Engine()
            engine.initialize()
        
        console.print()
        
        status_info = engine.get_status()
        
        if not status_info.get('agents_available'):
            print_error("Agent system is not available")
            raise typer.Exit(code=1)
        
        registered_agents = status_info.get('registered_agents', [])
        
        if not registered_agents:
            print_warning("No agents registered")
            print_info("Check your configuration and ensure agents are enabled")
            raise typer.Exit(code=0)
        
        # Create and display agents table
        agent_info = None
        if verbose and engine.agent_registry:
            agent_info = engine.agent_registry.list_all()
        
        agents_table = create_agents_table(registered_agents, verbose, agent_info)
        console.print(agents_table)
        console.print()
        
        print_success(f"Found {len(registered_agents)} agent(s)")
        
        engine.shutdown()
        
    except Exception as e:
        print_error(f"Failed to list agents: {e}")
        raise typer.Exit(code=1)


@app.command(name="tools")
def list_tools(
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Show detailed tool information"
        )
    ] = False,
):
    """
    List all available tools.
    
    Examples:
    
        # List all tools
        python main.py tools
        
        # Show detailed tool information
        python main.py tools --verbose
    """
    try:
        # Initialize engine with spinner
        with console.status("[bold cyan]🔧 Loading tool registry...", spinner="dots"):
            engine = Engine()
            engine.initialize()
        
        console.print()
        
        status_info = engine.get_status()
        
        if not status_info.get('tools_available'):
            print_error("Tool system is not available")
            raise typer.Exit(code=1)
        
        registered_tools = status_info.get('registered_tools', [])
        
        if not registered_tools:
            print_warning("No tools registered")
            print_info("Check your configuration and ensure tools are enabled")
            raise typer.Exit(code=0)
        
        # Create and display tools table
        tool_info = None
        if verbose and engine.tool_registry:
            tool_info = engine.tool_registry.list_all()
        
        tools_table = create_tools_table(registered_tools, verbose, tool_info)
        console.print(tools_table)
        console.print()
        
        print_success(f"Found {len(registered_tools)} tool(s)")
        
        engine.shutdown()
        
    except Exception as e:
        print_error(f"Failed to list tools: {e}")
        raise typer.Exit(code=1)


@app.command()
def status():
    """
    Check system status and provider availability.
    
    Example:
    
        python main.py status
    """
    try:
        # Initialize engine with spinner
        with console.status("[bold cyan]🔍 Checking system status...", spinner="dots"):
            engine = Engine()
            engine.initialize()
        
        console.print()
        
        status_info = engine.get_status()
        
        # Create main status table
        status_table = Table(
            title="🎯 Engine Status",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        status_table.add_column("Component", style="cyan", width=25)
        status_table.add_column("Status", style="white", width=30)
        
        # Add status rows
        status_table.add_row(
            "Engine Initialized",
            "[bold green]✓ Yes[/bold green]" if status_info['initialized'] else "[bold red]✗ No[/bold red]"
        )
        status_table.add_row(
            "Configuration Loaded",
            "[bold green]✓ Yes[/bold green]" if status_info['config_loaded'] else "[bold red]✗ No[/bold red]"
        )
        status_table.add_row(
            "Agents System",
            "[bold green]✓ Available[/bold green]" if status_info['agents_available'] else "[bold yellow]⚠ Not available[/bold yellow]"
        )
        status_table.add_row(
            "Tools System",
            "[bold green]✓ Available[/bold green]" if status_info['tools_available'] else "[bold yellow]⚠ Not available[/bold yellow]"
        )
        
        console.print(status_table)
        console.print()
        
        # Create providers table
        providers = status_info['available_providers']
        providers_table = Table(
            title="🔌 LLM Providers",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold green"
        )
        providers_table.add_column("Provider", style="cyan", width=20)
        providers_table.add_column("Status", style="green", width=35)
        
        if providers:
            for provider in providers:
                providers_table.add_row(provider, "[bold green]✓ Available[/bold green]")
        else:
            providers_table.add_row("None", "[bold yellow]⚠ No providers configured[/bold yellow]")
        
        console.print(providers_table)
        console.print()
        
        # Show warning if no providers
        if not providers:
            print_warning("No LLM providers available!")
            print_info("Please configure at least one provider (Ollama or OpenAI)")
            console.print()
        
        # Create agents table if any
        if status_info['registered_agents']:
            agents_table = create_agents_table(status_info['registered_agents'])
            console.print(agents_table)
            console.print()
        
        # Create tools table if any
        if status_info['registered_tools']:
            tools_table = create_tools_table(status_info['registered_tools'])
            console.print(tools_table)
            console.print()
        
        # Final status message
        if status_info['initialized'] and providers:
            print_success("System is ready!", prefix="🎉")
        elif status_info['initialized']:
            print_warning("System initialized but no LLM providers available")
        else:
            print_error("System not properly initialized")
        
        engine.shutdown()
        
    except Exception as e:
        print_error(f"Status check failed: {e}")
        raise typer.Exit(code=1)


# ============================================================================
# Project Management Commands
# ============================================================================

@app.command(name="projects")
def list_projects_cmd() -> None:
    """
    List all projects.
    
    Example:
    
        python main.py projects
    """
    try:
        with console.status("[bold cyan]🔍 Loading projects...", spinner="dots"):
            engine = Engine()
            engine.initialize()
        
        console.print()
        
        projects = engine.list_projects()
        
        if not projects:
            print_warning("No projects found")
            console.print()
            return
        
        # Create projects table
        projects_table = Table(
            title="📁 Projects",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        projects_table.add_column("Name", style="cyan", width=25)
        projects_table.add_column("Description", style="white", width=40)
        projects_table.add_column("Active", style="white", width=10)
        projects_table.add_column("Created", style="white", width=20)
        
        for project in projects:
            active_marker = "[bold green]✓[/bold green]" if project['is_active'] else ""
            created = project['created_at'][:10]  # Just the date
            projects_table.add_row(
                project['name'],
                project['description'][:40] if project['description'] else "",
                active_marker,
                created
            )
        
        console.print(projects_table)
        console.print()
        
        # Show active project
        current = engine.get_current_project()
        if current:
            print_success(f"Active project: {current['name']}", prefix="📌")
        
        engine.shutdown()
        
    except Exception as e:
        print_error(f"Failed to list projects: {e}")
        raise typer.Exit(code=1)


@app.command(name="create-project")
def create_project_cmd(
    name: Annotated[str, typer.Argument(help="Project name")],
    description: Annotated[str, typer.Option("--description", "-d", help="Project description")] = "",
    no_switch: Annotated[bool, typer.Option("--no-switch", help="Don't switch to the new project")] = False
) -> None:
    """
    Create a new project.
    
    Example:
    
        python main.py create-project "My AI Project" -d "Working on AI features"
    """
    try:
        with console.status("[bold cyan]🔧 Creating project...", spinner="dots"):
            engine = Engine()
            engine.initialize()
        
        console.print()
        
        project_id = engine.create_project(
            name=name,
            description=description,
            switch_to_new=not no_switch
        )
        
        if project_id:
            print_success(f"Project created: {name}", prefix="✓")
            if not no_switch:
                print_success(f"Switched to new project", prefix="📌")
        else:
            print_error("Failed to create project")
        
        console.print()
        engine.shutdown()
        
    except Exception as e:
        print_error(f"Failed to create project: {e}")
        raise typer.Exit(code=1)


@app.command(name="switch-project")
def switch_project_cmd(
    name: Annotated[str, typer.Argument(help="Project name (partial match supported)")]
) -> None:
    """
    Switch to a different project.
    
    Example:
    
        python main.py switch-project "My Project"
    """
    try:
        with console.status("[bold cyan]🔧 Switching project...", spinner="dots"):
            engine = Engine()
            engine.initialize()
        
        console.print()
        
        # Find project by name
        projects = engine.list_projects()
        matching_projects = [p for p in projects if name.lower() in p['name'].lower()]
        
        if not matching_projects:
            print_error(f"No project found matching: {name}")
            console.print()
            engine.shutdown()
            return
        
        if len(matching_projects) > 1:
            print_warning(f"Multiple projects match '{name}':")
            for p in matching_projects:
                console.print(f"  - {p['name']}")
            console.print()
            engine.shutdown()
            return
        
        project = matching_projects[0]
        if engine.switch_project(project['project_id']):
            print_success(f"Switched to project: {project['name']}", prefix="📌")
        else:
            print_error("Failed to switch project")
        
        console.print()
        engine.shutdown()
        
    except Exception as e:
        print_error(f"Failed to switch project: {e}")
        raise typer.Exit(code=1)


@app.command(name="delete-project")
def delete_project_cmd(
    name: Annotated[str, typer.Argument(help="Project name (partial match supported)")],
    force: Annotated[bool, typer.Option("--force", "-f", help="Skip confirmation")] = False
) -> None:
    """
    Delete a project and all its data.
    
    Example:
    
        python main.py delete-project "Old Project" --force
    """
    try:
        with console.status("[bold cyan]🔧 Loading projects...", spinner="dots"):
            engine = Engine()
            engine.initialize()
        
        console.print()
        
        # Find project by name
        projects = engine.list_projects()
        matching_projects = [p for p in projects if name.lower() in p['name'].lower()]
        
        if not matching_projects:
            print_error(f"No project found matching: {name}")
            console.print()
            engine.shutdown()
            return
        
        if len(matching_projects) > 1:
            print_warning(f"Multiple projects match '{name}':")
            for p in matching_projects:
                console.print(f"  - {p['name']}")
            console.print()
            engine.shutdown()
            return
        
        project = matching_projects[0]
        
        # Confirm deletion
        if not force:
            confirm = Confirm.ask(
                f"[bold red]⚠ Delete project '{project['name']}' and all its data?[/bold red]"
            )
            if not confirm:
                print_info("Deletion cancelled")
                console.print()
                engine.shutdown()
                return
        
        if engine.delete_project(project['project_id']):
            print_success(f"Project deleted: {project['name']}", prefix="✓")
        else:
            print_error("Failed to delete project")
        
        console.print()
        engine.shutdown()
        
    except Exception as e:
        print_error(f"Failed to delete project: {e}")
        raise typer.Exit(code=1)


# ============================================================================
# Chat History Commands
# ============================================================================

@app.command(name="chat-history")
def chat_history_cmd(
    limit: Annotated[int, typer.Option("--limit", "-n", help="Number of recent messages")] = 20,
    project: Annotated[Optional[str], typer.Option("--project", "-p", help="Project name")] = None
) -> None:
    """
    View chat history for the current or specified project.
    
    Example:
    
        python main.py chat-history --limit 10
    """
    try:
        with console.status("[bold cyan]🔍 Loading chat history...", spinner="dots"):
            engine = Engine()
            engine.initialize()
        
        console.print()
        
        # Get project ID
        project_id = None
        if project:
            projects = engine.list_projects()
            matching = [p for p in projects if project.lower() in p['name'].lower()]
            if matching:
                project_id = matching[0]['project_id']
        
        # Get chat history
        history = engine.get_chat_history(project_id=project_id, limit=limit)
        
        if not history:
            print_warning("No chat history found")
            console.print()
            engine.shutdown()
            return
        
        # Display chat history
        current_project = engine.get_current_project()
        project_name = current_project['name'] if current_project else "Unknown"
        
        console.print(Panel(
            f"[cyan]Project:[/cyan] {project_name}\n[cyan]Messages:[/cyan] {len(history)}",
            title="💬 Chat History",
            border_style="cyan"
        ))
        console.print()
        
        for msg in history:
            role = msg['role']
            content = msg['content']
            timestamp = msg.get('timestamp', '')[:19] if msg.get('timestamp') else ''
            
            if role == 'user':
                console.print(f"[bold cyan]User[/bold cyan] [{timestamp}]:")
                console.print(f"  {content}")
            elif role == 'assistant':
                console.print(f"[bold green]Assistant[/bold green] [{timestamp}]:")
                console.print(f"  {content}")
            elif role == 'system':
                console.print(f"[bold yellow]System[/bold yellow] [{timestamp}]:")
                console.print(f"  {content}")
            
            console.print()
        
        engine.shutdown()
        
    except Exception as e:
        print_error(f"Failed to load chat history: {e}")
        raise typer.Exit(code=1)


@app.command(name="summarize-chat")
def summarize_chat_cmd(
    project: Annotated[Optional[str], typer.Option("--project", "-p", help="Project name")] = None
) -> None:
    """
    Generate a summary of the chat history.
    
    Example:
    
        python main.py summarize-chat
    """
    try:
        with console.status("[bold cyan]🤖 Generating summary...", spinner="dots"):
            engine = Engine()
            engine.initialize()
            
            # Get project ID
            project_id = None
            if project:
                projects = engine.list_projects()
                matching = [p for p in projects if project.lower() in p['name'].lower()]
                if matching:
                    project_id = matching[0]['project_id']
            
            # Generate summary
            summary = engine.summarize_chat_history(project_id=project_id)
        
        console.print()
        
        if summary:
            console.print(Panel(
                summary,
                title="📝 Chat History Summary",
                border_style="green"
            ))
            console.print()
            print_success("Summary generated successfully", prefix="✓")
        else:
            print_warning("Could not generate summary (history may be too short)")
        
        console.print()
        engine.shutdown()
        
    except Exception as e:
        print_error(f"Failed to generate summary: {e}")
        raise typer.Exit(code=1)


# ============================================================================
# Prompt Management Commands
# ============================================================================

@app.command(name="prompt-save")
def prompt_save_cmd(
    name: Annotated[str, typer.Argument(help="Prompt name")],
    content: Annotated[Optional[str], typer.Option("--content", "-c", help="Prompt content")] = None,
    description: Annotated[str, typer.Option("--description", "-d", help="Prompt description")] = "",
    prompt_type: Annotated[str, typer.Option("--type", "-t", help="Type: 'prompt' or 'snippet'")] = "prompt",
    scope: Annotated[str, typer.Option("--scope", "-s", help="Scope: 'global' or 'project'")] = "global",
    tags: Annotated[Optional[str], typer.Option("--tags", help="Comma-separated tags")] = None,
    file: Annotated[Optional[Path], typer.Option("--file", "-f", help="Read content from file")] = None,
    interactive: Annotated[bool, typer.Option("--interactive", "-i", help="Interactive mode")] = False
) -> None:
    """
    Save a new prompt or snippet.
    
    Examples:
    
        # Save a simple prompt
        python main.py prompt-save "code-review" -c "Review the following code for best practices"
        
        # Save from file
        python main.py prompt-save "debug-template" -f template.txt --scope project
        
        # Interactive mode
        python main.py prompt-save "my-prompt" --interactive
    """
    from core import create_prompt_manager, PromptType, PromptScope
    
    try:
        # Initialize prompt manager
        project_dir = None
        if scope.lower() == "project":
            engine = Engine()
            engine.initialize()
            current_project = engine.get_current_project()
            if current_project:
                project_dir = Path(engine.config.projects_dir) / current_project['project_id']
            else:
                print_error("No active project. Create or switch to a project first.")
                raise typer.Exit(code=1)
            engine.shutdown()
        
        prompt_manager = create_prompt_manager(project_dir)
        
        # Interactive mode
        if interactive:
            console.print(Panel("📝 Interactive Prompt Creation", style="cyan bold"))
            console.print()
            
            if not name:
                name = Prompt.ask("Enter prompt name")
            
            description = Prompt.ask("Enter description (optional)", default="")
            
            console.print("\n[cyan]Enter content (press Ctrl+D or Ctrl+Z when done):[/cyan]")
            content_lines = []
            try:
                while True:
                    line = input()
                    content_lines.append(line)
            except EOFError:
                pass
            content = "\n".join(content_lines)
            
            tags_input = Prompt.ask("Enter tags (comma-separated, optional)", default="")
            tags_list = [t.strip() for t in tags_input.split(",")] if tags_input else []
        else:
            # Non-interactive mode
            if not content and not file:
                print_error("Either --content or --file must be provided")
                raise typer.Exit(code=1)
            
            # Read from file if specified
            if file:
                if not file.exists():
                    print_error(f"File not found: {file}")
                    raise typer.Exit(code=1)
                content = file.read_text(encoding='utf-8')
            
            tags_list = [t.strip() for t in tags.split(",")] if tags else []
        
        # Validate and convert types
        try:
            ptype = PromptType(prompt_type.lower())
        except ValueError:
            print_error(f"Invalid type: {prompt_type}. Must be 'prompt' or 'snippet'")
            raise typer.Exit(code=1)
        
        try:
            pscope = PromptScope(scope.lower())
        except ValueError:
            print_error(f"Invalid scope: {scope}. Must be 'global' or 'project'")
            raise typer.Exit(code=1)
        
        # Save prompt
        prompt = prompt_manager.save_prompt(
            name=name,
            content=content,
            description=description,
            prompt_type=ptype,
            scope=pscope,
            tags=tags_list
        )
        
        console.print()
        print_success(f"Saved {ptype.value} '{name}' with {pscope.value} scope", prefix="✓")
        
        if prompt.variables:
            console.print(f"[yellow]ℹ Variables detected:[/yellow] {', '.join(prompt.variables)}")
        
        console.print()
        
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"Failed to save prompt: {e}")
        raise typer.Exit(code=1)


@app.command(name="prompt-list")
def prompt_list_cmd(
    scope: Annotated[Optional[str], typer.Option("--scope", "-s", help="Filter by scope: 'global' or 'project'")] = None,
    prompt_type: Annotated[Optional[str], typer.Option("--type", "-t", help="Filter by type: 'prompt' or 'snippet'")] = None,
    tags: Annotated[Optional[str], typer.Option("--tags", help="Filter by tags (comma-separated)")] = None,
    search: Annotated[Optional[str], typer.Option("--search", help="Search term")] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show detailed information")] = False
) -> None:
    """
    List saved prompts and snippets.
    
    Examples:
    
        # List all prompts
        python main.py prompt-list
        
        # List global prompts only
        python main.py prompt-list --scope global
        
        # List snippets with specific tags
        python main.py prompt-list --type snippet --tags "python,debug"
        
        # Search prompts
        python main.py prompt-list --search "code review"
    """
    from core import create_prompt_manager, PromptType, PromptScope
    
    try:
        # Initialize prompt manager
        project_dir = None
        engine = Engine()
        engine.initialize()
        current_project = engine.get_current_project()
        if current_project:
            project_dir = Path(engine.config.projects_dir) / current_project['project_id']
        engine.shutdown()
        
        prompt_manager = create_prompt_manager(project_dir)
        
        # Parse filters
        pscope = PromptScope(scope.lower()) if scope else None
        ptype = PromptType(prompt_type.lower()) if prompt_type else None
        tags_list = [t.strip() for t in tags.split(",")] if tags else None
        
        # List prompts
        prompts = prompt_manager.list_prompts(
            scope=pscope,
            prompt_type=ptype,
            tags=tags_list,
            search_term=search
        )
        
        if not prompts:
            print_warning("No prompts found matching the criteria")
            console.print()
            return
        
        # Create table
        table = Table(
            title="📝 Saved Prompts & Snippets",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Name", style="cyan", width=25)
        table.add_column("Type", style="white", width=10)
        table.add_column("Scope", style="white", width=10)
        table.add_column("Tags", style="yellow", width=25)
        
        if verbose:
            table.add_column("Usage", style="white", width=8)
            table.add_column("Updated", style="white", width=12)
        
        for prompt in prompts:
            tags_str = ", ".join(prompt.tags[:3]) if prompt.tags else ""
            if len(prompt.tags) > 3:
                tags_str += f" +{len(prompt.tags) - 3}"
            
            row = [
                prompt.name,
                prompt.prompt_type.value,
                prompt.scope.value,
                tags_str
            ]
            
            if verbose:
                row.append(str(prompt.usage_count))
                row.append(prompt.updated_at.strftime("%Y-%m-%d"))
            
            table.add_row(*row)
        
        console.print()
        console.print(table)
        console.print()
        print_info(f"Total: {len(prompts)} prompt(s)", prefix="ℹ")
        console.print()
        
    except ValueError as e:
        print_error(f"Invalid filter: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"Failed to list prompts: {e}")
        raise typer.Exit(code=1)


@app.command(name="prompt-view")
def prompt_view_cmd(
    name: Annotated[str, typer.Argument(help="Prompt name")],
    scope: Annotated[Optional[str], typer.Option("--scope", "-s", help="Scope: 'global' or 'project'")] = None
) -> None:
    """
    View details of a specific prompt.
    
    Example:
    
        python main.py prompt-view "code-review"
    """
    from core import create_prompt_manager, PromptScope
    
    try:
        # Initialize prompt manager
        project_dir = None
        engine = Engine()
        engine.initialize()
        current_project = engine.get_current_project()
        if current_project:
            project_dir = Path(engine.config.projects_dir) / current_project['project_id']
        engine.shutdown()
        
        prompt_manager = create_prompt_manager(project_dir)
        
        # Parse scope
        pscope = PromptScope(scope.lower()) if scope else None
        
        # Get prompt
        prompt = prompt_manager.get_prompt_by_name(name, pscope)
        
        if not prompt:
            print_error(f"Prompt '{name}' not found")
            raise typer.Exit(code=1)
        
        # Display prompt details
        console.print()
        console.print(Panel(
            f"[bold cyan]Name:[/bold cyan] {prompt.name}\n"
            f"[bold cyan]Type:[/bold cyan] {prompt.prompt_type.value}\n"
            f"[bold cyan]Scope:[/bold cyan] {prompt.scope.value}\n"
            f"[bold cyan]Description:[/bold cyan] {prompt.description or 'N/A'}\n"
            f"[bold cyan]Tags:[/bold cyan] {', '.join(prompt.tags) if prompt.tags else 'None'}\n"
            f"[bold cyan]Variables:[/bold cyan] {', '.join(prompt.variables) if prompt.variables else 'None'}\n"
            f"[bold cyan]Usage Count:[/bold cyan] {prompt.usage_count}\n"
            f"[bold cyan]Created:[/bold cyan] {prompt.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"[bold cyan]Updated:[/bold cyan] {prompt.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            title="📝 Prompt Details",
            border_style="cyan"
        ))
        console.print()
        
        # Display content
        console.print(Panel(
            Syntax(prompt.content, "text", theme="monokai", word_wrap=True),
            title="📄 Content",
            border_style="green"
        ))
        console.print()
        
    except ValueError as e:
        print_error(f"Invalid scope: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"Failed to view prompt: {e}")
        raise typer.Exit(code=1)


@app.command(name="prompt-edit")
def prompt_edit_cmd(
    name: Annotated[str, typer.Argument(help="Prompt name")],
    scope: Annotated[Optional[str], typer.Option("--scope", "-s", help="Scope: 'global' or 'project'")] = None,
    new_name: Annotated[Optional[str], typer.Option("--name", help="New name")] = None,
    content: Annotated[Optional[str], typer.Option("--content", "-c", help="New content")] = None,
    description: Annotated[Optional[str], typer.Option("--description", "-d", help="New description")] = None,
    tags: Annotated[Optional[str], typer.Option("--tags", help="New tags (comma-separated)")] = None,
    file: Annotated[Optional[Path], typer.Option("--file", "-f", help="Read content from file")] = None
) -> None:
    """
    Edit an existing prompt.
    
    Examples:
    
        # Update description
        python main.py prompt-edit "code-review" -d "Updated description"
        
        # Update content from file
        python main.py prompt-edit "template" -f new_template.txt
        
        # Update tags
        python main.py prompt-edit "my-prompt" --tags "python,code,review"
    """
    from core import create_prompt_manager, PromptScope
    
    try:
        # Initialize prompt manager
        project_dir = None
        engine = Engine()
        engine.initialize()
        current_project = engine.get_current_project()
        if current_project:
            project_dir = Path(engine.config.projects_dir) / current_project['project_id']
        engine.shutdown()
        
        prompt_manager = create_prompt_manager(project_dir)
        
        # Parse scope
        pscope = PromptScope(scope.lower()) if scope else None
        
        # Get prompt
        prompt = prompt_manager.get_prompt_by_name(name, pscope)
        
        if not prompt:
            print_error(f"Prompt '{name}' not found")
            raise typer.Exit(code=1)
        
        # Read from file if specified
        if file:
            if not file.exists():
                print_error(f"File not found: {file}")
                raise typer.Exit(code=1)
            content = file.read_text(encoding='utf-8')
        
        # Parse tags
        tags_list = [t.strip() for t in tags.split(",")] if tags else None
        
        # Update prompt
        updated_prompt = prompt_manager.update_prompt(
            prompt_id=prompt.prompt_id,
            name=new_name,
            content=content,
            description=description,
            tags=tags_list
        )
        
        console.print()
        print_success(f"Updated prompt '{updated_prompt.name}'", prefix="✓")
        console.print()
        
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"Failed to edit prompt: {e}")
        raise typer.Exit(code=1)


@app.command(name="prompt-delete")
def prompt_delete_cmd(
    name: Annotated[str, typer.Argument(help="Prompt name")],
    scope: Annotated[Optional[str], typer.Option("--scope", "-s", help="Scope: 'global' or 'project'")] = None,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation")] = False
) -> None:
    """
    Delete a saved prompt.
    
    Example:
    
        python main.py prompt-delete "old-prompt" -y
    """
    from core import create_prompt_manager, PromptScope
    
    try:
        # Initialize prompt manager
        project_dir = None
        engine = Engine()
        engine.initialize()
        current_project = engine.get_current_project()
        if current_project:
            project_dir = Path(engine.config.projects_dir) / current_project['project_id']
        engine.shutdown()
        
        prompt_manager = create_prompt_manager(project_dir)
        
        # Parse scope
        pscope = PromptScope(scope.lower()) if scope else None
        
        # Get prompt
        prompt = prompt_manager.get_prompt_by_name(name, pscope)
        
        if not prompt:
            print_error(f"Prompt '{name}' not found")
            raise typer.Exit(code=1)
        
        # Confirm deletion
        if not yes:
            confirm = Confirm.ask(f"Delete prompt '{name}'?")
            if not confirm:
                print_info("Deletion cancelled")
                return
        
        # Delete prompt
        success = prompt_manager.delete_prompt(prompt.prompt_id)
        
        if success:
            console.print()
            print_success(f"Deleted prompt '{name}'", prefix="✓")
            console.print()
        else:
            print_error("Failed to delete prompt")
        
    except ValueError as e:
        print_error(f"Invalid scope: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"Failed to delete prompt: {e}")
        raise typer.Exit(code=1)


@app.command(name="prompt-use")
def prompt_use_cmd(
    name: Annotated[str, typer.Argument(help="Prompt name")],
    scope: Annotated[Optional[str], typer.Option("--scope", "-s", help="Scope: 'global' or 'project'")] = None,
    variables: Annotated[Optional[str], typer.Option("--vars", help="Variables in key=value format (comma-separated)")] = None,
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Save to file")] = None,
    copy: Annotated[bool, typer.Option("--copy", "-c", help="Copy to clipboard")] = False
) -> None:
    """
    Use a saved prompt with optional variable substitution.
    
    Examples:
    
        # Simple usage
        python main.py prompt-use "code-review"
        
        # With variables
        python main.py prompt-use "template" --vars "project_name=MyApp,version=1.0"
        
        # Save to file
        python main.py prompt-use "template" -o output.txt
    """
    from core import create_prompt_manager, PromptScope
    
    try:
        # Initialize prompt manager
        project_dir = None
        engine = Engine()
        engine.initialize()
        current_project = engine.get_current_project()
        if current_project:
            project_dir = Path(engine.config.projects_dir) / current_project['project_id']
        engine.shutdown()
        
        prompt_manager = create_prompt_manager(project_dir)
        
        # Parse scope
        pscope = PromptScope(scope.lower()) if scope else None
        
        # Get prompt
        prompt = prompt_manager.get_prompt_by_name(name, pscope)
        
        if not prompt:
            print_error(f"Prompt '{name}' not found")
            raise typer.Exit(code=1)
        
        # Parse variables
        vars_dict = {}
        if variables:
            for var_pair in variables.split(","):
                if "=" in var_pair:
                    key, value = var_pair.split("=", 1)
                    vars_dict[key.strip()] = value.strip()
        
        # Use prompt
        try:
            content = prompt_manager.use_prompt(prompt.prompt_id, vars_dict if vars_dict else None)
        except ValueError as e:
            print_error(str(e))
            raise typer.Exit(code=1)
        
        # Output
        if output:
            output.write_text(content, encoding='utf-8')
            console.print()
            print_success(f"Saved to {output}", prefix="✓")
            console.print()
        elif copy:
            try:
                import pyperclip
                pyperclip.copy(content)
                console.print()
                print_success("Copied to clipboard", prefix="✓")
                console.print()
            except ImportError:
                print_warning("pyperclip not installed. Install with: pip install pyperclip")
                console.print()
                console.print(Panel(content, title="📄 Content", border_style="green"))
                console.print()
        else:
            console.print()
            console.print(Panel(
                Syntax(content, "text", theme="monokai", word_wrap=True),
                title=f"📄 {name}",
                border_style="green"
            ))
            console.print()
        
    except ValueError as e:
        print_error(f"Invalid scope: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"Failed to use prompt: {e}")
        raise typer.Exit(code=1)


@app.command(name="prompt-stats")
def prompt_stats_cmd() -> None:
    """
    Show statistics about saved prompts.
    
    Example:
    
        python main.py prompt-stats
    """
    from core import create_prompt_manager
    
    try:
        # Initialize prompt manager
        project_dir = None
        engine = Engine()
        engine.initialize()
        current_project = engine.get_current_project()
        if current_project:
            project_dir = Path(engine.config.projects_dir) / current_project['project_id']
        engine.shutdown()
        
        prompt_manager = create_prompt_manager(project_dir)
        
        # Get statistics
        stats = prompt_manager.get_stats()
        
        console.print()
        
        # Summary panel
        summary = (
            f"[bold cyan]Total Prompts:[/bold cyan] {stats['total']}\n"
            f"[bold cyan]Global:[/bold cyan] {stats['global']}\n"
            f"[bold cyan]Project:[/bold cyan] {stats['project']}\n"
            f"[bold cyan]Prompts:[/bold cyan] {stats['prompts']}\n"
            f"[bold cyan]Snippets:[/bold cyan] {stats['snippets']}\n"
            f"[bold cyan]Tags:[/bold cyan] {len(stats['tags'])}"
        )
        
        console.print(Panel(summary, title="📊 Statistics", border_style="cyan"))
        console.print()
        
        # Most used prompts
        if stats['most_used']:
            table = Table(
                title="🏆 Most Used Prompts",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan"
            )
            table.add_column("Name", style="cyan", width=30)
            table.add_column("Type", style="white", width=10)
            table.add_column("Usage", style="green", width=10)
            
            for prompt_stat in stats['most_used']:
                table.add_row(
                    prompt_stat['name'],
                    prompt_stat['type'],
                    str(prompt_stat['usage_count'])
                )
            
            console.print(table)
            console.print()
        
        # Tags
        if stats['tags']:
            console.print(f"[bold cyan]Available Tags:[/bold cyan] {', '.join(stats['tags'])}")
            console.print()
        
    except Exception as e:
        print_error(f"Failed to get statistics: {e}")
        raise typer.Exit(code=1)


@app.command(name="prompt-export")
def prompt_export_cmd(
    output: Annotated[Path, typer.Argument(help="Output file path")],
    scope: Annotated[Optional[str], typer.Option("--scope", "-s", help="Filter by scope")] = None,
    tags: Annotated[Optional[str], typer.Option("--tags", help="Filter by tags")] = None
) -> None:
    """
    Export prompts to a file.
    
    Example:
    
        python main.py prompt-export my-prompts.json --scope global
    """
    from core import create_prompt_manager, PromptScope
    
    try:
        # Initialize prompt manager
        project_dir = None
        engine = Engine()
        engine.initialize()
        current_project = engine.get_current_project()
        if current_project:
            project_dir = Path(engine.config.projects_dir) / current_project['project_id']
        engine.shutdown()
        
        prompt_manager = create_prompt_manager(project_dir)
        
        # Parse filters
        pscope = PromptScope(scope.lower()) if scope else None
        tags_list = [t.strip() for t in tags.split(",")] if tags else None
        
        # Export
        count = prompt_manager.export_prompts(output, scope=pscope, tags=tags_list)
        
        console.print()
        print_success(f"Exported {count} prompt(s) to {output}", prefix="✓")
        console.print()
        
    except ValueError as e:
        print_error(f"Invalid filter: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"Failed to export prompts: {e}")
        raise typer.Exit(code=1)


@app.command(name="prompt-import")
def prompt_import_cmd(
    input_file: Annotated[Path, typer.Argument(help="Input file path")],
    scope: Annotated[Optional[str], typer.Option("--scope", "-s", help="Override scope for imported prompts")] = None,
    overwrite: Annotated[bool, typer.Option("--overwrite", help="Overwrite existing prompts")] = False
) -> None:
    """
    Import prompts from a file.
    
    Example:
    
        python main.py prompt-import my-prompts.json --scope global
    """
    from core import create_prompt_manager, PromptScope
    
    try:
        if not input_file.exists():
            print_error(f"File not found: {input_file}")
            raise typer.Exit(code=1)
        
        # Initialize prompt manager
        project_dir = None
        engine = Engine()
        engine.initialize()
        current_project = engine.get_current_project()
        if current_project:
            project_dir = Path(engine.config.projects_dir) / current_project['project_id']
        engine.shutdown()
        
        prompt_manager = create_prompt_manager(project_dir)
        
        # Parse scope
        pscope = PromptScope(scope.lower()) if scope else None
        
        # Import
        count = prompt_manager.import_prompts(input_file, scope=pscope, overwrite=overwrite)
        
        console.print()
        print_success(f"Imported {count} prompt(s) from {input_file}", prefix="✓")
        console.print()
        
    except ValueError as e:
        print_error(f"Invalid scope: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"Failed to import prompts: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
