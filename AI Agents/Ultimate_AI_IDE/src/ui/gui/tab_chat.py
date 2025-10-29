"""
AI Chat Tab

Interactive AI chat interface.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext

from .base import BaseTab, run_async


class ChatTab(BaseTab):
    """AI chat tab."""
    
    def setup_ui(self):
        """Setup chat UI."""
        # Chat history
        history_frame = ttk.LabelFrame(self, text="Chat History", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chat_history = scrolledtext.ScrolledText(
            history_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=20
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for styling
        self.chat_history.tag_config("user", foreground="blue", font=("Arial", 10, "bold"))
        self.chat_history.tag_config("ai", foreground="green", font=("Arial", 10))
        self.chat_history.tag_config("system", foreground="gray", font=("Arial", 9, "italic"))
        
        # Input area
        input_frame = ttk.Frame(self)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Message input
        self.message_input = scrolledtext.ScrolledText(
            input_frame,
            height=4,
            wrap=tk.WORD
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.message_input.bind("<Control-Return>", lambda e: self.send_message())
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(
            button_frame,
            text="Send",
            command=self.send_message,
            style="Accent.TButton"
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_chat
        ).pack(fill=tk.X, pady=2)
        
        # Welcome message
        self.append_system_message("Welcome to UAIDE AI Chat! Ask me anything about your code.")
        self.append_system_message("Tip: Press Ctrl+Enter to send messages quickly.")
    
    def append_message(self, sender: str, message: str, tag: str):
        """Append message to chat history."""
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"{sender}: ", tag)
        self.chat_history.insert(tk.END, f"{message}\n\n")
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)
    
    def append_user_message(self, message: str):
        """Append user message."""
        self.append_message("You", message, "user")
    
    def append_ai_message(self, message: str):
        """Append AI message."""
        self.append_message("AI", message, "ai")
    
    def append_system_message(self, message: str):
        """Append system message."""
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"[{message}]\n\n", "system")
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)
    
    def send_message(self):
        """Send message to AI."""
        message = self.message_input.get("1.0", tk.END).strip()
        
        if not message:
            return
        
        # Clear input
        self.message_input.delete("1.0", tk.END)
        
        # Add user message to history
        self.append_user_message(message)
        
        # Show thinking indicator
        self.append_system_message("AI is thinking...")
        
        def query():
            response = self.uaide.ai_backend.query(message)
            return response
        
        def callback(result, error=None):
            # Remove thinking indicator
            self.chat_history.config(state=tk.NORMAL)
            # Delete last line (thinking message)
            self.chat_history.delete("end-3l", "end-1l")
            self.chat_history.config(state=tk.DISABLED)
            
            if error:
                self.append_system_message(f"Error: {error}")
                self.show_error("Chat Error", error)
            elif result:
                self.append_ai_message(result)
            else:
                self.append_system_message("No response from AI")
        
        run_async(query, callback)
    
    def clear_chat(self):
        """Clear chat history."""
        if self.ask_yes_no("Clear Chat", "Are you sure you want to clear the chat history?"):
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.delete("1.0", tk.END)
            self.chat_history.config(state=tk.DISABLED)
            self.append_system_message("Chat cleared. How can I help you?")
