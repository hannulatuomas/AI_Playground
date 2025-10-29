"""
Batch-Specific Code Planning Agent

This agent specializes in planning Batch projects.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from ...base import CodePlannerBase


class BatchCodePlannerAgent(CodePlannerBase):
    """
    Agent specialized for Batch project planning.
    
    Features:
    - Batch-specific project structure
    - Framework recommendations
    - Best practices awareness
    """
    
    def __init__(
        self,
        name: str = "code_planner_batch",
        description: str = "Batch-specific code planning agent",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            primary_language="Batch",
            **kwargs
        )
    
    def _get_language_specific_context(self, context: Dict[str, Any]) -> str:
        """Get Batch-specific context for planning."""
        return """
## Batch-Specific Context

Follow Batch best practices:
- Use appropriate project structure
- Follow language conventions
- Include necessary configuration files
- Set up testing framework: custom


Supported file extensions: .bat, .cmd
"""
    
    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Batch-specific plan requirements."""
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
        """Enhance plan with Batch-specific details."""
        file_paths = [f['path'] for f in plan.get('files', [])]
        
        # Add language-specific files if not present
        # No package file to add
        
        
        
        
        
        
        # Add testing recommendations
        if 'testing' not in plan:
            plan['testing'] = {
                'framework': 'custom',
                'structure': 'tests/ directory',
            }
        
        return plan
    
    def _get_language_directory(self) -> Optional[Path]:
        """Get the Batch language directory."""
        return Path(__file__).parent
