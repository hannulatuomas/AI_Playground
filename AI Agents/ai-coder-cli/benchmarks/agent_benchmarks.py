
"""
Agent Execution Benchmarks

Benchmarks for measuring agent execution performance.
"""

import time
import statistics
from typing import Dict, List, Any
from pathlib import Path

from core.config import Config
from core.llm_router import LLMRouter
from tools.registry import ToolRegistry
from agents.languages.python import (
    PythonCodeEditor,
    PythonCodeTester,
    PythonCodePlanner,
    PythonCodeAnalyzer,
    PythonBuildAgent,
    PythonDebugAgent
)


class AgentBenchmarks:
    """Benchmark suite for agent execution performance."""
    
    def __init__(self, config: Config):
        """
        Initialize agent benchmarks.
        
        Args:
            config: System configuration
        """
        self.config = config
        self.llm_router = LLMRouter(config)
        self.tool_registry = ToolRegistry(config)
        self.results: List[Dict[str, Any]] = []
    
    def benchmark_agent(
        self,
        agent_class,
        task: str,
        context: Dict[str, Any],
        iterations: int = 3
    ) -> Dict[str, Any]:
        """
        Benchmark a single agent.
        
        Args:
            agent_class: Agent class to benchmark
            task: Task to execute
            context: Execution context
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        agent = agent_class(self.llm_router, self.tool_registry, self.config)
        execution_times = []
        
        for i in range(iterations):
            start_time = time.time()
            result = agent.execute(task, context)
            end_time = time.time()
            
            execution_time = end_time - start_time
            execution_times.append(execution_time)
        
        return {
            "agent": agent.name,
            "task": task,
            "iterations": iterations,
            "times": execution_times,
            "avg_time": statistics.mean(execution_times),
            "min_time": min(execution_times),
            "max_time": max(execution_times),
            "std_dev": statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        }
    
    def run_all_benchmarks(self) -> List[Dict[str, Any]]:
        """
        Run all agent benchmarks.
        
        Returns:
            List of benchmark results
        """
        print("Running agent benchmarks...")
        
        benchmarks = [
            {
                "agent_class": PythonCodeEditor,
                "task": "Create a simple hello world function",
                "context": {}
            },
            {
                "agent_class": PythonCodePlanner,
                "task": "Plan a REST API project",
                "context": {}
            },
            {
                "agent_class": PythonCodeAnalyzer,
                "task": "Analyze code quality",
                "context": {"code": "def hello(): pass"}
            },
            {
                "agent_class": PythonBuildAgent,
                "task": "Build Python package",
                "context": {"operation": "install_dependencies"}
            },
            {
                "agent_class": PythonDebugAgent,
                "task": "Debug exception",
                "context": {"exception_type": "ValueError"}
            }
        ]
        
        results = []
        for benchmark in benchmarks:
            print(f"Benchmarking {benchmark['agent_class'].__name__}...")
            result = self.benchmark_agent(
                benchmark["agent_class"],
                benchmark["task"],
                benchmark["context"],
                iterations=3
            )
            results.append(result)
            print(f"  Average time: {result['avg_time']:.3f}s")
        
        self.results = results
        return results
    
    def generate_report(self) -> str:
        """
        Generate a markdown report of benchmark results.
        
        Returns:
            Markdown formatted report
        """
        report = "# Agent Execution Benchmarks\n\n"
        report += f"**Total Agents Tested:** {len(self.results)}\n\n"
        
        report += "## Results\n\n"
        report += "| Agent | Task | Avg Time (s) | Min (s) | Max (s) | Std Dev |\n"
        report += "|-------|------|--------------|---------|---------|----------|\n"
        
        for result in self.results:
            report += f"| {result['agent']} | {result['task'][:30]}... | "
            report += f"{result['avg_time']:.3f} | {result['min_time']:.3f} | "
            report += f"{result['max_time']:.3f} | {result['std_dev']:.3f} |\n"
        
        return report
