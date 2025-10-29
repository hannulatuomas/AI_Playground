"""
CSharp-Specific Code Planning Agent

This agent specializes in planning CSharp projects.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from ...base import CodePlannerBase


class CSharpCodePlannerAgent(CodePlannerBase):
    """
    Agent specialized for CSharp project planning.
    
    Features:
    - CSharp-specific project structure
    - Framework recommendations
    - Best practices awareness
    """
    
    def __init__(
        self,
        name: str = "code_planner_csharp",
        description: str = "CSharp-specific code planning agent",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            primary_language="CSharp",
            **kwargs
        )
    
    def _get_language_specific_context(self, context: Dict[str, Any]) -> str:
        """Get CSharp-specific context for planning."""
        return """
## CSharp-Specific Context

Follow CSharp best practices:
- Use appropriate project structure
- Follow language conventions
- Include necessary configuration files
- Set up testing framework: xUnit
- Include csproj for dependencies

Supported file extensions: .cs
"""
    
    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate CSharp-specific plan requirements."""
        errors = []
        warnings = []
        
        file_paths = [f['path'] for f in plan.get('files', [])]
        
        # Check for language-specific files
        if "csproj" not in file_paths:
            warnings.append("Missing csproj file")
        
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
        """Enhance plan with CSharp-specific details."""
        file_paths = [f['path'] for f in plan.get('files', [])]
        
        # Add language-specific files if not present
        if "csproj" not in file_paths:
            plan.setdefault("files", []).append({{
                "path": "csproj",
                "purpose": "Project dependencies and configuration",
                "priority": "high"
            }})
        
        # Add testing recommendations
        if 'testing' not in plan:
            plan['testing'] = {
                'framework': 'xUnit',
                'structure': 'tests/ directory',
            }
        
        return plan
    
    def _get_language_directory(self) -> Optional[Path]:
        """Get the CSharp language directory."""
        return Path(__file__).parent
