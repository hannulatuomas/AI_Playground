"""
Security Scanner - Main Orchestrator

Coordinates all security scanning activities.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SecurityIssue:
    """Represents a security issue"""
    severity: str  # critical, high, medium, low
    category: str  # vulnerability, dependency, pattern, secret
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    fix_available: bool = False
    fix_description: Optional[str] = None
    references: List[str] = field(default_factory=list)


@dataclass
class SecurityScanResult:
    """Results from a security scan"""
    scan_time: datetime
    project_path: str
    issues: List[SecurityIssue]
    summary: Dict[str, int]
    risk_score: float  # 0-100
    
    def get_critical_issues(self) -> List[SecurityIssue]:
        """Get critical severity issues"""
        return [i for i in self.issues if i.severity == 'critical']
    
    def get_high_issues(self) -> List[SecurityIssue]:
        """Get high severity issues"""
        return [i for i in self.issues if i.severity == 'high']
    
    def get_by_category(self, category: str) -> List[SecurityIssue]:
        """Get issues by category"""
        return [i for i in self.issues if i.category == category]


class SecurityScanner:
    """
    Main security scanner orchestrator.
    
    Coordinates vulnerability scanning, dependency checking,
    pattern detection, and secret scanning.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize security scanner.
        
        Args:
            project_path: Path to project root
        """
        self.project_path = Path(project_path)
        self.issues: List[SecurityIssue] = []
        
        # Import scanners lazily to avoid circular imports
        from .vulnerability_scanner import VulnerabilityScanner
        from .dependency_checker import DependencyChecker
        from .pattern_detector import PatternDetector
        from .secret_scanner import SecretScanner
        from .reporter import SecurityReporter
        
        self.vulnerability_scanner = VulnerabilityScanner()
        self.dependency_checker = DependencyChecker()
        self.pattern_detector = PatternDetector()
        self.secret_scanner = SecretScanner()
        self.reporter = SecurityReporter()
    
    def scan_project(self, 
                    scan_vulnerabilities: bool = True,
                    scan_dependencies: bool = True,
                    scan_patterns: bool = True,
                    scan_secrets: bool = True) -> SecurityScanResult:
        """
        Run complete security scan on project.
        
        Args:
            scan_vulnerabilities: Scan for CVEs
            scan_dependencies: Check dependency security
            scan_patterns: Detect insecure patterns
            scan_secrets: Scan for exposed secrets
            
        Returns:
            SecurityScanResult with all findings
        """
        logger.info(f"Starting security scan of {self.project_path}")
        self.issues = []
        
        try:
            # Vulnerability scanning
            if scan_vulnerabilities:
                logger.info("Scanning for vulnerabilities...")
                vuln_issues = self.vulnerability_scanner.scan(self.project_path)
                self.issues.extend(vuln_issues)
            
            # Dependency checking
            if scan_dependencies:
                logger.info("Checking dependencies...")
                dep_issues = self.dependency_checker.check(self.project_path)
                self.issues.extend(dep_issues)
            
            # Pattern detection
            if scan_patterns:
                logger.info("Detecting insecure patterns...")
                pattern_issues = self.pattern_detector.detect(self.project_path)
                self.issues.extend(pattern_issues)
            
            # Secret scanning
            if scan_secrets:
                logger.info("Scanning for secrets...")
                secret_issues = self.secret_scanner.scan(self.project_path)
                self.issues.extend(secret_issues)
            
            # Calculate summary and risk score
            summary = self._calculate_summary()
            risk_score = self._calculate_risk_score()
            
            result = SecurityScanResult(
                scan_time=datetime.now(),
                project_path=str(self.project_path),
                issues=self.issues,
                summary=summary,
                risk_score=risk_score
            )
            
            logger.info(f"Security scan complete. Found {len(self.issues)} issues. Risk score: {risk_score}")
            return result
            
        except Exception as e:
            logger.error(f"Error during security scan: {e}")
            raise
    
    def _calculate_summary(self) -> Dict[str, int]:
        """Calculate issue summary by severity and category"""
        summary = {
            'total': len(self.issues),
            'critical': len([i for i in self.issues if i.severity == 'critical']),
            'high': len([i for i in self.issues if i.severity == 'high']),
            'medium': len([i for i in self.issues if i.severity == 'medium']),
            'low': len([i for i in self.issues if i.severity == 'low']),
            'vulnerabilities': len([i for i in self.issues if i.category == 'vulnerability']),
            'dependencies': len([i for i in self.issues if i.category == 'dependency']),
            'patterns': len([i for i in self.issues if i.category == 'pattern']),
            'secrets': len([i for i in self.issues if i.category == 'secret'])
        }
        return summary
    
    def _calculate_risk_score(self) -> float:
        """
        Calculate overall risk score (0-100).
        
        Weights:
        - Critical: 25 points each
        - High: 10 points each
        - Medium: 3 points each
        - Low: 1 point each
        """
        score = 0.0
        
        for issue in self.issues:
            if issue.severity == 'critical':
                score += 25
            elif issue.severity == 'high':
                score += 10
            elif issue.severity == 'medium':
                score += 3
            elif issue.severity == 'low':
                score += 1
        
        # Cap at 100
        return min(score, 100.0)
    
    def generate_report(self, result: SecurityScanResult, format: str = 'text') -> str:
        """
        Generate security report.
        
        Args:
            result: Scan results
            format: Report format (text, json, html, markdown)
            
        Returns:
            Formatted report
        """
        return self.reporter.generate(result, format)
    
    def get_fix_recommendations(self, issue: SecurityIssue) -> List[str]:
        """
        Get fix recommendations for an issue.
        
        Args:
            issue: Security issue
            
        Returns:
            List of fix recommendations
        """
        recommendations = []
        
        if issue.fix_available and issue.fix_description:
            recommendations.append(issue.fix_description)
        
        # Add category-specific recommendations
        if issue.category == 'vulnerability':
            recommendations.append("Update the affected package to the latest secure version")
            recommendations.append("Check for security patches from the vendor")
        elif issue.category == 'dependency':
            recommendations.append("Review and update outdated dependencies")
            recommendations.append("Consider alternative packages with better security")
        elif issue.category == 'pattern':
            recommendations.append("Refactor code to use secure coding practices")
            recommendations.append("Add input validation and sanitization")
        elif issue.category == 'secret':
            recommendations.append("Remove hardcoded secrets immediately")
            recommendations.append("Use environment variables or secret management systems")
            recommendations.append("Rotate the exposed credentials")
        
        return recommendations
