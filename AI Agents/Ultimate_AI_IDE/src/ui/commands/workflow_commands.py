"""
Workflow & Automation Commands

Commands for workflow execution, file splitting, dead code detection, and automation.
"""

import click


@click.group()
def workflow():
    """Workflow management commands"""
    pass


@workflow.command('list')
def workflow_list():
    """List available workflow templates"""
    from ...modules.workflow_engine import WorkflowTemplates
    
    templates = WorkflowTemplates.list_templates()
    
    click.echo("\n=== Available Workflow Templates ===\n")
    for name, description in templates.items():
        click.echo(f"  {name}")
        click.echo(f"    {description}\n")


@workflow.command('execute')
@click.argument('template_name')
@click.option('--project', '-p', help='Project path')
@click.option('--var', '-v', multiple=True, help='Variable in key=value format')
def workflow_execute(template_name, project, var):
    """Execute a workflow template"""
    from ...core.orchestrator import UAIDE
    
    # Parse variables
    variables = {}
    if project:
        variables['project_path'] = project
    
    for v in var:
        if '=' in v:
            key, value = v.split('=', 1)
            variables[key] = value
    
    try:
        uaide = UAIDE()
        click.echo(f"Executing workflow: {template_name}...")
        
        result = uaide.execute_workflow(template_name, variables)
        
        if result.success:
            click.echo(f"\n✓ {result.message}")
            if result.data:
                click.echo(f"\nCompleted steps: {len(result.data.get('steps', {}))}")
        else:
            click.echo(f"\n✗ {result.message}", err=True)
            if result.errors:
                for error in result.errors:
                    click.echo(f"  - {error}", err=True)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@workflow.command('info')
