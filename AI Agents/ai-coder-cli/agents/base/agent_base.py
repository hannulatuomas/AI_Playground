

"""
Abstract base class for all agents in the AI Agent Console.

This module defines the Agent interface that all concrete agent
implementations must follow. Includes integrated memory management
for conversation history and context persistence.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

# Import capability manager
try:
    from core.agent_capabilities import CapabilityManager
    CAPABILITIES_AVAILABLE = True
except ImportError:
    CAPABILITIES_AVAILABLE = False


class Agent(ABC):
    """
    Abstract base class for all agents.
    
    Agents are autonomous components that perform specific tasks such as
    code generation, file editing, git operations, or web data retrieval.
    
    The base agent class provides:
    - LLM integration for AI-powered decision making
    - Tool access for executing actions
    - Memory integration for conversation history and context
    - Standardized logging and error handling
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        llm_router: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[Any] = None,
        plugin_loader: Optional[Any] = None
    ):
        """
        Initialize the agent.
        
        Args:
            name: Agent name (unique identifier)
            description: Human-readable description of agent capabilities
            llm_router: LLM router for making LLM queries
            tool_registry: Registry of available tools
            config: Optional configuration dictionary
            memory_manager: Optional memory manager for conversation history
            plugin_loader: Optional plugin loader for plugin hooks
        """
        self.name = name
        self.description = description
        self.llm_router = llm_router
        self.tool_registry = tool_registry
        self.config = config or {}
        self.memory_manager = memory_manager
        self.plugin_loader = plugin_loader
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize capability manager if available
        if CAPABILITIES_AVAILABLE:
            self.capabilities = CapabilityManager(
                config=self.config,
                memory_manager=self.memory_manager
            )
            self.logger.debug(f"Capabilities initialized for agent '{name}'")
        else:
            self.capabilities = None
            self.logger.warning("Capabilities not available (import failed)")
        
        self.logger.info(f"Agent '{name}' initialized")
    
    @abstractmethod
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with the given context.
        
        This is the main entry point for agent execution. Concrete agents
        must implement this method to perform their specific functionality.
        
        Args:
            task: Task description or instruction
            context: Execution context containing:
                - previous agent results
                - user preferences
                - shared state
                
        Returns:
            Dictionary containing:
                - success: bool - Whether execution succeeded
                - message: str - Status/result message
                - data: Any - Task-specific output data
                - next_context: dict - Updated context for next agent
                
        Raises:
            Exception: If execution fails critically
        """
        pass
    
    def execute_with_hooks(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with plugin hooks.
        
        This method wraps the execute method and calls plugin hooks
        before and after execution. Use this method when you want
        plugin integration; use execute directly for no hooks.
        
        Args:
            task: Task description or instruction
            context: Execution context
            
        Returns:
            Dictionary containing execution result
        """
        # Call before hooks
        if self.plugin_loader:
            for plugin in self.plugin_loader.get_all_plugins().values():
                try:
                    plugin.hooks.on_agent_execute_before(self, task, context)
                except Exception as e:
                    self.logger.warning(f"Plugin hook error (before): {e}")
        
        # Execute the task
        result = self.execute(task, context)
        
        # Call after hooks
        if self.plugin_loader:
            for plugin in self.plugin_loader.get_all_plugins().values():
                try:
                    plugin.hooks.on_agent_execute_after(self, task, context, result)
                except Exception as e:
                    self.logger.warning(f"Plugin hook error (after): {e}")
        
        return result
    
    def _get_llm_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Helper method to get LLM response with model selection from config.
        
        Args:
            prompt: The prompt to send to LLM
            model: Optional model override (if None, uses config)
            temperature: Optional temperature override (if None, uses config)
            **kwargs: Additional LLM parameters
            
        Returns:
            Dictionary with LLM response data
            
        Raises:
            RuntimeError: If LLM router is not available
        """
        if not self.llm_router:
            raise RuntimeError(f"Agent '{self.name}' does not have LLM router configured")
        
        # Get model from config if not specified
        if model is None:
            model = self._get_assigned_model()
        
        # Get temperature from config if not specified
        if temperature is None:
            temperature = self._get_assigned_temperature()
        
        self.logger.debug(f"Querying LLM with model={model}, temp={temperature}, prompt_len={len(prompt)}")
        
        try:
            result = self.llm_router.query(
                prompt=prompt, 
                model=model, 
                temperature=temperature,
                **kwargs
            )
            self.logger.info(f"LLM query successful: model={result.get('model')}, provider={result.get('provider')}")
            return result
        except Exception as e:
            self.logger.error(f"LLM query failed: {e}")
            # Try fallback model if primary fails
            fallback_model = self._get_fallback_model()
            if fallback_model and fallback_model != model:
                self.logger.info(f"Attempting fallback to model: {fallback_model}")
                try:
                    result = self.llm_router.query(
                        prompt=prompt,
                        model=fallback_model,
                        temperature=temperature,
                        **kwargs
                    )
                    self.logger.info(f"Fallback query successful: model={result.get('model')}")
                    return result
                except Exception as fallback_error:
                    self.logger.error(f"Fallback query also failed: {fallback_error}")
            raise
    
    def _get_assigned_model(self) -> Optional[str]:
        """
        Get the assigned model for this agent from config.
        
        Returns:
            Model name or None if not configured
        """
        if not self.config:
            return None
        
        # Try to get model assignment from config
        model_assignments = self.config.get('model_assignments', {})
        agent_assignment = model_assignments.get(self.name, {})
        
        if isinstance(agent_assignment, dict):
            return agent_assignment.get('primary')
        
        return None
    
    def _get_fallback_model(self) -> Optional[str]:
        """
        Get the fallback model for this agent from config.
        
        Returns:
            Fallback model name or None if not configured
        """
        if not self.config:
            return None
        
        model_assignments = self.config.get('model_assignments', {})
        agent_assignment = model_assignments.get(self.name, {})
        
        if isinstance(agent_assignment, dict):
            return agent_assignment.get('fallback')
        
        return None
    
    def _get_assigned_temperature(self) -> float:
        """
        Get the assigned temperature for this agent from config.
        
        Returns:
            Temperature value (default 0.7 if not configured)
        """
        if not self.config:
            return 0.7
        
        model_assignments = self.config.get('model_assignments', {})
        agent_assignment = model_assignments.get(self.name, {})
        
        if isinstance(agent_assignment, dict):
            return agent_assignment.get('temperature', 0.7)
        
        return 0.7
    
    def _log_action(self, action: str, details: Optional[str] = None) -> None:
        """
        Helper method to log agent actions.
        
        Args:
            action: Action being performed
            details: Optional additional details
        """
        log_message = f"[{self.name}] {action}"
        if details:
            log_message += f": {details}"
        
        self.logger.info(log_message)
    
    def _get_tool(self, tool_name: str) -> Optional[Any]:
        """
        Helper method to retrieve a tool from the registry.
        
        Args:
            tool_name: Name of the tool to retrieve
            
        Returns:
            Tool instance or None if not found
        """
        if not self.tool_registry:
            self.logger.warning(f"No tool registry available for agent '{self.name}'")
            return None
        
        try:
            tool = self.tool_registry.get(tool_name)
            if tool:
                self.logger.debug(f"Retrieved tool: {tool_name}")
            else:
                self.logger.warning(f"Tool not found: {tool_name}")
            return tool
        except Exception as e:
            self.logger.error(f"Failed to retrieve tool '{tool_name}': {e}")
            return None
    
    def _build_error_result(self, message: str, error: Optional[Exception] = None) -> Dict[str, Any]:
        """
        Build a standardized error result.
        
        Args:
            message: Error message
            error: Optional exception object
            
        Returns:
            Error result dictionary
        """
        result = {
            'success': False,
            'message': message,
            'data': None,
            'next_context': {}
        }
        
        if error:
            result['error'] = str(error)
            result['error_type'] = type(error).__name__
        
        return result
    
    def _build_success_result(
        self,
        message: str,
        data: Any = None,
        next_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build a standardized success result.
        
        Args:
            message: Success message
            data: Optional result data
            next_context: Optional context updates for next agent
            
        Returns:
            Success result dictionary
        """
        return {
            'success': True,
            'message': message,
            'data': data,
            'next_context': next_context or {}
        }
    
    # ========================================================================
    # Memory Management Methods
    # ========================================================================
    
    def _get_memory_context(
        self,
        session_id: str,
        max_messages: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history from memory for context.
        
        Args:
            session_id: Memory session ID
            max_messages: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        if not self.memory_manager:
            self.logger.debug("No memory manager available")
            return []
        
        try:
            context = self.memory_manager.get_context_for_agent(
                session_id=session_id,
                agent_name=self.name,
                max_messages=max_messages
            )
            self.logger.debug(f"Retrieved {len(context)} messages from memory")
            return context
        except Exception as e:
            self.logger.error(f"Failed to get memory context: {e}")
            return []
    
    def _add_to_memory(
        self,
        session_id: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add agent's response to memory.
        
        Args:
            session_id: Memory session ID
            message: Agent's response message
            metadata: Optional message metadata
            
        Returns:
            True if added successfully
        """
        if not self.memory_manager:
            self.logger.debug("No memory manager available")
            return False
        
        try:
            success = self.memory_manager.add_agent_message(
                session_id=session_id,
                content=message,
                agent_name=self.name,
                metadata=metadata
            )
            if success:
                self.logger.debug(f"Added message to memory (session: {session_id[:8]})")
            return success
        except Exception as e:
            self.logger.error(f"Failed to add to memory: {e}")
            return False
    
    def _format_memory_context_for_prompt(
        self,
        context: List[Dict[str, Any]]
    ) -> str:
        """
        Format memory context for inclusion in LLM prompts.
        
        Args:
            context: List of message dictionaries from memory
            
        Returns:
            Formatted context string
        """
        if not context:
            return ""
        
        formatted_lines = ["Previous conversation context:"]
        for msg in context:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            agent_name = msg.get('agent_name', '')
            
            if role == 'user':
                formatted_lines.append(f"User: {content}")
            elif role == 'agent':
                formatted_lines.append(f"Agent ({agent_name}): {content}")
            elif role == 'system':
                formatted_lines.append(f"System: {content}")
        
        formatted_lines.append("")  # Empty line separator
        return "\n".join(formatted_lines)
    
    # ========================================================================
    # Language Documentation Loading (for language-specific agents)
    # ========================================================================
    
    def _load_language_docs(self) -> None:
        """
        Load language-specific documentation with priority system.
        
        DOCUMENTATION LOADING PRIORITY (CRITICAL):
        1. Load best_practices.md FIRST - provides general guidelines
        2. Load user_preferences.md SECOND - overrides best practices
        3. user_preferences.md is the LAST SOURCE OF TRUTH
        
        This ensures that user customizations always take precedence over
        default best practices when conflicts arise.
        
        Sets:
            self.best_practices: Content of best_practices.md (or None)
            self.user_preferences: Content of user_preferences.md (or None)
        
        Usage:
            In language-specific agents, call this method in __init__:
            
            ```python
            def __init__(self, ...):
                super().__init__(...)
                self._load_language_docs()
            ```
            
            Then in prompts, include both with clear priority:
            
            ```python
            prompt = f\"\"\"
            Best Practices:
            {self.best_practices if self.best_practices else 'N/A'}
            
            User Preferences (FINAL AUTHORITY - override conflicts):
            {self.user_preferences if self.user_preferences else 'N/A'}
            \"\"\"
            ```
        """
        docs_dir = Path(__file__).parent.parent / 'languages'
        
        # Determine language directory based on agent name
        # Extract language from agent name (e.g., "code_editor_python" -> "python")
        language = None
        agent_name_lower = self.name.lower()
        
        # Map common language identifiers to directory names
        lang_mapping = {
            'python': 'python',
            'webdev': 'web',
            'web': 'web',
            'javascript': 'web',
            'typescript': 'web',
            'js': 'web',
            'ts': 'web',
            'bash': 'bash',
            'sh': 'bash',
            'shell': 'bash',
            'zsh': 'bash',
            'csharp': 'csharp',
            'c#': 'csharp',
            'dotnet': 'csharp',
            'cpp': 'cpp',
            'c++': 'cpp',
            'powershell': 'powershell',
            'ps1': 'powershell',
            'batch': 'batch',
            'cmd': 'batch',
        }
        
        # Try to detect language from agent name
        for key, dir_name in lang_mapping.items():
            if key in agent_name_lower:
                language = dir_name
                break
        
        if not language:
            self.logger.warning(f"Could not determine language for agent '{self.name}'")
            self.best_practices = None
            self.user_preferences = None
            return
        
        language_dir = docs_dir / language
        
        if not language_dir.exists():
            self.logger.warning(f"Language directory not found: {language_dir}")
            self.best_practices = None
            self.user_preferences = None
            return
        
        # Initialize to None
        self.best_practices = None
        self.user_preferences = None
        
        # STEP 1: Load best_practices.md FIRST
        try:
            best_practices_file = language_dir / 'best_practices.md'
            if best_practices_file.exists():
                with open(best_practices_file, 'r', encoding='utf-8') as f:
                    self.best_practices = f.read()
                self.logger.info(f"Loaded best_practices.md for {language}")
            else:
                self.logger.warning(f"best_practices.md not found in {language_dir}")
        except Exception as e:
            self.logger.error(f"Failed to load best_practices.md: {e}")
        
        # STEP 2: Load user_preferences.md SECOND (overrides conflicts)
        try:
            user_prefs_file = language_dir / 'user_preferences.md'
            if user_prefs_file.exists():
                with open(user_prefs_file, 'r', encoding='utf-8') as f:
                    self.user_preferences = f.read()
                self.logger.info(f"Loaded user_preferences.md for {language} (FINAL AUTHORITY)")
            else:
                self.logger.warning(f"user_preferences.md not found in {language_dir}")
        except Exception as e:
            self.logger.error(f"Failed to load user_preferences.md: {e}")
        
        # Log priority reminder
        if self.best_practices and self.user_preferences:
            self.logger.info(
                f"Documentation loaded for {language} with priority: "
                "best_practices.md → user_preferences.md (FINAL)"
            )
    
    def _get_documentation_prompt(self) -> str:
        """
        Get formatted documentation for inclusion in LLM prompts.
        
        Returns a formatted string that clearly indicates the priority
        of user_preferences.md over best_practices.md.
        
        Returns:
            Formatted documentation string for prompts
        """
        if not hasattr(self, 'best_practices') or not hasattr(self, 'user_preferences'):
            return ""
        
        sections = []
        
        if self.best_practices:
            sections.append(f"""## Best Practices (General Guidelines)

{self.best_practices}
""")
        
        if self.user_preferences:
            sections.append(f"""## User Preferences (⚠️ FINAL AUTHORITY - Override Any Conflicts Above)

**CRITICAL**: These user preferences are the LAST SOURCE OF TRUTH. 
If any settings conflict with best practices above, ALWAYS use these preferences.

{self.user_preferences}
""")
        
        if not sections:
            return ""
        
        return "\n\n" + "\n\n".join(sections) + "\n\n"
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        memory_status = "with memory" if self.memory_manager else "no memory"
        return f"<{self.__class__.__name__}(name='{self.name}', {memory_status})>"
