
# AI Agent Console Plugins

This directory contains plugins that extend the AI Agent Console with custom agents, tools, and functionality.

## Plugin System Overview

The plugin system allows you to:
- **Create custom agents** for specialized tasks
- **Add custom tools** for new capabilities
- **Hook into system events** for monitoring and customization
- **Extend the orchestration system** with new workflows
- **Access the vector database** and memory system

## Plugin Structure

Each plugin should be in its own directory with the following structure:

```
plugins/
└── your_plugin_name/
    ├── plugin.py         # Plugin class definition
    ├── agents/           # Custom agents (optional)
    │   └── custom_agent.py
    ├── tools/            # Custom tools (optional)
    │   └── custom_tool.py
    ├── README.md         # Plugin documentation
    └── requirements.txt  # Plugin dependencies (optional)
```

## Creating a Plugin

### 1. Create Plugin Directory

```bash
mkdir -p plugins/my_plugin
cd plugins/my_plugin
```

### 2. Create plugin.py

```python
"""
My Custom Plugin

Description of what your plugin does.
"""

from core.plugin_base import Plugin, PluginMetadata
from agents.base.agent_base import Agent
from tools.base import Tool

# Import your custom agents and tools
from .agents.custom_agent import CustomAgent
from .tools.custom_tool import CustomTool


class MyPlugin(Plugin):
    """My custom plugin for AI Agent Console."""
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            author="Your Name",
            description="Description of your plugin",
            homepage="https://github.com/yourusername/my-plugin",
            dependencies=[],  # List of required plugin names
            min_console_version="2.4.0"
        )
    
    def initialize(self) -> None:
        """Initialize the plugin and register components."""
        # Register custom agents
        self.register_agent("CustomAgent", CustomAgent)
        
        # Register custom tools
        self.register_tool("CustomTool", CustomTool)
        
        # Set up hooks
        self.hooks.on_load = self.on_plugin_load
        self.hooks.on_agent_execute_before = self.before_agent_execute
    
    def on_plugin_load(self) -> None:
        """Called when plugin is loaded."""
        print(f"Plugin {self.get_metadata().name} loaded!")
    
    def before_agent_execute(self, agent, task, context):
        """Called before any agent executes."""
        # Add custom logic here
        pass
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        # Add cleanup logic here
        pass
```

### 3. Create Custom Agent (Optional)

```python
# agents/custom_agent.py

from agents.base.agent_base import Agent
from typing import Dict, Any


class CustomAgent(Agent):
    """Custom agent for specialized tasks."""
    
    def __init__(self, llm_router, tool_registry, config):
        super().__init__(llm_router, tool_registry, config)
        self.name = "CustomAgent"
        self.description = "Performs specialized tasks"
        self.capabilities = ["capability1", "capability2"]
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task."""
        try:
            # Your agent logic here
            result = self._perform_task(task, context)
            
            return {
                "success": True,
                "message": "Task completed successfully",
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _perform_task(self, task: str, context: Dict[str, Any]) -> Any:
        """Implement your task logic here."""
        # Use LLM
        llm_response = self.llm_router.query(
            f"Perform task: {task}",
            model=self.config.get("model", "llama3.3:latest")
        )
        
        # Use tools
        tool = self.tool_registry.get_tool("FileOperations")
        # ... tool usage
        
        return {"result": "task output"}
```

### 4. Create Custom Tool (Optional)

```python
# tools/custom_tool.py

from tools.base import Tool
from typing import Any, Dict


class CustomTool(Tool):
    """Custom tool for specific operations."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "CustomTool"
        self.description = "Performs specific operations"
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute the tool."""
        # Your tool logic here
        return {"result": "tool output"}
    
    def validate_input(self, *args, **kwargs) -> bool:
        """Validate tool input."""
        return True
```

### 5. Create README.md

Document your plugin:

```markdown
# My Plugin

Description of what your plugin does.

## Installation

1. Copy plugin directory to `plugins/my_plugin/`
2. Install dependencies: `pip install -r requirements.txt`
3. Enable in config.yaml

## Configuration

Add to your `config.yaml`:

\```yaml
plugins:
  enabled:
    - my_plugin
  my_plugin:
    setting1: value1
    setting2: value2
\```

## Usage

Examples of how to use your plugin.

## License

Your license here
```

## Plugin Configuration

### Enable Plugins

Edit `config.yaml`:

