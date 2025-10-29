
"""
Task Decomposition Module

Decomposes complex user prompts into AI-friendly lists of tasks and sub-tasks.
Uses LLM to intelligently break down requests while maintaining dependencies
and priorities.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional


logger = logging.getLogger(__name__)


class TaskDecomposer:
    """
    Decomposes complex prompts into structured task lists.
    
    Takes a user prompt and breaks it down into:
    - Main tasks
    - Sub-tasks
    - Dependencies
    - Priorities
    - Expected outputs
    """
    
    def __init__(self, llm_router: Optional[Any] = None):
        """
        Initialize task decomposer.
        
        Args:
            llm_router: LLM router for AI operations
        """
        self.llm_router = llm_router
        logger.info("TaskDecomposer initialized")
    
    def decompose(
        self,
        prompt: str,
        specifications: Optional[Dict[str, Any]] = None,
        max_subtasks: int = 20
    ) -> Dict[str, Any]:
        """
        Decompose a prompt into tasks and sub-tasks.
        
        Args:
            prompt: User's prompt
            specifications: Optional extracted specifications
            max_subtasks: Maximum number of subtasks per task
            
        Returns:
            Dictionary with task structure
        """
        logger.info(f"Decomposing prompt: {prompt[:100]}")
        
        if self.llm_router:
            return self._llm_decompose(prompt, specifications, max_subtasks)
        else:
            return self._rule_based_decompose(prompt, specifications, max_subtasks)
    
    def _llm_decompose(
        self,
        prompt: str,
        specifications: Optional[Dict[str, Any]],
        max_subtasks: int
    ) -> Dict[str, Any]:
        """
        Use LLM to decompose the prompt.
        
        Args:
            prompt: User's prompt
            specifications: Specifications
            max_subtasks: Max subtasks
            
        Returns:
            Task structure
        """
        decomposition_prompt = self._build_decomposition_prompt(
            prompt, specifications, max_subtasks
        )
        
        try:
            response = self.llm_router.query(
                prompt=decomposition_prompt,
                temperature=0.3,
                agent_name='task_orchestrator'
            )
            
            # Parse LLM response into structured format
            task_structure = self._parse_llm_response(response.get('response', ''))
            logger.info(f"LLM decomposed into {len(task_structure.get('tasks', []))} main tasks")
            
            return task_structure
            
        except Exception as e:
            logger.error(f"LLM decomposition failed: {e}")
            return self._rule_based_decompose(prompt, specifications, max_subtasks)
    
    def _build_decomposition_prompt(
        self,
        prompt: str,
        specifications: Optional[Dict[str, Any]],
        max_subtasks: int
    ) -> str:
        """
        Build a prompt for LLM task decomposition.
        
        Args:
            prompt: User's prompt
            specifications: Specifications
            max_subtasks: Max subtasks
            
        Returns:
            Decomposition prompt
        """
        spec_text = ""
        if specifications:
            spec_text = f"""
**Extracted Specifications:**
Goals: {', '.join(specifications.get('goals', []))}
Constraints: {', '.join(specifications.get('constraints', []))}
Preferences: {', '.join(specifications.get('preferences', []))}
"""
        
        return f"""You are a task decomposition expert. Break down the following user request into a structured list of tasks and sub-tasks.

**User Request:**
{prompt}
{spec_text}

**Instructions:**
1. Identify main tasks (high-level objectives)
2. Break each main task into concrete sub-tasks
3. Keep each task/sub-task atomic and actionable
4. Identify dependencies between tasks
5. Assign priority (1-10, higher = more important)
6. Limit to {max_subtasks} sub-tasks per main task

**Output Format:**
Provide a structured breakdown in the following format:

TASK 1: [Task description]
Priority: [1-10]
Dependencies: [List task numbers this depends on, or "None"]
Sub-tasks:
  1.1: [Sub-task description]
  1.2: [Sub-task description]
  ...

TASK 2: [Task description]
Priority: [1-10]
Dependencies: [e.g., "Task 1"]
Sub-tasks:
  2.1: [Sub-task description]
  ...

Be specific and actionable. Make sure tasks are clear enough for an AI agent to execute.
"""
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured task format.
        
        Args:
            response: LLM response text
            
        Returns:
            Structured task dictionary
        """
        tasks = []
        current_task = None
        
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('TASK '):
                # Save previous task
                if current_task:
                    tasks.append(current_task)
                
                # Start new task
                task_desc = line.split(':', 1)[1].strip() if ':' in line else line
                current_task = {
                    'id': f"task_{len(tasks) + 1}",
                    'description': task_desc,
                    'priority': 5,
                    'dependencies': [],
                    'subtasks': []
                }
            
            elif line.startswith('Priority:') and current_task:
                try:
                    priority = int(line.split(':')[1].strip())
                    current_task['priority'] = max(1, min(10, priority))
                except ValueError:
                    pass
            
            elif line.startswith('Dependencies:') and current_task:
                dep_text = line.split(':', 1)[1].strip().lower()
                if dep_text != 'none':
                    # Parse dependencies (simplified)
                    current_task['dependencies'] = [dep_text]
            
            elif line and current_task and ('.' in line[:5]):
                # Sub-task
                subtask_desc = line.split(':', 1)[1].strip() if ':' in line else line
                current_task['subtasks'].append({
                    'id': f"{current_task['id']}_sub_{len(current_task['subtasks']) + 1}",
                    'description': subtask_desc
                })
        
        # Save last task
        if current_task:
            tasks.append(current_task)
        
        return {'tasks': tasks}
    
    def _rule_based_decompose(
        self,
        prompt: str,
        specifications: Optional[Dict[str, Any]],
        max_subtasks: int
    ) -> Dict[str, Any]:
        """
        Rule-based task decomposition (fallback).
        
        Args:
            prompt: User's prompt
            specifications: Specifications
            max_subtasks: Max subtasks
            
        Returns:
            Task structure
        """
        logger.info("Using rule-based decomposition")
        
        # Simple heuristic-based decomposition
        tasks = []
        
        # Look for action words
        action_words = {
            'create': 'Create',
            'build': 'Build',
            'implement': 'Implement',
            'write': 'Write',
            'test': 'Test',
            'deploy': 'Deploy',
            'setup': 'Setup',
            'configure': 'Configure',
            'initialize': 'Initialize',
        }
        
        prompt_lower = prompt.lower()
        
        # Generate tasks based on keywords
        for keyword, action in action_words.items():
            if keyword in prompt_lower:
                task_id = f"task_{len(tasks) + 1}"
                tasks.append({
                    'id': task_id,
                    'description': f"{action} components as specified",
                    'priority': 5,
                    'dependencies': [],
                    'subtasks': [
                        {
                            'id': f"{task_id}_sub_1",
                            'description': f"Plan {keyword} approach"
                        },
                        {
                            'id': f"{task_id}_sub_2",
                            'description': f"Execute {keyword} operation"
                        },
                        {
                            'id': f"{task_id}_sub_3",
                            'description': f"Verify {keyword} result"
                        }
                    ]
                })
        
        # If no tasks generated, create a default task
        if not tasks:
            tasks.append({
                'id': 'task_1',
                'description': 'Complete the requested operation',
                'priority': 5,
                'dependencies': [],
                'subtasks': [
                    {
                        'id': 'task_1_sub_1',
                        'description': 'Analyze requirements'
                    },
                    {
                        'id': 'task_1_sub_2',
                        'description': 'Execute main operation'
                    },
                    {
                        'id': 'task_1_sub_3',
                        'description': 'Verify results'
                    }
                ]
            })
        
        return {'tasks': tasks}
