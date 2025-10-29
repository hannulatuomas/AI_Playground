# Agent Memory System Documentation

## Overview

The AI Agent Console includes a robust **Memory System** that provides conversation history tracking, context persistence, and intelligent memory management across agent interactions. This system enables agents to maintain context across multiple exchanges, remember previous interactions, and provide more coherent and contextually-aware responses.

## Architecture

### Core Components

1. **MemoryManager**: Central memory management system
2. **MemorySession**: Individual conversation sessions
3. **Message**: Individual message records
4. **MessageRole**: Message role enumeration (USER, AGENT, SYSTEM)

### Integration Points

- **Base Agent Class**: All agents have access to memory through `self.memory_manager`
- **Orchestrator**: Manages memory sessions during task execution
- **Engine**: Initializes and configures the memory manager

## Features

### 1. Conversation History Tracking

The memory system automatically tracks all interactions:

- **User Messages**: User inputs and task requests
- **Agent Messages**: Agent responses and outputs
- **System Messages**: System notifications and summaries

```python
# Messages are automatically tracked during orchestration
manager.add_user_message(session_id, "Create a Python script")
manager.add_agent_message(session_id, "Script created successfully", "code_editor")
```

### 2. Session Management

Organize conversations into sessions:

```python
# Create a new session
session_id = manager.create_session(
    max_context_window=4096,
    metadata={'project': 'my_project'}
)

# Get session information
session_info = manager.get_session_info(session_id)
print(f"Messages: {session_info['message_count']}")
print(f"Tokens: {session_info['total_tokens']}")

# List all sessions
sessions = manager.list_sessions()

# Delete old sessions
manager.delete_session(session_id)
```

### 3. Context Retrieval

Agents can retrieve relevant conversation context:

```python
# Get recent conversation history
history = manager.get_conversation_history(
    session_id=session_id,
    limit=10,
    include_system=True
)

# Get context for a specific agent
context = manager.get_context_for_agent(
    session_id=session_id,
    agent_name="code_editor",
    max_messages=10
)
```

### 4. Memory Search

Search through conversation history:

```python
# Search messages
results = manager.search_messages(
    session_id=session_id,
    query="Python script",
    role=MessageRole.AGENT,
    limit=5
)
```

### 5. Automatic Memory Summarization

When the context window is exceeded, the memory system automatically:

1. Identifies older messages to summarize
2. Uses LLM to generate a concise summary
3. Replaces old messages with the summary
4. Preserves recent messages for immediate context

This ensures agents always have relevant context without exceeding token limits.

```python
# Summarization is automatic, but can also be triggered manually
manager._summarize_session(session_id)
```

### 6. Persistent Storage

Sessions are automatically saved to disk:

- **Location**: `memory_storage/` directory
- **Format**: JSON files (one per session)
- **Auto-save**: Enabled by default

```python
# Manual save operations
manager.save_all_sessions()
manager.load_all_sessions()

# Cleanup old sessions
deleted = manager.cleanup_old_sessions(days=30)
```

## Usage in Agents

### Basic Memory Access

Agents inherit memory capabilities from the base Agent class:

```python
class MyCustomAgent(Agent):
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        session_id = context.get('session_id')
        
        if session_id and self.memory_manager:
            # Get previous conversation context
            memory_context = self._get_memory_context(session_id, max_messages=5)
            
            # Format context for LLM prompt
            context_str = self._format_memory_context_for_prompt(memory_context)
            
            # Include in your prompt
            prompt = f"{context_str}\n\nNew task: {task}"
            
            # ... execute task ...
            
            # Add result to memory
            self._add_to_memory(
                session_id=session_id,
                message="Task completed successfully",
                metadata={'task_type': 'custom_operation'}
            )
        
        return self._build_success_result("Task completed")
```

### Advanced Memory Usage

