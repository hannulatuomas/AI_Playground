

"""
Base class for all build agents.

This module defines the common interface and functionality for language-specific
build agents with project context awareness.
"""

import os
import subprocess
from abc import abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List

from .agent_base import Agent
from ..utils.codebase_awareness import CodebaseAwarenessMixin


class BuildAgentBase(Agent, CodebaseAwarenessMixin):
    """
    Abstract base class for build agents with project context awareness.
    
    Provides common functionality for:
    - Build system detection
    - Dependency installation
    - Package building
    - Test execution
    - Build validation
    - Clean operations
    - Project root detection and context loading
    - Rules hierarchy awareness (project_preferences > user_preferences > best_practices)
    
    Subclasses must implement:
    - _detect_build_system: Detect language-specific build system
    - _install_dependencies: Install language-specific dependencies
    - _build_package: Build language-specific packages
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        supported_build_systems: List[str],
        **kwargs
    ):
        """
        Initialize build agent with project context awareness.
        
        Args:
            name: Agent name
            description: Agent description
            supported_build_systems: List of supported build systems
            **kwargs: Additional arguments passed to Agent base class
        """
        super().__init__(name=name, description=description, **kwargs)
        self.supported_build_systems = supported_build_systems
        self._build_system = None
        self._timeout = self.config.get('build', {}).get('default_build_timeout', 600)
        
        # Initialize codebase awareness
        self.init_codebase_awareness()
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute build task with project context awareness.
        
        Args:
            task: Build task description
            context: Execution context with optional 'project_dir', 'operation'
            
        Returns:
            Result dictionary with build status and details
        """
        self._log_action("Build task", task[:100])
        
        try:
            # Initialize project context awareness
            success, error = self.ensure_codebase_awareness_initialized(context)
            if not success and error:
                self.logger.warning(f"Project context initialization: {error}")
            
            operation = context.get('operation', self._detect_operation(task))
            project_dir = context.get('project_dir', os.getcwd())
            
            # Validate project directory
            if not os.path.isdir(project_dir):
                return self._build_error_result(f"Invalid project directory: {project_dir}")
            
            # Route to appropriate operation
            if operation == 'detect_build_system':
                return self._detect_build_system(project_dir)
            elif operation == 'install_dependencies':
                return self._install_dependencies(project_dir, context)
            elif operation == 'build_package':
                return self._build_package(project_dir, context)
            elif operation == 'run_tests':
                return self._run_tests(project_dir, context)
            elif operation == 'validate_config':
                return self._validate_build_config(project_dir)
            elif operation == 'clean_build':
                return self._clean_build(project_dir)
            else:
                # Use LLM to understand the build request
                return self._llm_assisted_build(task, project_dir, context)
                
        except Exception as e:
            self.logger.error(f"Build task failed: {e}", exc_info=True)
            return self._build_error_result(f"Build task failed: {str(e)}", error=e)
    
    def _detect_operation(self, task: str) -> str:
        """
        Detect build operation from task description.
        
        Args:
            task: Task description
            
        Returns:
            Operation name
        """
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['detect', 'identify', 'find build system']):
            return 'detect_build_system'
        elif any(word in task_lower for word in ['install', 'dependencies', 'requirements']):
            return 'install_dependencies'
        elif any(word in task_lower for word in ['build', 'compile', 'package']):
            return 'build_package'
        elif any(word in task_lower for word in ['test', 'run tests']):
            return 'run_tests'
        elif any(word in task_lower for word in ['validate', 'check config', 'verify']):
            return 'validate_config'
        elif any(word in task_lower for word in ['clean', 'remove build']):
            return 'clean_build'
        
        return 'llm_assisted'
    
    @abstractmethod
    def _detect_build_system(self, project_dir: str) -> Dict[str, Any]:
        """
        Detect the build system used in the project.
        
        Subclasses must implement language-specific build system detection.
        
        Args:
            project_dir: Project directory path
            
        Returns:
            Result dictionary with detected build system
        """
        pass
    
    @abstractmethod
    def _install_dependencies(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Install project dependencies.
        
        Subclasses must implement language-specific dependency installation.
        
        Args:
            project_dir: Project directory path
            context: Execution context
            
        Returns:
            Result dictionary with installation status
        """
        pass
    
    @abstractmethod
    def _build_package(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the project package.
        
        Subclasses must implement language-specific package building.
        
        Args:
            project_dir: Project directory path
            context: Execution context
            
        Returns:
            Result dictionary with build status and artifacts
        """
        pass
    
    def _run_tests(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run project tests.
        
        This provides a default implementation that can be overridden
        by subclasses for language-specific test execution.
        
        Args:
            project_dir: Project directory path
            context: Execution context
            
        Returns:
            Result dictionary with test results
        """
        return self._build_error_result("Test execution not implemented for this language")
    
    def _validate_build_config(self, project_dir: str) -> Dict[str, Any]:
        """
        Validate build configuration files.
        
        This provides a default implementation that can be overridden
        by subclasses for language-specific validation.
        
        Args:
            project_dir: Project directory path
            
        Returns:
            Result dictionary with validation status
        """
        return self._build_success_result(
            "No specific validation implemented for this build system",
            data={'project_dir': project_dir}
        )
    
    def _clean_build(self, project_dir: str) -> Dict[str, Any]:
        """
        Clean build artifacts.
        
        This provides a default implementation that can be overridden
        by subclasses for language-specific clean operations.
        
        Args:
            project_dir: Project directory path
            
        Returns:
            Result dictionary with cleaned artifacts
        """
        return self._build_success_result(
            "No specific clean operation implemented for this build system",
            data={'project_dir': project_dir}
        )
    
    def _llm_assisted_build(self, task: str, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to assist with build task.
        
        Args:
            task: Task description
            project_dir: Project directory path
            context: Execution context
            
        Returns:
            Result dictionary with build guidance
        """
        # Detect build system for context
        detection = self._detect_build_system(project_dir)
        build_system = detection['data'].get('build_system', 'unknown') if detection['success'] else 'unknown'
        
        prompt = f"""You are a build system expert. Help with this build task:

Task: {task}

Project Directory: {project_dir}
Build System: {build_system}
Supported Systems: {', '.join(self.supported_build_systems)}

Provide:
1. Understanding of the build task
2. Recommended build commands
3. Step-by-step build process
4. Common issues and solutions

Be specific and actionable."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            guidance = llm_result.get('response', '')
            
            return self._build_success_result(
                "Build guidance provided",
                data={
                    'task': task,
                    'build_system': build_system,
                    'guidance': guidance
                }
            )
        except Exception as e:
            return self._build_error_result(f"LLM-assisted build failed: {str(e)}", error=e)
    
    def _run_command(
        self,
        cmd: List[str],
        cwd: str,
        timeout: Optional[int] = None
    ) -> subprocess.CompletedProcess:
        """
        Run a shell command with timeout and capture output.
        
        Args:
            cmd: Command and arguments as list
            cwd: Working directory
            timeout: Timeout in seconds (uses default if None)
            
        Returns:
            CompletedProcess instance
            
        Raises:
            subprocess.TimeoutExpired: If command times out
            subprocess.CalledProcessError: If command fails
        """
        if timeout is None:
            timeout = self._timeout
        
        self.logger.debug(f"Running command: {' '.join(cmd)} in {cwd}")
        
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return result
