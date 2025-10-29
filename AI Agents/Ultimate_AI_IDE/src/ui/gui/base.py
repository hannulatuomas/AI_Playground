"""
Base GUI Components and Utilities

Provides reusable GUI components and helper functions.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import Callable, Optional, Any
import threading


class BaseTab(ttk.Frame):
    """Base class for all GUI tabs."""
    
    def __init__(self, parent, uaide_instance):
        """
        Initialize base tab.
        
        Args:
            parent: Parent widget
            uaide_instance: UAIDE orchestrator instance
        """
        super().__init__(parent)
        self.uaide = uaide_instance
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement setup_ui()")
    
    def show_error(self, title: str, message: str):
        """Show error message dialog."""
        messagebox.showerror(title, message)
    
    def show_info(self, title: str, message: str):
        """Show info message dialog."""
        messagebox.showinfo(title, message)
    
    def show_success(self, title: str, message: str):
        """Show success message dialog."""
        messagebox.showinfo(title, message)
    
    def ask_yes_no(self, title: str, message: str) -> bool:
        """Ask yes/no question."""
        return messagebox.askyesno(title, message)
    
    def select_directory(self, title: str = "Select Directory") -> Optional[str]:
        """Open directory selection dialog."""
        return filedialog.askdirectory(title=title)
    
    def select_file(self, title: str = "Select File", 
                   filetypes: list = None) -> Optional[str]:
        """Open file selection dialog."""
        if filetypes is None:
            filetypes = [("All files", "*.*")]
        return filedialog.askopenfilename(title=title, filetypes=filetypes)


class LabeledEntry(ttk.Frame):
    """Entry widget with label."""
    
    def __init__(self, parent, label: str, **kwargs):
        super().__init__(parent)
        
        ttk.Label(self, text=label).pack(side=tk.LEFT, padx=(0, 5))
        self.entry = ttk.Entry(self, **kwargs)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def get(self) -> str:
        """Get entry value."""
        return self.entry.get()
    
    def set(self, value: str):
        """Set entry value."""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
    
    def clear(self):
        """Clear entry."""
        self.entry.delete(0, tk.END)


class LabeledCombobox(ttk.Frame):
    """Combobox widget with label."""
    
    def __init__(self, parent, label: str, values: list, **kwargs):
        super().__init__(parent)
        
        ttk.Label(self, text=label).pack(side=tk.LEFT, padx=(0, 5))
        self.combobox = ttk.Combobox(self, values=values, **kwargs)
        self.combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if values:
            self.combobox.current(0)
    
    def get(self) -> str:
        """Get selected value."""
        return self.combobox.get()
    
    def set(self, value: str):
        """Set selected value."""
        self.combobox.set(value)


class OutputPanel(ttk.Frame):
    """Scrolled text output panel."""
    
    def __init__(self, parent, height: int = 10):
        super().__init__(parent)
        
        self.text = scrolledtext.ScrolledText(
            self, 
            height=height, 
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.text.pack(fill=tk.BOTH, expand=True)
    
    def append(self, text: str):
        """Append text to output."""
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, text + "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)
    
    def clear(self):
        """Clear output."""
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)
    
    def get_text(self) -> str:
        """Get all text."""
        return self.text.get(1.0, tk.END)


def run_async(func: Callable, callback: Optional[Callable] = None):
    """
    Run function in background thread.
    
    Args:
        func: Function to run
        callback: Optional callback with result
    """
    def wrapper():
        try:
            result = func()
            if callback:
                callback(result)
        except Exception as e:
            if callback:
                callback(None, error=str(e))
    
    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
