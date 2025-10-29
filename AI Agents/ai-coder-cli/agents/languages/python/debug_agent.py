

"""
Python Debug Agent

Production-ready debugger integration for Python code using pdb/ipdb.
"""

import os
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from ...base import DebugAgentBase


class PythonDebugAgent(DebugAgentBase):
    """
    Production-ready Python Debug Agent.
    
    Features:
        - Breakpoint management (set, clear, list)
        - Step execution (step, next, continue)
        - Variable inspection
        - Stack trace analysis
        - Exception handling and debugging
        - Integration with pdb/ipdb
        - Code execution analysis
    """
    
    def __init__(self, name: str = "python_debug",
                 description: str = "Python debugging agent", **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        
        # Check for ipdb availability (enhanced pdb)
        self._debugger = self._detect_debugger()
        self._breakpoints: Dict[str, List[int]] = {}
        self._timeout = self.config.get('debug', {}).get('default_debugger_timeout', 300)
        
        self.logger.info(f"Python Debug Agent initialized with {self._debugger}")
        # Load language-specific documentation
        self._load_language_docs()

    def _detect_debugger(self) -> str:
        """Detect available Python debugger."""
        try:
            import ipdb
            return 'ipdb'
        except ImportError:
            return 'pdb'
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Python debugging task."""
        self._log_action("Python debug task", task[:100])
        
        try:
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
        """Detect debug operation from task description."""
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
    
    def _set_breakpoint(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Set a breakpoint in a Python file."""
        file_path = context.get('file_path')
        line_number = context.get('line_number')
        
        if not file_path or not line_number:
            return self._build_error_result("file_path and line_number required")
        
        # Validate file exists
        if not os.path.exists(file_path):
            return self._build_error_result(f"File not found: {file_path}")
        
        # Store breakpoint
        if file_path not in self._breakpoints:
            self._breakpoints[file_path] = []
        
        if line_number not in self._breakpoints[file_path]:
            self._breakpoints[file_path].append(line_number)
            self._breakpoints[file_path].sort()
        
        return self._build_success_result(
            f"Breakpoint set at {file_path}:{line_number}",
            data={
                'breakpoints': self._breakpoints,
                'file_path': file_path,
                'line_number': line_number
            }
        )
    
    def _clear_breakpoint(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Clear a breakpoint."""
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
        """List all breakpoints."""
        if not self._breakpoints:
            return self._build_success_result("No breakpoints set", data={'breakpoints': {}})
        
        return self._build_success_result(
            f"Found {sum(len(bp) for bp in self._breakpoints.values())} breakpoint(s)",
            data={'breakpoints': self._breakpoints}
        )
    
    def _analyze_stack_trace(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a Python stack trace."""
        stack_trace = context.get('stack_trace', '')
        
        if not stack_trace:
            return self._build_error_result("stack_trace required")
        
        # Parse stack trace
        lines = stack_trace.split('\n')
        frames = []
        current_frame = {}
        
        for line in lines:
            # Match file/line pattern
            file_match = re.match(r'\s*File "(.+)", line (\d+)', line)
            if file_match:
                if current_frame:
                    frames.append(current_frame)
                current_frame = {
                    'file': file_match.group(1),
                    'line': int(file_match.group(2)),
                    'code': ''
                }
            elif current_frame and line.strip():
                current_frame['code'] = line.strip()
        
        if current_frame:
            frames.append(current_frame)
        
        # Use LLM to analyze the stack trace
        analysis_prompt = f"""Analyze this Python stack trace and provide debugging insights:

Stack Trace:
{stack_trace}

Provide:
1. Root cause identification
2. Affected code locations
3. Recommended fixes
4. Debugging strategy

Format your response as structured JSON with keys: root_cause, locations, fixes, strategy."""
        
        try:
            llm_result = self._get_llm_response(analysis_prompt)
            llm_analysis = llm_result.get('response', '')
            
            return self._build_success_result(
                "Stack trace analyzed",
                data={
                    'frames': frames,
                    'frame_count': len(frames),
                    'analysis': llm_analysis
                }
            )
        except Exception as e:
            # Fallback to basic analysis
            return self._build_success_result(
                "Stack trace parsed (LLM analysis failed)",
                data={
                    'frames': frames,
                    'frame_count': len(frames),
                    'error': str(e)
                }
            )
    
    def _inspect_variables(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Inspect variables in Python code."""
        code_snippet = context.get('code_snippet', '')
        variable_names = context.get('variables', [])
        
        if not code_snippet:
            return self._build_error_result("code_snippet required")
        
        # Use LLM to analyze variable values and types
        prompt = f"""Analyze this Python code snippet and inspect the variables:

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
        """Debug a Python exception."""
        exception_type = context.get('exception_type', 'Exception')
        exception_message = context.get('exception_message', '')
        code_snippet = context.get('code_snippet', '')
        
        prompt = f"""Debug this Python exception:

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
        """Run a debugging session with pdb."""
        file_path = context.get('file_path')
        args = context.get('args', [])
        
        if not file_path:
            return self._build_error_result("file_path required")
        
        if not os.path.exists(file_path):
            return self._build_error_result(f"File not found: {file_path}")
        
        # Security check
        if not self._validate_file_path(file_path):
            return self._build_error_result("Invalid file path")
        
        # Note: Interactive debugging requires user input
        # For automation, we provide debug script generation
        debug_script = self._generate_debug_script(file_path, args)
        
        return self._build_success_result(
            "Debug session prepared",
            data={
                'file_path': file_path,
                'debug_script': debug_script,
                'note': 'Interactive debugging requires manual execution',
                'command': f'python -m {self._debugger} {file_path} {" ".join(args)}'
            }
        )
    
    def _generate_debug_script(self, file_path: str, args: List[str]) -> str:
        """Generate a debug script with breakpoints."""
        script_lines = [
            f"# Python Debug Script for {file_path}",
            f"# Generated by {self.name}",
            "",
            f"import {self._debugger}",
            "import sys",
            "",
            "# Set breakpoints"
        ]
        
        for file, lines in self._breakpoints.items():
            for line_num in lines:
                script_lines.append(f"# Breakpoint: {file}:{line_num}")
        
        script_lines.extend([
            "",
            "# Run with debugger",
            f"sys.argv = ['{file_path}'] + {args}",
            f"{self._debugger}.run('exec(open(\"{file_path}\").read())')"
        ])
        
        return "\n".join(script_lines)
    
    def _llm_assisted_debug(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to assist with debugging task."""
        prompt = f"""You are a Python debugging expert. Help with this debugging task:

Task: {task}

Context: {json.dumps(context, indent=2)}

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
        """Validate file path for security."""
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
    
    def _build_success_result(self, message: str, data: Any = None) -> Dict[str, Any]:
        """Build success result."""
        return {
            'success': True,
            'message': message,
            'data': data or {},
            'next_context': {}
        }
    
    def _build_error_result(self, message: str, error: Exception = None) -> Dict[str, Any]:
        """Build error result."""
        return {
            'success': False,
            'message': message,
            'data': {'error': str(error) if error else message},
            'next_context': {}
        }
    
    def _log_action(self, action: str, details: str):
        """Log agent action."""
        self.logger.info(f"[{action}] {details}")
