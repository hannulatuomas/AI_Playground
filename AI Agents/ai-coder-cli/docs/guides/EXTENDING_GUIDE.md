Here's the result of running `cat -n` on /home/ubuntu/ai-agent-console/docs/guides/EXTENDING_GUIDE.md:
     1	
     2	# AI Agent Console - Extending Guide
     3	
     4	**Version:** 2.4.1  
     5	**Last Updated:** October 13, 2025
     6	
     7	## Table of Contents
     8	
     9	1. [Quick Start](#quick-start)
    10	2. [New Architecture Overview](#new-architecture-overview)
    11	3. [Adding a New Agent](#adding-a-new-agent)
    12	4. [Adding Language Support](#adding-language-support)
    13	5. [Adding a New Tool](#adding-a-new-tool)
    14	6. [Agent-Tool Integration](#agent-tool-integration)
    15	7. [Plugin System](#plugin-system) ⭐ **NEW**
    16	8. [Configuration](#configuration)
    17	9. [Testing](#testing)
    18	10. [Best Practices](#best-practices)
    19	11. [Common Patterns](#common-patterns)
    20	12. [Troubleshooting](#troubleshooting)
    21	
    22	---
    23	
    24	## Quick Start
    25	
    26	### Prerequisites
    27	
    28	1. Python 3.10 or higher
    29	2. Development environment set up
    30	3. Familiarity with the codebase structure
    31	4. Understanding of abstract base classes
    32	
    33	### Development Workflow
    34	
    35	```bash
    36	# 1. Create your component
    37	# 2. Test it
    38	# 3. Register it
    39	# 4. Configure it
    40	# 5. Document it
    41	# 6. Commit it
    42	```
    43	
    44	---
    45	
    46	## New Architecture Overview
    47	
    48	### Refactored Agent Structure (v2.0)
    49	
    50	The agent system has been refactored to use an inheritance-based architecture with better organization:
    51	
    52	```
    53	agents/
    54	├── base/                           # Base classes for all agent types
    55	│   ├── __init__.py
    56	│   ├── agent_base.py              # Core Agent base class
    57	│   ├── code_editor_base.py        # Base for code editors
    58	│   ├── build_agent_base.py        # Base for build agents
    59	│   └── debug_agent_base.py        # Base for debug agents
    60	│
    61	├── generic/                        # Generic fallback agents
    62	│   ├── __init__.py
    63	│   ├── generic_code_editor.py     # Fallback code editor
    64	│   ├── generic_build_agent.py     # Fallback build agent
    65	│   └── generic_debug_agent.py     # Fallback debug agent
    66	│
    67	└── languages/                      # Language-specific implementations
    68	    ├── python/
    69	    │   ├── __init__.py
    70	    │   ├── code_editor.py         # PythonCodeEditorAgent
    71	    │   ├── build_agent.py         # PythonBuildAgent
    72	    │   └── debug_agent.py         # PythonDebugAgent
    73	    │
    74	    ├── csharp/
    75	    │   ├── __init__.py
    76	    │   ├── code_editor.py         # CSharpCodeEditorAgent
    77	    │   ├── build_agent.py         # CSharpBuildAgent
    78	    │   └── debug_agent.py         # CSharpDebugAgent
    79	    │
    80	    ├── cpp/                        # C++ agents
    81	    ├── web/                        # Web development agents
    82	    ├── bash/                       # Bash/shell agents
    83	    ├── powershell/                 # PowerShell agents
    84	    └── batch/                      # Batch script agents
    85	```
    86	
    87	### Key Benefits
    88	
    89	1. **Inheritance Hierarchy**: All language-specific agents inherit from base classes
    90	2. **Code Reuse**: Common functionality is in base classes
    91	3. **Extensibility**: Easy to add new languages by extending base classes
    92	4. **Fallback Support**: Generic agents handle unsupported languages
    93	5. **Better Organization**: Agents organized by language and type
    94	
    95	### Base Classes
    96	
    97	#### Agent (base/agent_base.py)
    98	Core base class for all agents with:
    99	- LLM integration
   100	- Memory management
   101	- Tool registry access
   102	- Standard result formatting
   103	
   104	#### CodeEditorBase (base/code_editor_base.py)
   105	Base class for code editors with:
   106	- File operations (create, modify, read)
   107	- Syntax validation (abstract)
   108	- Code formatting (abstract)
   109	- Code generation (abstract)
   110	
   111	#### BuildAgentBase (base/build_agent_base.py)
   112	Base class for build agents with:
   113	- Build system detection (abstract)
   114	- Dependency installation (abstract)
   115	- Package building (abstract)
   116	- Test execution
   117	- Build validation
   118	
   119	#### DebugAgentBase (base/debug_agent_base.py)
   120	Base class for debug agents with:
   121	- Breakpoint management
   122	- Stack trace analysis (abstract)
   123	- Variable inspection
   124	- Exception debugging
   125	- Debug session management
   126	
   127	---
   128	
   129	## Adding Language Support
   130	
   131	### Step 1: Create Language Directory
   132	
   133	Create a new directory for your language:
   134	
   135	```bash
   136	mkdir -p agents/languages/mylanguage
   137	touch agents/languages/mylanguage/__init__.py
   138	```
   139	
   140	### Step 2: Create Code Editor
   141	
   142	Create `agents/languages/mylanguage/code_editor.py`:
   143	
   144	```python
   145	"""
   146	MyLanguage-Specific Code Editor Agent
   147	"""
   148	
   149	from typing import Dict, Any
   150	from ...base import CodeEditorBase
   151	
   152	
   153	class MyLanguageCodeEditorAgent(CodeEditorBase):
   154	    """
   155	    Agent specialized for MyLanguage code editing.
   156	    """
   157	    
   158	    def __init__(
   159	        self,
   160	        name: str = "code_editor_mylanguage",
   161	        description: str = "MyLanguage-specific code editor",
   162	        **kwargs
   163	    ):
   164	        super().__init__(
   165	            name=name,
   166	            description=description,
   167	            supported_extensions=['.mylang', '.ml'],  # Your file extensions
   168	            **kwargs
   169	        )
   170	    
   171	    def _generate_code_content(
   172	        self,
   173	        operation: Dict[str, Any],
   174	        task: str,
   175	        context: Dict[str, Any]
   176	    ) -> str:
   177	        """Generate MyLanguage code using LLM."""
   178	        # Build a language-specific prompt
   179	        prompt = f"""Generate MyLanguage code for: {operation['path']}
   180	
   181	Task: {task}
   182	
   183	Requirements:
   184	- Follow MyLanguage best practices
   185	- Include proper documentation
   186	- Use idiomatic MyLanguage patterns
   187	
   188	Generate ONLY the code, no markdown."""
   189	
   190	        llm_result = self._get_llm_response(prompt, temperature=0.7)
   191	        content = llm_result.get('response', '')
   192	        return self._clean_code_blocks(content)
   193	    
   194	    def _validate_syntax(self, code: str) -> Dict[str, Any]:
   195	        """Validate MyLanguage syntax."""
   196	        try:
   197	            # Use your language's parser/validator
   198	            # Example: mylang_parser.parse(code)
   199	            return {'valid': True, 'error': None}
   200	        except Exception as e:
   201	            return {'valid': False, 'error': str(e)}
   202	    
   203	    def _apply_formatting(self, code: str) -> str:
   204	        """Apply MyLanguage formatting."""
   205	        # Use your language's formatter
   206	        # Example: return mylang_formatter.format(code)
   207	        
   208	        # Or apply basic formatting:
   209	        lines = [line.rstrip() for line in code.split('\n')]
   210	        result = '\n'.join(lines)
   211	        if result and not result.endswith('\n'):
   212	            result += '\n'
   213	        return result
   214	```
   215	
   216	### Step 3: Create Build Agent
   217	
   218	Create `agents/languages/mylanguage/build_agent.py`:
   219	
   220	```python
   221	"""
   222	MyLanguage Build Agent
   223	"""
   224	
   225	from typing import Dict, Any
   226	from pathlib import Path
   227	from ...base import BuildAgentBase
   228	
   229	
   230	class MyLanguageBuildAgent(BuildAgentBase):
   231	    """
   232	    Build agent for MyLanguage projects.
   233	    """
   234	    
   235	    def __init__(
   236	        self,
   237	        name: str = "build_mylanguage",
   238	        description: str = "MyLanguage build agent",
   239	        **kwargs
   240	    ):
   241	        super().__init__(
   242	            name=name,
   243	            description=description,
   244	            supported_build_systems=['mylang-build', 'make'],
   245	            **kwargs
   246	        )
   247	    
   248	    def _detect_build_system(self, project_dir: str) -> Dict[str, Any]:
   249	        """Detect MyLanguage build system."""
   250	        project_path = Path(project_dir)
   251	        
   252	        if (project_path / "mylang.build").exists():
   253	            self._build_system = 'mylang-build'
   254	            return self._build_success_result(
   255	                "Detected mylang-build",
   256	                data={'build_system': 'mylang-build'}
   257	            )
   258	        
   259	        return self._build_error_result("No build system detected")
   260	    
   261	    def _install_dependencies(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
   262	        """Install MyLanguage dependencies."""
   263	        detection = self._detect_build_system(project_dir)
   264	        if not detection['success']:
   265	            return detection
   266	        
   267	        cmd = ['mylang-build', 'deps']
   268	        
   269	        try:
   270	            result = self._run_command(cmd, project_dir)
   271	            if result.returncode == 0:
   272	                return self._build_success_result(
   273	                    "Dependencies installed",
   274	                    data={'output': result.stdout}
   275	                )
   276	            else:
   277	                return self._build_error_result(
   278	                    f"Installation failed: {result.stderr}"
   279	                )
   280	        except Exception as e:
   281	            return self._build_error_result(str(e), error=e)
   282	    
   283	    def _build_package(self, project_dir: str, context: Dict[str, Any]) -> Dict[str, Any]:
   284	        """Build MyLanguage package."""
   285	        cmd = ['mylang-build', 'build']
   286	        
   287	        try:
   288	            result = self._run_command(cmd, project_dir)
   289	            if result.returncode == 0:
   290	                return self._build_success_result(
   291	                    "Package built successfully",
   292	                    data={'output': result.stdout}
   293	                )
   294	            else:
   295	                return self._build_error_result(
   296	                    f"Build failed: {result.stderr}"
   297	                )
   298	        except Exception as e:
   299	            return self._build_error_result(str(e), error=e)
   300	```
   301	
   302	### Step 4: Create Debug Agent
   303	
   304	Create `agents/languages/mylanguage/debug_agent.py`:
   305	
   306	```python
   307	"""
   308	MyLanguage Debug Agent
   309	"""
   310	
   311	from typing import Dict, Any
   312	from ...base import DebugAgentBase
   313	
   314	
   315	class MyLanguageDebugAgent(DebugAgentBase):
   316	    """
   317	    Debug agent for MyLanguage.
   318	    """
   319	    
   320	    def __init__(
   321	        self,
   322	        name: str = "debug_mylanguage",
   323	        description: str = "MyLanguage debug agent",
   324	        **kwargs
   325	    ):
   326	        super().__init__(name=name, description=description, **kwargs)
   327	    
   328	    def _detect_debugger(self) -> str:
   329	        """Detect MyLanguage debugger."""
   330	        try:
   331	            import mylang_debugger
   332	            return 'mylang-debugger'
   333	        except ImportError:
   334	            return 'generic'
   335	    
   336	    def _set_breakpoint(self, context: Dict[str, Any]) -> Dict[str, Any]:
   337	        """Set breakpoint in MyLanguage code."""
   338	        file_path = context.get('file_path')
   339	        line_number = context.get('line_number')
   340	        
   341	        if not file_path or not line_number:
   342	            return self._build_error_result("file_path and line_number required")
   343	        
   344	        # Store breakpoint
   345	        if file_path not in self._breakpoints:
   346	            self._breakpoints[file_path] = []
   347	        
   348	        if line_number not in self._breakpoints[file_path]:
   349	            self._breakpoints[file_path].append(line_number)
   350	        
   351	        return self._build_success_result(
   352	            f"Breakpoint set at {file_path}:{line_number}",
   353	            data={'breakpoints': self._breakpoints}
   354	        )
   355	    
   356	    def _analyze_stack_trace(self, context: Dict[str, Any]) -> Dict[str, Any]:
   357	        """Analyze MyLanguage stack trace."""
   358	        stack_trace = context.get('stack_trace', '')
   359	        
   360	        if not stack_trace:
   361	            return self._build_error_result("stack_trace required")
   362	        
   363	        # Use LLM for analysis
   364	        prompt = f"""Analyze this MyLanguage stack trace:
   365	
   366	{stack_trace}
   367	
   368	Provide:
   369	1. Root cause
   370	2. Affected locations
   371	3. Recommended fixes
   372	
   373	Be specific."""
   374	        
   375	        try:
   376	            llm_result = self._get_llm_response(prompt)
   377	            analysis = llm_result.get('response', '')
   378	            
   379	            return self._build_success_result(
   380	                "Stack trace analyzed",
   381	                data={'analysis': analysis}
   382	            )
   383	        except Exception as e:
   384	            return self._build_error_result(str(e), error=e)
   385	```
   386	
   387	### Step 5: Update __init__.py
   388	
   389	Update `agents/languages/mylanguage/__init__.py`:
   390	
   391	```python
   392	"""
   393	MyLanguage language agents.
   394	"""
   395	
   396	from .code_editor import MyLanguageCodeEditorAgent
   397	from .build_agent import MyLanguageBuildAgent
   398	from .debug_agent import MyLanguageDebugAgent
   399	
   400	__all__ = [
   401	    'MyLanguageCodeEditorAgent',
   402	    'MyLanguageBuildAgent',
   403	    'MyLanguageDebugAgent',
   404	]
   405	```
   406	
   407	### Step 6: Register in Main __init__.py
   408	
   409	Update `agents/__init__.py` to include your new agents:
   410	
   411	```python
   412	# Add to imports section
   413	from .languages.mylanguage import (
   414	    MyLanguageCodeEditorAgent,
   415	    MyLanguageBuildAgent,
   416	    MyLanguageDebugAgent,
   417	)
   418	
   419	# Add to __all__ section
   420	__all__ = [
   421	    # ... existing entries ...
   422	    'MyLanguageCodeEditorAgent',
   423	    'MyLanguageBuildAgent',
   424	    'MyLanguageDebugAgent',
   425	]
   426	```
   427	
   428	### Step 7: Register with AgentRegistry
   429	
   430	The agents will be automatically available through imports. To explicitly register:
   431	
   432	```python
   433	from agents import AgentRegistry
   434	from agents.languages.mylanguage import MyLanguageCodeEditorAgent
   435	
   436	registry = AgentRegistry()
   437	registry.register(MyLanguageCodeEditorAgent, name="code_editor_mylanguage")
   438	```
   439	
   440	---
   441	
   442	## Adding a New Agent
   443	
   444	### Step 1: Create Agent File
   445	
   446	Create a new file in the `agents/` directory:
   447	
   448	```bash
   449	touch agents/my_custom_agent.py
   450	```
   451	
   452	### Step 2: Implement Agent Class
   453	
   454	```python
   455	"""
   456	My Custom Agent for specific task operations.
   457	
   458	This agent handles [describe what your agent does].
   459	"""
   460	
   461	import logging
   462	from typing import Dict, Any, Optional
   463	from agents.base import Agent
   464	
   465	
   466	class MyCustomAgent(Agent):
   467	    """
   468	    Agent for performing custom operations.
   469	    
   470	    This agent specializes in [specific domain]. It can:
   471	    - Feature 1
   472	    - Feature 2
   473	    - Feature 3
   474	    
   475	    Attributes:
   476	        name: Agent identifier
   477	        description: Human-readable description
   478	        llm_router: LLM router for AI queries
   479	        tool_registry: Registry of available tools
   480	        config: Configuration dictionary
   481	        memory_manager: Memory management system
   482	    """
   483	    
   484	    def __init__(
   485	        self,
   486	        name: str = "my_custom",
   487	        description: str = "Performs custom operations",
   488	        llm_router: Optional[Any] = None,
   489	        tool_registry: Optional[Any] = None,
   490	        config: Optional[Dict[str, Any]] = None,
   491	        memory_manager: Optional[Any] = None
   492	    ):
   493	        """
   494	        Initialize the custom agent.
   495	        
   496	        Args:
   497	            name: Agent name
   498	            description: Agent description
   499	            llm_router: LLM router instance
   500	            tool_registry: Tool registry instance
   501	            config: Configuration dictionary
   502	            memory_manager: Memory manager instance
   503	        """
   504	        super().__init__(
   505	            name=name,
   506	            description=description,
   507	            llm_router=llm_router,
   508	            tool_registry=tool_registry,
   509	            config=config,
   510	            memory_manager=memory_manager
   511	        )
   512	        
   513	        # Agent-specific initialization
   514	        self.custom_setting = config.get('custom_setting', 'default') if config else 'default'
   515	        self.logger.info(f"MyCustomAgent initialized with setting: {self.custom_setting}")
   516	    
   517	    @property
   518	    def capabilities(self) -> list[str]:
   519	        """
   520	        List agent capabilities.
   521	        
   522	        Returns:
   523	            List of capability strings
   524	        """
   525	        return [
   526	            "capability_1",
   527	            "capability_2",
   528	            "capability_3"
   529	        ]
   530	    
   531	    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
   532	        """
   533	        Execute the custom task.
   534	        
   535	        Args:
   536	            task: Task description
   537	            context: Execution context containing:
   538	                - session_id: Memory session ID (optional)
   539	                - previous_results: Results from previous agents
   540	                - user_preferences: User settings
   541	                
   542	        Returns:
   543	            Dictionary containing:
   544	                - success: bool - Whether execution succeeded
   545	                - message: str - Status message
   546	                - data: Any - Result data
   547	                - next_context: dict - Context for next agent
   548	                
   549	        Raises:
   550	            ValueError: If task parameters are invalid
   551	            RuntimeError: If execution fails critically
   552	        """
   553	        self._log_action("Starting custom task", task[:100])
   554	        
   555	        # Get memory context if available
   556	        session_id = context.get('session_id')
   557	        memory_context = []
   558	        if session_id and self.memory_manager:
   559	            memory_context = self._get_memory_context(session_id, max_messages=5)
   560	        
   561	        try:
   562	            # Validate input
   563	            if not task or not task.strip():
   564	                raise ValueError("Task cannot be empty")
   565	            
   566	            # Use LLM for intelligent processing
   567	            result = self._process_with_llm(task, context, memory_context)
   568	            
   569	            # Or use tools for concrete operations
   570	            # result = self._process_with_tools(task, context)
   571	            
   572	            # Add to memory if available
   573	            if session_id and self.memory_manager:
   574	                self._add_to_memory(
   575	                    session_id=session_id,
   576	                    message=f"Task completed: {result.get('summary', 'Success')}",
   577	                    metadata={
   578	                        'operation': 'custom_operation',
   579	                        'success': True
   580	                    }
   581	                )
   582	            
   583	            return self._build_success_result(
   584	                message="Custom task completed successfully",
   585	                data=result,
   586	                next_context={
   587	                    'custom_agent_result': result,
   588	                    'operation_type': 'custom'
   589	                }
   590	            )
   591	            
   592	        except ValueError as e:
   593	            self.logger.error(f"Validation error: {e}")
   594	            return self._build_error_result(f"Invalid task: {e}", e)
   595	            
   596	        except Exception as e:
   597	            self.logger.error(f"Execution failed: {e}", exc_info=True)
   598	            return self._build_error_result(f"Execution failed: {e}", e)
   599	    
   600	    def _process_with_llm(
   601	        self,
   602	        task: str,
   603	        context: Dict[str, Any],
   604	        memory_context: list
   605	    ) -> Dict[str, Any]:
   606	        """
   607	        Process task using LLM.
   608	        
   609	        Args:
   610	            task: Task description
   611	            context: Execution context
   612	            memory_context: Previous conversation history
   613	            
   614	        Returns:
   615	            Processing result dictionary
   616	            
   617	        Raises:
   618	            RuntimeError: If LLM query fails
   619	        """
   620	        # Format memory context for prompt
   621	        context_str = self._format_memory_context_for_prompt(memory_context)
   622	        
   623	        # Build prompt
   624	        prompt = f"""
   625	{context_str}
   626	
   627	You are a custom agent specialized in [domain].
   628	
   629	Task: {task}
   630	
   631	Context:
   632	{self._format_context(context)}
   633	
   634	Please perform the task and provide:
   635	1. Analysis of the task
   636	2. Step-by-step approach
   637	3. Final result
   638	
   639	Respond in JSON format:
   640	{{
   641	    "analysis": "...",
   642	    "steps": ["step1", "step2", ...],
   643	    "result": "...",
   644	    "summary": "..."
   645	}}
   646	"""
   647	        
   648	        # Query LLM (uses assigned model from config)
   649	        llm_result = self._get_llm_response(
   650	            prompt=prompt,
   651	            temperature=0.7  # Or use assigned temperature
   652	        )
   653	        
   654	        # Parse LLM response
   655	        try:
   656	            import json
   657	            response_text = llm_result.get('response', '{}')
   658	            result = json.loads(response_text)
   659	            return result
   660	        except json.JSONDecodeError:
   661	            # Fallback if JSON parsing fails
   662	            return {
   663	                'analysis': response_text,
   664	                'result': response_text,
   665	                'summary': 'Task processed'
   666	            }
   667	    
   668	    def _process_with_tools(
   669	        self,
   670	        task: str,
   671	        context: Dict[str, Any]
   672	    ) -> Dict[str, Any]:
   673	        """
   674	        Process task using tools.
   675	        
   676	        Args:
   677	            task: Task description
   678	            context: Execution context
   679	            
   680	        Returns:
   681	            Processing result dictionary
   682	            
   683	        Raises:
   684	            RuntimeError: If tool invocation fails
   685	        """
   686	        # Get required tool
   687	        file_tool = self._get_tool('filesystem')
   688	        if not file_tool:
   689	            raise RuntimeError("Filesystem tool not available")
   690	        
   691	        # Use tool
   692	        try:
   693	            result = file_tool.invoke({
   694	                'action': 'read',
   695	                'path': context.get('file_path', 'default.txt')
   696	            })
   697	            
   698	            return {
   699	                'content': result,
   700	                'summary': 'File read successfully'
   701	            }
   702	            
   703	        except Exception as e:
   704	            raise RuntimeError(f"Tool operation failed: {e}")
   705	    
   706	    def _format_context(self, context: Dict[str, Any]) -> str:
   707	        """
   708	        Format context for display in prompts.
   709	        
   710	        Args:
   711	            context: Context dictionary
   712	            
   713	        Returns:
   714	            Formatted context string
   715	        """
   716	        lines = []
   717	        for key, value in context.items():
   718	            if key not in ['session_id', 'next_context']:
   719	                lines.append(f"- {key}: {value}")
   720	        return "\n".join(lines) if lines else "No additional context"
   721	    
   722	    def __repr__(self) -> str:
   723	        """String representation of the agent."""
   724	        return f"<MyCustomAgent(name='{self.name}')>"
   725	```
   726	
   727	### Step 3: Register Agent
   728	
   729	Add your agent to `agents/__init__.py`:
   730	
   731	```python
   732	# Import your agent
   733	from agents.my_custom_agent import MyCustomAgent
   734	
   735	# Add to __all__ export
   736	__all__ = [
   737	    'Agent',
   738	    'AgentRegistry',
   739	    # ... existing agents ...
   740	    'MyCustomAgent',  # Add your agent here
   741	]
   742	```
   743	
   744	### Step 4: Register in Engine
   745	
   746	Add your agent to `core/engine.py` in the `_register_agents()` method:
   747	
   748	```python
   749	def _register_agents(self) -> None:
   750	    """Register all available agents."""
   751	    if not AGENTS_AVAILABLE:
   752	        return
   753	    
   754	    # ... existing imports ...
   755	    from agents.my_custom_agent import MyCustomAgent
   756	    
   757	    # Agent configuration
   758	    agent_classes = {
   759	        # ... existing agents ...
   760	        'my_custom': MyCustomAgent,
   761	    }
   762	    
   763	    # ... rest of registration logic ...
   764	```
   765	
   766	### Step 5: Add Configuration
   767	
   768	Add your agent to `config.yaml`:
   769	
   770	```yaml
   771	agents:
   772	  enabled_agents:
   773	    - "code_planner"
   774	    - "code_editor"
   775	    # ... existing agents ...
   776	    - "my_custom"  # Add your agent here
   777	  
   778	  model_assignments:
   779	    # ... existing assignments ...
   780	    my_custom:
   781	      primary: "llama3.3:latest"    # Choose appropriate model
   782	      fallback: "qwen2.5-coder:7b"  # Fallback model
   783	      temperature: 0.7               # Generation temperature
   784	```
   785	
   786	### Step 6: Test Your Agent
   787	
   788	Create a test file `test_my_custom_agent.py`:
   789	
   790	```python
   791	import pytest
   792	from agents.my_custom_agent import MyCustomAgent
   793	
   794	
   795	def test_agent_initialization():
   796	    """Test agent can be initialized."""
   797	    agent = MyCustomAgent()
   798	    assert agent.name == "my_custom"
   799	    assert agent.description is not None
   800	
   801	
   802	def test_agent_execute():
   803	    """Test agent execution."""
   804	    agent = MyCustomAgent()
   805	    
   806	    result = agent.execute(
   807	        task="Test task",
   808	        context={}
   809	    )
   810	    
   811	    assert 'success' in result
   812	    assert 'message' in result
   813	    assert 'data' in result
   814	
   815	
   816	def test_agent_with_llm():
   817	    """Test agent with mock LLM."""
   818	    from unittest.mock import Mock
   819	    
   820	    llm_router = Mock()
   821	    llm_router.query.return_value = {
   822	        'response': '{"result": "test"}',
   823	        'model': 'test_model',
   824	        'provider': 'test'
   825	    }
   826	    
   827	    agent = MyCustomAgent(llm_router=llm_router)
   828	    result = agent.execute("Test task", {})
   829	    
   830	    assert result['success'] == True
   831	
   832	
   833	def test_agent_error_handling():
   834	    """Test agent error handling."""
   835	    agent = MyCustomAgent()
   836	    
   837	    # Test with invalid input
   838	    result = agent.execute("", {})
   839	    
   840	    assert result['success'] == False
   841	    assert 'error' in result or 'Invalid' in result['message']
   842	
   843	
   844	if __name__ == '__main__':
   845	    pytest.main([__file__, '-v'])
   846	```
   847	
   848	Run tests:
   849	
   850	```bash
   851	pytest test_my_custom_agent.py -v
   852	```
   853	
   854	### Step 7: Document Your Agent
   855	
   856	Add documentation to `AGENT_INVENTORY.md`:
   857	
   858	```markdown
   859	| Agent Name | File | Purpose |
   860	|------------|------|---------|
   861	| **MyCustomAgent** | `my_custom_agent.py` | Performs custom operations |
   862	```
   863	
   864	---
   865	
   866	## Adding a New Tool
   867	
   868	### Step 1: Create Tool File
   869	
   870	Create a new file in the `tools/` directory:
   871	
   872	```bash
   873	touch tools/my_custom_tool.py
   874	```
   875	
   876	### Step 2: Implement Tool Class
   877	
   878	```python
   879	"""
   880	My Custom Tool for specific operations.
   881	
   882	This tool provides functionality for [describe what your tool does].
   883	"""
   884	
   885	import logging
   886	from typing import Dict, Any, Optional
   887	from tools.base import Tool
   888	
   889	
   890	class MyCustomTool(Tool):
   891	    """
   892	    Tool for performing custom operations.
   893	    
   894	    This tool provides:
   895	    - Operation 1
   896	    - Operation 2
   897	    - Operation 3
   898	    
   899	    Actions:
   900	        - 'operation1': Perform operation 1
   901	        - 'operation2': Perform operation 2
   902	        - 'operation3': Perform operation 3
   903	    
   904	    Parameters:
   905	        - action (str): Action to perform (required)
   906	        - param1 (str): Parameter 1 (required for some actions)
   907	        - param2 (int): Parameter 2 (optional)
   908	    
   909	    Example:
   910	        >>> tool = MyCustomTool()
   911	        >>> result = tool.invoke({
   912	        ...     'action': 'operation1',
   913	        ...     'param1': 'value'
   914	        ... })
   915	    """
   916	    
   917	    def __init__(self, config: Optional[Dict[str, Any]] = None):
   918	        """
   919	        Initialize the custom tool.
   920	        
   921	        Args:
   922	            config: Configuration dictionary containing:
   923	                - custom_setting: Custom setting value
   924	                - timeout: Operation timeout in seconds
   925	        """
   926	        super().__init__(
   927	            name='my_custom_tool',
   928	            description='Performs custom operations',
   929	            config=config
   930	        )
   931	        
   932	        # Tool-specific initialization
   933	        self.timeout = config.get('timeout', 30) if config else 30
   934	        self.custom_setting = config.get('custom_setting', 'default') if config else 'default'
   935	        
   936	        self.logger.info(f"MyCustomTool initialized with timeout={self.timeout}")
   937	    
   938	    @property
   939	    def supported_actions(self) -> list[str]:
   940	        """
   941	        List of supported actions.
   942	        
   943	        Returns:
   944	            List of action strings
   945	        """
   946	        return ['operation1', 'operation2', 'operation3']
   947	    
   948	    def invoke(self, params: Dict[str, Any]) -> Any:
   949	        """
   950	        Invoke the tool with given parameters.
   951	        
   952	        Args:
   953	            params: Parameters dictionary containing:
   954	                - action: Action to perform (required)
   955	                - param1: First parameter (varies by action)
   956	                - param2: Second parameter (varies by action)
   957	                
   958	        Returns:
   959	            Result of the operation (type varies by action)
   960	            
   961	        Raises:
   962	            ValueError: If required parameters are missing or invalid
   963	            RuntimeError: If operation fails
   964	        """
   965	        self._log_invocation(params)
   966	        
   967	        # Validate required parameters
   968	        self.validate_params(params, ['action'])
   969	        
   970	        action = params['action']
   971	        
   972	        # Validate action
   973	        if action not in self.supported_actions:
   974	            raise ValueError(
   975	                f"Unsupported action: {action}. "
   976	                f"Supported actions: {', '.join(self.supported_actions)}"
   977	            )
   978	        
   979	        # Dispatch to appropriate method
   980	        if action == 'operation1':
   981	            return self._operation1(params)
   982	        elif action == 'operation2':
   983	            return self._operation2(params)
   984	        elif action == 'operation3':
   985	            return self._operation3(params)
   986	    
   987	    def _operation1(self, params: Dict[str, Any]) -> Dict[str, Any]:
   988	        """
   989	        Perform operation 1.
   990	        
   991	        Args:
   992	            params: Parameters containing:
   993	                - param1: Required parameter
   994	                
   995	        Returns:
   996	            Operation result dictionary
   997	            
   998	        Raises:
   999	            ValueError: If param1 is invalid
  1000	            RuntimeError: If operation fails
  1001	        """
  1002	        # Validate parameters
  1003	        self.validate_params(params, ['param1'])
  1004	        param1 = params['param1']
  1005	        
  1006	        self.logger.info(f"Performing operation1 with param1={param1}")
  1007	        
  1008	        try:
  1009	            # Perform operation
  1010	            result = self._do_operation1(param1)
  1011	            
  1012	            return {
  1013	                'success': True,
  1014	                'result': result,
  1015	                'message': 'Operation 1 completed'
  1016	            }
  1017	            
  1018	        except Exception as e:
  1019	            self.logger.error(f"Operation 1 failed: {e}")
  1020	            raise RuntimeError(f"Operation 1 failed: {e}")
  1021	    
  1022	    def _operation2(self, params: Dict[str, Any]) -> Dict[str, Any]:
  1023	        """
  1024	        Perform operation 2.
  1025	        
  1026	        Args:
  1027	            params: Parameters containing:
  1028	                - param2: Optional parameter (default: 10)
  1029	                
  1030	        Returns:
  1031	            Operation result dictionary
  1032	        """
  1033	        param2 = params.get('param2', 10)
  1034	        
  1035	        self.logger.info(f"Performing operation2 with param2={param2}")
  1036	        
  1037	        try:
  1038	            result = self._do_operation2(param2)
  1039	            
  1040	            return {
  1041	                'success': True,
  1042	                'result': result,
  1043	                'message': 'Operation 2 completed'
  1044	            }
  1045	            
  1046	        except Exception as e:
  1047	            self.logger.error(f"Operation 2 failed: {e}")
  1048	            raise RuntimeError(f"Operation 2 failed: {e}")
  1049	    
  1050	    def _operation3(self, params: Dict[str, Any]) -> str:
  1051	        """
  1052	        Perform operation 3.
  1053	        
  1054	        Args:
  1055	            params: Parameters (no additional params needed)
  1056	                
  1057	        Returns:
  1058	            Operation result string
  1059	        """
  1060	        self.logger.info("Performing operation3")
  1061	        
  1062	        try:
  1063	            result = self._do_operation3()
  1064	            return result
  1065	            
  1066	        except Exception as e:
  1067	            self.logger.error(f"Operation 3 failed: {e}")
  1068	            raise RuntimeError(f"Operation 3 failed: {e}")
  1069	    
  1070	    def _do_operation1(self, param: str) -> str:
  1071	        """
  1072	        Core logic for operation 1.
  1073	        
  1074	        Args:
  1075	            param: Parameter value
  1076	            
  1077	        Returns:
  1078	            Operation result
  1079	        """
  1080	        # Implement your operation logic here
  1081	        return f"Processed: {param}"
  1082	    
  1083	    def _do_operation2(self, param: int) -> int:
  1084	        """
  1085	        Core logic for operation 2.
  1086	        
  1087	        Args:
  1088	            param: Parameter value
  1089	            
  1090	        Returns:
  1091	            Operation result
  1092	        """
  1093	        # Implement your operation logic here
  1094	        return param * 2
  1095	    
  1096	    def _do_operation3(self) -> str:
  1097	        """
  1098	        Core logic for operation 3.
  1099	        
  1100	        Returns:
  1101	            Operation result
  1102	        """
  1103	        # Implement your operation logic here
  1104	        return "Operation 3 result"
  1105	    
  1106	    def __repr__(self) -> str:
  1107	        """String representation of the tool."""
  1108	        return f"<MyCustomTool(timeout={self.timeout})>"
  1109	```
  1110	
  1111	### Step 3: Register Tool
  1112	
  1113	Add your tool to `tools/__init__.py`:
  1114	
  1115	```python
  1116	# Import your tool
  1117	from tools.my_custom_tool import MyCustomTool
  1118	
  1119	# Add to __all__ export
  1120	__all__ = [
  1121	    'Tool',
  1122	    'ToolRegistry',
  1123	    # ... existing tools ...
  1124	    'MyCustomTool',  # Add your tool here
  1125	]
  1126	```
  1127	
  1128	### Step 4: Register in Engine
  1129	
  1130	Add your tool to `core/engine.py` in the `_register_tools()` method:
  1131	
  1132	```python
  1133	def _register_tools(self) -> None:
  1134	    """Register all available tools."""
  1135	    if not TOOLS_AVAILABLE:
  1136	        return
  1137	    
  1138	    # ... existing imports ...
  1139	    from tools.my_custom_tool import MyCustomTool
  1140	    
  1141	    # Tool registration
  1142	    tool_configs = {
  1143	        # ... existing tools ...
  1144	        'my_custom_tool': {
  1145	            'custom_setting': self.config.tools.get('custom_setting', 'default'),
  1146	            'timeout': self.config.tools.get('custom_timeout', 30)
  1147	        }
  1148	    }
  1149	    
  1150	    for tool_name in self.config.tools.enabled_tools:
  1151	        if tool_name == 'my_custom_tool':
  1152	            self.tool_registry.register(
  1153	                MyCustomTool(config=tool_configs['my_custom_tool'])
  1154	            )
  1155	        # ... existing tool registrations ...
  1156	```
  1157	
  1158	### Step 5: Add Configuration
  1159	
  1160	Add your tool to `config.yaml`:
  1161	
  1162	```yaml
  1163	tools:
  1164	  enabled_tools:
  1165	    - "web_fetch"
  1166	    - "git"
  1167	    # ... existing tools ...
  1168	    - "my_custom_tool"  # Add your tool here
  1169	  
  1170	  # Tool-specific settings
  1171	  custom_setting: "production"
  1172	  custom_timeout: 60
  1173	```
  1174	
  1175	### Step 6: Test Your Tool
  1176	
  1177	Create a test file `test_my_custom_tool.py`:
  1178	
  1179	```python
  1180	import pytest
  1181	from tools.my_custom_tool import MyCustomTool
  1182	
  1183	
  1184	def test_tool_initialization():
  1185	    """Test tool can be initialized."""
  1186	    tool = MyCustomTool()
  1187	    assert tool.name == 'my_custom_tool'
  1188	    assert tool.timeout == 30
  1189	
  1190	
  1191	def test_tool_operation1():
  1192	    """Test operation 1."""
  1193	    tool = MyCustomTool()
  1194	    
  1195	    result = tool.invoke({
  1196	        'action': 'operation1',
  1197	        'param1': 'test'
  1198	    })
  1199	    
  1200	    assert result['success'] == True
  1201	    assert 'result' in result
  1202	
  1203	
  1204	def test_tool_operation2():
  1205	    """Test operation 2."""
  1206	    tool = MyCustomTool()
  1207	    
  1208	    result = tool.invoke({
  1209	        'action': 'operation2',
  1210	        'param2': 5
  1211	    })
  1212	    
  1213	    assert result['success'] == True
  1214	    assert result['result'] == 10  # 5 * 2
  1215	
  1216	
  1217	def test_tool_invalid_action():
  1218	    """Test invalid action handling."""
  1219	    tool = MyCustomTool()
  1220	    
  1221	    with pytest.raises(ValueError, match="Unsupported action"):
  1222	        tool.invoke({'action': 'invalid'})
  1223	
  1224	
  1225	def test_tool_missing_params():
  1226	    """Test missing parameter handling."""
  1227	    tool = MyCustomTool()
  1228	    
  1229	    with pytest.raises(ValueError, match="missing required parameters"):
  1230	        tool.invoke({'action': 'operation1'})  # Missing param1
  1231	
  1232	
  1233	if __name__ == '__main__':
  1234	    pytest.main([__file__, '-v'])
  1235	```
  1236	
  1237	---
  1238	
  1239	## Agent-Tool Integration
  1240	
  1241	### Using Tools in Agents
  1242	
  1243	Example of an agent using multiple tools:
  1244	
  1245	```python
  1246	class MyIntegratedAgent(Agent):
  1247	    """Agent that uses multiple tools."""
  1248	    
  1249	    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
  1250	        """Execute task using multiple tools."""
  1251	        
  1252	        # Get tools
  1253	        file_tool = self._get_tool('filesystem')
  1254	        web_tool = self._get_tool('web_fetch')
  1255	        custom_tool = self._get_tool('my_custom_tool')
  1256	        
  1257	        if not all([file_tool, web_tool, custom_tool]):
  1258	            return self._build_error_result("Required tools not available")
  1259	        
  1260	        try:
  1261	            # Use web tool to fetch data
  1262	            web_result = web_tool.invoke({
  1263	                'action': 'fetch',
  1264	                'url': 'https://example.com/data'
  1265	            })
  1266	            
  1267	            # Process data with custom tool
  1268	            processed = custom_tool.invoke({
  1269	                'action': 'operation1',
  1270	                'param1': web_result['content']
  1271	            })
  1272	            
  1273	            # Save result with file tool
  1274	            file_tool.invoke({
  1275	                'action': 'write',
  1276	                'path': 'result.txt',
  1277	                'content': processed['result']
  1278	            })
  1279	            
  1280	            return self._build_success_result(
  1281	                message="Task completed with multiple tools",
  1282	                data={'file': 'result.txt', 'content': processed['result']}
  1283	            )
  1284	            
  1285	        except Exception as e:
  1286	            return self._build_error_result(f"Tool integration failed: {e}", e)
  1287	```
  1288	
  1289	---
---

## Plugin System

**New in v2.4.0** ⭐

The plugin system allows you to extend the AI Agent Console without modifying core code. Plugins can add custom agents, tools, and hooks.

### Why Use Plugins?

- **Extensibility**: Add features without touching core code
- **Modularity**: Keep custom code separate and organized
- **Reusability**: Share plugins across projects or with community
- **Isolation**: Plugin failures don't affect core system
- **Easy Distribution**: Package and distribute custom functionality

### Plugin Architecture

```
plugins/
├── your_plugin/
│   ├── plugin.py           # Plugin class (required)
│   ├── agents/             # Custom agents (optional)
│   │   └── custom_agent.py
│   ├── tools/              # Custom tools (optional)
│   │   └── custom_tool.py
│   ├── README.md           # Documentation
│   └── requirements.txt    # Dependencies
```

### Creating a Plugin

#### Step 1: Create Plugin Directory

```bash
mkdir -p plugins/my_plugin
cd plugins/my_plugin
```

#### Step 2: Create plugin.py

```python
"""
My Custom Plugin

Description of what your plugin does.
"""

from core.plugin_base import Plugin, PluginMetadata
from agents.base.agent_base import Agent

# Import your custom components
from .agents.custom_agent import CustomAgent
from .tools.custom_tool import CustomTool


class MyPlugin(Plugin):
    """My custom plugin."""
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            author="Your Name",
            description="Custom plugin for specialized tasks",
            homepage="https://github.com/yourusername/my-plugin",
            dependencies=[],  # Other required plugins
            min_console_version="2.4.0"
        )
    
    def initialize(self) -> None:
        """Initialize plugin and register components."""
        # Register custom agent
        self.register_agent("CustomAgent", CustomAgent)
        
        # Register custom tool
        self.register_tool("CustomTool", CustomTool)
        
        # Set up hooks
        self.hooks.on_load = self.on_plugin_load
        self.hooks.on_agent_execute_before = self.before_agent_execute
    
    def on_plugin_load(self) -> None:
        """Called when plugin is loaded."""
        print(f"Plugin {self.get_metadata().name} loaded!")
    
    def before_agent_execute(self, agent, task, context):
        """Called before any agent executes."""
        # Add custom logic here
        pass
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass
```

#### Step 3: Create Custom Agent

```python
# agents/custom_agent.py

from agents.base.agent_base import Agent
from typing import Dict, Any


class CustomAgent(Agent):
    """Custom agent for specialized tasks."""
    
    def __init__(self, llm_router, tool_registry, config):
        super().__init__(llm_router, tool_registry, config)
        self.name = "CustomAgent"
        self.description = "Performs specialized tasks"
        self.capabilities = ["capability1", "capability2"]
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task."""
        try:
            # Your agent logic here
            prompt = f"Task: {task}\nContext: {context}"
            
            # Use LLM
            response = self.llm_router.query(
                prompt,
                model=self.config.get("model", "llama3.3:latest")
            )
            
            # Use tools if needed
            # tool = self.tool_registry.get_tool("FileOperations")
            # result = tool.execute(...)
            
            return {
                "success": True,
                "message": "Task completed",
                "data": {"response": response}
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

#### Step 4: Create Custom Tool

```python
# tools/custom_tool.py

from tools.base import Tool
from typing import Any, Dict


class CustomTool(Tool):
    """Custom tool for specific operations."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "CustomTool"
        self.description = "Performs specific operations"
    
    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Execute the tool."""
        try:
            # Your tool logic here
            if operation == "example_op":
                return {
                    "success": True,
                    "result": "Operation completed",
                    "data": kwargs
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

#### Step 5: Configure Plugin

Edit `config.yaml`:

```yaml
plugins:
  enabled: true
  auto_discover: true
  
  # Explicitly enable your plugin
  enabled_plugins:
    - my_plugin
  
  # Plugin-specific configuration
  my_plugin:
    api_key: "your_api_key_here"
    endpoint: "https://api.example.com"
    debug: true
```

#### Step 6: Load and Use Plugin

```python
from core.engine import Engine
from core.config import Config

# Initialize engine (plugins auto-load)
config = Config()
engine = Engine(config)

# Use your custom agent
result = engine.execute_task(
    "Use my custom agent for this task",
    context={"agent_type": "CustomAgent"}
)

print(result)
```

### Plugin Hooks

Plugins can hook into system events:

#### Available Hooks

```python
def on_load(self) -> None:
    """Called when plugin is loaded."""
    pass

def on_unload(self) -> None:
    """Called when plugin is unloaded."""
    pass

def on_agent_execute_before(self, agent, task, context) -> None:
    """Called before any agent executes."""
    pass

def on_agent_execute_after(self, agent, task, context, result) -> None:
    """Called after any agent executes."""
    pass

def on_tool_execute_before(self, tool, *args, **kwargs) -> None:
    """Called before any tool executes."""
    pass

def on_tool_execute_after(self, tool, result, *args, **kwargs) -> None:
    """Called after any tool executes."""
    pass

def on_memory_store(self, memory_type, content) -> None:
    """Called when memory is stored."""
    pass

def on_memory_retrieve(self, query, results) -> None:
    """Called when memory is retrieved."""
    pass
```

#### Using Hooks

```python
class MyPlugin(Plugin):
    def initialize(self):
        # Register hook methods
        self.hooks.on_agent_execute_before = self.log_agent_execution
        self.hooks.on_memory_store = self.audit_memory_storage
    
    def log_agent_execution(self, agent, task, context):
        """Log every agent execution."""
        logger.info(f"Agent {agent.name} executing: {task[:50]}...")
    
    def audit_memory_storage(self, memory_type, content):
        """Audit all memory storage operations."""
        audit_log.write({
            "timestamp": datetime.now(),
            "type": memory_type,
            "content_hash": hash(str(content))
        })
```

### Plugin Configuration

Plugins can access configuration:

```python
class MyPlugin(Plugin):
    def initialize(self):
        # Get plugin-specific config
        config = self.get_config()
        
        self.api_key = config.get("api_key")
        self.endpoint = config.get("endpoint", "default_endpoint")
        self.debug = config.get("debug", False)
        
        if self.debug:
            logger.setLevel(logging.DEBUG)
```

### Plugin Dependencies

Specify dependencies on other plugins:

```python
def get_metadata(self) -> PluginMetadata:
    return PluginMetadata(
        name="my_plugin",
        version="1.0.0",
        dependencies=["required_plugin1", "required_plugin2"],
        # ...
    )
```

Plugins are loaded in dependency order.

### Plugin Distribution

#### Package Your Plugin

```bash
# Create distribution package
cd plugins/my_plugin
tar -czf my_plugin-1.0.0.tar.gz .
```

#### Install Plugin

```bash
# Install from archive
cd plugins/
tar -xzf my_plugin-1.0.0.tar.gz -C ./
```

#### Publish Plugin

1. Create GitHub repository
2. Add comprehensive README
3. Include example usage
4. Tag releases with versions
5. Share in community

### Example Plugins

See `plugins/example_plugin/` for a complete working example that demonstrates:
- Custom agent creation
- Custom tool creation
- Plugin hooks
- Configuration usage
- Error handling

### Plugin Best Practices

1. **Error Handling**: Always handle errors gracefully
2. **Logging**: Use proper logging for debugging
3. **Configuration**: Make plugins configurable
4. **Documentation**: Document usage and API
5. **Testing**: Include tests for your plugin
6. **Versioning**: Follow semantic versioning
7. **Dependencies**: Document all dependencies

### Plugin Security

⚠️ **Important Security Considerations:**

- Only install plugins from trusted sources
- Review plugin code before installation
- Plugins have full system access
- Use plugin sandboxing (when available)
- Keep plugins updated

### Troubleshooting Plugins

#### Plugin Not Loading

1. Check plugin directory structure
2. Verify `plugin.py` exists
3. Check for syntax errors
4. Review logs for error messages
5. Verify dependencies are met

#### Plugin Not Working

1. Check plugin configuration in `config.yaml`
2. Verify plugin is in `enabled_plugins` list
3. Check plugin logs
4. Test with example plugin first
5. Review plugin documentation

#### Plugin Conflicts

1. Check for name conflicts with other plugins
2. Review plugin dependencies
3. Ensure compatible versions
4. Check hook interference
5. Test plugins individually

### Plugin Development Tools

```python
# Test plugin loading
from core.plugin_loader import PluginLoader
from pathlib import Path

plugin_loader = PluginLoader(config, agent_registry, tool_registry)
plugin = plugin_loader.load_plugin(Path("plugins/my_plugin"))
plugin_loader.initialize_plugin("my_plugin")

# List loaded plugins
plugins = plugin_loader.list_plugins()
for plugin in plugins:
    print(f"{plugin['name']} v{plugin['version']}")
```

### Advanced Plugin Features

#### Custom Workflows

Plugins can register custom workflows:

```python
def initialize(self):
    # Register custom workflow
    workflow_manager = self.get_workflow_manager()
    workflow_manager.register_workflow("my_workflow", MyWorkflow)
```

#### Vector Database Access

Plugins can access the vector database:

```python
def initialize(self):
    # Get vector memory manager
    vector_memory = self.get_vector_memory()
    
    # Store plugin data
    vector_memory.add_memory("plugin_collection", "data", metadata)
```

#### LLM Access

Plugins can access LLM router:

```python
def execute_with_llm(self, prompt):
    llm_router = self.get_llm_router()
    response = llm_router.query(prompt, model="llama3.3:latest")
    return response
```

### Complete Plugin Example

See `/plugins/example_plugin/` for a complete, working plugin that demonstrates all features.

### Resources

- [Plugin Base Classes](#plugin-system)
- [Plugin Loader](#plugin-system)
- [Plugin README](../../plugins/README.md)
- [Example Plugin](../../plugins/example_plugin/)
- [Testing Guide](./TESTING.md)

  1290	
  1291	## Configuration
  1292	
  1293	### Agent Configuration Best Practices
  1294	
  1295	```yaml
  1296	agents:
  1297	  enabled_agents:
  1298	    - "my_custom"
  1299	  
  1300	  model_assignments:
  1301	    my_custom:
  1302	      # Choose model based on task complexity
  1303	      primary: "qwen2.5-coder:7b"    # Fast for simple tasks
  1304	      # primary: "deepseek-r1:7b"    # Better reasoning
  1305	      # primary: "llama3.3:latest"   # Balanced
  1306	      
  1307	      fallback: "llama3.3:latest"    # Always have a fallback
  1308	      
  1309	      # Set temperature based on task type
  1310	      temperature: 0.3  # Low (0.1-0.3) for deterministic tasks
  1311	      # temperature: 0.7  # Medium (0.5-0.8) for balanced
  1312	      # temperature: 1.2  # High (1.0-2.0) for creative tasks
  1313	      
  1314	      max_tokens: 4096  # Optional: limit response length
  1315	```
  1316	
  1317	### Tool Configuration Best Practices
  1318	
  1319	```yaml
  1320	tools:
  1321	  enabled_tools:
  1322	    - "my_custom_tool"
  1323	  
  1324	  # Tool-specific settings
  1325	  my_custom_tool_timeout: 60
  1326	  my_custom_tool_retries: 3
  1327	  my_custom_tool_setting: "production"
  1328	```
  1329	
  1330	---
  1331	
  1332	## Testing
  1333	
  1334	### Unit Test Structure
  1335	
  1336	```python
  1337	import pytest
  1338	from unittest.mock import Mock, patch
  1339	from my_component import MyComponent
  1340	
  1341	
  1342	class TestMyComponent:
  1343	    """Test suite for MyComponent."""
  1344	    
  1345	    @pytest.fixture
  1346	    def component(self):
  1347	        """Create test component."""
  1348	        return MyComponent()
  1349	    
  1350	    @pytest.fixture
  1351	    def mock_llm(self):
  1352	        """Create mock LLM router."""
  1353	        mock = Mock()
  1354	        mock.query.return_value = {
  1355	            'response': 'test response',
  1356	            'model': 'test_model'
  1357	        }
  1358	        return mock
  1359	    
  1360	    def test_initialization(self, component):
  1361	        """Test component initialization."""
  1362	        assert component is not None
  1363	    
  1364	    def test_basic_operation(self, component):
  1365	        """Test basic operation."""
  1366	        result = component.do_something('test')
  1367	        assert result == 'expected'
  1368	    
  1369	    def test_with_mock(self, mock_llm):
  1370	        """Test with mocked dependency."""
  1371	        component = MyComponent(llm_router=mock_llm)
  1372	        result = component.execute('task', {})
  1373	        assert result['success'] == True
  1374	    
  1375	    def test_error_handling(self, component):
  1376	        """Test error handling."""
  1377	        with pytest.raises(ValueError):
  1378	            component.do_something(None)
  1379	```
  1380	
  1381	### Integration Test Example
  1382	
  1383	```python
  1384	def test_agent_tool_integration():
  1385	    """Test agent using tool."""
  1386	    from core.engine import Engine
  1387	    
  1388	    engine = Engine()
  1389	    engine.initialize()
  1390	    
  1391	    result = engine.execute_task(
  1392	        task="Test task using my_custom agent and tool",
  1393	        context={},
  1394	        agent_override=['my_custom']
  1395	    )
  1396	    
  1397	    assert result['success'] == True
  1398	```
  1399	
  1400	---
  1401	
  1402	## Best Practices
  1403	
  1404	### 1. Follow Existing Patterns
  1405	
  1406	- Inherit from base classes (`Agent` or `Tool`)
  1407	- Implement all required methods
  1408	- Use standard return formats
  1409	- Follow naming conventions
  1410	
  1411	### 2. Use Type Hints
  1412	
  1413	```python
  1414	def method(self, param: str) -> Dict[str, Any]:
  1415	    """Always include type hints."""
  1416	    pass
  1417	```
  1418	
  1419	### 3. Add Comprehensive Docstrings
  1420	
  1421	```python
  1422	def method(self, param: str) -> int:
  1423	    """
  1424	    Short description.
  1425	    
  1426	    Args:
  1427	        param: Parameter description
  1428	        
  1429	    Returns:
  1430	        Return value description
  1431	        
  1432	    Raises:
  1433	        Exception: When exception occurs
  1434	    """
  1435	    pass
  1436	```
  1437	
  1438	### 4. Handle Errors Gracefully
  1439	
  1440	```python
  1441	try:
  1442	    result = risky_operation()
  1443	    return self._build_success_result(result)
  1444	except SpecificError as e:
  1445	    logger.error(f"Operation failed: {e}")
  1446	    return self._build_error_result(str(e), e)
  1447	```
  1448	
  1449	### 5. Log Important Operations
  1450	
  1451	```python
  1452	self.logger.info(f"Starting operation: {operation_name}")
  1453	self.logger.debug(f"Parameters: {params}")
  1454	self.logger.error(f"Operation failed: {error}")
  1455	```
  1456	
  1457	### 6. Use Memory When Available
  1458	
  1459	```python
  1460	if session_id and self.memory_manager:
  1461	    memory_context = self._get_memory_context(session_id)
  1462	    # Use memory context in your logic
  1463	    
  1464	    # Add results to memory
  1465	    self._add_to_memory(session_id, "Operation completed")
  1466	```
  1467	
  1468	### 7. Make Tools Reusable
  1469	
  1470	- Tools should be stateless
  1471	- Don't make assumptions about usage context
  1472	- Validate all parameters
  1473	- Return consistent formats
  1474	
  1475	### 8. Test Thoroughly
  1476	
  1477	- Unit tests for all public methods
  1478	- Integration tests for agent-tool interaction
  1479	- Error case testing
  1480	- Edge case testing
  1481	
  1482	---
  1483	
  1484	## Common Patterns
  1485	
  1486	### Pattern 1: LLM-Powered Agent
  1487	
  1488	```python
  1489	def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
  1490	    """Agent that uses LLM for intelligence."""
  1491	    
  1492	    prompt = f"""
  1493	You are a {self.name} agent.
  1494	
  1495	Task: {task}
  1496	
  1497	Context: {context}
  1498	
  1499	Provide your response in JSON format.
  1500	"""
  1501	    
  1502	    llm_result = self._get_llm_response(prompt)
  1503	    result = self._parse_llm_response(llm_result)
  1504	    
  1505	    return self._build_success_result("Task completed", result)
  1506	```
  1507	
  1508	### Pattern 2: Tool-Based Agent
  1509	
  1510	```python
  1511	def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
  1512	    """Agent that uses tools for concrete operations."""
  1513	    
  1514	    tool = self._get_tool('required_tool')
  1515	    if not tool:
  1516	        return self._build_error_result("Required tool not available")
  1517	    
  1518	    try:
  1519	        result = tool.invoke({'action': 'do_something', 'param': task})
  1520	        return self._build_success_result("Task completed", result)
  1521	    except Exception as e:
  1522	        return self._build_error_result(f"Tool failed: {e}", e)
  1523	```
  1524	
  1525	### Pattern 3: Hybrid Agent
  1526	
  1527	```python
  1528	def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
  1529	    """Agent that combines LLM and tools."""
  1530	    
  1531	    # Use LLM to analyze task
  1532	    analysis = self._analyze_with_llm(task)
  1533	    
  1534	    # Use tools to execute
  1535	    tool_result = self._execute_with_tools(analysis)
  1536	    
  1537	    # Use LLM to summarize
  1538	    summary = self._summarize_with_llm(tool_result)
  1539	    
  1540	    return self._build_success_result(summary, tool_result)
  1541	```
  1542	
  1543	### Pattern 4: Multi-Step Agent
  1544	
  1545	```python
  1546	def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
  1547	    """Agent with multiple processing steps."""
  1548	    
  1549	    steps = [
  1550	        self._step1_validate,
  1551	        self._step2_process,
  1552	        self._step3_finalize
  1553	    ]
  1554	    
  1555	    result = None
  1556	    for step in steps:
  1557	        result = step(task, context, result)
  1558	        if not result['success']:
  1559	            return result  # Early exit on failure
  1560	    
  1561	    return result
  1562	```
  1563	
  1564	---
  1565	
  1566	## Troubleshooting
  1567	
  1568	### Agent Not Found
  1569	
  1570	**Problem:** `Agent 'my_custom' not found`
  1571	
  1572	**Solutions:**
  1573	1. Check agent is in `agents/__init__.py` exports
  1574	2. Verify registration in `core/engine.py`
  1575	3. Ensure agent is in `enabled_agents` in config.yaml
  1576	4. Check for import errors in agent file
  1577	
  1578	### Tool Not Available
  1579	
  1580	**Problem:** `Tool 'my_custom_tool' not found`
  1581	
  1582	**Solutions:**
  1583	1. Check tool is in `tools/__init__.py` exports
  1584	2. Verify registration in `core/engine.py`
  1585	3. Ensure tool is in `enabled_tools` in config.yaml
  1586	4. Check for import errors in tool file
  1587	
  1588	### LLM Query Fails
  1589	
  1590	**Problem:** `RuntimeError: LLM router not available`
  1591	
  1592	**Solutions:**
  1593	1. Ensure LLM router is passed to agent
  1594	2. Check Ollama is running: `ollama serve`
  1595	3. Verify OpenAI API key if using OpenAI
  1596	4. Check model assignments in config.yaml
  1597	
  1598	### Configuration Not Loaded
  1599	
  1600	**Problem:** Agent/tool doesn't use config settings
  1601	
  1602	**Solutions:**
  1603	1. Verify config.yaml syntax (YAML is whitespace-sensitive)
  1604	2. Check config is passed to component
  1605	3. Use `self.config.get('key', default)` for safe access
  1606	4. Test config loading with `python main.py config --show`
  1607	
  1608	### Import Errors
  1609	
  1610	**Problem:** `ModuleNotFoundError: No module named 'my_component'`
  1611	
  1612	**Solutions:**
  1613	1. Run from project root directory
  1614	2. Add `__init__.py` to package directories
  1615	3. Check file naming (Python naming conventions)
  1616	4. Verify Python path includes project directory
  1617	
  1618	---
  1619	
  1620	## Next Steps
  1621	
  1622	After extending the system:
  1623	
  1624	1. **Test thoroughly**: Write and run unit tests
  1625	2. **Document**: Update `AGENT_INVENTORY.md` or relevant docs
  1626	3. **Configure**: Add model assignments if needed
  1627	4. **Commit**: Use git to track changes
  1628	5. **Share**: Submit pull request if contributing
  1629	
  1630	---
  1631	
  1632	## Additional Resources
  1633	
  1634	- [DESIGN_PRINCIPLES.md](../architecture/DESIGN_PRINCIPLES.md) - Architecture overview
  1635	- [AI_CONTEXT.md](../architecture/AI_CONTEXT.md) - AI assistant guidance
  1636	- [Agent Base Classes](../../agents/base/) - Agent base class
  1637	- [Tool Base Class](../../tools/base.py) - Tool base class
  1638	- [config.yaml](../../config.yaml) - Configuration reference
  1639	
  1640	---
  1641	
  1642	**Happy Extending! 🚀**
  1643	
  1644	**Version:** 2.4.1  
  1645	**Last Updated:** October 13, 2025  
  1646	**Maintained by:** AI Agent Console Development Team
  1647	
  1648	
  1649	
  1650	
  1651	## Advanced Features
  1652	
  1653	### Using Vector Memory for Context-Aware Operations
  1654	
  1655	The system now includes `VectorMemoryManager` which extends the base memory system with semantic search capabilities using ChromaDB.
  1656	
  1657	#### Basic Usage
  1658	
  1659	```python
  1660	from core.vector_memory import VectorMemoryManager
  1661	
  1662	# Initialize with vector database
  1663	memory = VectorMemoryManager(
  1664	    storage_path=Path("./memory"),
  1665	    vector_db_path="./chroma_db"
  1666	)
  1667	
  1668	# Create a session
  1669	session_id = memory.create_session()
  1670	
  1671	# Add messages (automatically stored in vector DB)
  1672	memory.add_user_message(session_id, "How do I implement async in Python?")
  1673	memory.add_agent_message(session_id, "Use async/await keywords...", "code_editor")
  1674	
  1675	# Semantic search across history
  1676	similar = memory.semantic_search(
  1677	    query="python asyncio examples",
  1678	    n_results=5
  1679	)
  1680	
  1681	# Get relevant context for a new query
  1682	context = memory.get_relevant_context(
  1683	    query="show me async function examples",
  1684	    session_id=session_id,
  1685	    max_results=5
  1686	)
  1687	```
  1688	
  1689	#### Storing Task Information
  1690	
  1691	```python
  1692	# Store a task
  1693	memory.store_task(
  1694	    task_id="task_123",
  1695	    task_description="Implement user authentication system",
  1696	    agent_name="code_editor",
  1697	    metadata={"language": "python", "framework": "fastapi"}
  1698	)
  1699	
  1700	# Update task with outcome
  1701	memory.update_task(
  1702	    task_id="task_123",
  1703	    outcome="Successfully implemented JWT-based authentication",
  1704	    status="completed"
  1705	)
  1706	
  1707	# Search for similar tasks
  1708	similar_tasks = memory.search_tasks(
  1709	    query="authentication implementation",
  1710	    n_results=5
  1711	)
  1712	```
  1713	
  1714	#### Storing Context and File References
  1715	
  1716	```python
  1717	# Store important context
  1718	memory.store_context_snapshot(
  1719	    context_id="ctx_123",
  1720	    context_data="User wants to use FastAPI with JWT authentication",
  1721	    context_type="decision",
  1722	    metadata={"project": "api_server"}
  1723	)
  1724	
  1725	# Store file reference
  1726	memory.store_file_reference(
  1727	    file_path="/src/auth.py",
  1728	    content_summary="Contains JWT token generation and validation functions",
  1729	    metadata={"language": "python", "module": "authentication"}
  1730	)
  1731	
  1732	# Search file references
  1733	relevant_files = memory.search_file_references(
  1734	    query="authentication module",
  1735	    n_results=5
  1736	)
  1737	```
  1738	
  1739	### Using the Task Orchestrator
  1740	
  1741	The `TaskOrchestrator` agent manages complex multi-step workflows by decomposing tasks, extracting specifications, and coordinating agent execution.
  1742	
  1743	#### Basic Workflow
  1744	
  1745	```python
  1746	from agents.generic.task_orchestrator import TaskOrchestrator
  1747	
  1748	# Initialize orchestrator
  1749	orchestrator = TaskOrchestrator(
  1750	    llm_router=llm_router,
  1751	    tool_registry=tool_registry,
  1752	    memory_manager=vector_memory
  1753	)
  1754	
  1755	# Execute a complex workflow
  1756	result = orchestrator.execute({
  1757	    'prompt': 'Build a FastAPI web application with user authentication, database, and tests',
  1758	    'session_id': session_id,
  1759	    'context': {'language': 'python', 'framework': 'fastapi'}
  1760	})
  1761	
  1762	# Check results
  1763	print(f"Workflow ID: {result['workflow_id']}")
  1764	print(f"Tasks: {len(result['tasks'])}")
  1765	print(f"Specifications: {result['specifications']}")
  1766	```
  1767	
  1768	#### Understanding the Workflow
  1769	
  1770	The orchestrator performs these steps:
  1771	
  1772	1. **Specification Extraction**: Extracts goals, constraints, preferences, and success measures
  1773	2. **Task Decomposition**: Breaks down the prompt into main tasks and sub-tasks
  1774	3. **Context Gathering**: Retrieves relevant context from memory and vector database
  1775	4. **Agent Selection**: Chooses appropriate agents for each task
  1776	5. **Prompt Enhancement**: Refines prompts while preserving user intent
  1777	6. **Workflow Execution**: Coordinates agent execution with proper dependencies
  1778	
  1779	#### Custom Task Decomposition
  1780	
  1781	```python
  1782	from agents.generic.task_decomposition import TaskDecomposer
  1783	
  1784	decomposer = TaskDecomposer(llm_router=llm_router)
  1785	
  1786	task_structure = decomposer.decompose(
  1787	    prompt="Create a RESTful API with authentication",
  1788	    specifications={
  1789	        'goals': ['Build secure API', 'Implement JWT auth'],
  1790	        'constraints': ['Use Python', 'Must include tests']
  1791	    },
  1792	    max_subtasks=10
  1793	)
  1794	
  1795	print(f"Main tasks: {len(task_structure['tasks'])}")
  1796	for task in task_structure['tasks']:
  1797	    print(f"  - {task['description']}")
  1798	    for subtask in task['subtasks']:
  1799	        print(f"    - {subtask['description']}")
  1800	```
  1801	
  1802	#### Custom Specification Extraction
  1803	
  1804	```python
  1805	from agents.generic.specification_extraction import SpecificationExtractor
  1806	
  1807	extractor = SpecificationExtractor(llm_router=llm_router)
  1808	
  1809	specs = extractor.extract(
  1810	    "Build a Python web API using FastAPI with JWT authentication, "
  1811	    "PostgreSQL database, and comprehensive tests. Must follow REST best practices."
  1812	)
  1813	
  1814	print(f"Goals: {specs['goals']}")
  1815	print(f"Constraints: {specs['constraints']}")
  1816	print(f"Technical Requirements: {specs['technical_requirements']}")
  1817	print(f"Success Measures: {specs['success_measures']}")
  1818	```
  1819	
  1820	#### Context Management
  1821	
  1822	```python
  1823	from agents.generic.context_manager import ContextManager
  1824	
  1825	context_mgr = ContextManager(
  1826	    memory_manager=vector_memory,
  1827	    llm_router=llm_router,
  1828	    context_storage_path=Path("./workflow_context")
  1829	)
  1830	
  1831	# Gather context
  1832	context = context_mgr.gather_context(
  1833	    prompt="Implement user authentication",
  1834	    specifications=specs,
  1835	    task_structure=task_structure,
  1836	    session_id=session_id
  1837	)
  1838	
  1839	# Refine context
  1840	refined = context_mgr.refine_context(
  1841	    context=context,
  1842	    max_tokens=2000
  1843	)
  1844	
  1845	# Store context for later
  1846	context_mgr.store_context(
  1847	    workflow_id="wf_123",
  1848	    context=refined
  1849	)
  1850	```
  1851	
  1852	### Configuration
  1853	
  1854	Add these sections to your `config.yaml`:
  1855	
  1856	```yaml
  1857	# Memory Management
  1858	memory:
  1859	  enabled: true
  1860	  storage_path: "./memory"
  1861	  use_vector_memory: true
  1862	  vector_db_path: "./memory_vector_db"
  1863	  default_max_context_window: 4096
  1864	  auto_save: true
  1865	  enable_summarization: true
  1866	  embedding_model: "nomic-embed-text:latest"
  1867	  search:
  1868	    default_n_results: 10
  1869	    min_similarity: 0.6
  1870	
  1871	# Task Orchestration
  1872	orchestrator:
  1873	  enabled: true
  1874	  context_storage_path: "./workflow_context"
  1875	  max_subtasks_per_task: 20
  1876	  llm:
  1877	    decomposition_model: "qwen3-coder:30b"
  1878	    extraction_model: "qwen3-coder:30b"
  1879	    context_model: "qwen3-coder:30b"
  1880	    temperature: 0.3
  1881	  execution:
  1882	    enable_parallel: false
  1883	    max_concurrent_tasks: 3
  1884	    retry_failed_tasks: true
  1885	    max_retries: 2
  1886	```
  1887	
  1888	### Best Practices
  1889	
  1890	1. **Memory Management**:
  1891	   - Use vector memory for projects requiring context-aware operations
  1892	   - Store important decisions and context snapshots
  1893	   - Track file references for better context retrieval
  1894	   - Regularly search for similar past tasks to learn from history
  1895	
  1896	2. **Task Orchestration**:
  1897	   - Use for complex multi-step workflows (3+ major steps)
  1898	   - Provide clear, specific prompts for better decomposition
  1899	   - Include constraints and preferences in your prompts
  1900	   - Let the orchestrator handle agent selection
  1901	
  1902	3. **Context**:
  1903	   - Store context snapshots at key decision points
  1904	   - Use semantic search to find relevant past context
  1905	   - Refine context before passing to agents to stay within token limits
  1906	   - Track file references for code-related tasks
  1907	
  1908	4. **Performance**:
  1909	   - Vector operations can be expensive; use judiciously
  1910	   - Configure batch sizes based on your system resources
  1911	   - Consider using rule-based fallbacks for simple tasks
  1912	   - Monitor vector database size and clean up old data
  1913	
  1914	### Example: Complete Workflow
  1915	
  1916	```python
  1917	# Initialize system
  1918	from core import VectorMemoryManager, create_vector_memory_manager
  1919	from agents.generic import TaskOrchestrator
  1920	
  1921	# Create memory manager
  1922	memory = create_vector_memory_manager({
  1923	    'storage_path': './memory',
  1924	    'vector_db_path': './chroma_db',
  1925	    'llm_router': llm_router
  1926	})
  1927	
  1928	# Create session
  1929	session_id = memory.create_session(
  1930	    metadata={'project': 'my_api', 'language': 'python'}
  1931	)
  1932	
  1933	# Create orchestrator
  1934	orchestrator = TaskOrchestrator(
  1935	    llm_router=llm_router,
  1936	    tool_registry=tool_registry,
  1937	    memory_manager=memory
  1938	)
  1939	
  1940	# Execute workflow
  1941	result = orchestrator.execute({
  1942	    'prompt': '''
  1943	        Create a Python FastAPI application with:
  1944	        - User authentication using JWT
  1945	        - PostgreSQL database with SQLAlchemy
  1946	        - CRUD operations for users and posts
  1947	        - Unit tests with pytest
  1948	        - API documentation with OpenAPI
  1949	        - Docker deployment configuration
  1950	    ''',
  1951	    'session_id': session_id,
  1952	    'context': {
  1953	        'constraints': [
  1954	            'Use Python 3.11+',
  1955	            'Follow REST API best practices',
  1956	            'Include comprehensive error handling'
  1957	        ],
  1958	        'preferences': [
  1959	            'Use async/await for database operations',
  1960	            'Include type hints throughout'
  1961	        ]
  1962	    }
  1963	})
  1964	
  1965	# Check results
  1966	if result['success']:
  1967	    print(f"Workflow created: {result['workflow_id']}")
  1968	    print(f"Decomposed into {len(result['tasks'])} main tasks")
  1969	    
  1970	    for task in result['tasks']:
  1971	        print(f"\nTask: {task['description']}")
  1972	        print(f"Agent: {task['agent']}")
  1973	        print(f"Subtasks: {len(task['subtasks'])}")
  1974	else:
  1975	    print(f"Error: {result['error']}")
  1976	```
  1977	
  1978	This workflow will:
  1979	1. Extract specifications from the detailed prompt
  1980	2. Decompose into tasks (API setup, auth, database, tests, docs, deployment)
  1981	3. Select appropriate agents for each task
  1982	4. Gather relevant context from memory
  1983	5. Enhance prompts with context and specifications
  1984	6. Create an execution plan
  1985	
  1986	The orchestrator maintains context throughout, stores important decisions in the vector database, and can retrieve similar past work to inform current tasks.
  1987	
  1988	
  1989	
  1990	
  1991	---
  1992	
  1993	## Creating Custom Workflows
  1994	
  1995	**Version 2.2** - Added October 12, 2025
  1996	
  1997	The AI Agent Console includes a workflow automation system that allows you to define complex multi-step development workflows. This guide explains how to create custom workflows.
  1998	
  1999	### Understanding Workflows
  2000	
  2001	A **workflow** is a series of coordinated steps that use different agents to accomplish a complex development task. Each step can:
  2002	- Depend on other steps (execute only after dependencies complete)
  2003	- Have conditional execution (skip based on context)
  2004	- Handle errors differently (fail, continue, retry)
  2005	- Pass context to subsequent steps
  2006	
  2007	### Workflow Structure
  2008	
  2009	Workflows are defined in YAML files with the following structure:
  2010	
  2011	```yaml
  2012	workflow_id: my_custom_workflow
  2013	name: My Custom Workflow
  2014	description: Description of what this workflow does
  2015	version: 1.0.0
  2016	tags:
  2017	  - tag1
  2018	  - tag2
  2019	
  2020	steps:
  2021	  - step_id: step1
  2022	    name: Step 1 Name
  2023	    agent: agent_name
  2024	    action: action_to_perform
  2025	    params:
  2026	      param1: value1
  2027	      param2: "{{ context_variable }}"
  2028	    dependencies: []
  2029	    on_error: fail  # or continue, retry
  2030	    
  2031	  - step_id: step2
  2032	    name: Step 2 Name
  2033	    agent: another_agent
  2034	    action: another_action
  2035	    params:
  2036	      input: "{{ step_step1_result }}"
  2037	    dependencies:
  2038	      - step1
  2039	    condition: "step_step1_result.get('success', False)"
  2040	    on_error: continue
  2041	```
  2042	
  2043	### Step Properties
  2044	
  2045	Each step has the following properties:
  2046	
  2047	- **step_id** (required): Unique identifier for the step
  2048	- **name** (required): Human-readable step name
  2049	- **agent** (required): Agent to execute this step
  2050	- **action** (required): Action for the agent to perform
  2051	- **params** (optional): Parameters for the action
  2052	  - Can include context variables using `{{ variable_name }}`
  2053	  - Can reference previous step results using `{{ step_<step_id>_result }}`
  2054	- **dependencies** (optional): List of step IDs that must complete first
  2055	- **condition** (optional): Python expression for conditional execution
  2056	- **on_error** (optional): Error handling strategy
  2057	  - `fail`: Stop workflow on error (default)
  2058	  - `continue`: Continue to next step despite error
  2059	  - `retry`: Retry the step (future feature)
  2060	
  2061	### Context Variables
  2062	
  2063	Workflows maintain a context dictionary that is passed between steps. You can reference context variables in step parameters using `{{ variable_name }}` syntax.
  2064	
  2065	**Built-in Context Variables:**
  2066	- Variables passed when starting the workflow
  2067	- `step_<step_id>_result`: Result from previous steps
  2068	- Any custom variables set in workflow steps
  2069	
  2070	**Example:**
  2071	```yaml
  2072	params:
  2073	  project_name: "{{ project_name }}"
  2074	  language: "{{ step_detect_language_result.language }}"
  2075	  previous_step_output: "{{ step_analyze_code_result }}"
  2076	```
  2077	
  2078	### Conditional Execution
  2079	
  2080	Steps can be conditionally executed using the `condition` field. The condition is a Python expression evaluated in the workflow context.
  2081	
  2082	**Example:**
  2083	```yaml
  2084	- step_id: fix_tests
  2085	  name: Fix Test Failures
  2086	  agent: debug_agent
  2087	  action: fix_test_failures
  2088	  params:
  2089	    failures: "{{ step_run_tests_result.failures }}"
  2090	  dependencies:
  2091	    - run_tests
  2092	  condition: "not step_run_tests_result.get('all_passed', False)"
  2093	  on_error: continue
  2094	```
  2095	
  2096	### Error Handling
  2097	
  2098	Each step can specify how to handle errors:
  2099	
  2100	1. **fail** (default): Stop the workflow if this step fails
  2101	2. **continue**: Continue to next step even if this step fails
  2102	3. **retry** (future): Retry the step on failure
  2103	
  2104	**Example:**
  2105	```yaml
  2106	- step_id: optional_step
  2107	  name: Optional Operation
  2108	  agent: some_agent
  2109	  action: some_action
  2110	  on_error: continue  # Workflow continues even if this fails
  2111	```
  2112	
  2113	### Complete Example
  2114	
  2115	Here's a complete example workflow for adding a new API endpoint:
  2116	
  2117	```yaml
  2118	workflow_id: add_api_endpoint_workflow
  2119	name: Add API Endpoint
  2120	description: Add a new API endpoint with tests and documentation
  2121	version: 1.0.0
  2122	tags:
  2123	  - api
  2124	  - backend
  2125	  - development
  2126	
  2127	steps:
  2128	  - step_id: analyze_existing_api
  2129	    name: Analyze Existing API Structure
  2130	    agent: code_analyzer
  2131	    action: analyze_api_structure
  2132	    params:
  2133	      project_path: "{{ project_path }}"
  2134	    dependencies: []
  2135	    on_error: fail
  2136	
  2137	  - step_id: plan_endpoint
  2138	    name: Plan New Endpoint
  2139	    agent: code_planner
  2140	    action: plan_api_endpoint
  2141	    params:
  2142	      endpoint_spec: "{{ endpoint_spec }}"
  2143	      existing_structure: "{{ step_analyze_existing_api_result }}"
  2144	    dependencies:
  2145	      - analyze_existing_api
  2146	    on_error: fail
  2147	
  2148	  - step_id: implement_endpoint
  2149	    name: Implement API Endpoint
  2150	    agent: code_editor
  2151	    action: implement_code
  2152	    params:
  2153	      plan: "{{ step_plan_endpoint_result }}"
  2154	      project_path: "{{ project_path }}"
  2155	    dependencies:
  2156	      - plan_endpoint
  2157	    on_error: fail
  2158	
  2159	  - step_id: write_endpoint_tests
  2160	    name: Write Tests for Endpoint
  2161	    agent: code_tester
  2162	    action: generate_tests
  2163	    params:
  2164	      code_files: "{{ step_implement_endpoint_result.files }}"
  2165	      test_framework: "pytest"
  2166	    dependencies:
  2167	      - implement_endpoint
  2168	    on_error: continue
  2169	
  2170	  - step_id: run_endpoint_tests
  2171	    name: Run Endpoint Tests
  2172	    agent: code_tester
  2173	    action: run_tests
  2174	    params:
  2175	      test_path: "{{ step_write_endpoint_tests_result.test_path }}"
  2176	    dependencies:
  2177	      - write_endpoint_tests
  2178	    condition: "step_write_endpoint_tests_result.get('success', False)"
  2179	    on_error: fail
  2180	
  2181	  - step_id: update_api_docs
  2182	    name: Update API Documentation
  2183	    agent: documentation_generator
  2184	    action: update_api_docs
  2185	    params:
  2186	      endpoint_spec: "{{ endpoint_spec }}"
  2187	      implementation: "{{ step_implement_endpoint_result }}"
  2188	    dependencies:
  2189	      - implement_endpoint
  2190	    on_error: continue
  2191	
  2192	  - step_id: git_commit
  2193	    name: Commit Changes
  2194	    agent: git_agent
  2195	    action: commit
  2196	    params:
  2197	      message: "feat: Add {{ endpoint_spec.name }} API endpoint"
  2198	      description: |
  2199	        Added new API endpoint: {{ endpoint_spec.name }}
  2200	        
  2201	        Files:
  2202	        {% for file in step_implement_endpoint_result.files %}
  2203	        - {{ file }}
  2204	        {% endfor %}
  2205	        
  2206	        Tests: {{ 'Passed' if step_run_endpoint_tests_result.success else 'Added' }}
  2207	    dependencies:
  2208	      - run_endpoint_tests
  2209	      - update_api_docs
  2210	    on_error: continue
  2211	```
  2212	
  2213	### Creating a Workflow File
  2214	
  2215	1. **Create YAML file** in `orchestration/workflows/definitions/`:
  2216	   ```bash
  2217	   touch orchestration/workflows/definitions/my_workflow.yaml
  2218	   ```
  2219	
  2220	2. **Define workflow** following the structure above
  2221	
  2222	3. **Test workflow** by running it manually
  2223	
  2224	4. **Update config.yaml** to include your workflow in the available list:
  2225	   ```yaml
  2226	   workflows:
  2227	     available_workflows:
  2228	       - my_workflow
  2229	       # ... other workflows
  2230	   ```
  2231	
  2232	### Using Python-Defined Workflows
  2233	
  2234	For more complex workflows, you can define them in Python by subclassing `BaseWorkflow`:
  2235	
  2236	```python
  2237	from orchestration.workflows import BaseWorkflow
  2238	
  2239	class MyCustomWorkflow(BaseWorkflow):
  2240	    def __init__(self):
  2241	        super().__init__(
  2242	            workflow_id="my_custom_workflow",
  2243	            name="My Custom Workflow",
  2244	            description="A custom workflow defined in Python",
  2245	            version="1.0.0",
  2246	            tags=["custom"]
  2247	        )
  2248	    
  2249	    def _initialize_steps(self):
  2250	        """Define workflow steps."""
  2251	        # Step 1
  2252	        self.add_step(
  2253	            step_id="step1",
  2254	            name="First Step",
  2255	            agent="code_analyzer",
  2256	            action="analyze_code",
  2257	            params={"path": "src/"}
  2258	        )
  2259	        
  2260	        # Step 2 depends on step1
  2261	        self.add_step(
  2262	            step_id="step2",
  2263	            name="Second Step",
  2264	            agent="code_editor",
  2265	            action="implement_code",
  2266	            params={"analysis": "{{ step_step1_result }}"},
  2267	            dependencies=["step1"]
  2268	        )
  2269	```
  2270	
  2271	### Best Practices
  2272	
  2273	1. **Keep Steps Focused**: Each step should do one thing well
  2274	2. **Use Clear Names**: Step names should clearly indicate what they do
  2275	3. **Handle Errors**: Consider appropriate error handling for each step
  2276	4. **Document Context**: Comment what context variables are expected
  2277	5. **Test Workflows**: Test workflows with various scenarios
  2278	6. **Use Dependencies**: Properly order steps with dependencies
  2279	7. **Add Conditions**: Use conditions for optional or conditional steps
  2280	8. **Version Workflows**: Update version numbers when making changes
  2281	
  2282	### Workflow Manager Usage
  2283	
  2284	The WorkflowManager handles workflow discovery and execution:
  2285	
  2286	```python
  2287	from orchestration.workflows import WorkflowManager
  2288	from pathlib import Path
  2289	
  2290	# Initialize manager
  2291	wf_manager = WorkflowManager(
  2292	    workflows_dir=Path("./orchestration/workflows/definitions"),
  2293	    agent_registry=agent_registry,
  2294	    llm_router=llm_router
  2295	)
  2296	
  2297	# List available workflows
  2298	workflows = wf_manager.list_workflows()
  2299	print(f"Available workflows: {len(workflows)}")
  2300	
  2301	# Auto-select workflow based on task
  2302	workflow_id = wf_manager.select_workflow(
  2303	    "I need to refactor my code to improve quality"
  2304	)
  2305	
  2306	# Or prompt user to choose
  2307	workflow_id = wf_manager.prompt_user_for_workflow(
  2308	    "Which workflow do you want to use?",
  2309	    candidates=["refactor_workflow", "analyze_workflow"]
  2310	)
  2311	
  2312	# Execute workflow
  2313	result = await wf_manager.execute_workflow(
  2314	    workflow_id,
  2315	    context={
  2316	        'project_path': './my_project',
  2317	        'refactor_goal': 'Improve code maintainability'
  2318	    },
  2319	    auto_confirm=False
  2320	)
  2321	
  2322	# Check results
  2323	if result['success']:
  2324	    print(f"Workflow completed: {result['workflow_name']}")
  2325	    print(f"Steps completed: {result['progress']['completed']}")
  2326	else:
  2327	    print(f"Workflow failed: {result.get('error')}")
  2328	```
  2329	
  2330	### Debugging Workflows
  2331	
  2332	To debug workflow execution:
  2333	
  2334	1. **Enable Workflow Logging** in config.yaml:
  2335	   ```yaml
  2336	   workflows:
  2337	     execution:
  2338	       enable_logging: true
  2339	       log_dir: "./logs/workflows"
  2340	   ```
  2341	
  2342	2. **Check Workflow State**: Workflows save state on failure
  2343	   ```yaml
  2344	   workflows:
  2345	     execution:
  2346	       save_state_on_failure: true
  2347	       state_storage_dir: "./workflow_states"
  2348	   ```
  2349	
  2350	3. **Review Step Results**: Each step result is stored in workflow context
  2351	
  2352	4. **Use Continue on Error**: For debugging, use `on_error: continue` to see all step results
  2353	
  2354	### Integration with Task Orchestrator
  2355	
  2356	Workflows integrate seamlessly with the task orchestrator:
  2357	
  2358	1. User provides a high-level task
  2359	2. Task orchestrator analyzes the task
  2360	3. WorkflowManager selects appropriate workflow
  2361	4. Workflow executes steps using agents
  2362	5. Results are tracked and reported
  2363	
  2364	This allows for both manual workflow execution and automatic workflow selection based on task analysis.
  2365	
  2366	---
  2367	
  2368	**For more information:**
  2369	- See example workflows in `orchestration/workflows/definitions/`
  2370	- Read API documentation in [AI_CONTEXT.md](../architecture/AI_CONTEXT.md)
  2371	- Check workflow configuration in [config.yaml](../../config.yaml)
  2372	