"""
Code Generation Tab

Handles feature generation, class creation, and function generation.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext

from .base import BaseTab, LabeledEntry, LabeledCombobox, OutputPanel, run_async


class CodeTab(BaseTab):
    """Code generation tab."""
    
    def setup_ui(self):
        """Setup code generation UI."""
        # Create notebook for sub-tabs
        sub_notebook = ttk.Notebook(self)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sub-tabs
        self.feature_frame = self.create_feature_tab()
        self.class_frame = self.create_class_tab()
        self.function_frame = self.create_function_tab()
        
        sub_notebook.add(self.feature_frame, text="Generate Feature")
        sub_notebook.add(self.class_frame, text="Generate Class")
        sub_notebook.add(self.function_frame, text="Generate Function")
    
    def create_feature_tab(self):
        """Create feature generation tab."""
        frame = ttk.Frame(self)
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Feature Description", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Project path
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=5)
        self.feature_project_path = LabeledEntry(path_frame, "Project Path:", width=40)
        self.feature_project_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_feature_path
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Description
        ttk.Label(input_frame, text="Feature Description:").pack(anchor=tk.W, pady=(10, 5))
        self.feature_description = scrolledtext.ScrolledText(
            input_frame,
            height=8,
            wrap=tk.WORD
        )
        self.feature_description.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Generate button
        ttk.Button(
            input_frame,
            text="Generate Feature",
            command=self.generate_feature,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Output section
        output_frame = ttk.LabelFrame(frame, text="Generation Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.feature_output = OutputPanel(output_frame, height=12)
        self.feature_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def create_class_tab(self):
        """Create class generation tab."""
        frame = ttk.Frame(self)
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Class Details", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.class_name = LabeledEntry(input_frame, "Class Name:", width=40)
        self.class_name.pack(fill=tk.X, pady=5)
        
        self.class_language = LabeledCombobox(
            input_frame,
            "Language:",
            ["python", "javascript", "typescript", "csharp", "java"],
            width=20
        )
        self.class_language.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Description:").pack(anchor=tk.W, pady=(10, 5))
        self.class_description = scrolledtext.ScrolledText(
            input_frame,
            height=6,
            wrap=tk.WORD
        )
        self.class_description.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Generate button
        ttk.Button(
            input_frame,
            text="Generate Class",
            command=self.generate_class,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Output section
        output_frame = ttk.LabelFrame(frame, text="Generated Code", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.class_output = scrolledtext.ScrolledText(
            output_frame,
            height=15,
            wrap=tk.WORD
        )
        self.class_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def create_function_tab(self):
        """Create function generation tab."""
        frame = ttk.Frame(self)
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Function Details", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.func_name = LabeledEntry(input_frame, "Function Name:", width=40)
        self.func_name.pack(fill=tk.X, pady=5)
        
        self.func_language = LabeledCombobox(
            input_frame,
            "Language:",
            ["python", "javascript", "typescript", "csharp", "java"],
            width=20
        )
        self.func_language.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Description:").pack(anchor=tk.W, pady=(10, 5))
        self.func_description = scrolledtext.ScrolledText(
            input_frame,
            height=6,
            wrap=tk.WORD
        )
        self.func_description.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Generate button
        ttk.Button(
            input_frame,
            text="Generate Function",
            command=self.generate_function,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Output section
        output_frame = ttk.LabelFrame(frame, text="Generated Code", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.func_output = scrolledtext.ScrolledText(
            output_frame,
            height=15,
            wrap=tk.WORD
        )
        self.func_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def browse_feature_path(self):
        """Browse for project path."""
        path = self.select_directory("Select Project Directory")
        if path:
            self.feature_project_path.set(path)
    
    def generate_feature(self):
        """Generate feature."""
        project_path = self.feature_project_path.get().strip()
        description = self.feature_description.get("1.0", tk.END).strip()
        
        if not description:
            self.show_error("Validation Error", "Feature description is required")
            return
        
        self.feature_output.clear()
        self.feature_output.append(f"Generating feature...")
        self.feature_output.append(f"Description: {description[:100]}...")
        
        def generate():
            return self.uaide.generate_feature(
                description=description,
                project_path=project_path if project_path else None
            )
        
        def callback(result, error=None):
            if error:
                self.feature_output.append(f"\n❌ Error: {error}")
                self.show_error("Generation Failed", error)
            elif result and result.success:
                self.feature_output.append(f"\n✅ {result.message}")
                if result.data:
                    completed = result.data.get('completed_tasks', [])
                    failed = result.data.get('failed_tasks', [])
                    self.feature_output.append(f"Completed tasks: {len(completed)}")
                    if failed:
                        self.feature_output.append(f"Failed tasks: {len(failed)}")
                self.show_success("Success", "Feature generated successfully!")
            else:
                msg = result.message if result else "Unknown error"
                self.feature_output.append(f"\n❌ {msg}")
                self.show_error("Generation Failed", msg)
        
        run_async(generate, callback)
    
    def generate_class(self):
        """Generate class."""
        class_name = self.class_name.get().strip()
        language = self.class_language.get()
        description = self.class_description.get("1.0", tk.END).strip()
        
        if not class_name:
            self.show_error("Validation Error", "Class name is required")
            return
        
        if not description:
            self.show_error("Validation Error", "Description is required")
            return
        
        self.class_output.delete("1.0", tk.END)
        self.class_output.insert("1.0", f"Generating class '{class_name}'...\n")
        
        def generate():
            from ...modules.code_generator import CodeContext
            context = CodeContext(project_path=".", language=language)
            return self.uaide.code_generator.generate_class(
                class_name=class_name,
                description=description,
                context=context
            )
        
        def callback(result, error=None):
            self.class_output.delete("1.0", tk.END)
            if error:
                self.class_output.insert("1.0", f"Error: {error}")
                self.show_error("Generation Failed", error)
            elif result:
                self.class_output.insert("1.0", result)
                self.show_success("Success", "Class generated successfully!")
            else:
                self.class_output.insert("1.0", "Failed to generate class")
        
        run_async(generate, callback)
    
    def generate_function(self):
        """Generate function."""
        func_name = self.func_name.get().strip()
        language = self.func_language.get()
        description = self.func_description.get("1.0", tk.END).strip()
        
        if not func_name:
            self.show_error("Validation Error", "Function name is required")
            return
        
        if not description:
            self.show_error("Validation Error", "Description is required")
            return
        
        self.func_output.delete("1.0", tk.END)
        self.func_output.insert("1.0", f"Generating function '{func_name}'...\n")
        
        def generate():
            from ...modules.code_generator import CodeContext
            context = CodeContext(project_path=".", language=language)
            return self.uaide.code_generator.generate_function(
                function_name=func_name,
                description=description,
                context=context
            )
        
        def callback(result, error=None):
            self.func_output.delete("1.0", tk.END)
            if error:
                self.func_output.insert("1.0", f"Error: {error}")
                self.show_error("Generation Failed", error)
            elif result:
                self.func_output.insert("1.0", result)
                self.show_success("Success", "Function generated successfully!")
            else:
                self.func_output.insert("1.0", "Failed to generate function")
        
        run_async(generate, callback)
