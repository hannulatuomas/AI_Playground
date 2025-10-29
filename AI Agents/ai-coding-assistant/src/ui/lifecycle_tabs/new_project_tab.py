"""
New Project Tab - Template-based project creation

Handles:
- Template selection and preview
- Project configuration
- Git initialization
- Virtual environment creation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
import threading


class NewProjectTab:
    """New Project creation interface."""
    
    def __init__(self, parent, template_manager, project_initializer):
        """
        Initialize New Project tab.
        
        Args:
            parent: Parent widget
            template_manager: TemplateManager instance
            project_initializer: ProjectInitializer instance
        """
        self.parent = parent
        self.template_manager = template_manager
        self.project_initializer = project_initializer
        
        # Variables
        self.template_var = tk.StringVar()
        self.proj_name_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.license_var = tk.StringVar(value="MIT")
        self.dest_var = tk.StringVar()
        self.git_var = tk.BooleanVar(value=True)
        self.install_var = tk.BooleanVar(value=False)
        self.venv_var = tk.BooleanVar(value=False)
        
        self.create_widgets()
        self.refresh_templates()
    
    def create_widgets(self):
        """Create all widgets for new project tab."""
        # Scrollable frame
        canvas = tk.Canvas(self.parent)
        scroll = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        # Configuration section
        config = ttk.LabelFrame(frame, text="Configuration", padding="15")
        config.pack(fill='x', padx=10, pady=10)
        config.columnconfigure(1, weight=1)
        
        row = 0
        # Template
        ttk.Label(config, text="Template:").grid(row=row, column=0, sticky='w', pady=5)
        self.template_combo = ttk.Combobox(config, textvariable=self.template_var, 
                                          state='readonly', width=30)
        self.template_combo.grid(row=row, column=1, sticky='ew', pady=5, padx=(5, 0))
        self.template_combo.bind('<<ComboboxSelected>>', self.on_template_selected)
        ttk.Button(config, text="↻", command=self.refresh_templates, width=3).grid(
            row=row, column=2, padx=(5, 0))
        
        row += 1
        self.template_desc = ttk.Label(config, text="Select template...", 
                                       foreground='gray', wraplength=600)
        self.template_desc.grid(row=row, column=0, columnspan=3, sticky='w', pady=(0, 10))
        
        row += 1
        # Project name
        ttk.Label(config, text="Name:*").grid(row=row, column=0, sticky='w', pady=5)
        ttk.Entry(config, textvariable=self.proj_name_var).grid(
            row=row, column=1, columnspan=2, sticky='ew', pady=5, padx=(5, 0))
        
        row += 1
        # Author
        ttk.Label(config, text="Author:").grid(row=row, column=0, sticky='w', pady=5)
        ttk.Entry(config, textvariable=self.author_var).grid(
            row=row, column=1, columnspan=2, sticky='ew', pady=5, padx=(5, 0))
        
        row += 1
        # Email
        ttk.Label(config, text="Email:").grid(row=row, column=0, sticky='w', pady=5)
        ttk.Entry(config, textvariable=self.email_var).grid(
            row=row, column=1, columnspan=2, sticky='ew', pady=5, padx=(5, 0))
        
        row += 1
        # Description
        ttk.Label(config, text="Description:").grid(row=row, column=0, sticky='nw', pady=5)
        self.desc_text = tk.Text(config, height=3, width=40, font=('Arial', 9))
        self.desc_text.grid(row=row, column=1, columnspan=2, sticky='ew', pady=5, padx=(5, 0))
        
        row += 1
        # License
        ttk.Label(config, text="License:").grid(row=row, column=0, sticky='w', pady=5)
        ttk.Combobox(config, textvariable=self.license_var, 
                    values=['MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', 'None'],
                    state='readonly', width=20).grid(row=row, column=1, sticky='w', 
                                                    pady=5, padx=(5, 0))
        
        row += 1
        # Destination
        ttk.Label(config, text="Destination:*").grid(row=row, column=0, sticky='w', pady=5)
        dest_frame = ttk.Frame(config)
        dest_frame.grid(row=row, column=1, columnspan=2, sticky='ew', pady=5, padx=(5, 0))
        dest_frame.columnconfigure(0, weight=1)
        ttk.Entry(dest_frame, textvariable=self.dest_var).grid(row=0, column=0, sticky='ew')
        ttk.Button(dest_frame, text="Browse", command=self.browse_dest, 
                  width=10).grid(row=0, column=1, padx=(5, 0))
        
        # Options
        opts = ttk.LabelFrame(frame, text="Options", padding="15")
        opts.pack(fill='x', padx=10, pady=10)
        
        ttk.Checkbutton(opts, text="Initialize Git repository", 
                       variable=self.git_var).pack(anchor='w', pady=2)
        ttk.Checkbutton(opts, text="Install dependencies", 
                       variable=self.install_var).pack(anchor='w', pady=2)
        ttk.Checkbutton(opts, text="Create virtual environment", 
                       variable=self.venv_var).pack(anchor='w', pady=2)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Create Project", command=self.create_project, 
                  width=20).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_form, 
                  width=15).pack(side='left', padx=5)
        
        # Progress
        self.progress = ttk.Progressbar(frame, mode='indeterminate', length=700)
        self.progress.pack(padx=10, pady=5)
        self.progress.pack_forget()
        
        self.status = ttk.Label(frame, text="", foreground='blue')
        self.status.pack()
        
        # Log
        log_frame = ttk.LabelFrame(frame, text="Log", padding="10")
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.log = scrolledtext.ScrolledText(log_frame, height=8, wrap='word', 
                                             font=('Consolas', 9), state='disabled')
        self.log.pack(fill='both', expand=True)
    
    def refresh_templates(self):
        """Refresh template list."""
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
    
    def clear_form(self):
        """Clear form."""
        self.proj_name_var.set("")
        self.author_var.set("")
        self.email_var.set("")
        self.desc_text.delete('1.0', 'end')
        self.dest_var.set("")
        self.log.config(state='normal')
        self.log.delete('1.0', 'end')
        self.log.config(state='disabled')
        self.status.config(text="")
    
    def log_message(self, msg):
        """Log message."""
        self.log.config(state='normal')
        self.log.insert('end', msg + '\n')
        self.log.see('end')
        self.log.config(state='disabled')
        self.parent.update()
    
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
        
        self.progress.pack()
        self.progress.start()
        self.status.config(text="Creating project...")
        self.log_message(f"Creating: {name}")
        self.log_message(f"Template: {template}")
        
        def create_thread():
            try:
                success, msg = self.template_manager.create_from_template(
                    template, dest_path, config)
                
                if success:
                    self.log_message("✓ Project created!")
                    
                    if self.git_var.get():
                        self.log_message("Initializing Git...")
                        s, m = self.project_initializer.initialize_git(
                            dest_path, initial_message=f"Initial: {name}", 
                            add_gitignore=True)
                        self.log_message("✓ Git initialized" if s else f"⚠ Git: {m}")
                    
                    if self.venv_var.get():
                        self.log_message("Creating virtual environment...")
                        s, m = self.project_initializer.create_virtual_env(
                            dest_path, env_type='venv')
                        self.log_message("✓ Venv created" if s else f"⚠ Venv: {m}")
                    
                    self.parent.after(0, lambda: self.status.config(
                        text="✓ Success!", foreground='green'))
                    self.parent.after(0, lambda: messagebox.showinfo(
                        "Success", f"Created at:\n{dest_path}"))
                else:
                    self.log_message(f"✗ Failed: {msg}")
                    self.parent.after(0, lambda: self.status.config(
                        text="✗ Failed", foreground='red'))
                    self.parent.after(0, lambda: messagebox.showerror("Error", msg))
                    
            except Exception as e:
                self.log_message(f"✗ Error: {e}")
                self.parent.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.parent.after(0, self.progress.stop)
                self.parent.after(0, self.progress.pack_forget)
        
        threading.Thread(target=create_thread, daemon=True).start()
