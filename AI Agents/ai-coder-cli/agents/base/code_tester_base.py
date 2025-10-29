"""
Base class for all code testing agents.

This module defines the common interface and functionality for language-specific
code testing agents with project context awareness.
"""

import re
import subprocess
from abc import abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from .agent_base import Agent
from ..utils.codebase_awareness import CodebaseAwarenessMixin


class CodeTesterBase(Agent, CodebaseAwarenessMixin):
    """
    Abstract base class for code testing agents with project context awareness.
    
    Provides common functionality for:
    - Test framework detection
    - Test execution and result parsing
    - Test report generation
    - Coverage analysis
    - Project context awareness
    - Rules hierarchy (project > user > best practices)
    
    Subclasses must implement:
    - _detect_test_framework: Detect language-specific test framework
    - _build_test_command: Build test execution command
    - _parse_test_output: Parse framework-specific output
    - _get_supported_frameworks: Return list of supported frameworks
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        supported_frameworks: List[str],
        **kwargs
    ):
        """
        Initialize code testing agent with project context awareness.
        
        Args:
            name: Agent name
            description: Agent description
            supported_frameworks: List of test frameworks (e.g., ['pytest', 'unittest'])
            **kwargs: Additional arguments passed to Agent base class
        """
        super().__init__(name=name, description=description, **kwargs)
        self.supported_frameworks = supported_frameworks
        self.testing_preferences = {}
        
        # Initialize codebase awareness
        self.init_codebase_awareness()
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute code testing task with project context awareness.
        
        Args:
            task: Description of testing task
            context: Execution context with optional 'test_path', 'test_files', 'working_dir'
            
        Returns:
            Result dictionary with success status and test results
        """
        self._log_action("Starting code testing", task[:100])
        
        try:
            # Initialize project context awareness
            success, error = self.ensure_codebase_awareness_initialized(context)
            if not success and error:
                self.logger.warning(f"Project context initialization: {error}")
            
            # Load testing preferences
            self._load_testing_preferences()
            
            # Parse test request
            test_info = self._parse_test_request(task, context)
            
            if not test_info:
                return self._build_error_result("Could not determine what to test")
            
            # Detect test framework
            framework = self._detect_test_framework(test_info)
            if not framework:
                return self._build_error_result("Could not detect test framework")
            
            test_info['framework'] = framework
            self._log_action("Detected test framework", framework)
            
            # Run tests
            result = self._run_tests(test_info, context)
            
            return result
            
        except Exception as e:
            self.logger.exception("Code testing failed")
            return self._build_error_result(f"Testing error: {str(e)}", e)
    
    def _parse_test_request(self, task: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse test request from task and context.
        
        Args:
            task: Task description
            context: Execution context
            
        Returns:
            Dictionary with test information or None if parsing fails
        """
        test_info = {
            'test_path': context.get('test_path'),
            'test_files': context.get('test_files', []),
            'working_dir': context.get('working_dir', self.root_folder or Path.cwd()),
            'options': context.get('test_options', {})
        }
        
        # Try to extract test path from task
        if not test_info['test_path']:
            # Look for file patterns
            patterns = [
                r'test[s]?[/\\]([a-zA-Z0-9_/\\-]+)',
                r'([a-zA-Z0-9_/\\-]*test[a-zA-Z0-9_/\\-]*\.\w+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, task, re.IGNORECASE)
                if match:
                    test_info['test_path'] = match.group(1)
                    break
        
        # If still no path, look for common test directories
        if not test_info['test_path'] and not test_info['test_files']:
            working_dir = Path(test_info['working_dir'])
            
            # Common test directory names
            test_dirs = ['tests', 'test', '__tests__', 'spec', 'specs']
            
            for test_dir in test_dirs:
                test_path = working_dir / test_dir
                if test_path.exists():
                    test_info['test_path'] = str(test_path)
                    break
        
        return test_info if test_info['test_path'] or test_info['test_files'] else None
    
    def _run_tests(self, test_info: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run tests using detected framework.
        
        Args:
            test_info: Test information dictionary
            context: Execution context
            
        Returns:
            Result dictionary with test outcomes
        """
        framework = test_info['framework']
        working_dir = Path(test_info['working_dir'])
        test_path = test_info.get('test_path', '')
        
        # Build command based on framework
        command = self._build_test_command(framework, test_path, test_info.get('options', {}))
        
        if not command:
            return self._build_error_result(f"Unknown framework: {framework}")
        
        self._log_action("Running tests", f"{framework}: {' '.join(command)}")
        
        # Execute tests
        try:
            result = subprocess.run(
                command,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Parse results
            parsed_results = self._parse_test_output(
                framework,
                result.stdout,
                result.stderr,
                result.returncode
            )
            
            # Build response
            success = result.returncode == 0
            
            return self._build_success_result(
                message=f"Tests {'passed' if success else 'failed'}: {parsed_results['summary']}",
                data={
                    'framework': framework,
                    'success': success,
                    'return_code': result.returncode,
                    'results': parsed_results,
                    'stdout': result.stdout[:2000],  # Limit output
                    'stderr': result.stderr[:2000] if result.stderr else None
                },
                next_context={
                    'tests_passed': success,
                    'test_summary': parsed_results['summary'],
                    'test_results': parsed_results
                }
            )
            
        except subprocess.TimeoutExpired:
            return self._build_error_result("Test execution timed out (5 minutes)")
        except FileNotFoundError:
            return self._build_error_result(
                f"Test runner not found: {command[0]}. Is {framework} installed?"
            )
        except Exception as e:
            return self._build_error_result(f"Test execution failed: {str(e)}", e)
    
    def _load_testing_preferences(self) -> None:
        """Load testing preferences from language-specific files."""
        if not self.root_folder:
            return
        
        # Try to load testing_preferences.md from language directory
        language_dir = self._get_language_directory()
        if language_dir:
            prefs_file = language_dir / 'testing_preferences.md'
            if prefs_file.exists():
                try:
                    content = prefs_file.read_text(encoding='utf-8')
                    self.testing_preferences['language_specific'] = content
                    self.logger.info(f"Loaded testing preferences from {prefs_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to load testing preferences: {e}")
    
    def _get_language_directory(self) -> Optional[Path]:
        """Get the language-specific directory for this agent."""
        # Override in subclasses to provide language directory
        return None
    
    def ensure_codebase_awareness_initialized(
        self,
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Ensure codebase awareness is initialized.
        
        Args:
            context: Execution context that may contain file paths
            
        Returns:
            Tuple of (success, error_message)
        """
        if self.root_folder and self.codebase_structure:
            return True, None
        
        # Try to find root from context
        hint_path = None
        if 'file_path' in context:
            hint_path = context['file_path']
        elif 'test_path' in context:
            hint_path = context['test_path']
        elif 'working_dir' in context:
            hint_path = context['working_dir']
        
        # Find project root
        success, root, error = self.find_project_root(hint_path)
        if not success:
            return False, error
        
        # Load codebase structure
        success, structure, error = self.load_codebase_structure()
        if not success:
            # Warning only, not a critical error
            return True, error
        
        return True, None
    
    # Abstract methods to be implemented by subclasses
    
    @abstractmethod
    def _detect_test_framework(self, test_info: Dict[str, Any]) -> Optional[str]:
        """
        Detect which test framework to use.
        
        Args:
            test_info: Test information dictionary
            
        Returns:
            Framework name or None if detection fails
        """
        pass
    
    @abstractmethod
    def _build_test_command(
        self,
        framework: str,
        test_path: str,
        options: Dict[str, Any]
    ) -> Optional[List[str]]:
        """
        Build test execution command.
        
        Args:
            framework: Test framework name
            test_path: Path to tests
            options: Additional test options
            
        Returns:
            Command list or None if framework is unknown
        """
        pass
    
    @abstractmethod
    def _parse_test_output(
        self,
        framework: str,
        stdout: str,
        stderr: str,
        return_code: int
    ) -> Dict[str, Any]:
        """
        Parse test output to extract results.
        
        Args:
            framework: Test framework name
            stdout: Standard output
            stderr: Standard error
            return_code: Process return code
            
        Returns:
            Dictionary with parsed results
        """
        pass
    
    @abstractmethod
    def _get_supported_frameworks(self) -> List[str]:
        """
        Get list of supported test frameworks.
        
        Returns:
            List of framework names
        """
        pass
