

"""
CPP Build Agent

Production-ready build system integration for CPP projects.
Supports CMake, Make, MSBuild, and various compilers.
"""

import os
import subprocess
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from ...base import BuildAgentBase


class CPPBuildAgent(BuildAgentBase):
    """
    Production-ready CPP Build Agent.
    
    Features:
        - Build system detection (CMake, Make, MSBuild, Ninja)
        - Compiler detection (GCC, Clang, MSVC)
        - Project configuration and generation
        - Multi-configuration builds
        - Target building
        - Clean operations
        - Install and packaging
        - Cross-platform support
    """
    
    def __init__(
        self,
        name: str = "cpp_build",
        description: str = "CPP build and project management agent",
        **kwargs
    ):
        super().__init__(name=name, description=description, **kwargs)
        
        self._timeout = self.config.get('build', {}).get('default_build_timeout', 900)
        self._build_type = 'Release'
        
        self.logger.info("CPP Build Agent initialized")
        # Load language-specific documentation
        self._load_language_docs()

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CPP build task."""
        self._log_action("CPP build task", task[:100])
        
        try:
            operation = context.get('operation', self._detect_operation(task))
            project_dir = context.get('project_dir', os.getcwd())
            
            if not os.path.isdir(project_dir):
                return self._build_error_result(f"Invalid project directory: {project_dir}")
            
            if operation == 'detect_build_system':
                return self._detect_build_system(project_dir)
            elif operation == 'configure':
                return self._configure(project_dir, context)
            elif operation == 'build':
                return self._build(project_dir, context)
            elif operation == 'clean':
                return self._clean(project_dir, context)
            elif operation == 'install':
                return self._install(project_dir, context)
            elif operation == 'run_tests':
                return self._run_tests(project_dir, context)
            else:
                return self._llm_assisted_build(task, project_dir, context)
                
        except Exception as e:
            self.logger.error(f"Build task failed: {e}", exc_info=True)
            return self._build_error_result(f"Build task failed: {str(e)}", error=e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect build operation from task description."""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['detect', 'identify', 'find build']):
            return 'detect_build_system'
        elif any(word in task_lower for word in ['configure', 'generate', 'cmake']):
            return 'configure'
        elif any(word in task_lower for word in ['build', 'compile', 'make']):
            return 'build'
        elif any(word in task_lower for word in ['clean']):
            return 'clean'
        elif any(word in task_lower for word in ['install', 'deploy']):
            return 'install'
        elif any(word in task_lower for word in ['test', 'ctest']):
            return 'run_tests'
        
        return 'llm_assisted'
    
    def _detect_build_system(self, project_dir: str) -> Dict[str, Any]:
        """Detect CPP build system."""
        project_path = Path(project_dir)
        detected = []
        
        # Check for CMake
        if (project_path / "CMakeLists.txt").exists():
            detected.append('cmake')
        
        # Check for Make
        if (project_path / "Makefile").exists():
            detected.append('make')
        
        # Check for Visual Studio
        vcxproj_files = list(project_path.rglob("*.vcxproj"))
        if vcxproj_files:
            detected.append('msbuild')
        
        # Check for Ninja
        if (project_path / "build.ninja").exists():
            detected.append('ninja')
        
        # Check for Meson
        if (project_path / "meson.build").exists():
            detected.append('meson')
        
        if not detected:
            return self._build_error_result("No CPP build system detected")
        
        primary = detected[0]
        if 'cmake' in detected:
            primary = 'cmake'
        
        return self._build_success_result(
            f"Detected build system: {primary}",
            data={
                'build_system': primary,
                'all_systems': detected,
                'project_dir': project_dir
            }
        )
    
    def _configure(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Configure CPP project (CMake generation)."""
        build_dir = context.get('build_dir', 'build')
        build_type = context.get('build_type', self._build_type)
        generator = context.get('generator')  # e.g., 'Ninja', 'Unix Makefiles'
        
        detection = self._detect_build_system(project_dir)
        if not detection['success']:
            return detection
        
        build_system = detection['data']['build_system']
        
        try:
            if build_system == 'cmake':
                # Create build directory
                build_path = Path(project_dir) / build_dir
                build_path.mkdir(exist_ok=True)
                
                cmd = ['cmake', '..', f'-DCMAKE_BUILD_TYPE={build_type}']
                
                if generator:
                    cmd.extend(['-G', generator])
                
                # Add custom CMake options
                cmake_options = context.get('cmake_options', {})
                for key, value in cmake_options.items():
                    cmd.append(f'-D{key}={value}')
                
                result = subprocess.run(
                    cmd,
                    cwd=str(build_path),
                    capture_output=True,
                    text=True,
                    timeout=self._timeout
                )
                
                if result.returncode == 0:
                    return self._build_success_result(
                        f"CMake configuration successful ({build_type})",
                        data={
                            'build_dir': build_dir,
                            'build_type': build_type,
                            'generator': generator,
                            'output': result.stdout,
                            'command': ' '.join(cmd)
                        }
                    )
                else:
                    return self._build_error_result(
                        f"CMake configuration failed: {result.stderr}",
                        data={'output': result.stderr}
                    )
            else:
                return self._build_error_result(f"Configure not supported for {build_system}")
                
        except subprocess.TimeoutExpired:
            return self._build_error_result("Configuration timed out")
        except FileNotFoundError:
            return self._build_error_result("CMake not found. Install CMake")
        except Exception as e:
            return self._build_error_result(f"Configuration failed: {str(e)}", error=e)
    
    def _build(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build CPP project."""
        build_dir = context.get('build_dir', 'build')
        target = context.get('target')  # Specific target to build
        jobs = context.get('jobs', os.cpu_count())
        
        detection = self._detect_build_system(project_dir)
        if not detection['success']:
            return detection
        
        build_system = detection['data']['build_system']
        
        try:
            if build_system == 'cmake':
                build_path = Path(project_dir) / build_dir
                if not build_path.exists():
                    return self._build_error_result(
                        f"Build directory not found. Run configure first: {build_path}"
                    )
                
                cmd = ['cmake', '--build', '.']
                
                if target:
                    cmd.extend(['--target', target])
                
                if jobs:
                    cmd.extend(['-j', str(jobs)])
                
                result = subprocess.run(
                    cmd,
                    cwd=str(build_path),
                    capture_output=True,
                    text=True,
                    timeout=self._timeout
                )
                
            elif build_system == 'make':
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
                
            elif build_system == 'msbuild':
                # Find .vcxproj or .sln file
                vcxproj_files = list(Path(project_dir).rglob("*.vcxproj"))
                sln_files = list(Path(project_dir).rglob("*.sln"))
                
                if sln_files:
                    project_file = str(sln_files[0])
                elif vcxproj_files:
                    project_file = str(vcxproj_files[0])
                else:
                    return self._build_error_result("No Visual Studio project found")
                
                cmd = ['msbuild', project_file, '/p:Configuration=Release']
                
                result = subprocess.run(
                    cmd,
                    cwd=project_dir,
                    capture_output=True,
                    text=True,
                    timeout=self._timeout
                )
            else:
                return self._build_error_result(f"Build not supported for {build_system}")
            
            if result.returncode == 0:
                return self._build_success_result(
                    f"Build successful using {build_system}",
                    data={
                        'build_system': build_system,
                        'target': target,
                        'output': result.stdout,
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
        except FileNotFoundError as e:
            return self._build_error_result(f"Build tool not found: {str(e)}")
        except Exception as e:
            return self._build_error_result(f"Build failed: {str(e)}", error=e)
    
    def _clean(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean build artifacts."""
        build_dir = context.get('build_dir', 'build')
        
        detection = self._detect_build_system(project_dir)
        if not detection['success']:
            return detection
        
        build_system = detection['data']['build_system']
        
        try:
            if build_system == 'cmake':
                build_path = Path(project_dir) / build_dir
                if build_path.exists():
                    cmd = ['cmake', '--build', '.', '--target', 'clean']
                    result = subprocess.run(
                        cmd,
                        cwd=str(build_path),
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                else:
                    return self._build_error_result(f"Build directory not found: {build_path}")
                    
            elif build_system == 'make':
                cmd = ['make', 'clean']
                result = subprocess.run(
                    cmd,
                    cwd=project_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
            else:
                return self._build_error_result(f"Clean not supported for {build_system}")
            
            if result.returncode == 0:
                return self._build_success_result(
                    "Clean successful",
                    data={'output': result.stdout}
                )
            else:
                return self._build_error_result(
                    f"Clean failed: {result.stderr}",
                    data={'output': result.stderr}
                )
                
        except Exception as e:
            return self._build_error_result(f"Clean failed: {str(e)}", error=e)
    
    def _install(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Install built project."""
        build_dir = context.get('build_dir', 'build')
        install_prefix = context.get('install_prefix')
        
        detection = self._detect_build_system(project_dir)
        if not detection['success']:
            return detection
        
        build_system = detection['data']['build_system']
        
        try:
            if build_system == 'cmake':
                build_path = Path(project_dir) / build_dir
                cmd = ['cmake', '--install', '.']
                
                if install_prefix:
                    cmd.extend(['--prefix', install_prefix])
                
                result = subprocess.run(
                    cmd,
                    cwd=str(build_path),
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            elif build_system == 'make':
                cmd = ['make', 'install']
                
                if install_prefix:
                    cmd.extend([f'PREFIX={install_prefix}'])
                
                result = subprocess.run(
                    cmd,
                    cwd=project_dir,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            else:
                return self._build_error_result(f"Install not supported for {build_system}")
            
            if result.returncode == 0:
                return self._build_success_result(
                    "Install successful",
                    data={
                        'install_prefix': install_prefix,
                        'output': result.stdout
                    }
                )
            else:
                return self._build_error_result(
                    f"Install failed: {result.stderr}",
                    data={'output': result.stderr}
                )
                
        except Exception as e:
            return self._build_error_result(f"Install failed: {str(e)}", error=e)
    
    def _run_tests(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run CPP tests using CTest."""
        build_dir = context.get('build_dir', 'build')
        
        try:
            build_path = Path(project_dir) / build_dir
            if not build_path.exists():
                return self._build_error_result(f"Build directory not found: {build_path}")
            
            cmd = ['ctest', '--output-on-failure']
            
            result = subprocess.run(
                cmd,
                cwd=str(build_path),
                capture_output=True,
                text=True,
                timeout=self._timeout
            )
            
            return self._build_success_result(
                "Tests executed",
                data={
                    'exit_code': result.returncode,
                    'passed': result.returncode == 0,
                    'output': result.stdout,
                    'errors': result.stderr
                }
            )
            
        except subprocess.TimeoutExpired:
            return self._build_error_result("Test execution timed out")
        except FileNotFoundError:
            return self._build_error_result("CTest not found")
        except Exception as e:
            return self._build_error_result(f"Test execution failed: {str(e)}", error=e)
    
    def _llm_assisted_build(self, task: str, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to assist with build task."""
        detection = self._detect_build_system(project_dir)
        build_system = detection['data'].get('build_system', 'unknown') if detection['success'] else 'unknown'
        
        prompt = f"""You are a CPP build system expert. Help with this build task:

Task: {task}

Project Directory: {project_dir}
Build System: {build_system}
Context: {json.dumps(context, indent=2)}

Provide:
1. Understanding of the build task
2. Recommended build commands (CMake, Make, etc.)
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
