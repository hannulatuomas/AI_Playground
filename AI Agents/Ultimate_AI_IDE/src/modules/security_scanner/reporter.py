"""
Security Reporter

Generates security scan reports in various formats.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path

from .scanner import SecurityScanResult, SecurityIssue

logger = logging.getLogger(__name__)


class SecurityReporter:
    """
    Generates security reports in multiple formats.
    
    Supported formats:
    - text: Human-readable text report
    - json: Machine-readable JSON
    - html: Interactive HTML report
    - markdown: Markdown documentation
    - sarif: SARIF (Static Analysis Results Interchange Format)
    """
    
    def generate(self, result: SecurityScanResult, format: str = 'text') -> str:
        """
        Generate security report.
        
        Args:
            result: Security scan results
            format: Output format (text, json, html, markdown, sarif)
            
        Returns:
            Formatted report string
        """
        if format == 'json':
            return self._generate_json(result)
        elif format == 'html':
            return self._generate_html(result)
        elif format == 'markdown':
            return self._generate_markdown(result)
        elif format == 'sarif':
            return self._generate_sarif(result)
        else:
            return self._generate_text(result)
    
    def _generate_text(self, result: SecurityScanResult) -> str:
        """Generate text report"""
        lines = []
        
        lines.append("=" * 70)
        lines.append("SECURITY SCAN REPORT")
        lines.append("=" * 70)
        lines.append(f"Scan Time: {result.scan_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Project: {result.project_path}")
        lines.append(f"Risk Score: {result.risk_score:.1f}/100")
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 70)
        lines.append(f"Total Issues: {result.summary['total']}")
        lines.append(f"  Critical: {result.summary['critical']}")
        lines.append(f"  High:     {result.summary['high']}")
        lines.append(f"  Medium:   {result.summary['medium']}")
        lines.append(f"  Low:      {result.summary['low']}")
        lines.append("")
        lines.append("By Category:")
        lines.append(f"  Vulnerabilities: {result.summary['vulnerabilities']}")
        lines.append(f"  Dependencies:    {result.summary['dependencies']}")
        lines.append(f"  Patterns:        {result.summary['patterns']}")
        lines.append(f"  Secrets:         {result.summary['secrets']}")
        lines.append("")
        
        # Critical issues
        critical = result.get_critical_issues()
        if critical:
            lines.append("CRITICAL ISSUES")
            lines.append("-" * 70)
            for issue in critical:
                lines.append(self._format_issue_text(issue))
                lines.append("")
        
        # High issues
        high = result.get_high_issues()
        if high:
            lines.append("HIGH SEVERITY ISSUES")
            lines.append("-" * 70)
            for issue in high:
                lines.append(self._format_issue_text(issue))
                lines.append("")
        
        lines.append("=" * 70)
        lines.append(f"End of Report - {len(result.issues)} total issues found")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _format_issue_text(self, issue: SecurityIssue) -> str:
        """Format a single issue for text output"""
        lines = []
        lines.append(f"[{issue.severity.upper()}] {issue.title}")
        lines.append(f"Category: {issue.category}")
        if issue.file_path:
            location = f"{issue.file_path}"
            if issue.line_number:
                location += f":{issue.line_number}"
            lines.append(f"Location: {location}")
        if issue.cve_id:
            lines.append(f"CVE: {issue.cve_id}")
        if issue.cvss_score:
            lines.append(f"CVSS Score: {issue.cvss_score}")
        lines.append(f"Description: {issue.description}")
        if issue.fix_available and issue.fix_description:
            lines.append(f"Fix: {issue.fix_description}")
        return "\n".join(lines)
    
    def _generate_json(self, result: SecurityScanResult) -> str:
        """Generate JSON report"""
        report = {
            'scan_time': result.scan_time.isoformat(),
            'project_path': result.project_path,
            'risk_score': result.risk_score,
            'summary': result.summary,
            'issues': [
                {
                    'severity': issue.severity,
                    'category': issue.category,
                    'title': issue.title,
                    'description': issue.description,
                    'file_path': issue.file_path,
                    'line_number': issue.line_number,
                    'cve_id': issue.cve_id,
                    'cvss_score': issue.cvss_score,
                    'fix_available': issue.fix_available,
                    'fix_description': issue.fix_description,
                    'references': issue.references
                }
                for issue in result.issues
            ]
        }
        return json.dumps(report, indent=2)
    
    def _generate_markdown(self, result: SecurityScanResult) -> str:
        """Generate Markdown report"""
        lines = []
        
        lines.append("# Security Scan Report")
        lines.append("")
        lines.append(f"**Scan Time**: {result.scan_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Project**: `{result.project_path}`")
        lines.append(f"**Risk Score**: {result.risk_score:.1f}/100")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total Issues**: {result.summary['total']}")
        lines.append(f"  - Critical: {result.summary['critical']}")
        lines.append(f"  - High: {result.summary['high']}")
        lines.append(f"  - Medium: {result.summary['medium']}")
        lines.append(f"  - Low: {result.summary['low']}")
        lines.append("")
        lines.append("### By Category")
        lines.append("")
        lines.append(f"- Vulnerabilities: {result.summary['vulnerabilities']}")
        lines.append(f"- Dependencies: {result.summary['dependencies']}")
        lines.append(f"- Patterns: {result.summary['patterns']}")
        lines.append(f"- Secrets: {result.summary['secrets']}")
        lines.append("")
        
        # Issues by severity
        for severity in ['critical', 'high', 'medium', 'low']:
            issues = [i for i in result.issues if i.severity == severity]
            if issues:
                lines.append(f"## {severity.title()} Severity Issues")
                lines.append("")
                for issue in issues:
                    lines.append(f"### {issue.title}")
                    lines.append("")
                    lines.append(f"- **Category**: {issue.category}")
                    if issue.file_path:
                        location = f"`{issue.file_path}`"
                        if issue.line_number:
                            location += f" (line {issue.line_number})"
                        lines.append(f"- **Location**: {location}")
                    if issue.cve_id:
                        lines.append(f"- **CVE**: {issue.cve_id}")
                    lines.append(f"- **Description**: {issue.description}")
                    if issue.fix_available and issue.fix_description:
                        lines.append(f"- **Fix**: {issue.fix_description}")
                    lines.append("")
        
        return "\n".join(lines)
    
    def _generate_html(self, result: SecurityScanResult) -> str:
        """Generate HTML report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Security Scan Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
        .issue {{ border-left: 4px solid #ccc; padding: 10px; margin: 10px 0; }}
        .critical {{ border-left-color: #d32f2f; }}
        .high {{ border-left-color: #f57c00; }}
        .medium {{ border-left-color: #fbc02d; }}
        .low {{ border-left-color: #388e3c; }}
        .risk-score {{ font-size: 24px; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Security Scan Report</h1>
    <p><strong>Scan Time:</strong> {result.scan_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><strong>Project:</strong> {result.project_path}</p>
    <p><strong>Risk Score:</strong> <span class="risk-score">{result.risk_score:.1f}/100</span></p>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Issues:</strong> {result.summary['total']}</p>
        <ul>
            <li>Critical: {result.summary['critical']}</li>
            <li>High: {result.summary['high']}</li>
            <li>Medium: {result.summary['medium']}</li>
            <li>Low: {result.summary['low']}</li>
        </ul>
        <h3>By Category</h3>
        <ul>
            <li>Vulnerabilities: {result.summary['vulnerabilities']}</li>
            <li>Dependencies: {result.summary['dependencies']}</li>
            <li>Patterns: {result.summary['patterns']}</li>
            <li>Secrets: {result.summary['secrets']}</li>
        </ul>
    </div>
    
    <h2>Issues</h2>
"""
        
        for issue in result.issues:
            html += f"""
    <div class="issue {issue.severity}">
        <h3>[{issue.severity.upper()}] {issue.title}</h3>
        <p><strong>Category:</strong> {issue.category}</p>
"""
            if issue.file_path:
                location = issue.file_path
                if issue.line_number:
                    location += f":{issue.line_number}"
                html += f"        <p><strong>Location:</strong> {location}</p>\n"
            
            html += f"        <p>{issue.description}</p>\n"
            
            if issue.fix_available and issue.fix_description:
                html += f"        <p><strong>Fix:</strong> {issue.fix_description}</p>\n"
            
            html += "    </div>\n"
        
        html += """
</body>
</html>
"""
        return html
    
    def _generate_sarif(self, result: SecurityScanResult) -> str:
        """Generate SARIF format report"""
        sarif = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "UAIDE Security Scanner",
                        "version": "1.5.0",
                        "informationUri": "https://github.com/hannulatuomas/Ultimate_AI_IDE"
                    }
                },
                "results": [
                    {
                        "ruleId": f"{issue.category}_{issue.severity}",
                        "level": self._map_sarif_level(issue.severity),
                        "message": {
                            "text": issue.description
                        },
                        "locations": [{
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": issue.file_path or "unknown"
                                },
                                "region": {
                                    "startLine": issue.line_number or 1
                                }
                            }
                        }] if issue.file_path else []
                    }
                    for issue in result.issues
                ]
            }]
        }
        return json.dumps(sarif, indent=2)
    
    def _map_sarif_level(self, severity: str) -> str:
        """Map severity to SARIF level"""
        mapping = {
            'critical': 'error',
            'high': 'error',
            'medium': 'warning',
            'low': 'note'
        }
        return mapping.get(severity, 'warning')
