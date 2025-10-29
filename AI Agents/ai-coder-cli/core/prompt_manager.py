"""
Prompt Management System

This module provides a comprehensive prompt and snippet management system for the AI Agent Console.
It allows users to save, manage, and reuse prompts and snippets efficiently across different contexts.

Features:
- Save prompts and snippets with metadata (name, description, tags)
- Support for both Global (user-level) and Project-scoped storage
- CRUD operations for prompts/snippets
- Search and filter by tags, scope, or search terms
- Variable substitution in prompts (e.g., {{project_name}}, {{file_path}})
- Persist data to disk in JSON format
- Template management with versioning
- Import/export functionality

The PromptManager integrates with the project management system to provide
project-scoped prompts while also supporting global, user-level prompts.
"""

import logging
import json
import uuid
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class PromptScope(str, Enum):
    """Scope for prompts/snippets."""
    GLOBAL = "global"
    PROJECT = "project"


class PromptType(str, Enum):
    """Type of prompt/snippet."""
    PROMPT = "prompt"
    SNIPPET = "snippet"


@dataclass
class Prompt:
    """
    Represents a saved prompt or snippet with its metadata.
    
    Attributes:
        prompt_id: Unique identifier for the prompt
        name: Human-readable prompt name
        description: Prompt description
        content: The actual prompt/snippet content
        prompt_type: Type of prompt (PROMPT or SNIPPET)
        scope: Storage scope (GLOBAL or PROJECT)
        tags: List of tags for categorization
        variables: List of variable names used in the prompt (e.g., ['project_name', 'file_path'])
        created_at: Creation timestamp
        updated_at: Last update timestamp
        usage_count: Number of times this prompt has been used
        metadata: Additional custom metadata
    """
    prompt_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    content: str = ""
    prompt_type: PromptType = PromptType.PROMPT
    scope: PromptScope = PromptScope.GLOBAL
    tags: List[str] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization to extract variables from content."""
        if not self.variables and self.content:
            self.variables = self._extract_variables()
    
    def _extract_variables(self) -> List[str]:
        """Extract variable names from content using {{variable}} pattern."""
        pattern = r'\{\{(\w+)\}\}'
        matches = re.findall(pattern, self.content)
        return list(set(matches))  # Remove duplicates
    
    def substitute_variables(self, variables: Dict[str, str]) -> str:
        """
        Substitute variables in the prompt content.
        
        Args:
            variables: Dictionary mapping variable names to their values
            
        Returns:
            Content with variables substituted
            
        Raises:
            ValueError: If required variables are missing
        """
        missing_vars = set(self.variables) - set(variables.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")
        
        result = self.content
        for var_name, var_value in variables.items():
            result = result.replace(f"{{{{{var_name}}}}}", var_value)
        
        return result
    
    def increment_usage(self) -> None:
        """Increment the usage count."""
        self.usage_count += 1
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert prompt to dictionary for serialization."""
        return {
            'prompt_id': self.prompt_id,
            'name': self.name,
            'description': self.description,
            'content': self.content,
            'prompt_type': self.prompt_type.value,
            'scope': self.scope.value,
            'tags': self.tags,
            'variables': self.variables,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'usage_count': self.usage_count,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Prompt':
        """Create prompt from dictionary."""
        return cls(
            prompt_id=data['prompt_id'],
            name=data['name'],
            description=data.get('description', ''),
            content=data['content'],
            prompt_type=PromptType(data.get('prompt_type', 'prompt')),
            scope=PromptScope(data.get('scope', 'global')),
            tags=data.get('tags', []),
            variables=data.get('variables', []),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            usage_count=data.get('usage_count', 0),
            metadata=data.get('metadata', {})
        )
    
    def __repr__(self) -> str:
        """String representation of prompt."""
        return f"<Prompt id={self.prompt_id[:8]} name='{self.name}' type={self.prompt_type.value} scope={self.scope.value}>"


class PromptManager:
    """
    Manages prompts and snippets with support for global and project-scoped storage.
    
    Features:
    - CRUD operations for prompts/snippets
    - Global and project-scoped storage
    - Search and filtering
    - Variable substitution
    - Import/export functionality
    - Usage tracking
    """
    
    def __init__(
        self,
        global_storage_dir: Optional[Path] = None,
        project_storage_dir: Optional[Path] = None
    ):
        """
        Initialize the PromptManager.
        
        Args:
            global_storage_dir: Directory for global prompts (defaults to ~/.ai-agent-console/prompts/)
            project_storage_dir: Directory for project prompts (defaults to .project/prompts/ in current project)
        """
        # Set up global storage directory
        if global_storage_dir is None:
            home = Path.home()
            global_storage_dir = home / '.ai-agent-console' / 'prompts'
        
        self.global_storage_dir = Path(global_storage_dir)
        self.global_storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up project storage directory
        self.project_storage_dir = Path(project_storage_dir) if project_storage_dir else None
        if self.project_storage_dir:
            self.project_storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Global and project prompt storage files
        self.global_storage_file = self.global_storage_dir / 'prompts.json'
        
        # In-memory cache
        self._prompts: Dict[str, Prompt] = {}
        
        # Load existing prompts
        self._load_prompts()
        
        logger.info(f"PromptManager initialized with global storage: {self.global_storage_dir}")
        if self.project_storage_dir:
            logger.info(f"Project storage: {self.project_storage_dir}")
    
    def _load_prompts(self) -> None:
        """Load prompts from storage files."""
        # Load global prompts
        if self.global_storage_file.exists():
            try:
                with open(self.global_storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for prompt_data in data.get('prompts', []):
                        prompt = Prompt.from_dict(prompt_data)
                        self._prompts[prompt.prompt_id] = prompt
                logger.info(f"Loaded {len(data.get('prompts', []))} global prompts")
            except Exception as e:
                logger.error(f"Failed to load global prompts: {e}")
        
        # Load project prompts
        if self.project_storage_dir:
            project_storage_file = self.project_storage_dir / 'prompts.json'
            if project_storage_file.exists():
                try:
                    with open(project_storage_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for prompt_data in data.get('prompts', []):
                            prompt = Prompt.from_dict(prompt_data)
                            self._prompts[prompt.prompt_id] = prompt
                    logger.info(f"Loaded {len(data.get('prompts', []))} project prompts")
                except Exception as e:
                    logger.error(f"Failed to load project prompts: {e}")
    
    def _save_prompts(self, scope: Optional[PromptScope] = None) -> None:
        """
        Save prompts to storage files.
        
        Args:
            scope: If specified, only save prompts of this scope. Otherwise, save all.
        """
        # Save global prompts
        if scope is None or scope == PromptScope.GLOBAL:
            global_prompts = [
                p.to_dict() for p in self._prompts.values()
                if p.scope == PromptScope.GLOBAL
            ]
            data = {
                'version': '1.0',
                'updated_at': datetime.now().isoformat(),
                'prompts': global_prompts
            }
            try:
                with open(self.global_storage_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.debug(f"Saved {len(global_prompts)} global prompts")
            except Exception as e:
                logger.error(f"Failed to save global prompts: {e}")
        
        # Save project prompts
        if self.project_storage_dir and (scope is None or scope == PromptScope.PROJECT):
            project_prompts = [
                p.to_dict() for p in self._prompts.values()
                if p.scope == PromptScope.PROJECT
            ]
            data = {
                'version': '1.0',
                'updated_at': datetime.now().isoformat(),
                'prompts': project_prompts
            }
            project_storage_file = self.project_storage_dir / 'prompts.json'
            try:
                with open(project_storage_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.debug(f"Saved {len(project_prompts)} project prompts")
            except Exception as e:
                logger.error(f"Failed to save project prompts: {e}")
    
    def save_prompt(
        self,
        name: str,
        content: str,
        description: str = "",
        prompt_type: PromptType = PromptType.PROMPT,
        scope: PromptScope = PromptScope.GLOBAL,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Prompt:
        """
        Save a new prompt or snippet.
        
        Args:
            name: Name of the prompt
            content: The prompt/snippet content
            description: Description of the prompt
            prompt_type: Type of prompt (PROMPT or SNIPPET)
            scope: Storage scope (GLOBAL or PROJECT)
            tags: List of tags for categorization
            metadata: Additional custom metadata
            
        Returns:
            The created Prompt object
            
        Raises:
            ValueError: If name is empty or project scope is requested but no project is active
        """
        if not name:
            raise ValueError("Prompt name cannot be empty")
        
        if scope == PromptScope.PROJECT and self.project_storage_dir is None:
            raise ValueError("Cannot save project-scoped prompt: no active project")
        
        # Check if prompt with same name already exists in the same scope
        existing = self.get_prompt_by_name(name, scope)
        if existing:
            raise ValueError(f"Prompt with name '{name}' already exists in {scope.value} scope. Use update instead.")
        
        prompt = Prompt(
            name=name,
            description=description,
            content=content,
            prompt_type=prompt_type,
            scope=scope,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self._prompts[prompt.prompt_id] = prompt
        self._save_prompts(scope)
        
        logger.info(f"Saved {prompt_type.value} '{name}' with scope {scope.value}")
        return prompt
    
    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """
        Get a prompt by its ID.
        
        Args:
            prompt_id: The prompt ID
            
        Returns:
            The Prompt object or None if not found
        """
        return self._prompts.get(prompt_id)
    
    def get_prompt_by_name(self, name: str, scope: Optional[PromptScope] = None) -> Optional[Prompt]:
        """
        Get a prompt by its name.
        
        Args:
            name: The prompt name
            scope: If specified, only search in this scope
            
        Returns:
            The Prompt object or None if not found
        """
        for prompt in self._prompts.values():
            if prompt.name == name:
                if scope is None or prompt.scope == scope:
                    return prompt
        return None
    
    def list_prompts(
        self,
        scope: Optional[PromptScope] = None,
        prompt_type: Optional[PromptType] = None,
        tags: Optional[List[str]] = None,
        search_term: Optional[str] = None
    ) -> List[Prompt]:
        """
        List prompts with optional filtering.
        
        Args:
            scope: Filter by scope (GLOBAL or PROJECT)
            prompt_type: Filter by type (PROMPT or SNIPPET)
            tags: Filter by tags (prompts must have at least one matching tag)
            search_term: Search in name, description, or content
            
        Returns:
            List of matching Prompt objects
        """
        results = []
        
        for prompt in self._prompts.values():
            # Filter by scope
            if scope and prompt.scope != scope:
                continue
            
            # Filter by type
            if prompt_type and prompt.prompt_type != prompt_type:
                continue
            
            # Filter by tags
            if tags:
                if not any(tag in prompt.tags for tag in tags):
                    continue
            
            # Filter by search term
            if search_term:
                search_lower = search_term.lower()
                if not (
                    search_lower in prompt.name.lower() or
                    search_lower in prompt.description.lower() or
                    search_lower in prompt.content.lower()
                ):
                    continue
            
            results.append(prompt)
        
        # Sort by name
        results.sort(key=lambda p: p.name)
        
        return results
    
    def update_prompt(
        self,
        prompt_id: str,
        name: Optional[str] = None,
        content: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Prompt:
        """
        Update an existing prompt.
        
        Args:
            prompt_id: The prompt ID to update
            name: New name (optional)
            content: New content (optional)
            description: New description (optional)
            tags: New tags (optional)
            metadata: New metadata (optional)
            
        Returns:
            The updated Prompt object
            
        Raises:
            ValueError: If prompt not found
        """
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            raise ValueError(f"Prompt with ID '{prompt_id}' not found")
        
        # Update fields
        if name is not None:
            prompt.name = name
        if content is not None:
            prompt.content = content
            prompt.variables = prompt._extract_variables()
        if description is not None:
            prompt.description = description
        if tags is not None:
            prompt.tags = tags
        if metadata is not None:
            prompt.metadata = metadata
        
        prompt.updated_at = datetime.now()
        
        self._save_prompts(prompt.scope)
        logger.info(f"Updated prompt '{prompt.name}'")
        
        return prompt
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """
        Delete a prompt.
        
        Args:
            prompt_id: The prompt ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            return False
        
        scope = prompt.scope
        name = prompt.name
        
        del self._prompts[prompt_id]
        self._save_prompts(scope)
        
        logger.info(f"Deleted prompt '{name}'")
        return True
    
    def use_prompt(
        self,
        prompt_id: str,
        variables: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Use a prompt with optional variable substitution.
        
        Args:
            prompt_id: The prompt ID to use
            variables: Dictionary of variables to substitute
            
        Returns:
            The processed prompt content
            
        Raises:
            ValueError: If prompt not found or required variables are missing
        """
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            raise ValueError(f"Prompt with ID '{prompt_id}' not found")
        
        # Increment usage count
        prompt.increment_usage()
        self._save_prompts(prompt.scope)
        
        # Substitute variables if provided
        if variables and prompt.variables:
            return prompt.substitute_variables(variables)
        
        return prompt.content
    
    def export_prompts(
        self,
        output_file: Path,
        scope: Optional[PromptScope] = None,
        tags: Optional[List[str]] = None
    ) -> int:
        """
        Export prompts to a file.
        
        Args:
            output_file: Output file path
            scope: Filter by scope
            tags: Filter by tags
            
        Returns:
            Number of prompts exported
        """
        prompts = self.list_prompts(scope=scope, tags=tags)
        
        data = {
            'version': '1.0',
            'exported_at': datetime.now().isoformat(),
            'prompts': [p.to_dict() for p in prompts]
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Exported {len(prompts)} prompts to {output_file}")
            return len(prompts)
        except Exception as e:
            logger.error(f"Failed to export prompts: {e}")
            raise
    
    def import_prompts(
        self,
        input_file: Path,
        scope: Optional[PromptScope] = None,
        overwrite: bool = False
    ) -> int:
        """
        Import prompts from a file.
        
        Args:
            input_file: Input file path
            scope: Override scope for imported prompts
            overwrite: Whether to overwrite existing prompts with same name
            
        Returns:
            Number of prompts imported
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_count = 0
            for prompt_data in data.get('prompts', []):
                prompt = Prompt.from_dict(prompt_data)
                
                # Override scope if specified
                if scope:
                    prompt.scope = scope
                
                # Check if prompt already exists
                existing = self.get_prompt_by_name(prompt.name, prompt.scope)
                if existing:
                    if overwrite:
                        # Update existing prompt
                        self.update_prompt(
                            existing.prompt_id,
                            content=prompt.content,
                            description=prompt.description,
                            tags=prompt.tags,
                            metadata=prompt.metadata
                        )
                        imported_count += 1
                    else:
                        logger.warning(f"Skipping existing prompt: {prompt.name}")
                else:
                    # Generate new ID for imported prompt
                    prompt.prompt_id = str(uuid.uuid4())
                    self._prompts[prompt.prompt_id] = prompt
                    imported_count += 1
            
            if imported_count > 0:
                self._save_prompts()
            
            logger.info(f"Imported {imported_count} prompts from {input_file}")
            return imported_count
        except Exception as e:
            logger.error(f"Failed to import prompts: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored prompts.
        
        Returns:
            Dictionary with statistics
        """
        total = len(self._prompts)
        global_count = sum(1 for p in self._prompts.values() if p.scope == PromptScope.GLOBAL)
        project_count = sum(1 for p in self._prompts.values() if p.scope == PromptScope.PROJECT)
        prompt_count = sum(1 for p in self._prompts.values() if p.prompt_type == PromptType.PROMPT)
        snippet_count = sum(1 for p in self._prompts.values() if p.prompt_type == PromptType.SNIPPET)
        
        # Collect all tags
        all_tags = set()
        for p in self._prompts.values():
            all_tags.update(p.tags)
        
        # Find most used prompts
        most_used = sorted(self._prompts.values(), key=lambda p: p.usage_count, reverse=True)[:5]
        
        return {
            'total': total,
            'global': global_count,
            'project': project_count,
            'prompts': prompt_count,
            'snippets': snippet_count,
            'tags': sorted(list(all_tags)),
            'most_used': [
                {
                    'name': p.name,
                    'usage_count': p.usage_count,
                    'type': p.prompt_type.value
                }
                for p in most_used
            ]
        }


# Convenience function to create a PromptManager instance
def create_prompt_manager(
    project_dir: Optional[Path] = None
) -> PromptManager:
    """
    Create a PromptManager instance.
    
    Args:
        project_dir: Project directory (if working with a project)
        
    Returns:
        PromptManager instance
    """
    project_storage_dir = None
    if project_dir:
        project_storage_dir = Path(project_dir) / '.project' / 'prompts'
    
    return PromptManager(project_storage_dir=project_storage_dir)
