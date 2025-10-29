"""
Command-Line Interface (CLI) for AI Coding Assistant

Lightweight, minimal, user-friendly CLI with intuitive commands.
Integrates code generation, debugging, and language support features.
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import (
    LLMInterface,
    PromptEngine,
    LearningDB,
    ProjectManager,
    load_config_from_file
)
from core.model_manager import ModelManager
from features import (
    CodeGenerator, 
    Debugger, 
    LanguageSupport,
    ProjectNavigator,
    ContextManager,
    TaskManager,
    RuleEnforcer,
    ToolIntegrator
)
from features.project_lifecycle import (
    TemplateManager,
    ProjectScaffolder,
    ProjectInitializer,
    ProjectMaintainer,
    ProjectArchiver
)


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for CLI output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


class CLI:
    """
    Command-Line Interface for AI Coding Assistant.
    
    Provides intuitive commands for code generation and debugging.
    Features feedback loop for continuous improvement.
    """

    def __init__(self):
        """Initialize CLI with all components."""
        self.running = True
        self.last_result = None
        self.last_interaction_id = None
        
        # Initialize components
        self.config = None
        self.llm = None
        self.db = None
        self.engine = None
        self.generator = None
        self.debugger = None
        self.lang_support = None
        
        # New project management components (Phase 1-6)
        self.project_manager = None
        self.project_navigator = None
        self.context_manager = None
        self.task_manager = None
        self.rule_enforcer = None
        self.tool_integrator = None
        self.current_project = None
        
        # RAG components (Phase 8)
        self.rag_indexer = None
        self.rag_retriever = None
        self.rag_available = False
        
        # Model manager
        self.model_manager = None
        
        # Project lifecycle components (Phase 10)
        self.template_manager = None
        self.project_scaffolder = None
        self.project_initializer = None
        self.project_maintainer = None
        self.project_archiver = None
        
        # Command history
        self.history = []

    def colorize(self, text: str, color: str) -> str:
        """Add color to text for terminal output."""
        return f"{color}{text}{Colors.RESET}"

    def print_header(self):
        """Print application header."""
        print("\n" + "="*60)
        print(self.colorize("  AI Coding Assistant", Colors.BOLD + Colors.CYAN))
        print(self.colorize("  Powered by llama.cpp", Colors.CYAN))
        print("="*60 + "\n")

    def print_help(self):
        """Print help information."""
        help_text = f"""
{self.colorize('Available Commands:', Colors.BOLD + Colors.YELLOW)}

{self.colorize('Code Generation:', Colors.BOLD)}
  {self.colorize('gen', Colors.GREEN)} <language> <task>
    Generate code from natural language description
    Example: gen python Create a function to sort a list
    
  {self.colorize('generate', Colors.GREEN)} <language> <task>
    Alias for 'gen'

{self.colorize('Debugging:', Colors.BOLD)}
  {self.colorize('debug', Colors.GREEN)} <language>
    Debug code (will prompt for code and error message)
    Example: debug python
    
  {self.colorize('fix', Colors.GREEN)} <language>
    Alias for 'debug'

{self.colorize('Language Support:', Colors.BOLD)}
  {self.colorize('langs', Colors.GREEN)}
    List all supported languages
    
  {self.colorize('frameworks', Colors.GREEN)} [language]
    List supported frameworks (optionally for specific language)
    
  {self.colorize('template', Colors.GREEN)} <language>
    Show template for a language

{self.colorize('Statistics:', Colors.BOLD)}
  {self.colorize('stats', Colors.GREEN)} [language]
    Show statistics (optionally for specific language)
    
  {self.colorize('history', Colors.GREEN)}
    Show command history

{self.colorize('RAG (Semantic Search):', Colors.BOLD)}
  {self.colorize('rag index', Colors.GREEN)} [project_path]
    Index project for semantic search
    Example: rag index /path/to/project
    
  {self.colorize('rag query', Colors.GREEN)} <query>
    Search code semantically
    Example: rag query "JWT authentication"
    
  {self.colorize('rag status', Colors.GREEN)} [collection]
    Show RAG indexing status and statistics
    
  {self.colorize('rag collections', Colors.GREEN)}
    List all indexed collections
    
  {self.colorize('rag rebuild', Colors.GREEN)} [collection]
    Rebuild index for collection

{self.colorize('Model Management:', Colors.BOLD)}
  {self.colorize('models', Colors.GREEN)}
    List all available models
    
  {self.colorize('models llm', Colors.GREEN)}
    List only LLM models
    
  {self.colorize('models embedding', Colors.GREEN)}
    List only embedding models
    
  {self.colorize('model select', Colors.GREEN)} <model_name>
    Select active LLM model
    Example: model select llama-2-7b
    
  {self.colorize('model info', Colors.GREEN)} <model_name>
    Show detailed model information
    
  {self.colorize('model current', Colors.GREEN)}
    Show currently active model
    
  {self.colorize('model rescan', Colors.GREEN)}
    Rescan models directory

