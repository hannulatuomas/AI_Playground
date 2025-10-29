# API Documentation

## Core Modules

### LLMInterface

Handles interaction with llama.cpp.

```python
from core import LLMInterface, LLMConfig

# Create configuration
config = LLMConfig(
    model_path="path/to/model.gguf",
    executable_path="path/to/llama-cli",
    context_size=4096,
    temperature=0.7
)

# Initialize interface
llm = LLMInterface(config)

# Generate text
response = llm.generate("Your prompt here", max_tokens=1024)
```

### PromptEngine

Manages prompts for different tasks and languages.

```python
from core import PromptEngine, LearningDB, ProjectManager

db = LearningDB()
pm = ProjectManager()  # Optional for project-aware prompts
engine = PromptEngine(learning_db=db, project_manager=pm)

# Build a standard prompt
prompt = engine.build_prompt(
    task_type='generate',
    language='python',
    content='Create a sorting function'
)

# Build project-aware prompt (NEW v1.1.0)
prompt = engine.build_prompt(
    task_type='generate',
    language='python',
    content='Add authentication to API',
    include_project_context=True,
    project_files=['api/routes.py', 'api/models.py']
)

# Build prompt specifically for projects (NEW v1.1.0)
prompt = engine.build_project_prompt(
    task_description="Refactor database connection",
    relevant_files=['db/connection.py', 'db/models.py'],
    language='python'
)

# Get supported languages and tasks
languages = engine.get_supported_languages()
tasks = engine.get_supported_tasks()
```

### LearningDB

Stores and retrieves learning data for self-improvement.

```python
from core import LearningDB

db = LearningDB("data/db/learning.db")

# Add interaction
db.add_entry(
    query="Create a function",
    language="python",
    response="def func(): pass",
    task_type="generate",
    success=True,
    project_id="my-web-app",  # NEW v1.1.0
    file_path="src/utils.py"   # NEW v1.1.0
)

# Get statistics
stats = db.get_statistics()

# Get learnings
learnings = db.get_relevant_learnings(
    language="python",
    task_type="generate",
    project_id="my-web-app"  # NEW v1.1.0: Filter by project
)

# Get project-specific learnings (NEW v1.1.0)
project_learnings = db.get_project_learnings("my-web-app", limit=10)

# Get file history (NEW v1.1.0)
file_history = db.get_file_history("my-web-app", "src/utils.py", limit=5)
```

### ProjectManager (NEW v1.1.0)

Manages project-level operations including file indexing, summarization, and chunked reading.

```python
from core import ProjectManager, LLMInterface, load_config_from_file

# Initialize with LLM for summarization
config = load_config_from_file()
llm = LLMInterface(config)
pm = ProjectManager(llm_interface=llm)

# Set project root
pm.set_root_folder("/path/to/project")
root = pm.get_root_folder()

# Index all files (recursive)
file_index = pm.index_files(force_refresh=False)
print(f"Indexed {len(file_index)} files")

# Get file content with chunking
content, is_truncated = pm.get_file_content(
    relative_path="src/main.py",
    chunk_size=2000,
    start_line=0,
    max_lines=None
)

# Get file as chunks for large files
chunks = pm.get_file_chunks("src/large_file.py", chunk_size=2000)
for start_line, content in chunks:
    print(f"Chunk starting at line {start_line}")

# Summarize a file using LLM
summary = pm.summarize_file("src/main.py", force=False)
print(f"Summary: {summary}")

# Get list of files with filters
py_files = pm.get_file_list(language="python")
test_files = pm.get_file_list(pattern="test")

# Get project statistics
stats = pm.get_project_stats()
print(f"Total files: {stats['total_files']}")
print(f"Total size: {stats['total_size_mb']} MB")
print(f"Languages: {stats['languages']}")

# Manage exclusion patterns
pm.add_exclude_pattern("custom_dir")
pm.remove_exclude_pattern("custom_dir")

# Clear index
pm.clear_index()
```

#### ProjectManager Features
- **Recursive indexing** with automatic exclusions (.git, node_modules, etc.)
- **Binary file filtering** (25+ extensions: .exe, .dll, .jpg, .png, etc.)
- **Text file support** (30+ extensions: .py, .js, .cpp, etc.)
- **Large file handling** via configurable chunking (default 2000 lines)
- **File summarization** with LLM and SHA256-based change detection
- **Persistent index** saved to data/project_index.json
- **Multiple encodings** (UTF-8, Latin-1, CP1252, ISO-8859-1)
- **Cross-platform** path handling

## Feature Modules

### CodeGenerator

Generates code for various tasks.

