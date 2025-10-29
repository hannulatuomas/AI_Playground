Here's the result of running `cat -n` on /home/ubuntu/ai-agent-console/PROJECT_STRUCTURE.md:
     1	# AI Agent Console - Project Structure
     2	
     3	## Overview
     4	
     5	This document provides a comprehensive overview of the AI Agent Console project structure and organization.
**Last Updated:** October 14, 2025  
**Version:** 2.5.0
     8	**Version:** 2.4.1
     9	
    10	---
    11	
    12	## Directory Structure
    13	
    14	```
    15	ai-agent-console/
    16	├── agents/                     # Agent system
    17	│   ├── base/                   # Base agent classes
    18	│   │   ├── agent_base.py       # Abstract base agent
    19	│   │   ├── code_editor_base.py # Code editor base
    20	│   │   ├── code_planner_base.py # Code planner base
    21	│   │   ├── build_agent_base.py # Build agent base
    22	│   │   ├── debug_agent_base.py # Debug agent base
    23	│   │   ├── code_analyzer_base.py # Code analyzer base
    24	│   │   ├── code_tester_base.py # Code tester base
    25	│   │   ├── project_init_base.py # Project init base
    26	│   │   └── documentation_agent.py # Documentation base
    27	│   ├── generic/                # Generic agent implementations
    28	│   │   ├── generic_code_editor.py # Generic code editor
    29	│   │   ├── generic_code_planner.py # Generic code planner
    30	│   │   ├── generic_build_agent.py # Generic build agent
    31	│   │   ├── generic_debug_agent.py # Generic debug agent
    32	│   │   ├── generic_code_analyzer.py # Generic code analyzer
    33	│   │   ├── generic_code_tester.py # Generic code tester
    34	│   │   ├── generic_project_init.py # Generic project init
    35	│   │   ├── generic_documentation.py # Generic documentation
    36	│   │   ├── task_orchestrator.py # Task orchestration
    37	│   │   ├── task_decomposition.py # Task decomposition
    38	│   │   ├── specification_extraction.py # Spec extraction
    39	│   │   └── context_manager.py # Context management
    40	│   ├── languages/              # Language-specific agents
    41	│   │   ├── python/             # Python agents
    42	│   │   ├── csharp/             # C# agents
    43	│   │   ├── cpp/                # C++ agents
    44	│   │   ├── web/                # Web development agents
    45	│   │   ├── bash/               # Shell agents
    46	│   │   ├── powershell/         # PowerShell agents
    47	│   │   └── batch/              # Batch agents
    48	│   ├── utils/                  # Agent utilities
    49	│   │   ├── codebase_awareness.py # Codebase context
    50	│   │   ├── context_optimizer.py # Context optimization
    51	│   │   └── clarification_templates.py # Clarification helpers
    52	│   ├── registry.py             # Agent registry
    53	│   ├── git_agent.py            # Git operations agent
    54	│   ├── web_search.py           # Web search agent
    55	│   ├── web_data.py             # Web data retrieval agent
    56	│   ├── database.py             # Database agent
    57	│   ├── data_analysis.py        # Data analysis agent
    58	│   ├── cybersecurity.py        # Cybersecurity agent
    59	│   ├── windows_admin.py        # Windows admin agent
    60	│   ├── prompt_refiner.py       # Prompt refinement agent
    61	│   └── __init__.py             # Agent package init
    62	│
    63	├── tools/                      # Tool system
    64	│   ├── development/            # Development tools
    65	│   │   ├── linter_tool.py      # Code linting
    66	│   │   ├── formatter_tool.py   # Code formatting
    67	│   │   ├── static_analyzer_tool.py # Static analysis
    68	│   │   ├── code_quality_tool.py # Code quality checks
    69	│   │   └── dev_tools_manager.py # Development tools manager
    70	│   ├── base.py                 # Base tool class
    71	│   ├── registry.py             # Tool registry
    72	│   ├── git.py                  # Git tool
    73	│   ├── web_fetch.py            # Web fetching tool
    74	│   ├── file_operations.py      # File operations tool
    75	│   ├── file_io.py              # File I/O tool
    76	│   ├── shell_exec.py           # Shell execution tool
    77	│   ├── ollama_manager.py       # Ollama management tool
    78	│   ├── vector_db.py            # Vector database tool
    79	│   ├── embeddings.py           # Embeddings tool
    80	│   ├── mcp.py                  # MCP protocol tool
    81	│   └── __init__.py             # Tools package init
    82	│
    83	├── core/                       # Core system components
    84	│   ├── llm_router.py           # LLM routing and management
    85	│   ├── memory.py               # Conversation memory system
    86	│   ├── vector_memory.py        # Vector database memory
    87	│   ├── config.py               # Configuration management
    88	│   ├── engine.py               # Main execution engine
    89	│   ├── cache.py                # Caching system
    90	│   ├── database_enhanced.py    # Enhanced database support
    91	│   ├── chat_history.py         # Chat history management
    92	│   ├── project_manager.py      # Project management system
    93	│   ├── prompt_manager.py       # Prompt and snippet management (NEW v2.5)
    94	│   └── __init__.py             # Core package init
    95	│
    96	├── orchestration/              # Workflow orchestration
    97	│   ├── workflows/              # Workflow definitions
    98	│   │   ├── definitions/        # Workflow definition files
    99	│   │   ├── base_workflow.py    # Base workflow class
   100	│   │   └── workflow_manager.py # Workflow management
   101	│   └── __init__.py             # Orchestration package init
   102	│
   103	├── tests/                      # Test suite
   104	│   ├── unit/                   # Unit tests
   105	│   │   ├── agents/             # Agent unit tests
   106	│   │   ├── tools/              # Tool unit tests
   107	│   │   ├── core/               # Core unit tests
   108	│   │   └── orchestration/      # Orchestration unit tests
   109	│   ├── integration/            # Integration tests
   110	│   │   ├── agents/             # Agent integration tests
   111	│   │   └── orchestration/      # Orchestration integration tests
   112	│   ├── e2e/                    # End-to-end tests
   113	│   ├── fixtures/               # Test fixtures
   114	│   ├── mocks/                  # Mock objects
   115	│   └── conftest.py             # Pytest configuration
   116	│
   117	├── docs/                       # Documentation
   118	│   ├── guides/                 # User guides
   119	│   │   ├── user_guide.md       # User guide
   120	│   │   ├── EXAMPLE_USAGE.md    # Usage examples
   121	│   │   ├── EXTENDING_GUIDE.md  # Extending guide
   122	│   │   ├── SAVED_PROMPTS.md    # Saved prompts and snippets guide (NEW v2.5)
   123	│   │   ├── PROJECT_MANAGEMENT.md # Project management guide
   124	│   │   └── CHAT_HISTORY.md     # Chat history guide
   125	│   ├── reference/              # Reference documentation
   126	│   │   ├── AGENT_CATALOG.md    # Agent catalog
   127	│   │   ├── AGENT_INVENTORY.md  # Agent inventory
   128	│   │   ├── AGENT_TOOL_GUIDE.md # Agent-tool guide
   129	│   │   └── MODEL_ASSIGNMENTS.md # Model assignments
   130	│   ├── architecture/           # Architecture documentation
   131	│   │   ├── AI_CONTEXT.md       # AI context
   132	│   │   ├── DESIGN_PRINCIPLES.md # Design principles
   133	│   │   ├── MEMORY_SYSTEM.md    # Memory system
   134	│   │   ├── VECTOR_DB.md        # Vector database
   135	│   │   ├── RICH_UI_INTEGRATION.md # UI integration
   136	│   │   └── PROJECT_CONTEXT_AWARENESS.md # Context awareness
   137	│   ├── development/            # Development documentation
   138	│   │   ├── TODO.md             # TODO list
   139	│   │   ├── STATUS.md           # Project status
   140	│   │   ├── CHANGELOG.md        # Changelog
   141	│   │   ├── FUTURE_IMPROVEMENTS.md # Future improvements
   142	│   │   └── *.md                # Other dev docs
   143	│   └── README.md               # Documentation index
   144	│
   145	├── logs/                       # Log files
   146	│   └── app.log                 # Application log
   147	│
   148	├── main.py                     # Main entry point
   149	├── config.yaml                 # Main configuration file
   150	├── requirements.txt            # Production dependencies
   151	├── requirements-dev.txt        # Development dependencies
   152	├── pytest.ini                  # Pytest configuration
   153	├── mypy.ini                    # MyPy type checking config
   154	├── .gitignore                  # Git ignore rules
   155	├── README.md                   # Project README
   156	├── PROJECT_STRUCTURE.md        # This file
   157	└── setup_verify.py             # Setup verification script
   158	```
   159	
   160	---
   161	
   162	## Key Components
   163	
   164	### Agents (`/agents/`)
   165	
   166	The agent system is organized hierarchically:
   167	
   168	1. **Base Classes** (`/agents/base/`): Abstract base classes that define the agent interface
   169	2. **Generic Implementations** (`/agents/generic/`): Generic agent implementations that can work with any language
   170	3. **Language-Specific** (`/agents/languages/`): Specialized agents for specific programming languages
   171	4. **Specialized Agents**: Domain-specific agents (web, database, security, etc.)
   172	
   173	### Tools (`/tools/`)
   174	
   175	Tools provide concrete functionality that agents can use:
   176	
   177	- **Base Tool** (`base.py`): Abstract base class for all tools
   178	- **Development Tools** (`/development/`): Code quality, linting, formatting tools
   179	- **Integration Tools**: Git, web fetch, file operations, shell execution
   180	- **LLM Tools**: Ollama manager, embeddings
   181	- **Database Tools**: Vector database, ChromaDB integration
   182	
   183	### Core System (`/core/`)
   184	
   185	Core infrastructure components:
   186	
   187	- **LLM Router**: Manages LLM providers (Ollama, OpenAI) and model selection
   188	- **Memory System**: Conversation history and context management
   189	- **Vector Memory**: Semantic search and context-aware retrieval
   190	- **Configuration**: YAML-based configuration with validation
   191	- **Engine**: Main execution engine coordinating agents and tools
   192	- **Cache**: Caching system for LLM responses and data
   193	
   194	### Orchestration (`/orchestration/`)
   195	
   196	Workflow and task management:
   197	
   198	- **Workflow Manager**: Manages predefined workflows
   199	- **Workflow Definitions**: YAML-based workflow definitions
   200	- **Task Decomposition**: Breaks complex tasks into steps
   201	- **Specification Extraction**: Extracts requirements from tasks
   202	
   203	### Tests (`/tests/`)
   204	
   205	Comprehensive test suite:
   206	
   207	- **Unit Tests**: Test individual components in isolation
   208	- **Integration Tests**: Test component interactions
   209	- **End-to-End Tests**: Test complete workflows
   210	- **Fixtures and Mocks**: Test data and mock objects
   211	
   212	### Documentation (`/docs/`)
   213	
   214	Organized documentation:
   215	
   216	- **Guides**: User-facing guides and tutorials
   217	- **Reference**: Technical reference documentation
   218	- **Architecture**: System architecture and design docs
   219	- **Development**: Development status, TODO, changelog
   220	
   221	---
   222	
   223	## File Naming Conventions
   224	
   225	### Python Files
   226	- `snake_case.py` for all Python files
   227	- `*_base.py` for base classes
   228	- `*_agent.py` for agent implementations
   229	- `*_tool.py` for tool implementations
   230	- `test_*.py` for test files
   231	
   232	### Documentation Files
   233	- `UPPERCASE.md` for major documentation files
   234	- `lowercase.md` for guides and references
   235	- Clear, descriptive names
   236	
   237	### Configuration Files
   238	- `.yaml` extension preferred for configuration
   239	- `.toml` for legacy compatibility
   240	- `.ini` for tool-specific configs (pytest, mypy)
   241	
   242	---
   243	
   244	## Import Organization
   245	
   246	### Standard Import Order
   247	1. Standard library imports
   248	2. Third-party imports
   249	3. Local application imports
   250	
   251	### Example
   252	```python
   253	# Standard library
   254	import logging
   255	from typing import Dict, Any, Optional
   256	
   257	# Third-party
   258	import yaml
   259	from pydantic import BaseModel
   260	
   261	# Local
   262	from agents.base import Agent
   263	from tools.registry import ToolRegistry
   264	```
   265	
   266	---
   267	
   268	## Configuration Files
   269	
   270	### Main Configuration
   271	- `config.yaml`: Primary configuration file
   272	- `.env`: Environment variables (not in repo)
   273	
   274	### Tool Configurations
   275	- `pytest.ini`: Pytest configuration
   276	- `mypy.ini`: MyPy type checking configuration
   277	- `.gitignore`: Git ignore rules
   278	
   279	---
   280	
   281	## Development Files
   282	
   283	### Scripts
   284	- `main.py`: Main entry point for CLI
   285	- `setup_verify.py`: Verify installation and setup
   286	- `check_types.py`: Run type checking
   287	- `update_docs.py`: Update documentation
   288	- `generate_language_agents.py`: Generate language-specific agents
   289	- `generate_preference_files.py`: Generate preference files
   290	
   291	### Dependencies
   292	- `requirements.txt`: Production dependencies
   293	- `requirements-dev.txt`: Development dependencies (testing, linting, etc.)
   294	
   295	---
   296	
   297	## Data Storage
   298	
   299	### Runtime Data
   300	- `logs/`: Application logs
   301	- `memory_storage/`: Persistent conversation history
   302	- `chroma_db/`: Vector database storage (if enabled)
   303	- `.cache/`: Temporary cache files
   304	
   305	### Generated Files
   306	- `__pycache__/`: Python bytecode cache
   307	- `.pytest_cache/`: Pytest cache
   308	- `htmlcov/`: Coverage reports
   309	- `.mypy_cache/`: MyPy cache
   310	
   311	---
   312	
   313	## Best Practices
   314	
   315	### Code Organization
   316	1. Keep related functionality together
   317	2. Use clear, descriptive names
   318	3. Follow single responsibility principle
   319	4. Maintain consistent structure across modules
   320	
   321	### Documentation
   322	1. Update documentation with code changes
   323	2. Use docstrings for all public APIs
   324	3. Provide usage examples
   325	4. Keep README files up to date
   326	
   327	### Testing
   328	1. Write tests for new features
   329	2. Maintain test coverage above 80%
   330	3. Use descriptive test names
   331	4. Test edge cases and error conditions
   332	
   333	### Version Control
   334	1. Commit related changes together
   335	2. Write clear commit messages
   336	3. Use feature branches
   337	4. Keep commits focused and atomic
   338	
   339	---
   340	
   341	## Extension Points
   342	
   343	### Adding New Agents
   344	1. Create agent class in appropriate location
   345	2. Inherit from base agent class
   346	3. Implement required methods
   347	4. Register agent in `agents/__init__.py`
   348	5. Add configuration in `config.yaml`
   349	6. Document in `docs/reference/AGENT_CATALOG.md`
   350	
   351	### Adding New Tools
   352	1. Create tool class in `tools/`
   353	2. Inherit from `Tool` base class
   354	3. Implement `invoke()` method
   355	4. Register tool in tool registry
   356	5. Add configuration if needed
   357	6. Document in `docs/reference/AGENT_TOOL_GUIDE.md`
   358	
   359	### Adding New Workflows
   360	1. Create workflow definition in `orchestration/workflows/definitions/`
   361	2. Define workflow steps and agent assignments
   362	3. Register workflow in `WorkflowManager`
   363	4. Add tests for workflow
   364	5. Document in appropriate guide
   365	
   366	---
   367	
   368	## Maintenance
   369	
   370	### Regular Tasks
   371	- Update dependencies: `pip list --outdated`
   372	- Run tests: `pytest`
   373	- Check types: `mypy agents tools core orchestration`
   374	- Lint code: `flake8` and `pylint`
   375	- Format code: `black .` and `isort .`
   376	- Update documentation
   377	
   378	### Version Updates
   379	1. Update version in relevant files
   380	2. Update `CHANGELOG.md`
   381	3. Update `TODO.md` and `STATUS.md`
   382	4. Review and update documentation
   383	5. Run full test suite
   384	6. Commit and tag release
   385	
   386	---
   387	
   388	## Contact and Support
   389	
   390	For questions or issues:
   391	1. Check documentation in `/docs/`
   392	2. Review examples in `/docs/guides/EXAMPLE_USAGE.md`
   393	3. Check GitHub issues
   394	4. Refer to troubleshooting in README.md
   395	
   396	---
   397	
   398	**Last Updated:** October 13, 2025  
   399	**Version:** 2.4.1
   400	