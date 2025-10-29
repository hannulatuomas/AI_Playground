"""
Task Loop Processing System

Provides independent task processing capabilities for Workflows and Agents.
Implements a sophisticated plan-implement-test-fix-document-validate cycle.
"""

import logging
from typing import Dict, Any, List, Optional, Literal
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
import json
from pathlib import Path


logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks supported by the task loop processor."""
    FEATURE = "feature"
    BUG = "bug"
    ERROR = "error"
    ISSUE = "issue"
    QUESTION = "question"
    REFACTOR = "refactor"
    DOCUMENTATION = "documentation"
    TEST = "test"
    OTHER = "other"


class TaskStatus(Enum):
    """Status of a task in the processing loop."""
    PENDING = "pending"
    PLANNING = "planning"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    FIXING = "fixing"
    DOCUMENTING = "documenting"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """
    Represents a single task in the task loop.
    
    Supports different task types with comprehensive state tracking.
    """
    
    task_id: str
    title: str
    description: str
    task_type: TaskType
    priority: int = 5  # 1-10, where 1 is highest priority
    status: TaskStatus = TaskStatus.PENDING
    
    # Lifecycle timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Processing state
    plan: Optional[str] = None
    implementation_result: Optional[Dict[str, Any]] = None
    test_results: Optional[Dict[str, Any]] = None
    fix_attempts: int = 0
    max_fix_attempts: int = 3
    documentation: Optional[str] = None
    validation_result: Optional[Dict[str, Any]] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    
    # Results and artifacts
    artifacts: Dict[str, Any] = field(default_factory=dict)
    
    def mark_started(self):
        """Mark task as started."""
        self.started_at = datetime.now()
    
    def mark_completed(self):
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def mark_failed(self, error: str):
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.error_message = error
        self.completed_at = datetime.now()
    
    def mark_skipped(self, reason: str):
        """Mark task as skipped."""
        self.status = TaskStatus.SKIPPED
        self.error_message = reason
        self.completed_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'task_type': self.task_type.value,
            'priority': self.priority,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'plan': self.plan,
            'implementation_result': self.implementation_result,
            'test_results': self.test_results,
            'fix_attempts': self.fix_attempts,
            'max_fix_attempts': self.max_fix_attempts,
            'documentation': self.documentation,
            'validation_result': self.validation_result,
            'tags': self.tags,
            'dependencies': self.dependencies,
            'error_message': self.error_message,
            'artifacts': self.artifacts
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        task = cls(
            task_id=data['task_id'],
            title=data['title'],
            description=data['description'],
            task_type=TaskType(data['task_type']),
            priority=data.get('priority', 5),
            status=TaskStatus(data.get('status', 'pending'))
        )
        
        # Restore timestamps
        if data.get('created_at'):
            task.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('started_at'):
            task.started_at = datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            task.completed_at = datetime.fromisoformat(data['completed_at'])
        
        # Restore state
        task.plan = data.get('plan')
        task.implementation_result = data.get('implementation_result')
        task.test_results = data.get('test_results')
        task.fix_attempts = data.get('fix_attempts', 0)
        task.max_fix_attempts = data.get('max_fix_attempts', 3)
        task.documentation = data.get('documentation')
        task.validation_result = data.get('validation_result')
        task.tags = data.get('tags', [])
        task.dependencies = data.get('dependencies', [])
        task.error_message = data.get('error_message')
        task.artifacts = data.get('artifacts', {})
        
        return task


class TaskLoopProcessor:
    """
    Processes tasks through a sophisticated plan-implement-test-fix-document-validate cycle.
    
    Can be used by Workflows and Agents for independent task processing.
    """
    
    def __init__(
        self,
        llm_router: Any,
        agent_registry: Any,
        config: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        timeout: int = 3600
    ):
        """
        Initialize the task loop processor.
        
        Args:
            llm_router: LLM router for AI-powered decision making
            agent_registry: Agent registry for task execution
            config: Optional configuration dictionary
            max_retries: Maximum retry attempts for failed tasks
            timeout: Timeout for task processing in seconds
        """
        self.llm_router = llm_router
        self.agent_registry = agent_registry
        self.config = config or {}
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Task storage
        self.tasks: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []
        
        # State tracking
        self.current_task: Optional[Task] = None
        self.processing_started_at: Optional[datetime] = None
        self.processing_completed_at: Optional[datetime] = None
        
        logger.info("TaskLoopProcessor initialized")
    
    def add_task(
        self,
        task_id: str,
        title: str,
        description: str,
        task_type: TaskType = TaskType.OTHER,
        priority: int = 5,
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None
    ) -> Task:
        """
        Add a task to the processing queue.
        
        Args:
            task_id: Unique task identifier
            title: Task title
            description: Detailed task description
            task_type: Type of task
            priority: Task priority (1-10, 1 is highest)
            tags: Optional tags for categorization
            dependencies: Optional list of task IDs that must complete first
            
        Returns:
            Created Task object
        """
        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            tags=tags or [],
            dependencies=dependencies or []
        )
        
        self.tasks.append(task)
        logger.info(f"Added task: {task_id} - {title} (type: {task_type.value}, priority: {priority})")
        
        return task
    
    def add_tasks_from_list(self, tasks_data: List[Dict[str, Any]]) -> List[Task]:
        """
        Add multiple tasks from a list of dictionaries.
        
        Args:
            tasks_data: List of task dictionaries
            
        Returns:
            List of created Task objects
        """
        created_tasks = []
        
        for task_data in tasks_data:
            task = self.add_task(
                task_id=task_data['task_id'],
                title=task_data['title'],
                description=task_data['description'],
                task_type=TaskType(task_data.get('task_type', 'other')),
                priority=task_data.get('priority', 5),
                tags=task_data.get('tags', []),
                dependencies=task_data.get('dependencies', [])
            )
            created_tasks.append(task)
        
        logger.info(f"Added {len(created_tasks)} tasks to the queue")
        return created_tasks
    
    def get_next_task(self) -> Optional[Task]:
        """
        Get the next task to process based on priority and dependencies.
        
        Returns:
            Next task to process or None if no tasks are ready
        """
        # Filter pending tasks
        pending_tasks = [t for t in self.tasks if t.status == TaskStatus.PENDING]
        
        if not pending_tasks:
            return None
        
        # Filter by dependencies
        ready_tasks = []
        for task in pending_tasks:
            dependencies_met = True
            
            for dep_id in task.dependencies:
                dep_task = self.get_task(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    dependencies_met = False
                    break
            
            if dependencies_met:
                ready_tasks.append(task)
        
        if not ready_tasks:
            return None
        
        # Sort by priority (lower number = higher priority)
        ready_tasks.sort(key=lambda t: t.priority)
        
        return ready_tasks[0]
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        for task in self.tasks + self.completed_tasks + self.failed_tasks:
            if task.task_id == task_id:
                return task
        return None
    
    async def process_all_tasks(self) -> Dict[str, Any]:
        """
        Process all tasks in the queue.
        
        Returns:
            Processing results summary
        """
        self.processing_started_at = datetime.now()
        logger.info(f"Starting task loop processing with {len(self.tasks)} tasks")
        
        results = {
            'started_at': self.processing_started_at.isoformat(),
            'tasks_processed': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'tasks_skipped': 0,
            'task_results': []
        }
        
        try:
            while True:
                # Get next task
                task = self.get_next_task()
                
                if not task:
                    # No more tasks ready
                    remaining_pending = len([t for t in self.tasks if t.status == TaskStatus.PENDING])
                    
                    if remaining_pending > 0:
                        logger.warning(
                            f"{remaining_pending} tasks remain pending but have unmet dependencies or are blocked"
                        )
                    
                    break
                
                # Process the task
                logger.info(f"Processing task: {task.task_id} - {task.title}")
                task_result = await self.process_task(task)
                
                results['tasks_processed'] += 1
                results['task_results'].append(task_result)
                
                if task.status == TaskStatus.COMPLETED:
                    results['tasks_completed'] += 1
                    self.completed_tasks.append(task)
                    self.tasks.remove(task)
                elif task.status == TaskStatus.FAILED:
                    results['tasks_failed'] += 1
                    self.failed_tasks.append(task)
                    self.tasks.remove(task)
                elif task.status == TaskStatus.SKIPPED:
                    results['tasks_skipped'] += 1
                    self.completed_tasks.append(task)  # Treat skipped as "done"
                    self.tasks.remove(task)
        
        except Exception as e:
            logger.error(f"Fatal error in task loop processing: {e}", exc_info=True)
            results['error'] = str(e)
        
        finally:
            self.processing_completed_at = datetime.now()
            results['completed_at'] = self.processing_completed_at.isoformat()
            
            duration = (self.processing_completed_at - self.processing_started_at).total_seconds()
            results['duration_seconds'] = duration
            
            logger.info(
                f"Task loop processing completed. "
                f"Processed: {results['tasks_processed']}, "
                f"Completed: {results['tasks_completed']}, "
                f"Failed: {results['tasks_failed']}, "
                f"Duration: {duration:.2f}s"
            )
        
        return results
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """
        Process a single task through the complete cycle.
        
        Args:
            task: Task to process
            
        Returns:
            Task processing result
        """
        self.current_task = task
        task.mark_started()
        
        result = {
            'task_id': task.task_id,
            'title': task.title,
            'status': task.status.value,
            'stages': {}
        }
        
        try:
            # Stage 1: Plan
            logger.info(f"[{task.task_id}] Stage 1: Planning")
            task.status = TaskStatus.PLANNING
            plan_result = await self._plan_task(task)
            result['stages']['planning'] = plan_result
            
            if not plan_result['success']:
                task.mark_failed(f"Planning failed: {plan_result.get('error')}")
                result['status'] = task.status.value
                return result
            
            # Stage 2: Implement
            logger.info(f"[{task.task_id}] Stage 2: Implementing")
            task.status = TaskStatus.IMPLEMENTING
            impl_result = await self._implement_task(task)
            result['stages']['implementation'] = impl_result
            
            if not impl_result['success']:
                task.mark_failed(f"Implementation failed: {impl_result.get('error')}")
                result['status'] = task.status.value
                return result
            
            # Stage 3: Test
            logger.info(f"[{task.task_id}] Stage 3: Testing")
            task.status = TaskStatus.TESTING
            test_result = await self._test_task(task)
            result['stages']['testing'] = test_result
            
            # Stage 4: Fix (if tests failed)
            if not test_result['success'] and test_result.get('failures'):
                logger.info(f"[{task.task_id}] Stage 4: Fixing issues")
                fix_result = await self._fix_task(task, test_result)
                result['stages']['fixing'] = fix_result
                
                if not fix_result['success']:
                    task.mark_failed(f"Fix failed after {task.fix_attempts} attempts")
                    result['status'] = task.status.value
                    return result
            
            # Stage 5: Document
            logger.info(f"[{task.task_id}] Stage 5: Documenting")
            task.status = TaskStatus.DOCUMENTING
            doc_result = await self._document_task(task)
            result['stages']['documentation'] = doc_result
            
            # Stage 6: Validate
            logger.info(f"[{task.task_id}] Stage 6: Validating")
            task.status = TaskStatus.VALIDATING
            validation_result = await self._validate_task(task)
            result['stages']['validation'] = validation_result
            
            if validation_result['success']:
                task.mark_completed()
                logger.info(f"[{task.task_id}] Task completed successfully")
            else:
                task.mark_failed(f"Validation failed: {validation_result.get('error')}")
            
            result['status'] = task.status.value
            
        except Exception as e:
            logger.error(f"[{task.task_id}] Task processing failed: {e}", exc_info=True)
            task.mark_failed(f"Exception: {str(e)}")
            result['status'] = task.status.value
            result['error'] = str(e)
        
        finally:
            self.current_task = None
        
        return result
    
    async def _plan_task(self, task: Task) -> Dict[str, Any]:
        """Create a detailed plan for the task."""
        try:
            # Use LLM to create a plan
            prompt = f"""Create a detailed plan for the following task:

