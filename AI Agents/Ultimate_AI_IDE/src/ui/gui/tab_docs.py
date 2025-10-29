"""
Documentation Tab

Handles documentation generation and synchronization.
"""

import tkinter as tk
from tkinter import ttk

from .base import BaseTab, LabeledEntry, LabeledCombobox, OutputPanel, run_async


class DocsTab(BaseTab):
    """Documentation tab."""
    
    def setup_ui(self):
        """Setup documentation UI."""
        # Input section
        input_frame = ttk.LabelFrame(self, text="Documentation Generation", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Project path
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=5)
        self.docs_project_path = LabeledEntry(path_frame, "Project Path:", width=40)
        self.docs_project_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_docs_path
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        self.docs_language = LabeledCombobox(
            input_frame,
            "Language:",
            ["python", "javascript", "typescript", "java", "csharp"],
            width=20
        )
        self.docs_language.pack(fill=tk.X, pady=5)
        
        # Options
        options_frame = ttk.LabelFrame(input_frame, text="Options", padding=5)
        options_frame.pack(fill=tk.X, pady=10)
        
        self.generate_readme_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Generate README.md",
            variable=self.generate_readme_var
        ).pack(anchor=tk.W, pady=2)
        
        self.generate_api_docs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Generate API Documentation",
            variable=self.generate_api_docs_var
        ).pack(anchor=tk.W, pady=2)
        
        self.generate_changelog_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Generate CHANGELOG.md",
            variable=self.generate_changelog_var
        ).pack(anchor=tk.W, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame,
            text="Generate Documentation",
            command=self.generate_docs,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Sync Documentation",
            command=self.sync_docs
        ).pack(side=tk.LEFT, padx=5)
        
        # Output section
        output_frame = ttk.LabelFrame(self, text="Generation Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.docs_output = OutputPanel(output_frame, height=20)
        self.docs_output.pack(fill=tk.BOTH, expand=True)
    
    def browse_docs_path(self):
        """Browse for project path."""
        path = self.select_directory("Select Project Directory")
        if path:
            self.docs_project_path.set(path)
    
    def generate_docs(self):
        """Generate documentation."""
        project_path = self.docs_project_path.get().strip()
        language = self.docs_language.get()
        
        if not project_path:
            self.show_error("Validation Error", "Project path is required")
            return
        
        self.docs_output.clear()
        self.docs_output.append(f"Generating documentation for: {project_path}")
        
        generate_readme = self.generate_readme_var.get()
        generate_api = self.generate_api_docs_var.get()
        generate_changelog = self.generate_changelog_var.get()
        
        def generate():
            result = self.uaide.generate_docs(
                project_path=project_path,
                language=language
            )
            return result
        
        def callback(result, error=None):
            if error:
                self.docs_output.append(f"\n❌ Error: {error}")
                self.show_error("Generation Failed", error)
            elif result and result.success:
                self.docs_output.append(f"\n✅ {result.message}")
                if result.data:
                    files_created = result.data.get('files_created', 0)
                    files_updated = result.data.get('files_updated', 0)
                    undocumented = result.data.get('undocumented_items', 0)
                    
                    self.docs_output.append(f"\nFiles created: {files_created}")
                    self.docs_output.append(f"Files updated: {files_updated}")
                    if undocumented > 0:
                        self.docs_output.append(f"Undocumented items: {undocumented}")
                
                self.show_success("Success", "Documentation generated successfully!")
            else:
                msg = result.message if result else "Unknown error"
                self.docs_output.append(f"\n❌ {msg}")
                self.show_error("Generation Failed", msg)
        
        run_async(generate, callback)
    
    def sync_docs(self):
        """Sync documentation with code."""
        project_path = self.docs_project_path.get().strip()
        language = self.docs_language.get()
        
        if not project_path:
            self.show_error("Validation Error", "Project path is required")
            return
        
        self.docs_output.clear()
        self.docs_output.append(f"Synchronizing documentation...")
        
        def sync():
            report = self.uaide.doc_manager.sync_documentation(
                project_path=project_path,
                language=language
            )
            return report
        
        def callback(result, error=None):
            if error:
                self.docs_output.append(f"\n❌ Error: {error}")
                self.show_error("Sync Failed", error)
            elif result:
                self.docs_output.append(f"\n✅ Documentation synchronized!")
                self.docs_output.append(f"\nFiles created: {result.files_created}")
                self.docs_output.append(f"Files updated: {result.files_updated}")
                self.docs_output.append(f"Files deleted: {result.files_deleted}")
                
                if result.undocumented_items:
                    self.docs_output.append(f"\nUndocumented items ({len(result.undocumented_items)}):")
                    for item in result.undocumented_items[:10]:  # Show first 10
                        self.docs_output.append(f"  - {item}")
                    if len(result.undocumented_items) > 10:
                        self.docs_output.append(f"  ... and {len(result.undocumented_items) - 10} more")
                
                self.show_success("Success", "Documentation synchronized!")
            else:
                self.docs_output.append("\n❌ Sync failed")
        
        run_async(sync, callback)
