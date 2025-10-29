
"""
Generic Code Analyzer Agent

Fallback code analyzer for languages without specific implementations using LLM-based approaches.
"""

import re
from typing import Dict, Any, List

from ..base import CodeAnalyzerBase


class GenericCodeAnalyzer(CodeAnalyzerBase):
    """
    Generic code analyzer agent for any language.
    
    This agent provides fallback functionality for languages that don't
    have specific analysis implementations. It uses LLM-based analysis
    and generic code patterns.
    """
    
    def __init__(
        self,
        name: str = "code_analyzer_generic",
        description: str = "Generic code analyzer for any language",
        primary_language: str = "Generic",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            primary_language=primary_language,
            **kwargs
        )
    
    def _analyze_code_quality(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code quality using generic patterns and LLM.
        """
        issues = []
        score = 100
        
        # Generic quality checks
        lines = code.split('\n')
        
        # Check line length
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 120]
        if long_lines:
            issues.append({
                'type': 'style',
                'severity': 'warning',
                'message': f'Lines exceed 120 characters: {long_lines[:5]}',
                'lines': long_lines[:5]
            })
            score -= min(5, len(long_lines))
        
        # Check for TODO/FIXME comments
        todos = [i+1 for i, line in enumerate(lines) if 'TODO' in line.upper() or 'FIXME' in line.upper()]
        if todos:
            issues.append({
                'type': 'maintenance',
                'severity': 'info',
                'message': f'Found TODO/FIXME comments at lines: {todos[:5]}',
                'lines': todos[:5]
            })
        
        # Check for excessive nesting (simple indentation check)
        max_indent = 0
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent)
        
        if max_indent > 32:  # More than 8 levels with 4-space indent
            issues.append({
                'type': 'complexity',
                'severity': 'warning',
                'message': f'Excessive nesting detected (max indent: {max_indent} spaces)',
            })
            score -= 10
        
        # Use LLM for deeper analysis
        llm_analysis = self._llm_quality_check(code)
        if llm_analysis:
            issues.extend(llm_analysis.get('issues', []))
            # Adjust score based on LLM findings
            score = min(score, llm_analysis.get('score', score))
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': [
                'Keep functions/methods small and focused',
                'Use meaningful variable and function names',
                'Add comments for complex logic',
                'Follow consistent formatting style'
            ]
        }
    
    def _calculate_complexity(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate complexity metrics using generic patterns.
        """
        lines = code.split('\n')
        
        # Count non-blank, non-comment lines
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith(('#', '//', '/*', '*'))]
        loc = len(code_lines)
        
        # Count functions/methods (generic pattern)
        function_patterns = [
            r'\bfunction\s+\w+',  # JavaScript
            r'\bdef\s+\w+',       # Python, Ruby
            r'\b\w+\s+\w+\s*\([^)]*\)\s*\{',  # C, Java, C#
            r'\bsub\s+\w+',       # Perl
        ]
        
        functions = 0
        for pattern in function_patterns:
            functions += len(re.findall(pattern, code))
        
        # Count decision points (if, else, while, for, case, catch)
        decision_keywords = ['if', 'else', 'elif', 'while', 'for', 'switch', 'case', 'catch', 'except']
        cyclomatic = 1  # Base complexity
        
        for keyword in decision_keywords:
            # Count as whole words
            pattern = r'\b' + keyword + r'\b'
            cyclomatic += len(re.findall(pattern, code, re.IGNORECASE))
        
        # Calculate complexity score
        avg_complexity = cyclomatic / max(1, functions) if functions > 0 else cyclomatic
        
        complexity_score = 100
        if avg_complexity > 10:
            complexity_score -= 30
        elif avg_complexity > 5:
            complexity_score -= 15
        
        if loc > 1000:
            complexity_score -= 20
        elif loc > 500:
            complexity_score -= 10
        
        return {
            'score': max(0, complexity_score),
            'metrics': {
                'lines_of_code': loc,
                'functions': functions,
                'cyclomatic_complexity': cyclomatic,
                'average_complexity': round(avg_complexity, 2),
                'maintainability_index': self._calculate_maintainability(loc, cyclomatic, functions)
            },
            'issues': self._get_complexity_issues(loc, cyclomatic, avg_complexity),
            'recommendations': self._get_complexity_recommendations(loc, avg_complexity)
        }
    
    def _calculate_maintainability(self, loc: int, cyclomatic: int, functions: int) -> int:
        """Calculate maintainability index (0-100)."""
        # Simplified maintainability index
        if loc == 0:
            return 100
        
        volume = loc * 2.4  # Simplified Halstead volume
        mi = 171 - 5.2 * (volume ** 0.23) - 0.23 * cyclomatic - 16.2 * (loc ** 0.34)
        mi = max(0, min(100, mi))
        return int(mi)
    
    def _get_complexity_issues(self, loc: int, cyclomatic: int, avg_complexity: float) -> List[Dict[str, Any]]:
        """Get complexity-related issues."""
        issues = []
        
        if avg_complexity > 10:
            issues.append({
                'type': 'complexity',
                'severity': 'warning',
                'message': f'High average cyclomatic complexity: {avg_complexity:.2f} (threshold: 10)'
            })
        
        if loc > 1000:
            issues.append({
                'type': 'size',
                'severity': 'warning',
                'message': f'Large file: {loc} lines of code (consider splitting)'
            })
        
        return issues
    
    def _get_complexity_recommendations(self, loc: int, avg_complexity: float) -> List[str]:
        """Get complexity-related recommendations."""
        recommendations = []
        
        if avg_complexity > 10:
            recommendations.append('Break down complex functions into smaller, focused functions')
            recommendations.append('Use early returns to reduce nesting')
        
        if loc > 500:
            recommendations.append('Consider splitting this file into multiple modules')
        
        recommendations.append('Keep functions focused on a single responsibility')
        
        return recommendations
    
    def _check_security(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for common security issues using pattern matching.
        """
        issues = []
        score = 100
        
        # Common security anti-patterns
        security_patterns = [
            (r'eval\s*\(', 'Use of eval() - potential code injection', 'critical'),
            (r'exec\s*\(', 'Use of exec() - potential code injection', 'critical'),
            (r'password\s*=\s*["\']', 'Hardcoded password detected', 'critical'),
            (r'api[_-]?key\s*=\s*["\']', 'Hardcoded API key detected', 'critical'),
            (r'SELECT\s+.*\s+WHERE.*\+', 'Possible SQL injection vulnerability', 'critical'),
            (r'\.innerHTML\s*=', 'Use of innerHTML - XSS risk', 'warning'),
            (r'dangerouslySetInnerHTML', 'Use of dangerouslySetInnerHTML - XSS risk', 'warning'),
            (r'require\s*\(\s*[^"\']', 'Dynamic require() - potential security risk', 'warning'),
        ]
        
        for pattern, message, severity in security_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            match_lines = []
            for match in matches:
                # Find line number
                line_num = code[:match.start()].count('\n') + 1
                match_lines.append(line_num)
            
            if match_lines:
                issues.append({
                    'type': 'security',
                    'severity': severity,
                    'message': message,
                    'lines': match_lines
                })
                
                if severity == 'critical':
                    score -= 20
                else:
                    score -= 5
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': [
                'Never hardcode credentials or secrets',
                'Validate and sanitize all user inputs',
                'Use parameterized queries to prevent SQL injection',
                'Avoid eval() and exec() functions',
                'Keep dependencies up to date',
                'Follow OWASP security guidelines'
            ]
        }
    
    def _analyze_performance(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze potential performance issues.
        """
        issues = []
        score = 100
        
        # Common performance anti-patterns
        performance_patterns = [
            (r'for\s+.*\s+in\s+.*:\s*\n\s+for\s+.*\s+in', 'Nested loops - O(n²) complexity', 'warning'),
            (r'\.append\s*\(.*\)\s+for', 'List append in loop - consider list comprehension', 'info'),
            (r'sleep\s*\(', 'Sleep/blocking call detected', 'info'),
            (r'\+\s*=.*in\s+(for|while)', 'String concatenation in loop - use join()', 'warning'),
        ]
        
        for pattern, message, severity in performance_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            match_lines = []
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                match_lines.append(line_num)
            
            if match_lines:
                issues.append({
                    'type': 'performance',
                    'severity': severity,
                    'message': message,
                    'lines': match_lines
                })
                
                if severity == 'warning':
                    score -= 10
                else:
                    score -= 5
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': [
                'Optimize nested loops and reduce algorithmic complexity',
                'Use appropriate data structures for the task',
                'Avoid unnecessary object creation in loops',
                'Consider caching expensive computations',
                'Profile code to identify actual bottlenecks'
            ]
        }
    
    def _check_best_practices(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check adherence to general best practices.
        """
        issues = []
        score = 100
        
        lines = code.split('\n')
        
        # Check for documentation
        has_docstring = False
        docstring_patterns = [r'"""', r"'''", r'/\*\*', r'##']
        for pattern in docstring_patterns:
            if re.search(pattern, code):
                has_docstring = True
                break
        
        if not has_docstring:
            issues.append({
                'type': 'documentation',
                'severity': 'warning',
                'message': 'No documentation/docstrings found'
            })
            score -= 15
        
        # Check for magic numbers
        magic_numbers = re.findall(r'\b\d{2,}\b', code)
        if len(magic_numbers) > 5:
            issues.append({
                'type': 'maintainability',
                'severity': 'info',
                'message': f'Multiple magic numbers found ({len(magic_numbers)}) - consider using named constants'
            })
            score -= 5
        
        # Check for consistent naming (simple check)
        identifiers = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code)
        if identifiers:
            snake_case = sum(1 for i in identifiers if '_' in i and i.islower())
            camel_case = sum(1 for i in identifiers if i[0].islower() and any(c.isupper() for c in i[1:]))
            
            # If mixing styles significantly
            if snake_case > 10 and camel_case > 10:
                issues.append({
                    'type': 'style',
                    'severity': 'info',
                    'message': 'Mixed naming conventions detected (snake_case and camelCase)'
                })
                score -= 5
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': [
                'Add comprehensive documentation and comments',
                'Use named constants instead of magic numbers',
                'Follow consistent naming conventions',
                'Write unit tests for your code',
                'Use meaningful variable names',
                'Keep functions small and focused'
            ]
        }
    
    def _llm_quality_check(self, code: str) -> Dict[str, Any]:
        """
        Use LLM to perform deeper quality analysis.
        
        This is optional and only called if we want LLM-based insights.
        """
        # Limit code size for LLM analysis
        if len(code) > 2000:
            code = code[:2000] + "\n... (truncated)"
        
        prompt = f"""Analyze this code for quality issues:

```
{code}
```

Identify:
1. Code smells
2. Potential bugs
3. Design issues
4. Readability problems

Respond with JSON:
{{
    "score": 0-100,
    "issues": [
        {{"type": "type", "severity": "critical|warning|info", "message": "description"}}
    ]
}}
"""
        
        try:
            llm_result = self._get_llm_response(prompt, temperature=0.3)
            response = llm_result.get('response', '')
            
            # Try to parse JSON
            import json
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > 0:
                result = json.loads(response[json_start:json_end])
                return result
        except Exception as e:
            self.logger.warning(f"LLM quality check failed: {e}")
        
        return {'score': 100, 'issues': []}

