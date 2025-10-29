"""
Language Support Module

Provides language-specific handlers, validation, and framework detection.
"""

from typing import Dict, List, Optional, Tuple
import re


class LanguageSupport:
    """
    Handles language-specific logic, framework detection, and validation.
    """

    def __init__(self):
        """Initialize language support with handlers and configurations."""
        self._initialize_language_info()
        self._initialize_framework_patterns()

    def _initialize_language_info(self) -> None:
        """Initialize language information and file extensions."""
        
        self.language_info = {
            'python': {
                'extensions': ['.py', '.pyw', '.pyx'],
                'comment': '#',
                'common_keywords': ['def', 'class', 'import', 'if', 'for', 'while'],
                'frameworks': ['django', 'flask', 'fastapi', 'pytest', 'pandas', 'numpy']
            },
            'cpp': {
                'extensions': ['.cpp', '.cc', '.cxx', '.hpp', '.h', '.hxx'],
                'comment': '//',
                'common_keywords': ['class', 'void', 'int', 'include', 'namespace', 'template'],
                'frameworks': ['qt', 'boost', 'stl']
            },
            'csharp': {
                'extensions': ['.cs'],
                'comment': '//',
                'common_keywords': ['class', 'void', 'using', 'namespace', 'public', 'private'],
                'frameworks': ['.net', 'asp.net', 'entity framework', 'wpf', 'xamarin']
            },
            'javascript': {
                'extensions': ['.js', '.mjs', '.cjs'],
                'comment': '//',
                'common_keywords': ['function', 'const', 'let', 'var', 'class', 'import'],
                'frameworks': ['react', 'vue', 'angular', 'jquery', 'express']
            },
            'typescript': {
                'extensions': ['.ts', '.tsx'],
                'comment': '//',
                'common_keywords': ['interface', 'type', 'function', 'const', 'class', 'import'],
                'frameworks': ['react', 'angular', 'nest', 'express']
            },
            'html': {
                'extensions': ['.html', '.htm'],
                'comment': '<!--',
                'common_keywords': ['<!DOCTYPE', '<html', '<head', '<body', '<div', '<script'],
                'frameworks': []
            },
            'css': {
                'extensions': ['.css', '.scss', '.sass', '.less'],
                'comment': '/*',
                'common_keywords': ['@media', '@import', 'color', 'display', 'flex', 'grid'],
                'frameworks': ['bootstrap', 'tailwind', 'bulma', 'foundation']
            },
            'powershell': {
                'extensions': ['.ps1', '.psm1', '.psd1'],
                'comment': '#',
                'common_keywords': ['function', 'param', 'begin', 'process', 'end', 'if'],
                'frameworks': []
            },
            'bash': {
                'extensions': ['.sh', '.bash'],
                'comment': '#',
                'common_keywords': ['if', 'then', 'else', 'fi', 'for', 'while', 'function'],
                'frameworks': []
            },
            'sh': {
                'extensions': ['.sh'],
                'comment': '#',
                'common_keywords': ['if', 'then', 'else', 'fi', 'for', 'while'],
                'frameworks': []
            },
            'zsh': {
                'extensions': ['.zsh'],
                'comment': '#',
                'common_keywords': ['if', 'then', 'else', 'fi', 'for', 'while', 'function'],
                'frameworks': []
            },
            'batch': {
                'extensions': ['.bat', '.cmd'],
                'comment': 'REM',
                'common_keywords': ['@echo', 'if', 'else', 'for', 'set', 'goto', 'call'],
                'frameworks': []
            },
        }

        # Web frameworks (treated as special language variants)
        self.web_frameworks = {
            'react': {
                'base_language': 'javascript',
                'patterns': ['React', 'useState', 'useEffect', 'jsx', 'tsx', 'Component'],
                'file_extensions': ['.jsx', '.tsx']
            },
            'nodejs': {
                'base_language': 'javascript',
                'patterns': ['require', 'module.exports', 'express', 'http.createServer', '__dirname'],
                'file_extensions': ['.js', '.mjs']
            },
            'nextjs': {
                'base_language': 'javascript',
                'patterns': ['next', 'getServerSideProps', 'getStaticProps', 'App Router', 'next/'],
                'file_extensions': ['.js', '.jsx', '.ts', '.tsx']
            },
            'express': {
                'base_language': 'javascript',
                'patterns': ['express()', 'app.get', 'app.post', 'req.', 'res.', 'middleware'],
                'file_extensions': ['.js', '.ts']
            },
            'axios': {
                'base_language': 'javascript',
                'patterns': ['axios.get', 'axios.post', 'axios.create', 'axios.'],
                'file_extensions': ['.js', '.ts']
            },
        }

    def _initialize_framework_patterns(self) -> None:
        """Initialize regex patterns for framework detection."""
        
        self.framework_patterns = {
            'react': [
                r'import\s+.*\s+from\s+[\'"]react[\'"]',
                r'React\.',
                r'useState|useEffect|useContext',
                r'<\w+.*/>',  # JSX
            ],
            'nodejs': [
                r'require\([\'"].*[\'"]\)',
                r'module\.exports',
                r'process\.env',
                r'__dirname|__filename',
            ],
            'nextjs': [
                r'from\s+[\'"]next/',
                r'getServerSideProps|getStaticProps|getStaticPaths',
                r'export\s+default\s+function\s+\w+\(',
            ],
            'express': [
                r'express\(\)',
                r'app\.(get|post|put|delete|use)',
                r'req\.|res\.',
            ],
            'django': [
                r'from\s+django',
                r'models\.Model',
                r'def\s+\w+\(request',
            ],
            'flask': [
                r'from\s+flask\s+import',
                r'@app\.route',
                r'Flask\(__name__\)',
            ],
        }

    def detect_language(self, code: str, filename: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """
        Detect the programming language from code or filename.

        Args:
            code: Code snippet to analyze
            filename: Optional filename to check extension

        Returns:
            Tuple of (language, framework) where framework is optional
        """
        # First try filename extension
        if filename:
            lang = self._detect_from_filename(filename)
            if lang:
                framework = self._detect_framework(code, lang)
                return lang, framework

        # Try detecting from code patterns
        lang = self._detect_from_code(code)
        framework = self._detect_framework(code, lang) if lang else None
        
        return lang or 'text', framework

    def _detect_from_filename(self, filename: str) -> Optional[str]:
        """Detect language from filename extension."""
        filename_lower = filename.lower()
        
        for lang, info in self.language_info.items():
            for ext in info['extensions']:
                if filename_lower.endswith(ext):
                    return lang
        
        # Check web framework extensions
        for framework, info in self.web_frameworks.items():
            for ext in info['file_extensions']:
                if filename_lower.endswith(ext):
                    return framework
        
        return None

    def _detect_from_code(self, code: str) -> Optional[str]:
        """Detect language from code patterns."""
        code_lower = code.lower()
        
        # Score each language based on keyword matches
        scores = {}
        
        for lang, info in self.language_info.items():
            score = 0
            for keyword in info['common_keywords']:
                if keyword.lower() in code_lower:
                    score += 1
            
            if score > 0:
                scores[lang] = score
        
        if scores:
            # Return language with highest score
            return max(scores, key=scores.get)
        
        return None

    def _detect_framework(self, code: str, language: str) -> Optional[str]:
        """Detect framework from code patterns."""
        
        for framework, patterns in self.framework_patterns.items():
            matches = 0
            for pattern in patterns:
                if re.search(pattern, code, re.MULTILINE):
                    matches += 1
            
            # If we match at least 2 patterns, consider it detected
            if matches >= 2:
                return framework
        
        return None

    def get_language_info(self, language: str) -> Optional[Dict]:
        """
        Get information about a specific language.

        Args:
            language: Language name

        Returns:
            Dictionary with language info or None
        """
        lang_normalized = language.lower().strip()
        
        # Check standard languages
        if lang_normalized in self.language_info:
            return self.language_info[lang_normalized]
        
        # Check web frameworks
        if lang_normalized in self.web_frameworks:
            framework_info = self.web_frameworks[lang_normalized]
            base_lang = framework_info['base_language']
            base_info = self.language_info.get(base_lang, {}).copy()
            base_info['framework'] = lang_normalized
            base_info['patterns'] = framework_info['patterns']
            return base_info
        
        return None

    def validate_code_syntax(self, code: str, language: str) -> Tuple[bool, Optional[str]]:
        """
        Basic syntax validation for code (simple checks).

        Args:
            code: Code to validate
            language: Programming language

        Returns:
            Tuple of (is_valid, error_message)
        """
        lang_normalized = language.lower().strip()
        
        # Basic validation rules
        validators = {
            'python': self._validate_python,
            'javascript': self._validate_javascript,
            'typescript': self._validate_javascript,  # Similar syntax
            'cpp': self._validate_cpp,
            'csharp': self._validate_csharp,
            'bash': self._validate_shell,
            'sh': self._validate_shell,
            'zsh': self._validate_shell,
        }
        
        validator = validators.get(lang_normalized)
        if validator:
            return validator(code)
        
        # No specific validator, assume valid
        return True, None

    def _validate_python(self, code: str) -> Tuple[bool, Optional[str]]:
        """Basic Python syntax validation."""
        # Check for common syntax errors
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for missing colons
            if stripped.startswith(('if ', 'elif ', 'else', 'for ', 'while ', 'def ', 'class ', 'try', 'except', 'finally', 'with ')):
                if stripped.endswith(('if', 'elif', 'else', 'for', 'while', 'def', 'class', 'try', 'except', 'finally', 'with')):
                    if not stripped.endswith(':'):
                        return False, f"Line {i}: Missing colon at end of statement"
        
        return True, None

    def _validate_javascript(self, code: str) -> Tuple[bool, Optional[str]]:
        """Basic JavaScript/TypeScript syntax validation."""
        # Check for basic bracket matching
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        for char in code:
            if char in brackets.keys():
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    return False, "Unmatched closing bracket"
                opening = stack.pop()
                if brackets[opening] != char:
                    return False, f"Mismatched brackets: {opening} and {char}"
        
        if stack:
            return False, f"Unclosed bracket: {stack[-1]}"
        
        return True, None

    def _validate_cpp(self, code: str) -> Tuple[bool, Optional[str]]:
        """Basic C++ syntax validation."""
        # Check for basic bracket matching (same as JavaScript)
        return self._validate_javascript(code)

    def _validate_csharp(self, code: str) -> Tuple[bool, Optional[str]]:
        """Basic C# syntax validation."""
        # Check for basic bracket matching
        return self._validate_javascript(code)

    def _validate_shell(self, code: str) -> Tuple[bool, Optional[str]]:
        """Basic shell script validation."""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for common mistakes
            if 'if' in stripped and not any(x in stripped for x in ['then', ';']):
                if stripped.startswith('if ') and not stripped.endswith('\\'):
                    return False, f"Line {i}: 'if' statement should be followed by 'then'"
        
        return True, None

    def get_code_template(self, language: str, template_type: str = 'basic') -> str:
        """
        Get a code template for a language.

        Args:
            language: Programming language
            template_type: Type of template (basic, function, class)

        Returns:
            Code template string
        """
        lang_normalized = language.lower().strip()
        
        templates = {
            'python': {
                'basic': '# Python code\n',
                'function': 'def function_name(param):\n    """Docstring."""\n    pass\n',
                'class': 'class ClassName:\n    """Class docstring."""\n    \n    def __init__(self):\n        pass\n',
            },
            'cpp': {
                'basic': '// C++ code\n#include <iostream>\n\n',
                'function': 'void functionName(int param) {\n    // Implementation\n}\n',
                'class': 'class ClassName {\npublic:\n    ClassName();\n    ~ClassName();\nprivate:\n    // Members\n};\n',
            },
            'javascript': {
                'basic': '// JavaScript code\n',
                'function': 'function functionName(param) {\n    // Implementation\n}\n',
                'class': 'class ClassName {\n    constructor() {\n        // Initialization\n    }\n}\n',
            },
        }
        
        lang_templates = templates.get(lang_normalized, {'basic': f'// {language} code\n'})
        return lang_templates.get(template_type, lang_templates.get('basic', ''))

    def get_supported_languages(self) -> List[str]:
        """Get list of all supported languages."""
        languages = list(self.language_info.keys())
        frameworks = list(self.web_frameworks.keys())
        return sorted(languages + frameworks)

    def is_web_framework(self, language: str) -> bool:
        """Check if the language is a web framework."""
        return language.lower().strip() in self.web_frameworks


if __name__ == "__main__":
    # Test the language support module
    support = LanguageSupport()
    
    print("=== Supported Languages ===")
    print(", ".join(support.get_supported_languages()))
    print()
    
    # Test language detection
    python_code = """
def hello_world():
    print("Hello, World!")
    return 42
"""
    
    lang, framework = support.detect_language(python_code)
    print(f"Detected: {lang}, Framework: {framework}")
    
    # Test React detection
    react_code = """
import React, { useState } from 'react';

function MyComponent() {
    const [count, setCount] = useState(0);
    return <div>{count}</div>;
}
"""
    
    lang, framework = support.detect_language(react_code)
    print(f"Detected: {lang}, Framework: {framework}")
    
    # Test validation
    valid, error = support.validate_code_syntax("if True:\n    pass", "python")
    print(f"\nValidation: {valid}, Error: {error}")
    
    # Test template
    print("\n=== Python Function Template ===")
    print(support.get_code_template('python', 'function'))
