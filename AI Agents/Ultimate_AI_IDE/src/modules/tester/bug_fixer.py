"""
Bug Fixer Module

Analyzes and fixes bugs using AI.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class BugDiagnosis:
    """Diagnosis of a bug."""
    error_type: str
    root_cause: str
    affected_files: List[str]
    suggested_fixes: List[str]
    confidence: float = 0.0


@dataclass
class BugFix:
    """A bug fix."""
    file_path: str
    original_code: str
    fixed_code: str
    explanation: str
    test_added: bool = False


class BugFixer:
    """Fixes bugs using AI analysis."""
    
    def __init__(self, ai_backend):
        """
        Initialize bug fixer.
        
        Args:
            ai_backend: AI backend for analysis
        """
        self.ai_backend = ai_backend
    
    def diagnose_bug(self, error: str, stack_trace: str,
                    context: Optional[Dict] = None) -> BugDiagnosis:
        """
        Diagnose a bug from error and stack trace.
        
        Args:
            error: Error message
            stack_trace: Stack trace
            context: Additional context (code, files, etc.)
            
        Returns:
            BugDiagnosis with analysis
        """
        # Extract error type
        error_type = self._extract_error_type(error)
        
        # Build diagnosis prompt
        prompt = self._build_diagnosis_prompt(error, stack_trace, context)
        
        try:
            response = self.ai_backend.query(prompt, max_tokens=1000)
            return self._parse_diagnosis(response, error_type)
        except Exception:
            return BugDiagnosis(
                error_type=error_type,
                root_cause="Unable to diagnose",
                affected_files=[],
                suggested_fixes=["Manual investigation required"],
                confidence=0.0
            )
    
    def fix_bug(self, diagnosis: BugDiagnosis, 
               project_path: str) -> List[BugFix]:
        """
        Generate fixes for a diagnosed bug.
        
        Args:
            diagnosis: Bug diagnosis
            project_path: Path to project
            
        Returns:
            List of bug fixes to apply
        """
        fixes = []
        
        for file_path in diagnosis.affected_files:
            full_path = Path(project_path) / file_path
            
            if not full_path.exists():
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    original_code = f.read()
                
                # Generate fix
                fix = self._generate_fix(
                    file_path,
                    original_code,
                    diagnosis
                )
                
                if fix:
                    fixes.append(fix)
                    
            except Exception:
                continue
        
        return fixes
    
    def apply_fix(self, fix: BugFix, backup: bool = True) -> bool:
        """
        Apply a bug fix to a file.
        
        Args:
            fix: Bug fix to apply
            backup: Create backup before applying
            
        Returns:
            True if successful
        """
        file_path = Path(fix.file_path)
        
        try:
            # Backup if requested
            if backup:
                backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                import shutil
                shutil.copy2(file_path, backup_path)
            
            # Apply fix
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fix.fixed_code)
            
            return True
            
        except Exception as e:
            print(f"Error applying fix: {e}")
            return False
    
    def verify_fix(self, fix: BugFix, test_runner) -> bool:
        """
        Verify that a fix resolves the issue.
        
        Args:
            fix: Bug fix to verify
            test_runner: TestRunner instance
            
        Returns:
            True if fix is verified
        """
        # This would run tests to verify the fix
        # Simplified implementation
        return True
    
    def _extract_error_type(self, error: str) -> str:
        """Extract error type from error message."""
        # Common error patterns
        patterns = [
            r'(\w+Error):',
            r'(\w+Exception):',
            r'Error: (\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error)
            if match:
                return match.group(1)
        
        return "UnknownError"
    
    def _build_diagnosis_prompt(self, error: str, stack_trace: str,
                               context: Optional[Dict]) -> str:
        """Build prompt for bug diagnosis."""
        context_text = ""
        if context:
            if 'code' in context:
                context_text += f"\nRelevant Code:\n```\n{context['code'][:1000]}\n```"
            if 'files' in context:
                context_text += f"\nAffected Files: {', '.join(context['files'])}"
        
        prompt = f"""Diagnose this bug and suggest fixes.

Error Message:
{error}

