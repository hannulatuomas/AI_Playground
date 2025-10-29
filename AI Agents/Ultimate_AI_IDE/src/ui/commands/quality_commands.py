"""
Quality & Context Commands

Commands for bloat detection, quality monitoring, context management, and codebase indexing.
"""

import click
from pathlib import Path


@click.group()
def bloat():
    """Bloat detection and cleanup"""
    pass


@bloat.command('detect')
@click.option('--project', '-p', default='.', help='Project path')
def bloat_detect(project):
    """Detect bloat in project"""
    from ...modules.bloat_detector import BloatDetector
    
    try:
        detector = BloatDetector(project)
        click.echo("Detecting bloat...")
        
        results = detector.detect_all()
        
        total = sum(len(items) for items in results.values())
        click.echo(f"\n=== Bloat Detection Results ===\n")
        click.echo(f"Total items found: {total}\n")
        
        for category, items in results.items():
            if items:
                click.echo(f"{category}: {len(items)} items")
                for item in items[:3]:  # Show first 3
                    click.echo(f"  - {item.get('path', item.get('name', 'N/A'))}: {item.get('reason', '')}")
                if len(items) > 3:
                    click.echo(f"  ... and {len(items) - 3} more")
                click.echo()
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@bloat.command('clean')
@click.option('--project', '-p', default='.', help='Project path')
@click.option('--auto', is_flag=True, help='Auto-approve low-risk items')
def bloat_clean(project, auto):
    """Clean detected bloat"""
    from ...modules.bloat_detector import BloatDetector
    
    try:
        detector = BloatDetector(project)
        click.echo("Detecting bloat...")
        
        results = detector.detect_all()
        plan = detector.generate_cleanup_plan(results)
        
        click.echo(f"\n=== Cleanup Plan ===\n")
        click.echo(f"Total items: {plan['summary']['total_items']}")
        click.echo(f"Estimated space saved: {plan['summary']['estimated_space_saved']} bytes\n")
        
        if auto or click.confirm("Execute cleanup?"):
            execution_results = detector.execute_cleanup(plan, auto_approve_low_risk=auto)
            click.echo(f"\n✓ Executed: {execution_results['executed']}")
            click.echo(f"⊘ Skipped: {execution_results['skipped']}")
            click.echo(f"✗ Failed: {execution_results['failed']}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@click.group()
def quality():
    """Code quality monitoring"""
    pass


@quality.command('check')
@click.option('--project', '-p', default='.', help='Project path')
@click.option('--file', '-f', help='Check specific file')
def quality_check(project, file):
    """Check code quality"""
    from ...modules.quality_monitor import QualityMonitor
    
    try:
        monitor = QualityMonitor(project)
        
        if file:
            file_path = Path(file)
            issues = monitor.check_file(file_path)
            
            click.echo(f"\n=== Quality Check: {file} ===\n")
            if not issues:
                click.echo("✓ No issues found!")
            else:
                for issue in issues:
                    severity_icon = {'low': '○', 'medium': '◐', 'high': '●', 'critical': '✗'}
                    icon = severity_icon.get(issue.severity, '?')
                    click.echo(f"{icon} [{issue.severity.upper()}] {issue.type}")
                    click.echo(f"   {issue.message}")
                    if issue.suggestion:
                        click.echo(f"   → {issue.suggestion}")
                    click.echo()
        else:
            click.echo("Monitoring project...")
            all_issues = monitor.monitor_project()
            
            click.echo(f"\n=== Project Quality Report ===\n")
            click.echo(f"Files with issues: {len(all_issues)}")
            
            total = sum(len(issues) for issues in all_issues.values())
            click.echo(f"Total issues: {total}\n")
            
            for file_path, issues in list(all_issues.items())[:5]:
                click.echo(f"📄 {file_path}: {len(issues)} issues")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@quality.command('report')
@click.option('--project', '-p', default='.', help='Project path')
def quality_report(project):
    """Generate quality report"""
    from ...modules.quality_monitor import QualityMonitor
    
    try:
        monitor = QualityMonitor(project)
        click.echo("Generating quality report...")
        
        report = monitor.get_project_quality_report()
        
        click.echo(f"\n=== Project Quality Report ===\n")
        click.echo(f"Quality Score: {report['quality_score']}/100")
        click.echo(f"Files with issues: {report['total_files_with_issues']}")
        click.echo(f"Total issues: {report['total_issues']}\n")
        
        click.echo("Issues by severity:")
        for severity, count in report['severity_breakdown'].items():
            if count > 0:
                click.echo(f"  {severity}: {count}")
        
        if report['files_needing_refactoring']:
            click.echo(f"\nFiles needing refactoring: {len(report['files_needing_refactoring'])}")
            for item in report['files_needing_refactoring'][:3]:
                click.echo(f"  - {item['file']}")
                for reason in item['reasons']:
                    click.echo(f"    • {reason}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@click.group()
def context():
    """Context management"""
    pass


@context.command('status')
def context_status():
    """Show context status"""
    from ...modules.context_pruner import ContextPruner
    
    try:
        pruner = ContextPruner()
        stats = pruner.get_statistics()
        
        click.echo(f"\n=== Context Status ===\n")
        click.echo(f"Total items: {stats['total_items']}")
        click.echo(f"Total tokens: {stats['total_tokens']}")
        click.echo(f"Available tokens: {stats['available_tokens']}")
        click.echo(f"Usage: {stats['usage_percentage']}%")
        
        if stats['should_prune']:
            click.echo("\n⚠️  Context should be pruned")
        if stats['is_critical']:
            click.echo("✗ Context usage is CRITICAL!")
        
        click.echo(f"\nItems by type:")
        for item_type, count in stats['items_by_type'].items():
            click.echo(f"  {item_type}: {count}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@context.command('prune')
@click.option('--age', default=24.0, help='Max age in hours')
@click.option('--relevance', default=0.3, help='Min relevance score')
def context_prune(age, relevance):
    """Prune old context"""
    from ...modules.context_pruner import ContextPruner
    
    try:
        pruner = ContextPruner()
        
        click.echo("Pruning context...")
        pruned_old = pruner.prune_old_context(max_age_hours=age)
        pruned_relevance = pruner.prune_by_relevance(min_relevance=relevance)
        
        total_pruned = pruned_old + pruned_relevance
        click.echo(f"\n✓ Pruned {total_pruned} items")
        click.echo(f"  - By age: {pruned_old}")
        click.echo(f"  - By relevance: {pruned_relevance}")
        
        stats = pruner.get_statistics()
        click.echo(f"\nNew usage: {stats['usage_percentage']}%")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@click.group()
def index():
    """Codebase indexing"""
    pass


@index.command('build')
@click.option('--project', '-p', default='.', help='Project path')
@click.option('--incremental', is_flag=True, help='Incremental indexing')
def index_build(project, incremental):
    """Build codebase index"""
    from ...modules.codebase_indexer import CodebaseIndexer
    
    try:
        indexer = CodebaseIndexer(project)
        click.echo("Indexing project...")
        
        stats = indexer.index_project(incremental=incremental)
        
        click.echo(f"\n=== Indexing Complete ===\n")
        click.echo(f"Files indexed: {stats['files_indexed']}")
        click.echo(f"Total files: {stats['total_files']}")
        click.echo(f"Total classes: {stats['total_classes']}")
        click.echo(f"Total functions: {stats['total_functions']}")
        click.echo(f"Dependencies: {stats['total_dependencies']}")
        click.echo(f"Duration: {stats['duration_seconds']}s")
        
        # Save index
        indexer.save_index('.uaide_index.json')
        click.echo("\n✓ Index saved to .uaide_index.json")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@index.command('search')
@click.argument('symbol')
@click.option('--project', '-p', default='.', help='Project path')
def index_search(symbol, project):
    """Search for a symbol"""
    from ...modules.codebase_indexer import CodebaseIndexer
    
    try:
        indexer = CodebaseIndexer(project)
        
        # Try to load existing index
        index_file = Path('.uaide_index.json')
        if index_file.exists():
            indexer.load_index(str(index_file))
        else:
            click.echo("No index found. Building...")
            indexer.index_project()
        
        results = indexer.search_symbol(symbol)
        
        click.echo(f"\n=== Search Results for '{symbol}' ===\n")
        
        if results['classes']:
            click.echo(f"Classes ({len(results['classes'])}):")
            for cls in results['classes']:
                click.echo(f"  - {cls.name} in {cls.file_path}:{cls.line_number}")
        
        if results['functions']:
            click.echo(f"\nFunctions ({len(results['functions'])}):")
            for func in results['functions']:
                click.echo(f"  - {func.name} in {func.file_path}:{func.line_number}")
        
        if results['files']:
            click.echo(f"\nFiles ({len(results['files'])}):")
            for file in results['files'][:5]:
                click.echo(f"  - {file}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@index.command('analyze')
@click.option('--project', '-p', default='.', help='Project path')
def index_analyze(project):
    """Analyze project structure"""
    from ...modules.codebase_indexer import CodebaseIndexer
    
    try:
        indexer = CodebaseIndexer(project)
        
        # Try to load existing index
        index_file = Path('.uaide_index.json')
        if index_file.exists():
            indexer.load_index(str(index_file))
        else:
            click.echo("No index found. Building...")
            indexer.index_project()
        
        structure = indexer.get_project_structure()
        
        click.echo(f"\n=== Project Structure ===\n")
        click.echo(f"Total files: {structure['total_files']}")
        click.echo(f"Total lines: {structure['total_lines']}")
        click.echo(f"Total classes: {structure['total_classes']}")
        click.echo(f"Total functions: {structure['total_functions']}\n")
        
        click.echo("Files by language:")
        for lang, count in structure['by_language'].items():
            click.echo(f"  {lang}: {count}")
        
        click.echo("\nLargest files:")
        for file_info in structure['largest_files'][:5]:
            click.echo(f"  {file_info['path']}: {file_info['lines']} lines")
        
        # Check for circular dependencies
        circles = indexer.detect_circular_dependencies()
        if circles:
            click.echo(f"\n⚠️  Found {len(circles)} circular dependencies")
            for circle in circles[:3]:
                click.echo(f"  - {' -> '.join(circle)}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
