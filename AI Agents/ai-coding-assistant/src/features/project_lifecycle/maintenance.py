"""
Project Maintenance System

Handles project maintenance tasks: dependency updates, security scanning,
and code health analysis. Follows Zero-Bloat principles by focusing only
on maintenance and reporting, not on installation or fixes.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProjectMaintainer:
    """
    Maintains projects by checking dependencies, security, and code health.
    
    Responsibilities:
    - Check for outdated dependencies
    - Scan for security vulnerabilities
    - Analyze code health metrics
    - Generate maintenance reports
    
    Does NOT:
    - Install/update dependencies (user does this)
    - Fix vulnerabilities automatically (reports only)
    - Modify code (analysis only)
    
    Example:
        >>> from src.features.project_lifecycle import ProjectMaintainer
        >>> 
        >>> maintainer = ProjectMaintainer()
        >>> 
        >>> # Check outdated dependencies
        >>> outdated = maintainer.check_outdated_deps(Path("./my-project"))
        >>> 
        >>> # Scan vulnerabilities
        >>> vulns = maintainer.scan_vulnerabilities(Path("./my-project"))
        >>> 
        >>> # Analyze code health
        >>> health = maintainer.analyze_code_health(Path("./my-project"))
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the project maintainer.
        
        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
    
    def check_outdated_deps(
        self,
        path: Path,
        project_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Check for outdated dependencies.
        
        Args:
            path: Project directory path
            project_type: Project type (auto-detected if None)
        
        Returns:
            List of outdated packages with current and latest versions
        
        Example:
            >>> outdated = maintainer.check_outdated_deps(Path("./my-project"))
            >>> for pkg in outdated:
            ...     print(f"{pkg['name']}: {pkg['current']} -> {pkg['latest']}")
        """
        if not path.exists():
            logger.error(f"Path {path} does not exist")
            return []
        
        # Detect project type if not provided
        if project_type is None:
            project_type = self._detect_project_type(path)
        
        if project_type == "python":
            return self._check_python_outdated(path)
        elif project_type == "node":
            return self._check_node_outdated(path)
        elif project_type == "dotnet":
            return self._check_dotnet_outdated(path)
        else:
            logger.warning(f"Unknown project type for {path}")
            return []
    
    def scan_vulnerabilities(
        self,
        path: Path,
        project_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Scan for security vulnerabilities.
        
        Args:
            path: Project directory path
            project_type: Project type (auto-detected if None)
        
        Returns:
            List of vulnerabilities with severity and details
        
        Example:
            >>> vulns = maintainer.scan_vulnerabilities(Path("./my-project"))
            >>> for vuln in vulns:
            ...     print(f"{vuln['severity']}: {vuln['package']} - {vuln['title']}")
        """
        if not path.exists():
            logger.error(f"Path {path} does not exist")
            return []
        
        # Detect project type if not provided
        if project_type is None:
            project_type = self._detect_project_type(path)
        
        if project_type == "python":
            return self._scan_python_vulnerabilities(path)
        elif project_type == "node":
            return self._scan_node_vulnerabilities(path)
        elif project_type == "dotnet":
            return self._scan_dotnet_vulnerabilities(path)
        else:
            logger.warning(f"Unknown project type for {path}")
            return []
    
    def analyze_code_health(
        self,
        path: Path,
        project_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze code health metrics.
        
        Args:
            path: Project directory path
            project_type: Project type (auto-detected if None)
        
        Returns:
            Dictionary with health metrics
        
        Example:
            >>> health = maintainer.analyze_code_health(Path("./my-project"))
            >>> print(f"Files: {health['file_count']}")
            >>> print(f"Lines: {health['line_count']}")
        """
        if not path.exists():
            logger.error(f"Path {path} does not exist")
            return {}
        
        # Detect project type if not provided
        if project_type is None:
            project_type = self._detect_project_type(path)
        
        health = {
            "project_type": project_type,
            "analyzed_at": datetime.now().isoformat(),
            "file_count": 0,
            "line_count": 0,
            "issues": []
        }
        
        # Count files and lines
        if project_type == "python":
            files = list(path.rglob("*.py"))
            health["file_count"] = len(files)
            health["line_count"] = sum(
                len(f.read_text(encoding='utf-8', errors='ignore').splitlines())
                for f in files
                if f.is_file()
            )
        elif project_type == "node":
            files = list(path.rglob("*.js")) + list(path.rglob("*.ts"))
            # Exclude node_modules
            files = [f for f in files if "node_modules" not in str(f)]
            health["file_count"] = len(files)
            health["line_count"] = sum(
                len(f.read_text(encoding='utf-8', errors='ignore').splitlines())
                for f in files
                if f.is_file()
            )
        elif project_type == "dotnet":
            files = list(path.rglob("*.cs"))
            health["file_count"] = len(files)
            health["line_count"] = sum(
                len(f.read_text(encoding='utf-8', errors='ignore').splitlines())
                for f in files
                if f.is_file()
            )
        
        return health
    
    def generate_maintenance_report(
        self,
        path: Path,
        include_outdated: bool = True,
        include_vulnerabilities: bool = True,
        include_health: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive maintenance report.
        
        Args:
            path: Project directory path
            include_outdated: Include outdated dependencies
            include_vulnerabilities: Include vulnerability scan
            include_health: Include code health analysis
        
        Returns:
            Complete maintenance report
        
        Example:
            >>> report = maintainer.generate_maintenance_report(Path("./my-project"))
            >>> print(json.dumps(report, indent=2))
        """
        report = {
            "project_path": str(path),
            "generated_at": datetime.now().isoformat(),
            "project_type": self._detect_project_type(path)
        }
        
        if include_outdated:
            if self.verbose:
                logger.info("Checking outdated dependencies...")
            report["outdated_dependencies"] = self.check_outdated_deps(path)
        
        if include_vulnerabilities:
            if self.verbose:
                logger.info("Scanning vulnerabilities...")
            report["vulnerabilities"] = self.scan_vulnerabilities(path)
        
        if include_health:
            if self.verbose:
                logger.info("Analyzing code health...")
            report["code_health"] = self.analyze_code_health(path)
        
        # Summary
        report["summary"] = {
            "outdated_count": len(report.get("outdated_dependencies", [])),
            "vulnerability_count": len(report.get("vulnerabilities", [])),
            "critical_vulnerabilities": len([
                v for v in report.get("vulnerabilities", [])
                if v.get("severity", "").lower() == "critical"
            ]),
            "needs_attention": False
        }
        
        # Determine if needs attention
        report["summary"]["needs_attention"] = (
            report["summary"]["outdated_count"] > 0 or
            report["summary"]["vulnerability_count"] > 0
        )
        
        return report
    
    def get_update_commands(
        self,
        path: Path,
        project_type: Optional[str] = None
    ) -> List[str]:
        """
        Get commands to update dependencies.
        
        Args:
            path: Project directory path
            project_type: Project type (auto-detected if None)
        
        Returns:
            List of update command strings
        
        Example:
            >>> commands = maintainer.get_update_commands(Path("./my-project"))
            >>> for cmd in commands:
            ...     print(cmd)
        """
        if project_type is None:
            project_type = self._detect_project_type(path)
        
        commands = []
        
        if project_type == "python":
            commands = [
                "# Update Python dependencies",
                "pip install --upgrade pip",
                "pip list --outdated --format=json > outdated.json",
                "# Review outdated.json and update requirements.txt",
                "pip install -r requirements.txt --upgrade"
            ]
        elif project_type == "node":
            commands = [
                "# Update Node dependencies",
                "npm outdated",
                "npm update  # Updates within semver ranges",
                "# or use npm-check-updates for major updates:",
                "npx npm-check-updates -u",
                "npm install"
            ]
        elif project_type == "dotnet":
            commands = [
                "# Update .NET dependencies",
                "dotnet list package --outdated",
                "dotnet add package <PackageName>  # Update specific package",
                "dotnet restore"
            ]
        
        return commands
    
    # Private methods
    
    def _detect_project_type(self, path: Path) -> Optional[str]:
        """Detect project type from files."""
        if (path / "requirements.txt").exists() or (path / "setup.py").exists():
            return "python"
        elif (path / "package.json").exists():
            return "node"
        elif list(path.glob("*.csproj")):
            return "dotnet"
        return None
    
    def _check_python_outdated(self, path: Path) -> List[Dict[str, Any]]:
        """Check outdated Python packages."""
        try:
            # Use pip list --outdated
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                outdated = json.loads(result.stdout)
                return [
                    {
                        "name": pkg["name"],
                        "current": pkg["version"],
                        "latest": pkg["latest_version"],
                        "type": pkg.get("latest_filetype", "unknown")
                    }
                    for pkg in outdated
                ]
        except subprocess.TimeoutExpired:
            logger.warning("pip list command timed out")
        except json.JSONDecodeError:
            logger.warning("Failed to parse pip output")
        except Exception as e:
            logger.error(f"Error checking Python packages: {e}")
        
        return []
    
    def _check_node_outdated(self, path: Path) -> List[Dict[str, Any]]:
        """Check outdated Node packages."""
        try:
            # Use npm outdated --json
            result = subprocess.run(
                ["npm", "outdated", "--json"],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # npm outdated returns non-zero when packages are outdated
            if result.stdout:
                outdated = json.loads(result.stdout)
                return [
                    {
                        "name": name,
                        "current": info["current"],
                        "wanted": info["wanted"],
                        "latest": info["latest"],
                        "location": info.get("location", "")
                    }
                    for name, info in outdated.items()
                ]
        except subprocess.TimeoutExpired:
            logger.warning("npm outdated command timed out")
        except json.JSONDecodeError:
            logger.warning("Failed to parse npm output")
        except FileNotFoundError:
            logger.warning("npm not found")
        except Exception as e:
            logger.error(f"Error checking Node packages: {e}")
        
        return []
    
    def _check_dotnet_outdated(self, path: Path) -> List[Dict[str, Any]]:
        """Check outdated .NET packages."""
        try:
            # Use dotnet list package --outdated
            result = subprocess.run(
                ["dotnet", "list", "package", "--outdated"],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse output (format is text-based)
                lines = result.stdout.splitlines()
                outdated = []
                
                for line in lines:
                    # Look for lines with package info
                    # Format: "   > PackageName    1.0.0    1.0.1    1.1.0"
                    if ">" in line and len(line.split()) >= 4:
                        parts = line.split()
                        if len(parts) >= 5:
                            outdated.append({
                                "name": parts[1],
                                "current": parts[2],
                                "latest": parts[4]
                            })
                
                return outdated
        except subprocess.TimeoutExpired:
            logger.warning("dotnet command timed out")
        except FileNotFoundError:
            logger.warning("dotnet not found")
        except Exception as e:
            logger.error(f"Error checking .NET packages: {e}")
        
        return []
    
    def _scan_python_vulnerabilities(self, path: Path) -> List[Dict[str, Any]]:
        """Scan Python vulnerabilities."""
        vulnerabilities = []
        
        # Note: This would require 'safety' package to be installed
        # For zero-bloat, we check if it's available but don't require it
        try:
            result = subprocess.run(
                ["safety", "check", "--json"],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                data = json.loads(result.stdout)
                for vuln in data:
                    vulnerabilities.append({
                        "package": vuln[0],
                        "version": vuln[2],
                        "vulnerability_id": vuln[3],
                        "title": vuln[1],
                        "severity": "high"  # safety doesn't provide severity
                    })
        except FileNotFoundError:
            if self.verbose:
                logger.info("safety not installed (optional). Install with: pip install safety")
        except subprocess.TimeoutExpired:
            logger.warning("safety check timed out")
        except Exception as e:
            logger.error(f"Error running safety: {e}")
        
        return vulnerabilities
    
    def _scan_node_vulnerabilities(self, path: Path) -> List[Dict[str, Any]]:
        """Scan Node vulnerabilities."""
        vulnerabilities = []
        
        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                data = json.loads(result.stdout)
                
                # npm audit format varies by version
                if "vulnerabilities" in data:
                    for name, vuln_info in data["vulnerabilities"].items():
                        vulnerabilities.append({
                            "package": name,
                            "severity": vuln_info.get("severity", "unknown"),
                            "title": vuln_info.get("title", ""),
                            "via": vuln_info.get("via", [])
                        })
        except FileNotFoundError:
            if self.verbose:
                logger.info("npm not found")
        except subprocess.TimeoutExpired:
            logger.warning("npm audit timed out")
        except json.JSONDecodeError:
            logger.warning("Failed to parse npm audit output")
        except Exception as e:
            logger.error(f"Error running npm audit: {e}")
        
        return vulnerabilities
    
    def _scan_dotnet_vulnerabilities(self, path: Path) -> List[Dict[str, Any]]:
        """Scan .NET vulnerabilities."""
        vulnerabilities = []
        
        try:
            # dotnet list package --vulnerable
            result = subprocess.run(
                ["dotnet", "list", "package", "--vulnerable"],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and result.stdout:
                # Parse text output
                lines = result.stdout.splitlines()
                for line in lines:
                    if ">" in line and "vulnerable" in line.lower():
                        parts = line.split()
                        if len(parts) >= 3:
                            vulnerabilities.append({
                                "package": parts[1],
                                "version": parts[2],
                                "severity": "unknown"
                            })
        except FileNotFoundError:
            if self.verbose:
                logger.info("dotnet not found")
        except subprocess.TimeoutExpired:
            logger.warning("dotnet command timed out")
        except Exception as e:
            logger.error(f"Error running dotnet vulnerable check: {e}")
        
        return vulnerabilities


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    maintainer = ProjectMaintainer(verbose=True)
    
    # Example: Generate maintenance report
    print("Example: Maintenance Report")
    print("-" * 60)
    
    test_path = Path("./test-project")
    if test_path.exists():
        report = maintainer.generate_maintenance_report(test_path)
        print(json.dumps(report, indent=2))
