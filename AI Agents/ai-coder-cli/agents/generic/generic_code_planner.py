
"""
Generic Code Planning Agent

Fallback code planner for languages without specific implementations using LLM-based approaches.
"""

from typing import Dict, Any, List
from pathlib import Path

from ..base import CodePlannerBase


class GenericCodePlanner(CodePlannerBase):
    """
    Generic code planning agent for any language.
    
    This agent provides fallback functionality for languages that don't
    have specific planning implementations. It uses LLM with generic
    software architecture patterns.
    """
    
    def __init__(
        self,
        name: str = "code_planner_generic",
        description: str = "Generic code planner for any language",
        primary_language: str = "Generic",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            primary_language=primary_language,
            **kwargs
        )
    
    def _get_language_specific_context(self, context: Dict[str, Any]) -> str:
        """
        Get language-specific context for planning.
        
        For generic planner, we provide general software engineering context.
        """
        return """
## General Software Engineering Context

Apply industry-standard best practices:
- Follow SOLID principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion)
- Use design patterns where appropriate (Singleton, Factory, Observer, Strategy, etc.)
- Implement proper error handling and logging
- Write maintainable, readable, and well-documented code
- Consider scalability and performance from the start
- Separate concerns (e.g., UI, business logic, data access)
- Use version control-friendly structures
- Include README and documentation
- Plan for testing from the beginning

Consider the target language's:
- Standard library capabilities
- Common frameworks and tools
- Community best practices
- Package management system
- Testing frameworks
- Build tools and processes
"""
    
    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the generated plan for basic requirements.
        
        Checks for:
        - Required sections present
        - File paths are valid
        - Dependencies are specified
        - Implementation steps exist
        """
        errors = []
        warnings = []
        
        # Check required sections
        if not plan.get('overview'):
            errors.append("Missing project overview")
        
        if not plan.get('files') or len(plan['files']) == 0:
            errors.append("No files specified in plan")
        
        if not plan.get('steps') or len(plan['steps']) == 0:
            warnings.append("No implementation steps provided")
        
        # Validate file structure
        for file_info in plan.get('files', []):
            if not isinstance(file_info, dict):
                errors.append(f"Invalid file entry: {file_info}")
                continue
            
            if 'path' not in file_info:
                errors.append("File entry missing 'path' field")
            else:
                # Check for absolute paths (should be relative)
                path = file_info['path']
                if path.startswith('/') or (len(path) > 1 and path[1] == ':'):
                    warnings.append(f"File path should be relative: {path}")
            
            if 'purpose' not in file_info:
                warnings.append(f"File {file_info.get('path', 'unknown')} missing purpose description")
        
        # Validate tech stack
        tech_stack = plan.get('tech_stack', {})
        if not tech_stack.get('language'):
            warnings.append("Primary language not specified in tech stack")
        
        # Validate dependencies
        for dep in plan.get('dependencies', []):
            if not isinstance(dep, dict):
                warnings.append(f"Invalid dependency entry: {dep}")
                continue
            
            if 'name' not in dep:
                warnings.append("Dependency missing 'name' field")
        
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
        """
        Enhance plan with generic software engineering details.
        
        Adds:
        - Common project files (README, LICENSE, .gitignore)
        - Testing structure recommendations
        - Documentation suggestions
        """
        # Add common project files if not present
        common_files = {
            'README.md': 'Project documentation and getting started guide',
            'LICENSE': 'Project license file',
            '.gitignore': 'Git ignore patterns for the project',
            'CONTRIBUTING.md': 'Contribution guidelines',
        }
        
        existing_files = {f['path'] for f in plan.get('files', [])}
        
        for file_path, purpose in common_files.items():
            if file_path not in existing_files:
                plan.setdefault('files', []).append({
                    'path': file_path,
                    'purpose': purpose,
                    'priority': 'low'
                })
        
        # Add testing recommendations
        if 'testing' not in plan:
            plan['testing'] = {
                'framework': 'To be determined based on language',
                'structure': 'tests/ directory with unit and integration tests',
                'coverage_target': '80%'
            }
        
        # Add documentation recommendations
        if 'documentation' not in plan:
            plan['documentation'] = {
                'api_docs': 'Generated from code comments/docstrings',
                'user_guide': 'docs/ directory with user-facing documentation',
                'architecture': 'docs/architecture.md describing system design'
            }
        
        # Add best practices reminder
        if 'best_practices' not in plan or not plan['best_practices']:
            plan['best_practices'] = [
                'Follow SOLID principles',
                'Write clean, self-documenting code',
                'Include comprehensive error handling',
                'Add logging for debugging and monitoring',
                'Write tests alongside implementation',
                'Use version control effectively',
                'Document complex logic and design decisions'
            ]
        
        return plan

