
"""
Main orchestration engine for the AI Agent Console.

This module contains the core engine that coordinates configuration loading,
LLM routing, query processing, and agent orchestration with task analysis.
Includes Rich UI components for beautiful progress tracking and formatted output.
"""

import logging
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

# Rich imports for beautiful console output
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.status import Status
from rich.logging import RichHandler
from rich.table import Table
from rich import box
from rich.text import Text

from .config import AppConfig, setup_logging
from .llm_router import LLMRouter, LLMProviderError
from .memory import MemoryManager
from .project_manager import ProjectManager
from .chat_history import ChatHistoryManager

# Import orchestration system
try:
    from orchestration.workflows.workflow_manager import WorkflowManager
    WORKFLOWS_AVAILABLE = True
except ImportError:
    WORKFLOWS_AVAILABLE = False

# Import agent and tool systems
try:
    from agents import AgentRegistry, Agent
    from agents.generic import GenericCodeEditor, GenericCodePlanner
    from agents.git_agent import GitAgent
    from agents.web_data import WebDataAgent
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False

try:
    from tools import ToolRegistry, Tool
    from tools.web_fetch import WebFetchTool
    from tools.git import GitTool
    from tools.mcp import MCPClientTool
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False

# Import plugin system
try:
    from core.plugin_loader import PluginLoader
    PLUGINS_AVAILABLE = True
except ImportError:
    PLUGINS_AVAILABLE = False


logger = logging.getLogger(__name__)

# Initialize Rich Console for engine operations
_console = Console()


# ============================================================================
# Rich UI Helper Functions for Engine
# ============================================================================

def _print_engine_status(message: str, status: str = "info") -> None:
    """
    Print color-coded status messages in the engine.
    
    Args:
        message: Status message to display
        status: Type of status (info, success, warning, error)
    """
    if status == "success":
        _console.print(f"[bold green]✓[/bold green] {message}")
    elif status == "error":
        _console.print(f"[bold red]✗[/bold red] {message}", style="red")
    elif status == "warning":
        _console.print(f"[bold yellow]⚠[/bold yellow] {message}", style="yellow")
    else:  # info
        _console.print(f"[bold blue]ℹ[/bold blue] {message}", style="blue")


def _create_task_summary_panel(task: str, analysis: Dict[str, Any]) -> Panel:
    """
    Create a Rich panel for task summary.
    
    Args:
        task: Task description
        analysis: Task analysis dictionary
        
    Returns:
        Rich Panel object
    """
    content = f"[cyan]Task:[/cyan] {task}\n"
    content += f"[cyan]Selected Agents:[/cyan] {', '.join(analysis.get('agents', []))}\n"
    content += f"[cyan]Reasoning:[/cyan] {analysis.get('reasoning', 'N/A')}"
    
    return Panel(
        content,
        title="[bold magenta]🎯 Task Summary",
        border_style="magenta",
        padding=(1, 2)
    )


