"]}\n")
            self.stats_text.insert(tk.END, f"Unique queries: {stats['unique_queries']}\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Statistics failed:\n{e}")
    
    def build_graph(self):
        """Build call graph from project."""
        if not self.current_project:
            messagebox.showerror("Error", "Please select a project first")
            return
        
        self.update_status("Building call graph...")
        
        def build_task():
            try:
                graph = CodeGraphRetriever(project_root=self.current_project)
                stats = graph.build_graph()
                
                msg = f"Call graph built!\n\n"
                msg += f"Total nodes: {stats['total_nodes']}\n"
                msg += f"Functions: {stats['functions']}\n"
                msg += f"Classes: {stats['classes']}\n"
                msg += f"Files: {stats['files']}"
                
                self.after(0, lambda: self.update_status("✓ Graph built"))
                self.after(0, lambda: messagebox.showinfo("Success", msg))
                
            except Exception as e:
                self.after(0, lambda: self.update_status(f"✗ Graph build failed: {e}"))
                self.after(0, lambda: messagebox.showerror("Error", f"Graph build failed:\n{e}"))
        
        thread = threading.Thread(target=build_task, daemon=True)
        thread.start()
    
    def find_related_functions(self):
        """Find related functions via call graph."""
        function_name = self.graph_function_var.get().strip()
        if not function_name:
            messagebox.showwarning("Warning", "Please enter a function name")
            return
        
        if not self.current_project:
            messagebox.showerror("Error", "Please select a project first")
            return
        
        depth = self.graph_depth_var.get()
        self.update_status(f"Finding functions related to: {function_name}")
        
        def find_task():
            try:
                graph = CodeGraphRetriever(project_root=self.current_project)
                graph.build_graph()
                
                related = graph.find_related(function_name, max_results=20)
                
                if related:
                    output = f"Found {len(related)} functions related to '{function_name}':\n\n"
                    
                    for i, node in enumerate(related, 1):
                        output += f"[{i}] {node['name']} ({node['type']})\n"
                        output += f"    File: {node['file']}\n"
                        output += f"    Line: {node['line']}\n"
                        output += f"    Depth: {node['depth']}\n\n"
                    
                    self.after(0, lambda: self.graph_results.delete(1.0, tk.END))
                    self.after(0, lambda: self.graph_results.insert(tk.END, output))
                    self.after(0, lambda: self.update_status(f"✓ Found {len(related)} related functions"))
                else:
                    self.after(0, lambda: self.graph_results.delete(1.0, tk.END))
                    self.after(0, lambda: self.graph_results.insert(tk.END, f"No related functions found for: {function_name}"))
                    self.after(0, lambda: self.update_status(f"✗ No results found"))
                
            except Exception as e:
                self.after(0, lambda: self.update_status(f"✗ Search failed: {e}"))
                self.after(0, lambda: messagebox.showerror("Error", f"Search failed:\n{e}"))
        
        thread = threading.Thread(target=find_task, daemon=True)
        thread.start()
    
    def refresh_features_status(self):
        """Refresh features availability status."""
        # Clear tree
        for item in self.features_tree.get_children():
            self.features_tree.delete(item)
        
        if not self.phase9_available:
            self.features_tree.insert('', 'end', text='Phase 9 Not Available', 
                                     values=('✗ Not Installed', 'Install dependencies'))
            return
        
        # Get features status
        features = get_available_features()
        
        # Phase 9.1
        phase91 = self.features_tree.insert('', 'end', text='Phase 9.1 - Foundation', 
                                            values=('', '3 features'))
        
        for name in ['query_expansion', 'feedback_learning', 'graph_retrieval']:
            if name in features:
                status = '✓ Available' if features[name] else '✗ Not Available'
                desc = self._get_feature_description(name)
                self.features_tree.insert(phase91, 'end', text=name, values=(status, desc))
        
        # Phase 9.2
        phase92 = self.features_tree.insert('', 'end', text='Phase 9.2 - Code Understanding', 
                                            values=('', '3 features'))
        
        for name in ['code_embeddings', 'multimodal', 'integration']:
            if name in features:
                status = '✓ Available' if features[name] else '✗ Not Available'
                desc = self._get_feature_description(name)
                self.features_tree.insert(phase92, 'end', text=name, values=(status, desc))
        
        # Phase 9.3
        phase93 = self.features_tree.insert('', 'end', text='Phase 9.3 - Advanced Features', 
                                            values=('', '3 features'))
        
        for name in ['cross_encoder', 'hybrid_search', 'query_understanding']:
            if name in features:
                status = '✓ Available' if features[name] else '✗ Not Available'
                desc = self._get_feature_description(name)
                self.features_tree.insert(phase93, 'end', text=name, values=(status, desc))
        
        # Expand all
        self.features_tree.item(phase91, open=True)
        self.features_tree.item(phase92, open=True)
        self.features_tree.item(phase93, open=True)
    
    def _get_feature_description(self, name):
        """Get feature description."""
        descriptions = {
            'query_expansion': 'Automatic query variations',
            'feedback_learning': 'Learn from user interactions',
            'graph_retrieval': 'Code relationship understanding',
            'code_embeddings': 'CodeBERT semantic search',
            'multimodal': 'Search code + docs',
            'integration': 'Unified EnhancedRAG interface',
            'cross_encoder': 'Precision optimization',
            'hybrid_search': 'Vector + keyword (BM25)',
            'query_understanding': 'Intent classification'
        }
        return descriptions.get(name, '')
    
    def show_system_info(self):
        """Show system information."""
        info = "System Information\n"
        info += "="*60 + "\n\n"
        
        info += f"Phase 9 Available: {self.phase9_available}\n"
        
        if self.phase9_available:
            features = get_available_features()
            available = sum(features.values())
            total = len(features)
            info += f"Features Available: {available}/{total} ({available/total*100:.0f}%)\n\n"
            
            if self.enhanced_rag:
                stats = self.enhanced_rag.get_statistics()
                info += f"Features Enabled: {stats['total_features']}/8\n"
                info += f"\nEnabled Features:\n"
                for feat, enabled in stats['features_enabled'].items():
                    status = "✓" if enabled else "✗"
                    info += f"  {status} {feat}\n"
        
        info += f"\nCurrent Project: {self.current_project or 'None'}\n"
        
        messagebox.showinfo("System Information", info)
    
    def enable_all_features(self):
        """Enable all features."""
        self.use_query_expansion.set(True)
        self.use_feedback_learning.set(True)
        self.use_graph_retrieval.set(True)
        self.use_code_embeddings.set(True)
        self.use_multimodal.set(True)
        self.use_reranking.set(True)
        self.use_hybrid_search.set(True)
        self.use_query_understanding.set(True)
        self.update_status("All features enabled")
    
    def disable_all_features(self):
        """Disable all features."""
        self.use_query_expansion.set(False)
        self.use_feedback_learning.set(False)
        self.use_graph_retrieval.set(False)
        self.use_code_embeddings.set(False)
        self.use_multimodal.set(False)
        self.use_reranking.set(False)
        self.use_hybrid_search.set(False)
        self.use_query_understanding.set(False)
        self.update_status("All features disabled")
    
    def set_default_features(self):
        """Set default features (recommended)."""
        self.use_query_expansion.set(True)
        self.use_feedback_learning.set(True)
        self.use_graph_retrieval.set(False)
        self.use_code_embeddings.set(False)
        self.use_multimodal.set(False)
        self.use_reranking.set(False)
        self.use_hybrid_search.set(False)
        self.use_query_understanding.set(True)
        self.update_status("Default features set (recommended)")
    
    def update_status(self, message):
        """Update status bar."""
        self.status_bar.config(text=message)


def main():
    """Entry point for GUI with Phase 9."""
    app = GUIWithPhase9()
    app.mainloop()


if __name__ == "__main__":
    main()
