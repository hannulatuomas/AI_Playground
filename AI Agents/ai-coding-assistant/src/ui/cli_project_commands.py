"""
Project Lifecycle CLI Commands
Extension for CLI to handle project lifecycle management commands.
"""

from pathlib import Path


def get_colors():
    """Get Colors class from CLI module."""
    from .cli import Colors
    return Colors


def cmd_project(self, args: str):
    """Handle project lifecycle commands."""
    Colors = get_colors()
    
    if not self.template_manager:
        print(self.colorize("\n✗ Project lifecycle not available", Colors.RED))
        return
    
    if not args:
        print(self.colorize("✗ Usage: project <subcommand> [args]", Colors.RED))
        print("  Subcommands: new, templates, init, check-deps, update-deps,")
        print("               scan-security, health, archive, changelog, release")
        return
    
    # Parse subcommand
    parts = args.split(maxsplit=1)
    subcommand = parts[0].lower()
    subargs = parts[1] if len(parts) > 1 else ""
    
    # Bind all sub-functions to self
    funcs = {
        'new': cmd_project_new,
        'templates': cmd_project_templates,
        'init': cmd_project_init,
        'check-deps': cmd_project_check_deps,
        'update-deps': cmd_project_update_deps,
        'scan-security': cmd_project_scan_security,
        'health': cmd_project_health,
        'archive': cmd_project_archive,
        'changelog': cmd_project_changelog,
        'release': cmd_project_release
    }
    
    if subcommand in funcs:
        funcs[subcommand](self, subargs)
    else:
        print(self.colorize(f"✗ Unknown project subcommand: {subcommand}", Colors.RED))
        print("  Valid: new, templates, init, check-deps, update-deps,")
        print("         scan-security, health, archive, changelog, release")


def cmd_project_new(self, args: str):
    """Create new project from template."""
    Colors = get_colors()
    
    # Parse arguments
    parts = args.split()
    if len(parts) < 2:
        print(self.colorize("✗ Usage: project new <template> <name> [--option value ...]", Colors.RED))
        print("  Example: project new web-react my-app --author \"John Doe\"")
        return
    
    template_name = parts[0]
    project_name = parts[1]
    
    # Parse options
    options = {}
    i = 2
    while i < len(parts):
        if parts[i].startswith('--'):
            option = parts[i][2:]
            if i + 1 < len(parts) and not parts[i + 1].startswith('--'):
                options[option] = parts[i + 1]
                i += 2
            else:
                options[option] = True
                i += 1
        else:
            i += 1
    
    # Get template
    template = self.template_manager.get_template(template_name)
    if not template:
        print(self.colorize(f"✗ Template not found: {template_name}", Colors.RED))
        print("  Use 'project templates' to see available templates")
        return
    
    # Build config
    config = {
        'PROJECT_NAME': project_name,
        'AUTHOR': options.get('author', ''),
        'LICENSE': options.get('license', 'MIT'),
        'DESCRIPTION': options.get('description', f'A new {template_name} project')
    }
    
    # Get destination
    dest = Path(options.get('dest', f"./{project_name}")).resolve()
    
    print(self.colorize(f"\n→ Creating project: {project_name}", Colors.YELLOW))
    print(f"  Template: {template_name}")
    print(f"  Destination: {dest}")
    print("  This may take a moment...\n")
    
    try:
        # Scaffold project
        success, message = self.project_scaffolder.scaffold_project(
            template, dest, config
        )
        
        if not success:
            print(self.colorize(f"✗ {message}", Colors.RED))
            return
        
        print(self.colorize("✓ Project scaffolded successfully!", Colors.GREEN))
        
        # Initialize git if not disabled
        if not options.get('no-git', False):
            success_git, msg_git = self.project_initializer.initialize_git(
                dest, "Initial commit from template"
            )
            if success_git:
                print(self.colorize("✓ Git initialized", Colors.GREEN))
        
        # Show setup instructions
        instructions = self.project_initializer.get_setup_instructions(dest)
        print(self.colorize("\n=== Next Steps ===", Colors.BOLD + Colors.CYAN))
        for instruction in instructions:
            print(instruction)
        
    except Exception as e:
        print(self.colorize(f"✗ Error: {e}", Colors.RED))


