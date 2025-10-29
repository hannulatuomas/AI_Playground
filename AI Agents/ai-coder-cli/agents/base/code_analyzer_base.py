"""
Base class for all code analysis agents.

This module defines the common interface and functionality for language-specific
code analysis agents with project context awareness.
"""

import ast
import re
from abc import abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from .agent_base import Agent
from ..utils.codebase_awareness import CodebaseAwarenessMixin


class CodeAnalyzerBase(Agent, CodebaseAwarenessMixin):
    """
    Abstract base class for code analysis agents with project context awareness.
    
    Provides common functionality for:
    - Code quality analysis
    - Complexity metrics calculation
    - Security vulnerability scanning
    - Performance issue detection
    - Best practices adherence checking
    - Dependency analysis
    - Project context awareness
    - Rules hierarchy (project > user > best practices)
    
    Subclasses must implement:
    - _analyze_code_quality: Perform language-specific quality analysis
    - _calculate_complexity: Calculate complexity metrics
    - _check_security: Check for security issues
    - _analyze_performance: Analyze performance issues
    - _check_best_practices: Check adherence to best practices
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        primary_language: str,
        **kwargs
    ):
        """
        Initialize code analysis agent with project context awareness.
        
        Args:
            name: Agent name
            description: Agent description
            primary_language: Primary programming language
            **kwargs: Additional arguments passed to Agent base class
        """
        super().__init__(name=name, description=description, **kwargs)
        self.primary_language = primary_language
        self.analysis_preferences = {}
        
        # Initialize codebase awareness
        self.init_codebase_awareness()
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute code analysis task with project context awareness.
        
        Args:
            task: Description of analysis task
            context: Execution context with optional 'file_path', 'code', 'analysis_types'
            
        Returns:
            Result dictionary with success status and analysis results
        """
        self._log_action("Starting code analysis", task[:100])
        
        try:
            # Initialize project context awareness
            success, error = self.ensure_codebase_awareness_initialized(context)
            if not success and error:
                self.logger.warning(f"Project context initialization: {error}")
            
            # Load analysis preferences
            self._load_analysis_preferences()
            
            # Parse analysis request
            analysis_info = self._parse_analysis_request(task, context)
            
            if not analysis_info:
                return self._build_error_result("Could not determine what to analyze")
            
            # Perform analysis
            result = self._perform_analysis(analysis_info, context)
            
            return result
            
        except Exception as e:
            self.logger.exception("Code analysis failed")
            return self._build_error_result(f"Analysis error: {str(e)}", e)
    
    def _parse_analysis_request(self, task: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse analysis request from task and context.
        
        Args:
            task: Task description
            context: Execution context
            
        Returns:
            Dictionary with analysis information or None if parsing fails
        """
        analysis_info = {
            'file_path': context.get('file_path'),
            'code': context.get('code'),
            'analysis_types': context.get('analysis_types', ['all']),
            'working_dir': context.get('working_dir', self.root_folder or Path.cwd())
        }
        
        # Try to extract file path from task
        if not analysis_info['file_path']:
            # Look for file patterns
            pattern = r'([a-zA-Z0-9_/\\.-]+\.\w+)'
            match = re.search(pattern, task)
            if match:
                analysis_info['file_path'] = match.group(1)
        
        # Determine analysis types from task
        if 'analysis_types' not in context or context['analysis_types'] == ['all']:
            types = []
            if 'quality' in task.lower():
                types.append('quality')
            if 'complexity' in task.lower() or 'metric' in task.lower():
                types.append('complexity')
            if 'security' in task.lower() or 'vulnerab' in task.lower():
                types.append('security')
            if 'performance' in task.lower() or 'optim' in task.lower():
                types.append('performance')
            if 'best practice' in task.lower() or 'standard' in task.lower():
                types.append('best_practices')
            
            if types:
                analysis_info['analysis_types'] = types
            else:
                # Default to all if nothing specific mentioned
                analysis_info['analysis_types'] = ['quality', 'complexity', 'security', 'performance', 'best_practices']
        
        # Load code from file if not provided
        if not analysis_info['code'] and analysis_info['file_path']:
            try:
                file_path = Path(analysis_info['file_path'])
                if not file_path.is_absolute():
                    file_path = Path(analysis_info['working_dir']) / file_path
                
                if file_path.exists():
                    analysis_info['code'] = file_path.read_text(encoding='utf-8')
                else:
                    return None
            except Exception as e:
                self.logger.error(f"Failed to load code from file: {e}")
                return None
        
        return analysis_info if analysis_info['code'] else None
    
    def _perform_analysis(self, analysis_info: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform code analysis based on requested types.
        
        Args:
            analysis_info: Analysis information dictionary
            context: Execution context
            
        Returns:
            Result dictionary with analysis outcomes
        """
        code = analysis_info['code']
        analysis_types = analysis_info['analysis_types']
        
        results = {
            'file': analysis_info.get('file_path', 'inline code'),
            'language': self.primary_language,
            'analyses': {}
        }
        
        # Perform requested analyses
        if 'quality' in analysis_types:
            self._log_action("Analyzing code quality", "")
            results['analyses']['quality'] = self._analyze_code_quality(code, analysis_info)
        
        if 'complexity' in analysis_types:
            self._log_action("Calculating complexity", "")
            results['analyses']['complexity'] = self._calculate_complexity(code, analysis_info)
        
        if 'security' in analysis_types:
            self._log_action("Checking security", "")
            results['analyses']['security'] = self._check_security(code, analysis_info)
        
        if 'performance' in analysis_types:
            self._log_action("Analyzing performance", "")
            results['analyses']['performance'] = self._analyze_performance(code, analysis_info)
        
        if 'best_practices' in analysis_types:
            self._log_action("Checking best practices", "")
            results['analyses']['best_practices'] = self._check_best_practices(code, analysis_info)
        
        # Generate summary
        summary = self._generate_analysis_summary(results)
        results['summary'] = summary
        
        return self._build_success_result(
            message=f"Code analysis complete: {summary['overall_score']}/100",
            data=results,
            next_context={
                'analysis_results': results,
                'overall_score': summary['overall_score']
            }
        )
    
    def _generate_analysis_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary of analysis results.
        
        Args:
            results: Complete analysis results
            
        Returns:
            Summary dictionary
        """
        summary = {
            'overall_score': 0,
            'issues_found': 0,
            'critical_issues': 0,
            'warnings': 0,
            'recommendations': []
        }
        
        analyses = results.get('analyses', {})
        
        # Count issues and calculate score
        total_score = 0
        num_analyses = 0
        
        for analysis_type, analysis_data in analyses.items():
            if isinstance(analysis_data, dict):
                if 'score' in analysis_data:
                    total_score += analysis_data['score']
                    num_analyses += 1
                
                if 'issues' in analysis_data:
                    for issue in analysis_data['issues']:
                        summary['issues_found'] += 1
                        if issue.get('severity') == 'critical':
                            summary['critical_issues'] += 1
                        elif issue.get('severity') == 'warning':
                            summary['warnings'] += 1
                
                if 'recommendations' in analysis_data:
                    summary['recommendations'].extend(analysis_data['recommendations'])
        
        # Calculate overall score
        if num_analyses > 0:
            summary['overall_score'] = int(total_score / num_analyses)
        else:
            summary['overall_score'] = 100  # Default if no analyses were run
        
        return summary
    
    def _load_analysis_preferences(self) -> None:
        """Load analysis preferences from language-specific files."""
        if not self.root_folder:
            return
        
        # Try to load analysis_preferences.md from language directory
        language_dir = self._get_language_directory()
        if language_dir:
            prefs_file = language_dir / 'analysis_preferences.md'
            if prefs_file.exists():
                try:
                    content = prefs_file.read_text(encoding='utf-8')
                    self.analysis_preferences['language_specific'] = content
                    self.logger.info(f"Loaded analysis preferences from {prefs_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to load analysis preferences: {e}")
    
    def _get_language_directory(self) -> Optional[Path]:
        """Get the language-specific directory for this agent."""
        # Override in subclasses to provide language directory
        return None
    
    def ensure_codebase_awareness_initialized(
        self,
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Ensure codebase awareness is initialized.
        
        Args:
            context: Execution context that may contain file paths
            
        Returns:
            Tuple of (success, error_message)
        """
        if self.root_folder and self.codebase_structure:
            return True, None
        
        # Try to find root from context
        hint_path = context.get('file_path') or context.get('working_dir')
        
        # Find project root
        success, root, error = self.find_project_root(hint_path)
        if not success:
            return False, error
        
        # Load codebase structure
        success, structure, error = self.load_codebase_structure()
        if not success:
            # Warning only, not a critical error
            return True, error
        
        return True, None
    
    # Abstract methods to be implemented by subclasses
    
    @abstractmethod
    def _analyze_code_quality(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code quality for language-specific issues.
        
        Args:
            code: Source code to analyze
            analysis_info: Analysis information dictionary
            
        Returns:
            Dictionary with quality analysis results
        """
        pass
    
    @abstractmethod
    def _calculate_complexity(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate complexity metrics.
        
        Args:
            code: Source code to analyze
            analysis_info: Analysis information dictionary
            
        Returns:
            Dictionary with complexity metrics
        """
        pass
    
    @abstractmethod
    def _check_security(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for security vulnerabilities.
        
        Args:
            code: Source code to analyze
            analysis_info: Analysis information dictionary
            
        Returns:
            Dictionary with security analysis results
        """
        pass
    
    @abstractmethod
    def _analyze_performance(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze performance issues.
        
        Args:
            code: Source code to analyze
            analysis_info: Analysis information dictionary
            
        Returns:
            Dictionary with performance analysis results
        """
        pass
    
    @abstractmethod
    def _check_best_practices(self, code: str, analysis_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check adherence to best practices.
        
        Args:
            code: Source code to analyze
            analysis_info: Analysis information dictionary
            
        Returns:
            Dictionary with best practices check results
        """
        pass
