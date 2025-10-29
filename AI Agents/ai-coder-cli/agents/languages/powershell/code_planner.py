"""
PowerShell-Specific Code Planning Agent

This agent specializes in planning PowerShell projects.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from ...base import CodePlannerBase


class PowerShellCodePlannerAgent(CodePlannerBase):
    """
    Agent specialized for PowerShell project planning.
    
    Features:
    - PowerShell-specific project structure
    - Framework recommendations
    - Best practices awareness
    """
    
    def __init__(
        self,
        name: str = "code_planner_powershell",
        description: str = "PowerShell-specific code planning agent",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            primary_language="PowerShell",
            **kwargs
        )
    
    def _get_language_specific_context(self, context: Dict[str, Any]) -> str:
        """Get PowerShell-specific context for planning."""
        return """
## PowerShell-Specific Context

Follow PowerShell best practices:
- Use appropriate project structure
- Follow language conventions
- Include necessary configuration files
- Set up testing framework: Pester
- Include psd1 for dependencies

Supported file extensions: .ps1, .psm1
"""
    
    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate PowerShell-specific plan requirements."""
        errors = []
        warnings = []
        
        file_paths = [f['path'] for f in plan.get('files', [])]
        
        # Check for language-specific files
        if "psd1" not in file_paths:
            warnings.append("Missing psd1 file")
        
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
        """Enhance plan with PowerShell-specific details."""
        file_paths = [f['path'] for f in plan.get('files', [])]
        
        # Add language-specific files if not present
        if "psd1" not in file_paths:
            plan.setdefault("files", []).append({{
                "path": "psd1",
                "purpose": "Project dependencies and configuration",
                "priority": "high"
            }})
        
        # Add testing recommendations
        if 'testing' not in plan:
            plan['testing'] = {
                'framework': 'Pester',
                'structure': 'tests/ directory',
            }
        
        return plan
    
    def _get_language_directory(self) -> Optional[Path]:
        """Get the PowerShell language directory."""
        return Path(__file__).parent
