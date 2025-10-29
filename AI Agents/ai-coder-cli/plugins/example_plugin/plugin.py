
"""
Example Plugin for AI Agent Console

This is a complete example plugin that demonstrates how to:
- Create custom agents
- Create custom tools
- Use plugin hooks
- Configure plugins
- Access the system
"""

import logging
from typing import Dict, Any

from core.plugin_base import Plugin, PluginMetadata
from agents.base.agent_base import Agent
from tools.base import Tool


logger = logging.getLogger(__name__)


class ExampleCustomAgent(Agent):
    """
    Example custom agent that performs specialized tasks.
    
    This agent demonstrates how to create a custom agent in a plugin.
    """
    
    def __init__(self, llm_router, tool_registry, config):
        """
        Initialize the example agent.
        
        Args:
            llm_router: LLM router for making queries
            tool_registry: Tool registry for using tools
            config: Configuration dictionary
        """
        super().__init__(llm_router, tool_registry, config)
        self.name = "ExampleCustomAgent"
        self.description = "Example agent demonstrating plugin capabilities"
        self.capabilities = ["example_task", "demo_task"]
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task using the example agent.
        
        Args:
            task: Task description
            context: Execution context
            
        Returns:
            Result dictionary with success status and data
        """
        try:
            logger.info(f"ExampleCustomAgent executing task: {task}")
            
            # Example: Use LLM
            prompt = f"""
            You are an example agent in a plugin system.
            Task: {task}
            Context: {context}
            
            Provide a demonstration response.
            """
            
            llm_response = self.llm_router.query(
                prompt,
                model=self.config.get("agents.model_assignments.example_agent", "llama3.3:latest"),
                temperature=0.7
            )
            
            # Example: Use a tool
            # tool = self.tool_registry.get_tool("FileOperations")
            # tool_result = tool.execute(...)
            
            return {
                "success": True,
                "message": "Example agent completed successfully",
                "data": {
                    "task": task,
                    "response": llm_response,
                    "agent": self.name
                }
            }
            
        except Exception as e:
            logger.error(f"ExampleCustomAgent error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }


class ExampleCustomTool(Tool):
    """
    Example custom tool that performs specialized operations.
    
    This tool demonstrates how to create a custom tool in a plugin.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the example tool.
        
        Args:
            config: Tool configuration
        """
        super().__init__(config)
        self.name = "ExampleCustomTool"
        self.description = "Example tool demonstrating plugin capabilities"
    
    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool operation.
        
        Args:
            operation: Operation to perform
            **kwargs: Operation parameters
            
        Returns:
            Result dictionary
        """
        try:
            logger.info(f"ExampleCustomTool executing: {operation}")
            
            if operation == "demo":
                return {
                    "success": True,
                    "result": "Demo operation completed",
                    "data": kwargs
                }
            elif operation == "greet":
                name = kwargs.get("name", "World")
                return {
                    "success": True,
                    "result": f"Hello, {name}!",
                    "message": "Greeting generated"
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
                
        except Exception as e:
            logger.error(f"ExampleCustomTool error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_input(self, operation: str, **kwargs) -> bool:
        """
        Validate tool input.
        
        Args:
            operation: Operation to validate
            **kwargs: Operation parameters
            
        Returns:
            True if valid, False otherwise
        """
        valid_operations = ["demo", "greet"]
        return operation in valid_operations


class ExamplePlugin(Plugin):
    """
    Example plugin demonstrating the plugin system.
    
    This plugin shows how to:
    - Register custom agents and tools
    - Use plugin hooks
    - Access configuration
    - Interact with the system
    """
    
    def get_metadata(self) -> PluginMetadata:
        """
        Get plugin metadata.
        
        Returns:
            PluginMetadata with plugin information
        """
        return PluginMetadata(
            name="example_plugin",
            version="1.0.0",
            author="AI Agent Console Team",
            description="Example plugin demonstrating plugin system capabilities",
            homepage="https://github.com/yourusername/ai-agent-console",
            dependencies=[],  # No dependencies for this example
            min_console_version="2.4.0"
        )
    
    def initialize(self) -> None:
        """
        Initialize the plugin.
        
        This is called after the plugin is loaded and configured.
        Register agents, tools, and set up hooks here.
        """
        logger.info("Initializing ExamplePlugin")
        
        # Register custom agent
        self.register_agent("ExampleCustomAgent", ExampleCustomAgent)
        logger.info("Registered ExampleCustomAgent")
        
        # Register custom tool
        self.register_tool("ExampleCustomTool", ExampleCustomTool)
        logger.info("Registered ExampleCustomTool")
        
        # Set up hooks
        self.hooks.on_load = self._on_load
        self.hooks.on_unload = self._on_unload
        self.hooks.on_agent_execute_before = self._before_agent_execute
        self.hooks.on_agent_execute_after = self._after_agent_execute
        
        logger.info("ExamplePlugin initialized successfully")
    
    def cleanup(self) -> None:
        """
        Cleanup plugin resources.
        
        This is called before the plugin is unloaded.
        """
        logger.info("Cleaning up ExamplePlugin")
        # Add cleanup logic here if needed
    
    def _on_load(self) -> None:
        """Called when the plugin is loaded."""
        logger.info("ExamplePlugin loaded!")
        config = self.get_config()
        if config:
            logger.info(f"ExamplePlugin configuration: {config}")
    
    def _on_unload(self) -> None:
        """Called when the plugin is unloaded."""
        logger.info("ExamplePlugin unloaded!")
    
    def _before_agent_execute(
        self,
        agent: Agent,
        task: str,
        context: Dict[str, Any]
    ) -> None:
        """
        Called before any agent executes.
        
        Args:
            agent: The agent about to execute
            task: The task to execute
            context: Execution context
        """
        logger.debug(f"Agent {agent.name} about to execute: {task[:50]}...")
    
    def _after_agent_execute(
        self,
        agent: Agent,
        task: str,
        context: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        """
        Called after any agent executes.
        
        Args:
            agent: The agent that executed
            task: The executed task
            context: Execution context
            result: Execution result
        """
        success = result.get("success", False)
        logger.debug(f"Agent {agent.name} execution {'succeeded' if success else 'failed'}")
