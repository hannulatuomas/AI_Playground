"""
Project Manager

Main interface for project management operations.
"""

from pathlib import Path
from typing import Optional, List, Dict
from .detector import ProjectDetector, ProjectInfo
from .scaffolder import ProjectScaffolder


class ProjectManager:
    """Manages project creation and maintenance."""
    
    def __init__(self, ai_backend=None, db_manager=None):
        """
        Initialize project manager.
        
        Args:
            ai_backend: AI backend for intelligent operations
            db_manager: Database manager for storing project info
        """
        self.detector = ProjectDetector()
        self.scaffolder = ProjectScaffolder()
        self.ai_backend = ai_backend
        self.db_manager = db_manager
    
    def create_project(self, name: str, language: str, 
                      framework: Optional[str] = None,
                      path: str = ".", git_init: bool = True) -> ProjectInfo:
        """
        Create a new project with scaffolding.
        
        Args:
            name: Project name
            language: Programming language
            framework: Framework (optional)
            path: Where to create project
            git_init: Initialize git repository
            
        Returns:
            ProjectInfo for the created project
            
        Raises:
            ValueError: If project already exists or invalid parameters
        """
        # Validate inputs
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")
        
        if not language:
            raise ValueError("Language must be specified")
        
        # Create the project
        success = self.scaffolder.create_project(
            name=name,
            language=language,
            framework=framework,
            path=path,
            git_init=git_init
        )
        
        if not success:
            raise RuntimeError("Failed to create project")
        
        # Detect and return project info
        project_path = Path(path) / name
        project_info = self.detector.detect_project(str(project_path))
        
        # Store in database if available
        if self.db_manager and project_info:
            self._store_project(project_info)
        
        return project_info
    
    def detect_project(self, path: str) -> Optional[ProjectInfo]:
        """
        Detect project information from a directory.
        
        Args:
            path: Path to project directory
            
        Returns:
            ProjectInfo if valid project detected, None otherwise
        """
        return self.detector.detect_project(path)
    
    def maintain_project(self, path: str) -> Dict[str, any]:
        """
        Analyze and maintain a project.
        
        Args:
            path: Path to project directory
            
        Returns:
            Maintenance report with suggestions and actions taken
        """
        project_info = self.detect_project(path)
        
        if not project_info:
            return {
                'success': False,
                'error': 'Not a valid project directory'
            }
        
        report = {
            'success': True,
            'project': project_info,
            'issues': [],
            'suggestions': [],
            'actions_taken': []
        }
        
        # Check for missing essential files
        issues = self._check_project_health(project_info)
        report['issues'].extend(issues)
        
        # Generate suggestions using AI if available
        if self.ai_backend and issues:
            suggestions = self._get_ai_suggestions(project_info, issues)
            report['suggestions'].extend(suggestions)
        
        return report
    
    def list_projects(self) -> List[ProjectInfo]:
        """
        List all projects stored in database.
        
        Returns:
            List of ProjectInfo objects
        """
        if not self.db_manager:
            return []
        
        # TODO: Implement database query
        return []
    
    def _check_project_health(self, project_info: ProjectInfo) -> List[str]:
        """Check project for common issues."""
        issues = []
        
        project_path = Path(project_info.path)
        
        # Check for README
        if not (project_path / 'README.md').exists():
            issues.append('Missing README.md')
        
        # Check for .gitignore
        if not (project_path / '.gitignore').exists():
            issues.append('Missing .gitignore')
        
        # Check for tests directory
        if not project_info.structure.get('has_tests', False):
            issues.append('No tests directory found')
        
        # Check for git repository
        if not project_info.structure.get('has_git', False):
            issues.append('Not a git repository')
        
        # Language-specific checks
        if project_info.language == 'python':
            if 'requirements.txt' not in project_info.config_files:
                if 'pyproject.toml' not in project_info.config_files:
                    issues.append('Missing requirements.txt or pyproject.toml')
        
        elif project_info.language in ['javascript', 'typescript']:
            if 'package.json' not in project_info.config_files:
                issues.append('Missing package.json')
        
        return issues
    
    def _get_ai_suggestions(self, project_info: ProjectInfo, 
                           issues: List[str]) -> List[str]:
        """Get AI-powered suggestions for project improvement."""
        if not self.ai_backend:
            return []
        
        # Prepare prompt for AI
        prompt = f"""Analyze this project and provide suggestions:

Project: {project_info.name}
Language: {project_info.language}
Framework: {project_info.framework or 'None'}
Issues found:
{chr(10).join(f'- {issue}' for issue in issues)}

Provide 3-5 specific, actionable suggestions to improve this project.
Focus on best practices, maintainability, and code quality.
"""
        
        try:
            response = self.ai_backend.query(prompt, max_tokens=500)
            # Parse response into list of suggestions
            suggestions = [s.strip() for s in response.split('\n') 
                          if s.strip() and not s.strip().startswith('#')]
            return suggestions[:5]  # Limit to 5 suggestions
        except Exception:
            return []
    
    def _store_project(self, project_info: ProjectInfo):
        """Store project information in database."""
        if not self.db_manager:
            return
        
        # TODO: Implement database storage
        pass
