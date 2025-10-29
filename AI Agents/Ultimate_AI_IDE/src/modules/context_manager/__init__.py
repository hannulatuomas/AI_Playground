"""
Context Manager Module

Manages context for large codebases using embeddings.
Phase 4 implementation + v1.6.0 Advanced RAG features.
"""

from .manager import ContextManager
from .summarizer import CodeSummarizer, CodeSummary
from .embedder import CodeEmbedder, EmbeddingIndex
from .retriever import ContextRetriever, RetrievedContext
from .window_manager import WindowManager, Message

# v1.6.0 Advanced RAG features
from .code_embedder_advanced import CodeBERTEmbedder, CodeBERTIndex
from .multimodal_retriever import MultiModalRetriever, MultiModalResult
from .query_enhancer import QueryEnhancer
from .graph_retriever import GraphRetriever, CallGraphBuilder, CodeNode

__all__ = [
    # Core
    'ContextManager',
    'CodeSummarizer',
    'CodeSummary',
    'CodeEmbedder',
    'EmbeddingIndex',
    'ContextRetriever',
    'RetrievedContext',
    'WindowManager',
    'Message',
    # v1.6.0 Advanced RAG
    'CodeBERTEmbedder',
    'CodeBERTIndex',
    'MultiModalRetriever',
    'MultiModalResult',
    'QueryEnhancer',
    'GraphRetriever',
    'CallGraphBuilder',
    'CodeNode'
]
