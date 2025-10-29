"""
Dependency Tracking Tool - Analyzes codebase dependencies across multiple languages.

This tool provides dependency analysis including:
- Multi-language support (Python, C#, C++, JavaScript, HTML/CSS, Shell, PowerShell, Batch)
- Import and usage tracking
- Circular dependency detection
- Orphaned file identification
- Dependency graph generation
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import sys
import json

from .base import Tool

# Import the DependencyTracker from tools.lib
try:
    from .lib.dependency_tracker import DependencyTracker
    DEPENDENCY_TRACKER_AVAILABLE = True
except ImportError:
    DEPENDENCY_TRACKER_AVAILABLE = False


class DependencyTrackingTool(Tool):
    """
    Tool for tracking code dependencies across the project.
    
    Capabilities:
    - Analyze dependencies for multiple languages
    - Find circular dependencies
    - Identify orphaned files
    - Generate dependency graphs
    - Export dependency reports
    - Get file-specific dependency info
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the dependency tracking tool.
        
        Args:
            config: Configuration dictionary with optional:
                - project_root: Root directory of the project (default: current directory)
                - auto_analyze: Whether to auto-analyze on first use (default: False)
        """
        super().__init__(
            name='dependency_tracking',
            description='Multi-language codebase dependency analysis',
            config=config
        )
        
        if not DEPENDENCY_TRACKER_AVAILABLE:
            self.logger.warning(
                "DependencyTracker not available. Ensure tools/lib/dependency_tracker.py exists"
            )
        
        self.project_root = Path(self.config.get('project_root', '.'))
        self.auto_analyze = self.config.get('auto_analyze', False)
        
        # Lazy-load tracker (expensive operation)
        self._tracker = None
        self._analyzed = False
    
    @property
    def tracker(self) -> 'DependencyTracker':
        """Lazy-load dependency tracker."""
        if not DEPENDENCY_TRACKER_AVAILABLE:
            raise RuntimeError("DependencyTracker is not available")
        
        if self._tracker is None:
            self._tracker = DependencyTracker(str(self.project_root))
            
            if self.auto_analyze:
                self.logger.info("Auto-analyzing dependencies...")
                self._tracker.analyze()
                self._analyzed = True
        
        return self._tracker
    
    def invoke(self, params: Dict[str, Any]) -> Any:
        """
        Execute dependency tracking operation.
        
        Args:
            params: Dictionary with:
                - action: Operation to perform (analyze, get_stats, get_file_deps,
                         find_circular, find_orphaned, export_json, export_markdown,
                         export_graphviz, get_graph)
                - Additional action-specific parameters
                
        Returns:
            Operation result
        """
        if not DEPENDENCY_TRACKER_AVAILABLE:
            return {
                'success': False,
                'error': 'DependencyTracker not available'
            }
        
        self._log_invocation(params)
        
        action = params.get('action')
        if not action:
            raise ValueError("Parameter 'action' is required")
        
        # Route to appropriate method
        if action == 'analyze':
            return self._analyze()
        elif action == 'get_stats':
            return self._get_stats()
        elif action == 'get_file_deps':
            return self._get_file_deps(params.get('filepath'))
        elif action == 'find_circular':
            return self._find_circular()
        elif action == 'find_orphaned':
            return self._find_orphaned()
        elif action == 'export_json':
            return self._export_json(params.get('output_path'))
        elif action == 'export_markdown':
            return self._export_markdown(params.get('output_path'))
        elif action == 'export_graphviz':
            return self._export_graphviz(params.get('output_path'))
        elif action == 'get_graph':
            return self._get_graph()
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _ensure_analyzed(self) -> None:
        """Ensure dependencies have been analyzed."""
        if not self._analyzed:
            self.logger.info("Running dependency analysis...")
            self.tracker.analyze()
            self._analyzed = True
    
    def _analyze(self) -> Dict[str, Any]:
        """Run dependency analysis."""
        try:
            self.tracker.analyze()
            self._analyzed = True
            
            stats = self.tracker.get_dependency_stats()
            
            self.logger.info("Dependency analysis completed")
            
            return {
                'success': True,
                'stats': stats
            }
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_stats(self) -> Dict[str, Any]:
        """Get dependency statistics."""
        self._ensure_analyzed()
        
        try:
            stats = self.tracker.get_dependency_stats()
            
            return {
                'success': True,
                'stats': stats
            }
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_file_deps(self, filepath: str) -> Dict[str, Any]:
        """Get dependencies for a specific file."""
        if not filepath:
            raise ValueError("Parameter 'filepath' is required for get_file_deps")
        
        self._ensure_analyzed()
        
        try:
            # Normalize filepath
            filepath_obj = Path(filepath)
            if filepath_obj.is_absolute():
                normalized = str(filepath_obj.relative_to(self.project_root))
            else:
                normalized = str(filepath)
            
            # Get dependency info
            dep_info = self.tracker.dependencies.get(normalized, {})
            
            if not dep_info:
                return {
                    'success': False,
                    'filepath': filepath,
                    'error': 'File not found in dependency analysis'
                }
            
            return {
                'success': True,
                'filepath': normalized,
                'dependencies': dep_info
            }
        except Exception as e:
            self.logger.error(f"Failed to get file dependencies: {e}")
            return {
                'success': False,
                'filepath': filepath,
                'error': str(e)
            }
    
    def _find_circular(self) -> Dict[str, Any]:
        """Find circular dependencies."""
        self._ensure_analyzed()
        
        try:
            circular = self.tracker.find_circular_dependencies()
            
            return {
                'success': True,
                'circular_dependencies': circular,
                'count': len(circular)
            }
        except Exception as e:
            self.logger.error(f"Failed to find circular dependencies: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _find_orphaned(self) -> Dict[str, Any]:
        """Find orphaned files."""
        self._ensure_analyzed()
        
        try:
            orphaned = self.tracker.find_orphaned_files()
            
            return {
                'success': True,
                'orphaned_files': orphaned,
                'count': len(orphaned)
            }
        except Exception as e:
            self.logger.error(f"Failed to find orphaned files: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _export_json(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Export dependencies as JSON."""
        self._ensure_analyzed()
        
        try:
            # Default output path
            if not output_path:
                output_path = str(self.project_root / '.project' / 'dependencies' / 'dependencies.json')
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.tracker.export_json(output_path)
            
            self.logger.info(f"Exported dependencies to JSON: {output_path}")
            
            return {
                'success': True,
                'output_path': output_path
            }
        except Exception as e:
            self.logger.error(f"Failed to export JSON: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _export_markdown(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Export dependencies as Markdown."""
        self._ensure_analyzed()
        
        try:
            # Default output path
            if not output_path:
                output_path = str(self.project_root / '.project' / 'dependencies' / 'DEPENDENCY_REPORT.md')
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.tracker.export_markdown(output_path)
            
            self.logger.info(f"Exported dependencies to Markdown: {output_path}")
            
            return {
                'success': True,
                'output_path': output_path
            }
        except Exception as e:
            self.logger.error(f"Failed to export Markdown: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _export_graphviz(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Export dependencies as Graphviz DOT file."""
        self._ensure_analyzed()
        
        try:
            # Default output path
            if not output_path:
                output_path = str(self.project_root / '.project' / 'dependencies' / 'dependencies.dot')
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.tracker.export_graphviz(output_path)
            
            self.logger.info(f"Exported dependencies to Graphviz: {output_path}")
            
            return {
                'success': True,
                'output_path': output_path
            }
        except Exception as e:
            self.logger.error(f"Failed to export Graphviz: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_graph(self) -> Dict[str, Any]:
        """Get the dependency graph as a dictionary."""
        self._ensure_analyzed()
        
        try:
            # Convert graph to serializable format
            graph = {}
            
            for file, deps in self.tracker.import_graph.items():
                graph[file] = list(deps)
            
            return {
                'success': True,
                'graph': graph,
                'node_count': len(graph),
                'edge_count': sum(len(deps) for deps in graph.values())
            }
        except Exception as e:
            self.logger.error(f"Failed to get graph: {e}")
            return {
                'success': False,
                'error': str(e)
            }
