# New Infrastructure Tools Guide

## Overview

This guide documents the new infrastructure tools that have been integrated into the standard tool architecture. These tools provide essential functionality for project management, chat history, dependency tracking, context caching, and enhanced git commits.

## Table of Contents

- [ProjectManagementTool](#projectmanagementtool)
- [ChatHistoryTool](#chathistorytool)
- [DependencyTrackingTool](#dependencytrackingtool)
- [ContextCacheTool](#contextcachetool)
- [GitCommitEnhancedTool](#gitcommitenhancedtool)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)

---

## ProjectManagementTool

**Purpose**: Manages project-level state, global memory, TODO lists, and preferences.

### Configuration

```python
from tools import ProjectManagementTool

tool = ProjectManagementTool({
    'project_root': '.',  # Project root directory
    'memory_file': None   # Optional custom memory file path
})
```

### Actions

#### save_memory
Save data to global project memory.

```python
result = tool.invoke({
    'action': 'save_memory',
    'key': 'my_key',
    'data': {'any': 'data', 'structure': [1, 2, 3]}
})
# Returns: {'success': True, 'key': 'my_key', 'timestamp': '...'}
```

#### load_memory
Load data from global project memory.

```python
result = tool.invoke({
    'action': 'load_memory',
    'key': 'my_key'
})
# Returns: {'success': True, 'key': 'my_key', 'data': {...}, 'timestamp': '...'}
```

#### save_todo
Save a TODO list.

```python
result = tool.invoke({
    'action': 'save_todo',
    'name': 'sprint_tasks',
    'todos': [
        {'task': 'Implement feature X', 'status': 'in_progress', 'priority': 'high'},
        {'task': 'Write tests', 'status': 'pending', 'priority': 'medium'}
    ]
})
# Returns: {'success': True, 'name': 'sprint_tasks', 'count': 2}
```

#### load_todo
Load a TODO list.

```python
result = tool.invoke({
    'action': 'load_todo',
    'name': 'sprint_tasks'
})
# Returns: {'success': True, 'name': 'sprint_tasks', 'todos': [...], 'updated_at': '...'}
```

#### list_todos
List all TODO lists.

```python
result = tool.invoke({
    'action': 'list_todos'
})
# Returns: {'success': True, 'todos': [{'name': '...', 'count': N, 'updated_at': '...'}]}
```

#### save_preference
Save a user preference.

```python
result = tool.invoke({
    'action': 'save_preference',
    'key': 'theme',
    'value': 'dark'
})
# Returns: {'success': True, 'key': 'theme'}
```

#### load_preference
Load a user preference.

```python
result = tool.invoke({
    'action': 'load_preference',
    'key': 'theme'
})
# Returns: {'success': True, 'key': 'theme', 'value': 'dark', 'updated_at': '...'}
```

#### save_structure
Save project structure information.

```python
result = tool.invoke({
    'action': 'save_structure',
    'structure': {
        'directories': ['src', 'tests', 'docs'],
        'file_count': 42,
        'languages': ['python', 'javascript']
    }
})
# Returns: {'success': True, 'updated_at': '...'}
```

#### load_structure
Load project structure information.

```python
result = tool.invoke({
    'action': 'load_structure'
})
# Returns: {'success': True, 'structure': {...}, 'updated_at': '...'}
```

#### clear_memory
Clear memory entries.

```python
# Clear specific key
result = tool.invoke({
    'action': 'clear_memory',
    'key': 'my_key'
})

# Clear all memory
result = tool.invoke({
    'action': 'clear_memory'
})
# Returns: {'success': True, 'cleared': 'all'}
```

---

## ChatHistoryTool

**Purpose**: Manages conversation history, chat sessions, and context summaries.

### Configuration

```python
from tools import ChatHistoryTool

tool = ChatHistoryTool({
    'project_root': '.',
    'max_messages': 1000,  # Maximum messages per session
    'max_age_days': 30     # Maximum age of messages in days
})
```

### Actions

#### create_session
Create a new chat session.

```python
result = tool.invoke({
    'action': 'create_session',
    'session_id': 'user_123_session',
    'metadata': {
        'user': 'john_doe',
        'agent': 'code_assistant',
        'started_at': '2024-10-13T10:00:00'
    }
})
# Returns: {'success': True, 'session_id': '...', 'created_at': '...'}
```

#### save_message
Save a chat message to history.

```python
result = tool.invoke({
    'action': 'save_message',
    'session_id': 'user_123_session',
    'message': {
        'role': 'user',
        'content': 'How do I implement feature X?',
        'timestamp': '2024-10-13T10:05:00'
    }
})
# Returns: {'success': True, 'session_id': '...', 'message_count': N}
```

#### load_history
Load chat history for a session.

```python
result = tool.invoke({
    'action': 'load_history',
    'session_id': 'user_123_session',
    'limit': 50  # Optional: limit number of messages
})
# Returns: {'success': True, 'messages': [...], 'total_count': N, 'updated_at': '...'}
```

#### save_summary
Save a context summary for a session.

```python
result = tool.invoke({
    'action': 'save_summary',
    'session_id': 'user_123_session',
    'summary': 'User asked about implementing authentication. Discussed JWT tokens and best practices.'
})
# Returns: {'success': True, 'session_id': '...'}
```

#### load_summary
Load context summary for a session.

```python
result = tool.invoke({
    'action': 'load_summary',
    'session_id': 'user_123_session'
})
# Returns: {'success': True, 'summary': '...', 'updated_at': '...'}
```

#### list_sessions
List all chat sessions.

```python
result = tool.invoke({
    'action': 'list_sessions'
})
# Returns: {'success': True, 'sessions': [...], 'total_count': N}
```

#### prune_history
Prune old messages from history.

```python
# Prune specific session
result = tool.invoke({
    'action': 'prune_history',
    'session_id': 'user_123_session'
})

# Prune all sessions
result = tool.invoke({
    'action': 'prune_history'
})
# Returns: {'success': True, 'pruned_count': N, 'sessions_processed': M}
```

#### clear_session
Clear/delete a session.

```python
result = tool.invoke({
    'action': 'clear_session',
    'session_id': 'user_123_session'
})
# Returns: {'success': True, 'session_id': '...'}
```

---

## DependencyTrackingTool

**Purpose**: Analyzes codebase dependencies across multiple languages (Python, C#, C++, JavaScript, Shell, etc.).

### Configuration

```python
from tools import DependencyTrackingTool

tool = DependencyTrackingTool({
    'project_root': '.',
    'auto_analyze': False  # Auto-analyze on first use
})
```

### Actions

#### analyze
Run dependency analysis.

```python
result = tool.invoke({
    'action': 'analyze'
})
# Returns: {'success': True, 'stats': {...}}
```

#### get_stats
Get dependency statistics.

```python
result = tool.invoke({
    'action': 'get_stats'
})
# Returns: {
#     'success': True,
#     'stats': {
#         'total_files': 100,
#         'python_files': 50,
#         'orphaned_files_count': 5,
#         'circular_dependencies_count': 2
#     }
# }
```

#### get_file_deps
Get dependencies for a specific file.

```python
result = tool.invoke({
    'action': 'get_file_deps',
    'filepath': 'src/main.py'
})
# Returns: {
#     'success': True,
#     'filepath': 'src/main.py',
#     'dependencies': {
#         'imports': [...],
#         'imported_by': [...],
#         'language': 'python'
#     }
# }
```

#### find_circular
Find circular dependencies.

```python
result = tool.invoke({
    'action': 'find_circular'
})
# Returns: {
#     'success': True,
#     'circular_dependencies': [['file1.py', 'file2.py', 'file1.py']],
#     'count': 1
# }
```

#### find_orphaned
Find orphaned files.

```python
result = tool.invoke({
    'action': 'find_orphaned'
})
# Returns: {
#     'success': True,
#     'orphaned_files': ['unused.py', 'old_module.py'],
#     'count': 2
# }
```

#### export_json
Export dependencies as JSON.

```python
result = tool.invoke({
    'action': 'export_json',
    'output_path': '.project/dependencies/dependencies.json'  # Optional
})
# Returns: {'success': True, 'output_path': '...'}
```

#### export_markdown
Export dependencies as Markdown report.

```python
result = tool.invoke({
    'action': 'export_markdown',
    'output_path': '.project/dependencies/DEPENDENCY_REPORT.md'  # Optional
})
# Returns: {'success': True, 'output_path': '...'}
```

#### export_graphviz
Export dependencies as Graphviz DOT file.

```python
result = tool.invoke({
    'action': 'export_graphviz',
    'output_path': '.project/dependencies/dependencies.dot'  # Optional
})
# Returns: {'success': True, 'output_path': '...'}
```

#### get_graph
Get the dependency graph as a dictionary.

```python
result = tool.invoke({
    'action': 'get_graph'
})
# Returns: {
#     'success': True,
#     'graph': {'file1.py': ['file2.py', 'file3.py'], ...},
#     'node_count': N,
#     'edge_count': M
# }
```

---

## ContextCacheTool

**Purpose**: Manages context caching, workflow state, and result caching with TTL.

### Configuration

```python
from tools import ContextCacheTool

tool = ContextCacheTool({
    'project_root': '.',
    'default_ttl': 3600  # Default cache TTL in seconds
})
```

### Actions

#### cache_result
Cache an operation result.

```python
result = tool.invoke({
    'action': 'cache_result',
    'operation': 'expensive_computation',
    'params_dict': {'input': 'data', 'mode': 'fast'},
    'result': {'output': 'computed_result'},
    'ttl_seconds': 1800  # Optional, defaults to default_ttl
})
# Returns: {'success': True, 'operation': '...', 'ttl_seconds': 1800}
```

#### get_cached
Get cached result.

```python
result = tool.invoke({
    'action': 'get_cached',
    'operation': 'expensive_computation',
    'params_dict': {'input': 'data', 'mode': 'fast'}
})
# Returns: {
#     'success': True,
#     'operation': '...',
#     'cached': True,
#     'result': {'output': 'computed_result'}
# }
```

#### save_context
Save context data.

```python
result = tool.invoke({
    'action': 'save_context',
    'context_type': 'result',  # Types: todo, result, issue, status, etc.
    'name': 'build_output',
    'data': {'status': 'success', 'artifacts': [...]},
    'metadata': {'build_id': '12345'}  # Optional
})
# Returns: {'success': True, 'context_type': 'result', 'name': 'build_output'}
```

#### load_context
Load context data.

```python
result = tool.invoke({
    'action': 'load_context',
    'context_type': 'result',
    'name': 'build_output'
})
# Returns: {'success': True, 'context': {...}}
```

#### save_todo
Save TODO list.

```python
result = tool.invoke({
    'action': 'save_todo',
    'name': 'current_tasks',
    'todos': [{'task': 'Fix bug', 'status': 'pending'}]
})
# Returns: {'success': True, 'name': 'current_tasks', 'count': 1}
```

#### load_todo
Load TODO list.

```python
result = tool.invoke({
    'action': 'load_todo',
    'name': 'current_tasks'
})
# Returns: {'success': True, 'name': 'current_tasks', 'todos': [...]}
```

#### save_error
Save error information.

```python
result = tool.invoke({
    'action': 'save_error',
    'name': 'build_error',
    'error_data': {
        'error': 'Compilation failed',
        'file': 'main.py',
        'line': 42,
        'details': '...'
    }
})
# Returns: {'success': True, 'name': 'build_error'}
```

#### list_contexts
List contexts of a specific type.

```python
# List specific type
result = tool.invoke({
    'action': 'list_contexts',
    'context_type': 'result'
})

# List all types
result = tool.invoke({
    'action': 'list_contexts'
})
# Returns: {'success': True, 'all_contexts': {'result': [...], 'todo': [...]}}
```

#### clean_cache
Clean expired cache entries.

```python
result = tool.invoke({
    'action': 'clean_cache'
})
# Returns: {'success': True, 'removed_count': N}
```

#### invalidate_cache
Invalidate cache entries.

```python
# Invalidate specific entry
result = tool.invoke({
    'action': 'invalidate_cache',
    'operation': 'expensive_computation',
    'params_dict': {'input': 'data'}
})

# Invalidate all cache
result = tool.invoke({
    'action': 'invalidate_cache'
})
# Returns: {'success': True, 'invalidated_count': N}
```

---

## GitCommitEnhancedTool

**Purpose**: Provides enhanced git commit practices with detailed messages and summaries.

### Configuration

```python
from tools import GitCommitEnhancedTool

tool = GitCommitEnhancedTool({
    'project_root': '.',
    'repo_path': '.'  # Git repository path
})
```

### Actions

#### create_commit
Create an enhanced commit.

```python
result = tool.invoke({
    'action': 'create_commit',
    'message': 'feat: Add user authentication',
    'include_summary': True  # Generate commit_summary.md
})
# Returns: {
#     'success': True,
#     'commit_hash': 'abc123...',
#     'message': '...',
#     'summary_file': 'commit_summary.md'
# }
```

#### preview_commit
Preview what an enhanced commit would look like.

```python
result = tool.invoke({
    'action': 'preview_commit',
    'message': 'feat: Add user authentication'
})
# Returns: {'success': True, 'preview': {...}}
```

#### analyze_changes
Analyze staged changes.

```python
result = tool.invoke({
    'action': 'analyze_changes'
})
# Returns: {'success': True, 'analysis': {...}}
```

#### get_staged_changes
Get information about staged changes.

```python
result = tool.invoke({
    'action': 'get_staged_changes'
})
# Returns: {
#     'success': True,
#     'changes': {
#         'added': ['new_file.py'],
#         'modified': ['main.py'],
#         'deleted': ['old_file.py'],
#         'renamed': []
#     },
#     'total_files': 3
# }
```

#### get_diff_stats
Get diff statistics.

```python
result = tool.invoke({
    'action': 'get_diff_stats'
})
# Returns: {
#     'success': True,
#     'stats': {
#         'files_changed': 3,
#         'insertions': 50,
#         'deletions': 20
#     }
# }
```

#### generate_message
Generate a conventional commit message.

```python
result = tool.invoke({
    'action': 'generate_message',
    'message_type': 'feat',  # feat, fix, docs, style, refactor, test, chore
    'scope': 'auth',         # Optional scope
    'description': 'Add login functionality'
})
# Returns: {
#     'success': True,
#     'message': 'feat(auth): Add login functionality',
#     'type': 'feat',
#     'scope': 'auth',
#     'description': 'Add login functionality'
# }
```

#### generate_summary
Generate a summary for a commit.

```python
result = tool.invoke({
    'action': 'generate_summary',
    'commit_hash': 'abc123'  # Optional, defaults to HEAD
})
# Returns: {
#     'success': True,
#     'summary': {
#         'commit_hash': 'abc123',
#         'author': 'John Doe <john@example.com>',
#         'date': '...',
#         'message': '...',
#         'changes': {...}
#     }
# }
```

---

## Usage Examples

### Complete Agent Integration

```python
from tools import (
    ProjectManagementTool,
    ChatHistoryTool,
    ContextCacheTool,
    ToolRegistry
)

class MyAgent:
    def __init__(self, project_root='.'):
        self.project_root = project_root
        
        # Option 1: Create tool instances directly
        self.project_tool = ProjectManagementTool({'project_root': project_root})
        self.chat_tool = ChatHistoryTool({'project_root': project_root})
        self.cache_tool = ContextCacheTool({'project_root': project_root})
        
        # Option 2: Use ToolRegistry
        registry = ToolRegistry.get_instance()
        self.project_tool = registry.get('project_management') or self.project_tool
    
    def process_with_caching(self, data):
        """Process data with result caching."""
        # Check cache
        cached = self.cache_tool.invoke({
            'action': 'get_cached',
            'operation': 'process_data',
            'params_dict': {'data': str(data)}
        })
        
        if cached['cached']:
            return cached['result']
        
        # Process data
        result = self._expensive_processing(data)
        
        # Cache result
        self.cache_tool.invoke({
            'action': 'cache_result',
            'operation': 'process_data',
            'params_dict': {'data': str(data)},
            'result': result,
            'ttl_seconds': 3600
        })
        
        return result
    
    def save_conversation(self, session_id, message):
        """Save a conversation message."""
        self.chat_tool.invoke({
            'action': 'save_message',
            'session_id': session_id,
            'message': message
        })
    
    def save_task_progress(self, tasks):
        """Save task progress."""
        self.project_tool.invoke({
            'action': 'save_todo',
            'name': 'current_sprint',
            'todos': tasks
        })
```

---

## Best Practices

### 1. Tool Registration

Register tools globally for reuse across agents:

```python
from tools import ToolRegistry, ProjectManagementTool

registry = ToolRegistry.get_instance()
registry.register(ProjectManagementTool({'project_root': '.'}))

# Later, retrieve from registry
tool = registry.get('project_management')
```

### 2. Error Handling

Always check the `success` field in results:

```python
result = tool.invoke({'action': 'load_memory', 'key': 'my_key'})

if result['success']:
    data = result['data']
else:
    print(f"Error: {result['error']}")
```

### 3. Cache Management

Clean expired cache regularly:

```python
# Clean cache periodically (e.g., daily)
cache_tool.invoke({'action': 'clean_cache'})
```

### 4. Session Management

Clean old chat sessions to save space:

```python
# Prune old messages (> 30 days)
chat_tool.invoke({'action': 'prune_history'})
```

### 5. Dependency Analysis

Run dependency analysis before major refactoring:

```python
# Analyze dependencies
dep_tool.invoke({'action': 'analyze'})

# Check for circular dependencies
circular = dep_tool.invoke({'action': 'find_circular'})

if circular['count'] > 0:
    print(f"Found {circular['count']} circular dependencies!")
```

### 6. Conventional Commits

Use conventional commit format for better changelog generation:

```python
# Generate conventional commit message
message = git_tool.invoke({
    'action': 'generate_message',
    'message_type': 'feat',
    'scope': 'api',
    'description': 'Add user endpoints'
})['message']

# Create commit
git_tool.invoke({
    'action': 'create_commit',
    'message': message,
    'include_summary': True
})
```

---

## See Also

- [Migration Guide](./development/CHANGELOG.md) - Migrating from old integration layer
- [Tool Base Class](../tools/base.py) - Tool architecture details
- [Tool Registry](../tools/registry.py) - Tool registration system
- [Tests](../tests/unit/tools/test_new_tools.py) - Tool usage examples