```yaml
plugins:
  # Auto-discover plugins in plugins/ directory
  auto_discover: true
  
  # Or specify enabled plugins explicitly
  enabled:
    - example_plugin
    - my_plugin
  
  # Plugin-specific configuration
  example_plugin:
    setting1: value1
    setting2: value2
```

### Load Plugins Programmatically

```python
from core.plugin_loader import PluginLoader
from core.config import Config
from agents.registry import AgentRegistry
from tools.registry import ToolRegistry

# Initialize
config = Config()
agent_registry = AgentRegistry()
tool_registry = ToolRegistry(config)
plugin_loader = PluginLoader(config, agent_registry, tool_registry)

# Load all plugins
plugin_loader.load_all_plugins()

# Or load specific plugin
plugin_loader.load_plugin(Path("plugins/my_plugin"))
plugin_loader.initialize_plugin("my_plugin")

# List loaded plugins
plugins = plugin_loader.list_plugins()
for plugin in plugins:
    print(f"{plugin['name']} v{plugin['version']}")
```

## Plugin Hooks

Plugins can hook into system events:

### Available Hooks

```python
def on_load(self) -> None:
    """Called when plugin is loaded."""
    pass

def on_unload(self) -> None:
    """Called when plugin is unloaded."""
    pass

def on_agent_execute_before(self, agent, task, context) -> None:
    """Called before any agent executes."""
    pass

def on_agent_execute_after(self, agent, task, context, result) -> None:
    """Called after any agent executes."""
    pass

def on_tool_execute_before(self, tool, *args, **kwargs) -> None:
    """Called before any tool executes."""
    pass

def on_tool_execute_after(self, tool, result, *args, **kwargs) -> None:
    """Called after any tool executes."""
    pass

def on_memory_store(self, memory_type, content) -> None:
    """Called when memory is stored."""
    pass

def on_memory_retrieve(self, query, results) -> None:
    """Called when memory is retrieved."""
    pass
```

## Testing Plugins

Create tests for your plugin:

```python
# tests/test_my_plugin.py

import pytest
from plugins.my_plugin.plugin import MyPlugin


def test_plugin_metadata():
    """Test plugin metadata."""
    plugin = MyPlugin()
    metadata = plugin.get_metadata()
    
    assert metadata.name == "my_plugin"
    assert metadata.version == "1.0.0"


def test_plugin_initialization():
    """Test plugin initialization."""
    plugin = MyPlugin()
    plugin.initialize()
    
    # Check agents registered
    agents = plugin.get_agents()
    assert "CustomAgent" in agents
    
    # Check tools registered
    tools = plugin.get_tools()
    assert "CustomTool" in tools
```

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
def execute(self, task, context):
    try:
        result = self._perform_task(task, context)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error in plugin: {e}")
        return {"success": False, "error": str(e)}
```

### 2. Logging

Use Python's logging module:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Plugin action performed")
logger.warning("Potential issue detected")
logger.error("Error occurred")
```

### 3. Configuration

Make your plugin configurable:

```python
def initialize(self):
    config = self.get_config()
    self.api_key = config.get("api_key")
    self.endpoint = config.get("endpoint", "default_endpoint")
```

### 4. Dependencies

Document dependencies in requirements.txt:

```
requests>=2.28.0
beautifulsoup4>=4.11.0
```

### 5. Versioning

Follow semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

## Example Plugins

See the `example_plugin/` directory for a complete, working example.

## Troubleshooting

### Plugin Not Loading

1. Check plugin directory structure
2. Verify plugin.py exists
3. Check for syntax errors
4. Review logs for error messages

### Plugin Not Working

1. Verify configuration in config.yaml
2. Check dependencies are installed
3. Review plugin logs
4. Test with example plugin

### Dependencies Not Met

Ensure required plugins are loaded first by specifying dependencies:

```python
PluginMetadata(
    name="my_plugin",
    dependencies=["required_plugin1", "required_plugin2"],
    # ...
)
```

## Contributing Plugins

To share your plugin with the community:

1. Create a GitHub repository
2. Include comprehensive README
3. Add tests
4. Tag releases with version numbers
5. Submit to plugin directory (coming soon)

## Resources

- [Plugin Base Classes](#plugin-system)
- [Plugin Loader](#plugin-system)
- [EXTENDING_GUIDE.md](../docs/guides/EXTENDING_GUIDE.md)
- [Agent Base Class](../agents/base/)
- [Tool Base Class](../tools/)

## Support

For plugin development support:
- Open an issue on GitHub
- Check the documentation
- Review example plugins
- Ask in discussions

---

Happy plugin development! 🚀
