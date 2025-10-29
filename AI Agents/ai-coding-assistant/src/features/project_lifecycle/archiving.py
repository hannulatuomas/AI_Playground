"""
Project Archiving System

Handles project archiving and distribution preparation: documentation generation,
archive creation, changelog generation, and version management.
Follows Zero-Bloat principles by focusing on archiving and distribution only.
"""

import os
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import json
import re
import logging

logger = logging.getLogger(__name__)


class ProjectArchiver:
    """
    Archives projects for distribution and backup.
    
    Responsibilities:
    - Generate comprehensive project documentation
    - Create archives (zip, tar.gz)
    - Generate changelogs from git history
    - Generate release notes
    - Version bumping
    
    Does NOT:
    - Modify source code (version bumping updates metadata only)
    - Deploy or publish (user does this)
    - Manage git (only reads history)
    
    Example:
        >>> from src.features.project_lifecycle import ProjectArchiver
        >>> 
        >>> archiver = ProjectArchiver()
        >>> 
        >>> # Create archive
        >>> archive_path = archiver.create_archive(
        ...     Path("./my-project"),
        ...     format="zip"
        ... )
        >>> 
        >>> # Generate changelog
        >>> changelog = archiver.generate_changelog(
        ...     Path("./my-project"),
        ...     from_tag="v1.0.0"
        ... )
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the project archiver.
        
        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
    
    def generate_full_docs(
        self,
        project_path: Path,
        output_path: Optional[Path] = None
    ) -> Tuple[bool, str]:
        """
        Generate comprehensive project documentation.
        
        Args:
            project_path: Project directory path
            output_path: Output directory (defaults to project_path/docs)
        
        Returns:
            Tuple of (success: bool, message: str)
        
        Example:
            >>> success, msg = archiver.generate_full_docs(Path("./my-project"))
        """
        if not project_path.exists():
            return False, f"Project path {project_path} does not exist"
        
        if output_path is None:
            output_path = project_path / "docs"
        
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate API documentation index
            api_doc_path = output_path / "API.md"
            self._generate_api_doc(project_path, api_doc_path)
            
            # Generate project structure documentation
            structure_path = output_path / "PROJECT_STRUCTURE.md"
            self._generate_structure_doc(project_path, structure_path)
            
            # Generate usage guide
            usage_path = output_path / "USAGE.md"
            self._generate_usage_doc(project_path, usage_path)
            
            if self.verbose:
                logger.info(f"Documentation generated in {output_path}")
            
            return True, f"Documentation generated in {output_path}"
            
        except Exception as e:
            logger.error(f"Documentation generation failed: {e}")
            return False, f"Documentation generation failed: {str(e)}"
    
    def create_archive(
        self,
        project_path: Path,
        format: str = "zip",
        output_dir: Optional[Path] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[Path], str]:
        """
        Create project archive.
        
        Args:
            project_path: Project directory path
            format: Archive format ('zip' or 'tar.gz')
            output_dir: Output directory (defaults to parent of project_path)
            exclude_patterns: Patterns to exclude (e.g., ['*.pyc', '__pycache__'])
        
        Returns:
            Tuple of (success: bool, archive_path: Optional[Path], message: str)
        
        Example:
            >>> success, path, msg = archiver.create_archive(
            ...     Path("./my-project"),
            ...     format="zip"
            ... )
        """
        if not project_path.exists():
            return False, None, f"Project path {project_path} does not exist"
        
        if output_dir is None:
            output_dir = project_path.parent
        
        # Default exclusions
        if exclude_patterns is None:
            exclude_patterns = [
                '__pycache__',
                '*.pyc',
                '*.pyo',
                '.git',
                '.gitignore',
                'node_modules',
                'venv',
                'env',
                '.venv',
                'dist',
                'build',
                '*.egg-info',
                '.pytest_cache',
                '.coverage',
                '.DS_Store'
            ]
        
        try:
            project_name = project_path.name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format == "zip":
                archive_name = f"{project_name}_{timestamp}.zip"
                archive_path = output_dir / archive_name
                
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    self._add_to_zip(zipf, project_path, project_path, exclude_patterns)
                
            elif format == "tar.gz":
                archive_name = f"{project_name}_{timestamp}.tar.gz"
                archive_path = output_dir / archive_name
                
                with tarfile.open(archive_path, 'w:gz') as tarf:
                    self._add_to_tar(tarf, project_path, project_path, exclude_patterns)
            
            else:
                return False, None, f"Unsupported format: {format}"
            
            if self.verbose:
                logger.info(f"Archive created: {archive_path}")
            
            return True, archive_path, f"Archive created: {archive_path}"
            
        except Exception as e:
            logger.error(f"Archive creation failed: {e}")
            return False, None, f"Archive creation failed: {str(e)}"
    
    def generate_changelog(
        self,
        project_path: Path,
        from_tag: Optional[str] = None,
        to_tag: str = "HEAD",
        output_file: Optional[Path] = None
    ) -> Tuple[bool, str]:
        """
        Generate changelog from git history.
        
        Args:
            project_path: Project directory path
            from_tag: Starting git tag (if None, uses all history)
            to_tag: Ending git tag or commit
            output_file: Output file path (defaults to project_path/CHANGELOG.md)
        
        Returns:
            Tuple of (success: bool, message: str)
        
        Example:
            >>> success, msg = archiver.generate_changelog(
            ...     Path("./my-project"),
            ...     from_tag="v1.0.0"
            ... )
        """
        if not project_path.exists():
            return False, f"Project path {project_path} does not exist"
        
        # Check if git repo
        if not (project_path / ".git").exists():
            return False, "Not a git repository"
        
        if output_file is None:
            output_file = project_path / "CHANGELOG.md"
        
        try:
            # Get git log
            if from_tag:
                range_spec = f"{from_tag}..{to_tag}"
            else:
                range_spec = to_tag
            
            result = subprocess.run(
                ["git", "log", range_spec, "--pretty=format:%H|%h|%s|%an|%ad", "--date=short"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return False, f"Git log failed: {result.stderr}"
            
            # Parse commits
            commits = []
            for line in result.stdout.splitlines():
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 5:
                        commits.append({
                            'hash': parts[0],
                            'short_hash': parts[1],
                            'subject': parts[2],
                            'author': parts[3],
                            'date': parts[4]
                        })
            
            # Generate changelog content
            changelog = self._format_changelog(commits, from_tag, to_tag)
            
            # Write changelog
            output_file.write_text(changelog, encoding='utf-8')
            
            if self.verbose:
                logger.info(f"Changelog generated: {output_file}")
            
            return True, f"Changelog generated: {output_file}"
            
        except subprocess.TimeoutExpired:
            return False, "Git command timed out"
        except FileNotFoundError:
            return False, "Git not found"
        except Exception as e:
            logger.error(f"Changelog generation failed: {e}")
            return False, f"Changelog generation failed: {str(e)}"
    
    def generate_release_notes(
        self,
        project_path: Path,
        version: str,
        highlights: Optional[List[str]] = None,
        output_file: Optional[Path] = None
    ) -> Tuple[bool, str]:
        """
        Generate release notes for a version.
        
        Args:
            project_path: Project directory path
            version: Version number (e.g., "1.0.0")
            highlights: Key highlights for this release
            output_file: Output file path (defaults to project_path/RELEASE_NOTES.md)
        
        Returns:
            Tuple of (success: bool, message: str)
        
        Example:
            >>> success, msg = archiver.generate_release_notes(
            ...     Path("./my-project"),
            ...     version="1.2.0",
            ...     highlights=["New feature X", "Bug fix Y"]
            ... )
        """
        if not project_path.exists():
            return False, f"Project path {project_path} does not exist"
        
        if output_file is None:
            output_file = project_path / "RELEASE_NOTES.md"
        
        try:
            # Build release notes
            notes = [
                f"# Release Notes - Version {version}",
                "",
                f"**Release Date**: {datetime.now().strftime('%Y-%m-%d')}",
                ""
            ]
            
            if highlights:
                notes.extend([
                    "## Highlights",
                    ""
                ])
                for highlight in highlights:
                    notes.append(f"- {highlight}")
                notes.append("")
            
            # Try to get recent commits
            if (project_path / ".git").exists():
                try:
                    result = subprocess.run(
                        ["git", "log", "--pretty=format:%s", "-10"],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0 and result.stdout:
                        notes.extend([
                            "## Recent Changes",
                            ""
                        ])
                        for commit_msg in result.stdout.splitlines():
                            if commit_msg.strip():
                                notes.append(f"- {commit_msg.strip()}")
                        notes.append("")
                except:
                    pass  # Silently skip if git fails
            
            # Installation/upgrade section
            notes.extend([
                "## Installation",
                "",
                "See the README.md for installation instructions.",
                ""
            ])
            
            # Write release notes
            output_file.write_text("\n".join(notes), encoding='utf-8')
            
            if self.verbose:
                logger.info(f"Release notes generated: {output_file}")
            
            return True, f"Release notes generated: {output_file}"
            
        except Exception as e:
            logger.error(f"Release notes generation failed: {e}")
            return False, f"Release notes generation failed: {str(e)}"
    
    def bump_version(
        self,
        project_path: Path,
        bump_type: str = "patch",
        current_version: Optional[str] = None
    ) -> Tuple[bool, Optional[str], str]:
        """
        Bump project version.
        
        Args:
            project_path: Project directory path
            bump_type: Type of bump ('major', 'minor', 'patch')
            current_version: Current version (auto-detected if None)
        
        Returns:
            Tuple of (success: bool, new_version: Optional[str], message: str)
        
        Example:
            >>> success, new_ver, msg = archiver.bump_version(
            ...     Path("./my-project"),
            ...     bump_type="minor"
            ... )
        """
        if not project_path.exists():
            return False, None, f"Project path {project_path} does not exist"
        
        if bump_type not in ['major', 'minor', 'patch']:
            return False, None, f"Invalid bump type: {bump_type}"
        
        try:
            # Detect current version if not provided
            if current_version is None:
                current_version = self._detect_version(project_path)
            
            if current_version is None:
                return False, None, "Could not detect current version"
            
            # Parse version
            match = re.match(r'(\d+)\.(\d+)\.(\d+)', current_version)
            if not match:
                return False, None, f"Invalid version format: {current_version}"
            
            major, minor, patch = map(int, match.groups())
            
            # Bump version
            if bump_type == 'major':
                major += 1
                minor = 0
                patch = 0
            elif bump_type == 'minor':
                minor += 1
                patch = 0
            else:  # patch
                patch += 1
            
            new_version = f"{major}.{minor}.{patch}"
            
            # Update version in files
            updated_files = self._update_version_in_files(project_path, current_version, new_version)
            
            if self.verbose:
                logger.info(f"Version bumped: {current_version} -> {new_version}")
                logger.info(f"Updated files: {', '.join(str(f) for f in updated_files)}")
            
            message = f"Version bumped: {current_version} -> {new_version}"
            if updated_files:
                message += f"\nUpdated {len(updated_files)} file(s)"
            
            return True, new_version, message
            
        except Exception as e:
            logger.error(f"Version bump failed: {e}")
            return False, None, f"Version bump failed: {str(e)}"
    
    # Private methods
    
    def _generate_api_doc(self, project_path: Path, output_path: Path) -> None:
        """Generate API documentation."""
        content = [
            "# API Documentation",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Overview",
            "",
            "This document provides API reference for the project.",
            "",
            "## Modules",
            "",
            "### Main Module",
            "",
            "Documentation for main functionality.",
            ""
        ]
        
        output_path.write_text("\n".join(content), encoding='utf-8')
    
    def _generate_structure_doc(self, project_path: Path, output_path: Path) -> None:
        """Generate project structure documentation."""
        content = [
            "# Project Structure",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Directory Layout",
            "",
            "```",
        ]
        
        # Add directory tree
        for root, dirs, files in os.walk(project_path):
            # Skip common exclude dirs
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 'venv']]
            
            level = root.replace(str(project_path), '').count(os.sep)
            indent = '  ' * level
            content.append(f"{indent}{Path(root).name}/")
            
            sub_indent = '  ' * (level + 1)
            for file in files[:10]:  # Limit files shown
                content.append(f"{sub_indent}{file}")
        
        content.extend([
            "```",
            ""
        ])
        
        output_path.write_text("\n".join(content), encoding='utf-8')
    
    def _generate_usage_doc(self, project_path: Path, output_path: Path) -> None:
        """Generate usage documentation."""
        content = [
            "# Usage Guide",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Getting Started",
            "",
            "Instructions for using this project.",
            "",
            "## Basic Usage",
            "",
            "```python",
            "# Example usage",
            "```",
            ""
        ]
        
        output_path.write_text("\n".join(content), encoding='utf-8')
    
    def _should_exclude(self, path: Path, base: Path, patterns: List[str]) -> bool:
        """Check if path should be excluded."""
        rel_path = path.relative_to(base)
        path_str = str(rel_path)
        
        for pattern in patterns:
            if pattern.startswith('*'):
                if path_str.endswith(pattern[1:]):
                    return True
            elif pattern in path_str:
                return True
        
        return False
    
    def _add_to_zip(self, zipf: zipfile.ZipFile, path: Path, base: Path, exclude: List[str]) -> None:
        """Recursively add files to zip."""
        for item in path.iterdir():
            if self._should_exclude(item, base, exclude):
                continue
            
            arcname = str(item.relative_to(base.parent))
            
            if item.is_file():
                zipf.write(item, arcname)
            elif item.is_dir():
                self._add_to_zip(zipf, item, base, exclude)
    
    def _add_to_tar(self, tarf: tarfile.TarFile, path: Path, base: Path, exclude: List[str]) -> None:
        """Recursively add files to tar."""
        for item in path.iterdir():
            if self._should_exclude(item, base, exclude):
                continue
            
            arcname = str(item.relative_to(base.parent))
            tarf.add(item, arcname=arcname, recursive=False)
            
            if item.is_dir():
                self._add_to_tar(tarf, item, base, exclude)
    
    def _format_changelog(self, commits: List[Dict], from_tag: Optional[str], to_tag: str) -> str:
        """Format commits into changelog."""
        lines = [
            "# Changelog",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
            ""
        ]
        
        if from_tag:
            lines.append(f"## Changes from {from_tag} to {to_tag}")
        else:
            lines.append(f"## All Changes")
        
        lines.append("")
        
        for commit in commits:
            lines.append(f"- **{commit['date']}**: {commit['subject']} ({commit['short_hash']})")
        
        lines.append("")
        
        return "\n".join(lines)
    
    def _detect_version(self, project_path: Path) -> Optional[str]:
        """Detect current version from project files."""
        # Check package.json
        package_json = project_path / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                if 'version' in data:
                    return data['version']
            except:
                pass
        
        # Check setup.py
        setup_py = project_path / "setup.py"
        if setup_py.exists():
            try:
                content = setup_py.read_text()
                match = re.search(r'version\s*=\s*["\']([0-9.]+)["\']', content)
                if match:
                    return match.group(1)
            except:
                pass
        
        # Check pyproject.toml
        pyproject = project_path / "pyproject.toml"
        if pyproject.exists():
            try:
                content = pyproject.read_text()
                match = re.search(r'version\s*=\s*["\']([0-9.]+)["\']', content)
                if match:
                    return match.group(1)
            except:
                pass
        
        return None
    
    def _update_version_in_files(self, project_path: Path, old_version: str, new_version: str) -> List[Path]:
        """Update version in project files."""
        updated = []
        
        # Update package.json
        package_json = project_path / "package.json"
        if package_json.exists():
            try:
                content = package_json.read_text()
                new_content = content.replace(
                    f'"version": "{old_version}"',
                    f'"version": "{new_version}"'
                )
                if new_content != content:
                    package_json.write_text(new_content)
                    updated.append(package_json)
            except:
                pass
        
        # Update setup.py
        setup_py = project_path / "setup.py"
        if setup_py.exists():
            try:
                content = setup_py.read_text()
                new_content = re.sub(
                    r'version\s*=\s*["\']' + re.escape(old_version) + r'["\']',
                    f'version="{new_version}"',
                    content
                )
                if new_content != content:
                    setup_py.write_text(new_content)
                    updated.append(setup_py)
            except:
                pass
        
        # Update pyproject.toml
        pyproject = project_path / "pyproject.toml"
        if pyproject.exists():
            try:
                content = pyproject.read_text()
                new_content = re.sub(
                    r'version\s*=\s*["\']' + re.escape(old_version) + r'["\']',
                    f'version = "{new_version}"',
                    content
                )
                if new_content != content:
                    pyproject.write_text(new_content)
                    updated.append(pyproject)
            except:
                pass
        
        return updated


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    archiver = ProjectArchiver(verbose=True)
    
    # Example: Create archive
    print("Example: Create Project Archive")
    print("-" * 60)
    
    test_path = Path("./test-project")
    if test_path.exists():
        success, archive_path, msg = archiver.create_archive(test_path, format="zip")
        print(f"Result: {msg}")
