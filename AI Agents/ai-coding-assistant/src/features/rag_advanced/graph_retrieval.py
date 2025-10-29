"""
Graph-based Retrieval Module

Uses AST and call graphs to find related code.
Expands context by traversing code relationships.

Example:
    >>> graph_retriever = CodeGraphRetriever(project_root="/path/to/project")
    >>> graph_retriever.build_graph()
    >>> related = graph_retriever.expand_context(["function_123"], depth=2)
"""

from typing import List, Dict, Optional, Any, Set
from pathlib import Path
import ast
import re


class CodeGraphRetriever:
    """
    Graph-based code retrieval using AST and call graphs.
    
    Features:
    - AST-based call graph construction
    - Function/class dependency tracking
    - Context expansion via graph traversal
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize graph retriever.
        
        Args:
            project_root: Path to project root
        """
        self.project_root = Path(project_root) if project_root else None
        self.graph = {}  # node_id -> {callees: [], callers: [], metadata: {}}
        self.node_lookup = {}  # function_name -> node_id
    
    def build_graph(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """
        Build call graph from project AST.
        
        Args:
            force_rebuild: Force rebuild even if graph exists
            
        Returns:
            Graph statistics
        """
        if not self.project_root or not self.project_root.exists():
            raise ValueError("Invalid project root")
        
        if self.graph and not force_rebuild:
            return self._get_graph_stats()
        
        # Reset graph
        self.graph = {}
        self.node_lookup = {}
        
        # Process Python files
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                self._process_file(file_path, content)
            except Exception as e:
                # Skip files with errors
                continue
        
        return self._get_graph_stats()
    
    def _process_file(self, file_path: Path, content: str):
        """Process a single file and extract call relationships."""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return
        
        rel_path = file_path.relative_to(self.project_root)
        
        # Extract functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._process_function(node, str(rel_path))
            elif isinstance(node, ast.ClassDef):
                self._process_class(node, str(rel_path))
    
    def _process_function(self, node: ast.FunctionDef, file_path: str):
        """Process a function node."""
        node_id = f"{file_path}:{node.name}:{node.lineno}"
        
        # Extract function calls
        callees = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    callees.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    callees.append(child.func.attr)
        
        # Store in graph
        self.graph[node_id] = {
            'type': 'function',
            'name': node.name,
            'file': file_path,
            'line': node.lineno,
            'callees': list(set(callees)),
            'callers': [],
            'metadata': {}
        }
        
        self.node_lookup[node.name] = node_id
    
    def _process_class(self, node: ast.ClassDef, file_path: str):
        """Process a class node."""
        node_id = f"{file_path}:{node.name}:{node.lineno}"
        
        # Process class methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_id = f"{file_path}:{node.name}.{item.name}:{item.lineno}"
                methods.append(method_id)
                self._process_function(item, file_path)
        
        # Store class node
        self.graph[node_id] = {
            'type': 'class',
            'name': node.name,
            'file': file_path,
            'line': node.lineno,
            'methods': methods,
            'metadata': {}
        }
        
        self.node_lookup[node.name] = node_id
    
    def expand_context(
        self,
        node_ids: List[str],
        depth: int = 2,
        include_callers: bool = True,
        include_callees: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Expand context using graph traversal.
        
        Args:
            node_ids: Starting node IDs
            depth: Traversal depth
            include_callers: Include functions that call these
            include_callees: Include functions called by these
            
        Returns:
            List of related nodes with metadata
        """
        visited = set()
        result = []
        queue = [(nid, 0) for nid in node_ids]
        
        while queue:
            node_id, current_depth = queue.pop(0)
            
            if node_id in visited or current_depth > depth:
                continue
            
            visited.add(node_id)
            
            if node_id not in self.graph:
                continue
            
            node = self.graph[node_id]
            result.append({
                'node_id': node_id,
                'depth': current_depth,
                **node
            })
            
            # Add neighbors to queue
            if current_depth < depth:
                if include_callees:
                    for callee_name in node.get('callees', []):
                        if callee_name in self.node_lookup:
                            callee_id = self.node_lookup[callee_name]
                            if callee_id not in visited:
                                queue.append((callee_id, current_depth + 1))
                
                if include_callers:
                    for caller_id in node.get('callers', []):
                        if caller_id not in visited:
                            queue.append((caller_id, current_depth + 1))
        
        return result
    
    def find_related(
        self,
        function_name: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find functions related to given function.
        
        Args:
            function_name: Function name to search
            max_results: Maximum results
            
        Returns:
            List of related functions
        """
        if function_name not in self.node_lookup:
            return []
        
        node_id = self.node_lookup[function_name]
        related = self.expand_context([node_id], depth=2)
        
        return related[:max_results]
    
    def get_dependencies(self, node_id: str) -> List[str]:
        """
        Get direct dependencies of a node.
        
        Args:
            node_id: Node identifier
            
        Returns:
            List of dependency node IDs
        """
        if node_id not in self.graph:
            return []
        
        node = self.graph[node_id]
        dependencies = []
        
        for callee_name in node.get('callees', []):
            if callee_name in self.node_lookup:
                dependencies.append(self.node_lookup[callee_name])
        
        return dependencies
    
    def get_dependents(self, node_id: str) -> List[str]:
        """
        Get nodes that depend on this node.
        
        Args:
            node_id: Node identifier
            
        Returns:
            List of dependent node IDs
        """
        if node_id not in self.graph:
            return []
        
        return self.graph[node_id].get('callers', [])
    
    def _get_graph_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        total_nodes = len(self.graph)
        functions = sum(1 for n in self.graph.values() if n['type'] == 'function')
        classes = sum(1 for n in self.graph.values() if n['type'] == 'class')
        
        return {
            'total_nodes': total_nodes,
            'functions': functions,
            'classes': classes,
            'files': len(set(n['file'] for n in self.graph.values()))
        }
    
    def visualize_subgraph(
        self,
        node_ids: List[str],
        depth: int = 1,
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate visualization of subgraph.
        
        Args:
            node_ids: Starting nodes
            depth: Depth to visualize
            output_file: Optional file to save to
            
        Returns:
            DOT format string
        """
        nodes = self.expand_context(node_ids, depth=depth)
        
        # Generate DOT format
        dot_lines = ["digraph CodeGraph {"]
        dot_lines.append("  node [shape=box];")
        
        for node in nodes:
            node_id = node['node_id']
            label = f"{node['name']}\\n{node['file']}"
            dot_lines.append(f'  "{node_id}" [label="{label}"];')
            
            # Add edges
            for callee_name in node.get('callees', []):
                if callee_name in self.node_lookup:
                    callee_id = self.node_lookup[callee_name]
                    if any(n['node_id'] == callee_id for n in nodes):
                        dot_lines.append(f'  "{node_id}" -> "{callee_id}";')
        
        dot_lines.append("}")
        dot_content = "\n".join(dot_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(dot_content)
        
        return dot_content


if __name__ == "__main__":
    print("Graph-based Retrieval Module")
    print("=============================\n")
    print("This module provides AST-based call graph retrieval.")
    print("\nFeatures:")
    print("  - Call graph construction")
    print("  - Context expansion")
    print("  - Dependency tracking")
    print("\nNote: Basic implementation provided. Can be extended with:")
    print("  - Cross-language support")
    print("  - Import graph")
    print("  - Class hierarchy")