Title: {task.title}
Type: {task.task_type.value}
Description: {task.description}

Please provide:
1. Step-by-step approach
2. Required resources/tools
3. Potential challenges
4. Success criteria

Be specific and actionable."""

            response = self.llm_router.query(
                prompt=prompt,
                temperature=0.7,
                agent_name='task_planner'
            )
            
            plan = response.get('response', '')
            task.plan = plan
            
            return {
                'success': True,
                'plan': plan
            }
            
        except Exception as e:
            logger.error(f"Planning failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _implement_task(self, task: Task) -> Dict[str, Any]:
        """Implement the task based on the plan."""
        try:
            # Determine appropriate agent based on task type
            agent_name = self._get_agent_for_task(task)
            
            if not agent_name:
                return {
                    'success': False,
                    'error': f"No suitable agent found for task type: {task.task_type.value}"
                }
            
            # Get agent
            agent = self.agent_registry.get_agent(agent_name)
            
            if not agent:
                return {
                    'success': False,
                    'error': f"Agent not found: {agent_name}"
                }
            
            # Execute task
            context = {
                'task': task.to_dict(),
                'plan': task.plan
            }
            
            result = agent.execute(task.description, context)
            task.implementation_result = result
            
            return {
                'success': result.get('success', False),
                'result': result,
                'agent': agent_name
            }
            
        except Exception as e:
            logger.error(f"Implementation failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _test_task(self, task: Task) -> Dict[str, Any]:
        """Test the implementation."""
        try:
            # Get test agent
            tester_agent = self.agent_registry.get_agent('code_tester')
            
            if not tester_agent:
                logger.warning("No test agent available, skipping tests")
                return {
                    'success': True,
                    'skipped': True,
                    'message': 'No test agent available'
                }
            
            # Run tests
            test_context = {
                'task': task.to_dict(),
                'implementation': task.implementation_result
            }
            
            test_result = tester_agent.execute('Run tests', test_context)
            task.test_results = test_result
            
            return {
                'success': test_result.get('success', False),
                'result': test_result,
                'failures': test_result.get('failures', [])
            }
            
        except Exception as e:
            logger.error(f"Testing failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _fix_task(self, task: Task, test_result: Dict[str, Any]) -> Dict[str, Any]:
        """Fix issues found during testing."""
        task.status = TaskStatus.FIXING
        
        while task.fix_attempts < task.max_fix_attempts:
            task.fix_attempts += 1
            
            try:
                logger.info(f"Fix attempt {task.fix_attempts}/{task.max_fix_attempts}")
                
                # Get debug agent
                debug_agent = self.agent_registry.get_agent('debug_agent')
                
                if not debug_agent:
                    return {
                        'success': False,
                        'error': 'No debug agent available'
                    }
                
                # Analyze and fix
                fix_context = {
                    'task': task.to_dict(),
                    'test_results': test_result,
                    'attempt': task.fix_attempts
                }
                
                fix_result = debug_agent.execute('Fix test failures', fix_context)
                
                # Re-test
                retest_result = await self._test_task(task)
                
                if retest_result['success']:
                    return {
                        'success': True,
                        'attempts': task.fix_attempts,
                        'result': fix_result
                    }
                    
            except Exception as e:
                logger.error(f"Fix attempt {task.fix_attempts} failed: {e}", exc_info=True)
        
        return {
            'success': False,
            'error': f'Failed to fix issues after {task.max_fix_attempts} attempts'
        }
    
    async def _document_task(self, task: Task) -> Dict[str, Any]:
        """Create documentation for the task."""
        try:
            # Use LLM to generate documentation
            prompt = f"""Generate documentation for the completed task:

