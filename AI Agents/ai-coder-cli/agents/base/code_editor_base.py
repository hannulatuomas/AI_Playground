

"""
Base class for all code editor agents.

This module defines the common interface and functionality for language-specific
code editor agents with project context awareness.
"""

import re
from abc import abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List

from .agent_base import Agent
from ..utils.codebase_awareness import CodebaseAwarenessMixin


class CodeEditorBase(Agent, CodebaseAwarenessMixin):
    """
    Abstract base class for code editor agents with project context awareness.
    
    Provides common functionality for:
    - File operations (create, modify, read)
    - Code generation using LLM with project context
    - Syntax validation
    - Code formatting
    - Language-specific extensions and patterns
    - Project root detection and context loading
    - Rules hierarchy awareness (project_preferences > user_preferences > best_practices)
    
    Subclasses must implement:
    - _generate_code_content: Generate language-specific code
    - _validate_syntax: Validate language-specific syntax
    - _apply_formatting: Apply language-specific formatting
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        supported_extensions: List[str],
        **kwargs
    ):
        """
        Initialize code editor agent with project context awareness.
        
        Args:
            name: Agent name
            description: Agent description
            supported_extensions: List of file extensions (e.g., ['.py', '.pyw'])
            **kwargs: Additional arguments passed to Agent base class
        """
        super().__init__(name=name, description=description, **kwargs)
        self.supported_extensions = supported_extensions
        
        # Initialize codebase awareness
        self.init_codebase_awareness()
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute code editing task with project context awareness.
        
        Args:
            task: Description of code editing task
            context: Execution context with optional 'file_path', 'content', 'plan'
            
        Returns:
            Result dictionary with success status and file details
        """
        self._log_action("Starting code editing", task[:100])
        
        try:
            # Initialize project context awareness
            success, error = self.ensure_codebase_awareness_initialized(context)
            if not success and error:
                self.logger.warning(f"Project context initialization: {error}")
            
            # Parse task to determine operation
            operation = self._parse_task(task, context)
            
            if not operation:
                return self._build_error_result("Could not parse code editing task")
            
            # Validate file extension
            if not self._is_supported_file(operation['path']):
                return self._build_error_result(
                    f"Unsupported file type for {self.name}: {operation['path']}"
                )
            
            # Generate or validate content
            if operation['action'] == 'create':
                result = self._create_file(operation, task, context)
            elif operation['action'] == 'modify':
                result = self._modify_file(operation, task, context)
            elif operation['action'] == 'read':
                result = self._read_file(operation)
            else:
                return self._build_error_result(f"Unknown action: {operation['action']}")
            
            return result
            
        except Exception as e:
            self.logger.exception("Code editing failed")
            return self._build_error_result(f"Code editing error: {str(e)}", e)
    
    def _parse_task(self, task: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse task to extract file operation details.
        
        This method checks context for explicit file information, or parses
        the task string to determine the action and file path.
        
        Args:
            task: Task description
            context: Execution context
            
        Returns:
            Operation dictionary with 'action', 'path', 'content', etc.
        """
        # Check context for explicit file information
        if 'file_path' in context:
            return {
                'action': context.get('action', 'create'),
                'path': context['file_path'],
                'content': context.get('content'),
            }
        
        # Extract from plan
        if 'plan' in context and 'files' in context['plan']:
            for file_info in context['plan']['files']:
                file_path = file_info.get('path', '')
                if self._is_supported_file(file_path):
                    return {
                        'action': 'create',
                        'path': file_path,
                        'content': None,
                        'purpose': file_info.get('purpose', '')
                    }
        
        # Parse from task string (basic pattern matching)
        # Look for action words and file paths
        action = 'create'
        if any(word in task.lower() for word in ['modify', 'edit', 'update', 'change']):
            action = 'modify'
        elif any(word in task.lower() for word in ['read', 'show', 'display']):
            action = 'read'
        
        # Try to extract file path
        for ext in self.supported_extensions:
            pattern = rf'([a-zA-Z0-9_/.\-]+{re.escape(ext)})'
            match = re.search(pattern, task)
            if match:
                return {
                    'action': action,
                    'path': match.group(1),
                    'content': None
                }
        
        return None
    
    def _is_supported_file(self, path: str) -> bool:
        """
        Check if path has a supported extension.
        
        Args:
            path: File path
            
        Returns:
            True if extension is supported
        """
        return Path(path).suffix in self.supported_extensions
    
    def _create_file(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new code file.
        
        Args:
            operation: Operation details from _parse_task
            task: Task description
            context: Execution context
            
        Returns:
            Result dictionary
        """
        try:
            # Generate content if not provided
            if not operation.get('content'):
                content = self._generate_code_content(operation, task, context)
            else:
                content = operation['content']
            
            # Validate syntax
            validation = self._validate_syntax(content)
            if not validation['valid']:
                self.logger.warning(f"Syntax warning: {validation['error']}")
                # Continue anyway, LLM might fix in next iteration
            
            # Apply formatting
            content = self._apply_formatting(content)
            
            # Write file
            file_path = Path(operation['path'])
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._log_action("Created file", str(file_path))
            
            return self._build_success_result(
                message=f"Created file: {file_path}",
                data={
                    'path': str(file_path),
                    'lines': len(content.splitlines()),
                    'size': len(content),
                    'syntax_valid': validation['valid']
                },
                next_context={
                    'last_created_file': str(file_path)
                }
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to create file: {str(e)}", e)
    
    def _modify_file(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Modify existing code file.
        
        Args:
            operation: Operation details
            task: Task description
            context: Execution context
            
        Returns:
            Result dictionary
        """
        try:
            file_path = Path(operation['path'])
            
            # Read existing content
            if not file_path.exists():
                return self._build_error_result(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Generate modification using LLM
            modified_content = self._generate_modification(
                original_content,
                task,
                context
            )
            
            # Validate syntax
            validation = self._validate_syntax(modified_content)
            if not validation['valid']:
                self.logger.warning(f"Modified code has syntax issues: {validation['error']}")
            
            # Apply formatting
            modified_content = self._apply_formatting(modified_content)
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            return self._build_success_result(
                message=f"Modified file: {file_path}",
                data={
                    'path': str(file_path),
                    'lines_before': len(original_content.splitlines()),
                    'lines_after': len(modified_content.splitlines()),
                    'syntax_valid': validation['valid']
                }
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to modify file: {str(e)}", e)
    
    def _read_file(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Read and return file content.
        
        Args:
            operation: Operation details
            
        Returns:
            Result dictionary with file content
        """
        try:
            file_path = Path(operation['path'])
            
            if not file_path.exists():
                return self._build_error_result(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self._build_success_result(
                message=f"Read file: {file_path}",
                data={
                    'path': str(file_path),
                    'content': content,
                    'lines': len(content.splitlines()),
                    'size': len(content)
                }
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to read file: {str(e)}", e)
    
    @abstractmethod
    def _generate_code_content(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate language-specific code content using LLM.
        
        Subclasses must implement this to generate code appropriate
        for their target language.
        
        Args:
            operation: Operation details
            task: Task description
            context: Execution context
            
        Returns:
            Generated code as string
        """
        pass
    
    def _generate_modification(
        self,
        original_content: str,
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate modified code content.
        
        This provides a default implementation that can be overridden
        by subclasses for language-specific modifications.
        
        Args:
            original_content: Original file content
            task: Task description
            context: Execution context
            
        Returns:
            Modified code as string
        """
        prompt = f"""Modify the following code according to the task.

Original Code:
```
{original_content}
```

Task: {task}

Requirements:
- Maintain existing functionality unless explicitly changed
- Keep the same code style
- Preserve comments and documentation unless changed

Generate the complete modified code (no markdown).
"""
        
        llm_result = self._get_llm_response(prompt, temperature=0.7)
        content = llm_result.get('response', '')
        
        return self._clean_code_blocks(content)
    
    @abstractmethod
    def _validate_syntax(self, code: str) -> Dict[str, Any]:
        """
        Validate language-specific syntax.
        
        Subclasses must implement language-specific syntax validation.
        
        Args:
            code: Code content to validate
            
        Returns:
            Dictionary with 'valid' boolean and optional 'error' message
        """
        pass
    
    @abstractmethod
    def _apply_formatting(self, code: str) -> str:
        """
        Apply language-specific formatting.
        
        Subclasses must implement language-specific code formatting.
        
        Args:
            code: Code content to format
            
        Returns:
            Formatted code
        """
        pass
    
    def _clean_code_blocks(self, content: str) -> str:
        """
        Remove markdown code blocks from LLM output.
        
        This is a common utility method for cleaning LLM responses.
        
        Args:
            content: LLM response content
            
        Returns:
            Cleaned code content
        """
        # Remove ```language\n...\n```
        pattern = r'```(?:\w+)?\n?(.*?)\n?```'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        return content.strip()
    
    def _get_enriched_prompt_context(
        self,
        base_prompt: str,
        include_codebase: bool = True,
        include_project_context: bool = True
    ) -> str:
        """
        Get enriched prompt context with project awareness.
        
        This method enhances the base prompt with:
        - Codebase structure context
        - Project goals and plan
        - Current tasks
        - Rules hierarchy (project_preferences > user_preferences > best_practices)
        
        Subclasses should call this method when building prompts for LLM.
        
        Args:
            base_prompt: Base prompt text
            include_codebase: Include codebase structure context
            include_project_context: Include project goals, plan, and tasks
            
        Returns:
            Enriched prompt with project context
        """
        enriched_prompt = base_prompt
        
        # Add codebase structure context
        if include_codebase and self.root_folder:
            codebase_context = self.get_codebase_context_for_prompt()
            if codebase_context:
                enriched_prompt = f"{codebase_context}\n\n---\n\n{enriched_prompt}"
        
        # Add project context (goals, plan, tasks)
        if include_project_context and self.root_folder:
            project_context = self.get_project_context_for_prompt(
                include_goals=True,
                include_plan=True,
                include_todo=True,
                include_preferences=True
            )
            if project_context:
                enriched_prompt = f"{project_context}\n---\n\n{enriched_prompt}"
        
        return enriched_prompt
