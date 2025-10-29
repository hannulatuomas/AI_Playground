"""
Extended CLI Commands for Project Management

Additional commands for Phases 1-6 functionality.
"""

def add_extended_help(self):
    """Add extended help for project commands."""
    extended = f"""
{self.colorize('Project Management:', Colors.BOLD)}
  {self.colorize('project', Colors.GREEN)} <path>
    Set project root folder and index files
    Example: project /path/to/my-project
    
  {self.colorize('scan', Colors.GREEN)}
    Rescan project for file changes
    
  {self.colorize('search', Colors.GREEN)} <query>
    Search files in project
    Example: search "database connection"
    
  {self.colorize('task', Colors.GREEN)} <description>
    Decompose and execute complex task
    Example: task "Add JWT authentication"
    
  {self.colorize('rules', Colors.GREEN)} [add|list|show]
    Manage coding rules
    
  {self.colorize('test', Colors.GREEN)} [--fix]
    Run tests (optional: auto-fix failures)
    
  {self.colorize('commit', Colors.GREEN)} [message]
    Git commit with auto-generated message
    
  {self.colorize('status', Colors.GREEN)}
    Show project and git status
"""
    return extended


# Command implementations
def cmd_project(self, args: str):
    """Set project root folder."""
    if not args:
        if self.current_project:
            print(self.colorize(f"\nCurrent project: {self.current_project}", Colors.CYAN))
            if self.project_manager:
                stats = self.project_manager.get_project_stats()
                print(f"  Files: {stats['total_files']}")
                print(f"  Languages: {', '.join(list(stats['by_language'].keys())[:5])}")
        else:
            print(self.colorize("✗ No project set", Colors.RED))
            print("  Usage: project <path>")
        return
    
    path = args.strip()
    print(self.colorize(f"\n→ Setting project root: {path}", Colors.YELLOW))
    
    # Initialize project manager
    if not self.project_manager:
        self.project_manager = ProjectManager(llm_interface=self.llm)
    
    if self.project_manager.set_root_folder(path):
        self.current_project = path
        
        print(self.colorize("→ Indexing project files...", Colors.YELLOW))
        stats = self.project_manager.index_files()
        
        print(self.colorize(f"\n✓ Project initialized!", Colors.GREEN))
        print(f"  Files: {stats['total_files']}")
        print(f"  Size: {stats['total_size'] / 1024:.1f} KB")
        
        # Initialize other components
        self.project_navigator = ProjectNavigator(self.project_manager, self.llm)
        self.context_manager = ContextManager(
            self.project_manager, self.project_navigator, self.db, self.engine
        )
        self.task_manager = TaskManager(
            self.llm, self.project_manager, self.project_navigator,
            self.context_manager, self.generator, self.debugger, self.db
        )
        self.rule_enforcer = RuleEnforcer(self.db, self.project_manager, self.llm)
        self.tool_integrator = ToolIntegrator(
            self.project_manager, self.llm, self.debugger, self.context_manager
        )
        
        print(self.colorize("✓ All project features enabled", Colors.GREEN))
    else:
        print(self.colorize(f"✗ Invalid path: {path}", Colors.RED))


def cmd_scan(self, args: str):
    """Scan project for changes."""
    if not self.project_navigator:
        print(self.colorize("✗ No project set. Use 'project <path>' first", Colors.RED))
        return
    
    print(self.colorize("\n→ Scanning for changes...", Colors.YELLOW))
    changes = self.project_navigator.scan_project(summarize_new=True)
    
    print(self.colorize("\n✓ Scan complete!", Colors.GREEN))
    print(f"  New files: {len(changes['new'])}")
    print(f"  Modified: {len(changes['modified'])}")
    print(f"  Deleted: {len(changes['deleted'])}")


def cmd_search(self, args: str):
    """Search files in project."""
    if not self.project_navigator:
        print(self.colorize("✗ No project set", Colors.RED))
        return
    
    if not args:
        print(self.colorize("✗ Usage: search <query>", Colors.RED))
        return
    
    query = args.strip()
    print(self.colorize(f"\n→ Searching for: {query}", Colors.YELLOW))
    
    results = self.project_navigator.search_files(query, max_results=10)
    
    if results:
        print(self.colorize(f"\n✓ Found {len(results)} results:", Colors.GREEN))
        for i, result in enumerate(results, 1):
            score = result['score']
            path = result['path']
            print(f"  {i}. [{score:.2f}] {path}")
    else:
        print(self.colorize("\n✗ No results found", Colors.YELLOW))


