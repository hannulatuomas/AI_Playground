"""
Multi-Modal Retriever

Retrieves context from both code and documentation using separate embeddings.
Part of v1.6.0 - Advanced RAG & Retrieval.
"""

import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import numpy as np

from .code_embedder_advanced import CodeBERTEmbedder
from .embedder import CodeEmbedder

logger = logging.getLogger(__name__)


@dataclass
class MultiModalResult:
    """Result from multi-modal retrieval."""
    content: str
    source_type: str  # 'code' or 'doc'
    file_path: str
    similarity: float
    metadata: Dict[str, Any]


class MultiModalRetriever:
    """
    Multi-modal retriever for code and documentation.
    
    Features:
    - Separate embeddings for code and docs
    - Cross-modal search
    - Weighted combination
    - Better context building
    """
    
    def __init__(
        self,
        code_embedder: Optional[CodeBERTEmbedder] = None,
        doc_embedder: Optional[CodeEmbedder] = None,
        code_weight: float = 0.6,
        doc_weight: float = 0.4
    ):
        """
        Initialize multi-modal retriever.
        
        Args:
            code_embedder: Embedder for code
            doc_embedder: Embedder for documentation
            code_weight: Weight for code results (0-1)
            doc_weight: Weight for doc results (0-1)
        """
        self.code_embedder = code_embedder or CodeBERTEmbedder()
        self.doc_embedder = doc_embedder or CodeEmbedder()
        self.code_weight = code_weight
        self.doc_weight = doc_weight
        
        # Indices
        self.code_index = {}  # file_path -> List[(chunk, embedding)]
        self.doc_index = {}   # file_path -> List[(chunk, embedding)]
        
        # Metadata
        self.code_metadata = {}
        self.doc_metadata = {}
        
        logger.info("Initialized MultiModalRetriever")
    
    def index_code_file(self, file_path: str, chunk_size: int = 100) -> bool:
        """
        Index a code file.
        
        Args:
            file_path: Path to code file
            chunk_size: Lines per chunk
            
        Returns:
            True if successful
        """
        try:
            embeddings = self.code_embedder.embed_file(file_path, chunk_size)
            self.code_index[file_path] = embeddings
            
            self.code_metadata[file_path] = {
                'type': 'code',
                'chunks': len(embeddings),
                'language': Path(file_path).suffix,
                'size': os.path.getsize(file_path)
            }
            
            logger.debug(f"Indexed code file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index code file {file_path}: {e}")
            return False
    
    def index_doc_file(self, file_path: str, chunk_size: int = 500) -> bool:
        """
        Index a documentation file.
        
        Args:
            file_path: Path to doc file
            chunk_size: Characters per chunk
            
        Returns:
            True if successful
        """
        try:
            # Read documentation
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chunk documentation
            chunks = []
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                if chunk.strip():
                    chunks.append(chunk)
            
            # Generate embeddings using doc embedder
            embeddings = []
            for chunk in chunks:
                emb = self.doc_embedder.generate_embedding(chunk)
                embeddings.append((chunk, np.array(emb)))
            
            self.doc_index[file_path] = embeddings
            
            self.doc_metadata[file_path] = {
                'type': 'doc',
                'chunks': len(embeddings),
                'format': Path(file_path).suffix,
                'size': os.path.getsize(file_path)
            }
            
            logger.debug(f"Indexed doc file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index doc file {file_path}: {e}")
            return False
    
    def index_directory(
        self,
        directory: str,
        code_extensions: Optional[List[str]] = None,
        doc_extensions: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """
        Index all files in a directory.
        
        Args:
            directory: Directory to index
            code_extensions: Code file extensions
            doc_extensions: Doc file extensions
            
        Returns:
            Statistics dict
        """
        if code_extensions is None:
            code_extensions = ['.py', '.js', '.ts', '.java', '.cs', '.cpp', '.go', '.rs']
        
        if doc_extensions is None:
            doc_extensions = ['.md', '.txt', '.rst', '.adoc']
        
        stats = {'code_files': 0, 'doc_files': 0, 'errors': 0}
        
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    ext = Path(file).suffix.lower()
                    
                    if ext in code_extensions:
                        if self.index_code_file(file_path):
                            stats['code_files'] += 1
                        else:
                            stats['errors'] += 1
                    
                    elif ext in doc_extensions:
                        if self.index_doc_file(file_path):
                            stats['doc_files'] += 1
                        else:
                            stats['errors'] += 1
            
            logger.info(f"Indexed directory: {directory} - {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to index directory {directory}: {e}")
            return stats
    
    def retrieve_code_and_docs(
        self,
        query: str,
        top_k: int = 10,
        code_only: bool = False,
        docs_only: bool = False
    ) -> List[MultiModalResult]:
        """
        Retrieve both code and documentation for a query.
        
        Args:
            query: Search query
            top_k: Number of results
            code_only: Only search code
            docs_only: Only search docs
            
        Returns:
            List of multi-modal results
        """
        results = []
        
        try:
            # Search code
            if not docs_only:
                code_results = self._search_code(query, top_k)
                results.extend(code_results)
            
            # Search docs
            if not code_only:
                doc_results = self._search_docs(query, top_k)
                results.extend(doc_results)
            
            # Sort by weighted similarity
            results.sort(key=lambda x: x.similarity, reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []
    
    def _search_code(self, query: str, top_k: int) -> List[MultiModalResult]:
        """Search code index."""
        results = []
        
        try:
            # Generate query embedding
            query_emb = self.code_embedder.embed_code(query)
            
            # Search all code chunks
            for file_path, chunks in self.code_index.items():
                for chunk, emb in chunks:
                    similarity = np.dot(query_emb, emb) / (
                        np.linalg.norm(query_emb) * np.linalg.norm(emb)
                    )
                    
                    # Apply code weight
                    weighted_similarity = similarity * self.code_weight
                    
                    results.append(MultiModalResult(
                        content=chunk,
                        source_type='code',
                        file_path=file_path,
                        similarity=weighted_similarity,
                        metadata=self.code_metadata.get(file_path, {})
                    ))
            
            # Sort and return top results
            results.sort(key=lambda x: x.similarity, reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Code search failed: {e}")
            return []
    
    def _search_docs(self, query: str, top_k: int) -> List[MultiModalResult]:
        """Search documentation index."""
        results = []
        
        try:
            # Generate query embedding
            query_emb = np.array(self.doc_embedder.generate_embedding(query))
            
            # Search all doc chunks
            for file_path, chunks in self.doc_index.items():
                for chunk, emb in chunks:
                    similarity = np.dot(query_emb, emb) / (
                        np.linalg.norm(query_emb) * np.linalg.norm(emb)
                    )
                    
                    # Apply doc weight
                    weighted_similarity = similarity * self.doc_weight
                    
                    results.append(MultiModalResult(
                        content=chunk,
                        source_type='doc',
                        file_path=file_path,
                        similarity=weighted_similarity,
                        metadata=self.doc_metadata.get(file_path, {})
                    ))
            
            # Sort and return top results
            results.sort(key=lambda x: x.similarity, reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Doc search failed: {e}")
            return []
    
    def cross_modal_search(
        self,
        query: str,
        mode: str = 'both',
        top_k: int = 10
    ) -> List[MultiModalResult]:
        """
        Search across code and docs with different modes.
        
        Args:
            query: Search query
            mode: 'code', 'docs', or 'both'
            top_k: Number of results
            
        Returns:
            List of results
        """
        if mode == 'code':
            return self.retrieve_code_and_docs(query, top_k, code_only=True)
        elif mode == 'docs':
            return self.retrieve_code_and_docs(query, top_k, docs_only=True)
        else:
            return self.retrieve_code_and_docs(query, top_k)
    
    def combine_results(
        self,
        code_results: List[MultiModalResult],
        doc_results: List[MultiModalResult],
        strategy: str = 'interleave'
    ) -> List[MultiModalResult]:
        """
        Intelligently combine code and doc results.
        
        Args:
            code_results: Code search results
            doc_results: Doc search results
            strategy: 'interleave', 'code_first', or 'doc_first'
            
        Returns:
            Combined results
        """
        if strategy == 'interleave':
            # Interleave results
            combined = []
            max_len = max(len(code_results), len(doc_results))
            for i in range(max_len):
                if i < len(code_results):
                    combined.append(code_results[i])
                if i < len(doc_results):
                    combined.append(doc_results[i])
            return combined
        
        elif strategy == 'code_first':
            return code_results + doc_results
        
        elif strategy == 'doc_first':
            return doc_results + code_results
        
        else:
            # Default: sort by similarity
            combined = code_results + doc_results
            combined.sort(key=lambda x: x.similarity, reverse=True)
            return combined
    
    def get_context_for_task(
        self,
        task_description: str,
        max_tokens: int = 4000,
        include_code: bool = True,
        include_docs: bool = True
    ) -> str:
        """
        Build context for a task from code and docs.
        
        Args:
            task_description: Description of the task
            max_tokens: Maximum context tokens
            include_code: Include code snippets
            include_docs: Include documentation
            
        Returns:
            Context string
        """
        try:
            # Retrieve relevant content
            results = self.retrieve_code_and_docs(
                task_description,
                top_k=20,
                code_only=not include_docs,
                docs_only=not include_code
            )
            
            # Build context
            context_parts = []
            current_tokens = 0
            
            for result in results:
                # Estimate tokens (rough: 4 chars = 1 token)
                tokens = len(result.content) // 4
                
                if current_tokens + tokens > max_tokens:
                    break
                
                context_parts.append(f"# From {result.source_type}: {result.file_path}\n{result.content}\n")
                current_tokens += tokens
            
            context = "\n---\n".join(context_parts)
            logger.info(f"Built context with {len(context_parts)} parts (~{current_tokens} tokens)")
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to build context: {e}")
            return ""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get retriever statistics."""
        code_chunks = sum(len(chunks) for chunks in self.code_index.values())
        doc_chunks = sum(len(chunks) for chunks in self.doc_index.values())
        
        return {
            'code_files': len(self.code_index),
            'doc_files': len(self.doc_index),
            'code_chunks': code_chunks,
            'doc_chunks': doc_chunks,
            'total_chunks': code_chunks + doc_chunks,
            'code_weight': self.code_weight,
            'doc_weight': self.doc_weight
        }
    
    def set_weights(self, code_weight: float, doc_weight: float):
        """
        Update retrieval weights.
        
        Args:
            code_weight: Weight for code (0-1)
            doc_weight: Weight for docs (0-1)
        """
        self.code_weight = code_weight
        self.doc_weight = doc_weight
        logger.info(f"Updated weights - code: {code_weight}, doc: {doc_weight}")
    
    def clear_index(self, index_type: Optional[str] = None):
        """
        Clear indices.
        
        Args:
            index_type: 'code', 'doc', or None (both)
        """
        if index_type is None or index_type == 'code':
            self.code_index.clear()
            self.code_metadata.clear()
            logger.info("Cleared code index")
        
        if index_type is None or index_type == 'doc':
            self.doc_index.clear()
            self.doc_metadata.clear()
            logger.info("Cleared doc index")
