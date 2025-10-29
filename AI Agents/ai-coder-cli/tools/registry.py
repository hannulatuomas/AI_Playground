
"""
Tool registry for managing and discovering tools.

This module provides a centralized registry for tool classes,
enabling dynamic tool discovery and instantiation.
"""

import logging
from typing import Dict, List, Type, Optional, Any


logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry for managing tool classes and instances.
    
    Implements a singleton pattern to ensure a single global registry.
    Supports dynamic tool registration and retrieval.
    """
    
    _instance: Optional['ToolRegistry'] = None
    
    def __new__(cls) -> 'ToolRegistry':
        """
        Ensure only one registry instance exists (Singleton pattern).
        
        Returns:
            The singleton ToolRegistry instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry (only once)."""
        if self._initialized:
            return
        
        self._tools: Dict[str, Any] = {}
        self._initialized = True
        
        logger.info("ToolRegistry initialized")
    
    @classmethod
    def get_instance(cls) -> 'ToolRegistry':
        """
        Get the singleton registry instance.
        
        This is a class method for accessing the singleton instance,
        useful for tests and plugin integrations.
        
        Returns:
            The singleton ToolRegistry instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register(self, tool: Any, name: Optional[str] = None) -> None:
        """
        Register a tool instance or class.
        
        Args:
            tool: Tool instance or class to register
            name: Optional custom name (defaults to tool.name for instances)
            
        Raises:
            ValueError: If tool is invalid or name conflicts
        """
        # Use tool's name if not provided
        if name is None:
            # For instances, try to get the name attribute
            if hasattr(tool, 'name') and not isinstance(tool, type):
                name = tool.name
            else:
                raise ValueError("Tool must have a 'name' attribute or name must be provided")
        
        # Warn if overwriting
        if name in self._tools:
            logger.warning(f"Tool '{name}' is already registered, overwriting")
        
        self._tools[name] = tool
        
        # Log appropriately based on whether it's a class or instance
        if isinstance(tool, type):
            logger.info(f"Registered tool: {name} (class: {tool.__name__})")
        else:
            logger.info(f"Registered tool: {name} (instance: {tool.__class__.__name__})")
    
    def get(self, name: str) -> Optional[Any]:
        """
        Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """
        List all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())
    
    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered tools with metadata.
        
        Returns:
            Dictionary mapping tool names to metadata:
                - class_name: Class name
                - description: Tool description
        """
        result = {}
        
        for name, tool in self._tools.items():
            result[name] = {
                'class_name': tool.__class__.__name__,
                'description': getattr(tool, 'description', 'No description')
            }
        
        return result
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            name: Tool name
            
        Returns:
            True if tool was removed, False if not found
        """
        if name in self._tools:
            del self._tools[name]
            logger.info(f"Unregistered tool: {name}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all registered tools."""
        count = len(self._tools)
        self._tools.clear()
        logger.info(f"Cleared {count} registered tools")
    
    def __len__(self) -> int:
        """Return number of registered tools."""
        return len(self._tools)
    
    def __repr__(self) -> str:
        """String representation of the registry."""
        return f"<ToolRegistry(tools={len(self._tools)})>"
