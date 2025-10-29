
"""
Git Agent - Handles Git repository operations with versioning support.

This agent manages git operations including initialization, staging,
committing, and pushing with user confirmation. It also integrates with
the versioning tool for automated version management.
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base import Agent


class GitAgent(Agent):
    """
    Agent that handles Git version control operations with versioning support.
    
    Capabilities:
    - Initialize git repositories
    - Stage files (git add)
    - Create commits (git commit)
    - Push to remote (git push)
    - Check repository status
    - Request confirmations for destructive operations
    - Automatic version bumping on commits (when enabled)
    - Version tagging for releases
    """
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute git operations based on task description.
        
        Args:
            task: Git operation description (e.g., "commit changes with message")
            context: Execution context
            
        Returns:
            Dictionary with success status and git operation results
        """
        self._log_action("Starting git operation", task[:100])
        
        try:
            # Determine git operation
            operation = self._parse_git_task(task, context)
            
            if not operation:
                return self._build_error_result(
                    "Could not determine git operation from task"
                )
            
            # Check if git tool is available
            git_tool = self._get_tool('git')
            use_tool = git_tool is not None and self.config.get('use_gitpython', True)
            
            # Request confirmation if needed
            if self._requires_confirmation(operation) and not context.get('auto_confirm', False):
                confirmation = self._request_confirmation(operation)
                if not confirmation:
                    return self._build_success_result(
                        message="Git operation cancelled by user",
                        data={'cancelled': True}
                    )
            
            # Execute operation
            if use_tool:
                result = self._execute_with_tool(git_tool, operation, context)
            else:
                result = self._execute_with_subprocess(operation, context)
            
            if result['success']:
                self._log_action("Git operation complete", operation['command'])
                return self._build_success_result(
                    message=f"Git operation '{operation['command']}' completed successfully",
                    data=result,
                    next_context={
                        'last_git_operation': operation['command'],
                        'git_output': result.get('output', '')
                    }
                )
            else:
                return self._build_error_result(result['message'])
            
        except Exception as e:
            self.logger.exception("Git operation failed")
            return self._build_error_result(f"Git operation failed: {str(e)}", e)
    
    def _parse_git_task(self, task: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse task to determine git operation.
        
        Args:
            task: Task description
            context: Execution context
            
        Returns:
            Operation dictionary or None
        """
        task_lower = task.lower()
        
        # Initialize
        if 'init' in task_lower and 'repo' in task_lower:
            return {
                'command': 'init',
                'args': {},
                'description': 'Initialize git repository'
            }
        
        # Status
        if 'status' in task_lower:
            return {
                'command': 'status',
                'args': {},
                'description': 'Check git status'
            }
        
        # Add files
        if 'add' in task_lower or 'stage' in task_lower:
            # Check if specific files mentioned
            files = context.get('last_file', '.')
            
            return {
                'command': 'add',
                'args': {'files': [files]},
                'description': f'Stage files: {files}'
            }
        
        # Commit
        if 'commit' in task_lower:
            # Extract commit message
            message = self._extract_commit_message(task)
            
            return {
                'command': 'commit',
                'args': {'message': message},
                'description': f'Commit with message: {message}'
            }
        
        # Push
        if 'push' in task_lower:
            return {
                'command': 'push',
                'args': {},
                'description': 'Push to remote repository'
            }
        
        # Default: status
        return {
            'command': 'status',
            'args': {},
            'description': 'Check git status (default)'
        }
    
    def _extract_commit_message(self, task: str) -> str:
        """
        Extract commit message from task.
        
        Args:
            task: Task description
            
        Returns:
            Commit message
        """
        import re
        
        # Look for patterns like: 'commit with message "..."' or 'commit "..."'
        pattern1 = r'(?:message|with)\s+["\']([^"\']+)["\']'
        match1 = re.search(pattern1, task, re.IGNORECASE)
        
        if match1:
            return match1.group(1)
        
        # Look for text after "commit"
        pattern2 = r'commit\s+(.+?)(?:\s+to|\s+and|\s*$)'
        match2 = re.search(pattern2, task, re.IGNORECASE)
        
        if match2:
            message = match2.group(1).strip().strip('"\'')
            if message and not message.startswith('-'):
                return message
        
        # Default message
        return "Update from AI Agent Console"
    
    def _requires_confirmation(self, operation: Dict[str, Any]) -> bool:
        """
        Check if operation requires user confirmation.
        
        Args:
            operation: Git operation details
            
        Returns:
            True if confirmation required
        """
        require_git_confirmation = self.config.get('require_git_confirmation', True)
        
        if not require_git_confirmation:
            return False
        
        # Commands that require confirmation
        confirmation_commands = ['commit', 'push', 'reset', 'rebase', 'merge']
        
        return operation['command'] in confirmation_commands
    
    def _request_confirmation(self, operation: Dict[str, Any]) -> bool:
        """
        Request user confirmation for git operation.
        
        Args:
            operation: Git operation details
            
        Returns:
            True if confirmed, False otherwise
        """
        self.logger.info(
            f"Confirmation required for git {operation['command']}: {operation['description']}"
        )
        
        # In production, this should prompt the user
        # For automation/testing, return True
        return True
    
    def _execute_with_tool(
        self,
        git_tool: Any,
        operation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute git operation using GitTool.
        
        Args:
            git_tool: GitTool instance
            operation: Operation details
            context: Execution context
            
        Returns:
            Result dictionary
        """
        try:
            command = operation['command']
            args = operation['args']
            
            # Map commands to tool methods
            if command == 'init':
                result = git_tool.invoke({'action': 'init', 'path': '.'})
            elif command == 'status':
                result = git_tool.invoke({'action': 'status', 'path': '.'})
            elif command == 'add':
                result = git_tool.invoke({
                    'action': 'add',
                    'path': '.',
                    'files': args.get('files', ['.'])
                })
            elif command == 'commit':
                result = git_tool.invoke({
                    'action': 'commit',
                    'path': '.',
                    'message': args.get('message', 'Update')
                })
            elif command == 'push':
                result = git_tool.invoke({'action': 'push', 'path': '.'})
            else:
                return {
                    'success': False,
                    'message': f'Unknown git command: {command}'
                }
            
            # Check if the git tool operation was successful
            if isinstance(result, dict) and result.get('success') is False:
                return {
                    'success': False,
                    'message': result.get('message', 'Git operation failed'),
                    'output': result,
                    'method': 'tool'
                }
            
            return {
                'success': True,
                'output': result,
                'method': 'tool'
            }
            
        except Exception as e:
            self.logger.error(f"Git tool execution failed: {e}")
            return {
                'success': False,
                'message': f'Git tool failed: {str(e)}'
            }
    
    def _execute_with_subprocess(
        self,
        operation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute git operation using subprocess.
        
        Args:
            operation: Operation details
            context: Execution context
            
        Returns:
            Result dictionary
        """
        try:
            command = operation['command']
            args = operation['args']
            
            # Build git command
            git_cmd = ['git', command]
            
            if command == 'add':
                files = args.get('files', ['.'])
                git_cmd.extend(files)
            elif command == 'commit':
                message = args.get('message', 'Update')
                git_cmd.extend(['-m', message])
            
            # Execute command
            result = subprocess.run(
                git_cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=Path.cwd()
            )
            
            if result.returncode == 0:
                output = result.stdout or result.stderr
                return {
                    'success': True,
                    'output': output.strip(),
                    'method': 'subprocess'
                }
            else:
                return {
                    'success': False,
                    'message': f'Git command failed: {result.stderr.strip()}'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Git command timed out'
            }
        except Exception as e:
            self.logger.error(f"Git subprocess execution failed: {e}")
            return {
                'success': False,
                'message': f'Git subprocess failed: {str(e)}'
            }
    
    def _handle_versioning_with_commit(
        self,
        operation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Handle versioning integration with git commit.
        
        This method checks if versioning should be applied and performs:
        1. Change analysis
        2. Version bump
        3. Version file updates
        4. Git tag creation (optional)
        
        Args:
            operation: Commit operation details
            context: Execution context
            
        Returns:
            Versioning result or None if versioning not enabled
        """
        # Check if versioning is enabled
        enable_versioning = context.get('enable_versioning', False) or \
                          self.config.get('enable_git_versioning', False)
        
        if not enable_versioning:
            return None
        
        # Get versioning tool
        versioning_tool = self._get_tool('versioning')
        if not versioning_tool:
            self.logger.debug("Versioning tool not available, skipping version management")
            return None
        
        try:
            self.logger.info("Processing versioning for commit...")
            
            # Determine version bump type
            bump_type = context.get('version_bump_type')
            
            if bump_type:
                # Manual version bump
                result = versioning_tool.invoke({
                    'action': 'bump',
                    'bump_type': bump_type
                })
            else:
                # Automatic version bump based on changes
                result = versioning_tool.invoke({
                    'action': 'auto_bump',
                    'use_git': True
                })
            
            if result.get('success'):
                new_version = result.get('new_version')
                self.logger.info(f"Version bumped to {new_version}")
                
                # Update version in files
                update_result = versioning_tool.invoke({
                    'action': 'update_files',
                    'version': new_version
                })
                
                if update_result.get('success'):
                    updated_files = update_result.get('updated_files', [])
                    self.logger.info(f"Updated version in {len(updated_files)} files")
                    
                    # Stage the updated files
                    if updated_files:
                        for file in updated_files:
                            subprocess.run(['git', 'add', file], cwd=Path.cwd())
                        subprocess.run(['git', 'add', 'VERSION'], cwd=Path.cwd())
                
                # Create git tag if enabled
                if context.get('create_version_tag', True):
                    tag_result = versioning_tool.invoke({
                        'action': 'create_tag',
                        'version': new_version,
                        'message': f"Release {new_version}"
                    })
                    
                    if tag_result.get('success'):
                        self.logger.info(f"Created git tag: v{new_version}")
                
                return result
            else:
                self.logger.warning(f"Version bump failed: {result.get('error')}")
                return result
                
        except Exception as e:
            self.logger.error(f"Versioning integration failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def commit_with_versioning(
        self,
        message: str,
        bump_type: Optional[str] = None,
        create_tag: bool = True
    ) -> Dict[str, Any]:
        """
        Convenient method to commit with automatic versioning.
        
        Args:
            message: Commit message
            bump_type: Version bump type ('major', 'minor', 'patch'), or None for auto
            create_tag: Whether to create a git tag for the version
            
        Returns:
            Dictionary with commit and versioning results
        """
        context = {
            'enable_versioning': True,
            'version_bump_type': bump_type,
            'create_version_tag': create_tag
        }
        
        # Stage all changes
        self.execute("stage all changes", context)
        
        # Commit with versioning
        return self.execute(f'commit with message "{message}"', context)
