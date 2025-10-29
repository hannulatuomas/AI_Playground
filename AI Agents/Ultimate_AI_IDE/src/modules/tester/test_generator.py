"""
Test Generation Module

Generates unit tests using AI.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class TestCase:
    """Represents a test case."""
    __test__ = False  # Not a pytest test class
    name: str
    description: str
    code: str
    target_function: str


@dataclass
class TestFile:
    """Represents a test file."""
    __test__ = False  # Not a pytest test class
    file_path: str
    language: str
    framework: str
    test_cases: List[TestCase]
    imports: List[str]
    fixtures: List[str]


class TestGenerator:
    """Generates test cases using AI."""
    __test__ = False  # Not a pytest test class
    
    def __init__(self, ai_backend):
        """
        Initialize test generator.
        
        Args:
            ai_backend: AI backend for test generation
        """
        self.ai_backend = ai_backend
    
    def generate_tests(self, file_path: str, language: str,
                      framework: Optional[str] = None) -> TestFile:
        """
        Generate tests for a file.
        
        Args:
            file_path: Path to source file
            language: Programming language
            framework: Test framework (pytest, jest, etc.)
            
        Returns:
            TestFile with generated tests
        """
        # Detect test framework if not specified
        if not framework:
            framework = self._detect_test_framework(language)
        
        # Read source file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except Exception:
            return TestFile(
                file_path=self._get_test_file_path(file_path, language),
                language=language,
                framework=framework,
                test_cases=[],
                imports=[],
                fixtures=[]
            )
        
        # Extract functions/classes to test
        functions = self._extract_functions(source_code, language)
        classes = self._extract_classes(source_code, language)
        
        # Generate test cases
        test_cases = []
        
        for func in functions:
            cases = self._generate_function_tests(func, source_code, 
                                                  language, framework)
            test_cases.extend(cases)
        
        for cls in classes:
            cases = self._generate_class_tests(cls, source_code,
                                               language, framework)
            test_cases.extend(cases)
        
        # Generate imports and fixtures
        imports = self._generate_imports(file_path, language, framework)
        fixtures = self._generate_fixtures(test_cases, language, framework)
        
        return TestFile(
            file_path=self._get_test_file_path(file_path, language),
            language=language,
            framework=framework,
            test_cases=test_cases,
            imports=imports,
            fixtures=fixtures
        )
    
    def generate_test_for_function(self, function_code: str, 
                                   language: str,
                                   framework: str) -> List[TestCase]:
        """
        Generate tests for a specific function.
        
        Args:
            function_code: Function source code
            language: Programming language
            framework: Test framework
            
        Returns:
            List of test cases
        """
        return self._generate_function_tests(
            self._parse_function(function_code, language),
            function_code,
            language,
            framework
        )
    
    def _generate_function_tests(self, func_info: Dict, source_code: str,
                                language: str, framework: str) -> List[TestCase]:
        """Generate test cases for a function."""
        if not self.ai_backend:
            return []
        
        prompt = self._build_test_prompt(
            func_info['name'],
            func_info['signature'],
            source_code,
            language,
            framework,
            'function'
        )
        
        try:
            response = self.ai_backend.query(prompt, max_tokens=1500)
            return self._parse_test_response(response, func_info['name'], 
                                            language, framework)
        except Exception:
            return []
    
    def _generate_class_tests(self, class_info: Dict, source_code: str,
                             language: str, framework: str) -> List[TestCase]:
        """Generate test cases for a class."""
        if not self.ai_backend:
            return []
        
        prompt = self._build_test_prompt(
            class_info['name'],
            class_info['methods'],
            source_code,
            language,
            framework,
            'class'
        )
        
        try:
            response = self.ai_backend.query(prompt, max_tokens=2000)
            return self._parse_test_response(response, class_info['name'],
                                            language, framework)
        except Exception:
            return []
    
    def _build_test_prompt(self, name: str, signature: str, 
                          source_code: str, language: str,
                          framework: str, test_type: str) -> str:
        """Build prompt for test generation."""
        # Truncate source code if too long
        if len(source_code) > 2000:
            source_code = source_code[:2000] + "\n... (truncated)"
        
        prompt = f"""Generate comprehensive unit tests for this {language} {test_type}.

{test_type.capitalize()}: {name}
Signature: {signature}

Source Code Context:
```
{source_code}
```

Requirements:
- Use {framework} framework
- Test normal cases
- Test edge cases
- Test error conditions
- Use appropriate fixtures/mocks
- Aim for 100% coverage
- Include descriptive test names
- Add comments explaining test purpose

