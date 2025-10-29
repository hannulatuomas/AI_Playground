"""
Template Validation CLI Commands

Commands for validating scaffolded projects.
"""

import click
from pathlib import Path
from ...modules.template_validator import TemplateValidator


@click.group()
def template():
    """Template validation commands."""
    pass


@template.command()
@click.option('--project', '-p', default='.', help='Project path to validate')
@click.option('--strict', is_flag=True, help='Fail on any issues')
def validate(project, strict):
    """
    Validate scaffolded project for bloat and incomplete code.
    
    Examples:
        uaide template validate
        uaide template validate --project ./my_project
        uaide template validate --strict
    """
    try:
        click.echo(f"🔍 Validating project: {project}\n")
        
        validator = TemplateValidator(project)
        result = validator.validate_project()
        
        # Display results
        if result['is_clean']:
            click.secho("✓ Project is clean! No issues found.", fg='green', bold=True)
            click.echo(f"\nCleanliness Score: {validator.get_clean_score():.1f}/100")
            return
        
        # Show summary
        summary = result['summary']
        click.echo(f"Found {result['total_issues']} issues:\n")
        
        if summary['example_code'] > 0:
            click.secho(f"  ⚠️  Example Code: {summary['example_code']}", fg='yellow')
        if summary['todo'] > 0:
            click.secho(f"  📝 TODOs/FIXMEs: {summary['todo']}", fg='blue')
        if summary['placeholder'] > 0:
            click.secho(f"  🚧 Placeholders: {summary['placeholder']}", fg='red')
        if summary['unused_dependency'] > 0:
            click.secho(f"  📦 Unused Dependencies: {summary['unused_dependency']}", fg='yellow')
        
        click.echo(f"\nBy Severity:")
        click.secho(f"  High:   {summary['high']}", fg='red' if summary['high'] > 0 else 'white')
        click.secho(f"  Medium: {summary['medium']}", fg='yellow' if summary['medium'] > 0 else 'white')
        click.secho(f"  Low:    {summary['low']}", fg='green' if summary['low'] > 0 else 'white')
        
        click.echo(f"\nCleanliness Score: {validator.get_clean_score():.1f}/100")
        
        # Show detailed issues
        click.echo("\nDetailed Issues:")
        for issue in result['issues'][:10]:  # Show first 10
            click.echo(f"\n  [{issue.severity.upper()}] {issue.issue_type}")
            click.echo(f"  File: {issue.file_path}:{issue.line_number}")
            click.echo(f"  {issue.description}")
            click.echo(f"  💡 {issue.suggestion}")
        
        if result['total_issues'] > 10:
            click.echo(f"\n  ... and {result['total_issues'] - 10} more issues")
        
        if strict and result['total_issues'] > 0:
            raise click.ClickException("Validation failed in strict mode")
    
    except Exception as e:
        raise click.ClickException(f"Validation failed: {e}")


@template.command()
@click.option('--project', '-p', default='.', help='Project path')
def score(project):
    """
    Get cleanliness score for project.
    
    Example:
        uaide template score
    """
    try:
        validator = TemplateValidator(project)
        result = validator.validate_project()
        score = validator.get_clean_score()
        
        click.echo(f"\n📊 Cleanliness Score: {score:.1f}/100")
        
        if score == 100:
            click.secho("🎉 Perfect! Project is completely clean.", fg='green', bold=True)
        elif score >= 80:
            click.secho("✓ Good! Minor issues found.", fg='green')
        elif score >= 60:
            click.secho("⚠️  Fair. Some cleanup needed.", fg='yellow')
        else:
            click.secho("✗ Poor. Significant cleanup required.", fg='red')
        
        click.echo(f"\nTotal Issues: {result['total_issues']}")
    
    except Exception as e:
        raise click.ClickException(f"Failed to calculate score: {e}")
