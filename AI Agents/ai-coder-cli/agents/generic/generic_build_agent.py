

"""
Generic Build Agent

Fallback build agent for unsupported languages using LLM-based approaches.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List

from ..base import BuildAgentBase


class GenericBuildAgent(BuildAgentBase):
    """
    Generic build agent for any language/build system.
    
    This agent provides fallback functionality for build systems that don't
    have specific implementations. It uses LLM to understand and suggest
    build processes.
    """
    
    def __init__(
        self,
        name: str = "build_generic",
        description: str = "Generic build agent for any language",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            supported_build_systems=['generic', 'makefile', 'custom'],
            **kwargs
        )
    
    def _detect_build_system(self, project_dir: str) -> Dict[str, Any]:
        """
        Detect build system by scanning for common build files.
        """
        project_path = Path(project_dir)
        detected_systems = []
        
        # Common build files across languages
        build_files = {
            'Makefile': 'make',
            'makefile': 'make',
            'CMakeLists.txt': 'cmake',
            'build.gradle': 'gradle',
            'pom.xml': 'maven',
            'package.json': 'npm',
            'Cargo.toml': 'cargo',
            'go.mod': 'go',
            'build.xml': 'ant',
            'Rakefile': 'rake',
        }
        
        for build_file, system in build_files.items():
            if (project_path / build_file).exists():
                detected_systems.append(system)
        
        if not detected_systems:
            return self._build_error_result(
                "No build system detected. Manual build commands may be required."
            )
        
        primary_system = detected_systems[0]
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
        """
        Install dependencies using LLM guidance.
        """
        # Detect build system first
        detection = self._detect_build_system(project_dir)
        if not detection['success']:
            return self._build_error_result(
                "Cannot install dependencies without detected build system. "
                "Please specify dependency installation commands manually."
            )
        
        build_system = detection['data']['build_system']
        
        # Common dependency commands
        dependency_commands = {
            'npm': ['npm', 'install'],
            'make': ['make', 'deps'],
            'cmake': ['cmake', '.'],
            'gradle': ['gradle', 'dependencies'],
            'maven': ['mvn', 'dependency:resolve'],
            'cargo': ['cargo', 'build'],
            'go': ['go', 'mod', 'download'],
        }
        
        cmd = dependency_commands.get(build_system)
        
        if not cmd:
            return self._build_error_result(
                f"No default dependency command for {build_system}. "
                "Please specify manually."
            )
        
        try:
            result = self._run_command(cmd, project_dir)
            
            if result.returncode == 0:
                return self._build_success_result(
                    f"Dependencies installed using {build_system}",
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
        except FileNotFoundError:
            return self._build_error_result(f"Build tool not found: {cmd[0]}")
        except Exception as e:
            return self._build_error_result(f"Dependency installation failed: {str(e)}", error=e)
    
    def _build_package(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build package using detected build system.
        """
        detection = self._detect_build_system(project_dir)
        if not detection['success']:
            return self._build_error_result(
                "Cannot build without detected build system. "
                "Please specify build commands manually."
            )
        
        build_system = detection['data']['build_system']
        
        # Common build commands
        build_commands = {
            'make': ['make'],
            'cmake': ['cmake', '--build', '.'],
            'gradle': ['gradle', 'build'],
            'maven': ['mvn', 'package'],
            'npm': ['npm', 'run', 'build'],
            'cargo': ['cargo', 'build'],
            'go': ['go', 'build'],
        }
        
        cmd = build_commands.get(build_system)
        
        if not cmd:
            return self._build_error_result(
                f"No default build command for {build_system}. "
                "Please specify manually."
            )
        
        try:
            result = self._run_command(cmd, project_dir)
            
            if result.returncode == 0:
                return self._build_success_result(
                    f"Package built using {build_system}",
                    data={
                        'build_system': build_system,
                        'output': result.stdout,
                        'command': ' '.join(cmd)
                    }
                )
            else:
                return self._build_error_result(
                    f"Build failed: {result.stderr}",
                    data={'output': result.stderr, 'command': ' '.join(cmd)}
                )
        except subprocess.TimeoutExpired:
            return self._build_error_result("Build timed out")
        except FileNotFoundError:
            return self._build_error_result(f"Build tool not found: {cmd[0]}")
        except Exception as e:
            return self._build_error_result(f"Build failed: {str(e)}", error=e)
