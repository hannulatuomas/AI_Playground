"""
Code Analysis Module

Analyzes feature requests and existing code.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field


@dataclass
class FeaturePlan:
    """Plan for implementing a feature."""
    description: str
    affected_files: List[str] = field(default_factory=list)
    new_files: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    classes_to_create: List[str] = field(default_factory=list)
    functions_to_create: List[str] = field(default_factory=list)
    imports_needed: List[str] = field(default_factory=list)
    estimated_lines: int = 0
    modular: bool = True


@dataclass
class CodeContext:
    """Context about existing code."""
    project_path: str
    language: str
    framework: Optional[str] = None
    existing_classes: List[str] = field(default_factory=list)
    existing_functions: List[str] = field(default_factory=list)
    existing_files: List[str] = field(default_factory=list)
    imports: Set[str] = field(default_factory=set)


class CodeAnalyzer:
    """Analyzes code and feature requests."""
    
    def __init__(self, ai_backend=None):
        """
        Initialize analyzer.
        
        Args:
            ai_backend: AI backend for intelligent analysis
        """
        self.ai_backend = ai_backend
    
    def analyze_request(self, description: str, 
                       context: CodeContext) -> FeaturePlan:
        """
        Analyze a feature request and create implementation plan.
        
        Args:
            description: Feature description from user
            context: Current code context
            
        Returns:
            FeaturePlan with implementation details
        """
        plan = FeaturePlan(description=description)
        
        # Use AI to analyze if available
        if self.ai_backend:
            plan = self._ai_analyze_request(description, context)
        else:
            # Basic analysis without AI
            plan = self._basic_analyze_request(description, context)
        
        # Ensure modularity (files under 500 lines)
        if plan.estimated_lines > 500:
            plan.modular = False
            # Should split into multiple files
        
        return plan
    
    def get_code_context(self, project_path: str, 
                        language: str) -> CodeContext:
        """
        Extract context from existing code.
        
        Args:
            project_path: Path to project
            language: Programming language
            
        Returns:
            CodeContext with existing code information
        """
        context = CodeContext(
            project_path=project_path,
            language=language
        )
        
        project = Path(project_path)
        
        # Find all code files
        extensions = self._get_extensions_for_language(language)
        
        for ext in extensions:
            for file_path in project.rglob(f'*{ext}'):
                if self._should_analyze_file(file_path):
                    context.existing_files.append(str(file_path))
                    self._extract_symbols(file_path, context)
        
        return context
    
    def check_duplicates(self, code: str, context: CodeContext) -> List[Dict]:
        """
        Check for duplicate or similar code.
        
        Args:
            code: Code to check
            context: Project context
            
        Returns:
            List of potential duplicates with similarity scores
        """
        duplicates = []
        
        # Extract key identifiers from new code
        identifiers = self._extract_identifiers(code, context.language)
        
        # Check against existing code
        for file_path in context.existing_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_code = f.read()
                    
                similarity = self._calculate_similarity(code, existing_code)
                
                if similarity > 0.7:  # 70% similar
                    duplicates.append({
                        'file': file_path,
                        'similarity': similarity,
                        'suggestion': 'Consider refactoring or reusing existing code'
                    })
            except Exception:
                continue
        
        return duplicates
    
    def _ai_analyze_request(self, description: str, 
                           context: CodeContext) -> FeaturePlan:
        """Use AI to analyze feature request."""
        prompt = f"""Analyze this feature request and create an implementation plan.

Feature Request: {description}

Project Context:
- Language: {context.language}
- Framework: {context.framework or 'None'}
- Existing Classes: {', '.join(context.existing_classes[:10])}
- Existing Functions: {', '.join(context.existing_functions[:10])}

Create a plan including:
1. Files to create or modify
2. Classes and functions needed
3. Dependencies required
4. Estimated lines of code
5. Keep files under 500 lines (modular design)

