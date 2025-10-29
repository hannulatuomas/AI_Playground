"""
Graph-Based Retriever

Retrieves code context using AST call graphs and dependency analysis.
Part of v1.6.0 - Advanced RAG & Retrieval.
"""

import os
import ast
import logging
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class CodeNode:
    """Node in the code graph."""
    name: str
    node_type: str  # 'function', 'class', 'method', 'import'
    file_path: str
    line_number: int
    code: str
    dependencies: Set[str]
    dependents: Set[str]


class CallGraphBuilder:
    """Builds call graphs from Python code."""
    
    def __init__(self):
        """Initialize call graph builder."""
        self.graph = {}  # name -> CodeNode
        self.file_nodes = defaultdict(list)  # file_path -> List[CodeNode]
        logger.info("Initialized CallGraphBuilder")
    
    def build_from_file(self, file_path: str) -> bool:
        """
        Build call graph from a Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            True if successful
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=file_path)
            
            # Extract functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self._add_function(node, file_path, source)
                elif isinstance(node, ast.ClassDef):
                    self._add_class(node, file_path, source)
            
            logger.debug(f"Built call graph for: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to build call graph for {file_path}: {e}")
            return False
    
    def _add_function(self, node: ast.FunctionDef, file_path: str, source: str):
        """Add function node to graph."""
        try:
            # Get function code
            code_lines = source.split('\n')
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 10
            code = '\n'.join(code_lines[start_line:end_line])
            
            # Extract dependencies (function calls)
            dependencies = set()
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        dependencies.add(child.func.id)
                    elif isinstance(child.func, ast.Attribute):
                        dependencies.add(child.func.attr)
            
            # Create node
            code_node = CodeNode(
                name=node.name,
                node_type='function',
                file_path=file_path,
                line_number=node.lineno,
                code=code,
                dependencies=dependencies,
                dependents=set()
            )
            
            self.graph[node.name] = code_node
            self.file_nodes[file_path].append(code_node)
            
        except Exception as e:
            logger.error(f"Failed to add function {node.name}: {e}")
    
    def _add_class(self, node: ast.ClassDef, file_path: str, source: str):
        """Add class node to graph."""
        try:
            # Get class code
            code_lines = source.split('\n')
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 20
            code = '\n'.join(code_lines[start_line:end_line])
            
            # Extract dependencies
            dependencies = set()
            for child in node.bases:
                if isinstance(child, ast.Name):
                    dependencies.add(child.id)
            
            # Create node
            code_node = CodeNode(
                name=node.name,
                node_type='class',
                file_path=file_path,
                line_number=node.lineno,
                code=code,
                dependencies=dependencies,
                dependents=set()
            )
            
            self.graph[node.name] = code_node
            self.file_nodes[file_path].append(code_node)
            
            # Add methods
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_name = f"{node.name}.{item.name}"
                    self._add_method(item, node.name, file_path, source)
            
        except Exception as e:
            logger.error(f"Failed to add class {node.name}: {e}")
    
    def _add_method(self, node: ast.FunctionDef, class_name: str, file_path: str, source: str):
        """Add method node to graph."""
        try:
            code_lines = source.split('\n')
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 10
            code = '\n'.join(code_lines[start_line:end_line])
            
            # Extract dependencies
            dependencies = set()
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        dependencies.add(child.func.id)
                    elif isinstance(child.func, ast.Attribute):
                        dependencies.add(child.func.attr)
            
            method_name = f"{class_name}.{node.name}"
            
            code_node = CodeNode(
                name=method_name,
                node_type='method',
                file_path=file_path,
                line_number=node.lineno,
                code=code,
                dependencies=dependencies,
                dependents=set()
            )
            
            self.graph[method_name] = code_node
            self.file_nodes[file_path].append(code_node)
            
        except Exception as e:
            logger.error(f"Failed to add method {node.name}: {e}")
    
    def resolve_dependencies(self):
        """Resolve dependencies and build reverse edges."""
        for node_name, node in self.graph.items():
            for dep in node.dependencies:
                if dep in self.graph:
                    self.graph[dep].dependents.add(node_name)
        
        logger.info("Resolved dependencies in call graph")


class GraphRetriever:
    """
    Graph-based code retriever.
    
    Features:
    - Build AST call graph
    - Traverse dependencies
    - Context expansion
    - Related code discovery
    """
    
    def __init__(self):
        """Initialize graph retriever."""
        self.call_graph = CallGraphBuilder()
        logger.info("Initialized GraphRetriever")
    
    def index_file(self, file_path: str) -> bool:
        """
        Index a code file.
        
        Args:
            file_path: Path to code file
            
        Returns:
            True if successful
        """
        return self.call_graph.build_from_file(file_path)
    
    def index_directory(self, directory: str, extensions: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Index all code files in a directory.
        
        Args:
            directory: Directory to index
            extensions: File extensions to index
            
        Returns:
            Statistics dict
        """
        if extensions is None:
            extensions = ['.py']  # Currently only Python supported
        
        stats = {'files': 0, 'nodes': 0, 'errors': 0}
        
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        file_path = os.path.join(root, file)
                        if self.index_file(file_path):
                            stats['files'] += 1
                        else:
                            stats['errors'] += 1
            
            # Resolve dependencies
            self.call_graph.resolve_dependencies()
            stats['nodes'] = len(self.call_graph.graph)
            
            logger.info(f"Indexed directory: {directory} - {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to index directory {directory}: {e}")
            return stats
    
    def find_node(self, name: str) -> Optional[CodeNode]:
        """
        Find a node by name.
        
        Args:
            name: Node name
            
        Returns:
            CodeNode or None
        """
        return self.call_graph.graph.get(name)
    
    def get_dependencies(self, name: str, depth: int = 1) -> List[CodeNode]:
        """
        Get dependencies of a node.
        
        Args:
            name: Node name
            depth: Traversal depth
            
        Returns:
            List of dependent nodes
        """
        result = []
        visited = set()
        
        def traverse(node_name: str, current_depth: int):
            if current_depth > depth or node_name in visited:
                return
            
            visited.add(node_name)
            node = self.call_graph.graph.get(node_name)
            
            if node:
                result.append(node)
                for dep in node.dependencies:
                    traverse(dep, current_depth + 1)
        
        traverse(name, 0)
        return result
    
    def get_dependents(self, name: str, depth: int = 1) -> List[CodeNode]:
        """
        Get dependents of a node (reverse dependencies).
        
        Args:
            name: Node name
            depth: Traversal depth
            
        Returns:
            List of dependent nodes
        """
        result = []
        visited = set()
        
        def traverse(node_name: str, current_depth: int):
            if current_depth > depth or node_name in visited:
                return
            
            visited.add(node_name)
            node = self.call_graph.graph.get(node_name)
            
            if node:
                result.append(node)
                for dep in node.dependents:
                    traverse(dep, current_depth + 1)
        
        traverse(name, 0)
        return result
    
    def expand_context(self, name: str, expansion_depth: int = 2) -> str:
        """
        Expand context around a node.
        
        Args:
            name: Node name
            expansion_depth: How far to expand
            
        Returns:
            Expanded context string
        """
        try:
            # Get the node
            node = self.find_node(name)
            if not node:
                return ""
            
            # Get dependencies and dependents
            deps = self.get_dependencies(name, expansion_depth)
            dependents = self.get_dependents(name, expansion_depth)
            
            # Build context
            context_parts = [f"# Main: {node.name}\n{node.code}\n"]
            
            if deps:
                context_parts.append("\n# Dependencies:")
                for dep in deps[:5]:  # Limit to 5
                    context_parts.append(f"\n## {dep.name} ({dep.file_path}:{dep.line_number})\n{dep.code}\n")
            
            if dependents:
                context_parts.append("\n# Used by:")
                for dep in dependents[:5]:  # Limit to 5
                    context_parts.append(f"\n## {dep.name} ({dep.file_path}:{dep.line_number})\n{dep.code}\n")
            
            context = "\n".join(context_parts)
            logger.info(f"Expanded context for {name}: {len(deps)} deps, {len(dependents)} dependents")
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to expand context for {name}: {e}")
            return ""
    
    def find_related_code(self, name: str, max_results: int = 10) -> List[CodeNode]:
        """
        Find code related to a given node.
        
        Args:
            name: Node name
            max_results: Maximum results
            
        Returns:
            List of related nodes
        """
        try:
            node = self.find_node(name)
            if not node:
                return []
            
            # Get all related nodes
            related = set()
            
            # Add dependencies
            deps = self.get_dependencies(name, depth=2)
            related.update(n.name for n in deps)
            
            # Add dependents
            dependents = self.get_dependents(name, depth=2)
            related.update(n.name for n in dependents)
            
            # Get nodes from same file
            file_nodes = self.call_graph.file_nodes.get(node.file_path, [])
            related.update(n.name for n in file_nodes)
            
            # Remove self
            related.discard(name)
            
            # Get node objects
            result = [self.call_graph.graph[n] for n in related if n in self.call_graph.graph]
            
            logger.info(f"Found {len(result)} related nodes for {name}")
            return result[:max_results]
            
        except Exception as e:
            logger.error(f"Failed to find related code for {name}: {e}")
            return []
    
    def search_by_pattern(self, pattern: str) -> List[CodeNode]:
        """
        Search nodes by name pattern.
        
        Args:
            pattern: Search pattern (substring)
            
        Returns:
            List of matching nodes
        """
        results = []
        pattern_lower = pattern.lower()
        
        for name, node in self.call_graph.graph.items():
            if pattern_lower in name.lower():
                results.append(node)
        
        logger.info(f"Found {len(results)} nodes matching pattern: {pattern}")
        return results
    
    def get_call_chain(self, from_name: str, to_name: str) -> Optional[List[str]]:
        """
        Find call chain from one node to another.
        
        Args:
            from_name: Starting node
            to_name: Target node
            
        Returns:
            List of node names in the chain, or None
        """
        try:
            # BFS to find shortest path
            from collections import deque
            
            queue = deque([(from_name, [from_name])])
            visited = {from_name}
            
            while queue:
                current, path = queue.popleft()
                
                if current == to_name:
                    return path
                
                node = self.call_graph.graph.get(current)
                if node:
                    for dep in node.dependencies:
                        if dep not in visited:
                            visited.add(dep)
                            queue.append((dep, path + [dep]))
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find call chain: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get retriever statistics."""
        total_deps = sum(len(node.dependencies) for node in self.call_graph.graph.values())
        total_dependents = sum(len(node.dependents) for node in self.call_graph.graph.values())
        
        node_types = defaultdict(int)
        for node in self.call_graph.graph.values():
            node_types[node.node_type] += 1
        
        return {
            'total_nodes': len(self.call_graph.graph),
            'total_files': len(self.call_graph.file_nodes),
            'total_dependencies': total_deps,
            'total_dependents': total_dependents,
            'node_types': dict(node_types),
            'avg_dependencies': total_deps / len(self.call_graph.graph) if self.call_graph.graph else 0
        }
    
    def export_graph(self, output_file: str, format: str = 'dot') -> bool:
        """
        Export call graph to file.
        
        Args:
            output_file: Output file path
            format: Export format ('dot', 'json')
            
        Returns:
            True if successful
        """
        try:
            if format == 'dot':
                # Export as Graphviz DOT format
                with open(output_file, 'w') as f:
                    f.write("digraph CallGraph {\n")
                    for name, node in self.call_graph.graph.items():
                        for dep in node.dependencies:
                            if dep in self.call_graph.graph:
                                f.write(f'  "{name}" -> "{dep}";\n')
                    f.write("}\n")
            
            elif format == 'json':
                import json
                # Export as JSON
                graph_data = {}
                for name, node in self.call_graph.graph.items():
                    graph_data[name] = {
                        'type': node.node_type,
                        'file': node.file_path,
                        'line': node.line_number,
                        'dependencies': list(node.dependencies),
                        'dependents': list(node.dependents)
                    }
                
                with open(output_file, 'w') as f:
                    json.dump(graph_data, f, indent=2)
            
            logger.info(f"Exported call graph to: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export graph: {e}")
            return False
