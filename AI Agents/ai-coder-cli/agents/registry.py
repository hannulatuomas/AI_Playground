
"""
Agent registry for managing and discovering agents.

This module provides a centralized registry for agent classes,
enabling dynamic agent discovery and instantiation.
"""

import logging
from typing import Dict, List, Type, Optional, Any


logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Registry for managing agent classes and instances.
    
    Implements a singleton pattern to ensure a single global registry.
    Supports dynamic agent registration and instantiation.
    """
    
    _instance: Optional['AgentRegistry'] = None
    
    def __new__(cls) -> 'AgentRegistry':
        """
        Ensure only one registry instance exists (Singleton pattern).
        
        Returns:
            The singleton AgentRegistry instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry (only once)."""
        if self._initialized:
            return
        
        self._agent_classes: Dict[str, Type] = {}
        self._agent_instances: Dict[str, Any] = {}
        self._initialized = True
        
        logger.info("AgentRegistry initialized")
    
    @classmethod
    def get_instance(cls) -> 'AgentRegistry':
        """
        Get the singleton registry instance.
        
        This is a class method for accessing the singleton instance,
        useful for tests and plugin integrations.
        
        Returns:
            The singleton AgentRegistry instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register(self, agent_class: Type, name: Optional[str] = None) -> None:
        """
        Register an agent class.
        
        Args:
            agent_class: The agent class to register (must inherit from Agent)
            name: Optional custom name (defaults to class-derived name)
            
        Raises:
            ValueError: If agent class is invalid or name conflicts
        """
        # Derive name from class if not provided
        if name is None:
            # Convert CamelCase to snake_case
            class_name = agent_class.__name__
            if class_name.endswith('Agent'):
                class_name = class_name[:-5]  # Remove 'Agent' suffix
            
            # Convert to snake_case
            import re
            name = re.sub('([A-Z]+)', r'_\1', class_name).lower().strip('_')
        
        # Validate
        if name in self._agent_classes:
            logger.warning(f"Agent '{name}' is already registered, overwriting")
        
        self._agent_classes[name] = agent_class
        logger.info(f"Registered agent: {name} ({agent_class.__name__})")
    
    def get(self, name: str) -> Optional[Type]:
        """
        Get an agent class by name.
        
        Args:
            name: Agent name
            
        Returns:
            Agent class or None if not found
        """
        return self._agent_classes.get(name)
    
    def get_or_create_agent(
        self,
        name: str,
        llm_router: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[Any] = None,
        plugin_loader: Optional[Any] = None,
        force_new: bool = False
    ) -> Any:
        """
        Get or create an agent instance.
        
        This method maintains a cache of agent instances. By default, it returns
        the cached instance if available. Use force_new=True to create a new instance.
        
        Args:
            name: Agent name
            llm_router: LLM router for the agent
            tool_registry: Tool registry for the agent
            config: Configuration dictionary
            memory_manager: Memory manager for conversation history
            plugin_loader: Plugin loader for plugin hooks
            force_new: Force creation of new instance
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: If agent not found or instantiation fails
        """
        # Check cache (unless force_new)
        if not force_new and name in self._agent_instances:
            logger.debug(f"Returning cached agent instance: {name}")
            return self._agent_instances[name]
        
        # Get agent class
        agent_class = self.get(name)
        if not agent_class:
            raise ValueError(f"Agent not found: {name}")
        
        # Get description from class
        description = getattr(agent_class, '__doc__', f'{name} agent').split('\n')[0]
        
        # Instantiate
        try:
            # Try to instantiate with all parameters (memory_manager and plugin_loader)
            try:
                agent_instance = agent_class(
                    name=name,
                    description=description,
                    llm_router=llm_router,
                    tool_registry=tool_registry,
                    config=config,
                    memory_manager=memory_manager,
                    plugin_loader=plugin_loader
                )
            except TypeError:
                # Fallback for agents that don't support plugin_loader yet (try with memory_manager)
                try:
                    agent_instance = agent_class(
                        name=name,
                        description=description,
                        llm_router=llm_router,
                        tool_registry=tool_registry,
                        config=config,
                        memory_manager=memory_manager
                    )
                except TypeError:
                    # Fallback for agents that don't support memory_manager or plugin_loader
                    logger.debug(f"Agent '{name}' does not support memory_manager/plugin_loader parameters, using fallback")
                    agent_instance = agent_class(
                        name=name,
                        description=description,
                        llm_router=llm_router,
                        tool_registry=tool_registry,
                        config=config
                    )
            
            # Cache instance
            self._agent_instances[name] = agent_instance
            logger.debug(f"Created and cached agent instance: {name}")
            
            return agent_instance
            
        except Exception as e:
            logger.error(f"Failed to instantiate agent '{name}': {e}")
            raise ValueError(f"Failed to create agent '{name}': {e}") from e
    
    def list_agents(self) -> List[str]:
        """
        List all registered agent names.
        
        Returns:
            List of agent names
        """
        return list(self._agent_classes.keys())
    
    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered agents with metadata.
        
        Returns:
            Dictionary mapping agent names to metadata:
                - class_name: Class name
                - description: Agent description
                - instance_cached: Whether instance is cached
        """
        result = {}
        
        for name, agent_class in self._agent_classes.items():
            result[name] = {
                'class_name': agent_class.__name__,
                'description': getattr(agent_class, '__doc__', 'No description').split('\n')[0],
                'instance_cached': name in self._agent_instances
            }
        
        return result
    
    def unregister(self, name: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            name: Agent name
            
        Returns:
            True if agent was removed, False if not found
        """
        removed = False
        
        # Remove from class registry
        if name in self._agent_classes:
            del self._agent_classes[name]
            removed = True
        
        # Remove from instance cache
        if name in self._agent_instances:
            del self._agent_instances[name]
        
        if removed:
            logger.info(f"Unregistered agent: {name}")
        
        return removed
    
    def clear_cache(self) -> None:
        """Clear all cached agent instances."""
        count = len(self._agent_instances)
        self._agent_instances.clear()
        logger.info(f"Cleared {count} cached agent instances")
    
    def get_for_task(self, task_description: str) -> List[str]:
        """
        Get suggested agents for a task (simple keyword-based).
        
        This is a fallback method for task analysis. The primary task
        analysis should use LLM-based classification.
        
        Args:
            task_description: Description of the task
            
        Returns:
            List of suggested agent names
        """
        task_lower = task_description.lower()
        suggested = []
        
        # Simple keyword matching
        keywords = {
            'code_planner': ['plan', 'design', 'architecture', 'structure', 'organize'],
            'code_editor': ['create', 'write', 'modify', 'edit', 'file', 'code'],
            'git_agent': ['git', 'commit', 'push', 'version', 'repository'],
            'web_data': ['web', 'fetch', 'download', 'scrape', 'url', 'http']
        }
        
        for agent_name, agent_keywords in keywords.items():
            if agent_name in self._agent_classes:
                if any(keyword in task_lower for keyword in agent_keywords):
                    suggested.append(agent_name)
        
        return suggested or ['code_planner']  # Default fallback
    
    def __len__(self) -> int:
        """Return number of registered agents."""
        return len(self._agent_classes)
    
    def __repr__(self) -> str:
        """String representation of the registry."""
        return f"<AgentRegistry(agents={len(self._agent_classes)}, cached={len(self._agent_instances)})>"
