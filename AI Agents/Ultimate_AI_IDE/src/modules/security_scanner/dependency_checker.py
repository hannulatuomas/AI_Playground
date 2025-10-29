"""
Dependency Checker

Analyzes project dependencies for security and health issues.
"""

import logging
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from .scanner import SecurityIssue

logger = logging.getLogger(__name__)


@dataclass
class DependencyInfo:
    """Information about a dependency"""
    name: str
    current_version: str
    latest_version: Optional[str] = None
    is_outdated: bool = False
    age_days: Optional[int] = None
    license: Optional[str] = None
    has_security_issues: bool = False
    transitive: bool = False


class DependencyChecker:
    """
    Checks project dependencies for security and health issues.
    
    Analyzes:
    - Outdated dependencies
    - License compliance
    - Dependency health
    - Transitive dependency risks
    - Malicious packages
    """
    
    def __init__(self):
        """Initialize dependency checker"""
        self.dependencies: Dict[str, DependencyInfo] = {}
    
    def check(self, project_path: Path) -> List[SecurityIssue]:
        """
        Check project dependencies.
        
        Args:
            project_path: Path to project root
            
        Returns:
            List of dependency-related security issues
        """
        issues = []
        
        try:
            # Check Python dependencies
            if (project_path / "requirements.txt").exists():
                issues.extend(self._check_python_deps(project_path))
            
            # Check Node.js dependencies
            if (project_path / "package.json").exists():
                issues.extend(self._check_nodejs_deps(project_path))
            
            # Check .NET dependencies
            if list(project_path.glob("*.csproj")):
                issues.extend(self._check_dotnet_deps(project_path))
            
            logger.info(f"Dependency check found {len(issues)} issues")
            return issues
            
        except Exception as e:
            logger.error(f"Error during dependency check: {e}")
            return issues
    
    def _check_python_deps(self, project_path: Path) -> List[SecurityIssue]:
        """Check Python dependencies"""
        issues = []
        
        try:
            # Check for outdated packages
            result = subprocess.run(
                ['pip', 'list', '--outdated', '--format', 'json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                outdated = json.loads(result.stdout)
                
                for pkg in outdated:
                    issue = SecurityIssue(
                        severity='medium',
                        category='dependency',
                        title=f"Outdated package: {pkg['name']}",
                        description=f"Version {pkg['version']} is outdated. Latest: {pkg['latest_version']}",
                        fix_available=True,
                        fix_description=f"Update to version {pkg['latest_version']}"
                    )
                    issues.append(issue)
            
            # Check for packages with known issues
            issues.extend(self._check_python_licenses(project_path))
            
        except Exception as e:
            logger.warning(f"Python dependency check failed: {e}")
        
        return issues
    
    def _check_python_licenses(self, project_path: Path) -> List[SecurityIssue]:
        """Check Python package licenses"""
        issues = []
        
        # List of problematic licenses
        problematic_licenses = ['GPL', 'AGPL', 'SSPL']
        
        try:
            result = subprocess.run(
                ['pip-licenses', '--format', 'json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                licenses = json.loads(result.stdout)
                
                for pkg in licenses:
                    license_name = pkg.get('License', '')
                    if any(prob in license_name for prob in problematic_licenses):
                        issue = SecurityIssue(
                            severity='low',
                            category='dependency',
                            title=f"License concern: {pkg['Name']}",
                            description=f"Package uses {license_name} license which may have restrictions",
                            fix_available=False,
                            fix_description="Review license compatibility with your project"
                        )
                        issues.append(issue)
        
        except FileNotFoundError:
            logger.debug("pip-licenses not installed")
        except Exception as e:
            logger.warning(f"License check failed: {e}")
        
        return issues
    
    def _check_nodejs_deps(self, project_path: Path) -> List[SecurityIssue]:
        """Check Node.js dependencies"""
        issues = []
        
        try:
            # Check for outdated packages
            result = subprocess.run(
                ['npm', 'outdated', '--json'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                try:
                    outdated = json.loads(result.stdout)
                    
                    for pkg_name, pkg_info in outdated.items():
                        current = pkg_info.get('current', 'unknown')
                        latest = pkg_info.get('latest', 'unknown')
                        
                        issue = SecurityIssue(
                            severity='medium',
                            category='dependency',
                            title=f"Outdated npm package: {pkg_name}",
                            description=f"Version {current} is outdated. Latest: {latest}",
                            fix_available=True,
                            fix_description=f"Run 'npm update {pkg_name}'"
                        )
                        issues.append(issue)
                except json.JSONDecodeError:
                    pass  # No outdated packages
        
        except Exception as e:
            logger.warning(f"Node.js dependency check failed: {e}")
        
        return issues
    
    def _check_dotnet_deps(self, project_path: Path) -> List[SecurityIssue]:
        """Check .NET dependencies"""
        issues = []
        
        try:
            result = subprocess.run(
                ['dotnet', 'list', 'package', '--outdated'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout and 'outdated' in result.stdout.lower():
                # Parse output
                lines = result.stdout.split('\n')
                for line in lines:
                    if '>' in line:  # Indicates outdated package
                        issue = SecurityIssue(
                            severity='medium',
                            category='dependency',
                            title="Outdated .NET package",
                            description=line.strip(),
                            fix_available=True,
                            fix_description="Update the package in your .csproj file"
                        )
                        issues.append(issue)
        
        except Exception as e:
            logger.warning(f".NET dependency check failed: {e}")
        
        return issues
    
    def check_dependency_health(self, package_name: str, version: str) -> Dict[str, Any]:
        """
        Check health metrics for a specific dependency.
        
        Args:
            package_name: Name of the package
            version: Version string
            
        Returns:
            Health metrics dictionary
        """
        health = {
            'name': package_name,
            'version': version,
            'is_maintained': True,
            'last_update_days': None,
            'has_security_policy': False,
            'download_count': None,
            'github_stars': None
        }
        
        # In production, this would query package registries (PyPI, npm, etc.)
        # For now, return basic structure
        return health
    
    def detect_malicious_packages(self, project_path: Path) -> List[SecurityIssue]:
        """
        Detect potentially malicious packages.
        
        Checks for:
        - Typosquatting
        - Known malicious packages
        - Suspicious package names
        
        Args:
            project_path: Path to project
            
        Returns:
            List of issues for suspicious packages
        """
        issues = []
        
        # Known typosquatting patterns
        typosquat_patterns = {
            'requests': ['reqeusts', 'requsets'],
            'urllib3': ['urlib3', 'urllib'],
            'numpy': ['numppy', 'nunpy']
        }
        
        # This would be expanded with actual package analysis
        # For now, return empty list
        return issues