def cmd_project_templates(self, args: str):
    """List available templates."""
    Colors = get_colors()
    
    # Parse options
    search_query = None
    if '--search' in args:
        parts = args.split('--search', 1)
        if len(parts) > 1:
            search_query = parts[1].strip()
    
    templates = self.template_manager.list_templates()
    
    if search_query:
        templates = [t for t in templates if search_query.lower() in t.lower()]
        print(self.colorize(f"\nTemplates matching '{search_query}' ({len(templates)}):", Colors.BOLD + Colors.CYAN))
    else:
        print(self.colorize(f"\nAvailable Templates ({len(templates)}):", Colors.BOLD + Colors.CYAN))
    
    if not templates:
        print("  No templates found")
        return
    
    for template_name in templates:
        template = self.template_manager.get_template(template_name)
        if template:
            desc = template.get('description', 'No description')
            print(f"\n  • {self.colorize(template_name, Colors.BOLD)}")
            print(f"    {desc}")
            
            # Show languages/frameworks
            if 'tags' in template:
                tags = ', '.join(template['tags'])
                print(f"    Tags: {tags}")


def cmd_project_init(self, args: str):
    """Initialize existing folder as project."""
    Colors = get_colors()
    project_path = Path(self.current_project or '.').resolve()
    
    # Parse options
    options = {}
    for part in args.split():
        if part.startswith('--'):
            options[part[2:]] = True
    
    print(self.colorize(f"\n→ Initializing project: {project_path}", Colors.YELLOW))
    
    try:
        # Detect project type
        project_type = self.project_initializer.detect_project_type(project_path)
        if project_type:
            print(f"  Detected type: {project_type}")
        else:
            print("  Could not detect project type")
        
        # Initialize git if requested
        if options.get('git', False):
            success, msg = self.project_initializer.initialize_git(project_path)
            if success:
                print(self.colorize("✓ Git initialized", Colors.GREEN))
            else:
                print(self.colorize(f"⚠ {msg}", Colors.YELLOW))
        
        # Generate LICENSE if requested
        if 'license' in options:
            license_type = input("  License type (MIT/Apache-2.0/GPL-3.0): ").strip() or "MIT"
            author = input("  Author name: ").strip() or ""
            success, msg = self.project_initializer.generate_license_file(
                project_path, license_type, author
            )
            if success:
                print(self.colorize(f"✓ {msg}", Colors.GREEN))
        
        print(self.colorize("\n✓ Project initialized!", Colors.GREEN))
        
        # Show setup instructions
        instructions = self.project_initializer.get_setup_instructions(project_path)
        print(self.colorize("\n=== Setup Instructions ===", Colors.BOLD + Colors.CYAN))
        for instruction in instructions:
            print(instruction)
        
    except Exception as e:
        print(self.colorize(f"✗ Error: {e}", Colors.RED))


def cmd_project_check_deps(self, args: str):
    """Check for outdated dependencies."""
    Colors = get_colors()
    project_path = Path(self.current_project or '.').resolve()
    
    print(self.colorize(f"\n→ Checking dependencies in: {project_path}", Colors.YELLOW))
    print("  This may take a moment...\n")
    
    try:
        outdated = self.project_maintainer.check_outdated_deps(project_path)
        
        if not outdated:
            print(self.colorize("✓ All dependencies are up to date!", Colors.GREEN))
            return
        
        print(self.colorize(f"Found {len(outdated)} outdated dependencies:", Colors.BOLD + Colors.YELLOW))
        print()
        
        for pkg in outdated:
            print(f"  • {self.colorize(pkg['name'], Colors.BOLD)}")
            print(f"    Current: {pkg['current']}")
            print(f"    Latest:  {self.colorize(pkg['latest'], Colors.GREEN)}")
            print()
        
        print(self.colorize("⚠ Run 'project update-deps' for update commands", Colors.YELLOW))
        
    except Exception as e:
        print(self.colorize(f"✗ Error: {e}", Colors.RED))


