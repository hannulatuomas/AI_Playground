"""
Automation Tab

Automation engine control and monitoring interface.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path

from .base import BaseTab, OutputPanel, run_async


class AutomationTab(BaseTab):
    """Automation engine control tab."""
    
    def setup_ui(self):
        """Setup automation UI."""
        # Status panel
        status_frame = ttk.LabelFrame(self, text="Automation Engine Status", padding=10)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Status grid
        status_grid = ttk.Frame(status_frame)
        status_grid.pack(fill=tk.X, pady=5)
        
        # Enabled status
        ttk.Label(status_grid, text="Status:", font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.enabled_label = ttk.Label(status_grid, text="Unknown", foreground="gray")
        self.enabled_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Statistics
        ttk.Label(status_grid, text="Triggers Registered:", font=('TkDefaultFont', 10)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.triggers_label = ttk.Label(status_grid, text="0")
        self.triggers_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(status_grid, text="Actions Registered:", font=('TkDefaultFont', 10)).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.actions_label = ttk.Label(status_grid, text="0")
        self.actions_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(status_grid, text="Triggers Fired:", font=('TkDefaultFont', 10)).grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.fired_label = ttk.Label(status_grid, text="0")
        self.fired_label.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(status_grid, text="Actions Executed:", font=('TkDefaultFont', 10)).grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.executed_label = ttk.Label(status_grid, text="0")
        self.executed_label.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(status_grid, text="Actions Failed:", font=('TkDefaultFont', 10)).grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.failed_label = ttk.Label(status_grid, text="0", foreground="red")
        self.failed_label.grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Control buttons
        button_frame = ttk.Frame(status_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame,
            text="Refresh Status",
            command=self.refresh_status
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Enable Automation",
            command=self.enable_automation,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Disable Automation",
            command=self.disable_automation
        ).pack(side=tk.LEFT, padx=5)
        
        # Triggers panel
        triggers_frame = ttk.LabelFrame(self, text="Automation Triggers", padding=10)
        triggers_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for triggers
        columns = ("Trigger", "Action", "Priority", "Status")
        self.triggers_tree = ttk.Treeview(triggers_frame, columns=columns, show="tree headings", height=12)
        
        self.triggers_tree.heading("#0", text="Type")
        self.triggers_tree.heading("Trigger", text="Trigger")
        self.triggers_tree.heading("Action", text="Action")
        self.triggers_tree.heading("Priority", text="Priority")
        self.triggers_tree.heading("Status", text="Status")
        
        self.triggers_tree.column("#0", width=150)
        self.triggers_tree.column("Trigger", width=200)
        self.triggers_tree.column("Action", width=200)
        self.triggers_tree.column("Priority", width=80)
        self.triggers_tree.column("Status", width=80)
        
        scrollbar = ttk.Scrollbar(triggers_frame, orient=tk.VERTICAL, command=self.triggers_tree.yview)
        self.triggers_tree.configure(yscrollcommand=scrollbar.set)
        
        self.triggers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preferences panel
        prefs_frame = ttk.LabelFrame(self, text="Automation Preferences", padding=10)
        prefs_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.auto_quality_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            prefs_frame,
            text="Auto Quality Check",
            variable=self.auto_quality_var
        ).pack(anchor=tk.W, pady=2)
        
        self.auto_refactor_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            prefs_frame,
            text="Auto Refactor",
            variable=self.auto_refactor_var
        ).pack(anchor=tk.W, pady=2)
        
        self.auto_test_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            prefs_frame,
            text="Auto Run Tests",
            variable=self.auto_test_var
        ).pack(anchor=tk.W, pady=2)
        
        self.auto_split_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            prefs_frame,
            text="Auto Split Large Files",
            variable=self.auto_split_var
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Button(
            prefs_frame,
            text="Save Preferences",
            command=self.save_preferences
        ).pack(pady=10)
        
        # Output
        output_frame = ttk.LabelFrame(self, text="Automation Log", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.output = OutputPanel(output_frame, height=8)
        self.output.pack(fill=tk.BOTH, expand=True)
        
        # Load initial status
        self.refresh_status()
    
    @run_async
    def refresh_status(self):
        """Refresh automation status."""
        try:
            self.output.write("Refreshing status...\n", 'info')
            
            stats = self.orchestrator.automation_engine.get_stats()
            
            # Update status labels
            if stats['enabled']:
                self.enabled_label.config(text="✓ Enabled", foreground="green")
            else:
                self.enabled_label.config(text="✗ Disabled", foreground="red")
            
            self.triggers_label.config(text=str(stats['triggers_registered']))
            self.actions_label.config(text=str(stats['actions_registered']))
            self.fired_label.config(text=str(stats['triggers_fired']))
            self.executed_label.config(text=str(stats['actions_executed']))
            self.failed_label.config(text=str(stats['actions_failed']))
            
            # Load triggers
            self.load_triggers()
            
            self.output.write("✓ Status refreshed\n", 'success')
        
        except Exception as e:
            self.output.write(f"Error: {e}\n", 'error')
    
    @run_async
    def load_triggers(self):
        """Load automation triggers."""
        try:
            # Clear tree
            for item in self.triggers_tree.get_children():
                self.triggers_tree.delete(item)
            
            triggers = self.orchestrator.automation_engine.list_triggers()
            
            for trigger_type, rules in triggers.items():
                # Add trigger type as parent
                parent = self.triggers_tree.insert('', tk.END, text=trigger_type, open=True)
                
                # Add rules as children
                for rule in rules:
                    status = "✓ Enabled" if rule['enabled'] else "✗ Disabled"
                    self.triggers_tree.insert(parent, tk.END, values=(
                        "",
                        rule['action'],
                        rule['priority'],
                        status
                    ))
        
        except Exception as e:
            self.output.write(f"Error loading triggers: {e}\n", 'error')
    
    @run_async
    def enable_automation(self):
        """Enable automation engine."""
        try:
            self.orchestrator.automation_engine.enable()
            self.output.write("✓ Automation engine enabled\n", 'success')
            self.refresh_status()
        
        except Exception as e:
            self.output.write(f"Error: {e}\n", 'error')
    
    @run_async
    def disable_automation(self):
        """Disable automation engine."""
        try:
            self.orchestrator.automation_engine.disable()
            self.output.write("✓ Automation engine disabled\n", 'success')
            self.refresh_status()
        
        except Exception as e:
            self.output.write(f"Error: {e}\n", 'error')
    
    def save_preferences(self):
        """Save automation preferences."""
        try:
            # Get preferences
            prefs = {
                'auto_quality_check': self.auto_quality_var.get(),
                'auto_refactor': self.auto_refactor_var.get(),
                'auto_test': self.auto_test_var.get(),
                'auto_split': self.auto_split_var.get()
            }
            
            # Save to automation engine preferences
            for key, value in prefs.items():
                self.orchestrator.automation_engine.preferences.set(key, value)
            
            self.output.write("✓ Preferences saved\n", 'success')
            messagebox.showinfo("Success", "Automation preferences saved")
        
        except Exception as e:
            self.output.write(f"Error: {e}\n", 'error')
            messagebox.showerror("Error", f"Failed to save preferences: {e}")
