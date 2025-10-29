# Chat History and Summarization Guide

This guide explains how to use the chat history and intelligent summarization features in the AI Agent Console, which help maintain context across long conversations.

## Overview

The Chat History system provides:

- **Automatic History Tracking**: All conversations are automatically saved
- **Intelligent Summarization**: Long conversations are automatically compressed
- **Context Preservation**: Important information is retained across sessions
- **Project-Scoped History**: Each project maintains its own chat history
- **Summary Generation**: Generate summaries on demand or automatically
- **History Retrieval**: Access past conversations easily

## Quick Start

### Viewing Chat History

View the chat history for the current project:

```bash
python main.py chat-history --limit 20
```

View history for a specific project:

```bash
python main.py chat-history --project "My Project" --limit 10
```

### Generating Summaries

Create a summary of the current project's chat history:

```bash
python main.py summarize-chat
```

Summarize a specific project's history:

```bash
python main.py summarize-chat --project "Data Analysis"
```

## Features

### Automatic History Saving

All chat messages are automatically saved:

- **User Messages**: Everything you type
- **Assistant Responses**: All AI responses
- **System Messages**: Important system notifications
- **Metadata**: Timestamps, project context, etc.

### Intelligent Summarization

The system can automatically compress long conversations:

- **Configurable Triggers**: Set when summarization happens
- **Context Preservation**: Important information is retained
- **Summary Integration**: Summaries become part of the context
- **Incremental Summaries**: Can summarize summaries for very long conversations

### Summarization Strategies

Choose when to trigger summarization:

1. **Message Count**: After N messages (default: 20)
2. **Token Count**: After N tokens (default: 8000)
3. **Time-Based**: After certain time periods
4. **Manual**: Only when explicitly requested

## Architecture

### Chat History Structure

Each history entry contains:

```python
{
    "history_id": "unique-uuid",
    "project_id": "project-uuid",
    "messages": [
        {
            "role": "user",
            "content": "Message content",
            "timestamp": "2025-10-13T12:00:00",
            "metadata": {},
            "tokens": 10
        }
    ],
    "summaries": [
        {
            "summary_text": "Summary of conversation",
            "original_message_count": 20,
            "original_token_count": 5000,
            "created_at": "2025-10-13T12:30:00",
            "strategy_used": "message_count"
        }
    ]
}
```

### Storage Structure

Chat history is stored per project:

```
./chat_history/
├── project_{project-id-1}.json    # History for project 1
├── project_{project-id-2}.json    # History for project 2
└── ...
```

### Summarization Process

1. **Trigger Detection**: System detects when summarization is needed
2. **Context Building**: Builds prompt with messages to summarize
3. **LLM Summarization**: Uses LLM to generate summary
4. **History Compression**: Replaces old messages with summary
5. **Recent Preservation**: Keeps most recent messages intact

## Programmatic Usage

### Using ChatHistoryManager

```python
from core import ChatHistoryManager
from pathlib import Path

# Initialize the manager
chm = ChatHistoryManager(
    storage_path=Path("./chat_history"),
    llm_router=llm_router,
    auto_save=True,
    enable_auto_summarization=True,
    summarize_after_messages=20,
    keep_recent_messages=10
)

# Create history for a project
history_id = chm.create_history(project_id="proj-123")

# Add messages
chm.add_user_message(history_id, "Hello, AI!")
chm.add_assistant_message(history_id, "Hi! How can I help?")
chm.add_system_message(history_id, "Task completed")

# Get messages
messages = chm.get_messages(history_id, limit=20)

# Get recent messages only
recent = chm.get_recent_messages(history_id, count=5)

# Generate summary
summary_text = chm.summarize_history(history_id, keep_recent=10)

# Get all summaries
summaries = chm.get_summaries(history_id)

# Get full context (includes summaries)
context = chm.get_full_context(history_id)

# Get statistics
stats = chm.get_history_stats(history_id)

# Clear history
chm.clear_history(history_id)

# Export history
chm.export_history(history_id, Path("./backup/history.json"))
```

### Integration with Engine

The Engine automatically manages chat history:

```python
from core import Engine

engine = Engine()
engine.initialize()

# Get chat history for current project
history = engine.get_chat_history(limit=20)

# Get history for specific project
history = engine.get_chat_history(project_id="proj-123", limit=10)

# Generate summary
summary = engine.summarize_chat_history()

# Summary for specific project
summary = engine.summarize_chat_history(project_id="proj-123")
```

## Configuration

### Summarization Settings

Configure summarization behavior:

```python
chm = ChatHistoryManager(
    storage_path=Path("./chat_history"),
    llm_router=llm_router,
    
    # Enable/disable auto-summarization
    enable_auto_summarization=True,
    
    # Summarization strategy
    summarization_strategy=SummarizationStrategy.MESSAGE_COUNT,
    
    # Thresholds
    summarize_after_messages=20,    # After this many messages
    summarize_after_tokens=8000,    # Or after this many tokens
    
    # What to keep
    keep_recent_messages=10,        # Keep this many recent messages
    
    # Persistence
    auto_save=True
)
```