Output format:
FILES_TO_MODIFY: [list]
NEW_FILES: [list]
CLASSES: [list]
FUNCTIONS: [list]
DEPENDENCIES: [list]
ESTIMATED_LINES: [number]
"""
        
        try:
            response = self.ai_backend.query(prompt, max_tokens=800)
            return self._parse_ai_response(response, description)
        except Exception:
            # Fallback to basic analysis
            return self._basic_analyze_request(description, context)
    
    def _basic_analyze_request(self, description: str, 
                               context: CodeContext) -> FeaturePlan:
        """Basic analysis without AI."""
        plan = FeaturePlan(description=description)
        
        # Simple heuristics
        desc_lower = description.lower()
        
        # Detect if creating new feature
        if 'create' in desc_lower or 'add' in desc_lower or 'new' in desc_lower:
            # Estimate new file needed
            if 'class' in desc_lower:
                plan.new_files.append('new_module.py')
                plan.estimated_lines = 100
            elif 'function' in desc_lower:
                plan.estimated_lines = 50
        
        # Detect if modifying existing
        if 'modify' in desc_lower or 'update' in desc_lower or 'change' in desc_lower:
            # Would need to identify which files
            plan.estimated_lines = 50
        
        return plan
    
    def _parse_ai_response(self, response: str, 
                          description: str) -> FeaturePlan:
        """Parse AI response into FeaturePlan."""
        plan = FeaturePlan(description=description)
        
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('FILES_TO_MODIFY:'):
                files = line.split(':', 1)[1].strip()
                plan.affected_files = [f.strip() for f in files.split(',') if f.strip()]
            
            elif line.startswith('NEW_FILES:'):
                files = line.split(':', 1)[1].strip()
                plan.new_files = [f.strip() for f in files.split(',') if f.strip()]
            
            elif line.startswith('CLASSES:'):
                classes = line.split(':', 1)[1].strip()
                plan.classes_to_create = [c.strip() for c in classes.split(',') if c.strip()]
            
            elif line.startswith('FUNCTIONS:'):
                funcs = line.split(':', 1)[1].strip()
                plan.functions_to_create = [f.strip() for f in funcs.split(',') if f.strip()]
            
            elif line.startswith('DEPENDENCIES:'):
                deps = line.split(':', 1)[1].strip()
                plan.dependencies = [d.strip() for d in deps.split(',') if d.strip()]
            
            elif line.startswith('ESTIMATED_LINES:'):
                try:
                    lines_str = line.split(':', 1)[1].strip()
                    plan.estimated_lines = int(re.search(r'\d+', lines_str).group())
                except:
                    plan.estimated_lines = 100
        
        return plan
    
    def _get_extensions_for_language(self, language: str) -> List[str]:
        """Get file extensions for a language."""
        extensions_map = {
            'python': ['.py'],
            'javascript': ['.js', '.mjs', '.cjs'],
            'typescript': ['.ts', '.tsx'],
            'csharp': ['.cs'],
            'cpp': ['.cpp', '.cc', '.cxx', '.hpp', '.h'],
            'java': ['.java'],
            'go': ['.go'],
            'rust': ['.rs'],
        }
        return extensions_map.get(language, ['.txt'])
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """Check if file should be analyzed."""
        # Skip test files, migrations, etc.
        path_str = str(file_path).lower()
        filename = file_path.name.lower()
        
        # Skip by directory patterns
        dir_skip_patterns = [
            'tests/', '__pycache__',
            'node_modules/', 'venv/', 'env/', '.git/',
            'migrations/', 'dist/', 'build/'
        ]
        
        for pattern in dir_skip_patterns:
            if pattern in path_str:
                return False
        
        # Skip by filename patterns
        if filename.startswith('test_') or filename.endswith('_test.py'):
            return False
        
        return True
    
    def _extract_symbols(self, file_path: Path, context: CodeContext):
        """Extract classes and functions from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if context.language == 'python':
                # Extract Python classes
                classes = re.findall(r'class\s+(\w+)', content)
                context.existing_classes.extend(classes)
                
                # Extract Python functions
                functions = re.findall(r'def\s+(\w+)', content)
                context.existing_functions.extend(functions)
                
                # Extract imports
                imports = re.findall(r'(?:from\s+[\w.]+\s+)?import\s+([\w,\s]+)', content)
                for imp in imports:
                    context.imports.update(i.strip() for i in imp.split(','))
            
            elif context.language in ['javascript', 'typescript']:
                # Extract JS/TS classes
                classes = re.findall(r'class\s+(\w+)', content)
                context.existing_classes.extend(classes)
                
                # Extract functions
                functions = re.findall(r'function\s+(\w+)', content)
                context.existing_functions.extend(functions)
                
                # Extract arrow functions and methods
                arrow_funcs = re.findall(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(', content)
                context.existing_functions.extend(arrow_funcs)
            
            elif context.language == 'csharp':
                # Extract C# classes
                classes = re.findall(r'class\s+(\w+)', content)
                context.existing_classes.extend(classes)
                
                # Extract methods
                methods = re.findall(r'(?:public|private|protected|internal)\s+(?:static\s+)?(?:async\s+)?\w+\s+(\w+)\s*\(', content)
                context.existing_functions.extend(methods)
        
        except Exception:
            pass  # Skip files that can't be read
    
    def _extract_identifiers(self, code: str, language: str) -> Set[str]:
        """Extract identifiers from code."""
        identifiers = set()
        
        # Extract class names
        classes = re.findall(r'class\s+(\w+)', code)
        identifiers.update(classes)
        
        # Extract function names
        if language == 'python':
            functions = re.findall(r'def\s+(\w+)', code)
        else:
            functions = re.findall(r'function\s+(\w+)', code)
        
        identifiers.update(functions)
        
        return identifiers
    
    def _calculate_similarity(self, code1: str, code2: str) -> float:
        """Calculate similarity between two code snippets."""
        # Simple similarity based on common lines
        lines1 = set(line.strip() for line in code1.split('\n') 
                    if line.strip() and not line.strip().startswith('#'))
        lines2 = set(line.strip() for line in code2.split('\n') 
                    if line.strip() and not line.strip().startswith('#'))
        
        if not lines1 or not lines2:
            return 0.0
        
        common = lines1.intersection(lines2)
        return len(common) / max(len(lines1), len(lines2))
