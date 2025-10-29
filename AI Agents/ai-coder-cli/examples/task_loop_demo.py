#!/usr/bin/env python3
"""
Task Loop Processing Demo

Demonstrates the Task Loop Processing System for independent,
automated task management through the complete lifecycle.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.task_loop_processor import TaskLoopProcessor, TaskType, TaskStatus
from orchestration.workflows.task_loop_workflow import TaskLoopWorkflow
from core.llm_router import LLMRouter
from core.config import AppConfig


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_task_info(task):
    """Print task information."""
    print(f"Task ID: {task.task_id}")
    print(f"Title: {task.title}")
    print(f"Type: {task.task_type.value}")
    print(f"Priority: {task.priority}")
    print(f"Status: {task.status.value}")
    if task.dependencies:
        print(f"Dependencies: {', '.join(task.dependencies)}")
    if task.tags:
        print(f"Tags: {', '.join(task.tags)}")


def demo_task_creation():
    """Demonstrate task creation and structure."""
    print_section("Task Creation Demo")
    
    from orchestration.task_loop_processor import Task
    
    # Create different types of tasks
    tasks = [
        Task(
            task_id="feat_001",
            title="Add user authentication",
            description="Implement JWT-based user authentication",
            task_type=TaskType.FEATURE,
            priority=1,
            tags=["authentication", "security"]
        ),
        Task(
            task_id="bug_001",
            title="Fix memory leak",
            description="Fix memory leak in data processing module",
            task_type=TaskType.BUG,
            priority=2,
            tags=["performance", "critical"]
        ),
        Task(
            task_id="doc_001",
            title="Update API documentation",
            description="Update API docs for new authentication endpoints",
            task_type=TaskType.DOCUMENTATION,
            priority=3,
            tags=["documentation"],
            dependencies=["feat_001"]
        ),
        Task(
            task_id="test_001",
            title="Write unit tests",
            description="Write comprehensive unit tests for auth module",
            task_type=TaskType.TEST,
            priority=2,
            tags=["testing"],
            dependencies=["feat_001"]
        )
    ]
    
    print("Created 4 sample tasks:\n")
    
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task.title}")
        print(f"   Type: {task.task_type.value}, Priority: {task.priority}")
        print(f"   Status: {task.status.value}")
        if task.dependencies:
            print(f"   Dependencies: {', '.join(task.dependencies)}")
        print()


def demo_task_processor_basic():
    """Demonstrate basic task processor usage."""
    print_section("Task Processor Basic Usage")
    
    # Mock dependencies (for demo purposes)
    class MockLLMRouter:
        def query(self, prompt, **kwargs):
            return {
                'response': f"Mock response for: {prompt[:50]}...",
                'provider': 'mock'
            }
    
    class MockAgent:
        def execute(self, task, context):
            return {
                'success': True,
                'message': 'Task executed successfully',
                'data': {}
            }
    
    class MockAgentRegistry:
        def get_agent(self, name):
            return MockAgent()
    
    # Initialize processor
    processor = TaskLoopProcessor(
        llm_router=MockLLMRouter(),
        agent_registry=MockAgentRegistry()
    )
    
    print("Initialized TaskLoopProcessor")
    
    # Add tasks
    print("\nAdding tasks...")
    
    processor.add_task(
        task_id="task_001",
        title="Implement feature A",
        description="Add feature A to the system",
        task_type=TaskType.FEATURE,
        priority=1
    )
    
    processor.add_task(
        task_id="task_002",
        title="Test feature A",
        description="Write tests for feature A",
        task_type=TaskType.TEST,
        priority=2,
        dependencies=["task_001"]
    )
    
    processor.add_task(
        task_id="task_003",
        title="Document feature A",
        description="Create documentation for feature A",
        task_type=TaskType.DOCUMENTATION,
        priority=3,
        dependencies=["task_001"]
    )
    
    print(f"Added {len(processor.tasks)} tasks")
    
    # Show task queue
    print("\nTask Queue:")
    for task in processor.tasks:
        print(f"  - {task.task_id}: {task.title} (priority: {task.priority})")
    
    # Get next task
    print("\nGetting next task to process...")
    next_task = processor.get_next_task()
    
    if next_task:
        print(f"Next task: {next_task.task_id} - {next_task.title}")
        print(f"  Type: {next_task.task_type.value}")
        print(f"  Priority: {next_task.priority}")
    else:
        print("No tasks ready to process")
    
    # Show progress
    print("\nCurrent Progress:")
    progress = processor.get_progress()
    print(f"  Total tasks: {progress['total_tasks']}")
    print(f"  Pending: {progress['pending']}")
    print(f"  In progress: {progress['in_progress']}")
    print(f"  Completed: {progress['completed']}")
    print(f"  Failed: {progress['failed']}")


async def demo_task_lifecycle():
    """Demonstrate the complete task lifecycle."""
    print_section("Task Lifecycle Demo")
    
    print("Task processing goes through these stages:\n")
    
    stages = [
        ("1. PLANNING", "Analyze task and create detailed plan"),
        ("2. IMPLEMENTING", "Execute the plan and make code changes"),
        ("3. TESTING", "Run tests to verify implementation"),
        ("4. FIXING", "If tests fail, analyze and fix issues"),
        ("5. DOCUMENTING", "Generate documentation and commit messages"),
        ("6. VALIDATING", "Ensure task is fully complete")
    ]
    
    for stage, description in stages:
        print(f"{stage}")
        print(f"   {description}\n")
    
    print("Each stage produces results that are stored in the task object:")
    print("  - task.plan: The generated plan")
    print("  - task.implementation_result: Implementation output")
    print("  - task.test_results: Test execution results")
    print("  - task.fix_attempts: Number of fix attempts made")
    print("  - task.documentation: Generated documentation")
    print("  - task.validation_result: Final validation checks")


def demo_task_list_file():
    """Demonstrate loading tasks from a file."""
    print_section("Task List File Demo")
    
    # Create example task list
    tasks_data = {
        "tasks": [
            {
                "task_id": "feat_001",
                "title": "Add user registration",
                "description": "Implement user registration with email verification",
                "task_type": "feature",
                "priority": 1,
                "tags": ["authentication", "user-management"],
                "dependencies": []
            },
            {
                "task_id": "feat_002",
                "title": "Add user login",
                "description": "Implement user login with JWT tokens",
                "task_type": "feature",
                "priority": 1,
                "tags": ["authentication", "security"],
                "dependencies": ["feat_001"]
            },
            {
                "task_id": "bug_001",
                "title": "Fix email validation",
                "description": "Email validation is not working correctly",
                "task_type": "bug",
                "priority": 2,
                "tags": ["bug", "validation"],
                "dependencies": ["feat_001"]
            },
            {
                "task_id": "test_001",
                "title": "Write auth tests",
                "description": "Create comprehensive tests for authentication",
                "task_type": "test",
                "priority": 3,
                "tags": ["testing", "authentication"],
                "dependencies": ["feat_001", "feat_002"]
            },
            {
                "task_id": "doc_001",
                "title": "Document authentication flow",
                "description": "Create documentation for the authentication system",
                "task_type": "documentation",
                "priority": 4,
                "tags": ["documentation"],
                "dependencies": ["feat_001", "feat_002"]
            }
        ]
    }
    
    print("Example tasks.json file:\n")
    print(json.dumps(tasks_data, indent=2))
    
    # Save example file
    example_file = Path("example_tasks.json")
    with open(example_file, 'w') as f:
        json.dump(tasks_data, f, indent=2)
    
    print(f"\n✓ Saved example to {example_file}")
    print("\nTo use this file:")
    print("  workflow = TaskLoopWorkflow.from_task_list(")
    print("      tasks_file='example_tasks.json',")
    print("      llm_router=llm_router,")
    print("      agent_registry=agent_registry")
    print("  )")
    print("  results = await workflow.execute()")


async def demo_workflow_usage():
    """Demonstrate TaskLoopWorkflow usage."""
    print_section("TaskLoopWorkflow Demo")
    
    print("The TaskLoopWorkflow provides high-level task processing:\n")
    
    code_example = '''
import asyncio
from orchestration.workflows.task_loop_workflow import TaskLoopWorkflow
from core.llm_router import LLMRouter
from core.config import AppConfig
from agents.registry import AgentRegistry

async def main():
    # Initialize
    config = AppConfig.load()
    llm_router = LLMRouter(config)
    agent_registry = AgentRegistry(llm_router=llm_router, config=config)
    
    # Create workflow from task list
    workflow = TaskLoopWorkflow.from_task_list(
        tasks_file="tasks.json",
        llm_router=llm_router,
        agent_registry=agent_registry
    )
    
    # Execute workflow
    print("Starting task processing...")
    results = await workflow.execute()
    
    # Print results
    print(f"\\nProcessed: {results['tasks_processed']}")
    print(f"Completed: {results['tasks_completed']}")
    print(f"Failed: {results['tasks_failed']}")
    print(f"Duration: {results['duration_seconds']:.2f}s")
    
    # Check progress
    progress = workflow.get_progress()
    print(f"\\nFinal progress: {progress['progress_percent']:.1f}%")

asyncio.run(main())
'''
    
    print(code_example)


def demo_state_persistence():
    """Demonstrate state save/load."""
    print_section("State Persistence Demo")
    
    print("Tasks can be saved and resumed:\n")
    
    print("1. Save state during processing:")
    print("   processor.save_state(Path('task_state.json'))")
    print("   workflow.save_state(Path('workflow_state.json'))")
    
    print("\n2. Resume from saved state:")
    print("   processor = TaskLoopProcessor(llm_router, agent_registry)")
    print("   processor.load_state(Path('task_state.json'))")
    print("   results = await processor.process_all_tasks()")
    
    print("\n3. Saved state includes:")
    print("   - All pending tasks")
    print("   - Completed tasks")
    print("   - Failed tasks")
    print("   - Processing timestamps")
    print("   - Task progress and artifacts")


def demo_progress_monitoring():
    """Demonstrate progress monitoring."""
    print_section("Progress Monitoring Demo")
    
    monitoring_code = '''
import asyncio

async def monitor_progress(processor):
    """Real-time progress monitoring."""
    print("Monitoring task progress...")
    
    while not processor.processing_completed_at:
        progress = processor.get_progress()
        
        # Print progress bar
        percent = progress['progress_percent']
        bar_length = 40
        filled = int(bar_length * percent / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\\r[{bar}] {percent:.1f}% ", end="")
        
        # Show current task
        if progress['current_task']:
            current = progress['current_task']
            print(f"- {current['title'][:30]}...", end="")
        
        await asyncio.sleep(1)
    
    print("\\n✓ Processing completed!")

# Run monitoring alongside processing
monitor_task = asyncio.create_task(monitor_progress(processor))
results = await processor.process_all_tasks()
await monitor_task
'''
    
    print(monitoring_code)


def demo_use_cases():
    """Show common use cases."""
    print_section("Common Use Cases")
    
    use_cases = [
        {
            "title": "Sprint Planning",
            "description": "Process all tasks from a sprint backlog",
            "tasks": ["Features", "Bug fixes", "Documentation", "Tests"]
        },
        {
            "title": "Codebase Refactoring",
            "description": "Systematic refactoring of a codebase",
            "tasks": ["Extract modules", "Update tests", "Update docs", "Verify functionality"]
        },
        {
            "title": "Bug Fixing Session",
            "description": "Process a list of prioritized bugs",
            "tasks": ["Critical bugs", "High priority bugs", "Medium priority bugs"]
        },
        {
            "title": "Feature Development",
            "description": "Implement a feature with dependencies",
            "tasks": ["Database schema", "API endpoints", "Business logic", "UI components", "Tests", "Docs"]
        },
        {
            "title": "Technical Debt Cleanup",
            "description": "Address accumulated technical debt",
            "tasks": ["Code cleanup", "Update dependencies", "Remove deprecated code", "Add missing tests"]
        }
    ]
    
    for i, use_case in enumerate(use_cases, 1):
        print(f"{i}. {use_case['title']}")
        print(f"   {use_case['description']}")
        print(f"   Tasks: {', '.join(use_case['tasks'])}")
        print()


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("  TASK LOOP PROCESSING SYSTEM DEMONSTRATION")
    print("=" * 70)
    
    # Run demos
    demo_task_creation()
    demo_task_processor_basic()
    asyncio.run(demo_task_lifecycle())
    demo_task_list_file()
    asyncio.run(demo_workflow_usage())
    demo_state_persistence()
    demo_progress_monitoring()
    demo_use_cases()
    
    print("\n" + "=" * 70)
    print("  Demo completed!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Create your own tasks.json file")
    print("  2. Initialize the workflow with your agents")
    print("  3. Run: asyncio.run(workflow.execute())")
    print("  4. Monitor progress and review results")
    print("\n")


if __name__ == "__main__":
    main()
