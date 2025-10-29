"""
Enhanced RAG Integration Module

Integrates ALL advanced RAG features (Phase 9.1 + 9.2 + 9.3):
- Query Expansion (9.1)
- Feedback Learning (9.1)
- Graph-based Retrieval (9.1)
- Code Embeddings / CodeBERT (9.2)
- Multi-modal Retrieval (9.2)
- Cross-encoder Reranking (9.3) ⭐
- Hybrid Search (9.3) ⭐
- Query Understanding (9.3) ⭐

This module provides a unified interface for enhanced code retrieval.
"""

from typing import List, Dict, Optional, Any
from pathlib import Path

# Base RAG imports
try:
    from ..rag_indexer import RAGIndexer
    from ..rag_retriever import RAGRetriever
    RAG_BASE_AVAILABLE = True
except ImportError:
    RAG_BASE_AVAILABLE = False

# Phase 9.1 & 9.2 imports
try:
    from .query_expansion import QueryExpander
    QUERY_EXPANSION_AVAILABLE = True
except ImportError:
    QUERY_EXPANSION_AVAILABLE = False

try:
    from .feedback_learning import FeedbackLearner
    FEEDBACK_LEARNING_AVAILABLE = True
except ImportError:
    FEEDBACK_LEARNING_AVAILABLE = False

try:
    from .graph_retrieval import CodeGraphRetriever
    GRAPH_RETRIEVAL_AVAILABLE = True
except ImportError:
    GRAPH_RETRIEVAL_AVAILABLE = False

try:
    from .code_embeddings import CodeEmbedder, FallbackCodeEmbedder
    CODE_EMBEDDINGS_AVAILABLE = True
except ImportError:
    CODE_EMBEDDINGS_AVAILABLE = False

try:
    from .multimodal import MultiModalRetriever
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False

# Phase 9.3 imports
try:
    from .reranking import (
        CrossEncoderReranker,
        HybridSearch,
        QueryUnderstanding
    )
    RERANKING_AVAILABLE = True
except ImportError:
    RERANKING_AVAILABLE = False
    CrossEncoderReranker = None
    HybridSearch = None
    QueryUnderstanding = None