def cmd_project_update_deps(self, args: str):
    """Show commands to update dependencies."""
    Colors = get_colors()
    project_path = Path(self.current_project or '.').resolve()
    
    print(self.colorize(f"\n→ Dependency update commands for: {project_path}", Colors.YELLOW))
    
    try:
        commands = self.project_maintainer.get_update_commands(project_path)
        
        if not commands:
            print("  No update commands available")
            return
        
        print()
        for cmd in commands:
            if cmd.startswith('#'):
                print(self.colorize(cmd, Colors.CYAN))
            else:
                print(f"  $ {cmd}")
        print()
        
    except Exception as e:
        print(self.colorize(f"✗ Error: {e}", Colors.RED))


def cmd_project_scan_security(self, args: str):
    """Scan for security vulnerabilities."""
    Colors = get_colors()
    project_path = Path(self.current_project or '.').resolve()
    
    print(self.colorize(f"\n→ Scanning for vulnerabilities in: {project_path}", Colors.YELLOW))
    print("  This may take a moment...\n")
    
    try:
        vulnerabilities = self.project_maintainer.scan_vulnerabilities(project_path)
        
        if not vulnerabilities:
            print(self.colorize("✓ No known vulnerabilities found!", Colors.GREEN))
            return
        
        # Count by severity
        critical = [v for v in vulnerabilities if v.get('severity', '').lower() == 'critical']
        high = [v for v in vulnerabilities if v.get('severity', '').lower() == 'high']
        
        print(self.colorize(f"Found {len(vulnerabilities)} vulnerabilities:", Colors.BOLD + Colors.RED))
        if critical:
            print(self.colorize(f"  • Critical: {len(critical)}", Colors.BG_RED + Colors.WHITE))
        if high:
            print(self.colorize(f"  • High: {len(high)}", Colors.RED))
        print()
        
        # Show details
        for vuln in vulnerabilities[:10]:  # Show first 10
            severity = vuln.get('severity', 'unknown').upper()
            color = Colors.RED if severity in ['CRITICAL', 'HIGH'] else Colors.YELLOW
            
            print(f"  {self.colorize(severity, color)}: {vuln.get('package', 'unknown')}")
            if 'title' in vuln:
                print(f"    {vuln['title']}")
            print()
        
        if len(vulnerabilities) > 10:
            print(f"  ... and {len(vulnerabilities) - 10} more\n")
        
    except Exception as e:
        print(self.colorize(f"✗ Error: {e}", Colors.RED))


def cmd_project_health(self, args: str):
    """Analyze code health."""
    Colors = get_colors()
    project_path = Path(self.current_project or '.').resolve()
    
    print(self.colorize(f"\n→ Analyzing code health: {project_path}", Colors.YELLOW))
    print()
    
    try:
        health = self.project_maintainer.analyze_code_health(project_path)
        
        if not health:
            print("  Could not analyze project")
            return
        
        print(self.colorize("=== Code Health Metrics ===", Colors.BOLD + Colors.CYAN))
        print(f"  Project type: {health.get('project_type', 'unknown')}")
        print(f"  Files: {health.get('file_count', 0)}")
        print(f"  Lines of code: {health.get('line_count', 0):,}")
        
        if health.get('issues'):
            print(f"\n  Issues: {len(health['issues'])}")
            for issue in health['issues'][:5]:
                print(f"    • {issue}")
        else:
            print(self.colorize("\n  ✓ No major issues detected", Colors.GREEN))
        
        print()
        
    except Exception as e:
        print(self.colorize(f"✗ Error: {e}", Colors.RED))


