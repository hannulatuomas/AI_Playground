"""
RAG Performance Integration Module

Integrates all performance optimizations with RAG components.
Provides a unified interface for optimal RAG performance.

Usage:
    >>> from src.core.rag_performance import create_optimized_rag
    >>> indexer, retriever, memory_mgr = create_optimized_rag(preset='fast')
    >>> collection = indexer.build_vector_db('/path/to/project')
    >>> results = retriever.retrieve("authentication code")
"""

from typing import Optional, Tuple, Dict, Any
from pathlib import Path

# Import performance components
try:
    from src.core.performance_config import (
        get_preset_config,
        detect_optimal_config,
        PerformanceConfig
    )
    from src.core.embedding_cache import EmbeddingCache
    from src.core.query_cache import QueryCache
    from src.core.memory_manager import MemoryManager
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False
    print("Warning: Performance optimization modules not available")

# Import RAG components
try:
    from src.features.rag_indexer import RAGIndexer
    from src.features.rag_retriever import RAGRetriever
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("Warning: RAG modules not available")


class OptimizedRAGSystem:
    """
    Fully integrated RAG system with performance optimizations.
    
    Combines RAG indexing/retrieval with caching and memory management.
    """
    
    def __init__(
        self,
        config: Optional[PerformanceConfig] = None,
        preset: str = 'default'
    ):
        """
        Initialize optimized RAG system.
        
        Args:
            config: Performance configuration (if None, uses preset)
            preset: Preset name if config not provided
        
        Example:
            >>> system = OptimizedRAGSystem(preset='fast')
            >>> system.index_project('/path/to/project')
            >>> results = system.search("authentication code")
        """
        if not PERFORMANCE_AVAILABLE or not RAG_AVAILABLE:
            raise ImportError(
                "Required modules not available. "
                "Ensure RAG and performance modules are installed."
            )
        
        # Load configuration
        if config is None:
            self.config = get_preset_config(preset)
        else:
            self.config = config
        
        # Create caches
        self.embedding_cache = EmbeddingCache(
            max_size=self.config.memory.max_embedding_cache_size,
            strategy=self.config.search.cache_strategy,
            enable_persistence=True
        )
        
        self.query_cache = QueryCache(
            max_size=1000,
            ttl_seconds=self.config.search.cache_ttl_seconds,
            strategy=self.config.search.cache_strategy,
            enable_persistence=True
        )
        
        # Create memory manager
        self.memory_mgr = MemoryManager(
            gc_threshold_mb=self.config.memory.gc_threshold_mb,
            enable_auto_gc=self.config.memory.enable_auto_gc,
            gc_interval_seconds=self.config.memory.gc_interval_seconds,
            enable_model_unloading=self.config.memory.unload_model_on_idle,
            model_idle_timeout_seconds=self.config.memory.model_idle_timeout_seconds
        )
        
        # Create RAG components with optimizations
        self.indexer = RAGIndexer(
            embedding_model=self.config.embedding.model_name,
            batch_size=self.config.embedding.batch_size,
            use_gpu=self.config.embedding.use_gpu,
            quantize=self.config.embedding.enable_quantization
        )
        
        self.retriever = None  # Created when needed
        self.current_collection = None
        
        # Register callbacks
        self._register_callbacks()
        
        # Start monitoring
        self.memory_mgr.start_monitoring()
        
        print(f"✓ OptimizedRAGSystem initialized with '{preset}' preset")
    
    def _register_callbacks(self):
        """Register cleanup callbacks with memory manager."""
        # Clear caches on cleanup
        self.memory_mgr.register_cleanup_callback(self.embedding_cache.clear)
        self.memory_mgr.register_cleanup_callback(self.query_cache.clear)
        
        # Unload model on idle
        self.memory_mgr.register_model_unload_callback(self.indexer.unload_model)
    
    def index_project(
        self,
        root_folder: str,
        project_name: Optional[str] = None,
        force_rebuild: bool = False
    ) -> str:
        """
        Index a project with performance optimizations.
        
        Args:
            root_folder: Project root folder
            project_name: Optional project name
            force_rebuild: Force rebuild if already indexed
        
        Returns:
            Collection name
        
        Example:
            >>> collection = system.index_project('/path/to/project')
            >>> print(f"Indexed: {collection}")
        """
        # Mark model activity
        self.memory_mgr.mark_model_activity()
        
        # Use adaptive batch sizing
        original_batch_size = self.indexer.batch_size
        self.indexer.batch_size = self.memory_mgr.get_adaptive_batch_size(
            base_batch_size=original_batch_size,
            max_batch_memory_mb=self.config.memory.max_batch_memory_mb
        )
        
        try:
            # Index project
            collection_name = self.indexer.build_vector_db(
                root_folder=root_folder,
                project_name=project_name,
                force_rebuild=force_rebuild
            )
            
            self.current_collection = collection_name
            
            # Create retriever for this collection
            self.retriever = RAGRetriever(
                indexer=self.indexer,
                collection_name=collection_name
            )
            
            return collection_name
            
        finally:
            # Restore original batch size
            self.indexer.batch_size = original_batch_size
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        language_filter: Optional[str] = None
    ) -> list:
        """
        Search with caching and optimizations.
        
        Args:
            query: Search query
            top_k: Number of results
            language_filter: Optional language filter
        
        Returns:
            List of search results
        
        Example:
            >>> results = system.search("JWT authentication")
            >>> for result in results:
            ...     print(f"{result['file_path']}: {result['score']:.3f}")
        """
        if not self.retriever:
            raise ValueError("No collection indexed. Call index_project() first.")
        
        # Check query cache
        cached_results = self.query_cache.get(query)
        if cached_results is not None:
            print("✓ Query cache hit")
            return cached_results
        
        # Mark model activity
        self.memory_mgr.mark_model_activity()
        
        # Perform retrieval
        results = self.retriever.retrieve(
            query=query,
            collection_name=self.current_collection,
            top_k=top_k,
            language_filter=language_filter
        )
        
        # Cache results
        self.query_cache.put(query, results)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get performance statistics from all components.
        
        Returns:
            Dictionary with comprehensive statistics
        
        Example:
            >>> stats = system.get_statistics()
            >>> print(f"Embedding cache hit rate: {stats['embedding_cache']['hit_rate']}")
        """
        return {
            'embedding_cache': self.embedding_cache.get_stats(),
            'query_cache': self.query_cache.get_stats(),
            'memory': self.memory_mgr.get_statistics(),
            'configuration': {
                'preset': 'custom',
                'model': self.config.embedding.model_name,
                'batch_size': self.config.embedding.batch_size,
                'quantization': self.config.embedding.enable_quantization,
                'gpu': self.config.embedding.use_gpu
            }
        }
    
    def cleanup(self):
        """Clean up resources and save state."""
        print("\nCleaning up OptimizedRAGSystem...")
        
        # Stop monitoring
        self.memory_mgr.stop_monitoring()
        
        # Save caches
        self.embedding_cache.save_to_disk()
        self.query_cache.save_to_disk()
        
        # Unload model
        self.indexer.unload_model()
        
        print("✓ Cleanup complete")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


def create_optimized_rag(
    preset: str = 'default',
    config: Optional[PerformanceConfig] = None
) -> Tuple[RAGIndexer, RAGRetriever, MemoryManager]:
    """
    Create optimized RAG components with performance enhancements.
    
    Args:
        preset: Configuration preset name
        config: Optional custom configuration
    
    Returns:
        Tuple of (indexer, retriever, memory_manager)
    
    Example:
        >>> indexer, retriever, memory_mgr = create_optimized_rag('fast')
        >>> memory_mgr.start_monitoring()
        >>> collection = indexer.build_vector_db('/path/to/project')
        >>> results = retriever.retrieve("authentication")
    """
    if not PERFORMANCE_AVAILABLE or not RAG_AVAILABLE:
        raise ImportError("Required modules not available")
    
    # Load configuration
    if config is None:
        config = get_preset_config(preset)
    
    # Create caches
    embedding_cache = EmbeddingCache(
        max_size=config.memory.max_embedding_cache_size,
        strategy=config.search.cache_strategy
    )
    
    query_cache = QueryCache(
        max_size=1000,
        ttl_seconds=config.search.cache_ttl_seconds,
        strategy=config.search.cache_strategy
    )
    
    # Create memory manager
    memory_mgr = MemoryManager(
        gc_threshold_mb=config.memory.gc_threshold_mb,
        enable_auto_gc=config.memory.enable_auto_gc,
        gc_interval_seconds=config.memory.gc_interval_seconds,
        enable_model_unloading=config.memory.unload_model_on_idle,
        model_idle_timeout_seconds=config.memory.model_idle_timeout_seconds
    )
    
    # Create RAG components
    indexer = RAGIndexer(
        embedding_model=config.embedding.model_name,
        batch_size=config.embedding.batch_size,
        use_gpu=config.embedding.use_gpu,
        quantize=config.embedding.enable_quantization
    )
    
    retriever = RAGRetriever(indexer=indexer)
    
    # Register callbacks
    memory_mgr.register_cleanup_callback(embedding_cache.clear)
    memory_mgr.register_cleanup_callback(query_cache.clear)
    memory_mgr.register_model_unload_callback(indexer.unload_model)
    
    print(f"✓ Created optimized RAG components with '{preset}' preset")
    
    return indexer, retriever, memory_mgr


if __name__ == "__main__":
    print("=== RAG Performance Integration Tests ===\n")
    
    try:
        # Test 1: Create optimized system
        print("1. Creating Optimized RAG System:")
        system = OptimizedRAGSystem(preset='fast')
        print("   ✓ System created\n")
        
        # Test 2: Get statistics
        print("2. Get Statistics:")
        stats = system.get_statistics()
        print(f"   Configuration: {stats['configuration']['model']}")
        print(f"   Batch size: {stats['configuration']['batch_size']}")
        print(f"   Quantization: {stats['configuration']['quantization']}")
        print("   ✓ Statistics retrieved\n")
        
        # Test 3: Test context manager
        print("3. Test Context Manager:")
        with OptimizedRAGSystem(preset='balanced') as sys:
            print("   ✓ Context manager works")
        print("   ✓ Cleanup automatic\n")
        
        # Test 4: Test factory function
        print("4. Test Factory Function:")
        indexer, retriever, memory_mgr = create_optimized_rag('default')
        print("   ✓ Components created")
        print(f"   Model: {indexer.embedding_model_name}")
        print(f"   Batch: {indexer.batch_size}\n")
        
        # Cleanup
        system.cleanup()
        memory_mgr.stop_monitoring()
        
        print("✓ All integration tests passed!")
        
    except ImportError as e:
        print(f"✗ Required packages not installed: {e}")
        print("Install RAG dependencies and performance modules")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
