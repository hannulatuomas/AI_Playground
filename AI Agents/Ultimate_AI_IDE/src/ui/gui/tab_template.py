"""
Template Validation Tab

Template validation and cleanliness checking interface.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path

from .base import BaseTab, LabeledEntry, OutputPanel, run_async


class TemplateTab(BaseTab):
    """Template validation tab."""
    
    def setup_ui(self):
        """Setup template validation UI."""
        # Controls
        control_frame = ttk.LabelFrame(self, text="Validation Settings", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.project_path = LabeledEntry(control_frame, "Project Path:", width=50)
        self.project_path.pack(fill=tk.X, pady=5)
        self.project_path.set(".")
        
        # Options
        options_frame = ttk.Frame(control_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        self.strict_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Strict Mode (fail on any issues)",
            variable=self.strict_var
        ).pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame,
            text="Validate Project",
            command=self.validate_project,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Get Score",
            command=self.get_score
        ).pack(side=tk.LEFT, padx=5)
        
        # Dashboard
        dashboard_frame = ttk.LabelFrame(self, text="Validation Dashboard", padding=10)
        dashboard_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Score display
        score_frame = ttk.Frame(dashboard_frame)
        score_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(score_frame, text="Cleanliness Score:", font=('TkDefaultFont', 12, 'bold')).pack(side=tk.LEFT, padx=5)
        self.score_label = ttk.Label(score_frame, text="--/100", font=('TkDefaultFont', 16, 'bold'))
        self.score_label.pack(side=tk.LEFT, padx=5)
        
        self.score_progress = ttk.Progressbar(score_frame, length=200, mode='determinate')
        self.score_progress.pack(side=tk.LEFT, padx=10)
        
        # Summary grid
        summary_frame = ttk.Frame(dashboard_frame)
        summary_frame.pack(fill=tk.X, pady=10)
        
        # Issue types
        ttk.Label(summary_frame, text="Example Code:", font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.example_label = ttk.Label(summary_frame, text="0")
        self.example_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(summary_frame, text="TODOs/FIXMEs:", font=('TkDefaultFont', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.todo_label = ttk.Label(summary_frame, text="0")
        self.todo_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(summary_frame, text="Placeholders:", font=('TkDefaultFont', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, padx=5)
        self.placeholder_label = ttk.Label(summary_frame, text="0")
        self.placeholder_label.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(summary_frame, text="Unused Deps:", font=('TkDefaultFont', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, padx=5)
        self.deps_label = ttk.Label(summary_frame, text="0")
        self.deps_label.grid(row=3, column=1, sticky=tk.W, padx=5)
        
        # Severity
        ttk.Label(summary_frame, text="High:", font=('TkDefaultFont', 10)).grid(row=0, column=2, sticky=tk.W, padx=20)
        self.high_label = ttk.Label(summary_frame, text="0", foreground="red")
        self.high_label.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(summary_frame, text="Medium:", font=('TkDefaultFont', 10)).grid(row=1, column=2, sticky=tk.W, padx=20)
        self.medium_label = ttk.Label(summary_frame, text="0", foreground="orange")
        self.medium_label.grid(row=1, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(summary_frame, text="Low:", font=('TkDefaultFont', 10)).grid(row=2, column=2, sticky=tk.W, padx=20)
        self.low_label = ttk.Label(summary_frame, text="0")
        self.low_label.grid(row=2, column=3, sticky=tk.W, padx=5)
        
        # Issues list
        issues_frame = ttk.LabelFrame(self, text="Validation Issues", padding=10)
        issues_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for issues
        columns = ("Type", "Severity", "File", "Line", "Description")
        self.issues_tree = ttk.Treeview(issues_frame, columns=columns, show="headings", height=10)
        
        self.issues_tree.heading("Type", text="Type")
        self.issues_tree.heading("Severity", text="Severity")
        self.issues_tree.heading("File", text="File")
        self.issues_tree.heading("Line", text="Line")
        self.issues_tree.heading("Description", text="Description")
        
        self.issues_tree.column("Type", width=120)
        self.issues_tree.column("Severity", width=80)
        self.issues_tree.column("File", width=200)
        self.issues_tree.column("Line", width=60)
        self.issues_tree.column("Description", width=300)
        
        scrollbar = ttk.Scrollbar(issues_frame, orient=tk.VERTICAL, command=self.issues_tree.yview)
        self.issues_tree.configure(yscrollcommand=scrollbar.set)
        
        self.issues_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure tags
        self.issues_tree.tag_configure('high', foreground='darkred', font=('TkDefaultFont', 9, 'bold'))
        self.issues_tree.tag_configure('medium', foreground='orange')
        self.issues_tree.tag_configure('low', foreground='gray')
        
        # Output
        output_frame = ttk.LabelFrame(self, text="Validation Log", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.output = OutputPanel(output_frame, height=6)
        self.output.pack(fill=tk.BOTH, expand=True)
    
    @run_async
    def validate_project(self):
        """Validate project for bloat and incomplete code."""
        try:
            self.output.clear()
            self.output.write("🔍 Validating project...\n", 'info')
            
            project_path = self.project_path.get()
            
            from ...modules.template_validator import TemplateValidator
            validator = TemplateValidator(project_path)
            result = validator.validate_project()
            
            # Update dashboard
            score = validator.get_clean_score()
            self.score_label.config(text=f"{score:.1f}/100")
            self.score_progress['value'] = score
            
            # Update summary
            summary = result['summary']
            self.example_label.config(text=str(summary['example_code']))
            self.todo_label.config(text=str(summary['todo']))
            self.placeholder_label.config(text=str(summary['placeholder']))
            self.deps_label.config(text=str(summary['unused_dependency']))
            
            self.high_label.config(text=str(summary['high']))
            self.medium_label.config(text=str(summary['medium']))
            self.low_label.config(text=str(summary['low']))
            
            # Populate issues tree
            self.populate_issues(result['issues'])
            
            # Log results
            if result['is_clean']:
                self.output.write("\n✓ Project is clean! No issues found.\n", 'success')
            else:
                self.output.write(f"\n⚠️  Found {result['total_issues']} issues\n", 'warning')
                self.output.write(f"Cleanliness Score: {score:.1f}/100\n", 'info')
                
                if summary['high'] > 0:
                    self.output.write(f"⚠️  {summary['high']} high severity issues!\n", 'error')
        
        except Exception as e:
            self.output.write(f"\nError: {e}\n", 'error')
    
    @run_async
    def get_score(self):
        """Get cleanliness score only."""
        try:
            self.output.clear()
            self.output.write("📊 Calculating cleanliness score...\n", 'info')
            
            project_path = self.project_path.get()
            
            from ...modules.template_validator import TemplateValidator
            validator = TemplateValidator(project_path)
            result = validator.validate_project()
            score = validator.get_clean_score()
            
            self.score_label.config(text=f"{score:.1f}/100")
            self.score_progress['value'] = score
            
            if score == 100:
                self.output.write("\n🎉 Perfect! Project is completely clean.\n", 'success')
            elif score >= 80:
                self.output.write("\n✓ Good! Minor issues found.\n", 'success')
            elif score >= 60:
                self.output.write("\n⚠️  Fair. Some cleanup needed.\n", 'warning')
            else:
                self.output.write("\n✗ Poor. Significant cleanup required.\n", 'error')
            
            self.output.write(f"\nTotal Issues: {result['total_issues']}\n", 'info')
        
        except Exception as e:
            self.output.write(f"\nError: {e}\n", 'error')
    
    def populate_issues(self, issues):
        """Populate issues tree."""
        # Clear tree
        for item in self.issues_tree.get_children():
            self.issues_tree.delete(item)
        
        # Add issues
        for issue in issues:
            self.issues_tree.insert('', tk.END, values=(
                issue.issue_type,
                issue.severity,
                Path(issue.file_path).name,
                issue.line_number,
                issue.description[:60]
            ), tags=(issue.severity,))