Title: {task.title}
Type: {task.task_type.value}
Description: {task.description}
Plan: {task.plan}

Please provide:
1. Summary of changes
2. Usage examples (if applicable)
3. Notes for future reference
4. Git commit message

Be concise but complete."""

            response = self.llm_router.query(
                prompt=prompt,
                temperature=0.7,
                agent_name='documentation_generator'
            )
            
            documentation = response.get('response', '')
            task.documentation = documentation
            
            return {
                'success': True,
                'documentation': documentation
            }
            
        except Exception as e:
            logger.error(f"Documentation failed: {e}", exc_info=True)
            return {
                'success': True,  # Don't fail task if documentation fails
                'error': str(e),
                'documentation': None
            }
    
    async def _validate_task(self, task: Task) -> Dict[str, Any]:
        """Validate that the task is fully complete."""
        try:
            # Check all required stages completed
            validation_checks = {
                'has_plan': task.plan is not None,
                'has_implementation': task.implementation_result is not None,
                'tests_passed': task.test_results and task.test_results.get('success', False),
                'has_documentation': task.documentation is not None
            }
            
            all_passed = all(validation_checks.values())
            
            if all_passed:
                task.validation_result = {'passed': True, 'checks': validation_checks}
                return {
                    'success': True,
                    'checks': validation_checks
                }
            else:
                failed_checks = [k for k, v in validation_checks.items() if not v]
                task.validation_result = {'passed': False, 'checks': validation_checks, 'failed': failed_checks}
                return {
                    'success': False,
                    'error': f"Validation failed: {', '.join(failed_checks)}",
                    'checks': validation_checks
                }
                
        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_agent_for_task(self, task: Task) -> Optional[str]:
        """Determine the appropriate agent for a task type."""
        agent_mapping = {
            TaskType.FEATURE: 'code_editor',
            TaskType.BUG: 'debug_agent',
            TaskType.ERROR: 'debug_agent',
            TaskType.ISSUE: 'debug_agent',
            TaskType.REFACTOR: 'code_editor',
            TaskType.DOCUMENTATION: 'documentation_agent',
            TaskType.TEST: 'code_tester',
            TaskType.QUESTION: None,  # Handle separately
            TaskType.OTHER: 'code_editor'
        }
        
        return agent_mapping.get(task.task_type, 'code_editor')
    
    def save_state(self, filepath: Path) -> None:
        """Save processor state to file."""
        state = {
            'tasks': [t.to_dict() for t in self.tasks],
            'completed_tasks': [t.to_dict() for t in self.completed_tasks],
            'failed_tasks': [t.to_dict() for t in self.failed_tasks],
            'processing_started_at': self.processing_started_at.isoformat() if self.processing_started_at else None,
            'processing_completed_at': self.processing_completed_at.isoformat() if self.processing_completed_at else None
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Saved task loop processor state to {filepath}")
    
    def load_state(self, filepath: Path) -> None:
        """Load processor state from file."""
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        self.tasks = [Task.from_dict(t) for t in state['tasks']]
        self.completed_tasks = [Task.from_dict(t) for t in state['completed_tasks']]
        self.failed_tasks = [Task.from_dict(t) for t in state['failed_tasks']]
        
        if state['processing_started_at']:
            self.processing_started_at = datetime.fromisoformat(state['processing_started_at'])
        if state['processing_completed_at']:
            self.processing_completed_at = datetime.fromisoformat(state['processing_completed_at'])
        
        logger.info(f"Loaded task loop processor state from {filepath}")
    
    def get_progress(self) -> Dict[str, Any]:
        """Get processing progress information."""
        total = len(self.tasks) + len(self.completed_tasks) + len(self.failed_tasks)
        
        return {
            'total_tasks': total,
            'pending': len([t for t in self.tasks if t.status == TaskStatus.PENDING]),
            'in_progress': len([t for t in self.tasks if t.status not in [TaskStatus.PENDING, TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.SKIPPED]]),
            'completed': len(self.completed_tasks),
            'failed': len(self.failed_tasks),
            'progress_percent': (len(self.completed_tasks) + len(self.failed_tasks)) / total * 100 if total > 0 else 0,
            'current_task': self.current_task.to_dict() if self.current_task else None
        }
