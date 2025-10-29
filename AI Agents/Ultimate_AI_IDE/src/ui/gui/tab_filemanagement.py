"""
File Management Tab

File splitting and management interface.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path

from .base import BaseTab, LabeledEntry, OutputPanel, run_async


class FileManagementTab(BaseTab):
    """File management and splitting tab."""
    
    def setup_ui(self):
        """Setup file management UI."""
        # Create notebook for sub-tabs
        sub_notebook = ttk.Notebook(self)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sub-tabs
        self.detect_frame = self.create_detect_tab()
        self.split_frame = self.create_split_tab()
        
        sub_notebook.add(self.detect_frame, text="Detect Large Files")
        sub_notebook.add(self.split_frame, text="Split File")
    
    def create_detect_tab(self):
        """Create large file detection tab."""
        frame = ttk.Frame(self)
        
        # Controls
        control_frame = ttk.LabelFrame(frame, text="Detection Settings", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.detect_project_path = LabeledEntry(control_frame, "Project Path:", width=50)
        self.detect_project_path.pack(fill=tk.X, pady=5)
        self.detect_project_path.set(".")
        
        settings_row = ttk.Frame(control_frame)
        settings_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_row, text="Max Lines:").pack(side=tk.LEFT, padx=5)
        self.max_lines = ttk.Spinbox(settings_row, from_=100, to=1000, increment=50, width=10)
        self.max_lines.set(500)
        self.max_lines.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="Detect Large Files",
            command=self.detect_large_files,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Results
        results_frame = ttk.LabelFrame(frame, text="Large Files Found", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for files
        columns = ("Path", "Lines", "Excess", "Language")
        self.files_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=12)
        
        self.files_tree.heading("Path", text="File Path")
        self.files_tree.heading("Lines", text="Lines")
        self.files_tree.heading("Excess", text="Excess")
        self.files_tree.heading("Language", text="Language")
        
        self.files_tree.column("Path", width=400)
        self.files_tree.column("Lines", width=80)
        self.files_tree.column("Excess", width=80)
        self.files_tree.column("Language", width=100)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=scrollbar.set)
        
        self.files_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Output
        output_frame = ttk.LabelFrame(frame, text="Detection Log", padding=10)
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.detect_output = OutputPanel(output_frame, height=6)
        self.detect_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def create_split_tab(self):
        """Create file splitting tab."""
        frame = ttk.Frame(self)
        
        # Controls
        control_frame = ttk.LabelFrame(frame, text="Split Settings", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.split_file_path = LabeledEntry(control_frame, "File to Split:", width=50)
        self.split_file_path.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            control_frame,
            text="Browse...",
            command=self.browse_file
        ).pack(pady=5)
        
        # Strategy selection
        strategy_frame = ttk.Frame(control_frame)
        strategy_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(strategy_frame, text="Split Strategy:").pack(side=tk.LEFT, padx=5)
        self.strategy_var = tk.StringVar(value="auto")
        strategies = ["auto", "by_class", "by_function", "by_responsibility", "by_size"]
        self.strategy_combo = ttk.Combobox(
            strategy_frame,
            textvariable=self.strategy_var,
            values=strategies,
            state="readonly",
            width=20
        )
        self.strategy_combo.pack(side=tk.LEFT, padx=5)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame,
            text="Suggest Split Points",
            command=self.suggest_splits
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Execute Split",
            command=self.execute_split,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        self.dry_run_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            button_frame,
            text="Dry Run",
            variable=self.dry_run_var
        ).pack(side=tk.LEFT, padx=5)
        
        # Suggestions
        suggestions_frame = ttk.LabelFrame(frame, text="Split Suggestions", padding=10)
        suggestions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.suggestions_text = scrolledtext.ScrolledText(suggestions_frame, height=10, wrap=tk.WORD)
        self.suggestions_text.pack(fill=tk.BOTH, expand=True)
        
        # Output
        output_frame = ttk.LabelFrame(frame, text="Split Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.split_output = OutputPanel(output_frame, height=8)
        self.split_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    @run_async
    def detect_large_files(self):
        """Detect large files in project."""
        try:
            self.detect_output.clear()
            self.detect_output.write("Detecting large files...\n", 'info')
            
            project_path = self.detect_project_path.get()
            result = self.orchestrator.detect_large_files(project_path)
            
            # Clear tree
            for item in self.files_tree.get_children():
                self.files_tree.delete(item)
            
            if result.success:
                large_files = result.data.get('large_files', [])
                
                if not large_files:
                    self.detect_output.write("✓ No large files found!\n", 'success')
                else:
                    self.detect_output.write(f"Found {len(large_files)} large files\n", 'info')
                    
                    for file_info in large_files:
                        self.files_tree.insert('', tk.END, values=(
                            file_info['path'],
                            file_info['lines'],
                            file_info['excess'],
                            file_info['language']
                        ))
            else:
                self.detect_output.write(f"Error: {result.message}\n", 'error')
        
        except Exception as e:
            self.detect_output.write(f"Error: {e}\n", 'error')
    
    @run_async
    def suggest_splits(self):
        """Suggest split points for file."""
        try:
            file_path = self.split_file_path.get()
            if not file_path:
                messagebox.showwarning("No File", "Please select a file to split")
                return
            
            self.suggestions_text.delete('1.0', tk.END)
            self.split_output.clear()
            self.split_output.write("Analyzing file...\n", 'info')
            
            from ...modules.file_splitter import FileSplitter
            splitter = FileSplitter()
            suggestions = splitter.suggest_split_points(file_path)
            
            if suggestions.get('success'):
                self.suggestions_text.insert('1.0', f"File: {file_path}\n")
                self.suggestions_text.insert(tk.END, f"Total Lines: {suggestions['total_lines']}\n")
                self.suggestions_text.insert(tk.END, f"Classes: {suggestions.get('classes', 0)}\n")
                self.suggestions_text.insert(tk.END, f"Functions: {suggestions.get('functions', 0)}\n\n")
                
                self.suggestions_text.insert(tk.END, "Suggested Strategies:\n\n")
                for suggestion in suggestions.get('suggestions', []):
                    self.suggestions_text.insert(tk.END, f"Strategy: {suggestion['strategy']}\n")
                    self.suggestions_text.insert(tk.END, f"{suggestion['description']}\n")
                    self.suggestions_text.insert(tk.END, f"Resulting files: ~{suggestion['files']}\n\n")
                
                self.split_output.write("✓ Analysis complete\n", 'success')
            else:
                self.split_output.write(f"Error: {suggestions.get('error', 'Unknown error')}\n", 'error')
        
        except Exception as e:
            self.split_output.write(f"Error: {e}\n", 'error')
    
    @run_async
    def execute_split(self):
        """Execute file split."""
        try:
            file_path = self.split_file_path.get()
            if not file_path:
                messagebox.showwarning("No File", "Please select a file to split")
                return
            
            strategy = self.strategy_var.get()
            dry_run = self.dry_run_var.get()
            
            self.split_output.clear()
            
            if dry_run:
                self.split_output.write(f"[DRY RUN] Would split {file_path} using strategy: {strategy}\n", 'info')
                return
            
            self.split_output.write(f"Splitting {file_path}...\n", 'info')
            
            result = self.orchestrator.split_file(file_path, strategy)
            
            if result.success:
                self.split_output.write(f"\n✓ {result.message}\n", 'success')
                if result.data.get('files_created'):
                    self.split_output.write("\nCreated files:\n", 'info')
                    for new_file in result.data['files_created']:
                        self.split_output.write(f"  - {new_file}\n")
            else:
                self.split_output.write(f"\n✗ {result.message}\n", 'error')
        
        except Exception as e:
            self.split_output.write(f"Error: {e}\n", 'error')
    
    def browse_file(self):
        """Browse for file to split."""
        path = filedialog.askopenfilename(
            title="Select File to Split",
            filetypes=[
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("TypeScript files", "*.ts"),
                ("All files", "*.*")
            ]
        )
        if path:
            self.split_file_path.set(path)
