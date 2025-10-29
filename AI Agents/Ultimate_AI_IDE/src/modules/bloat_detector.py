"""
Bloat Detector Module

Detects and removes unnecessary files, code, and dependencies from projects.
Ensures zero-bloat project initialization and maintenance.
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class BloatDetector:
    """Detects and manages code bloat in projects."""
    
    # Common bloat patterns
    EXAMPLE_PATTERNS = [
        r'example.*\.py$',
        r'sample.*\.py$',
        r'demo.*\.py$',
        r'test_example.*\.py$',
        r'.*\.example\..*$',
    ]
    
    UNNECESSARY_FILES = {
        '.DS_Store',
        'Thumbs.db',
        'desktop.ini',
        '.vscode/settings.json.default',
        '.idea/workspace.xml.default',
    }
    
    BLOAT_COMMENTS = [
        'TODO: Remove this example',
        'Example code',
        'Sample implementation',
        'Demo code',
        'This is just a placeholder',
    ]
    
    def __init__(self, project_path: str):
        """
        Initialize bloat detector.
        
        Args:
            project_path: Path to project root
        """
        self.project_path = Path(project_path)
        self.bloat_items: List[Dict] = []
    
    def detect_all(self) -> Dict[str, List[Dict]]:
        """
        Detect all types of bloat.
        
        Returns:
            Dictionary with bloat categories and items
        """
        results = {
            'unnecessary_files': self.detect_unnecessary_files(),
            'example_code': self.detect_example_code(),
            'unused_dependencies': self.detect_unused_dependencies(),
            'redundant_code': self.detect_redundant_code(),
            'empty_files': self.detect_empty_files(),
            'bloat_comments': self.detect_bloat_comments(),
        }
        
        total_items = sum(len(items) for items in results.values())
        logger.info(f"Detected {total_items} bloat items across {len(results)} categories")
        
        return results
    
    def detect_unnecessary_files(self) -> List[Dict]:
        """
        Detect unnecessary files (OS-specific, temp files, etc.).
        
        Returns:
            List of unnecessary file info
        """
        unnecessary = []
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}]
            
            for file in files:
                if file in self.UNNECESSARY_FILES:
                    file_path = Path(root) / file
                    unnecessary.append({
                        'type': 'unnecessary_file',
                        'path': str(file_path.relative_to(self.project_path)),
                        'reason': 'OS-specific or temporary file',
                        'size': file_path.stat().st_size if file_path.exists() else 0
                    })
        
        return unnecessary
    
    def detect_example_code(self) -> List[Dict]:
        """
        Detect example/demo/sample code files.
        
        Returns:
            List of example code files
        """
        examples = []
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}]
            
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.project_path)
                
                # Check filename patterns
                for pattern in self.EXAMPLE_PATTERNS:
                    if re.match(pattern, file, re.IGNORECASE):
                        examples.append({
                            'type': 'example_code',
                            'path': str(rel_path),
                            'reason': f'Matches example pattern: {pattern}',
                            'size': file_path.stat().st_size
                        })
                        break
        
        return examples
    
    def detect_unused_dependencies(self) -> List[Dict]:
        """
        Detect unused dependencies in requirements.txt or package.json.
        
        Returns:
            List of potentially unused dependencies
        """
        unused = []
        
        # Check Python dependencies
        req_file = self.project_path / 'requirements.txt'
        if req_file.exists():
            unused.extend(self._check_python_dependencies(req_file))
        
        # Check Node.js dependencies
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            unused.extend(self._check_node_dependencies(package_json))
        
        return unused
    
    def _check_python_dependencies(self, req_file: Path) -> List[Dict]:
        """Check Python dependencies for usage."""
        unused = []
        
        try:
            with open(req_file, 'r', encoding='utf-8') as f:
                requirements = [line.strip().split('==')[0].split('>=')[0].split('<=')[0] 
                               for line in f if line.strip() and not line.startswith('#')]
            
            # Get all Python imports in project
            imports = self._get_all_imports()
            
            for req in requirements:
                # Normalize package name (e.g., 'python-dotenv' -> 'dotenv')
                normalized = req.lower().replace('-', '_').replace('.', '_')
                
                # Check if imported anywhere
                if not any(normalized in imp.lower() for imp in imports):
                    unused.append({
                        'type': 'unused_dependency',
                        'name': req,
                        'file': 'requirements.txt',
                        'reason': 'Not imported in any Python file'
                    })
        
        except Exception as e:
            logger.error(f"Error checking Python dependencies: {e}")
        
        return unused
    
    def _check_node_dependencies(self, package_json: Path) -> List[Dict]:
        """Check Node.js dependencies for usage."""
        unused = []
        
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            dependencies = package_data.get('dependencies', {})
            
            # Get all require/import statements in JS/TS files
            imports = self._get_all_js_imports()
            
            for dep in dependencies:
                if not any(dep in imp for imp in imports):
                    unused.append({
                        'type': 'unused_dependency',
                        'name': dep,
                        'file': 'package.json',
                        'reason': 'Not imported in any JS/TS file'
                    })
        
        except Exception as e:
            logger.error(f"Error checking Node dependencies: {e}")
        
        return unused
    
    def _get_all_imports(self) -> Set[str]:
        """Get all Python imports in project."""
        imports = set()
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            tree = ast.parse(f.read())
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    imports.add(alias.name.split('.')[0])
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    imports.add(node.module.split('.')[0])
                    except:
                        pass
        
        return imports
    
    def _get_all_js_imports(self) -> Set[str]:
        """Get all JS/TS imports in project."""
        imports = set()
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}]
            
            for file in files:
                if file.endswith(('.js', '.ts', '.jsx', '.tsx')):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Find require() and import statements
                        require_pattern = r"require\(['\"]([^'\"]+)['\"]\)"
                        import_pattern = r"import\s+.*\s+from\s+['\"]([^'\"]+)['\"]"
                        
                        imports.update(re.findall(require_pattern, content))
                        imports.update(re.findall(import_pattern, content))
                    except:
                        pass
        
        return imports
    
    def detect_redundant_code(self) -> List[Dict]:
        """
        Detect redundant or duplicate code.
        
        Returns:
            List of redundant code items
        """
        redundant = []
        
        # Detect duplicate functions
        function_signatures = {}
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            tree = ast.parse(f.read())
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                sig = f"{node.name}_{len(node.args.args)}"
                                if sig in function_signatures:
                                    redundant.append({
                                        'type': 'duplicate_function',
                                        'name': node.name,
                                        'path': str(file_path.relative_to(self.project_path)),
                                        'also_in': function_signatures[sig],
                                        'reason': 'Potential duplicate function'
                                    })
                                else:
                                    function_signatures[sig] = str(file_path.relative_to(self.project_path))
                    except:
                        pass
        
        return redundant
    
    def detect_empty_files(self) -> List[Dict]:
        """
        Detect empty or nearly empty files.
        
        Returns:
            List of empty files
        """
        empty = []
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.css', '.html')):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                        
                        # Count non-comment, non-whitespace lines
                        lines = [l for l in content.split('\n') if l.strip() and not l.strip().startswith(('#', '//'))]
                        
                        if len(lines) == 0:
                            empty.append({
                                'type': 'empty_file',
                                'path': str(file_path.relative_to(self.project_path)),
                                'reason': 'File is empty or contains only comments',
                                'size': file_path.stat().st_size
                            })
                    except:
                        pass
        
        return empty
    
    def detect_bloat_comments(self) -> List[Dict]:
        """
        Detect bloat-indicating comments (TODO remove, example, etc.).
        
        Returns:
            List of files with bloat comments
        """
        bloat_comments = []
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        for i, line in enumerate(content.split('\n'), 1):
                            for pattern in self.BLOAT_COMMENTS:
                                if pattern.lower() in line.lower():
                                    bloat_comments.append({
                                        'type': 'bloat_comment',
                                        'path': str(file_path.relative_to(self.project_path)),
                                        'line': i,
                                        'comment': line.strip(),
                                        'reason': f'Contains bloat indicator: {pattern}'
                                    })
                    except:
                        pass
        
        return bloat_comments
    
    def generate_cleanup_plan(self, bloat_results: Dict[str, List[Dict]]) -> Dict:
        """
        Generate a cleanup plan based on detected bloat.
        
        Args:
            bloat_results: Results from detect_all()
            
        Returns:
            Cleanup plan with actions
        """
        plan = {
            'summary': {
                'total_items': sum(len(items) for items in bloat_results.values()),
                'categories': {k: len(v) for k, v in bloat_results.items()},
                'estimated_space_saved': 0
            },
            'actions': []
        }
        
        # Calculate space savings
        for category, items in bloat_results.items():
            for item in items:
                if 'size' in item:
                    plan['summary']['estimated_space_saved'] += item['size']
        
        # Generate actions
        for category, items in bloat_results.items():
            for item in items:
                action = {
                    'type': category,
                    'action': self._get_action_for_item(item),
                    'item': item,
                    'risk': self._assess_risk(item)
                }
                plan['actions'].append(action)
        
        return plan
    
    def _get_action_for_item(self, item: Dict) -> str:
        """Determine appropriate action for bloat item."""
        item_type = item.get('type', '')
        
        actions = {
            'unnecessary_file': 'delete',
            'example_code': 'delete',
            'empty_file': 'delete',
            'unused_dependency': 'remove_from_requirements',
            'duplicate_function': 'review_and_consolidate',
            'bloat_comment': 'remove_comment'
        }
        
        return actions.get(item_type, 'review')
    
    def _assess_risk(self, item: Dict) -> str:
        """Assess risk level of removing item."""
        item_type = item.get('type', '')
        
        # Low risk items
        if item_type in {'unnecessary_file', 'empty_file', 'bloat_comment'}:
            return 'low'
        
        # Medium risk items
        if item_type in {'example_code', 'unused_dependency'}:
            return 'medium'
        
        # High risk items
        if item_type in {'duplicate_function', 'redundant_code'}:
            return 'high'
        
        return 'medium'
    
    def execute_cleanup(self, plan: Dict, auto_approve_low_risk: bool = True) -> Dict:
        """
        Execute cleanup plan.
        
        Args:
            plan: Cleanup plan from generate_cleanup_plan()
            auto_approve_low_risk: Automatically execute low-risk actions
            
        Returns:
            Execution results
        """
        results = {
            'executed': 0,
            'skipped': 0,
            'failed': 0,
            'actions': []
        }
        
        for action in plan['actions']:
            if action['risk'] == 'low' and auto_approve_low_risk:
                try:
                    self._execute_action(action)
                    results['executed'] += 1
                    results['actions'].append({
                        'action': action,
                        'status': 'success'
                    })
                except Exception as e:
                    results['failed'] += 1
                    results['actions'].append({
                        'action': action,
                        'status': 'failed',
                        'error': str(e)
                    })
            else:
                results['skipped'] += 1
                results['actions'].append({
                    'action': action,
                    'status': 'skipped',
                    'reason': 'Requires manual approval'
                })
        
        logger.info(f"Cleanup executed: {results['executed']} actions, {results['skipped']} skipped, {results['failed']} failed")
        
        return results
    
    def _execute_action(self, action: Dict):
        """Execute a single cleanup action."""
        action_type = action['action']
        item = action['item']
        
        if action_type == 'delete':
            file_path = self.project_path / item['path']
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted: {item['path']}")
        
        elif action_type == 'remove_comment':
            # Remove bloat comment from file
            file_path = self.project_path / item['path']
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Remove the specific line
                if 0 < item['line'] <= len(lines):
                    lines.pop(item['line'] - 1)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                logger.info(f"Removed bloat comment from: {item['path']}")
