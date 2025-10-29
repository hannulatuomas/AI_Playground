
"""
LLM Performance Benchmarks

Benchmarks for measuring LLM query performance.
"""

import time
import statistics
from typing import Dict, List, Any

from core.config import Config
from core.llm_router import LLMRouter


class LLMBenchmarks:
    """Benchmark suite for LLM performance."""
    
    def __init__(self, config: Config):
        """
        Initialize LLM benchmarks.
        
        Args:
            config: System configuration
        """
        self.config = config
        self.llm_router = LLMRouter(config)
        self.results: List[Dict[str, Any]] = []
    
    def benchmark_query(
        self,
        prompt: str,
        model: str,
        iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Benchmark LLM query performance.
        
        Args:
            prompt: Prompt to send
            model: Model to use
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        execution_times = []
        response_lengths = []
        
        for i in range(iterations):
            start_time = time.time()
            response = self.llm_router.query(prompt, model=model)
            end_time = time.time()
            
            execution_time = end_time - start_time
            execution_times.append(execution_time)
            response_lengths.append(len(response) if response else 0)
        
        return {
            "model": model,
            "prompt_length": len(prompt),
            "iterations": iterations,
            "times": execution_times,
            "avg_time": statistics.mean(execution_times),
            "min_time": min(execution_times),
            "max_time": max(execution_times),
            "std_dev": statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            "avg_response_length": statistics.mean(response_lengths),
            "tokens_per_second": statistics.mean(response_lengths) / statistics.mean(execution_times)
        }
    
    def run_all_benchmarks(self) -> List[Dict[str, Any]]:
        """
        Run all LLM benchmarks.
        
        Returns:
            List of benchmark results
        """
        print("Running LLM benchmarks...")
        
        # Get available models from config
        models = [
            "llama3.3:latest",
            "qwen2.5-coder:7b",
            "mistral:latest"
        ]
        
        prompts = [
            "Write a hello world function in Python",
            "Explain what a REST API is in one paragraph",
            "Create a simple sorting algorithm"
        ]
        
        results = []
        for model in models:
            if not self.llm_router.is_model_available(model):
                print(f"Skipping {model} (not available)")
                continue
            
            print(f"Benchmarking {model}...")
            for i, prompt in enumerate(prompts):
                result = self.benchmark_query(prompt, model, iterations=3)
                result["prompt_name"] = f"Prompt {i+1}"
                results.append(result)
                print(f"  {result['prompt_name']}: {result['avg_time']:.3f}s")
        
        self.results = results
        return results
    
    def generate_report(self) -> str:
        """
        Generate a markdown report of benchmark results.
        
        Returns:
            Markdown formatted report
        """
        report = "# LLM Query Benchmarks\n\n"
        report += f"**Total Tests:** {len(self.results)}\n\n"
        
        report += "## Results\n\n"
        report += "| Model | Prompt | Avg Time (s) | Min (s) | Max (s) | Tokens/s |\n"
        report += "|-------|--------|--------------|---------|---------|----------|\n"
        
        for result in self.results:
            report += f"| {result['model']} | {result['prompt_name']} | "
            report += f"{result['avg_time']:.3f} | {result['min_time']:.3f} | "
            report += f"{result['max_time']:.3f} | {result['tokens_per_second']:.1f} |\n"
        
        return report