```python
from features import CodeGenerator

generator = CodeGenerator(llm, prompt_engine, learning_db)

# Generate code
result = generator.generate_code(
    task="Create a web server",
    language="python"
)

print(result['code'])
print(result['explanation'])

# Provide feedback
generator.provide_feedback(success=True)
```

### Debugger

Debugs and fixes code.

```python
from features import Debugger

debugger = Debugger(llm, prompt_engine, learning_db)

# Debug code
result = debugger.debug_code(
    code="def func()\n    pass",
    language="python",
    error_message="SyntaxError: invalid syntax"
)

print(result['fixed_code'])
print(result['explanation'])

# Analyze error patterns
analysis = debugger.analyze_error_patterns("python")
print(analysis['most_common'])

# Get preventive suggestions
suggestions = debugger.suggest_preventive_measures("python")
```

### LanguageSupport

Provides language-specific functionality.

```python
from features import LanguageSupport

support = LanguageSupport()

# Detect language
lang, framework = support.detect_language(code, filename="test.py")

# Get language info
info = support.get_language_info("python")

# Validate syntax
is_valid, error = support.validate_code_syntax(code, "python")

# Get supported languages
languages = support.get_supported_languages()
```

### ProjectNavigator (NEW v1.2.0)

Intelligent project file navigation and operations.

```python
from features import ProjectNavigator
from core import ProjectManager, LLMInterface, load_config_from_file

# Initialize
config = load_config_from_file()
llm = LLMInterface(config)
pm = ProjectManager(llm_interface=llm)
pm.set_root_folder("/path/to/project")

navigator = ProjectNavigator(pm, llm)

# Scan for changes
changes = navigator.scan_project(summarize_new=True)
print(f"New: {len(changes['new'])}")
print(f"Modified: {len(changes['modified'])}")
print(f"Deleted: {len(changes['deleted'])}")

# Search files
results = navigator.search_files(
    query="database connection",
    max_results=10,
    search_in=['python']  # Optional language filter
)
for result in results:
    print(f"{result['path']} (score: {result['score']})")

# Get relevant context for task
context = navigator.get_relevant_context(
    task="Add JWT authentication to API",
    max_files=5,
    use_llm_ranking=True,
    language_filter="python"
)
for file_info in context:
    print(f"{file_info['path']}: {file_info['summary'][:100]}")

# Edit file safely
changes = [
    {
        'type': 'replace',
        'start_line': 10,
        'end_line': 15,
        'new_content': 'def new_function():\n    pass'
    },
    {
        'type': 'insert',
        'line': 20,
        'new_content': '# TODO: Add error handling'
    }
]

# Preview changes (dry-run)
result = navigator.edit_file('src/main.py', changes, dry_run=True)
print(result['diff'])

# Apply changes with backup
result = navigator.edit_file(
    rel_path='src/main.py',
    changes=changes,
    create_backup=True,
    dry_run=False
)
if result['success']:
    print(f"Backup: {result['backup_path']}")

# List backups
backups = navigator.list_backups('src/main.py')
for backup in backups:
    print(f"{backup['timestamp']}: {backup['backup_path']}")

# Restore from backup
navigator.restore_from_backup(backups[0]['backup_path'])
```

#### ProjectNavigator Features

**Scanning**:
- Incremental change detection via timestamps
- Auto-summarize new/modified files
- Track new, modified, deleted files

**Search**:
- Multi-term keyword matching
- Relevance scoring (0.0-2.5 range)
- Language filtering
- Max 100 results for large codebases
- Match details provided

**Editing**:
- 4 change types: replace, insert, delete, diff
- Automatic timestamped backups
- Unified diff generation
- Dry-run mode
- Rollback on failure
- Index invalidation

**Context Selection**:
- LLM-powered relevance ranking
- Fallback keyword ranking
- Configurable max files
- Language filtering
- Scored results (0.0-1.0)

**Backup Management**:
- Timestamped backups: `filename.YYYYMMDD_HHMMSS.bak`
- Organized by directory structure
- List and restore functionality

## Configuration

### Config File Format (data/config.json)

```json
{
  "model_path": "/path/to/model.gguf",
  "executable_path": "/path/to/llama-cli",
  "context_size": 4096,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "repeat_penalty": 1.1,
  "threads": 4,
  "gpu_layers": 0
}
```

### Loading and Saving Config

```python
from core.llm_interface import load_config_from_file, save_config_to_file

# Load config
config = load_config_from_file("data/config.json")

# Save config
save_config_to_file(config, "data/config.json")
```

## CLI Commands

### Code Generation
```bash
/gen <language> <description>
```
Example:
```bash
/gen python Create a function to calculate fibonacci numbers
```

### Debugging
```bash
/debug <language> [file]
```
Examples:
```bash
/debug cpp mycode.cpp
/debug python
# Then paste code and provide error message
```

