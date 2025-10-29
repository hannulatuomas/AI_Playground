"""
Bash-Specific Code Planning Agent

This agent specializes in planning Bash projects.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from ...base import CodePlannerBase


class ShellCodePlannerAgent(CodePlannerBase):
    """
    Agent specialized for Bash project planning.
    
    Features:
    - Bash-specific project structure
    - Framework recommendations
    - Best practices awareness
    """
    
    def __init__(
        self,
        name: str = "code_planner_bash",
        description: str = "Bash-specific code planning agent",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            primary_language="Bash",
            **kwargs
        )
    
    def _get_language_specific_context(self, context: Dict[str, Any]) -> str:
        """Get Bash-specific context for planning."""
        return """
## Bash-Specific Context

Follow Bash best practices:
- Use appropriate project structure
- Follow language conventions
- Include necessary configuration files
- Set up testing framework: bats


Supported file extensions: .sh, .bash
"""
    
    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Bash-specific plan requirements."""
        errors = []
        warnings = []
        
        file_paths = [f['path'] for f in plan.get('files', [])]
        
        # Check for language-specific files
        # No package file check
        
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _enhance_plan_with_language_specifics(
        self,
        plan: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance plan with Bash-specific details."""
        file_paths = [f['path'] for f in plan.get('files', [])]
        
        # Add language-specific files if not present
        # No package file to add
        
        
        
        
        
        
        # Add testing recommendations
        if 'testing' not in plan:
            plan['testing'] = {
                'framework': 'bats',
                'structure': 'tests/ directory',
            }
        
        return plan
    
    def _get_language_directory(self) -> Optional[Path]:
        """Get the Bash language directory."""
        return Path(__file__).parent
