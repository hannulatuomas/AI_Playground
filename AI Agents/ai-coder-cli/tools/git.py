
"""
Git Tool - Git repository operations using gitpython.

This tool provides git operations with sandboxing support.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    import git
    from git import Repo, GitCommandError
    GITPYTHON_AVAILABLE = True
except ImportError:
    GITPYTHON_AVAILABLE = False

from .base import Tool


class GitTool(Tool):
    """
    Tool for Git repository operations.
    
    Capabilities:
    - Initialize repositories
    - Add files to staging
    - Create commits
    - Push to remote
    - Check repository status
    - Sandboxed operations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the git tool.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(
            name='git',
            description='Git version control operations',
            config=config
        )
        
        if not GITPYTHON_AVAILABLE:
            self.logger.warning(
                "gitpython not available. Install with: pip install gitpython"
            )
        
        self.enable_sandboxing = self.config.get('enable_sandboxing', True)
        self.sandbox_dir = self.config.get('sandbox_working_directory')
    
    def invoke(self, params: Dict[str, Any]) -> Any:
        """
        Execute git operation.
        
        Args:
            params: Dictionary with:
                - action: Git operation (init, status, add, commit, push)
                - path: Repository path
                - Additional action-specific parameters
                
        Returns:
            Operation result
        """
        if not GITPYTHON_AVAILABLE:
            raise RuntimeError(
                "gitpython is not installed. Install with: pip install gitpython"
            )
        
        self._log_invocation(params)
        
        action = params.get('action')
        if not action:
            raise ValueError("Parameter 'action' is required")
        
        # Validate path if sandboxing enabled
        repo_path = Path(params.get('path', '.')).resolve()
        if self.enable_sandboxing and not self._is_safe_path(repo_path):
            raise ValueError(f"Path not allowed by sandboxing: {repo_path}")
        
        # Route to appropriate method
        if action == 'init':
            return self._init_repo(repo_path)
        elif action == 'status':
            return self._get_status(repo_path)
        elif action == 'add':
            return self._add_files(repo_path, params.get('files', ['.']))
        elif action == 'commit':
            return self._commit(repo_path, params.get('message', 'Update'))
        elif action == 'push':
            return self._push(repo_path)
        else:
            raise ValueError(f"Unknown git action: {action}")
    
    def _is_safe_path(self, path: Path) -> bool:
        """
        Check if path is safe for operations.
        
        Args:
            path: Path to validate
            
        Returns:
            True if safe, False otherwise
        """
        if not self.enable_sandboxing:
            return True
        
        # Check if within sandbox directory
        if self.sandbox_dir:
            sandbox = Path(self.sandbox_dir).resolve()
            try:
                path.relative_to(sandbox)
                return True
            except ValueError:
                return False
        
        # Check against blocked paths
        blocked_paths = ['/etc', '/sys', '/proc', '/boot', '/dev', '/root']
        for blocked in blocked_paths:
            blocked_path = Path(blocked).resolve()
            try:
                path.relative_to(blocked_path)
                return False
            except ValueError:
                continue
        
        return True
    
    def _init_repo(self, path: Path) -> Dict[str, Any]:
        """
        Initialize a git repository.
        
        Args:
            path: Repository path
            
        Returns:
            Result dictionary
        """
        try:
            repo = Repo.init(path)
            return {
                'success': True,
                'message': f'Initialized git repository at {path}',
                'path': str(path)
            }
        except Exception as e:
            self.logger.error(f"Git init failed: {e}")
            raise RuntimeError(f"Failed to initialize repository: {e}") from e
    
    def _get_status(self, path: Path) -> Dict[str, Any]:
        """
        Get repository status.
        
        Args:
            path: Repository path
            
        Returns:
            Status dictionary
        """
        try:
            repo = Repo(path)
            
            # Get changed files
            changed = [item.a_path for item in repo.index.diff(None)]
            untracked = repo.untracked_files
            staged = [item.a_path for item in repo.index.diff('HEAD')]
            
            return {
                'success': True,
                'changed': changed,
                'untracked': untracked,
                'staged': staged,
                'clean': not (changed or untracked or staged)
            }
        except Exception as e:
            self.logger.error(f"Git status failed: {e}")
            raise RuntimeError(f"Failed to get status: {e}") from e
    
    def _add_files(self, path: Path, files: List[str]) -> Dict[str, Any]:
        """
        Add files to staging area.
        
        Args:
            path: Repository path
            files: List of file patterns to add
            
        Returns:
            Result dictionary
        """
        try:
            repo = Repo(path)
            
            # Add files
            if '.' in files or '*' in files:
                # Add all
                repo.git.add(A=True)
                added = 'all files'
            else:
                repo.index.add(files)
                added = ', '.join(files)
            
            return {
                'success': True,
                'message': f'Added {added} to staging',
                'files': files
            }
        except Exception as e:
            self.logger.error(f"Git add failed: {e}")
            raise RuntimeError(f"Failed to add files: {e}") from e
    
    def _commit(self, path: Path, message: str) -> Dict[str, Any]:
        """
        Create a commit.
        
        Args:
            path: Repository path
            message: Commit message
            
        Returns:
            Result dictionary
        """
        try:
            repo = Repo(path)
            
            # Check if there's anything to commit
            if not repo.is_dirty():
                return {
                    'success': True,
                    'message': 'Nothing to commit, working tree clean',
                    'commit': None
                }
            
            # Create commit
            commit = repo.index.commit(message)
            
            return {
                'success': True,
                'message': f'Created commit: {message}',
                'commit': str(commit.hexsha[:8]),
                'author': str(commit.author),
                'date': commit.committed_datetime.isoformat()
            }
        except Exception as e:
            self.logger.error(f"Git commit failed: {e}")
            raise RuntimeError(f"Failed to create commit: {e}") from e
    
    def _push(self, path: Path) -> Dict[str, Any]:
        """
        Push to remote repository.
        
        Args:
            path: Repository path
            
        Returns:
            Result dictionary
        """
        try:
            repo = Repo(path)
            
            # Check if remote exists
            if not repo.remotes:
                return {
                    'success': False,
                    'message': 'No remote repository configured',
                    'error': 'No remote found'
                }
            
            # Push to origin
            origin = repo.remote('origin')
            push_info = origin.push()
            
            return {
                'success': True,
                'message': 'Pushed to remote repository',
                'remote': 'origin',
                'info': str(push_info)
            }
        except Exception as e:
            self.logger.error(f"Git push failed: {e}")
            raise RuntimeError(f"Failed to push: {e}") from e
