

"""
CSharp Build Agent

Production-ready build system integration for CSharp projects.
Supports MSBuild, dotnet CLI, and NuGet package management.
"""

import os
import subprocess
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from ...base import BuildAgentBase


class CSharpBuildAgent(BuildAgentBase):
    """
    Production-ready CSharp Build Agent.
    
    Features:
        - Build system detection (dotnet CLI, MSBuild)
        - Project compilation (.csproj, .sln)
        - NuGet package restoration
        - Build configuration (Debug/Release)
        - Solution building
        - Test execution (xUnit, NUnit, MSTest)
        - Publish and deployment
        - Clean operations
    """
    
    def __init__(
        self,
        name: str = "csharp_build",
        description: str = "CSharp build and project management agent",
        **kwargs
    ):
        super().__init__(name=name, description=description, **kwargs)
        
        self._timeout = self.config.get('build', {}).get('default_build_timeout', 600)
        self._default_config = 'Release'
        
        self.logger.info("CSharp Build Agent initialized")
        # Load language-specific documentation
        self._load_language_docs()

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CSharp build task."""
        self._log_action("CSharp build task", task[:100])
        
        try:
            operation = context.get('operation', self._detect_operation(task))
            project_dir = context.get('project_dir', os.getcwd())
            
            if not os.path.isdir(project_dir):
                return self._build_error_result(f"Invalid project directory: {project_dir}")
            
            if operation == 'detect_projects':
                return self._detect_projects(project_dir)
            elif operation == 'restore_packages':
                return self._restore_packages(project_dir, context)
            elif operation == 'build_project':
                return self._build_project(project_dir, context)
            elif operation == 'build_solution':
                return self._build_solution(project_dir, context)
            elif operation == 'run_tests':
                return self._run_tests(project_dir, context)
            elif operation == 'publish':
                return self._publish(project_dir, context)
            elif operation == 'clean':
                return self._clean(project_dir, context)
            else:
                return self._llm_assisted_build(task, project_dir, context)
                
        except Exception as e:
            self.logger.error(f"Build task failed: {e}", exc_info=True)
            return self._build_error_result(f"Build task failed: {str(e)}", error=e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect build operation from task description."""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['detect', 'find project', 'list projects']):
            return 'detect_projects'
        elif any(word in task_lower for word in ['restore', 'nuget', 'packages']):
            return 'restore_packages'
        elif 'solution' in task_lower or '.sln' in task_lower:
            return 'build_solution'
        elif any(word in task_lower for word in ['build', 'compile']):
            return 'build_project'
        elif any(word in task_lower for word in ['test', 'xunit', 'nunit', 'mstest']):
            return 'run_tests'
        elif any(word in task_lower for word in ['publish', 'deploy', 'release']):
            return 'publish'
        elif any(word in task_lower for word in ['clean']):
            return 'clean'
        
        return 'llm_assisted'
    
    def _detect_projects(self, project_dir: str) -> Dict[str, Any]:
        """Detect CSharp projects and solutions."""
        project_path = Path(project_dir)
        
        # Find .csproj files
        csproj_files = list(project_path.rglob("*.csproj"))
        
        # Find .sln files
        sln_files = list(project_path.rglob("*.sln"))
        
        # Find .vbproj files (Visual Basic)
        vbproj_files = list(project_path.rglob("*.vbproj"))
        
        # Find .fsproj files (F#)
        fsproj_files = list(project_path.rglob("*.fsproj"))
        
        all_projects = {
            'csharp': [str(f) for f in csproj_files],
            'vb': [str(f) for f in vbproj_files],
            'fsharp': [str(f) for f in fsproj_files],
            'solutions': [str(f) for f in sln_files]
        }
        
        total_projects = len(csproj_files) + len(vbproj_files) + len(fsproj_files)
        
        if total_projects == 0 and len(sln_files) == 0:
            return self._build_error_result("No CSharp projects or solutions found")
        
        return self._build_success_result(
            f"Found {total_projects} project(s) and {len(sln_files)} solution(s)",
            data=all_projects
        )
    
    def _restore_packages(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Restore NuGet packages."""
        project_file = context.get('project_file')
        
        try:
            if project_file:
                cmd = ['dotnet', 'restore', project_file]
            else:
                cmd = ['dotnet', 'restore']
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            if result.returncode == 0:
                return self._build_success_result(
                    "NuGet packages restored successfully",
                    data={
                        'output': result.stdout,
                        'command': ' '.join(cmd)
                    }
                )
            else:
                return self._build_error_result(
                    f"Package restoration failed: {result.stderr}",
                    data={'output': result.stderr}
                )
                
        except subprocess.TimeoutExpired:
            return self._build_error_result("Package restoration timed out")
        except FileNotFoundError:
            return self._build_error_result("dotnet CLI not found. Install .NET SDK")
        except Exception as e:
            return self._build_error_result(f"Package restoration failed: {str(e)}", error=e)
    
    def _build_project(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build a CSharp project."""
        project_file = context.get('project_file')
        configuration = context.get('configuration', self._default_config)
        
        try:
            if project_file:
                cmd = ['dotnet', 'build', project_file, '-c', configuration]
            else:
                cmd = ['dotnet', 'build', '-c', configuration]
            
            # Add additional options
            if context.get('no_restore'):
                cmd.append('--no-restore')
            
            if context.get('verbosity'):
                cmd.extend(['-v', context['verbosity']])
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            if result.returncode == 0:
                return self._build_success_result(
                    f"Project built successfully ({configuration})",
                    data={
                        'configuration': configuration,
                        'output': result.stdout,
                        'command': ' '.join(cmd)
                    }
                )
            else:
                return self._build_error_result(
                    f"Build failed: {result.stderr}",
                    data={
                        'output': result.stderr,
                        'command': ' '.join(cmd)
                    }
                )
                
        except subprocess.TimeoutExpired:
            return self._build_error_result("Build timed out")
        except Exception as e:
            return self._build_error_result(f"Build failed: {str(e)}", error=e)
    
    def _build_solution(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build a CSharp solution."""
        solution_file = context.get('solution_file')
        configuration = context.get('configuration', self._default_config)
        
        # Find solution file if not specified
        if not solution_file:
            detection = self._detect_projects(project_dir)
            if detection['success'] and detection['data']['solutions']:
                solution_file = detection['data']['solutions'][0]
            else:
                return self._build_error_result("No solution file found or specified")
        
        try:
            cmd = ['dotnet', 'build', solution_file, '-c', configuration]
            
            if context.get('no_restore'):
                cmd.append('--no-restore')
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            if result.returncode == 0:
                return self._build_success_result(
                    f"Solution built successfully ({configuration})",
                    data={
                        'solution': solution_file,
                        'configuration': configuration,
                        'output': result.stdout,
                        'command': ' '.join(cmd)
                    }
                )
            else:
                return self._build_error_result(
                    f"Solution build failed: {result.stderr}",
                    data={'output': result.stderr}
                )
                
        except subprocess.TimeoutExpired:
            return self._build_error_result("Solution build timed out")
        except Exception as e:
            return self._build_error_result(f"Solution build failed: {str(e)}", error=e)
    
    def _run_tests(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run CSharp tests."""
        test_project = context.get('test_project')
        configuration = context.get('configuration', self._default_config)
        
        try:
            if test_project:
                cmd = ['dotnet', 'test', test_project, '-c', configuration]
            else:
                cmd = ['dotnet', 'test', '-c', configuration]
            
            if context.get('no_build'):
                cmd.append('--no-build')
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            return self._build_success_result(
                f"Tests executed ({configuration})",
                data={
                    'exit_code': result.returncode,
                    'passed': result.returncode == 0,
                    'output': result.stdout,
                    'errors': result.stderr,
                    'command': ' '.join(cmd)
                }
            )
            
        except subprocess.TimeoutExpired:
            return self._build_error_result("Test execution timed out")
        except Exception as e:
            return self._build_error_result(f"Test execution failed: {str(e)}", error=e)
    
    def _publish(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Publish a CSharp project."""
        project_file = context.get('project_file')
        configuration = context.get('configuration', self._default_config)
        output_dir = context.get('output_dir', './publish')
        runtime = context.get('runtime')  # e.g., 'win-x64', 'linux-x64'
        
        try:
            if project_file:
                cmd = ['dotnet', 'publish', project_file, '-c', configuration, '-o', output_dir]
            else:
                cmd = ['dotnet', 'publish', '-c', configuration, '-o', output_dir]
            
            if runtime:
                cmd.extend(['-r', runtime])
            
            if context.get('self_contained') is not None:
                if context['self_contained']:
                    cmd.append('--self-contained')
                else:
                    cmd.append('--no-self-contained')
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            if result.returncode == 0:
                return self._build_success_result(
                    f"Project published successfully to {output_dir}",
                    data={
                        'output_dir': output_dir,
                        'configuration': configuration,
                        'runtime': runtime,
                        'output': result.stdout,
                        'command': ' '.join(cmd)
                    }
                )
            else:
                return self._build_error_result(
                    f"Publish failed: {result.stderr}",
                    data={'output': result.stderr}
                )
                
        except subprocess.TimeoutExpired:
            return self._build_error_result("Publish timed out")
        except Exception as e:
            return self._build_error_result(f"Publish failed: {str(e)}", error=e)
    
    def _clean(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean build artifacts."""
        project_file = context.get('project_file')
        
        try:
            if project_file:
                cmd = ['dotnet', 'clean', project_file]
            else:
                cmd = ['dotnet', 'clean']
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return self._build_success_result(
                    "Build artifacts cleaned",
                    data={
                        'output': result.stdout,
                        'command': ' '.join(cmd)
                    }
                )
            else:
                return self._build_error_result(
                    f"Clean failed: {result.stderr}",
                    data={'output': result.stderr}
                )
                
        except Exception as e:
            return self._build_error_result(f"Clean failed: {str(e)}", error=e)
    
    def _llm_assisted_build(self, task: str, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to assist with build task."""
        detection = self._detect_projects(project_dir)
        projects_info = detection['data'] if detection['success'] else {}
        
        prompt = f"""You are a CSharp build system expert. Help with this build task:

Task: {task}

Project Directory: {project_dir}
Detected Projects: {json.dumps(projects_info, indent=2)}
Context: {json.dumps(context, indent=2)}

Provide:
1. Understanding of the build task
2. Recommended dotnet CLI commands
3. Step-by-step build process
4. Common issues and solutions

Be specific and actionable."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            guidance = llm_result.get('response', '')
            
            return self._build_success_result(
                "Build guidance provided",
                data={
                    'task': task,
                    'projects': projects_info,
                    'guidance': guidance
                }
            )
        except Exception as e:
            return self._build_error_result(f"LLM-assisted build failed: {str(e)}", error=e)
