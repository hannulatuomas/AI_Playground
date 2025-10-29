"""
Code Optimizer

Optimizes code structure and organization.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class StructureSuggestion:
    """Suggestion for project structure improvement."""
    suggestion_type: str
    description: str
    affected_files: List[str]
    priority: str


@dataclass
class OptimizationReport:
    """Report of optimization suggestions."""
    suggestions: List[StructureSuggestion] = field(default_factory=list)
    misplaced_files: List[str] = field(default_factory=list)
    recommended_structure: Dict[str, List[str]] = field(default_factory=dict)


class StructureOptimizer:
    """Optimizes project structure and organization."""
    
    def __init__(self):
        """Initialize structure optimizer."""
        self.common_patterns = {
            'python': {
                'src': ['*.py'],
                'tests': ['test_*.py', '*_test.py'],
                'docs': ['*.md', '*.rst'],
                'scripts': ['*.sh', '*.bat', '*.ps1']
            },
            'javascript': {
                'src': ['*.js', '*.jsx'],
                'test': ['*.test.js', '*.spec.js'],
                'docs': ['*.md'],
                'scripts': ['*.sh']
            }
        }
    
    def optimize_structure(self, project_path: str, 
                          language: str = 'python') -> OptimizationReport:
        """
        Analyze and suggest project structure improvements.
        
        Args:
            project_path: Root path of project
            language: Programming language
            
        Returns:
            OptimizationReport with suggestions
        """
        report = OptimizationReport()
        project_root = Path(project_path)
        
        if not project_root.exists():
            return report
        
        current_structure = self._analyze_current_structure(project_root, language)
        
        ideal_structure = self._get_ideal_structure(language)
        
        report.suggestions = self._generate_suggestions(
            current_structure, ideal_structure
        )
        
        report.misplaced_files = self._find_misplaced_files(
            current_structure, ideal_structure
        )
        
        report.recommended_structure = ideal_structure
        
        return report
    
    def _analyze_current_structure(self, root: Path, 
                                   language: str) -> Dict[str, List[str]]:
        """Analyze current project structure."""
        structure = {}
        
        for item in root.rglob('*'):
            if item.is_file():
                rel_path = item.relative_to(root)
                parent = str(rel_path.parent) if rel_path.parent != Path('.') else 'root'
                
                if parent not in structure:
                    structure[parent] = []
                structure[parent].append(item.name)
        
        return structure
    
    def _get_ideal_structure(self, language: str) -> Dict[str, List[str]]:
        """Get ideal project structure for language."""
        if language == 'python':
            return {
                'src': ['Main source code'],
                'tests': ['Test files'],
                'docs': ['Documentation'],
                'scripts': ['Utility scripts'],
                'config': ['Configuration files']
            }
        elif language in ['javascript', 'typescript']:
            return {
                'src': ['Source code'],
                'test': ['Tests'],
                'docs': ['Documentation'],
                'public': ['Static assets'],
                'config': ['Configuration']
            }
        else:
            return {
                'src': ['Source code'],
                'test': ['Tests'],
                'docs': ['Documentation']
            }
    
    def _generate_suggestions(self, current: Dict[str, List[str]],
                            ideal: Dict[str, List[str]]) -> List[StructureSuggestion]:
        """Generate structure improvement suggestions."""
        suggestions = []
        
        missing_dirs = set(ideal.keys()) - set(current.keys())
        for dir_name in missing_dirs:
            suggestions.append(StructureSuggestion(
                suggestion_type='missing_directory',
                description=f"Create {dir_name}/ directory for {ideal[dir_name][0]}",
                affected_files=[],
                priority='medium'
            ))
        
        if 'root' in current and len(current['root']) > 10:
            suggestions.append(StructureSuggestion(
                suggestion_type='cluttered_root',
                description='Root directory has too many files',
                affected_files=current['root'],
                priority='high'
            ))
        
        return suggestions
    
    def _find_misplaced_files(self, current: Dict[str, List[str]],
                             ideal: Dict[str, List[str]]) -> List[str]:
        """Find files that are in wrong directories."""
        misplaced = []
        
        if 'root' in current:
            for filename in current['root']:
                if filename.startswith('test_') or filename.endswith('_test.py'):
                    misplaced.append(f"{filename} should be in tests/")
                elif filename.endswith('.md') and filename not in ['README.md', 'LICENSE']:
                    misplaced.append(f"{filename} should be in docs/")
        
        return misplaced
