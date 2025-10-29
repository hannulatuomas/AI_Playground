"""
Code Analysis Tab

Dead code detection and analysis interface.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path

from .base import BaseTab, LabeledEntry, OutputPanel, run_async


class CodeAnalysisTab(BaseTab):
    """Code analysis and dead code detection tab."""
    
    def setup_ui(self):
        """Setup code analysis UI."""
        # Controls
        control_frame = ttk.LabelFrame(self, text="Analysis Settings", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.project_path = LabeledEntry(control_frame, "Project Path:", width=50)
        self.project_path.pack(fill=tk.X, pady=5)
        self.project_path.set(".")
        
        ttk.Button(
            control_frame,
            text="Analyze Project",
            command=self.analyze_project,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Results notebook
        results_notebook = ttk.Notebook(self)
        results_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create result tabs
        self.unused_funcs_frame = self.create_unused_functions_tab()
        self.unused_classes_frame = self.create_unused_classes_tab()
        self.unreachable_frame = self.create_unreachable_code_tab()
        self.orphaned_frame = self.create_orphaned_files_tab()
        
        results_notebook.add(self.unused_funcs_frame, text="Unused Functions")
        results_notebook.add(self.unused_classes_frame, text="Unused Classes")
        results_notebook.add(self.unreachable_frame, text="Unreachable Code")
        results_notebook.add(self.orphaned_frame, text="Orphaned Files")
        
        # Summary
        summary_frame = ttk.LabelFrame(self, text="Analysis Summary", padding=10)
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.summary_text = tk.Text(summary_frame, height=4, wrap=tk.WORD)
        self.summary_text.pack(fill=tk.X)
        
        # Output
        output_frame = ttk.LabelFrame(self, text="Analysis Log", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.output = OutputPanel(output_frame, height=8)
        self.output.pack(fill=tk.BOTH, expand=True)
    
    def create_unused_functions_tab(self):
        """Create unused functions tab."""
        frame = ttk.Frame(self)
        
        # Treeview
        columns = ("Function", "File", "Reason")
        self.unused_funcs_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        self.unused_funcs_tree.heading("Function", text="Function Name")
        self.unused_funcs_tree.heading("File", text="File")
        self.unused_funcs_tree.heading("Reason", text="Reason")
        
        self.unused_funcs_tree.column("Function", width=200)
        self.unused_funcs_tree.column("File", width=300)
        self.unused_funcs_tree.column("Reason", width=300)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.unused_funcs_tree.yview)
        self.unused_funcs_tree.configure(yscrollcommand=scrollbar.set)
        
        self.unused_funcs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return frame
    
    def create_unused_classes_tab(self):
        """Create unused classes tab."""
        frame = ttk.Frame(self)
        
        # Treeview
        columns = ("Class", "File")
        self.unused_classes_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        self.unused_classes_tree.heading("Class", text="Class Name")
        self.unused_classes_tree.heading("File", text="File")
        
        self.unused_classes_tree.column("Class", width=250)
        self.unused_classes_tree.column("File", width=450)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.unused_classes_tree.yview)
        self.unused_classes_tree.configure(yscrollcommand=scrollbar.set)
        
        self.unused_classes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return frame
    
    def create_unreachable_code_tab(self):
        """Create unreachable code tab."""
        frame = ttk.Frame(self)
        
        # Treeview
        columns = ("File", "Line", "Function", "Reason")
        self.unreachable_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        self.unreachable_tree.heading("File", text="File")
        self.unreachable_tree.heading("Line", text="Line")
        self.unreachable_tree.heading("Function", text="Function")
        self.unreachable_tree.heading("Reason", text="Reason")
        
        self.unreachable_tree.column("File", width=250)
        self.unreachable_tree.column("Line", width=60)
        self.unreachable_tree.column("Function", width=150)
        self.unreachable_tree.column("Reason", width=300)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.unreachable_tree.yview)
        self.unreachable_tree.configure(yscrollcommand=scrollbar.set)
        
        self.unreachable_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return frame
    
    def create_orphaned_files_tab(self):
        """Create orphaned files tab."""
        frame = ttk.Frame(self)
        
        # Listbox
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.orphaned_list = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=('TkDefaultFont', 10))
        self.orphaned_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.orphaned_list.yview)
        
        return frame
    
    @run_async
    def analyze_project(self):
        """Analyze project for dead code."""
        try:
            self.output.clear()
            self.output.write("Analyzing project for dead code...\n", 'info')
            
            project_path = self.project_path.get()
            result = self.orchestrator.detect_dead_code(project_path)
            
            # Clear all trees
            for item in self.unused_funcs_tree.get_children():
                self.unused_funcs_tree.delete(item)
            for item in self.unused_classes_tree.get_children():
                self.unused_classes_tree.delete(item)
            for item in self.unreachable_tree.get_children():
                self.unreachable_tree.delete(item)
            self.orphaned_list.delete(0, tk.END)
            
            if result.success:
                data = result.data
                self.output.write(f"✓ {result.message}\n", 'success')
                
                # Populate unused functions
                unused_funcs = data.get('unused_functions', [])
                for item in unused_funcs[:50]:  # Limit to 50
                    self.unused_funcs_tree.insert('', tk.END, values=(
                        item['name'],
                        item['file'],
                        item.get('reason', 'Not called anywhere')
                    ))
                
                # Populate unused classes
                unused_classes = data.get('unused_classes', [])
                for item in unused_classes[:50]:
                    self.unused_classes_tree.insert('', tk.END, values=(
                        item['name'],
                        item['file']
                    ))
                
                # Populate unreachable code
                unreachable = data.get('unreachable_code', [])
                for item in unreachable[:50]:
                    self.unreachable_tree.insert('', tk.END, values=(
                        item['file'],
                        item['line'],
                        item.get('function', 'N/A'),
                        item.get('reason', 'After return statement')
                    ))
                
                # Populate orphaned files
                orphaned = data.get('orphaned_files', [])
                for item in orphaned[:50]:
                    self.orphaned_list.insert(tk.END, item['file'])
                
                # Update summary
                self.summary_text.delete('1.0', tk.END)
                self.summary_text.insert('1.0', f"Unused Functions: {len(unused_funcs)}\n")
                self.summary_text.insert(tk.END, f"Unused Classes: {len(unused_classes)}\n")
                self.summary_text.insert(tk.END, f"Unreachable Code: {len(unreachable)}\n")
                self.summary_text.insert(tk.END, f"Orphaned Files: {len(orphaned)}\n")
                
                total = len(unused_funcs) + len(unused_classes) + len(unreachable) + len(orphaned)
                self.output.write(f"\nTotal dead code items: {total}\n", 'info')
            else:
                self.output.write(f"Error: {result.message}\n", 'error')
        
        except Exception as e:
            self.output.write(f"Error: {e}\n", 'error')
