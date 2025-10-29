"""
JavaScript/TypeScript Test Generator

Generates Jest and Mocha tests.
"""

from pathlib import Path
from typing import List

from ..code_analyzer import CodeAnalysisResult, FunctionInfo, ClassInfo, ParameterInfo


class JavaScriptTestGenerator:
    """Generates JavaScript/TypeScript tests."""
    
    def __init__(self, llm=None, config=None):
        """Initialize generator."""
        self.llm = llm
        self.config = config
    
    def generate_tests(self, analysis: CodeAnalysisResult, source_path: Path) -> str:
        """Generate JS/TS tests."""
        if self.config and self.config.framework == "mocha":
            return self._generate_mocha(analysis, source_path)
        return self._generate_jest(analysis, source_path)
    
    def _generate_jest(self, analysis: CodeAnalysisResult, source_path: Path) -> str:
        """Generate Jest tests."""
        lines = [f"const {{ "]
        
        imported = []
        for func in analysis.functions:
            imported.append(f"  {func.name}")
        for cls in analysis.classes:
            imported.append(f"  {cls.name}")
        
        if imported:
            lines.append(',\n'.join(imported))
        lines.extend([f"}} = require('./{source_path.stem}');", ''])
        
        for func in analysis.functions:
            lines.extend(self._gen_function_jest(func))
            lines.append('')
        
        for cls in analysis.classes:
            lines.extend(self._gen_class_jest(cls))
            lines.append('')
        
        return '\n'.join(lines)
    
    def _gen_function_jest(self, func: FunctionInfo) -> List[str]:
        """Generate Jest tests for function."""
        lines = [
            f"describe('{func.name}', () => {{",
            f"  test('should work with valid inputs', () => {{"
        ]
        
        sample_args = self._gen_sample_args_js(func.parameters)
        args_str = ', '.join(sample_args)
        
        lines.extend([
            f"    const result = {func.name}({args_str});",
            f"    expect(result).toBeDefined();",
            f"  }});",
            ''
        ])
        
        if self.config and self.config.include_error_cases:
            lines.extend([
                f"  test('should throw on invalid input', () => {{",
                f"    expect(() => {func.name}(null)).toThrow();",
                f"  }});",
            ])
        
        lines.append("});")
        return lines
    
    def _gen_class_jest(self, cls: ClassInfo) -> List[str]:
        """Generate Jest tests for class."""
        lines = [
            f"describe('{cls.name}', () => {{",
            f"  let instance;",
            '',
            f"  beforeEach(() => {{",
            f"    instance = new {cls.name}();",
            f"  }});",
            '',
            f"  test('should create instance', () => {{",
            f"    expect(instance).toBeInstanceOf({cls.name});",
            f"  }});",
            ''
        ]
        
        for method in cls.methods:
            if method.name == 'constructor':
                continue
            
            lines.extend([
                f"  test('{method.name} should work', () => {{",
                f"    const result = instance.{method.name}();",
                f"    expect(result).toBeDefined();",
                f"  }});",
                ''
            ])
        
        lines.append("});")
        return lines
    
    def _generate_mocha(self, analysis: CodeAnalysisResult, source_path: Path) -> str:
        """Generate Mocha tests."""
        lines = [
            "const { expect } = require('chai');",
            f"const {{ "
        ]
        
        imported = []
        for func in analysis.functions:
            imported.append(f"  {func.name}")
        for cls in analysis.classes:
            imported.append(f"  {cls.name}")
        
        if imported:
            lines.append(',\n'.join(imported))
        lines.extend([f"}} = require('./{source_path.stem}');", ''])
        
        for func in analysis.functions:
            lines.extend(self._gen_function_mocha(func))
            lines.append('')
        
        return '\n'.join(lines)
    
    def _gen_function_mocha(self, func: FunctionInfo) -> List[str]:
        """Generate Mocha tests for function."""
        lines = [
            f"describe('{func.name}', function() {{",
            f"  it('should work with valid inputs', function() {{"
        ]
        
        sample_args = self._gen_sample_args_js(func.parameters)
        args_str = ', '.join(sample_args)
        
        lines.extend([
            f"    const result = {func.name}({args_str});",
            f"    expect(result).to.exist;",
            f"  }});",
            "});"
        ])
        
        return lines
    
    def _gen_sample_args_js(self, parameters: List[ParameterInfo]) -> List[str]:
        """Generate sample JS arguments."""
        args = []
        for param in parameters:
            type_hint = param.type_hint or ""
            
            if 'number' in type_hint.lower() or 'int' in type_hint.lower():
                args.append('1')
            elif 'string' in type_hint.lower():
                args.append('"test"')
            elif 'bool' in type_hint.lower():
                args.append('true')
            elif 'array' in type_hint.lower():
                args.append('[]')
            elif 'object' in type_hint.lower():
                args.append('{}')
            else:
                args.append('null')
        
        return args
    
    def generate_mocks(self, dependencies: List[str]) -> str:
        """Generate Jest mocks."""
        lines = ['// Mock dependencies', '']
        
        for dep in dependencies:
            lines.append(f"jest.mock('{dep}');")
        
        return '\n'.join(lines)
