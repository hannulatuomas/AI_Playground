"""
Prompt Manager

Manages and organizes reusable prompts.
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import json


@dataclass
class Prompt:
    """Reusable prompt template."""
    name: str
    template: str
    variables: List[str] = field(default_factory=list)
    category: str = "general"
    description: str = ""


class PromptManager:
    """Manages reusable prompts."""
    
    def __init__(self, prompts_file: str = "prompts.json"):
        """
        Initialize prompt manager.
        
        Args:
            prompts_file: File to store prompts
        """
        self.prompts_file = Path(prompts_file)
        self.prompts: Dict[str, Prompt] = {}
        self._load_prompts()
    
    def add_prompt(self, name: str, template: str, 
                  variables: Optional[List[str]] = None,
                  category: str = "general",
                  description: str = "") -> Prompt:
        """
        Add a new prompt.
        
        Args:
            name: Prompt name
            template: Prompt template with {variables}
            variables: List of variable names
            category: Prompt category
            description: Prompt description
            
        Returns:
            Created Prompt object
        """
        if variables is None:
            # Extract variables from template
            import re
            variables = re.findall(r'\{(\w+)\}', template)
        
        prompt = Prompt(
            name=name,
            template=template,
            variables=variables,
            category=category,
            description=description
        )
        
        self.prompts[name] = prompt
        self._save_prompts()
        
        return prompt
    
    def get_prompt(self, name: str, **kwargs) -> Optional[str]:
        """
        Get and render a prompt.
        
        Args:
            name: Prompt name
            **kwargs: Variable values
            
        Returns:
            Rendered prompt string
        """
        if name not in self.prompts:
            return None
        
        prompt = self.prompts[name]
        
        try:
            return prompt.template.format(**kwargs)
        except KeyError as e:
            print(f"Missing variable {e} for prompt {name}")
            return None
    
    def update_prompt(self, name: str, template: Optional[str] = None,
                     variables: Optional[List[str]] = None,
                     category: Optional[str] = None,
                     description: Optional[str] = None) -> bool:
        """
        Update an existing prompt.
        
        Args:
            name: Prompt name
            template: New template
            variables: New variables
            category: New category
            description: New description
            
        Returns:
            True if successful
        """
        if name not in self.prompts:
            return False
        
        prompt = self.prompts[name]
        
        if template is not None:
            prompt.template = template
        if variables is not None:
            prompt.variables = variables
        if category is not None:
            prompt.category = category
        if description is not None:
            prompt.description = description
        
        self._save_prompts()
        return True
    
    def delete_prompt(self, name: str) -> bool:
        """
        Delete a prompt.
        
        Args:
            name: Prompt name
            
        Returns:
            True if successful
        """
        if name in self.prompts:
            del self.prompts[name]
            self._save_prompts()
            return True
        return False
    
    def list_prompts(self, category: Optional[str] = None) -> List[Prompt]:
        """
        List all prompts, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of prompts
        """
        if category:
            return [p for p in self.prompts.values() if p.category == category]
        return list(self.prompts.values())
    
    def get_categories(self) -> List[str]:
        """Get list of all categories."""
        return list(set(p.category for p in self.prompts.values()))
    
    def _load_prompts(self):
        """Load prompts from file."""
        if not self.prompts_file.exists():
            return
        
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for name, prompt_data in data.items():
                prompt = Prompt(
                    name=name,
                    template=prompt_data['template'],
                    variables=prompt_data.get('variables', []),
                    category=prompt_data.get('category', 'general'),
                    description=prompt_data.get('description', '')
                )
                self.prompts[name] = prompt
                
        except Exception as e:
            print(f"Error loading prompts: {e}")
    
    def _save_prompts(self):
        """Save prompts to file."""
        data = {}
        
        for name, prompt in self.prompts.items():
            data[name] = {
                'template': prompt.template,
                'variables': prompt.variables,
                'category': prompt.category,
                'description': prompt.description
            }
        
        try:
            # Create directory if needed
            self.prompts_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving prompts: {e}")
