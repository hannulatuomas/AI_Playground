"""
Base class for all code planning agents.

This module defines the common interface and functionality for language-specific
code planning agents with project context awareness.
"""

import json
from abc import abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from .agent_base import Agent
from ..utils.codebase_awareness import CodebaseAwarenessMixin


class CodePlannerBase(Agent, CodebaseAwarenessMixin):
    """
    Abstract base class for code planning agents with project context awareness.
    
    Provides common functionality for:
    - Project requirement analysis
    - Technology stack recommendations
    - File structure generation
    - Implementation plan creation
    - Dependency identification
    - Project context awareness
    - Rules hierarchy (project > user > best practices)
    
    Subclasses must implement:
    - _get_language_specific_context: Provide language-specific planning context
    - _validate_plan: Validate generated plan for language-specific requirements
    - _enhance_plan_with_language_specifics: Add language-specific details to plan
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        primary_language: str,
        **kwargs
    ):
        """
        Initialize code planning agent with project context awareness.
        
        Args:
            name: Agent name
            description: Agent description
            primary_language: Primary programming language
            **kwargs: Additional arguments passed to Agent base class
        """
        super().__init__(name=name, description=description, **kwargs)
        self.primary_language = primary_language
        self.planning_preferences = {}
        
        # Initialize codebase awareness
        self.init_codebase_awareness()
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute code planning task with project context awareness.
        
        Args:
            task: Project description or requirements
            context: Execution context
            
        Returns:
            Result dictionary with success status and plan data
        """
        self._log_action("Starting code planning", task[:100])
        
        try:
            # Initialize project context awareness
            success, error = self.ensure_codebase_awareness_initialized(context)
            if not success and error:
                self.logger.warning(f"Project context initialization: {error}")
            
            # Load planning preferences
            self._load_planning_preferences()
            
            # Build planning prompt
            prompt = self._build_planning_prompt(task, context)
            
            # Get LLM response
            llm_result = self._get_llm_response(prompt, temperature=0.7)
            
            if not llm_result.get('success', True):
                return self._build_error_result(
                    "Failed to get LLM response for planning",
                    Exception(llm_result.get('error', 'Unknown error'))
                )
            
            response_text = llm_result.get('response', '')
            
            # Parse the plan
            plan = self._parse_plan(response_text)
            
            if not plan:
                return self._build_error_result(
                    "Failed to parse planning response",
                    Exception("Could not extract plan from LLM response")
                )
            
            # Validate plan
            validation_result = self._validate_plan(plan)
            if not validation_result['valid']:
                self.logger.warning(f"Plan validation issues: {validation_result['errors']}")
            
            # Enhance with language-specific details
            plan = self._enhance_plan_with_language_specifics(plan, context)
            
            # Add metadata
            plan['provider'] = llm_result.get('provider')
            plan['model'] = llm_result.get('model')
            plan['language'] = self.primary_language
            
            self._log_action("Planning complete", f"Generated plan with {len(plan.get('files', []))} files")
            
            return self._build_success_result(
                message=f"Project plan generated successfully with {len(plan.get('files', []))} files",
                data=plan,
                next_context={
                    'plan': plan,
                    'planner_used': True,
                    'primary_language': self.primary_language
                }
            )
            
        except Exception as e:
            self.logger.exception("Code planning failed")
            return self._build_error_result(f"Code planning failed: {str(e)}", e)
    
    def _build_planning_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """
        Build the LLM prompt for code planning.
        
        Args:
            task: Task description
            context: Execution context
            
        Returns:
            Formatted prompt string
        """
        # Get language-specific context
        lang_context = self._get_language_specific_context(context)
        
        prompt = f"""You are an expert software architect and project planner specializing in {self.primary_language}.

Task: {task}

Please analyze this task and create a detailed implementation plan. Your plan should include:

1. **Project Overview**: Brief description of what will be built
2. **Technology Stack**: Recommended languages, frameworks, and libraries
3. **File Structure**: List of files to create with their purposes
4. **Dependencies**: Required packages or tools
5. **Implementation Steps**: Step-by-step guide for implementation
6. **Best Practices**: Relevant coding standards and patterns

"""
        
        # Add language-specific context
        if lang_context:
            prompt += f"\n{lang_context}\n"
        
        # Add planning preferences
        if self.planning_preferences.get('language_specific'):
            prompt += f"\n## Planning Preferences:\n{self.planning_preferences['language_specific'][:500]}\n"
        
        # Add project context if available
        if self.codebase_structure:
            prompt += f"\n## Existing Project Context:\n"
            prompt += f"Root: {self.root_folder}\n"
            prompt += f"Structure: {str(self.codebase_structure)[:500]}\n"
        
        # Add context information if available
        if 'previous_plan' in context:
            prompt += f"\n\nPrevious plan context: {context['previous_plan']}"
        
        if 'requirements' in context:
            prompt += f"\n\nAdditional Requirements: {context['requirements']}"
        
        prompt += """

Format your response as JSON with this structure:
{
    "overview": "Project description",
    "tech_stack": {
        "language": "primary programming language",
        "frameworks": ["framework1", "framework2"],
        "libraries": ["lib1", "lib2"],
        "tools": ["tool1", "tool2"]
    },
    "files": [
        {
            "path": "relative/path/to/file.ext",
            "purpose": "What this file does",
            "priority": "high|medium|low",
            "dependencies": ["other_file.ext"]
        }
    ],
    "dependencies": [
        {
            "name": "package-name",
            "version": "1.0.0",
            "purpose": "Why we need this"
        }
    ],
    "steps": [
        "Step 1: Do something",
        "Step 2: Do something else"
    ],
    "best_practices": [
        "Practice 1: Description",
        "Practice 2: Description"
    ]
}

Respond with ONLY valid JSON, no additional text or markdown formatting.
"""
        
        return prompt
    
    def _parse_plan(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response to extract the plan.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed plan dictionary or empty dict if parsing fails
        """
        try:
            # Find JSON in response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                self.logger.warning("No JSON found in planning response")
                return {}
            
            json_text = response[json_start:json_end]
            plan = json.loads(json_text)
            
            # Validate plan structure
            required_keys = ['overview', 'tech_stack', 'files', 'steps']
            for key in required_keys:
                if key not in plan:
                    if key == 'files' or key == 'steps':
                        plan[key] = []
                    elif key == 'tech_stack':
                        plan[key] = {'language': self.primary_language}
                    else:
                        plan[key] = ''
            
            # Ensure optional keys exist
            if 'dependencies' not in plan:
                plan['dependencies'] = []
            if 'best_practices' not in plan:
                plan['best_practices'] = []
            
            return plan
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON from response: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error parsing plan: {e}")
            return {}
    
    def _load_planning_preferences(self) -> None:
        """Load planning preferences from language-specific files."""
        if not self.root_folder:
            return
        
        # Try to load planning_preferences.md from language directory
        language_dir = self._get_language_directory()
        if language_dir:
            prefs_file = language_dir / 'planning_preferences.md'
            if prefs_file.exists():
                try:
                    content = prefs_file.read_text(encoding='utf-8')
                    self.planning_preferences['language_specific'] = content
                    self.logger.info(f"Loaded planning preferences from {prefs_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to load planning preferences: {e}")
    
    def _get_language_directory(self) -> Optional[Path]:
        """Get the language-specific directory for this agent."""
        # Override in subclasses to provide language directory
        return None
    
    def ensure_codebase_awareness_initialized(
        self,
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Ensure codebase awareness is initialized.
        
        Args:
            context: Execution context that may contain file paths
            
        Returns:
            Tuple of (success, error_message)
        """
        if self.root_folder and self.codebase_structure:
            return True, None
        
        # Try to find root from context
        hint_path = context.get('working_dir') or context.get('project_path')
        
        # Find project root
        success, root, error = self.find_project_root(hint_path)
        if not success:
            return False, error
        
        # Load codebase structure
        success, structure, error = self.load_codebase_structure()
        if not success:
            # Warning only, not a critical error
            return True, error
        
        return True, None
    
    # Abstract methods to be implemented by subclasses
    
    @abstractmethod
    def _get_language_specific_context(self, context: Dict[str, Any]) -> str:
        """
        Get language-specific context for planning.
        
        Args:
            context: Execution context
            
        Returns:
            Language-specific context string
        """
        pass
    
    @abstractmethod
    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the generated plan for language-specific requirements.
        
        Args:
            plan: Generated plan dictionary
            
        Returns:
            Dictionary with 'valid' (bool) and 'errors' (list) keys
        """
        pass
    
    @abstractmethod
    def _enhance_plan_with_language_specifics(
        self,
        plan: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance plan with language-specific details.
        
        Args:
            plan: Generated plan dictionary
            context: Execution context
            
        Returns:
            Enhanced plan dictionary
        """
        pass
