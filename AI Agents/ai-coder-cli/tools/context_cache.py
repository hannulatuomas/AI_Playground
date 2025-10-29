"""
Context Cache Tool - Manages context caching and workflow state.

This tool provides context management including:
- Result caching with TTL
- Workflow state tracking
- Context type management (TODO, RESULT, ISSUE, etc.)
- Cache invalidation and cleanup
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import sys
import json
from datetime import datetime, timedelta
from enum import Enum

from .base import Tool

# Import the ContextManager from tools.lib
try:
    from .lib.context_manager import ContextManager, ContextType
    CONTEXT_MANAGER_AVAILABLE = True
except ImportError:
    CONTEXT_MANAGER_AVAILABLE = False
    # Define fallback ContextType if import fails
    class ContextType(Enum):
        TODO = "todo"
        RESULT = "result"
        ISSUE = "issue"
        STATUS = "status"
        STRUCTURE = "structure"
        ERROR = "error"
        TEST_PLAN = "test_plan"
        PREFERENCE = "preference"
        CHOICE = "choice"
        CACHE = "cache"


class ContextCacheTool(Tool):
    """
    Tool for managing context and caching workflow results.
    
    Capabilities:
    - Cache operation results with TTL
    - Save and load context by type
    - Track workflow state
    - Manage errors and issues
    - Clean expired cache entries
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the context cache tool.
        
        Args:
            config: Configuration dictionary with optional:
                - project_root: Root directory of the project (default: current directory)
                - default_ttl: Default cache TTL in seconds (default: 3600)
        """
        super().__init__(
            name='context_cache',
            description='Context management and result caching',
            config=config
        )
        
        if not CONTEXT_MANAGER_AVAILABLE:
            self.logger.warning(
                "ContextManager not available. Ensure tools/lib/context_manager.py exists"
            )
        
        self.project_root = Path(self.config.get('project_root', '.'))
        self.default_ttl = self.config.get('default_ttl', 3600)
        
        # Lazy-load context manager
        self._context_manager = None
    
    @property
    def context_manager(self) -> 'ContextManager':
        """Lazy-load context manager."""
        if not CONTEXT_MANAGER_AVAILABLE:
            raise RuntimeError("ContextManager is not available")
        
        if self._context_manager is None:
            self._context_manager = ContextManager(str(self.project_root))
        
        return self._context_manager
    
    def invoke(self, params: Dict[str, Any]) -> Any:
        """
        Execute context cache operation.
        
        Args:
            params: Dictionary with:
                - action: Operation to perform (cache_result, get_cached, save_context,
                         load_context, save_todo, load_todo, save_error, list_contexts,
                         clean_cache, invalidate_cache)
                - Additional action-specific parameters
                
        Returns:
            Operation result
        """
        if not CONTEXT_MANAGER_AVAILABLE:
            return {
                'success': False,
                'error': 'ContextManager not available'
            }
        
        self._log_invocation(params)
        
        action = params.get('action')
        if not action:
            raise ValueError("Parameter 'action' is required")
        
        # Route to appropriate method
        if action == 'cache_result':
            return self._cache_result(
                params.get('operation'),
                params.get('params_dict'),
                params.get('result'),
                params.get('ttl_seconds')
            )
        elif action == 'get_cached':
            return self._get_cached(
                params.get('operation'),
                params.get('params_dict')
            )
        elif action == 'save_context':
            return self._save_context(
                params.get('context_type'),
                params.get('name'),
                params.get('data'),
                params.get('metadata')
            )
        elif action == 'load_context':
            return self._load_context(
                params.get('context_type'),
                params.get('name')
            )
        elif action == 'save_todo':
            return self._save_todo(
                params.get('name'),
                params.get('todos')
            )
        elif action == 'load_todo':
            return self._load_todo(params.get('name'))
        elif action == 'save_error':
            return self._save_error(
                params.get('name'),
                params.get('error_data')
            )
        elif action == 'list_contexts':
            return self._list_contexts(params.get('context_type'))
        elif action == 'clean_cache':
            return self._clean_cache()
        elif action == 'invalidate_cache':
            return self._invalidate_cache(
                params.get('operation'),
                params.get('params_dict')
            )
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _cache_result(
        self,
        operation: str,
        params_dict: Dict[str, Any],
        result: Any,
        ttl_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """Cache an operation result."""
        if not operation:
            raise ValueError("Parameter 'operation' is required")
        if params_dict is None:
            raise ValueError("Parameter 'params_dict' is required")
        if result is None:
            raise ValueError("Parameter 'result' is required")
        
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        
        try:
            self.context_manager.cache_result(operation, params_dict, result, ttl)
            
            self.logger.info(f"Cached result for operation: {operation}")
            
            return {
                'success': True,
                'operation': operation,
                'ttl_seconds': ttl
            }
        except Exception as e:
            self.logger.error(f"Failed to cache result: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_cached(
        self,
        operation: str,
        params_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get cached result."""
        if not operation:
            raise ValueError("Parameter 'operation' is required")
        if params_dict is None:
            raise ValueError("Parameter 'params_dict' is required")
        
        try:
            result = self.context_manager.get_cached_result(operation, params_dict)
            
            if result is not None:
                return {
                    'success': True,
                    'operation': operation,
                    'cached': True,
                    'result': result
                }
            else:
                return {
                    'success': True,
                    'operation': operation,
                    'cached': False,
                    'result': None
                }
        except Exception as e:
            self.logger.error(f"Failed to get cached result: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _save_context(
        self,
        context_type: str,
        name: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Save context data."""
        if not context_type:
            raise ValueError("Parameter 'context_type' is required")
        if not name:
            raise ValueError("Parameter 'name' is required")
        if not data:
            raise ValueError("Parameter 'data' is required")
        
        try:
            # Convert context_type string to enum
            ctx_type = ContextType(context_type)
            
            self.context_manager.save_context(ctx_type, name, data, metadata)
            
            self.logger.info(f"Saved context: {context_type}/{name}")
            
            return {
                'success': True,
                'context_type': context_type,
                'name': name
            }
        except ValueError as e:
            return {
                'success': False,
                'error': f"Invalid context type: {context_type}"
            }
        except Exception as e:
            self.logger.error(f"Failed to save context: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_context(
        self,
        context_type: str,
        name: str
    ) -> Dict[str, Any]:
        """Load context data."""
        if not context_type:
            raise ValueError("Parameter 'context_type' is required")
        if not name:
            raise ValueError("Parameter 'name' is required")
        
        try:
            # Convert context_type string to enum
            ctx_type = ContextType(context_type)
            
            context = self.context_manager.load_context(ctx_type, name)
            
            if context:
                return {
                    'success': True,
                    'context_type': context_type,
                    'name': name,
                    'context': context
                }
            else:
                return {
                    'success': False,
                    'context_type': context_type,
                    'name': name,
                    'error': 'Context not found'
                }
        except ValueError as e:
            return {
                'success': False,
                'error': f"Invalid context type: {context_type}"
            }
        except Exception as e:
            self.logger.error(f"Failed to load context: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _save_todo(
        self,
        name: str,
        todos: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Save TODO list."""
        if not name:
            raise ValueError("Parameter 'name' is required")
        if not todos:
            raise ValueError("Parameter 'todos' is required")
        
        try:
            self.context_manager.save_todo(name, todos)
            
            self.logger.info(f"Saved TODO list: {name}")
            
            return {
                'success': True,
                'name': name,
                'count': len(todos)
            }
        except Exception as e:
            self.logger.error(f"Failed to save TODO: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_todo(self, name: str) -> Dict[str, Any]:
        """Load TODO list."""
        if not name:
            raise ValueError("Parameter 'name' is required")
        
        try:
            todos = self.context_manager.load_todo(name)
            
            if todos is not None:
                return {
                    'success': True,
                    'name': name,
                    'todos': todos
                }
            else:
                return {
                    'success': False,
                    'name': name,
                    'error': 'TODO list not found'
                }
        except Exception as e:
            self.logger.error(f"Failed to load TODO: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _save_error(
        self,
        name: str,
        error_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save error information."""
        if not name:
            raise ValueError("Parameter 'name' is required")
        if not error_data:
            raise ValueError("Parameter 'error_data' is required")
        
        try:
            self.context_manager.save_error(name, error_data)
            
            self.logger.info(f"Saved error: {name}")
            
            return {
                'success': True,
                'name': name
            }
        except Exception as e:
            self.logger.error(f"Failed to save error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _list_contexts(self, context_type: Optional[str] = None) -> Dict[str, Any]:
        """List contexts of a specific type."""
        try:
            context_dir = self.project_root / '.project' / 'context'
            
            if context_type:
                # List specific type
                type_dir = context_dir / context_type
                if not type_dir.exists():
                    return {
                        'success': False,
                        'error': f"Context type directory not found: {context_type}"
                    }
                
                contexts = []
                for file in type_dir.glob('*.json'):
                    contexts.append(file.stem)
                
                return {
                    'success': True,
                    'context_type': context_type,
                    'contexts': contexts,
                    'count': len(contexts)
                }
            else:
                # List all types
                all_contexts = {}
                for ctx_type in ContextType:
                    type_dir = context_dir / ctx_type.value
                    if type_dir.exists():
                        contexts = [f.stem for f in type_dir.glob('*.json')]
                        all_contexts[ctx_type.value] = contexts
                
                return {
                    'success': True,
                    'all_contexts': all_contexts
                }
        except Exception as e:
            self.logger.error(f"Failed to list contexts: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _clean_cache(self) -> Dict[str, Any]:
        """Clean expired cache entries."""
        try:
            cache_dir = self.project_root / '.project' / 'cache'
            
            if not cache_dir.exists():
                return {
                    'success': True,
                    'removed_count': 0
                }
            
            removed_count = 0
            now = datetime.now()
            
            for cache_file in cache_dir.glob('*.json'):
                try:
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)
                    
                    # Check if expired
                    expires_at = cache_data.get('expires_at')
                    if expires_at:
                        expire_time = datetime.fromisoformat(expires_at)
                        if now > expire_time:
                            cache_file.unlink()
                            removed_count += 1
                except Exception as e:
                    self.logger.warning(f"Error processing cache file {cache_file}: {e}")
            
            self.logger.info(f"Cleaned {removed_count} expired cache entries")
            
            return {
                'success': True,
                'removed_count': removed_count
            }
        except Exception as e:
            self.logger.error(f"Failed to clean cache: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _invalidate_cache(
        self,
        operation: Optional[str] = None,
        params_dict: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Invalidate cache entries."""
        try:
            cache_dir = self.project_root / '.project' / 'cache'
            
            if not cache_dir.exists():
                return {
                    'success': True,
                    'invalidated_count': 0
                }
            
            if operation and params_dict is not None:
                # Invalidate specific cache entry
                cache_key = self.context_manager._generate_cache_key(operation, params_dict)
                cache_file = cache_dir / f"{cache_key}.json"
                
                if cache_file.exists():
                    cache_file.unlink()
                    self.logger.info(f"Invalidated cache for operation: {operation}")
                    return {
                        'success': True,
                        'invalidated_count': 1,
                        'operation': operation
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Cache entry not found'
                    }
            else:
                # Invalidate all cache
                count = 0
                for cache_file in cache_dir.glob('*.json'):
                    cache_file.unlink()
                    count += 1
                
                self.logger.info(f"Invalidated all cache ({count} entries)")
                
                return {
                    'success': True,
                    'invalidated_count': count
                }
        except Exception as e:
            self.logger.error(f"Failed to invalidate cache: {e}")
            return {
                'success': False,
                'error': str(e)
            }