Generate 3-5 test cases. Output format:
TEST: test_name
DESCRIPTION: what it tests
CODE:
```
[test code]
```
"""
        
        return prompt
    
    def _parse_test_response(self, response: str, target: str,
                            language: str, framework: str) -> List[TestCase]:
        """Parse AI response into test cases."""
        test_cases = []
        
        # Split by TEST: markers
        parts = response.split('TEST:')
        
        for part in parts[1:]:  # Skip first empty part
            try:
                lines = part.strip().split('\n')
                
                # Extract test name
                test_name = lines[0].strip()
                
                # Extract description
                description = ""
                for line in lines:
                    if line.startswith('DESCRIPTION:'):
                        description = line.split(':', 1)[1].strip()
                        break
                
                # Extract code
                code = ""
                in_code = False
                for line in lines:
                    if line.strip().startswith('CODE:') or line.strip() == '```':
                        in_code = True
                        continue
                    if in_code:
                        if line.strip() == '```':
                            break
                        code += line + '\n'
                
                if test_name and code:
                    test_cases.append(TestCase(
                        name=test_name,
                        description=description,
                        code=code.strip(),
                        target_function=target
                    ))
            except Exception:
                continue
        
        return test_cases
    
    def _extract_functions(self, code: str, language: str) -> List[Dict]:
        """Extract function information from code."""
        functions = []
        
        if language == 'python':
            pattern = r'def\s+(\w+)\s*\((.*?)\)(?:\s*->\s*[\w\[\],\s]+)?:'
            matches = re.finditer(pattern, code)
            
            for match in matches:
                func_name = match.group(1)
                params = match.group(2)
                
                # Skip private functions and test functions
                if not func_name.startswith('_') and not func_name.startswith('test_'):
                    functions.append({
                        'name': func_name,
                        'signature': f"def {func_name}({params})",
                        'params': params
                    })
        
        elif language in ['javascript', 'typescript']:
            # Function declarations
            pattern = r'function\s+(\w+)\s*\((.*?)\)'
            matches = re.finditer(pattern, code)
            
            for match in matches:
                functions.append({
                    'name': match.group(1),
                    'signature': match.group(0),
                    'params': match.group(2)
                })
            
            # Arrow functions
            pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\((.*?)\)\s*=>'
            matches = re.finditer(pattern, code)
            
            for match in matches:
                functions.append({
                    'name': match.group(1),
                    'signature': match.group(0),
                    'params': match.group(2)
                })
        
        return functions
    
    def _extract_classes(self, code: str, language: str) -> List[Dict]:
        """Extract class information from code."""
        classes = []
        
        if language == 'python':
            pattern = r'class\s+(\w+)(?:\((.*?)\))?:'
            matches = re.finditer(pattern, code)
            
            for match in matches:
                class_name = match.group(1)
                
                # Extract methods
                class_start = match.start()
                # Find next class or end of file
                next_class = re.search(r'\nclass\s+', code[class_start + 1:])
                class_end = class_start + next_class.start() if next_class else len(code)
                class_code = code[class_start:class_end]
                
                methods = re.findall(r'def\s+(\w+)', class_code)
                
                classes.append({
                    'name': class_name,
                    'methods': [m for m in methods if not m.startswith('_')]
                })
        
        elif language in ['javascript', 'typescript']:
            pattern = r'class\s+(\w+)'
            matches = re.finditer(pattern, code)
            
            for match in matches:
                classes.append({
                    'name': match.group(1),
                    'methods': []  # Would need more complex parsing
                })
        
        return classes
    
    def _parse_function(self, code: str, language: str) -> Dict:
        """Parse function from code."""
        if language == 'python':
            match = re.search(r'def\s+(\w+)\s*\((.*?)\)', code)
            if match:
                return {
                    'name': match.group(1),
                    'signature': match.group(0),
                    'params': match.group(2)
                }
        
        return {'name': 'unknown', 'signature': '', 'params': ''}
    
    def _generate_imports(self, file_path: str, language: str,
                         framework: str) -> List[str]:
        """Generate import statements for test file."""
        imports = []
        
        # Get module name from file path
        module_path = Path(file_path)
        module_name = module_path.stem
        
        if language == 'python':
            imports.append(f"import pytest" if framework == 'pytest' else "import unittest")
            imports.append(f"from {module_name} import *")
        
        elif language in ['javascript', 'typescript']:
            imports.append(f"import {{ describe, it, expect }} from '{framework}';")
            imports.append(f"import * as module from './{module_name}';")
        
        return imports
    
    def _generate_fixtures(self, test_cases: List[TestCase], 
                          language: str, framework: str) -> List[str]:
        """Generate test fixtures."""
        fixtures = []
        
        # This would be more sophisticated in real implementation
        if language == 'python' and framework == 'pytest':
            fixtures.append("""
@pytest.fixture
def sample_data():
    return {"key": "value"}
""")
        
        return fixtures
    
    def _detect_test_framework(self, language: str) -> str:
        """Detect appropriate test framework for language."""
        frameworks = {
            'python': 'pytest',
            'javascript': 'jest',
            'typescript': 'jest',
            'csharp': 'xunit',
            'cpp': 'gtest',
            'java': 'junit'
        }
        return frameworks.get(language, 'unittest')
    
    def _get_test_file_path(self, source_path: str, language: str) -> str:
        """Generate test file path from source path."""
        path = Path(source_path)
        
        if language == 'python':
            return str(path.parent / f"test_{path.name}")
        elif language in ['javascript', 'typescript']:
            return str(path.parent / f"{path.stem}.test{path.suffix}")
        else:
            return str(path.parent / f"{path.stem}_test{path.suffix}")
