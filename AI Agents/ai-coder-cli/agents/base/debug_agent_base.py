

"""
Base class for all debug agents.

This module defines the common interface and functionality for language-specific
debug agents with project context awareness.
"""

import os
import re
from abc import abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List

from .agent_base import Agent
from ..utils.codebase_awareness import CodebaseAwarenessMixin


class DebugAgentBase(Agent, CodebaseAwarenessMixin):
    """
    Abstract base class for debug agents with project context awareness.
    
    Provides common functionality for:
    - Breakpoint management
    - Stack trace analysis
    - Variable inspection
    - Exception debugging
    - Code execution analysis
    - Project root detection and context loading
    - Rules hierarchy awareness (project_preferences > user_preferences > best_practices)
    
    Subclasses must implement:
    - _detect_debugger: Detect available debugger for the language
    - _set_breakpoint: Set language-specific breakpoints
    - _analyze_stack_trace: Analyze language-specific stack traces
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        **kwargs
    ):
        """
        Initialize debug agent with project context awareness.
        
        Args:
            name: Agent name
            description: Agent description
            **kwargs: Additional arguments passed to Agent base class
        """
        super().__init__(name=name, description=description, **kwargs)
        self._debugger = self._detect_debugger()
        self._breakpoints: Dict[str, List[int]] = {}
        self._timeout = self.config.get('debug', {}).get('default_debugger_timeout', 300)
        
        # Initialize codebase awareness
        self.init_codebase_awareness()
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute debugging task with project context awareness.
        
        Args:
            task: Debug task description
            context: Execution context with optional debug information
            
        Returns:
            Result dictionary with debug status and details
        """
        self._log_action("Debug task", task[:100])
        
        try:
            # Initialize project context awareness
            success, error = self.ensure_codebase_awareness_initialized(context)
            if not success and error:
                self.logger.warning(f"Project context initialization: {error}")
            
            operation = context.get('operation', self._detect_operation(task))
            
            if operation == 'set_breakpoint':
                return self._set_breakpoint(context)
            elif operation == 'clear_breakpoint':
                return self._clear_breakpoint(context)
            elif operation == 'list_breakpoints':
                return self._list_breakpoints()
            elif operation == 'analyze_stack':
                return self._analyze_stack_trace(context)
            elif operation == 'inspect_variables':
                return self._inspect_variables(context)
            elif operation == 'debug_exception':
                return self._debug_exception(context)
            elif operation == 'run_debug_session':
                return self._run_debug_session(context)
            else:
                # Use LLM to understand the debugging request
                return self._llm_assisted_debug(task, context)
                
        except Exception as e:
            self.logger.error(f"Debug task failed: {e}", exc_info=True)
            return self._build_error_result(f"Debug task failed: {str(e)}", error=e)
    
    def _detect_operation(self, task: str) -> str:
        """
        Detect debug operation from task description.
        
        Args:
            task: Task description
            
        Returns:
            Operation name
        """
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['breakpoint', 'break at', 'stop at']):
            if 'clear' in task_lower or 'remove' in task_lower:
                return 'clear_breakpoint'
            elif 'list' in task_lower or 'show' in task_lower:
                return 'list_breakpoints'
            else:
                return 'set_breakpoint'
        elif 'stack' in task_lower or 'trace' in task_lower or 'traceback' in task_lower:
            return 'analyze_stack'
        elif any(word in task_lower for word in ['variable', 'inspect', 'value of', 'check']):
            return 'inspect_variables'
        elif 'exception' in task_lower or 'error' in task_lower or 'crash' in task_lower:
            return 'debug_exception'
        elif 'debug' in task_lower or 'run' in task_lower:
            return 'run_debug_session'
        
        return 'llm_assisted'
    
    @abstractmethod
    def _detect_debugger(self) -> str:
        """
        Detect available debugger for the language.
        
        Subclasses must implement language-specific debugger detection.
        
        Returns:
            Debugger name
        """
        pass
    
    @abstractmethod
    def _set_breakpoint(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set a breakpoint.
        
        Subclasses must implement language-specific breakpoint setting.
        
        Args:
            context: Context with file_path and line_number
            
        Returns:
            Result dictionary with breakpoint details
        """
        pass
    
    def _clear_breakpoint(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clear a breakpoint.
        
        This provides a default implementation for clearing breakpoints.
        
        Args:
            context: Context with optional file_path and line_number
            
        Returns:
            Result dictionary
        """
        file_path = context.get('file_path')
        line_number = context.get('line_number')
        
        if not file_path:
            # Clear all breakpoints
            self._breakpoints.clear()
            return self._build_success_result("All breakpoints cleared")
        
        if file_path not in self._breakpoints:
            return self._build_error_result(f"No breakpoints set in {file_path}")
        
        if line_number:
            if line_number in self._breakpoints[file_path]:
                self._breakpoints[file_path].remove(line_number)
                return self._build_success_result(
                    f"Breakpoint cleared at {file_path}:{line_number}"
                )
            else:
                return self._build_error_result(
                    f"No breakpoint at {file_path}:{line_number}"
                )
        else:
            # Clear all breakpoints for this file
            del self._breakpoints[file_path]
            return self._build_success_result(f"All breakpoints cleared in {file_path}")
    
    def _list_breakpoints(self) -> Dict[str, Any]:
        """
        List all breakpoints.
        
        Returns:
            Result dictionary with breakpoint list
        """
        if not self._breakpoints:
            return self._build_success_result("No breakpoints set", data={'breakpoints': {}})
        
        return self._build_success_result(
            f"Found {sum(len(bp) for bp in self._breakpoints.values())} breakpoint(s)",
            data={'breakpoints': self._breakpoints}
        )
    
    @abstractmethod
    def _analyze_stack_trace(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a stack trace.
        
        Subclasses must implement language-specific stack trace analysis.
        
        Args:
            context: Context with stack_trace
            
        Returns:
            Result dictionary with analysis
        """
        pass
    
    def _inspect_variables(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inspect variables in code.
        
        This provides a default LLM-based implementation.
        
        Args:
            context: Context with code_snippet and optional variables list
            
        Returns:
            Result dictionary with variable analysis
        """
        code_snippet = context.get('code_snippet', '')
        variable_names = context.get('variables', [])
        
        if not code_snippet:
            return self._build_error_result("code_snippet required")
        
        # Use LLM to analyze variable values and types
        prompt = f"""Analyze this code snippet and inspect the variables:

Code:
{code_snippet}

Variables to inspect: {', '.join(variable_names) if variable_names else 'all'}

Provide:
1. Variable types
2. Expected values
3. Scope analysis
4. Potential issues

Format as structured analysis."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            analysis = llm_result.get('response', '')
            
            return self._build_success_result(
                "Variables inspected",
                data={
                    'code': code_snippet,
                    'variables': variable_names,
                    'analysis': analysis
                }
            )
        except Exception as e:
            return self._build_error_result(f"Variable inspection failed: {str(e)}", error=e)
    
    def _debug_exception(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Debug an exception.
        
        This provides a default LLM-based implementation.
        
        Args:
            context: Context with exception details
            
        Returns:
            Result dictionary with debug information
        """
        exception_type = context.get('exception_type', 'Exception')
        exception_message = context.get('exception_message', '')
        code_snippet = context.get('code_snippet', '')
        
        prompt = f"""Debug this exception:

Exception Type: {exception_type}
Message: {exception_message}

Code Context:
{code_snippet}

Provide:
1. Explanation of the exception
2. Common causes
3. How to reproduce
4. Recommended fixes with code examples
5. Prevention strategies

Be specific and actionable."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            debug_info = llm_result.get('response', '')
            
            return self._build_success_result(
                "Exception analyzed",
                data={
                    'exception_type': exception_type,
                    'message': exception_message,
                    'debug_info': debug_info
                }
            )
        except Exception as e:
            return self._build_error_result(f"Exception debugging failed: {str(e)}", error=e)
    
    def _run_debug_session(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a debugging session.
        
        This provides a default implementation that can be overridden.
        
        Args:
            context: Context with file_path and args
            
        Returns:
            Result dictionary with debug session details
        """
        file_path = context.get('file_path')
        
        if not file_path:
            return self._build_error_result("file_path required")
        
        if not os.path.exists(file_path):
            return self._build_error_result(f"File not found: {file_path}")
        
        return self._build_success_result(
            "Debug session prepared (requires manual execution)",
            data={
                'file_path': file_path,
                'debugger': self._debugger,
                'note': 'Interactive debugging requires manual execution'
            }
        )
    
    def _llm_assisted_debug(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to assist with debugging task.
        
        Args:
            task: Task description
            context: Execution context
            
        Returns:
            Result dictionary with debug guidance
        """
        prompt = f"""You are a debugging expert. Help with this debugging task:

Task: {task}

Context: {context}

Provide:
1. Understanding of the debugging task
2. Recommended debugging approach
3. Specific actions to take
4. Expected outcomes

Be practical and specific."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            guidance = llm_result.get('response', '')
            
            return self._build_success_result(
                "Debug guidance provided",
                data={
                    'task': task,
                    'guidance': guidance,
                    'debugger': self._debugger
                }
            )
        except Exception as e:
            return self._build_error_result(f"LLM-assisted debugging failed: {str(e)}", error=e)
    
    def _validate_file_path(self, file_path: str) -> bool:
        """
        Validate file path for security.
        
        Args:
            file_path: File path to validate
            
        Returns:
            True if path is valid and allowed
        """
        try:
            # Check if path is within allowed directories
            blocked_paths = self.config.get('security', {}).get('blocked_paths', [])
            abs_path = os.path.abspath(file_path)
            
            for blocked in blocked_paths:
                if abs_path.startswith(blocked):
                    self.logger.warning(f"Blocked path access: {abs_path}")
                    return False
            
            return True
        except Exception:
            return False
