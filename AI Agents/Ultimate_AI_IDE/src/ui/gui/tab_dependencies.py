"""
Dependencies Tab

Dependency management and update interface.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path

from .base import BaseTab, LabeledEntry, OutputPanel, run_async


class DependenciesTab(BaseTab):
    """Dependency management tab."""
    
    def setup_ui(self):
        """Setup dependencies UI."""
        # Create notebook for sub-tabs
        sub_notebook = ttk.Notebook(self)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sub-tabs
        self.check_frame = self.create_check_tab()
        self.update_frame = self.create_update_tab()
        
        sub_notebook.add(self.check_frame, text="Check Updates")
        sub_notebook.add(self.update_frame, text="Update Dependencies")
    
    def create_check_tab(self):
        """Create check updates tab."""
        frame = ttk.Frame(self)
        
        # Controls
        control_frame = ttk.LabelFrame(frame, text="Check Settings", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.project_path = LabeledEntry(control_frame, "Project Path:", width=50)
        self.project_path.pack(fill=tk.X, pady=5)
        self.project_path.set(".")
        
        ttk.Button(
            control_frame,
            text="Check for Updates",
            command=self.check_updates,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(frame, text="Available Updates", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for updates
        columns = ("Package", "Current", "Latest", "Type")
        self.updates_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
        
        self.updates_tree.heading("Package", text="Package")
        self.updates_tree.heading("Current", text="Current Version")
        self.updates_tree.heading("Latest", text="Latest Version")
        self.updates_tree.heading("Type", text="Update Type")
        
        self.updates_tree.column("Package", width=200)
        self.updates_tree.column("Current", width=120)
        self.updates_tree.column("Latest", width=120)
        self.updates_tree.column("Type", width=100)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.updates_tree.yview)
        self.updates_tree.configure(yscrollcommand=scrollbar.set)
        
        self.updates_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure tags
        self.updates_tree.tag_configure('breaking', foreground='red', font=('TkDefaultFont', 9, 'bold'))
        self.updates_tree.tag_configure('safe', foreground='green')
        
        # Output
        output_frame = ttk.LabelFrame(frame, text="Log", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.check_output = OutputPanel(output_frame, height=6)
        self.check_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def create_update_tab(self):
        """Create update dependencies tab."""
        frame = ttk.Frame(self)
        
        # Controls
        control_frame = ttk.LabelFrame(frame, text="Update Settings", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.update_project_path = LabeledEntry(control_frame, "Project Path:", width=50)
        self.update_project_path.pack(fill=tk.X, pady=5)
        self.update_project_path.set(".")
        
        # Options
        options_frame = ttk.Frame(control_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        self.safe_only_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Safe Updates Only (no breaking changes)",
            variable=self.safe_only_var
        ).pack(anchor=tk.W)
        
        self.run_tests_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Run Tests After Update",
            variable=self.run_tests_var
        ).pack(anchor=tk.W)
        
        self.auto_rollback_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Auto-Rollback on Failure",
            variable=self.auto_rollback_var
        ).pack(anchor=tk.W)
        
        # Package selection
        pkg_frame = ttk.Frame(control_frame)
        pkg_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(pkg_frame, text="Specific Package (optional):").pack(side=tk.LEFT, padx=5)
        self.package_entry = ttk.Entry(pkg_frame, width=30)
        self.package_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame,
            text="Update All Safe",
            command=lambda: self.update_dependencies(safe_only=True),
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Update Specific",
            command=lambda: self.update_dependencies(specific=True)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Update All",
            command=lambda: self.update_dependencies(safe_only=False)
        ).pack(side=tk.LEFT, padx=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(frame, text="Update Status", padding=10)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready", font=('TkDefaultFont', 10, 'bold'))
        self.status_label.pack()
        
        self.progress = ttk.Progressbar(status_frame, length=400, mode='indeterminate')
        self.progress.pack(pady=5)
        
        # Results
        results_frame = ttk.LabelFrame(frame, text="Update Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Updated packages
        ttk.Label(results_frame, text="Updated:", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.updated_label = ttk.Label(results_frame, text="0 packages", foreground="green")
        self.updated_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Failed packages
        ttk.Label(results_frame, text="Failed:", font=('TkDefaultFont', 9, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.failed_label = ttk.Label(results_frame, text="0 packages", foreground="red")
        self.failed_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Test status
        ttk.Label(results_frame, text="Tests:", font=('TkDefaultFont', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, padx=5)
        self.tests_label = ttk.Label(results_frame, text="Not run")
        self.tests_label.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Output
        output_frame = ttk.LabelFrame(frame, text="Update Log", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.update_output = OutputPanel(output_frame, height=8)
        self.update_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    @run_async
    def check_updates(self):
        """Check for available updates."""
        try:
            self.check_output.clear()
            self.check_output.write("🔍 Checking for outdated dependencies...\n", 'info')
            
            project_path = self.project_path.get()
            
            from ...modules.dependency_manager import DependencyManager
            manager = DependencyManager(project_path)
            
            self.check_output.write(f"Package Manager: {manager.package_manager}\n", 'info')
            
            updates = manager.check_outdated()
            
            # Clear tree
            for item in self.updates_tree.get_children():
                self.updates_tree.delete(item)
            
            if not updates:
                self.check_output.write("\n✓ All dependencies are up to date!\n", 'success')
                return
            
            # Populate tree
            breaking_count = 0
            safe_count = 0
            
            for update in updates:
                update_type = "⚠️ Breaking" if update.is_breaking else "✓ Safe"
                tag = 'breaking' if update.is_breaking else 'safe'
                
                self.updates_tree.insert('', tk.END, values=(
                    update.name,
                    update.current_version,
                    update.latest_version,
                    update_type
                ), tags=(tag,))
                
                if update.is_breaking:
                    breaking_count += 1
                else:
                    safe_count += 1
            
            self.check_output.write(f"\n✓ Found {len(updates)} outdated dependencies\n", 'success')
            self.check_output.write(f"  • Safe updates: {safe_count}\n", 'info')
            if breaking_count > 0:
                self.check_output.write(f"  • Breaking changes: {breaking_count}\n", 'warning')
        
        except Exception as e:
            self.check_output.write(f"\nError: {e}\n", 'error')
    
    @run_async
    def update_dependencies(self, safe_only=False, specific=False):
        """Update dependencies."""
        try:
            self.update_output.clear()
            self.status_label.config(text="Updating...")
            self.progress.start()
            
            project_path = self.update_project_path.get()
            
            from ...modules.dependency_manager import DependencyManager
            manager = DependencyManager(project_path)
            
            # Determine packages to update
            packages = None
            if specific:
                pkg = self.package_entry.get().strip()
                if pkg:
                    packages = [pkg]
                    self.update_output.write(f"📦 Updating specific package: {pkg}\n", 'info')
                else:
                    self.update_output.write("⚠️ No package specified\n", 'warning')
                    self.progress.stop()
                    self.status_label.config(text="Ready")
                    return
            elif safe_only or self.safe_only_var.get():
                self.update_output.write("🔍 Finding safe updates...\n", 'info')
                safe_updates = manager.suggest_safe_updates()
                packages = [u.name for u in safe_updates]
                if not packages:
                    self.update_output.write("✓ No safe updates available\n", 'success')
                    self.progress.stop()
                    self.status_label.config(text="Ready")
                    return
                self.update_output.write(f"📦 Updating {len(packages)} safe packages\n", 'info')
            else:
                self.update_output.write("📦 Updating all dependencies...\n", 'info')
            
            # Perform update
            result = manager.update_dependencies(
                packages=packages,
                test_after=self.run_tests_var.get(),
                rollback_on_failure=self.auto_rollback_var.get()
            )
            
            # Update UI
            self.updated_label.config(text=f"{len(result.updated)} packages")
            self.failed_label.config(text=f"{len(result.failed)} packages")
            
            if result.test_results:
                if result.test_results.get('success'):
                    self.tests_label.config(text="✓ Passed", foreground="green")
                else:
                    self.tests_label.config(text="✗ Failed", foreground="red")
            else:
                self.tests_label.config(text="Not run")
            
            # Log results
            if result.success:
                self.update_output.write(f"\n✓ Successfully updated {len(result.updated)} dependencies\n", 'success')
                for pkg in result.updated:
                    self.update_output.write(f"  • {pkg}\n", 'info')
                
                if result.test_results and result.test_results.get('success'):
                    self.update_output.write("\n✓ All tests passed\n", 'success')
                
                self.status_label.config(text="Update Complete")
            else:
                self.update_output.write(f"\n✗ Update failed\n", 'error')
                
                if result.failed:
                    self.update_output.write("\nFailed packages:\n", 'error')
                    for pkg in result.failed:
                        self.update_output.write(f"  • {pkg}\n", 'error')
                
                if result.rolled_back:
                    self.update_output.write("\n↩️ Changes have been rolled back\n", 'warning')
                
                self.status_label.config(text="Update Failed")
            
            self.progress.stop()
        
        except Exception as e:
            self.update_output.write(f"\nError: {e}\n", 'error')
            self.progress.stop()
            self.status_label.config(text="Error")
