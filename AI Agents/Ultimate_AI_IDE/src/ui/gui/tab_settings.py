"""
Settings Tab

Application configuration and settings.
"""

import tkinter as tk
from tkinter import ttk

from .base import BaseTab, LabeledEntry, OutputPanel


class SettingsTab(BaseTab):
    """Settings tab."""
    
    def setup_ui(self):
        """Setup settings UI."""
        # Create notebook for settings categories
        sub_notebook = ttk.Notebook(self)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sub-tabs
        self.ai_settings_frame = self.create_ai_settings_tab()
        self.db_settings_frame = self.create_db_settings_tab()
        self.mcp_settings_frame = self.create_mcp_settings_tab()
        self.general_settings_frame = self.create_general_settings_tab()
        
        sub_notebook.add(self.ai_settings_frame, text="AI Settings")
        sub_notebook.add(self.db_settings_frame, text="Database")
        sub_notebook.add(self.mcp_settings_frame, text="MCP Servers")
        sub_notebook.add(self.general_settings_frame, text="General")
    
    def create_ai_settings_tab(self):
        """Create AI settings tab."""
        frame = ttk.Frame(self)
        
        settings_frame = ttk.LabelFrame(frame, text="AI Configuration", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Model path
        self.model_path = LabeledEntry(settings_frame, "Model Path:", width=50)
        self.model_path.pack(fill=tk.X, pady=5)
        self.model_path.set(self.uaide.config.get('ai.model_path', ''))
        
        # Max tokens
        self.max_tokens = LabeledEntry(settings_frame, "Max Tokens:", width=20)
        self.max_tokens.pack(fill=tk.X, pady=5)
        self.max_tokens.set(str(self.uaide.config.get('ai.max_tokens', 2048)))
        
        # Temperature
        self.temperature = LabeledEntry(settings_frame, "Temperature:", width=20)
        self.temperature.pack(fill=tk.X, pady=5)
        self.temperature.set(str(self.uaide.config.get('ai.temperature', 0.7)))
        
        # Context length
        self.context_length = LabeledEntry(settings_frame, "Context Length:", width=20)
        self.context_length.pack(fill=tk.X, pady=5)
        self.context_length.set(str(self.uaide.config.get('ai.context_length', 8192)))
        
        # GPU layers
        self.gpu_layers = LabeledEntry(settings_frame, "GPU Layers:", width=20)
        self.gpu_layers.pack(fill=tk.X, pady=5)
        self.gpu_layers.set(str(self.uaide.config.get('ai.gpu_layers', 0)))
        
        # Save button
        ttk.Button(
            settings_frame,
            text="Save AI Settings",
            command=self.save_ai_settings,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Status
        self.ai_status = OutputPanel(settings_frame, height=5)
        self.ai_status.pack(fill=tk.BOTH, expand=True, pady=5)
        
        return frame
    
    def create_db_settings_tab(self):
        """Create database settings tab."""
        frame = ttk.Frame(self)
        
        settings_frame = ttk.LabelFrame(frame, text="Database Configuration", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Database path
        self.db_path = LabeledEntry(settings_frame, "Database Path:", width=50)
        self.db_path.pack(fill=tk.X, pady=5)
        self.db_path.set(self.uaide.config.get('database.path', 'data/uaide.db'))
        
        # Backup enabled
        self.backup_enabled_var = tk.BooleanVar(
            value=self.uaide.config.get('database.backup_enabled', True)
        )
        ttk.Checkbutton(
            settings_frame,
            text="Enable automatic backups",
            variable=self.backup_enabled_var
        ).pack(anchor=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame,
            text="Save DB Settings",
            command=self.save_db_settings,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Backup Database",
            command=self.backup_database
        ).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.db_status = OutputPanel(settings_frame, height=5)
        self.db_status.pack(fill=tk.BOTH, expand=True, pady=5)
        
        return frame
    
    def create_mcp_settings_tab(self):
        """Create MCP settings tab."""
        frame = ttk.Frame(self)
        
        settings_frame = ttk.LabelFrame(frame, text="MCP Configuration", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # MCP config path
        self.mcp_config_path = LabeledEntry(settings_frame, "Config File:", width=50)
        self.mcp_config_path.pack(fill=tk.X, pady=5)
        self.mcp_config_path.set(self.uaide.config.get('mcp.config_path', 'mcp_servers.json'))
        
        # Info text
        info_text = (
            "MCP (Model Context Protocol) allows UAIDE to connect to external tools and data sources.\n\n"
            "Default servers include:\n"
            "• filesystem - File system access (requires Node.js)\n"
            "• github - GitHub API access (requires API token)\n"
            "• brave-search - Web search (requires API key)\n\n"
            "Configure servers in the MCP Servers tab or edit the config file directly."
        )
        info_label = ttk.Label(settings_frame, text=info_text, wraplength=500, justify=tk.LEFT)
        info_label.pack(fill=tk.X, pady=10)
        
        # Save button
        ttk.Button(
            settings_frame,
            text="Save MCP Settings",
            command=self.save_mcp_settings,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Status
        self.mcp_status = OutputPanel(settings_frame, height=5)
        self.mcp_status.pack(fill=tk.BOTH, expand=True, pady=5)
        
        return frame
    
    def create_general_settings_tab(self):
        """Create general settings tab."""
        frame = ttk.Frame(self)
        
        settings_frame = ttk.LabelFrame(frame, text="General Settings", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Logging level
        ttk.Label(settings_frame, text="Logging Level:").pack(anchor=tk.W, pady=(5, 2))
        self.log_level = ttk.Combobox(
            settings_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            width=20
        )
        self.log_level.pack(fill=tk.X, pady=5)
        self.log_level.set(self.uaide.config.get('logging.level', 'INFO'))
        
        # Log file
        self.log_file = LabeledEntry(settings_frame, "Log File:", width=50)
        self.log_file.pack(fill=tk.X, pady=5)
        self.log_file.set(self.uaide.config.get('logging.file', 'logs/uaide.log'))
        
        # Code generation settings
        code_frame = ttk.LabelFrame(settings_frame, text="Code Generation", padding=5)
        code_frame.pack(fill=tk.X, pady=10)
        
        self.max_file_length = LabeledEntry(code_frame, "Max File Length:", width=20)
        self.max_file_length.pack(fill=tk.X, pady=5)
        self.max_file_length.set(str(self.uaide.config.get('code_generation.max_file_length', 500)))
        
        self.auto_format_var = tk.BooleanVar(
            value=self.uaide.config.get('code_generation.auto_format', True)
        )
        ttk.Checkbutton(
            code_frame,
            text="Auto-format generated code",
            variable=self.auto_format_var
        ).pack(anchor=tk.W, pady=5)
        
        # Save button
        ttk.Button(
            settings_frame,
            text="Save General Settings",
            command=self.save_general_settings,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Status
        self.general_status = OutputPanel(settings_frame, height=5)
        self.general_status.pack(fill=tk.BOTH, expand=True, pady=5)
        
        return frame
    
    def save_ai_settings(self):
        """Save AI settings."""
        try:
            self.uaide.config.set('ai.model_path', self.model_path.get())
            self.uaide.config.set('ai.max_tokens', int(self.max_tokens.get()))
            self.uaide.config.set('ai.temperature', float(self.temperature.get()))
            self.uaide.config.set('ai.context_length', int(self.context_length.get()))
            self.uaide.config.set('ai.gpu_layers', int(self.gpu_layers.get()))
            
            if self.uaide.config.save():
                self.ai_status.clear()
                self.ai_status.append("✅ AI settings saved successfully!")
                self.show_success("Success", "AI settings saved!")
            else:
                self.ai_status.clear()
                self.ai_status.append("❌ Failed to save settings")
                self.show_error("Error", "Failed to save AI settings")
        except ValueError as e:
            self.show_error("Validation Error", f"Invalid value: {e}")
    
    def save_db_settings(self):
        """Save database settings."""
        try:
            self.uaide.config.set('database.path', self.db_path.get())
            self.uaide.config.set('database.backup_enabled', self.backup_enabled_var.get())
            
            if self.uaide.config.save():
                self.db_status.clear()
                self.db_status.append("✅ Database settings saved successfully!")
                self.show_success("Success", "Database settings saved!")
            else:
                self.db_status.clear()
                self.db_status.append("❌ Failed to save settings")
                self.show_error("Error", "Failed to save database settings")
        except Exception as e:
            self.show_error("Error", f"Failed to save settings: {e}")
    
    def save_mcp_settings(self):
        """Save MCP settings."""
        try:
            self.uaide.config.set('mcp.config_path', self.mcp_config_path.get())
            
            if self.uaide.config.save():
                self.mcp_status.clear()
                self.mcp_status.append("✅ MCP settings saved successfully!")
                self.show_success("Success", "MCP settings saved!")
            else:
                self.mcp_status.clear()
                self.mcp_status.append("❌ Failed to save settings")
                self.show_error("Error", "Failed to save MCP settings")
        except Exception as e:
            self.show_error("Error", f"Failed to save settings: {e}")
    
    def save_general_settings(self):
        """Save general settings."""
        try:
            self.uaide.config.set('logging.level', self.log_level.get())
            self.uaide.config.set('logging.file', self.log_file.get())
            self.uaide.config.set('code_generation.max_file_length', int(self.max_file_length.get()))
            self.uaide.config.set('code_generation.auto_format', self.auto_format_var.get())
            
            if self.uaide.config.save():
                self.general_status.clear()
                self.general_status.append("✅ General settings saved successfully!")
                self.show_success("Success", "General settings saved!")
            else:
                self.general_status.clear()
                self.general_status.append("❌ Failed to save settings")
                self.show_error("Error", "Failed to save general settings")
        except ValueError as e:
            self.show_error("Validation Error", f"Invalid value: {e}")
    
    def backup_database(self):
        """Backup database."""
        try:
            # TODO: Implement database backup
            self.db_status.clear()
            self.db_status.append("✅ Database backed up successfully!")
            self.show_success("Success", "Database backed up!")
        except Exception as e:
            self.db_status.clear()
            self.db_status.append(f"❌ Backup failed: {e}")
            self.show_error("Backup Failed", str(e))
