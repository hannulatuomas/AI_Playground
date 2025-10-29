
"""
Batch Script Debug Agent

Production-ready debugger for Windows Batch (.bat/.cmd) scripts.
"""

import os
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from ...base import DebugAgentBase


class BatchDebugAgent(DebugAgentBase):
    """
    Production-ready Batch Script Debug Agent.
    
    Features:
        - Batch script error analysis
        - Command echo debugging
        - Variable value inspection
        - Exit code analysis
        - Syntax validation
        - Common batch script errors
    """
    
    def __init__(self, name: str = "batch_debug",
                 description: str = "Batch script debugging agent", **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        
        self._timeout = self.config.get('debug', {}).get('default_debugger_timeout', 300)
        
        self.logger.info("Batch Debug Agent initialized")
        # Load language-specific documentation
        self._load_language_docs()

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Batch debugging task."""
        self._log_action("Batch debug task", task[:100])
        
        try:
            operation = context.get('operation', self._detect_operation(task))
            
            if operation == 'analyze_error':
                return self._analyze_error(context)
            elif operation == 'inspect_variables':
                return self._inspect_variables(context)
            elif operation == 'validate_syntax':
                return self._validate_syntax(context)
            elif operation == 'debug_exit_code':
                return self._debug_exit_code(context)
            else:
                return self._llm_assisted_debug(task, context)
                
        except Exception as e:
            self.logger.error(f"Batch debug task failed: {e}", exc_info=True)
            return self._build_error_result(f"Debug task failed: {str(e)}", error=e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect debug operation from task description."""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['error', 'fail', 'crash']):
            return 'analyze_error'
        elif any(word in task_lower for word in ['variable', 'value', 'inspect', '%']):
            return 'inspect_variables'
        elif 'syntax' in task_lower or 'validate' in task_lower:
            return 'validate_syntax'
        elif 'exit' in task_lower or 'errorlevel' in task_lower or 'return' in task_lower:
            return 'debug_exit_code'
        
        return 'llm_assisted'
    
    def _analyze_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze batch script error."""
        error_message = context.get('error_message', '')
        code_snippet = context.get('code_snippet', '')
        
        prompt = f"""Analyze this Windows Batch script error:

Error: {error_message}

Code:
{code_snippet}

Provide:
1. Explanation of the error
2. Common causes in batch scripts
3. Recommended fixes with batch code examples
4. Best practices for batch scripting
5. Debugging commands (ECHO, PAUSE, etc.)

Be specific to Windows batch scripting."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            analysis = llm_result.get('response', '')
            
            return self._build_success_result(
                "Error analyzed",
                data={
                    'error': error_message,
                    'analysis': analysis,
                    'debug_tip': 'Add @ECHO ON at the beginning to see command execution'
                }
            )
        except Exception as e:
            return self._build_error_result(f"Error analysis failed: {str(e)}", error=e)
    
    def _inspect_variables(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Inspect batch variables."""
        code_snippet = context.get('code_snippet', '')
        variable_names = context.get('variables', [])
        
        prompt = f"""Analyze these batch script variables:

Code:
{code_snippet}

Variables: {', '.join(variable_names) if variable_names else 'all'}

Provide:
1. Variable expansion rules (%VAR% vs !VAR!)
2. Environment vs local variables
3. Delayed expansion requirements
4. Expected values
5. Common variable issues
6. How to debug with ECHO

Format as structured analysis."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            analysis = llm_result.get('response', '')
            
            return self._build_success_result(
                "Variables inspected",
                data={
                    'code': code_snippet,
                    'variables': variable_names,
                    'analysis': analysis,
                    'debug_commands': [
                        'ECHO %VARIABLE%',
                        'SET VARIABLE',
                        'SETLOCAL EnableDelayedExpansion'
                    ]
                }
            )
        except Exception as e:
            return self._build_error_result(f"Variable inspection failed: {str(e)}", error=e)
    
    def _validate_syntax(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate batch script syntax."""
        code_snippet = context.get('code_snippet', '')
        file_path = context.get('file_path')
        
        if not code_snippet and not file_path:
            return self._build_error_result("code_snippet or file_path required")
        
        prompt = f"""Validate this batch script syntax and identify issues:

Code:
{code_snippet if code_snippet else f'File: {file_path}'}

Check for:
1. Syntax errors
2. Missing quotes or parentheses
3. Incorrect command usage
4. Label and GOTO issues
5. FOR loop syntax
6. IF statement syntax

Provide fixes for each issue."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            validation = llm_result.get('response', '')
            
            return self._build_success_result(
                "Syntax validated",
                data={
                    'validation': validation,
                    'note': 'Batch scripts often fail silently; use ECHO ON for debugging'
                }
            )
        except Exception as e:
            return self._build_error_result(f"Syntax validation failed: {str(e)}", error=e)
    
    def _debug_exit_code(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Debug exit codes and ERRORLEVEL."""
        exit_code = context.get('exit_code')
        code_snippet = context.get('code_snippet', '')
        
        prompt = f"""Debug this batch script exit code issue:

Exit Code: {exit_code if exit_code is not None else 'Unknown'}

Code:
{code_snippet}

Provide:
1. Meaning of the exit code
2. How ERRORLEVEL works in batch
3. Proper error checking techniques
4. Common exit code values (0=success, 1=error, etc.)
5. Recommended error handling patterns

Be specific to batch scripting."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            debug_info = llm_result.get('response', '')
            
            return self._build_success_result(
                "Exit code analyzed",
                data={
                    'exit_code': exit_code,
                    'debug_info': debug_info,
                    'error_check_examples': [
                        'IF %ERRORLEVEL% NEQ 0 GOTO error',
                        'IF ERRORLEVEL 1 GOTO error',
                        'command || GOTO error'
                    ]
                }
            )
        except Exception as e:
            return self._build_error_result(f"Exit code debugging failed: {str(e)}", error=e)
    
    def _llm_assisted_debug(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM for batch debugging assistance."""
        prompt = f"""You are a Windows Batch scripting expert. Help with this debugging task:

Task: {task}

Context: {json.dumps(context, indent=2)}

Provide:
1. Understanding of the debugging task
2. Recommended debugging approach for batch scripts
3. Specific debugging commands (ECHO, PAUSE, etc.)
4. Expected outcomes
5. Common batch script pitfalls

Be practical and batch-specific."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            guidance = llm_result.get('response', '')
            
            return self._build_success_result(
                "Debug guidance provided",
                data={
                    'task': task,
                    'guidance': guidance
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
