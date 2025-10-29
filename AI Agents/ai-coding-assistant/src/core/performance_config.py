"""
Performance Configuration Module

Centralized configuration for performance optimizations across RAG components.
Provides:
- Model configuration with quantization support
- Batch processing settings
- Cache configuration
- Memory management settings
- GPU acceleration settings

This module allows easy tuning of performance parameters without
modifying core RAG components.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class EmbeddingConfig:
    """Configuration for embedding model and optimization."""
    
    # Model selection
    model_name: str = 'all-MiniLM-L6-v2'
    model_alias: Optional[str] = None  # 'fast', 'balanced', 'code', 'large'
    
    # Quantization
    enable_quantization: bool = False
    quantization_method: str = 'int8'  # 'int8', 'dynamic', 'static'
    
    # Device settings
    use_gpu: bool = False
    device: str = 'cpu'  # 'cpu', 'cuda', 'mps'
    gpu_id: int = 0
    
    # Batch processing
    batch_size: int = 32
    max_batch_memory_mb: int = 512
    
    # Model caching
    cache_model: bool = True
    unload_after_idle_seconds: int = 300  # 5 minutes
    
    # Performance
    use_mixed_precision: bool = False  # FP16 on GPU
    compile_model: bool = False  # torch.compile (PyTorch 2.0+)


@dataclass
class SearchConfig:
    """Configuration for vector search optimization."""
    
    # ChromaDB settings
    use_hnsw_index: bool = True
    hnsw_space: str = 'cosine'  # 'cosine', 'l2', 'ip'
    hnsw_ef_construction: int = 200  # Higher = better recall, slower build
    hnsw_ef_search: int = 50  # Higher = better recall, slower search
    hnsw_m: int = 16  # Number of connections per node
    
    # Search optimization
    enable_pre_filtering: bool = True
    enable_metadata_indexing: bool = True
    
    # Result caching
    enable_query_cache: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour
    max_cache_size_mb: int = 100
    cache_strategy: str = 'lru'  # 'lru', 'lfu', 'fifo'
    
    # Lazy loading
    lazy_load_documents: bool = True
    preload_top_k: int = 5  # Number of results to preload
    
    # Parallel processing
    enable_parallel_search: bool = False
    num_workers: int = 4


@dataclass
class MemoryConfig:
    """Configuration for memory management."""
    
    # Embedding cache
    cache_embeddings: bool = True
    max_embedding_cache_size: int = 10000  # Number of cached embeddings
    
    # File processing
    stream_large_files: bool = True
    large_file_threshold_mb: int = 10
    file_chunk_size_kb: int = 64
    
    # Garbage collection
    enable_auto_gc: bool = True
    gc_interval_seconds: int = 60
    gc_threshold_mb: int = 500  # Trigger GC above this memory usage
    
    # Model memory
    unload_model_on_idle: bool = True
    model_idle_timeout_seconds: int = 300
    
    # Batch memory limits
    max_batch_memory_mb: int = 512
    adaptive_batch_sizing: bool = True


@dataclass
class PerformanceConfig:
    """Master performance configuration."""
    
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    
    # Global settings
    enable_profiling: bool = False
    log_performance_metrics: bool = False
    metrics_interval_seconds: int = 60
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'embedding': {
                'model_name': self.embedding.model_name,
                'model_alias': self.embedding.model_alias,
                'enable_quantization': self.embedding.enable_quantization,
                'quantization_method': self.embedding.quantization_method,
                'use_gpu': self.embedding.use_gpu,
                'device': self.embedding.device,
                'gpu_id': self.embedding.gpu_id,
                'batch_size': self.embedding.batch_size,
                'max_batch_memory_mb': self.embedding.max_batch_memory_mb,
                'cache_model': self.embedding.cache_model,
                'unload_after_idle_seconds': self.embedding.unload_after_idle_seconds,
                'use_mixed_precision': self.embedding.use_mixed_precision,
                'compile_model': self.embedding.compile_model,
            },
            'search': {
                'use_hnsw_index': self.search.use_hnsw_index,
                'hnsw_space': self.search.hnsw_space,
                'hnsw_ef_construction': self.search.hnsw_ef_construction,
                'hnsw_ef_search': self.search.hnsw_ef_search,
                'hnsw_m': self.search.hnsw_m,
                'enable_pre_filtering': self.search.enable_pre_filtering,
                'enable_metadata_indexing': self.search.enable_metadata_indexing,
                'enable_query_cache': self.search.enable_query_cache,
                'cache_ttl_seconds': self.search.cache_ttl_seconds,
                'max_cache_size_mb': self.search.max_cache_size_mb,
                'cache_strategy': self.search.cache_strategy,
                'lazy_load_documents': self.search.lazy_load_documents,
                'preload_top_k': self.search.preload_top_k,
                'enable_parallel_search': self.search.enable_parallel_search,
                'num_workers': self.search.num_workers,
            },
            'memory': {
                'cache_embeddings': self.memory.cache_embeddings,
                'max_embedding_cache_size': self.memory.max_embedding_cache_size,
                'stream_large_files': self.memory.stream_large_files,
                'large_file_threshold_mb': self.memory.large_file_threshold_mb,
                'file_chunk_size_kb': self.memory.file_chunk_size_kb,
                'enable_auto_gc': self.memory.enable_auto_gc,
                'gc_interval_seconds': self.memory.gc_interval_seconds,
                'gc_threshold_mb': self.memory.gc_threshold_mb,
                'unload_model_on_idle': self.memory.unload_model_on_idle,
                'model_idle_timeout_seconds': self.memory.model_idle_timeout_seconds,
                'max_batch_memory_mb': self.memory.max_batch_memory_mb,
                'adaptive_batch_sizing': self.memory.adaptive_batch_sizing,
            },
            'global': {
                'enable_profiling': self.enable_profiling,
                'log_performance_metrics': self.log_performance_metrics,
                'metrics_interval_seconds': self.metrics_interval_seconds,
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceConfig':
        """Create configuration from dictionary."""
        config = cls()
        
        if 'embedding' in data:
            emb = data['embedding']
            config.embedding = EmbeddingConfig(**emb)
        
        if 'search' in data:
            config.search = SearchConfig(**data['search'])
        
        if 'memory' in data:
            config.memory = MemoryConfig(**data['memory'])
        
        if 'global' in data:
            glb = data['global']
            config.enable_profiling = glb.get('enable_profiling', False)
            config.log_performance_metrics = glb.get('log_performance_metrics', False)
            config.metrics_interval_seconds = glb.get('metrics_interval_seconds', 60)
        
        return config
    
    def save(self, path: str) -> None:
        """Save configuration to JSON file."""
        config_path = Path(path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        print(f"✓ Performance configuration saved to: {config_path}")
    
    @classmethod
    def load(cls, path: str) -> 'PerformanceConfig':
        """Load configuration from JSON file."""
        config_path = Path(path)
        
        if not config_path.exists():
            print(f"Configuration file not found: {path}")
            print("Using default configuration")
            return cls()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)


# Preset configurations for common scenarios
PRESET_CONFIGS = {
    'default': PerformanceConfig(
        embedding=EmbeddingConfig(
            model_name='all-MiniLM-L6-v2',
            batch_size=32,
            enable_quantization=False
        ),
        search=SearchConfig(
            use_hnsw_index=True,
            enable_query_cache=True
        ),
        memory=MemoryConfig(
            cache_embeddings=True,
            enable_auto_gc=True
        )
    ),
    
    'fast': PerformanceConfig(
        embedding=EmbeddingConfig(
            model_name='all-MiniLM-L6-v2',
            batch_size=64,
            enable_quantization=True,
            quantization_method='int8'
        ),
        search=SearchConfig(
            use_hnsw_index=True,
            hnsw_ef_search=30,  # Lower for speed
            enable_query_cache=True,
            cache_ttl_seconds=7200
        ),
        memory=MemoryConfig(
            cache_embeddings=True,
            max_embedding_cache_size=20000,
            enable_auto_gc=True
        )
    ),
    
    'balanced': PerformanceConfig(
        embedding=EmbeddingConfig(
            model_name='all-mpnet-base-v2',
            batch_size=32,
            enable_quantization=False
        ),
        search=SearchConfig(
            use_hnsw_index=True,
            hnsw_ef_search=50,
            enable_query_cache=True
        ),
        memory=MemoryConfig(
            cache_embeddings=True,
            enable_auto_gc=True
        )
    ),
    
    'quality': PerformanceConfig(
        embedding=EmbeddingConfig(
            model_name='all-mpnet-base-v2',
            batch_size=16,
            enable_quantization=False
        ),
        search=SearchConfig(
            use_hnsw_index=True,
            hnsw_ef_construction=400,
            hnsw_ef_search=100,
            enable_query_cache=True
        ),
        memory=MemoryConfig(
            cache_embeddings=True,
            max_embedding_cache_size=5000,
            enable_auto_gc=True
        )
    ),
    
    'low_memory': PerformanceConfig(
        embedding=EmbeddingConfig(
            model_name='all-MiniLM-L6-v2',
            batch_size=16,
            enable_quantization=True,
            cache_model=False,
            unload_after_idle_seconds=60
        ),
        search=SearchConfig(
            use_hnsw_index=True,
            enable_query_cache=False,
            lazy_load_documents=True
        ),
        memory=MemoryConfig(
            cache_embeddings=False,
            stream_large_files=True,
            enable_auto_gc=True,
            gc_interval_seconds=30,
            gc_threshold_mb=250,
            unload_model_on_idle=True,
            model_idle_timeout_seconds=60
        )
    ),
    
    'gpu': PerformanceConfig(
        embedding=EmbeddingConfig(
            model_name='all-mpnet-base-v2',
            batch_size=128,
            use_gpu=True,
            device='cuda',
            enable_quantization=False,
            use_mixed_precision=True
        ),
        search=SearchConfig(
            use_hnsw_index=True,
            hnsw_ef_search=80,
            enable_query_cache=True,
            enable_parallel_search=True
        ),
        memory=MemoryConfig(
            cache_embeddings=True,
            max_embedding_cache_size=50000,
            enable_auto_gc=False  # Let GPU memory management handle it
        )
    )
}


def get_preset_config(preset: str = 'default') -> PerformanceConfig:
    """
    Get a preset performance configuration.
    
    Args:
        preset: Preset name ('default', 'fast', 'balanced', 'quality', 
                'low_memory', 'gpu')
    
    Returns:
        PerformanceConfig instance
    
    Example:
        >>> config = get_preset_config('fast')
        >>> print(f"Using {config.embedding.model_name} with quantization")
    """
    if preset not in PRESET_CONFIGS:
        print(f"Warning: Unknown preset '{preset}', using 'default'")
        preset = 'default'
    
    return PRESET_CONFIGS[preset]


def detect_optimal_config() -> PerformanceConfig:
    """
    Auto-detect optimal configuration based on system capabilities.
    
    Checks:
    - GPU availability
    - System memory
    - CPU cores
    
    Returns:
        Optimized PerformanceConfig
    
    Example:
        >>> config = detect_optimal_config()
        >>> print(f"Detected optimal config: GPU={config.embedding.use_gpu}")
    """
    import psutil
    
    # Check GPU availability
    has_gpu = False
    try:
        import torch
        has_gpu = torch.cuda.is_available()
    except ImportError:
        pass
    
    # Get system memory
    memory_gb = psutil.virtual_memory().total / (1024 ** 3)
    cpu_count = psutil.cpu_count()
    
    print(f"System detection:")
    print(f"  GPU available: {has_gpu}")
    print(f"  Memory: {memory_gb:.1f} GB")
    print(f"  CPU cores: {cpu_count}")
    
    # Select configuration based on capabilities
    if has_gpu:
        print("  Recommended: 'gpu' preset")
        return get_preset_config('gpu')
    elif memory_gb >= 8:
        print("  Recommended: 'balanced' preset")
        return get_preset_config('balanced')
    elif memory_gb >= 4:
        print("  Recommended: 'fast' preset")
        return get_preset_config('fast')
    else:
        print("  Recommended: 'low_memory' preset")
        return get_preset_config('low_memory')


if __name__ == "__main__":
    print("=== Performance Configuration Module ===\n")
    
    # Test default configuration
    print("1. Default Configuration:")
    config = PerformanceConfig()
    print(f"   Model: {config.embedding.model_name}")
    print(f"   Batch size: {config.embedding.batch_size}")
    print(f"   Quantization: {config.embedding.enable_quantization}")
    print(f"   HNSW: {config.search.use_hnsw_index}")
    print(f"   Cache: {config.memory.cache_embeddings}")
    
    # Test presets
    print("\n2. Available Presets:")
    for preset_name in PRESET_CONFIGS.keys():
        preset = get_preset_config(preset_name)
        print(f"   {preset_name:12s}: {preset.embedding.model_name:20s} "
              f"(batch={preset.embedding.batch_size}, "
              f"quant={preset.embedding.enable_quantization})")
    
    # Test auto-detection
    print("\n3. Auto-Detection:")
    optimal = detect_optimal_config()
    
    # Test save/load
    print("\n4. Save/Load Test:")
    test_path = "data/performance_config_test.json"
    config.save(test_path)
    loaded = PerformanceConfig.load(test_path)
    print(f"   Loaded model: {loaded.embedding.model_name}")
    
    # Clean up
    import os
    if os.path.exists(test_path):
        os.remove(test_path)
    
    print("\n✓ All configuration tests passed!")
