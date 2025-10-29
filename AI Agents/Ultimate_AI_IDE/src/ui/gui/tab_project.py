"""
Project Management Tab

Handles project creation, detection, and maintenance.
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path

from .base import BaseTab, LabeledEntry, LabeledCombobox, OutputPanel, run_async


class ProjectTab(BaseTab):
    """Project management tab."""
    
    def setup_ui(self):
        """Setup project management UI."""
        # Create notebook for sub-tabs
        sub_notebook = ttk.Notebook(self)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sub-tabs
        self.new_project_frame = self.create_new_project_tab()
        self.detect_project_frame = self.create_detect_project_tab()
        self.list_projects_frame = self.create_list_projects_tab()
        
        sub_notebook.add(self.new_project_frame, text="New Project")
        sub_notebook.add(self.detect_project_frame, text="Detect Project")
        sub_notebook.add(self.list_projects_frame, text="My Projects")
    
    def create_new_project_tab(self):
        """Create new project tab."""
        frame = ttk.Frame(self)
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Project Details", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.project_name = LabeledEntry(input_frame, "Project Name:", width=40)
        self.project_name.pack(fill=tk.X, pady=5)
        
        self.project_language = LabeledCombobox(
            input_frame,
            "Language:",
            ["python", "javascript", "typescript", "csharp", "cpp", "java", "go", "rust"],
            width=20
        )
        self.project_language.pack(fill=tk.X, pady=5)
        
        self.project_framework = LabeledCombobox(
            input_frame,
            "Framework (optional):",
            ["", "fastapi", "flask", "django", "react", "nextjs", "express", "vue", "angular"],
            width=20
        )
        self.project_framework.pack(fill=tk.X, pady=5)
        
        # Path selection
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=5)
        self.project_path = LabeledEntry(path_frame, "Path:", width=40)
        self.project_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_project_path
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Options
        options_frame = ttk.Frame(input_frame)
        options_frame.pack(fill=tk.X, pady=5)
        self.git_init_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Initialize Git repository",
            variable=self.git_init_var
        ).pack(side=tk.LEFT)
        
        # Create button
        ttk.Button(
            input_frame,
            text="Create Project",
            command=self.create_project,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Output section
        output_frame = ttk.LabelFrame(frame, text="Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.new_project_output = OutputPanel(output_frame, height=15)
        self.new_project_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def create_detect_project_tab(self):
        """Create detect project tab."""
        frame = ttk.Frame(self)
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Detect Existing Project", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Path selection
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=5)
        self.detect_path = LabeledEntry(path_frame, "Project Path:", width=40)
        self.detect_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_detect_path
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Detect button
        ttk.Button(
            input_frame,
            text="Detect Project",
            command=self.detect_project,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Output section
        output_frame = ttk.LabelFrame(frame, text="Detection Results", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.detect_output = OutputPanel(output_frame, height=15)
        self.detect_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def create_list_projects_tab(self):
        """Create list projects tab."""
        frame = ttk.Frame(self)
        
        # Toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            toolbar,
            text="Refresh",
            command=self.refresh_projects
        ).pack(side=tk.LEFT, padx=2)
        
        # Projects list
        list_frame = ttk.LabelFrame(frame, text="Projects", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for projects
        columns = ("Name", "Language", "Framework", "Path")
        self.projects_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.projects_tree.heading(col, text=col)
            self.projects_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.projects_tree.yview)
        self.projects_tree.configure(yscrollcommand=scrollbar.set)
        
        self.projects_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load projects on creation
        self.refresh_projects()
        
        return frame
    
    def browse_project_path(self):
        """Browse for project path."""
        path = self.select_directory("Select Project Location")
        if path:
            self.project_path.set(path)
    
    def browse_detect_path(self):
        """Browse for detection path."""
        path = self.select_directory("Select Project to Detect")
        if path:
            self.detect_path.set(path)
    
    def create_project(self):
        """Create new project."""
        name = self.project_name.get().strip()
        language = self.project_language.get()
        framework = self.project_framework.get() or None
        path = self.project_path.get().strip()
        
        if not name:
            self.show_error("Validation Error", "Project name is required")
            return
        
        if not language:
            self.show_error("Validation Error", "Language is required")
            return
        
        self.new_project_output.clear()
        self.new_project_output.append(f"Creating project '{name}'...")
        
        def create():
            return self.uaide.new_project(
                name=name,
                language=language,
                framework=framework,
                path=path if path else None
            )
        
        def callback(result, error=None):
            if error:
                self.new_project_output.append(f"❌ Error: {error}")
                self.show_error("Creation Failed", error)
            elif result and result.success:
                self.new_project_output.append(f"✅ {result.message}")
                self.new_project_output.append(f"Path: {result.data.get('project_path', 'N/A')}")
                self.show_success("Success", result.message)
                self.refresh_projects()
            else:
                msg = result.message if result else "Unknown error"
                self.new_project_output.append(f"❌ {msg}")
                self.show_error("Creation Failed", msg)
        
        run_async(create, callback)
    
    def detect_project(self):
        """Detect existing project."""
        path = self.detect_path.get().strip()
        
        if not path:
            self.show_error("Validation Error", "Project path is required")
            return
        
        self.detect_output.clear()
        self.detect_output.append(f"Detecting project at: {path}")
        
        def detect():
            return self.uaide.project_manager.detect_project(path)
        
        def callback(result, error=None):
            if error:
                self.detect_output.append(f"❌ Error: {error}")
                self.show_error("Detection Failed", error)
            elif result:
                self.detect_output.append(f"✅ Project detected!")
                self.detect_output.append(f"Name: {result.name}")
                self.detect_output.append(f"Language: {result.language}")
                self.detect_output.append(f"Framework: {result.framework or 'None'}")
                self.detect_output.append(f"Dependencies: {len(result.dependencies)}")
                self.detect_output.append(f"Config files: {', '.join(result.config_files)}")
            else:
                self.detect_output.append("❌ No project detected at this path")
                self.show_info("Not Found", "No project detected at the specified path")
        
        run_async(detect, callback)
    
    def refresh_projects(self):
        """Refresh projects list."""
        # Clear existing items
        for item in self.projects_tree.get_children():
            self.projects_tree.delete(item)
        
        # Get projects from database
        try:
            projects = self.uaide.database.list_projects()
            for project in projects:
                self.projects_tree.insert("", tk.END, values=(
                    project.get("name", ""),
                    project.get("language", ""),
                    project.get("framework", ""),
                    project.get("path", "")
                ))
        except Exception as e:
            self.show_error("Error", f"Failed to load projects: {e}")