{self.colorize('Project Lifecycle Management:', Colors.BOLD)}
  {self.colorize('project new', Colors.GREEN)} <template> <name> [options]
    Create new project from template
    Options: --author, --license, --no-git, --no-install
    Example: project new web-react my-app --author "John Doe"
    
  {self.colorize('project templates', Colors.GREEN)} [--search query]
    List available templates or search
    Example: project templates --search web
    
  {self.colorize('project init', Colors.GREEN)} [options]
    Initialize existing folder as project
    Options: --license, --git
    
  {self.colorize('project check-deps', Colors.GREEN)}
    Check for dependency updates
    
  {self.colorize('project update-deps', Colors.GREEN)}
    Show commands to update dependencies
    
  {self.colorize('project scan-security', Colors.GREEN)}
    Scan for security vulnerabilities
    
  {self.colorize('project health', Colors.GREEN)}
    Analyze code health metrics
    
  {self.colorize('project archive', Colors.GREEN)} [--format zip|tar.gz]
    Create project archive
    
  {self.colorize('project changelog', Colors.GREEN)} [--from tag]
    Generate changelog from git history
    
  {self.colorize('project release', Colors.GREEN)} <version>
    Prepare release with version bump

{self.colorize('System:', Colors.BOLD)}
  {self.colorize('help', Colors.GREEN)}
    Show this help message
    
  {self.colorize('clear', Colors.GREEN)}
    Clear the screen
    
  {self.colorize('exit', Colors.GREEN)} or {self.colorize('quit', Colors.GREEN)}
    Exit the application

{self.colorize('Tips:', Colors.BOLD)}
  - After each generation/debug, you'll be asked for feedback
  - Feedback helps improve future results
  - Use Tab for command completion (if supported by your terminal)
