"""
UAIDE Orchestrator

Main orchestrator that integrates all modules.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass

from ..ai.backend import AIBackend
from ..db.database import Database
from ..config.config import Config
from ..modules.project_manager import ProjectManager
from ..modules.code_generator import CodeGenerator
from ..modules.tester import TestGenerator, TestRunner, BugFixer
from ..modules.doc_manager import DocManager
from ..modules.refactorer import CodeRefactorer
from ..modules.context_manager import ContextManager
from ..modules.rule_manager import RuleManager
from ..modules.task_decomposer import TaskDecomposer, TaskPlanner, TaskExecutor
from ..modules.self_improver import EventLogger
from .event_bus import EventBus
from ..mcp.manager import MCPServerManager
from ..modules.workflow_engine import WorkflowEngine
from ..modules.file_splitter import FileSplitter
from ..modules.dead_code_detector import DeadCodeDetector
from ..modules.automation_engine import AutomationEngine, TriggerType, ActionType
from ..modules.bloat_detector import BloatDetector
from ..modules.quality_monitor import QualityMonitor
from ..modules.context_pruner import ContextPruner
from ..modules.codebase_indexer import CodebaseIndexer


@dataclass
class Result:
    """Generic result object."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None


class UAIDE:
    """
    Ultimate AI-Powered IDE - Main orchestrator.
    
    Integrates all modules into a cohesive system.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize UAIDE.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = Config(config_path) if config_path else Config()
        self.config.load()
        
        # Initialize core components
        self.ai_backend = AIBackend(self.config.get('ai', {}))
        self.database = Database(self.config.get('database.path', 'data/uaide.db'))
        self.event_bus = EventBus()
        self.mcp_manager = MCPServerManager(self.config.get('mcp.config_path', 'mcp_servers.json'))
        
        # Initialize modules
        self._initialize_modules()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Start MCP servers (non-blocking, errors are logged but don't stop initialization)
        try:
            self.mcp_manager.start_all()
        except Exception as e:
            logger.warning(f"MCP servers failed to start: {e}")
        
        print("UAIDE initialized successfully")
    
    def _initialize_modules(self):
        """Initialize all modules."""
        # Project management
        self.project_manager = ProjectManager(self.ai_backend, self.database)
        
        # Code generation
        self.code_generator = CodeGenerator(self.ai_backend)
        
        # Testing
        self.test_generator = TestGenerator(self.ai_backend)
        self.test_runner = TestRunner()
        self.bug_fixer = BugFixer(self.ai_backend)
        
        # Documentation
        self.doc_manager = DocManager(self.ai_backend)
        
        # Refactoring
        self.refactorer = CodeRefactorer(self.ai_backend)
        
        # Context management
        self.context_manager = ContextManager(self.ai_backend)
        
        # Rule management
        self.rule_manager = RuleManager()
        
        # Task decomposition
        self.task_decomposer = TaskDecomposer(self.ai_backend)
        self.task_planner = TaskPlanner()
        self.task_executor = TaskExecutor()
        
        # Self-improvement
        self.event_logger = EventLogger()
        
        # v1.3.0 Quality & Monitoring
        # Note: BloatDetector, DeadCodeDetector, QualityMonitor, and CodebaseIndexer require project_path, instantiated when needed
        self.context_pruner = ContextPruner(self.ai_backend)
        
        # v1.4.0 Workflow & Automation
        self.workflow_engine = WorkflowEngine()
        self.file_splitter = FileSplitter()
        self.automation_engine = AutomationEngine()
        self.security_scanner = None  # Lazy initialization
        
        # Setup workflow action handlers
        self._setup_workflow_handlers()
        
        # Setup automation triggers
        self._setup_automation()
    
    def _setup_event_handlers(self):
        """Setup event handlers for inter-module communication."""
        # When code is generated, trigger documentation and tests
        self.event_bus.subscribe('code.generated', self._on_code_generated)
        
        # When tests complete, log results
        self.event_bus.subscribe('test.completed', self._on_test_completed)
        
        # When error occurs, log for learning
        self.event_bus.subscribe('error.occurred', self._on_error_occurred)
    
    def _on_code_generated(self, event):
        """Handle code generation event."""
        # Auto-generate documentation
        if self.config.get('auto_generate_docs', False):
            try:
                self.doc_manager.sync_documentation(
                    event.data.get('project_path'),
                    event.data.get('language', 'python')
                )
            except Exception as e:
                print(f"Error auto-generating docs: {e}")
    
    def _on_test_completed(self, event):
        """Handle test completion event."""
        # Log test results for learning
        self.event_logger.log_event(
            module='tester',
            action='test_completed',
            input_data={'files': event.data.get('files', [])},
            output_data={'results': event.data.get('results', {})},
            success=event.data.get('all_passed', False)
        )
    
    def _on_error_occurred(self, event):
        """Handle error event."""
        # Log error for learning
        self.event_logger.log_event(
            module=event.data.get('module', 'unknown'),
            action=event.data.get('action', 'unknown'),
            input_data=event.data.get('input', {}),
            output_data={},
            success=False,
            error=event.data.get('error'),
            error_type=event.data.get('error_type')
        )
    
    def new_project(self, name: str, language: str, 
                   framework: Optional[str] = None,
                   path: Optional[str] = None) -> Result:
        """
        Create a new project.
        
        Args:
            name: Project name
            language: Programming language
            framework: Optional framework
            path: Optional project path
            
        Returns:
            Result object
        """
        try:
            project_path = path or f"./{name}"
            
            # Create project
            project = self.project_manager.create_project(
                name=name,
                language=language,
                framework=framework,
                path=project_path
            )
            
            # Emit event
            self.event_bus.emit('project.created', {
                'name': name,
                'language': language,
                'framework': framework,
                'path': project_path
            }, source='project_manager')
            
            return Result(
                success=True,
                message=f"Project '{name}' created successfully",
                data={'project_path': project_path}
            )
            
        except Exception as e:
            self.event_bus.emit('error.occurred', {
                'module': 'project_manager',
                'action': 'new_project',
                'error': str(e),
                'error_type': type(e).__name__
            })
            
            return Result(
                success=False,
                message=f"Failed to create project: {str(e)}",
                errors=[str(e)]
            )
    
    def generate_feature(self, description: str, 
                        project_path: Optional[str] = None) -> Result:
        """
        Generate a feature using task decomposition.
        
        Args:
            description: Feature description
            project_path: Optional project path
            
        Returns:
            Result object
        """
        try:
            # Get context if project path provided
            if project_path:
                self.context_manager.index_project(project_path)
                context = self.context_manager.get_context_for_task(description)
            else:
                context = ""
            
            # Decompose task
            subtasks = self.task_decomposer.decompose_task(description)
            
            # Create execution plan
            plan = self.task_planner.create_plan(description, subtasks)
            
            # Execute plan
            result = self.task_executor.execute_plan(plan)
            
            # Emit event
            self.event_bus.emit('code.generated', {
                'description': description,
                'project_path': project_path,
                'subtasks_completed': len(result.completed_tasks),
                'success': result.success
            }, source='code_generator')
            
            return Result(
                success=result.success,
                message=f"Feature generated: {len(result.completed_tasks)}/{len(plan.subtasks)} tasks completed",
                data={
                    'completed_tasks': result.completed_tasks,
                    'failed_tasks': result.failed_tasks
                },
                errors=result.errors if result.errors else None
            )
            
        except Exception as e:
            self.event_bus.emit('error.occurred', {
                'module': 'code_generator',
                'action': 'generate_feature',
                'input': {'description': description},
                'error': str(e),
                'error_type': type(e).__name__
            })
            
            return Result(
                success=False,
                message=f"Failed to generate feature: {str(e)}",
                errors=[str(e)]
            )
    
    def test_code(self, project_path: str, 
                 files: Optional[List[str]] = None) -> Result:
        """
        Run tests on code.
        
        Args:
            project_path: Project path
            files: Optional specific files to test
            
        Returns:
            Result object
        """
        try:
            # Run tests
            results = self.test_runner.run_tests(project_path, files)
            
            # Emit event
            self.event_bus.emit('test.completed', {
                'project_path': project_path,
                'files': files or [],
                'results': {
                    'total': results.total,
                    'passed': results.passed,
                    'failed': results.failed
                },
                'all_passed': results.failed == 0
            }, source='tester')
            
            return Result(
                success=results.failed == 0,
                message=f"Tests: {results.passed}/{results.total} passed",
                data={
                    'total': results.total,
                    'passed': results.passed,
                    'failed': results.failed,
                    'coverage': results.coverage
                }
            )
            
        except Exception as e:
            return Result(
                success=False,
                message=f"Failed to run tests: {str(e)}",
                errors=[str(e)]
            )
    
    def refactor(self, file_path: str, language: str = 'python') -> Result:
        """
        Refactor code.
        
        Args:
            file_path: Path to file
            language: Programming language
            
        Returns:
            Result object
        """
        try:
            result = self.refactorer.refactor_file(file_path, language)
            
            if result:
                return Result(
                    success=True,
                    message=f"Code refactored successfully",
                    data={
                        'changes': result.changes_made,
                        'improvements': result.improvements
                    }
                )
            else:
                return Result(
                    success=False,
                    message="Refactoring failed"
                )
                
        except Exception as e:
            return Result(
                success=False,
                message=f"Failed to refactor: {str(e)}",
                errors=[str(e)]
            )
    
    def generate_docs(self, project_path: str, 
                     language: str = 'python') -> Result:
        """
        Generate documentation.
        
        Args:
            project_path: Project path
            language: Programming language
            
        Returns:
            Result object
        """
        try:
            report = self.doc_manager.sync_documentation(project_path, language)
            
            return Result(
                success=True,
                message="Documentation generated",
                data={
                    'files_created': report.files_created,
                    'files_updated': report.files_updated,
                    'undocumented_items': len(report.undocumented_items)
                }
            )
            
        except Exception as e:
            return Result(
                success=False,
                message=f"Failed to generate docs: {str(e)}",
                errors=[str(e)]
            )
    
    def _setup_workflow_handlers(self):
        """Setup workflow action handlers"""
        # Register action handlers for workflow engine
        self.workflow_engine.register_action('analyze_request', self._workflow_analyze_request)
        self.workflow_engine.register_action('check_existing_code', self._workflow_check_existing)
        self.workflow_engine.register_action('generate_feature_code', self._workflow_generate_code)
        self.workflow_engine.register_action('validate_syntax', self._workflow_validate_syntax)
        self.workflow_engine.register_action('generate_unit_tests', self._workflow_generate_tests)
        self.workflow_engine.register_action('run_test_suite', self._workflow_run_tests)
        self.workflow_engine.register_action('check_code_quality', self._workflow_check_quality)
        self.workflow_engine.register_action('refactor_code', self._workflow_refactor)
        self.workflow_engine.register_action('update_documentation', self._workflow_update_docs)
    
    def _setup_automation(self):
        """Setup automation engine"""
        # Register action handlers
        self.automation_engine.register_action_handler(ActionType.QUALITY_CHECK, self._auto_quality_check)
        self.automation_engine.register_action_handler(ActionType.REFACTOR, self._auto_refactor)
        self.automation_engine.register_action_handler(ActionType.FILE_SPLIT, self._auto_file_split)
        self.automation_engine.register_action_handler(ActionType.BLOAT_CLEANUP, self._auto_bloat_cleanup)
        self.automation_engine.register_action_handler(ActionType.CONTEXT_PRUNE, self._auto_context_prune)
        # v1.5.0 handlers
        self.automation_engine.register_action_handler(ActionType.SECURITY_SCAN, self._auto_security_scan)
        self.automation_engine.register_action_handler(ActionType.DEPENDENCY_UPDATE, self._auto_dependency_update)
        self.automation_engine.register_action_handler(ActionType.TEMPLATE_VALIDATE, self._auto_template_validate)
        
        # Setup automation triggers
        self.automation_engine.setup_default_triggers()
        
        # Import security methods
        from .orchestrator_security import (
            scan_security, scan_vulnerabilities, check_dependencies,
            detect_insecure_patterns, scan_secrets, generate_security_report
        )
        self.scan_security = lambda *args, **kwargs: scan_security(self, *args, **kwargs)
        self.scan_vulnerabilities = lambda *args, **kwargs: scan_vulnerabilities(self, *args, **kwargs)
        self.check_dependencies = lambda *args, **kwargs: check_dependencies(self, *args, **kwargs)
        self.detect_insecure_patterns = lambda *args, **kwargs: detect_insecure_patterns(self, *args, **kwargs)
        self.scan_secrets = lambda *args, **kwargs: scan_secrets(self, *args, **kwargs)
        self.generate_security_report = lambda *args, **kwargs: generate_security_report(self, *args, **kwargs)
        
        # Import template validation methods
        from .orchestrator_template import validate_template, get_template_score
        self.validate_template = lambda *args, **kwargs: validate_template(self, *args, **kwargs)
        self.get_template_score = lambda *args, **kwargs: get_template_score(self, *args, **kwargs)
    
    # Workflow action handlers
    def _workflow_analyze_request(self, params: Dict, variables: Dict) -> Any:
        """Analyze feature request"""
        return self.task_decomposer.decompose_task(params.get('feature', ''))
    
    def _workflow_check_existing(self, params: Dict, variables: Dict) -> Any:
        """Check for existing code"""
        project_path = params.get('project_path')
        if project_path:
            return self.code_generator.check_duplicates(project_path, params.get('feature', ''))
        return None
    
    def _workflow_generate_code(self, params: Dict, variables: Dict) -> Any:
        """Generate feature code"""
        return self.code_generator.generate_feature(
            params.get('feature', ''),
            params.get('project_path')
        )
    
    def _workflow_validate_syntax(self, params: Dict, variables: Dict) -> Any:
        """Validate code syntax"""
        project_path = params.get('project_path')
        if project_path:
            return self.code_generator.validate_code(project_path)
        return True
    
    def _workflow_generate_tests(self, params: Dict, variables: Dict) -> Any:
        """Generate unit tests"""
        return self.test_generator.generate_tests(
            params.get('project_path'),
            params.get('feature', '')
        )
    
    def _workflow_run_tests(self, params: Dict, variables: Dict) -> Any:
        """Run test suite"""
        return self.test_runner.run_tests(params.get('project_path'))
    
    def _workflow_check_quality(self, params: Dict, variables: Dict) -> Any:
        """Check code quality"""
        project_path = params.get('project_path')
        if project_path:
            monitor = QualityMonitor(project_path)
            return monitor.monitor_project()
        return None
    
    def _workflow_refactor(self, params: Dict, variables: Dict) -> Any:
        """Refactor code"""
        project_path = params.get('project_path')
        if project_path:
            return self.refactorer.refactor_project(project_path)
        return None
    
    def _workflow_update_docs(self, params: Dict, variables: Dict) -> Any:
        """Update documentation"""
        return self.doc_manager.sync_documentation(
            params.get('project_path'),
            params.get('language', 'python')
        )
    
    # Automation action handlers
    def _auto_quality_check(self, context: Dict) -> Any:
        """Automated quality check"""
        project_path = context.get('project_path')
        if project_path:
            monitor = QualityMonitor(project_path)
            return monitor.monitor_project()
        return None
    
    def _auto_refactor(self, context: Dict) -> Any:
        """Automated refactoring"""
        file_path = context.get('file_path')
        if file_path:
            return self.refactorer.refactor_file(file_path)
        return None
    
    def _auto_file_split(self, context: Dict) -> Any:
        """Automated file splitting"""
        file_path = context.get('file_path')
        if file_path:
            return self.file_splitter.split_file(file_path, strategy='auto')
        return None
    
    def _auto_bloat_cleanup(self, context: Dict) -> Any:
        """Automated bloat cleanup"""
        project_path = context.get('project_path')
        if project_path:
            detector = BloatDetector(project_path)
            results = detector.detect_all()
            plan = detector.generate_cleanup_plan(results)
            return detector.execute_cleanup(plan, auto_approve_low_risk=True)
        return None
    
    def _auto_context_prune(self, context: Dict) -> Any:
        """Automated context pruning"""
        return self.context_pruner.prune_context(
            context.get('messages', []),
            max_tokens=context.get('max_tokens', 4000)
        )
    
    # v1.5.0 Automation handlers
    def _auto_security_scan(self, context: Dict) -> Any:
        """Automated security scanning"""
        project_path = context.get('project_path', '.')
        return self.scan_security(project_path)
    
    def _auto_dependency_update(self, context: Dict) -> Any:
        """Automated dependency update"""
        from ..modules.dependency_manager import DependencyManager
        project_path = context.get('project_path', '.')
        manager = DependencyManager(project_path)
        # Only update safe (non-breaking) dependencies
        safe_updates = manager.suggest_safe_updates()
        if safe_updates:
            packages = [u.name for u in safe_updates]
            return manager.update_dependencies(packages=packages, test_after=True, rollback_on_failure=True)
        return None
    
    def _auto_template_validate(self, context: Dict) -> Any:
        """Automated template validation"""
        project_path = context.get('project_path', '.')
        return self.validate_template(project_path, strict=False)
    
    # New v1.4.0 methods
    def execute_workflow(self, workflow_name: str, variables: Optional[Dict] = None) -> Result:
        """
        Execute a workflow
        
        Args:
            workflow_name: Workflow template name or ID
            variables: Variables for workflow
            
        Returns:
            Result object
        """
        try:
            result = self.workflow_engine.execute_template(workflow_name, variables)
            
            return Result(
                success=result['success'],
                message=f"Workflow completed in {result['duration']:.2f}s",
                data=result
            )
        except Exception as e:
            return Result(
                success=False,
                message=f"Workflow execution failed: {str(e)}",
                errors=[str(e)]
            )
    
    def detect_large_files(self, project_path: str) -> Result:
        """Detect files exceeding size limit"""
        try:
            large_files = self.file_splitter.detect_large_files(project_path)
            
            return Result(
                success=True,
                message=f"Found {len(large_files)} large files",
                data={'large_files': large_files}
            )
        except Exception as e:
            return Result(
                success=False,
                message=f"Failed to detect large files: {str(e)}",
                errors=[str(e)]
            )
    
    def split_file(self, file_path: str, strategy: str = 'auto') -> Result:
        """Split a large file"""
        try:
            result = self.file_splitter.split_file(file_path, strategy)
            
            return Result(
                success=result['success'],
                message=f"File split into {len(result.get('files_created', []))} files",
                data=result
            )
        except Exception as e:
            return Result(
                success=False,
                message=f"Failed to split file: {str(e)}",
                errors=[str(e)]
            )
    
    def detect_dead_code(self, project_path: str) -> Result:
        """Detect dead code in project"""
        try:
            detector = DeadCodeDetector(project_path)
            results = detector.analyze_project()
            
            total_dead = sum(len(items) for items in results.values())
            
            return Result(
                success=True,
                message=f"Found {total_dead} dead code items",
                data=results
            )
        except Exception as e:
            return Result(
                success=False,
                message=f"Failed to detect dead code: {str(e)}",
                errors=[str(e)]
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            'context_manager': self.context_manager.get_stats(),
            'event_history': len(self.event_bus.event_history),
            'rules_loaded': len(self.rule_manager.rules),
            'workflows_loaded': len(self.workflow_engine.list_workflows()),
            'automation_stats': self.automation_engine.get_stats()
        }
