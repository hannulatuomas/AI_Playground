"""
Integration tests for Plugin System.

Tests the full plugin lifecycle including:
- Plugin discovery and loading
- Plugin initialization
- Plugin hook execution with agents and tools
- Plugin registration of custom agents and tools
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, MagicMock

from core.plugin_base import Plugin, PluginMetadata
from core.plugin_loader import PluginLoader
from core.config import Config
from agents.base.agent_base import Agent
from agents.registry import AgentRegistry
from tools.base import Tool
from tools.registry import ToolRegistry


@pytest.mark.integration
class TestPluginSystemIntegration:
    """Integration tests for the plugin system."""
    
    @pytest.fixture
    def temp_plugin_dir(self):
        """Create a temporary directory for test plugins."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = Mock(spec=Config)
        config.get = Mock(side_effect=lambda key, default=None: {
            'plugins.auto_discover': True,
            'plugins.enabled': [],
            'plugins.test_plugin.setting1': 'value1'
        }.get(key, default))
        return config
    
    @pytest.fixture
    def agent_registry(self):
        """Create a fresh agent registry."""
        registry = AgentRegistry.get_instance()
        registry.clear_cache()
        return registry
    
    @pytest.fixture
    def tool_registry(self):
        """Create a fresh tool registry."""
        registry = ToolRegistry.get_instance()
        registry.clear()
        return registry
    
    @pytest.fixture
    def plugin_loader(self, mock_config, agent_registry, tool_registry, temp_plugin_dir):
        """Create a plugin loader instance."""
        return PluginLoader(
            config=mock_config,
            agent_registry=agent_registry,
            tool_registry=tool_registry,
            plugin_dir=temp_plugin_dir
        )
    
    def test_plugin_discovery(self, plugin_loader, temp_plugin_dir):
        """Test plugin discovery in directory."""
        # Create a test plugin structure
        test_plugin_dir = temp_plugin_dir / "test_plugin"
        test_plugin_dir.mkdir()
        (test_plugin_dir / "__init__.py").write_text("# Test plugin")
        (test_plugin_dir / "plugin.py").write_text("""
from core.plugin_base import Plugin, PluginMetadata

class TestPlugin(Plugin):
    def get_metadata(self):
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="Test",
            description="Test plugin"
        )
    
    def initialize(self):
        pass
""")
        
        # Discover plugins
        discovered = plugin_loader.discover_plugins()
        
        assert len(discovered) == 1
        assert discovered[0].name == "test_plugin"
    
    def test_plugin_loading(self, plugin_loader, temp_plugin_dir):
        """Test loading a single plugin."""
        # Create test plugin
        test_plugin_dir = temp_plugin_dir / "test_plugin"
        test_plugin_dir.mkdir()
        (test_plugin_dir / "plugin.py").write_text("""
from core.plugin_base import Plugin, PluginMetadata

class TestPlugin(Plugin):
    def get_metadata(self):
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="Test",
            description="Test plugin"
        )
    
    def initialize(self):
        self.initialized = True
""")
        
        # Load plugin
        plugin = plugin_loader.load_plugin(test_plugin_dir)
        
        assert plugin is not None
        assert plugin.get_metadata().name == "test_plugin"
        assert plugin.get_metadata().version == "1.0.0"
    
    def test_plugin_initialization(self, plugin_loader, temp_plugin_dir):
        """Test plugin initialization process."""
        # Create test plugin
        test_plugin_dir = temp_plugin_dir / "test_plugin"
        test_plugin_dir.mkdir()
        (test_plugin_dir / "plugin.py").write_text("""
from core.plugin_base import Plugin, PluginMetadata

class TestPlugin(Plugin):
    def get_metadata(self):
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="Test",
            description="Test plugin"
        )
    
    def initialize(self):
        config = self.get_config()
        self.setting1 = config.get('setting1', 'default')
""")
        
        # Load and initialize
        plugin = plugin_loader.load_plugin(test_plugin_dir)
        plugin_loader.initialize_plugin("test_plugin")
        
        # Verify initialization
        loaded_plugin = plugin_loader.get_plugin("test_plugin")
        assert loaded_plugin is not None
        assert hasattr(loaded_plugin, 'setting1')
    
    def test_plugin_agent_registration(self, plugin_loader, agent_registry, temp_plugin_dir):
        """Test plugin registering custom agents."""
        # Create test plugin with custom agent
        test_plugin_dir = temp_plugin_dir / "test_plugin"
        test_plugin_dir.mkdir()
        (test_plugin_dir / "plugin.py").write_text("""
from core.plugin_base import Plugin, PluginMetadata
from agents.base.agent_base import Agent
from typing import Dict, Any

class CustomAgent(Agent):
    def __init__(self, llm_router=None, tool_registry=None, config=None, **kwargs):
        super().__init__(
            name="CustomAgent",
            description="Custom plugin agent",
            llm_router=llm_router,
            tool_registry=tool_registry,
            config=config
        )
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "message": "Custom agent executed"}

class TestPlugin(Plugin):
    def get_metadata(self):
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="Test",
            description="Test plugin"
        )
    
    def initialize(self):
        self.register_agent("CustomAgent", CustomAgent)
""")
        
        # Load and initialize
        plugin = plugin_loader.load_plugin(test_plugin_dir)
        plugin_loader.initialize_plugin("test_plugin")
        
        # Verify agent registration
        assert agent_registry.get("CustomAgent") is not None
    
    def test_plugin_tool_registration(self, plugin_loader, tool_registry, temp_plugin_dir):
        """Test plugin registering custom tools."""
        # Create test plugin with custom tool
        test_plugin_dir = temp_plugin_dir / "test_plugin"
        test_plugin_dir.mkdir()
        (test_plugin_dir / "plugin.py").write_text("""
from core.plugin_base import Plugin, PluginMetadata
from tools.base import Tool
from typing import Dict, Any

class CustomTool(Tool):
    def __init__(self, config=None, **kwargs):
        super().__init__(
            name="CustomTool",
            description="Custom plugin tool",
            config=config
        )
    
    def invoke(self, params: Dict[str, Any]) -> Any:
        return {"success": True, "result": "Custom tool invoked"}

class TestPlugin(Plugin):
    def get_metadata(self):
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="Test",
            description="Test plugin"
        )
    
    def initialize(self):
        self.register_tool("CustomTool", CustomTool)
""")
        
        # Load and initialize
        plugin = plugin_loader.load_plugin(test_plugin_dir)
        plugin_loader.initialize_plugin("test_plugin")
        
        # Verify tool registration
        assert tool_registry.get("CustomTool") is not None
    
    def test_plugin_hooks_with_agent(self, plugin_loader, temp_plugin_dir):
        """Test plugin hooks being called during agent execution."""
        # Create test plugin with hooks
        test_plugin_dir = temp_plugin_dir / "test_plugin"
        test_plugin_dir.mkdir()
        (test_plugin_dir / "plugin.py").write_text("""
from core.plugin_base import Plugin, PluginMetadata
from typing import Dict, Any

class TestPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.before_called = False
        self.after_called = False
    
    def get_metadata(self):
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="Test",
            description="Test plugin"
        )
    
    def initialize(self):
        self.hooks.on_agent_execute_before = self._before_hook
        self.hooks.on_agent_execute_after = self._after_hook
    
    def _before_hook(self, agent, task, context):
        self.before_called = True
    
    def _after_hook(self, agent, task, context, result):
        self.after_called = True
""")
        
        # Load and initialize
        plugin = plugin_loader.load_plugin(test_plugin_dir)
        plugin_loader.initialize_plugin("test_plugin")
        
        # Create a test agent with plugin_loader
        class TestAgent(Agent):
            def __init__(self):
                super().__init__(
                    name="TestAgent",
                    description="Test agent",
                    plugin_loader=plugin_loader
                )
            
            def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
                return {"success": True}
        
        agent = TestAgent()
        
        # Execute with hooks
        result = agent.execute_with_hooks("test task", {})
        
        # Verify hooks were called
        loaded_plugin = plugin_loader.get_plugin("test_plugin")
        assert loaded_plugin.before_called is True
        assert loaded_plugin.after_called is True
    
    def test_plugin_hooks_with_tool(self, plugin_loader, temp_plugin_dir):
        """Test plugin hooks being called during tool invocation."""
        # Create test plugin with hooks
        test_plugin_dir = temp_plugin_dir / "test_plugin"
        test_plugin_dir.mkdir()
        (test_plugin_dir / "plugin.py").write_text("""
from core.plugin_base import Plugin, PluginMetadata
from typing import Dict, Any

class TestPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.tool_before_called = False
        self.tool_after_called = False
    
    def get_metadata(self):
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="Test",
            description="Test plugin"
        )
    
    def initialize(self):
        self.hooks.on_tool_execute_before = self._tool_before_hook
        self.hooks.on_tool_execute_after = self._tool_after_hook
    
    def _tool_before_hook(self, tool, **kwargs):
        self.tool_before_called = True
    
    def _tool_after_hook(self, tool, result, **kwargs):
        self.tool_after_called = True
""")
        
        # Load and initialize
        plugin = plugin_loader.load_plugin(test_plugin_dir)
        plugin_loader.initialize_plugin("test_plugin")
        
        # Create a test tool with plugin_loader
        class TestTool(Tool):
            def __init__(self):
                super().__init__(
                    name="TestTool",
                    description="Test tool",
                    plugin_loader=plugin_loader
                )
            
            def invoke(self, params: Dict[str, Any]) -> Any:
                return {"success": True}
        
        tool = TestTool()
        
        # Invoke with hooks
        result = tool.invoke_with_hooks({"test": "param"})
        
        # Verify hooks were called
        loaded_plugin = plugin_loader.get_plugin("test_plugin")
        assert loaded_plugin.tool_before_called is True
        assert loaded_plugin.tool_after_called is True
    
    def test_plugin_unloading(self, plugin_loader, agent_registry, tool_registry, temp_plugin_dir):
        """Test plugin unloading and cleanup."""
        # Create test plugin
        test_plugin_dir = temp_plugin_dir / "test_plugin"
        test_plugin_dir.mkdir()
        (test_plugin_dir / "plugin.py").write_text("""
from core.plugin_base import Plugin, PluginMetadata
from agents.base.agent_base import Agent
from tools.base import Tool
from typing import Dict, Any

class CustomAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(name="CustomAgent", description="Custom agent", **kwargs)
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True}

class CustomTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(name="CustomTool", description="Custom tool", **kwargs)
    def invoke(self, params: Dict[str, Any]) -> Any:
        return {"success": True}

class TestPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.cleanup_called = False
    
    def get_metadata(self):
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="Test",
            description="Test plugin"
        )
    
    def initialize(self):
        self.register_agent("CustomAgent", CustomAgent)
        self.register_tool("CustomTool", CustomTool)
    
    def cleanup(self):
        self.cleanup_called = True
""")
        
        # Load and initialize
        plugin = plugin_loader.load_plugin(test_plugin_dir)
        plugin_loader.initialize_plugin("test_plugin")
        
        # Verify registration
        assert agent_registry.get("CustomAgent") is not None
        assert tool_registry.get("CustomTool") is not None
        
        # Unload plugin
        plugin_loader.unload_plugin("test_plugin")
        
        # Verify cleanup and unregistration
        assert agent_registry.get("CustomAgent") is None
        assert tool_registry.get("CustomTool") is None
        assert plugin_loader.get_plugin("test_plugin") is None
    
    def test_plugin_list(self, plugin_loader, temp_plugin_dir):
        """Test listing loaded plugins."""
        # Create multiple test plugins
        for i in range(3):
            test_plugin_dir = temp_plugin_dir / f"test_plugin_{i}"
            test_plugin_dir.mkdir()
            (test_plugin_dir / "plugin.py").write_text(f"""
from core.plugin_base import Plugin, PluginMetadata

class TestPlugin{i}(Plugin):
    def get_metadata(self):
        return PluginMetadata(
            name="test_plugin_{i}",
            version="1.0.{i}",
            author="Test",
            description="Test plugin {i}"
        )
    
    def initialize(self):
        pass
""")
        
        # Load all plugins
        plugin_loader.load_all_plugins()
        
        # List plugins
        plugins = plugin_loader.list_plugins()
        
        assert len(plugins) == 3
        assert all('name' in p and 'version' in p for p in plugins)
    
    def test_plugin_version_compatibility(self, plugin_loader, temp_plugin_dir):
        """Test plugin version compatibility checking."""
        # Create plugin requiring newer console version
        test_plugin_dir = temp_plugin_dir / "test_plugin"
        test_plugin_dir.mkdir()
        (test_plugin_dir / "plugin.py").write_text("""
from core.plugin_base import Plugin, PluginMetadata

class TestPlugin(Plugin):
    def get_metadata(self):
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="Test",
            description="Test plugin",
            min_console_version="99.0.0"  # Future version
        )
    
    def initialize(self):
        pass
""")
        
        # Try to load plugin (should fail due to version)
        with pytest.raises(Exception):  # Should raise PluginLoadError
            plugin_loader.load_plugin(test_plugin_dir)
    
    def test_example_plugin_loading(self, mock_config, agent_registry, tool_registry):
        """Test loading the actual example plugin."""
        # Use the real example plugin directory
        example_plugin_dir = Path("plugins/example_plugin")
        
        if not example_plugin_dir.exists():
            pytest.skip("Example plugin not found")
        
        plugin_loader = PluginLoader(
            config=mock_config,
            agent_registry=agent_registry,
            tool_registry=tool_registry,
            plugin_dir=Path("plugins")
        )
        
        # Try to load the example plugin
        plugin = plugin_loader.load_plugin(example_plugin_dir)
        
        assert plugin is not None
        assert plugin.get_metadata().name == "example_plugin"
        
        # Initialize it
        plugin_loader.initialize_plugin("example_plugin")
        
        # Verify agents and tools were registered
        assert agent_registry.get("ExampleCustomAgent") is not None
        assert tool_registry.get("ExampleCustomTool") is not None


