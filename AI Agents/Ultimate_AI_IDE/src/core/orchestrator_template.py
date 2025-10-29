"""
Orchestrator Template Validation Methods

Template validation methods for the UAIDE orchestrator.
"""

from typing import Dict, Any
from pathlib import Path
from ..utils.result import Result


def validate_template(self, project_path: str, strict: bool = False) -> Result:
    """
    Validate scaffolded project for bloat and incomplete code.
    
    Args:
        project_path: Path to project
        strict: Fail on any issues
        
    Returns:
        Result with validation findings
    """
    try:
        from ..modules.template_validator import TemplateValidator
        
        validator = TemplateValidator(project_path)
        result = validator.validate_project()
        score = validator.get_clean_score()
        
        # Emit event
        self.event_bus.emit('template_validated', {
            'project_path': project_path,
            'total_issues': result['total_issues'],
            'score': score,
            'is_clean': result['is_clean']
        })
        
        if strict and not result['is_clean']:
            return Result(
                success=False,
                message=f"Validation failed: {result['total_issues']} issues found",
                data={
                    'result': result,
                    'score': score
                }
            )
        
        return Result(
            success=True,
            message=f"Validation complete. Score: {score:.1f}/100",
            data={
                'result': result,
                'score': score,
                'issues': result['issues'],
                'summary': result['summary']
            }
        )
        
    except Exception as e:
        return Result(
            success=False,
            message=f"Template validation failed: {e}",
            errors=[str(e)]
        )


def get_template_score(self, project_path: str) -> Result:
    """
    Get cleanliness score for project.
    
    Args:
        project_path: Path to project
        
    Returns:
        Result with score
    """
    try:
        from ..modules.template_validator import TemplateValidator
        
        validator = TemplateValidator(project_path)
        result = validator.validate_project()
        score = validator.get_clean_score()
        
        return Result(
            success=True,
            message=f"Cleanliness score: {score:.1f}/100",
            data={
                'score': score,
                'total_issues': result['total_issues']
            }
        )
        
    except Exception as e:
        return Result(
            success=False,
            message=f"Score calculation failed: {e}",
            errors=[str(e)]
        )
