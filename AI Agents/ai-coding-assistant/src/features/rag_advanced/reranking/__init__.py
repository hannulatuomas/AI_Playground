"""
Reranking and Advanced Search Features

This package contains advanced search and reranking features:
- Cross-encoder reranking
- Hybrid search (vector + BM25)
- Query understanding with LLM
"""

__version__ = '1.9.3'

try:
    from .cross_encoder import CrossEncoderReranker
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False
    CrossEncoderReranker = None

try:
    from .hybrid_search import HybridSearch, BM25
    HYBRID_SEARCH_AVAILABLE = True
except ImportError:
    HYBRID_SEARCH_AVAILABLE = False
    HybridSearch = None
    BM25 = None

try:
    from .query_understanding import QueryUnderstanding
    QUERY_UNDERSTANDING_AVAILABLE = True
except ImportError:
    QUERY_UNDERSTANDING_AVAILABLE = False
    QueryUnderstanding = None


__all__ = [
    'CrossEncoderReranker',
    'HybridSearch',
    'BM25',
    'QueryUnderstanding',
    'CROSS_ENCODER_AVAILABLE',
    'HYBRID_SEARCH_AVAILABLE',
    'QUERY_UNDERSTANDING_AVAILABLE',
]


def get_available_features():
    """Get list of available reranking features."""
    return {
        'cross_encoder': CROSS_ENCODER_AVAILABLE,
        'hybrid_search': HYBRID_SEARCH_AVAILABLE,
        'query_understanding': QUERY_UNDERSTANDING_AVAILABLE
    }


def print_feature_status():
    """Print status of all reranking features."""
    print("Reranking Features Status:")
    print("=" * 50)
    features = get_available_features()
    for name, available in features.items():
        status = "✓ Available" if available else "✗ Not available"
        print(f"  {name:25} {status}")
    print("=" * 50)


if __name__ == "__main__":
    print_feature_status()