@click.argument('template_name')
def workflow_info(template_name):
    """Show workflow template information"""
    from ...modules.workflow_engine import WorkflowTemplates
    
    try:
        template = WorkflowTemplates.get_template(template_name)
        
        click.echo(f"\n=== {template['name']} ===\n")
        click.echo(f"Description: {template.get('description', 'N/A')}")
        click.echo(f"Version: {template.get('version', '1.0')}")
        click.echo(f"Steps: {len(template['steps'])}\n")
        
        click.echo("Workflow steps:")
        for i, step in enumerate(template['steps'], 1):
            click.echo(f"  {i}. {step['name']}")
            click.echo(f"     Action: {step['action']}")
            if step.get('depends_on'):
                click.echo(f"     Depends on: {', '.join(step['depends_on']) if isinstance(step['depends_on'], list) else step['depends_on']}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@click.group()
def split():
    """File splitting commands"""
    pass


@split.command('detect')
@click.option('--project', '-p', default='.', help='Project path')
@click.option('--max-lines', '-m', default=500, help='Maximum lines per file')
def split_detect(project, max_lines):
    """Detect large files that should be split"""
    from ...core.orchestrator import UAIDE
    
    try:
        uaide = UAIDE()
        result = uaide.detect_large_files(project)
        
        if result.success:
            large_files = result.data.get('large_files', [])
            
            if not large_files:
                click.echo("✓ No large files found!")
            else:
                click.echo(f"\n=== Found {len(large_files)} Large Files ===\n")
                for file_info in large_files:
                    click.echo(f"  {file_info['path']}")
                    click.echo(f"    Lines: {file_info['lines']} (excess: {file_info['excess']})")
                    click.echo(f"    Language: {file_info['language']}\n")
        else:
            click.echo(f"Error: {result.message}", err=True)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@split.command('suggest')
@click.argument('file_path')
def split_suggest(file_path):
    """Suggest split points for a file"""
    from ...modules.file_splitter import FileSplitter
    
    try:
        splitter = FileSplitter()
        suggestions = splitter.suggest_split_points(file_path)
        
        if suggestions.get('success'):
            click.echo(f"\n=== Split Suggestions for {file_path} ===\n")
            click.echo(f"Total lines: {suggestions['total_lines']}")
            click.echo(f"Classes: {suggestions.get('classes', 0)}")
            click.echo(f"Functions: {suggestions.get('functions', 0)}\n")
            
            click.echo("Suggested strategies:")
            for suggestion in suggestions.get('suggestions', []):
                click.echo(f"\n  Strategy: {suggestion['strategy']}")
                click.echo(f"  {suggestion['description']}")
                click.echo(f"  Resulting files: ~{suggestion['files']}")
        else:
            click.echo(f"Error: {suggestions.get('error', 'Unknown error')}", err=True)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@split.command('execute')
@click.argument('file_path')
@click.option('--strategy', '-s', default='auto', help='Split strategy')
@click.option('--dry-run', is_flag=True, help='Show what would be done without doing it')
def split_execute(file_path, strategy, dry_run):
    """Split a large file"""
    from ...core.orchestrator import UAIDE
    
    try:
        uaide = UAIDE()
        
        if dry_run:
            click.echo(f"[DRY RUN] Would split {file_path} using strategy: {strategy}")
            return
        
        click.echo(f"Splitting {file_path}...")
        result = uaide.split_file(file_path, strategy)
        
        if result.success:
            click.echo(f"\n✓ {result.message}")
            if result.data.get('files_created'):
                click.echo("\nCreated files:")
                for new_file in result.data['files_created']:
                    click.echo(f"  - {new_file}")
        else:
            click.echo(f"\n✗ {result.message}", err=True)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@click.group()
def deadcode():
    """Dead code detection commands"""
    pass


@deadcode.command('detect')
@click.option('--project', '-p', default='.', help='Project path')
def deadcode_detect(project):
    """Detect dead code in project"""
    from ...core.orchestrator import UAIDE
    
    try:
        uaide = UAIDE()
        click.echo("Analyzing project for dead code...")
        
        result = uaide.detect_dead_code(project)
        
        if result.success:
            data = result.data
            click.echo(f"\n✓ {result.message}\n")
            
            # Show unused functions
            if data.get('unused_functions'):
                click.echo(f"Unused Functions ({len(data['unused_functions'])}):")
                for item in data['unused_functions'][:10]:
                    click.echo(f"  - {item['name']} in {item['file']}")
                    click.echo(f"    {item['reason']}")
            
            # Show unused classes
            if data.get('unused_classes'):
                click.echo(f"\nUnused Classes ({len(data['unused_classes'])}):")
                for item in data['unused_classes'][:10]:
                    click.echo(f"  - {item['name']} in {item['file']}")
            
            # Show unreachable code
            if data.get('unreachable_code'):
                click.echo(f"\nUnreachable Code ({len(data['unreachable_code'])}):")
                for item in data['unreachable_code'][:10]:
                    click.echo(f"  - {item['file']}:{item['line']} in {item['function']}")
            
            # Show orphaned files
            if data.get('orphaned_files'):
                click.echo(f"\nOrphaned Files ({len(data['orphaned_files'])}):")
                for item in data['orphaned_files'][:10]:
                    click.echo(f"  - {item['file']}")
        else:
            click.echo(f"Error: {result.message}", err=True)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@click.group()
def automation():
    """Automation engine commands"""
    pass


@automation.command('status')
def automation_status():
    """Show automation engine status"""
    from ...core.orchestrator import UAIDE
    
    try:
        uaide = UAIDE()
        stats = uaide.automation_engine.get_stats()
        
        click.echo("\n=== Automation Engine Status ===\n")
        click.echo(f"Enabled: {'Yes' if stats['enabled'] else 'No'}")
        click.echo(f"Triggers registered: {stats['triggers_registered']}")
        click.echo(f"Actions registered: {stats['actions_registered']}")
        click.echo(f"Triggers fired: {stats['triggers_fired']}")
        click.echo(f"Actions executed: {stats['actions_executed']}")
        click.echo(f"Actions failed: {stats['actions_failed']}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@automation.command('enable')
def automation_enable():
    """Enable automation engine"""
    from ...core.orchestrator import UAIDE
    
    try:
        uaide = UAIDE()
        uaide.automation_engine.enable()
        click.echo("✓ Automation engine enabled")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@automation.command('disable')
def automation_disable():
    """Disable automation engine"""
    from ...core.orchestrator import UAIDE
    
    try:
        uaide = UAIDE()
        uaide.automation_engine.disable()
        click.echo("✓ Automation engine disabled")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@automation.command('triggers')
def automation_triggers():
    """List all automation triggers"""
    from ...core.orchestrator import UAIDE
    
    try:
        uaide = UAIDE()
        triggers = uaide.automation_engine.list_triggers()
        
        click.echo("\n=== Automation Triggers ===\n")
        for trigger_type, rules in triggers.items():
            click.echo(f"{trigger_type}:")
            for rule in rules:
                status = "✓" if rule['enabled'] else "✗"
                click.echo(f"  {status} {rule['action']} (priority: {rule['priority']})")
            click.echo()
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
