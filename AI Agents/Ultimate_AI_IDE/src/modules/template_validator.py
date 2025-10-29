"""
Template Validator Module

Validates scaffolded projects to ensure zero-bloat principle.
Detects example code, TODOs, placeholders, and unnecessary dependencies.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """Represents a validation issue found in code"""
    file_path: str
    line_number: int
    issue_type: str  # example_code, todo, placeholder, unused_dependency
    description: str
    severity: str  # high, medium, low
    suggestion: str


class TemplateValidator:
    """
    Validates scaffolded projects for bloat and incomplete code.
    
    Detects:
    - Example/demo code
    - TODO/FIXME comments
    - Placeholder implementations
    - Unnecessary dependencies
    """
    
    def __init__(self, project_path: str):
        """
        Initialize template validator.
        
        Args:
            project_path: Path to project root
        """
        self.project_path = Path(project_path)
        self.issues: List[ValidationIssue] = []
        
        # Patterns for detection
        self.example_patterns = [
            r'example',
            r'demo',
            r'sample',
            r'test_data',
            r'dummy',
            r'mock_.*',
            r'fake_.*'
        ]
        
        self.todo_patterns = [
            r'TODO',
            r'FIXME',
            r'XXX',
            r'HACK',
            r'NOTE:.*implement',
            r'placeholder'
        ]
        
        self.placeholder_patterns = [
            r'pass\s*$',
            r'raise NotImplementedError',
            r'\.\.\.(\s*#.*)?$',  # Ellipsis
            r'return None\s*#.*placeholder',
            r'def.*:\s*pass',
            r'class.*:\s*pass'
        ]
    
    def validate_project(self) -> Dict[str, Any]:
        """
        Validate entire project.
        
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Validating project: {self.project_path}")
        self.issues = []
        
        # Scan source files
        source_files = self._get_source_files()
        for file_path in source_files:
            self._validate_file(file_path)
        
        # Check dependencies
        self._validate_dependencies()
        
        # Generate summary
        summary = self._generate_summary()
        
        return {
            'total_issues': len(self.issues),
            'issues': self.issues,
            'summary': summary,
            'is_clean': len(self.issues) == 0
        }
    
    def _get_source_files(self) -> List[Path]:
        """Get all source files to validate"""
        extensions = ['.py', '.js', '.ts', '.java', '.cs', '.cpp', '.c']
        files = []
        
        for ext in extensions:
            files.extend(self.project_path.rglob(f'*{ext}'))
        
        # Filter out common directories to skip
        skip_dirs = {'node_modules', 'venv', '.venv', '__pycache__', 'build', 'dist', '.git', 'tests', 'test'}
        files = [f for f in files if not any(skip in f.parts for skip in skip_dirs)]
        
        return files
    
    def _validate_file(self, file_path: Path):
        """Validate a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Check for example code
                self._check_example_code(file_path, line_num, line)
                
                # Check for TODOs
                self._check_todos(file_path, line_num, line)
                
                # Check for placeholders
                self._check_placeholders(file_path, line_num, line)
        
        except Exception as e:
            logger.warning(f"Error validating {file_path}: {e}")
    
    def _check_example_code(self, file_path: Path, line_num: int, line: str):
        """Check for example/demo code"""
        line_lower = line.lower()
        
        for pattern in self.example_patterns:
            if re.search(pattern, line_lower):
                # Skip comments that are just documentation
                if line.strip().startswith('#') or line.strip().startswith('//'):
                    continue
                
                self.issues.append(ValidationIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    issue_type='example_code',
                    description=f"Potential example/demo code: {line.strip()[:50]}",
                    severity='high',
                    suggestion="Remove example code and replace with production implementation"
                ))
                break
    
    def _check_todos(self, file_path: Path, line_num: int, line: str):
        """Check for TODO/FIXME comments"""
        for pattern in self.todo_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    issue_type='todo',
                    description=f"Incomplete code marker: {line.strip()[:50]}",
                    severity='medium',
                    suggestion="Complete the implementation or remove the TODO"
                ))
                break
    
    def _check_placeholders(self, file_path: Path, line_num: int, line: str):
        """Check for placeholder implementations"""
        line_stripped = line.strip()
        
        for pattern in self.placeholder_patterns:
            if re.search(pattern, line_stripped):
                # Skip if it's a valid use of pass (like in except blocks)
                if 'except' in line or 'finally' in line:
                    continue
                
                self.issues.append(ValidationIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    issue_type='placeholder',
                    description=f"Placeholder implementation: {line.strip()[:50]}",
                    severity='high',
                    suggestion="Replace placeholder with actual implementation"
                ))
                break
    
    def _validate_dependencies(self):
        """Check for unnecessary dependencies"""
        # Check requirements.txt
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            self._check_python_dependencies(req_file)
        
        # Check package.json
        pkg_file = self.project_path / "package.json"
        if pkg_file.exists():
            self._check_npm_dependencies(pkg_file)
    
    def _check_python_dependencies(self, req_file: Path):
        """Check Python dependencies for unnecessary packages"""
        try:
            content = req_file.read_text()
            lines = content.split('\n')
            
            # Common example/test dependencies that shouldn't be in production
            unnecessary = ['faker', 'factory-boy', 'hypothesis', 'mock']
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip().lower()
                for dep in unnecessary:
                    if dep in line and not line.startswith('#'):
                        self.issues.append(ValidationIssue(
                            file_path=str(req_file),
                            line_number=line_num,
                            issue_type='unused_dependency',
                            description=f"Potentially unnecessary dependency: {line}",
                            severity='medium',
                            suggestion=f"Move {dep} to dev dependencies or remove if not needed"
                        ))
        
        except Exception as e:
            logger.warning(f"Error checking Python dependencies: {e}")
    
    def _check_npm_dependencies(self, pkg_file: Path):
        """Check npm dependencies for unnecessary packages"""
        try:
            import json
            content = json.loads(pkg_file.read_text())
            
            # Common example/test dependencies
            unnecessary = ['faker', 'chance', 'casual']
            
            deps = content.get('dependencies', {})
            for dep_name in deps:
                if any(unnecessary_dep in dep_name.lower() for unnecessary_dep in unnecessary):
                    self.issues.append(ValidationIssue(
                        file_path=str(pkg_file),
                        line_number=0,
                        issue_type='unused_dependency',
                        description=f"Potentially unnecessary dependency: {dep_name}",
                        severity='medium',
                        suggestion=f"Move {dep_name} to devDependencies or remove if not needed"
                    ))
        
        except Exception as e:
            logger.warning(f"Error checking npm dependencies: {e}")
    
    def _generate_summary(self) -> Dict[str, int]:
        """Generate summary of issues by type and severity"""
        summary = {
            'example_code': 0,
            'todo': 0,
            'placeholder': 0,
            'unused_dependency': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for issue in self.issues:
            summary[issue.issue_type] += 1
            summary[issue.severity] += 1
        
        return summary
    
    def get_clean_score(self) -> float:
        """
        Calculate cleanliness score (0-100).
        
        Returns:
            Score where 100 = perfectly clean, 0 = many issues
        """
        if not self.issues:
            return 100.0
        
        # Weight by severity
        penalty = 0
        for issue in self.issues:
            if issue.severity == 'high':
                penalty += 10
            elif issue.severity == 'medium':
                penalty += 5
            else:
                penalty += 2
        
        score = max(0, 100 - penalty)
        return score
