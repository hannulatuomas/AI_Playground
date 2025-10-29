"""
Orchestrator Security Methods

Security scanning methods for the UAIDE orchestrator.
"""

from typing import Dict, Any
from pathlib import Path
from ..utils.result import Result


def scan_security(self, project_path: str, 
                 scan_vulnerabilities: bool = True,
                 scan_dependencies: bool = True,
                 scan_patterns: bool = True,
                 scan_secrets: bool = True) -> Result:
    """
    Run comprehensive security scan on project.
    
    Args:
        project_path: Path to project
        scan_vulnerabilities: Scan for CVEs
        scan_dependencies: Check dependency security
        scan_patterns: Detect insecure patterns
        scan_secrets: Scan for exposed secrets
        
    Returns:
        Result with scan findings
    """
    try:
        # Lazy initialize security scanner
        if self.security_scanner is None:
            from ..modules.security_scanner import SecurityScanner
            self.security_scanner = SecurityScanner(project_path)
        
        # Run scan
        result = self.security_scanner.scan_project(
            scan_vulnerabilities=scan_vulnerabilities,
            scan_dependencies=scan_dependencies,
            scan_patterns=scan_patterns,
            scan_secrets=scan_secrets
        )
        
        # Emit event
        self.event_bus.emit('security_scan_complete', {
            'project_path': project_path,
            'total_issues': result.summary['total'],
            'risk_score': result.risk_score
        })
        
        return Result(
            success=True,
            message=f"Security scan complete. Found {result.summary['total']} issues.",
            data={
                'scan_result': result,
                'summary': result.summary,
                'risk_score': result.risk_score,
                'issues': [
                    {
                        'severity': issue.severity,
                        'category': issue.category,
                        'title': issue.title,
                        'description': issue.description,
                        'file_path': issue.file_path,
                        'line_number': issue.line_number
                    }
                    for issue in result.issues
                ]
            }
        )
        
    except Exception as e:
        return Result(
            success=False,
            message=f"Security scan failed: {e}",
            errors=[str(e)]
        )


def scan_vulnerabilities(self, project_path: str) -> Result:
    """
    Scan for known vulnerabilities (CVEs).
    
    Args:
        project_path: Path to project
        
    Returns:
        Result with vulnerability findings
    """
    try:
        from ..modules.security_scanner import VulnerabilityScanner
        
        scanner = VulnerabilityScanner()
        issues = scanner.scan(Path(project_path))
        
        return Result(
            success=True,
            message=f"Found {len(issues)} vulnerabilities",
            data={'vulnerabilities': issues}
        )
        
    except Exception as e:
        return Result(
            success=False,
            message=f"Vulnerability scan failed: {e}",
            errors=[str(e)]
        )


def check_dependencies(self, project_path: str) -> Result:
    """
    Check dependency security and health.
    
    Args:
        project_path: Path to project
        
    Returns:
        Result with dependency issues
    """
    try:
        from ..modules.security_scanner import DependencyChecker
        
        checker = DependencyChecker()
        issues = checker.check(Path(project_path))
        
        return Result(
            success=True,
            message=f"Found {len(issues)} dependency issues",
            data={'dependency_issues': issues}
        )
        
    except Exception as e:
        return Result(
            success=False,
            message=f"Dependency check failed: {e}",
            errors=[str(e)]
        )


def detect_insecure_patterns(self, project_path: str) -> Result:
    """
    Detect insecure coding patterns.
    
    Args:
        project_path: Path to project
        
    Returns:
        Result with pattern issues
    """
    try:
        from ..modules.security_scanner import PatternDetector
        
        detector = PatternDetector()
        issues = detector.detect(Path(project_path))
        
        return Result(
            success=True,
            message=f"Found {len(issues)} insecure patterns",
            data={'pattern_issues': issues}
        )
        
    except Exception as e:
        return Result(
            success=False,
            message=f"Pattern detection failed: {e}",
            errors=[str(e)]
        )


def scan_secrets(self, project_path: str) -> Result:
    """
    Scan for exposed secrets and credentials.
    
    Args:
        project_path: Path to project
        
    Returns:
        Result with exposed secrets
    """
    try:
        from ..modules.security_scanner import SecretScanner
        
        scanner = SecretScanner()
        issues = scanner.scan(Path(project_path))
        
        if issues:
            return Result(
                success=True,
                message=f"⚠️ Found {len(issues)} exposed secrets! Rotate credentials immediately!",
                data={'secrets': issues}
            )
        else:
            return Result(
                success=True,
                message="No exposed secrets found",
                data={'secrets': []}
            )
        
    except Exception as e:
        return Result(
            success=False,
            message=f"Secret scan failed: {e}",
            errors=[str(e)]
        )


def generate_security_report(self, project_path: str, format: str = 'text') -> Result:
    """
    Generate security report.
    
    Args:
        project_path: Path to project
        format: Report format (text, json, html, markdown, sarif)
        
    Returns:
        Result with report content
    """
    try:
        # Run full scan
        scan_result = self.scan_security(project_path)
        
        if not scan_result.success:
            return scan_result
        
        # Generate report
        from ..modules.security_scanner import SecurityReporter
        
        reporter = SecurityReporter()
        report = reporter.generate(scan_result.data['scan_result'], format)
        
        return Result(
            success=True,
            message="Security report generated",
            data={'report': report, 'format': format}
        )
        
    except Exception as e:
        return Result(
            success=False,
            message=f"Report generation failed: {e}",
            errors=[str(e)]
        )
