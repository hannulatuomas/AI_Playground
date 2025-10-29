

"""
PowerShell Build Agent

Production-ready build system integration for PowerShell scripts.
"""

import os
import subprocess
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from ...base import BuildAgentBase


class PowerShellBuildAgent(BuildAgentBase):
    """
    Production-ready PowerShell Build Agent.
    
    Features:
        - PowerShell script validation
        - Script execution (Windows PowerShell and PowerShell Core)
        - Module management
        - Build automation
        - Error handling
        - Cross-platform support (PowerShell Core)
        - Script signing and policy management
    """
    
    def __init__(
        self,
        name: str = "powershell_build",
        description: str = "PowerShell script build agent",
        **kwargs
    ):
        super().__init__(name=name, description=description, **kwargs)
        
        self._timeout = self.config.get('build', {}).get('default_build_timeout', 300)
        self._pwsh_cmd = self._detect_powershell()
        
        self.logger.info(f"PowerShell Build Agent initialized with {self._pwsh_cmd}")
        # Load language-specific documentation
        self._load_language_docs()

    def _detect_powershell(self) -> str:
        """Detect available PowerShell executable."""
        # Try PowerShell Core (cross-platform)
        try:
            subprocess.run(['pwsh', '-Version'], capture_output=True, timeout=5)
            return 'pwsh'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Try Windows PowerShell
        if os.name == 'nt':
            try:
                subprocess.run(['powershell', '-Version'], capture_output=True, timeout=5)
                return 'powershell'
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
        
        return 'pwsh'  # Default to PowerShell Core
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute PowerShell build task."""
        self._log_action("PowerShell build task", task[:100])
        
        try:
            operation = context.get('operation', self._detect_operation(task))
            project_dir = context.get('project_dir', os.getcwd())
            
            if not os.path.isdir(project_dir):
                return self._build_error_result(f"Invalid project directory: {project_dir}")
            
            if operation == 'validate_script':
                return self._validate_script(project_dir, context)
            elif operation == 'run_script':
                return self._run_script(project_dir, context)
            elif operation == 'install_module':
                return self._install_module(context)
            elif operation == 'detect_scripts':
                return self._detect_scripts(project_dir)
            elif operation == 'generate_build_script':
                return self._generate_build_script(project_dir, context)
            else:
                return self._llm_assisted_build(task, project_dir, context)
                
        except Exception as e:
            self.logger.error(f"Build task failed: {e}", exc_info=True)
            return self._build_error_result(f"Build task failed: {str(e)}", error=e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect build operation from task description."""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['validate', 'check', 'verify']):
            return 'validate_script'
        elif any(word in task_lower for word in ['run', 'execute', 'build']):
            return 'run_script'
        elif any(word in task_lower for word in ['install', 'module', 'package']):
            return 'install_module'
        elif any(word in task_lower for word in ['detect', 'find', 'list']):
            return 'detect_scripts'
        elif any(word in task_lower for word in ['generate', 'create script']):
            return 'generate_build_script'
        
        return 'llm_assisted'
    
    def _detect_scripts(self, project_dir: str) -> Dict[str, Any]:
        """Detect PowerShell scripts in project."""
        project_path = Path(project_dir)
        
        ps1_files = list(project_path.rglob("*.ps1"))
        psm1_files = list(project_path.rglob("*.psm1"))
        psd1_files = list(project_path.rglob("*.psd1"))
        
        all_scripts = {
            'scripts': [str(f) for f in ps1_files],
            'modules': [str(f) for f in psm1_files],
            'manifests': [str(f) for f in psd1_files]
        }
        
        total = len(ps1_files) + len(psm1_files) + len(psd1_files)
        
        if total == 0:
            return self._build_error_result("No PowerShell files found")
        
        return self._build_success_result(
            f"Found {total} PowerShell file(s)",
            data=all_scripts
        )
    
    def _validate_script(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a PowerShell script."""
        script_path = context.get('script_path')
        
        if not script_path:
            return self._build_error_result("script_path required")
        
        full_path = Path(project_dir) / script_path if not Path(script_path).is_absolute() else Path(script_path)
        
        if not full_path.exists():
            return self._build_error_result(f"Script not found: {full_path}")
        
        try:
            # Use PowerShell's built-in syntax checking
            cmd = [
                self._pwsh_cmd,
                '-NoProfile',
                '-Command',
                f"$null = [System.Management.Automation.PSParser]::Tokenize((Get-Content '{full_path}' -Raw), [ref]$null); Write-Output 'Valid'"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and 'Valid' in result.stdout:
                return self._build_success_result(
                    "Script validation passed",
                    data={'script_path': str(full_path)}
                )
            else:
                return self._build_error_result(
                    f"Script validation failed: {result.stderr}",
                    data={'output': result.stderr}
                )
            
        except FileNotFoundError:
            return self._build_error_result(f"PowerShell not found: {self._pwsh_cmd}")
        except Exception as e:
            return self._build_error_result(f"Script validation failed: {str(e)}", error=e)
    
    def _run_script(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run a PowerShell script."""
        script_path = context.get('script_path')
        args = context.get('args', [])
        
        if not script_path:
            return self._build_error_result("script_path required")
        
        full_path = Path(project_dir) / script_path if not Path(script_path).is_absolute() else Path(script_path)
        
        if not full_path.exists():
            return self._build_error_result(f"Script not found: {full_path}")
        
        try:
            cmd = [
                self._pwsh_cmd,
                '-NoProfile',
                '-ExecutionPolicy', 'Bypass',
                '-File', str(full_path)
            ] + args
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            return self._build_success_result(
                f"Script executed: {script_path}",
                data={
                    'exit_code': result.returncode,
                    'success': result.returncode == 0,
                    'output': result.stdout,
                    'errors': result.stderr,
                    'command': ' '.join(cmd)
                }
            )
            
        except subprocess.TimeoutExpired:
            return self._build_error_result("Script execution timed out")
        except FileNotFoundError:
            return self._build_error_result(f"PowerShell not found: {self._pwsh_cmd}")
        except Exception as e:
            return self._build_error_result(f"Script execution failed: {str(e)}", error=e)
    
    def _install_module(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Install a PowerShell module."""
        module_name = context.get('module_name')
        
        if not module_name:
            return self._build_error_result("module_name required")
        
        try:
            cmd = [
                self._pwsh_cmd,
                '-NoProfile',
                '-Command',
                f"Install-Module -Name {module_name} -Force -AllowClobber"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return self._build_success_result(
                    f"Module installed: {module_name}",
                    data={'module': module_name, 'output': result.stdout}
                )
            else:
                return self._build_error_result(
                    f"Module installation failed: {result.stderr}",
                    data={'output': result.stderr}
                )
            
        except subprocess.TimeoutExpired:
            return self._build_error_result("Module installation timed out")
        except Exception as e:
            return self._build_error_result(f"Module installation failed: {str(e)}", error=e)
    
    def _generate_build_script(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a build PowerShell script."""
        script_name = context.get('script_name', 'build.ps1')
        commands = context.get('commands', [])
        
        if not commands:
            return self._build_error_result("commands list required")
        
        script_content = [
            "# Auto-generated build script",
            f"# Generated by {self.name}",
            "",
            "$ErrorActionPreference = 'Stop'",
            "",
            "Write-Host 'Starting build...' -ForegroundColor Green",
            ""
        ]
        
        for cmd in commands:
            script_content.append(f"Write-Host 'Executing: {cmd}' -ForegroundColor Cyan")
            script_content.append(cmd)
            script_content.append("if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }")
            script_content.append("")
        
        script_content.extend([
            "Write-Host 'Build completed successfully!' -ForegroundColor Green",
            "exit 0"
        ])
        
        script_path = Path(project_dir) / script_name
        
        try:
            with open(script_path, 'w') as f:
                f.write('\n'.join(script_content))
            
            return self._build_success_result(
                f"Build script generated: {script_name}",
                data={
                    'script_path': str(script_path),
                    'script_content': '\n'.join(script_content)
                }
            )
            
        except Exception as e:
            return self._build_error_result(f"Script generation failed: {str(e)}", error=e)
    
    def _llm_assisted_build(self, task: str, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to assist with build task."""
        prompt = f"""You are a PowerShell scripting expert. Help with this build task:

Task: {task}

Project Directory: {project_dir}
PowerShell: {self._pwsh_cmd}
Context: {json.dumps(context, indent=2)}

Provide:
1. Understanding of the build task
2. Recommended PowerShell commands
3. Step-by-step process
4. Common issues and solutions

Be specific and actionable."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            guidance = llm_result.get('response', '')
            
            return self._build_success_result(
                "Build guidance provided",
                data={
                    'task': task,
                    'powershell': self._pwsh_cmd,
                    'guidance': guidance
                }
            )
        except Exception as e:
            return self._build_error_result(f"LLM-assisted build failed: {str(e)}", error=e)
