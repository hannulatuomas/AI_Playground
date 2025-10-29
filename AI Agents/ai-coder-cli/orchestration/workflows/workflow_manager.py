"""
Workflow Manager

Manages workflow discovery, selection, and execution.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml

from .base_workflow import BaseWorkflow, WorkflowStep


logger = logging.getLogger(__name__)


class WorkflowManager:
    """
    Manages workflows for the AI Agent Console.
    
    Responsibilities:
    - Load workflow definitions from YAML files
    - Auto-select appropriate workflows based on task type
    - Prompt user when workflow selection is ambiguous
    - Execute workflows by coordinating with agents
    - Track workflow execution progress
    """
    
    def __init__(
        self,
        workflows_dir: Optional[Path] = None,
        agent_registry: Optional[Any] = None,
        llm_router: Optional[Any] = None
    ):
        """
        Initialize the workflow manager.
        
        Args:
            workflows_dir: Directory containing workflow YAML files
            agent_registry: Agent registry for workflow execution
            llm_router: LLM router for intelligent workflow selection
        """
        self.workflows_dir = workflows_dir or Path(__file__).parent / "definitions"
        self.agent_registry = agent_registry
        self.llm_router = llm_router
        
        # Workflow storage
        self.workflows: Dict[str, BaseWorkflow] = {}
        self.active_workflows: Dict[str, BaseWorkflow] = {}
        
        # Load workflows from directory
        self._load_workflows()
        
        logger.info(f"WorkflowManager initialized with {len(self.workflows)} workflows")
    
    def _load_workflows(self):
        """Load all workflow definitions from the workflows directory."""
        if not self.workflows_dir.exists():
            logger.warning(f"Workflows directory does not exist: {self.workflows_dir}")
            self.workflows_dir.mkdir(parents=True, exist_ok=True)
            return
        
        yaml_files = list(self.workflows_dir.glob("*.yaml")) + list(self.workflows_dir.glob("*.yml"))
        
        for yaml_file in yaml_files:
            try:
                workflow = BaseWorkflow.from_yaml(yaml_file)
                self.workflows[workflow.workflow_id] = workflow
                logger.info(f"Loaded workflow: {workflow.name} (ID: {workflow.workflow_id})")
            except Exception as e:
                logger.error(f"Failed to load workflow from {yaml_file}: {e}")
    
    def get_workflow(self, workflow_id: str) -> Optional[BaseWorkflow]:
        """
        Get a workflow by ID.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Workflow instance or None
        """
        return self.workflows.get(workflow_id)
    
    def list_workflows(self, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List available workflows.
        
        Args:
            tags: Optional tags to filter by
            
        Returns:
            List of workflow metadata
        """
        workflows = []
        
        for workflow in self.workflows.values():
            # Filter by tags if specified
            if tags and not any(tag in workflow.tags for tag in tags):
                continue
            
            workflows.append({
                'workflow_id': workflow.workflow_id,
                'name': workflow.name,
                'description': workflow.description,
                'version': workflow.version,
                'tags': workflow.tags,
                'num_steps': len(workflow.steps)
            })
        
        return workflows
    
    def select_workflow(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Automatically select the most appropriate workflow for a task.
        
        Uses keyword matching and LLM-based selection to find the best workflow.
        
        Args:
            task_description: Description of the task
            context: Optional context information
            
        Returns:
            Workflow ID or None if no suitable workflow found
        """
        task_lower = task_description.lower()
        
        # Keyword-based matching
        workflow_keywords = {
            'new_project_workflow': [
                'new project', 'initialize project', 'create project',
                'start project', 'setup project', 'scaffold'
            ],
            'new_feature_workflow': [
                'new feature', 'add feature', 'implement feature',
                'feature implementation', 'create feature'
            ],
            'refactor_workflow': [
                'refactor', 'refactoring', 'restructure', 'improve code',
                'clean up code', 'code improvement'
            ],
            'extend_project_workflow': [
                'extend', 'add to project', 'enhance project',
                'expand project', 'add capability'
            ],
            'debug_workflow': [
                'debug', 'fix bug', 'troubleshoot', 'error',
                'issue', 'problem', 'not working'
            ],
            'test_workflow': [
                'test', 'testing', 'write tests', 'unit test',
                'integration test', 'test coverage'
            ],
            'analyze_workflow': [
                'analyze', 'analysis', 'code analysis', 'review',
                'inspect', 'check quality'
            ],
            'build_workflow': [
                'build', 'compile', 'package', 'deploy',
                'distribution', 'release'
            ]
        }
        
        # Score each workflow
        workflow_scores = {}
        
        for workflow_id, keywords in workflow_keywords.items():
            score = sum(1 for keyword in keywords if keyword in task_lower)
            if score > 0:
                workflow_scores[workflow_id] = score
        
        # If no matches, try LLM-based selection
        if not workflow_scores and self.llm_router:
            workflow_id = self._llm_select_workflow(task_description, context)
            if workflow_id:
                return workflow_id
        
        # If multiple matches with same score, return None (ambiguous)
        if len(workflow_scores) > 1:
            max_score = max(workflow_scores.values())
            top_workflows = [wf for wf, score in workflow_scores.items() if score == max_score]
            
            if len(top_workflows) > 1:
                logger.info(f"Ambiguous workflow selection: {top_workflows}")
                return None  # Let user choose
        
        # Return highest scoring workflow
        if workflow_scores:
            return max(workflow_scores.items(), key=lambda x: x[1])[0]
        
        return None
    
    def _llm_select_workflow(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Use LLM to select the most appropriate workflow.
        
        Args:
            task_description: Task description
            context: Optional context
            
        Returns:
            Workflow ID or None
        """
        workflows_info = self.list_workflows()
        workflows_desc = "\n".join([
            f"- {wf['workflow_id']}: {wf['description']}"
            for wf in workflows_info
        ])
        
        prompt = f"""Given the following task and available workflows, select the most appropriate workflow.

Task: {task_description}

Available Workflows:
{workflows_desc}

Respond with ONLY the workflow_id of the best match, or "NONE" if no workflow is appropriate.
"""
        
        try:
            response = self.llm_router.query(
                prompt=prompt,
                temperature=0.2,
                agent_name='workflow_manager'
            )
            
            result = response.get('response', '').strip()
            
            # Validate the response
            if result in self.workflows:
                return result
            
            # Check if it's one of our workflow IDs (case-insensitive)
            for wf_id in self.workflows:
                if result.lower() == wf_id.lower():
                    return wf_id
            
        except Exception as e:
            logger.error(f"LLM workflow selection failed: {e}")
        
        return None
    
    def prompt_user_for_workflow(
        self,
        task_description: str,
        candidates: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Prompt user to select a workflow when automatic selection is ambiguous.
        
        Args:
            task_description: Task description
            candidates: Optional list of candidate workflow IDs
            
        Returns:
            Selected workflow ID or None
        """
        if candidates:
            workflows = [self.workflows[wf_id] for wf_id in candidates if wf_id in self.workflows]
        else:
            workflows = list(self.workflows.values())
        
        if not workflows:
            return None
        
        print(f"\nMultiple workflows could handle this task: '{task_description}'")
        print("\nAvailable workflows:")
        
        for i, workflow in enumerate(workflows, 1):
            print(f"  {i}. {workflow.name}")
            print(f"     {workflow.description}")
            print(f"     Steps: {len(workflow.steps)}")
            print()
        
        print(f"  {len(workflows) + 1}. None - proceed without a workflow")
        print()
        
        try:
            choice = input("Select a workflow (enter number): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(workflows):
                return workflows[choice_num - 1].workflow_id
            elif choice_num == len(workflows) + 1:
                return None
        except (ValueError, KeyboardInterrupt):
            pass
        
        return None
    
    async def execute_workflow(
        self,
        workflow_id: str,
        context: Optional[Dict[str, Any]] = None,
        auto_confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            workflow_id: ID of the workflow to execute
            context: Execution context
            auto_confirm: Whether to auto-confirm actions
            
        Returns:
            Execution results
        """
        workflow = self.get_workflow(workflow_id)
        
        if not workflow:
            return {
                'success': False,
                'error': f'Workflow not found: {workflow_id}'
            }
        
        # Initialize workflow context
        if context:
            workflow.context.update(context)
        
        # Mark workflow as active
        self.active_workflows[workflow_id] = workflow
        workflow.status = "running"
        workflow.started_at = datetime.now()
        
        logger.info(f"Starting workflow execution: {workflow.name}")
        
        results = {
            'workflow_id': workflow_id,
            'workflow_name': workflow.name,
            'started_at': workflow.started_at.isoformat(),
            'steps': []
        }
        
        try:
            # Execute workflow steps
            while not workflow.is_complete():
                ready_steps = workflow.get_ready_steps()
                
                if not ready_steps:
                    # No more steps ready, check if we're stuck
                    if not workflow.is_complete():
                        logger.error("Workflow stuck - no steps ready but workflow not complete")
                        break
                    break
                
                # Execute ready steps (could be parallelized in the future)
                for step in ready_steps:
                    step_result = await self._execute_step(step, workflow, auto_confirm)
                    results['steps'].append(step_result)
                    
                    # Update workflow context with step result
                    workflow.context[f'step_{step.step_id}_result'] = step_result
            
            # Mark workflow as complete
            workflow.status = "completed" if not workflow.has_failures() else "failed"
            workflow.completed_at = datetime.now()
            
            results['completed_at'] = workflow.completed_at.isoformat()
            results['status'] = workflow.status
            results['progress'] = workflow.get_progress()
            results['success'] = not workflow.has_failures()
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            workflow.status = "failed"
            results['success'] = False
            results['error'] = str(e)
        
        finally:
            # Remove from active workflows
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
        
        return results
    
    async def _execute_step(
        self,
        step: WorkflowStep,
        workflow: BaseWorkflow,
        auto_confirm: bool
    ) -> Dict[str, Any]:
        """
        Execute a single workflow step.
        
        Args:
            step: Workflow step to execute
            workflow: Parent workflow
            auto_confirm: Auto-confirm actions
            
        Returns:
            Step execution result
        """
        logger.info(f"Executing step: {step.name} (ID: {step.step_id})")
        step.mark_started()
        
        try:
            # Get the agent
            if not self.agent_registry:
                raise Exception("Agent registry not available")
            
            agent = self.agent_registry.get_agent(step.agent)
            
            if not agent:
                raise Exception(f"Agent not found: {step.agent}")
            
            # Prepare parameters with context
            params = step.params.copy()
            params['context'] = workflow.context
            params['auto_confirm'] = auto_confirm
            
            # Execute the agent action
            result = agent.execute(params)
            
            # Mark step as completed
            step.mark_completed(result)
            
            return {
                'step_id': step.step_id,
                'name': step.name,
                'status': 'completed',
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Step execution failed: {e}", exc_info=True)
            
            # Handle error based on step's error strategy
            if step.on_error == "continue":
                step.mark_completed({'error': str(e), 'continued': True})
                return {
                    'step_id': step.step_id,
                    'name': step.name,
                    'status': 'completed_with_error',
                    'error': str(e)
                }
            elif step.on_error == "retry":
                # TODO: Implement retry logic
                step.mark_failed(str(e))
                return {
                    'step_id': step.step_id,
                    'name': step.name,
                    'status': 'failed',
                    'error': str(e)
                }
            else:  # fail
                step.mark_failed(str(e))
                return {
                    'step_id': step.step_id,
                    'name': step.name,
                    'status': 'failed',
                    'error': str(e)
                }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow status or None
        """
        workflow = self.active_workflows.get(workflow_id) or self.workflows.get(workflow_id)
        
        if not workflow:
            return None
        
        return workflow.to_dict()


from datetime import datetime
