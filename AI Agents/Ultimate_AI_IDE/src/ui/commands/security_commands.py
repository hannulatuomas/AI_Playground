"""
Security CLI Commands

Commands for security scanning and vulnerability management.
"""

import click
from pathlib import Path
from ...modules.security_scanner import SecurityScanner


@click.group()
def security():
    """Security scanning and vulnerability management commands."""
    pass


@security.command()
@click.option('--project', '-p', default='.', help='Project path to scan')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'html', 'markdown', 'sarif']), 
              default='text', help='Report format')
@click.option('--output', '-o', help='Output file path (default: stdout)')
@click.option('--no-vulnerabilities', is_flag=True, help='Skip vulnerability scanning')
@click.option('--no-dependencies', is_flag=True, help='Skip dependency checking')
@click.option('--no-patterns', is_flag=True, help='Skip pattern detection')
@click.option('--no-secrets', is_flag=True, help='Skip secret scanning')
def scan(project, format, output, no_vulnerabilities, no_dependencies, no_patterns, no_secrets):
    """
    Run comprehensive security scan on project.
    
    Examples:
        uaide security scan
        uaide security scan --project ./my_project
        uaide security scan --format json --output report.json
        uaide security scan --no-secrets  # Skip secret scanning
    """
    try:
        click.echo(f"🔒 Starting security scan of {project}...")
        
        scanner = SecurityScanner(project)
        result = scanner.scan_project(
            scan_vulnerabilities=not no_vulnerabilities,
            scan_dependencies=not no_dependencies,
            scan_patterns=not no_patterns,
            scan_secrets=not no_secrets
        )
        
        # Generate report
        report = scanner.generate_report(result, format)
        
        # Output report
        if output:
            Path(output).write_text(report)
            click.echo(f"✓ Report saved to {output}")
        else:
            click.echo(report)
        
        # Summary
        click.echo(f"\n📊 Scan Summary:")
        click.echo(f"  Total Issues: {result.summary['total']}")
        click.echo(f"  Risk Score: {result.risk_score:.1f}/100")
        
        if result.summary['critical'] > 0:
            click.secho(f"  ⚠️  Critical: {result.summary['critical']}", fg='red', bold=True)
        if result.summary['high'] > 0:
            click.secho(f"  ⚠️  High: {result.summary['high']}", fg='yellow')
        
        # Exit with error code if critical issues found
        if result.summary['critical'] > 0:
            raise click.ClickException("Critical security issues found!")
        
    except Exception as e:
        raise click.ClickException(f"Security scan failed: {e}")


@security.command()
@click.argument('cve_id')
def check(cve_id):
    """
    Check specific CVE information.
    
    Example:
        uaide security check CVE-2024-1234
    """
    try:
        from ...modules.security_scanner import VulnerabilityScanner
        
        scanner = VulnerabilityScanner()
        cve_info = scanner.check_cve(cve_id)
        
        if cve_info:
            click.echo(f"\n📋 CVE Information: {cve_id}")
            click.echo(f"  Description: {cve_info.description}")
            click.echo(f"  CVSS Score: {cve_info.cvss_score}")
            click.echo(f"  Severity: {cve_info.severity}")
            if cve_info.fixed_versions:
                click.echo(f"  Fixed in: {', '.join(cve_info.fixed_versions)}")
        else:
            click.echo(f"No information found for {cve_id}")
            
    except Exception as e:
        raise click.ClickException(f"CVE check failed: {e}")


@security.command()
@click.option('--project', '-p', default='.', help='Project path')
@click.option('--severity', type=click.Choice(['critical', 'high', 'medium', 'low']),
              help='Filter by severity')
def list(project, severity):
    """
    List security issues in project.
    
    Example:
        uaide security list
        uaide security list --severity critical
    """
    try:
        scanner = SecurityScanner(project)
        result = scanner.scan_project()
        
        issues = result.issues
        if severity:
            issues = [i for i in issues if i.severity == severity]
        
        if not issues:
            click.echo("✓ No security issues found!")
            return
        
        click.echo(f"\n🔍 Found {len(issues)} security issues:\n")
        
        for i, issue in enumerate(issues, 1):
            severity_color = {
                'critical': 'red',
                'high': 'yellow',
                'medium': 'blue',
                'low': 'green'
            }.get(issue.severity, 'white')
            
            click.secho(f"{i}. [{issue.severity.upper()}] {issue.title}", fg=severity_color, bold=True)
            click.echo(f"   Category: {issue.category}")
            if issue.file_path:
                location = issue.file_path
                if issue.line_number:
                    location += f":{issue.line_number}"
                click.echo(f"   Location: {location}")
            click.echo(f"   {issue.description}\n")
            
    except Exception as e:
        raise click.ClickException(f"Failed to list issues: {e}")


