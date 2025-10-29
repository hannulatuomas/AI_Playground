
"""
Plugin Loader

This module handles loading, managing, and coordinating plugins for the AI Agent Console.
Plugins can extend the system with custom agents, tools, and functionality.
"""

import importlib
import importlib.util
import inspect
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
from packaging import version

from core.plugin_base import (
    Plugin,
    PluginMetadata,
    PluginError,
    PluginLoadError,
    PluginInitializationError,
    PluginDependencyError
)
from core.config import Config
from agents.registry import AgentRegistry
from tools.registry import ToolRegistry


logger = logging.getLogger(__name__)


class PluginLoader:
    """
    Manages loading and lifecycle of plugins.
    
    The PluginLoader discovers, loads, initializes, and manages plugins.
    It handles plugin dependencies and provides access to plugin agents and tools.
    """
    
    def __init__(
        self,
        config: Config,
        agent_registry: AgentRegistry,
        tool_registry: ToolRegistry,
        plugin_dir: Optional[Path] = None
    ):
        """
        Initialize the plugin loader.
        
        Args:
            config: System configuration
            agent_registry: Agent registry for registering plugin agents
            tool_registry: Tool registry for registering plugin tools
            plugin_dir: Directory containing plugins (default: ./plugins)
        """
        self.config = config
        self.agent_registry = agent_registry
        self.tool_registry = tool_registry
        self.plugin_dir = plugin_dir or Path("plugins")
        
        self._plugins: Dict[str, Plugin] = {}
        self._loaded_plugins: Dict[str, PluginMetadata] = {}
        self._plugin_hooks: Dict[str, List[Plugin]] = {}
        
        # Minimum console version
        self.console_version = "2.4.0"
        
        logger.info(f"PluginLoader initialized with plugin directory: {self.plugin_dir}")
    
    def discover_plugins(self) -> List[Path]:
        """
        Discover available plugins in the plugin directory.
        
        Returns:
            List of paths to plugin directories
        """
        if not self.plugin_dir.exists():
            logger.warning(f"Plugin directory does not exist: {self.plugin_dir}")
            return []
        
        plugins = []
        for item in self.plugin_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                # Check for __init__.py or plugin.py
                if (item / "__init__.py").exists() or (item / "plugin.py").exists():
                    plugins.append(item)
                    logger.debug(f"Discovered plugin: {item.name}")
        
        logger.info(f"Discovered {len(plugins)} plugins")
        return plugins
    
    def load_plugin(self, plugin_path: Path) -> Optional[Plugin]:
        """
        Load a single plugin from a directory.
        
        Args:
            plugin_path: Path to the plugin directory
            
        Returns:
            Loaded Plugin instance or None if loading failed
            
        Raises:
            PluginLoadError: If plugin loading fails
        """
        plugin_name = plugin_path.name
        logger.info(f"Loading plugin: {plugin_name}")
        
        try:
            # Try to import the plugin module
            spec = None
            module_path = None
            
            # Try plugin.py first, then __init__.py
            if (plugin_path / "plugin.py").exists():
                module_path = plugin_path / "plugin.py"
            elif (plugin_path / "__init__.py").exists():
                module_path = plugin_path / "__init__.py"
            else:
                raise PluginLoadError(f"No plugin.py or __init__.py found in {plugin_path}")
            
            # Load the module
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_name}",
                module_path
            )
            
            if spec is None or spec.loader is None:
                raise PluginLoadError(f"Failed to load plugin spec for {plugin_name}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"plugins.{plugin_name}"] = module
            spec.loader.exec_module(module)
            
            # Find Plugin subclass in the module
            plugin_class = None
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Plugin) and obj != Plugin:
                    plugin_class = obj
                    break
            
            if plugin_class is None:
                raise PluginLoadError(f"No Plugin subclass found in {plugin_name}")
            
            # Instantiate the plugin
            plugin = plugin_class()
            
            # Get and validate metadata
            metadata = plugin.get_metadata()
            self._validate_metadata(metadata)
            
            # Check console version compatibility
            if not self._check_version_compatibility(metadata.min_console_version):
                raise PluginLoadError(
                    f"Plugin {plugin_name} requires console version "
                    f"{metadata.min_console_version}, but current version is {self.console_version}"
                )
            
            # Check dependencies
            if metadata.dependencies:
                missing = self._check_dependencies(metadata.dependencies)
                if missing:
                    raise PluginDependencyError(
                        f"Plugin {plugin_name} has unmet dependencies: {', '.join(missing)}"
                    )
            
            # Store plugin
            self._plugins[plugin_name] = plugin
            self._loaded_plugins[plugin_name] = metadata
            
            logger.info(f"Successfully loaded plugin: {plugin_name} v{metadata.version}")
            return plugin
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {str(e)}")
            raise PluginLoadError(f"Failed to load plugin {plugin_name}: {str(e)}") from e
    
    def initialize_plugin(self, plugin_name: str) -> None:
        """
        Initialize a loaded plugin.
        
        Args:
            plugin_name: Name of the plugin to initialize
            
        Raises:
            PluginInitializationError: If initialization fails
        """
        if plugin_name not in self._plugins:
            raise PluginInitializationError(f"Plugin {plugin_name} not loaded")
        
        plugin = self._plugins[plugin_name]
        logger.info(f"Initializing plugin: {plugin_name}")
        
        try:
            # Configure plugin from config.yaml
            # Check if config has plugins attribute
            plugin_config = {}
            if hasattr(self.config, 'plugins'):
                plugin_config = getattr(self.config.plugins, plugin_name, {})
            plugin.configure(plugin_config)
            
            # Call plugin initialization
            plugin.hooks.on_load()
            plugin.initialize()
            
            # Register plugin agents
            for agent_name, agent_class in plugin.get_agents().items():
                self.agent_registry.register(agent_class, agent_name)
                logger.info(f"Registered agent '{agent_name}' from plugin '{plugin_name}'")
            
            # Register plugin tools
            for tool_name, tool_class in plugin.get_tools().items():
                self.tool_registry.register(tool_class, tool_name)
                logger.info(f"Registered tool '{tool_name}' from plugin '{plugin_name}'")
            
            logger.info(f"Successfully initialized plugin: {plugin_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize plugin {plugin_name}: {str(e)}")
            raise PluginInitializationError(
                f"Failed to initialize plugin {plugin_name}: {str(e)}"
            ) from e
    
    def unload_plugin(self, plugin_name: str) -> None:
        """
        Unload a plugin.
        
        Args:
            plugin_name: Name of the plugin to unload
        """
        if plugin_name not in self._plugins:
            logger.warning(f"Plugin {plugin_name} not loaded")
            return
        
        plugin = self._plugins[plugin_name]
        logger.info(f"Unloading plugin: {plugin_name}")
        
        try:
            # Call cleanup hooks
            plugin.cleanup()
            plugin.hooks.on_unload()
            
            # Unregister agents
            for agent_name in plugin.get_agents().keys():
                self.agent_registry.unregister(agent_name)
            
            # Unregister tools
            for tool_name in plugin.get_tools().keys():
                self.tool_registry.unregister(tool_name)
            
            # Remove from loaded plugins
            del self._plugins[plugin_name]
            del self._loaded_plugins[plugin_name]
            
            logger.info(f"Successfully unloaded plugin: {plugin_name}")
            
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_name}: {str(e)}")
    
    def load_all_plugins(self) -> None:
        """
        Discover, load, and initialize all plugins.
        """
        logger.info("Loading all plugins")
        
        # Get plugin configuration
        # Check if config has plugins attribute
        enabled_plugins = []
        auto_discover = True
        if hasattr(self.config, 'plugins'):
            if hasattr(self.config.plugins, 'enabled'):
                enabled_plugins = self.config.plugins.enabled or []
            if hasattr(self.config.plugins, 'auto_discover'):
                auto_discover = self.config.plugins.auto_discover
        
        # Discover plugins
        discovered = self.discover_plugins()
        
        # Filter to enabled plugins if specified
        if enabled_plugins:
            discovered = [p for p in discovered if p.name in enabled_plugins]
        
        # Load plugins
        loaded_count = 0
        failed_count = 0
        
        for plugin_path in discovered:
            try:
                plugin = self.load_plugin(plugin_path)
                if plugin:
                    self.initialize_plugin(plugin_path.name)
                    loaded_count += 1
            except (PluginLoadError, PluginInitializationError, PluginDependencyError) as e:
                logger.error(f"Failed to load plugin {plugin_path.name}: {str(e)}")
                failed_count += 1
        
        logger.info(
            f"Plugin loading complete: {loaded_count} successful, {failed_count} failed"
        )
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        Get a loaded plugin by name.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin instance or None if not found
        """
        return self._plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, Plugin]:
        """
        Get all loaded plugins.
        
        Returns:
            Dictionary of plugin name to Plugin instance
        """
        return self._plugins.copy()
    
    def get_plugin_metadata(self, plugin_name: str) -> Optional[PluginMetadata]:
        """
        Get metadata for a loaded plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            PluginMetadata or None if not found
        """
        return self._loaded_plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, str]]:
        """
        List all loaded plugins with their metadata.
        
        Returns:
            List of plugin information dictionaries
        """
        plugins_info = []
        for name, metadata in self._loaded_plugins.items():
            plugins_info.append({
                "name": metadata.name,
                "version": metadata.version,
                "author": metadata.author,
                "description": metadata.description,
                "homepage": metadata.homepage or "N/A"
            })
        return plugins_info
    
    def _validate_metadata(self, metadata: PluginMetadata) -> None:
        """
        Validate plugin metadata.
        
        Args:
            metadata: Plugin metadata to validate
            
        Raises:
            PluginLoadError: If metadata is invalid
        """
        if not metadata.name:
            raise PluginLoadError("Plugin metadata missing name")
        if not metadata.version:
            raise PluginLoadError("Plugin metadata missing version")
        
        # Validate version format
        try:
            version.parse(metadata.version)
        except version.InvalidVersion:
            raise PluginLoadError(f"Invalid version format: {metadata.version}")
    
    def _check_version_compatibility(self, min_version: str) -> bool:
        """
        Check if the plugin's minimum version requirement is met.
        
        Args:
            min_version: Minimum console version required
            
        Returns:
            True if compatible, False otherwise
        """
        try:
            return version.parse(self.console_version) >= version.parse(min_version)
        except version.InvalidVersion:
            return False
    
    def _check_dependencies(self, dependencies: List[str]) -> List[str]:
        """
        Check if plugin dependencies are met.
        
        Args:
            dependencies: List of required plugin names
            
        Returns:
            List of missing dependencies
        """
        missing = []
        for dep in dependencies:
            if dep not in self._loaded_plugins:
                missing.append(dep)
        return missing
