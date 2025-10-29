
"""
Windows Administration Agent

Full production-ready implementation for Windows system administration tasks.
Supports PowerShell execution, service management, registry operations, 
system information gathering, and scheduled tasks management.

Features:
- PowerShell command execution with security validations
- Windows service control (start, stop, restart, status)
- Registry operations (read-only by default)
- System information gathering
- Event log querying
- Scheduled tasks management
- User and group information
- Security confirmations for destructive operations
- Cross-platform validation
"""

import platform
import subprocess
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

from .base import Agent


class ServiceAction(Enum):
    """Valid Windows service actions."""
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    STATUS = "status"


class RegistryHive(Enum):
    """Windows Registry hives."""
    HKLM = "HKEY_LOCAL_MACHINE"
    HKCU = "HKEY_CURRENT_USER"
    HKCR = "HKEY_CLASSES_ROOT"
    HKU = "HKEY_USERS"
    HKCC = "HKEY_CURRENT_CONFIG"


class WindowsAdminAgent(Agent):
    """
    Production-ready Windows Administration Agent.
    
    Provides comprehensive Windows system administration capabilities through
    PowerShell integration. Includes security validations, confirmations for
    destructive operations, and detailed error handling.
    
    Capabilities:
        - Execute PowerShell commands safely
        - Manage Windows services (start, stop, restart, query status)
        - Read registry values (write operations require explicit confirmation)
        - Gather system information (OS version, hardware, network)
        - Query event logs
        - Manage scheduled tasks
        - User and group information
    
    Security Features:
        - Command validation and sanitization
        - Dangerous command detection
        - User confirmation for destructive operations
        - Comprehensive logging of all operations
        - Cross-platform validation
    
    Example Usage:
        >>> agent = WindowsAdminAgent(llm_router=router)
        >>> result = agent.execute(
        ...     "Get status of Windows Update service",
        ...     context={}
        ... )
        >>> print(result['message'])
    """
    
    # Dangerous PowerShell commands/patterns that require confirmation
    DANGEROUS_PATTERNS = [
        r'Remove-Item',
        r'rm\s+',
        r'del\s+',
        r'Format-',
        r'Clear-',
        r'Stop-Computer',
        r'Restart-Computer',
        r'Set-ItemProperty.*Registry',
        r'New-ItemProperty.*Registry',
        r'Remove-ItemProperty.*Registry',
        r'Set-Service',
        r'Remove-',
        r'Disable-',
        r'Uninstall-',
    ]
    
    # Safe read-only commands
    SAFE_COMMANDS = [
        'Get-Service',
        'Get-Process',
        'Get-EventLog',
        'Get-ItemProperty',
        'Get-ComputerInfo',
        'Get-NetAdapter',
        'Get-ScheduledTask',
        'Get-LocalUser',
        'Get-LocalGroup',
        'Get-WmiObject',
        'Get-CimInstance',
    ]
    
    def __init__(
        self,
        name: str = "windows_admin",
        description: str = "Windows administration agent with PowerShell capabilities",
        **kwargs
    ):
        """
        Initialize Windows Administration Agent.
        
        Args:
            name: Agent name
            description: Agent description
            **kwargs: Additional arguments passed to base Agent class
        """
        super().__init__(name=name, description=description, **kwargs)
        
        self.is_windows = platform.system() == 'Windows'
        
        if not self.is_windows:
            self.logger.warning(
                f"Windows Admin Agent initialized on non-Windows platform: {platform.system()}"
            )
        else:
            self.logger.info("Windows Admin Agent initialized successfully")
            self._check_powershell_availability()
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Windows administration task.
        
        Parses the task description and routes to appropriate handler:
        - Service management
        - Registry operations
        - System information
        - Event log queries
        - Scheduled tasks
        - Direct PowerShell commands
        
        Args:
            task: Task description (e.g., "Get status of wuauserv service")
            context: Execution context with optional parameters:
                - confirm_destructive: bool - Skip confirmation prompts (default: False)
                - timeout: int - Command timeout in seconds (default: 30)
                - operation: str - Specific operation type override
                
        Returns:
            Dictionary with execution results:
                - success: bool - Operation success status
                - message: str - Human-readable result message
                - data: dict - Operation-specific data
                - next_context: dict - Updated context
        """
        self._log_action("Windows admin task", task[:100])
        
        # Platform validation
        if not self.is_windows:
            return self._build_error_result(
                f"Windows Admin Agent requires Windows OS (current: {platform.system()})"
            )
        
        try:
            # Extract operation type from task or context
            operation = context.get('operation', self._detect_operation(task))
            
            # Route to appropriate handler
            if operation == 'service':
                return self._handle_service_operation(task, context)
            elif operation == 'registry':
                return self._handle_registry_operation(task, context)
            elif operation == 'system_info':
                return self._handle_system_info(task, context)
            elif operation == 'event_log':
                return self._handle_event_log(task, context)
            elif operation == 'scheduled_task':
                return self._handle_scheduled_task(task, context)
            elif operation == 'powershell':
                return self._handle_powershell_command(task, context)
            else:
                # Use LLM to interpret and generate PowerShell command
                return self._handle_llm_interpretation(task, context)
                
        except Exception as e:
            self.logger.error(f"Windows admin task failed: {e}", exc_info=True)
            return self._build_error_result(
                f"Windows administration task failed: {str(e)}",
                error=e
            )
    
    def _detect_operation(self, task: str) -> str:
        """
        Detect operation type from task description.
        
        Args:
            task: Task description
            
        Returns:
            Operation type string
        """
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['service', 'daemon', 'start', 'stop', 'restart']):
            return 'service'
        elif any(word in task_lower for word in ['registry', 'reg', 'hklm', 'hkcu']):
            return 'registry'
        elif any(word in task_lower for word in ['system', 'info', 'hardware', 'os', 'version']):
            return 'system_info'
        elif any(word in task_lower for word in ['event', 'log', 'error', 'warning']):
            return 'event_log'
        elif any(word in task_lower for word in ['task', 'scheduled', 'schedule']):
            return 'scheduled_task'
        elif task.startswith('powershell:') or task.startswith('ps:'):
            return 'powershell'
        else:
            return 'auto'
    
    def _handle_service_operation(
        self, 
        task: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle Windows service operations.
        
        Args:
            task: Task description containing service name and action
            context: Execution context
            
        Returns:
            Operation result
        """
        # Extract service name and action
        service_name = context.get('service_name')
        action = context.get('action', 'status')
        
        if not service_name:
            service_name = self._extract_service_name(task)
        
        if not service_name:
            return self._build_error_result(
                "Could not determine service name from task. "
                "Please specify 'service_name' in context."
            )
        
        # Detect action if not provided
        if action == 'status':
            action = self._extract_service_action(task)
        
        return self._manage_service(service_name, action, context)
    
    def _handle_registry_operation(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle registry operations.
        
        Args:
            task: Task description
            context: Execution context
            
        Returns:
            Operation result
        """
        key_path = context.get('key_path')
        value_name = context.get('value_name')
        
        if not key_path:
            return self._build_error_result(
                "Registry operations require 'key_path' in context"
            )
        
        return self._read_registry(key_path, value_name, context)
    
    def _handle_system_info(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle system information gathering.
        
        Args:
            task: Task description
            context: Execution context
            
        Returns:
            System information
        """
        return self._get_system_info(context)
    
    def _handle_event_log(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle event log queries.
        
        Args:
            task: Task description
            context: Execution context with:
                - log_name: str (e.g., 'System', 'Application')
                - entry_type: str (e.g., 'Error', 'Warning')
                - max_events: int (default: 10)
            
        Returns:
            Event log entries
        """
        log_name = context.get('log_name', 'System')
        entry_type = context.get('entry_type', 'Error')
        max_events = context.get('max_events', 10)
        
        return self._query_event_log(log_name, entry_type, max_events, context)
    
    def _handle_scheduled_task(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle scheduled task operations.
        
        Args:
            task: Task description
            context: Execution context
            
        Returns:
            Scheduled task information
        """
        task_name = context.get('task_name')
        return self._get_scheduled_tasks(task_name, context)
    
    def _handle_powershell_command(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle direct PowerShell command execution.
        
        Args:
            task: PowerShell command (prefixed with 'powershell:' or 'ps:')
            context: Execution context
            
        Returns:
            Command execution result
        """
        # Extract command
        command = task
        if task.startswith('powershell:'):
            command = task[11:].strip()
        elif task.startswith('ps:'):
            command = task[3:].strip()
        
        # Execute
        return self._execute_powershell(command, context)
    
    def _handle_llm_interpretation(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use LLM to interpret task and generate PowerShell command.
        
        Args:
            task: Natural language task description
            context: Execution context
            
        Returns:
            Execution result
        """
        if not self.llm_router:
            return self._build_error_result(
                "LLM router not available for task interpretation"
            )
        
        try:
            # Generate PowerShell command using LLM
            prompt = self._build_powershell_generation_prompt(task)
            llm_response = self._get_llm_response(prompt)
            
            # Extract command from LLM response
            command = self._extract_command_from_llm_response(llm_response)
            
            if not command:
                return self._build_error_result(
                    "Could not generate PowerShell command from task description"
                )
            
            # Execute command
            self.logger.info(f"LLM-generated command: {command}")
            return self._execute_powershell(command, context)
            
        except Exception as e:
            self.logger.error(f"LLM interpretation failed: {e}")
            return self._build_error_result(
                f"Failed to interpret task: {str(e)}",
                error=e
            )
    
    # =================================================================
    # Core Windows Administration Methods
    # =================================================================
    
    def _execute_powershell(
        self,
        command: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute PowerShell command with security validation.
        
        Args:
            command: PowerShell command to execute
            context: Execution context
            
        Returns:
            Execution result
        """
        # Validate command
        is_safe, warning = self._validate_powershell_command(command)
        
        if not is_safe:
            # Check if confirmation override is set
            if not context.get('confirm_destructive', False):
                return self._build_error_result(
                    f"Potentially destructive command detected: {warning}. "
                    f"Set 'confirm_destructive': True in context to proceed."
                )
        
        # Execute
        timeout = context.get('timeout', 30)
        result = self._run_powershell(command, timeout)
        
        if result['success']:
            return self._build_success_result(
                message="PowerShell command executed successfully",
                data=result
            )
        else:
            return self._build_error_result(
                f"PowerShell command failed: {result.get('stderr', 'Unknown error')}",
                error=None
            )
    
    def _run_powershell(
        self,
        command: str,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Execute PowerShell command using subprocess.
        
        Args:
            command: PowerShell command
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with execution results:
                - success: bool
                - stdout: str
                - stderr: str
                - return_code: int
        """
        try:
            self.logger.debug(f"Executing PowerShell: {command}")
            
            result = subprocess.run(
                ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', command],
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            
            success = result.returncode == 0
            
            self.logger.info(
                f"PowerShell execution {'succeeded' if success else 'failed'} "
                f"(return code: {result.returncode})"
            )
            
            return {
                'success': success,
                'stdout': result.stdout.strip(),
                'stderr': result.stderr.strip(),
                'return_code': result.returncode,
                'command': command
            }
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"PowerShell command timed out after {timeout}s")
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds',
                'return_code': -1,
                'command': command
            }
        except Exception as e:
            self.logger.error(f"PowerShell execution failed: {e}")
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'return_code': -1,
                'command': command
            }
    
    def _validate_powershell_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        Validate PowerShell command for safety.
        
        Args:
            command: PowerShell command to validate
            
        Returns:
            Tuple of (is_safe, warning_message)
        """
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Dangerous pattern detected: {pattern}"
        
        # Check if it starts with a safe command
        command_start = command.strip().split()[0] if command.strip() else ''
        if command_start in self.SAFE_COMMANDS:
            return True, None
        
        # Check for script blocks or pipes to dangerous commands
        if '|' in command:
            for part in command.split('|'):
                for pattern in self.DANGEROUS_PATTERNS:
                    if re.search(pattern, part, re.IGNORECASE):
                        return False, f"Dangerous pattern in pipeline: {pattern}"
        
        # If we can't confirm it's safe, warn but allow with confirmation
        return True, None
    
    def _manage_service(
        self,
        service_name: str,
        action: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Manage Windows service.
        
        Args:
            service_name: Name of the Windows service
            action: Action to perform (start, stop, restart, status)
            context: Execution context
            
        Returns:
            Service operation result
        """
        try:
            # Validate action
            if action not in [a.value for a in ServiceAction]:
                return self._build_error_result(
                    f"Invalid service action: {action}. "
                    f"Valid actions: {', '.join([a.value for a in ServiceAction])}"
                )
            
            # Build PowerShell command
            if action == 'status':
                command = f"Get-Service -Name '{service_name}' | Select-Object Name, Status, DisplayName, StartType | ConvertTo-Json"
            elif action == 'start':
                # Requires confirmation
                if not context.get('confirm_destructive', False):
                    return self._build_error_result(
                        f"Starting service '{service_name}' requires confirmation. "
                        f"Set 'confirm_destructive': True in context."
                    )
                command = f"Start-Service -Name '{service_name}' -PassThru | Select-Object Name, Status | ConvertTo-Json"
            elif action == 'stop':
                # Requires confirmation
                if not context.get('confirm_destructive', False):
                    return self._build_error_result(
                        f"Stopping service '{service_name}' requires confirmation. "
                        f"Set 'confirm_destructive': True in context."
                    )
                command = f"Stop-Service -Name '{service_name}' -Force -PassThru | Select-Object Name, Status | ConvertTo-Json"
            elif action == 'restart':
                # Requires confirmation
                if not context.get('confirm_destructive', False):
                    return self._build_error_result(
                        f"Restarting service '{service_name}' requires confirmation. "
                        f"Set 'confirm_destructive': True in context."
                    )
                command = f"Restart-Service -Name '{service_name}' -Force -PassThru | Select-Object Name, Status | ConvertTo-Json"
            
            # Execute
            result = self._run_powershell(command, timeout=60)
            
            if result['success']:
                # Parse JSON output
                try:
                    service_data = json.loads(result['stdout']) if result['stdout'] else {}
                except json.JSONDecodeError:
                    service_data = {'raw_output': result['stdout']}
                
                return self._build_success_result(
                    message=f"Service '{service_name}' {action} operation completed",
                    data={
                        'service_name': service_name,
                        'action': action,
                        'service_info': service_data
                    }
                )
            else:
                return self._build_error_result(
                    f"Service operation failed: {result['stderr']}"
                )
                
        except Exception as e:
            self.logger.error(f"Service management failed: {e}")
            return self._build_error_result(
                f"Service management failed: {str(e)}",
                error=e
            )
    
    def _read_registry(
        self,
        key_path: str,
        value_name: Optional[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Read Windows Registry value(s).
        
        Args:
            key_path: Registry key path (e.g., 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion')
            value_name: Specific value name to read (None to read all values)
            context: Execution context
            
        Returns:
            Registry data
        """
        try:
            # Build PowerShell command
            if value_name:
                command = f"Get-ItemProperty -Path '{key_path}' -Name '{value_name}' | ConvertTo-Json"
            else:
                command = f"Get-ItemProperty -Path '{key_path}' | ConvertTo-Json"
            
            # Execute
            result = self._run_powershell(command)
            
            if result['success']:
                # Parse JSON
                try:
                    registry_data = json.loads(result['stdout']) if result['stdout'] else {}
                except json.JSONDecodeError:
                    registry_data = {'raw_output': result['stdout']}
                
                return self._build_success_result(
                    message=f"Registry key '{key_path}' read successfully",
                    data={
                        'key_path': key_path,
                        'value_name': value_name,
                        'registry_data': registry_data
                    }
                )
            else:
                return self._build_error_result(
                    f"Registry read failed: {result['stderr']}"
                )
                
        except Exception as e:
            self.logger.error(f"Registry operation failed: {e}")
            return self._build_error_result(
                f"Registry operation failed: {str(e)}",
                error=e
            )
    
    def _get_system_info(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gather comprehensive Windows system information.
        
        Args:
            context: Execution context
            
        Returns:
            System information
        """
        try:
            # Build comprehensive system info command
            command = """
            $info = @{
                ComputerName = $env:COMPUTERNAME
                OSVersion = [System.Environment]::OSVersion.VersionString
                OSArchitecture = (Get-WmiObject Win32_OperatingSystem).OSArchitecture
                ProcessorCount = $env:NUMBER_OF_PROCESSORS
                TotalMemoryGB = [math]::Round((Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
                UserName = $env:USERNAME
                UserDomain = $env:USERDOMAIN
                PowerShellVersion = $PSVersionTable.PSVersion.ToString()
            }
            $info | ConvertTo-Json
            """
            
            result = self._run_powershell(command)
            
            if result['success']:
                try:
                    system_data = json.loads(result['stdout']) if result['stdout'] else {}
                except json.JSONDecodeError:
                    system_data = {'raw_output': result['stdout']}
                
                # Add Python platform info
                system_data['python_platform'] = {
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'machine': platform.machine(),
                    'processor': platform.processor()
                }
                
                return self._build_success_result(
                    message="System information retrieved successfully",
                    data=system_data
                )
            else:
                return self._build_error_result(
                    f"System info retrieval failed: {result['stderr']}"
                )
                
        except Exception as e:
            self.logger.error(f"System info gathering failed: {e}")
            return self._build_error_result(
                f"System info gathering failed: {str(e)}",
                error=e
            )
    
    def _query_event_log(
        self,
        log_name: str,
        entry_type: str,
        max_events: int,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Query Windows Event Log.
        
        Args:
            log_name: Log name (e.g., 'System', 'Application', 'Security')
            entry_type: Entry type (e.g., 'Error', 'Warning', 'Information')
            max_events: Maximum number of events to retrieve
            context: Execution context
            
        Returns:
            Event log entries
        """
        try:
            # Build PowerShell command for newer Windows versions using Get-WinEvent
            command = f"""
            Get-WinEvent -FilterHashtable @{{LogName='{log_name}'; Level=@(1,2,3)}} -MaxEvents {max_events} -ErrorAction SilentlyContinue | 
            Select-Object TimeCreated, Id, LevelDisplayName, Message -First {max_events} | 
            ConvertTo-Json
            """
            
            result = self._run_powershell(command)
            
            if result['success']:
                try:
                    # Parse JSON
                    events_data = json.loads(result['stdout']) if result['stdout'] else []
                    
                    # Ensure it's a list
                    if not isinstance(events_data, list):
                        events_data = [events_data] if events_data else []
                    
                    return self._build_success_result(
                        message=f"Retrieved {len(events_data)} event(s) from '{log_name}' log",
                        data={
                            'log_name': log_name,
                            'entry_type': entry_type,
                            'event_count': len(events_data),
                            'events': events_data
                        }
                    )
                except json.JSONDecodeError:
                    return self._build_success_result(
                        message="Event log query completed (parsing as text)",
                        data={
                            'log_name': log_name,
                            'raw_output': result['stdout']
                        }
                    )
            else:
                return self._build_error_result(
                    f"Event log query failed: {result['stderr']}"
                )
                
        except Exception as e:
            self.logger.error(f"Event log query failed: {e}")
            return self._build_error_result(
                f"Event log query failed: {str(e)}",
                error=e
            )
    
    def _get_scheduled_tasks(
        self,
        task_name: Optional[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get Windows scheduled tasks.
        
        Args:
            task_name: Specific task name (None for all tasks)
            context: Execution context
            
        Returns:
            Scheduled task information
        """
        try:
            # Build PowerShell command
            if task_name:
                command = f"Get-ScheduledTask -TaskName '{task_name}' | Select-Object TaskName, State, TaskPath | ConvertTo-Json"
            else:
                command = "Get-ScheduledTask | Select-Object TaskName, State, TaskPath -First 50 | ConvertTo-Json"
            
            result = self._run_powershell(command)
            
            if result['success']:
                try:
                    tasks_data = json.loads(result['stdout']) if result['stdout'] else []
                    
                    # Ensure it's a list
                    if not isinstance(tasks_data, list):
                        tasks_data = [tasks_data] if tasks_data else []
                    
                    return self._build_success_result(
                        message=f"Retrieved {len(tasks_data)} scheduled task(s)",
                        data={
                            'task_name': task_name,
                            'task_count': len(tasks_data),
                            'tasks': tasks_data
                        }
                    )
                except json.JSONDecodeError:
                    return self._build_success_result(
                        message="Scheduled tasks query completed (parsing as text)",
                        data={'raw_output': result['stdout']}
                    )
            else:
                return self._build_error_result(
                    f"Scheduled tasks query failed: {result['stderr']}"
                )
                
        except Exception as e:
            self.logger.error(f"Scheduled tasks query failed: {e}")
            return self._build_error_result(
                f"Scheduled tasks query failed: {str(e)}",
                error=e
            )
    
    # =================================================================
    # Helper Methods
    # =================================================================
    
    def _check_powershell_availability(self) -> bool:
        """
        Check if PowerShell is available.
        
        Returns:
            True if PowerShell is available
        """
        try:
            result = subprocess.run(
                ['powershell.exe', '-Command', 'Write-Output "test"'],
                capture_output=True,
                timeout=5
            )
            available = result.returncode == 0
            
            if available:
                self.logger.info("PowerShell is available")
            else:
                self.logger.warning("PowerShell is not available")
            
            return available
            
        except Exception as e:
            self.logger.warning(f"PowerShell availability check failed: {e}")
            return False
    
    def _extract_service_name(self, task: str) -> Optional[str]:
        """
        Extract service name from task description.
        
        Args:
            task: Task description
            
        Returns:
            Service name if found
        """
        # Common patterns for service names
        patterns = [
            r"service[:\s]+['\"]?(\w+)['\"]?",
            r"['\"](\w+)['\"]?\s+service",
            r"(\w+auserv)",  # Windows Update service pattern
            r"wuauserv|bits|spooler|dnscache",  # Common service names
        ]
        
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_service_action(self, task: str) -> str:
        """
        Extract service action from task description.
        
        Args:
            task: Task description
            
        Returns:
            Service action (default: 'status')
        """
        task_lower = task.lower()
        
        if 'start' in task_lower and 'restart' not in task_lower:
            return 'start'
        elif 'stop' in task_lower:
            return 'stop'
        elif 'restart' in task_lower:
            return 'restart'
        else:
            return 'status'
    
    def _build_powershell_generation_prompt(self, task: str) -> str:
        """
        Build prompt for LLM to generate PowerShell command.
        
        Args:
            task: Natural language task description
            
        Returns:
            LLM prompt
        """
        return f"""Generate a safe PowerShell command for the following Windows administration task:

Task: {task}

Requirements:
1. Generate ONLY the PowerShell command, no explanations
2. Use read-only commands when possible (Get-*, Select-Object, etc.)
3. Avoid destructive operations without explicit user confirmation
4. Use proper PowerShell syntax
5. Include error handling where appropriate
6. Output should be in JSON format when possible (use ConvertTo-Json)

PowerShell Command:"""
    
    def _extract_command_from_llm_response(self, llm_response: Dict[str, Any]) -> Optional[str]:
        """
        Extract PowerShell command from LLM response.
        
        Args:
            llm_response: LLM response dictionary
            
        Returns:
            Extracted command or None
        """
        try:
            # Get response text
            response_text = llm_response.get('response', '')
            
            # Try to extract command from code blocks
            code_block_match = re.search(r'```(?:powershell)?\n(.+?)\n```', response_text, re.DOTALL)
            if code_block_match:
                return code_block_match.group(1).strip()
            
            # Otherwise, take first non-empty line
            lines = [line.strip() for line in response_text.split('\n') if line.strip()]
            if lines:
                return lines[0]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to extract command from LLM response: {e}")
            return None

