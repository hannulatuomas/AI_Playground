# Performance Benchmarks

**Version:** 2.4.1  
**Last Updated:** October 13, 2025

This document explains the performance benchmarking system for the AI Agent Console, including how to run benchmarks, interpret results, and optimize performance.

## Table of Contents

1. [Overview](#overview)
2. [Running Benchmarks](#running-benchmarks)
3. [Benchmark Types](#benchmark-types)
4. [Interpreting Results](#interpreting-results)
5. [Performance Optimization](#performance-optimization)
6. [Sample Results](#sample-results)
7. [Continuous Monitoring](#continuous-monitoring)

---

## Overview

The AI Agent Console includes a comprehensive benchmarking suite to measure and track performance across all system components:

- **Agent Execution** - Measure agent performance for various tasks
- **LLM Queries** - Benchmark LLM response times and throughput
- **Memory Operations** - Test memory storage and retrieval speed
- **Orchestration** - Measure task coordination overhead
- **End-to-End** - Full workflow performance

### Why Benchmark?

- **Identify Bottlenecks**: Find slow components
- **Track Performance**: Monitor performance over time
- **Optimize**: Make data-driven optimization decisions
- **Regression Testing**: Catch performance regressions
- **Capacity Planning**: Understand system limits

---

## Running Benchmarks

### Prerequisites

```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Verify Ollama is running with required models
ollama list
```

### Run All Benchmarks

```bash
# Run complete benchmark suite
python benchmarks/benchmark_runner.py

# Specify output file
python benchmarks/benchmark_runner.py --output my_report.md

# Use custom config
python benchmarks/benchmark_runner.py --config custom_config.yaml
```

### Run Specific Benchmarks

```python
from core.config import Config
from benchmarks.agent_benchmarks import AgentBenchmarks

# Initialize
config = Config()
agent_bench = AgentBenchmarks(config)

# Run benchmarks
results = agent_bench.run_all_benchmarks()

# Generate report
report = agent_bench.generate_report()
print(report)
```

### Benchmark Output

Benchmarks produce:
- **Console Output**: Real-time progress and results
- **Markdown Report**: Detailed report with tables and recommendations
- **Raw Data**: Python dictionaries with all measurements

---

## Benchmark Types

### 1. Agent Execution Benchmarks

**File:** `benchmarks/agent_benchmarks.py`

Tests agent execution performance across different agent types.

**Metrics:**
- Average execution time
- Minimum/maximum time
- Standard deviation
- Success rate

**Agents Tested:**
- Code Editors (Python, C#, C++, Web, Bash, PowerShell, Batch)
- Code Testers
- Code Planners
- Code Analyzers
- Build Agents
- Debug Agents

**Example:**

```python
from benchmarks.agent_benchmarks import AgentBenchmarks

bench = AgentBenchmarks(config)
result = bench.benchmark_agent(
    PythonCodeEditor,
    "Create a hello world function",
    {},
    iterations=5
)

print(f"Average time: {result['avg_time']:.3f}s")
```

### 2. LLM Query Benchmarks

**File:** `benchmarks/llm_benchmarks.py`

Measures LLM performance across different models and prompt types.

**Metrics:**
- Query response time
- Tokens per second
- Response length
- Model-specific performance

**Models Tested:**
- llama3.3:latest
- qwen2.5-coder:7b
- mistral:latest
- (User-configured models)

**Example:**

```python
from benchmarks.llm_benchmarks import LLMBenchmarks

bench = LLMBenchmarks(config)
result = bench.benchmark_query(
    "Write a Python function",
    "llama3.3:latest",
    iterations=5
)

print(f"Tokens/sec: {result['tokens_per_second']:.1f}")
```

### 3. Memory System Benchmarks

**File:** `benchmarks/memory_benchmarks.py`

Tests memory and vector database operations.

**Operations Tested:**
- Memory storage (add)
- Memory retrieval (search)
- Vector database storage
- Vector database search
- Embedding generation

**Metrics:**
- Storage time per operation
- Search time per query
- Embedding generation time
- Database overhead

**Example:**

```python
from benchmarks.memory_benchmarks import MemoryBenchmarks

bench = MemoryBenchmarks(config)
results = bench.run_all_benchmarks()

for result in results:
    print(f"{result['operation']}: {result['avg_time']:.4f}s")
```

### 4. Orchestration Benchmarks

**File:** `benchmarks/orchestration_benchmarks.py`

Measures task orchestration system performance.

**Operations Tested:**
- Task decomposition
- Agent selection
- Context management
- Full orchestration workflow

**Metrics:**
- Decomposition time
- Selection overhead
- Total orchestration time

**Example:**

```python
from benchmarks.orchestration_benchmarks import OrchestrationBenchmarks

bench = OrchestrationBenchmarks(config)
results = bench.run_all_benchmarks()

print(bench.generate_report())
```

---

## Interpreting Results

### Understanding Metrics

#### Average Time (avg_time)
- **What:** Mean execution time across all iterations
- **Good:** < 2s for most operations
- **Acceptable:** 2-5s for complex operations
- **Slow:** > 5s (investigate bottlenecks)

#### Standard Deviation (std_dev)
- **What:** Variation in execution times
- **Good:** < 10% of average time (consistent)
- **Acceptable:** 10-25% (moderate variation)
- **Bad:** > 25% (inconsistent, investigate)

#### Tokens Per Second (tokens/s)
- **What:** LLM throughput
- **Good:** > 50 tokens/s (fast model)
- **Acceptable:** 20-50 tokens/s (medium)
- **Slow:** < 20 tokens/s (consider faster model)

### Reading Benchmark Reports

```markdown
| Agent | Task | Avg Time (s) | Min (s) | Max (s) | Std Dev |
|-------|------|--------------|---------|---------|---------|
| PythonCodeEditor | Create function | 2.345 | 2.123 | 2.678 | 0.234 |
```

**Analysis:**
- Average time of 2.3s is acceptable for code generation
- Standard deviation of 0.23s (10% of avg) shows consistency
- Min-max range of 0.5s is reasonable

### Performance Targets

| Component | Target | Good | Acceptable | Slow |
|-----------|--------|------|------------|------|
| Agent Execution | < 2s | < 1s | 1-3s | > 3s |
| LLM Query | < 3s | < 2s | 2-5s | > 5s |
| Memory Store | < 0.1s | < 0.05s | 0.05-0.2s | > 0.2s |
| Memory Search | < 0.5s | < 0.2s | 0.2-1s | > 1s |
| Vector Store | < 0.2s | < 0.1s | 0.1-0.5s | > 0.5s |
| Vector Search | < 1s | < 0.5s | 0.5-2s | > 2s |
| Orchestration | < 5s | < 3s | 3-10s | > 10s |

---

## Performance Optimization

### Agent Optimization

#### 1. Use Appropriate Models
```yaml
# config.yaml
agents:
  model_assignments:
    # Use faster models for simple tasks
    simple_tasks:
      primary_model: "mistral:latest"  # Faster
    # Use powerful models for complex tasks
    complex_tasks:
      primary_model: "qwen2.5-coder:7b"  # More capable
```

#### 2. Enable Caching
```yaml
llm:
  caching:
    enabled: true
    ttl: 3600  # Cache for 1 hour
```

#### 3. Optimize Prompts
- Keep prompts concise
- Provide clear context
- Use structured formats
- Avoid redundant information

### LLM Optimization

#### 1. Model Selection
```python
# Fast models for simple tasks
simple_model = "mistral:latest"

# Powerful models for complex tasks
complex_model = "qwen2.5-coder:7b"

# Choose based on task complexity
model = complex_model if is_complex else simple_model
```

#### 2. Temperature Settings
```python
# Lower temperature for deterministic tasks (faster)
temperature = 0.2  # For code generation

# Higher temperature for creative tasks
temperature = 0.7  # For brainstorming
```

#### 3. Batch Queries
```python
# Batch multiple queries when possible
queries = ["task1", "task2", "task3"]
results = [llm_router.query(q, model) for q in queries]
```

### Memory Optimization

#### 1. Optimize Collection Size
```yaml
vector_db:
  chroma:
    # Limit collection size
    max_collection_size: 10000
```

#### 2. Prune Old Memories
```python
# Regularly prune old/irrelevant memories
memory_manager.prune_old_memories(days=30)
```

#### 3. Use Appropriate Search Limits
```python
# Don't retrieve more than needed
results = memory_manager.search_memory(query, limit=5)  # Not 100
```

### Orchestration Optimization

#### 1. Minimize Decomposition
```python
# Skip decomposition for simple tasks
if is_simple_task(task):
    return execute_directly(task)
```

#### 2. Cache Agent Capabilities
```python
# Cache agent selection results
@cache
def select_agent(task, context):
    # ... selection logic
```

#### 3. Parallel Execution
```python
# Execute independent subtasks in parallel
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor() as executor:
    results = executor.map(execute_subtask, subtasks)
```

---

## Sample Results

### Sample Benchmark Report

```markdown
# AI Agent Console - Performance Benchmarks

**Date:** 2025-10-12 15:30:00
**Version:** 2.4.1

## Agent Execution Benchmarks

| Agent | Task | Avg Time (s) | Min (s) | Max (s) | Std Dev |
|-------|------|--------------|---------|---------|---------|
| PythonCodeEditor | Create function | 2.123 | 1.987 | 2.456 | 0.189 |
| PythonCodePlanner | Plan REST API | 3.456 | 3.234 | 3.789 | 0.234 |
| PythonCodeAnalyzer | Analyze code | 1.876 | 1.654 | 2.123 | 0.198 |

## LLM Query Benchmarks

| Model | Prompt | Avg Time (s) | Tokens/s |
|-------|--------|--------------|----------|
| llama3.3:latest | Simple function | 2.345 | 42.3 |
| qwen2.5-coder:7b | Algorithm | 3.678 | 35.6 |
| mistral:latest | Explanation | 1.987 | 56.2 |

## Memory System Benchmarks

| Operation | Avg Time (s) | Min (s) | Max (s) |
|-----------|--------------|---------|---------|
| Memory Store | 0.0234 | 0.0198 | 0.0289 |
| Memory Search | 0.1234 | 0.1098 | 0.1456 |
| Vector Store | 0.0876 | 0.0765 | 0.1023 |
| Vector Search | 0.2345 | 0.2123 | 0.2678 |
```

### Performance Analysis

**Strong Areas:**
- Memory storage is very fast (< 0.03s)
- LLM throughput is good (35-56 tokens/s)
- Agent execution is consistent (low std dev)

**Areas for Improvement:**
- Vector search could be optimized (0.23s)
- Code planner is slower than other agents (3.46s)
- Consider using faster models for simple tasks

---

## Continuous Monitoring

### Regular Benchmarking

Run benchmarks regularly to track performance:

```bash
# Run weekly benchmarks
./scripts/weekly_benchmarks.sh

# Compare with previous results
python scripts/compare_benchmarks.py \
  --baseline last_week.md \
  --current this_week.md
```

### Automated Benchmarking

Add to CI/CD pipeline:

```yaml
# .github/workflows/benchmarks.yml
name: Performance Benchmarks

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run benchmarks
        run: python benchmarks/benchmark_runner.py
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-report
          path: benchmark_report.md
```

### Performance Monitoring Dashboard

Create a dashboard to track performance over time:

```python
# scripts/dashboard.py
import matplotlib.pyplot as plt

def plot_performance_trends(results):
    """Plot performance trends over time."""
    dates = [r['date'] for r in results]
    times = [r['avg_time'] for r in results]
    
    plt.plot(dates, times)
    plt.title('Agent Performance Over Time')
    plt.xlabel('Date')
    plt.ylabel('Average Time (s)')
    plt.savefig('performance_trend.png')
```

---

## Troubleshooting

### Slow Performance

**Issue:** Benchmarks show slow performance

**Solutions:**
1. Check system resources (CPU, memory)
2. Verify Ollama is running properly
3. Review model selection (use faster models)
4. Enable caching
5. Optimize prompts and context

### Inconsistent Results

**Issue:** High standard deviation in results

**Solutions:**
1. Increase number of iterations
2. Ensure system is not under load
3. Check for background processes
4. Verify network stability (for API calls)

### Benchmark Failures

**Issue:** Benchmarks fail or crash

**Solutions:**
1. Check logs for error messages
2. Verify configuration is correct
3. Ensure all dependencies are installed
4. Test components individually

---

## Best Practices

### When to Benchmark

- **Before major changes** - Establish baseline
- **After optimizations** - Verify improvements
- **Regular intervals** - Track trends (weekly/monthly)
- **Before releases** - Ensure no regressions

### What to Benchmark

- **Critical paths** - Most frequently used operations
- **Known bottlenecks** - Areas identified as slow
- **New features** - Verify performance of new code
- **All components** - Comprehensive system health

### How to Use Results

1. **Establish Baselines** - Record initial performance
2. **Set Targets** - Define acceptable performance levels
3. **Monitor Trends** - Track changes over time
4. **Identify Issues** - Detect regressions early
5. **Optimize** - Make data-driven improvements
6. **Verify** - Confirm optimizations work

---

## Resources

- [Benchmarks Guide](BENCHMARKS.md) (coming soon)
- [Architecture Documentation](../architecture/DESIGN_PRINCIPLES.md)
- [LLM Configuration](../reference/MODEL_ASSIGNMENTS.md)
- [Memory System](../architecture/MEMORY_SYSTEM.md)

---

## Contributing

Help improve benchmarks:

1. Add new benchmark types
2. Improve accuracy of measurements
3. Create visualization tools
4. Document performance insights
5. Share optimization techniques

---

**Happy benchmarking! 📊**