```python
class AdvancedAgent(Agent):
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        session_id = context.get('session_id')
        
        if not session_id or not self.memory_manager:
            # No memory available, proceed without context
            return self._execute_without_memory(task)
        
        # Get relevant context from memory
        memory_context = self.memory_manager.get_context_for_agent(
            session_id=session_id,
            agent_name=self.name,
            max_messages=10
        )
        
        # Search for related previous tasks
        related_tasks = self.memory_manager.search_messages(
            session_id=session_id,
            query=task[:50],  # Search using task keywords
            limit=3
        )
        
        # Build enhanced prompt with context
        prompt = self._build_prompt_with_context(
            task=task,
            recent_context=memory_context,
            related_context=related_tasks
        )
        
        # Execute with LLM
        result = self._get_llm_response(prompt)
        
        # Store result in memory
        self._add_to_memory(
            session_id=session_id,
            message=result.get('response'),
            metadata={
                'task': task,
                'success': True,
                'tokens_used': result.get('usage', {}).get('total_tokens')
            }
        )
        
        return self._build_success_result(
            message="Task completed with memory context",
            data=result
        )
```

## Configuration

### Memory Manager Initialization

The memory manager is automatically initialized by the Engine:

```python
# In core/engine.py
memory_manager = MemoryManager(
    storage_path=Path("memory_storage"),  # Where to store sessions
    default_max_context_window=4096,       # Default token limit
    auto_save=True,                        # Auto-save after changes
    enable_summarization=True,             # Enable auto-summarization
    llm_router=self.router                 # LLM for summarization
)
```

### Custom Configuration

You can customize memory behavior:

```python
# Create custom memory manager
custom_manager = MemoryManager(
    storage_path=Path("my_memory"),
    default_max_context_window=8192,    # Larger context window
    auto_save=False,                    # Manual save control
    enable_summarization=False          # Disable summarization
)

# Create session with custom settings
session_id = custom_manager.create_session(
    max_context_window=16384,           # Session-specific limit
    metadata={
        'user_id': 'user123',
        'project': 'important_project'
    }
)
```

## Memory Data Structure

### Message Structure

```python
{
    'role': 'user' | 'agent' | 'system',
    'content': 'Message content',
    'agent_name': 'code_editor',  # For agent messages
    'timestamp': '2025-10-10T10:30:00',
    'metadata': {
        'success': True,
        'task_type': 'file_creation'
    },
    'tokens': 150  # Estimated token count
}
```

### Session Structure

```python
{
    'session_id': 'abc123...',
    'messages': [<Message>, <Message>, ...],
    'created_at': '2025-10-10T10:00:00',
    'updated_at': '2025-10-10T10:30:00',
    'metadata': {
        'project': 'my_project',
        'summary': 'Conversation summary...'
    },
    'max_context_window': 4096
}
```

## Best Practices

### 1. Session Management

- **Create sessions** for related conversations
- **Reuse sessions** for follow-up tasks
- **Clean up** old sessions periodically

```python
# Reuse session for related tasks
context = {'session_id': existing_session_id}
result = orchestrator.execute_task(task, agent_sequence, context)
```

### 2. Memory in Prompts

Always include memory context in LLM prompts:

```python
memory_context = self._get_memory_context(session_id, max_messages=5)
context_str = self._format_memory_context_for_prompt(memory_context)

prompt = f"""
{context_str}

Current task: {task}

Please complete the task considering the previous conversation context.
"""
```

### 3. Metadata Usage

Use metadata to enhance memory:

```python
self._add_to_memory(
    session_id=session_id,
    message="File created successfully",
    metadata={
        'operation': 'file_create',
        'file_path': '/path/to/file.py',
        'file_size': 1024,
        'success': True
    }
)
```

### 4. Context Window Management

Monitor and manage context windows:

```python
session = manager.get_session(session_id)
if session.is_context_window_exceeded():
    # Trigger summarization or cleanup
    manager._summarize_session(session_id)
```

## API Reference

### MemoryManager Methods

#### Session Management
- `create_session(session_id=None, max_context_window=None, metadata=None) -> str`
- `get_session(session_id: str) -> MemorySession`
- `delete_session(session_id: str) -> bool`
- `list_sessions() -> List[str]`
- `get_session_info(session_id: str) -> Dict[str, Any]`

#### Message Management
- `add_message(session_id, role, content, agent_name=None, metadata=None) -> bool`
- `add_user_message(session_id, content, metadata=None) -> bool`
- `add_agent_message(session_id, content, agent_name, metadata=None) -> bool`
- `add_system_message(session_id, content, metadata=None) -> bool`

