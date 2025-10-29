

"""
Batch Script Build Agent

Production-ready build system integration for Windows Batch scripts.
"""

import os
import subprocess
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from ...base import BuildAgentBase


class BatchBuildAgent(BuildAgentBase):
    """
    Production-ready Batch Script Build Agent.
    
    Features:
        - Batch script validation
        - Script execution
        - Environment variable management
        - Command validation
        - Error handling
        - Build script generation
        - Dependency checking
    """
    
    def __init__(
        self,
        name: str = "batch_build",
        description: str = "Windows Batch script build agent",
        **kwargs
    ):
        super().__init__(name=name, description=description, **kwargs)
        
        self._timeout = self.config.get('build', {}).get('default_build_timeout', 300)
        
        self.logger.info("Batch Build Agent initialized")
        # Load language-specific documentation
        self._load_language_docs()

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Batch build task."""
        self._log_action("Batch build task", task[:100])
        
        try:
            operation = context.get('operation', self._detect_operation(task))
            project_dir = context.get('project_dir', os.getcwd())
            
            if not os.path.isdir(project_dir):
                return self._build_error_result(f"Invalid project directory: {project_dir}")
            
            if operation == 'validate_script':
                return self._validate_script(project_dir, context)
            elif operation == 'run_script':
                return self._run_script(project_dir, context)
            elif operation == 'generate_build_script':
                return self._generate_build_script(project_dir, context)
            elif operation == 'detect_scripts':
                return self._detect_scripts(project_dir)
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
        elif any(word in task_lower for word in ['generate', 'create script']):
            return 'generate_build_script'
        elif any(word in task_lower for word in ['detect', 'find', 'list']):
            return 'detect_scripts'
        
        return 'llm_assisted'
    
    def _detect_scripts(self, project_dir: str) -> Dict[str, Any]:
        """Detect batch scripts in project."""
        project_path = Path(project_dir)
        
        batch_files = list(project_path.rglob("*.bat"))
        cmd_files = list(project_path.rglob("*.cmd"))
        
        all_scripts = [str(f) for f in batch_files + cmd_files]
        
        if not all_scripts:
            return self._build_error_result("No batch scripts found")
        
        return self._build_success_result(
            f"Found {len(all_scripts)} batch script(s)",
            data={'scripts': all_scripts}
        )
    
    def _validate_script(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a batch script."""
        script_path = context.get('script_path')
        
        if not script_path:
            return self._build_error_result("script_path required")
        
        full_path = Path(project_dir) / script_path if not Path(script_path).is_absolute() else Path(script_path)
        
        if not full_path.exists():
            return self._build_error_result(f"Script not found: {full_path}")
        
        issues = []
        warnings = []
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Basic validation
                for i, line in enumerate(lines, 1):
                    line_stripped = line.strip()
                    
                    # Check for common issues
                    if line_stripped.startswith('goto :') and ':' not in line_stripped[5:]:
                        issues.append(f"Line {i}: Invalid goto label")
                    
                    # Check for undefined variables (very basic)
                    if '%' in line and line.count('%') % 2 != 0:
                        warnings.append(f"Line {i}: Unmatched % symbol")
                    
                    # Check for @echo off
                    if i == 1 and '@echo off' not in line_stripped.lower():
                        warnings.append("Line 1: Missing @echo off")
            
            if issues:
                return self._build_error_result(
                    f"Script validation failed with {len(issues)} issue(s)",
                    data={'issues': issues, 'warnings': warnings}
                )
            
            return self._build_success_result(
                "Script validation passed",
                data={'warnings': warnings, 'script_path': str(full_path)}
            )
            
        except Exception as e:
            return self._build_error_result(f"Script validation failed: {str(e)}", error=e)
    
    def _run_script(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run a batch script."""
        script_path = context.get('script_path')
        args = context.get('args', [])
        env = context.get('env', {})
        
        if not script_path:
            return self._build_error_result("script_path required")
        
        full_path = Path(project_dir) / script_path if not Path(script_path).is_absolute() else Path(script_path)
        
        if not full_path.exists():
            return self._build_error_result(f"Script not found: {full_path}")
        
        # Check if running on Windows
        if os.name != 'nt':
            return self._build_error_result("Batch scripts can only run on Windows")
        
        try:
            # Prepare environment
            run_env = os.environ.copy()
            run_env.update(env)
            
            cmd = [str(full_path)] + args
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout,
                env=run_env,
                shell=True
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
        except Exception as e:
            return self._build_error_result(f"Script execution failed: {str(e)}", error=e)
    
    def _generate_build_script(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a build batch script."""
        script_name = context.get('script_name', 'build.bat')
        commands = context.get('commands', [])
        
        if not commands:
            return self._build_error_result("commands list required")
        
        script_content = [
            "@echo off",
            "REM Auto-generated build script",
            f"REM Generated by {self.name}",
            "",
            "echo Starting build...",
            ""
        ]
        
        for cmd in commands:
            script_content.append(cmd)
            script_content.append("if %errorlevel% neq 0 exit /b %errorlevel%")
            script_content.append("")
        
        script_content.extend([
            "echo Build completed successfully!",
            "exit /b 0"
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
        prompt = f"""You are a Windows Batch scripting expert. Help with this build task:

Task: {task}

Project Directory: {project_dir}
Context: {json.dumps(context, indent=2)}

Provide:
1. Understanding of the build task
2. Recommended batch commands
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
                    'guidance': guidance
                }
            )
        except Exception as e:
            return self._build_error_result(f"LLM-assisted build failed: {str(e)}", error=e)
