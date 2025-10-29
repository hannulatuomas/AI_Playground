"""
Refactorer Module

Code refactoring and optimization.
Phase 3 implementation.
"""

from .analyzer import CodeAnalyzer, AnalysisReport, CodeSmell, ComplexityMetrics
from .refactor import CodeRefactorer, RefactoredCode
from .splitter import FileSplitter, FileSplit
from .optimizer import StructureOptimizer, OptimizationReport, StructureSuggestion

__all__ = [
    'CodeAnalyzer',
    'AnalysisReport',
    'CodeSmell',
    'ComplexityMetrics',
    'CodeRefactorer',
    'RefactoredCode',
    'FileSplitter',
    'FileSplit',
    'StructureOptimizer',
    'OptimizationReport',
    'StructureSuggestion'
]
