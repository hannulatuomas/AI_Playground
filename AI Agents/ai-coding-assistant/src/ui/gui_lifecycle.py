"""
Enhanced GUI with Project Lifecycle Management - Part 1: Base + New Project

Complete implementation featuring Phase 10 components.
This file contains the base GUI and New Project section.
"""

import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
import threading
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import LLMInterface, PromptEngine, LearningDB, load_config_from_file
from features import CodeGenerator, Debugger, LanguageSupport

try:
    from features.project_lifecycle import (
        TemplateManager, ProjectScaffolder, ProjectInitializer,
        ProjectMaintainer, ProjectArchiver
    )
    LIFECYCLE_AVAILABLE = True
except ImportError:
    LIFECYCLE_AVAILABLE = False


class ProjectLifecycleGUI:
    """Enhanced GUI with Project Lifecycle Management."""

    def __init__(self, root):
        self.root = root
        self.root.title("AI Coding Assistant - Project Lifecycle")
        self.root.geometry("1100x800")
        
        # Components
        self.config = None
        self.llm = None
        self.db = None
        self.engine = None
        self.generator = None
        self.debugger = None
        self.lang_support = None
        self.template_manager = None
        self.project_scaffolder = None
        self.project_initializer = None
        self.project_maintainer = None
        self.project_archiver = None
        self.current_project_path = None
        
        self.create_widgets()
        self.initialize_components()

    def create_widgets(self):
        """Create all widgets."""
        main = ttk.Frame(self.root, padding="10")
        main.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)
        
        # Header
        header = ttk.Frame(main)
        header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Label(header, text="🤖 AI Coding Assistant", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        self.status_label = ttk.Label(header, text="● Initializing...", foreground='orange')
        self.status_label.pack(side=tk.RIGHT)
        
        # Notebook
        self.notebook = ttk.Notebook(main)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.code_tab = ttk.Frame(self.notebook)
        self.project_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.code_tab, text="💻 Code")
        self.notebook.add(self.project_tab, text="🏗️ Project Lifecycle")
        
        self.create_code_tab()
        self.create_project_tab()

    def create_code_tab(self):
        """Create code tab."""
        frame = ttk.LabelFrame(self.code_tab, text="Quick Code Generation", padding="20")
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        lang_frame = ttk.Frame(frame)
        lang_frame.pack(fill='x', pady=5)
        ttk.Label(lang_frame, text="Language:").pack(side='left')
        self.language_var = tk.StringVar()
        self.language_combo = ttk.Combobox(lang_frame, textvariable=self.language_var, width=20, state='readonly')
        self.language_combo.pack(side='left', padx=10)
        
        ttk.Label(frame, text="Task:").pack(anchor='w', pady=(10, 5))
        self.input_text = scrolledtext.ScrolledText(frame, height=6, wrap='word', font=('Consolas', 10))
        self.input_text.pack(fill='both', expand=True, pady=5)
        
        ttk.Button(frame, text="Generate Code", command=self.generate_code, width=20).pack(pady=10)
        
        ttk.Label(frame, text="Output:").pack(anchor='w', pady=(10, 5))
        self.output_text = scrolledtext.ScrolledText(frame, height=10, wrap='word', font=('Consolas', 10), state='disabled')
        self.output_text.pack(fill='both', expand=True)

    def create_project_tab(self):
        """Create project lifecycle tab."""
        if not LIFECYCLE_AVAILABLE:
            ttk.Label(self.project_tab, text="⚠️ Project Lifecycle not installed", 
                     font=('Arial', 14, 'bold'), foreground='red').pack(pady=50)
            return
        
        sub = ttk.Notebook(self.project_tab)
        sub.pack(fill='both', expand=True, padx=10, pady=10)
        
        new_frame = ttk.Frame(sub)
        maint_frame = ttk.Frame(sub)
        archive_frame = ttk.Frame(sub)
        
        sub.add(new_frame, text="📝 New Project")
        sub.add(maint_frame, text="🔧 Maintenance")
        sub.add(archive_frame, text="📦 Archiving")
        
        self.create_new_project_section(new_frame)
        self.create_maintenance_section(maint_frame)
        self.create_archiving_section(archive_frame)

    def create_new_project_section(self, parent):
        """Create new project section with scrolling."""
        canvas = tk.Canvas(parent)
        scroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        # Config
        config = ttk.LabelFrame(frame, text="Configuration", padding="15")
        config.pack(fill='x', padx=10, pady=10)
        config.columnconfigure(1, weight=1)
        
        row = 0
        ttk.Label(config, text="Template:").grid(row=row, column=0, sticky='w', pady=5)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(config, textvariable=self.template_var, state='readonly', width=30)
        self.template_combo.grid(row=row, column=1, sticky='ew', pady=5, padx=(5, 0))
        self.template_combo.bind('<<ComboboxSelected>>', self.on_template_selected)
        ttk.Button(config, text="↻", command=self.refresh_templates, width=3).grid(row=row, column=2, padx=(5, 0))
        
        row += 1
        self.template_desc = ttk.Label(config, text="Select template...", foreground='gray', wraplength=600)
        self.template_desc.grid(row=row, column=0, columnspan=3, sticky='w', pady=(0, 10))
        
        row += 1
        ttk.Label(config, text="Name:*").grid(row=row, column=0, sticky='w', pady=5)
        self.proj_name_var = tk.StringVar()
        ttk.Entry(config, textvariable=self.proj_name_var).grid(row=row, column=1, columnspan=2, sticky='ew', pady=5, padx=(5, 0))
        
        row += 1
        ttk.Label(config, text="Author:").grid(row=row, column=0, sticky='w', pady=5)
        self.author_var = tk.StringVar()
        ttk.Entry(config, textvariable=self.author_var).grid(row=row, column=1, columnspan=2, sticky='ew', pady=5, padx=(5, 0))
        
        row += 1
        ttk.Label(config, text="Email:").grid(row=row, column=0, sticky='w', pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(config, textvariable=self.email_var).grid(row=row, column=1, columnspan=2, sticky='ew', pady=5, padx=(5, 0))
        
        row += 1
        ttk.Label(config, text="Description:").grid(row=row, column=0, sticky='nw', pady=5)
        self.desc_text = tk.Text(config, height=3, width=40, font=('Arial', 9))
        self.desc_text.grid(row=row, column=1, columnspan=2, sticky='ew', pady=5, padx=(5, 0))
        
        row += 1
        ttk.Label(config, text="License:").grid(row=row, column=0, sticky='w', pady=5)
        self.license_var = tk.StringVar(value="MIT")
        ttk.Combobox(config, textvariable=self.license_var, 
                    values=['MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', 'None'],
                    state='readonly', width=20).grid(row=row, column=1, sticky='w', pady=5, padx=(5, 0))
        
        row += 1
        ttk.Label(config, text="Destination:*").grid(row=row, column=0, sticky='w', pady=5)
        dest_frame = ttk.Frame(config)
        dest_frame.grid(row=row, column=1, columnspan=2, sticky='ew', pady=5, padx=(5, 0))
        dest_frame.columnconfigure(0, weight=1)
        self.dest_var = tk.StringVar()
        ttk.Entry(dest_frame, textvariable=self.dest_var).grid(row=0, column=0, sticky='ew')
        ttk.Button(dest_frame, text="Browse", command=self.browse_dest, width=10).grid(row=0, column=1, padx=(5, 0))
        
        # Options
        opts = ttk.LabelFrame(frame, text="Options", padding="15")
        opts.pack(fill='x', padx=10, pady=10)
        
        self.git_var = tk.BooleanVar(value=True)
        self.install_var = tk.BooleanVar(value=False)
        self.venv_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(opts, text="Initialize Git repository", variable=self.git_var).pack(anchor='w', pady=2)
        ttk.Checkbutton(opts, text="Install dependencies", variable=self.install_var).pack(anchor='w', pady=2)
        ttk.Checkbutton(opts, text="Create virtual environment", variable=self.venv_var).pack(anchor='w', pady=2)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Create Project", command=self.create_project, width=20).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_project_form, width=15).pack(side='left', padx=5)
        
        # Progress
        self.proj_progress = ttk.Progressbar(frame, mode='indeterminate', length=700)
        self.proj_progress.pack(padx=10, pady=5)
        self.proj_progress.pack_forget()
        
        self.proj_status = ttk.Label(frame, text="", foreground='blue')
        self.proj_status.pack()
        
        # Log
        log_frame = ttk.LabelFrame(frame, text="Log", padding="10")
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.proj_log = scrolledtext.ScrolledText(log_frame, height=8, wrap='word', font=('Consolas', 9), state='disabled')
        self.proj_log.pack(fill='both', expand=True)

    def create_maintenance_section(self, parent):
        """Placeholder for maintenance section."""
        ttk.Label(parent, text="Maintenance section - To be implemented", 
                 font=('Arial', 12)).pack(pady=50)

    def create_archiving_section(self, parent):
        """Placeholder for archiving section."""
        ttk.Label(parent, text="Archiving section - To be implemented", 
                 font=('Arial', 12)).pack(pady=50)

    def initialize_components(self):
        """Initialize components."""
        try:
            self.status_label.config(text="● Initializing...", foreground='orange')
            self.root.update()
            
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
            
            langs = self.lang_support.get_supported_languages()
            self.language_combo['values'] = langs
            if langs:
                self.language_combo.current(0)
            
            if LIFECYCLE_AVAILABLE:
                self.template_manager = TemplateManager()
                self.project_scaffolder = ProjectScaffolder()
                self.project_initializer = ProjectInitializer()
                self.project_maintainer = ProjectMaintainer()
                self.project_archiver = ProjectArchiver()
                self.refresh_templates()
            
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

    def refresh_templates(self):
        """Refresh template list."""
        if not self.template_manager:
            return
        
        try:
            templates = self.template_manager.list_templates()
            names = [t['name'] for t in templates]
            self.template_combo['values'] = names
            if names:
                self.template_combo.current(0)
                self.on_template_selected(None)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load templates: {e}")
    
    def on_template_selected(self, event):
        """Handle template selection."""
        name = self.template_var.get()
        if not name:
            return
        
        try:
            template = self.template_manager.get_template(name)
            if template:
                desc = template.get('description', 'No description')
                version = template.get('version', 'N/A')
                self.template_desc.config(text=f"{desc} (v{version})")
        except Exception as e:
            self.template_desc.config(text=f"Error: {e}")
    
    def browse_dest(self):
        """Browse for destination."""
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_var.set(folder)
    
    def clear_project_form(self):
        """Clear project form."""
        self.proj_name_var.set("")
        self.author_var.set("")
        self.email_var.set("")
        self.desc_text.delete('1.0', 'end')
        self.dest_var.set("")
        self.proj_log.config(state='normal')
        self.proj_log.delete('1.0', 'end')
        self.proj_log.config(state='disabled')
        self.proj_status.config(text="")
    
    def log_project(self, msg):
        """Log to project log."""
        self.proj_log.config(state='normal')
        self.proj_log.insert('end', msg + '\n')
        self.proj_log.see('end')
        self.proj_log.config(state='disabled')
        self.root.update()
    
    def create_project(self):
        """Create new project."""
        template = self.template_var.get()
        name = self.proj_name_var.get()
        dest = self.dest_var.get()
        
        if not template:
            messagebox.showwarning("Warning", "Select a template")
            return
        if not name:
            messagebox.showwarning("Warning", "Enter project name")
            return
        if not dest:
            messagebox.showwarning("Warning", "Select destination")
            return
        
        config = {
            'PROJECT_NAME': name,
            'AUTHOR': self.author_var.get() or 'Developer',
            'EMAIL': self.email_var.get() or '',
            'DESCRIPTION': self.desc_text.get('1.0', 'end').strip() or 'A new project',
            'LICENSE': self.license_var.get()
        }
        
        dest_path = Path(dest) / name
        
        self.proj_progress.pack()
        self.proj_progress.start()
        self.proj_status.config(text="Creating project...")
        self.log_project(f"Creating: {name}")
        self.log_project(f"Template: {template}")
        
        def create_thread():
            try:
                success, msg = self.template_manager.create_from_template(template, dest_path, config)
                
                if success:
                    self.log_project("✓ Project created!")
                    
                    if self.git_var.get():
                        self.log_project("Initializing Git...")
                        s, m = self.project_initializer.initialize_git(dest_path, initial_message=f"Initial: {name}", add_gitignore=True)
                        self.log_project("✓ Git initialized" if s else f"⚠ Git failed: {m}")
                    
                    if self.venv_var.get():
                        self.log_project("Creating virtual environment...")
                        s, m = self.project_initializer.create_virtual_env(dest_path, env_type='venv')
                        self.log_project("✓ Venv created" if s else f"⚠ Venv failed: {m}")
                    
                    self.root.after(0, lambda: self.proj_status.config(text="✓ Success!", foreground='green'))
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"Created at:\n{dest_path}"))
                else:
                    self.log_project(f"✗ Failed: {msg}")
                    self.root.after(0, lambda: self.proj_status.config(text="✗ Failed", foreground='red'))
                    self.root.after(0, lambda: messagebox.showerror("Error", msg))
                    
            except Exception as e:
                self.log_project(f"✗ Error: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.root.after(0, self.proj_progress.stop)
                self.root.after(0, self.proj_progress.pack_forget)
        
        threading.Thread(target=create_thread, daemon=True).start()


def main():
    root = tk.Tk()
    app = ProjectLifecycleGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
