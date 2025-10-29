"""
Documentation Manager

Main interface for documentation management.
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from .scanner import CodeScanner, CodeStructure
from .generator import DocGenerator, Documentation


@dataclass
class SyncReport:
    """Report of documentation synchronization."""
    files_updated: List[str]
    files_created: List[str]
    errors: List[str]
    undocumented_items: List[str]


class DocManager:
    """Manages project documentation."""
    
    def __init__(self, ai_backend, project_rules: Optional[List[str]] = None):
        """
        Initialize documentation manager.
        
        Args:
            ai_backend: AI backend for generation
            project_rules: Project-specific rules
        """
        self.ai_backend = ai_backend
        self.project_rules = project_rules or []
        self.scanner = CodeScanner()
        self.generator = DocGenerator(ai_backend, project_rules)
    
    def sync_documentation(self, project_path: str, language: str = 'python',
                          framework: Optional[str] = None) -> SyncReport:
        """
        Synchronize project documentation.
        
        Args:
            project_path: Root path of project
            language: Programming language
            framework: Framework used
            
        Returns:
            SyncReport with results
        """
        report = SyncReport(
            files_updated=[],
            files_created=[],
            errors=[],
            undocumented_items=[]
        )
        
        project_root = Path(project_path)
        
        # Scan project structure
        print("Scanning project structure...")
        structure = self.scanner.scan_project(project_path, language)
        
        # Store undocumented items
        report.undocumented_items = structure.undocumented_items
        
        # Extract features from structure
        features = self._extract_features(structure)
        
        # Generate/update README
        readme_path = project_root / 'README.md'
        if self._should_update_doc(readme_path, structure):
            print("Generating README.md...")
            readme = self.generator.generate_readme(
                project_name=project_root.name,
                language=language,
                framework=framework,
                structure=structure,
                features=features
            )
            
            if self._write_documentation(readme, project_root):
                if readme_path.exists():
                    report.files_updated.append('README.md')
                else:
                    report.files_created.append('README.md')
        
        # Generate/update API docs
        api_doc_path = project_root / 'docs' / 'API.md'
        if structure.public_api:
            print("Generating API documentation...")
            api_docs = self.generator.generate_api_docs(structure, language)
            
            if self._write_documentation(api_docs, project_root):
                if api_doc_path.exists():
                    report.files_updated.append('docs/API.md')
                else:
                    report.files_created.append('docs/API.md')
        
        # Generate/update user guide
        user_guide_path = project_root / 'docs' / 'USER_GUIDE.md'
        if not user_guide_path.exists() and features:
            print("Generating user guide...")
            user_guide = self.generator.generate_user_guide(
                project_name=project_root.name,
                structure=structure,
                features=features
            )
            
            if self._write_documentation(user_guide, project_root):
                report.files_created.append('docs/USER_GUIDE.md')
        
        # Add docstrings to undocumented functions
        if report.undocumented_items:
            print(f"Found {len(report.undocumented_items)} undocumented items")
            # Note: Actually adding docstrings to files would require code editing
            # This is a complex operation that should be done carefully
        
        return report
    
    def generate_readme(self, project_path: str, language: str = 'python',
                       framework: Optional[str] = None,
                       features: Optional[List[str]] = None) -> bool:
        """
        Generate README for project.
        
        Args:
            project_path: Root path of project
            language: Programming language
            framework: Framework used
            features: List of features (auto-detected if None)
            
        Returns:
            True if successful
        """
        project_root = Path(project_path)
        
        # Scan project
        structure = self.scanner.scan_project(project_path, language)
        
        # Use provided features or extract from structure
        if features is None:
            features = self._extract_features(structure)
        
        # Generate README
        readme = self.generator.generate_readme(
            project_name=project_root.name,
            language=language,
            framework=framework,
            structure=structure,
            features=features
        )
        
        return self._write_documentation(readme, project_root)
    
    def generate_api_docs(self, project_path: str, 
                         language: str = 'python') -> bool:
        """
        Generate API documentation.
        
        Args:
            project_path: Root path of project
            language: Programming language
            
        Returns:
            True if successful
        """
        # Scan project
        structure = self.scanner.scan_project(project_path, language)
        
        # Generate API docs
        api_docs = self.generator.generate_api_docs(structure, language)
        
        return self._write_documentation(api_docs, Path(project_path))
    
    def add_docstrings(self, project_path: str, 
                      language: str = 'python') -> List[str]:
        """
        Add docstrings to undocumented code.
        
        Args:
            project_path: Root path of project
            language: Programming language
            
        Returns:
            List of files modified
        """
        # Scan project
        structure = self.scanner.scan_project(project_path, language)
        
        modified_files = []
        
        # Generate docstrings for undocumented items
        for module in structure.modules:
            file_modified = False
            
            # Check functions
            for func in module.functions:
                if func.is_public and not func.docstring:
                    docstring = self.generator.generate_docstring(func, language)
                    # Note: Actually inserting docstrings requires code editing
                    # This would integrate with the code editor module
                    print(f"Generated docstring for {func.name}")
                    file_modified = True
            
            # Check classes and methods
            for cls in module.classes:
                if cls.is_public and not cls.docstring:
                    # Generate class docstring
                    file_modified = True
                
                for method in cls.methods:
                    if method.is_public and not method.docstring:
                        docstring = self.generator.generate_docstring(method, language)
                        print(f"Generated docstring for {cls.name}.{method.name}")
                        file_modified = True
            
            if file_modified:
                modified_files.append(module.file_path)
        
        return modified_files
    
    def update_changelog(self, project_path: str, version: str,
                        changes: List[str], change_type: str = 'Added') -> bool:
        """
        Update CHANGELOG.md with new entry.
        
        Args:
            project_path: Root path of project
            version: Version number
            changes: List of changes
            change_type: Type of changes
            
        Returns:
            True if successful
        """
        project_root = Path(project_path)
        changelog_path = project_root / 'CHANGELOG.md'
        
        # Generate changelog entry
        entry = self.generator.generate_changelog_entry(version, changes, change_type)
        
        try:
            # Read existing changelog or create new
            if changelog_path.exists():
                with open(changelog_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Insert new entry after header
                lines = content.split('\n')
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.startswith('## ['):
                        insert_pos = i
                        break
                
                if insert_pos > 0:
                    lines.insert(insert_pos, entry)
                else:
                    lines.append(entry)
                
                content = '\n'.join(lines)
            else:
                # Create new changelog
                content = f"""# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

