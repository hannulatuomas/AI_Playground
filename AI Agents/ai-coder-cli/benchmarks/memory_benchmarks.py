
"""
Memory System Benchmarks

Benchmarks for memory and vector database operations.
"""

import time
import statistics
from typing import Dict, List, Any

from core.config import Config
from core.memory.memory_manager import MemoryManager
from core.memory.vector_memory import VectorMemoryManager


class MemoryBenchmarks:
    """Benchmark suite for memory system performance."""
    
    def __init__(self, config: Config):
        """
        Initialize memory benchmarks.
        
        Args:
            config: System configuration
        """
        self.config = config
        self.memory_manager = MemoryManager(config)
        self.vector_memory = VectorMemoryManager(config)
        self.results: List[Dict[str, Any]] = []
    
    def benchmark_memory_store(self, iterations: int = 10) -> Dict[str, Any]:
        """
        Benchmark memory storage operations.
        
        Args:
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        execution_times = []
        
        for i in range(iterations):
            content = f"Test memory content {i}"
            
            start_time = time.time()
            self.memory_manager.add_memory("test", content, {"index": i})
            end_time = time.time()
            
            execution_times.append(end_time - start_time)
        
        return {
            "operation": "Memory Store",
            "iterations": iterations,
            "avg_time": statistics.mean(execution_times),
            "min_time": min(execution_times),
            "max_time": max(execution_times)
        }
    
    def benchmark_memory_search(self, iterations: int = 10) -> Dict[str, Any]:
        """
        Benchmark memory search operations.
        
        Args:
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        # Add some test data
        for i in range(20):
            self.memory_manager.add_memory("test", f"Test content {i}", {"index": i})
        
        execution_times = []
        
        for i in range(iterations):
            start_time = time.time()
            results = self.memory_manager.search_memory("test content", limit=5)
            end_time = time.time()
            
            execution_times.append(end_time - start_time)
        
        return {
            "operation": "Memory Search",
            "iterations": iterations,
            "avg_time": statistics.mean(execution_times),
            "min_time": min(execution_times),
            "max_time": max(execution_times)
        }
    
    def benchmark_vector_store(self, iterations: int = 10) -> Dict[str, Any]:
        """
        Benchmark vector database storage.
        
        Args:
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        execution_times = []
        
        for i in range(iterations):
            content = f"Test vector content {i}"
            
            start_time = time.time()
            self.vector_memory.add_memory("test_collection", content, {"index": i})
            end_time = time.time()
            
            execution_times.append(end_time - start_time)
        
        return {
            "operation": "Vector Store",
            "iterations": iterations,
            "avg_time": statistics.mean(execution_times),
            "min_time": min(execution_times),
            "max_time": max(execution_times)
        }
    
    def benchmark_vector_search(self, iterations: int = 10) -> Dict[str, Any]:
        """
        Benchmark vector database search.
        
        Args:
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        # Add some test data
        for i in range(20):
            self.vector_memory.add_memory("test_collection", f"Vector content {i}", {"index": i})
        
        execution_times = []
        
        for i in range(iterations):
            start_time = time.time()
            results = self.vector_memory.search("vector content", n_results=5)
            end_time = time.time()
            
            execution_times.append(end_time - start_time)
        
        return {
            "operation": "Vector Search",
            "iterations": iterations,
            "avg_time": statistics.mean(execution_times),
            "min_time": min(execution_times),
            "max_time": max(execution_times)
        }
    
    def run_all_benchmarks(self) -> List[Dict[str, Any]]:
        """
        Run all memory benchmarks.
        
        Returns:
            List of benchmark results
        """
        print("Running memory system benchmarks...")
        
        results = []
        
        print("Benchmarking memory store...")
        results.append(self.benchmark_memory_store())
        
        print("Benchmarking memory search...")
        results.append(self.benchmark_memory_search())
        
        print("Benchmarking vector store...")
        results.append(self.benchmark_vector_store())
        
        print("Benchmarking vector search...")
        results.append(self.benchmark_vector_search())
        
        self.results = results
        return results
    
    def generate_report(self) -> str:
        """
        Generate a markdown report of benchmark results.
        
        Returns:
            Markdown formatted report
        """
        report = "# Memory System Benchmarks\n\n"
        report += f"**Total Operations Tested:** {len(self.results)}\n\n"
        
        report += "## Results\n\n"
        report += "| Operation | Avg Time (s) | Min (s) | Max (s) |\n"
        report += "|-----------|--------------|---------|----------|\n"
        
        for result in self.results:
            report += f"| {result['operation']} | "
            report += f"{result['avg_time']:.4f} | {result['min_time']:.4f} | "
            report += f"{result['max_time']:.4f} |\n"
        
        return report
