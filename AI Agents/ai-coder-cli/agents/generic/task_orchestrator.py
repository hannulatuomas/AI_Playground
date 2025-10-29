
"""
Task Orchestration Agent

This agent manages complex multi-step workflows by decomposing tasks, selecting
appropriate agents, enhancing prompts, managing context, and coordinating execution.

Capabilities:
- Task decomposition into AI-friendly sub-tasks
- Specification extraction (goals, rules, preferences, success measures)
- Intelligent agent selection
- Prompt enhancement while preserving user intent
- Context management with vector database integration
- Workflow execution coordination
- Progress tracking and reporting
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from ..base import Agent
from .task_decomposition import TaskDecomposer
from .specification_extraction import SpecificationExtractor
from .context_manager import ContextManager
from core.vector_memory import VectorMemoryManager


logger = logging.getLogger(__name__)


class TaskOrchestrator(Agent):
    """
    Orchestrates complex multi-step workflows.
    
    The orchestrator takes a user's complex request and:
    1. Decomposes it into manageable tasks and sub-tasks
    2. Extracts specifications, goals, and constraints
    3. Selects appropriate agents for each task
    4. Enhances prompts while maintaining user intent
    5. Manages context across the workflow
    6. Coordinates agent execution
    7. Tracks progress and provides updates
    
    Example:
        >>> orchestrator = TaskOrchestrator(llm_router=router, tool_registry=tools)
        >>> result = orchestrator.execute({
        ...     'prompt': 'Build a Python web API with FastAPI, include tests',
        ...     'session_id': session_id
        ... })
    """
    
    def __init__(
        self,
        name: str = "task_orchestrator",
        description: str = "Orchestrates complex multi-step workflows",
        llm_router: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[VectorMemoryManager] = None
    ):
        """
        Initialize the task orchestrator.
        
        Args:
            name: Agent name
            description: Agent description
            llm_router: LLM router for AI operations
            tool_registry: Tool registry
            config: Configuration dictionary
            memory_manager: Vector-enhanced memory manager
        """
        super().__init__(
            name=name,
            description=description,
            llm_router=llm_router,
            tool_registry=tool_registry,
            config=config,
            memory_manager=memory_manager
        )
        
        # Initialize components
        self.task_decomposer = TaskDecomposer(llm_router=llm_router)
        self.spec_extractor = SpecificationExtractor(llm_router=llm_router)
        self.context_manager = ContextManager(
            memory_manager=memory_manager,
            llm_router=llm_router
        )
        
        # Workflow state
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        
        logger.info("TaskOrchestrator initialized")
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complex workflow.
        
        Args:
            params: Dictionary with:
                - prompt: User's request
                - session_id: Session identifier
                - context: Optional additional context
                - max_subtasks: Optional limit on subtasks
                
        Returns:
            Dictionary with workflow results
        """
        prompt = params.get('prompt', '')
        session_id = params.get('session_id')
        additional_context = params.get('context', {})
        max_subtasks = params.get('max_subtasks', 20)
        
        if not prompt:
            return {
                'success': False,
                'error': 'No prompt provided'
            }
        
        # Create workflow ID
        workflow_id = str(uuid.uuid4())
        
        logger.info(f"Starting workflow {workflow_id[:8]} for prompt: {prompt[:100]}")
        
        try:
            # Step 1: Extract specifications
            logger.info("Step 1: Extracting specifications...")
            specifications = self.spec_extractor.extract(prompt)
            
            # Step 2: Decompose into tasks
            logger.info("Step 2: Decomposing into tasks...")
            task_structure = self.task_decomposer.decompose(
                prompt=prompt,
                specifications=specifications,
                max_subtasks=max_subtasks
            )
            
            # Step 3: Gather and refine context
            logger.info("Step 3: Gathering context...")
            workflow_context = self.context_manager.gather_context(
                prompt=prompt,
                specifications=specifications,
                task_structure=task_structure,
                session_id=session_id,
                additional_context=additional_context
            )
            
            # Step 4: Select agents for tasks
            logger.info("Step 4: Selecting agents...")
            agent_assignments = self._select_agents_for_tasks(
                task_structure=task_structure,
                specifications=specifications
            )
            
            # Step 5: Enhance prompts for each task
            logger.info("Step 5: Enhancing task prompts...")
            enhanced_tasks = self._enhance_task_prompts(
                task_structure=task_structure,
                agent_assignments=agent_assignments,
                specifications=specifications,
                workflow_context=workflow_context
            )
            
            # Create workflow state
            workflow_state = {
                'workflow_id': workflow_id,
                'status': 'ready',
                'prompt': prompt,
                'specifications': specifications,
                'task_structure': task_structure,
                'agent_assignments': agent_assignments,
                'enhanced_tasks': enhanced_tasks,
                'context': workflow_context,
                'session_id': session_id,
                'created_at': datetime.now().isoformat(),
                'progress': {
                    'total_tasks': len(enhanced_tasks),
                    'completed': 0,
                    'failed': 0
                }
            }
            
            self.active_workflows[workflow_id] = workflow_state
            
            # Step 6: Execute workflow
            logger.info("Step 6: Executing workflow...")
            execution_result = self._execute_workflow(workflow_id)
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'specifications': specifications,
                'tasks': enhanced_tasks,
                'execution': execution_result,
                'message': f"Workflow completed with {execution_result['completed']} tasks"
            }
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id[:8]} failed: {e}", exc_info=True)
            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': str(e)
            }
    
    def _select_agents_for_tasks(
        self,
        task_structure: Dict[str, Any],
        specifications: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Select appropriate agents for each task.
        
        Enhanced with complete coding workflow awareness including:
        - Project initialization agents (by language)
        - Code planning agents
        - Language-specific code editors
        - Code analysis agents
        - Language-specific debug agents
        - Language-specific test agents
        - Language-specific build agents
        - Documentation agents
        - Git agents
        
        Args:
            task_structure: Decomposed task structure
            specifications: Extracted specifications
            
        Returns:
            Dictionary mapping task IDs to agent names
        """
        assignments = {}
        
        # Enhanced agent selection rules for complete coding workflow
        agent_rules = {
            # Project Initialization
            'project_init_python': ['initialize python', 'setup python project', 'create python project', 'new python project'],
            'project_init_csharp': ['initialize c#', 'initialize csharp', 'setup c# project', 'setup csharp project', 'create c# project', 'new .net project'],
            'project_init_cpp': ['initialize c++', 'initialize cpp', 'setup c++ project', 'create c++ project', 'new c++ project'],
            'project_init_webdev': ['initialize web', 'setup web project', 'create web app', 'new react', 'new vue', 'new angular', 'initialize javascript', 'initialize typescript'],
            'project_init_bash': ['initialize bash', 'setup bash project', 'create shell project', 'new bash script'],
            'project_init_powershell': ['initialize powershell', 'setup powershell project', 'create powershell script'],
            'project_init': ['initialize project', 'setup project', 'create project', 'new project', 'scaffold'],
            
            # Code Planning
            'code_planner': ['plan code', 'design architecture', 'plan implementation', 'design system', 'architecture', 'plan feature'],
            
            # Code Editing (Language-specific)
            'code_editor_python': ['write python', 'edit python', 'python code', 'implement python', 'modify python file'],
            'code_editor_csharp': ['write c#', 'write csharp', 'edit c#', 'c# code', 'implement c#', '.net code'],
            'code_editor_cpp': ['write c++', 'write cpp', 'edit c++', 'c++ code', 'implement c++'],
            'code_editor_webdev': ['write javascript', 'write typescript', 'write react', 'write html', 'write css', 'web code', 'frontend code'],
            'code_editor_shell': ['write bash', 'write shell', 'shell script', 'bash script', 'shell code'],
            'code_editor_powershell': ['write powershell', 'powershell script', 'ps1 code'],
            'code_editor_batch': ['write batch', 'batch script', 'cmd script'],
            'code_editor': ['write code', 'implement', 'create file', 'edit', 'modify code', 'code generation'],
            
            # Code Analysis
            'code_analyzer': ['analyze code', 'code analysis', 'check code quality', 'code review', 'static analysis', 'complexity analysis'],
            
            # Debugging (Language-specific)
            'python_debug': ['debug python', 'fix python error', 'python bug', 'troubleshoot python'],
            'csharp_debug': ['debug c#', 'debug csharp', 'fix c# error', 'c# bug', 'troubleshoot c#'],
            'cpp_debug': ['debug c++', 'debug cpp', 'fix c++ error', 'c++ bug', 'memory leak'],
            'webdev_debug': ['debug javascript', 'debug typescript', 'debug web', 'fix frontend error', 'browser error'],
            'shell_debug': ['debug bash', 'debug shell', 'fix shell error', 'shell bug'],
            'powershell_debug': ['debug powershell', 'fix powershell error', 'powershell bug'],
            'batch_debug': ['debug batch', 'fix batch error', 'cmd error'],
            
            # Testing (Language-specific)
            'python_test': ['test python', 'python tests', 'pytest', 'python unittest', 'write python tests'],
            'csharp_test': ['test c#', 'c# tests', 'xunit', 'nunit', 'write c# tests'],
            'cpp_test': ['test c++', 'c++ tests', 'gtest', 'write c++ tests'],
            'webdev_test': ['test javascript', 'test typescript', 'jest', 'mocha', 'write web tests'],
            'code_tester': ['test code', 'write tests', 'unit test', 'integration test', 'testing'],
            
            # Building (Language-specific)
            'python_build': ['build python', 'package python', 'python setup', 'pip package'],
            'csharp_build': ['build c#', 'compile c#', 'dotnet build', 'msbuild'],
            'cpp_build': ['build c++', 'compile c++', 'cmake', 'make'],
            'webdev_build': ['build web', 'webpack', 'vite', 'npm build', 'yarn build'],
            'shell_build': ['build shell', 'package shell'],
            'powershell_build': ['build powershell', 'package powershell'],
            
            # Documentation
            'documentation_generator': ['generate docs', 'create documentation', 'document code', 'api docs', 'write documentation'],
            'documentation_writer': ['write docs', 'documentation', 'readme', 'user guide'],
            
            # Version Control
            'git_agent': ['git', 'commit', 'push', 'pull', 'version control', 'git operation'],
            
            # Other specialized agents
            'web_search': ['search', 'find information', 'lookup', 'research', 'google'],
            'database': ['database', 'query', 'sql', 'data storage', 'mongodb', 'postgres'],
            'data_analysis': ['analyze data', 'data analysis', 'pandas', 'statistics', 'visualization'],
            'api_agent': ['api', 'http', 'rest', 'endpoint', 'api call', 'fetch data'],
            'cybersecurity': ['security', 'vulnerability', 'penetration test', 'security audit'],
        }
        
        # Detect language from specifications
        detected_language = self._detect_language_from_specs(specifications)
        
        for task in task_structure.get('tasks', []):
            task_id = task.get('id', '')
            task_desc = task.get('description', '').lower()
            
            # Find best matching agent
            best_agent = self._find_best_agent(task_desc, agent_rules, detected_language)
            assignments[task_id] = best_agent
            
            # Assign agents for subtasks
            for subtask in task.get('subtasks', []):
                subtask_id = subtask.get('id', '')
                subtask_desc = subtask.get('description', '').lower()
                
                best_subtask_agent = self._find_best_agent(subtask_desc, agent_rules, detected_language)
                assignments[subtask_id] = best_subtask_agent
        
        logger.info(f"Assigned {len(assignments)} tasks to agents")
        return assignments
    
    def _detect_language_from_specs(self, specifications: Dict[str, Any]) -> Optional[str]:
        """
        Detect programming language from specifications.
        
        Args:
            specifications: Extracted specifications
            
        Returns:
            Detected language or None
        """
        # Check tech stack
        tech_stack = specifications.get('tech_stack', {})
        if tech_stack.get('language'):
            return tech_stack['language'].lower()
        
        # Check from goals and constraints
        text = ' '.join(specifications.get('goals', []) + specifications.get('constraints', []))
        text = text.lower()
        
        language_keywords = {
            'python': ['python', 'django', 'flask', 'fastapi', 'pytest'],
            'csharp': ['c#', 'csharp', '.net', 'dotnet', 'asp.net'],
            'cpp': ['c++', 'cpp'],
            'javascript': ['javascript', 'js', 'node.js', 'nodejs'],
            'typescript': ['typescript', 'ts'],
            'bash': ['bash', 'shell'],
            'powershell': ['powershell', 'ps1'],
        }
        
        for lang, keywords in language_keywords.items():
            if any(keyword in text for keyword in keywords):
                return lang
        
        return None
    
    def _find_best_agent(
        self,
        task_desc: str,
        agent_rules: Dict[str, List[str]],
        detected_language: Optional[str]
    ) -> str:
        """
        Find the best matching agent for a task description.
        
        Args:
            task_desc: Task description (lowercase)
            agent_rules: Agent selection rules
            detected_language: Detected programming language
            
        Returns:
            Agent name
        """
        best_agent = 'code_editor'  # Default
        max_matches = 0
        
        for agent_name, keywords in agent_rules.items():
            matches = sum(1 for keyword in keywords if keyword in task_desc)
            if matches > max_matches:
                max_matches = matches
                best_agent = agent_name
        
        # If we detected a language, prefer language-specific agents
        if detected_language and max_matches > 0:
            # Map generic agent to language-specific version
            if best_agent == 'code_editor':
                lang_map = {
                    'python': 'code_editor_python',
                    'csharp': 'code_editor_csharp',
                    'cpp': 'code_editor_cpp',
                    'javascript': 'code_editor_webdev',
                    'typescript': 'code_editor_webdev',
                    'bash': 'code_editor_shell',
                    'powershell': 'code_editor_powershell',
                }
                best_agent = lang_map.get(detected_language, 'code_editor')
            elif best_agent == 'project_init':
                lang_map = {
                    'python': 'project_init_python',
                    'csharp': 'project_init_csharp',
                    'cpp': 'project_init_cpp',
                    'javascript': 'project_init_webdev',
                    'typescript': 'project_init_webdev',
                    'bash': 'project_init_bash',
                    'powershell': 'project_init_powershell',
                }
                best_agent = lang_map.get(detected_language, 'project_init')
        
        return best_agent
    
    def _enhance_task_prompts(
        self,
        task_structure: Dict[str, Any],
        agent_assignments: Dict[str, str],
        specifications: Dict[str, Any],
        workflow_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Enhance prompts for each task while preserving user intent.
        
        Args:
            task_structure: Task structure
            agent_assignments: Agent assignments
            specifications: Specifications
            workflow_context: Workflow context
            
        Returns:
            List of enhanced tasks
        """
        enhanced_tasks = []
        
        # Build context summary
        context_summary = self._build_context_summary(workflow_context)
        
        # Build specification summary
        spec_summary = self._build_spec_summary(specifications)
        
        for task in task_structure.get('tasks', []):
            task_id = task.get('id', '')
            agent_name = agent_assignments.get(task_id, 'code_editor')
            
            # Create enhanced prompt
            enhanced_prompt = self._create_enhanced_prompt(
                task=task,
                agent_name=agent_name,
                spec_summary=spec_summary,
                context_summary=context_summary
            )
            
            enhanced_task = {
                'id': task_id,
                'description': task.get('description', ''),
                'agent': agent_name,
                'enhanced_prompt': enhanced_prompt,
                'original_prompt': task.get('description', ''),
                'dependencies': task.get('dependencies', []),
                'priority': task.get('priority', 5),
                'subtasks': []
            }
            
            # Process subtasks
            for subtask in task.get('subtasks', []):
                subtask_id = subtask.get('id', '')
                subtask_agent = agent_assignments.get(subtask_id, 'code_editor')
                
                enhanced_subtask_prompt = self._create_enhanced_prompt(
                    task=subtask,
                    agent_name=subtask_agent,
                    spec_summary=spec_summary,
                    context_summary=context_summary,
                    is_subtask=True
                )
                
                enhanced_task['subtasks'].append({
                    'id': subtask_id,
                    'description': subtask.get('description', ''),
                    'agent': subtask_agent,
                    'enhanced_prompt': enhanced_subtask_prompt,
                    'original_prompt': subtask.get('description', '')
                })
            
            enhanced_tasks.append(enhanced_task)
        
        return enhanced_tasks
    
    def _create_enhanced_prompt(
        self,
        task: Dict[str, Any],
        agent_name: str,
        spec_summary: str,
        context_summary: str,
        is_subtask: bool = False
    ) -> str:
        """
        Create an enhanced prompt for a task.
        
        Args:
            task: Task definition
            agent_name: Target agent name
            spec_summary: Specification summary
            context_summary: Context summary
            is_subtask: Whether this is a subtask
            
        Returns:
            Enhanced prompt string
        """
        task_type = "Subtask" if is_subtask else "Task"
        description = task.get('description', '')
        
        prompt_parts = [
            f"# {task_type}: {description}",
            "",
            "## Context and Specifications",
            spec_summary,
            "",
            "## Relevant Context",
            context_summary,
            "",
            "## Instructions",
            f"As the {agent_name} agent, complete the following:",
            description,
            "",
            "## Requirements",
            "- Follow all specifications and constraints",
            "- Maintain code quality and best practices",
            "- Provide clear outputs and error messages",
            "- Update relevant documentation",
        ]
        
        # Add task-specific requirements
        if task.get('expected_output'):
            prompt_parts.extend([
                "",
                "## Expected Output",
                task['expected_output']
            ])
        
        return "\n".join(prompt_parts)
    
    def _build_context_summary(self, workflow_context: Dict[str, Any]) -> str:
        """
        Build a context summary for prompts.
        
        Args:
            workflow_context: Workflow context
            
        Returns:
            Context summary string
        """
        parts = []
        
        if workflow_context.get('recent_messages'):
            parts.append("Recent conversation highlights:")
            for msg in workflow_context['recent_messages'][:3]:
                parts.append(f"- {msg.get('content', '')[:100]}")
        
        if workflow_context.get('relevant_files'):
            parts.append("\nRelevant files:")
            for file_ref in workflow_context['relevant_files'][:5]:
                parts.append(f"- {file_ref}")
        
        if workflow_context.get('similar_tasks'):
            parts.append("\nSimilar past tasks:")
            for task in workflow_context['similar_tasks'][:3]:
                parts.append(f"- {task.get('content', '')[:100]}")
        
        return "\n".join(parts) if parts else "No additional context available."
    
    def _build_spec_summary(self, specifications: Dict[str, Any]) -> str:
        """
        Build a specification summary.
        
        Args:
            specifications: Extracted specifications
            
        Returns:
            Specification summary string
        """
        parts = []
        
        if specifications.get('goals'):
            parts.append("**Goals:**")
            for goal in specifications['goals']:
                parts.append(f"- {goal}")
        
        if specifications.get('constraints'):
            parts.append("\n**Constraints:**")
            for constraint in specifications['constraints']:
                parts.append(f"- {constraint}")
        
        if specifications.get('preferences'):
            parts.append("\n**Preferences:**")
            for pref in specifications['preferences']:
                parts.append(f"- {pref}")
        
        return "\n".join(parts) if parts else "No specific constraints or preferences."
    
    def _execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow by coordinating agent execution.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Execution results
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return {'success': False, 'error': 'Workflow not found'}
        
        results = {
            'completed': 0,
            'failed': 0,
            'task_results': []
        }
        
        enhanced_tasks = workflow['enhanced_tasks']
        
        # For now, return execution plan
        # In a full implementation, this would:
        # 1. Resolve task dependencies
        # 2. Execute tasks in order
        # 3. Pass context between tasks
        # 4. Handle errors and retries
        # 5. Store results in vector memory
        
        for task in enhanced_tasks:
            task_result = {
                'task_id': task['id'],
                'agent': task['agent'],
                'status': 'planned',
                'prompt': task['enhanced_prompt']
            }
            results['task_results'].append(task_result)
        
        workflow['status'] = 'execution_planned'
        
        logger.info(f"Workflow {workflow_id[:8]} execution plan created")
        
        return results
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Workflow status dictionary
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return {'error': 'Workflow not found'}
        
        return {
            'workflow_id': workflow_id,
            'status': workflow['status'],
            'progress': workflow['progress'],
            'created_at': workflow['created_at']
        }
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return [
            'task_decomposition',
            'specification_extraction',
            'agent_selection',
            'prompt_enhancement',
            'context_management',
            'workflow_coordination',
            'progress_tracking'
        ]
