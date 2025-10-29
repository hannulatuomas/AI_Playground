"""
Graphical User Interface (GUI) for AI Coding Assistant

Optional lightweight GUI using tkinter.
Provides fields for input, buttons for actions, and display area for results.
"""

import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
from typing import Optional
import threading

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import (
    LLMInterface,
    PromptEngine,
    LearningDB,
    load_config_from_file,
    ModelManager
)
from features import CodeGenerator, Debugger, LanguageSupport


class GUI:
    """
    Graphical User Interface for AI Coding Assistant.
    
    Lightweight tkinter-based GUI with intuitive layout.
    Provides code generation and debugging functionality.
    """

    def __init__(self, root):
        """
        Initialize GUI.
        
        Args:
            root: tkinter root window
        """
        self.root = root
        self.root.title("AI Coding Assistant")
        self.root.geometry("900x700")
        
        # Components
        self.config = None
        self.llm = None
        self.db = None
        self.engine = None
        self.generator = None
        self.debugger = None
        self.lang_support = None
        self.model_manager = None
        
        # State
        self.last_interaction_id = None
        self.last_mode = None  # 'generate' or 'debug'
        
        # Create UI
        self.create_widgets()
        
        # Initialize components
        self.initialize_components()

    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Output area expands
        
        # === Header ===
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame,
            text="🤖 AI Coding Assistant",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Powered by llama.cpp",
            font=('Arial', 9),
            foreground='gray'
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Status indicator
        self.status_label = ttk.Label(
            header_frame,
            text="● Not initialized",
            foreground='red'
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # === Mode Selection ===
        mode_frame = ttk.LabelFrame(main_frame, text="Mode", padding="10")
        mode_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.mode_var = tk.StringVar(value="generate")
        
        ttk.Radiobutton(
            mode_frame,
            text="Code Generation",
            variable=self.mode_var,
            value="generate",
            command=self.on_mode_change
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Radiobutton(
            mode_frame,
            text="Debugging",
            variable=self.mode_var,
            value="debug",
            command=self.on_mode_change
        ).pack(side=tk.LEFT)
        
        # === Input Area ===
        input_frame = ttk.LabelFrame(main_frame, text="Input", padding="10")
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Language selection
        ttk.Label(input_frame, text="Language:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.language_var = tk.StringVar()
        self.language_combo = ttk.Combobox(
            input_frame,
            textvariable=self.language_var,
            width=20,
            state='readonly'
        )
        self.language_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Task/Code input (changes based on mode)
        self.input_label = ttk.Label(input_frame, text="Task:")
        self.input_label.grid(row=1, column=0, sticky=(tk.W, tk.N), pady=5)
        
        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            height=6,
            wrap=tk.WORD,
            font=('Consolas', 10)
        )
        self.input_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Error message (only for debug mode)
        self.error_label = ttk.Label(input_frame, text="Error Message:")
        self.error_entry = ttk.Entry(input_frame)
        
        # Action buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        self.action_button = ttk.Button(
            button_frame,
            text="Generate Code",
            command=self.on_action,
            width=20
        )
        self.action_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Clear",
            command=self.on_clear,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # === Output Area ===
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            state='disabled'
        )
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add tags for colored output
        self.output_text.tag_config('success', foreground='green')
        self.output_text.tag_config('error', foreground='red')
        self.output_text.tag_config('info', foreground='blue')
        self.output_text.tag_config('heading', font=('Consolas', 11, 'bold'))
        
        # === Feedback Area ===
        feedback_frame = ttk.LabelFrame(main_frame, text="Feedback", padding="10")
        feedback_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(feedback_frame, text="Did this work?").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            feedback_frame,
            text="✓ Yes",
            command=lambda: self.on_feedback(True),
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            feedback_frame,
            text="✗ No",
            command=lambda: self.on_feedback(False),
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        self.feedback_entry = ttk.Entry(feedback_frame, width=40)
        self.feedback_entry.pack(side=tk.LEFT, padx=(10, 5))
        ttk.Label(feedback_frame, text="(optional)").pack(side=tk.LEFT)

    def initialize_components(self):
        """Initialize all components."""
        try:
            self.append_output("Initializing components...\n", 'info')
            
            # Load configuration
            self.config = load_config_from_file()
            if not self.config:
                self.append_output("✗ Configuration not found\n", 'error')
                self.append_output("  Run: python main.py --setup\n")
                return
            
            # Initialize database
            self.db = LearningDB()
            
            # Initialize prompt engine
            self.engine = PromptEngine(learning_db=self.db)
            
            # Initialize LLM
            self.llm = LLMInterface(self.config)
            
            # Initialize features
            self.generator = CodeGenerator(self.llm, self.engine, self.db)
            self.debugger = Debugger(self.llm, self.engine, self.db)
            self.lang_support = LanguageSupport()
            
            # Initialize model manager
            try:
                self.model_manager = ModelManager()
                self.append_output("✓ Model manager ready\n", 'success')
            except Exception as e:
                self.append_output(f"⚠ Model manager not available: {e}\n", 'error')
            
            # Populate language dropdown
            languages = self.lang_support.get_supported_languages()
            self.language_combo['values'] = languages
            if languages:
                self.language_combo.current(0)
            
            # Update status
            self.status_label.config(text="● Ready", foreground='green')
            self.append_output("✓ All components initialized!\n", 'success')
            self.append_output("\nReady to generate code or debug!\n", 'info')
            
        except Exception as e:
            self.append_output(f"✗ Initialization failed: {e}\n", 'error')
            self.status_label.config(text="● Error", foreground='red')

    def on_mode_change(self):
        """Handle mode change (generate/debug)."""
        mode = self.mode_var.get()
        
        if mode == "generate":
            # Update UI for generation mode
            self.input_label.config(text="Task:")
            self.input_text.delete('1.0', tk.END)
            self.input_text.insert('1.0', "Create a function to...")
            self.action_button.config(text="Generate Code")
            
            # Hide error message field
            self.error_label.grid_remove()
            self.error_entry.grid_remove()
            
        else:  # debug
            # Update UI for debug mode
            self.input_label.config(text="Code:")
            self.input_text.delete('1.0', tk.END)
            self.input_text.insert('1.0', "# Paste your code here")
            self.action_button.config(text="Debug Code")
            
            # Show error message field
            self.error_label.grid(row=2, column=0, sticky=tk.W, pady=5)
            self.error_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))

    def append_output(self, text: str, tag: Optional[str] = None):
        """
        Append text to output area.
        
        Args:
            text: Text to append
            tag: Optional tag for styling
        """
        self.output_text.config(state='normal')
        if tag:
            self.output_text.insert(tk.END, text, tag)
        else:
            self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')

    def clear_output(self):
        """Clear output area."""
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.config(state='disabled')

    def on_action(self):
        """Handle action button (generate or debug)."""
        mode = self.mode_var.get()
        
        if mode == "generate":
            self.on_generate()
        else:
            self.on_debug()

    def on_generate(self):
        """Handle code generation."""
        # Get inputs
        language = self.language_var.get()
        task = self.input_text.get('1.0', tk.END).strip()
        
        if not language:
            messagebox.showwarning("Input Required", "Please select a language")
            return
        
        if not task or task == "Create a function to...":
            messagebox.showwarning("Input Required", "Please enter a task description")
            return
        
        # Clear output
        self.clear_output()
        self.append_output(f"→ Generating {language} code...\n\n", 'info')
        self.status_label.config(text="● Generating...", foreground='orange')
        self.root.update()
        
        try:
            # Generate code
            result = self.generator.generate_code(task=task, language=language)
            
            if result['success']:
                # Display code
                self.append_output("Generated Code:\n", 'heading')
                self.append_output("-" * 70 + "\n")
                self.append_output(result['code'] + "\n")
                self.append_output("-" * 70 + "\n\n")
                
                # Display explanation
                if result['explanation']:
                    self.append_output("Explanation:\n", 'heading')
                    self.append_output(result['explanation'] + "\n\n")
                
                # Display framework
                if result['framework']:
                    self.append_output(f"✓ Framework detected: {result['framework']}\n", 'success')
                
                # Store for feedback
                self.last_interaction_id = result['interaction_id']
                self.last_mode = 'generate'
                
                self.status_label.config(text="● Ready", foreground='green')
            else:
                self.append_output(f"✗ Generation failed: {result['error']}\n", 'error')
                self.status_label.config(text="● Error", foreground='red')
                
        except Exception as e:
            self.append_output(f"✗ Error: {e}\n", 'error')
            self.status_label.config(text="● Error", foreground='red')

    def on_debug(self):
        """Handle code debugging."""
        # Get inputs
        language = self.language_var.get()
        code = self.input_text.get('1.0', tk.END).strip()
        error_msg = self.error_entry.get().strip()
        
        if not language:
            messagebox.showwarning("Input Required", "Please select a language")
            return
        
        if not code or code == "# Paste your code here":
            messagebox.showwarning("Input Required", "Please enter code to debug")
            return
        
        # Clear output
        self.clear_output()
        self.append_output(f"→ Debugging {language} code...\n\n", 'info')
        self.status_label.config(text="● Debugging...", foreground='orange')
        self.root.update()
        
        try:
            # Debug code
            result = self.debugger.debug_code(
                code=code,
                language=language,
                error_msg=error_msg if error_msg else None
            )
            
            if result['success']:
                # Display fixed code
                self.append_output("Fixed Code:\n", 'heading')
                self.append_output("-" * 70 + "\n")
                self.append_output(result['fixed_code'] + "\n")
                self.append_output("-" * 70 + "\n\n")
                
                # Display explanation
                if result['explanation']:
                    self.append_output("Explanation:\n", 'heading')
                    self.append_output(result['explanation'] + "\n\n")
                
                # Display changes
                if result['changes']:
                    self.append_output("Changes Made:\n", 'heading')
                    for i, change in enumerate(result['changes'], 1):
                        self.append_output(f"  {i}. {change}\n")
                
                # Store for feedback
                self.last_interaction_id = result['interaction_id']
                self.last_mode = 'debug'
                
                self.status_label.config(text="● Ready", foreground='green')
            else:
                self.append_output(f"✗ Debugging failed: {result['error']}\n", 'error')
                self.status_label.config(text="● Error", foreground='red')
                
        except Exception as e:
            self.append_output(f"✗ Error: {e}\n", 'error')
            self.status_label.config(text="● Error", foreground='red')

    def on_clear(self):
        """Clear all input and output."""
        self.input_text.delete('1.0', tk.END)
        self.error_entry.delete(0, tk.END)
        self.feedback_entry.delete(0, tk.END)
        self.clear_output()
        
        # Reset placeholder text
        if self.mode_var.get() == "generate":
            self.input_text.insert('1.0', "Create a function to...")
        else:
            self.input_text.insert('1.0', "# Paste your code here")

    def on_feedback(self, success: bool):
        """
        Handle feedback submission.
        
        Args:
            success: Whether the result was successful
        """
        if not self.last_interaction_id:
            messagebox.showinfo("No Action", "No recent action to provide feedback for")
            return
        
        # Get optional feedback text
        feedback_text = self.feedback_entry.get().strip()
        
        try:
            # Submit feedback
            if self.last_mode == 'generate':
                self.generator.provide_feedback(
                    interaction_id=self.last_interaction_id,
                    success=success,
                    feedback=feedback_text if feedback_text else None
                )
            else:  # debug
                self.debugger.provide_feedback(
                    interaction_id=self.last_interaction_id,
                    success=success,
                    feedback=feedback_text if feedback_text else None
                )
            
            # Show confirmation
            result_text = "worked" if success else "didn't work"
            messagebox.showinfo("Feedback Recorded", f"Thank you! Feedback that it {result_text} has been recorded.")
            
            # Clear feedback entry
            self.feedback_entry.delete(0, tk.END)
            
            # Reset interaction ID
            self.last_interaction_id = None
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record feedback: {e}")


def main():
    """Entry point for GUI."""
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