@pytest.mark.integration
class TestPluginWorkflows:
    """Integration tests for complete plugin workflows."""
    
    def test_full_plugin_lifecycle(self, tmp_path):
        """Test complete plugin lifecycle from discovery to execution."""
        # Setup
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()
        
        test_plugin_dir = plugin_dir / "workflow_plugin"
        test_plugin_dir.mkdir()
        (test_plugin_dir / "plugin.py").write_text("""
from core.plugin_base import Plugin, PluginMetadata
from agents.base.agent_base import Agent
from typing import Dict, Any

class WorkflowAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(name="WorkflowAgent", description="Workflow agent", **kwargs)
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "task": task, "data": "workflow_data"}

class WorkflowPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.execution_log = []
    
    def get_metadata(self):
        return PluginMetadata(
            name="workflow_plugin",
            version="1.0.0",
            author="Test",
            description="Workflow plugin"
        )
    
    def initialize(self):
        self.register_agent("WorkflowAgent", WorkflowAgent)
        self.hooks.on_agent_execute_before = self._log_before
        self.hooks.on_agent_execute_after = self._log_after
    
    def _log_before(self, agent, task, context):
        self.execution_log.append(f"BEFORE: {task}")
    
    def _log_after(self, agent, task, context, result):
        self.execution_log.append(f"AFTER: {task} -> {result.get('success')}")
""")
        
        # Create plugin loader
        mock_config = Mock(spec=Config)
        mock_config.get = Mock(return_value={})
        agent_registry = AgentRegistry.get_instance()
        tool_registry = ToolRegistry.get_instance()
        
        plugin_loader = PluginLoader(
            config=mock_config,
            agent_registry=agent_registry,
            tool_registry=tool_registry,
            plugin_dir=plugin_dir
        )
        
        # 1. Discover
        discovered = plugin_loader.discover_plugins()
        assert len(discovered) == 1
        
        # 2. Load
        plugin = plugin_loader.load_plugin(test_plugin_dir)
        assert plugin is not None
        
        # 3. Initialize
        plugin_loader.initialize_plugin("workflow_plugin")
        
        # 4. Use registered agent
        agent_class = agent_registry.get("WorkflowAgent")
        assert agent_class is not None
        
        agent = agent_class(plugin_loader=plugin_loader)
        
        # 5. Execute with hooks
        result = agent.execute_with_hooks("test workflow task", {})
        
        assert result["success"] is True
        
        # 6. Verify hooks were called
        loaded_plugin = plugin_loader.get_plugin("workflow_plugin")
        assert len(loaded_plugin.execution_log) == 2
        assert "BEFORE: test workflow task" in loaded_plugin.execution_log
        assert "AFTER: test workflow task -> True" in loaded_plugin.execution_log
        
        # 7. Unload
        plugin_loader.unload_plugin("workflow_plugin")
        assert agent_registry.get("WorkflowAgent") is None
