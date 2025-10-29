"""
Refactoring Tab

Handles code analysis and refactoring.
"""

import tkinter as tk
from tkinter import ttk

from .base import BaseTab, LabeledEntry, LabeledCombobox, OutputPanel, run_async


class RefactorTab(BaseTab):
    """Refactoring tab."""
    
    def setup_ui(self):
        """Setup refactoring UI."""
        # Create notebook for sub-tabs
        sub_notebook = ttk.Notebook(self)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sub-tabs
        self.analyze_frame = self.create_analyze_tab()
        self.refactor_frame = self.create_refactor_tab()
        
        sub_notebook.add(self.analyze_frame, text="Analyze Code")
        sub_notebook.add(self.refactor_frame, text="Refactor")
    
    def create_analyze_tab(self):
        """Create code analysis tab."""
        frame = ttk.Frame(self)
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Code Analysis", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # File path
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=5)
        self.analyze_file_path = LabeledEntry(path_frame, "File Path:", width=40)
        self.analyze_file_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_analyze_file
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        self.analyze_language = LabeledCombobox(
            input_frame,
            "Language:",
            ["python", "javascript", "typescript", "java", "csharp"],
            width=20
        )
        self.analyze_language.pack(fill=tk.X, pady=5)
        
        # Analyze button
        ttk.Button(
            input_frame,
            text="Analyze Code",
            command=self.analyze_code,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Output section
        output_frame = ttk.LabelFrame(frame, text="Analysis Results", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.analyze_output = OutputPanel(output_frame, height=18)
        self.analyze_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def create_refactor_tab(self):
        """Create refactoring tab."""
        frame = ttk.Frame(self)
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Refactor Code", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # File path
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=5)
        self.refactor_file_path = LabeledEntry(path_frame, "File Path:", width=40)
        self.refactor_file_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_refactor_file
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        self.refactor_language = LabeledCombobox(
            input_frame,
            "Language:",
            ["python", "javascript", "typescript", "java", "csharp"],
            width=20
        )
        self.refactor_language.pack(fill=tk.X, pady=5)
        
        # Refactoring options
        options_frame = ttk.LabelFrame(input_frame, text="Refactoring Options", padding=5)
        options_frame.pack(fill=tk.X, pady=10)
        
        self.improve_naming_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Improve naming",
            variable=self.improve_naming_var
        ).pack(anchor=tk.W, pady=2)
        
        self.reduce_complexity_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Reduce complexity",
            variable=self.reduce_complexity_var
        ).pack(anchor=tk.W, pady=2)
        
        self.add_docstrings_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Add/improve docstrings",
            variable=self.add_docstrings_var
        ).pack(anchor=tk.W, pady=2)
        
        self.optimize_imports_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Optimize imports",
            variable=self.optimize_imports_var
        ).pack(anchor=tk.W, pady=2)
        
        # Refactor button
        ttk.Button(
            input_frame,
            text="Refactor Code",
            command=self.refactor_code,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Output section
        output_frame = ttk.LabelFrame(frame, text="Refactoring Results", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.refactor_output = OutputPanel(output_frame, height=18)
        self.refactor_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def browse_analyze_file(self):
        """Browse for file to analyze."""
        path = self.select_file(
            "Select File to Analyze",
            [("Python files", "*.py"), ("JavaScript files", "*.js"), ("All files", "*.*")]
        )
        if path:
            self.analyze_file_path.set(path)
    
    def browse_refactor_file(self):
        """Browse for file to refactor."""
        path = self.select_file(
            "Select File to Refactor",
            [("Python files", "*.py"), ("JavaScript files", "*.js"), ("All files", "*.*")]
        )
        if path:
            self.refactor_file_path.set(path)
    
    def analyze_code(self):
        """Analyze code quality."""
        file_path = self.analyze_file_path.get().strip()
        language = self.analyze_language.get()
        
        if not file_path:
            self.show_error("Validation Error", "File path is required")
            return
        
        self.analyze_output.clear()
        self.analyze_output.append(f"Analyzing: {file_path}")
        
        def analyze():
            # Read file
            with open(file_path, 'r') as f:
                code = f.read()
            
            analysis = self.uaide.refactorer.analyze_code(code, language)
            return analysis
        
        def callback(result, error=None):
            if error:
                self.analyze_output.append(f"\n❌ Error: {error}")
                self.show_error("Analysis Failed", error)
            elif result:
                self.analyze_output.append(f"\n✅ Analysis Complete")
                self.analyze_output.append(f"\nComplexity Score: {result.complexity_score}/10")
                self.analyze_output.append(f"Maintainability: {result.maintainability_score}/10")
                self.analyze_output.append(f"Lines of Code: {result.lines_of_code}")
                
                if result.issues:
                    self.analyze_output.append(f"\nIssues Found ({len(result.issues)}):")
                    for issue in result.issues:
                        severity = issue.get('severity', 'info')
                        message = issue.get('message', '')
                        self.analyze_output.append(f"  [{severity.upper()}] {message}")
                
                if result.suggestions:
                    self.analyze_output.append(f"\nSuggestions:")
                    for suggestion in result.suggestions:
                        self.analyze_output.append(f"  • {suggestion}")
                
                self.show_success("Analysis Complete", "Code analysis completed!")
            else:
                self.analyze_output.append("\n❌ Analysis failed")
        
        run_async(analyze, callback)
    
    def refactor_code(self):
        """Refactor code."""
        file_path = self.refactor_file_path.get().strip()
        language = self.refactor_language.get()
        
        if not file_path:
            self.show_error("Validation Error", "File path is required")
            return
        
        self.refactor_output.clear()
        self.refactor_output.append(f"Refactoring: {file_path}")
        
        def refactor():
            return self.uaide.refactor(
                file_path=file_path,
                language=language
            )
        
        def callback(result, error=None):
            if error:
                self.refactor_output.append(f"\n❌ Error: {error}")
                self.show_error("Refactoring Failed", error)
            elif result and result.success:
                self.refactor_output.append(f"\n✅ {result.message}")
                if result.data:
                    changes = result.data.get('changes', [])
                    improvements = result.data.get('improvements', [])
                    
                    if changes:
                        self.refactor_output.append(f"\nChanges Made ({len(changes)}):")
                        for change in changes:
                            self.refactor_output.append(f"  • {change}")
                    
                    if improvements:
                        self.refactor_output.append(f"\nImprovements:")
                        for improvement in improvements:
                            self.refactor_output.append(f"  • {improvement}")
                
                self.show_success("Success", "Code refactored successfully!")
            else:
                msg = result.message if result else "Unknown error"
                self.refactor_output.append(f"\n❌ {msg}")
                self.show_error("Refactoring Failed", msg)
        
        run_async(refactor, callback)
