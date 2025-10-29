"""
Security Tab

Security scanning and vulnerability management interface.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path

from .base import BaseTab, LabeledEntry, OutputPanel, run_async


class SecurityTab(BaseTab):
    """Security scanning and vulnerability management tab."""
    
    def setup_ui(self):
        """Setup security UI."""
        # Create notebook for sub-tabs
        sub_notebook = ttk.Notebook(self)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sub-tabs
        self.scan_frame = self.create_scan_tab()
        self.vulnerabilities_frame = self.create_vulnerabilities_tab()
        self.secrets_frame = self.create_secrets_tab()
        self.patterns_frame = self.create_patterns_tab()
        
        sub_notebook.add(self.scan_frame, text="Security Scan")
        sub_notebook.add(self.vulnerabilities_frame, text="Vulnerabilities")
        sub_notebook.add(self.secrets_frame, text="Secrets")
        sub_notebook.add(self.patterns_frame, text="Patterns")
    
    def create_scan_tab(self):
        """Create security scan tab."""
        frame = ttk.Frame(self)
        
        # Controls
        control_frame = ttk.LabelFrame(frame, text="Scan Settings", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.project_path = LabeledEntry(control_frame, "Project Path:", width=50)
        self.project_path.pack(fill=tk.X, pady=5)
        self.project_path.set(".")
        
        ttk.Button(
            control_frame,
            text="Browse...",
            command=self.browse_project
        ).pack(pady=5)
        
        # Scan options
        options_frame = ttk.Frame(control_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        self.scan_vulnerabilities_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Scan Vulnerabilities",
            variable=self.scan_vulnerabilities_var
        ).pack(anchor=tk.W)
        
        self.scan_dependencies_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Check Dependencies",
            variable=self.scan_dependencies_var
        ).pack(anchor=tk.W)
        
        self.scan_patterns_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Detect Insecure Patterns",
            variable=self.scan_patterns_var
        ).pack(anchor=tk.W)
        
        self.scan_secrets_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Scan for Secrets",
            variable=self.scan_secrets_var
        ).pack(anchor=tk.W)
        
        # Scan button
        ttk.Button(
            control_frame,
            text="Run Security Scan",
            command=self.run_scan,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Dashboard
        dashboard_frame = ttk.LabelFrame(frame, text="Security Dashboard", padding=10)
        dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Risk score
        score_frame = ttk.Frame(dashboard_frame)
        score_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(score_frame, text="Risk Score:", font=('TkDefaultFont', 12, 'bold')).pack(side=tk.LEFT, padx=5)
        self.risk_score_label = ttk.Label(score_frame, text="--/100", font=('TkDefaultFont', 16, 'bold'))
        self.risk_score_label.pack(side=tk.LEFT, padx=5)
        
        self.risk_progress = ttk.Progressbar(score_frame, length=200, mode='determinate')
        self.risk_progress.pack(side=tk.LEFT, padx=10)
        
        # Summary grid
        summary_frame = ttk.Frame(dashboard_frame)
        summary_frame.pack(fill=tk.X, pady=10)
        
        # Critical
        ttk.Label(summary_frame, text="Critical:", font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.critical_label = ttk.Label(summary_frame, text="0", foreground="red", font=('TkDefaultFont', 12, 'bold'))
        self.critical_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # High
        ttk.Label(summary_frame, text="High:", font=('TkDefaultFont', 10)).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.high_label = ttk.Label(summary_frame, text="0", foreground="orange")
        self.high_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Medium
        ttk.Label(summary_frame, text="Medium:", font=('TkDefaultFont', 10)).grid(row=2, column=0, sticky=tk.W, padx=5)
        self.medium_label = ttk.Label(summary_frame, text="0")
        self.medium_label.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Low
        ttk.Label(summary_frame, text="Low:", font=('TkDefaultFont', 10)).grid(row=3, column=0, sticky=tk.W, padx=5)
        self.low_label = ttk.Label(summary_frame, text="0", foreground="gray")
        self.low_label.grid(row=3, column=1, sticky=tk.W, padx=5)
        
        # By category
        ttk.Label(summary_frame, text="Vulnerabilities:", font=('TkDefaultFont', 10)).grid(row=0, column=2, sticky=tk.W, padx=20)
        self.vuln_label = ttk.Label(summary_frame, text="0")
        self.vuln_label.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(summary_frame, text="Dependencies:", font=('TkDefaultFont', 10)).grid(row=1, column=2, sticky=tk.W, padx=20)
        self.deps_label = ttk.Label(summary_frame, text="0")
        self.deps_label.grid(row=1, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(summary_frame, text="Patterns:", font=('TkDefaultFont', 10)).grid(row=2, column=2, sticky=tk.W, padx=20)
        self.patterns_label = ttk.Label(summary_frame, text="0")
        self.patterns_label.grid(row=2, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(summary_frame, text="Secrets:", font=('TkDefaultFont', 10)).grid(row=3, column=2, sticky=tk.W, padx=20)
        self.secrets_label = ttk.Label(summary_frame, text="0")
        self.secrets_label.grid(row=3, column=3, sticky=tk.W, padx=5)
        
        # Output
        output_frame = ttk.LabelFrame(frame, text="Scan Log", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.scan_output = OutputPanel(output_frame, height=8)
        self.scan_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def create_vulnerabilities_tab(self):
        """Create vulnerabilities tab."""
        frame = ttk.Frame(self)
        
        # Treeview for vulnerabilities
        columns = ("Severity", "Package", "CVE", "CVSS", "Description")
        self.vuln_tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
        
        self.vuln_tree.heading("Severity", text="Severity")
        self.vuln_tree.heading("Package", text="Package")
        self.vuln_tree.heading("CVE", text="CVE ID")
        self.vuln_tree.heading("CVSS", text="CVSS")
        self.vuln_tree.heading("Description", text="Description")
        
        self.vuln_tree.column("Severity", width=80)
        self.vuln_tree.column("Package", width=150)
        self.vuln_tree.column("CVE", width=120)
        self.vuln_tree.column("CVSS", width=60)
        self.vuln_tree.column("Description", width=400)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.vuln_tree.yview)
        self.vuln_tree.configure(yscrollcommand=scrollbar.set)
        
        self.vuln_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure tags for severity colors
        self.vuln_tree.tag_configure('critical', foreground='darkred', font=('TkDefaultFont', 9, 'bold'))
        self.vuln_tree.tag_configure('high', foreground='red')
        self.vuln_tree.tag_configure('medium', foreground='orange')
        self.vuln_tree.tag_configure('low', foreground='gray')
        
        return frame
    
    def create_secrets_tab(self):
        """Create secrets tab."""
        frame = ttk.Frame(self)
        
        # Warning label
        warning_frame = ttk.Frame(frame)
        warning_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(
            warning_frame,
            text="⚠️ CRITICAL: Rotate all exposed credentials immediately!",
            foreground="red",
            font=('TkDefaultFont', 10, 'bold')
        ).pack()
        
        # Treeview for secrets
        columns = ("Type", "File", "Line", "Description")
        self.secrets_tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
        
        self.secrets_tree.heading("Type", text="Secret Type")
        self.secrets_tree.heading("File", text="File")
        self.secrets_tree.heading("Line", text="Line")
        self.secrets_tree.heading("Description", text="Description")
        
        self.secrets_tree.column("Type", width=150)
        self.secrets_tree.column("File", width=300)
        self.secrets_tree.column("Line", width=60)
        self.secrets_tree.column("Description", width=300)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.secrets_tree.yview)
        self.secrets_tree.configure(yscrollcommand=scrollbar.set)
        
        self.secrets_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return frame
    
    def create_patterns_tab(self):
        """Create insecure patterns tab."""
        frame = ttk.Frame(self)
        
        # Treeview for patterns
        columns = ("Severity", "Pattern", "File", "Line", "Fix")
        self.patterns_tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
        
        self.patterns_tree.heading("Severity", text="Severity")
        self.patterns_tree.heading("Pattern", text="Pattern")
        self.patterns_tree.heading("File", text="File")
        self.patterns_tree.heading("Line", text="Line")
        self.patterns_tree.heading("Fix", text="Fix Suggestion")
        
        self.patterns_tree.column("Severity", width=80)
        self.patterns_tree.column("Pattern", width=200)
        self.patterns_tree.column("File", width=250)
        self.patterns_tree.column("Line", width=60)
        self.patterns_tree.column("Fix", width=300)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.patterns_tree.yview)
        self.patterns_tree.configure(yscrollcommand=scrollbar.set)
        
        self.patterns_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure tags
        self.patterns_tree.tag_configure('critical', foreground='darkred', font=('TkDefaultFont', 9, 'bold'))
        self.patterns_tree.tag_configure('high', foreground='red')
        self.patterns_tree.tag_configure('medium', foreground='orange')
        self.patterns_tree.tag_configure('low', foreground='gray')
        
        return frame
    
    @run_async
    def run_scan(self):
        """Run security scan."""
        try:
            self.scan_output.clear()
            self.scan_output.write("🔒 Starting security scan...\n", 'info')
            
            project_path = self.project_path.get()
            
            # Run scan
            result = self.orchestrator.scan_security(
                project_path,
                scan_vulnerabilities=self.scan_vulnerabilities_var.get(),
                scan_dependencies=self.scan_dependencies_var.get(),
                scan_patterns=self.scan_patterns_var.get(),
                scan_secrets=self.scan_secrets_var.get()
            )
            
            if result.success:
                summary = result.data['summary']
                risk_score = result.data['risk_score']
                
                # Update dashboard
                self.risk_score_label.config(text=f"{risk_score:.1f}/100")
                self.risk_progress['value'] = risk_score
                
                # Update severity counts
                self.critical_label.config(text=str(summary['critical']))
                self.high_label.config(text=str(summary['high']))
                self.medium_label.config(text=str(summary['medium']))
                self.low_label.config(text=str(summary['low']))
                
                # Update category counts
                self.vuln_label.config(text=str(summary['vulnerabilities']))
                self.deps_label.config(text=str(summary['dependencies']))
                self.patterns_label.config(text=str(summary['patterns']))
                self.secrets_label.config(text=str(summary['secrets']))
                
                # Populate trees
                self.populate_vulnerabilities(result.data['issues'])
                self.populate_secrets(result.data['issues'])
                self.populate_patterns(result.data['issues'])
                
                self.scan_output.write(f"\n✓ {result.message}\n", 'success')
                self.scan_output.write(f"Risk Score: {risk_score:.1f}/100\n", 'info')
                
                if summary['critical'] > 0:
                    self.scan_output.write(f"⚠️ {summary['critical']} CRITICAL issues found!\n", 'error')
            else:
                self.scan_output.write(f"\n✗ {result.message}\n", 'error')
        
        except Exception as e:
            self.scan_output.write(f"\nError: {e}\n", 'error')
    
    def populate_vulnerabilities(self, issues):
        """Populate vulnerabilities tree."""
        # Clear tree
        for item in self.vuln_tree.get_children():
            self.vuln_tree.delete(item)
        
        # Add vulnerabilities
        vulns = [i for i in issues if i['category'] == 'vulnerability']
        for issue in vulns:
            self.vuln_tree.insert('', tk.END, values=(
                issue['severity'],
                issue.get('file_path', 'N/A'),
                issue.get('cve_id', 'N/A'),
                issue.get('cvss_score', 'N/A'),
                issue['description'][:100]
            ), tags=(issue['severity'],))
    
    def populate_secrets(self, issues):
        """Populate secrets tree."""
        # Clear tree
        for item in self.secrets_tree.get_children():
            self.secrets_tree.delete(item)
        
        # Add secrets
        secrets = [i for i in issues if i['category'] == 'secret']
        for issue in secrets:
            self.secrets_tree.insert('', tk.END, values=(
                issue['title'],
                issue.get('file_path', 'N/A'),
                issue.get('line_number', 'N/A'),
                issue['description'][:100]
            ))
    
    def populate_patterns(self, issues):
        """Populate patterns tree."""
        # Clear tree
        for item in self.patterns_tree.get_children():
            self.patterns_tree.delete(item)
        
        # Add patterns
        patterns = [i for i in issues if i['category'] == 'pattern']
        for issue in patterns:
            self.patterns_tree.insert('', tk.END, values=(
                issue['severity'],
                issue['title'],
                issue.get('file_path', 'N/A'),
                issue.get('line_number', 'N/A'),
                issue.get('fix_description', 'N/A')[:50]
            ), tags=(issue['severity'],))
    
    def browse_project(self):
        """Browse for project directory."""
        path = filedialog.askdirectory(title="Select Project Directory")
        if path:
            self.project_path.set(path)
