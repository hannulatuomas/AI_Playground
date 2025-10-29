# Task Loop Processing System

This document provides comprehensive information about the Task Loop Processing System for independent, automated task management.

## Overview

The Task Loop Processing System enables Workflows and Agents to independently process lists of tasks through a sophisticated lifecycle:

1. **Plan**: Analyze the task and create a detailed plan
2. **Implement**: Execute the plan and make necessary code changes
3. **Test**: Run relevant tests to verify the implementation
4. **Fix**: If tests fail, analyze failures and fix issues (with retry logic)
5. **Document**: Update documentation and create commit messages
6. **Validate**: Ensure the task is fully complete before moving on

## Features

- **Multiple Task Types**: Features, bugs, errors, issues, questions, refactoring, documentation, tests
- **Priority-based Processing**: Tasks are processed in priority order
- **Dependency Management**: Tasks can depend on other tasks
- **Automatic Retry**: Failed tests trigger automatic fix attempts
- **State Persistence**: Save and resume task processing
- **Progress Tracking**: Real-time progress monitoring
- **Comprehensive Logging**: Detailed logs for each stage

## Installation

No additional installation required - the task loop processor is built into the orchestration system.

## Quick Start

### Create a Task List

Create a JSON file with your tasks (`tasks.json`):

```json
{
  "tasks": [
    {
      "task_id": "feat_001",
      "title": "Add user authentication",
      "description": "Implement user authentication with JWT tokens",
      "task_type": "feature",
      "priority": 1,
      "tags": ["authentication", "security"],
      "dependencies": []
    },
    {
      "task_id": "bug_001",
      "title": "Fix login redirect",
      "description": "Users are not redirected after successful login",
      "task_type": "bug",
      "priority": 2,
      "tags": ["bug", "ui"],
      "dependencies": ["feat_001"]
    },
    {
      "task_id": "doc_001",
      "title": "Document authentication API",
      "description": "Create API documentation for authentication endpoints",
      "task_type": "documentation",
      "priority": 3,
      "tags": ["documentation"],
      "dependencies": ["feat_001"]
    }
  ]
}
```

### Using the Task Loop Workflow

```python
import asyncio
from orchestration.workflows.task_loop_workflow import TaskLoopWorkflow
from core.llm_router import LLMRouter
from core.config import AppConfig
from agents.registry import AgentRegistry

async def main():
    # Initialize dependencies
    config = AppConfig.load()
    llm_router = LLMRouter(config)
    agent_registry = AgentRegistry(llm_router=llm_router, config=config)
    
    # Load tasks from file
    workflow = TaskLoopWorkflow.from_task_list(
        tasks_file="tasks.json",
        llm_router=llm_router,
        agent_registry=agent_registry
    )
    
    # Execute workflow
    results = await workflow.execute()
    
    # Print results
    print(f"Processed: {results['tasks_processed']}")
    print(f"Completed: {results['tasks_completed']}")
    print(f"Failed: {results['tasks_failed']}")
    print(f"Duration: {results['duration_seconds']:.2f}s")

# Run
asyncio.run(main())
```

### Using the Task Loop Processor Directly

```python
from orchestration.task_loop_processor import TaskLoopProcessor, TaskType

# Initialize processor
processor = TaskLoopProcessor(
    llm_router=llm_router,
    agent_registry=agent_registry,
    max_retries=3,
    timeout=3600
)

# Add tasks programmatically
processor.add_task(
    task_id="task_001",
    title="Implement feature X",
    description="Detailed description of feature X",
    task_type=TaskType.FEATURE,
    priority=1,
    tags=["feature", "backend"],
    dependencies=[]
)

processor.add_task(
    task_id="task_002",
    title="Test feature X",
    description="Write tests for feature X",
    task_type=TaskType.TEST,
    priority=2,
    tags=["testing"],
    dependencies=["task_001"]
)

# Process all tasks
results = await processor.process_all_tasks()
```

## Task Types

The system supports various task types, each mapped to appropriate agents:

| Task Type | Description | Default Agent |
|-----------|-------------|---------------|
| `feature` | New feature implementation | `code_editor` |
| `bug` | Bug fix | `debug_agent` |
| `error` | Error resolution | `debug_agent` |
| `issue` | General issue | `debug_agent` |
| `question` | Question/inquiry | (Handled specially) |
| `refactor` | Code refactoring | `code_editor` |
| `documentation` | Documentation | `documentation_agent` |
| `test` | Test creation | `code_tester` |
| `other` | Miscellaneous | `code_editor` |

## Task Structure

### Required Fields

```python
{
    "task_id": str,        # Unique identifier
    "title": str,          # Short title
    "description": str,    # Detailed description
    "task_type": str,      # Type from TaskType enum
}
```

### Optional Fields

```python
{
    "priority": int,           # 1-10, where 1 is highest (default: 5)
    "tags": [str],            # Categorization tags
    "dependencies": [str],    # Task IDs that must complete first
    "max_fix_attempts": int   # Maximum fix attempts if tests fail (default: 3)
}
```

