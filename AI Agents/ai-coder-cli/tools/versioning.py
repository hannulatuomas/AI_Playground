
"""
Versioning Tool - Automated version management with semantic versioning.

This tool provides automated version management capabilities for the AI Agent Console,
including:
- Semantic versioning (MAJOR.MINOR.PATCH)
- Automatic version bumping based on changes
- Version file updates across the project
- Git tag creation
- Changelog generation
- Integration with git commit workflows
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

from .base import Tool
from .lib.version_manager import VersionManager, VersionBumpType, ChangeAnalysis, VersionInfo


class VersioningTool(Tool):
    """
    Tool for automated version management with semantic versioning.
    
    Capabilities:
    - Get current version
    - Bump version (major, minor, patch)
    - Analyze changes to suggest version bump
    - Update version across multiple files
    - Create git tags for versions
    - Generate changelog entries
    - Integrate with git workflows
    
    Usage:
        tool = VersioningTool(config={'project_root': '/path/to/project'})
        
        # Get current version
        result = tool.invoke({'action': 'get_version'})
        
        # Analyze changes and bump version automatically
        result = tool.invoke({'action': 'auto_bump'})
        
        # Manually bump version
        result = tool.invoke({'action': 'bump', 'bump_type': 'minor'})
        
        # Update version in files
        result = tool.invoke({'action': 'update_files', 'version': '2.5.0'})
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize the versioning tool.
        
        Args:
            config: Configuration dictionary with optional:
                - project_root: Root directory of the project (default: current directory)
        """
        super().__init__(
            name='versioning',
            description='Automated version management with semantic versioning',
            config=config,
            **kwargs
        )
        
        project_root = self.config.get('project_root', Path.cwd())
        self.version_manager = VersionManager(project_root=project_root, logger=self.logger)
        
        self.logger.info("Versioning tool initialized")
    
    def invoke(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke the versioning tool.
        
        Supported actions:
        - 'get_version': Get current version
        - 'bump': Manually bump version (requires 'bump_type': 'major'|'minor'|'patch')
        - 'auto_bump': Analyze changes and bump version automatically
        - 'analyze': Analyze changes without bumping version
        - 'update_files': Update version in project files (requires 'version')
        - 'create_tag': Create git tag for version (optional 'message')
        - 'full_release': Complete release workflow (analyze, bump, update, tag)
        
        Args:
            params: Dictionary with:
                - action: Action to perform (required)
                - Additional parameters based on action
                
        Returns:
            Dictionary with:
                - success: Boolean indicating success
                - action: Action performed
                - version: Current or new version
                - Additional data based on action
        """
        self._log_invocation(params)
        self.validate_params(params, ['action'])
        
        action = params['action']
        
        try:
            if action == 'get_version':
                return self._get_version()
            
            elif action == 'bump':
                return self._bump_version(params)
            
            elif action == 'auto_bump':
                return self._auto_bump_version(params)
            
            elif action == 'analyze':
                return self._analyze_changes(params)
            
            elif action == 'update_files':
                return self._update_files(params)
            
            elif action == 'create_tag':
                return self._create_tag(params)
            
            elif action == 'full_release':
                return self._full_release(params)
            
            else:
                return {
                    'success': False,
                    'error': f"Unknown action: {action}",
                    'supported_actions': [
                        'get_version', 'bump', 'auto_bump', 'analyze',
                        'update_files', 'create_tag', 'full_release'
                    ]
                }
                
        except Exception as e:
            self.logger.error(f"Versioning tool error: {e}", exc_info=True)
            return {
                'success': False,
                'action': action,
                'error': str(e)
            }
    
    def _get_version(self) -> Dict[str, Any]:
        """Get current version."""
        version = self.version_manager.get_current_version()
        
        return {
            'success': True,
            'action': 'get_version',
            'version': str(version),
            'version_parts': {
                'major': version.major,
                'minor': version.minor,
                'patch': version.patch,
                'prerelease': version.prerelease,
                'build': version.build
            }
        }
    
    def _bump_version(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Manually bump version."""
        self.validate_params(params, ['bump_type'])
        
        bump_type_str = params['bump_type'].lower()
        
        # Validate bump type
        if bump_type_str not in ['major', 'minor', 'patch']:
            return {
                'success': False,
                'action': 'bump',
                'error': f"Invalid bump_type: {bump_type_str}. Must be 'major', 'minor', or 'patch'"
            }
        
        bump_type = VersionBumpType[bump_type_str.upper()]
        old_version = self.version_manager.get_current_version()
        new_version = self.version_manager.bump_version(bump_type)
        
        return {
            'success': True,
            'action': 'bump',
            'bump_type': bump_type_str,
            'old_version': str(old_version),
            'new_version': str(new_version),
            'message': f"Version bumped from {old_version} to {new_version}"
        }
    
    def _auto_bump_version(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically bump version based on change analysis."""
        # Get optional parameters
        commit_messages = params.get('commit_messages')
        file_changes = params.get('file_changes')
        use_git = params.get('use_git', True)
        
        # Analyze changes
        analysis = self.version_manager.analyze_changes(
            commit_messages=commit_messages,
            file_changes=file_changes,
            use_git=use_git
        )
        
        if not analysis.suggested_bump:
            return {
                'success': False,
                'action': 'auto_bump',
                'error': 'No changes detected for version bump'
            }
        
        # Bump version
        old_version = self.version_manager.get_current_version()
        new_version = self.version_manager.bump_version(analysis.suggested_bump)
        
        return {
            'success': True,
            'action': 'auto_bump',
            'bump_type': analysis.suggested_bump.value,
            'old_version': str(old_version),
            'new_version': str(new_version),
            'analysis': {
                'has_breaking_changes': analysis.has_breaking_changes,
                'has_new_features': analysis.has_new_features,
                'has_bug_fixes': analysis.has_bug_fixes,
                'has_deprecations': analysis.has_deprecations,
                'commits_analyzed': len(analysis.commit_messages),
                'files_changed': len(analysis.file_changes)
            },
            'message': f"Version auto-bumped from {old_version} to {new_version} ({analysis.suggested_bump.value})"
        }
    
    def _analyze_changes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze changes without bumping version."""
        commit_messages = params.get('commit_messages')
        file_changes = params.get('file_changes')
        use_git = params.get('use_git', True)
        
        analysis = self.version_manager.analyze_changes(
            commit_messages=commit_messages,
            file_changes=file_changes,
            use_git=use_git
        )
        
        current_version = self.version_manager.get_current_version()
        
        return {
            'success': True,
            'action': 'analyze',
            'current_version': str(current_version),
            'suggested_bump': analysis.suggested_bump.value if analysis.suggested_bump else None,
            'analysis': {
                'has_breaking_changes': analysis.has_breaking_changes,
                'has_new_features': analysis.has_new_features,
                'has_bug_fixes': analysis.has_bug_fixes,
                'has_deprecations': analysis.has_deprecations,
                'commit_messages': analysis.commit_messages,
                'file_changes': analysis.file_changes
            }
        }
    
    def _update_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update version in project files."""
        # Use current version if not specified
        if 'version' in params:
            version = VersionInfo.from_string(params['version'])
        else:
            version = self.version_manager.get_current_version()
        
        results = self.version_manager.update_version_in_files(version)
        
        updated_files = [f for f, success in results.items() if success]
        skipped_files = [f for f, success in results.items() if not success]
        
        return {
            'success': True,
            'action': 'update_files',
            'version': str(version),
            'updated_files': updated_files,
            'skipped_files': skipped_files,
            'message': f"Updated version to {version} in {len(updated_files)} files"
        }
    
    def _create_tag(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create git tag for version."""
        # Use current version if not specified
        if 'version' in params:
            version = VersionInfo.from_string(params['version'])
        else:
            version = self.version_manager.get_current_version()
        
        message = params.get('message')
        success = self.version_manager.create_version_tag(version, message)
        
        return {
            'success': success,
            'action': 'create_tag',
            'version': str(version),
            'tag_name': f"v{version}",
            'message': f"Created tag v{version}" if success else "Failed to create tag"
        }
    
    def _full_release(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete release workflow:
        1. Analyze changes
        2. Bump version (auto or manual)
        3. Update version in files
        4. Create git tag
        """
        results = []
        
        # Step 1: Analyze changes
        self.logger.info("Step 1: Analyzing changes")
        analyze_result = self._analyze_changes(params)
        results.append(('analyze', analyze_result))
        
        if not analyze_result['success']:
            return {
                'success': False,
                'action': 'full_release',
                'error': 'Change analysis failed',
                'steps': results
            }
        
        # Step 2: Bump version
        self.logger.info("Step 2: Bumping version")
        if 'bump_type' in params:
            bump_result = self._bump_version(params)
        else:
            bump_result = self._auto_bump_version(params)
        results.append(('bump', bump_result))
        
        if not bump_result['success']:
            return {
                'success': False,
                'action': 'full_release',
                'error': 'Version bump failed',
                'steps': results
            }
        
        new_version = bump_result['new_version']
        
        # Step 3: Update files
        self.logger.info("Step 3: Updating version in files")
        update_result = self._update_files({'version': new_version})
        results.append(('update_files', update_result))
        
        # Step 4: Create tag (optional, based on config)
        if params.get('create_tag', True):
            self.logger.info("Step 4: Creating git tag")
            tag_result = self._create_tag({
                'version': new_version,
                'message': params.get('tag_message')
            })
            results.append(('create_tag', tag_result))
        
        return {
            'success': True,
            'action': 'full_release',
            'new_version': new_version,
            'steps': results,
            'message': f"Successfully released version {new_version}"
        }
