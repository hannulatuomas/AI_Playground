
"""
CPP Debug Agent

Production-ready debugger integration for CPP code using GDB/LLDB.
"""

import os
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from ...base import DebugAgentBase


class CPPDebugAgent(DebugAgentBase):
    """
    Production-ready CPP Debug Agent.
    
    Features:
        - Breakpoint management for CPP code
        - GDB/LLDB integration
        - Core dump analysis
        - Memory debugging (valgrind, sanitizers)
        - Stack trace analysis for CPP exceptions
        - Segfault debugging
        - Memory leak detection
    """
    
    def __init__(self, name: str = "cpp_debug",
                 description: str = "CPP debugging agent", **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        
        self._breakpoints: Dict[str, List[int]] = {}
        self._timeout = self.config.get('debug', {}).get('default_debugger_timeout', 300)
        self._debugger = self._detect_debugger()
        
        self.logger.info(f"CPP Debug Agent initialized with {self._debugger}")
        # Load language-specific documentation
        self._load_language_docs()

    def _detect_debugger(self) -> str:
        """Detect available CPP debugger."""
        for debugger in ['gdb', 'lldb']:
            try:
                result = subprocess.run(
                    [debugger, '--version'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return debugger
            except Exception:
                continue
        return 'none'
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CPP debugging task."""
        self._log_action("CPP debug task", task[:100])
        
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
            elif operation == 'analyze_coredump':
                return self._analyze_coredump(context)
            elif operation == 'memory_debug':
                return self._debug_memory(context)
            elif operation == 'segfault_debug':
                return self._debug_segfault(context)
            else:
                return self._llm_assisted_debug(task, context)
                
        except Exception as e:
            self.logger.error(f"CPP debug task failed: {e}", exc_info=True)
            return self._build_error_result(f"Debug task failed: {str(e)}", error=e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect debug operation from task description."""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['breakpoint', 'break at']):
            if 'clear' in task_lower or 'remove' in task_lower:
                return 'clear_breakpoint'
            elif 'list' in task_lower or 'show' in task_lower:
                return 'list_breakpoints'
            else:
                return 'set_breakpoint'
        elif 'stack' in task_lower or 'backtrace' in task_lower:
            return 'analyze_stack'
        elif 'core' in task_lower or 'dump' in task_lower:
            return 'analyze_coredump'
        elif 'memory' in task_lower or 'leak' in task_lower or 'valgrind' in task_lower:
            return 'memory_debug'
        elif 'segfault' in task_lower or 'segmentation' in task_lower or 'sigsegv' in task_lower:
            return 'segfault_debug'
        
        return 'llm_assisted'
    
    def _set_breakpoint(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Set a breakpoint in CPP code."""
        file_path = context.get('file_path')
        line_number = context.get('line_number')
        
        if not file_path or not line_number:
            return self._build_error_result("file_path and line_number required")
        
        if not os.path.exists(file_path):
            return self._build_error_result(f"File not found: {file_path}")
        
        if file_path not in self._breakpoints:
            self._breakpoints[file_path] = []
        
        if line_number not in self._breakpoints[file_path]:
            self._breakpoints[file_path].append(line_number)
            self._breakpoints[file_path].sort()
        
        # Generate GDB command
        gdb_cmd = f"break {file_path}:{line_number}"
        lldb_cmd = f"breakpoint set --file {file_path} --line {line_number}"
        
        return self._build_success_result(
            f"Breakpoint set at {file_path}:{line_number}",
            data={
                'breakpoints': self._breakpoints,
                'file_path': file_path,
                'line_number': line_number,
                'gdb_command': gdb_cmd,
                'lldb_command': lldb_cmd
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
            return self._build_error_result(f"No breakpoints in {file_path}")
        
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
        """Analyze CPP stack trace."""
        stack_trace = context.get('stack_trace', '')
        
        if not stack_trace:
            return self._build_error_result("stack_trace required")
        
        prompt = f"""Analyze this CPP stack trace/backtrace:

Stack Trace:
{stack_trace}

Provide:
1. Root cause identification
2. Frame-by-frame analysis
3. Potential memory issues (dangling pointers, use-after-free, etc.)
4. Recommended fixes with CPP code examples
5. Debugging strategy with GDB/LLDB commands

Be specific to CPP and memory safety."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            analysis = llm_result.get('response', '')
            
            return self._build_success_result(
                "Stack trace analyzed",
                data={
                    'stack_trace': stack_trace,
                    'analysis': analysis,
                    'debugger': self._debugger
                }
            )
        except Exception as e:
            return self._build_error_result(f"Stack trace analysis failed: {str(e)}", error=e)
    
    def _analyze_coredump(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a core dump file."""
        coredump_path = context.get('coredump_path')
        executable_path = context.get('executable_path')
        
        if not coredump_path:
            return self._build_error_result("coredump_path required")
        
        if not os.path.exists(coredump_path):
            return self._build_error_result(f"Core dump not found: {coredump_path}")
        
        # Generate debugging commands
        gdb_cmd = f"gdb {executable_path if executable_path else ''} {coredump_path}"
        lldb_cmd = f"lldb -c {coredump_path} {executable_path if executable_path else ''}"
        
        prompt = f"""Provide guidance for analyzing a CPP core dump:

Core dump: {coredump_path}
Executable: {executable_path or 'Not specified'}

Provide:
1. Step-by-step GDB/LLDB commands to analyze the core dump
2. What to look for (stack trace, register values, memory state)
3. Common causes of crashes
4. How to extract useful information

Be practical and command-focused."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            guidance = llm_result.get('response', '')
            
            return self._build_success_result(
                "Core dump analysis guidance",
                data={
                    'coredump': coredump_path,
                    'executable': executable_path,
                    'gdb_command': gdb_cmd,
                    'lldb_command': lldb_cmd,
                    'guidance': guidance
                }
            )
        except Exception as e:
            return self._build_error_result(f"Core dump analysis failed: {str(e)}", error=e)
    
    def _debug_memory(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Debug memory issues."""
        code_snippet = context.get('code_snippet', '')
        executable_path = context.get('executable_path')
        
        prompt = f"""Analyze this CPP code for memory-related issues:

Code:
{code_snippet}

Provide:
1. Potential memory leaks
2. Buffer overflows and underflows
3. Use-after-free vulnerabilities
4. Dangling pointer issues
5. Valgrind/AddressSanitizer usage recommendations
6. Code fixes with examples

Focus on CPP memory safety."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            analysis = llm_result.get('response', '')
            
            # Add tool recommendations
            tools_info = {
                'valgrind': f"valgrind --leak-check=full {executable_path or './program'}",
                'asan': "Compile with -fsanitize=address",
                'msan': "Compile with -fsanitize=memory",
                'tsan': "Compile with -fsanitize=thread"
            }
            
            return self._build_success_result(
                "Memory analysis completed",
                data={
                    'analysis': analysis,
                    'tools': tools_info
                }
            )
        except Exception as e:
            return self._build_error_result(f"Memory debugging failed: {str(e)}", error=e)
    
    def _debug_segfault(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Debug segmentation fault."""
        code_snippet = context.get('code_snippet', '')
        error_message = context.get('error_message', '')
        
        prompt = f"""Debug this CPP segmentation fault:

Error: {error_message}

Code:
{code_snippet}

Provide:
1. Likely causes (null pointer, buffer overflow, stack overflow, etc.)
2. How to reproduce and identify the exact line
3. GDB/LLDB debugging steps
4. Recommended fixes with code examples
5. Prevention strategies

Be specific to CPP segfault debugging."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            debug_info = llm_result.get('response', '')
            
            return self._build_success_result(
                "Segfault analyzed",
                data={
                    'error': error_message,
                    'debug_info': debug_info,
                    'debugger': self._debugger
                }
            )
        except Exception as e:
            return self._build_error_result(f"Segfault debugging failed: {str(e)}", error=e)
    
    def _llm_assisted_debug(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM for CPP debugging assistance."""
        prompt = f"""You are a CPP debugging expert. Help with this debugging task:

Task: {task}

Context: {json.dumps(context, indent=2)}

Provide:
1. Understanding of the debugging task
2. Recommended debugging approach for CPP
3. Specific GDB/LLDB commands
4. Expected outcomes
5. Memory safety considerations

Be practical and CPP-specific."""
        
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
