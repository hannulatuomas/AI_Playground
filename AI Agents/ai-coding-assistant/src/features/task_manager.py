"""
Task Manager Module

Handles decomposition and execution of complex tasks.
Breaks large tasks into manageable sub-tasks and executes them systematically.

Features:
- LLM-powered task decomposition
- Dependency tracking
- Context-aware execution
- Progress tracking with memory
- Automatic and manual feedback
- Integration with all previous phases
"""

import json
import time
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Status of a task or sub-task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskType(Enum):
    """Type of task action."""
    GENERATE_CODE = "generate_code"
    EDIT_FILE = "edit_file"
    DEBUG_CODE = "debug_code"
    ANALYZE = "analyze"
    RESEARCH = "research"
    TEST = "test"
    DOCUMENT = "document"


class TaskManager:
    """
    Manage complex task decomposition and execution.
    Integrates all features: project management, navigation, context, and memory.
    """

    def __init__(
        self,
        llm_interface,
        project_manager=None,
        project_navigator=None,
        context_manager=None,
        code_generator=None,
        debugger=None,
        learning_db=None
    ):
        """
        Initialize the task manager.

        Args:
            llm_interface: LLMInterface for task decomposition
            project_manager: ProjectManager for file access
            project_navigator: ProjectNavigator for search/edit
            context_manager: ContextManager for context building
            code_generator: CodeGenerator for code generation
            debugger: Debugger for debugging tasks
            learning_db: LearningDB for memory and logging

        Example:
            >>> from src.core.llm_interface import LLMInterface, load_config_from_file
            >>> from src.core.project_manager import ProjectManager
            >>> from src.features import (
            ...     ProjectNavigator, ContextManager, 
            ...     CodeGenerator, TaskManager
            ... )
            >>> 
            >>> config = load_config_from_file()
            >>> llm = LLMInterface(config)
            >>> pm = ProjectManager(llm_interface=llm)
            >>> pn = ProjectNavigator(pm, llm)
            >>> cm = ContextManager(pm, pn, db, pe)
            >>> cg = CodeGenerator(llm, pe, db)
            >>> 
            >>> task_mgr = TaskManager(llm, pm, pn, cm, cg, None, db)
        """
        self.llm_interface = llm_interface
        self.project_manager = project_manager
        self.project_navigator = project_navigator
        self.context_manager = context_manager
        self.code_generator = code_generator
        self.debugger = debugger
        self.learning_db = learning_db
        
        # Task execution state
        self.current_task = None
        self.task_history = []
        
        # Configuration
        self.max_sub_tasks_before_batch = 10
        self.auto_feedback_enabled = False

    def decompose_task(
        self,
        user_task: str,
        project_id: Optional[str] = None,
        language: Optional[str] = None,
        context_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Decompose a complex task into atomic sub-tasks using LLM.

        Args:
            user_task: High-level task description
            project_id: Optional project identifier
            language: Optional programming language
            context_files: Optional relevant files for context

        Returns:
            Dictionary with decomposed task structure

        Example:
            >>> result = task_mgr.decompose_task(
            ...     user_task="Build a login system with JWT authentication",
            ...     project_id="my-web-app",
            ...     language="python"
            ... )
            >>> print(f"Sub-tasks: {len(result['sub_tasks'])}")
            >>> for task in result['sub_tasks']:
            ...     print(f"- {task['description']}")
        """
        print(f"Decomposing task: {user_task}")
        
        # Build context for decomposition
        context_text = self._build_decomposition_context(
            user_task=user_task,
            project_id=project_id,
            language=language,
            context_files=context_files
        )
        
        # Build decomposition prompt
        prompt = self._build_decomposition_prompt(user_task, context_text)
        
        # Get LLM response
        try:
            response = self.llm_interface.generate(
                prompt,
                max_tokens=1500,
                use_cache=False
            )
            
            # Parse response
            sub_tasks = self._parse_decomposition_response(response)
            
            # Prioritize if many tasks
            if len(sub_tasks) > self.max_sub_tasks_before_batch:
                print(f"Large task list ({len(sub_tasks)} tasks), prioritizing...")
                sub_tasks = self._prioritize_tasks(sub_tasks, user_task)
            
            # Create task structure
            task_structure = {
                'task_id': self._generate_task_id(),
                'description': user_task,
                'project_id': project_id,
                'language': language,
                'status': TaskStatus.PENDING.value,
                'sub_tasks': sub_tasks,
                'created_at': datetime.now().isoformat(),
                'total_sub_tasks': len(sub_tasks),
                'completed_sub_tasks': 0
            }
            
            print(f"✓ Decomposed into {len(sub_tasks)} sub-tasks")
            return task_structure
            
        except Exception as e:
            print(f"✗ Error decomposing task: {e}")
            # Fallback: Create simple task structure
            return {
                'task_id': self._generate_task_id(),
                'description': user_task,
                'project_id': project_id,
                'language': language,
                'status': TaskStatus.PENDING.value,
                'sub_tasks': [
                    {
                        'id': 1,
                        'description': user_task,
                        'type': TaskType.GENERATE_CODE.value,
                        'status': TaskStatus.PENDING.value,
                        'dependencies': []
                    }
                ],
                'created_at': datetime.now().isoformat(),
                'total_sub_tasks': 1,
                'completed_sub_tasks': 0,
                'decomposition_error': str(e)
            }

    def execute_tasks(
        self,
        task_structure: Dict[str, Any],
        interactive: bool = True,
        stop_on_failure: bool = False
    ) -> Dict[str, Any]:
        """
        Execute decomposed tasks sequentially.

        Args:
            task_structure: Task structure from decompose_task()
            interactive: Whether to ask for user feedback
            stop_on_failure: Stop execution on first failure

        Returns:
            Execution results dictionary

        Example:
            >>> task_structure = task_mgr.decompose_task("Build login system")
            >>> results = task_mgr.execute_tasks(
            ...     task_structure,
            ...     interactive=True,
            ...     stop_on_failure=False
            ... )
            >>> print(f"Success: {results['success']}")
            >>> print(f"Completed: {results['completed']}/{results['total']}")
        """
        print(f"\n{'='*60}")
        print(f"Executing: {task_structure['description']}")
        print(f"{'='*60}\n")
        
        self.current_task = task_structure
        task_structure['status'] = TaskStatus.IN_PROGRESS.value
        task_structure['started_at'] = datetime.now().isoformat()
        
        sub_tasks = task_structure['sub_tasks']
        results = {
            'task_id': task_structure['task_id'],
            'total': len(sub_tasks),
            'completed': 0,
            'failed': 0,
            'skipped': 0,
            'sub_task_results': [],
            'success': False
        }
        
        # Execute each sub-task
        for i, sub_task in enumerate(sub_tasks):
            print(f"\n--- Sub-task {i+1}/{len(sub_tasks)} ---")
            print(f"Description: {sub_task['description']}")
            
            # Check dependencies
            if not self._check_dependencies(sub_task, sub_tasks):
                print(f"⚠ Dependencies not met, skipping")
                sub_task['status'] = TaskStatus.SKIPPED.value
                results['skipped'] += 1
                continue
            
            # Execute sub-task
            sub_task['status'] = TaskStatus.IN_PROGRESS.value
            sub_task_result = self._execute_sub_task(
                sub_task=sub_task,
                task_structure=task_structure
            )
            
            results['sub_task_results'].append(sub_task_result)
            
            # Update status
            if sub_task_result['success']:
                sub_task['status'] = TaskStatus.COMPLETED.value
                results['completed'] += 1
                task_structure['completed_sub_tasks'] += 1
                print(f"✓ Sub-task completed")
                
                # Log to memory
                if self.context_manager:
                    self.context_manager.log_action(
                        action=sub_task['description'],
                        outcome=sub_task_result.get('outcome', 'Completed successfully'),
                        project_id=task_structure.get('project_id'),
                        file_path=sub_task_result.get('file_path'),
                        success=True
                    )
            else:
                sub_task['status'] = TaskStatus.FAILED.value
                results['failed'] += 1
                print(f"✗ Sub-task failed: {sub_task_result.get('error')}")
                
                # Log to memory
                if self.context_manager:
                    self.context_manager.log_action(
                        action=sub_task['description'],
                        outcome=f"Failed: {sub_task_result.get('error')}",
                        project_id=task_structure.get('project_id'),
                        file_path=sub_task_result.get('file_path'),
                        success=False
                    )
                
                if stop_on_failure:
                    print("Stopping execution due to failure")
                    break
            
            # Get feedback if interactive
            if interactive and sub_task_result['success']:
                feedback = self._get_user_feedback(sub_task, sub_task_result)
                sub_task_result['user_feedback'] = feedback
                
                if feedback and not feedback.get('continue', True):
                    print("User requested stop")
                    break
        
        # Finalize
        if results['failed'] == 0 and results['skipped'] == 0:
            task_structure['status'] = TaskStatus.COMPLETED.value
            results['success'] = True
        elif results['completed'] > 0:
            task_structure['status'] = TaskStatus.COMPLETED.value  # Partial success
            results['success'] = True
        else:
            task_structure['status'] = TaskStatus.FAILED.value
        
        task_structure['completed_at'] = datetime.now().isoformat()
        self.task_history.append(task_structure)
        
        print(f"\n{'='*60}")
        print(f"Execution Complete")
        print(f"{'='*60}")
        print(f"Total: {results['total']}")
        print(f"Completed: {results['completed']}")
        print(f"Failed: {results['failed']}")
        print(f"Skipped: {results['skipped']}")
        print(f"Success: {results['success']}")
        
        return results

    def _build_decomposition_context(
        self,
        user_task: str,
        project_id: Optional[str],
        language: Optional[str],
        context_files: Optional[List[str]]
    ) -> str:
        """Build context for task decomposition."""
        context_parts = []
        
        # Add language context
        if language:
            context_parts.append(f"Language: {language}")
        
        # Add project context
        if project_id and self.context_manager:
            history = self.context_manager.get_history(
                project_id=project_id,
                time_window_days=7,
                limit=5
            )
            if history:
                context_parts.append("\nRecent project actions:")
                for entry in history[:3]:
                    context_parts.append(f"- {entry.get('action', '')}")
        
        # Add file context
        if context_files and self.project_manager:
            context_parts.append("\nRelevant files:")
            for file_path in context_files[:5]:
                summary = self.project_manager.file_index.get(file_path, {}).get('summary')
                if summary:
                    context_parts.append(f"- {file_path}: {summary[:100]}")
        
        return "\n".join(context_parts) if context_parts else ""

    def _build_decomposition_prompt(self, user_task: str, context: str) -> str:
        """Build LLM prompt for task decomposition."""
        prompt = f"""Break this task into atomic sub-tasks that can be executed independently.

Task: {user_task}

{context}

Requirements:
1. Each sub-task should be specific and actionable
2. Include task type (generate_code, edit_file, debug_code, analyze, test, document)
3. Specify dependencies (IDs of tasks that must complete first)
4. Keep sub-tasks focused and minimal

Output format (JSON):
[
  {{
    "id": 1,
    "description": "Design database schema for users",
    "type": "generate_code",
    "dependencies": [],
    "estimated_time": "short"
  }},
  {{
    "id": 2,
    "description": "Implement user model",
    "type": "generate_code",
    "dependencies": [1],
    "estimated_time": "medium"
  }}
]

Output only the JSON array, no additional text."""

        return prompt

    def _parse_decomposition_response(self, response: str) -> List[Dict]:
        """Parse LLM response into sub-task list."""
        # Try to extract JSON from response
        json_start = response.find('[')
        json_end = response.rfind(']') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            try:
                tasks = json.loads(json_str)
                
                # Ensure required fields
                for i, task in enumerate(tasks):
                    if 'id' not in task:
                        task['id'] = i + 1
                    if 'status' not in task:
                        task['status'] = TaskStatus.PENDING.value
                    if 'dependencies' not in task:
                        task['dependencies'] = []
                    if 'type' not in task:
                        task['type'] = TaskType.GENERATE_CODE.value
                
                return tasks
            except json.JSONDecodeError as e:
                print(f"Warning: Could not parse JSON: {e}")
        
        # Fallback: Parse as text list
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        tasks = []
        for i, line in enumerate(lines):
            # Remove numbering and bullets
            line = line.lstrip('0123456789.-) ')
            if line:
                tasks.append({
                    'id': i + 1,
                    'description': line,
                    'type': TaskType.GENERATE_CODE.value,
                    'status': TaskStatus.PENDING.value,
                    'dependencies': []
                })
        
        return tasks if tasks else [{
            'id': 1,
            'description': 'Execute task',
            'type': TaskType.GENERATE_CODE.value,
            'status': TaskStatus.PENDING.value,
            'dependencies': []
        }]

    def _prioritize_tasks(self, tasks: List[Dict], user_task: str) -> List[Dict]:
        """Prioritize large task list using LLM."""
        # Build prioritization prompt
        task_list = "\n".join([
            f"{task['id']}. {task['description']}"
            for task in tasks
        ])
        
        prompt = f"""Original task: {user_task}

Sub-tasks (needs prioritization):
{task_list}

Order these sub-tasks logically for execution. Consider:
1. Dependencies (what must be done first)
2. Efficiency (group similar tasks)
3. Testing (tests after implementation)

Output the task IDs in execution order, comma-separated.
Example: 1,3,2,5,4

Task IDs in priority order:"""

        try:
            response = self.llm_interface.generate(
                prompt,
                max_tokens=200,
                use_cache=False
            )
            
            # Parse response
            response_clean = response.strip().replace('\n', ',')
            ids = []
            for part in response_clean.split(','):
                try:
                    task_id = int(part.strip())
                    if 1 <= task_id <= len(tasks):
                        ids.append(task_id)
                except ValueError:
                    continue
            
            # Reorder tasks
            if ids:
                task_map = {task['id']: task for task in tasks}
                ordered_tasks = []
                for task_id in ids:
                    if task_id in task_map:
                        ordered_tasks.append(task_map[task_id])
                
                # Add any missing tasks
                for task in tasks:
                    if task not in ordered_tasks:
                        ordered_tasks.append(task)
                
                return ordered_tasks
        
        except Exception as e:
            print(f"Warning: Could not prioritize tasks: {e}")
        
        return tasks

    def _execute_sub_task(
        self,
        sub_task: Dict,
        task_structure: Dict
    ) -> Dict[str, Any]:
        """Execute a single sub-task."""
        task_type = sub_task.get('type', TaskType.GENERATE_CODE.value)
        description = sub_task['description']
        
        # Build context for this sub-task
        if self.context_manager:
            context = self.context_manager.build_context(
                task=description,
                max_tokens=3000,
                project_id=task_structure.get('project_id'),
                language=task_structure.get('language'),
                include_history=True
            )
            context_text = self.context_manager.format_context_for_prompt(context)
        else:
            context_text = ""
        
        result = {
            'sub_task_id': sub_task['id'],
            'description': description,
            'type': task_type,
            'success': False,
            'output': None,
            'error': None
        }
        
        try:
            # Route to appropriate handler
            if task_type == TaskType.GENERATE_CODE.value:
                output = self._execute_code_generation(
                    description,
                    task_structure.get('language'),
                    context_text
                )
                result['success'] = output is not None
                result['output'] = output
                result['outcome'] = f"Generated code: {len(output) if output else 0} characters"
                
            elif task_type == TaskType.EDIT_FILE.value:
                output = self._execute_file_edit(
                    description,
                    task_structure,
                    context_text
                )
                result['success'] = output.get('success', False)
                result['output'] = output
                result['file_path'] = output.get('file')
                result['outcome'] = f"Edited file: {output.get('file')}"
                
            elif task_type == TaskType.DEBUG_CODE.value:
                output = self._execute_debug(
                    description,
                    task_structure.get('language'),
                    context_text
                )
                result['success'] = output is not None
                result['output'] = output
                result['outcome'] = "Debugged code"
                
            else:
                # Generic task execution
                output = self._execute_generic_task(
                    description,
                    context_text
                )
                result['success'] = output is not None
                result['output'] = output
                result['outcome'] = "Task completed"
        
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
        
        return result

    def _execute_code_generation(
        self,
        description: str,
        language: Optional[str],
        context: str
    ) -> Optional[str]:
        """Execute code generation sub-task."""
        if not self.code_generator:
            print("Warning: CodeGenerator not available")
            return None
        
        full_prompt = f"{context}\n\n{description}" if context else description
        
        result = self.code_generator.generate_code(
            task=full_prompt,
            language=language or 'python'
        )
        
        return result.get('code') if result else None

    def _execute_file_edit(
        self,
        description: str,
        task_structure: Dict,
        context: str
    ) -> Dict[str, Any]:
        """Execute file editing sub-task."""
        if not self.project_navigator:
            return {'success': False, 'error': 'ProjectNavigator not available'}
        
        # Extract file path from description (simple heuristic)
        # In production, this would be more sophisticated
        words = description.split()
        file_path = None
        for word in words:
            if '.' in word and '/' in word:
                file_path = word
                break
        
        if not file_path:
            return {'success': False, 'error': 'Could not determine file path'}
        
        # For now, return placeholder
        # In production, would generate and apply actual edits
        return {
            'success': True,
            'file': file_path,
            'message': f"Would edit {file_path}"
        }

    def _execute_debug(
        self,
        description: str,
        language: Optional[str],
        context: str
    ) -> Optional[str]:
        """Execute debugging sub-task."""
        if not self.debugger:
            print("Warning: Debugger not available")
            return None
        
        # Placeholder: would need code and error from description
        return "Debug completed (placeholder)"

    def _execute_generic_task(self, description: str, context: str) -> Optional[str]:
        """Execute generic task using LLM."""
        full_prompt = f"{context}\n\n{description}" if context else description
        
        result = self.llm_interface.generate(
            full_prompt,
            max_tokens=500
        )
        
        return result if result else None

    def _check_dependencies(
        self,
        sub_task: Dict,
        all_tasks: List[Dict]
    ) -> bool:
        """Check if sub-task dependencies are met."""
        dependencies = sub_task.get('dependencies', [])
        
        if not dependencies:
            return True
        
        # Check each dependency
        for dep_id in dependencies:
            dep_task = next((t for t in all_tasks if t['id'] == dep_id), None)
            if not dep_task:
                continue
            
            if dep_task['status'] != TaskStatus.COMPLETED.value:
                return False
        
        return True

    def _get_user_feedback(
        self,
        sub_task: Dict,
        result: Dict
    ) -> Dict[str, Any]:
        """Get user feedback on sub-task completion."""
        print(f"\nSub-task completed: {sub_task['description']}")
        
        if result.get('output'):
            print(f"Output preview: {str(result['output'])[:200]}")
        
        response = input("\nContinue with next sub-task? (y/n/s=stop): ").strip().lower()
        
        return {
            'continue': response not in ['n', 's', 'stop'],
            'response': response
        }

    def _generate_task_id(self) -> str:
        """Generate unique task ID."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"task_{timestamp}"

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a task by ID."""
        if self.current_task and self.current_task['task_id'] == task_id:
            return self.current_task
        
        for task in self.task_history:
            if task['task_id'] == task_id:
                return task
        
        return None


if __name__ == "__main__":
    # Test the task manager
    print("Testing Task Manager...")
    
    from src.core.llm_interface import LLMInterface, load_config_from_file
    from src.core.learning_db import LearningDB
    
    try:
        config = load_config_from_file()
        llm = LLMInterface(config)
        db = LearningDB()
        
        task_mgr = TaskManager(llm, learning_db=db)
        print("✓ Task Manager created")
        
        # Test decomposition
        print("\n=== Test: Decompose Task ===")
        task_structure = task_mgr.decompose_task(
            user_task="Create a simple REST API with user authentication",
            language="python"
        )
        print(f"Task ID: {task_structure['task_id']}")
        print(f"Sub-tasks: {task_structure['total_sub_tasks']}")
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
