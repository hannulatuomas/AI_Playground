# Project Management Guide

This guide explains how to use the project management features in the AI Agent Console, which allow you to organize your work into separate projects with isolated contexts.

## Overview

The Project Management system provides:

- **Multiple Projects**: Create and manage multiple projects with independent contexts
- **Project Switching**: Easily switch between projects without losing context
- **Isolated Memory**: Each project has its own memory and chat history
- **Persistent State**: All project data persists across sessions
- **Project Metadata**: Store descriptions and custom metadata for projects

## Quick Start

### Creating a Project

Create a new project using the CLI:

```bash
python main.py create-project "My AI Project" -d "Working on AI features"
```

This will create a new project and automatically switch to it.

### Listing Projects

View all your projects:

```bash
python main.py projects
```

This displays a table showing all projects, their descriptions, creation dates, and which one is currently active.

### Switching Projects

Switch to a different project:

```bash
python main.py switch-project "My AI Project"
```

The command supports partial name matching, so you don't need to type the full project name.

### Deleting Projects

Delete a project and all its data:

```bash
python main.py delete-project "Old Project" --force
```

The `--force` flag skips the confirmation prompt.

## Architecture

### Project Structure

Each project has:

```python
{
    "project_id": "unique-uuid",
    "name": "Project Name",
    "description": "Project description",
    "created_at": "2025-10-13T12:00:00",
    "updated_at": "2025-10-13T12:30:00",
    "metadata": {},  # Custom metadata
    "memory_session_id": "session-uuid",  # Linked memory session
    "is_active": true  # Whether this is the active project
}
```

### Storage Structure

Projects are stored in the following directory structure:

```
./projects/
├── {project-id-1}.json        # Project metadata
├── {project-id-2}.json
└── {project-id-1}/            # Project-specific data
    ├── session_id.txt         # Memory session ID
    └── ...                    # Other project files
```

### Memory Integration

Each project has its own isolated memory space:

- **Memory Session**: Each project gets a unique memory session
- **Context Isolation**: Memory from one project doesn't leak into another
- **Automatic Switching**: Memory context switches automatically when you switch projects

## Programmatic Usage

### Using ProjectManager in Code

```python
from core import ProjectManager

# Initialize the project manager
pm = ProjectManager(
    storage_path=Path("./projects"),
    auto_save=True
)

# Create a new project
project_id = pm.create_project(
    name="My Project",
    description="A new AI project"
)

# List all projects
projects = pm.list_projects()

# Get a specific project
project = pm.get_project(project_id)

# Update project
pm.update_project(
    project_id=project_id,
    description="Updated description"
)

# Set as active project
pm.set_active_project(project_id)

# Get active project
active = pm.get_active_project()

# Delete project
pm.delete_project(project_id)
```

### Integration with Engine

The Engine automatically integrates project management:

```python
from core import Engine

engine = Engine()
engine.initialize()

# Create a new project
project_id = engine.create_project(
    name="New Project",
    description="Description",
    switch_to_new=True  # Automatically switch to it
)

# Get current project
current = engine.get_current_project()

# Switch projects
engine.switch_project(other_project_id)

# List all projects
projects = engine.list_projects()

# Delete project (includes memory and history)
engine.delete_project(project_id)
```

## Best Practices

### Project Organization

1. **Use Descriptive Names**: Give projects clear, descriptive names
2. **Add Descriptions**: Use descriptions to document project purpose
3. **Regular Cleanup**: Delete old projects you no longer need
4. **Backup Important Projects**: Export project data periodically

### Memory Management

1. **Project-Specific Contexts**: Keep conversations project-specific
2. **Switch Before Working**: Always switch to the correct project before starting work
3. **Review History**: Check chat history to resume context

### Performance

1. **Limit Active Projects**: Keep the number of active projects manageable
2. **Clean Old Sessions**: Use cleanup commands to remove old data
3. **Auto-Save**: Keep auto-save enabled for data persistence

## Advanced Features

### Custom Metadata

Store custom data in project metadata:

```python
pm.update_project(
    project_id=project_id,
    metadata={
        "client": "ACME Corp",
        "deadline": "2025-12-31",
        "priority": "high",
        "tags": ["ai", "automation"]
    }
)
```

### Project Export/Import

Export a project to share or backup:

```python
# Export
pm.export_project(project_id, Path("./backup/project.json"))

# Import
new_project_id = pm.import_project(Path("./backup/project.json"))
```

### Finding Projects

Search for projects by name:

```python
# Find projects containing "AI"
ai_projects = pm.find_projects_by_name("AI")
```

## Troubleshooting

### Project Not Found

If you get "project not found" errors:

1. Check the project exists: `python main.py projects`
2. Verify the project name is correct (case-insensitive match)
3. Check storage directory permissions

### Memory Not Switching

If memory context doesn't switch:

1. Ensure project has a valid memory session
2. Restart the engine to reload state
3. Check logs for errors

### Data Loss

To prevent data loss:

1. Enable auto-save (default)
2. Don't manually edit storage files
3. Use export for backups
4. Check write permissions on storage directory

## CLI Reference

### Commands

- `projects` - List all projects
- `create-project <name>` - Create a new project
  - `--description, -d` - Project description
  - `--no-switch` - Don't switch to new project
- `switch-project <name>` - Switch to a project
- `delete-project <name>` - Delete a project
  - `--force, -f` - Skip confirmation

### Examples

```bash
# Create and switch to a new project
python main.py create-project "Data Analysis" -d "Customer data analysis project"

# List all projects
python main.py projects

# Switch to an existing project
python main.py switch-project "Data"  # Partial match works

# Delete a project with confirmation
python main.py delete-project "Old Project"

# Delete without confirmation
python main.py delete-project "Old Project" --force
```

## Integration with Other Features

### Chat History

Each project has its own chat history. See [Chat History Guide](CHAT_HISTORY.md) for details.

### Memory System

Projects integrate with the memory system for context persistence. See [Memory Guide](../architecture/MEMORY_SYSTEM.md) for details.

### Agents

Agents work within the context of the active project. All agent interactions are scoped to the current project.

## Future Enhancements

Planned features for future versions:

- Project templates
- Project sharing and collaboration
- Project statistics and analytics
- Project archiving
- Project tags and categories
- Project search and filtering
- Project dependencies
- Workspace management (groups of projects)
