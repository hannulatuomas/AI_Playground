
# Example Plugin

This is a complete example plugin that demonstrates all features of the AI Agent Console plugin system.

## Features Demonstrated

- **Custom Agent**: ExampleCustomAgent that performs specialized tasks
- **Custom Tool**: ExampleCustomTool with multiple operations
- **Plugin Hooks**: Before/after agent execution hooks
- **Configuration**: Plugin-specific configuration support
- **Error Handling**: Proper error handling and logging
- **Documentation**: Comprehensive documentation

## Installation

This plugin is included with the AI Agent Console. To enable it:

1. Edit `config.yaml`:

```yaml
plugins:
  enabled:
    - example_plugin
  
  example_plugin:
    debug_mode: true
    custom_setting: "example_value"
```

2. Restart the AI Agent Console

## Usage

### Using the Example Agent

```python
from core.engine import Engine
from core.config import Config

# Initialize engine (plugins are auto-loaded)
config = Config()
engine = Engine(config)

# Use the custom agent
result = engine.execute_task(
    "Demonstrate the example plugin capabilities",
    context={"agent_type": "ExampleCustomAgent"}
)

print(result)
```

### Using the Example Tool

```python
from tools.registry import ToolRegistry
from core.config import Config

# Initialize tool registry (plugins are auto-loaded)
config = Config()
tool_registry = ToolRegistry(config)

# Get the custom tool
example_tool = tool_registry.get_tool("ExampleCustomTool")

# Use the tool
result = example_tool.execute("greet", name="AI Developer")
print(result)  # {"success": True, "result": "Hello, AI Developer!"}
```

## Plugin Structure

```
example_plugin/
├── plugin.py           # Main plugin class and components
└── README.md          # This file
```

## Configuration

Available configuration options:

```yaml
plugins:
  example_plugin:
    # Enable debug logging
    debug_mode: true
    
    # Custom settings for your plugin
    custom_setting: "value"
    
    # API keys or credentials (if needed)
    # api_key: "your_key_here"
```

## Custom Agent: ExampleCustomAgent

### Capabilities
- `example_task`: Demonstrates task execution
- `demo_task`: Shows plugin integration

### Usage Example

```python
result = agent.execute(
    "Show me how the example plugin works",
    context={}
)
```

## Custom Tool: ExampleCustomTool

### Operations
- `demo`: Demonstrates tool execution
- `greet`: Generates a greeting message

### Usage Example

```python
# Demo operation
result = tool.execute("demo", param1="value1", param2="value2")

# Greet operation
result = tool.execute("greet", name="World")
```

## Hooks

This plugin demonstrates the following hooks:

### on_load
Called when the plugin is loaded. Logs plugin initialization.

### on_unload
Called when the plugin is unloaded. Performs cleanup.

### on_agent_execute_before
Called before any agent executes. Logs the agent and task.

### on_agent_execute_after
Called after any agent executes. Logs the result status.

## Development

To modify this plugin:

1. Edit `plugin.py`
2. Make your changes
3. Restart the AI Agent Console
4. Test your changes

## Testing

Test the example plugin:

```python
import pytest
from plugins.example_plugin.plugin import ExamplePlugin

def test_plugin_metadata():
    plugin = ExamplePlugin()
    metadata = plugin.get_metadata()
    assert metadata.name == "example_plugin"
    assert metadata.version == "1.0.0"

def test_plugin_registration():
    plugin = ExamplePlugin()
    plugin.initialize()
    
    agents = plugin.get_agents()
    assert "ExampleCustomAgent" in agents
    
    tools = plugin.get_tools()
    assert "ExampleCustomTool" in tools
```

## License

Part of the AI Agent Console project.

## Contributing

This is an example plugin. Feel free to use it as a template for your own plugins!

## Support

For questions about plugin development:
- Check the main plugin documentation: `/plugins/README.md`
- Review the plugin base classes: `/core/plugin_base.py`
- See the extending guide: `/docs/guides/EXTENDING_GUIDE.md`

---

Happy plugin development! 🚀
