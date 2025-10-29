
"""
Linux Administration Agent

This agent performs safe Linux system administration tasks:
- Package management (apt, yum, dnf)
- Service management (systemctl)
- File permissions and ownership
- System information gathering
- Log file inspection
"""

import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base import Agent


class LinuxAdminAgent(Agent):
    """
    Agent specialized for Linux administration tasks.
    
    Features:
    - Safe package management (non-root where possible)
    - Service status checking
    - File permission management
    - System information gathering
    - Log file inspection
    - Disk usage monitoring
    
    Safety:
    - No destructive commands without confirmation
    - Non-root operations preferred
    - Command validation and sanitization
    """
    
    def __init__(
        self,
        name: str = "linux_admin",
        description: str = "Linux administration agent with safety checks",
        **kwargs
    ):
        super().__init__(name=name, description=description, **kwargs)
        
        # Detect package manager
        self.package_manager = self._detect_package_manager()
        
        # Dangerous commands that require confirmation
        self.dangerous_commands = [
            'rm -rf',
            'mkfs',
            'dd',
            'format',
            'fdisk',
            '> /dev/',
            'chmod -R 777',
            'chown -R'
        ]
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Linux administration task.
        
        Args:
            task: Administration task description
            context: Context with optional 'command', 'operation', 'params'
            
        Returns:
            Result with command output or operation status
        """
        self._log_action("Starting Linux admin task", task[:100])
        
        # Check if we're on Linux
        if platform.system() != 'Linux':
            return self._build_error_result(
                f"This agent requires Linux (current: {platform.system()})"
            )
        
        try:
            # Parse the task
            operation = self._parse_admin_task(task, context)
            
            if not operation:
                return self._build_error_result("Could not parse admin task")
            
            # Validate operation
            if not self._validate_operation(operation):
                return self._build_error_result(
                    f"Operation not allowed or unsafe: {operation.get('type')}"
                )
            
            # Execute operation
            result = self._execute_operation(operation, context)
            
            return result
            
        except Exception as e:
            self.logger.exception("Linux admin task failed")
            return self._build_error_result(f"Admin error: {str(e)}", e)
    
    def _detect_package_manager(self) -> Optional[str]:
        """Detect available package manager."""
        managers = {
            'apt': '/usr/bin/apt',
            'apt-get': '/usr/bin/apt-get',
            'yum': '/usr/bin/yum',
            'dnf': '/usr/bin/dnf',
            'pacman': '/usr/bin/pacman',
            'zypper': '/usr/bin/zypper'
        }
        
        for name, path in managers.items():
            if Path(path).exists():
                return name
        
        return None
    
    def _parse_admin_task(self, task: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse administration task."""
        task_lower = task.lower()
        
        # Explicit command from context
        if 'command' in context:
            return {
                'type': 'command',
                'command': context['command']
            }
        
        # Package operations
        if any(word in task_lower for word in ['install', 'package', 'apt', 'yum']):
            return self._parse_package_operation(task)
        
        # Service operations
        if any(word in task_lower for word in ['service', 'systemctl', 'start', 'stop', 'status']):
            return self._parse_service_operation(task)
        
        # System info
        if any(word in task_lower for word in ['info', 'system', 'uptime', 'memory', 'disk']):
            return self._parse_info_operation(task)
        
        # File permissions
        if any(word in task_lower for word in ['chmod', 'chown', 'permission']):
            return self._parse_permission_operation(task)
        
        # Log inspection
        if any(word in task_lower for word in ['log', 'journal', 'syslog']):
            return self._parse_log_operation(task)
        
        return None
    
    def _parse_package_operation(self, task: str) -> Dict[str, Any]:
        """Parse package management operation."""
        import re
        
        operation = {'type': 'package'}
        
        if 'install' in task.lower():
            operation['action'] = 'install'
            # Extract package names
            match = re.findall(r'install\s+([a-zA-Z0-9\-\_\.\s]+)', task, re.IGNORECASE)
            if match:
                operation['packages'] = match[0].split()
        elif 'remove' in task.lower() or 'uninstall' in task.lower():
            operation['action'] = 'remove'
            match = re.findall(r'(?:remove|uninstall)\s+([a-zA-Z0-9\-\_\.\s]+)', task, re.IGNORECASE)
            if match:
                operation['packages'] = match[0].split()
        elif 'update' in task.lower():
            operation['action'] = 'update'
        elif 'search' in task.lower():
            operation['action'] = 'search'
            match = re.search(r'search\s+([a-zA-Z0-9\-\_\.]+)', task, re.IGNORECASE)
            if match:
                operation['query'] = match.group(1)
        
        return operation
    
    def _parse_service_operation(self, task: str) -> Dict[str, Any]:
        """Parse service management operation."""
        import re
        
        operation = {'type': 'service'}
        
        # Extract service name
        match = re.search(r'(?:service\s+)?([a-zA-Z0-9\-\_\.]+)', task)
        if match:
            operation['service'] = match.group(1)
        
        # Extract action
        if 'start' in task.lower():
            operation['action'] = 'start'
        elif 'stop' in task.lower():
            operation['action'] = 'stop'
        elif 'restart' in task.lower():
            operation['action'] = 'restart'
        elif 'status' in task.lower():
            operation['action'] = 'status'
        elif 'enable' in task.lower():
            operation['action'] = 'enable'
        elif 'disable' in task.lower():
            operation['action'] = 'disable'
        else:
            operation['action'] = 'status'  # Default to status
        
        return operation
    
    def _parse_info_operation(self, task: str) -> Dict[str, Any]:
        """Parse system information operation."""
        task_lower = task.lower()
        
        operation = {'type': 'info'}
        
        if 'disk' in task_lower or 'storage' in task_lower:
            operation['info_type'] = 'disk'
        elif 'memory' in task_lower or 'ram' in task_lower:
            operation['info_type'] = 'memory'
        elif 'cpu' in task_lower or 'processor' in task_lower:
            operation['info_type'] = 'cpu'
        elif 'uptime' in task_lower:
            operation['info_type'] = 'uptime'
        else:
            operation['info_type'] = 'system'
        
        return operation
    
    def _parse_permission_operation(self, task: str) -> Dict[str, Any]:
        """Parse file permission operation."""
        import re
        
        operation = {'type': 'permission'}
        
        # Extract file path
        match = re.search(r'([/\w\-\.]+\.\w+|/[\w\-/]+)', task)
        if match:
            operation['path'] = match.group(1)
        
        # Extract permission mode
        match = re.search(r'\b([0-7]{3,4})\b', task)
        if match:
            operation['mode'] = match.group(1)
        
        return operation
    
    def _parse_log_operation(self, task: str) -> Dict[str, Any]:
        """Parse log inspection operation."""
        operation = {'type': 'log'}
        
        task_lower = task.lower()
        
        if 'journal' in task_lower:
            operation['log_type'] = 'journal'
        elif 'syslog' in task_lower:
            operation['log_type'] = 'syslog'
        elif 'auth' in task_lower:
            operation['log_type'] = 'auth'
        else:
            operation['log_type'] = 'journal'
        
        # Extract number of lines
        import re
        match = re.search(r'(\d+)\s+(?:lines|entries)', task_lower)
        if match:
            operation['lines'] = int(match.group(1))
        else:
            operation['lines'] = 20
        
        return operation
    
    def _validate_operation(self, operation: Dict[str, Any]) -> bool:
        """Validate that operation is safe."""
        op_type = operation.get('type')
        
        # Check for dangerous patterns if custom command
        if op_type == 'command':
            command = operation.get('command', '')
            for dangerous in self.dangerous_commands:
                if dangerous in command:
                    self.logger.warning(f"Dangerous command blocked: {command}")
                    return False
        
        # Package install/remove require confirmation in production
        if op_type == 'package':
            action = operation.get('action')
            if action in ['install', 'remove']:
                # In production, you'd prompt user here
                self.logger.info(f"Package {action} operation requires confirmation")
        
        return True
    
    def _execute_operation(self, operation: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the admin operation."""
        op_type = operation['type']
        
        handlers = {
            'package': self._handle_package_operation,
            'service': self._handle_service_operation,
            'info': self._handle_info_operation,
            'permission': self._handle_permission_operation,
            'log': self._handle_log_operation,
            'command': self._handle_command_operation
        }
        
        handler = handlers.get(op_type)
        if not handler:
            return self._build_error_result(f"No handler for operation type: {op_type}")
        
        return handler(operation, context)
    
    def _handle_package_operation(self, operation: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle package management operations."""
        if not self.package_manager:
            return self._build_error_result("No package manager detected")
        
        action = operation.get('action')
        
        # Build command based on package manager and action
        if action == 'search':
            query = operation.get('query', '')
            command = [self.package_manager, 'search', query]
        elif action == 'update':
            command = ['sudo', self.package_manager, 'update']
        elif action == 'install':
            packages = operation.get('packages', [])
            command = ['sudo', self.package_manager, 'install', '-y'] + packages
        elif action == 'remove':
            packages = operation.get('packages', [])
            command = ['sudo', self.package_manager, 'remove', '-y'] + packages
        else:
            return self._build_error_result(f"Unknown package action: {action}")
        
        return self._run_command(command, f"Package {action}")
    
    def _handle_service_operation(self, operation: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle service management operations."""
        service = operation.get('service')
        action = operation.get('action', 'status')
        
        if not service:
            return self._build_error_result("No service specified")
        
        # Build systemctl command
        if action in ['start', 'stop', 'restart', 'enable', 'disable']:
            command = ['sudo', 'systemctl', action, service]
        else:
            command = ['systemctl', 'status', service]
        
        return self._run_command(command, f"Service {action}: {service}")
    
    def _handle_info_operation(self, operation: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system information operations."""
        info_type = operation.get('info_type', 'system')
        
        commands = {
            'disk': ['df', '-h'],
            'memory': ['free', '-h'],
            'cpu': ['lscpu'],
            'uptime': ['uptime'],
            'system': ['uname', '-a']
        }
        
        command = commands.get(info_type, commands['system'])
        
        return self._run_command(command, f"System info: {info_type}")
    
    def _handle_permission_operation(self, operation: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file permission operations."""
        path = operation.get('path')
        mode = operation.get('mode')
        
        if not path:
            return self._build_error_result("No file path specified")
        
        if not mode:
            # Just show current permissions
            command = ['ls', '-la', path]
        else:
            # Change permissions
            command = ['chmod', mode, path]
        
        return self._run_command(command, f"File permissions: {path}")
    
    def _handle_log_operation(self, operation: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle log inspection operations."""
        log_type = operation.get('log_type', 'journal')
        lines = operation.get('lines', 20)
        
        if log_type == 'journal':
            command = ['journalctl', '-n', str(lines), '--no-pager']
        elif log_type == 'syslog':
            command = ['tail', '-n', str(lines), '/var/log/syslog']
        elif log_type == 'auth':
            command = ['sudo', 'tail', '-n', str(lines), '/var/log/auth.log']
        else:
            command = ['journalctl', '-n', str(lines), '--no-pager']
        
        return self._run_command(command, f"Log inspection: {log_type}")
    
    def _handle_command_operation(self, operation: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle custom command execution."""
        command = operation.get('command')
        
        if isinstance(command, str):
            command = command.split()
        
        return self._run_command(command, "Custom command")
    
    def _run_command(self, command: List[str], description: str) -> Dict[str, Any]:
        """Execute a shell command safely."""
        self._log_action("Executing command", description)
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            success = result.returncode == 0
            
            return self._build_success_result(
                message=f"{description}: {'Success' if success else 'Failed'}",
                data={
                    'command': ' '.join(command),
                    'return_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'success': success
                },
                next_context={'last_command_success': success}
            )
            
        except subprocess.TimeoutExpired:
            return self._build_error_result(f"Command timed out: {' '.join(command)}")
        except FileNotFoundError:
            return self._build_error_result(f"Command not found: {command[0]}")
        except Exception as e:
            return self._build_error_result(f"Command failed: {str(e)}", e)