### Summarization Strategies

Choose from different strategies:

```python
from core.chat_history import SummarizationStrategy

# After N messages
strategy=SummarizationStrategy.MESSAGE_COUNT

# After N tokens
strategy=SummarizationStrategy.TOKEN_COUNT

# After time period
strategy=SummarizationStrategy.TIME_BASED

# Only manual
strategy=SummarizationStrategy.MANUAL
```

## Best Practices

### When to Summarize

1. **Long Conversations**: Automatically summarize after 20-30 messages
2. **Token Limits**: Summarize before hitting model context limits
3. **Session Boundaries**: Summarize at natural conversation breaks
4. **Before Switching**: Summarize before switching projects

### What to Keep

1. **Recent Messages**: Always keep the most recent 5-10 messages
2. **Important Context**: Ensure summaries capture key information
3. **Decisions**: Preserve important decisions and outcomes
4. **Action Items**: Keep track of pending tasks

### Performance Tips

1. **Adjust Thresholds**: Tune based on your needs
2. **Manual Summaries**: Use manual mode for better control
3. **Regular Cleanup**: Clear old histories periodically
4. **Export Backups**: Keep backups of important conversations

## Advanced Features

### Custom Summarization

Build custom prompts for summarization:

```python
# The default summarization prompt captures:
# - Key topics discussed
# - Important decisions
# - Context for future conversation
# - Action items
# - Integrates with previous summaries
```

### Summary Chaining

For very long conversations, summaries can be chained:

1. First summarization creates summary of first 20 messages
2. More messages accumulate
3. Second summarization incorporates first summary
4. Creates comprehensive summary of all interactions

### History Analysis

Get insights from chat history:

```python
# Get statistics
stats = chm.get_history_stats(history_id)

# Statistics include:
# - Total message count
# - Total token count
# - Number of summaries
# - Creation/update times
# - Project association
```

### Message Search

Search through history (coming soon):

```python
# Search messages
results = chm.search_messages(
    history_id=history_id,
    query="API integration",
    role="user",
    limit=10
)
```

## Troubleshooting

### Summary Not Generated

If summarization fails:

1. Check LLM router is configured
2. Verify LLM is responding
3. Check token limits aren't exceeded
4. Review logs for errors

### History Not Persisting

If history isn't saved:

1. Verify auto_save is enabled
2. Check storage directory permissions
3. Ensure disk space is available
4. Review logs for write errors

### Context Not Loading

If context doesn't load:

1. Check project ID is correct
2. Verify history file exists
3. Check file permissions
4. Try reloading the history

## CLI Reference

### Commands

- `chat-history` - View chat history
  - `--limit, -n` - Number of messages to show
  - `--project, -p` - Project name (partial match)
  
- `summarize-chat` - Generate summary
  - `--project, -p` - Project name

### Examples

```bash
# View last 10 messages for current project
python main.py chat-history --limit 10

# View history for specific project
python main.py chat-history --project "Data Analysis" -n 20

# Generate summary for current project
python main.py summarize-chat

# Summarize specific project
python main.py summarize-chat --project "AI Research"
```

## Integration with Other Features

### Project Management

Chat history is automatically scoped to projects:

- Each project has its own independent history
- Switching projects switches chat context
- Deleting a project deletes its history

### Memory System

Chat history complements the memory system:

- Memory: Short-term conversation context
- Chat History: Long-term conversation storage
- Both work together to maintain context

### Agents

Agents can access chat history for context:

- Summaries are included in agent context
- Recent messages provide immediate context
- Historical context helps with continuity

## Examples

### Resume a Conversation

```python
# Load previous context
engine = Engine()
engine.initialize()

# Get recent history
history = engine.get_chat_history(limit=10)

# Review context
for msg in history:
    print(f"{msg['role']}: {msg['content']}")

# Get summary for broader context
summary = engine.summarize_chat_history()
print(f"Previous context: {summary}")

# Continue conversation with full context
```

### Export Conversation

```python
# Export for documentation or analysis
chm = engine.chat_history_manager
history = chm.get_history_by_project(project_id)

if history:
    chm.export_history(
        history.history_id,
        Path("./exports/conversation_export.json")
    )
```

### Analyze Conversation Patterns

```python
# Get statistics
stats = chm.get_history_stats(history_id)

print(f"Total messages: {stats['message_count']}")
print(f"Total tokens: {stats['total_tokens']}")
print(f"Summaries created: {stats['summary_count']}")
print(f"Duration: {stats['created_at']} to {stats['updated_at']}")
```

## Future Enhancements

Planned features:

- Advanced search capabilities
- Message tagging and categorization
- Conversation analytics
- Export to multiple formats (Markdown, PDF)
- Conversation branching
- Multi-user conversation support
- Conversation templates
- Smart context loading
