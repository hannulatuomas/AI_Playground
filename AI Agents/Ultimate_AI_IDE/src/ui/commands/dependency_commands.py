"""
Dependency Management CLI Commands

Commands for managing project dependencies.
"""

import click
from pathlib import Path
from ...modules.dependency_manager import DependencyManager


@click.group()
def deps():
    """Dependency management commands."""
    pass


@deps.command()
@click.option('--project', '-p', default='.', help='Project path')
def check(project):
    """
    Check for outdated dependencies.
    
    Example:
        uaide deps check
        uaide deps check --project ./my_project
    """
    try:
        click.echo("🔍 Checking for outdated dependencies...\n")
        
        manager = DependencyManager(project)
        updates = manager.check_outdated()
        
        if not updates:
            click.secho("✓ All dependencies are up to date!", fg='green', bold=True)
            return
        
        click.echo(f"Found {len(updates)} outdated dependencies:\n")
        
        # Group by breaking/non-breaking
        breaking = [u for u in updates if u.is_breaking]
        safe = [u for u in updates if not u.is_breaking]
        
        if breaking:
            click.secho("⚠️  Breaking Changes (Major Version):", fg='red', bold=True)
            for update in breaking:
                click.echo(f"  • {update.name}: {update.current_version} → {update.latest_version}")
            click.echo()
        
        if safe:
            click.secho("✓ Safe Updates (Minor/Patch):", fg='green')
            for update in safe:
                click.echo(f"  • {update.name}: {update.current_version} → {update.latest_version}")
        
    except Exception as e:
        raise click.ClickException(f"Failed to check dependencies: {e}")


@deps.command()
@click.option('--project', '-p', default='.', help='Project path')
@click.option('--package', multiple=True, help='Specific packages to update')
@click.option('--no-test', is_flag=True, help='Skip running tests')
@click.option('--no-rollback', is_flag=True, help='Disable automatic rollback')
@click.option('--safe-only', is_flag=True, help='Only update non-breaking changes')
def update(project, package, no_test, no_rollback, safe_only):
    """
    Update dependencies with testing and rollback.
    
    Examples:
        uaide deps update  # Update all
        uaide deps update --package requests  # Update specific package
        uaide deps update --safe-only  # Only safe updates
        uaide deps update --no-test  # Skip tests
    """
    try:
        manager = DependencyManager(project)
        
        # Get packages to update
        packages_to_update = list(package) if package else None
        
        # If safe-only, filter to non-breaking updates
        if safe_only and not packages_to_update:
            click.echo("🔍 Finding safe updates...")
            safe_updates = manager.suggest_safe_updates()
            packages_to_update = [u.name for u in safe_updates]
            
            if not packages_to_update:
                click.secho("✓ No safe updates available", fg='green')
                return
            
            click.echo(f"Will update {len(packages_to_update)} packages safely\n")
        
        click.echo("📦 Updating dependencies...")
        if not no_test:
            click.echo("   (Tests will run after update)")
        
        result = manager.update_dependencies(
            packages=packages_to_update,
            test_after=not no_test,
            rollback_on_failure=not no_rollback
        )
        
        if result.success:
            click.secho(f"\n✓ Successfully updated {len(result.updated)} dependencies", fg='green', bold=True)
            for pkg in result.updated:
                click.echo(f"  • {pkg}")
            
            if result.test_results:
                if result.test_results.get('success'):
                    click.secho("\n✓ All tests passed", fg='green')
                else:
                    click.secho("\n⚠️  Some tests failed", fg='yellow')
        else:
            click.secho("\n✗ Update failed", fg='red', bold=True)
            
            if result.failed:
                click.echo("\nFailed packages:")
                for pkg in result.failed:
                    click.echo(f"  • {pkg}")
            
            if result.rolled_back:
                click.secho("\n↩️  Changes have been rolled back", fg='yellow')
            
            if result.errors:
                click.echo("\nErrors:")
                for error in result.errors:
                    click.echo(f"  • {error}")
    
    except Exception as e:
        raise click.ClickException(f"Update failed: {e}")


@deps.command()
@click.option('--project', '-p', default='.', help='Project path')
def safe(project):
    """
    List safe (non-breaking) updates.
    
    Example:
        uaide deps safe
    """
    try:
        manager = DependencyManager(project)
        safe_updates = manager.suggest_safe_updates()
        
        if not safe_updates:
            click.secho("✓ No safe updates available", fg='green')
            return
        
        click.echo(f"Found {len(safe_updates)} safe updates:\n")
        
        for update in safe_updates:
            click.echo(f"  • {update.name}: {update.current_version} → {update.latest_version}")
        
        click.echo(f"\n💡 Run 'uaide deps update --safe-only' to apply these updates")
    
    except Exception as e:
        raise click.ClickException(f"Failed to check safe updates: {e}")


@deps.command()
@click.option('--project', '-p', default='.', help='Project path')
def info(project):
    """
    Show dependency manager information.
    
    Example:
        uaide deps info
    """
    try:
        manager = DependencyManager(project)
        
        click.echo("📦 Dependency Manager Information\n")
        click.echo(f"Project: {manager.project_path}")
        click.echo(f"Package Manager: {manager.package_manager}")
        
        if manager.backup_dir.exists():
            backups = list(manager.backup_dir.iterdir())
            click.echo(f"Backups: {len(backups)}")
        else:
            click.echo("Backups: 0")
    
    except Exception as e:
        raise click.ClickException(f"Failed to get info: {e}")
