"""
Dependency Manager Module

Manages project dependencies with automatic updates, testing, and rollback.
"""

import logging
import json
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

logger = logging.getLogger(__name__)


@dataclass
class DependencyUpdate:
    """Represents a dependency update"""
    name: str
    current_version: str
    latest_version: str
    is_breaking: bool = False
    changelog_url: Optional[str] = None
    security_fixes: List[str] = None
    
    def __post_init__(self):
        if self.security_fixes is None:
            self.security_fixes = []


@dataclass
class UpdateResult:
    """Result of dependency update operation"""
    success: bool
    updated: List[str]
    failed: List[str]
    rolled_back: bool = False
    test_results: Optional[Dict] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class DependencyManager:
    """
    Manages project dependencies with automatic updates.
    
    Features:
    - Check for outdated dependencies
    - Detect breaking changes
    - Safe update with testing
    - Automatic rollback on failure
    - Support multiple package managers
    """
    
    def __init__(self, project_path: str):
        """
        Initialize dependency manager.
        
        Args:
            project_path: Path to project root
        """
        self.project_path = Path(project_path)
        self.backup_dir = self.project_path / ".uaide_backups"
        self.package_manager = self._detect_package_manager()
    
    def _detect_package_manager(self) -> str:
        """Detect which package manager the project uses"""
        if (self.project_path / "requirements.txt").exists():
            return "pip"
        elif (self.project_path / "package.json").exists():
            return "npm"
        elif (self.project_path / "yarn.lock").exists():
            return "yarn"
        elif list(self.project_path.glob("*.csproj")):
            return "dotnet"
        elif (self.project_path / "pom.xml").exists():
            return "maven"
        else:
            return "unknown"
    
    def check_outdated(self) -> List[DependencyUpdate]:
        """
        Check for outdated dependencies.
        
        Returns:
            List of available updates
        """
        logger.info(f"Checking for outdated dependencies using {self.package_manager}")
        
        if self.package_manager == "pip":
            return self._check_outdated_pip()
        elif self.package_manager == "npm":
            return self._check_outdated_npm()
        elif self.package_manager == "yarn":
            return self._check_outdated_yarn()
        elif self.package_manager == "dotnet":
            return self._check_outdated_dotnet()
        else:
            logger.warning(f"Unsupported package manager: {self.package_manager}")
            return []
    
    def _check_outdated_pip(self) -> List[DependencyUpdate]:
        """Check outdated Python packages"""
        updates = []
        
        try:
            result = subprocess.run(
                ['pip', 'list', '--outdated', '--format', 'json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                outdated = json.loads(result.stdout)
                
                for pkg in outdated:
                    # Check if update is breaking (major version change)
                    is_breaking = self._is_breaking_change(
                        pkg['version'],
                        pkg['latest_version']
                    )
                    
                    updates.append(DependencyUpdate(
                        name=pkg['name'],
                        current_version=pkg['version'],
                        latest_version=pkg['latest_version'],
                        is_breaking=is_breaking
                    ))
        
        except Exception as e:
            logger.error(f"Failed to check outdated pip packages: {e}")
        
        return updates
    
    def _check_outdated_npm(self) -> List[DependencyUpdate]:
        """Check outdated npm packages"""
        updates = []
        
        try:
            result = subprocess.run(
                ['npm', 'outdated', '--json'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                try:
                    outdated = json.loads(result.stdout)
                    
                    for name, info in outdated.items():
                        is_breaking = self._is_breaking_change(
                            info.get('current', '0.0.0'),
                            info.get('latest', '0.0.0')
                        )
                        
                        updates.append(DependencyUpdate(
                            name=name,
                            current_version=info.get('current', 'unknown'),
                            latest_version=info.get('latest', 'unknown'),
                            is_breaking=is_breaking
                        ))
                except json.JSONDecodeError:
                    pass  # No outdated packages
        
        except Exception as e:
            logger.error(f"Failed to check outdated npm packages: {e}")
        
        return updates
    
    def _check_outdated_yarn(self) -> List[DependencyUpdate]:
        """Check outdated yarn packages"""
        # Similar to npm but using yarn commands
        return self._check_outdated_npm()  # Simplified for now
    
    def _check_outdated_dotnet(self) -> List[DependencyUpdate]:
        """Check outdated .NET packages"""
        updates = []
        
        try:
            result = subprocess.run(
                ['dotnet', 'list', 'package', '--outdated'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse output (simplified)
            if result.stdout and 'outdated' in result.stdout.lower():
                logger.info("Found outdated .NET packages")
        
        except Exception as e:
            logger.error(f"Failed to check outdated .NET packages: {e}")
        
        return updates
    
    def _is_breaking_change(self, current: str, latest: str) -> bool:
        """
        Detect if version change is breaking (major version bump).
        
        Uses semantic versioning (MAJOR.MINOR.PATCH).
        """
        try:
            # Extract major version numbers
            current_major = int(current.split('.')[0])
            latest_major = int(latest.split('.')[0])
            
            return latest_major > current_major
        except (ValueError, IndexError):
            # If we can't parse versions, assume it might be breaking
            return True
    
    def update_dependencies(self,
                          packages: Optional[List[str]] = None,
                          test_after: bool = True,
                          rollback_on_failure: bool = True) -> UpdateResult:
        """
        Update dependencies with testing and rollback.
        
        Args:
            packages: Specific packages to update (None = all)
            test_after: Run tests after update
            rollback_on_failure: Rollback if tests fail
            
        Returns:
            UpdateResult with status and details
        """
        logger.info(f"Updating dependencies: {packages or 'all'}")
        
        # Create backup
        backup_path = self._create_backup()
        
        try:
            # Perform update
            updated, failed = self._perform_update(packages)
            
            # Run tests if requested
            test_results = None
            if test_after and updated:
                logger.info("Running tests after update...")
                test_results = self._run_tests()
                
                if not test_results.get('success', False) and rollback_on_failure:
                    logger.warning("Tests failed, rolling back...")
                    self._rollback(backup_path)
                    return UpdateResult(
                        success=False,
                        updated=[],
                        failed=updated + failed,
                        rolled_back=True,
                        test_results=test_results,
                        errors=["Tests failed after update, rolled back"]
                    )
            
            # Clean up backup if successful
            if backup_path and backup_path.exists():
                shutil.rmtree(backup_path)
            
            return UpdateResult(
                success=len(failed) == 0,
                updated=updated,
                failed=failed,
                test_results=test_results
            )
        
        except Exception as e:
            logger.error(f"Update failed: {e}")
            if rollback_on_failure and backup_path:
                self._rollback(backup_path)
                return UpdateResult(
                    success=False,
                    updated=[],
                    failed=packages or [],
                    rolled_back=True,
                    errors=[str(e)]
                )
            raise
    
    def _create_backup(self) -> Optional[Path]:
        """Create backup of dependency files"""
        try:
            self.backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{timestamp}"
            backup_path.mkdir()
            
            # Backup dependency files
            files_to_backup = [
                "requirements.txt",
                "package.json",
                "package-lock.json",
                "yarn.lock"
            ]
            
            for filename in files_to_backup:
                src = self.project_path / filename
                if src.exists():
                    shutil.copy2(src, backup_path / filename)
            
            logger.info(f"Created backup at {backup_path}")
            return backup_path
        
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def _perform_update(self, packages: Optional[List[str]]) -> Tuple[List[str], List[str]]:
        """Perform the actual update"""
        updated = []
        failed = []
        
        if self.package_manager == "pip":
            updated, failed = self._update_pip(packages)
        elif self.package_manager == "npm":
            updated, failed = self._update_npm(packages)
        elif self.package_manager == "yarn":
            updated, failed = self._update_yarn(packages)
        
        return updated, failed
    
    def _update_pip(self, packages: Optional[List[str]]) -> Tuple[List[str], List[str]]:
        """Update pip packages"""
        updated = []
        failed = []
        
        try:
            if packages:
                for pkg in packages:
                    result = subprocess.run(
                        ['pip', 'install', '--upgrade', pkg],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    if result.returncode == 0:
                        updated.append(pkg)
                    else:
                        failed.append(pkg)
            else:
                # Update all from requirements.txt
                req_file = self.project_path / "requirements.txt"
                if req_file.exists():
                    result = subprocess.run(
                        ['pip', 'install', '--upgrade', '-r', str(req_file)],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    if result.returncode == 0:
                        updated.append("all")
        
        except Exception as e:
            logger.error(f"Pip update failed: {e}")
            failed.extend(packages or ["all"])
        
        return updated, failed
    
    def _update_npm(self, packages: Optional[List[str]]) -> Tuple[List[str], List[str]]:
        """Update npm packages"""
        updated = []
        failed = []
        
        try:
            if packages:
                for pkg in packages:
                    result = subprocess.run(
                        ['npm', 'update', pkg],
                        cwd=self.project_path,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    if result.returncode == 0:
                        updated.append(pkg)
                    else:
                        failed.append(pkg)
            else:
                result = subprocess.run(
                    ['npm', 'update'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    updated.append("all")
        
        except Exception as e:
            logger.error(f"npm update failed: {e}")
            failed.extend(packages or ["all"])
        
        return updated, failed
    
    def _update_yarn(self, packages: Optional[List[str]]) -> Tuple[List[str], List[str]]:
        """Update yarn packages"""
        # Similar to npm
        return self._update_npm(packages)
    
    def _run_tests(self) -> Dict[str, Any]:
        """Run project tests"""
        try:
            # Try pytest for Python projects
            if self.package_manager == "pip":
                result = subprocess.run(
                    ['pytest', '-v'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                return {
                    'success': result.returncode == 0,
                    'output': result.stdout
                }
            
            # Try npm test for Node projects
            elif self.package_manager in ["npm", "yarn"]:
                result = subprocess.run(
                    ['npm', 'test'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                return {
                    'success': result.returncode == 0,
                    'output': result.stdout
                }
        
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return {'success': False, 'error': str(e)}
        
        return {'success': True, 'message': 'No tests configured'}
    
    def _rollback(self, backup_path: Path):
        """Rollback to backup"""
        try:
            logger.info(f"Rolling back from {backup_path}")
            
            for backup_file in backup_path.iterdir():
                target = self.project_path / backup_file.name
                shutil.copy2(backup_file, target)
            
            logger.info("Rollback complete")
        
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            raise
    
    def suggest_safe_updates(self) -> List[DependencyUpdate]:
        """
        Suggest safe (non-breaking) updates.
        
        Returns:
            List of safe updates (minor/patch versions)
        """
        all_updates = self.check_outdated()
        safe_updates = [u for u in all_updates if not u.is_breaking]
        
        logger.info(f"Found {len(safe_updates)} safe updates out of {len(all_updates)} total")
        return safe_updates
