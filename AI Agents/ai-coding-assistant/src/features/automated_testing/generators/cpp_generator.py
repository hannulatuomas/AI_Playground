"""
C++ Test Generator

Generates Google Test and Catch2 tests.
"""

from pathlib import Path
from typing import List

from ..code_analyzer import CodeAnalysisResult, FunctionInfo, ClassInfo


class CppTestGenerator:
    """Generates C++ tests."""
    
    def __init__(self, llm=None, config=None):
        """Initialize generator."""
        self.llm = llm
        self.config = config
    
    def generate_tests(self, analysis: CodeAnalysisResult, source_path: Path) -> str:
        """Generate C++ tests."""
        framework = self.config.framework if self.config else "gtest"
        
        if framework == "catch2":
            return self._generate_catch2(analysis, source_path)
        else:
            return self._generate_gtest(analysis, source_path)
    
    def _generate_gtest(self, analysis: CodeAnalysisResult, source_path: Path) -> str:
        """Generate Google Test tests."""
        lines = [
            '#include <gtest/gtest.h>',
            f'#include "{source_path.name}"',
            ''
        ]
        
        for func in analysis.functions:
            lines.extend(self._gen_function_gtest(func))
            lines.append('')
        
        for cls in analysis.classes:
            lines.extend(self._gen_class_gtest(cls))
            lines.append('')
        
        lines.extend([
            'int main(int argc, char **argv) {',
            '    testing::InitGoogleTest(&argc, argv);',
            '    return RUN_ALL_TESTS();',
            '}'
        ])
        
        return '\n'.join(lines)
    
    def _gen_function_gtest(self, func: FunctionInfo) -> List[str]:
        """Generate Google Test for function."""
        test_name = func.name.title().replace('_', '')
        lines = [
            f'TEST({test_name}Test, BasicTest) {{',
            f'    // Test {func.name}',
            f'    // EXPECT_EQ(expected, actual);',
            f'    EXPECT_TRUE(true);',
            f'}}'
        ]
        return lines
    
    def _gen_class_gtest(self, cls: ClassInfo) -> List[str]:
        """Generate Google Test for class."""
        lines = [
            f'TEST({cls.name}Test, CreateInstance) {{',
            f'    {cls.name} instance;',
            f'    // Add assertions',
            f'    EXPECT_TRUE(true);',
            f'}}'
        ]
        return lines
    
    def _generate_catch2(self, analysis: CodeAnalysisResult, source_path: Path) -> str:
        """Generate Catch2 tests."""
        lines = [
            '#define CATCH_CONFIG_MAIN',
            '#include <catch2/catch.hpp>',
            f'#include "{source_path.name}"',
            ''
        ]
        
        for func in analysis.functions:
            lines.extend(self._gen_function_catch2(func))
            lines.append('')
        
        for cls in analysis.classes:
            lines.extend(self._gen_class_catch2(cls))
            lines.append('')
        
        return '\n'.join(lines)
    
    def _gen_function_catch2(self, func: FunctionInfo) -> List[str]:
        """Generate Catch2 test for function."""
        lines = [
            f'TEST_CASE("{func.name} test", "[{func.name}]") {{',
            f'    // Test {func.name}',
            f'    REQUIRE(true);',
            f'}}'
        ]
        return lines
    
    def _gen_class_catch2(self, cls: ClassInfo) -> List[str]:
        """Generate Catch2 test for class."""
        lines = [
            f'TEST_CASE("{cls.name} test", "[{cls.name}]") {{',
            f'    {cls.name} instance;',
            f'    REQUIRE(true);',
            f'}}'
        ]
        return lines
