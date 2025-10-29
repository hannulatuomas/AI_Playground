
"""
Abstract base class for all tools in the AI Agent Console.

This module defines the Tool interface that all concrete tool
implementations must follow.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time


class Tool(ABC):
    """
    Abstract base class for all tools.
    
    Tools are utilities that agents can use to perform specific operations
    such as web fetching, git operations, or MCP protocol communication.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        config: Optional[Dict[str, Any]] = None,
        plugin_loader: Optional[Any] = None
    ):
        """
        Initialize the tool.
        
        Args:
            name: Tool name (unique identifier)
            description: Human-readable description of tool capabilities
            config: Optional configuration dictionary
            plugin_loader: Optional plugin loader for plugin hooks
        """
        self.name = name
        self.description = description
        self.config = config or {}
        self.plugin_loader = plugin_loader
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        self.logger.info(f"Tool '{name}' initialized")
    
    @abstractmethod
    def invoke(self, params: Dict[str, Any]) -> Any:
        """
        Invoke the tool with the given parameters.
        
        This is the main entry point for tool execution. Concrete tools
        must implement this method to perform their specific functionality.
        
        Args:
            params: Dictionary of parameters for the tool invocation
            
        Returns:
            Tool-specific result (can be any type)
            
        Raises:
            Exception: If invocation fails
        """
        pass
    
    def invoke_with_hooks(self, params: Dict[str, Any]) -> Any:
        """
        Invoke the tool with plugin hooks.
        
        This method wraps the invoke method and calls plugin hooks
        before and after invocation. Use this method when you want
        plugin integration; use invoke directly for no hooks.
        
        Args:
            params: Tool parameters
            
        Returns:
            Tool result
        """
        # Call before hooks
        if self.plugin_loader:
            for plugin in self.plugin_loader.get_all_plugins().values():
                try:
                    plugin.hooks.on_tool_execute_before(self, **params)
                except Exception as e:
                    self.logger.warning(f"Plugin hook error (before): {e}")
        
        # Invoke the tool
        result = self.invoke(params)
        
        # Call after hooks
        if self.plugin_loader:
            for plugin in self.plugin_loader.get_all_plugins().values():
                try:
                    plugin.hooks.on_tool_execute_after(self, result, **params)
                except Exception as e:
                    self.logger.warning(f"Plugin hook error (after): {e}")
        
        return result
    
    def invoke_with_retry(
        self,
        params: Dict[str, Any],
        max_retries: int = 3,
        initial_delay: float = 1.0
    ) -> Any:
        """
        Invoke tool with retry logic and exponential backoff.
        
        Args:
            params: Tool parameters
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            
        Returns:
            Tool result
            
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        delay = initial_delay
        
        for attempt in range(max_retries + 1):
            try:
                self.logger.debug(f"Tool '{self.name}' invocation attempt {attempt + 1}")
                return self.invoke(params)
                
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    self.logger.warning(
                        f"Tool '{self.name}' attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    self.logger.error(
                        f"Tool '{self.name}' failed after {max_retries + 1} attempts"
                    )
        
        raise RuntimeError(
            f"Tool '{self.name}' failed after {max_retries + 1} attempts"
        ) from last_exception
    
    def validate_params(self, params: Dict[str, Any], required: list) -> None:
        """
        Validate that required parameters are present.
        
        Args:
            params: Parameters to validate
            required: List of required parameter names
            
        Raises:
            ValueError: If required parameters are missing
        """
        missing = [key for key in required if key not in params]
        
        if missing:
            raise ValueError(
                f"Tool '{self.name}' missing required parameters: {', '.join(missing)}"
            )
    
    def _log_invocation(self, params: Dict[str, Any]) -> None:
        """
        Log tool invocation details.
        
        Args:
            params: Invocation parameters
        """
        # Mask sensitive data
        safe_params = self._mask_sensitive_params(params)
        self.logger.info(f"Tool '{self.name}' invoked with params: {safe_params}")
    
    def _mask_sensitive_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mask sensitive parameters for logging.
        
        Args:
            params: Original parameters
            
        Returns:
            Masked parameters dictionary
        """
        sensitive_keys = ['password', 'token', 'api_key', 'secret', 'auth']
        masked = params.copy()
        
        for key in masked:
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                value = masked[key]
                if isinstance(value, str) and len(value) > 8:
                    masked[key] = f"{value[:4]}...{value[-4:]}"
                else:
                    masked[key] = "***"
        
        return masked
    
    def __repr__(self) -> str:
        """String representation of the tool."""
        return f"<{self.__class__.__name__}(name='{self.name}')>"
