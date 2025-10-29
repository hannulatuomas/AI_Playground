# Phase 9 Advanced RAG Features - Complete CLI Integration Guide

## Overview

This document explains how to use ALL Phase 9 advanced RAG features from both CLI and GUI.

## Quick Summary

**Currently**: Basic RAG is integrated (`rag index`, `rag query`)
**New**: Phase 9 advanced features need CLI commands

## Commands to Add

### 1. Enhanced RAG Query (with all features)
```bash
# Use all Phase 9 features in one query
rag query-advanced "JWT authentication" --language python --use-all

# Use specific features
rag query-advanced "JWT auth" --reranking --hybrid --understanding

# Configure weights
rag query-advanced "auth" --hybrid-alpha 0.7 --top-k 10
```

### 2. Query Expansion
```bash
# See query variations
rag expand "JWT auth" --language python

# Use expanded queries in search
rag query "JWT auth" --expand
```

### 3. Cross-Encoder Reranking
```bash
# Rerank existing results
rag query "authentication" --rerank --model ms-marco-mini

# With score fusion
rag query "auth" --rerank --fusion-weight 0.7
```

### 4. Hybrid Search
```bash
# Hybrid search (vector + BM25)
rag hybrid "JWT authentication" --alpha 0.6

# Different fusion methods
rag hybrid "auth" --fusion rrf  # reciprocal rank fusion
rag hybrid "auth" --fusion linear
rag hybrid "auth" --fusion max
```

### 5. Query Understanding
```bash
# Understand query intent
rag understand "how do I authenticate users?"

# Auto-reformulate and search
rag query "how to auth?" --understand
```

### 6. Feedback Learning
```bash
# Record feedback on result
rag feedback <result_id> --useful
rag feedback <result_id> --not-useful

# View feedback stats
rag feedback-stats

# Export feedback data
rag feedback-export feedback.csv
```

### 7. Graph Retrieval
```bash
# Build call graph
rag graph-build

# Find related code
rag graph-related "authenticate" --depth 2

# Visualize subgraph
rag graph-viz "authenticate" --output graph.dot
```

### 8. Feature Management
```bash
# Check which features are available
rag features-status

# Configure features
rag config --enable-all  # Enable all 8 features
rag config --enable reranking,hybrid,understanding
rag config --disable code-embeddings

# Show current configuration
rag config-show
```

## Integration Points

### Add to `cli.py` - cmd_rag method

```python
def cmd_rag(self, args: str):
    \"\"\"Handle RAG commands with Phase 9 features.\"\"\"
    
    # Parse subcommand
    parts = args.split(maxsplit=1)
    subcommand = parts[0].lower()
    subargs = parts[1] if len(parts) > 1 else ""
    
    # Phase 9 commands
    if subcommand == 'query-advanced':
        self.cmd_rag_query_advanced(subargs)
    elif subcommand == 'expand':
        self.cmd_rag_expand(subargs)
    elif subcommand == 'hybrid':
        self.cmd_rag_hybrid(subargs)
    elif subcommand == 'understand':
        self.cmd_rag_understand(subargs)
    elif subcommand == 'feedback':
        self.cmd_rag_feedback(subargs)
    elif subcommand == 'feedback-stats':
        self.cmd_rag_feedback_stats(subargs)
    elif subcommand == 'graph-build':
        self.cmd_rag_graph_build(subargs)
    elif subcommand == 'graph-related':
        self.cmd_rag_graph_related(subargs)
    elif subcommand == 'features-status':
        self.cmd_rag_features_status(subargs)
    elif subcommand == 'config':
        self.cmd_rag_config(subargs)
    # ... existing commands
```

## GUI Integration

### Add New Tab: "Advanced Search"

```python
# In gui_enhanced.py or gui.py

def create_advanced_search_tab(self):
    \"\"\"Create advanced RAG search tab.\"\"\"
    tab = ttk.Frame(self.notebook)
    
    # Query input
    ttk.Label(tab, text="Query:").pack()
    query_entry = ttk.Entry(tab, width=60)
    query_entry.pack()
    
    # Feature toggles
    features_frame = ttk.LabelFrame(tab, text="Enable Features")
    features_frame.pack(fill='x', padx=5, pady=5)
    
    self.use_query_expansion = tk.BooleanVar(value=True)
    self.use_reranking = tk.BooleanVar(value=False)
    self.use_hybrid = tk.BooleanVar(value=False)
    self.use_understanding = tk.BooleanVar(value=False)
    self.use_feedback = tk.BooleanVar(value=True)
    self.use_graph = tk.BooleanVar(value=False)
    
    ttk.Checkbutton(features_frame, text="Query Expansion",
                    variable=self.use_query_expansion).pack(side='left')
    ttk.Checkbutton(features_frame, text="Reranking",
                    variable=self.use_reranking).pack(side='left')
    ttk.Checkbutton(features_frame, text="Hybrid Search",
                    variable=self.use_hybrid).pack(side='left')
    ttk.Checkbutton(features_frame, text="Query Understanding",
                    variable=self.use_understanding).pack(side='left')
    
    # Search button
    search_btn = ttk.Button(tab, text="Advanced Search",
                           command=lambda: self.do_advanced_search(query_entry.get()))
    search_btn.pack()
    
    # Results display
    results_text = scrolledtext.ScrolledText(tab, height=20)
    results_text.pack(fill='both', expand=True)
    
    return tab
```

