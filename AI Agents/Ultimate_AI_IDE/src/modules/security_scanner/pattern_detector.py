"""
Pattern Detector

Detects insecure coding patterns and vulnerabilities in source code.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Pattern
from dataclasses import dataclass

from .scanner import SecurityIssue

logger = logging.getLogger(__name__)


@dataclass
class InsecurePattern:
    """Defines an insecure code pattern"""
    name: str
    pattern: Pattern
    severity: str
    description: str
    fix_suggestion: str
    languages: List[str]


class PatternDetector:
    """
    Detects insecure coding patterns in source code.
    
    Detects:
    - SQL injection vulnerabilities
    - XSS vulnerabilities
    - Command injection
    - Path traversal
    - Hardcoded credentials
    - Weak cryptography
    - Insecure deserialization
    """
    
    def __init__(self):
        """Initialize pattern detector with security patterns"""
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> List[InsecurePattern]:
        """Load insecure code patterns"""
        patterns = []
        
        # SQL Injection patterns
        patterns.append(InsecurePattern(
            name='sql_injection_concat',
            pattern=re.compile(r'(execute|cursor\.execute|query)\s*\(\s*["\'].*\+.*["\']', re.IGNORECASE),
            severity='critical',
            description='Potential SQL injection via string concatenation',
            fix_suggestion='Use parameterized queries instead of string concatenation',
            languages=['python', 'java', 'csharp']
        ))
        
        patterns.append(InsecurePattern(
            name='sql_injection_fstring',
            pattern=re.compile(r'(execute|cursor\.execute|query)\s*\(\s*f["\']', re.IGNORECASE),
            severity='critical',
            description='Potential SQL injection via f-string',
            fix_suggestion='Use parameterized queries with placeholders',
            languages=['python']
        ))
        
        # XSS patterns
        patterns.append(InsecurePattern(
            name='xss_innerhtml',
            pattern=re.compile(r'innerHTML\s*=\s*.*\+', re.IGNORECASE),
            severity='high',
            description='Potential XSS via innerHTML assignment',
            fix_suggestion='Use textContent or sanitize input before assignment',
            languages=['javascript', 'typescript']
        ))
        
        patterns.append(InsecurePattern(
            name='xss_document_write',
            pattern=re.compile(r'document\.write\s*\(', re.IGNORECASE),
            severity='high',
            description='Potential XSS via document.write',
            fix_suggestion='Use safer DOM manipulation methods',
            languages=['javascript', 'typescript']
        ))
        
        # Command Injection patterns
        patterns.append(InsecurePattern(
            name='command_injection_system',
            pattern=re.compile(r'os\.system\s*\(.*\+', re.IGNORECASE),
            severity='critical',
            description='Potential command injection via os.system',
            fix_suggestion='Use subprocess with list arguments instead',
            languages=['python']
        ))
        
        patterns.append(InsecurePattern(
            name='command_injection_subprocess',
            pattern=re.compile(r'subprocess\.(call|run|Popen)\s*\(.*\+.*shell\s*=\s*True', re.IGNORECASE),
            severity='critical',
            description='Potential command injection via subprocess with shell=True',
            fix_suggestion='Use subprocess with list arguments and shell=False',
            languages=['python']
        ))
        
        patterns.append(InsecurePattern(
            name='command_injection_eval',
            pattern=re.compile(r'\beval\s*\(', re.IGNORECASE),
            severity='critical',
            description='Use of eval() can lead to code injection',
            fix_suggestion='Avoid eval(), use safer alternatives like ast.literal_eval',
            languages=['python', 'javascript']
        ))
        
        # Path Traversal patterns
        patterns.append(InsecurePattern(
            name='path_traversal',
            pattern=re.compile(r'open\s*\(.*\+.*["\']', re.IGNORECASE),
            severity='high',
            description='Potential path traversal vulnerability',
            fix_suggestion='Validate and sanitize file paths, use Path.resolve()',
            languages=['python', 'javascript']
        ))
        
        # Hardcoded Credentials patterns
        patterns.append(InsecurePattern(
            name='hardcoded_password',
            pattern=re.compile(r'(password|passwd|pwd)\s*=\s*["\'][^"\']{3,}["\']', re.IGNORECASE),
            severity='critical',
            description='Hardcoded password detected',
            fix_suggestion='Use environment variables or secure credential storage',
            languages=['python', 'javascript', 'java', 'csharp']
        ))
        
        patterns.append(InsecurePattern(
            name='hardcoded_api_key',
            pattern=re.compile(r'(api[_-]?key|apikey|api[_-]?secret)\s*=\s*["\'][a-zA-Z0-9]{20,}["\']', re.IGNORECASE),
            severity='critical',
            description='Hardcoded API key detected',
            fix_suggestion='Use environment variables or secret management',
            languages=['python', 'javascript', 'java', 'csharp']
        ))
        
        # Weak Cryptography patterns
        patterns.append(InsecurePattern(
            name='weak_hash_md5',
            pattern=re.compile(r'hashlib\.md5\s*\(', re.IGNORECASE),
            severity='medium',
            description='Use of weak MD5 hash algorithm',
            fix_suggestion='Use SHA-256 or stronger hash algorithms',
            languages=['python']
        ))
        
        patterns.append(InsecurePattern(
            name='weak_hash_sha1',
            pattern=re.compile(r'hashlib\.sha1\s*\(', re.IGNORECASE),
            severity='medium',
            description='Use of weak SHA-1 hash algorithm',
            fix_suggestion='Use SHA-256 or stronger hash algorithms',
            languages=['python']
        ))
        
        # Insecure Deserialization patterns
        patterns.append(InsecurePattern(
            name='insecure_pickle',
            pattern=re.compile(r'pickle\.loads?\s*\(', re.IGNORECASE),
            severity='high',
            description='Insecure deserialization with pickle',
            fix_suggestion='Use JSON or validate pickle data source',
            languages=['python']
        ))
        
        return patterns
    
    def detect(self, project_path: Path) -> List[SecurityIssue]:
        """
        Detect insecure patterns in project.
        
        Args:
            project_path: Path to project root
            
        Returns:
            List of security issues found
        """
        issues = []
        
        try:
            # Scan all source files
            for file_path in self._get_source_files(project_path):
                issues.extend(self._scan_file(file_path))
            
            logger.info(f"Pattern detection found {len(issues)} issues")
            return issues
            
        except Exception as e:
            logger.error(f"Error during pattern detection: {e}")
            return issues
    
    def _get_source_files(self, project_path: Path) -> List[Path]:
        """Get all source files to scan"""
        extensions = ['.py', '.js', '.ts', '.java', '.cs', '.cpp', '.c', '.php', '.rb']
        files = []
        
        for ext in extensions:
            files.extend(project_path.rglob(f'*{ext}'))
        
        # Filter out common directories to skip
        skip_dirs = {'node_modules', 'venv', '.venv', '__pycache__', 'build', 'dist', '.git'}
        files = [f for f in files if not any(skip in f.parts for skip in skip_dirs)]
        
        return files
    
    def _scan_file(self, file_path: Path) -> List[SecurityIssue]:
        """Scan a single file for insecure patterns"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Determine file language
            language = self._detect_language(file_path)
            
            # Check each pattern
            for pattern_def in self.patterns:
                if language not in pattern_def.languages:
                    continue
                
                # Search for pattern
                for line_num, line in enumerate(lines, 1):
                    if pattern_def.pattern.search(line):
                        issue = SecurityIssue(
                            severity=pattern_def.severity,
                            category='pattern',
                            title=pattern_def.name.replace('_', ' ').title(),
                            description=pattern_def.description,
                            file_path=str(file_path),
                            line_number=line_num,
                            fix_available=True,
                            fix_description=pattern_def.fix_suggestion
                        )
                        issues.append(issue)
        
        except Exception as e:
            logger.warning(f"Error scanning {file_path}: {e}")
        
        return issues
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        ext = file_path.suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cs': 'csharp',
            '.cpp': 'cpp',
            '.c': 'c',
            '.php': 'php',
            '.rb': 'ruby'
        }
        
        return language_map.get(ext, 'unknown')
