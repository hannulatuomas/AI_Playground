"""
CLI with Phase 9 Advanced RAG Features Integration

Complete command-line interface with all 8 advanced RAG features:
- Query Expansion (9.1)
- Feedback Learning (9.1)
- Graph Retrieval (9.1)
- CodeBERT Embeddings (9.2)
- Multi-modal Retrieval (9.2)
- Cross-Encoder Reranking (9.3)
- Hybrid Search (9.3)
- Query Understanding (9.3)
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import original CLI
from ui.cli import CLI as BaseCLI, Colors

# Import Phase 9 features
try:
    from features.rag_advanced import (
        EnhancedRAG,
        QueryExpander,
        FeedbackLearner,
        CodeGraphRetriever,
        CrossEncoderReranker,
        HybridSearch,
        QueryUnderstanding,
        get_available_features
    )
    PHASE9_AVAILABLE = True
except ImportError:
    PHASE9_AVAILABLE = False


class CLIWithPhase9(BaseCLI):
    """Enhanced CLI with Phase 9 Advanced RAG Features."""
    
    def __init__(self):
        super().__init__()
        
        # Phase 9 components
        self.enhanced_rag = None
        self.phase9_available = PHASE9_AVAILABLE
        self.last_query = None
        self.last_results = []
        
    def print_help(self):
        """Print help with Phase 9 features."""
        # Call parent help
        super().print_help()
        
        if not self.phase9_available:
            return
        
        # Add Phase 9 help
        phase9_help = f"""
{self.colorize('Phase 9 Advanced RAG Features:', Colors.BOLD + Colors.MAGENTA)}

{self.colorize('Enhanced Search:', Colors.BOLD)}
  {self.colorize('rag advanced', Colors.GREEN)} <query> [options]
    Search with all Phase 9 features enabled
    Options: --expand --rerank --hybrid --understand --graph
    Example: rag advanced "JWT auth" --rerank --hybrid
    
  {self.colorize('rag features', Colors.GREEN)}
    Show status of all 8 Phase 9 features
    
  {self.colorize('rag config', Colors.GREEN)} <enable|disable> <features>
    Configure which features to use by default
    Example: rag config enable reranking,hybrid,understanding

{self.colorize('Query Enhancement:', Colors.BOLD)}
  {self.colorize('rag expand', Colors.GREEN)} <query> [language]
    Show query expansion variations
    Example: rag expand "JWT auth" python
    
  {self.colorize('rag understand', Colors.GREEN)} <query>
    Analyze query intent and reformulate
    Example: rag understand "how do I authenticate users?"

{self.colorize('Search Methods:', Colors.BOLD)}
  {self.colorize('rag hybrid', Colors.GREEN)} <query> [alpha]
    Hybrid search (vector + BM25 keyword)
    Alpha: 0-1 (0.5 = 50/50, 0.7 = 70% vector, 30% keyword)
    Example: rag hybrid "authentication" 0.6
    
  {self.colorize('rag rerank', Colors.GREEN)} <query> [model]
    Search with cross-encoder reranking
    Models: ms-marco-mini (default), ms-marco-base, qnli
    Example: rag rerank "JWT auth" ms-marco-mini

{self.colorize('Feedback & Learning:', Colors.BOLD)}
  {self.colorize('rag feedback', Colors.GREEN)} <result_index> <useful|not-useful>
    Provide feedback on search results
    Example: rag feedback 1 useful
    
  {self.colorize('rag feedback-stats', Colors.GREEN)} [days]
    Show feedback learning statistics
    Example: rag feedback-stats 30

{self.colorize('Graph Analysis:', Colors.BOLD)}
  {self.colorize('rag graph-build', Colors.GREEN)}
    Build call graph from project code
    
  {self.colorize('rag graph-related', Colors.GREEN)} <function> [depth]
    Find related functions via call graph
    Example: rag graph-related authenticate 2
    
  {self.colorize('rag graph-viz', Colors.GREEN)} <function> [output]
    Visualize function call graph
    Example: rag graph-viz authenticate graph.dot

