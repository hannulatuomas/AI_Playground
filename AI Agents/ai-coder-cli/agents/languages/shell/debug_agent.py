
"""
Shell Script Debug Agent

Production-ready debugger for shell scripts (bash/zsh/sh/ksh/dash).
Provides comprehensive debugging support with shell-specific awareness.
"""

import os
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from ...base import DebugAgentBase


class ShellDebugAgent(DebugAgentBase):
    """
    Production-ready Shell Script Debug Agent.
    
    Features:
        - Bash/Zsh/Sh debugging support
        - Script trace analysis (set -x)
        - Variable inspection
        - Exit code debugging
        - Shellcheck integration recommendations
        - Common shell script pitfalls
    """
    
    def __init__(self, name: str = "shell_debug",
                 description: str = "Shell script debugging agent (bash/zsh/sh/ksh/dash)", **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        
        self._timeout = self.config.get('debug', {}).get('default_debugger_timeout', 300)
        self._shellcheck_available = self._check_shellcheck()
        
        # Shell-specific debugging features
        self.shell_debug_flags = {
            'bash': ['set -x', 'set -v', 'set -e', 'set -u', 'set -o pipefail', 'trap ERR'],
            'zsh': ['set -x', 'set -v', 'setopt XTRACE', 'setopt VERBOSE', 'trap ERR'],
            'sh': ['set -x', 'set -v', 'set -e', 'set -u'],  # POSIX-only
            'dash': ['set -x', 'set -v', 'set -e', 'set -u'],
            'ksh': ['set -x', 'set -v', 'set -e', 'set -u', 'trap ERR']
        }
        
        self.logger.info(f"Shell Debug Agent initialized (shellcheck: {self._shellcheck_available})")
        # Load language-specific documentation
        self._load_language_docs()

    def _check_shellcheck(self) -> bool:
        """Check if shellcheck is available."""
        try:
            result = subprocess.run(
                ['shellcheck', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _detect_shell_from_file(self, file_path: str) -> str:
        """
        Detect shell type from script file.
        
        Args:
            file_path: Path to shell script
            
        Returns:
            Shell type (bash, zsh, sh, ksh, dash)
        """
        if not os.path.exists(file_path):
            return 'bash'  # Default
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#!'):
                    for shell in ['bash', 'zsh', 'ksh', 'dash']:
                        if shell in first_line:
                            return shell
                    if '/sh' in first_line or first_line.endswith('sh'):
                        return 'sh'
        except Exception:
            pass
        
        # Check file extension
        if file_path.endswith('.bash'):
            return 'bash'
        elif file_path.endswith('.zsh'):
            return 'zsh'
        elif file_path.endswith('.ksh'):
            return 'ksh'
        elif file_path.endswith('.dash'):
            return 'dash'
        elif file_path.endswith('.sh'):
            return 'sh'
        
        return 'bash'  # Default
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute shell debugging task."""
        self._log_action("Shell debug task", task[:100])
        
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
            elif operation == 'trace_execution':
                return self._trace_execution(context)
            else:
                return self._llm_assisted_debug(task, context)
                
        except Exception as e:
            self.logger.error(f"Shell debug task failed: {e}", exc_info=True)
            return self._build_error_result(f"Debug task failed: {str(e)}", error=e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect debug operation from task description."""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['error', 'fail', 'crash']):
            return 'analyze_error'
        elif any(word in task_lower for word in ['variable', '$', 'value', 'inspect']):
            return 'inspect_variables'
        elif 'syntax' in task_lower or 'shellcheck' in task_lower or 'validate' in task_lower:
            return 'validate_syntax'
        elif 'exit' in task_lower or 'return' in task_lower or '$?' in task:
            return 'debug_exit_code'
        elif 'trace' in task_lower or 'set -x' in task_lower or 'debug output' in task_lower:
            return 'trace_execution'
        
        return 'llm_assisted'
    
    def _analyze_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze shell script error."""
        error_message = context.get('error_message', '')
        code_snippet = context.get('code_snippet', '')
        shell_type = context.get('shell_type', 'bash')
        
        prompt = f"""Analyze this {shell_type} script error:

Error: {error_message}

Code:
{code_snippet}

Provide:
1. Explanation of the error
2. Common causes in shell scripts
3. Recommended fixes with shell code examples
4. Best practices for {shell_type}
5. Debugging commands (set -x, set -e, etc.)

Be specific to {shell_type} scripting."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            analysis = llm_result.get('response', '')
            
            return self._build_success_result(
                "Error analyzed",
                data={
                    'error': error_message,
                    'analysis': analysis,
                    'debug_flags': [
                        'set -x  # Print commands before execution',
                        'set -e  # Exit on error',
                        'set -u  # Error on undefined variables',
                        'set -o pipefail  # Pipeline fails if any command fails'
                    ]
                }
            )
        except Exception as e:
            return self._build_error_result(f"Error analysis failed: {str(e)}", error=e)
    
    def _inspect_variables(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Inspect shell variables."""
        code_snippet = context.get('code_snippet', '')
        variable_names = context.get('variables', [])
        shell_type = context.get('shell_type', 'bash')
        
        prompt = f"""Analyze these {shell_type} script variables:

Code:
{code_snippet}

Variables: {', '.join(variable_names) if variable_names else 'all'}

Provide:
1. Variable expansion rules ($VAR vs ${VAR})
2. Quoting issues ("$VAR" vs '$VAR')
3. Array variables (if applicable)
4. Special variables ($?, $!, $$, $@, $*, etc.)
5. Expected values
6. Common variable issues
7. How to debug with echo/printf

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
                        'echo "VAR=$VAR"',
                        'set | grep VAR',
                        'declare -p VAR'
                    ]
                }
            )
        except Exception as e:
            return self._build_error_result(f"Variable inspection failed: {str(e)}", error=e)
    
    def _validate_syntax(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate shell script syntax."""
        code_snippet = context.get('code_snippet', '')
        file_path = context.get('file_path')
        shell_type = context.get('shell_type', 'bash')
        
        if not code_snippet and not file_path:
            return self._build_error_result("code_snippet or file_path required")
        
        # Try shellcheck if available
        shellcheck_output = None
        if self._shellcheck_available and file_path and os.path.exists(file_path):
            try:
                result = subprocess.run(
                    ['shellcheck', '-f', 'json', file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.stdout:
                    shellcheck_output = result.stdout
            except Exception as e:
                self.logger.warning(f"Shellcheck failed: {e}")
        
        prompt = f"""Validate this {shell_type} script syntax and identify issues:

Code:
{code_snippet if code_snippet else f'File: {file_path}'}

{f'Shellcheck output: {shellcheck_output}' if shellcheck_output else ''}

Check for:
1. Syntax errors
2. Quoting issues
3. Command not found
4. Missing semicolons or newlines
5. Conditional test issues ([ vs [[)
6. Loop syntax

Provide fixes for each issue."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            validation = llm_result.get('response', '')
            
            return self._build_success_result(
                "Syntax validated",
                data={
                    'validation': validation,
                    'shellcheck_output': shellcheck_output,
                    'shellcheck_available': self._shellcheck_available,
                    'syntax_check_cmd': f'{shell_type} -n {file_path if file_path else "script.sh"}'
                }
            )
        except Exception as e:
            return self._build_error_result(f"Syntax validation failed: {str(e)}", error=e)
    
    def _debug_exit_code(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Debug exit codes."""
        exit_code = context.get('exit_code')
        code_snippet = context.get('code_snippet', '')
        
        prompt = f"""Debug this shell script exit code issue:

Exit Code: {exit_code if exit_code is not None else 'Unknown'}

Code:
{code_snippet}

Provide:
1. Meaning of the exit code
2. How $? works in shell scripts
3. Common exit code values (0=success, 1=general error, 2=misuse, 126/127=command issues)
4. Proper error checking techniques
5. Recommended error handling patterns (trap, ||, &&)

Be specific to shell scripting."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            debug_info = llm_result.get('response', '')
            
            # Standard exit codes
            exit_code_meanings = {
                0: "Success",
                1: "General error",
                2: "Misuse of shell command",
                126: "Command cannot execute",
                127: "Command not found",
                128: "Invalid exit argument",
                130: "Script terminated by Ctrl+C",
                255: "Exit status out of range"
            }
            
            meaning = exit_code_meanings.get(exit_code, "Unknown") if exit_code is not None else "N/A"
            
            return self._build_success_result(
                "Exit code analyzed",
                data={
                    'exit_code': exit_code,
                    'standard_meaning': meaning,
                    'debug_info': debug_info,
                    'error_check_examples': [
                        'command || exit 1',
                        'if ! command; then exit 1; fi',
                        'command; if [ $? -ne 0 ]; then exit 1; fi'
                    ]
                }
            )
        except Exception as e:
            return self._build_error_result(f"Exit code debugging failed: {str(e)}", error=e)
    
    def _trace_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide execution tracing guidance."""
        code_snippet = context.get('code_snippet', '')
        file_path = context.get('file_path')
        
        prompt = f"""Provide execution tracing guidance for this shell script:

Code:
{code_snippet if code_snippet else f'File: {file_path}'}

Provide:
1. How to enable tracing (set -x)
2. How to read trace output
3. Conditional tracing techniques
4. PS4 variable customization for better trace output
5. Logging strategies
6. Where to add debug statements

Be practical and command-focused."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            guidance = llm_result.get('response', '')
            
            return self._build_success_result(
                "Execution tracing guidance",
                data={
                    'guidance': guidance,
                    'trace_examples': [
                        '#!/bin/bash\\nset -x  # Enable at start',
                        'set -x; command; set +x  # Trace specific section',
                        'PS4="+${BASH_SOURCE}:${LINENO}: "  # Better trace output',
                        'bash -x script.sh  # Run with tracing'
                    ]
                }
            )
        except Exception as e:
            return self._build_error_result(f"Trace guidance failed: {str(e)}", error=e)
    
    def _llm_assisted_debug(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM for shell debugging assistance."""
        shell_type = context.get('shell_type', 'bash')
        
        prompt = f"""You are a {shell_type} shell scripting expert. Help with this debugging task:

Task: {task}

Context: {json.dumps(context, indent=2)}

Provide:
1. Understanding of the debugging task
2. Recommended debugging approach for shell scripts
3. Specific debugging commands and techniques
4. Expected outcomes
5. Common shell script pitfalls

Be practical and shell-specific."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            guidance = llm_result.get('response', '')
            
            return self._build_success_result(
                "Debug guidance provided",
                data={
                    'task': task,
                    'guidance': guidance,
                    'shellcheck_available': self._shellcheck_available
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
