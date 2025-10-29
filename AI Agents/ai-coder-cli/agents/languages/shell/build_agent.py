

"""
Shell Script Build Agent

Production-ready build system integration for shell scripts (bash/zsh/sh).
"""

import os
import subprocess
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from ...base import BuildAgentBase


class ShellBuildAgent(BuildAgentBase):
    """
    Production-ready Shell Script Build Agent.
    
    Features:
        - Shell script validation (bash/zsh/sh)
        - Script execution
        - ShellCheck integration for linting
        - Environment management
        - Build automation
        - Cross-platform shell support
        - Make integration
    """
    
    def __init__(
        self,
        name: str = "shell_build",
        description: str = "Shell script build agent (bash/zsh/sh)",
        **kwargs
    ):
        super().__init__(name=name, description=description, **kwargs)
        
        self._timeout = self.config.get('build', {}).get('default_build_timeout', 300)
        self._shell_cmd = self._detect_shell()
        self._has_shellcheck = self._check_shellcheck()
        
        self.logger.info(f"Shell Build Agent initialized with {self._shell_cmd}")
        # Load language-specific documentation
        self._load_language_docs()

    def _detect_shell(self) -> str:
        """
        Detect best available shell.
        
        Priority: bash > zsh > ksh > dash > sh
        """
        shells = ['bash', 'zsh', 'ksh', 'dash', 'sh']
        
        for shell in shells:
            try:
                result = subprocess.run(
                    [shell, '--version'],
                    capture_output=True,
                    timeout=5,
                    text=True
                )
                if result.returncode == 0:
                    self.logger.info(f"Detected shell: {shell}")
                    return shell
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        self.logger.warning("No common shell found, defaulting to 'sh'")
        return 'sh'  # Default fallback
    
    def _check_shellcheck(self) -> bool:
        """Check if shellcheck is available."""
        try:
            result = subprocess.run(
                ['shellcheck', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute shell build task."""
        self._log_action("Shell build task", task[:100])
        
        try:
            operation = context.get('operation', self._detect_operation(task))
            project_dir = context.get('project_dir', os.getcwd())
            
            if not os.path.isdir(project_dir):
                return self._build_error_result(f"Invalid project directory: {project_dir}")
            
            if operation == 'validate_script':
                return self._validate_script(project_dir, context)
            elif operation == 'run_script':
                return self._run_script(project_dir, context)
            elif operation == 'detect_scripts':
                return self._detect_scripts(project_dir)
            elif operation == 'run_make':
                return self._run_make(project_dir, context)
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
        
        if any(word in task_lower for word in ['validate', 'check', 'lint', 'verify']):
            return 'validate_script'
        elif any(word in task_lower for word in ['run', 'execute', 'build']):
            if 'make' in task_lower or 'makefile' in task_lower:
                return 'run_make'
            return 'run_script'
        elif any(word in task_lower for word in ['detect', 'find', 'list']):
            return 'detect_scripts'
        elif any(word in task_lower for word in ['generate', 'create script']):
            return 'generate_build_script'
        elif 'make' in task_lower:
            return 'run_make'
        
        return 'llm_assisted'
    
    def _detect_scripts(self, project_dir: str) -> Dict[str, Any]:
        """Detect shell scripts in project (bash/zsh/sh/ksh/dash)."""
        project_path = Path(project_dir)
        
        # Find by extension
        sh_files = list(project_path.rglob("*.sh"))
        bash_files = list(project_path.rglob("*.bash"))
        zsh_files = list(project_path.rglob("*.zsh"))
        ksh_files = list(project_path.rglob("*.ksh"))
        dash_files = list(project_path.rglob("*.dash"))
        
        # Also find scripts without extension but with shebang
        shebang_scripts = {
            'bash': [],
            'zsh': [],
            'sh': [],
            'ksh': [],
            'dash': [],
            'unknown': []
        }
        
        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix == '' and not file.name.startswith('.'):
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        first_line = f.readline()
                        if first_line.startswith('#!'):
                            shell_identified = False
                            for shell in ['bash', 'zsh', 'sh', 'ksh', 'dash']:
                                if shell in first_line:
                                    shebang_scripts[shell].append(str(file))
                                    shell_identified = True
                                    break
                            if not shell_identified and any(s in first_line for s in ['sh', 'shell']):
                                shebang_scripts['unknown'].append(str(file))
                except Exception:
                    pass
        
        all_scripts = {
            'sh': [str(f) for f in sh_files],
            'bash': [str(f) for f in bash_files],
            'zsh': [str(f) for f in zsh_files],
            'ksh': [str(f) for f in ksh_files],
            'dash': [str(f) for f in dash_files],
            'shebang_scripts': shebang_scripts
        }
        
        total = (len(sh_files) + len(bash_files) + len(zsh_files) + 
                len(ksh_files) + len(dash_files) + 
                sum(len(v) for v in shebang_scripts.values()))
        
        if total == 0:
            return self._build_error_result("No shell scripts found")
        
        # Create summary
        summary = []
        if sh_files:
            summary.append(f"{len(sh_files)} .sh files")
        if bash_files:
            summary.append(f"{len(bash_files)} .bash files")
        if zsh_files:
            summary.append(f"{len(zsh_files)} .zsh files")
        if ksh_files:
            summary.append(f"{len(ksh_files)} .ksh files")
        if dash_files:
            summary.append(f"{len(dash_files)} .dash files")
        for shell, scripts in shebang_scripts.items():
            if scripts:
                summary.append(f"{len(scripts)} {shell} shebang scripts")
        
        return self._build_success_result(
            f"Found {total} shell script(s): {', '.join(summary)}",
            data=all_scripts
        )
    
    def _validate_script(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a shell script."""
        script_path = context.get('script_path')
        
        if not script_path:
            return self._build_error_result("script_path required")
        
        full_path = Path(project_dir) / script_path if not Path(script_path).is_absolute() else Path(script_path)
        
        if not full_path.exists():
            return self._build_error_result(f"Script not found: {full_path}")
        
        issues = []
        warnings = []
        
        # Use shellcheck if available
        if self._has_shellcheck:
            try:
                cmd = ['shellcheck', '-f', 'json', str(full_path)]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.stdout:
                    try:
                        shellcheck_results = json.loads(result.stdout)
                        for issue in shellcheck_results:
                            level = issue.get('level', 'warning')
                            line = issue.get('line', 0)
                            message = issue.get('message', '')
                            
                            if level == 'error':
                                issues.append(f"Line {line}: {message}")
                            else:
                                warnings.append(f"Line {line}: {message}")
                    except json.JSONDecodeError:
                        pass
                
                if issues:
                    return self._build_error_result(
                        f"Script validation failed with {len(issues)} issue(s)",
                        data={'issues': issues, 'warnings': warnings}
                    )
                
                return self._build_success_result(
                    "Script validation passed",
                    data={'warnings': warnings, 'script_path': str(full_path)}
                )
                
            except subprocess.TimeoutExpired:
                return self._build_error_result("Validation timed out")
            except Exception as e:
                # Fallback to basic validation
                pass
        
        # Basic validation without shellcheck
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline()
                if not first_line.startswith('#!'):
                    warnings.append("Missing shebang line")
            
            # Try syntax check
            cmd = [self._shell_cmd, '-n', str(full_path)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                issues.append(f"Syntax error: {result.stderr}")
            
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
        """Run a shell script."""
        script_path = context.get('script_path')
        args = context.get('args', [])
        shell = context.get('shell', self._shell_cmd)
        
        if not script_path:
            return self._build_error_result("script_path required")
        
        full_path = Path(project_dir) / script_path if not Path(script_path).is_absolute() else Path(script_path)
        
        if not full_path.exists():
            return self._build_error_result(f"Script not found: {full_path}")
        
        # Make script executable
        try:
            os.chmod(full_path, 0o755)
        except Exception as e:
            self.logger.warning(f"Could not make script executable: {e}")
        
        try:
            cmd = [shell, str(full_path)] + args
            
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
        except Exception as e:
            return self._build_error_result(f"Script execution failed: {str(e)}", error=e)
    
    def _run_make(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run make command."""
        target = context.get('target', '')
        jobs = context.get('jobs', os.cpu_count())
        
        # Check if Makefile exists
        makefile_path = Path(project_dir) / 'Makefile'
        if not makefile_path.exists():
            return self._build_error_result("Makefile not found")
        
        try:
            cmd = ['make']
            
            if target:
                cmd.append(target)
            
            if jobs:
                cmd.extend(['-j', str(jobs)])
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            if result.returncode == 0:
                return self._build_success_result(
                    f"Make completed successfully",
                    data={
                        'target': target,
                        'output': result.stdout,
                        'command': ' '.join(cmd)
                    }
                )
            else:
                return self._build_error_result(
                    f"Make failed: {result.stderr}",
                    data={'output': result.stderr}
                )
            
        except subprocess.TimeoutExpired:
            return self._build_error_result("Make execution timed out")
        except FileNotFoundError:
            return self._build_error_result("Make not found. Install build-essential")
        except Exception as e:
            return self._build_error_result(f"Make execution failed: {str(e)}", error=e)
    
    def _generate_build_script(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a build shell script."""
        script_name = context.get('script_name', 'build.sh')
        commands = context.get('commands', [])
        shell = context.get('shell', 'bash')
        
        if not commands:
            return self._build_error_result("commands list required")
        
        script_content = [
            f"#!/usr/bin/env {shell}",
            "",
            "# Auto-generated build script",
            f"# Generated by {self.name}",
            "",
            "set -e  # Exit on error",
            "set -u  # Error on undefined variables",
            "",
            "echo 'Starting build...'",
            ""
        ]
        
        for cmd in commands:
            script_content.append(f"echo 'Executing: {cmd}'")
            script_content.append(cmd)
            script_content.append("")
        
        script_content.extend([
            "echo 'Build completed successfully!'",
            "exit 0"
        ])
        
        script_path = Path(project_dir) / script_name
        
        try:
            with open(script_path, 'w') as f:
                f.write('\n'.join(script_content))
            
            # Make script executable
            os.chmod(script_path, 0o755)
            
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
        prompt = f"""You are a shell scripting expert (bash/zsh/sh). Help with this build task:

Task: {task}

Project Directory: {project_dir}
Shell: {self._shell_cmd}
ShellCheck Available: {self._has_shellcheck}
Context: {json.dumps(context, indent=2)}

Provide:
1. Understanding of the build task
2. Recommended shell commands
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
                    'shell': self._shell_cmd,
                    'guidance': guidance
                }
            )
        except Exception as e:
            return self._build_error_result(f"LLM-assisted build failed: {str(e)}", error=e)