## Processing Lifecycle

### 1. Planning Stage

The system uses the LLM to create a detailed plan:

```python
# Generated plan includes:
- Step-by-step approach
- Required resources/tools
- Potential challenges
- Success criteria
```

### 2. Implementation Stage

The appropriate agent executes the task:

```python
# Agent selection based on task type
- Features → code_editor
- Bugs → debug_agent
- Tests → code_tester
- Docs → documentation_agent
```

### 3. Testing Stage

Tests are run to verify the implementation:

```python
# If code_tester agent available:
- Runs relevant tests
- Captures test results
- Identifies failures

# If no test agent:
- Skips testing stage
- Proceeds to documentation
```

### 4. Fixing Stage (if needed)

If tests fail, automatic fix attempts are made:

```python
# Fix loop (up to max_fix_attempts):
1. Analyze test failures
2. Use debug_agent to fix issues
3. Re-run tests
4. Repeat until tests pass or max attempts reached
```

### 5. Documentation Stage

Documentation is generated:

```python
# LLM generates:
- Summary of changes
- Usage examples
- Implementation notes
- Git commit message
```

### 6. Validation Stage

Final validation ensures completeness:

```python
# Checks:
- Plan created: ✓
- Implementation completed: ✓
- Tests passed: ✓
- Documentation generated: ✓
```

## Priority and Dependencies

### Priority Processing

Tasks are processed in priority order (lower number = higher priority):

```json
{
  "tasks": [
    {
      "task_id": "critical",
      "title": "Critical security fix",
      "priority": 1
    },
    {
      "task_id": "important",
      "title": "Important feature",
      "priority": 2
    },
    {
      "task_id": "normal",
      "title": "Normal task",
      "priority": 5
    },
    {
      "task_id": "low",
      "title": "Low priority cleanup",
      "priority": 10
    }
  ]
}
```

### Dependency Management

Tasks with dependencies wait for prerequisite tasks to complete:

```json
{
  "tasks": [
    {
      "task_id": "database",
      "title": "Setup database schema",
      "priority": 1,
      "dependencies": []
    },
    {
      "task_id": "api",
      "title": "Create API endpoints",
      "priority": 1,
      "dependencies": ["database"]
    },
    {
      "task_id": "frontend",
      "title": "Build UI components",
      "priority": 1,
      "dependencies": ["api"]
    }
  ]
}
```

## State Management

### Save State

```python
from pathlib import Path

# Save processor state
processor.save_state(Path("task_state.json"))

# Save workflow state
workflow.save_state(Path("workflow_state.json"))
```

### Load State

```python
# Create processor
processor = TaskLoopProcessor(llm_router, agent_registry)

# Load saved state
processor.load_state(Path("task_state.json"))

# Resume processing
results = await processor.process_all_tasks()
```

### Saved State Structure

```json
{
  "tasks": [...],
  "completed_tasks": [...],
  "failed_tasks": [...],
  "processing_started_at": "2024-01-15T10:30:00",
  "processing_completed_at": null
}
```

## Progress Monitoring

### Get Progress

```python
# Get current progress
progress = processor.get_progress()

print(f"Total tasks: {progress['total_tasks']}")
print(f"Pending: {progress['pending']}")
print(f"In progress: {progress['in_progress']}")
print(f"Completed: {progress['completed']}")
print(f"Failed: {progress['failed']}")
print(f"Progress: {progress['progress_percent']:.1f}%")

# Current task info
if progress['current_task']:
    current = progress['current_task']
    print(f"Current: {current['title']} ({current['status']})")
```

### Real-time Monitoring

```python
import asyncio

async def monitor_progress(processor):
    """Monitor processing progress."""
    while not processor.processing_completed_at:
        progress = processor.get_progress()
        print(f"\rProgress: {progress['progress_percent']:.1f}%", end="")
        await asyncio.sleep(1)
    print("\nCompleted!")

# Run monitoring in background
monitor_task = asyncio.create_task(monitor_progress(processor))
results = await processor.process_all_tasks()
await monitor_task
```

## Configuration

### Processor Configuration

```python
processor = TaskLoopProcessor(
    llm_router=llm_router,
    agent_registry=agent_registry,
    config={
        'enable_testing': True,
        'enable_documentation': True,
        'auto_fix': True
    },
    max_retries=3,      # Retry failed tasks
    timeout=3600        # Timeout in seconds
)
```

### Task Configuration

```python
task = processor.add_task(
    task_id="task_001",
    title="Example Task",
    description="...",
    task_type=TaskType.FEATURE,
    priority=5,
    tags=["backend", "api"],
    dependencies=[]
)

# Override default fix attempts for this task
task.max_fix_attempts = 5
```

## Error Handling

### Task Failures