#### Memory Retrieval
- `get_conversation_history(session_id, limit=None, include_system=True) -> List[Dict]`
- `get_context_for_agent(session_id, agent_name, max_messages=10) -> List[Dict]`
- `search_messages(session_id, query, role=None, agent_name=None, limit=10) -> List[Dict]`

#### Persistence
- `save_all_sessions() -> int`
- `load_all_sessions() -> int`
- `cleanup_old_sessions(days=30) -> int`

### Agent Memory Methods

#### Base Agent Class Methods
- `_get_memory_context(session_id, max_messages=10) -> List[Dict]`
- `_add_to_memory(session_id, message, metadata=None) -> bool`
- `_format_memory_context_for_prompt(context: List[Dict]) -> str`

## Examples

### Example 1: Multi-Turn Conversation

```python
# First interaction
session_id = manager.create_session()
manager.add_user_message(session_id, "Create a Python hello world script")
manager.add_agent_message(session_id, "Created hello.py", "code_editor")

# Second interaction (with context)
manager.add_user_message(session_id, "Now add a function to greet by name")
context = manager.get_conversation_history(session_id)
# Agent can see previous interaction about hello.py
manager.add_agent_message(session_id, "Updated hello.py with greet function", "code_editor")
```

### Example 2: Project Context Preservation

```python
# Start project session
session_id = manager.create_session(metadata={'project': 'web_app'})

# Multiple agents working with shared context
manager.add_user_message(session_id, "Plan a Flask web application")
manager.add_agent_message(session_id, "Created project plan", "code_planner")

manager.add_user_message(session_id, "Create the main app file")
# code_editor can see the plan from code_planner
manager.add_agent_message(session_id, "Created app.py", "code_editor")

manager.add_user_message(session_id, "Add database models")
# code_editor knows about the Flask app and existing structure
manager.add_agent_message(session_id, "Created models.py", "code_editor")
```

### Example 3: Memory Search

```python
# Search for previous Python-related tasks
results = manager.search_messages(
    session_id=session_id,
    query="Python",
    role=MessageRole.AGENT,
    limit=5
)

for msg in results:
    print(f"[{msg['timestamp']}] {msg['agent_name']}: {msg['content']}")
```

## Troubleshooting

### Memory Not Persisting

**Issue**: Sessions not saved to disk

**Solutions**:
1. Check that `auto_save=True` in MemoryManager initialization
2. Verify write permissions on `memory_storage/` directory
3. Manually call `manager.save_all_sessions()`

### Context Window Exceeded

**Issue**: "Context window exceeded" errors

**Solutions**:
1. Enable summarization: `enable_summarization=True`
2. Increase context window: `max_context_window=8192`
3. Reduce `max_messages` when retrieving context
4. Manually cleanup old messages

### Memory Not Available in Agent

**Issue**: `self.memory_manager` is None

**Solutions**:
1. Ensure Engine initialized memory manager
2. Check agent instantiation includes `memory_manager` parameter
3. Update agent's `__init__` to accept `memory_manager`

## Performance Considerations

### Token Estimation

The system uses a simple heuristic (4 characters ≈ 1 token). For accurate counts, integrate a proper tokenizer:

```python
# Override token estimation
def custom_token_count(text: str) -> int:
    # Use your tokenizer
    import tiktoken
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

# Patch the session method
session._estimate_tokens = custom_token_count
```

### Storage Optimization

- Clean up old sessions regularly
- Use metadata instead of full messages for summaries
- Compress or archive old session files

### Memory Usage

- Monitor session count with `len(manager)`
- Clear cached sessions periodically
- Use session-specific context windows

## Future Enhancements

Potential improvements for the memory system:

1. **Vector Database Integration**: Use embeddings for semantic search
2. **Multi-User Support**: Isolate memory by user ID
3. **Memory Sharing**: Share context across related sessions
4. **Advanced Summarization**: Multi-level summarization strategies
5. **Memory Importance**: Prioritize important messages
6. **Cross-Session Search**: Search across all sessions
7. **Memory Analytics**: Track memory usage patterns

## Conclusion

The AI Agent Console Memory System provides a production-ready solution for maintaining conversation context across agent interactions. It seamlessly integrates with the existing architecture while providing powerful features for memory management, persistence, and retrieval.

For questions or issues, please refer to the main project documentation or submit an issue on the project repository.
