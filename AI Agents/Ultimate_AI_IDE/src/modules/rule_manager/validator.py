"""
Rule Validator

Validates code against rules.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from .manager import Rule, RuleCategory
import re


@dataclass
class Violation:
    """Rule violation."""
    rule_id: int
    rule_text: str
    severity: str  # 'low', 'medium', 'high'
    line_number: Optional[int]
    description: str
    suggestion: str


@dataclass
class ValidationResult:
    """Code validation result."""
    passed: bool
    violations: List[Violation]
    score: float  # 0-100


class RuleValidator:
    """Validates code against rules."""
    
    def __init__(self):
        """Initialize validator."""
        pass
    
    def validate_code(self, code: str, rules: List[Rule],
                     language: str = 'python') -> ValidationResult:
        """
        Validate code against rules.
        
        Args:
            code: Code to validate
            rules: List of rules to check
            language: Programming language
            
        Returns:
            ValidationResult
        """
        violations = []
        
        for rule in rules:
            rule_violations = self._check_rule(code, rule, language)
            violations.extend(rule_violations)
        
        # Calculate score
        max_violations = len(rules) * 2  # Assume max 2 violations per rule
        actual_violations = len(violations)
        score = max(0, 100 - (actual_violations / max(max_violations, 1)) * 100)
        
        passed = len(violations) == 0
        
        return ValidationResult(
            passed=passed,
            violations=violations,
            score=score
        )
    
    def _check_rule(self, code: str, rule: Rule, language: str) -> List[Violation]:
        """Check specific rule."""
        violations = []
        
        # Basic pattern matching for common rules
        if language == 'python':
            violations.extend(self._check_python_rules(code, rule))
        elif language in ['javascript', 'typescript']:
            violations.extend(self._check_js_rules(code, rule))
        
        return violations
    
    def _check_python_rules(self, code: str, rule: Rule) -> List[Violation]:
        """Check Python-specific rules."""
        violations = []
        lines = code.split('\n')
        
        # Check line length
        if 'line length' in rule.rule_text.lower():
            max_length = 100
            for i, line in enumerate(lines):
                if len(line) > max_length:
                    violations.append(Violation(
                        rule_id=rule.id,
                        rule_text=rule.rule_text,
                        severity='low',
                        line_number=i + 1,
                        description=f'Line exceeds {max_length} characters',
                        suggestion=f'Break line into multiple lines'
                    ))
        
        # Check for bare except
        if 'bare except' in rule.rule_text.lower():
            for i, line in enumerate(lines):
                if re.search(r'except\s*:', line):
                    violations.append(Violation(
                        rule_id=rule.id,
                        rule_text=rule.rule_text,
                        severity='medium',
                        line_number=i + 1,
                        description='Using bare except clause',
                        suggestion='Specify exception type: except ValueError:'
                    ))
        
        # Check for global variables
        if 'global variable' in rule.rule_text.lower():
            for i, line in enumerate(lines):
                if line.strip().startswith('global '):
                    violations.append(Violation(
                        rule_id=rule.id,
                        rule_text=rule.rule_text,
                        severity='medium',
                        line_number=i + 1,
                        description='Using global variable',
                        suggestion='Pass as parameter or use class attribute'
                    ))
        
        return violations
    
    def _check_js_rules(self, code: str, rule: Rule) -> List[Violation]:
        """Check JavaScript-specific rules."""
        violations = []
        lines = code.split('\n')
        
        # Check for var usage
        if 'never var' in rule.rule_text.lower():
            for i, line in enumerate(lines):
                if re.search(r'\bvar\s+', line):
                    violations.append(Violation(
                        rule_id=rule.id,
                        rule_text=rule.rule_text,
                        severity='medium',
                        line_number=i + 1,
                        description='Using var instead of const/let',
                        suggestion='Use const or let instead'
                    ))
        
        # Check for == usage
        if '===' in rule.rule_text:
            for i, line in enumerate(lines):
                if re.search(r'[^=!]==(?!=)', line):
                    violations.append(Violation(
                        rule_id=rule.id,
                        rule_text=rule.rule_text,
                        severity='low',
                        line_number=i + 1,
                        description='Using == instead of ===',
                        suggestion='Use === for strict equality'
                    ))
        
        return violations
    
    def format_violations(self, result: ValidationResult) -> str:
        """Format validation result as readable text."""
        if result.passed:
            return "✓ All rules passed!"
        
        text = f"Validation Score: {result.score:.1f}/100\n"
        text += f"Found {len(result.violations)} violation(s):\n\n"
        
        for violation in result.violations:
            text += f"[{violation.severity.upper()}] "
            if violation.line_number:
                text += f"Line {violation.line_number}: "
            text += f"{violation.description}\n"
            text += f"  Rule: {violation.rule_text}\n"
            text += f"  Suggestion: {violation.suggestion}\n\n"
        
        return text