```python
results = await processor.process_all_tasks()

# Check for failures
if results['tasks_failed'] > 0:
    print("Some tasks failed:")
    
    for task in processor.failed_tasks:
        print(f"- {task.task_id}: {task.error_message}")
        
        # Analyze failure
        if task.fix_attempts >= task.max_fix_attempts:
            print(f"  Failed after {task.fix_attempts} fix attempts")
        
        # View test results
        if task.test_results:
            print(f"  Test failures: {task.test_results.get('failures', [])}")
```

### Skipped Tasks

```python
# Tasks can be skipped due to:
# - Unmet dependencies
# - Condition failures
# - Manual skip

for result in results['task_results']:
    if result['status'] == 'skipped':
        print(f"Skipped: {result['task_id']}")
```

## Advanced Features

### Custom Agent Mapping

```python
# Override default agent for specific task types
processor._get_agent_for_task = lambda task: {
    TaskType.FEATURE: 'custom_feature_agent',
    TaskType.BUG: 'custom_debug_agent',
}.get(task.task_type, 'code_editor')
```

### Task Filtering

```python
# Process only specific task types
for task in processor.tasks:
    if task.task_type == TaskType.BUG:
        await processor.process_task(task)
```

### Artifact Collection

```python
# Tasks can store artifacts
task.artifacts['git_commit'] = "abc123"
task.artifacts['test_coverage'] = 85.5
task.artifacts['files_modified'] = ["api.py", "tests.py"]

# Access artifacts after processing
for task in processor.completed_tasks:
    if 'git_commit' in task.artifacts:
        print(f"{task.title}: {task.artifacts['git_commit']}")
```

## Best Practices

1. **Break Down Large Tasks**: Create multiple smaller tasks instead of one large task
2. **Use Dependencies**: Structure tasks with clear dependencies for proper ordering
3. **Set Appropriate Priorities**: Use priority to ensure critical tasks run first
4. **Tag Effectively**: Use tags for filtering and organization
5. **Save State Regularly**: Persist state for long-running processes
6. **Monitor Progress**: Watch for stuck or failing tasks
7. **Review Failed Tasks**: Analyze failures to improve task definitions
8. **Test Incrementally**: Don't queue too many untested tasks at once

## Examples

### Example 1: Feature Development

```json
{
  "tasks": [
    {
      "task_id": "design_001",
      "title": "Design API schema",
      "description": "Design the REST API schema for user management",
      "task_type": "feature",
      "priority": 1
    },
    {
      "task_id": "impl_001",
      "title": "Implement API endpoints",
      "description": "Implement user CRUD endpoints",
      "task_type": "feature",
      "priority": 2,
      "dependencies": ["design_001"]
    },
    {
      "task_id": "test_001",
      "title": "Write API tests",
      "description": "Create unit and integration tests",
      "task_type": "test",
      "priority": 3,
      "dependencies": ["impl_001"]
    },
    {
      "task_id": "doc_001",
      "title": "Document API",
      "description": "Create API documentation",
      "task_type": "documentation",
      "priority": 4,
      "dependencies": ["impl_001"]
    }
  ]
}
```

### Example 2: Bug Fixing

```json
{
  "tasks": [
    {
      "task_id": "bug_001",
      "title": "Fix memory leak",
      "description": "Fix memory leak in data processing module",
      "task_type": "bug",
      "priority": 1,
      "tags": ["critical", "performance"]
    },
    {
      "task_id": "bug_002",
      "title": "Fix UI alignment",
      "description": "Fix alignment issues on mobile",
      "task_type": "bug",
      "priority": 5,
      "tags": ["ui", "mobile"]
    }
  ]
}
```

### Example 3: Refactoring

```json
{
  "tasks": [
    {
      "task_id": "refactor_001",
      "title": "Extract authentication logic",
      "description": "Extract auth logic into separate module",
      "task_type": "refactor",
      "priority": 3
    },
    {
      "task_id": "refactor_002",
      "title": "Update auth tests",
      "description": "Update tests for refactored auth module",
      "task_type": "test",
      "priority": 3,
      "dependencies": ["refactor_001"]
    }
  ]
}
```

## Troubleshooting

### Tasks Not Processing

**Problem**: Tasks remain pending

**Solutions**:
1. Check for unmet dependencies
2. Verify agent registry has required agents
3. Check task priorities
4. Review logs for errors

### Tests Keep Failing

**Problem**: Tasks fail at testing stage repeatedly

**Solutions**:
1. Increase `max_fix_attempts`
2. Review test failures in task results
3. Manually investigate the first failure
4. Improve task description for better implementation

### Slow Processing

**Problem**: Task processing is very slow

**Solutions**:
1. Use faster LLM models
2. Reduce context sizes
3. Process fewer tasks concurrently
4. Optimize agent implementations

## Resources

- [Task Loop Processing](TASK_LOOP_PROCESSING.md)
- [Agent Development Guide](./reference/AGENT_CATALOG.md)
- [LLM Router Documentation](./architecture/AI_CONTEXT.md)

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Review task results for failure reasons
3. Verify agent availability
4. Test with simpler tasks first
