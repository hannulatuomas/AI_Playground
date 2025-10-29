

"""
Python Build Agent

Production-ready build system integration for Python projects.
Supports setuptools, pip, poetry, and wheel building.
"""

import os
import subprocess
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging

from ...base import BuildAgentBase


class PythonBuildAgent(BuildAgentBase):
    """
    Production-ready Python Build Agent.
    
    Features:
        - Build system detection (setuptools, poetry, pip)
        - Dependency installation and management
        - Virtual environment support
        - Package building (wheel, sdist)
        - Requirements.txt management
        - Build configuration validation
        - Test execution integration
        - Distribution building
    """
    
    def __init__(
        self,
        name: str = "python_build",
        description: str = "Python build and package management agent",
        **kwargs
    ):
        super().__init__(name=name, description=description, **kwargs)
        
        self._build_system = None
        self._timeout = self.config.get('build', {}).get('default_build_timeout', 600)
        self._supported_build_systems = ['poetry', 'setuptools', 'pip']
        
        self.logger.info("Python Build Agent initialized")
        # Load language-specific documentation
        self._load_language_docs()

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Python build task."""
        self._log_action("Python build task", task[:100])
        
        try:
            operation = context.get('operation', self._detect_operation(task))
            project_dir = context.get('project_dir', os.getcwd())
            
            # Validate project directory
            if not os.path.isdir(project_dir):
                return self._build_error_result(f"Invalid project directory: {project_dir}")
            
            if operation == 'detect_build_system':
                return self._detect_build_system(project_dir)
            elif operation == 'install_dependencies':
                return self._install_dependencies(project_dir, context)
            elif operation == 'build_package':
                return self._build_package(project_dir, context)
            elif operation == 'run_tests':
                return self._run_tests(project_dir, context)
            elif operation == 'create_virtualenv':
                return self._create_virtualenv(project_dir, context)
            elif operation == 'validate_config':
                return self._validate_build_config(project_dir)
            elif operation == 'clean_build':
                return self._clean_build(project_dir)
            else:
                # Use LLM to understand the build request
                return self._llm_assisted_build(task, project_dir, context)
                
        except Exception as e:
            self.logger.error(f"Build task failed: {e}", exc_info=True)
            return self._build_error_result(f"Build task failed: {str(e)}", error=e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect build operation from task description."""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['detect', 'identify', 'find build system']):
            return 'detect_build_system'
        elif any(word in task_lower for word in ['install', 'dependencies', 'requirements']):
            return 'install_dependencies'
        elif any(word in task_lower for word in ['build', 'compile', 'package', 'wheel', 'sdist']):
            return 'build_package'
        elif any(word in task_lower for word in ['test', 'pytest', 'unittest']):
            return 'run_tests'
        elif any(word in task_lower for word in ['virtualenv', 'venv', 'virtual environment']):
            return 'create_virtualenv'
        elif any(word in task_lower for word in ['validate', 'check config', 'verify']):
            return 'validate_config'
        elif any(word in task_lower for word in ['clean', 'remove build']):
            return 'clean_build'
        
        return 'llm_assisted'
    
    def _detect_build_system(self, project_dir: str) -> Dict[str, Any]:
        """Detect the Python build system used in the project."""
        project_path = Path(project_dir)
        detected_systems = []
        
        # Check for poetry
        if (project_path / "pyproject.toml").exists():
            with open(project_path / "pyproject.toml", 'r') as f:
                content = f.read()
                if 'poetry' in content.lower():
                    detected_systems.append('poetry')
                elif 'build-system' in content:
                    detected_systems.append('setuptools')
        
        # Check for setup.py
        if (project_path / "setup.py").exists():
            detected_systems.append('setuptools')
        
        # Check for requirements.txt
        if (project_path / "requirements.txt").exists():
            detected_systems.append('pip')
        
        # Check for setup.cfg
        if (project_path / "setup.cfg").exists():
            detected_systems.append('setuptools')
        
        if not detected_systems:
            return self._build_error_result("No Python build system detected")
        
        # Prioritize poetry > setuptools > pip
        primary_system = detected_systems[0]
        if 'poetry' in detected_systems:
            primary_system = 'poetry'
        elif 'setuptools' in detected_systems:
            primary_system = 'setuptools'
        
        self._build_system = primary_system
        
        return self._build_success_result(
            f"Detected build system: {primary_system}",
            data={
                'build_system': primary_system,
                'all_systems': detected_systems,
                'project_dir': project_dir
            }
        )
    
    def _install_dependencies(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Install project dependencies."""
        # Detect build system first
        detection = self._detect_build_system(project_dir)
        if not detection['success']:
            return detection
        
        build_system = detection['data']['build_system']
        dev_dependencies = context.get('dev', False)
        
        try:
            if build_system == 'poetry':
                cmd = ['poetry', 'install']
                if not dev_dependencies:
                    cmd.append('--no-dev')
            elif build_system == 'setuptools':
                cmd = ['pip', 'install', '-e', '.']
                if dev_dependencies:
                    cmd.extend(['-r', 'requirements-dev.txt'])
            else:  # pip
                cmd = ['pip', 'install', '-r', 'requirements.txt']
                if dev_dependencies and os.path.exists(os.path.join(project_dir, 'requirements-dev.txt')):
                    cmd.extend(['-r', 'requirements-dev.txt'])
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            if result.returncode == 0:
                return self._build_success_result(
                    f"Dependencies installed successfully using {build_system}",
                    data={
                        'build_system': build_system,
                        'output': result.stdout,
                        'command': ' '.join(cmd)
                    }
                )
            else:
                return self._build_error_result(
                    f"Dependency installation failed: {result.stderr}",
                    data={'output': result.stderr, 'command': ' '.join(cmd)}
                )
                
        except subprocess.TimeoutExpired:
            return self._build_error_result("Dependency installation timed out")
        except FileNotFoundError as e:
            return self._build_error_result(f"Build tool not found: {str(e)}")
        except Exception as e:
            return self._build_error_result(f"Dependency installation failed: {str(e)}", error=e)
    
    def _build_package(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build Python package (wheel/sdist)."""
        detection = self._detect_build_system(project_dir)
        if not detection['success']:
            return detection
        
        build_system = detection['data']['build_system']
        build_type = context.get('build_type', 'wheel')  # wheel, sdist, or both
        
        try:
            if build_system == 'poetry':
                cmd = ['poetry', 'build']
                if build_type == 'wheel':
                    cmd.append('--format=wheel')
                elif build_type == 'sdist':
                    cmd.append('--format=sdist')
            else:
                # Use python -m build (modern approach)
                cmd = ['python', '-m', 'build']
                if build_type == 'wheel':
                    cmd.extend(['--wheel'])
                elif build_type == 'sdist':
                    cmd.extend(['--sdist'])
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            if result.returncode == 0:
                # Find built artifacts
                dist_dir = Path(project_dir) / 'dist'
                artifacts = []
                if dist_dir.exists():
                    artifacts = [str(f) for f in dist_dir.iterdir() if f.is_file()]
                
                return self._build_success_result(
                    f"Package built successfully using {build_system}",
                    data={
                        'build_system': build_system,
                        'artifacts': artifacts,
                        'output': result.stdout,
                        'command': ' '.join(cmd)
                    }
                )
            else:
                return self._build_error_result(
                    f"Package build failed: {result.stderr}",
                    data={'output': result.stderr, 'command': ' '.join(cmd)}
                )
                
        except subprocess.TimeoutExpired:
            return self._build_error_result("Package build timed out")
        except Exception as e:
            return self._build_error_result(f"Package build failed: {str(e)}", error=e)
    
    def _run_tests(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run Python tests."""
        test_framework = context.get('framework', self._detect_test_framework(project_dir))
        test_path = context.get('test_path', 'tests')
        
        try:
            if test_framework == 'pytest':
                cmd = ['pytest', test_path, '-v']
            elif test_framework == 'unittest':
                cmd = ['python', '-m', 'unittest', 'discover', '-s', test_path]
            else:
                return self._build_error_result("No test framework detected")
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            return self._build_success_result(
                f"Tests executed using {test_framework}",
                data={
                    'framework': test_framework,
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
    
    def _detect_test_framework(self, project_dir: str) -> str:
        """Detect the test framework used."""
        project_path = Path(project_dir)
        
        # Check for pytest
        if (project_path / "pytest.ini").exists() or (project_path / "setup.cfg").exists():
            return 'pytest'
        
        # Check for conftest.py (pytest)
        if list(project_path.rglob("conftest.py")):
            return 'pytest'
        
        # Default to unittest
        return 'unittest'
    
    def _create_virtualenv(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a virtual environment."""
        venv_name = context.get('venv_name', 'venv')
        venv_path = Path(project_dir) / venv_name
        
        if venv_path.exists():
            return self._build_error_result(f"Virtual environment already exists: {venv_path}")
        
        try:
            cmd = ['python', '-m', 'venv', str(venv_path)]
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                # Provide activation instructions
                if os.name == 'nt':
                    activate_cmd = f"{venv_name}\\Scripts\\activate.bat"
                else:
                    activate_cmd = f"source {venv_name}/bin/activate"
                
                return self._build_success_result(
                    f"Virtual environment created: {venv_path}",
                    data={
                        'venv_path': str(venv_path),
                        'activate_command': activate_cmd,
                        'output': result.stdout
                    }
                )
            else:
                return self._build_error_result(f"Virtual environment creation failed: {result.stderr}")
                
        except Exception as e:
            return self._build_error_result(f"Virtual environment creation failed: {str(e)}", error=e)
    
    def _validate_build_config(self, project_dir: str) -> Dict[str, Any]:
        """Validate build configuration files."""
        project_path = Path(project_dir)
        issues = []
        warnings = []
        
        # Check for setup.py
        if (project_path / "setup.py").exists():
            try:
                with open(project_path / "setup.py", 'r') as f:
                    content = f.read()
                    if 'setup(' not in content:
                        issues.append("setup.py missing setup() call")
            except Exception as e:
                issues.append(f"Cannot read setup.py: {str(e)}")
        
        # Check for pyproject.toml
        if (project_path / "pyproject.toml").exists():
            try:
                import tomli
                with open(project_path / "pyproject.toml", 'rb') as f:
                    config = tomli.load(f)
                    if 'project' not in config and 'tool' not in config:
                        issues.append("pyproject.toml missing [project] or [tool] sections")
            except ImportError:
                warnings.append("tomli not installed, cannot validate pyproject.toml")
            except Exception as e:
                issues.append(f"Invalid pyproject.toml: {str(e)}")
        
        # Check for requirements.txt
        if (project_path / "requirements.txt").exists():
            try:
                with open(project_path / "requirements.txt", 'r') as f:
                    lines = f.readlines()
                    if not lines:
                        warnings.append("requirements.txt is empty")
            except Exception as e:
                issues.append(f"Cannot read requirements.txt: {str(e)}")
        
        if issues:
            return self._build_error_result(
                f"Build configuration validation failed with {len(issues)} issue(s)",
                data={'issues': issues, 'warnings': warnings}
            )
        
        return self._build_success_result(
            "Build configuration is valid",
            data={'warnings': warnings, 'project_dir': project_dir}
        )
    
    def _clean_build(self, project_dir: str) -> Dict[str, Any]:
        """Clean build artifacts."""
        project_path = Path(project_dir)
        cleaned = []
        
        # Directories to clean
        clean_dirs = ['build', 'dist', '*.egg-info', '__pycache__', '.pytest_cache']
        
        for pattern in clean_dirs:
            for path in project_path.glob(pattern):
                try:
                    if path.is_dir():
                        import shutil
                        shutil.rmtree(path)
                        cleaned.append(str(path))
                except Exception as e:
                    self.logger.warning(f"Failed to remove {path}: {e}")
        
        return self._build_success_result(
            f"Cleaned {len(cleaned)} build artifact(s)",
            data={'cleaned': cleaned}
        )
    
    def _llm_assisted_build(self, task: str, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to assist with build task."""
        # Detect build system for context
        detection = self._detect_build_system(project_dir)
        build_system = detection['data'].get('build_system', 'unknown') if detection['success'] else 'unknown'
        
        prompt = f"""You are a Python build system expert. Help with this build task:

Task: {task}

Project Directory: {project_dir}
Build System: {build_system}
Context: {json.dumps(context, indent=2)}

Provide:
1. Understanding of the build task
2. Recommended build commands
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
                    'build_system': build_system,
                    'guidance': guidance
                }
            )
        except Exception as e:
            return self._build_error_result(f"LLM-assisted build failed: {str(e)}", error=e)
