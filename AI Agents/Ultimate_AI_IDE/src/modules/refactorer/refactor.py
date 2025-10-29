"""
Code Refactorer

Refactors code to improve quality using AI.
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from .analyzer import CodeAnalyzer, AnalysisReport


@dataclass
class RefactoredCode:
    """Refactored code result."""
    original_file: str
    refactored_content: str
    changes_made: List[str]
    improvements: List[str]


class CodeRefactorer:
    """Refactors code using AI backend."""
    
    def __init__(self, ai_backend, project_rules: Optional[List[str]] = None):
        """
        Initialize code refactorer.
        
        Args:
            ai_backend: AI backend for refactoring
            project_rules: Project-specific coding rules
        """
        self.ai_backend = ai_backend
        self.project_rules = project_rules or []
        self.analyzer = CodeAnalyzer()
    
    def refactor_file(self, file_path: str, language: str = 'python',
                     focus: Optional[str] = None) -> Optional[RefactoredCode]:
        """
        Refactor a code file.
        
        Args:
            file_path: Path to file
            language: Programming language
            focus: Specific focus
            
        Returns:
            RefactoredCode with improvements
        """
        path = Path(file_path)
        
        if not path.exists():
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        analysis = self.analyzer.analyze_code(file_path, language)
        
        prompt = self._build_refactoring_prompt(
            original_content, language, analysis, focus
        )
        
        try:
            refactored = self.ai_backend.query(prompt, max_tokens=3000)
            refactored = self._clean_code(refactored, language)
            
            changes = self._identify_changes(original_content, refactored)
            improvements = self._identify_improvements(analysis)
            
            return RefactoredCode(
                original_file=file_path,
                refactored_content=refactored,
                changes_made=changes,
                improvements=improvements
            )
        except Exception as e:
            print(f"Error refactoring {file_path}: {e}")
            return None
    
    def improve_code(self, code: str, language: str = 'python') -> str:
        """
        Improve code snippet.
        
        Args:
            code: Code to improve
            language: Programming language
            
        Returns:
            Improved code
        """
        prompt = self._build_improvement_prompt(code, language)
        
        try:
            improved = self.ai_backend.query(prompt, max_tokens=2000)
            return self._clean_code(improved, language)
        except Exception as e:
            print(f"Error improving code: {e}")
            return code
    
    def _build_refactoring_prompt(self, code: str, language: str,
                                  analysis: AnalysisReport,
                                  focus: Optional[str]) -> str:
        """Build prompt for code refactoring."""
        rules_text = "\n".join(self.project_rules) if self.project_rules else ""
        
        issues = []
        for smell in analysis.code_smells:
            issues.append(f"- {smell.description}: {smell.suggestion}")
        
        issues_text = "\n".join(issues[:10]) if issues else "No major issues"
        
        prompt = f"""Refactor this {language} code following best practices:

Code:
```{language}
{code}
```

Analysis Results:
- Lines of code: {analysis.metrics.lines_of_code}
- Cyclomatic complexity: {analysis.metrics.cyclomatic_complexity}
- Code smells found: {len(analysis.code_smells)}

Issues to address:
{issues_text}

Requirements:
- Improve readability
- Reduce complexity
- Remove duplication
- Add type hints (if {language} supports)
- Improve naming
- Keep modular (max 500 lines)
- Maintain functionality
- Add comments for complex logic
{f'- Focus on: {focus}' if focus else ''}

{f'Project Rules: {rules_text}' if rules_text else ''}

Generate only the refactored code, no explanations."""
        
        return prompt
    
    def _build_improvement_prompt(self, code: str, language: str) -> str:
        """Build prompt for code improvement."""
        rules_text = "\n".join(self.project_rules) if self.project_rules else ""
        
        prompt = f"""Improve this {language} code:

```{language}
{code}
```

Apply these improvements:
- Better variable/function names
- Add type hints
- Improve structure
- Add docstrings
- Remove redundancy
- Optimize algorithms

{f'Follow these rules: {rules_text}' if rules_text else ''}

Generate only the improved code."""
        
        return prompt
    
    def _clean_code(self, code: str, language: str) -> str:
        """Clean up generated code."""
        if code.startswith('```'):
            lines = code.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            code = '\n'.join(lines)
        
        return code.strip()
    
    def _identify_changes(self, original: str, refactored: str) -> List[str]:
        """Identify changes made during refactoring."""
        changes = []
        
        orig_lines = original.split('\n')
        ref_lines = refactored.split('\n')
        
        if len(ref_lines) < len(orig_lines):
            changes.append(f"Reduced from {len(orig_lines)} to {len(ref_lines)} lines")
        
        if 'def ' in refactored and refactored.count('"""') > original.count('"""'):
            changes.append("Added docstrings")
        
        if '->' in refactored and '->' not in original:
            changes.append("Added type hints")
        
        return changes if changes else ["Code refactored"]
    
    def _identify_improvements(self, analysis: AnalysisReport) -> List[str]:
        """Identify improvements from analysis."""
        improvements = []
        
        for smell in analysis.code_smells:
            improvements.append(smell.suggestion)
        
        if analysis.optimization_opportunities:
            improvements.extend(analysis.optimization_opportunities)
        
        return improvements[:5]