"""
        print(help_text)

    def initialize_components(self) -> bool:
        """
        Initialize all components (LLM, database, features).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print(self.colorize("Initializing components...", Colors.YELLOW))
            
            # Load configuration
            self.config = load_config_from_file()
            if not self.config:
                print(self.colorize("✗ Configuration not found", Colors.RED))
                print("  Run: python main.py --setup")
                return False
            
            print(self.colorize("✓ Configuration loaded", Colors.GREEN))
            
            # Initialize database
            self.db = LearningDB()
            print(self.colorize("✓ Database initialized", Colors.GREEN))
            
            # Initialize prompt engine
            self.engine = PromptEngine(learning_db=self.db)
            print(self.colorize("✓ Prompt engine ready", Colors.GREEN))
            
            # Initialize LLM
            self.llm = LLMInterface(self.config)
            print(self.colorize("✓ LLM interface ready", Colors.GREEN))
            
            # Initialize features
            self.generator = CodeGenerator(self.llm, self.engine, self.db)
            print(self.colorize("✓ Code generator ready", Colors.GREEN))
            
            self.debugger = Debugger(self.llm, self.engine, self.db)
            print(self.colorize("✓ Debugger ready", Colors.GREEN))
            
            self.lang_support = LanguageSupport()
            print(self.colorize("✓ Language support loaded", Colors.GREEN))
            
            # Try to initialize RAG components (optional)
            try:
                from features import RAG_AVAILABLE
                if RAG_AVAILABLE:
                    from features import RAGIndexer, RAGRetriever
                    self.rag_indexer = RAGIndexer()
                    self.rag_retriever = RAGRetriever(indexer=self.rag_indexer)
                    self.rag_available = True
                    print(self.colorize("✓ RAG system ready (semantic search available)", Colors.GREEN))
            except (ImportError, Exception):
                # RAG not available - silent fail
                pass
            
            # Initialize model manager
            try:
                self.model_manager = ModelManager()
                print(self.colorize("✓ Model manager ready", Colors.GREEN))
            except Exception as e:
                print(self.colorize(f"⚠ Model manager not available: {e}", Colors.YELLOW))
            
            # Initialize project lifecycle components
            try:
                self.template_manager = TemplateManager()
                self.project_scaffolder = ProjectScaffolder()
                self.project_initializer = ProjectInitializer()
                self.project_maintainer = ProjectMaintainer()
                self.project_archiver = ProjectArchiver()
                print(self.colorize("✓ Project lifecycle tools ready", Colors.GREEN))
            except Exception as e:
                print(self.colorize(f"⚠ Project lifecycle not available: {e}", Colors.YELLOW))
            
            print(self.colorize("\n✓ All components initialized!", Colors.BOLD + Colors.GREEN))
            return True
            
        except FileNotFoundError as e:
            print(self.colorize(f"✗ File not found: {e}", Colors.RED))
            print("  Make sure llama.cpp is built and model is downloaded")
            return False
        except Exception as e:
            print(self.colorize(f"✗ Initialization failed: {e}", Colors.RED))
            return False

    def parse_command(self, cmd_line: str) -> tuple:
        """
        Parse command line input.
        
        Args:
            cmd_line: Command line string
            
        Returns:
            Tuple of (command, args)
        """
        parts = cmd_line.strip().split(maxsplit=1)
        if not parts:
            return None, []
        
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        return command, args

    def cmd_generate(self, args: str):
        """Handle code generation command."""
        if not args:
            print(self.colorize("✗ Usage: gen <language> <task>", Colors.RED))
            return
        
        # Parse language and task
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            print(self.colorize("✗ Please specify both language and task", Colors.RED))
            print("  Example: gen python Create a function to calculate factorial")
            return
        
        language, task = parts
        
        print(self.colorize(f"\n→ Generating {language} code...", Colors.YELLOW))
        print(f"  Task: {task}\n")
        
        try:
            # Generate code
            result = self.generator.generate_code(task=task, language=language)
            
            if result['success']:
                # Display code
                print(self.colorize("Generated Code:", Colors.BOLD + Colors.GREEN))
                print(self.colorize("-" * 60, Colors.GREEN))
                print(result['code'])
                print(self.colorize("-" * 60, Colors.GREEN))
                
                # Display explanation
                if result['explanation']:
                    print(self.colorize("\nExplanation:", Colors.BOLD + Colors.CYAN))
                    print(result['explanation'])
                
                # Display framework if detected
                if result['framework']:
                    print(self.colorize(f"\n✓ Framework detected: {result['framework']}", Colors.MAGENTA))
                
                # Store for feedback
                self.last_result = result
                self.last_interaction_id = result['interaction_id']
                
                # Request feedback
                self.request_feedback()
            else:
                print(self.colorize(f"✗ Generation failed: {result['error']}", Colors.RED))
                
        except Exception as e:
            print(self.colorize(f"✗ Error: {e}", Colors.RED))

    def cmd_debug(self, args: str):
        """Handle debugging command."""
        if not args:
            print(self.colorize("✗ Usage: debug <language>", Colors.RED))
            return
        
        language = args.strip()
        
        # Get code to debug
        print(self.colorize("\nEnter code to debug (empty line to finish):", Colors.YELLOW))
        code_lines = []
        while True:
            try:
                line = input(self.colorize("  > ", Colors.CYAN))
                if not line:
                    break
                code_lines.append(line)
            except EOFError:
                break
        
        if not code_lines:
            print(self.colorize("✗ No code provided", Colors.RED))
            return
        
        code = '\n'.join(code_lines)
        
        # Get error message (optional)
        print(self.colorize("\nError message (press Enter if none):", Colors.YELLOW))
        error_msg = input(self.colorize("  > ", Colors.CYAN))
        
        print(self.colorize(f"\n→ Debugging {language} code...", Colors.YELLOW))
        
        try:
            # Debug code
            result = self.debugger.debug_code(
                code=code,
                language=language,
                error_msg=error_msg if error_msg else None
            )
            
            if result['success']:
                # Display fixed code
                print(self.colorize("\nFixed Code:", Colors.BOLD + Colors.GREEN))
                print(self.colorize("-" * 60, Colors.GREEN))
                print(result['fixed_code'])
                print(self.colorize("-" * 60, Colors.GREEN))
                
                # Display explanation
                if result['explanation']:
                    print(self.colorize("\nExplanation:", Colors.BOLD + Colors.CYAN))
                    print(result['explanation'])
                
                # Display changes
                if result['changes']:
                    print(self.colorize("\nChanges Made:", Colors.BOLD + Colors.MAGENTA))
                    for i, change in enumerate(result['changes'], 1):
                        print(f"  {i}. {change}")
                
                # Store for feedback
                self.last_result = result
                self.last_interaction_id = result['interaction_id']
                
                # Request feedback
                self.request_feedback()
            else:
                print(self.colorize(f"✗ Debugging failed: {result['error']}", Colors.RED))
                
        except Exception as e:
            print(self.colorize(f"✗ Error: {e}", Colors.RED))

    def cmd_langs(self, args: str):
        """List all supported languages."""
        languages = self.lang_support.get_supported_languages()
        
        print(self.colorize(f"\nSupported Languages ({len(languages)}):", Colors.BOLD + Colors.CYAN))
        
        # Display in columns
        cols = 3
        for i in range(0, len(languages), cols):
            row = languages[i:i+cols]
            formatted = [f"{lang:15}" for lang in row]
            print("  " + " ".join(formatted))
        
        print(f"\nUse 'template <language>' to see best practices for a language")

    def cmd_frameworks(self, args: str):
        """List supported frameworks."""
        language = args.strip() if args else None
        
        if language:
            frameworks = self.lang_support.get_supported_frameworks(language)
            if frameworks:
                print(self.colorize(f"\nFrameworks for {language}:", Colors.BOLD + Colors.CYAN))
                for fw in frameworks:
                    print(f"  • {fw}")
            else:
                print(self.colorize(f"\n✗ No frameworks found for {language}", Colors.YELLOW))
        else:
            frameworks = self.lang_support.get_supported_frameworks()
            print(self.colorize(f"\nAll Supported Frameworks ({len(frameworks)}):", Colors.BOLD + Colors.CYAN))
            for fw in frameworks:
                print(f"  • {fw}")

    def cmd_template(self, args: str):
        """Show template for a language."""
        if not args:
            print(self.colorize("✗ Usage: template <language>", Colors.RED))
            return
        
        language = args.strip()
        template = self.lang_support.get_template(language)
        
        if template:
            print(self.colorize(f"\nTemplate for {language}:", Colors.BOLD + Colors.CYAN))
            print(self.colorize("-" * 60, Colors.CYAN))
            print(template)
            print(self.colorize("-" * 60, Colors.CYAN))
        else:
            print(self.colorize(f"✗ No template found for '{language}'", Colors.RED))
            print("  Use 'langs' to see supported languages")

    def cmd_stats(self, args: str):
        """Show statistics."""
        language = args.strip() if args else None
        
        try:
            if language:
                stats = self.db.get_language_stats(language)
                print(self.colorize(f"\nStatistics for {language}:", Colors.BOLD + Colors.CYAN))
            else:
                stats = self.db.get_statistics()
                print(self.colorize("\nOverall Statistics:", Colors.BOLD + Colors.CYAN))
            
            print(f"  Total interactions: {stats.get('total_interactions', 0)}")
            print(f"  Success rate: {stats.get('success_rate', 0):.1f}%")
            
            if 'by_language' in stats:
                print(self.colorize("\n  By Language:", Colors.BOLD))
                for lang, count in stats['by_language'].items():
                    print(f"    {lang}: {count}")
                    
        except Exception as e:
            print(self.colorize(f"✗ Error: {e}", Colors.RED))

    def cmd_history(self, args: str):
        """Show command history."""
        if not self.history:
            print(self.colorize("\nNo command history", Colors.YELLOW))
            return
        
        print(self.colorize(f"\nCommand History ({len(self.history)}):", Colors.BOLD + Colors.CYAN))
        for i, cmd in enumerate(self.history[-10:], 1):  # Last 10 commands
            print(f"  {i}. {cmd}")
    
    def cmd_rag(self, args: str):
        """Handle RAG commands."""
        if not self.rag_available:
            print(self.colorize("\n✗ RAG not available", Colors.RED))
            print("  Install dependencies: pip install sentence-transformers chromadb numpy")
            return
        
        if not args:
            print(self.colorize("✗ Usage: rag <subcommand> [args]", Colors.RED))
            print("  Subcommands: index, query, status, collections, rebuild")
            return
        
        # Parse subcommand
        parts = args.split(maxsplit=1)
        subcommand = parts[0].lower()
        subargs = parts[1] if len(parts) > 1 else ""
        
        if subcommand == 'index':
            self.cmd_rag_index(subargs)
        elif subcommand == 'query':
            self.cmd_rag_query(subargs)
        elif subcommand == 'status':
            self.cmd_rag_status(subargs)
        elif subcommand == 'collections':
            self.cmd_rag_collections(subargs)
        elif subcommand == 'rebuild':
            self.cmd_rag_rebuild(subargs)
        else:
            print(self.colorize(f"✗ Unknown RAG subcommand: {subcommand}", Colors.RED))
            print("  Valid: index, query, status, collections, rebuild")
    
    def cmd_rag_index(self, args: str):
        """Index a project for semantic search."""
        project_path = args.strip() if args else self.current_project
        
        if not project_path:
            print(self.colorize("✗ No project path specified", Colors.RED))
            print("  Usage: rag index /path/to/project")
            return
        
        project_path = os.path.abspath(project_path)
        
        if not os.path.exists(project_path):
            print(self.colorize(f"✗ Project path does not exist: {project_path}", Colors.RED))
            return
        
        print(self.colorize(f"\n→ Indexing project: {project_path}", Colors.YELLOW))
        print("  This may take a few moments...\n")
        
        try:
            collection = self.rag_indexer.build_vector_db(project_path)
            print(self.colorize(f"\n✓ Project indexed successfully!", Colors.GREEN))
            print(f"  Collection: {collection}")
            
            # Show statistics
            stats = self.rag_retriever.get_statistics(collection_name=collection)
            print(f"  Total chunks: {stats['total_chunks']}")
            print(f"  Total files: {stats['total_files']}")
            print(f"  Languages: {', '.join(stats['languages'].keys())}")
            
        except Exception as e:
            print(self.colorize(f"✗ Indexing failed: {e}", Colors.RED))
    
    def cmd_rag_query(self, args: str):
        """Query the RAG system semantically."""
        if not args:
            print(self.colorize("✗ No query specified", Colors.RED))
            print("  Usage: rag query <query>")
            print("  Example: rag query 'JWT authentication implementation'")
            return
        
        query = args.strip()
        
        # Get available collections
        collections = self.rag_indexer.list_collections()
        if not collections:
            print(self.colorize("✗ No indexed projects found", Colors.YELLOW))
            print("  Run 'rag index /path/to/project' first")
            return
        
        # Use first collection or let user choose
        collection = collections[0]
        if len(collections) > 1:
            print(self.colorize(f"\nMultiple collections found. Using: {collection}", Colors.YELLOW))
        
        print(self.colorize(f"\n→ Searching: {query}", Colors.YELLOW))
        print(f"  Collection: {collection}\n")
        
        try:
            results = self.rag_retriever.retrieve(
                query=query,
                collection_name=collection,
                top_k=5,
                threshold=0.7
            )
            
            if results:
                print(self.colorize(f"✓ Found {len(results)} relevant code chunks:\n", Colors.GREEN))
                
                for i, result in enumerate(results, 1):
                    print(self.colorize(f"[{i}] {result['file_path']}", Colors.BOLD + Colors.CYAN))
                    if result.get('start_line'):
                        print(f"    Lines: {result['start_line']}-{result['end_line']}")
                    print(f"    Relevance: {result['score']:.2%}")
                    print(f"    Language: {result['language']}")
                    
                    # Show snippet
                    content = result['content']
                    if len(content) > 200:
                        content = content[:200] + "..."
                    print(f"    Snippet: {content}\n")
            else:
                print(self.colorize("✗ No relevant results found", Colors.YELLOW))
                print("  Try a different query or lower the threshold")
                
        except Exception as e:
            print(self.colorize(f"✗ Query failed: {e}", Colors.RED))
    
    def cmd_rag_status(self, args: str):
        """Show RAG status and statistics."""
        collection = args.strip() if args else None
        
        try:
            if collection:
                # Show specific collection
                stats = self.rag_retriever.get_statistics(collection_name=collection)
                print(self.colorize(f"\nRAG Status for: {collection}", Colors.BOLD + Colors.CYAN))
            else:
                # Show all collections
                collections = self.rag_indexer.list_collections()
                if not collections:
                    print(self.colorize("\n✗ No indexed projects", Colors.YELLOW))
                    print("  Run 'rag index /path/to/project' to get started")
                    return
                
                print(self.colorize(f"\nRAG Status ({len(collections)} collections):", Colors.BOLD + Colors.CYAN))
                
                for coll in collections:
                    stats = self.rag_retriever.get_statistics(collection_name=coll)
                    print(f"\n  • {self.colorize(coll, Colors.BOLD)}")
                    print(f"    Files: {stats['total_files']}")
                    print(f"    Chunks: {stats['total_chunks']}")
                    print(f"    Languages: {', '.join(list(stats['languages'].keys())[:3])}")
                return
            
            # Show detailed stats
            print(f"  Total files: {stats['total_files']}")
            print(f"  Total chunks: {stats['total_chunks']}")
            print(f"\n  Languages:")
            for lang, count in stats['languages'].items():
                print(f"    {lang}: {count} chunks")
                
        except Exception as e:
            print(self.colorize(f"✗ Error: {e}", Colors.RED))
    
    def cmd_rag_collections(self, args: str):
        """List all indexed collections."""
        try:
            collections = self.rag_indexer.list_collections()
            
            if not collections:
                print(self.colorize("\n✗ No indexed collections", Colors.YELLOW))
                print("  Run 'rag index /path/to/project' to create one")
                return
            
            print(self.colorize(f"\nIndexed Collections ({len(collections)}):", Colors.BOLD + Colors.CYAN))
            
            for i, coll in enumerate(collections, 1):
                info = self.rag_indexer.get_collection_info(coll)
                print(f"\n  {i}. {self.colorize(coll, Colors.BOLD)}")
                if info['exists']:
                    print(f"     Chunks: {info['total_chunks']}")
                    if 'metadata' in info and info['metadata']:
                        meta = info['metadata']
                        if 'total_files' in meta:
                            print(f"     Files: {meta['total_files']}")
                        if 'indexed_at' in meta:
                            print(f"     Indexed: {meta['indexed_at'][:19]}")
        
        except Exception as e:
            print(self.colorize(f"✗ Error: {e}", Colors.RED))
    
    def cmd_rag_rebuild(self, args: str):
        """Rebuild index for a collection."""
        if not args:
            print(self.colorize("✗ No collection specified", Colors.RED))
            print("  Usage: rag rebuild <collection_name>")
            print("  Use 'rag collections' to see available collections")
            return
        
        collection = args.strip()
        
        # Get collection info
        try:
            info = self.rag_indexer.get_collection_info(collection)
            if not info['exists']:
                print(self.colorize(f"✗ Collection not found: {collection}", Colors.RED))
                return
            
            # Confirm rebuild
            print(self.colorize(f"\n⚠ This will rebuild the index for: {collection}", Colors.YELLOW))
            response = input(self.colorize("  Continue? (y/n): ", Colors.YELLOW)).lower().strip()
            
            if response not in ['y', 'yes']:
                print("  Cancelled")
                return
            
            # Get project path from metadata
            if 'metadata' not in info or 'root_folder' not in info['metadata']:
                print(self.colorize("✗ Cannot determine project path", Colors.RED))
                return
            
            project_path = info['metadata']['root_folder']
            
            print(self.colorize(f"\n→ Rebuilding index...", Colors.YELLOW))
            
            # Rebuild
            new_collection = self.rag_indexer.build_vector_db(
                root_folder=project_path,
                project_name=collection,
                force_rebuild=True
            )
            
            print(self.colorize(f"\n✓ Index rebuilt successfully!", Colors.GREEN))
            
        except Exception as e:
            print(self.colorize(f"✗ Rebuild failed: {e}", Colors.RED))

    def cmd_clear(self, args: str):
        """Clear the screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_header()
    
    def cmd_models(self, args: str):
        """List available models."""
        if not self.model_manager:
            print(self.colorize("✗ Model manager not available", Colors.RED))
            return
        
        model_type = args.strip().lower() if args else None
        
        if model_type and model_type not in ['llm', 'embedding']:
            print(self.colorize(f"✗ Invalid model type: {model_type}", Colors.RED))
            print("  Valid types: llm, embedding")
            return
        
        try:
            models = self.model_manager.list_models(model_type=model_type)
            
            if not models:
                print(self.colorize("\n✗ No models found", Colors.YELLOW))
                print("  Place model files in data/models/ and run 'model rescan'")
                return
            
            # Get active model
            active_name = self.model_manager.get_active_llm()
            
            # Group by type
            llm_models = [m for m in models if m.type == 'llm']
            emb_models = [m for m in models if m.type == 'embedding']
            
            if not model_type or model_type == 'llm':
                print(self.colorize(f"\n=== LLM Models ({len(llm_models)}) ===", Colors.BOLD + Colors.CYAN))
                if llm_models:
                    for i, model in enumerate(llm_models, 1):
                        prefix = "✓" if model.name == active_name else " "
                        status = self.colorize(" [ACTIVE]", Colors.GREEN) if model.name == active_name else ""
                        print(f"  {prefix} {i}. {self.model_manager.format_model_info(model)}{status}")
                else:
                    print("  No LLM models found")
                    print("  Place .gguf files in data/models/")
            
            if not model_type or model_type == 'embedding':
                print(self.colorize(f"\n=== Embedding Models ({len(emb_models)}) ===", Colors.BOLD + Colors.CYAN))
                if emb_models:
                    for i, model in enumerate(emb_models, 1):
                        print(f"  {i}. {self.model_manager.format_model_info(model)}")
                else:
                    print("  No embedding models found")
            
            # Show stats
            stats = self.model_manager.get_model_stats()
            print(self.colorize(f"\n=== Statistics ===", Colors.BOLD + Colors.CYAN))
            print(f"  Total models: {stats['total']}")
            print(f"  Total size: {stats['total_size_mb']:.1f} MB")
            
        except Exception as e:
            print(self.colorize(f"✗ Error: {e}", Colors.RED))
    
    def cmd_model(self, args: str):
        """Handle model subcommands."""
        if not self.model_manager:
            print(self.colorize("✗ Model manager not available", Colors.RED))
            return
        
        if not args:
            print(self.colorize("✗ Usage: model <subcommand> [args]", Colors.RED))
            print("  Subcommands: select, info, current, rescan")
            return
        
        # Parse subcommand
        parts = args.split(maxsplit=1)
        subcommand = parts[0].lower()
        subargs = parts[1] if len(parts) > 1 else ""
        
        if subcommand == 'select':
            self.cmd_model_select(subargs)
        elif subcommand == 'info':
            self.cmd_model_info(subargs)
        elif subcommand == 'current':
            self.cmd_model_current(subargs)
        elif subcommand == 'rescan':
            self.cmd_model_rescan(subargs)
        else:
            print(self.colorize(f"✗ Unknown model subcommand: {subcommand}", Colors.RED))
            print("  Valid: select, info, current, rescan")
    
    def cmd_model_select(self, args: str):
        """Select active LLM model."""
        if not args:
            print(self.colorize("✗ Usage: model select <model_name>", Colors.RED))
            print("  Use 'models llm' to see available models")
            return
        
        model_name = args.strip()
        
        try:
            # Check if model exists
            model = self.model_manager.get_model(model_name)
            if not model:
                print(self.colorize(f"✗ Model not found: {model_name}", Colors.RED))
                print("  Use 'models llm' to see available models")
                return
            
            if model.type != 'llm':
                print(self.colorize(f"✗ Not an LLM model: {model_name}", Colors.RED))
                return
            
            if not model.is_available:
                print(self.colorize(f"✗ Model not available: {model_name}", Colors.RED))
                print(f"  Path: {model.path}")
                return
            
            # Set as active
            if self.model_manager.set_active_llm(model_name):
                print(self.colorize(f"✓ Active model set to: {model_name}", Colors.GREEN))
                print(f"  {model.description}")
                print(f"  Size: {model.size_mb:.1f} MB")
                if model.context_size:
                    print(f"  Context: {model.context_size} tokens")
                print(self.colorize("\n⚠ Restart the application for changes to take effect", Colors.YELLOW))
            else:
                print(self.colorize("✗ Failed to set active model", Colors.RED))
                
        except Exception as e:
            print(self.colorize(f"✗ Error: {e}", Colors.RED))
    
    def cmd_model_info(self, args: str):
        """Show detailed model information."""
        if not args:
            print(self.colorize("✗ Usage: model info <model_name>", Colors.RED))
            return
        
        model_name = args.strip()
        
        try:
            model = self.model_manager.get_model(model_name)
            if not model:
                print(self.colorize(f"✗ Model not found: {model_name}", Colors.RED))
                return
            
            print(self.colorize(f"\n=== Model Information: {model.name} ===", Colors.BOLD + Colors.CYAN))
            print(f"  Type: {model.type.upper()}")
            print(f"  Description: {model.description}")
            print(f"  Size: {model.size_mb:.1f} MB")
            
            if model.parameters:
                print(f"  Parameters: {model.parameters}")
            
            if model.quantization:
                print(f"  Quantization: {model.quantization}")
            
            if model.context_size:
                print(f"  Context size: {model.context_size} tokens")
            
            if model.path != 'huggingface':
                print(f"  Path: {model.path}")
                print(f"  Available: {'✓ Yes' if model.is_available else '✗ No'}")
            else:
                print(f"  Source: Hugging Face (downloaded on first use)")
            
            # Check if active
            if model.type == 'llm':
                active = self.model_manager.get_active_llm()
                if active == model.name:
                    print(self.colorize("\n  Status: ACTIVE", Colors.GREEN))
                    
        except Exception as e:
            print(self.colorize(f"✗ Error: {e}", Colors.RED))
    
    def cmd_model_current(self, args: str):
        """Show currently active model."""
        try:
            active = self.model_manager.get_active_llm()
            
            if not active:
                print(self.colorize("\n✗ No active model configured", Colors.YELLOW))
                print("  Use 'model select <name>' to set one")
                return
            
            model = self.model_manager.get_model(active)
            if not model:
                print(self.colorize(f"\n✗ Active model not found: {active}", Colors.RED))
                return
            
            print(self.colorize("\n=== Active LLM Model ===", Colors.BOLD + Colors.CYAN))
            print(f"  Name: {model.name}")
            print(f"  Description: {model.description}")
            print(f"  Size: {model.size_mb:.1f} MB")
            if model.context_size:
                print(f"  Context: {model.context_size} tokens")
            print(f"  Path: {model.path}")
            
        except Exception as e:
            print(self.colorize(f"✗ Error: {e}", Colors.RED))
    
    def cmd_model_rescan(self, args: str):
        """Rescan models directory."""
        try:
            print(self.colorize("\n→ Rescanning models directory...", Colors.YELLOW))
            self.model_manager.rescan()
            print(self.colorize("✓ Rescan complete!", Colors.GREEN))
            
            # Show updated stats
            stats = self.model_manager.get_model_stats()
            print(f"\n  Found {stats['llm']} LLM models")
            print(f"  Found {stats['embedding']} embedding models")
            print(f"  Total size: {stats['total_size_mb']:.1f} MB")
            
        except Exception as e:
            print(self.colorize(f"✗ Error: {e}", Colors.RED))

    def request_feedback(self):
        """Request user feedback after an action."""
        if not self.last_interaction_id:
            return
        
        print(self.colorize("\n" + "-" * 60, Colors.YELLOW))
        print(self.colorize("Feedback (helps improve future results):", Colors.BOLD + Colors.YELLOW))
        
        # Get success/failure
        while True:
            response = input(self.colorize("Did this work? (y/n): ", Colors.YELLOW)).lower().strip()
            if response in ['y', 'n', 'yes', 'no']:
                success = response in ['y', 'yes']
                break
            print(self.colorize("Please enter 'y' or 'n'", Colors.RED))
        
        # Get optional feedback text
        feedback_text = input(self.colorize("Additional feedback (optional): ", Colors.YELLOW)).strip()
        
        # Update database
        try:
            if self.last_result and 'code' in self.last_result:
                self.generator.provide_feedback(
                    interaction_id=self.last_interaction_id,
                    success=success,
                    feedback=feedback_text if feedback_text else None
                )
            elif self.last_result and 'fixed_code' in self.last_result:
                self.debugger.provide_feedback(
                    interaction_id=self.last_interaction_id,
                    success=success,
                    feedback=feedback_text if feedback_text else None
                )
            
            print(self.colorize("✓ Feedback recorded. Thank you!", Colors.GREEN))
        except Exception as e:
            print(self.colorize(f"✗ Failed to record feedback: {e}", Colors.RED))
        
        print(self.colorize("-" * 60, Colors.YELLOW))

    def run(self):
        """Main CLI loop."""
        # Print header
        self.print_header()
        
        # Initialize components
        if not self.initialize_components():
            print(self.colorize("\n✗ Failed to initialize. Exiting.", Colors.RED))
            return 1
        
        # Print initial help
        print(self.colorize("\nType 'help' for available commands", Colors.CYAN))
        print(self.colorize("Type 'exit' or 'quit' to exit\n", Colors.CYAN))
        
        # Main loop
        while self.running:
            try:
                # Get input
                cmd_line = input(self.colorize("\nai-assistant> ", Colors.BOLD + Colors.GREEN))
                
                if not cmd_line.strip():
                    continue
                
                # Add to history
                self.history.append(cmd_line)
                
                # Parse command
                command, args = self.parse_command(cmd_line)
                
                if not command:
                    continue
                
                # Handle commands
                if command in ['exit', 'quit', 'q']:
                    print(self.colorize("\nGoodbye! 👋", Colors.CYAN))
                    self.running = False
                
                elif command in ['help', 'h', '?']:
                    self.print_help()
                
                elif command in ['gen', 'generate']:
                    self.cmd_generate(args)
                
                elif command in ['debug', 'fix']:
                    self.cmd_debug(args)
                
                elif command == 'langs':
                    self.cmd_langs(args)
                
                elif command == 'frameworks':
                    self.cmd_frameworks(args)
                
                elif command == 'template':
                    self.cmd_template(args)
                
                elif command == 'stats':
                    self.cmd_stats(args)
                
                elif command == 'history':
                    self.cmd_history(args)
                
                elif command == 'clear':
                    self.cmd_clear(args)
                
                elif command == 'rag':
                    self.cmd_rag(args)
                
                elif command == 'models':
                    self.cmd_models(args)
                
                elif command == 'model':
                    self.cmd_model(args)
                
                elif command == 'project':
                    # Import project commands module
                    from . import cli_project_commands as proj_cmds
                    # Bind methods to self
                    proj_cmds.cmd_project(self, args)
                
                else:
                    print(self.colorize(f"✗ Unknown command: {command}", Colors.RED))
                    print("  Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print(self.colorize("\n\nUse 'exit' or 'quit' to exit", Colors.YELLOW))
            except EOFError:
                print(self.colorize("\n\nGoodbye! 👋", Colors.CYAN))
                self.running = False
            except Exception as e:
                print(self.colorize(f"\n✗ Error: {e}", Colors.RED))
        
        return 0


def main():
    """Entry point for CLI."""
    cli = CLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