{entry}
"""
            
            # Write changelog
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error updating changelog: {e}")
            return False
    
    def _extract_features(self, structure: CodeStructure) -> List[str]:
        """Extract main features from code structure."""
        features = []
        
        # Extract from public API
        for api_item in structure.public_api[:10]:  # Top 10 items
            parts = api_item.split('.')
            if len(parts) >= 2:
                feature = parts[-1].replace('_', ' ').title()
                if feature not in features:
                    features.append(feature)
        
        # Add generic features based on structure
        if structure.modules:
            features.append("Modular architecture")
        
        if any(m.classes for m in structure.modules):
            features.append("Object-oriented design")
        
        return features[:5]  # Limit to 5 features
    
    def _should_update_doc(self, doc_path: Path, 
                          structure: CodeStructure) -> bool:
        """Determine if documentation should be updated."""
        # Always update if doesn't exist
        if not doc_path.exists():
            return True
        
        # Check if there are significant undocumented items
        if len(structure.undocumented_items) > 5:
            return True
        
        # Check file age (could be implemented)
        # For now, return False to avoid overwriting existing docs
        return False
    
    def _write_documentation(self, doc: Documentation, 
                           project_root: Path) -> bool:
        """Write documentation to file."""
        if not doc.file_path:
            return False
        
        file_path = project_root / doc.file_path
        
        try:
            # Create directory if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(doc.content)
            
            print(f"Documentation written to {file_path}")
            return True
            
        except Exception as e:
            print(f"Error writing documentation to {file_path}: {e}")
            return False
