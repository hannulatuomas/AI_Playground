"""
Code Summarizer

Generates concise summaries of code files for context management.
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import ast
import re


@dataclass
class CodeSummary:
    """Summary of a code file."""
    file_path: str
    language: str
    purpose: str
    classes: List[Dict[str, str]]  # [{name, description, methods}]
    functions: List[Dict[str, str]]  # [{name, signature, description}]
    imports: List[str]
    key_structures: List[str]
    complexity: str  # 'low', 'medium', 'high'
    lines_of_code: int


class CodeSummarizer:
    """Generates summaries of code files."""
    
    def __init__(self, ai_backend):
        """
        Initialize code summarizer.
        
        Args:
            ai_backend: AI backend for generating summaries
        """
        self.ai_backend = ai_backend
    
    def summarize_file(self, file_path: str, language: str = 'python') -> CodeSummary:
        """
        Generate summary of a code file.
        
        Args:
            file_path: Path to code file
            language: Programming language
            
        Returns:
            CodeSummary object
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if language == 'python':
            return self._summarize_python(file_path, content)
        elif language in ['javascript', 'typescript']:
            return self._summarize_js(file_path, content)
        else:
            return self._summarize_generic(file_path, content, language)
    
    def _summarize_python(self, file_path: str, content: str) -> CodeSummary:
        """Summarize Python file."""
        lines = content.split('\n')
        loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        
        # Extract structure using AST
        try:
            tree = ast.parse(content)
            
            # Extract imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # Extract classes
            classes = []
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    classes.append({
                        'name': node.name,
                        'description': ast.get_docstring(node) or 'No description',
                        'methods': ', '.join(methods[:5])  # Limit to 5 methods
                    })
            
            # Extract functions
            functions = []
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.FunctionDef):
                    # Get signature
                    args = [arg.arg for arg in node.args.args if arg.arg not in ['self', 'cls']]
                    signature = f"{node.name}({', '.join(args)})"
                    
                    functions.append({
                        'name': node.name,
                        'signature': signature,
                        'description': (ast.get_docstring(node) or 'No description')[:100]
                    })
            
            # Get module docstring as purpose
            purpose = ast.get_docstring(tree) or "No description available"
            
            # Determine complexity
            complexity = 'low'
            if loc > 300 or len(classes) > 5:
                complexity = 'high'
            elif loc > 100 or len(classes) > 2:
                complexity = 'medium'
            
            return CodeSummary(
                file_path=file_path,
                language='python',
                purpose=purpose[:200],
                classes=classes,
                functions=functions,
                imports=imports[:10],  # Limit to 10 imports
                key_structures=[],
                complexity=complexity,
                lines_of_code=loc
            )
            
        except SyntaxError:
            # Fallback for files with syntax errors
            return self._summarize_generic(file_path, content, 'python')
    
    def _summarize_js(self, file_path: str, content: str) -> CodeSummary:
        """Summarize JavaScript/TypeScript file."""
        lines = content.split('\n')
        loc = len([l for l in lines if l.strip() and not l.strip().startswith('//')])
        
        # Extract imports (basic regex)
        imports = []
        import_pattern = r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]'
        imports = re.findall(import_pattern, content)
        
        # Extract classes
        classes = []
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            classes.append({
                'name': match.group(1),
                'description': 'JavaScript class',
                'methods': ''
            })
        
        # Extract functions
        functions = []
        func_pattern = r'(?:function|const|let|var)\s+(\w+)\s*=?\s*(?:async\s*)?\([^)]*\)'
        for match in re.finditer(func_pattern, content):
            functions.append({
                'name': match.group(1),
                'signature': match.group(0)[:50],
                'description': 'Function'
            })
        
        # Get purpose from first comment
        purpose_match = re.search(r'/\*\*\s*(.*?)\s*\*/', content, re.DOTALL)
        purpose = purpose_match.group(1)[:200] if purpose_match else "No description"
        
        complexity = 'medium' if loc > 100 else 'low'
        
        return CodeSummary(
            file_path=file_path,
            language='javascript',
            purpose=purpose,
            classes=classes,
            functions=functions[:10],
            imports=imports[:10],
            key_structures=[],
            complexity=complexity,
            lines_of_code=loc
        )
    
    def _summarize_generic(self, file_path: str, content: str, 
                          language: str) -> CodeSummary:
        """Generic summary for unsupported languages."""
        lines = content.split('\n')
        loc = len([l for l in lines if l.strip()])
        
        # Use AI to generate summary
        summary_text = self._ai_summarize(content, language)
        
        return CodeSummary(
            file_path=file_path,
            language=language,
            purpose=summary_text[:200],
            classes=[],
            functions=[],
            imports=[],
            key_structures=[],
            complexity='medium',
            lines_of_code=loc
        )
    
    def _ai_summarize(self, content: str, language: str) -> str:
        """Use AI to generate summary."""
        # Truncate content if too long
        if len(content) > 4000:
            content = content[:4000] + "\n... (truncated)"
        
        prompt = f"""Summarize this {language} code file briefly:

{content}

Provide a 1-2 sentence summary of what this file does.
Focus on the main purpose and key functionality."""
        
        try:
            summary = self.ai_backend.query(prompt, max_tokens=200)
            return summary.strip()
        except Exception as e:
            return f"Code file ({language})"
    
    def format_summary(self, summary: CodeSummary) -> str:
        """
        Format summary as readable text.
        
        Args:
            summary: CodeSummary object
            
        Returns:
            Formatted string
        """
        text = f"File: {summary.file_path}\n"
        text += f"Language: {summary.language}\n"
        text += f"Purpose: {summary.purpose}\n"
        text += f"Lines of Code: {summary.lines_of_code}\n"
        text += f"Complexity: {summary.complexity}\n\n"
        
        if summary.classes:
            text += "Classes:\n"
            for cls in summary.classes[:5]:
                text += f"  - {cls['name']}: {cls['description'][:50]}\n"
                if cls['methods']:
                    text += f"    Methods: {cls['methods']}\n"
            text += "\n"
        
        if summary.functions:
            text += "Functions:\n"
            for func in summary.functions[:10]:
                text += f"  - {func['signature']}\n"
            text += "\n"
        
        if summary.imports:
            text += f"Key Imports: {', '.join(summary.imports[:5])}\n"
        
        return text