def _create_orchestration_table(results: List[Dict[str, Any]]) -> Table:
    """
    Create a Rich table for orchestration results.
    
    Args:
        results: List of agent execution results
        
    Returns:
        Rich Table object
    """
    table = Table(
        title="🎯 Orchestration Results",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("№", style="cyan", width=5)
    table.add_column("Agent", style="magenta", width=20)
    table.add_column("Status", style="white", width=12)
    table.add_column("Message", style="white", width=45)
    
    for i, result in enumerate(results, 1):
        agent_name = result.get('agent', 'unknown')
        agent_data = result.get('result', {})
        success = agent_data.get('success', False)
        message = agent_data.get('message', 'No message')
        
        status_text = "[bold green]✓ Success[/bold green]" if success else "[bold red]✗ Failed[/bold red]"
        table.add_row(str(i), agent_name, status_text, message[:45])
    
    return table


class EngineError(Exception):
    """Base exception for engine errors."""
    pass


class TaskAnalyzer:
    """
    LLM-based task analyzer for determining agent execution sequence.
    
    Analyzes user tasks and determines which agents should be used
    and in what order to accomplish the task.
    """
    
    def __init__(self, llm_router: LLMRouter):
        """
        Initialize the task analyzer.
        
        Args:
            llm_router: LLM router for making analysis calls
        """
        self.llm_router = llm_router
        self.logger = logging.getLogger(f"{__name__}.TaskAnalyzer")
    
    def analyze_task(self, task: str, available_agents: List[str]) -> Dict[str, Any]:
        """
        Analyze a task and determine required agents.
        
        Args:
            task: User's task description
            available_agents: List of available agent names
            
        Returns:
            Dictionary containing:
                - agents: List of agent names to use in order
                - reasoning: Explanation of agent selection
                - parallel: Whether agents can run in parallel
        """
        self.logger.info(f"Analyzing task: {task[:100]}...")
        
        prompt = self._build_analysis_prompt(task, available_agents)
        
        try:
            # Use Rich status spinner for LLM call
            with _console.status("[bold cyan]🤖 Analyzing task with LLM...", spinner="dots") as status:
                response = self.llm_router.query(prompt=prompt, temperature=0.3)
                analysis = self._parse_analysis(response['response'])
            
            self.logger.info(f"Task analysis complete: {len(analysis['agents'])} agents selected")
            _print_engine_status(
                f"Task analysis complete: {len(analysis['agents'])} agent(s) selected",
                "success"
            )
            return analysis
            
        except Exception as e:
            self.logger.error(f"Task analysis failed: {e}")
            _print_engine_status(f"Task analysis failed, using fallback: {e}", "warning")
            # Fallback to basic analysis
            return self._fallback_analysis(task, available_agents)
    
    def _build_analysis_prompt(self, task: str, available_agents: List[str]) -> str:
        """Build the LLM prompt for task analysis."""
        return f"""Analyze the following task and determine which agents are needed to complete it.

Task: {task}

Available Agents:
- code_planner: Plans software projects, generates file structures and implementation plans
- code_editor: Creates and modifies code files with user confirmation
- git_agent: Handles Git operations (init, add, commit, push) with confirmations
- web_data: Retrieves and processes web data, fetches URLs

Instructions:
1. Identify which agents are needed to complete this task
2. Determine the order in which agents should execute
3. Provide reasoning for your selections

Respond with JSON in this format:
{{
    "agents": ["agent1", "agent2"],
    "reasoning": "Explanation of why these agents in this order",
    "parallel": false
}}

Only include agents from the available list. Return ONLY the JSON, no additional text.
"""
    
    def _parse_analysis(self, response: str) -> Dict[str, Any]:
        """Parse LLM analysis response."""
        try:
            # Find JSON in response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response[json_start:json_end]
            analysis = json.loads(json_text)
            
            # Validate structure
            if 'agents' not in analysis:
                analysis['agents'] = []
            if 'reasoning' not in analysis:
                analysis['reasoning'] = 'No reasoning provided'
            if 'parallel' not in analysis:
                analysis['parallel'] = False
            
            return analysis
            
        except Exception as e:
            self.logger.warning(f"Failed to parse analysis: {e}")
            raise
    
    def _fallback_analysis(self, task: str, available_agents: List[str]) -> Dict[str, Any]:
        """Provide a fallback analysis when LLM analysis fails."""
        # Simple keyword-based fallback
        task_lower = task.lower()
        selected_agents = []
        
        if any(word in task_lower for word in ['plan', 'design', 'structure', 'architecture']):
            if 'code_planner' in available_agents:
                selected_agents.append('code_planner')
        
        if any(word in task_lower for word in ['create', 'write', 'modify', 'edit', 'file']):
            if 'code_editor' in available_agents:
                selected_agents.append('code_editor')
        
        if any(word in task_lower for word in ['git', 'commit', 'push', 'version']):
            if 'git_agent' in available_agents:
                selected_agents.append('git_agent')
        
        if any(word in task_lower for word in ['web', 'fetch', 'url', 'download', 'scrape']):
            if 'web_data' in available_agents:
                selected_agents.append('web_data')
        
        # If no agents selected, default to code_planner
        if not selected_agents and 'code_planner' in available_agents:
            selected_agents = ['code_planner']
        
        return {
            'agents': selected_agents,
            'reasoning': 'Fallback analysis based on keywords',
            'parallel': False
        }


class Orchestrator:
    """
    Agent orchestrator that chains agents to accomplish tasks.
    
    Manages the execution of multiple agents in sequence, passing
    context and results between agents.
    """
    
    def __init__(
        self,
        agent_registry: "AgentRegistry",
        tool_registry: Optional["ToolRegistry"],
        llm_router: LLMRouter,
        config: AppConfig,
        memory_manager: Optional[MemoryManager] = None,
        plugin_loader: Optional["PluginLoader"] = None
    ):
        """
        Initialize the orchestrator.
        
        Args:
            agent_registry: Registry of available agents
            tool_registry: Registry of available tools
            llm_router: LLM router for agents to use
            config: Application configuration
            memory_manager: Optional memory manager for conversation history
            plugin_loader: Optional plugin loader for plugin hooks
        """
        self.agent_registry = agent_registry
        self.tool_registry = tool_registry
        self.llm_router = llm_router
        self.config = config
        self.memory_manager = memory_manager
        self.plugin_loader = plugin_loader
        self.logger = logging.getLogger(f"{__name__}.Orchestrator")
    
    def execute_task(
        self,
        task: str,
        agent_sequence: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a task using a sequence of agents.
        
        Args:
            task: Task description
            agent_sequence: List of agent names to execute in order
            context: Optional initial context
            
        Returns:
            Dictionary containing:
                - success: Overall success status
                - results: Results from each agent
                - final_result: Result from last agent
                - message: Status message
                - session_id: Memory session ID (if memory enabled)
        """
        context = context or {}
        context['auto_confirm'] = self.config.agents.auto_confirm
        
        # Create or get memory session
        session_id = context.get('session_id')
        if self.memory_manager:
            if not session_id:
                session_id = self.memory_manager.create_session()
                context['session_id'] = session_id
                self.logger.info(f"Created memory session: {session_id[:8]}")
            
            # Add user task to memory
            self.memory_manager.add_user_message(
                session_id=session_id,
                content=task,
                metadata={'agent_sequence': agent_sequence}
            )
        
        self.logger.info(f"Starting orchestration with {len(agent_sequence)} agents")
        _print_engine_status(f"Starting orchestration with {len(agent_sequence)} agent(s)", "info")
        
        results = []
        current_context = context.copy()
        
        try:
            # Use Rich Progress bar for agent execution
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=_console
            ) as progress:
                
                main_task = progress.add_task(
                    "[cyan]Executing agents...",
                    total=len(agent_sequence)
                )
                
                for i, agent_name in enumerate(agent_sequence):
                    self.logger.info(f"Executing agent {i+1}/{len(agent_sequence)}: {agent_name}")
                    
                    # Update progress description
                    progress.update(
                        main_task,
                        description=f"[cyan]Executing agent {i+1}/{len(agent_sequence)}: [bold magenta]{agent_name}[/bold magenta]"
                    )
                    
                    # Get or create agent
                    agent = self.agent_registry.get_or_create_agent(
                        name=agent_name,
                        llm_router=self.llm_router,
                        tool_registry=self.tool_registry,
                        config=self.config.agents.model_dump(),
                        memory_manager=self.memory_manager,
                        plugin_loader=self.plugin_loader
                    )
                    
                    # Execute agent
                    result = agent.execute(task, current_context)
                    results.append({
                        'agent': agent_name,
                        'result': result
                    })
                    
                    # Add agent result to memory
                    if self.memory_manager and session_id:
                        result_message = result.get('message', 'Task completed')
                        self.memory_manager.add_agent_message(
                            session_id=session_id,
                            content=result_message,
                            agent_name=agent_name,
                            metadata={
                                'success': result.get('success', False),
                                'data_summary': str(result.get('data', ''))[:200]  # Truncate for memory
                            }
                        )
                    
                    # Update progress
                    progress.update(main_task, advance=1)
                    
                    # Update context with results for next agent
                    if result.get('success'):
                        current_context[f'{agent_name}_result'] = result.get('result')
                        current_context['previous_agent'] = agent_name
                        _print_engine_status(f"Agent '{agent_name}' completed successfully", "success")
                    else:
                        self.logger.warning(f"Agent {agent_name} failed: {result.get('message')}")
                        _print_engine_status(f"Agent '{agent_name}' failed: {result.get('message')}", "warning")
                        # Continue anyway, but mark as failed
                        current_context[f'{agent_name}_failed'] = True
                    
                    # Check max iterations
                    if i >= self.config.agents.max_iterations:
                        self.logger.warning(f"Reached max iterations: {self.config.agents.max_iterations}")
                        _print_engine_status(f"Reached max iterations: {self.config.agents.max_iterations}", "warning")
                        break
            
            # Determine overall success
            overall_success = all(r['result'].get('success', False) for r in results)
            final_result = results[-1]['result'] if results else None
            
            # Display orchestration results table
            if results:
                _console.print()
                table = _create_orchestration_table(results)
                _console.print(table)
                _console.print()
            
            if overall_success:
                _print_engine_status(f"Orchestration complete: All {len(results)} agent(s) succeeded", "success")
            else:
                _print_engine_status(f"Orchestration complete: Some agents failed", "warning")
            
            result_dict = {
                'success': overall_success,
                'results': results,
                'final_result': final_result,
                'message': f"Orchestration complete: {len(results)} agents executed",
                'context': current_context
            }
            
            if session_id:
                result_dict['session_id'] = session_id
            
            return result_dict
            
        except Exception as e:
            self.logger.error(f"Orchestration failed: {e}")
            _print_engine_status(f"Orchestration failed: {str(e)}", "error")
            return {
                'success': False,
                'results': results,
                'final_result': None,
                'message': f"Orchestration failed: {str(e)}",
                'error': str(e)
            }


class Engine:
    """
    Main orchestration engine for AI agent operations.
    
    This engine serves as the central coordinator for:
    - Configuration management
    - LLM provider routing
    - Query processing and response handling
    
    In future phases, this will be extended to:
    - Manage multiple AI agents
    - Coordinate agent communication
    - Handle tool/MCP integration
    """
    
    def __init__(self, config: Optional[AppConfig] = None, config_path: Optional[Path] = None):
        """
        Initialize the engine.
        
        Args:
            config: Optional pre-loaded configuration
            config_path: Optional path to configuration file
        """
        self.config = config or AppConfig.load(config_path)
        self.router: Optional[LLMRouter] = None
        self.agent_registry: Optional["AgentRegistry"] = None
        self.tool_registry: Optional["ToolRegistry"] = None
        self.task_analyzer: Optional[TaskAnalyzer] = None
        self.orchestrator: Optional[Orchestrator] = None
        self.workflow_manager: Optional["WorkflowManager"] = None
        self.memory_manager: Optional[MemoryManager] = None
        self.project_manager: Optional[ProjectManager] = None
        self.chat_history_manager: Optional[ChatHistoryManager] = None
        self.plugin_loader: Optional["PluginLoader"] = None
        self._initialized = False
        
        # Setup logging based on configuration
        setup_logging(self.config)
        
        logger.info("Engine initialized")
        logger.debug(f"Configuration: {self.config.mask_sensitive_data()}")
    
    def initialize(self) -> None:
        """
        Initialize the engine components.
        
        This sets up the LLM router, agent registry, tool registry,
        task analyzer, and orchestrator.
        
        Raises:
            EngineError: If initialization fails
        """
        try:
            logger.info("Initializing engine components...")
            
            # Initialize LLM router
            self.router = LLMRouter(self.config)
            
            # Check for available providers
            available_providers = self.router.get_available_providers()
            if not available_providers:
                raise EngineError(
                    "No LLM providers are available. Please ensure at least one provider "
                    "(Ollama or OpenAI) is configured and running."
                )
            
            # Initialize tool registry
            if TOOLS_AVAILABLE:
                self.tool_registry = ToolRegistry()
                self._register_tools()
                logger.info(f"Tool registry initialized with {len(self.tool_registry)} tools")
            else:
                logger.warning("Tool system not available (import failed)")
            
            # Initialize agent registry
            if AGENTS_AVAILABLE:
                self.agent_registry = AgentRegistry()
                self._register_agents()
                logger.info(f"Agent registry initialized with {len(self.agent_registry)} agents")
            else:
                logger.warning("Agent system not available (import failed)")
            
            # Initialize project manager
            project_storage_path = Path("projects")
            self.project_manager = ProjectManager(
                storage_path=project_storage_path,
                auto_save=True,
                create_default_project=True
            )
            logger.info(f"Project manager initialized with {len(self.project_manager)} projects")
            
            # Initialize memory manager with project scoping
            memory_storage_path = Path("memory_storage")
            self.memory_manager = MemoryManager(
                storage_path=memory_storage_path,
                default_max_context_window=4096,
                auto_save=True,
                enable_summarization=True,
                llm_router=self.router,
                project_scoped=True
            )
            logger.info(f"Memory manager initialized with storage at: {memory_storage_path}")
            
            # Initialize chat history manager
            chat_history_path = Path("chat_history")
            self.chat_history_manager = ChatHistoryManager(
                storage_path=chat_history_path,
                llm_router=self.router,
                auto_save=True,
                enable_auto_summarization=True
            )
            logger.info(f"Chat history manager initialized with storage at: {chat_history_path}")
            
            # Link project manager with memory and chat history
            active_project = self.project_manager.get_active_project()
            if active_project:
                # Set memory context for active project
                self.memory_manager.switch_project_context(active_project.project_id)
                
                # Get or create memory session for the project
                memory_session_id = self.memory_manager.get_project_session_id(active_project.project_id)
                if not memory_session_id:
                    memory_session_id = self.memory_manager.create_project_session(active_project.project_id)
                
                # Update project with session ID
                self.project_manager.set_project_memory_session_id(
                    active_project.project_id,
                    memory_session_id
                )
                
                # Get or create chat history for the project
                chat_history = self.chat_history_manager.get_history_by_project(active_project.project_id)
                if not chat_history:
                    self.chat_history_manager.create_history(project_id=active_project.project_id)
                
                logger.info(f"Active project: {active_project.name} ({active_project.project_id[:8]})")
            
            # Initialize task analyzer
            self.task_analyzer = TaskAnalyzer(self.router)
            logger.info("Task analyzer initialized")
            
            # Initialize orchestrator
            if self.agent_registry:
                self.orchestrator = Orchestrator(
                    agent_registry=self.agent_registry,
                    tool_registry=self.tool_registry,
                    llm_router=self.router,
                    config=self.config,
                    memory_manager=self.memory_manager,
                    plugin_loader=None  # Will be set after plugin system initialization
                )
                logger.info("Orchestrator initialized")
            
            # Initialize workflow manager
            if WORKFLOWS_AVAILABLE and self.agent_registry:
                workflows_dir = Path(__file__).parent.parent / "orchestration" / "workflows" / "definitions"
                self.workflow_manager = WorkflowManager(
                    workflows_dir=workflows_dir,
                    agent_registry=self.agent_registry,
                    llm_router=self.router
                )
                logger.info(f"Workflow manager initialized with {len(self.workflow_manager.workflows)} workflows")
            else:
                if not WORKFLOWS_AVAILABLE:
                    logger.warning("Workflow system not available (import failed)")
            
            # Initialize plugin system (after all core systems are ready)
            if PLUGINS_AVAILABLE and self.agent_registry and self.tool_registry:
                plugins_dir = Path(__file__).parent.parent / "plugins"
                self.plugin_loader = PluginLoader(
                    config=self.config,
                    agent_registry=self.agent_registry,
                    tool_registry=self.tool_registry,
                    plugin_dir=plugins_dir
                )
                # Load all plugins
                self.plugin_loader.load_all_plugins()
                logger.info(f"Plugin system initialized with {len(self.plugin_loader.get_all_plugins())} plugins loaded")
                
                # Update orchestrator with plugin_loader
                if self.orchestrator:
                    self.orchestrator.plugin_loader = self.plugin_loader
                    logger.debug("Orchestrator updated with plugin_loader")
            else:
                if not PLUGINS_AVAILABLE:
                    logger.warning("Plugin system not available (import failed)")
                elif not (self.agent_registry and self.tool_registry):
                    logger.warning("Plugin system requires agent and tool registries to be available")
            
            logger.info(f"Engine initialized successfully with providers: {available_providers}")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize engine: {e}")
            raise EngineError(f"Engine initialization failed: {e}") from e
    
    def _register_tools(self) -> None:
        """Register enabled tools."""
        if not self.tool_registry:
            return
        
        enabled_tools = self.config.tools.enabled_tools
        tool_config = self.config.tools.model_dump()
        
        for tool_name in enabled_tools:
            try:
                if tool_name == 'web_fetch':
                    self.tool_registry.register(WebFetchTool(config=tool_config))
                elif tool_name == 'git':
                    self.tool_registry.register(GitTool(config=tool_config))
                elif tool_name == 'mcp':
                    self.tool_registry.register(MCPClientTool(config=tool_config))
                else:
                    logger.warning(f"Unknown tool: {tool_name}")
            except Exception as e:
                logger.error(f"Failed to register tool {tool_name}: {e}")
    
    def _register_agents(self) -> None:
        """Register enabled agents."""
        if not self.agent_registry:
            return
        
        enabled_agents = self.config.agents.enabled_agents
        
        agent_classes = {
            'code_planner': GenericCodePlanner,
            'code_editor': GenericCodeEditor,
            'git_agent': GitAgent,
            'web_data': WebDataAgent,
        }
        
        for agent_name in enabled_agents:
            try:
                agent_class = agent_classes.get(agent_name)
                if agent_class:
                    self.agent_registry.register(agent_class)
                else:
                    logger.warning(f"Unknown agent: {agent_name}")
            except Exception as e:
                logger.error(f"Failed to register agent {agent_name}: {e}")
    
    def process_query(
        self,
        query: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a user query through the LLM router.
        
        Args:
            query: The user's query/prompt
            model: Optional model name override
            provider: Optional provider override ("ollama" or "openai")
            **kwargs: Additional parameters for the LLM provider
            
        Returns:
            Dictionary containing:
                - response: The LLM response
                - provider: The provider that handled the query
                - model: The model used
                - success: Boolean indicating success
                - error: Error message if failed
                
        Raises:
            EngineError: If engine is not initialized
        """
        if not self._initialized:
            raise EngineError("Engine not initialized. Call initialize() first.")
        
        logger.info(f"Processing query (length: {len(query)})")
        logger.debug(f"Query parameters - model: {model}, provider: {provider}")
        
        try:
            # Route query through LLM router
            result = self.router.query(
                prompt=query,
                model=model,
                provider=provider,
                **kwargs
            )
            
            result['success'] = True
            result['error'] = None
            
            logger.info(
                f"Query processed successfully by {result['provider']} "
                f"using model {result['model']}"
            )
            
            return result
            
        except LLMProviderError as e:
            logger.error(f"Query processing failed: {e}")
            return {
                'response': None,
                'provider': None,
                'model': None,
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.exception("Unexpected error during query processing")
            return {
                'response': None,
                'provider': None,
                'model': None,
                'success': False,
                'error': f"Unexpected error: {e}"
            }
    
    def execute_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        agent_override: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a task using agent orchestration.
        
        This is the main method for task execution with automatic agent selection
        and orchestration.
        
        Args:
            task: Task description
            context: Optional context dictionary
            agent_override: Optional list of agents to use (skips task analysis)
            
        Returns:
            Dictionary containing:
                - success: Boolean indicating success
                - analysis: Task analysis results
                - orchestration: Orchestration results
                - message: Status message
                
        Raises:
            EngineError: If engine is not initialized or orchestration not available
        """
        if not self._initialized:
            raise EngineError("Engine not initialized. Call initialize() first.")
        
        if not self.orchestrator:
            raise EngineError("Orchestrator not available. Agent system may not be loaded.")
        
        logger.info(f"Executing task: {task[:100]}...")
        
        try:
            # Analyze task to determine agent sequence (unless overridden)
            if agent_override:
                analysis = {
                    'agents': agent_override,
                    'reasoning': 'User-specified agents',
                    'parallel': False
                }
            else:
                available_agents = self.agent_registry.list_agents()
                analysis = self.task_analyzer.analyze_task(task, available_agents)
            
            logger.info(f"Selected agents: {analysis['agents']}")
            logger.info(f"Reasoning: {analysis['reasoning']}")
            
            # Execute task with orchestrator
            orchestration_result = self.orchestrator.execute_task(
                task=task,
                agent_sequence=analysis['agents'],
                context=context
            )
            
            return {
                'success': orchestration_result['success'],
                'analysis': analysis,
                'orchestration': orchestration_result,
                'message': 'Task execution complete'
            }
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {
                'success': False,
                'analysis': None,
                'orchestration': None,
                'message': f"Task execution failed: {str(e)}",
                'error': str(e)
            }
    
    def run_interactive_loop(self) -> None:
        """
        Run an interactive query loop (for testing/development).
        
        This allows direct interaction with the engine for testing purposes.
        Uses Rich for beautiful formatted output.
        """
        if not self._initialized:
            self.initialize()
        
        # Display welcome panel
        welcome_panel = Panel(
            "[bold cyan]AI Agent Console - Interactive Mode[/bold cyan]\n\n"
            "[white]Type your queries below.[/white]\n"
            "[yellow]Commands:[/yellow] [bold]exit, quit, q[/bold] - Exit interactive mode\n"
            "[yellow]Commands:[/yellow] [bold]clear[/bold] - Clear screen",
            title="[bold magenta]🤖 Welcome",
            border_style="magenta",
            padding=(1, 2)
        )
        _console.print(welcome_panel)
        _console.print()
        
        while True:
            try:
                # Get user input using Rich prompt
                from rich.prompt import Prompt
                query = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
                
                if not query:
                    continue
                
                if query.lower() in ('exit', 'quit', 'q'):
                    _print_engine_status("Goodbye! 👋", "info")
                    break
                
                if query.lower() == 'clear':
                    _console.clear()
                    _console.print(welcome_panel)
                    _console.print()
                    continue
                
                # Process query with status spinner
                _console.print()
                with _console.status("[bold cyan]🤖 Processing query...", spinner="dots"):
                    result = self.process_query(query)
                
                _console.print()
                
                if result['success']:
                    # Show metadata
                    metadata = f"[dim]Provider: {result['provider']} | Model: {result['model']}[/dim]"
                    _console.print(metadata)
                    
                    # Show response in a panel
                    response_panel = Panel(
                        result['response'],
                        title="[bold green]🤖 Response",
                        border_style="green",
                        padding=(1, 2)
                    )
                    _console.print(response_panel)
                else:
                    _print_engine_status(f"Error: {result['error']}", "error")
                
                _console.print()
                    
            except KeyboardInterrupt:
                _console.print("\n")
                _print_engine_status("Interrupted. Goodbye! 👋", "info")
                break
            except Exception as e:
                logger.exception("Error in interactive loop")
                _console.print()
                _print_engine_status(f"Error: {e}", "error")
                _console.print()
    
    # ========================================================================
    # Project Management Methods
    # ========================================================================
    
    def switch_project(self, project_id: str) -> bool:
        """
        Switch to a different project.
        
        Args:
            project_id: Project ID to switch to
            
        Returns:
            True if switched successfully
        """
        if not self.project_manager:
            logger.error("Project manager not initialized")
            return False
        
        # Set as active project
        if not self.project_manager.set_active_project(project_id):
            return False
        
        # Switch memory context
        if self.memory_manager:
            self.memory_manager.switch_project_context(project_id)
            
            # Get or create memory session for the project
            memory_session_id = self.memory_manager.get_project_session_id(project_id)
            if not memory_session_id:
                memory_session_id = self.memory_manager.create_project_session(project_id)
            
            # Update project with session ID
            self.project_manager.set_project_memory_session_id(project_id, memory_session_id)
        
        # Ensure chat history exists for the project
        if self.chat_history_manager:
            chat_history = self.chat_history_manager.get_history_by_project(project_id)
            if not chat_history:
                self.chat_history_manager.create_history(project_id=project_id)
        
        logger.info(f"Switched to project: {project_id[:8]}")
        return True
    
    def get_current_project(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current active project.
        
        Returns:
            Dictionary with project info or None
        """
        if not self.project_manager:
            return None
        
        project = self.project_manager.get_active_project()
        if project:
            return project.to_dict()
        return None
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects.
        
        Returns:
            List of project dictionaries
        """
        if not self.project_manager:
            return []
        
        return self.project_manager.list_projects()
    
    def create_project(
        self,
        name: str,
        description: str = "",
        switch_to_new: bool = True
    ) -> Optional[str]:
        """
        Create a new project.
        
        Args:
            name: Project name
            description: Project description
            switch_to_new: Whether to switch to the new project
            
        Returns:
            Project ID or None if failed
        """
        if not self.project_manager:
            logger.error("Project manager not initialized")
            return None
        
        project_id = self.project_manager.create_project(name=name, description=description)
        
        if switch_to_new:
            self.switch_project(project_id)
        
        return project_id
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.
        
        Args:
            project_id: Project ID to delete
            
        Returns:
            True if deleted successfully
        """
        if not self.project_manager:
            return False
        
        # Delete associated memory and chat history
        if self.memory_manager:
            self.memory_manager.delete_project_memory(project_id)
        
        if self.chat_history_manager:
            history = self.chat_history_manager.get_history_by_project(project_id)
            if history:
                self.chat_history_manager.delete_history(history.history_id)
        
        # Delete the project
        return self.project_manager.delete_project(project_id)
    
    def get_chat_history(
        self,
        project_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get chat history for a project.
        
        Args:
            project_id: Project ID (uses active project if None)
            limit: Optional limit on number of messages
            
        Returns:
            List of message dictionaries
        """
        if not self.chat_history_manager:
            return []
        
        if project_id is None and self.project_manager:
            active_project = self.project_manager.get_active_project()
            if active_project:
                project_id = active_project.project_id
        
        if project_id is None:
            return []
        
        history = self.chat_history_manager.get_history_by_project(project_id)
        if history:
            return self.chat_history_manager.get_messages(history.history_id, limit=limit)
        
        return []
    
    def summarize_chat_history(self, project_id: Optional[str] = None) -> Optional[str]:
        """
        Summarize chat history for a project.
        
        Args:
            project_id: Project ID (uses active project if None)
            
        Returns:
            Summary text or None if failed
        """
        if not self.chat_history_manager:
            return None
        
        if project_id is None and self.project_manager:
            active_project = self.project_manager.get_active_project()
            if active_project:
                project_id = active_project.project_id
        
        if project_id is None:
            return None
        
        history = self.chat_history_manager.get_history_by_project(project_id)
        if history:
            return self.chat_history_manager.summarize_history(history.history_id)
        
        return None
    
    # ========================================================================
    # Shutdown and Status
    # ========================================================================
    
    def shutdown(self) -> None:
        """Clean up resources and shutdown the engine."""
        logger.info("Shutting down engine")
        
        # Save all data before shutdown
        if self.project_manager:
            self.project_manager.save_all_projects()
        
        if self.memory_manager:
            self.memory_manager.save_all_sessions()
        
        if self.chat_history_manager:
            self.chat_history_manager.save_all_histories()
        
        self._initialized = False
        self.router = None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get engine status information.
        
        Returns:
            Dictionary with engine status information
        """
        status = {
            'initialized': self._initialized,
            'available_providers': [],
            'config_loaded': self.config is not None,
            'agents_available': AGENTS_AVAILABLE,
            'tools_available': TOOLS_AVAILABLE,
            'registered_agents': [],
            'registered_tools': [],
        }
        
        if self.router:
            status['available_providers'] = self.router.get_available_providers()
        
        if self.agent_registry:
            status['registered_agents'] = self.agent_registry.list_agents()
        
        if self.tool_registry:
            status['registered_tools'] = self.tool_registry.list_tools()
        
        return status