## Example: Complete Integration

### cli_rag_advanced.py (new file)

```python
\"\"\"
CLI commands for Phase 9 Advanced RAG Features
\"\"\"

class RAGAdvancedCLI:
    def __init__(self, enhanced_rag):
        self.rag = enhanced_rag
    
    def cmd_query_advanced(self, query, **options):
        \"\"\"Advanced query with all features.\"\"\"
        results = self.rag.retrieve(
            query=query,
            use_query_expansion=options.get('expand', True),
            use_reranking=options.get('rerank', False),
            use_hybrid=options.get('hybrid', False),
            use_query_understanding=options.get('understand', False),
            use_graph_context=options.get('graph', False),
            top_k=options.get('top_k', 5)
        )
        
        return results
    
    def cmd_expand(self, query, language=None):
        \"\"\"Show query expansions.\"\"\"
        from features.rag_advanced import QueryExpander
        expander = QueryExpander()
        expansions = expander.expand_query(query, language=language)
        return expansions
    
    def cmd_feedback(self, result_id, feedback_type):
        \"\"\"Record feedback.\"\"\"
        self.rag.record_feedback(
            query=self.last_query,
            result_id=result_id,
            feedback_type=feedback_type
        )
```

## Implementation Priority

1. **High Priority** (most useful):
   - `rag query-advanced` - Use all features at once
   - `rag config` - Enable/disable features
   - `rag features-status` - Check what's available

2. **Medium Priority**:
   - `rag expand` - Show query variations
   - `rag feedback` - Record feedback
   - `rag hybrid` - Hybrid search

3. **Low Priority** (advanced users):
   - `rag understand` - Query intent analysis
   - `rag graph-*` - Graph operations
   - Individual feature commands

## Quick Implementation

To quickly add Phase 9 features to CLI, add this to `cli.py`:

```python
# After existing RAG commands

def cmd_rag_features(self, args: str):
    \"\"\"Show Phase 9 features status.\"\"\"
    from features.rag_advanced import get_available_features
    
    features = get_available_features()
    
    print(self.colorize("\\nPhase 9 Advanced RAG Features:", Colors.BOLD + Colors.CYAN))
    print("="*60)
    
    for name, available in features.items():
        status = "✓ Available" if available else "✗ Not available"
        color = Colors.GREEN if available else Colors.YELLOW
        print(f"  {name:25} {self.colorize(status, color)}")
    
    print("="*60)
    print(f"\\nTotal: {sum(features.values())}/{len(features)} features available")
    
    if sum(features.values()) < len(features):
        print(self.colorize("\\n⚠ Install dependencies for missing features:", Colors.YELLOW))
        print("  pip install transformers torch  # For CodeBERT")

def cmd_rag_advanced_query(self, query: str):
    \"\"\"Use enhanced RAG with all Phase 9 features.\"\"\"
    from features.rag_advanced import EnhancedRAG
    
    # Initialize with all features
    rag = EnhancedRAG(
        project_root=self.current_project,
        use_all_features=True
    )
    
    print(self.colorize("\\n→ Enhanced search (using all 8 features)...", Colors.YELLOW))
    
    results = rag.retrieve(query, top_k=5)
    
    # Display results
    for i, result in enumerate(results, 1):
        print(f"\\n[{i}] {result['file_path']}")
        print(f"    Score: {result['score']:.2%}")
        # Show snippet
        print(f"    {result['content'][:200]}...")
```

## Summary

**Status**: Phase 9 features are implemented but need CLI/GUI integration

**Quick Fix**: Add the `rag features` and `rag query-advanced` commands to CLI

**Full Integration**: Would require ~500 lines of CLI/GUI code to expose all 8 features

**Recommendation**: 
1. Add `rag features-status` command (shows what's available)
2. Add `rag advanced-query` command (uses all features)
3. Add GUI "Advanced Search" tab with feature toggles

Would you like me to implement the complete CLI/GUI integration for all Phase 9 features now?
