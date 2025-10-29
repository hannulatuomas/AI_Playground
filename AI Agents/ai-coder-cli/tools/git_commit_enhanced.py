"""
Enhanced Git Commit Tool - Provides enhanced git commit practices with detailed messages and summaries.

This tool extends git commit functionality with:
- Detailed commit message generation
- Commit summary documentation
- Change analysis and categorization
- Conventional commit format support
- Commit preview functionality
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import sys
import subprocess

from .base import Tool

# Import the GitCommitEnhancer from tools.lib
try:
    from .lib.git_commit_enhancer import GitCommitEnhancer
    GIT_COMMIT_ENHANCER_AVAILABLE = True
except ImportError:
    GIT_COMMIT_ENHANCER_AVAILABLE = False


class GitCommitEnhancedTool(Tool):
    """
    Tool for enhanced git commit practices.
    
    Capabilities:
    - Create enhanced commits with detailed messages
    - Generate commit summaries
    - Analyze staged changes
    - Preview commits before creating
    - Support conventional commit format
    - Generate commit documentation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the enhanced git commit tool.
        
        Args:
            config: Configuration dictionary with optional:
                - project_root: Root directory of the project (default: current directory)
                - repo_path: Git repository path (default: project_root)
        """
        super().__init__(
            name='git_commit_enhanced',
            description='Enhanced git commit practices with detailed messages',
            config=config
        )
        
        if not GIT_COMMIT_ENHANCER_AVAILABLE:
            self.logger.warning(
                "GitCommitEnhancer not available. Ensure tools/lib/git_commit_enhancer.py exists"
            )
        
        self.project_root = Path(self.config.get('project_root', '.'))
        self.repo_path = Path(self.config.get('repo_path', self.project_root))
        
        # Lazy-load enhancer
        self._enhancer = None
    
    @property
    def enhancer(self) -> 'GitCommitEnhancer':
        """Lazy-load git commit enhancer."""
        if not GIT_COMMIT_ENHANCER_AVAILABLE:
            raise RuntimeError("GitCommitEnhancer is not available")
        
        if self._enhancer is None:
            self._enhancer = GitCommitEnhancer(str(self.repo_path))
        
        return self._enhancer
    
    def invoke(self, params: Dict[str, Any]) -> Any:
        """
        Execute enhanced git commit operation.
        
        Args:
            params: Dictionary with:
                - action: Operation to perform (create_commit, preview_commit,
                         analyze_changes, get_staged_changes, get_diff_stats,
                         generate_message, generate_summary)
                - Additional action-specific parameters
                
        Returns:
            Operation result
        """
        if not GIT_COMMIT_ENHANCER_AVAILABLE:
            return {
                'success': False,
                'error': 'GitCommitEnhancer not available'
            }
        
        self._log_invocation(params)
        
        action = params.get('action')
        if not action:
            raise ValueError("Parameter 'action' is required")
        
        # Route to appropriate method
        if action == 'create_commit':
            return self._create_commit(
                params.get('message'),
                params.get('include_summary', True)
            )
        elif action == 'preview_commit':
            return self._preview_commit(params.get('message'))
        elif action == 'analyze_changes':
            return self._analyze_changes()
        elif action == 'get_staged_changes':
            return self._get_staged_changes()
        elif action == 'get_diff_stats':
            return self._get_diff_stats()
        elif action == 'generate_message':
            return self._generate_message(
                params.get('message_type', 'feat'),
                params.get('scope'),
                params.get('description')
            )
        elif action == 'generate_summary':
            return self._generate_summary(params.get('commit_hash'))
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _create_commit(
        self,
        message: str,
        include_summary: bool = True
    ) -> Dict[str, Any]:
        """Create an enhanced commit."""
        if not message:
            raise ValueError("Parameter 'message' is required for create_commit")
        
        try:
            result = self.enhancer.create_enhanced_commit(message, include_summary)
            
            if result.get('success'):
                self.logger.info(f"Created enhanced commit: {result.get('commit_hash', 'unknown')}")
                return {
                    'success': True,
                    'commit_hash': result.get('commit_hash'),
                    'message': result.get('message'),
                    'summary_file': result.get('summary_file')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }
        except Exception as e:
            self.logger.error(f"Failed to create commit: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _preview_commit(self, message: str) -> Dict[str, Any]:
        """Preview what an enhanced commit would look like."""
        if not message:
            raise ValueError("Parameter 'message' is required for preview_commit")
        
        try:
            preview = self.enhancer.preview_commit(message)
            
            return {
                'success': True,
                'preview': preview
            }
        except Exception as e:
            self.logger.error(f"Failed to preview commit: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_changes(self) -> Dict[str, Any]:
        """Analyze staged changes."""
        try:
            analysis = self.enhancer.analyze_changes()
            
            return {
                'success': True,
                'analysis': analysis
            }
        except Exception as e:
            self.logger.error(f"Failed to analyze changes: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_staged_changes(self) -> Dict[str, Any]:
        """Get information about staged changes."""
        try:
            changes = self.enhancer.get_staged_changes()
            
            return {
                'success': True,
                'changes': changes,
                'total_files': sum(len(files) for files in changes.values())
            }
        except Exception as e:
            self.logger.error(f"Failed to get staged changes: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_diff_stats(self) -> Dict[str, Any]:
        """Get diff statistics."""
        try:
            stats = self.enhancer.get_diff_stats()
            
            return {
                'success': True,
                'stats': stats
            }
        except Exception as e:
            self.logger.error(f"Failed to get diff stats: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_message(
        self,
        message_type: str,
        scope: Optional[str],
        description: str
    ) -> Dict[str, Any]:
        """Generate a conventional commit message."""
        if not description:
            raise ValueError("Parameter 'description' is required for generate_message")
        
        try:
            # Build conventional commit message
            if scope:
                message = f"{message_type}({scope}): {description}"
            else:
                message = f"{message_type}: {description}"
            
            return {
                'success': True,
                'message': message,
                'type': message_type,
                'scope': scope,
                'description': description
            }
        except Exception as e:
            self.logger.error(f"Failed to generate message: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_summary(self, commit_hash: Optional[str] = None) -> Dict[str, Any]:
        """Generate a summary for a commit."""
        try:
            # If no commit hash provided, use HEAD
            if not commit_hash:
                commit_hash = 'HEAD'
            
            # Get commit info
            result = subprocess.run(
                ['git', 'show', '--stat', commit_hash],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_info = result.stdout
            
            # Parse commit info
            lines = commit_info.split('\n')
            commit_line = lines[0] if lines else ''
            author_line = lines[1] if len(lines) > 1 else ''
            date_line = lines[2] if len(lines) > 2 else ''
            message_lines = []
            
            # Find message lines
            in_message = False
            for line in lines[4:]:
                if not line.strip():
                    if in_message:
                        break
                    in_message = True
                elif in_message:
                    message_lines.append(line.strip())
            
            message = '\n'.join(message_lines)
            
            # Get file changes
            stats_result = subprocess.run(
                ['git', 'show', '--name-status', commit_hash],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse file changes
            changes = {
                'added': [],
                'modified': [],
                'deleted': []
            }
            
            for line in stats_result.stdout.split('\n'):
                if line and '\t' in line:
                    status, *files = line.split('\t')
                    if status == 'A':
                        changes['added'].extend(files)
                    elif status == 'M':
                        changes['modified'].extend(files)
                    elif status == 'D':
                        changes['deleted'].extend(files)
            
            summary = {
                'commit_hash': commit_hash,
                'author': author_line.replace('Author:', '').strip(),
                'date': date_line.replace('Date:', '').strip(),
                'message': message,
                'changes': changes
            }
            
            return {
                'success': True,
                'summary': summary
            }
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git command failed: {e}")
            return {
                'success': False,
                'error': f"Git error: {e.stderr}"
            }
        except Exception as e:
            self.logger.error(f"Failed to generate summary: {e}")
            return {
                'success': False,
                'error': str(e)
            }
