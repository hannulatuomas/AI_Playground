"""
Secret Scanner

Scans for exposed secrets, credentials, and sensitive information in code.
"""

import logging
import re
from pathlib import Path
from typing import List, Pattern
from dataclasses import dataclass

from .scanner import SecurityIssue

logger = logging.getLogger(__name__)


@dataclass
class SecretPattern:
    """Defines a secret detection pattern"""
    name: str
    pattern: Pattern
    description: str


class SecretScanner:
    """
    Scans for exposed secrets and credentials in source code.
    
    Detects:
    - API keys
    - Passwords
    - Private keys
    - AWS credentials
    - Database connection strings
    - OAuth tokens
    - JWT secrets
    """
    
    def __init__(self):
        """Initialize secret scanner with detection patterns"""
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> List[SecretPattern]:
        """Load secret detection patterns"""
        patterns = []
        
        # Generic API Key patterns
        patterns.append(SecretPattern(
            name='generic_api_key',
            pattern=re.compile(r'["\']?api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', re.IGNORECASE),
            description='Potential API key detected'
        ))
        
        # AWS Access Key
        patterns.append(SecretPattern(
            name='aws_access_key',
            pattern=re.compile(r'AKIA[0-9A-Z]{16}'),
            description='AWS Access Key ID detected'
        ))
        
        # AWS Secret Key
        patterns.append(SecretPattern(
            name='aws_secret_key',
            pattern=re.compile(r'["\']?aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9/+=]{40})["\']', re.IGNORECASE),
            description='AWS Secret Access Key detected'
        ))
        
        # GitHub Token
        patterns.append(SecretPattern(
            name='github_token',
            pattern=re.compile(r'gh[pousr]_[A-Za-z0-9_]{36,}'),
            description='GitHub Personal Access Token detected'
        ))
        
        # Generic Password
        patterns.append(SecretPattern(
            name='password',
            pattern=re.compile(r'["\']?password["\']?\s*[:=]\s*["\']([^"\']{8,})["\']', re.IGNORECASE),
            description='Hardcoded password detected'
        ))
        
        # Database Connection String
        patterns.append(SecretPattern(
            name='db_connection',
            pattern=re.compile(r'(mysql|postgresql|mongodb)://[^:]+:[^@]+@', re.IGNORECASE),
            description='Database connection string with credentials detected'
        ))
        
        # Private Key
        patterns.append(SecretPattern(
            name='private_key',
            pattern=re.compile(r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----'),
            description='Private key detected'
        ))
        
        # JWT Token
        patterns.append(SecretPattern(
            name='jwt_token',
            pattern=re.compile(r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*'),
            description='JWT token detected'
        ))
        
        # Slack Token
        patterns.append(SecretPattern(
            name='slack_token',
            pattern=re.compile(r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,}'),
            description='Slack token detected'
        ))
        
        # Google API Key
        patterns.append(SecretPattern(
            name='google_api_key',
            pattern=re.compile(r'AIza[0-9A-Za-z_-]{35}'),
            description='Google API key detected'
        ))
        
        # Stripe API Key
        patterns.append(SecretPattern(
            name='stripe_key',
            pattern=re.compile(r'sk_live_[0-9a-zA-Z]{24,}'),
            description='Stripe API key detected'
        ))
        
        # Twilio API Key
        patterns.append(SecretPattern(
            name='twilio_key',
            pattern=re.compile(r'SK[0-9a-fA-F]{32}'),
            description='Twilio API key detected'
        ))
        
        # Generic Secret
        patterns.append(SecretPattern(
            name='generic_secret',
            pattern=re.compile(r'["\']?secret["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', re.IGNORECASE),
            description='Potential secret detected'
        ))
        
        return patterns
    
    def scan(self, project_path: Path) -> List[SecurityIssue]:
        """
        Scan project for exposed secrets.
        
        Args:
            project_path: Path to project root
            
        Returns:
            List of security issues for exposed secrets
        """
        issues = []
        
        try:
            # Scan all text files
            for file_path in self._get_scannable_files(project_path):
                issues.extend(self._scan_file(file_path))
            
            logger.info(f"Secret scan found {len(issues)} issues")
            return issues
            
        except Exception as e:
            logger.error(f"Error during secret scan: {e}")
            return issues
    
    def _get_scannable_files(self, project_path: Path) -> List[Path]:
        """Get all files to scan for secrets"""
        # Scan source files and config files
        extensions = [
            '.py', '.js', '.ts', '.java', '.cs', '.cpp', '.c', '.php', '.rb',
            '.json', '.yaml', '.yml', '.xml', '.env', '.config', '.ini', '.toml'
        ]
        
        files = []
        for ext in extensions:
            files.extend(project_path.rglob(f'*{ext}'))
        
        # Also scan files without extension (like .env)
        for file_path in project_path.rglob('*'):
            if file_path.is_file() and not file_path.suffix:
                if file_path.name in ['.env', '.envrc', 'credentials', 'secrets']:
                    files.append(file_path)
        
        # Filter out directories to skip
        skip_dirs = {'node_modules', 'venv', '.venv', '__pycache__', 'build', 'dist', '.git'}
        files = [f for f in files if not any(skip in f.parts for skip in skip_dirs)]
        
        return files
    
    def _scan_file(self, file_path: Path) -> List[SecurityIssue]:
        """Scan a single file for secrets"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check each pattern
            for pattern_def in self.patterns:
                for line_num, line in enumerate(lines, 1):
                    match = pattern_def.pattern.search(line)
                    if match:
                        # Mask the secret in the description
                        masked_line = self._mask_secret(line)
                        
                        issue = SecurityIssue(
                            severity='critical',
                            category='secret',
                            title=f"Exposed Secret: {pattern_def.name}",
                            description=f"{pattern_def.description}\nLine: {masked_line}",
                            file_path=str(file_path),
                            line_number=line_num,
                            fix_available=True,
                            fix_description="Remove the hardcoded secret and use environment variables or a secret management system. Rotate the exposed credential immediately."
                        )
                        issues.append(issue)
        
        except Exception as e:
            logger.warning(f"Error scanning {file_path} for secrets: {e}")
        
        return issues
    
    def _mask_secret(self, line: str) -> str:
        """Mask secrets in a line for safe display"""
        # Replace potential secrets with asterisks
        masked = re.sub(r'["\']([a-zA-Z0-9_\-/+=]{20,})["\']', r'"***REDACTED***"', line)
        return masked.strip()
    
    def validate_secret(self, secret: str, secret_type: str) -> bool:
        """
        Validate if a detected string is actually a secret.
        
        Reduces false positives by checking:
        - Length
        - Entropy
        - Format
        
        Args:
            secret: The detected secret string
            secret_type: Type of secret detected
            
        Returns:
            True if likely a real secret
        """
        # Basic validation - in production this would be more sophisticated
        if len(secret) < 8:
            return False
        
        # Check entropy (randomness)
        unique_chars = len(set(secret))
        if unique_chars < len(secret) * 0.5:  # Low entropy
            return False
        
        return True
