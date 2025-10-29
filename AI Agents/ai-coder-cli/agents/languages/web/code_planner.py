"""
Web (JS/TS)-Specific Code Planning Agent

This agent specializes in planning Web (JS/TS) projects.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from ...base import CodePlannerBase


class WebJSTSCodePlannerAgent(CodePlannerBase):
    """
    Agent specialized for Web (JS/TS) project planning.
    
    Features:
    - Web (JS/TS)-specific project structure
    - Framework recommendations
    - Best practices awareness
    """
    
    def __init__(
        self,
        name: str = "code_planner_web",
        description: str = "Web (JS/TS)-specific code planning agent",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            primary_language="Web (JS/TS)",
            **kwargs
        )
    
    def _get_language_specific_context(self, context: Dict[str, Any]) -> str:
        """Get Web (JS/TS)-specific context for planning."""
        return """
## Web (JS/TS)-Specific Context

Follow Web (JS/TS) best practices:
- Use appropriate project structure
- Follow language conventions
- Include necessary configuration files
- Set up testing framework: Jest
- Include package.json for dependencies

Supported file extensions: .js, .ts, .jsx, .tsx
"""
    
    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Web (JS/TS)-specific plan requirements."""
        errors = []
        warnings = []
        
        file_paths = [f['path'] for f in plan.get('files', [])]
        
        # Check for language-specific files
        if "package.json" not in file_paths:
            warnings.append("Missing package.json file")
        
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
        """Enhance plan with Web (JS/TS)-specific details."""
        file_paths = [f['path'] for f in plan.get('files', [])]
        
        # Add language-specific files if not present
        if "package.json" not in file_paths:
            plan.setdefault("files", []).append({{
                "path": "package.json",
                "purpose": "Project dependencies and configuration",
                "priority": "high"
            }})
        
        # Add testing recommendations
        if 'testing' not in plan:
            plan['testing'] = {
                'framework': 'Jest',
                'structure': 'tests/ directory',
            }
        
        return plan
    
    def _get_language_directory(self) -> Optional[Path]:
        """Get the Web (JS/TS) language directory."""
        return Path(__file__).parent