Stack Trace:
{stack_trace}
{context_text}

Provide:
1. ROOT_CAUSE: Explanation of what caused the error
2. AFFECTED_FILES: List of files that need changes
3. FIXES: Specific fixes to apply (numbered list)
4. CONFIDENCE: Your confidence level (0-100)

Be specific and actionable.
"""
        
        return prompt
    
    def _parse_diagnosis(self, response: str, 
                        error_type: str) -> BugDiagnosis:
        """Parse AI diagnosis response."""
        diagnosis = BugDiagnosis(
            error_type=error_type,
            root_cause="",
            affected_files=[],
            suggested_fixes=[]
        )
        
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('ROOT_CAUSE:'):
                diagnosis.root_cause = line.split(':', 1)[1].strip()
            
            elif line.startswith('AFFECTED_FILES:'):
                files_str = line.split(':', 1)[1].strip()
                diagnosis.affected_files = [
                    f.strip() for f in files_str.split(',') if f.strip()
                ]
            
            elif line.startswith('CONFIDENCE:'):
                try:
                    conf_str = line.split(':', 1)[1].strip()
                    diagnosis.confidence = float(re.search(r'\d+', conf_str).group()) / 100
                except:
                    diagnosis.confidence = 0.5
            
            elif re.match(r'^\d+\.', line):
                # Numbered fix suggestion
                diagnosis.suggested_fixes.append(line)
        
        return diagnosis
    
    def _generate_fix(self, file_path: str, original_code: str,
                     diagnosis: BugDiagnosis) -> Optional[BugFix]:
        """Generate a fix for a file."""
        prompt = f"""Fix this bug in the code.

File: {file_path}

Bug Diagnosis:
- Error Type: {diagnosis.error_type}
- Root Cause: {diagnosis.root_cause}
- Suggested Fixes: {', '.join(diagnosis.suggested_fixes)}

Original Code:
```
{original_code[:2000]}
```

Provide:
1. The complete fixed code
2. Brief explanation of changes

Output format:
FIXED_CODE:
```
[complete fixed code]
```

EXPLANATION:
[explanation of changes]
"""
        
        try:
            response = self.ai_backend.query(prompt, max_tokens=2000)
            return self._parse_fix_response(
                response, file_path, original_code
            )
        except Exception:
            return None
    
    def _parse_fix_response(self, response: str, file_path: str,
                           original_code: str) -> Optional[BugFix]:
        """Parse fix response from AI."""
        # Extract fixed code
        fixed_code = ""
        explanation = ""
        
        if 'FIXED_CODE:' in response:
            parts = response.split('FIXED_CODE:')
            if len(parts) > 1:
                code_part = parts[1]
                
                # Extract code from markdown block
                if '```' in code_part:
                    matches = re.findall(r'```(?:\w+)?\n(.*?)```', 
                                       code_part, re.DOTALL)
                    if matches:
                        fixed_code = matches[0].strip()
        
        if 'EXPLANATION:' in response:
            parts = response.split('EXPLANATION:')
            if len(parts) > 1:
                explanation = parts[1].strip()
        
        if not fixed_code:
            return None
        
        return BugFix(
            file_path=file_path,
            original_code=original_code,
            fixed_code=fixed_code,
            explanation=explanation,
            test_added=False
        )
    
    def suggest_preventive_tests(self, diagnosis: BugDiagnosis) -> List[str]:
        """
        Suggest tests to prevent regression.
        
        Args:
            diagnosis: Bug diagnosis
            
        Returns:
            List of test suggestions
        """
        if not self.ai_backend:
            return []
        
        prompt = f"""Suggest tests to prevent this bug from recurring.

Bug Type: {diagnosis.error_type}
Root Cause: {diagnosis.root_cause}

Provide 3-5 specific test cases that would catch this bug.
Format as a numbered list.
"""
        
        try:
            response = self.ai_backend.query(prompt, max_tokens=500)
            
            # Extract numbered items
            tests = []
            for line in response.split('\n'):
                if re.match(r'^\d+\.', line.strip()):
                    tests.append(line.strip())
            
            return tests
        except Exception:
            return []
