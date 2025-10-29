"""
Project Lifecycle GUI - Modular Version

Clean, maintainable GUI using separate tab modules.
Each tab is in its own file for better organization.

Usage:
    python -m src.ui.gui_lifecycle_modular
"""

import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import LLMInterface, PromptEngine, LearningDB, load_config_from_file
from features import CodeGenerator, Debugger, LanguageSupport

# Import project lifecycle components
try:
    from features.project_lifecycle import (
        TemplateManager, ProjectScaffolder, ProjectInitializer,
        ProjectMaintainer, ProjectArchiver
    )
    LIFECYCLE_AVAILABLE = True
except ImportError:
    LIFECYCLE_AVAILABLE = False

# Import tab modules
if LIFECYCLE_AVAILABLE:
    from ui.lifecycle_tabs import NewProjectTab, MaintenanceTab, ArchivingTab


class ProjectLifecycleGUI:
    """Modular GUI with Project Lifecycle Management."""

    def __init__(self, root):
        """Initialize GUI."""
        self.root = root
        self.root.title("AI Coding Assistant - Project Lifecycle")
        self.root.geometry("1100x800")
        
        # Core components
        self.config = None
        self.llm = None
        self.db = None
        self.engine = None
        self.generator = None
        self.debugger = None
        self.lang_support = None
        
        # Lifecycle components
        self.template_manager = None
        self.project_initializer = None
        self.project_maintainer = None
        self.project_archiver = None
        
        # Tab instances
        self.new_project_tab = None
        self.maintenance_tab = None
        self.archiving_tab = None
        
        self.create_widgets()
        self.initialize_components()

    def create_widgets(self):
        """Create main GUI structure."""
        main = ttk.Frame(self.root, padding="10")
        main.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)
        
        # Header
        self.create_header(main)
        
        # Notebook
        self.notebook = ttk.Notebook(main)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.code_tab = ttk.Frame(self.notebook)
        self.project_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.code_tab, text="💻 Code")
        self.notebook.add(self.project_tab, text="🏗️ Project Lifecycle")
        
        self.create_code_tab()
        self.create_project_lifecycle_tab()

    def create_header(self, parent):
        """Create header with title and status."""
        header = ttk.Frame(parent)
        header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(header, text="🤖 AI Coding Assistant", 
                 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(header, text="● Initializing...", foreground='orange')
        self.status_label.pack(side=tk.RIGHT)

    def create_code_tab(self):
        """Create simplified code generation tab."""
        frame = ttk.LabelFrame(self.code_tab, text="Quick Code Generation", padding="20")
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Language
        lang_frame = ttk.Frame(frame)
        lang_frame.pack(fill='x', pady=5)
        ttk.Label(lang_frame, text="Language:").pack(side='left')
        self.language_var = tk.StringVar()
        self.language_combo = ttk.Combobox(lang_frame, textvariable=self.language_var, 
                                          width=20, state='readonly')
        self.language_combo.pack(side='left', padx=10)
        
        # Task
        ttk.Label(frame, text="Task:").pack(anchor='w', pady=(10, 5))
        self.input_text = scrolledtext.ScrolledText(frame, height=6, wrap='word', 
                                                    font=('Consolas', 10))
        self.input_text.pack(fill='both', expand=True, pady=5)
        
        # Button
        ttk.Button(frame, text="Generate Code", command=self.generate_code, 
                  width=20).pack(pady=10)
        
        # Output
        ttk.Label(frame, text="Output:").pack(anchor='w', pady=(10, 5))
        self.output_text = scrolledtext.ScrolledText(frame, height=10, wrap='word', 
                                                     font=('Consolas', 10), state='disabled')
        self.output_text.pack(fill='both', expand=True)

    def create_project_lifecycle_tab(self):
        """Create project lifecycle tab with sub-tabs."""
        if not LIFECYCLE_AVAILABLE:
            ttk.Label(self.project_tab, text="⚠️ Project Lifecycle not installed", 
                     font=('Arial', 14, 'bold'), foreground='red').pack(pady=50)
            return
        
        # Sub-notebook for lifecycle sections
        sub_notebook = ttk.Notebook(self.project_tab)
        sub_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create frames for each tab
        new_project_frame = ttk.Frame(sub_notebook)
        maintenance_frame = ttk.Frame(sub_notebook)
        archiving_frame = ttk.Frame(sub_notebook)
        
        sub_notebook.add(new_project_frame, text="📝 New Project")
        sub_notebook.add(maintenance_frame, text="🔧 Maintenance")
        sub_notebook.add(archiving_frame, text="📦 Archiving")
        
        # Initialize tab modules (will be done after components are ready)
        self.new_project_frame = new_project_frame
        self.maintenance_frame = maintenance_frame
        self.archiving_frame = archiving_frame

    def initialize_components(self):
        """Initialize all components."""
        try:
            self.status_label.config(text="● Initializing...", foreground='orange')
            self.root.update()
            
            # Core components
            self.config = load_config_from_file()
            if not self.config:
                messagebox.showerror("Error", "Config not found. Run: python main.py --setup")
                self.status_label.config(text="● Error", foreground='red')
                return
            
            self.db = LearningDB()
            self.engine = PromptEngine(learning_db=self.db)
            self.llm = LLMInterface(self.config)
            self.generator = CodeGenerator(self.llm, self.engine, self.db)
            self.debugger = Debugger(self.llm, self.engine, self.db)
            self.lang_support = LanguageSupport()
            
            # Populate languages
            langs = self.lang_support.get_supported_languages()
            self.language_combo['values'] = langs
            if langs:
                self.language_combo.current(0)
            
            # Lifecycle components
            if LIFECYCLE_AVAILABLE:
                self.template_manager = TemplateManager()
                self.project_initializer = ProjectInitializer()
                self.project_maintainer = ProjectMaintainer()
                self.project_archiver = ProjectArchiver()
                
                # Initialize tab modules
                self.new_project_tab = NewProjectTab(
                    self.new_project_frame, 
                    self.template_manager, 
                    self.project_initializer
                )
                
                self.maintenance_tab = MaintenanceTab(
                    self.maintenance_frame,
                    self.project_maintainer
                )
                
                self.archiving_tab = ArchivingTab(
                    self.archiving_frame,
                    self.project_archiver
                )
            
            self.status_label.config(text="● Ready", foreground='green')
            
        except Exception as e:
            messagebox.showerror("Error", f"Init failed: {e}")
            self.status_label.config(text="● Error", foreground='red')

    def generate_code(self):
        """Generate code."""
        lang = self.language_var.get()
        task = self.input_text.get('1.0', 'end').strip()
        
        if not lang or not task:
            messagebox.showwarning("Warning", "Enter language and task")
            return
        
        self.status_label.config(text="● Generating...", foreground='orange')
        self.root.update()
        
        try:
            result = self.generator.generate_code(task=task, language=lang)
            
            self.output_text.config(state='normal')
            self.output_text.delete('1.0', 'end')
            self.output_text.insert('1.0', result['code'] + '\n\n')
            if result.get('explanation'):
                self.output_text.insert('end', result['explanation'])
            self.output_text.config(state='disabled')
            
            self.status_label.config(text="● Ready", foreground='green')
            
        except Exception as e:
            messagebox.showerror("Error", f"Generation failed: {e}")
            self.status_label.config(text="● Error", foreground='red')


def main():
    """Entry point."""
    root = tk.Tk()
    app = ProjectLifecycleGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
