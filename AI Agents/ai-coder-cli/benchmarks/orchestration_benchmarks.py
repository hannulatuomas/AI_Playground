
"""
Orchestration System Benchmarks

Benchmarks for task orchestration performance.
"""

import time
import statistics
from typing import Dict, List, Any

from core.config import Config
from orchestration.task_orchestrator import TaskOrchestrator


class OrchestrationBenchmarks:
    """Benchmark suite for orchestration system performance."""
    
    def __init__(self, config: Config):
        """
        Initialize orchestration benchmarks.
        
        Args:
            config: System configuration
        """
        self.config = config
        self.orchestrator = TaskOrchestrator(config)
        self.results: List[Dict[str, Any]] = []
    
    def benchmark_task_decomposition(self, iterations: int = 3) -> Dict[str, Any]:
        """
        Benchmark task decomposition.
        
        Args:
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        task = "Create a Python web application with database and authentication"
        execution_times = []
        
        for i in range(iterations):
            start_time = time.time()
            subtasks = self.orchestrator.decompose_task(task)
            end_time = time.time()
            
            execution_times.append(end_time - start_time)
        
        return {
            "operation": "Task Decomposition",
            "task": task[:50] + "...",
            "iterations": iterations,
            "avg_time": statistics.mean(execution_times),
            "min_time": min(execution_times),
            "max_time": max(execution_times)
        }
    
    def benchmark_agent_selection(self, iterations: int = 5) -> Dict[str, Any]:
        """
        Benchmark agent selection.
        
        Args:
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        tasks = [
            "Write Python code",
            "Debug C# application",
            "Build C++ project",
            "Create web component",
            "Write bash script"
        ]
        
        execution_times = []
        
        for i in range(iterations):
            task = tasks[i % len(tasks)]
            
            start_time = time.time()
            agent = self.orchestrator.select_agent(task, {})
            end_time = time.time()
            
            execution_times.append(end_time - start_time)
        
        return {
            "operation": "Agent Selection",
            "iterations": iterations,
            "avg_time": statistics.mean(execution_times),
            "min_time": min(execution_times),
            "max_time": max(execution_times)
        }
    
    def benchmark_full_orchestration(self, iterations: int = 2) -> Dict[str, Any]:
        """
        Benchmark full orchestration workflow.
        
        Args:
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        task = "Create a simple Python function that adds two numbers"
        execution_times = []
        
        for i in range(iterations):
            start_time = time.time()
            result = self.orchestrator.execute(task, {})
            end_time = time.time()
            
            execution_times.append(end_time - start_time)
        
        return {
            "operation": "Full Orchestration",
            "task": task,
            "iterations": iterations,
            "avg_time": statistics.mean(execution_times),
            "min_time": min(execution_times),
            "max_time": max(execution_times)
        }
    
    def run_all_benchmarks(self) -> List[Dict[str, Any]]:
        """
        Run all orchestration benchmarks.
        
        Returns:
            List of benchmark results
        """
        print("Running orchestration system benchmarks...")
        
        results = []
        
        print("Benchmarking task decomposition...")
        results.append(self.benchmark_task_decomposition())
        
        print("Benchmarking agent selection...")
        results.append(self.benchmark_agent_selection())
        
        print("Benchmarking full orchestration...")
        results.append(self.benchmark_full_orchestration())
        
        self.results = results
        return results
    
    def generate_report(self) -> str:
        """
        Generate a markdown report of benchmark results.
        
        Returns:
            Markdown formatted report
        """
        report = "# Orchestration System Benchmarks\n\n"
        report += f"**Total Operations Tested:** {len(self.results)}\n\n"
        
        report += "## Results\n\n"
        report += "| Operation | Avg Time (s) | Min (s) | Max (s) |\n"
        report += "|-----------|--------------|---------|----------|\n"
        
        for result in self.results:
            report += f"| {result['operation']} | "
            report += f"{result['avg_time']:.3f} | {result['min_time']:.3f} | "
            report += f"{result['max_time']:.3f} |\n"
        
        return report