def cmd_task(self, args: str):
    """Decompose and execute complex task."""
    if not self.task_manager:
        print(self.colorize("✗ No project set", Colors.RED))
        return
    
    if not args:
        print(self.colorize("✗ Usage: task <description>", Colors.RED))
        return
    
    description = args.strip()
    
    # Get language
    lang = input(self.colorize("Language (press Enter for auto-detect): ", Colors.CYAN)).strip()
    if not lang and self.project_manager:
        # Auto-detect from project
        lang = None
    
    print(self.colorize(f"\n→ Decomposing task: {description}", Colors.YELLOW))
    
    task_structure = self.task_manager.decompose_task(
        user_task=description,
        project_id=self.current_project,
        language=lang
    )
    
    print(self.colorize(f"\n✓ Task decomposed into {task_structure['total_sub_tasks']} sub-tasks", Colors.GREEN))
    
    # Show sub-tasks
    for i, sub_task in enumerate(task_structure['sub_tasks'], 1):
        print(f"  {i}. {sub_task['description']}")
    
    # Ask to execute
    response = input(self.colorize("\nExecute tasks? (y/n): ", Colors.YELLOW)).lower()
    if response in ['y', 'yes']:
        print(self.colorize("\n→ Executing tasks...", Colors.YELLOW))
        results = self.task_manager.execute_tasks(task_structure, interactive=False)
        
        print(self.colorize(f"\n✓ Execution complete!", Colors.GREEN))
        print(f"  Completed: {results['completed']}/{results['total']}")
        print(f"  Failed: {results['failed']}")


def cmd_rules(self, args: str):
    """Manage coding rules."""
    if not self.rule_enforcer:
        print(self.colorize("✗ No project set", Colors.RED))
        return
    
    parts = args.split(maxsplit=1) if args else []
    action = parts[0] if parts else 'list'
    
    if action == 'add':
        if len(parts) < 2:
            print(self.colorize("✗ Usage: rules add <rule>", Colors.RED))
            return
        
        rule = parts[1]
        # Get existing rules
        existing = self.rule_enforcer.get_rules(project_id=self.current_project)
        existing.append(rule)
        
        self.rule_enforcer.set_rules(existing, project_id=self.current_project)
        print(self.colorize(f"✓ Rule added: {rule}", Colors.GREEN))
    
    elif action in ['list', 'show']:
        rules = self.rule_enforcer.get_rules(project_id=self.current_project)
        print(self.colorize(f"\nProject Rules ({len(rules)}):", Colors.CYAN))
        for i, rule in enumerate(rules, 1):
            print(f"  {i}. {rule}")
    
    else:
        print(self.colorize(f"✗ Unknown action: {action}", Colors.RED))
        print("  Usage: rules [add|list|show]")


def cmd_test(self, args: str):
    """Run tests."""
    if not self.tool_integrator:
        print(self.colorize("✗ No project set", Colors.RED))
        return
    
    auto_fix = '--fix' in args
    
    print(self.colorize("\n→ Running tests...", Colors.YELLOW))
    result = self.tool_integrator.run_tests(auto_fix=auto_fix, max_fix_attempts=3)
    
    if result['success']:
        print(self.colorize(f"\n✓ Tests complete!", Colors.GREEN))
        print(f"  Framework: {result['framework']}")
        print(f"  Passed: {result['passed']}")
        print(f"  Failed: {result['failed']}")
        
        if auto_fix and result['fix_attempts'] > 0:
            print(f"  Fix attempts: {result['fix_attempts']}")
        
        if result['all_passed']:
            print(self.colorize("  ✓ All tests passed!", Colors.BOLD + Colors.GREEN))
    else:
        print(self.colorize(f"\n✗ Tests failed: {result.get('error')}", Colors.RED))


def cmd_commit(self, args: str):
    """Git commit."""
    if not self.tool_integrator:
        print(self.colorize("✗ No project set", Colors.RED))
        return
    
    message = args.strip() if args else None
    generate = not message
    
    print(self.colorize("\n→ Committing changes...", Colors.YELLOW))
    result = self.tool_integrator.git_commit(message=message, generate_message=generate)
    
    if result['success']:
        print(self.colorize(f"\n✓ Committed!", Colors.GREEN))
        print(f"  Message: {result['message']}")
        print(f"  Hash: {result['commit_hash']}")
        print(f"  Files: {len(result['files_committed'])}")
    else:
        print(self.colorize(f"\n✗ Commit failed: {result['error']}", Colors.RED))


def cmd_status(self, args: str):
    """Show project and git status."""
    if not self.current_project:
        print(self.colorize("✗ No project set", Colors.RED))
        return
    
    print(self.colorize("\nProject Status:", Colors.BOLD + Colors.CYAN))
    print(f"  Root: {self.current_project}")
    
    if self.project_manager:
        stats = self.project_manager.get_project_stats()
        print(f"  Files: {stats['total_files']}")
        print(f"  Size: {stats['total_size'] / 1024:.1f} KB")
    
    if self.tool_integrator:
        git_status = self.tool_integrator.git_status()
        if git_status['initialized']:
            print(self.colorize("\nGit Status:", Colors.BOLD + Colors.CYAN))
            print(f"  Branch: {git_status['branch']}")
            print(f"  Changed: {len(git_status['changed_files'])}")
            print(f"  Untracked: {len(git_status['untracked_files'])}")
        else:
            print(self.colorize("\nGit: Not initialized", Colors.YELLOW))
