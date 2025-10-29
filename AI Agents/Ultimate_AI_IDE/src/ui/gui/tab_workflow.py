"""
Workflow Tab

Workflow management and execution interface.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path

from .base import BaseTab, LabeledEntry, OutputPanel, run_async


class WorkflowTab(BaseTab):
    """Workflow management tab."""
    
    def setup_ui(self):
        """Setup workflow UI."""
        # Main container with two panes
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left pane: Template list
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Right pane: Execution
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        self.create_template_list(left_frame)
        self.create_execution_panel(right_frame)
    
    def create_template_list(self, parent):
        """Create workflow template list."""
        ttk.Label(parent, text="Workflow Templates", font=('TkDefaultFont', 12, 'bold')).pack(pady=5)
        
        # Template listbox
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.template_list = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=('TkDefaultFont', 10)
        )
        self.template_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.template_list.yview)
        
        self.template_list.bind('<<ListboxSelect>>', self.on_template_select)
        
        # Load templates button
        ttk.Button(
            parent,
            text="Refresh Templates",
            command=self.load_templates
        ).pack(pady=5)
        
        # Template info
        info_frame = ttk.LabelFrame(parent, text="Template Info", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.template_info = scrolledtext.ScrolledText(info_frame, height=10, wrap=tk.WORD)
        self.template_info.pack(fill=tk.BOTH, expand=True)
        
        # Load templates on init
        self.load_templates()
    
    def create_execution_panel(self, parent):
        """Create workflow execution panel."""
        ttk.Label(parent, text="Execute Workflow", font=('TkDefaultFont', 12, 'bold')).pack(pady=5)
        
        # Settings
        settings_frame = ttk.LabelFrame(parent, text="Workflow Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.project_path = LabeledEntry(settings_frame, "Project Path:", width=40)
        self.project_path.pack(fill=tk.X, pady=5)
        self.project_path.set(".")
        
        # Variables
        var_frame = ttk.LabelFrame(settings_frame, text="Variables (key=value)", padding=5)
        var_frame.pack(fill=tk.X, pady=5)
        
        self.variables_text = tk.Text(var_frame, height=4, wrap=tk.WORD)
        self.variables_text.pack(fill=tk.X)
        self.variables_text.insert('1.0', "feature_name=My Feature\nlanguage=python")
        
        # Execute button
        ttk.Button(
            settings_frame,
            text="Execute Workflow",
            command=self.execute_workflow,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Progress
        progress_frame = ttk.LabelFrame(parent, text="Execution Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack()
        
        # Output
        output_frame = ttk.LabelFrame(parent, text="Execution Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.output = OutputPanel(output_frame, height=15)
        self.output.pack(fill=tk.BOTH, expand=True)
    
    @run_async
    def load_templates(self):
        """Load workflow templates."""
        try:
            from ...modules.workflow_engine import WorkflowTemplates
            
            self.template_list.delete(0, tk.END)
            templates = WorkflowTemplates.list_templates()
            
            for name in templates.keys():
                self.template_list.insert(tk.END, name)
            
            self.output.write(f"Loaded {len(templates)} workflow templates\n")
        except Exception as e:
            self.output.write(f"Error loading templates: {e}\n", 'error')
    
    def on_template_select(self, event):
        """Handle template selection."""
        selection = self.template_list.curselection()
        if not selection:
            return
        
        template_name = self.template_list.get(selection[0])
        self.show_template_info(template_name)
    
    @run_async
    def show_template_info(self, template_name):
        """Show template information."""
        try:
            from ...modules.workflow_engine import WorkflowTemplates
            
            template = WorkflowTemplates.get_template(template_name)
            
            self.template_info.delete('1.0', tk.END)
            self.template_info.insert('1.0', f"Name: {template['name']}\n")
            self.template_info.insert(tk.END, f"Description: {template.get('description', 'N/A')}\n")
            self.template_info.insert(tk.END, f"Version: {template.get('version', '1.0')}\n")
            self.template_info.insert(tk.END, f"Steps: {len(template['steps'])}\n\n")
            
            self.template_info.insert(tk.END, "Workflow Steps:\n")
            for i, step in enumerate(template['steps'], 1):
                self.template_info.insert(tk.END, f"  {i}. {step['name']}\n")
                self.template_info.insert(tk.END, f"     Action: {step['action']}\n")
                if step.get('depends_on'):
                    deps = step['depends_on'] if isinstance(step['depends_on'], list) else [step['depends_on']]
                    self.template_info.insert(tk.END, f"     Depends on: {', '.join(deps)}\n")
        except Exception as e:
            self.template_info.delete('1.0', tk.END)
            self.template_info.insert('1.0', f"Error: {e}")
    
    @run_async
    def execute_workflow(self):
        """Execute selected workflow."""
        selection = self.template_list.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a workflow template")
            return
        
        template_name = self.template_list.get(selection[0])
        
        try:
            self.progress_bar.start()
            self.status_label.config(text=f"Executing {template_name}...")
            self.output.clear()
            self.output.write(f"Starting workflow: {template_name}\n", 'info')
            
            # Parse variables
            variables = {'project_path': self.project_path.get()}
            var_text = self.variables_text.get('1.0', tk.END).strip()
            for line in var_text.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    variables[key.strip()] = value.strip()
            
            # Execute workflow
            result = self.orchestrator.execute_workflow(template_name, variables)
            
            self.progress_bar.stop()
            
            if result.success:
                self.status_label.config(text="✓ Completed")
                self.output.write(f"\n✓ {result.message}\n", 'success')
                if result.data:
                    steps = result.data.get('steps', {})
                    self.output.write(f"Completed {len(steps)} steps\n", 'info')
            else:
                self.status_label.config(text="✗ Failed")
                self.output.write(f"\n✗ {result.message}\n", 'error')
                if result.errors:
                    for error in result.errors:
                        self.output.write(f"  - {error}\n", 'error')
        
        except Exception as e:
            self.progress_bar.stop()
            self.status_label.config(text="✗ Error")
            self.output.write(f"\nError: {e}\n", 'error')
    
    def browse_project(self):
        """Browse for project directory."""
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Select Project Directory")
        if path:
            self.project_path.set(path)
