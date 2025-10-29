"""
MCP Tab

MCP (Model Context Protocol) server management and tool execution.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import json

from .base import BaseTab, LabeledEntry, LabeledCombobox, OutputPanel, run_async


class MCPTab(BaseTab):
    """MCP server management tab."""
    
    def setup_ui(self):
        """Setup MCP UI."""
        # Create notebook for sub-tabs
        sub_notebook = ttk.Notebook(self)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sub-tabs
        self.servers_frame = self.create_servers_tab()
        self.tools_frame = self.create_tools_tab()
        self.resources_frame = self.create_resources_tab()
        
        sub_notebook.add(self.servers_frame, text="Servers")
        sub_notebook.add(self.tools_frame, text="Tools")
        sub_notebook.add(self.resources_frame, text="Resources")
    
    def create_servers_tab(self):
        """Create servers management tab."""
        frame = ttk.Frame(self)
        
        # Toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            toolbar,
            text="Refresh",
            command=self.refresh_servers
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            toolbar,
            text="Start Selected",
            command=self.start_selected_server
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            toolbar,
            text="Stop Selected",
            command=self.stop_selected_server
        ).pack(side=tk.LEFT, padx=2)
        
        # Servers list
        list_frame = ttk.LabelFrame(frame, text="MCP Servers", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for servers
        columns = ("Status", "Name", "Tools", "Resources", "Prompts", "Description")
        self.servers_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        self.servers_tree.heading("Status", text="Status")
        self.servers_tree.heading("Name", text="Name")
        self.servers_tree.heading("Tools", text="Tools")
        self.servers_tree.heading("Resources", text="Resources")
        self.servers_tree.heading("Prompts", text="Prompts")
        self.servers_tree.heading("Description", text="Description")
        
        self.servers_tree.column("Status", width=80)
        self.servers_tree.column("Name", width=120)
        self.servers_tree.column("Tools", width=60)
        self.servers_tree.column("Resources", width=80)
        self.servers_tree.column("Prompts", width=70)
        self.servers_tree.column("Description", width=300)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.servers_tree.yview)
        self.servers_tree.configure(yscrollcommand=scrollbar.set)
        
        self.servers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Output
        output_frame = ttk.LabelFrame(frame, text="Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.servers_output = OutputPanel(output_frame, height=8)
        self.servers_output.pack(fill=tk.BOTH, expand=True)
        
        # Load servers on creation
        self.refresh_servers()
        
        return frame
    
    def create_tools_tab(self):
        """Create tools browser and executor tab."""
        frame = ttk.Frame(self)
        
        # Tools list
        list_frame = ttk.LabelFrame(frame, text="Available Tools", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Toolbar
        toolbar = ttk.Frame(list_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            toolbar,
            text="Refresh",
            command=self.refresh_tools
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(toolbar, text="Filter by server:").pack(side=tk.LEFT, padx=(10, 5))
        self.tools_server_filter = ttk.Combobox(toolbar, width=15, state="readonly")
        self.tools_server_filter.pack(side=tk.LEFT)
        self.tools_server_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_tools())
        
        # Treeview for tools
        columns = ("Name", "Server", "Description")
        self.tools_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        self.tools_tree.heading("Name", text="Tool Name")
        self.tools_tree.heading("Server", text="Server")
        self.tools_tree.heading("Description", text="Description")
        
        self.tools_tree.column("Name", width=150)
        self.tools_tree.column("Server", width=120)
        self.tools_tree.column("Description", width=400)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tools_tree.yview)
        self.tools_tree.configure(yscrollcommand=scrollbar.set)
        
        self.tools_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tool execution
        exec_frame = ttk.LabelFrame(frame, text="Execute Tool", padding=10)
        exec_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tool_name_entry = LabeledEntry(exec_frame, "Tool Name:", width=40)
        self.tool_name_entry.pack(fill=tk.X, pady=5)
        
        self.tool_server_entry = LabeledEntry(exec_frame, "Server:", width=40)
        self.tool_server_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(exec_frame, text="Arguments (JSON):").pack(anchor=tk.W, pady=(5, 2))
        self.tool_args_text = scrolledtext.ScrolledText(exec_frame, height=4, wrap=tk.WORD)
        self.tool_args_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.tool_args_text.insert("1.0", "{}")
        
        ttk.Button(
            exec_frame,
            text="Execute Tool",
            command=self.execute_tool,
            style="Accent.TButton"
        ).pack(pady=5)
        
        # Output
        output_frame = ttk.LabelFrame(frame, text="Tool Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tools_output = OutputPanel(output_frame, height=8)
        self.tools_output.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection to populate execution fields
        self.tools_tree.bind("<<TreeviewSelect>>", self.on_tool_selected)
        
        # Load tools
        self.refresh_tools()
        
        return frame
    
    def create_resources_tab(self):
        """Create resources browser tab."""
        frame = ttk.Frame(self)
        
        # Resources list
        list_frame = ttk.LabelFrame(frame, text="Available Resources", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Toolbar
        toolbar = ttk.Frame(list_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(
            toolbar,
            text="Refresh",
            command=self.refresh_resources
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(toolbar, text="Filter by server:").pack(side=tk.LEFT, padx=(10, 5))
        self.resources_server_filter = ttk.Combobox(toolbar, width=15, state="readonly")
        self.resources_server_filter.pack(side=tk.LEFT)
        self.resources_server_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_resources())
        
        # Treeview for resources
        columns = ("Name", "Server", "URI", "Type", "Description")
        self.resources_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        self.resources_tree.heading("Name", text="Resource Name")
        self.resources_tree.heading("Server", text="Server")
        self.resources_tree.heading("URI", text="URI")
        self.resources_tree.heading("Type", text="MIME Type")
        self.resources_tree.heading("Description", text="Description")
        
        self.resources_tree.column("Name", width=150)
        self.resources_tree.column("Server", width=100)
        self.resources_tree.column("URI", width=200)
        self.resources_tree.column("Type", width=100)
        self.resources_tree.column("Description", width=250)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.resources_tree.yview)
        self.resources_tree.configure(yscrollcommand=scrollbar.set)
        
        self.resources_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Output
        output_frame = ttk.LabelFrame(frame, text="Resource Content", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.resources_output = scrolledtext.ScrolledText(output_frame, height=10, wrap=tk.WORD)
        self.resources_output.pack(fill=tk.BOTH, expand=True)
        
        # Load resources
        self.refresh_resources()
        
        return frame
    
    def refresh_servers(self):
        """Refresh servers list."""
        # Clear existing items
        for item in self.servers_tree.get_children():
            self.servers_tree.delete(item)
        
        def get_status():
            return self.uaide.mcp_manager.get_server_status()
        
        def callback(result, error=None):
            if error:
                self.servers_output.append(f"❌ Error: {error}")
                return
            
            if not result:
                self.servers_output.append("No MCP servers configured")
                return
            
            for name, info in result.items():
                status = "✓ Connected" if info['connected'] else ("✗ Disabled" if not info['enabled'] else "○ Stopped")
                tools = str(info['tools']) if info['connected'] else "-"
                resources = str(info['resources']) if info['connected'] else "-"
                prompts = str(info['prompts']) if info['connected'] else "-"
                
                self.servers_tree.insert("", tk.END, values=(
                    status,
                    name,
                    tools,
                    resources,
                    prompts,
                    info['description']
                ))
            
            self.servers_output.append(f"✅ Loaded {len(result)} servers")
        
        run_async(get_status, callback)
    
    def start_selected_server(self):
        """Start selected server."""
        selection = self.servers_tree.selection()
        if not selection:
            self.show_error("Selection Required", "Please select a server to start")
            return
        
        item = self.servers_tree.item(selection[0])
        server_name = item['values'][1]  # Name column
        
        def start():
            return self.uaide.mcp_manager.start_server(server_name)
        
        def callback(result, error=None):
            if error:
                self.servers_output.append(f"❌ Error starting {server_name}: {error}")
                self.show_error("Start Failed", error)
            elif result:
                self.servers_output.append(f"✅ Started server: {server_name}")
                self.refresh_servers()
                self.refresh_tools()
                self.refresh_resources()
            else:
                self.servers_output.append(f"❌ Failed to start: {server_name}")
        
        run_async(start, callback)
    
    def stop_selected_server(self):
        """Stop selected server."""
        selection = self.servers_tree.selection()
        if not selection:
            self.show_error("Selection Required", "Please select a server to stop")
            return
        
        item = self.servers_tree.item(selection[0])
        server_name = item['values'][1]  # Name column
        
        def stop():
            self.uaide.mcp_manager.stop_server(server_name)
            return True
        
        def callback(result, error=None):
            if error:
                self.servers_output.append(f"❌ Error stopping {server_name}: {error}")
            else:
                self.servers_output.append(f"✅ Stopped server: {server_name}")
                self.refresh_servers()
                self.refresh_tools()
                self.refresh_resources()
        
        run_async(stop, callback)
    
    def refresh_tools(self):
        """Refresh tools list."""
        # Clear existing items
        for item in self.tools_tree.get_children():
            self.tools_tree.delete(item)
        
        def get_tools():
            tools = self.uaide.mcp_manager.get_all_tools()
            servers = list(set([t.server_name for t in tools]))
            return tools, servers
        
        def callback(result, error=None):
            if error:
                self.tools_output.append(f"❌ Error: {error}")
                return
            
            tools, servers = result
            
            # Update server filter
            self.tools_server_filter['values'] = ["All"] + servers
            if not self.tools_server_filter.get():
                self.tools_server_filter.set("All")
            
            # Filter tools
            server_filter = self.tools_server_filter.get()
            if server_filter and server_filter != "All":
                tools = [t for t in tools if t.server_name == server_filter]
            
            for tool in tools:
                self.tools_tree.insert("", tk.END, values=(
                    tool.name,
                    tool.server_name,
                    tool.description
                ))
            
            self.tools_output.append(f"✅ Loaded {len(tools)} tools")
        
        run_async(get_tools, callback)
    
    def on_tool_selected(self, event):
        """Handle tool selection."""
        selection = self.tools_tree.selection()
        if not selection:
            return
        
        item = self.tools_tree.item(selection[0])
        tool_name = item['values'][0]
        server_name = item['values'][1]
        
        self.tool_name_entry.set(tool_name)
        self.tool_server_entry.set(server_name)
    
    def execute_tool(self):
        """Execute selected tool."""
        tool_name = self.tool_name_entry.get().strip()
        server_name = self.tool_server_entry.get().strip()
        args_text = self.tool_args_text.get("1.0", tk.END).strip()
        
        if not tool_name or not server_name:
            self.show_error("Validation Error", "Tool name and server are required")
            return
        
        try:
            arguments = json.loads(args_text)
        except json.JSONDecodeError as e:
            self.show_error("Invalid JSON", f"Arguments must be valid JSON: {e}")
            return
        
        self.tools_output.clear()
        self.tools_output.append(f"Executing {tool_name} on {server_name}...")
        
        def call():
            from ...mcp.types import MCPToolCall
            return self.uaide.mcp_manager.call_tool(MCPToolCall(
                tool_name=tool_name,
                arguments=arguments,
                server_name=server_name
            ))
        
        def callback(result, error=None):
            if error:
                self.tools_output.append(f"\n❌ Error: {error}")
                self.show_error("Execution Failed", error)
            elif result.success:
                self.tools_output.append(f"\n✅ Tool executed successfully")
                self.tools_output.append(f"\nResult:")
                self.tools_output.append(json.dumps(result.content, indent=2))
            else:
                self.tools_output.append(f"\n❌ Tool execution failed: {result.error}")
                self.show_error("Execution Failed", result.error)
        
        run_async(call, callback)
    
    def refresh_resources(self):
        """Refresh resources list."""
        # Clear existing items
        for item in self.resources_tree.get_children():
            self.resources_tree.delete(item)
        
        def get_resources():
            resources = self.uaide.mcp_manager.get_all_resources()
            servers = list(set([r.server_name for r in resources]))
            return resources, servers
        
        def callback(result, error=None):
            if error:
                self.resources_output.delete("1.0", tk.END)
                self.resources_output.insert("1.0", f"Error: {error}")
                return
            
            resources, servers = result
            
            # Update server filter
            self.resources_server_filter['values'] = ["All"] + servers
            if not self.resources_server_filter.get():
                self.resources_server_filter.set("All")
            
            # Filter resources
            server_filter = self.resources_server_filter.get()
            if server_filter and server_filter != "All":
                resources = [r for r in resources if r.server_name == server_filter]
            
            for resource in resources:
                self.resources_tree.insert("", tk.END, values=(
                    resource.name,
                    resource.server_name,
                    resource.uri,
                    resource.mime_type or "-",
                    resource.description
                ))
            
            self.resources_output.delete("1.0", tk.END)
            self.resources_output.insert("1.0", f"Loaded {len(resources)} resources")
        
        run_async(get_resources, callback)
