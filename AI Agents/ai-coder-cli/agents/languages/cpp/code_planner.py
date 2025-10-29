"""
CPP-Specific Code Planning Agent

This agent specializes in planning CPP projects.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from ...base import CodePlannerBase


class CPPCodePlannerAgent(CodePlannerBase):
    """
    Agent specialized for CPP project planning.
    
    Features:
    - CPP-specific project structure
    - Framework recommendations
    - Best practices awareness
    """
    
    def __init__(
        self,
        name: str = "code_planner_cpp",
        description: str = "CPP-specific code planning agent",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            primary_language="CPP",
            **kwargs
        )
    
    def _get_language_specific_context(self, context: Dict[str, Any]) -> str:
        """Get CPP-specific context for planning."""
        return """
## CPP-Specific Context

Follow CPP best practices:
- Use appropriate project structure
- Follow language conventions
- Include necessary configuration files
- Set up testing framework: Google Test
- Include CMakeLists.txt for dependencies

Supported file extensions: .cpp, .cc, .cxx, .h, .hpp
"""
    
    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate CPP-specific plan requirements."""
        errors = []
        warnings = []
        
        file_paths = [f['path'] for f in plan.get('files', [])]
        
        # Check for language-specific files
        if "CMakeLists.txt" not in file_paths:
            warnings.append("Missing CMakeLists.txt file")
        
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
        """Enhance plan with CPP-specific details."""
        file_paths = [f['path'] for f in plan.get('files', [])]
        
        # Add language-specific files if not present
        if "CMakeLists.txt" not in file_paths:
            plan.setdefault("files", []).append({{
                "path": "CMakeLists.txt",
                "purpose": "Project dependencies and configuration",
                "priority": "high"
            }})
        
        # Add testing recommendations
        if 'testing' not in plan:
            plan['testing'] = {
                'framework': 'Google Test',
                'structure': 'tests/ directory',
            }
        
        return plan
    
    def _get_language_directory(self) -> Optional[Path]:
        """Get the CPP language directory."""
        return Path(__file__).parent
