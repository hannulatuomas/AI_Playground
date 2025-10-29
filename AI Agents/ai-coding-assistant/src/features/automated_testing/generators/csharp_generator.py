"""
C# Test Generator

Generates xUnit, NUnit, and MSTest tests.
"""

from pathlib import Path
from typing import List

from ..code_analyzer import CodeAnalysisResult, ClassInfo


class CSharpTestGenerator:
    """Generates C# tests."""
    
    def __init__(self, llm=None, config=None):
        """Initialize generator."""
        self.llm = llm
        self.config = config
    
    def generate_tests(self, analysis: CodeAnalysisResult, source_path: Path) -> str:
        """Generate C# tests."""
        framework = self.config.framework if self.config else "xunit"
        
        if framework == "nunit":
            return self._generate_nunit(analysis, source_path)
        elif framework == "mstest":
            return self._generate_mstest(analysis, source_path)
        else:
            return self._generate_xunit(analysis, source_path)
    
    def _generate_xunit(self, analysis: CodeAnalysisResult, source_path: Path) -> str:
        """Generate xUnit tests."""
        namespace = source_path.stem.replace('-', '_')
        lines = [
            'using Xunit;',
            f'using {namespace};',
            '',
            f'namespace {namespace}.Tests',
            '{'
        ]
        
        for cls in analysis.classes:
            test_lines = self._gen_class_xunit(cls)
            lines.extend(['    ' + line for line in test_lines])
        
        lines.append('}')
        return '\n'.join(lines)
    
    def _gen_class_xunit(self, cls: ClassInfo) -> List[str]:
        """Generate xUnit test class."""
        lines = [
            f'public class {cls.name}Tests',
            '{',
            f'    [Fact]',
            f'    public void {cls.name}_ShouldCreateInstance()',
            f'    {{',
            f'        var instance = new {cls.name}();',
            f'        Assert.NotNull(instance);',
            f'    }}',
            '}'
        ]
        return lines
    
    def _generate_nunit(self, analysis: CodeAnalysisResult, source_path: Path) -> str:
        """Generate NUnit tests."""
        namespace = source_path.stem.replace('-', '_')
        lines = [
            'using NUnit.Framework;',
            f'using {namespace};',
            '',
            f'namespace {namespace}.Tests',
            '{',
            '    [TestFixture]'
        ]
        
        for cls in analysis.classes:
            test_lines = self._gen_class_nunit(cls)
            lines.extend(['    ' + line for line in test_lines])
        
        lines.append('}')
        return '\n'.join(lines)
    
    def _gen_class_nunit(self, cls: ClassInfo) -> List[str]:
        """Generate NUnit test class."""
        lines = [
            f'public class {cls.name}Tests',
            '{',
            f'    [Test]',
            f'    public void {cls.name}_ShouldCreateInstance()',
            f'    {{',
            f'        var instance = new {cls.name}();',
            f'        Assert.IsNotNull(instance);',
            f'    }}',
            '}'
        ]
        return lines
    
    def _generate_mstest(self, analysis: CodeAnalysisResult, source_path: Path) -> str:
        """Generate MSTest tests."""
        namespace = source_path.stem.replace('-', '_')
        lines = [
            'using Microsoft.VisualStudio.TestTools.UnitTesting;',
            f'using {namespace};',
            '',
            f'namespace {namespace}.Tests',
            '{',
            '    [TestClass]'
        ]
        
        for cls in analysis.classes:
            test_lines = self._gen_class_mstest(cls)
            lines.extend(['    ' + line for line in test_lines])
        
        lines.append('}')
        return '\n'.join(lines)
    
    def _gen_class_mstest(self, cls: ClassInfo) -> List[str]:
        """Generate MSTest test class."""
        lines = [
            f'public class {cls.name}Tests',
            '{',
            f'    [TestMethod]',
            f'    public void {cls.name}_ShouldCreateInstance()',
            f'    {{',
            f'        var instance = new {cls.name}();',
            f'        Assert.IsNotNull(instance);',
            f'    }}',
            '}'
        ]
        return lines
