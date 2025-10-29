"""
Test Generator Module - Main Interface

Generates comprehensive test suites for multiple languages and frameworks.
"""

from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass

from .code_analyzer import CodeAnalyzer, Language, CodeAnalysisResult
from .generators.python_generator import PythonTestGenerator
from .generators.javascript_generator import JavaScriptTestGenerator
from .generators.csharp_generator import CSharpTestGenerator
from .generators.cpp_generator import CppTestGenerator


@dataclass
class TestGenerationConfig:
    """Configuration for test generation."""
    framework: str = "pytest"
    include_mocks: bool = True
    include_edge_cases: bool = True
    include_error_cases: bool = True
    include_integration: bool = False
    max_tests_per_function: int = 10
    use_llm_for_complex: bool = True


class TestGenerator:
    """
    Main test generator interface.
    
    Delegates to language-specific generators.
    """
    
    def __init__(self, llm=None, config: Optional[TestGenerationConfig] = None):
        """Initialize the test generator."""
        self.llm = llm
        self.config = config or TestGenerationConfig()
        self.code_analyzer = CodeAnalyzer()
        
        # Initialize language-specific generators
        self.python_gen = PythonTestGenerator(llm, config)
        self.js_gen = JavaScriptTestGenerator(llm, config)
        self.csharp_gen = CSharpTestGenerator(llm, config)
        self.cpp_gen = CppTestGenerator(llm, config)
    
    def generate_unit_tests(
        self,
        file_path: Path,
        target: Optional[str] = None,
        output_path: Optional[Path] = None
    ) -> str:
        """Generate unit tests for a file."""
        analysis = self.code_analyzer.analyze_file(file_path)
        
        # Filter by target
        if target:
            analysis.functions = [f for f in analysis.functions if f.name == target]
            analysis.classes = [c for c in analysis.classes if c.name == target]
        
        # Delegate to language-specific generator
        if analysis.language == Language.PYTHON:
            test_code = self.python_gen.generate_tests(analysis, file_path)
        elif analysis.language in (Language.JAVASCRIPT, Language.TYPESCRIPT):
            test_code = self.js_gen.generate_tests(analysis, file_path)
        elif analysis.language == Language.CSHARP:
            test_code = self.csharp_gen.generate_tests(analysis, file_path)
        elif analysis.language == Language.CPP:
            test_code = self.cpp_gen.generate_tests(analysis, file_path)
        else:
            raise ValueError(f"Unsupported language: {analysis.language}")
        
        # Save if output path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(test_code)
        
        return test_code
    
    def generate_class_tests(
        self,
        file_path: Path,
        class_name: str,
        output_path: Optional[Path] = None
    ) -> str:
        """Generate tests for a specific class."""
        return self.generate_unit_tests(file_path, target=class_name, output_path=output_path)
    
    def generate_integration_tests(
        self,
        module_path: Path,
        output_path: Optional[Path] = None
    ) -> str:
        """Generate integration tests for a module."""
        template = """
# Integration tests - TODO: Implement based on module structure
import pytest

def test_integration():
    '''Integration test placeholder.'''
    pass
"""
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(template)
        
        return template
    
    def generate_edge_cases(self, code_analysis: CodeAnalysisResult) -> List[str]:
        """Generate edge case descriptions."""
        edge_cases = []
        for func in code_analysis.functions:
            func_edge_cases = self.code_analyzer.detect_edge_cases(func.parameters)
            for edge_case in func_edge_cases:
                edge_cases.append(f"Test {func.name} with {edge_case['description']}")
        return edge_cases
    
    def generate_mocks(self, dependencies: List[str]) -> str:
        """Generate mock objects."""
        if self.config.framework == "pytest":
            return self.python_gen.generate_mocks(dependencies)
        elif self.config.framework == "jest":
            return self.js_gen.generate_mocks(dependencies)
        else:
            return "# Mock generation not implemented for this framework"
