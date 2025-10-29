

"""
WebDev Build Agent

Production-ready build system integration for full-stack web development projects.

Supported Technologies:
- Package Managers: npm, yarn, pnpm
- Build Tools: Webpack, Vite, Parcel, Rollup, Turbopack, esbuild
- Frontend Frameworks: React, Next.js, Vue, Nuxt, Angular, Svelte
- Backend Frameworks: Express, Fastify, Koa, NestJS
- Testing Frameworks: Jest, Vitest, Mocha, Jasmine, Playwright, Cypress
- Linters/Formatters: ESLint, Prettier, Biome
"""

import os
import subprocess
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from ...base import BuildAgentBase


class WebJSTSBuildAgent(BuildAgentBase):
    """
    Production-ready WebDev Build Agent.
    
    Features:
        - Package manager detection (npm, yarn, pnpm)
        - Dependency installation
        - Build tool integration (webpack, vite, parcel, rollup)
        - Script execution from package.json
        - Production builds
        - Development server management
        - Linting and formatting
        - Test execution
    """
    
    def __init__(
        self,
        name: str = "webdev_build",
        description: str = "Full-stack web development build agent (npm/yarn/pnpm/webpack/vite/parcel/rollup)",
        **kwargs
    ):
        super().__init__(name=name, description=description, **kwargs)
        
        self._timeout = self.config.get('build', {}).get('default_build_timeout', 600)
        self._package_manager = None
        
        # Supported package managers with commands
        self.package_managers = {
            'npm': {
                'install': ['npm', 'install'],
                'install_dev': ['npm', 'install', '--save-dev'],
                'run_script': ['npm', 'run'],
                'build': ['npm', 'run', 'build'],
                'test': ['npm', 'test'],
                'start': ['npm', 'start']
            },
            'yarn': {
                'install': ['yarn', 'install'],
                'install_dev': ['yarn', 'add', '--dev'],
                'run_script': ['yarn'],
                'build': ['yarn', 'build'],
                'test': ['yarn', 'test'],
                'start': ['yarn', 'start']
            },
            'pnpm': {
                'install': ['pnpm', 'install'],
                'install_dev': ['pnpm', 'add', '--save-dev'],
                'run_script': ['pnpm'],
                'build': ['pnpm', 'build'],
                'test': ['pnpm', 'test'],
                'start': ['pnpm', 'start']
            }
        }
        
        # Build tools detection
        self.build_tools = {
            'webpack': ['webpack.config.js', 'webpack.config.ts'],
            'vite': ['vite.config.js', 'vite.config.ts', 'vite.config.mjs'],
            'parcel': ['.parcelrc', 'parcel-bundler'],
            'rollup': ['rollup.config.js', 'rollup.config.mjs', 'rollup.config.ts'],
            'turbopack': ['turbo.json'],
            'esbuild': ['esbuild.config.js'],
            'nextjs': ['next.config.js', 'next.config.mjs'],
            'angular': ['angular.json'],
            'vue-cli': ['vue.config.js'],
            'nuxt': ['nuxt.config.js', 'nuxt.config.ts']
        }
        
        self.logger.info("WebDev Build Agent initialized with full-stack support")
        # Load language-specific documentation
        self._load_language_docs()

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute WebDev build task."""
        self._log_action("WebDev build task", task[:100])
        
        try:
            operation = context.get('operation', self._detect_operation(task))
            project_dir = context.get('project_dir', os.getcwd())
            
            if not os.path.isdir(project_dir):
                return self._build_error_result(f"Invalid project directory: {project_dir}")
            
            if operation == 'detect_package_manager':
                return self._detect_package_manager(project_dir)
            elif operation == 'install_dependencies':
                return self._install_dependencies(project_dir, context)
            elif operation == 'build':
                return self._build(project_dir, context)
            elif operation == 'run_script':
                return self._run_script(project_dir, context)
            elif operation == 'run_tests':
                return self._run_tests(project_dir, context)
            elif operation == 'lint':
                return self._lint(project_dir, context)
            elif operation == 'start_dev_server':
                return self._start_dev_server(project_dir, context)
            else:
                return self._llm_assisted_build(task, project_dir, context)
                
        except Exception as e:
            self.logger.error(f"Build task failed: {e}", exc_info=True)
            return self._build_error_result(f"Build task failed: {str(e)}", error=e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect build operation from task description."""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['detect', 'identify', 'find package']):
            return 'detect_package_manager'
        elif any(word in task_lower for word in ['install', 'dependencies', 'node_modules']):
            return 'install_dependencies'
        elif any(word in task_lower for word in ['build', 'compile', 'bundle', 'webpack', 'vite', 'rollup']):
            return 'build'
        elif any(word in task_lower for word in ['run script', 'npm run', 'yarn run']):
            return 'run_script'
        elif any(word in task_lower for word in ['test', 'jest', 'mocha', 'vitest']):
            return 'run_tests'
        elif any(word in task_lower for word in ['lint', 'eslint', 'prettier']):
            return 'lint'
        elif any(word in task_lower for word in ['dev server', 'start', 'serve']):
            return 'start_dev_server'
        
        return 'llm_assisted'
    
    def _detect_package_manager(self, project_dir: str) -> Dict[str, Any]:
        """Detect the package manager used in the project."""
        project_path = Path(project_dir)
        detected = []
        
        # Check for package.json (required)
        if not (project_path / "package.json").exists():
            return self._build_error_result("No package.json found")
        
        # Check for lock files
        if (project_path / "package-lock.json").exists():
            detected.append('npm')
        
        if (project_path / "yarn.lock").exists():
            detected.append('yarn')
        
        if (project_path / "pnpm-lock.yaml").exists():
            detected.append('pnpm')
        
        # Check which package managers are available
        available_managers = []
        for manager in ['npm', 'yarn', 'pnpm']:
            try:
                result = subprocess.run(
                    [manager, '--version'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    available_managers.append(manager)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
        
        # Determine primary package manager
        if detected:
            primary = detected[0]
        elif available_managers:
            primary = available_managers[0]
        else:
            return self._build_error_result("No package manager available")
        
        self._package_manager = primary
        
        return self._build_success_result(
            f"Detected package manager: {primary}",
            data={
                'package_manager': primary,
                'detected_from_lockfile': detected,
                'available': available_managers
            }
        )
    
    def _install_dependencies(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Install project dependencies."""
        detection = self._detect_package_manager(project_dir)
        if not detection['success']:
            return detection
        
        package_manager = detection['data']['package_manager']
        
        try:
            if package_manager == 'npm':
                cmd = ['npm', 'install']
            elif package_manager == 'yarn':
                cmd = ['yarn', 'install']
            elif package_manager == 'pnpm':
                cmd = ['pnpm', 'install']
            else:
                return self._build_error_result(f"Unsupported package manager: {package_manager}")
            
            # Add flags
            if context.get('production'):
                if package_manager == 'npm':
                    cmd.append('--production')
                elif package_manager == 'yarn':
                    cmd.append('--production')
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            if result.returncode == 0:
                return self._build_success_result(
                    f"Dependencies installed using {package_manager}",
                    data={
                        'package_manager': package_manager,
                        'output': result.stdout[-1000:],  # Last 1000 chars
                        'command': ' '.join(cmd)
                    }
                )
            else:
                return self._build_error_result(
                    f"Dependency installation failed: {result.stderr}",
                    data={'output': result.stderr}
                )
                
        except subprocess.TimeoutExpired:
            return self._build_error_result("Dependency installation timed out")
        except FileNotFoundError:
            return self._build_error_result(f"Package manager not found: {package_manager}")
        except Exception as e:
            return self._build_error_result(f"Dependency installation failed: {str(e)}", error=e)
    
    def _build(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build the web project."""
        detection = self._detect_package_manager(project_dir)
        if not detection['success']:
            return detection
        
        package_manager = detection['data']['package_manager']
        build_script = context.get('build_script', 'build')
        
        try:
            # Check if build script exists in package.json
            package_json_path = Path(project_dir) / "package.json"
            with open(package_json_path, 'r') as f:
                package_json = json.load(f)
                scripts = package_json.get('scripts', {})
                
                if build_script not in scripts:
                    return self._build_error_result(
                        f"Build script '{build_script}' not found in package.json"
                    )
            
            if package_manager == 'npm':
                cmd = ['npm', 'run', build_script]
            elif package_manager == 'yarn':
                cmd = ['yarn', build_script]
            elif package_manager == 'pnpm':
                cmd = ['pnpm', 'run', build_script]
            else:
                return self._build_error_result(f"Unsupported package manager: {package_manager}")
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            if result.returncode == 0:
                # Try to detect build output directory
                build_dirs = ['dist', 'build', 'out', '.next', '.output']
                output_dir = None
                for dir_name in build_dirs:
                    dir_path = Path(project_dir) / dir_name
                    if dir_path.exists():
                        output_dir = str(dir_path)
                        break
                
                return self._build_success_result(
                    f"Build completed successfully using {package_manager}",
                    data={
                        'package_manager': package_manager,
                        'build_script': build_script,
                        'output_dir': output_dir,
                        'output': result.stdout[-1000:],
                        'command': ' '.join(cmd)
                    }
                )
            else:
                return self._build_error_result(
                    f"Build failed: {result.stderr}",
                    data={'output': result.stderr}
                )
                
        except subprocess.TimeoutExpired:
            return self._build_error_result("Build timed out")
        except json.JSONDecodeError:
            return self._build_error_result("Invalid package.json")
        except FileNotFoundError:
            return self._build_error_result("package.json not found")
        except Exception as e:
            return self._build_error_result(f"Build failed: {str(e)}", error=e)
    
    def _run_script(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run a custom script from package.json."""
        script_name = context.get('script_name')
        
        if not script_name:
            return self._build_error_result("script_name required")
        
        detection = self._detect_package_manager(project_dir)
        if not detection['success']:
            return detection
        
        package_manager = detection['data']['package_manager']
        
        try:
            if package_manager == 'npm':
                cmd = ['npm', 'run', script_name]
            elif package_manager == 'yarn':
                cmd = ['yarn', script_name]
            elif package_manager == 'pnpm':
                cmd = ['pnpm', 'run', script_name]
            else:
                return self._build_error_result(f"Unsupported package manager: {package_manager}")
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            return self._build_success_result(
                f"Script '{script_name}' executed",
                data={
                    'script_name': script_name,
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
    
    def _run_tests(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run web project tests."""
        detection = self._detect_package_manager(project_dir)
        if not detection['success']:
            return detection
        
        package_manager = detection['data']['package_manager']
        test_script = context.get('test_script', 'test')
        
        try:
            if package_manager == 'npm':
                cmd = ['npm', 'run', test_script]
            elif package_manager == 'yarn':
                cmd = ['yarn', test_script]
            elif package_manager == 'pnpm':
                cmd = ['pnpm', 'run', test_script]
            else:
                return self._build_error_result(f"Unsupported package manager: {package_manager}")
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            return self._build_success_result(
                f"Tests executed",
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
    
    def _lint(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run linting on the project."""
        detection = self._detect_package_manager(project_dir)
        if not detection['success']:
            return detection
        
        package_manager = detection['data']['package_manager']
        lint_script = context.get('lint_script', 'lint')
        
        try:
            # Check if lint script exists
            package_json_path = Path(project_dir) / "package.json"
            with open(package_json_path, 'r') as f:
                package_json = json.load(f)
                scripts = package_json.get('scripts', {})
                
                if lint_script not in scripts:
                    return self._build_error_result(
                        f"Lint script '{lint_script}' not found in package.json"
                    )
            
            if package_manager == 'npm':
                cmd = ['npm', 'run', lint_script]
            elif package_manager == 'yarn':
                cmd = ['yarn', lint_script]
            elif package_manager == 'pnpm':
                cmd = ['pnpm', 'run', lint_script]
            else:
                return self._build_error_result(f"Unsupported package manager: {package_manager}")
            
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            return self._build_success_result(
                f"Linting completed",
                data={
                    'exit_code': result.returncode,
                    'passed': result.returncode == 0,
                    'output': result.stdout,
                    'errors': result.stderr,
                    'command': ' '.join(cmd)
                }
            )
            
        except subprocess.TimeoutExpired:
            return self._build_error_result("Linting timed out")
        except Exception as e:
            return self._build_error_result(f"Linting failed: {str(e)}", error=e)
    
    def _start_dev_server(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Start development server."""
        detection = self._detect_package_manager(project_dir)
        if not detection['success']:
            return detection
        
        package_manager = detection['data']['package_manager']
        dev_script = context.get('dev_script', 'dev')
        
        # Check for alternative dev script names
        try:
            package_json_path = Path(project_dir) / "package.json"
            with open(package_json_path, 'r') as f:
                package_json = json.load(f)
                scripts = package_json.get('scripts', {})
                
                if dev_script not in scripts:
                    # Try alternatives
                    alternatives = ['start', 'serve', 'dev', 'develop']
                    for alt in alternatives:
                        if alt in scripts:
                            dev_script = alt
                            break
                    else:
                        return self._build_error_result(
                            f"No dev server script found in package.json"
                        )
        except Exception as e:
            return self._build_error_result(f"Failed to read package.json: {str(e)}")
        
        if package_manager == 'npm':
            cmd = ['npm', 'run', dev_script]
        elif package_manager == 'yarn':
            cmd = ['yarn', dev_script]
        elif package_manager == 'pnpm':
            cmd = ['pnpm', 'run', dev_script]
        else:
            return self._build_error_result(f"Unsupported package manager: {package_manager}")
        
        # Note: Dev servers typically run indefinitely
        return self._build_success_result(
            f"Dev server command prepared",
            data={
                'command': ' '.join(cmd),
                'dev_script': dev_script,
                'note': 'Dev server must be started manually or in background',
                'suggestion': f'Run: cd {project_dir} && {" ".join(cmd)}'
            }
        )
    
    def _llm_assisted_build(self, task: str, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to assist with build task."""
        detection = self._detect_package_manager(project_dir)
        package_manager = detection['data'].get('package_manager', 'unknown') if detection['success'] else 'unknown'
        
        prompt = f"""You are a web development build system expert. Help with this build task:

Task: {task}

Project Directory: {project_dir}
Package Manager: {package_manager}
Context: {json.dumps(context, indent=2)}

Provide:
1. Understanding of the build task
2. Recommended commands (npm/yarn/pnpm)
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
                    'package_manager': package_manager,
                    'guidance': guidance
                }
            )
        except Exception as e:
            return self._build_error_result(f"LLM-assisted build failed: {str(e)}", error=e)