@security.command()
@click.option('--project', '-p', default='.', help='Project path')
@click.option('--auto', is_flag=True, help='Automatically apply fixes')
def fix(project, auto):
    """
    Get fix recommendations for security issues.
    
    Example:
        uaide security fix
        uaide security fix --auto  # Apply fixes automatically
    """
    try:
        scanner = SecurityScanner(project)
        result = scanner.scan_project()
        
        fixable = [i for i in result.issues if i.fix_available]
        
        if not fixable:
            click.echo("No fixable issues found.")
            return
        
        click.echo(f"\n🔧 Found {len(fixable)} fixable issues:\n")
        
        for i, issue in enumerate(fixable, 1):
            click.echo(f"{i}. {issue.title}")
            click.echo(f"   Fix: {issue.fix_description}")
            
            if auto:
                click.echo("   [Auto-fix not yet implemented]")
            click.echo()
        
        if not auto:
            click.echo("💡 Tip: Use --auto to automatically apply fixes (when available)")
            
    except Exception as e:
        raise click.ClickException(f"Fix operation failed: {e}")


@security.command()
@click.option('--project', '-p', default='.', help='Project path')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'html', 'markdown']),
              default='text', help='Report format')
@click.option('--output', '-o', help='Output file path')
def report(project, format, output):
    """
    Generate detailed security report.
    
    Example:
        uaide security report --format html --output security_report.html
    """
    try:
        click.echo("📊 Generating security report...")
        
        scanner = SecurityScanner(project)
        result = scanner.scan_project()
        report_content = scanner.generate_report(result, format)
        
        if output:
            Path(output).write_text(report_content)
            click.echo(f"✓ Report saved to {output}")
        else:
            click.echo(report_content)
            
    except Exception as e:
        raise click.ClickException(f"Report generation failed: {e}")


@security.command()
@click.option('--project', '-p', default='.', help='Project path')
def secrets(project):
    """
    Scan for exposed secrets and credentials.
    
    Example:
        uaide security secrets
    """
    try:
        from ...modules.security_scanner import SecretScanner
        
        click.echo("🔐 Scanning for exposed secrets...")
        
        scanner = SecretScanner()
        issues = scanner.scan(Path(project))
        
        if not issues:
            click.secho("✓ No exposed secrets found!", fg='green', bold=True)
            return
        
        click.secho(f"\n⚠️  Found {len(issues)} exposed secrets!", fg='red', bold=True)
        click.echo("\n⚠️  CRITICAL: Rotate these credentials immediately!\n")
        
        for i, issue in enumerate(issues, 1):
            click.echo(f"{i}. {issue.title}")
            if issue.file_path:
                click.echo(f"   File: {issue.file_path}:{issue.line_number}")
            click.echo(f"   {issue.description}\n")
        
        click.echo("💡 Recommended actions:")
        click.echo("  1. Remove hardcoded secrets from code")
        click.echo("  2. Use environment variables or secret management")
        click.echo("  3. Rotate all exposed credentials")
        click.echo("  4. Add secrets to .gitignore")
        
    except Exception as e:
        raise click.ClickException(f"Secret scan failed: {e}")


@security.command()
@click.option('--project', '-p', default='.', help='Project path')
def patterns(project):
    """
    Detect insecure coding patterns.
    
    Example:
        uaide security patterns
    """
    try:
        from ...modules.security_scanner import PatternDetector
        
        click.echo("🔍 Detecting insecure patterns...")
        
        detector = PatternDetector()
        issues = detector.detect(Path(project))
        
        if not issues:
            click.secho("✓ No insecure patterns found!", fg='green', bold=True)
            return
        
        click.echo(f"\nFound {len(issues)} insecure patterns:\n")
        
        # Group by severity
        by_severity = {}
        for issue in issues:
            by_severity.setdefault(issue.severity, []).append(issue)
        
        for severity in ['critical', 'high', 'medium', 'low']:
            if severity in by_severity:
                color = {'critical': 'red', 'high': 'yellow', 'medium': 'blue', 'low': 'green'}[severity]
                click.secho(f"\n{severity.upper()} Severity:", fg=color, bold=True)
                for issue in by_severity[severity]:
                    click.echo(f"  • {issue.title}")
                    if issue.file_path:
                        click.echo(f"    {issue.file_path}:{issue.line_number}")
                    click.echo(f"    Fix: {issue.fix_description}\n")
        
    except Exception as e:
        raise click.ClickException(f"Pattern detection failed: {e}")
