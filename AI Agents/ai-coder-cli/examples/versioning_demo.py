#!/usr/bin/env python3
"""
Versioning System Demo - Demonstrates the automated versioning capabilities

This example shows how to use the versioning tool for:
1. Getting current version
2. Analyzing changes
3. Manual version bumping
4. Automatic version bumping
5. Updating version files
6. Creating git tags
7. Full release workflow

Usage:
    python examples/versioning_demo.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.versioning import VersioningTool
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def print_section(title: str):
    """Print a section header."""
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print("=" * 60)


def print_result(result: dict):
    """Print a result dictionary in a formatted way."""
    if result.get('success'):
        console.print("[green]✓ Success[/green]")
    else:
        console.print("[red]✗ Failed[/red]")
    
    for key, value in result.items():
        if key not in ['success', 'analysis', 'steps', 'version_parts']:
            console.print(f"  [yellow]{key}:[/yellow] {value}")


def demo_get_version(versioning: VersioningTool):
    """Demo: Get current version."""
    print_section("1. Get Current Version")
    
    result = versioning.invoke({'action': 'get_version'})
    print_result(result)
    
    if result['success']:
        parts = result['version_parts']
        console.print(f"\n  Version breakdown:")
        console.print(f"    Major: {parts['major']}")
        console.print(f"    Minor: {parts['minor']}")
        console.print(f"    Patch: {parts['patch']}")


def demo_analyze_changes(versioning: VersioningTool):
    """Demo: Analyze changes."""
    print_section("2. Analyze Changes")
    
    # Sample commit messages
    sample_commits = [
        "feat: Add versioning system with semantic versioning support",
        "feat: Add virtual environment setup scripts",
        "fix: Update documentation links",
        "add: Create comprehensive versioning guide",
    ]
    
    console.print("\nAnalyzing sample commits:")
    for commit in sample_commits:
        console.print(f"  • {commit}")
    
    result = versioning.invoke({
        'action': 'analyze',
        'use_git': False,
        'commit_messages': sample_commits
    })
    
    print_result(result)
    
    if result['success']:
        analysis = result['analysis']
        
        # Create analysis table
        table = Table(title="Change Analysis")
        table.add_column("Category", style="cyan")
        table.add_column("Detected", style="yellow")
        
        table.add_row("Breaking Changes", "✓" if analysis['has_breaking_changes'] else "✗")
        table.add_row("New Features", "✓" if analysis['has_new_features'] else "✗")
        table.add_row("Bug Fixes", "✓" if analysis['has_bug_fixes'] else "✗")
        table.add_row("Deprecations", "✓" if analysis['has_deprecations'] else "✗")
        
        console.print()
        console.print(table)


def demo_version_bump_types(versioning: VersioningTool):
    """Demo: Different version bump types."""
    print_section("3. Version Bump Types (Simulation)")
    
    current = versioning.invoke({'action': 'get_version'})
    current_version = current['version']
    
    # Simulate different bump types
    from tools.lib.version_manager import VersionInfo, VersionBumpType
    
    version = VersionInfo.from_string(current_version)
    
    table = Table(title="Version Bump Examples")
    table.add_column("Bump Type", style="cyan")
    table.add_column("Current", style="yellow")
    table.add_column("New Version", style="green")
    table.add_column("Use Case", style="white")
    
    table.add_row(
        "PATCH",
        current_version,
        str(version.bump(VersionBumpType.PATCH)),
        "Bug fixes, documentation"
    )
    
    table.add_row(
        "MINOR",
        current_version,
        str(version.bump(VersionBumpType.MINOR)),
        "New features (backward compatible)"
    )
    
    table.add_row(
        "MAJOR",
        current_version,
        str(version.bump(VersionBumpType.MAJOR)),
        "Breaking changes"
    )
    
    console.print()
    console.print(table)


def demo_commit_message_patterns(versioning: VersioningTool):
    """Demo: Show commit message patterns."""
    print_section("4. Commit Message Patterns")
    
    patterns = [
        ("MAJOR", "Breaking Changes", [
            "BREAKING: Remove deprecated API",
            "feat: Change interface (backward incompatible)",
        ]),
        ("MINOR", "New Features", [
            "feat: Add new feature",
            "feature: Implement new capability",
            "add: New tool for version management",
        ]),
        ("PATCH", "Bug Fixes", [
            "fix: Correct memory leak",
            "bugfix: Resolve issue with parsing",
            "patch: Fix typo in documentation",
        ]),
    ]
    
    for bump_type, category, examples in patterns:
        console.print(f"\n[bold]{bump_type} - {category}:[/bold]")
        for example in examples:
            console.print(f"  [green]✓[/green] {example}")


def demo_integration_example(versioning: VersioningTool):
    """Demo: Integration with Git Agent."""
    print_section("5. Integration with Git Agent")
    
    code = '''
from agents import GitAgent

# Initialize git agent
git_agent = GitAgent()

# Option 1: Commit with automatic version detection
result = git_agent.commit_with_versioning(
    message="feat: Add new features",
    bump_type=None,  # Auto-detect from commit message
    create_tag=True  # Create git tag
)

# Option 2: Manual version bump
result = git_agent.commit_with_versioning(
    message="Release version 2.6.0",
    bump_type='minor',  # Specify bump type
    create_tag=True
)

# Option 3: Using context
context = {
    'enable_versioning': True,
    'version_bump_type': 'minor',
    'create_version_tag': True
}
result = git_agent.execute('commit with message "feat: ..."', context)
'''
    
    console.print("\n[dim]" + code + "[/dim]")


def demo_full_workflow():
    """Demo: Complete release workflow."""
    print_section("6. Full Release Workflow Example")
    
    workflow = '''
Step-by-step release process:

1. Develop features
   └─ Make code changes
   └─ Test changes
   └─ Update documentation

2. Commit with descriptive messages
   └─ git commit -m "feat: Add new feature"
   └─ git commit -m "fix: Resolve bug"

3. Analyze changes (optional)
   └─ versioning.invoke({'action': 'analyze'})
   └─ Review suggested bump

4. Create release
   └─ versioning.invoke({'action': 'full_release'})
   OR
   └─ git_agent.commit_with_versioning(...)

5. Automatic steps performed:
   ✓ Analyze commits
   ✓ Bump version (2.5.0 → 2.6.0)
   ✓ Update VERSION file
   ✓ Update version in all project files
   ✓ Stage updated files
   ✓ Commit changes
   ✓ Create git tag (v2.6.0)

6. Push changes
   └─ git push origin main --tags
'''
    
    console.print(workflow)


def main():
    """Run all demos."""
    console.print(Panel.fit(
        "[bold cyan]AI Agent Console - Versioning System Demo[/bold cyan]\n"
        "Demonstrates automated version management with semantic versioning",
        border_style="cyan"
    ))
    
    # Initialize versioning tool
    try:
        versioning = VersioningTool(config={'project_root': project_root})
        console.print("\n[green]✓ Versioning tool initialized[/green]")
    except Exception as e:
        console.print(f"\n[red]✗ Error initializing versioning tool: {e}[/red]")
        return 1
    
    # Run demos
    try:
        demo_get_version(versioning)
        demo_analyze_changes(versioning)
        demo_version_bump_types(versioning)
        demo_commit_message_patterns(versioning)
        demo_integration_example(versioning)
        demo_full_workflow()
        
        # Summary
        console.print(Panel.fit(
            "[bold green]Demo Complete![/bold green]\n\n"
            "Key Features:\n"
            "  ✓ Semantic versioning (MAJOR.MINOR.PATCH)\n"
            "  ✓ Automatic change detection\n"
            "  ✓ Multi-file version updates\n"
            "  ✓ Git integration\n"
            "  ✓ Agent integration\n\n"
            "For more information:\n"
            "  📖 docs/guides/VERSIONING_SYSTEM.md\n"
            "  📖 docs/guides/VIRTUAL_ENV_SETUP.md",
            border_style="green"
        ))
        
        return 0
        
    except Exception as e:
        console.print(f"\n[red]✗ Error during demo: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
