"""
Task Decomposer

Breaks down complex tasks into manageable sub-tasks.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
import json


@dataclass
class SubTask:
    """Sub-task definition."""
    id: int
    description: str
    dependencies: List[int] = field(default_factory=list)
    estimated_time: str = "10 min"
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[str] = None
    error: Optional[str] = None


@dataclass
class TaskAnalysis:
    """Task analysis result."""
    complexity: str  # 'simple', 'moderate', 'complex'
    estimated_subtasks: int
    requires_decomposition: bool
    components: List[str]
    risks: List[str]


class TaskDecomposer:
    """Decomposes complex tasks into sub-tasks."""
    
    def __init__(self, ai_backend):
        """
        Initialize task decomposer.
        
        Args:
            ai_backend: AI backend for decomposition
        """
        self.ai_backend = ai_backend
    
    def analyze_task(self, description: str, context: Optional[Dict] = None) -> TaskAnalysis:
        """
        Analyze task complexity.
        
        Args:
            description: Task description
            context: Optional context information
            
        Returns:
            TaskAnalysis object
        """
        # Simple heuristic-based analysis
        word_count = len(description.split())
        
        # Determine complexity
        if word_count < 10:
            complexity = 'simple'
            estimated_subtasks = 1
            requires_decomposition = False
        elif word_count < 30:
            complexity = 'moderate'
            estimated_subtasks = 3
            requires_decomposition = True
        else:
            complexity = 'complex'
            estimated_subtasks = 5
            requires_decomposition = True
        
        # Identify components (keywords)
        components = []
        keywords = ['api', 'database', 'authentication', 'frontend', 'backend',
                   'test', 'documentation', 'deployment']
        
        desc_lower = description.lower()
        for keyword in keywords:
            if keyword in desc_lower:
                components.append(keyword)
        
        # Identify risks
        risks = []
        if 'complex' in desc_lower or 'large' in desc_lower:
            risks.append("High complexity may require more time")
        if 'database' in desc_lower:
            risks.append("Database changes require careful migration")
        if 'authentication' in desc_lower or 'security' in desc_lower:
            risks.append("Security-critical feature requires extra testing")
        
        return TaskAnalysis(
            complexity=complexity,
            estimated_subtasks=estimated_subtasks,
            requires_decomposition=requires_decomposition,
            components=components,
            risks=risks
        )
    
    def decompose_task(self, description: str, language: str = 'python',
                      framework: Optional[str] = None,
                      max_subtasks: int = 10) -> List[SubTask]:
        """
        Decompose task into sub-tasks.
        
        Args:
            description: Task description
            language: Programming language
            framework: Framework
            max_subtasks: Maximum number of sub-tasks
            
        Returns:
            List of SubTask objects
        """
        # Build prompt for AI
        prompt = self._build_decomposition_prompt(description, language, framework)
        
        try:
            # Get AI response
            response = self.ai_backend.query(prompt, max_tokens=1500)
            
            # Parse response
            subtasks = self._parse_subtasks(response)
            
            # Limit number of subtasks
            if len(subtasks) > max_subtasks:
                subtasks = subtasks[:max_subtasks]
            
            return subtasks
            
        except Exception as e:
            print(f"Error decomposing task: {e}")
            # Fallback: create simple subtasks
            return self._create_fallback_subtasks(description)
    
    def _build_decomposition_prompt(self, description: str, language: str,
                                   framework: Optional[str]) -> str:
        """Build prompt for task decomposition."""
        prompt = f"""Break down this feature into small, manageable sub-tasks:

Feature: {description}
Language: {language}
Framework: {framework or 'None'}

Requirements:
1. Each sub-task should take < 15 minutes
2. Sub-tasks should be atomic (one clear objective)
3. Include dependencies between tasks (use task IDs)
4. Order tasks logically
5. Include testing tasks

Output as JSON array with this exact format:
[
  {{
    "id": 1,
    "description": "Clear description of what to do",
    "dependencies": [],
    "estimated_time": "10 min"
  }},
  {{
    "id": 2,
    "description": "Another task",
    "dependencies": [1],
    "estimated_time": "8 min"
  }}
]

Generate only the JSON array, no additional text."""
        
        return prompt
    
    def _parse_subtasks(self, response: str) -> List[SubTask]:
        """Parse AI response into SubTask objects."""
        # Clean response
        response = response.strip()
        
        # Extract JSON if wrapped in markdown
        if '```json' in response:
            start = response.find('```json') + 7
            end = response.find('```', start)
            response = response[start:end].strip()
        elif '```' in response:
            start = response.find('```') + 3
            end = response.find('```', start)
            response = response[start:end].strip()
        
        try:
            data = json.loads(response)
            
            subtasks = []
            for item in data:
                subtask = SubTask(
                    id=item['id'],
                    description=item['description'],
                    dependencies=item.get('dependencies', []),
                    estimated_time=item.get('estimated_time', '10 min'),
                    status='pending'
                )
                subtasks.append(subtask)
            
            return subtasks
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return []
    
    def _create_fallback_subtasks(self, description: str) -> List[SubTask]:
        """Create simple fallback subtasks."""
        return [
            SubTask(
                id=1,
                description=f"Implement: {description}",
                dependencies=[],
                estimated_time="15 min"
            ),
            SubTask(
                id=2,
                description=f"Test: {description}",
                dependencies=[1],
                estimated_time="10 min"
            ),
            SubTask(
                id=3,
                description=f"Document: {description}",
                dependencies=[1, 2],
                estimated_time="5 min"
            )
        ]
    
    def validate_dependencies(self, subtasks: List[SubTask]) -> bool:
        """
        Validate that dependencies are valid.
        
        Args:
            subtasks: List of subtasks
            
        Returns:
            True if valid
        """
        task_ids = {task.id for task in subtasks}
        
        for task in subtasks:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    print(f"Invalid dependency: Task {task.id} depends on non-existent task {dep_id}")
                    return False
                
                if dep_id >= task.id:
                    print(f"Invalid dependency: Task {task.id} depends on later task {dep_id}")
                    return False
        
        return True
    
    def get_ready_tasks(self, subtasks: List[SubTask]) -> List[SubTask]:
        """
        Get tasks that are ready to execute (dependencies met).
        
        Args:
            subtasks: List of all subtasks
            
        Returns:
            List of ready tasks
        """
        completed_ids = {task.id for task in subtasks if task.status == 'completed'}
        
        ready = []
        for task in subtasks:
            if task.status == 'pending':
                # Check if all dependencies are completed
                if all(dep_id in completed_ids for dep_id in task.dependencies):
                    ready.append(task)
        
        return ready
    
    def estimate_total_time(self, subtasks: List[SubTask]) -> str:
        """
        Estimate total time for all subtasks.
        
        Args:
            subtasks: List of subtasks
            
        Returns:
            Estimated time string
        """
        total_minutes = 0
        
        for task in subtasks:
            # Parse time string (e.g., "10 min", "1 hour")
            time_str = task.estimated_time.lower()
            
            if 'min' in time_str:
                minutes = int(''.join(filter(str.isdigit, time_str)))
                total_minutes += minutes
            elif 'hour' in time_str:
                hours = int(''.join(filter(str.isdigit, time_str)))
                total_minutes += hours * 60
        
        if total_minutes < 60:
            return f"{total_minutes} minutes"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            if minutes > 0:
                return f"{hours} hour(s) {minutes} minutes"
            else:
                return f"{hours} hour(s)"
