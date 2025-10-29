
"""
PowerShell Debug Agent

Production-ready debugger for PowerShell scripts.
"""

import os
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from ...base import DebugAgentBase


class PowerShellDebugAgent(DebugAgentBase):
    """
    Production-ready PowerShell Debug Agent.
    
    Features:
        - Breakpoint management for PowerShell
        - Stack trace analysis for PowerShell errors
        - Variable inspection and watch expressions
        - Exception debugging (ErrorRecord, Exception)
        - Cmdlet parameter validation
        - Pipeline debugging
    """
    
    def __init__(self, name: str = "powershell_debug",
                 description: str = "PowerShell debugging agent", **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        
        self._breakpoints: Dict[str, List[int]] = {}
        self._timeout = self.config.get('debug', {}).get('default_debugger_timeout', 300)
        self._pwsh_available = self._check_powershell()
        
        self.logger.info(f"PowerShell Debug Agent initialized (PowerShell available: {self._pwsh_available})")
        # Load language-specific documentation
        self._load_language_docs()

    def _check_powershell(self) -> bool:
        """Check if PowerShell is available."""
        for cmd in ['pwsh', 'powershell']:
            try:
                result = subprocess.run(
                    [cmd, '-Version'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return True
            except Exception:
                continue
        return False
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute PowerShell debugging task."""
        self._log_action("PowerShell debug task", task[:100])
        
        try:
            operation = context.get('operation', self._detect_operation(task))
            
            if operation == 'set_breakpoint':
                return self._set_breakpoint(context)
            elif operation == 'clear_breakpoint':
                return self._clear_breakpoint(context)
            elif operation == 'list_breakpoints':
                return self._list_breakpoints()
            elif operation == 'analyze_error':
                return self._analyze_error(context)
            elif operation == 'inspect_variables':
                return self._inspect_variables(context)
            elif operation == 'debug_pipeline':
                return self._debug_pipeline(context)
            else:
                return self._llm_assisted_debug(task, context)
                
        except Exception as e:
            self.logger.error(f"PowerShell debug task failed: {e}", exc_info=True)
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
        elif 'error' in task_lower or 'exception' in task_lower or 'errorrecord' in task_lower:
            return 'analyze_error'
        elif any(word in task_lower for word in ['variable', '$', 'inspect', 'value']):
            return 'inspect_variables'
        elif 'pipeline' in task_lower or '|' in task:
            return 'debug_pipeline'
        
        return 'llm_assisted'
    
    def _set_breakpoint(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Set a breakpoint in PowerShell script."""
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
        
        # Generate PowerShell breakpoint command
        ps_cmd = f"Set-PSBreakpoint -Script '{file_path}' -Line {line_number}"
        
        return self._build_success_result(
            f"Breakpoint set at {file_path}:{line_number}",
            data={
                'breakpoints': self._breakpoints,
                'file_path': file_path,
                'line_number': line_number,
                'powershell_command': ps_cmd
            }
        )
    
    def _clear_breakpoint(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Clear a breakpoint."""
        file_path = context.get('file_path')
        line_number = context.get('line_number')
        
        if not file_path:
            self._breakpoints.clear()
            return self._build_success_result(
                "All breakpoints cleared",
                data={'powershell_command': 'Get-PSBreakpoint | Remove-PSBreakpoint'}
            )
        
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
            return self._build_success_result(
                "No breakpoints set",
                data={
                    'breakpoints': {},
                    'powershell_command': 'Get-PSBreakpoint'
                }
            )
        
        return self._build_success_result(
            f"Found {sum(len(bp) for bp in self._breakpoints.values())} breakpoint(s)",
            data={'breakpoints': self._breakpoints}
        )
    
    def _analyze_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze PowerShell error."""
        error_message = context.get('error_message', '')
        error_record = context.get('error_record', '')
        code_snippet = context.get('code_snippet', '')
        
        prompt = f"""Analyze this PowerShell error:

Error: {error_message}
ErrorRecord: {error_record}

Code:
{code_snippet}

Provide:
1. Explanation of the error
2. Common causes in PowerShell
3. Understanding ErrorRecord properties
4. Recommended fixes with PowerShell code examples
5. Error handling best practices (Try/Catch, $ErrorActionPreference)
6. Debugging commands ($Error[0], Get-Error, etc.)

Be specific to PowerShell error handling."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            analysis = llm_result.get('response', '')
            
            return self._build_success_result(
                "Error analyzed",
                data={
                    'error': error_message,
                    'analysis': analysis,
                    'debug_commands': [
                        '$Error[0] | Format-List * -Force',
                        'Get-Error',
                        '$Error[0].InvocationInfo.PositionMessage'
                    ]
                }
            )
        except Exception as e:
            return self._build_error_result(f"Error analysis failed: {str(e)}", error=e)
    
    def _inspect_variables(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Inspect PowerShell variables."""
        code_snippet = context.get('code_snippet', '')
        variable_names = context.get('variables', [])
        
        prompt = f"""Analyze these PowerShell variables:

Code:
{code_snippet}

Variables: {', '.join(variable_names) if variable_names else 'all'}

Provide:
1. Variable types (string, int, array, hashtable, PSObject, etc.)
2. Scope analysis (local, script, global)
3. Expected values
4. Automatic variables ($_, $PSItem, $args, etc.)
5. Common variable issues
6. How to inspect with Get-Variable

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
                        'Get-Variable',
                        '$PSBoundParameters',
                        'Get-Variable -Scope Script'
                    ]
                }
            )
        except Exception as e:
            return self._build_error_result(f"Variable inspection failed: {str(e)}", error=e)
    
    def _debug_pipeline(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Debug PowerShell pipeline."""
        pipeline_code = context.get('pipeline_code', '')
        
        if not pipeline_code:
            return self._build_error_result("pipeline_code required")
        
        prompt = f"""Debug this PowerShell pipeline:

Pipeline:
{pipeline_code}

Provide:
1. How the pipeline processes objects
2. Potential issues (wrong object types, null values, etc.)
3. How to inspect pipeline objects ($_ at each stage)
4. Performance considerations
5. Recommended debugging techniques
6. Fixed or improved pipeline code

Be specific to PowerShell pipelines."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            debug_info = llm_result.get('response', '')
            
            return self._build_success_result(
                "Pipeline analyzed",
                data={
                    'pipeline': pipeline_code,
                    'debug_info': debug_info,
                    'debug_tip': 'Add | ForEach-Object { Write-Host $_; $_ } to inspect pipeline objects'
                }
            )
        except Exception as e:
            return self._build_error_result(f"Pipeline debugging failed: {str(e)}", error=e)
    
    def _llm_assisted_debug(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM for PowerShell debugging assistance."""
        prompt = f"""You are a PowerShell debugging expert. Help with this debugging task:

Task: {task}

Context: {json.dumps(context, indent=2)}

Provide:
1. Understanding of the debugging task
2. Recommended debugging approach for PowerShell
3. Specific debugging commands and techniques
4. Expected outcomes
5. PowerShell best practices

Be practical and PowerShell-specific."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            guidance = llm_result.get('response', '')
            
            return self._build_success_result(
                "Debug guidance provided",
                data={
                    'task': task,
                    'guidance': guidance,
                    'powershell_available': self._pwsh_available
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
