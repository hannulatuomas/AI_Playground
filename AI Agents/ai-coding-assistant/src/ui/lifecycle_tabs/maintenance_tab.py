"""
Maintenance Tab - Project health and dependency management

Handles:
- Dependency checking and updates
- Security vulnerability scanning
- Code health analysis
- Maintenance report generation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
import json


class MaintenanceTab:
    """Project maintenance interface."""
    
    def __init__(self, parent, project_maintainer):
        """
        Initialize Maintenance tab.
        
        Args:
            parent: Parent widget
            project_maintainer: ProjectMaintainer instance
        """
        self.parent = parent
        self.project_maintainer = project_maintainer
        self.current_project_path = None
        
        # Variables
        self.maint_path_var = tk.StringVar(value="No project selected")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all widgets for maintenance tab."""
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(1, weight=1)
        
        # Project selector
        sel = ttk.LabelFrame(self.parent, text="Project", padding="10")
        sel.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        sel.columnconfigure(1, weight=1)
        
        ttk.Label(sel, text="Path:").grid(row=0, column=0, sticky='w', pady=5)
        path_frame = ttk.Frame(sel)
        path_frame.grid(row=0, column=1, sticky='ew', pady=5, padx=(5, 0))
        path_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(path_frame, textvariable=self.maint_path_var, 
                 state='readonly').grid(row=0, column=0, sticky='ew')
        ttk.Button(path_frame, text="Select", command=self.select_project, 
                  width=10).grid(row=0, column=1, padx=(5, 0))
        ttk.Button(path_frame, text="Report", command=self.gen_report, 
                  width=12).grid(row=0, column=2, padx=(5, 0))
        
        # Sub-tabs
        sub = ttk.Notebook(self.parent)
        sub.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        
        deps = ttk.Frame(sub)
        sec = ttk.Frame(sub)
        health = ttk.Frame(sub)
        
        sub.add(deps, text="📦 Dependencies")
        sub.add(sec, text="🛡️ Security")
        sub.add(health, text="❤️ Health")
        
        self.create_deps_tab(deps)
        self.create_security_tab(sec)
        self.create_health_tab(health)
    
    def create_deps_tab(self, parent):
        """Create dependencies tab."""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        btn = ttk.Frame(parent)
        btn.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        ttk.Button(btn, text="Check Updates", command=self.check_deps, 
                  width=18).pack(side='left', padx=5)
        ttk.Button(btn, text="Show Commands", command=self.show_cmds, 
                  width=18).pack(side='left', padx=5)
        self.deps_status = ttk.Label(btn, text="", foreground='gray')
        self.deps_status.pack(side='left', padx=10)
        
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        self.deps_tree = ttk.Treeview(tree_frame, columns=('current', 'latest', 'status'), 
                                     show='tree headings', height=15)
        self.deps_tree.heading('#0', text='Package')
        self.deps_tree.heading('current', text='Current')
        self.deps_tree.heading('latest', text='Latest')
        self.deps_tree.heading('status', text='Status')
        self.deps_tree.column('#0', width=200)
        self.deps_tree.column('current', width=100)
        self.deps_tree.column('latest', width=100)
        self.deps_tree.column('status', width=100)
        self.deps_tree.grid(row=0, column=0, sticky='nsew')
        
        scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.deps_tree.yview)
        scroll.grid(row=0, column=1, sticky='ns')
        self.deps_tree.configure(yscrollcommand=scroll.set)
        
        self.deps_tree.tag_configure('outdated', foreground='orange')
        self.deps_tree.tag_configure('uptodate', foreground='green')
    
    def create_security_tab(self, parent):
        """Create security tab."""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        btn = ttk.Frame(parent)
        btn.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        ttk.Button(btn, text="Scan Vulnerabilities", command=self.scan_vulns, 
                  width=22).pack(side='left', padx=5)
        self.sec_status = ttk.Label(btn, text="", foreground='gray')
        self.sec_status.pack(side='left', padx=10)
        
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        self.sec_tree = ttk.Treeview(tree_frame, columns=('severity', 'package', 'issue'), 
                                    show='tree headings', height=15)
        self.sec_tree.heading('#0', text='ID')
        self.sec_tree.heading('severity', text='Severity')
        self.sec_tree.heading('package', text='Package')
        self.sec_tree.heading('issue', text='Issue')
        self.sec_tree.column('#0', width=80)
        self.sec_tree.column('severity', width=100)
        self.sec_tree.column('package', width=150)
        self.sec_tree.column('issue', width=400)
        self.sec_tree.grid(row=0, column=0, sticky='nsew')
        
        scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.sec_tree.yview)
        scroll.grid(row=0, column=1, sticky='ns')
        self.sec_tree.configure(yscrollcommand=scroll.set)
        
        self.sec_tree.tag_configure('critical', foreground='red', font=('Arial', 10, 'bold'))
        self.sec_tree.tag_configure('high', foreground='orange')
        self.sec_tree.tag_configure('medium', foreground='yellow4')
        self.sec_tree.tag_configure('low', foreground='blue')
    
    def create_health_tab(self, parent):
        """Create health tab."""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)
        
        btn = ttk.Frame(parent)
        btn.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        ttk.Button(btn, text="Analyze Health", command=self.analyze_health, 
                  width=18).pack(side='left', padx=5)
        self.health_status = ttk.Label(btn, text="", foreground='gray')
        self.health_status.pack(side='left', padx=10)
        
        metrics = ttk.LabelFrame(parent, text="Metrics", padding="15")
        metrics.grid(row=1, column=0, sticky='ew', padx=10, pady=10)
        metrics.columnconfigure(1, weight=1)
        
        ttk.Label(metrics, text="Type:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=5)
        self.h_type = ttk.Label(metrics, text="N/A")
        self.h_type.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(metrics, text="Files:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky='w', pady=5)
        self.h_files = ttk.Label(metrics, text="0")
        self.h_files.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(metrics, text="Lines:", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky='w', pady=5)
        self.h_lines = ttk.Label(metrics, text="0")
        self.h_lines.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(metrics, text="Issues:", font=('Arial', 10, 'bold')).grid(
            row=3, column=0, sticky='w', pady=5)
        self.h_issues = ttk.Label(metrics, text="0")
        self.h_issues.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))
        
        issues_frame = ttk.LabelFrame(parent, text="Issues", padding="10")
        issues_frame.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)
        issues_frame.columnconfigure(0, weight=1)
        issues_frame.rowconfigure(0, weight=1)
        
        self.h_issues_text = scrolledtext.ScrolledText(issues_frame, height=10, 
                                                       wrap='word', font=('Arial', 9))
        self.h_issues_text.grid(row=0, column=0, sticky='nsew')
    
    # Handlers
    def select_project(self):
        """Select project."""
        folder = filedialog.askdirectory(title="Select Project")
        if folder:
            self.maint_path_var.set(folder)
            self.current_project_path = Path(folder)
    
    def gen_report(self):
        """Generate maintenance report."""
        if not self.current_project_path:
            messagebox.showwarning("Warning", "Select a project first")
            return
        
        self.deps_status.config(text="Generating report...")
        self.parent.update()
        
        try:
            report = self.project_maintainer.generate_maintenance_report(
                self.current_project_path, include_outdated=True, 
                include_vulnerabilities=True, include_health=True
            )
            
            report_path = self.current_project_path / "MAINTENANCE_REPORT.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            messagebox.showinfo("Success",
                f"Report generated!\n\nSummary:\n" +
                f"Outdated: {report['summary']['outdated_count']}\n" +
                f"Vulnerabilities: {report['summary']['vulnerability_count']}\n" +
                f"Saved to: {report_path}"
            )
            self.deps_status.config(text="Report generated")
        except Exception as e:
            messagebox.showerror("Error", f"Report failed: {e}")
            self.deps_status.config(text="Error")
    
    def check_deps(self):
        """Check dependencies."""
        if not self.current_project_path:
            messagebox.showwarning("Warning", "Select a project first")
            return
        
        self.deps_status.config(text="Checking...")
        self.parent.update()
        
        try:
            proj_type = self.project_maintainer._detect_project_type(self.current_project_path)
            if not proj_type:
                messagebox.showinfo("Info", "Cannot detect project type")
                self.deps_status.config(text="Unknown type")
                return
            
            outdated = self.project_maintainer.check_outdated_deps(
                self.current_project_path, project_type=proj_type)
            
            for item in self.deps_tree.get_children():
                self.deps_tree.delete(item)
            
            if outdated:
                for dep in outdated:
                    tag = 'outdated' if dep['is_outdated'] else 'uptodate'
                    status = 'Outdated' if dep['is_outdated'] else 'Up to date'
                    self.deps_tree.insert('', 'end', text=dep['name'],
                                         values=(dep['current'], dep['latest'], status), 
                                         tags=(tag,))
            else:
                self.deps_tree.insert('', 'end', text='No dependencies or all up to date')
            
            self.deps_status.config(text=f"Found {len(outdated)} packages")
        except Exception as e:
            messagebox.showerror("Error", f"Check failed: {e}")
            self.deps_status.config(text="Error")
    
    def show_cmds(self):
        """Show update commands."""
        if not self.current_project_path:
            messagebox.showwarning("Warning", "Select a project first")
            return
        
        try:
            proj_type = self.project_maintainer._detect_project_type(self.current_project_path)
            if not proj_type:
                messagebox.showinfo("Info", "Cannot detect project type")
                return
            
            cmds = self.project_maintainer.get_update_commands(
                self.current_project_path, project_type=proj_type)
            if cmds:
                messagebox.showinfo("Update Commands", 
                                   "Update commands:\n\n" + "\n".join(cmds))
            else:
                messagebox.showinfo("Info", "No update commands available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")
    
    def scan_vulns(self):
        """Scan vulnerabilities."""
        if not self.current_project_path:
            messagebox.showwarning("Warning", "Select a project first")
            return
        
        self.sec_status.config(text="Scanning...")
        self.parent.update()
        
        try:
            proj_type = self.project_maintainer._detect_project_type(self.current_project_path)
            if not proj_type:
                messagebox.showinfo("Info", "Cannot detect project type")
                self.sec_status.config(text="Unknown type")
                return
            
            vulns = self.project_maintainer.scan_vulnerabilities(
                self.current_project_path, project_type=proj_type)
            
            for item in self.sec_tree.get_children():
                self.sec_tree.delete(item)
            
            if vulns:
                for i, vuln in enumerate(vulns, 1):
                    severity = vuln.get('severity', 'unknown').lower()
                    self.sec_tree.insert('', 'end', text=str(i),
                                        values=(vuln.get('severity', 'Unknown'),
                                               vuln.get('package', 'Unknown'),
                                               vuln.get('issue', 'No description')[:60] + '...'),
                                        tags=(severity,))
            else:
                self.sec_tree.insert('', 'end', text='No vulnerabilities found!')
            
            self.sec_status.config(text=f"Found {len(vulns)} vulnerabilities")
            
            if vulns:
                critical = sum(1 for v in vulns if v.get('severity', '').lower() == 'critical')
                if critical > 0:
                    messagebox.showwarning("Critical!", f"{critical} critical vulnerabilities!")
        except Exception as e:
            messagebox.showerror("Error", f"Scan failed: {e}")
            self.sec_status.config(text="Error")
    
    def analyze_health(self):
        """Analyze code health."""
        if not self.current_project_path:
            messagebox.showwarning("Warning", "Select a project first")
            return
        
        self.health_status.config(text="Analyzing...")
        self.parent.update()
        
        try:
            proj_type = self.project_maintainer._detect_project_type(self.current_project_path)
            health = self.project_maintainer.analyze_code_health(
                self.current_project_path, project_type=proj_type)
            
            if health:
                self.h_type.config(text=health.get('project_type', 'Unknown'))
                self.h_files.config(text=str(health.get('file_count', 0)))
                self.h_lines.config(text=str(health.get('line_count', 0)))
                self.h_issues.config(text=str(len(health.get('issues', []))))
                
                self.h_issues_text.delete('1.0', 'end')
                issues = health.get('issues', [])
                if issues:
                    for issue in issues:
                        self.h_issues_text.insert('end', f"• {issue}\n")
                else:
                    self.h_issues_text.insert('end', "No issues detected!")
                
                self.health_status.config(text="Analysis complete")
            else:
                messagebox.showinfo("Info", "Could not analyze project")
                self.health_status.config(text="Failed")
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {e}")
            self.health_status.config(text="Error")