### Code Operations
```bash
/explain <language>    # Explain code
/optimize <language>   # Optimize code
/refactor <language>   # Refactor code
```

### Information
```bash
/languages    # List supported languages
/stats        # Show statistics
/errors <lang> # Show error patterns
```

### Feedback
```bash
/feedback <y/n>  # Provide feedback on last response
```

## Extending the Assistant

### Adding a New Language

1. Edit `src/features/lang_support.py`
2. Add language to `language_info` dictionary:

```python
'newlang': {
    'extensions': ['.ext'],
    'comment': '#',
    'common_keywords': ['keyword1', 'keyword2'],
    'frameworks': []
}
```

3. Edit `src/core/prompt_engine.py`
4. Add language-specific system prompt:

```python
'newlang': """You are a NewLang expert. Follow best practices..."""
```

### Adding a New Task Type

1. Edit `src/core/prompt_engine.py`
2. Add task template to `task_templates`:

```python
'newtask': PromptTemplate(
    system="You are performing a new task.",
    user_prefix="Task: {language}\n\n",
    user_suffix="\n\nProvide solution."
)
```

### Creating Custom Features

1. Create new module in `src/features/`
2. Import core components:

```python
from core import LLMInterface, PromptEngine, LearningDB

class MyFeature:
    def __init__(self, llm, prompt_engine, learning_db):
        self.llm = llm
        self.prompt_engine = prompt_engine
        self.learning_db = learning_db
    
    def my_method(self, input_data):
        # Your implementation
        pass
```

3. Integrate in `src/main.py` or `src/ui/cli.py`

## Error Handling

### Common Errors and Solutions

**FileNotFoundError: llama.cpp executable not found**
- Verify llama.cpp is built
- Check executable path in config
- Try running llama.cpp directly

**FileNotFoundError: Model file not found**
- Download a GGUF model
- Place in data/models/
- Update config with correct path

**TimeoutError: Generation timed out**
- Reduce max_tokens
- Reduce context_size
- Use a smaller/faster model

**RuntimeError: llama.cpp failed**
- Check llama.cpp works independently
- Verify model compatibility
- Check system resources (RAM)

## Database Schema

### interactions table (UPDATED v1.1.0)
- id (INTEGER PRIMARY KEY)
- query (TEXT)
- language (TEXT)
- task_type (TEXT)
- response (TEXT)
- feedback (TEXT)
- success (BOOLEAN)
- error_type (TEXT)
- correction (TEXT)
- project_id (TEXT) - NEW: Project identifier
- file_path (TEXT) - NEW: File path within project
- timestamp (DATETIME)

### error_patterns table
- id (INTEGER PRIMARY KEY)
- language (TEXT)
- error_type (TEXT)
- pattern (TEXT)
- solution (TEXT)
- occurrence_count (INTEGER)
- last_seen (DATETIME)

### best_practices table
- id (INTEGER PRIMARY KEY)
- language (TEXT)
- practice (TEXT)
- context (TEXT)
- confidence_score (REAL)
- usage_count (INTEGER)
- timestamp (DATETIME)

## Performance Tips

1. **Model Selection**: Use Q4_K_M quantization for balance of speed/quality
2. **Context Size**: Reduce to 2048 for faster generation
3. **GPU Offloading**: Set gpu_layers > 0 if you have compatible GPU
4. **Caching**: Enable response caching for repeated queries
5. **Threading**: Adjust threads parameter based on CPU cores

## Security Considerations

1. **Local Execution**: All processing is local, no data sent externally
2. **Model Safety**: Only use models from trusted sources
3. **Code Execution**: Never execute generated code without review
4. **Input Validation**: Sanitize user inputs before processing
5. **File Access**: Be cautious with file operations

## Troubleshooting

### Debug Mode

Set environment variable for verbose output:
```bash
export DEBUG=1
python src/main.py
```

### Test Components

Test individual components:
```bash
# Test LLM interface
python src/core/llm_interface.py

# Test learning DB
python src/core/learning_db.py

# Test language support
python src/features/lang_support.py

# Run all tests
python tests/tests.py
```

### Reset Learning Data

Clear all learned patterns:
```bash
# In CLI
/clear

# Or manually
rm data/db/learning.db
```

## Best Practices

### Providing Feedback
- Always provide feedback (y/n) after each generation
- Be specific when something doesn't work
- Include error messages when debugging fails

### Writing Effective Prompts
- Be specific about requirements
- Include context when needed
- Mention frameworks/libraries you're using
- Specify edge cases to handle

### Using the Learning System
- Review error patterns regularly with `/errors <lang>`
- Check statistics with `/stats`
- Export learnings periodically for backup

## License

MIT License - See LICENSE file for details
