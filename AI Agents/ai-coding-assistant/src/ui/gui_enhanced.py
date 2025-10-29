"""
Enhanced GUI for AI Coding Assistant - Project Management Features

Fully integrated GUI with all Phase 1-7 features:
- Project Management
- File Navigation  
- Task Decomposition
- Rule Enforcement
- Tool Integration
- Testing
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import (
    LLMInterface, PromptEngine, LearningDB,
    ProjectManager, load_config_from_file
)
from features import (
    CodeGenerator, Debugger, LanguageSupport,
    ProjectNavigator, ContextManager, TaskManager,
    RuleEnforcer, ToolIntegrator
)


class EnhancedGUI:
    """Enhanced GUI with full project management features."""

    def __init__(self, root):
        self.root = root
        self.root.title("AI Coding Assistant - Enhanced")
        self.root.geometry("1200x800")
        
        # Components
        self.config = None
        self.llm = None
        self.db = None
        self.engine = None
        self.generator = None
        self.debugger = None
        self.lang_support = None
        
        # Project components
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
        
        # Create notebook (tabbed interface)
        self.create_notebook()
        
        # Initialize
        self.initialize_components()

    def create_notebook(self):
        """Create tabbed interface."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Tab 1: Code Generation & Debug
        self.tab_code = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_code, text="  Code  ")
        self.create_code_tab()
        
        # Tab 2: Project Management
        self.tab_project = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_project, text="  Project  ")
        self.create_project_tab()
        
        # Tab 3: Tasks
        self.tab_tasks = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_tasks, text="  Tasks  ")
        self.create_tasks_tab()
        
        # Tab 4: Tools (Git, Tests)
        self.tab_tools = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_tools, text="  Tools  ")
        self.create_tools_tab()
        
        # Tab 5: Rules & Settings
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text="  Settings  ")
        self.create_settings_tab()
        
        # Tab 6: RAG (Semantic Search)
        self.tab_rag = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_rag, text="  RAG  ")
        self.create_rag_tab()

    def create_code_tab(self):
        """Create code generation/debug tab."""
        # Status bar
        status_frame = ttk.Frame(self.tab_code)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(status_frame, text="Status:", font=('Arial', 10, 'bold')).pack(side='left')
        self.status_label = ttk.Label(status_frame, text="● Initializing...", foreground='orange')
        self.status_label.pack(side='left', padx=10)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(self.tab_code, text="Mode", padding=10)
        mode_frame.pack(fill='x', padx=10, pady=5)
        
        self.mode_var = tk.StringVar(value="generate")
        ttk.Radiobutton(mode_frame, text="Generate Code", variable=self.mode_var, 
                       value="generate", command=self.on_mode_change).pack(side='left', padx=10)
        ttk.Radiobutton(mode_frame, text="Debug Code", variable=self.mode_var,
                       value="debug", command=self.on_mode_change).pack(side='left')
        
        # Input frame
        input_frame = ttk.LabelFrame(self.tab_code, text="Input", padding=10)
        input_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Language selection
        lang_frame = ttk.Frame(input_frame)
        lang_frame.pack(fill='x', pady=5)
        ttk.Label(lang_frame, text="Language:").pack(side='left')
        self.language_var = tk.StringVar()
        self.language_combo = ttk.Combobox(lang_frame, textvariable=self.language_var,
                                          width=20, state='readonly')
        self.language_combo.pack(side='left', padx=10)
        
        # Input text
        self.input_text = scrolledtext.ScrolledText(input_frame, height=8, wrap='word',
                                                    font=('Consolas', 10))
        self.input_text.pack(fill='both', expand=True, pady=5)
        
        # Action buttons
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill='x', pady=5)
        self.action_btn = ttk.Button(btn_frame, text="Generate", command=self.on_code_action, width=15)
        self.action_btn.pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.on_clear_code, width=15).pack(side='left')
        
        # Output frame
        output_frame = ttk.LabelFrame(self.tab_code, text="Output", padding=10)
        output_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap='word',
                                                     font=('Consolas', 10), state='disabled')
        self.output_text.pack(fill='both', expand=True)

    def create_project_tab(self):
        """Create project management tab."""
        # Project selector
        proj_frame = ttk.LabelFrame(self.tab_project, text="Project", padding=10)
        proj_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(proj_frame, text="Root Folder:").pack(side='left')
        self.project_path_var = tk.StringVar(value="No project loaded")
        ttk.Entry(proj_frame, textvariable=self.project_path_var, state='readonly').pack(
            side='left', fill='x', expand=True, padx=10)
        ttk.Button(proj_frame, text="Browse...", command=self.on_browse_project).pack(side='left', padx=5)
        ttk.Button(proj_frame, text="Scan", command=self.on_scan_project).pack(side='left')
        
        # Split frame for file tree and search
        split_frame = ttk.Frame(self.tab_project)
        split_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left: File tree
        tree_frame = ttk.LabelFrame(split_frame, text="Project Files", padding=10)
        tree_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.file_tree = ttk.Treeview(tree_frame, selectmode='browse')
        self.file_tree.pack(fill='both', expand=True)
        tree_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.file_tree.yview)
        tree_scroll.pack(side='right', fill='y')
        self.file_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Right: Search and info
        right_frame = ttk.Frame(split_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Search
        search_frame = ttk.LabelFrame(right_frame, text="Search Files", padding=10)
        search_frame.pack(fill='x', pady=(0, 5))
        
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill='x')
        self.search_var = tk.StringVar()
        ttk.Entry(search_input_frame, textvariable=self.search_var).pack(side='left', fill='x', expand=True)
        ttk.Button(search_input_frame, text="Search", command=self.on_search_files).pack(side='left', padx=(5, 0))
        
        self.search_results = tk.Listbox(search_frame, height=8)
        self.search_results.pack(fill='both', expand=True, pady=5)
        
        # Project stats
        stats_frame = ttk.LabelFrame(right_frame, text="Project Stats", padding=10)
        stats_frame.pack(fill='both', expand=True)
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=10, wrap='word',
                                                    font=('Consolas', 9), state='disabled')
        self.stats_text.pack(fill='both', expand=True)

    def create_tasks_tab(self):
        """Create task management tab."""
        # Task input
        input_frame = ttk.LabelFrame(self.tab_tasks, text="New Task", padding=10)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(input_frame, text="Task Description:").pack(anchor='w')
        self.task_desc_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.task_desc_var).pack(fill='x', pady=5)
        
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill='x')
        ttk.Button(btn_frame, text="Decompose Task", command=self.on_decompose_task, width=20).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Execute Task", command=self.on_execute_task, width=20).pack(side='left')
        
        # Task list
        list_frame = ttk.LabelFrame(self.tab_tasks, text="Sub-tasks", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.task_tree = ttk.Treeview(list_frame, columns=('status', 'type'), show='tree headings')
        self.task_tree.heading('#0', text='Description')
        self.task_tree.heading('status', text='Status')
        self.task_tree.heading('type', text='Type')
        self.task_tree.column('status', width=100)
        self.task_tree.column('type', width=120)
        self.task_tree.pack(fill='both', expand=True)
        
        # Task output
        output_frame = ttk.LabelFrame(self.tab_tasks, text="Execution Log", padding=10)
        output_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.task_output = scrolledtext.ScrolledText(output_frame, height=8, wrap='word',
                                                     font=('Consolas', 9), state='disabled')
        self.task_output.pack(fill='both', expand=True)

    def create_tools_tab(self):
        """Create tools (Git/Tests) tab."""
        # Git section
        git_frame = ttk.LabelFrame(self.tab_tools, text="Git Operations", padding=10)
        git_frame.pack(fill='x', padx=10, pady=5)
        
        status_frame = ttk.Frame(git_frame)
        status_frame.pack(fill='x', pady=5)
        ttk.Button(status_frame, text="Git Status", command=self.on_git_status, width=15).pack(side='left', padx=5)
        ttk.Button(status_frame, text="Commit", command=self.on_git_commit, width=15).pack(side='left')
        
        self.git_status_text = scrolledtext.ScrolledText(git_frame, height=6, wrap='word',
                                                         font=('Consolas', 9), state='disabled')
        self.git_status_text.pack(fill='x', pady=5)
        
        # Testing section
        test_frame = ttk.LabelFrame(self.tab_tools, text="Testing", padding=10)
        test_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        test_btn_frame = ttk.Frame(test_frame)
        test_btn_frame.pack(fill='x', pady=5)
        ttk.Button(test_btn_frame, text="Run Tests", command=self.on_run_tests, width=15).pack(side='left', padx=5)
        ttk.Button(test_btn_frame, text="Run with Auto-Fix", command=self.on_run_tests_fix, width=20).pack(side='left')
        
        self.test_output = scrolledtext.ScrolledText(test_frame, wrap='word',
                                                     font=('Consolas', 9), state='disabled')
        self.test_output.pack(fill='both', expand=True, pady=5)

    def create_settings_tab(self):
        """Create settings and rules tab."""
        # Rules section
        rules_frame = ttk.LabelFrame(self.tab_settings, text="Coding Rules", padding=10)
        rules_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Add rule
        add_frame = ttk.Frame(rules_frame)
        add_frame.pack(fill='x', pady=5)
        ttk.Label(add_frame, text="New Rule:").pack(side='left')
        self.new_rule_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.new_rule_var).pack(side='left', fill='x', expand=True, padx=10)
        ttk.Button(add_frame, text="Add Rule", command=self.on_add_rule).pack(side='left')
        
        # Rules list
        self.rules_listbox = tk.Listbox(rules_frame, height=15)
        self.rules_listbox.pack(fill='both', expand=True, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(rules_frame)
        btn_frame.pack(fill='x')
        ttk.Button(btn_frame, text="Refresh Rules", command=self.on_load_rules).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Remove Selected", command=self.on_remove_rule).pack(side='left')
    
    def create_rag_tab(self):
        """Create RAG (semantic search) tab."""
        # Status frame
        status_frame = ttk.LabelFrame(self.tab_rag, text="RAG Status", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.rag_status_label = ttk.Label(status_frame, text="● Not initialized", foreground='orange')
        self.rag_status_label.pack(side='left')
        
        ttk.Button(status_frame, text="Refresh Status", command=self.on_rag_refresh_status).pack(side='right')
        
        # Indexing frame
        index_frame = ttk.LabelFrame(self.tab_rag, text="Indexing", padding=10)
        index_frame.pack(fill='x', padx=10, pady=5)
        
        # Project path
        path_frame = ttk.Frame(index_frame)
        path_frame.pack(fill='x', pady=5)
        ttk.Label(path_frame, text="Project:").pack(side='left')
        self.rag_project_var = tk.StringVar(value="No project selected")
        ttk.Entry(path_frame, textvariable=self.rag_project_var, state='readonly').pack(
            side='left', fill='x', expand=True, padx=10)
        ttk.Button(path_frame, text="Browse...", command=self.on_rag_browse).pack(side='left', padx=5)
        
        # Index button
        btn_frame = ttk.Frame(index_frame)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Index Project", command=self.on_rag_index, width=20).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Rebuild Index", command=self.on_rag_rebuild, width=20).pack(side='left')
        
        # Progress
        self.rag_progress_var = tk.StringVar(value="Ready")
        ttk.Label(index_frame, textvariable=self.rag_progress_var).pack(pady=5)
        
        # Collections frame
        coll_frame = ttk.LabelFrame(self.tab_rag, text="Indexed Collections", padding=10)
        coll_frame.pack(fill='x', padx=10, pady=5)
        
        # Collections list
        list_frame = ttk.Frame(coll_frame)
        list_frame.pack(fill='x')
        
        self.rag_collections_list = tk.Listbox(list_frame, height=5)
        self.rag_collections_list.pack(side='left', fill='both', expand=True)
        self.rag_collections_list.bind('<<ListboxSelect>>', self.on_rag_collection_select)
        
        scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.rag_collections_list.yview)
        scroll.pack(side='right', fill='y')
        self.rag_collections_list.configure(yscrollcommand=scroll.set)
        
        ttk.Button(coll_frame, text="Refresh Collections", command=self.on_rag_list_collections).pack(pady=5)
        
        # Statistics
        stats_frame = ttk.Frame(coll_frame)
        stats_frame.pack(fill='x', pady=5)
        
        self.rag_stats_text = scrolledtext.ScrolledText(stats_frame, height=4, wrap='word',
                                                         font=('Consolas', 9), state='disabled')
        self.rag_stats_text.pack(fill='x')
        
        # Query frame
        query_frame = ttk.LabelFrame(self.tab_rag, text="Semantic Search", padding=10)
        query_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Query input
        input_frame = ttk.Frame(query_frame)
        input_frame.pack(fill='x', pady=5)
        ttk.Label(input_frame, text="Query:").pack(side='left')
        self.rag_query_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.rag_query_var).pack(side='left', fill='x', expand=True, padx=10)
        ttk.Button(input_frame, text="Search", command=self.on_rag_query, width=15).pack(side='left')
        
        # Filters
        filter_frame = ttk.Frame(query_frame)
        filter_frame.pack(fill='x', pady=5)
        ttk.Label(filter_frame, text="Language Filter:").pack(side='left')
        self.rag_lang_filter_var = tk.StringVar(value="All")
        rag_lang_combo = ttk.Combobox(filter_frame, textvariable=self.rag_lang_filter_var,
                                      width=15, state='readonly')
        rag_lang_combo['values'] = ['All', 'python', 'javascript', 'typescript', 'java', 'cpp', 'csharp']
        rag_lang_combo.pack(side='left', padx=10)
        
        ttk.Label(filter_frame, text="Top-K:").pack(side='left', padx=(20, 5))
        self.rag_topk_var = tk.IntVar(value=5)
        ttk.Spinbox(filter_frame, from_=1, to=20, textvariable=self.rag_topk_var, width=5).pack(side='left')
        
        # Results
        ttk.Label(query_frame, text="Results:").pack(anchor='w', pady=(10, 5))
        self.rag_results_text = scrolledtext.ScrolledText(query_frame, wrap='word',
                                                          font=('Consolas', 9), state='disabled')
        self.rag_results_text.pack(fill='both', expand=True)

    def initialize_components(self):
        """Initialize all components."""
        try:
            self.status_label.config(text="● Initializing...", foreground='orange')
            self.root.update()
            
            self.config = load_config_from_file()
            if not self.config:
                messagebox.showerror("Error", "Configuration not found")
                return
            
            self.db = LearningDB()
            self.engine = PromptEngine(learning_db=self.db)
            self.llm = LLMInterface(self.config)
            
            self.generator = CodeGenerator(self.llm, self.engine, self.db)
            self.debugger = Debugger(self.llm, self.engine, self.db)
            self.lang_support = LanguageSupport()
            
            # Populate languages
            languages = self.lang_support.get_supported_languages()
            self.language_combo['values'] = languages
            if languages:
                self.language_combo.current(0)
            
            self.status_label.config(text="● Ready", foreground='green')
            self.append_output("✓ All components initialized!\n")
            
            # Try to initialize RAG (optional)
            try:
                from features import RAG_AVAILABLE
                if RAG_AVAILABLE:
                    from features import RAGIndexer, RAGRetriever
                    self.rag_indexer = RAGIndexer()
                    self.rag_retriever = RAGRetriever(indexer=self.rag_indexer)
                    self.rag_available = True
                    self.rag_status_label.config(text="● Ready", foreground='green')
                    self.on_rag_list_collections()
                else:
                    self.rag_status_label.config(text="● Not installed", foreground='red')
            except Exception as e:
                self.rag_status_label.config(text=f"● Error: {e}", foreground='red')
            
        except Exception as e:
            messagebox.showerror("Error", f"Initialization failed: {e}")
            self.status_label.config(text="● Error", foreground='red')

    def on_browse_project(self):
        """Browse for project folder."""
        folder = filedialog.askdirectory(title="Select Project Folder")
        if folder:
            self.load_project(folder)

    def load_project(self, path):
        """Load project and initialize components."""
        try:
            self.status_label.config(text="● Loading project...", foreground='orange')
            self.root.update()
            
            # Initialize project manager
            if not self.project_manager:
                self.project_manager = ProjectManager(llm_interface=self.llm)
            
            if self.project_manager.set_root_folder(path):
                self.current_project = path
                self.project_path_var.set(path)
                
                # Index files
                stats = self.project_manager.index_files()
                
                # Initialize other components
                self.project_navigator = ProjectNavigator(self.project_manager, self.llm)
                self.context_manager = ContextManager(
                    self.project_manager, self.project_navigator, self.db, self.engine
                )
                self.task_manager = TaskManager(
                    self.llm, self.project_manager, self.project_navigator,
                    self.context_manager, self.generator, self.debugger, self.db
                )
                self.rule_enforcer = RuleEnforcer(self.db, self.project_manager, self.llm)
                self.tool_integrator = ToolIntegrator(
                    self.project_manager, self.llm, self.debugger, self.context_manager
                )
                
                # Update UI
                self.update_file_tree()
                self.update_project_stats()
                self.on_load_rules()
                
                self.status_label.config(text="● Project loaded", foreground='green')
                messagebox.showinfo("Success", f"Project loaded!\n{stats['total_files']} files indexed")
            else:
                messagebox.showerror("Error", "Invalid project path")
                self.status_label.config(text="● Error", foreground='red')
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project: {e}")
            self.status_label.config(text="● Error", foreground='red')

    def update_file_tree(self):
        """Update file tree display."""
        if not self.project_manager:
            return
        
        self.file_tree.delete(*self.file_tree.get_children())
        
        for path in sorted(self.project_manager.file_index.keys())[:100]:  # Limit to 100
            self.file_tree.insert('', 'end', text=path)

    def update_project_stats(self):
        """Update project statistics display."""
        if not self.project_manager:
            return
        
        stats = self.project_manager.get_project_stats()
        
        text = f"Files: {stats['total_files']}\n"
        text += f"Size: {stats['total_size'] / 1024:.1f} KB\n\n"
        text += "By Language:\n"
        for lang, count in sorted(stats['by_language'].items(), key=lambda x: -x[1])[:10]:
            text += f"  {lang}: {count}\n"
        
        self.stats_text.config(state='normal')
        self.stats_text.delete('1.0', 'end')
        self.stats_text.insert('1.0', text)
        self.stats_text.config(state='disabled')

    def on_scan_project(self):
        """Scan project for changes."""
        if not self.project_navigator:
            messagebox.showwarning("Warning", "No project loaded")
            return
        
        changes = self.project_navigator.scan_project(summarize_new=True)
        msg = f"New: {len(changes['new'])}\n"
        msg += f"Modified: {len(changes['modified'])}\n"
        msg += f"Deleted: {len(changes['deleted'])}"
        messagebox.showinfo("Scan Complete", msg)
        
        self.update_file_tree()
        self.update_project_stats()

    def on_search_files(self):
        """Search files in project."""
        if not self.project_navigator:
            messagebox.showwarning("Warning", "No project loaded")
            return
        
        query = self.search_var.get()
        if not query:
            return
        
        results = self.project_navigator.search_files(query, max_results=20)
        
        self.search_results.delete(0, 'end')
        for result in results:
            self.search_results.insert('end', f"[{result['score']:.2f}] {result['path']}")

    def on_decompose_task(self):
        """Decompose task into sub-tasks."""
        if not self.task_manager:
            messagebox.showwarning("Warning", "No project loaded")
            return
        
        desc = self.task_desc_var.get()
        if not desc:
            return
        
        self.status_label.config(text="● Decomposing...", foreground='orange')
        self.root.update()
        
        try:
            task = self.task_manager.decompose_task(
                user_task=desc,
                project_id=self.current_project
            )
            
            # Clear tree
            self.task_tree.delete(*self.task_tree.get_children())
            
            # Add sub-tasks
            for sub_task in task['sub_tasks']:
                self.task_tree.insert('', 'end',
                                     text=sub_task['description'],
                                     values=(sub_task['status'], sub_task['type']))
            
            self.status_label.config(text="● Ready", foreground='green')
            messagebox.showinfo("Success", f"Decomposed into {task['total_sub_tasks']} sub-tasks")
            
        except Exception as e:
            messagebox.showerror("Error", f"Decomposition failed: {e}")
            self.status_label.config(text="● Error", foreground='red')

    def on_execute_task(self):
        """Execute decomposed task."""
        messagebox.showinfo("Info", "Task execution not yet implemented in GUI")

    def on_git_status(self):
        """Show git status."""
        if not self.tool_integrator:
            messagebox.showwarning("Warning", "No project loaded")
            return
        
        status = self.tool_integrator.git_status()
        
        text = ""
        if status['initialized']:
            text += f"Branch: {status['branch']}\n"
            text += f"Changed: {len(status['changed_files'])}\n"
            text += f"Untracked: {len(status['untracked_files'])}\n"
        else:
            text = status['error']
        
        self.git_status_text.config(state='normal')
        self.git_status_text.delete('1.0', 'end')
        self.git_status_text.insert('1.0', text)
        self.git_status_text.config(state='disabled')

    def on_git_commit(self):
        """Commit changes."""
        if not self.tool_integrator:
            messagebox.showwarning("Warning", "No project loaded")
            return
        
        result = self.tool_integrator.git_commit(generate_message=True)
        
        if result['success']:
            messagebox.showinfo("Success", f"Committed!\n{result['message']}")
        else:
            messagebox.showerror("Error", result['error'])

    def on_run_tests(self):
        """Run tests."""
        self._run_tests(auto_fix=False)

    def on_run_tests_fix(self):
        """Run tests with auto-fix."""
        self._run_tests(auto_fix=True)

    def _run_tests(self, auto_fix):
        """Run tests implementation."""
        if not self.tool_integrator:
            messagebox.showwarning("Warning", "No project loaded")
            return
        
        self.status_label.config(text="● Running tests...", foreground='orange')
        self.root.update()
        
        try:
            result = self.tool_integrator.run_tests(auto_fix=auto_fix)
            
            text = f"Framework: {result['framework']}\n"
            text += f"Passed: {result['passed']}\n"
            text += f"Failed: {result['failed']}\n"
            if auto_fix and result['fix_attempts'] > 0:
                text += f"Fix attempts: {result['fix_attempts']}\n"
            
            self.test_output.config(state='normal')
            self.test_output.delete('1.0', 'end')
            self.test_output.insert('1.0', text)
            self.test_output.config(state='disabled')
            
            self.status_label.config(text="● Ready", foreground='green')
            
            if result['all_passed']:
                messagebox.showinfo("Success", "All tests passed!")
            else:
                messagebox.showwarning("Tests Failed", f"{result['failed']} tests failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Test execution failed: {e}")
            self.status_label.config(text="● Error", foreground='red')

    def on_add_rule(self):
        """Add new rule."""
        if not self.rule_enforcer:
            messagebox.showwarning("Warning", "No project loaded")
            return
        
        rule = self.new_rule_var.get()
        if not rule:
            return
        
        existing = self.rule_enforcer.get_rules(project_id=self.current_project)
        existing.append(rule)
        
        self.rule_enforcer.set_rules(existing, project_id=self.current_project)
        self.new_rule_var.set("")
        self.on_load_rules()
        messagebox.showinfo("Success", "Rule added!")

    def on_load_rules(self):
        """Load and display rules."""
        if not self.rule_enforcer:
            return
        
        rules = self.rule_enforcer.get_rules(project_id=self.current_project)
        
        self.rules_listbox.delete(0, 'end')
        for rule in rules:
            self.rules_listbox.insert('end', rule)

    def on_remove_rule(self):
        """Remove selected rule."""
        messagebox.showinfo("Info", "Rule removal not yet implemented")

    def on_mode_change(self):
        """Handle mode change."""
        if self.mode_var.get() == "generate":
            self.action_btn.config(text="Generate")
        else:
            self.action_btn.config(text="Debug")

    def on_code_action(self):
        """Handle code action (generate/debug)."""
        if self.mode_var.get() == "generate":
            self.on_generate_code()
        else:
            self.on_debug_code()

    def on_generate_code(self):
        """Generate code."""
        lang = self.language_var.get()
        task = self.input_text.get('1.0', 'end').strip()
        
        if not lang or not task:
            messagebox.showwarning("Warning", "Please provide language and task")
            return
        
        self.status_label.config(text="● Generating...", foreground='orange')
        self.root.update()
        
        try:
            result = self.generator.generate_code(task=task, language=lang)
            
            self.output_text.config(state='normal')
            self.output_text.delete('1.0', 'end')
            self.output_text.insert('1.0', result['code'] + "\n\n")
            if result['explanation']:
                self.output_text.insert('end', result['explanation'])
            self.output_text.config(state='disabled')
            
            self.status_label.config(text="● Ready", foreground='green')
            
        except Exception as e:
            messagebox.showerror("Error", f"Generation failed: {e}")
            self.status_label.config(text="● Error", foreground='red')

    def on_debug_code(self):
        """Debug code."""
        lang = self.language_var.get()
        code = self.input_text.get('1.0', 'end').strip()
        
        if not lang or not code:
            messagebox.showwarning("Warning", "Please provide language and code")
            return
        
        self.status_label.config(text="● Debugging...", foreground='orange')
        self.root.update()
        
        try:
            result = self.debugger.debug_code(code=code, language=lang)
            
            self.output_text.config(state='normal')
            self.output_text.delete('1.0', 'end')
            self.output_text.insert('1.0', result['fixed_code'] + "\n\n")
            if result['explanation']:
                self.output_text.insert('end', result['explanation'])
            self.output_text.config(state='disabled')
            
            self.status_label.config(text="● Ready", foreground='green')
            
        except Exception as e:
            messagebox.showerror("Error", f"Debugging failed: {e}")
            self.status_label.config(text="● Error", foreground='red')

    def on_clear_code(self):
        """Clear code input/output."""
        self.input_text.delete('1.0', 'end')
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', 'end')
        self.output_text.config(state='disabled')

    def append_output(self, text):
        """Append to output."""
        self.output_text.config(state='normal')
        self.output_text.insert('end', text)
        self.output_text.config(state='disabled')
    
    # RAG Handlers
    
    def on_rag_refresh_status(self):
        """Refresh RAG status."""
        if self.rag_available:
            self.rag_status_label.config(text="● Ready", foreground='green')
            self.on_rag_list_collections()
        else:
            self.rag_status_label.config(text="● Not available", foreground='red')
            messagebox.showinfo("RAG Not Available",
                              "Install RAG dependencies:\n"
                              "pip install sentence-transformers chromadb numpy")
    
    def on_rag_browse(self):
        """Browse for project to index."""
        folder = filedialog.askdirectory(title="Select Project to Index")
        if folder:
            self.rag_project_var.set(folder)
    
    def on_rag_index(self):
        """Index project with RAG."""
        if not self.rag_available:
            messagebox.showwarning("Warning", "RAG not available")
            return
        
        project_path = self.rag_project_var.get()
        if project_path == "No project selected":
            # Use current project if available
            if self.current_project:
                project_path = self.current_project
                self.rag_project_var.set(project_path)
            else:
                messagebox.showwarning("Warning", "No project selected")
                return
        
        self.rag_progress_var.set("Indexing... (this may take a few moments)")
        self.root.update()
        
        try:
            collection = self.rag_indexer.build_vector_db(project_path)
            
            # Get statistics
            stats = self.rag_retriever.get_statistics(collection_name=collection)
            
            self.rag_progress_var.set(f"Indexed! {stats['total_files']} files, {stats['total_chunks']} chunks")
            self.on_rag_list_collections()
            
            messagebox.showinfo("Success",
                              f"Project indexed successfully!\n"
                              f"Collection: {collection}\n"
                              f"Files: {stats['total_files']}\n"
                              f"Chunks: {stats['total_chunks']}")
        except Exception as e:
            self.rag_progress_var.set(f"Error: {e}")
            messagebox.showerror("Error", f"Indexing failed: {e}")
    
    def on_rag_rebuild(self):
        """Rebuild index."""
        if not self.rag_available:
            messagebox.showwarning("Warning", "RAG not available")
            return
        
        # Get selected collection
        selection = self.rag_collections_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "No collection selected")
            return
        
        collection = self.rag_collections_list.get(selection[0])
        
        if not messagebox.askyesno("Confirm", f"Rebuild index for {collection}?"):
            return
        
        self.rag_progress_var.set("Rebuilding...")
        self.root.update()
        
        try:
            # Get collection info to find project path
            info = self.rag_indexer.get_collection_info(collection)
            if 'metadata' in info and 'root_folder' in info['metadata']:
                project_path = info['metadata']['root_folder']
                
                # Rebuild
                collection = self.rag_indexer.build_vector_db(
                    root_folder=project_path,
                    project_name=collection,
                    force_rebuild=True
                )
                
                self.rag_progress_var.set("Rebuild complete!")
                self.on_rag_list_collections()
                messagebox.showinfo("Success", "Index rebuilt successfully!")
            else:
                messagebox.showerror("Error", "Cannot determine project path")
        except Exception as e:
            self.rag_progress_var.set(f"Error: {e}")
            messagebox.showerror("Error", f"Rebuild failed: {e}")
    
    def on_rag_list_collections(self):
        """List all indexed collections."""
        if not self.rag_available:
            return
        
        try:
            collections = self.rag_indexer.list_collections()
            
            self.rag_collections_list.delete(0, 'end')
            for coll in collections:
                self.rag_collections_list.insert('end', coll)
            
            if not collections:
                self.rag_stats_text.config(state='normal')
                self.rag_stats_text.delete('1.0', 'end')
                self.rag_stats_text.insert('1.0', "No collections indexed yet.")
                self.rag_stats_text.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list collections: {e}")
    
    def on_rag_collection_select(self, event):
        """Handle collection selection."""
        if not self.rag_available:
            return
        
        selection = self.rag_collections_list.curselection()
        if not selection:
            return
        
        collection = self.rag_collections_list.get(selection[0])
        
        try:
            # Get statistics
            stats = self.rag_retriever.get_statistics(collection_name=collection)
            
            text = f"Collection: {stats['collection_name']}\n"
            text += f"Total files: {stats['total_files']}\n"
            text += f"Total chunks: {stats['total_chunks']}\n"
            text += f"Languages: {', '.join(list(stats['languages'].keys())[:5])}\n"
            
            self.rag_stats_text.config(state='normal')
            self.rag_stats_text.delete('1.0', 'end')
            self.rag_stats_text.insert('1.0', text)
            self.rag_stats_text.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get statistics: {e}")
    
    def on_rag_query(self):
        """Perform semantic search."""
        if not self.rag_available:
            messagebox.showwarning("Warning", "RAG not available")
            return
        
        query = self.rag_query_var.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a query")
            return
        
        # Get selected collection or use first available
        selection = self.rag_collections_list.curselection()
        if selection:
            collection = self.rag_collections_list.get(selection[0])
        else:
            collections = self.rag_indexer.list_collections()
            if not collections:
                messagebox.showwarning("Warning", "No collections indexed")
                return
            collection = collections[0]
        
        self.rag_progress_var.set("Searching...")
        self.root.update()
        
        try:
            # Get filters
            top_k = self.rag_topk_var.get()
            lang_filter = self.rag_lang_filter_var.get()
            if lang_filter == "All":
                lang_filter = None
            
            # Search
            results = self.rag_retriever.retrieve(
                query=query,
                collection_name=collection,
                top_k=top_k,
                threshold=0.7,
                language_filter=lang_filter
            )
            
            # Display results
            self.rag_results_text.config(state='normal')
            self.rag_results_text.delete('1.0', 'end')
            
            if results:
                self.rag_results_text.insert('1.0', f"Found {len(results)} relevant code chunks:\n\n")
                
                for i, result in enumerate(results, 1):
                    text = f"[{i}] {result['file_path']}\n"
                    if result.get('start_line'):
                        text += f"    Lines: {result['start_line']}-{result['end_line']}\n"
                    text += f"    Relevance: {result['score']:.2%}\n"
                    text += f"    Language: {result['language']}\n"
                    text += f"    Content:\n{result['content'][:300]}...\n\n"
                    
                    self.rag_results_text.insert('end', text)
            else:
                self.rag_results_text.insert('1.0', "No relevant results found.\n" +
                                                   "Try a different query or lower the threshold.")
            
            self.rag_results_text.config(state='disabled')
            self.rag_progress_var.set(f"Found {len(results)} results")
            
        except Exception as e:
            self.rag_progress_var.set(f"Error: {e}")
            messagebox.showerror("Error", f"Search failed: {e}")


def main():
    """Entry point."""
    root = tk.Tk()
    app = EnhancedGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
