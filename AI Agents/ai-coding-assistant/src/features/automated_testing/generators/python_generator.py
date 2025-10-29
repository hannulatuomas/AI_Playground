"""
Python Test Generator

Generates pytest and unittest tests for Python code.
"""

from pathlib import Path
from typing import List, Optional

from ..code_analyzer import CodeAnalysisResult, FunctionInfo, ClassInfo, ParameterInfo


class PythonTestGenerator:
    """Generates Python tests (pytest or unittest)."""
    
    def __init__(self, llm=None, config=None):
        """Initialize generator."""
        self.llm = llm
        self.config = config
    
    def generate_tests(self, analysis: CodeAnalysisResult, source_path: Path) -> str:
        """Generate Python tests."""
        if self.config and self.config.framework == "unittest":
            return self._generate_unittest(analysis, source_path)
        return self._generate_pytest(analysis, source_path)
    
    def _generate_pytest(self, analysis: CodeAnalysisResult, source_path: Path) -> str:
        """Generate pytest tests."""
        lines = [
            '"""',
            f'Test suite for {source_path.name}',
            'Generated automatically by AI Coding Assistant',
            '"""',
            '',
            'import pytest',
            f'from {source_path.stem} import ('
        ]
        
        # Imports
        imported = []
        for func in analysis.functions:
            imported.append(f'    {func.name}')
        for cls in analysis.classes:
            imported.append(f'    {cls.name}')
        
        if imported:
            lines.append(',\n'.join(imported))
        lines.extend([')', '', ''])
        
        # Generate tests
        for func in analysis.functions:
            lines.extend(self._gen_function_pytest(func))
            lines.append('')
        
        for cls in analysis.classes:
            lines.extend(self._gen_class_pytest(cls))
            lines.append('')
        
        return '\n'.join(lines)
    
    def _gen_function_pytest(self, func: FunctionInfo) -> List[str]:
        """Generate pytest tests for a function."""
        lines = []
        class_name = f"Test{func.name.title().replace('_', '')}"
        
        lines.extend([
            f'class {class_name}:',
            f'    """Test suite for {func.name} function."""',
            '',
            f'    def test_{func.name}_happy_path(self):',
            f'        """Test {func.name} with valid inputs."""'
        ])
        
        # Sample call
        sample_args = self._gen_sample_args(func.parameters)
        args_str = ', '.join(sample_args)
        lines.append(f'        result = {func.name}({args_str})')
        
        # Assertion
        if func.return_type and func.return_type != 'None':
            lines.append(f'        assert result is not None')
        else:
            lines.append(f'        # Add specific assertions here')
        lines.append('')
        
        # Edge cases
        if self.config and self.config.include_edge_cases:
            lines.extend([
                f'    def test_{func.name}_edge_cases(self):',
                f'        """Test {func.name} with edge cases."""',
                f'        # Test with zero',
                f'        # Test with empty',
                f'        # Test with None',
                f'        pass',
                ''
            ])
        
        # Error cases
        if self.config and self.config.include_error_cases:
            lines.extend([
                f'    def test_{func.name}_invalid_input(self):',
                f'        """Test {func.name} with invalid inputs."""',
                f'        with pytest.raises(Exception):',
                f'            {func.name}(None)',
                ''
            ])
        
        return lines
    
    def _gen_class_pytest(self, cls: ClassInfo) -> List[str]:
        """Generate pytest tests for a class."""
        lines = []
        test_class = f"Test{cls.name}"
        
        lines.extend([
            f'class {test_class}:',
            f'    """Test suite for {cls.name} class."""',
            '',
            '    @pytest.fixture',
            f'    def {cls.name.lower()}_instance(self):',
            f'        """Create a test instance of {cls.name}."""'
        ])
        
        # Find __init__
        init_method = next((m for m in cls.methods if m.name == '__init__'), None)
        if init_method and init_method.parameters:
            sample_args = self._gen_sample_args(init_method.parameters[1:])
            args_str = ', '.join(sample_args)
            lines.append(f'        return {cls.name}({args_str})')
        else:
            lines.append(f'        return {cls.name}()')
        
        lines.extend(['', f'    def test_{cls.name.lower()}_creation(self, {cls.name.lower()}_instance):',
                     f'        """Test {cls.name} instance creation."""',
                     f'        assert {cls.name.lower()}_instance is not None',
                     f'        assert isinstance({cls.name.lower()}_instance, {cls.name})',
                     ''])
        
        # Test methods
        for method in cls.methods:
            if method.name.startswith('_') and method.name != '__init__':
                continue
            if method.name == '__init__':
                continue
            
            lines.extend([
                f'    def test_{cls.name.lower()}_{method.name}(self, {cls.name.lower()}_instance):',
                f'        """Test {cls.name}.{method.name} method."""'
            ])
            
            sample_args = self._gen_sample_args(method.parameters[1:])
            args_str = ', '.join(sample_args)
            
            if method.is_async:
                lines.append(f'        # async method - use pytest-asyncio')
            else:
                lines.append(f'        result = {cls.name.lower()}_instance.{method.name}({args_str})')
            
            if method.return_type and method.return_type != 'None':
                lines.append(f'        assert result is not None')
            else:
                lines.append(f'        # Add assertions')
            lines.append('')
        
        return lines
    
    def _generate_unittest(self, analysis: CodeAnalysisResult, source_path: Path) -> str:
        """Generate unittest tests."""
        lines = [
            '"""',
            f'Test suite for {source_path.name}',
            '"""',
            '',
            'import unittest',
            f'from {source_path.stem} import ('
        ]
        
        imported = []
        for func in analysis.functions:
            imported.append(f'    {func.name}')
        for cls in analysis.classes:
            imported.append(f'    {cls.name}')
        
        if imported:
            lines.append(',\n'.join(imported))
        lines.extend([')', '', ''])
        
        # Generate tests
        for func in analysis.functions:
            lines.extend(self._gen_function_unittest(func))
            lines.append('')
        
        for cls in analysis.classes:
            lines.extend(self._gen_class_unittest(cls))
            lines.append('')
        
        lines.extend(['', "if __name__ == '__main__':", '    unittest.main()'])
        
        return '\n'.join(lines)
    
    def _gen_function_unittest(self, func: FunctionInfo) -> List[str]:
        """Generate unittest tests for a function."""
        lines = []
        class_name = f"Test{func.name.title().replace('_', '')}"
        
        lines.extend([
            f'class {class_name}(unittest.TestCase):',
            f'    """Test suite for {func.name}."""',
            '',
            f'    def test_{func.name}_happy_path(self):',
            f'        """Test with valid inputs."""'
        ])
        
        sample_args = self._gen_sample_args(func.parameters)
        args_str = ', '.join(sample_args)
        lines.append(f'        result = {func.name}({args_str})')
        
        if func.return_type and func.return_type != 'None':
            lines.append(f'        self.assertIsNotNone(result)')
        else:
            lines.append(f'        # Add assertions')
        lines.append('')
        
        return lines
    
    def _gen_class_unittest(self, cls: ClassInfo) -> List[str]:
        """Generate unittest tests for a class."""
        lines = []
        test_class = f"Test{cls.name}"
        
        lines.extend([
            f'class {test_class}(unittest.TestCase):',
            f'    """Test suite for {cls.name}."""',
            '',
            '    def setUp(self):',
            f'        """Set up test fixtures."""'
        ])
        
        init_method = next((m for m in cls.methods if m.name == '__init__'), None)
        if init_method and init_method.parameters:
            sample_args = self._gen_sample_args(init_method.parameters[1:])
            args_str = ', '.join(sample_args)
            lines.append(f'        self.instance = {cls.name}({args_str})')
        else:
            lines.append(f'        self.instance = {cls.name}()')
        
        lines.extend(['', f'    def test_creation(self):',
                     f'        """Test instance creation."""',
                     f'        self.assertIsNotNone(self.instance)',
                     ''])
        
        return lines
    
    def _gen_sample_args(self, parameters: List[ParameterInfo]) -> List[str]:
        """Generate sample arguments."""
        args = []
        for param in parameters:
            type_hint = param.type_hint or ""
            
            if param.default_value:
                args.append(param.default_value)
            elif 'int' in type_hint.lower():
                args.append('1')
            elif 'str' in type_hint.lower():
                args.append('"test"')
            elif 'bool' in type_hint.lower():
                args.append('True')
            elif 'list' in type_hint.lower():
                args.append('[]')
            elif 'dict' in type_hint.lower():
                args.append('{}')
            else:
                args.append('None')
        
        return args
    
    def generate_mocks(self, dependencies: List[str]) -> str:
        """Generate pytest mocks."""
        lines = ['# Mock dependencies', 'from unittest.mock import Mock, patch', '']
        
        for dep in dependencies:
            lines.append(f'@patch("{dep}")')
            lines.append(f'def test_with_{dep.replace(".", "_")}_mock(mock_{dep.split(".")[-1]}):')
            lines.append(f'    mock_{dep.split(".")[-1]}.return_value = None')
            lines.append(f'    # Test code here')
            lines.append('')
        
        return '\n'.join(lines)
