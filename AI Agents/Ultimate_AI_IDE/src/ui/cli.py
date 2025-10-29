"""
Command Line Interface

Main CLI controller for UAIDE using Click framework.
"""

import click
import sys
from pathlib import Path
from typing import Optional
import logging

from .commands.workflow_commands import workflow, split, deadcode, automation
from .commands.quality_commands import bloat, quality, context, index
from .commands.mcp_commands import mcp
from .commands.security_commands import security
from .commands.dependency_commands import deps
from .commands.template_commands import template
from .commands.rag_commands import rag

from ..config.config import Config
from ..db.database import Database
from ..ai.backend import AIBackend
from ..utils import setup_logger

setup_logger('uaide', 'INFO', 'logs/uaide.log')

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='1.6.0')
@click.option('--config', '-c', default='config.json', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, config: str, verbose: bool):
    """Ultimate AI-Powered IDE - Command Line Interface v1.6.0"""
    # Initialize context
    ctx.ensure_object(dict)
    
    # Load configuration
    cfg = Config(config)
    cfg.load()
    ctx.obj['config'] = cfg
    
    # Setup logging
    log_level = 'DEBUG' if verbose else cfg.get('logging.level', 'INFO')
    log_file = cfg.get('logging.file', 'logs/uaide.log')
    setup_logger('uaide', log_level, log_file)
    
    # Initialize database
    db = Database(cfg.get('database.path', 'data/uaide.db'))
    if not db.connect():
        click.echo("Error: Could not connect to database", err=True)
        sys.exit(1)
    if not db.initialize():
        click.echo("Error: Could not initialize database", err=True)
        sys.exit(1)
    ctx.obj['db'] = db
    
    logger.info("UAIDE CLI initialized")


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize UAIDE in current directory"""
    click.echo("Initializing UAIDE...")
    
    cfg = ctx.obj['config']
    
    # Create necessary directories
    dirs = ['data', 'logs', 'models']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
        click.echo(f"✓ Created directory: {d}")
    
    # Create config file if it doesn't exist
    if not Path('config.json').exists():
        cfg.save('config.json')
        click.echo("✓ Created config.json")
    
    click.echo("\n✓ UAIDE initialized successfully!")
    click.echo("\nNext steps:")
    click.echo("  1. Download a model to models/ directory")
    click.echo("  2. Update config.json with model path")
    click.echo("  3. Run 'uaide status' to verify setup")


@cli.command()
@click.argument('name')
@click.option('--language', '-l', help='Programming language')
@click.option('--framework', '-f', help='Framework')
@click.option('--path', '-p', default='.', help='Project path')
@click.pass_context
def new_project(ctx, name: str, language: Optional[str], framework: Optional[str], path: str):
    """Create a new project"""
    from ..db.models import Project
    
    click.echo(f"Creating new project: {name}")
    
    db = ctx.obj['db']
    project_path = Path(path) / name
    
    # Check if project already exists
    existing = db.get_project_by_path(str(project_path))
    if existing:
        click.echo(f"Error: Project already exists at {project_path}", err=True)
        return
    
    # Create project
    project = Project(
        name=name,
        path=str(project_path),
        language=language,
        framework=framework
    )
    
    project_id = db.add_project(project)
    if project_id:
        click.echo(f"✓ Project created with ID: {project_id}")
        click.echo(f"  Path: {project_path}")
        if language:
            click.echo(f"  Language: {language}")
        if framework:
            click.echo(f"  Framework: {framework}")
    else:
        click.echo("Error: Could not create project", err=True)


@cli.command()
@click.pass_context
def status(ctx):
    """Show UAIDE status"""
    cfg = ctx.obj['config']
    db = ctx.obj['db']
    
    click.echo("=== UAIDE Status ===\n")
    
    # Configuration
    click.echo("Configuration:")
    click.echo(f"  Config file: {cfg.config_path}")
    click.echo(f"  Database: {cfg.get('database.path')}")
    click.echo(f"  Model path: {cfg.get('ai.model_path')}")
    
    # Database
    projects = db.list_projects()
    click.echo(f"\nProjects: {len(projects)}")
    for p in projects[:5]:
        click.echo(f"  - {p.name} ({p.language or 'unknown'})")
    
    # AI Backend
    model_path = cfg.get('ai.model_path')
    model_exists = Path(model_path).exists() if model_path else False
    
    # Check for llama.cpp binary
    llama_binary = None
    llama_dir = Path("llama-cpp")
    if llama_dir.exists():
        for binary_name in ["llama-cli.exe", "main.exe", "llama.exe", "llama-cli", "main", "llama"]:
            binary_path = llama_dir / binary_name
            if binary_path.exists():
                llama_binary = str(binary_path)
                break
    
    click.echo(f"\nAI Backend:")
    click.echo(f"  llama.cpp binary: {llama_binary if llama_binary else '✗ Not found'}")
    if llama_binary:
        click.echo(f"  Status: ✓ Found")
    else:
        click.echo(f"  Status: ✗ Not found - See docs/LLAMA_CPP_SETUP.md")
    
    click.echo(f"\nAI Model:")
    click.echo(f"  Path: {model_path}")
    click.echo(f"  Status: {'✓ Found' if model_exists else '✗ Not found'}")
    
    click.echo()


@cli.command()
@click.argument('text')
@click.option('--scope', type=click.Choice(['global', 'project']), default='global')
@click.option('--category', help='Rule category')
@click.option('--priority', type=int, default=0, help='Rule priority')
@click.pass_context
def add_rule(ctx, text: str, scope: str, category: Optional[str], priority: int):
    """Add a new rule"""
    from ..db.models import Rule
    
    db = ctx.obj['db']
    
    rule = Rule(
        rule_text=text,
        scope=scope,
        category=category,
        priority=priority
    )
    
    rule_id = db.add_rule(rule)
    if rule_id:
        click.echo(f"✓ Rule added with ID: {rule_id}")
    else:
        click.echo("Error: Could not add rule", err=True)


@cli.command()
@click.option('--scope', type=click.Choice(['global', 'project', 'all']), default='all')
@click.pass_context
def list_rules(ctx, scope: str):
    """List all rules"""
    db = ctx.obj['db']
    
    scope_filter = None if scope == 'all' else scope
    rules = db.get_rules(scope=scope_filter)
    
    if not rules:
        click.echo("No rules found")
        return
    
    click.echo(f"\n=== Rules ({len(rules)}) ===\n")
    for rule in rules:
        click.echo(f"[{rule.scope.upper()}] {rule.rule_text}")
        if rule.category:
            click.echo(f"  Category: {rule.category}")
        if rule.priority != 0:
            click.echo(f"  Priority: {rule.priority}")
        click.echo()


@cli.command()
@click.option('--key', help='Configuration key')
@click.option('--value', help='Configuration value')
@click.pass_context
def config(ctx, key: Optional[str], value: Optional[str]):
    """Get or set configuration values"""
    cfg = ctx.obj['config']
    
    if key and value:
        # Set value
        cfg.set(key, value)
        cfg.save()
        click.echo(f"✓ Set {key} = {value}")
    elif key:
        # Get value
        val = cfg.get(key)
        click.echo(f"{key} = {val}")
    else:
        # Show all config
        import json
        click.echo(json.dumps(cfg.get_all(), indent=2))


@cli.command()
@click.pass_context
def chat(ctx):
    """Interactive AI chat mode"""
    cfg = ctx.obj['config']
    
    click.echo("=== AI Chat Mode ===")
    click.echo("Type 'exit' or 'quit' to leave\n")
    
    # Initialize AI backend
    ai = AIBackend(cfg.get('ai'))
    model_path = cfg.get('ai.model_path')
    
    if not Path(model_path).exists():
        click.echo(f"Error: Model not found at {model_path}", err=True)
        click.echo("Please download a model and update config.json")
        return
    
    click.echo("Loading model...")
    if not ai.load_model(model_path):
        click.echo("Error: Could not load model", err=True)
        return
    
    click.echo("Model loaded! Start chatting:\n")
    
    try:
        while True:
            user_input = click.prompt("You", type=str)
            
            if user_input.lower() in ['exit', 'quit']:
                break
            
            response = ai.query_with_context(user_input)
            click.echo(f"AI: {response}\n")
    
    except KeyboardInterrupt:
        click.echo("\n\nExiting chat...")
    finally:
        ai.close()


# ============================================================================
# Import Command Modules
# ============================================================================

from .commands import (
    mcp,
    bloat, quality, context, index,
    workflow, split, deadcode, automation
)

# Register command groups
cli.add_command(mcp)
cli.add_command(bloat)
cli.add_command(security)
cli.add_command(deps)
cli.add_command(template)
cli.add_command(context)
cli.add_command(index)
cli.add_command(workflow)
cli.add_command(split)
cli.add_command(deadcode)
cli.add_command(automation)
cli.add_command(rag)


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    cli(obj={})