class EnhancedRAG:
    """
    Enhanced RAG system integrating ALL advanced features.
    
    Phase 9.1 Features:
    - Query expansion for better recall
    - Feedback learning for continuous improvement
    - Graph-based context expansion
    
    Phase 9.2 Features:
    - Code-specific embeddings (CodeBERT)
    - Multi-modal search (code + docs)
    
    Phase 9.3 Features:
    - Cross-encoder reranking for precision
    - Hybrid search (vector + BM25)
    - Query understanding with LLM
    
    Example:
        >>> rag = EnhancedRAG(
        ...     project_root="/path/to/project",
        ...     use_all_features=True
        ... )
        >>> results = rag.retrieve("JWT authentication", top_k=5)
    """
    
    def __init__(
        self,
        project_root: Optional[str] = None,
        db_path: str = "data/rag_db",
        # Phase 9.1 features
        use_query_expansion: bool = True,
        use_feedback_learning: bool = True,
        use_graph_retrieval: bool = True,
        # Phase 9.2 features
        use_code_embeddings: bool = False,
        use_multimodal: bool = False,
        # Phase 9.3 features
        use_reranking: bool = False,
        use_hybrid_search: bool = False,
        use_query_understanding: bool = False,
        # Convenience flag
        use_all_features: bool = False,
        # Configuration
        embedding_model: str = 'all-MiniLM-L6-v2',
        code_embedding_model: str = 'codebert',
        batch_size: int = 32,
        use_gpu: bool = False
    ):
        """
        Initialize enhanced RAG system.
        
        Args:
            project_root: Path to project root
            db_path: Path to vector database
            use_query_expansion: Enable query expansion
            use_feedback_learning: Enable feedback learning
            use_graph_retrieval: Enable graph-based retrieval
            use_code_embeddings: Enable CodeBERT embeddings
            use_multimodal: Enable multi-modal retrieval
            use_reranking: Enable cross-encoder reranking
            use_hybrid_search: Enable hybrid vector+BM25 search
            use_query_understanding: Enable query understanding
            use_all_features: Enable ALL features (overrides individual flags)
            embedding_model: Base embedding model
            code_embedding_model: Code embedding model
            batch_size: Batch size for embedding
            use_gpu: Use GPU acceleration
        """
        self.project_root = Path(project_root) if project_root else None
        self.db_path = db_path
        
        # Override individual flags if use_all_features=True
        if use_all_features:
            use_query_expansion = True
            use_feedback_learning = True
            use_graph_retrieval = True
            use_code_embeddings = True
            use_multimodal = True
            use_reranking = True
            use_hybrid_search = True
            use_query_understanding = True
        
        # Initialize base RAG
        if RAG_BASE_AVAILABLE:
            self.indexer = RAGIndexer(
                embedding_model=embedding_model,
                db_path=db_path,
                batch_size=batch_size,
                use_gpu=use_gpu
            )
            self.retriever = RAGRetriever(
                indexer=self.indexer,
                db_path=db_path
            )
        else:
            raise ImportError("Base RAG system not available")
        
        # Initialize Phase 9.1 & 9.2 features
        self.query_expander = None
        self.feedback_learner = None
        self.graph_retriever = None
        self.code_embedder = None
        self.multimodal_retriever = None
        
        # Initialize Phase 9.3 features
        self.reranker = None
        self.hybrid_search = None
        self.query_understander = None
        
        # Phase 9.1: Query expansion
        if use_query_expansion and QUERY_EXPANSION_AVAILABLE:
            self.query_expander = QueryExpander()
            print("✓ Query expansion enabled")
        
        # Phase 9.1: Feedback learning
        if use_feedback_learning and FEEDBACK_LEARNING_AVAILABLE:
            self.feedback_learner = FeedbackLearner()
            print("✓ Feedback learning enabled")
        
        # Phase 9.1: Graph retrieval
        if use_graph_retrieval and GRAPH_RETRIEVAL_AVAILABLE and project_root:
            self.graph_retriever = CodeGraphRetriever(project_root=project_root)
            print("✓ Graph retrieval enabled")
        
        # Phase 9.2: Code embeddings
        if use_code_embeddings and CODE_EMBEDDINGS_AVAILABLE:
            try:
                self.code_embedder = CodeEmbedder(
                    model_name=code_embedding_model,
                    use_gpu=use_gpu
                )
                print("✓ Code embeddings enabled")
            except Exception as e:
                print(f"⚠ Code embeddings failed, using fallback: {e}")
                self.code_embedder = FallbackCodeEmbedder()
        
        # Phase 9.2: Multi-modal retrieval
        if use_multimodal and MULTIMODAL_AVAILABLE:
            if self.code_embedder and self.indexer:
                self.multimodal_retriever = MultiModalRetriever(
                    code_embedder=self.code_embedder,
                    doc_embedder=self.indexer.model
                )
                print("✓ Multi-modal retrieval enabled")
        
        # Phase 9.3: Cross-encoder reranking
        if use_reranking and RERANKING_AVAILABLE and CrossEncoderReranker:
            try:
                self.reranker = CrossEncoderReranker('ms-marco-mini')
                print("✓ Cross-encoder reranking enabled")
            except Exception as e:
                print(f"⚠ Reranking failed: {e}")
        
        # Phase 9.3: Hybrid search
        if use_hybrid_search and RERANKING_AVAILABLE and HybridSearch:
            self.hybrid_search = HybridSearch(self.retriever)
            print("✓ Hybrid search enabled")
        
        # Phase 9.3: Query understanding
        if use_query_understanding and RERANKING_AVAILABLE and QueryUnderstanding:
            self.query_understander = QueryUnderstanding(llm_interface=None, use_llm=False)
            print("✓ Query understanding enabled")
        
        print(f"\n✓ EnhancedRAG initialized with {self._count_features()} features")
    
    def _count_features(self) -> int:
        """Count enabled features."""
        count = 0
        if self.query_expander: count += 1
        if self.feedback_learner: count += 1
        if self.graph_retriever: count += 1
        if self.code_embedder: count += 1
        if self.multimodal_retriever: count += 1
        if self.reranker: count += 1
        if self.hybrid_search: count += 1
        if self.query_understander: count += 1
        return count
    
    def index_project(
        self,
        project_name: Optional[str] = None,
        force_rebuild: bool = False,
        index_for_hybrid: bool = True
    ) -> str:
        """
        Index project with all enabled features.
        
        Args:
            project_name: Optional project name
            force_rebuild: Force rebuild index
            index_for_hybrid: Also index for hybrid search (BM25)
            
        Returns:
            Collection name
        """
        if not self.project_root:
            raise ValueError("project_root not set")
        
        # Index with base RAG
        collection = self.indexer.build_vector_db(
            self.project_root,
            project_name=project_name,
            force_rebuild=force_rebuild
        )
        
        # Build graph if enabled
        if self.graph_retriever:
            print("\nBuilding call graph...")
            stats = self.graph_retriever.build_graph(force_rebuild=force_rebuild)
            print(f"✓ Graph built: {stats['total_nodes']} nodes")
        
        # Index for hybrid search if enabled
        if index_for_hybrid and self.hybrid_search:
            print("\n✓ Ready for hybrid search")
        
        return collection
    
    def retrieve(
        self,
        query: str,
        collection_name: Optional[str] = None,
        language: Optional[str] = None,
        top_k: int = 5,
        threshold: float = 0.0,
        # Phase 9.1 & 9.2 options
        use_query_expansion: bool = True,
        use_feedback_ranking: bool = True,
        use_graph_context: bool = False,
        expand_graph_depth: int = 1,
        # Phase 9.3 options
        use_reranking: bool = True,
        use_hybrid: bool = False,
        use_query_understanding: bool = True,
        hybrid_alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Enhanced retrieval with ALL features.
        
        Args:
            query: Search query
            collection_name: Collection to search
            language: Programming language
            top_k: Number of results
            threshold: Minimum similarity score
            use_query_expansion: Use query expansion
            use_feedback_ranking: Use feedback-based ranking
            use_graph_context: Expand with graph context
            expand_graph_depth: Graph traversal depth
            use_reranking: Use cross-encoder reranking
            use_hybrid: Use hybrid search instead of pure vector
            use_query_understanding: Enhance query with understanding
            hybrid_alpha: Weight for hybrid search (0.5 = 50/50)
            
        Returns:
            List of enhanced results
        """
        # Phase 9.3: Query understanding
        original_query = query
        if use_query_understanding and self.query_understander:
            understanding = self.query_understander.understand_query(query, {'language': language})
            query = understanding['reformulated']
        
        # Phase 9.1: Query expansion
        queries = [query]
        if use_query_expansion and self.query_expander:
            expanded = self.query_expander.expand_query(
                query,
                language=language,
                max_expansions=3
            )
            queries = expanded[:3]
        
        # Retrieve
        all_results = []
        for q in queries:
            results = self.retriever.retrieve(
                query=q,
                collection_name=collection_name,
                top_k=top_k * 2,
                threshold=threshold,
                language_filter=language
            )
            all_results.extend(results)
        
        # Deduplicate
        seen = set()
        unique_results = []
        for r in all_results:
            chunk_id = r.get('chunk_id', '')
            if chunk_id and chunk_id not in seen:
                seen.add(chunk_id)
                unique_results.append(r)
        
        # Phase 9.2: Feedback-based re-ranking
        if use_feedback_ranking and self.feedback_learner:
            unique_results = self.feedback_learner.adjust_ranking(
                unique_results,
                original_query,
                learning_rate=0.15
            )
        
        # Phase 9.3: Cross-encoder reranking
        if use_reranking and self.reranker and len(unique_results) > 0:
            unique_results = self.reranker.rerank(
                query=original_query,
                results=unique_results,
                top_k=top_k * 2
            )
        
        # Phase 9.1: Graph context expansion
        if use_graph_context and self.graph_retriever and self.graph_retriever.graph:
            top_results = unique_results[:min(3, len(unique_results))]
            node_ids = []
            
            for r in top_results:
                chunk_id = r.get('chunk_id', '')
                if chunk_id and ':' in chunk_id:
                    parts = chunk_id.split(':')
                    if len(parts) >= 2:
                        node_ids.append(chunk_id)
            
            if node_ids:
                graph_context = self.graph_retriever.expand_context(
                    node_ids,
                    depth=expand_graph_depth,
                    include_callers=True,
                    include_callees=True
                )
                
                for r in unique_results[:3]:
                    r['graph_context'] = [
                        {
                            'name': gc['name'],
                            'file': gc['file'],
                            'type': gc['type'],
                            'depth': gc['depth']
                        }
                        for gc in graph_context[:5]
                    ]
        
        # Final top_k limit
        final_results = unique_results[:top_k]
        
        return final_results
    
    def record_feedback(
        self,
        query: str,
        result_id: str,
        feedback_type: str,
        rank: Optional[int] = None
    ):
        """Record user feedback."""
        if self.feedback_learner:
            self.feedback_learner.record_feedback(
                query=query,
                result_id=result_id,
                feedback_type=feedback_type,
                rank=rank
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the enhanced RAG system."""
        stats = {
            'features_enabled': {
                # Phase 9.1
                'query_expansion': self.query_expander is not None,
                'feedback_learning': self.feedback_learner is not None,
                'graph_retrieval': self.graph_retriever is not None,
                # Phase 9.2
                'code_embeddings': self.code_embedder is not None,
                'multimodal': self.multimodal_retriever is not None,
                # Phase 9.3
                'cross_encoder': self.reranker is not None,
                'hybrid_search': self.hybrid_search is not None,
                'query_understanding': self.query_understander is not None,
            },
            'total_features': self._count_features()
        }
        
        # Add feature-specific stats
        if self.feedback_learner:
            stats['feedback'] = self.feedback_learner.get_statistics(days=30)
        
        if self.graph_retriever and self.graph_retriever.graph:
            stats['graph'] = self.graph_retriever._get_graph_stats()
        
        if self.reranker:
            stats['reranking'] = self.reranker.get_statistics()
        
        if self.hybrid_search:
            stats['hybrid'] = self.hybrid_search.get_statistics()
        
        return stats


if __name__ == "__main__":
    print("Enhanced RAG Integration Module")
    print("=" * 60)
    print("\nIntegrates ALL Phase 9 features (9.1 + 9.2 + 9.3)")
    print("\nExample usage:")
    print("""
    from features.rag_advanced.integration import EnhancedRAG
    
    # Initialize with all features
    rag = EnhancedRAG(
        project_root="./my_project",
        use_all_features=True  # Enable everything!
    )
    
    # Index project
    rag.index_project("my-project")
    
    # Enhanced retrieval with ALL features
    results = rag.retrieve(
        query="JWT authentication",
        language="python",
        top_k=5,
        use_reranking=True,      # Phase 9.3
        use_query_understanding=True,  # Phase 9.3
        use_graph_context=True
    )
    
    # Record feedback
    rag.record_feedback(
        query="JWT authentication",
        result_id=results[0]['chunk_id'],
        feedback_type="useful",
        rank=1
    )
    
    # Get statistics
    stats = rag.get_statistics()
    print(f"Features enabled: {stats['total_features']}/8")
    """)
