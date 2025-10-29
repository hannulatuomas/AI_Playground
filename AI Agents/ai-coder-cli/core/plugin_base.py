
"""
Plugin Base Classes

This module defines the base classes and interfaces for the AI Agent Console plugin system.
Plugins can extend the system with custom agents, tools, and hooks.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass
import logging

from agents.base.agent_base import Agent
from tools.base import Tool


logger = logging.getLogger(__name__)


@dataclass
class PluginMetadata:
    """
    Metadata for a plugin.
    
    Attributes:
        name: Plugin name
        version: Plugin version (semver)
        author: Plugin author
        description: Brief plugin description
        homepage: Plugin homepage URL
        dependencies: List of required plugin names
        min_console_version: Minimum AI Agent Console version required
    """
    name: str
    version: str
    author: str
    description: str
    homepage: Optional[str] = None
    dependencies: Optional[List[str]] = None
    min_console_version: str = "2.0.0"
    
    def __post_init__(self):
        """Validate metadata after initialization."""
        if not self.name:
            raise ValueError("Plugin name is required")
        if not self.version:
            raise ValueError("Plugin version is required")
        if self.dependencies is None:
            self.dependencies = []


class PluginHooks:
    """
    Plugin hooks for integrating with the AI Agent Console lifecycle.
    
    Plugins can override these methods to hook into various system events.
    """
    
    def on_load(self) -> None:
        """
        Called when the plugin is loaded.
        Use for initialization tasks.
        """
        pass
    
    def on_unload(self) -> None:
        """
        Called when the plugin is unloaded.
        Use for cleanup tasks.
        """
        pass
    
    def on_agent_execute_before(self, agent: Agent, task: str, context: Dict[str, Any]) -> None:
        """
        Called before an agent executes a task.
        
        Args:
            agent: The agent about to execute
            task: The task to execute
            context: The execution context
        """
        pass
    
    def on_agent_execute_after(
        self,
        agent: Agent,
        task: str,
        context: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        """
        Called after an agent executes a task.
        
        Args:
            agent: The agent that executed
            task: The executed task
            context: The execution context
            result: The execution result
        """
        pass
    
    def on_tool_execute_before(self, tool: Tool, *args, **kwargs) -> None:
        """
        Called before a tool is executed.
        
        Args:
            tool: The tool about to execute
            *args: Tool arguments
            **kwargs: Tool keyword arguments
        """
        pass
    
    def on_tool_execute_after(
        self,
        tool: Tool,
        result: Any,
        *args,
        **kwargs
    ) -> None:
        """
        Called after a tool is executed.
        
        Args:
            tool: The tool that executed
            result: The tool result
            *args: Tool arguments
            **kwargs: Tool keyword arguments
        """
        pass
    
    def on_memory_store(self, memory_type: str, content: Dict[str, Any]) -> None:
        """
        Called when memory is stored.
        
        Args:
            memory_type: Type of memory being stored
            content: Memory content
        """
        pass
    
    def on_memory_retrieve(self, query: str, results: List[Dict[str, Any]]) -> None:
        """
        Called when memory is retrieved.
        
        Args:
            query: The search query
            results: Retrieved memory results
        """
        pass


class Plugin(ABC):
    """
    Base class for AI Agent Console plugins.
    
    All plugins must inherit from this class and implement the required methods.
    Plugins can register custom agents, tools, and hooks.
    """
    
    def __init__(self):
        """Initialize the plugin."""
        self.hooks = PluginHooks()
        self._agents: Dict[str, Type[Agent]] = {}
        self._tools: Dict[str, Type[Tool]] = {}
        self._config: Dict[str, Any] = {}
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Get plugin metadata.
        
        Returns:
            PluginMetadata object with plugin information
        """
        pass
    
    def register_agent(self, name: str, agent_class: Type[Agent]) -> None:
        """
        Register a custom agent.
        
        Args:
            name: Unique agent name
            agent_class: Agent class (must inherit from Agent)
        """
        if not issubclass(agent_class, Agent):
            raise TypeError(f"{agent_class} must inherit from Agent")
        
        self._agents[name] = agent_class
        logger.info(f"Plugin {self.get_metadata().name} registered agent: {name}")
    
    def register_tool(self, name: str, tool_class: Type[Tool]) -> None:
        """
        Register a custom tool.
        
        Args:
            name: Unique tool name
            tool_class: Tool class (must inherit from Tool)
        """
        if not issubclass(tool_class, Tool):
            raise TypeError(f"{tool_class} must inherit from Tool")
        
        self._tools[name] = tool_class
        logger.info(f"Plugin {self.get_metadata().name} registered tool: {name}")
    
    def get_agents(self) -> Dict[str, Type[Agent]]:
        """
        Get all agents registered by this plugin.
        
        Returns:
            Dictionary of agent name to agent class
        """
        return self._agents.copy()
    
    def get_tools(self) -> Dict[str, Type[Tool]]:
        """
        Get all tools registered by this plugin.
        
        Returns:
            Dictionary of tool name to tool class
        """
        return self._tools.copy()
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the plugin with settings from config.yaml.
        
        Args:
            config: Plugin configuration dictionary
        """
        self._config = config
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get plugin configuration.
        
        Returns:
            Plugin configuration dictionary
        """
        return self._config.copy()
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the plugin.
        
        This method is called after the plugin is loaded and configured.
        Use this to register agents, tools, and set up hooks.
        """
        pass
    
    def cleanup(self) -> None:
        """
        Cleanup plugin resources.
        
        This method is called before the plugin is unloaded.
        Override to perform cleanup tasks.
        """
        pass


class PluginError(Exception):
    """Base exception for plugin-related errors."""
    pass


class PluginLoadError(PluginError):
    """Exception raised when a plugin fails to load."""
    pass


class PluginInitializationError(PluginError):
    """Exception raised when a plugin fails to initialize."""
    pass


class PluginDependencyError(PluginError):
    """Exception raised when plugin dependencies are not met."""
    pass
