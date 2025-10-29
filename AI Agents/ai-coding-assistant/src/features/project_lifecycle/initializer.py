"""
Project Initialization System

Handles post-scaffolding initialization: virtual environments, git setup,
dependency detection, and optional wizard for interactive project setup.
Follows Zero-Bloat principles by keeping initialization separate from scaffolding.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ProjectInitializer:
    """
    Initializes projects after scaffolding with zero bloat.
    
    Responsibilities:
    - Detect project type and dependencies
    - Create virtual environments (Python, Node, .NET)
    - Initialize git repositories
    - Generate documentation (README, LICENSE)
    
    Does NOT:
    - Manage templates (TemplateManager does this)
    - Create files (ProjectScaffolder does this)
    - Execute arbitrary commands (security risk)
    
    Example:
        >>> from src.features.project_lifecycle import ProjectInitializer
        >>> 
        >>> initializer = ProjectInitializer()
        >>> 
        >>> # Detect project type
        >>> project_type = initializer.detect_project_type(Path("./my-app"))
        >>> 
        >>> # Initialize git
        >>> success, msg = initializer.initialize_git(
        ...     Path("./my-app"),
        ...     "Initial commit"
        ... )
    """
    
    # License templates (basic versions)
    LICENSES = {
        "MIT": """MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""",
        
        "Apache-2.0": """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Copyright {year} {author}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.""",
        
        "GPL-3.0": """GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) {year} {author}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>."""
    }
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the project initializer.
        
        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
    
    def detect_project_type(self, path: Path) -> Optional[str]:
        """
        Detect project type based on files present.
        
        Args:
            path: Project directory path
        
        Returns:
            Project type: 'python', 'node', 'dotnet', or None
        
        Example:
            >>> initializer = ProjectInitializer()
            >>> project_type = initializer.detect_project_type(Path("./my-app"))
            >>> print(project_type)  # 'python', 'node', 'dotnet', or None
        """
        if not path.exists():
            return None
        
        # Python indicators
        if (path / "requirements.txt").exists() or \
           (path / "setup.py").exists() or \
           (path / "pyproject.toml").exists():
            return "python"
        
        # Node indicators
        if (path / "package.json").exists():
            return "node"
        
        # .NET indicators
        if list(path.glob("*.csproj")) or \
           list(path.glob("*.sln")):
            return "dotnet"
        
        return None
    
    def detect_dependencies(self, path: Path) -> List[str]:
        """
        Detect dependencies that need to be installed.
        
        Args:
            path: Project directory path
        
        Returns:
            List of dependency file paths found
        
        Example:
            >>> deps = initializer.detect_dependencies(Path("./my-app"))
            >>> print(deps)  # ['requirements.txt', 'package.json']
        """
        dependencies = []
        
        # Python
        if (path / "requirements.txt").exists():
            dependencies.append("requirements.txt")
        if (path / "requirements-dev.txt").exists():
            dependencies.append("requirements-dev.txt")
        
        # Node
        if (path / "package.json").exists():
            dependencies.append("package.json")
        
        # .NET
        if list(path.glob("*.csproj")):
            dependencies.append("*.csproj")
        
        return dependencies
    
    def initialize_git(
        self,
        path: Path,
        initial_message: str = "Initial commit",
        add_gitignore: bool = True
    ) -> Tuple[bool, str]:
        """
        Initialize git repository.
        
        Args:
            path: Project directory path
            initial_message: Initial commit message
            add_gitignore: Whether to create .gitignore if missing
        
        Returns:
            Tuple of (success: bool, message: str)
        
        Example:
            >>> success, msg = initializer.initialize_git(
            ...     Path("./my-app"),
            ...     "Initial commit from template"
            ... )
        """
        try:
            if not path.exists():
                return False, f"Path {path} does not exist"
            
            # Check if git is available
            try:
                subprocess.run(
                    ["git", "--version"],
                    check=True,
                    capture_output=True,
                    timeout=5
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False, "Git is not installed or not in PATH"
            
            # Initialize git
            result = subprocess.run(
                ["git", "init"],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False, f"Git init failed: {result.stderr}"
            
            # Create basic .gitignore if requested and missing
            if add_gitignore and not (path / ".gitignore").exists():
                self._create_default_gitignore(path)
            
            # Add all files
            subprocess.run(
                ["git", "add", "."],
                cwd=path,
                capture_output=True,
                timeout=10
            )
            
            # Initial commit
            subprocess.run(
                ["git", "commit", "-m", initial_message],
                cwd=path,
                capture_output=True,
                timeout=10
            )
            
            if self.verbose:
                logger.info(f"Git initialized in {path}")
            
            return True, f"Git repository initialized in {path}"
            
        except subprocess.TimeoutExpired:
            return False, "Git command timed out"
        except Exception as e:
            logger.error(f"Git initialization failed: {e}")
            return False, f"Git initialization failed: {str(e)}"
    
    def create_virtual_env(
        self,
        path: Path,
        env_type: str = "venv",
        python_version: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Create Python virtual environment.
        
        Args:
            path: Project directory path
            env_type: Type of environment ('venv', 'virtualenv', 'conda')
            python_version: Specific Python version (for conda)
        
        Returns:
            Tuple of (success: bool, message: str)
        
        Example:
            >>> success, msg = initializer.create_virtual_env(
            ...     Path("./my-app"),
            ...     env_type="venv"
            ... )
        """
        try:
            if not path.exists():
                return False, f"Path {path} does not exist"
            
            project_type = self.detect_project_type(path)
            if project_type != "python":
                return False, "Not a Python project"
            
            venv_path = path / "venv"
            
            if env_type == "venv":
                # Use built-in venv
                result = subprocess.run(
                    [sys.executable, "-m", "venv", "venv"],
                    cwd=path,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    return False, f"venv creation failed: {result.stderr}"
                
                return True, f"Virtual environment created at {venv_path}"
            
            elif env_type == "virtualenv":
                # Use virtualenv package
                result = subprocess.run(
                    ["virtualenv", "venv"],
                    cwd=path,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    return False, f"virtualenv creation failed: {result.stderr}"
                
                return True, f"Virtual environment created at {venv_path}"
            
            elif env_type == "conda":
                # Use conda
                env_name = path.name
                cmd = ["conda", "create", "-n", env_name, "-y"]
                if python_version:
                    cmd.append(f"python={python_version}")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode != 0:
                    return False, f"conda env creation failed: {result.stderr}"
                
                return True, f"Conda environment '{env_name}' created"
            
            else:
                return False, f"Unknown environment type: {env_type}"
            
        except subprocess.TimeoutExpired:
            return False, "Virtual environment creation timed out"
        except FileNotFoundError:
            return False, f"{env_type} is not installed or not in PATH"
        except Exception as e:
            logger.error(f"Virtual environment creation failed: {e}")
            return False, f"Virtual environment creation failed: {str(e)}"
    
    def select_license(self, license_type: str = "MIT") -> Optional[str]:
        """
        Get license text by type.
        
        Args:
            license_type: License type ('MIT', 'Apache-2.0', 'GPL-3.0')
        
        Returns:
            License text or None if not found
        
        Example:
            >>> license_text = initializer.select_license("MIT")
            >>> print(license_text[:50])  # First 50 chars
        """
        return self.LICENSES.get(license_type)
    
    def generate_license_file(
        self,
        path: Path,
        license_type: str = "MIT",
        author: str = "",
        year: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Generate LICENSE file.
        
        Args:
            path: Project directory path
            license_type: License type
            author: Author name
            year: Copyright year (defaults to current year)
        
        Returns:
            Tuple of (success: bool, message: str)
        
        Example:
            >>> success, msg = initializer.generate_license_file(
            ...     Path("./my-app"),
            ...     license_type="MIT",
            ...     author="John Doe"
            ... )
        """
        try:
            license_text = self.select_license(license_type)
            if not license_text:
                return False, f"Unknown license type: {license_type}"
            
            if year is None:
                from datetime import datetime
                year = datetime.now().year
            
            # Replace placeholders
            license_text = license_text.replace("{year}", str(year))
            license_text = license_text.replace("{author}", author)
            
            # Write LICENSE file
            license_path = path / "LICENSE"
            license_path.write_text(license_text, encoding='utf-8')
            
            if self.verbose:
                logger.info(f"LICENSE file created: {license_path}")
            
            return True, f"LICENSE file created with {license_type} license"
            
        except Exception as e:
            logger.error(f"License file creation failed: {e}")
            return False, f"License file creation failed: {str(e)}"
    
    def generate_readme(
        self,
        path: Path,
        info: Dict[str, Any],
        overwrite: bool = False
    ) -> Tuple[bool, str]:
        """
        Generate or enhance README.md file.
        
        Args:
            path: Project directory path
            info: Project information dictionary
            overwrite: Whether to overwrite existing README
        
        Returns:
            Tuple of (success: bool, message: str)
        
        Example:
            >>> info = {
            ...     "name": "My Project",
            ...     "description": "A great project",
            ...     "author": "John Doe"
            ... }
            >>> success, msg = initializer.generate_readme(Path("./my-app"), info)
        """
        try:
            readme_path = path / "README.md"
            
            if readme_path.exists() and not overwrite:
                return True, "README.md already exists (use overwrite=True to replace)"
            
            # Build README content
            content = self._build_readme_content(info)
            
            # Write README
            readme_path.write_text(content, encoding='utf-8')
            
            if self.verbose:
                logger.info(f"README.md created: {readme_path}")
            
            action = "updated" if (readme_path.exists() and overwrite) else "created"
            return True, f"README.md {action}"
            
        except Exception as e:
            logger.error(f"README generation failed: {e}")
            return False, f"README generation failed: {str(e)}"
    
    def get_setup_instructions(self, path: Path) -> List[str]:
        """
        Get setup instructions for the project.
        
        Args:
            path: Project directory path
        
        Returns:
            List of setup instruction strings
        
        Example:
            >>> instructions = initializer.get_setup_instructions(Path("./my-app"))
            >>> for instruction in instructions:
            ...     print(instruction)
        """
        instructions = []
        project_type = self.detect_project_type(path)
        
        if project_type == "python":
            instructions.extend([
                "# Python Project Setup",
                "1. Create virtual environment:",
                "   python -m venv venv",
                "2. Activate virtual environment:",
                "   - Windows: venv\\Scripts\\activate",
                "   - Linux/macOS: source venv/bin/activate",
                "3. Install dependencies:",
                "   pip install -r requirements.txt"
            ])
        
        elif project_type == "node":
            instructions.extend([
                "# Node.js Project Setup",
                "1. Install dependencies:",
                "   npm install",
                "   # or: yarn install",
                "   # or: pnpm install",
                "2. Run development server:",
                "   npm run dev"
            ])
        
        elif project_type == "dotnet":
            instructions.extend([
                "# .NET Project Setup",
                "1. Restore packages:",
                "   dotnet restore",
                "2. Build project:",
                "   dotnet build",
                "3. Run project:",
                "   dotnet run"
            ])
        
        # Git setup
        if not (path / ".git").exists():
            instructions.extend([
                "",
                "# Git Setup",
                "git init",
                "git add .",
                "git commit -m 'Initial commit'"
            ])
        
        return instructions
    
    # Private methods
    
    def _create_default_gitignore(self, path: Path) -> None:
        """Create a basic .gitignore file."""
        project_type = self.detect_project_type(path)
        
        gitignore_content = []
        
        if project_type == "python":
            gitignore_content = [
                "# Python",
                "__pycache__/",
                "*.py[cod]",
                "*.so",
                ".Python",
                "venv/",
                "env/",
                "*.egg-info/",
                ".pytest_cache/",
                ".coverage",
                "",
                "# IDEs",
                ".vscode/",
                ".idea/",
                "*.swp",
                ".DS_Store"
            ]
        elif project_type == "node":
            gitignore_content = [
                "# Node",
                "node_modules/",
                "dist/",
                "build/",
                "*.log",
                ".env",
                "",
                "# IDEs",
                ".vscode/",
                ".idea/",
                ".DS_Store"
            ]
        elif project_type == "dotnet":
            gitignore_content = [
                "# .NET",
                "bin/",
                "obj/",
                "*.user",
                "*.suo",
                ".vs/",
                "",
                "# IDEs",
                ".vscode/",
                ".idea/",
                ".DS_Store"
            ]
        else:
            gitignore_content = [
                "# General",
                ".DS_Store",
                "*.log",
                "*.tmp",
                "",
                "# IDEs",
                ".vscode/",
                ".idea/"
            ]
        
        gitignore_path = path / ".gitignore"
        gitignore_path.write_text("\n".join(gitignore_content), encoding='utf-8')
    
    def _build_readme_content(self, info: Dict[str, Any]) -> str:
        """Build README.md content from info."""
        name = info.get("name", "Project")
        description = info.get("description", "")
        author = info.get("author", "")
        
        content = [
            f"# {name}",
            "",
        ]
        
        if description:
            content.extend([description, ""])
        
        content.extend([
            "## Installation",
            "",
            "```bash",
            "# Installation instructions here",
            "```",
            "",
            "## Usage",
            "",
            "```bash",
            "# Usage examples here",
            "```",
            ""
        ])
        
        if author:
            content.extend([
                "## Author",
                "",
                author,
                ""
            ])
        
        return "\n".join(content)


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    initializer = ProjectInitializer(verbose=True)
    
    # Example: Detect project type
    print("Example 1: Detect project type")
    print("-" * 60)
    test_path = Path("./test-project")
    project_type = initializer.detect_project_type(test_path)
    print(f"Project type: {project_type}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Example: Get setup instructions
    print("Example 2: Get setup instructions")
    print("-" * 60)
    if test_path.exists():
        instructions = initializer.get_setup_instructions(test_path)
        for instruction in instructions:
            print(instruction)
