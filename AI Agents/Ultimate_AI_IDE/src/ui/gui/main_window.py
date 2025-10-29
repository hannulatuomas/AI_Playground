"""
Main GUI Window

Main application window with menu bar and tab container.
"""

import sys
from pathlib import Path
from typing import Optional

# Check if tkinter is available
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError as e:
    # Re-raise as ImportError so it can be caught by ui/__init__.py
    # This allows CLI to work without tkinter
    raise ImportError(
        "tkinter is not installed. GUI requires tkinter. "
        "Use CLI interface instead or install tkinter."
    ) from e

from ...core.orchestrator import UAIDE
from .tab_project import ProjectTab
from .tab_code import CodeTab
from .tab_test import TestTab
from .tab_docs import DocsTab
from .tab_refactor import RefactorTab
from .tab_chat import ChatTab
from .tab_mcp import MCPTab
from .tab_quality import QualityTab
from .tab_workflow import WorkflowTab
from .tab_filemanagement import FileManagementTab
from .tab_codeanalysis import CodeAnalysisTab
from .tab_automation import AutomationTab
from .tab_security import SecurityTab
from .tab_dependencies import DependenciesTab
from .tab_template import TemplateTab
from .tab_rag import RAGTab
from .tab_settings import SettingsTab


class UAIDEApp:
    """Main UAIDE GUI Application."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize UAIDE GUI.
        
        Args:
            config_path: Optional path to config file
        """
        self.root = tk.Tk()
        self.root.title("UAIDE - Ultimate AI-Powered IDE")
        self.root.geometry("1200x800")
        
        # Initialize UAIDE backend
        try:
            self.uaide = UAIDE(config_path)
        except Exception as e:
            messagebox.showerror(
                "Initialization Error",
                f"Failed to initialize UAIDE:\n{e}"
            )
            sys.exit(1)
        
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
    
    def setup_ui(self):
        """Setup main UI components."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.project_tab = ProjectTab(self.notebook, self.uaide)
        self.code_tab = CodeTab(self.notebook, self.uaide)
        self.test_tab = TestTab(self.notebook, self.uaide)
        self.docs_tab = DocsTab(self.notebook, self.uaide)
        self.refactor_tab = RefactorTab(self.notebook, self.uaide)
        self.chat_tab = ChatTab(self.notebook, self.uaide)
        self.mcp_tab = MCPTab(self.notebook, self.uaide)
        self.quality_tab = QualityTab(self.notebook, self.uaide)
        # v1.4.0 tabs
        self.workflow_tab = WorkflowTab(self.notebook, self.uaide)
        self.filemanagement_tab = FileManagementTab(self.notebook, self.uaide)
        self.codeanalysis_tab = CodeAnalysisTab(self.notebook, self.uaide)
        self.automation_tab = AutomationTab(self.notebook, self.uaide)
        # v1.5.0 tabs
        self.security_tab = SecurityTab(self.notebook, self.uaide)
        self.dependencies_tab = DependenciesTab(self.notebook, self.uaide)
        self.template_tab = TemplateTab(self.notebook, self.uaide)
        # v1.6.0 tabs
        self.rag_tab = RAGTab(self.notebook, self.uaide)
        self.settings_tab = SettingsTab(self.notebook, self.uaide)
        
        # Add tabs to notebook
        self.notebook.add(self.project_tab, text="📁 Projects")
        self.notebook.add(self.code_tab, text="💻 Code Generation")
        self.notebook.add(self.test_tab, text="🧪 Testing")
        self.notebook.add(self.docs_tab, text="📚 Documentation")
        self.notebook.add(self.refactor_tab, text="🔧 Refactoring")
        self.notebook.add(self.chat_tab, text="💬 AI Chat")
        self.notebook.add(self.mcp_tab, text="🔌 MCP Servers")
        self.notebook.add(self.quality_tab, text="📊 Quality")
        # v1.4.0 tabs
        self.notebook.add(self.workflow_tab, text="🔄 Workflows")
        self.notebook.add(self.filemanagement_tab, text="📂 File Management")
        self.notebook.add(self.codeanalysis_tab, text="🔍 Code Analysis")
        self.notebook.add(self.automation_tab, text="⚡ Automation")
        # v1.5.0 tabs
        self.notebook.add(self.security_tab, text="🔒 Security")
        self.notebook.add(self.dependencies_tab, text="📦 Dependencies")
        self.notebook.add(self.template_tab, text="✨ Template")
        # v1.6.0 tabs
        self.notebook.add(self.rag_tab, text="🧠 Advanced RAG")
        self.notebook.add(self.settings_tab, text="⚙️ Settings")
    
    def setup_menu(self):
        """Setup menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Generate Tests", command=self.goto_tests)
        tools_menu.add_command(label="Generate Docs", command=self.goto_docs)
        tools_menu.add_command(label="Refactor Code", command=self.goto_refactor)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Documentation", command=self.show_docs)
    
    def setup_statusbar(self):
        """Setup status bar."""
        self.statusbar = ttk.Label(
            self.root, 
            text="Ready", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status(self, message: str):
        """Update status bar message."""
        self.statusbar.config(text=message)
    
    def new_project(self):
        """Navigate to new project tab."""
        self.notebook.select(self.project_tab)
    
    def open_project(self):
        """Navigate to project tab."""
        self.notebook.select(self.project_tab)
    
    def goto_tests(self):
        """Navigate to testing tab."""
        self.notebook.select(self.test_tab)
    
    def goto_docs(self):
        """Navigate to documentation tab."""
        self.notebook.select(self.docs_tab)
    
    def goto_refactor(self):
        """Navigate to refactoring tab."""
        self.notebook.select(self.refactor_tab)
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About UAIDE",
            "UAIDE - Ultimate AI-Powered IDE\n\n"
            "Version: 0.1.0\n\n"
            "An AI-powered development environment with:\n"
            "• Project Management\n"
            "• Code Generation\n"
            "• Automated Testing\n"
            "• Documentation Generation\n"
            "• Code Refactoring\n"
            "• AI Chat Assistant"
        )
    
    def show_docs(self):
        """Show documentation."""
        docs_path = Path("docs/README.md")
        if docs_path.exists():
            messagebox.showinfo(
                "Documentation",
                f"Documentation available at:\n{docs_path.absolute()}"
            )
        else:
            messagebox.showinfo(
                "Documentation",
                "Documentation not found.\n"
                "Please check the docs/ directory."
            )
    
    def quit_app(self):
        """Quit application."""
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.root.quit()
    
    def run(self):
        """Run the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point for GUI."""
    app = UAIDEApp()
    app.run()


if __name__ == "__main__":
    main()
