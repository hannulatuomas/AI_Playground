"""
RAG Tab

GUI tab for Advanced RAG & Retrieval features (v1.6.0).
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from typing import Optional
import threading

from .base import BaseTab
from ...modules.context_manager import (
    CodeBERTEmbedder,
    CodeBERTIndex,
    MultiModalRetriever,
    QueryEnhancer,
    GraphRetriever
)


class RAGTab(BaseTab):
    """Tab for Advanced RAG & Retrieval features."""
    
    def __init__(self, parent, uaide):
        """Initialize RAG tab."""
        super().__init__(parent, uaide, "Advanced RAG")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components."""
        # Create sub-tabs
        sub_notebook = ttk.Notebook(self.frame)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sub-tabs
        self.setup_codebert_tab(sub_notebook)
        self.setup_multimodal_tab(sub_notebook)
        self.setup_query_tab(sub_notebook)
        self.setup_graph_tab(sub_notebook)
    
    def setup_codebert_tab(self, parent):
        """Setup CodeBERT embeddings tab."""
        frame = ttk.Frame(parent)
        parent.add(frame, text="CodeBERT")
        
        # Title
        title = ttk.Label(frame, text="CodeBERT Embeddings", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # Index section
        index_frame = ttk.LabelFrame(frame, text="Index Management", padding=10)
        index_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Directory selection
        dir_frame = ttk.Frame(index_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dir_frame, text="Directory:").pack(side=tk.LEFT)
        self.codebert_dir_var = tk.StringVar(value=".")
        ttk.Entry(dir_frame, textvariable=self.codebert_dir_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_codebert_dir).pack(side=tk.LEFT)
        
        # Index button
        ttk.Button(index_frame, text="Build CodeBERT Index", 
                  command=self.build_codebert_index).pack(pady=5)
        
        # Search section
        search_frame = ttk.LabelFrame(frame, text="Search", padding=10)
        search_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Query input
        query_frame = ttk.Frame(search_frame)
        query_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(query_frame, text="Query:").pack(side=tk.LEFT)
        self.codebert_query_var = tk.StringVar()
        ttk.Entry(query_frame, textvariable=self.codebert_query_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(query_frame, text="Search", command=self.search_codebert).pack(side=tk.LEFT)
        
        # Results
        ttk.Label(search_frame, text="Results:").pack(anchor=tk.W, pady=5)
        self.codebert_results = scrolledtext.ScrolledText(search_frame, height=15)
        self.codebert_results.pack(fill=tk.BOTH, expand=True)
        
        # Statistics
        stats_frame = ttk.Frame(frame)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.codebert_stats_label = ttk.Label(stats_frame, text="Ready")
        self.codebert_stats_label.pack(side=tk.LEFT)
    
    def setup_multimodal_tab(self, parent):
        """Setup multi-modal retrieval tab."""
        frame = ttk.Frame(parent)
        parent.add(frame, text="Multi-Modal")
        
        # Title
        title = ttk.Label(frame, text="Multi-Modal Retrieval", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # Index section
        index_frame = ttk.LabelFrame(frame, text="Index Management", padding=10)
        index_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Directory selection
        dir_frame = ttk.Frame(index_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dir_frame, text="Directory:").pack(side=tk.LEFT)
        self.multimodal_dir_var = tk.StringVar(value=".")
        ttk.Entry(dir_frame, textvariable=self.multimodal_dir_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_multimodal_dir).pack(side=tk.LEFT)
        
        # Index button
        ttk.Button(index_frame, text="Build Multi-Modal Index", 
                  command=self.build_multimodal_index).pack(pady=5)
        
        # Search section
        search_frame = ttk.LabelFrame(frame, text="Search", padding=10)
        search_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Query and mode
        query_frame = ttk.Frame(search_frame)
        query_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(query_frame, text="Query:").pack(side=tk.LEFT)
        self.multimodal_query_var = tk.StringVar()
        ttk.Entry(query_frame, textvariable=self.multimodal_query_var, width=40).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(query_frame, text="Mode:").pack(side=tk.LEFT, padx=5)
        self.multimodal_mode_var = tk.StringVar(value="both")
        mode_combo = ttk.Combobox(query_frame, textvariable=self.multimodal_mode_var, 
                                  values=["both", "code", "docs"], width=10, state="readonly")
        mode_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(query_frame, text="Search", command=self.search_multimodal).pack(side=tk.LEFT)
        
        # Results
        ttk.Label(search_frame, text="Results:").pack(anchor=tk.W, pady=5)
        self.multimodal_results = scrolledtext.ScrolledText(search_frame, height=15)
        self.multimodal_results.pack(fill=tk.BOTH, expand=True)
        
        # Statistics
        stats_frame = ttk.Frame(frame)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.multimodal_stats_label = ttk.Label(stats_frame, text="Ready")
        self.multimodal_stats_label.pack(side=tk.LEFT)
    
    def setup_query_tab(self, parent):
        """Setup query enhancement tab."""
        frame = ttk.Frame(parent)
        parent.add(frame, text="Query Enhancement")
        
        # Title
        title = ttk.Label(frame, text="Query Enhancement", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Input Query", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        query_frame = ttk.Frame(input_frame)
        query_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(query_frame, text="Query:").pack(side=tk.LEFT)
        self.query_enhance_var = tk.StringVar()
        ttk.Entry(query_frame, textvariable=self.query_enhance_var, width=50).pack(side=tk.LEFT, padx=5)
        
        # Options
        options_frame = ttk.Frame(input_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        self.query_synonyms_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Add Synonyms", 
                       variable=self.query_synonyms_var).pack(side=tk.LEFT, padx=5)
        
        self.query_expansion_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Expand Query", 
                       variable=self.query_expansion_var).pack(side=tk.LEFT, padx=5)
        
        self.query_llm_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Use LLM", 
                       variable=self.query_llm_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(input_frame, text="Enhance Query", 
                  command=self.enhance_query).pack(pady=5)
        
        # Results section
        results_frame = ttk.LabelFrame(frame, text="Enhanced Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.query_results = scrolledtext.ScrolledText(results_frame, height=20)
        self.query_results.pack(fill=tk.BOTH, expand=True)
    
    def setup_graph_tab(self, parent):
        """Setup graph retrieval tab."""
        frame = ttk.Frame(parent)
        parent.add(frame, text="Call Graph")
        
        # Title
        title = ttk.Label(frame, text="Call Graph Analysis", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # Build section
        build_frame = ttk.LabelFrame(frame, text="Build Graph", padding=10)
        build_frame.pack(fill=tk.X, padx=10, pady=5)
        
        dir_frame = ttk.Frame(build_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dir_frame, text="Directory:").pack(side=tk.LEFT)
        self.graph_dir_var = tk.StringVar(value=".")
        ttk.Entry(dir_frame, textvariable=self.graph_dir_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_graph_dir).pack(side=tk.LEFT)
        
        ttk.Button(build_frame, text="Build Call Graph", 
                  command=self.build_call_graph).pack(pady=5)
        
        # Analysis section
        analysis_frame = ttk.LabelFrame(frame, text="Analysis", padding=10)
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Node search
        search_frame = ttk.Frame(analysis_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Node:").pack(side=tk.LEFT)
        self.graph_node_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.graph_node_var, width=30).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="Expand Context", 
                  command=self.expand_graph_context).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Find Related", 
                  command=self.find_related_code).pack(side=tk.LEFT, padx=2)
        
        # Results
        ttk.Label(analysis_frame, text="Results:").pack(anchor=tk.W, pady=5)
        self.graph_results = scrolledtext.ScrolledText(analysis_frame, height=15)
        self.graph_results.pack(fill=tk.BOTH, expand=True)
        
        # Statistics
        stats_frame = ttk.Frame(frame)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.graph_stats_label = ttk.Label(stats_frame, text="Ready")
        self.graph_stats_label.pack(side=tk.LEFT)
    
    # CodeBERT methods
    def browse_codebert_dir(self):
        """Browse for directory to index."""
        directory = filedialog.askdirectory(title="Select Directory to Index")
        if directory:
            self.codebert_dir_var.set(directory)
    
    def build_codebert_index(self):
        """Build CodeBERT index."""
        directory = self.codebert_dir_var.get()
        if not directory:
            messagebox.showwarning("Warning", "Please select a directory")
            return
        
        self.codebert_stats_label.config(text="Building index...")
        
        def build():
            try:
                index = CodeBERTIndex(".uaide/codebert_index")
                
                # Index Python files
                from pathlib import Path
                files_indexed = 0
                for file_path in Path(directory).rglob('*.py'):
                    if index.index_file(str(file_path)):
                        files_indexed += 1
                
                index.save()
                
                self.root.after(0, lambda: self.codebert_stats_label.config(
                    text=f"Indexed {files_indexed} files"))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", f"Indexed {files_indexed} files"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self.codebert_stats_label.config(text="Error"))
        
        threading.Thread(target=build, daemon=True).start()
    
    def search_codebert(self):
        """Search with CodeBERT."""
        query = self.codebert_query_var.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a query")
            return
        
        self.codebert_results.delete(1.0, tk.END)
        self.codebert_results.insert(tk.END, "Searching...\n")
        
        def search():
            try:
                index = CodeBERTIndex(".uaide/codebert_index")
                if not index.load():
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Warning", "No index found. Build index first."))
                    return
                
                results = index.search(query, top_k=5)
                
                self.root.after(0, lambda: self.display_codebert_results(results))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        threading.Thread(target=search, daemon=True).start()
    
    def display_codebert_results(self, results):
        """Display CodeBERT search results."""
        self.codebert_results.delete(1.0, tk.END)
        
        if not results:
            self.codebert_results.insert(tk.END, "No results found.\n")
            return
        
        self.codebert_results.insert(tk.END, f"Found {len(results)} results:\n\n")
        
        for i, (file_path, chunk, similarity) in enumerate(results, 1):
            self.codebert_results.insert(tk.END, f"{i}. {file_path}\n")
            self.codebert_results.insert(tk.END, f"   Similarity: {similarity:.3f}\n")
            self.codebert_results.insert(tk.END, f"   {chunk[:200]}...\n\n")
    
    # Multi-modal methods
    def browse_multimodal_dir(self):
        """Browse for directory to index."""
        directory = filedialog.askdirectory(title="Select Directory to Index")
        if directory:
            self.multimodal_dir_var.set(directory)
    
    def build_multimodal_index(self):
        """Build multi-modal index."""
        directory = self.multimodal_dir_var.get()
        if not directory:
            messagebox.showwarning("Warning", "Please select a directory")
            return
        
        self.multimodal_stats_label.config(text="Building index...")
        
        def build():
            try:
                retriever = MultiModalRetriever()
                stats = retriever.index_directory(directory)
                
                self.root.after(0, lambda: self.multimodal_stats_label.config(
                    text=f"Code: {stats['code_files']}, Docs: {stats['doc_files']}"))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", f"Indexed {stats['code_files']} code files and {stats['doc_files']} doc files"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self.multimodal_stats_label.config(text="Error"))
        
        threading.Thread(target=build, daemon=True).start()
    
    def search_multimodal(self):
        """Search with multi-modal retrieval."""
        query = self.multimodal_query_var.get()
        mode = self.multimodal_mode_var.get()
        
        if not query:
            messagebox.showwarning("Warning", "Please enter a query")
            return
        
        self.multimodal_results.delete(1.0, tk.END)
        self.multimodal_results.insert(tk.END, f"Searching ({mode})...\n")
        
        # Note: This is a simplified version
        # In production, you'd load a saved index
        self.multimodal_results.insert(tk.END, "\nFeature requires indexed data.\n")
        self.multimodal_results.insert(tk.END, "Build index first using 'Build Multi-Modal Index' button.\n")
    
    # Query enhancement methods
    def enhance_query(self):
        """Enhance query."""
        query = self.query_enhance_var.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a query")
            return
        
        self.query_results.delete(1.0, tk.END)
        self.query_results.insert(tk.END, "Enhancing query...\n")
        
        def enhance():
            try:
                ai_backend = self.uaide.ai_backend if self.query_llm_var.get() else None
                enhancer = QueryEnhancer(ai_backend)
                
                result = enhancer.enhance_query(
                    query,
                    use_synonyms=self.query_synonyms_var.get(),
                    use_expansion=self.query_expansion_var.get(),
                    use_llm=self.query_llm_var.get()
                )
                
                self.root.after(0, lambda: self.display_query_results(result, enhancer))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        threading.Thread(target=enhance, daemon=True).start()
    
    def display_query_results(self, result, enhancer):
        """Display query enhancement results."""
        self.query_results.delete(1.0, tk.END)
        
        self.query_results.insert(tk.END, f"Original: {result['original']}\n\n")
        self.query_results.insert(tk.END, f"Enhanced: {result['enhanced']}\n\n")
        
        if result['expansions']:
            self.query_results.insert(tk.END, f"Expansions ({len(result['expansions'])}):\n")
            for exp in result['expansions']:
                self.query_results.insert(tk.END, f"  • {exp}\n")
            self.query_results.insert(tk.END, "\n")
        
        if result['reformulations']:
            self.query_results.insert(tk.END, f"Reformulations ({len(result['reformulations'])}):\n")
            for ref in result['reformulations']:
                self.query_results.insert(tk.END, f"  • {ref}\n")
            self.query_results.insert(tk.END, "\n")
        
        # Intent and filters
        intent = enhancer.detect_intent(result['original'])
        self.query_results.insert(tk.END, f"Detected Intent: {intent}\n\n")
        
        filters = enhancer.suggest_filters(result['original'])
        if any(filters.values()):
            self.query_results.insert(tk.END, "Suggested Filters:\n")
            for filter_type, values in filters.items():
                if values:
                    self.query_results.insert(tk.END, f"  {filter_type}: {', '.join(values)}\n")
    
    # Graph methods
    def browse_graph_dir(self):
        """Browse for directory to analyze."""
        directory = filedialog.askdirectory(title="Select Directory to Analyze")
        if directory:
            self.graph_dir_var.set(directory)
    
    def build_call_graph(self):
        """Build call graph."""
        directory = self.graph_dir_var.get()
        if not directory:
            messagebox.showwarning("Warning", "Please select a directory")
            return
        
        self.graph_stats_label.config(text="Building call graph...")
        
        def build():
            try:
                retriever = GraphRetriever()
                stats = retriever.index_directory(directory)
                
                graph_stats = retriever.get_statistics()
                
                self.root.after(0, lambda: self.graph_stats_label.config(
                    text=f"Nodes: {graph_stats['total_nodes']}, Files: {graph_stats['total_files']}"))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", f"Built call graph with {graph_stats['total_nodes']} nodes"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self.graph_stats_label.config(text="Error"))
        
        threading.Thread(target=build, daemon=True).start()
    
    def expand_graph_context(self):
        """Expand context around a node."""
        node_name = self.graph_node_var.get()
        if not node_name:
            messagebox.showwarning("Warning", "Please enter a node name")
            return
        
        self.graph_results.delete(1.0, tk.END)
        self.graph_results.insert(tk.END, f"Expanding context for: {node_name}\n\n")
        
        # Note: This requires a built graph
        self.graph_results.insert(tk.END, "Feature requires a built call graph.\n")
        self.graph_results.insert(tk.END, "Build graph first using 'Build Call Graph' button.\n")
    
    def find_related_code(self):
        """Find related code."""
        node_name = self.graph_node_var.get()
        if not node_name:
            messagebox.showwarning("Warning", "Please enter a node name")
            return
        
        self.graph_results.delete(1.0, tk.END)
        self.graph_results.insert(tk.END, f"Finding code related to: {node_name}\n\n")
        
        # Note: This requires a built graph
        self.graph_results.insert(tk.END, "Feature requires a built call graph.\n")
        self.graph_results.insert(tk.END, "Build graph first using 'Build Call Graph' button.\n")
