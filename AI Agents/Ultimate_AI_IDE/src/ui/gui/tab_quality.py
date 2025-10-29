"""
Quality Tab

Code quality monitoring and reporting with real-time analysis.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path

from .base import BaseTab, LabeledEntry, OutputPanel, run_async


class QualityTab(BaseTab):
    """Code quality monitoring tab."""
    
    def setup_ui(self):
        """Setup quality UI."""
        # Create notebook for sub-tabs
        sub_notebook = ttk.Notebook(self)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sub-tabs
        self.monitor_frame = self.create_monitor_tab()
        self.report_frame = self.create_report_tab()
        self.refactor_frame = self.create_refactor_tab()
        
        sub_notebook.add(self.monitor_frame, text="Monitor")
        sub_notebook.add(self.report_frame, text="Report")
        sub_notebook.add(self.refactor_frame, text="Refactoring")
    
    def create_monitor_tab(self):
        """Create quality monitoring tab."""
        frame = ttk.Frame(self)
        
        # Controls
        control_frame = ttk.LabelFrame(frame, text="Monitor Settings", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.project_path = LabeledEntry(control_frame, "Project Path:", width=50)
        self.project_path.pack(fill=tk.X, pady=5)
        self.project_path.set(".")
        
        ttk.Button(
            control_frame,
            text="Browse...",
            command=self.browse_project
        ).pack(pady=5)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame,
            text="Check Quality",
            command=self.check_quality,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="Monitor Project",
            command=self.monitor_project
        ).pack(side=tk.LEFT, padx=2)
        
        # Issues list
        issues_frame = ttk.LabelFrame(frame, text="Quality Issues", padding=10)
        issues_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for issues
        columns = ("Severity", "Type", "File", "Line", "Message")
        self.issues_tree = ttk.Treeview(issues_frame, columns=columns, show="headings", height=15)
        
        self.issues_tree.heading("Severity", text="Severity")
        self.issues_tree.heading("Type", text="Type")
        self.issues_tree.heading("File", text="File")
        self.issues_tree.heading("Line", text="Line")
        self.issues_tree.heading("Message", text="Message")
        
        self.issues_tree.column("Severity", width=80)
        self.issues_tree.column("Type", width=120)
        self.issues_tree.column("File", width=200)
        self.issues_tree.column("Line", width=60)
        self.issues_tree.column("Message", width=400)
        
        scrollbar = ttk.Scrollbar(issues_frame, orient=tk.VERTICAL, command=self.issues_tree.yview)
        self.issues_tree.configure(yscrollcommand=scrollbar.set)
        
        self.issues_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure tags for severity colors
        self.issues_tree.tag_configure('low', foreground='gray')
        self.issues_tree.tag_configure('medium', foreground='orange')
        self.issues_tree.tag_configure('high', foreground='red')
        self.issues_tree.tag_configure('critical', foreground='darkred', font=('TkDefaultFont', 9, 'bold'))
        
        # Output
        output_frame = ttk.LabelFrame(frame, text="Details", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.monitor_output = OutputPanel(output_frame, height=8)
        self.monitor_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def create_report_tab(self):
        """Create quality report tab."""
        frame = ttk.Frame(self)
        
        # Controls
        control_frame = ttk.LabelFrame(frame, text="Report Settings", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            control_frame,
            text="Generate Report",
            command=self.generate_report,
            style="Accent.TButton"
        ).pack(pady=5)
        
        # Report display
        report_frame = ttk.LabelFrame(frame, text="Quality Report", padding=10)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Score display
        score_frame = ttk.Frame(report_frame)
        score_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(score_frame, text="Quality Score:", font=('TkDefaultFont', 12, 'bold')).pack(side=tk.LEFT, padx=5)
        self.score_label = ttk.Label(score_frame, text="--/100", font=('TkDefaultFont', 16, 'bold'))
        self.score_label.pack(side=tk.LEFT, padx=5)
        
        # Progress bar for score
        self.score_progress = ttk.Progressbar(score_frame, length=200, mode='determinate')
        self.score_progress.pack(side=tk.LEFT, padx=10)
        
        # Report text
        self.report_text = scrolledtext.ScrolledText(report_frame, height=20, wrap=tk.WORD)
        self.report_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        return frame
    
    def create_refactor_tab(self):
        """Create refactoring suggestions tab."""
        frame = ttk.Frame(self)
        
        # Controls
        control_frame = ttk.LabelFrame(frame, text="Refactoring Analysis", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            control_frame,
            text="Analyze Files",
            command=self.analyze_refactoring,
            style="Accent.TButton"
        ).pack(pady=5)
        
        # Files needing refactoring
        files_frame = ttk.LabelFrame(frame, text="Files Needing Refactoring", padding=10)
        files_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for files
        columns = ("File", "Reasons", "Priority")
        self.refactor_tree = ttk.Treeview(files_frame, columns=columns, show="headings", height=10)
        
        self.refactor_tree.heading("File", text="File")
        self.refactor_tree.heading("Reasons", text="Reasons")
        self.refactor_tree.heading("Priority", text="Priority")
        
        self.refactor_tree.column("File", width=300)
        self.refactor_tree.column("Reasons", width=400)
        self.refactor_tree.column("Priority", width=100)
        
        scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.refactor_tree.yview)
        self.refactor_tree.configure(yscrollcommand=scrollbar.set)
        
        self.refactor_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Suggestions
        suggestions_frame = ttk.LabelFrame(frame, text="Refactoring Suggestions", padding=10)
        suggestions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.suggestions_text = scrolledtext.ScrolledText(suggestions_frame, height=10, wrap=tk.WORD)
        self.suggestions_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection to show suggestions
        self.refactor_tree.bind("<<TreeviewSelect>>", self.on_refactor_file_selected)
        
        return frame
    
    def browse_project(self):
        """Browse for project directory."""
        from tkinter import filedialog
        directory = filedialog.askdirectory(title="Select Project Directory")
        if directory:
            self.project_path.set(directory)
    
    def check_quality(self):
        """Check code quality for project."""
        project = self.project_path.get().strip()
        if not project:
            self.show_error("Validation Error", "Please specify a project path")
            return
        
        self.monitor_output.clear()
        self.monitor_output.append("Checking code quality...")
        
        # Clear existing issues
        for item in self.issues_tree.get_children():
            self.issues_tree.delete(item)
        
        def check():
            from ...modules.quality_monitor import QualityMonitor
            monitor = QualityMonitor(project)
            return monitor.monitor_project()
        
        def callback(result, error=None):
            if error:
                self.monitor_output.append(f"\n❌ Error: {error}")
                self.show_error("Check Failed", error)
                return
            
            total_issues = sum(len(issues) for issues in result.values())
            self.monitor_output.append(f"\n✅ Found {total_issues} issues in {len(result)} files")
            
            # Display issues
            for file_path, issues in result.items():
                for issue in issues:
                    self.issues_tree.insert("", tk.END, values=(
                        issue.severity.upper(),
                        issue.type,
                        file_path,
                        issue.line_number or "-",
                        issue.message
                    ), tags=(issue.severity,))
        
        run_async(check, callback)
    
    def monitor_project(self):
        """Monitor project continuously."""
        self.check_quality()
        # Could add auto-refresh here
    
    def generate_report(self):
        """Generate quality report."""
        project = self.project_path.get().strip() or "."
        
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert("1.0", "Generating quality report...\n")
        
        def generate():
            from ...modules.quality_monitor import QualityMonitor
            monitor = QualityMonitor(project)
            return monitor.get_project_quality_report()
        
        def callback(result, error=None):
            if error:
                self.report_text.delete("1.0", tk.END)
                self.report_text.insert("1.0", f"Error: {error}")
                self.show_error("Report Failed", error)
                return
            
            # Update score
            score = result['quality_score']
            self.score_label.config(text=f"{score}/100")
            self.score_progress['value'] = score
            
            # Color code the score
            if score >= 80:
                self.score_label.config(foreground='green')
            elif score >= 60:
                self.score_label.config(foreground='orange')
            else:
                self.score_label.config(foreground='red')
            
            # Generate report text
            report_lines = [
                "=== PROJECT QUALITY REPORT ===\n",
                f"\nQuality Score: {score}/100\n",
                f"Files with Issues: {result['total_files_with_issues']}",
                f"Total Issues: {result['total_issues']}\n",
                "\nIssues by Severity:",
            ]
            
            for severity, count in result['severity_breakdown'].items():
                if count > 0:
                    report_lines.append(f"  {severity.capitalize()}: {count}")
            
            if result['files_needing_refactoring']:
                report_lines.append(f"\n\nFiles Needing Refactoring: {len(result['files_needing_refactoring'])}")
                for item in result['files_needing_refactoring'][:10]:
                    report_lines.append(f"\n📄 {item['file']}")
                    for reason in item['reasons']:
                        report_lines.append(f"   • {reason}")
            
            self.report_text.delete("1.0", tk.END)
            self.report_text.insert("1.0", "\n".join(report_lines))
        
        run_async(generate, callback)
    
    def analyze_refactoring(self):
        """Analyze files needing refactoring."""
        project = self.project_path.get().strip() or "."
        
        # Clear existing items
        for item in self.refactor_tree.get_children():
            self.refactor_tree.delete(item)
        
        self.suggestions_text.delete("1.0", tk.END)
        self.suggestions_text.insert("1.0", "Analyzing files for refactoring needs...\n")
        
        def analyze():
            from ...modules.quality_monitor import QualityMonitor
            monitor = QualityMonitor(project)
            report = monitor.get_project_quality_report()
            return report['files_needing_refactoring']
        
        def callback(result, error=None):
            if error:
                self.suggestions_text.delete("1.0", tk.END)
                self.suggestions_text.insert("1.0", f"Error: {error}")
                return
            
            if not result:
                self.suggestions_text.delete("1.0", tk.END)
                self.suggestions_text.insert("1.0", "✅ No files need refactoring!")
                return
            
            for item in result:
                reasons_text = "; ".join(item['reasons'][:2])
                if len(item['reasons']) > 2:
                    reasons_text += f" (+{len(item['reasons']) - 2} more)"
                
                priority = "High" if len(item['reasons']) > 2 else "Medium"
                
                self.refactor_tree.insert("", tk.END, values=(
                    item['file'],
                    reasons_text,
                    priority
                ))
            
            self.suggestions_text.delete("1.0", tk.END)
            self.suggestions_text.insert("1.0", f"Found {len(result)} files needing refactoring.\n\nSelect a file to see suggestions.")
        
        run_async(analyze, callback)
    
    def on_refactor_file_selected(self, event):
        """Handle refactor file selection."""
        selection = self.refactor_tree.selection()
        if not selection:
            return
        
        item = self.refactor_tree.item(selection[0])
        file_path = item['values'][0]
        
        self.suggestions_text.delete("1.0", tk.END)
        self.suggestions_text.insert("1.0", f"Generating suggestions for {file_path}...\n")
        
        def get_suggestions():
            from ...modules.quality_monitor import QualityMonitor
            from pathlib import Path
            
            project = self.project_path.get().strip() or "."
            monitor = QualityMonitor(project)
            
            full_path = Path(project) / file_path
            return monitor.generate_refactoring_suggestions(full_path)
        
        def callback(result, error=None):
            if error:
                self.suggestions_text.delete("1.0", tk.END)
                self.suggestions_text.insert("1.0", f"Error: {error}")
                return
            
            if not result:
                self.suggestions_text.delete("1.0", tk.END)
                self.suggestions_text.insert("1.0", "No specific suggestions available.")
                return
            
            suggestions_lines = [f"=== Refactoring Suggestions for {file_path} ===\n"]
            
            for i, suggestion in enumerate(result, 1):
                suggestions_lines.append(f"\n{i}. [{suggestion['priority'].upper()}] {suggestion['type']}")
                suggestions_lines.append(f"   {suggestion['description']}")
                suggestions_lines.append(f"   → {suggestion['suggestion']}")
                if 'line' in suggestion:
                    suggestions_lines.append(f"   Line: {suggestion['line']}")
            
            self.suggestions_text.delete("1.0", tk.END)
            self.suggestions_text.insert("1.0", "\n".join(suggestions_lines))
        
        run_async(get_suggestions, callback)