def cmd_project_archive(self, args: str):
    """Create project archive."""
    Colors = get_colors()
    project_path = Path(self.current_project or '.').resolve()
    
    # Parse format
    archive_format = "zip"
    if '--format' in args:
        parts = args.split('--format', 1)
        if len(parts) > 1:
            archive_format = parts[1].strip().split()[0]
    
    print(self.colorize(f"\n→ Creating {archive_format} archive of: {project_path}", Colors.YELLOW))
    print("  This may take a moment...\n")
    
    try:
        success, archive_path, message = self.project_archiver.create_archive(
            project_path, format=archive_format
        )
        
        if success and archive_path:
            print(self.colorize("✓ Archive created successfully!", Colors.GREEN))
            print(f"  Location: {archive_path}")
            size_mb = archive_path.stat().st_size / (1024 * 1024)
            print(f"  Size: {size_mb:.2f} MB")
        else:
            print(self.colorize(f"✗ {message}", Colors.RED))
        
    except Exception as e:
        print(self.colorize(f"✗ Error: {e}", Colors.RED))


def cmd_project_changelog(self, args: str):
    """Generate changelog."""
    Colors = get_colors()
    project_path = Path(self.current_project or '.').resolve()
    
    # Parse from tag
    from_tag = None
    if '--from' in args:
        parts = args.split('--from', 1)
        if len(parts) > 1:
            from_tag = parts[1].strip().split()[0]
    
    print(self.colorize(f"\n→ Generating changelog for: {project_path}", Colors.YELLOW))
    if from_tag:
        print(f"  From tag: {from_tag}")
    print()
    
    try:
        success, message = self.project_archiver.generate_changelog(
            project_path, from_tag=from_tag
        )
        
        if success:
            print(self.colorize("✓ Changelog generated!", Colors.GREEN))
            print(f"  {message}")
        else:
            print(self.colorize(f"✗ {message}", Colors.RED))
        
    except Exception as e:
        print(self.colorize(f"✗ Error: {e}", Colors.RED))


def cmd_project_release(self, args: str):
    """Prepare release."""
    Colors = get_colors()
    project_path = Path(self.current_project or '.').resolve()
    
    if not args.strip():
        print(self.colorize("✗ Usage: project release <version>", Colors.RED))
        print("  Example: project release 1.2.0")
        return
    
    version = args.strip().split()[0]
    
    print(self.colorize(f"\n→ Preparing release {version} for: {project_path}", Colors.YELLOW))
    print()
    
    try:
        # Generate release notes
        highlights = input("  Key highlights (comma-separated, or Enter to skip): ").strip()
        highlight_list = [h.strip() for h in highlights.split(',')] if highlights else None
        
        success, msg = self.project_archiver.generate_release_notes(
            project_path, version, highlights=highlight_list
        )
        
        if success:
            print(self.colorize("✓ Release notes generated!", Colors.GREEN))
        else:
            print(self.colorize(f"⚠ {msg}", Colors.YELLOW))
        
        # Bump version
        bump_type = input("  Bump type (major/minor/patch) [patch]: ").strip() or "patch"
        success_bump, new_version, msg_bump = self.project_archiver.bump_version(
            project_path, bump_type=bump_type
        )
        
        if success_bump:
            print(self.colorize(f"✓ {msg_bump}", Colors.GREEN))
        else:
            print(self.colorize(f"⚠ {msg_bump}", Colors.YELLOW))
        
        # Generate changelog
        success_log, msg_log = self.project_archiver.generate_changelog(project_path)
        if success_log:
            print(self.colorize("✓ Changelog updated!", Colors.GREEN))
        
        print(self.colorize("\n✓ Release preparation complete!", Colors.BOLD + Colors.GREEN))
        print(f"  Version: {new_version if success_bump else version}")
        print("\n  Next steps:")
        print("  1. Review and commit changes")
        print("  2. Create git tag: git tag v" + (new_version if success_bump else version))
        print("  3. Push with tags: git push --tags")
        
    except Exception as e:
        print(self.colorize(f"✗ Error: {e}", Colors.RED))
