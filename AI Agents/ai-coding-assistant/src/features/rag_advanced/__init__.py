"""
Advanced RAG Features

This package contains advanced RAG features for improved code retrieval:
- Fine-tuned code embeddings (CodeBERT) ✓
- Multi-modal retrieval (code + documentation) ✓
- Graph-based retrieval (AST call graphs) ✓
- Query expansion (synonyms, reformulation) ✓
- User feedback learning (personalization) ✓
- Cross-encoder reranking ✓
- Hybrid search (vector + BM25) ✓
- Query understanding with LLM ✓
"""

__version__ = '1.9.3'

# Phase 9.1 & 9.2 imports
try:
    from .code_embeddings import CodeEmbedder, FallbackCodeEmbedder
    CODE_EMBEDDINGS_AVAILABLE = True
except ImportError:
    CODE_EMBEDDINGS_AVAILABLE = False
    CodeEmbedder = None
    FallbackCodeEmbedder = None

try:
    from .multimodal import MultiModalRetriever
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False
    MultiModalRetriever = None

try:
    from .graph_retrieval import CodeGraphRetriever
    GRAPH_RETRIEVAL_AVAILABLE = True
except ImportError:
    GRAPH_RETRIEVAL_AVAILABLE = False
    CodeGraphRetriever = None

try:
    from .query_expansion import QueryExpander
    QUERY_EXPANSION_AVAILABLE = True
except ImportError:
    QUERY_EXPANSION_AVAILABLE = False
    QueryExpander = None

try:
    from .feedback_learning import FeedbackLearner
    FEEDBACK_LEARNING_AVAILABLE = True
except ImportError:
    FEEDBACK_LEARNING_AVAILABLE = False
    FeedbackLearner = None

try:
    from .integration import EnhancedRAG
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    EnhancedRAG = None

# Phase 9.3 imports
try:
    from .reranking import (
        CrossEncoderReranker,
        HybridSearch,
        BM25,
        QueryUnderstanding,
        CROSS_ENCODER_AVAILABLE,
        HYBRID_SEARCH_AVAILABLE,
        QUERY_UNDERSTANDING_AVAILABLE
    )
    RERANKING_AVAILABLE = True
except ImportError:
    RERANKING_AVAILABLE = False
    CrossEncoderReranker = None
    HybridSearch = None
    BM25 = None
    QueryUnderstanding = None
    CROSS_ENCODER_AVAILABLE = False
    HYBRID_SEARCH_AVAILABLE = False
    QUERY_UNDERSTANDING_AVAILABLE = False


__all__ = [
    # Phase 9.1 & 9.2
    'CodeEmbedder',
    'FallbackCodeEmbedder',
    'MultiModalRetriever',
    'CodeGraphRetriever',
    'QueryExpander',
    'FeedbackLearner',
    'EnhancedRAG',
    # Phase 9.3
    'CrossEncoderReranker',
    'HybridSearch',
    'BM25',
    'QueryUnderstanding',
    # Availability flags
    'CODE_EMBEDDINGS_AVAILABLE',
    'MULTIMODAL_AVAILABLE',
    'GRAPH_RETRIEVAL_AVAILABLE',
    'QUERY_EXPANSION_AVAILABLE',
    'FEEDBACK_LEARNING_AVAILABLE',
    'INTEGRATION_AVAILABLE',
    'RERANKING_AVAILABLE',
    'CROSS_ENCODER_AVAILABLE',
    'HYBRID_SEARCH_AVAILABLE',
    'QUERY_UNDERSTANDING_AVAILABLE',
]


def get_available_features():
    """Get list of all available advanced RAG features."""
    return {
        # Phase 9.1
        'query_expansion': QUERY_EXPANSION_AVAILABLE,
        'feedback_learning': FEEDBACK_LEARNING_AVAILABLE,
        'graph_retrieval': GRAPH_RETRIEVAL_AVAILABLE,
        # Phase 9.2
        'code_embeddings': CODE_EMBEDDINGS_AVAILABLE,
        'multimodal': MULTIMODAL_AVAILABLE,
        'integration': INTEGRATION_AVAILABLE,
        # Phase 9.3
        'cross_encoder': CROSS_ENCODER_AVAILABLE,
        'hybrid_search': HYBRID_SEARCH_AVAILABLE,
        'query_understanding': QUERY_UNDERSTANDING_AVAILABLE,
    }


def print_feature_status():
    """Print status of all advanced features."""
    print("Advanced RAG Features Status (Phase 9.1 + 9.2 + 9.3):")
    print("=" * 60)
    
    features = get_available_features()
    
    print("\n Phase 9.1 - Foundation:")
    for name in ['query_expansion', 'feedback_learning', 'graph_retrieval']:
        status = "✓ Available" if features[name] else "✗ Not available"
        print(f"  {name:25} {status}")
    
    print("\n Phase 9.2 - Code Understanding:")
    for name in ['code_embeddings', 'multimodal', 'integration']:
        status = "✓ Available" if features[name] else "✗ Not available"
        print(f"  {name:25} {status}")
    
    print("\n Phase 9.3 - Advanced Features:")
    for name in ['cross_encoder', 'hybrid_search', 'query_understanding']:
        status = "✓ Available" if features[name] else "✗ Not available"
        print(f"  {name:25} {status}")
    
    print("=" * 60)
    
    total = len(features)
    available = sum(1 for v in features.values() if v)
    print(f"\nTotal: {available}/{total} features available ({available/total*100:.0f}%)")


if __name__ == "__main__":
    print_feature_status()
