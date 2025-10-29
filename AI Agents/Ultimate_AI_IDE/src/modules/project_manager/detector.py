"""
Project Detection Module

Detects project type, language, framework, and structure.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import json


@dataclass
class ProjectInfo:
    """Information about a detected project."""
    path: str
    name: str
    language: str
    framework: Optional[str] = None
    dependencies: List[str] = None
    structure: Dict[str, any] = None
    config_files: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.structure is None:
            self.structure = {}
        if self.config_files is None:
            self.config_files = []


class ProjectDetector:
    """Detects project information from filesystem."""
    
    # Language detection by file extensions
    LANGUAGE_EXTENSIONS = {
        'python': {'.py', '.pyw', '.pyx'},
        'javascript': {'.js', '.mjs', '.cjs', '.jsx'},
        'typescript': {'.ts', '.tsx'},
        'csharp': {'.cs', '.csx'},
        'cpp': {'.cpp', '.cc', '.cxx', '.hpp', '.h'},
        'c': {'.c', '.h'},
        'java': {'.java'},
        'go': {'.go'},
        'rust': {'.rs'},
        'shell': {'.sh', '.bash', '.zsh'},
        'powershell': {'.ps1', '.psm1'},
        'batch': {'.bat', '.cmd'},
        'html': {'.html', '.htm'},
        'css': {'.css', '.scss', '.sass', '.less'},
    }
    
    # Framework detection by config files
    FRAMEWORK_MARKERS = {
        'python': {
            'django': ['manage.py', 'settings.py'],
            'flask': ['app.py', 'wsgi.py'],
            'fastapi': ['main.py'],
        },
        'javascript': {
            'react': ['package.json'],  # Check package.json content
            'nextjs': ['next.config.js', 'next.config.mjs'],
            'express': ['package.json'],  # Check package.json content
            'vue': ['vue.config.js'],
            'angular': ['angular.json'],
        },
        'typescript': {
            'react': ['tsconfig.json', 'package.json'],
            'nextjs': ['next.config.ts', 'tsconfig.json'],
            'nestjs': ['nest-cli.json'],
        },
        'csharp': {
            'aspnet': ['.csproj'],
        }
    }
    
    # Config files to look for
    CONFIG_FILES = {
        'python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
        'javascript': ['package.json', 'package-lock.json', 'yarn.lock'],
        'typescript': ['tsconfig.json', 'package.json'],
        'csharp': ['.csproj', '.sln'],
        'cpp': ['CMakeLists.txt', 'Makefile'],
        'go': ['go.mod', 'go.sum'],
        'rust': ['Cargo.toml', 'Cargo.lock'],
    }
    
    def detect_project(self, path: str) -> Optional[ProjectInfo]:
        """
        Detect project information from a directory.
        
        Args:
            path: Path to project directory
            
        Returns:
            ProjectInfo if valid project detected, None otherwise
        """
        path = Path(path).resolve()
        
        if not path.exists() or not path.is_dir():
            return None
        
        # Detect language
        language = self._detect_language(path)
        if not language:
            return None
        
        # Detect framework
        framework = self._detect_framework(path, language)
        
        # Find config files
        config_files = self._find_config_files(path, language)
        
        # Parse dependencies
        dependencies = self._parse_dependencies(path, language, config_files)
        
        # Analyze structure
        structure = self._analyze_structure(path)
        
        return ProjectInfo(
            path=str(path),
            name=path.name,
            language=language,
            framework=framework,
            dependencies=dependencies,
            structure=structure,
            config_files=config_files
        )
    
    def _detect_language(self, path: Path) -> Optional[str]:
        """Detect primary language by counting file extensions."""
        extension_counts = {}
        
        for file_path in path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
                    if ext in extensions:
                        extension_counts[lang] = extension_counts.get(lang, 0) + 1
        
        if not extension_counts:
            return None
        
        # Return language with most files
        return max(extension_counts, key=extension_counts.get)
    
    def _detect_framework(self, path: Path, language: str) -> Optional[str]:
        """Detect framework based on marker files."""
        # Check for React by .jsx/.tsx files
        if language in ['javascript', 'typescript']:
            has_jsx = any(path.rglob('*.jsx'))
            has_tsx = any(path.rglob('*.tsx'))
            if has_jsx or has_tsx:
                # Verify it's React by checking package.json
                pkg_json = path / 'package.json'
                if pkg_json.exists():
                    try:
                        with open(pkg_json, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            deps = {**data.get('dependencies', {}), 
                                   **data.get('devDependencies', {})}
                            if 'react' in deps:
                                return 'react'
                    except:
                        pass
        
        if language not in self.FRAMEWORK_MARKERS:
            return None
        
        for framework, markers in self.FRAMEWORK_MARKERS[language].items():
            # Check if all marker files exist
            if all((path / marker).exists() or self._find_file(path, marker) 
                   for marker in markers):
                # Additional checks for package.json-based detection
                if 'package.json' in markers:
                    pkg_json = path / 'package.json'
                    if pkg_json.exists():
                        try:
                            with open(pkg_json, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                deps = {**data.get('dependencies', {}), 
                                       **data.get('devDependencies', {})}
                                
                                if framework == 'react' and 'react' in deps:
                                    return 'react'
                                elif framework == 'express' and 'express' in deps:
                                    return 'express'
                        except:
                            pass
                else:
                    return framework
        
        return None
    
    def _find_file(self, path: Path, filename: str) -> bool:
        """Check if file exists in project (recursive search)."""
        for file_path in path.rglob(filename):
            if file_path.is_file():
                return True
        return False
    
    def _find_config_files(self, path: Path, language: str) -> List[str]:
        """Find configuration files for the language."""
        config_files = []
        
        if language in self.CONFIG_FILES:
            for config_file in self.CONFIG_FILES[language]:
                if (path / config_file).exists():
                    config_files.append(config_file)
        
        return config_files
    
    def _parse_dependencies(self, path: Path, language: str, 
                           config_files: List[str]) -> List[str]:
        """Parse dependencies from config files."""
        dependencies = []
        
        try:
            if language == 'python':
                # Parse requirements.txt
                req_file = path / 'requirements.txt'
                if req_file.exists():
                    with open(req_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                # Extract package name (before ==, >=, etc.)
                                pkg = line.split('==')[0].split('>=')[0].split('<=')[0]
                                dependencies.append(pkg.strip())
            
            elif language in ['javascript', 'typescript']:
                # Parse package.json
                pkg_json = path / 'package.json'
                if pkg_json.exists():
                    with open(pkg_json, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        deps = {**data.get('dependencies', {}), 
                               **data.get('devDependencies', {})}
                        dependencies = list(deps.keys())
        
        except Exception:
            pass  # Ignore parsing errors
        
        return dependencies
    
    def _analyze_structure(self, path: Path) -> Dict[str, any]:
        """Analyze project directory structure."""
        structure = {
            'total_files': 0,
            'total_dirs': 0,
            'has_tests': False,
            'has_docs': False,
            'has_src': False,
            'has_git': False,
        }
        
        for item in path.rglob('*'):
            if item.is_file():
                structure['total_files'] += 1
            elif item.is_dir():
                structure['total_dirs'] += 1
                
                dir_name = item.name.lower()
                if dir_name in ['test', 'tests', '__tests__']:
                    structure['has_tests'] = True
                elif dir_name in ['doc', 'docs', 'documentation']:
                    structure['has_docs'] = True
                elif dir_name in ['src', 'source']:
                    structure['has_src'] = True
                elif dir_name == '.git':
                    structure['has_git'] = True
        
        return structure
