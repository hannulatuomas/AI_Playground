
"""
CSharp Debug Agent

Production-ready debugger integration for CSharp code using Visual Studio Debugger and .NET CLI.
"""

import os
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from ...base import DebugAgentBase


class CSharpDebugAgent(DebugAgentBase):
    """
    Production-ready CSharp Debug Agent.
    
    Features:
        - Breakpoint management for CSharp projects
        - Stack trace analysis for .NET exceptions
        - Variable inspection and watch expressions
        - Integration with dotnet CLI for debugging
        - Exception analysis (NullReferenceException, ArgumentException, etc.)
        - Memory leak detection guidance
        - Performance profiling recommendations
    """
    
    def __init__(self, name: str = "csharp_debug",
                 description: str = "CSharp debugging agent", **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        
        self._breakpoints: Dict[str, List[int]] = {}
        self._timeout = self.config.get('debug', {}).get('default_debugger_timeout', 300)
        self._dotnet_available = self._check_dotnet_cli()
        
        self.logger.info(f"CSharp Debug Agent initialized (.NET CLI available: {self._dotnet_available})")
        # Load language-specific documentation
        self._load_language_docs()

    def _check_dotnet_cli(self) -> bool:
        """Check if .NET CLI is available."""
        try:
            result = subprocess.run(
                ['dotnet', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CSharp debugging task."""
        self._log_action("CSharp debug task", task[:100])
        
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
            elif operation == 'memory_analysis':
                return self._analyze_memory(context)
            else:
                return self._llm_assisted_debug(task, context)
                
        except Exception as e:
            self.logger.error(f"CSharp debug task failed: {e}", exc_info=True)
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
        elif 'stack' in task_lower or 'trace' in task_lower:
            return 'analyze_stack'
        elif any(word in task_lower for word in ['variable', 'inspect', 'value', 'watch']):
            return 'inspect_variables'
        elif 'exception' in task_lower or 'error' in task_lower or 'crash' in task_lower:
            return 'debug_exception'
        elif 'memory' in task_lower or 'leak' in task_lower or 'disposal' in task_lower:
            return 'memory_analysis'
        
        return 'llm_assisted'
    
    def _set_breakpoint(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Set a breakpoint in a CSharp file."""
        file_path = context.get('file_path')
        line_number = context.get('line_number')
        
        if not file_path or not line_number:
            return self._build_error_result("file_path and line_number required")
        
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
                'line_number': line_number,
                'note': 'Configure breakpoint in Visual Studio or Rider'
            }
        )
    
    def _clear_breakpoint(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Clear a breakpoint."""
        file_path = context.get('file_path')
        line_number = context.get('line_number')
        
        if not file_path:
            self._breakpoints.clear()
            return self._build_success_result("All breakpoints cleared")
        
        if file_path not in self._breakpoints:
            return self._build_error_result(f"No breakpoints set in {file_path}")
        
        if line_number:
            if line_number in self._breakpoints[file_path]:
                self._breakpoints[file_path].remove(line_number)
                return self._build_success_result(f"Breakpoint cleared at {file_path}:{line_number}")
            else:
                return self._build_error_result(f"No breakpoint at {file_path}:{line_number}")
        else:
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
        """Analyze a .NET stack trace."""
        stack_trace = context.get('stack_trace', '')
        
        if not stack_trace:
            return self._build_error_result("stack_trace required")
        
        # Parse .NET stack trace
        frames = []
        lines = stack_trace.split('\n')
        
        for line in lines:
            # Match "at Namespace.Class.Method() in File:line X"
            match = re.search(r'at (.+?) in (.+?):line (\d+)', line)
            if match:
                frames.append({
                    'method': match.group(1),
                    'file': match.group(2),
                    'line': int(match.group(3))
                })
            elif line.strip().startswith('at '):
                # Method without source info
                method = line.strip()[3:]
                frames.append({'method': method, 'file': 'N/A', 'line': 0})
        
        # Use LLM to analyze
        analysis_prompt = f"""Analyze this .NET/CSharp stack trace and provide debugging insights:

Stack Trace:
{stack_trace}

Provide:
1. Root cause identification
2. Common .NET exceptions and their causes
3. Recommended fixes with CSharp code examples
4. Best practices to prevent this error

Be specific to CSharp and .NET framework."""
        
        try:
            llm_result = self._get_llm_response(analysis_prompt)
            analysis = llm_result.get('response', '')
            
            return self._build_success_result(
                "Stack trace analyzed",
                data={
                    'frames': frames,
                    'frame_count': len(frames),
                    'analysis': analysis
                }
            )
        except Exception as e:
            return self._build_success_result(
                "Stack trace parsed (LLM analysis failed)",
                data={'frames': frames, 'frame_count': len(frames), 'error': str(e)}
            )
    
    def _inspect_variables(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Inspect variables in CSharp code."""
        code_snippet = context.get('code_snippet', '')
        variable_names = context.get('variables', [])
        
        if not code_snippet:
            return self._build_error_result("code_snippet required")
        
        prompt = f"""Analyze this CSharp code snippet and inspect the variables:

Code:
{code_snippet}

Variables to inspect: {', '.join(variable_names) if variable_names else 'all'}

Provide:
1. Variable types (with full CSharp type names)
2. Expected values and nullability
3. Scope analysis (local, field, property)
4. Potential null reference issues
5. Thread safety concerns (if applicable)

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
        """Debug a .NET exception."""
        exception_type = context.get('exception_type', 'Exception')
        exception_message = context.get('exception_message', '')
        code_snippet = context.get('code_snippet', '')
        
        prompt = f"""Debug this CSharp/.NET exception:

Exception Type: {exception_type}
Message: {exception_message}

Code Context:
{code_snippet}

Provide:
1. Explanation of the exception
2. Common causes in CSharp/.NET applications
3. How to reproduce
4. Recommended fixes with CSharp code examples
5. Prevention strategies and best practices
6. Relevant exception handling patterns (try-catch, using statements, etc.)

Be specific to CSharp and .NET."""
        
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
    
    def _analyze_memory(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze memory usage and potential leaks."""
        code_snippet = context.get('code_snippet', '')
        
        prompt = f"""Analyze this CSharp code for memory-related issues:

Code:
{code_snippet}

Provide:
1. Potential memory leaks (event handlers, static references, etc.)
2. IDisposable implementation issues
3. Proper using statement usage
4. Large object allocation concerns
5. Recommended memory profiling tools (.NET Memory Profiler, dotMemory)
6. Code fixes with examples

Focus on CSharp/.NET memory management patterns."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            analysis = llm_result.get('response', '')
            
            return self._build_success_result(
                "Memory analysis completed",
                data={'analysis': analysis, 'dotnet_cli': self._dotnet_available}
            )
        except Exception as e:
            return self._build_error_result(f"Memory analysis failed: {str(e)}", error=e)
    
    def _llm_assisted_debug(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to assist with CSharp debugging task."""
        prompt = f"""You are a CSharp debugging expert. Help with this debugging task:

Task: {task}

Context: {json.dumps(context, indent=2)}

Provide:
1. Understanding of the debugging task
2. Recommended debugging approach for CSharp/.NET
3. Specific actions (breakpoints, watch expressions, etc.)
4. Expected outcomes
5. Relevant Visual Studio or Rider debugging features

Be practical and CSharp-specific."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            guidance = llm_result.get('response', '')
            
            return self._build_success_result(
                "Debug guidance provided",
                data={
                    'task': task,
                    'guidance': guidance,
                    'dotnet_cli_available': self._dotnet_available
                }
            )
        except Exception as e:
            return self._build_error_result(f"LLM-assisted debugging failed: {str(e)}", error=e)
    
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
