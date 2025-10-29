"""
Dead Code Detector Module

Advanced dead code detection with call graph analysis.
Detects unused functions, classes, and unreachable code.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class DeadCodeDetector:
    """Detect dead and unreachable code"""
    
    def __init__(self, project_path: str):
        """
        Initialize dead code detector
        
        Args:
            project_path: Path to project root
        """
        self.project_path = Path(project_path)
        self.call_graph = defaultdict(set)
        self.definitions = {}  # name -> file_path
        self.usages = defaultdict(set)  # name -> set of files using it
        self.entry_points = set()
    
    def analyze_project(self) -> Dict[str, any]:
        """
        Analyze entire project for dead code
        
        Returns:
            Analysis results
        """
        logger.info("Building call graph...")
        self._build_call_graph()
        
        logger.info("Detecting dead code...")
        results = {
            'unused_functions': self.detect_unused_functions(),
            'unused_classes': self.detect_unused_classes(),
            'unreachable_code': self.detect_unreachable_code(),
            'orphaned_files': self.detect_orphaned_files()
        }
        
        total_dead = sum(len(items) for items in results.values())
        logger.info(f"Found {total_dead} dead code items")
        
        return results
    
    def _build_call_graph(self):
        """Build call graph for the project"""
        python_files = list(self.project_path.rglob('*.py'))
        
        # Skip test files and common directories
        python_files = [
            f for f in python_files
            if not any(skip in str(f) for skip in ['test_', '__pycache__', '.venv', 'venv'])
        ]
        
        # First pass: collect all definitions
        for file_path in python_files:
            self._collect_definitions(file_path)
        
        # Second pass: collect all usages
        for file_path in python_files:
            self._collect_usages(file_path)
        
        # Identify entry points
        self._identify_entry_points()
    
    def _collect_definitions(self, file_path: Path):
        """Collect function and class definitions"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    self.definitions[func_name] = str(file_path.relative_to(self.project_path))
                
                elif isinstance(node, ast.ClassDef):
                    class_name = node.name
                    self.definitions[class_name] = str(file_path.relative_to(self.project_path))
                    
                    # Also collect methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_name = f"{class_name}.{item.name}"
                            self.definitions[method_name] = str(file_path.relative_to(self.project_path))
        
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")
    
    def _collect_usages(self, file_path: Path):
        """Collect function and class usages"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            rel_path = str(file_path.relative_to(self.project_path))
            
            for node in ast.walk(tree):
                # Function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        self.usages[node.func.id].add(rel_path)
                    elif isinstance(node.func, ast.Attribute):
                        # Method calls like obj.method()
                        if isinstance(node.func.value, ast.Name):
                            method_name = f"{node.func.value.id}.{node.func.attr}"
                            self.usages[method_name].add(rel_path)
                
                # Class instantiation
                elif isinstance(node, ast.Name):
                    self.usages[node.id].add(rel_path)
        
        except Exception as e:
            logger.warning(f"Error analyzing {file_path}: {e}")
    
    def _identify_entry_points(self):
        """Identify entry points (main, __init__, etc.)"""
        # Common entry points
        entry_patterns = [
            'main',
            '__main__',
            '__init__',
            'run',
            'execute',
            'start',
            'app',
            'cli'
        ]
        
        for name in self.definitions:
            if any(pattern in name.lower() for pattern in entry_patterns):
                self.entry_points.add(name)
        
        # Also consider anything imported in __init__.py as entry point
        for file_path in self.project_path.rglob('__init__.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            self.entry_points.add(alias.name)
            except:
                pass
    
    def detect_unused_functions(self) -> List[Dict]:
        """Detect functions that are never called"""
        unused = []
        
        for name, file_path in self.definitions.items():
            # Skip special methods and entry points
            if name.startswith('_') or name in self.entry_points:
                continue
            
            # Skip if it's a method (contains '.')
            if '.' in name:
                continue
            
            # Check if used anywhere
            if name not in self.usages or len(self.usages[name]) == 0:
                unused.append({
                    'type': 'unused_function',
                    'name': name,
                    'file': file_path,
                    'reason': 'Function is never called',
                    'safe_to_remove': True
                })
            # Check if only used in same file (potential dead code)
            elif len(self.usages[name]) == 1 and list(self.usages[name])[0] == file_path:
                unused.append({
                    'type': 'unused_function',
                    'name': name,
                    'file': file_path,
                    'reason': 'Function only used in same file',
                    'safe_to_remove': False  # Might be internal helper
                })
        
        return unused
    
    def detect_unused_classes(self) -> List[Dict]:
        """Detect classes that are never instantiated"""
        unused = []
        
        for name, file_path in self.definitions.items():
            # Skip if it's a method
            if '.' in name:
                continue
            
            # Check if it looks like a class (starts with capital)
            if not name[0].isupper():
                continue
            
            # Skip entry points
            if name in self.entry_points:
                continue
            
            # Check if used anywhere
            if name not in self.usages or len(self.usages[name]) == 0:
                unused.append({
                    'type': 'unused_class',
                    'name': name,
                    'file': file_path,
                    'reason': 'Class is never instantiated or referenced',
                    'safe_to_remove': True
                })
        
        return unused
    
    def detect_unreachable_code(self) -> List[Dict]:
        """Detect unreachable code blocks"""
        unreachable = []
        
        for file_path in self.project_path.rglob('*.py'):
            if any(skip in str(file_path) for skip in ['test_', '__pycache__', '.venv']):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                rel_path = str(file_path.relative_to(self.project_path))
                
                # Check for code after return/raise/break/continue
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        unreachable_in_func = self._check_unreachable_in_function(node, content)
                        for item in unreachable_in_func:
                            item['file'] = rel_path
                            unreachable.append(item)
            
            except Exception as e:
                logger.warning(f"Error checking {file_path}: {e}")
        
        return unreachable
    
    def _check_unreachable_in_function(self, func_node: ast.FunctionDef, content: str) -> List[Dict]:
        """Check for unreachable code in a function"""
        unreachable = []
        
        def check_block(statements: List[ast.stmt]) -> bool:
            """Check if block has unreachable code"""
            for i, stmt in enumerate(statements):
                # If we hit return/raise, everything after is unreachable
                if isinstance(stmt, (ast.Return, ast.Raise)):
                    if i < len(statements) - 1:
                        next_stmt = statements[i + 1]
                        unreachable.append({
                            'type': 'unreachable_code',
                            'function': func_node.name,
                            'line': next_stmt.lineno,
                            'reason': f'Code after {stmt.__class__.__name__.lower()} statement',
                            'safe_to_remove': True
                        })
                        return True
                
                # Check nested blocks
                if isinstance(stmt, ast.If):
                    check_block(stmt.body)
                    check_block(stmt.orelse)
                elif isinstance(stmt, (ast.For, ast.While)):
                    check_block(stmt.body)
                elif isinstance(stmt, ast.Try):
                    check_block(stmt.body)
                    for handler in stmt.handlers:
                        check_block(handler.body)
            
            return False
        
        check_block(func_node.body)
        return unreachable
    
    def detect_orphaned_files(self) -> List[Dict]:
        """Detect Python files that are never imported"""
        orphaned = []
        
        # Get all Python files
        python_files = set(
            str(f.relative_to(self.project_path))
            for f in self.project_path.rglob('*.py')
            if not any(skip in str(f) for skip in ['test_', '__pycache__', '.venv'])
        )
        
        # Get all imported files
        imported_files = set()
        for file_path in self.project_path.rglob('*.py'):
            if any(skip in str(file_path) for skip in ['test_', '__pycache__', '.venv']):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module:
                            # Convert module path to file path
                            module_file = node.module.replace('.', os.sep) + '.py'
                            imported_files.add(module_file)
            except:
                pass
        
        # Find orphaned files
        for file_path in python_files:
            # Skip __init__.py and __main__.py
            if file_path.endswith(('__init__.py', '__main__.py')):
                continue
            
            # Skip entry point files
            if any(entry in file_path for entry in ['main.py', 'cli.py', 'app.py']):
                continue
            
            if file_path not in imported_files:
                orphaned.append({
                    'type': 'orphaned_file',
                    'file': file_path,
                    'reason': 'File is never imported',
                    'safe_to_remove': False  # Might be entry point
                })
        
        return orphaned
    
    def generate_removal_plan(self, analysis_results: Dict) -> Dict:
        """
        Generate a safe removal plan
        
        Args:
            analysis_results: Results from analyze_project()
            
        Returns:
            Removal plan with safety assessment
        """
        plan = {
            'safe_to_remove': [],
            'review_required': [],
            'summary': {
                'total_items': 0,
                'safe_items': 0,
                'review_items': 0
            }
        }
        
        for category, items in analysis_results.items():
            for item in items:
                plan['summary']['total_items'] += 1
                
                if item.get('safe_to_remove', False):
                    plan['safe_to_remove'].append(item)
                    plan['summary']['safe_items'] += 1
                else:
                    plan['review_required'].append(item)
                    plan['summary']['review_items'] += 1
        
        return plan
    
    def get_usage_report(self, name: str) -> Dict:
        """
        Get detailed usage report for a function/class
        
        Args:
            name: Function or class name
            
        Returns:
            Usage report
        """
        return {
            'name': name,
            'defined_in': self.definitions.get(name, 'Unknown'),
            'used_in': list(self.usages.get(name, [])),
            'usage_count': len(self.usages.get(name, [])),
            'is_entry_point': name in self.entry_points
        }