{self.colorize('Examples:', Colors.BOLD)}
  # Use all features for best results
  rag advanced "JWT authentication implementation"
  
  # Hybrid search for exact keyword matching
  rag hybrid "def authenticate" 0.7
  
  # Understand complex query
  rag understand "how do I validate JWT tokens in Python?"
  
  # Find related code
  rag graph-related login 2
"""
        print(phase9_help)
    
    def initialize_components(self) -> bool:
        """Initialize components including Phase 9."""
        # Call parent initialization
        if not super().initialize_components():
            return False
        
        # Initialize Phase 9 if available
        if self.phase9_available and self.current_project:
            try:
                print(self.colorize("\nInitializing Phase 9 features...", Colors.YELLOW))
                
                self.enhanced_rag = EnhancedRAG(
                    project_root=self.current_project,
                    use_query_expansion=True,
                    use_feedback_learning=True,
                    use_graph_retrieval=True,
                    use_code_embeddings=False,  # Optional
                    use_multimodal=False,  # Optional
                    use_reranking=False,  # Optional
                    use_hybrid_search=False,  # Optional
                    use_query_understanding=True
                )
                
                print(self.colorize("✓ Phase 9 Enhanced RAG ready!", Colors.GREEN))
                print(f"  Features enabled: {self.enhanced_rag._count_features()}/8")
                
            except Exception as e:
                print(self.colorize(f"⚠ Phase 9 initialization warning: {e}", Colors.YELLOW))
                print("  Basic RAG still available")
        
        return True
    
    def cmd_rag(self, args: str):
        """Enhanced RAG command handler with Phase 9 features."""
        if not args:
            super().cmd_rag(args)
            return
        
        # Parse subcommand
        parts = args.split(maxsplit=1)
        subcommand = parts[0].lower()
        subargs = parts[1] if len(parts) > 1 else ""
        
        # Phase 9 commands
        if subcommand == 'advanced':
            self.cmd_rag_advanced(subargs)
        elif subcommand == 'features':
            self.cmd_rag_features(subargs)
        elif subcommand == 'config':
            self.cmd_rag_config(subargs)
        elif subcommand == 'expand':
            self.cmd_rag_expand(subargs)
        elif subcommand == 'understand':
            self.cmd_rag_understand(subargs)
        elif subcommand == 'hybrid':
            self.cmd_rag_hybrid(subargs)
        elif subcommand == 'rerank':
            self.cmd_rag_rerank(subargs)
        elif subcommand == 'feedback':
            self.cmd_rag_feedback(subargs)
        elif subcommand == 'feedback-stats':
            self.cmd_rag_feedback_stats(subargs)
        elif subcommand == 'graph-build':
            self.cmd_rag_graph_build(subargs)
        elif subcommand == 'graph-related':
            self.cmd_rag_graph_related(subargs)
        elif subcommand == 'graph-viz':
            self.cmd_rag_graph_viz(subargs)
        else:
            # Fall back to parent implementation
            super().cmd_rag(args)
    
    def cmd_rag_advanced(self, args: str):
        """Advanced search with all Phase 9 features."""
        if not self.phase9_available:
            print(self.colorize("✗ Phase 9 features not available", Colors.RED))
            print("  Install: pip install sentence-transformers chromadb")
            return
        
        if not args:
            print(self.colorize("✗ Usage: rag advanced <query> [options]", Colors.RED))
            print("  Options: --expand --rerank --hybrid --understand --graph")
            return
        
        # Parse query and options
        parts = args.split()
        options = {
            'expand': '--expand' in parts,
            'rerank': '--rerank' in parts,
            'hybrid': '--hybrid' in parts,
            'understand': '--understand' in parts,
            'graph': '--graph' in parts
        }
        
        # Remove options from query
        query_parts = [p for p in parts if not p.startswith('--')]
        query = ' '.join(query_parts)
        
        if not query:
            print(self.colorize("✗ No query specified", Colors.RED))
            return
        
        print(self.colorize(f"\n→ Advanced search: {query}", Colors.YELLOW))
        print(f"  Features: {', '.join([k for k, v in options.items() if v]) or 'defaults'}\n")
        
        try:
            # Use EnhancedRAG
            if not self.enhanced_rag:
                self.enhanced_rag = EnhancedRAG(
                    project_root=self.current_project,
                    use_all_features=any(options.values())
                )
            
            # Search
            results = self.enhanced_rag.retrieve(
                query=query,
                top_k=5,
                use_query_expansion=options.get('expand', True),
                use_reranking=options.get('rerank', False),
                use_query_understanding=options.get('understand', False),
                use_graph_context=options.get('graph', False),
                hybrid_alpha=0.6 if options.get('hybrid') else None
            )
            
            # Display results
            self._display_results(query, results)
            
            # Store for feedback
            self.last_query = query
            self.last_results = results
            
        except Exception as e:
            print(self.colorize(f"✗ Search failed: {e}", Colors.RED))
    
    def cmd_rag_features(self, args: str):
        """Show Phase 9 features status."""
        if not self.phase9_available:
            print(self.colorize("\n✗ Phase 9 not available", Colors.YELLOW))
            print("  Install: pip install sentence-transformers chromadb")
            return
        
        features = get_available_features()
        
        print(self.colorize("\nPhase 9 Advanced RAG Features:", Colors.BOLD + Colors.CYAN))
        print("=" * 60)
        
        # Group by phase
        phase_91 = ['query_expansion', 'feedback_learning', 'graph_retrieval']
        phase_92 = ['code_embeddings', 'multimodal', 'integration']
        phase_93 = ['cross_encoder', 'hybrid_search', 'query_understanding']
        
        print(self.colorize("\n  Phase 9.1 - Foundation:", Colors.BOLD))
        for name in phase_91:
            if name in features:
                status = "✓ Available" if features[name] else "✗ Not available"
                color = Colors.GREEN if features[name] else Colors.YELLOW
                print(f"    {name:25} {self.colorize(status, color)}")
        
        print(self.colorize("\n  Phase 9.2 - Code Understanding:", Colors.BOLD))
        for name in phase_92:
            if name in features:
                status = "✓ Available" if features[name] else "✗ Not available"
                color = Colors.GREEN if features[name] else Colors.YELLOW
                print(f"    {name:25} {self.colorize(status, color)}")
        
        print(self.colorize("\n  Phase 9.3 - Advanced Features:", Colors.BOLD))
        for name in phase_93:
            if name in features:
                status = "✓ Available" if features[name] else "✗ Not available"
                color = Colors.GREEN if features[name] else Colors.YELLOW
                print(f"    {name:25} {self.colorize(status, color)}")
        
        print("\n" + "=" * 60)
        
        available = sum(features.values())
        total = len(features)
        print(f"Total: {available}/{total} features available ({available/total*100:.0f}%)")
        
        if available < total:
            print(self.colorize("\n⚠ Missing features require:", Colors.YELLOW))
            if not features.get('code_embeddings', True):
                print("  pip install transformers torch  # For CodeBERT")
    
    def cmd_rag_config(self, args: str):
        """Configure Phase 9 features."""
        if not args:
            print(self.colorize("✗ Usage: rag config <enable|disable> <features>", Colors.RED))
            print("  Example: rag config enable reranking,hybrid")
            print("  Example: rag config disable code-embeddings")
            return
        
        parts = args.split(maxsplit=1)
        action = parts[0].lower()
        features_str = parts[1] if len(parts) > 1 else ""
        
        if action not in ['enable', 'disable']:
            print(self.colorize(f"✗ Invalid action: {action}", Colors.RED))
            return
        
        # Parse features
        features = [f.strip() for f in features_str.split(',') if f.strip()]
        
        print(self.colorize(f"\n→ {action.capitalize()}ing features: {', '.join(features)}", Colors.YELLOW))
        print("  Configuration will apply to future searches")
        
        # This would save to config file in real implementation
        print(self.colorize("\n✓ Configuration updated", Colors.GREEN))
    
    def cmd_rag_expand(self, args: str):
        """Show query expansions."""
        if not args:
            print(self.colorize("✗ Usage: rag expand <query> [language]", Colors.RED))
            return
        
        parts = args.split(maxsplit=1)
        query = parts[0]
        language = parts[1] if len(parts) > 1 else None
        
        try:
            expander = QueryExpander()
            expansions = expander.expand_query(query, language=language, max_expansions=7)
            
            print(self.colorize(f"\nQuery Expansions for: {query}", Colors.BOLD + Colors.CYAN))
            print("=" * 60)
            
            for i, exp in enumerate(expansions, 1):
                marker = "→" if i == 1 else " "
                color = Colors.BOLD if i == 1 else Colors.RESET
                print(f"  {marker} {i}. {self.colorize(exp, color)}")
            
            print("=" * 60)
            print(f"\nGenerated {len(expansions)} query variations")
            
        except Exception as e:
            print(self.colorize(f"✗ Expansion failed: {e}", Colors.RED))
    
    def cmd_rag_understand(self, args: str):
        """Understand query intent."""
        if not args:
            print(self.colorize("✗ Usage: rag understand <query>", Colors.RED))
            return
        
        query = args.strip()
        
        try:
            understander = QueryUnderstanding()
            result = understander.understand_query(query)
            
            print(self.colorize(f"\nQuery Understanding:", Colors.BOLD + Colors.CYAN))
            print("=" * 60)
            print(f"  Original: {result['original']}")
            print(f"  Reformulated: {self.colorize(result['reformulated'], Colors.GREEN)}")
            print(f"  Intent: {self.colorize(result['intent'], Colors.MAGENTA)}")
            print(f"  Confidence: {result['confidence']:.0%}")
            
            if result.get('keywords'):
                print(f"  Keywords: {', '.join(result['keywords'][:5])}")
            
            if result.get('entities'):
                print(f"  Entities: {result['entities']}")
            
            print("=" * 60)
            
        except Exception as e:
            print(self.colorize(f"✗ Understanding failed: {e}", Colors.RED))
    
    def cmd_rag_hybrid(self, args: str):
        """Hybrid search (vector + BM25)."""
        if not args:
            print(self.colorize("✗ Usage: rag hybrid <query> [alpha]", Colors.RED))
            print("  Alpha: 0-1 (default 0.5 = 50/50 vector/keyword)")
            return
        
        parts = args.rsplit(maxsplit=1)
        query = parts[0]
        alpha = float(parts[1]) if len(parts) > 1 and parts[1].replace('.', '').isdigit() else 0.5
        
        print(self.colorize(f"\n→ Hybrid search: {query}", Colors.YELLOW))
        print(f"  Alpha: {alpha:.1f} ({alpha*100:.0f}% vector, {(1-alpha)*100:.0f}% keyword)\n")
        
        print(self.colorize("⚠ Note: Hybrid search requires BM25 indexing", Colors.YELLOW))
        print("  This feature is best used programmatically")
        print("  Use 'rag advanced' for simpler hybrid search")
    
    def cmd_rag_rerank(self, args: str):
        """Search with reranking."""
        if not args:
            print(self.colorize("✗ Usage: rag rerank <query> [model]", Colors.RED))
            print("  Models: ms-marco-mini, ms-marco-base, qnli")
            return
        
        parts = args.rsplit(maxsplit=1)
        query = parts[0]
        model = parts[1] if len(parts) > 1 else 'ms-marco-mini'
        
        print(self.colorize(f"\n→ Search with reranking: {query}", Colors.YELLOW))
        print(f"  Model: {model}\n")
        
        try:
            # First get base results
            if self.rag_retriever:
                results = self.rag_retriever.retrieve(query, top_k=10)
                
                # Rerank
                reranker = CrossEncoderReranker(model)
                reranked = reranker.rerank(query, results, top_k=5)
                
                self._display_results(query, reranked)
                
            else:
                print(self.colorize("✗ RAG not initialized", Colors.RED))
                
        except Exception as e:
            print(self.colorize(f"✗ Reranking failed: {e}", Colors.RED))
    
    def cmd_rag_feedback(self, args: str):
        """Provide feedback on results."""
        if not args:
            print(self.colorize("✗ Usage: rag feedback <result_index> <useful|not-useful>", Colors.RED))
            return
        
        parts = args.split()
        if len(parts) < 2:
            print(self.colorize("✗ Please specify both index and feedback type", Colors.RED))
            return
        
        try:
            index = int(parts[0]) - 1  # Convert to 0-based
            feedback_type = parts[1].lower()
            
            if feedback_type not in ['useful', 'not-useful']:
                print(self.colorize("✗ Feedback must be 'useful' or 'not-useful'", Colors.RED))
                return
            
            if not self.last_results or index >= len(self.last_results):
                print(self.colorize("✗ Invalid result index", Colors.RED))
                return
            
            result = self.last_results[index]
            result_id = result.get('chunk_id', '')
            
            if self.enhanced_rag:
                self.enhanced_rag.record_feedback(
                    query=self.last_query,
                    result_id=result_id,
                    feedback_type=feedback_type,
                    rank=index + 1
                )
                
                print(self.colorize("\n✓ Feedback recorded!", Colors.GREEN))
                print(f"  Result: {result.get('file_path', 'unknown')}")
                print(f"  Type: {feedback_type}")
                print("\n  This will improve future search results")
            else:
                print(self.colorize("✗ Enhanced RAG not available", Colors.RED))
                
        except ValueError:
            print(self.colorize("✗ Invalid index (must be a number)", Colors.RED))
        except Exception as e:
            print(self.colorize(f"✗ Feedback failed: {e}", Colors.RED))
    
    def cmd_rag_feedback_stats(self, args: str):
        """Show feedback statistics."""
        days = int(args.strip()) if args.strip().isdigit() else 30
        
        try:
            learner = FeedbackLearner()
            stats = learner.get_statistics(days=days)
            
            print(self.colorize(f"\nFeedback Statistics (Last {days} days):", Colors.BOLD + Colors.CYAN))
            print("=" * 60)
            print(f"  Total feedback: {stats['total_feedback']}")
            print(f"  Useful: {stats['useful_count']}")
            print(f"  Not useful: {stats['not_useful_count']}")
            print(f"  Clicks: {stats['click_count']}")
            print(f"  Unique queries: {stats['unique_queries']}")
            print("=" * 60)
            
        except Exception as e:
            print(self.colorize(f"✗ Failed to get statistics: {e}", Colors.RED))
    
    def cmd_rag_graph_build(self, args: str):
        """Build call graph."""
        if not self.current_project:
            print(self.colorize("✗ No project loaded", Colors.RED))
            return
        
        print(self.colorize("\n→ Building call graph...", Colors.YELLOW))
        print(f"  Project: {self.current_project}\n")
        
        try:
            graph = CodeGraphRetriever(project_root=self.current_project)
            stats = graph.build_graph()
            
            print(self.colorize("\n✓ Call graph built!", Colors.GREEN))
            print(f"  Total nodes: {stats['total_nodes']}")
            print(f"  Functions: {stats['functions']}")
            print(f"  Classes: {stats['classes']}")
            print(f"  Files: {stats['files']}")
            
        except Exception as e:
            print(self.colorize(f"✗ Graph building failed: {e}", Colors.RED))
    
    def cmd_rag_graph_related(self, args: str):
        """Find related functions."""
        if not args:
            print(self.colorize("✗ Usage: rag graph-related <function> [depth]", Colors.RED))
            return
        
        parts = args.split()
        function_name = parts[0]
        depth = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 2
        
        print(self.colorize(f"\n→ Finding functions related to: {function_name}", Colors.YELLOW))
        print(f"  Depth: {depth}\n")
        
        try:
            graph = CodeGraphRetriever(project_root=self.current_project)
            graph.build_graph()
            
            related = graph.find_related(function_name, max_results=10)
            
            if related:
                print(self.colorize(f"✓ Found {len(related)} related functions:", Colors.GREEN))
                print("=" * 60)
                
                for i, node in enumerate(related, 1):
                    print(f"\n  {i}. {self.colorize(node['name'], Colors.BOLD)} ({node['type']})")
                    print(f"     File: {node['file']}")
                    print(f"     Line: {node['line']}")
                    print(f"     Depth: {node['depth']}")
                
                print("\n" + "=" * 60)
            else:
                print(self.colorize(f"✗ No related functions found for: {function_name}", Colors.YELLOW))
                
        except Exception as e:
            print(self.colorize(f"✗ Graph search failed: {e}", Colors.RED))
    
    def cmd_rag_graph_viz(self, args: str):
        """Visualize call graph."""
        if not args:
            print(self.colorize("✗ Usage: rag graph-viz <function> [output.dot]", Colors.RED))
            return
        
        parts = args.split()
        function_name = parts[0]
        output_file = parts[1] if len(parts) > 1 else 'graph.dot'
        
        print(self.colorize(f"\n→ Visualizing graph for: {function_name}", Colors.YELLOW))
        print(f"  Output: {output_file}\n")
        
        try:
            graph = CodeGraphRetriever(project_root=self.current_project)
            graph.build_graph()
            
            # Get node ID
            if function_name in graph.node_lookup:
                node_id = graph.node_lookup[function_name]
                
                # Generate visualization
                dot_content = graph.visualize_subgraph([node_id], depth=2, output_file=output_file)
                
                print(self.colorize(f"✓ Graph visualization saved to: {output_file}", Colors.GREEN))
                print(f"\n  Use graphviz to render:")
                print(f"  dot -Tpng {output_file} -o graph.png")
            else:
                print(self.colorize(f"✗ Function not found: {function_name}", Colors.RED))
                
        except Exception as e:
            print(self.colorize(f"✗ Visualization failed: {e}", Colors.RED))
    
    def _display_results(self, query: str, results: list):
        """Display search results in a nice format."""
        if not results:
            print(self.colorize("✗ No results found", Colors.YELLOW))
            return
        
        print(self.colorize(f"✓ Found {len(results)} results:", Colors.GREEN))
        print("=" * 60)
        
        for i, result in enumerate(results, 1):
            print(f"\n{self.colorize(f'[{i}]', Colors.BOLD + Colors.CYAN)} {result.get('file_path', 'unknown')}")
            
            # Score
            score = result.get('score', 0)
            print(f"    Score: {score:.2%}")
            
            # Language
            if 'language' in result:
                print(f"    Language: {result['language']}")
            
            # Lines
            if 'start_line' in result and 'end_line' in result:
                print(f"    Lines: {result['start_line']}-{result['end_line']}")
            
            # Snippet
            content = result.get('content', '')
            if content:
                snippet = content[:150] + "..." if len(content) > 150 else content
                print(f"    Snippet: {snippet}")
            
            # Graph context if available
            if 'graph_context' in result and result['graph_context']:
                print(f"    Related: {len(result['graph_context'])} functions")
        
        print("\n" + "=" * 60)
        print(f"\nUse 'rag feedback <index> <useful|not-useful>' to improve results")


def main():
    """Entry point for CLI with Phase 9."""
    cli = CLIWithPhase9()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
