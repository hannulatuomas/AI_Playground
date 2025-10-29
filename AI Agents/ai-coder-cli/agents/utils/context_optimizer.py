"""
Context Optimization Utility

This module provides context optimization for coding agents using vector
similarity search to include only relevant portions of documentation files.

Features:
- Vector-based similarity search
- Chunk-based document processing
- Relevance scoring and ranking
- Context window management
- Caching of embeddings
"""

import logging
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from tools.embeddings import EmbeddingGenerator, create_embedding_generator
from tools.vector_db import ChromaVectorDB, create_vector_db


logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a chunk of a document."""
    content: str
    source_file: str
    start_line: int
    end_line: int
    metadata: Dict[str, Any]


@dataclass
class RelevantContext:
    """Represents relevant context extracted from documents."""
    chunks: List[DocumentChunk]
    total_tokens: int
    relevance_scores: List[float]


class ContextOptimizer:
    """
    Optimizes context for LLM prompts by using vector similarity search.
    
    Instead of embedding entire documentation files (best_practices.md,
    user_preferences.md, etc.), this optimizer:
    1. Chunks documents into smaller sections
    2. Generates embeddings for each chunk
    3. Uses vector similarity to find relevant chunks for current task
    4. Includes only the most relevant sections in the prompt
    
    This significantly reduces context window usage while maintaining quality.
    """
    
    def __init__(
        self,
        vector_db: Optional[ChromaVectorDB] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        collection_name: str = "code_context",
        chunk_size: int = 500,  # characters per chunk
        overlap: int = 50,       # overlap between chunks
        max_context_tokens: int = 2000,  # max tokens in optimized context
    ):
        """
        Initialize context optimizer.
        
        Args:
            vector_db: Vector database instance (created if None)
            embedding_generator: Embedding generator (created if None)
            collection_name: Name for vector DB collection
            chunk_size: Size of document chunks in characters
            overlap: Overlap between adjacent chunks
            max_context_tokens: Maximum tokens in optimized context
        """
        self.vector_db = vector_db or create_vector_db()
        self.embedding_generator = embedding_generator or create_embedding_generator()
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.max_context_tokens = max_context_tokens
        
        # Initialize collection
        self._ensure_collection()
    
    def _ensure_collection(self) -> None:
        """Ensure vector DB collection exists."""
        try:
            # Check if collection exists
            existing = self.vector_db.list_collections()
            if self.collection_name not in existing:
                # Create collection
                self.vector_db.create_collection(
                    name=self.collection_name,
                    metadata={'purpose': 'Code context optimization'}
                )
                logger.info(f"Created vector DB collection: {self.collection_name}")
        except Exception as e:
            logger.warning(f"Could not ensure collection exists: {e}")
    
    def index_document(
        self,
        file_path: Path,
        document_type: str = "documentation",
        force_reindex: bool = False
    ) -> bool:
        """
        Index a document file for later retrieval.
        
        Args:
            file_path: Path to document file
            document_type: Type of document (e.g., 'best_practices', 'user_preferences')
            force_reindex: Force reindexing even if already indexed
            
        Returns:
            True if indexing successful, False otherwise
        """
        try:
            if not file_path.exists():
                logger.warning(f"Document file not found: {file_path}")
                return False
            
            # Read document
            content = file_path.read_text(encoding='utf-8')
            
            # Generate document hash for caching
            doc_hash = hashlib.md5(content.encode()).hexdigest()
            doc_id = f"{file_path.stem}_{doc_hash}"
            
            # Check if already indexed
            if not force_reindex:
                try:
                    existing = self.vector_db.get(
                        collection_name=self.collection_name,
                        ids=[doc_id]
                    )
                    if existing and existing.get('ids'):
                        logger.info(f"Document already indexed: {file_path.name}")
                        return True
                except:
                    pass  # Document not found, continue with indexing
            
            # Chunk document
            chunks = self._chunk_document(content, str(file_path))
            
            if not chunks:
                logger.warning(f"No chunks generated for {file_path}")
                return False
            
            # Generate embeddings and add to vector DB
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                
                # Generate embedding
                embedding = self.embedding_generator.generate_embedding(chunk.content)
                
                # Add to vector DB
                self.vector_db.add(
                    collection_name=self.collection_name,
                    documents=[chunk.content],
                    embeddings=[embedding],
                    metadatas=[{
                        'source_file': chunk.source_file,
                        'document_type': document_type,
                        'start_line': chunk.start_line,
                        'end_line': chunk.end_line,
                        'chunk_index': i,
                        **chunk.metadata
                    }],
                    ids=[chunk_id]
                )
            
            logger.info(f"Indexed {len(chunks)} chunks from {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index document {file_path}: {e}")
            return False
    
    def get_relevant_context(
        self,
        query: str,
        document_types: Optional[List[str]] = None,
        top_k: int = 5,
        min_relevance: float = 0.5
    ) -> RelevantContext:
        """
        Get relevant context for a query using similarity search.
        
        Args:
            query: Query text (e.g., task description)
            document_types: Filter by document types (None = all types)
            top_k: Number of top chunks to retrieve
            min_relevance: Minimum relevance score (0-1)
            
        Returns:
            RelevantContext with relevant chunks and scores
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.generate_embedding(query)
            
            # Build filter
            where_filter = None
            if document_types:
                where_filter = {'document_type': {'$in': document_types}}
            
            # Search vector DB
            results = self.vector_db.query(
                collection_name=self.collection_name,
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter
            )
            
            if not results or not results.get('documents'):
                logger.warning("No relevant context found")
                return RelevantContext(chunks=[], total_tokens=0, relevance_scores=[])
            
            # Process results
            chunks = []
            scores = []
            total_tokens = 0
            
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                # Convert distance to similarity score (1 - normalized distance)
                score = 1 - min(distance, 1.0)
                
                if score < min_relevance:
                    continue
                
                # Estimate tokens (rough: 1 token ≈ 4 characters)
                chunk_tokens = len(doc) // 4
                
                if total_tokens + chunk_tokens > self.max_context_tokens:
                    # Would exceed max tokens, stop here
                    break
                
                chunk = DocumentChunk(
                    content=doc,
                    source_file=metadata.get('source_file', 'unknown'),
                    start_line=metadata.get('start_line', 0),
                    end_line=metadata.get('end_line', 0),
                    metadata=metadata
                )
                
                chunks.append(chunk)
                scores.append(score)
                total_tokens += chunk_tokens
            
            logger.info(f"Retrieved {len(chunks)} relevant chunks ({total_tokens} tokens)")
            
            return RelevantContext(
                chunks=chunks,
                total_tokens=total_tokens,
                relevance_scores=scores
            )
            
        except Exception as e:
            logger.error(f"Failed to get relevant context: {e}")
            return RelevantContext(chunks=[], total_tokens=0, relevance_scores=[])
    
    def _chunk_document(
        self,
        content: str,
        source_file: str
    ) -> List[DocumentChunk]:
        """
        Split document into overlapping chunks.
        
        Args:
            content: Document content
            source_file: Source file path
            
        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        lines = content.split('\n')
        
        # Combine lines into chunks of approximately chunk_size characters
        current_chunk = []
        current_size = 0
        start_line = 0
        
        for i, line in enumerate(lines):
            line_size = len(line) + 1  # +1 for newline
            
            if current_size + line_size > self.chunk_size and current_chunk:
                # Create chunk
                chunk_content = '\n'.join(current_chunk)
                chunks.append(DocumentChunk(
                    content=chunk_content,
                    source_file=source_file,
                    start_line=start_line,
                    end_line=i - 1,
                    metadata={'size': current_size}
                ))
                
                # Start new chunk with overlap
                # Keep last few lines for overlap
                overlap_lines = []
                overlap_size = 0
                for line in reversed(current_chunk):
                    if overlap_size + len(line) < self.overlap:
                        overlap_lines.insert(0, line)
                        overlap_size += len(line) + 1
                    else:
                        break
                
                current_chunk = overlap_lines + [line]
                current_size = overlap_size + line_size
                start_line = i - len(overlap_lines)
            else:
                current_chunk.append(line)
                current_size += line_size
        
        # Add final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunks.append(DocumentChunk(
                content=chunk_content,
                source_file=source_file,
                start_line=start_line,
                end_line=len(lines) - 1,
                metadata={'size': current_size}
            ))
        
        return chunks
    
    def format_context_for_prompt(self, relevant_context: RelevantContext) -> str:
        """
        Format relevant context for inclusion in LLM prompt.
        
        Args:
            relevant_context: RelevantContext object
            
        Returns:
            Formatted context string
        """
        if not relevant_context.chunks:
            return ""
        
        sections = []
        sections.append("## Relevant Context\n")
        sections.append("The following sections have been selected as most relevant to your task:\n")
        
        for i, (chunk, score) in enumerate(zip(
            relevant_context.chunks,
            relevant_context.relevance_scores
        ), 1):
            source = Path(chunk.source_file).name
            sections.append(f"\n### Context {i} (from {source}, relevance: {score:.2f})")
            sections.append(f"```")
            sections.append(chunk.content)
            sections.append(f"```\n")
        
        return '\n'.join(sections)
    
    def index_language_documents(
        self,
        language_path: Path,
        force_reindex: bool = False
    ) -> Dict[str, bool]:
        """
        Index all documentation files for a language.
        
        Args:
            language_path: Path to language directory
            force_reindex: Force reindexing
            
        Returns:
            Dictionary of {document_type: success}
        """
        results = {}
        
        # Documents to index
        doc_files = {
            'best_practices': 'best_practices.md',
            'user_preferences': 'user_preferences.md',
            'documentation_preferences': 'documentation_preferences.md',
            'testing_preferences': 'testing_preferences.md',
            'planning_preferences': 'planning_preferences.md',
            'analysis_preferences': 'analysis_preferences.md',
        }
        
        for doc_type, filename in doc_files.items():
            file_path = language_path / filename
            if file_path.exists():
                success = self.index_document(file_path, doc_type, force_reindex)
                results[doc_type] = success
            else:
                logger.debug(f"Document not found: {file_path}")
                results[doc_type] = False
        
        return results


def create_context_optimizer(**kwargs) -> ContextOptimizer:
    """
    Factory function to create ContextOptimizer instance.
    
    Args:
        **kwargs: Arguments passed to ContextOptimizer
        
    Returns:
        ContextOptimizer instance
    """
    return ContextOptimizer(**kwargs)


def optimize_context(context: Dict[str, Any], max_tokens: int = 2000) -> Dict[str, Any]:
    """
    Optimize context by truncating or compressing large elements.
    
    Args:
        context: Context dictionary to optimize
        max_tokens: Maximum token budget
        
    Returns:
        Optimized context dictionary
    """
    optimized = {}
    current_tokens = 0
    
    for key, value in context.items():
        # Estimate tokens
        if isinstance(value, str):
            value_tokens = len(value) // 4
        elif isinstance(value, (list, dict)):
            value_tokens = len(str(value)) // 4
        else:
            value_tokens = 10  # Small overhead
        
        # Check if we can fit this element
        if current_tokens + value_tokens <= max_tokens:
            optimized[key] = value
            current_tokens += value_tokens
        else:
            # Try to truncate
            remaining_tokens = max_tokens - current_tokens
            if remaining_tokens > 100:  # Only if there's meaningful space
                if isinstance(value, str):
                    # Truncate string
                    truncated_length = remaining_tokens * 4
                    optimized[key] = value[:truncated_length] + "... [truncated]"
                    current_tokens += remaining_tokens
                elif isinstance(value, list):
                    # Take first few elements
                    items_to_take = min(len(value), remaining_tokens // 20)
                    optimized[key] = value[:items_to_take]
                    current_tokens += remaining_tokens
            break  # No more space
    
    return optimized


def truncate_code_context(code: str, max_lines: int = 100) -> str:
    """
    Truncate code context to maximum number of lines.
    
    Args:
        code: Code string to truncate
        max_lines: Maximum number of lines
        
    Returns:
        Truncated code string
    """
    lines = code.split('\n')
    
    if len(lines) <= max_lines:
        return code
    
    # Keep first and last portions, accounting for the truncation message
    keep_start = (max_lines - 1) // 2  # -1 for truncation message line
    keep_end = max_lines - keep_start - 1
    
    truncated = lines[:keep_start]
    truncated.append(f"... [{len(lines) - max_lines} lines truncated] ...")
    truncated.extend(lines[-keep_end:])
    
    return '\n'.join(truncated)


def compress_history(history: List[Dict[str, Any]], max_messages: int = 20) -> List[Dict[str, Any]]:
    """
    Compress conversation history by keeping most recent messages.
    
    Args:
        history: List of message dictionaries
        max_messages: Maximum number of messages to keep
        
    Returns:
        Compressed history list
    """
    if len(history) <= max_messages:
        return history
    
    # Keep most recent messages
    return history[-max_messages:]


def prioritize_context_elements(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prioritize context elements based on priority field.
    
    Args:
        elements: List of context element dictionaries
        
    Returns:
        Sorted list with high priority elements first
    """
    priority_map = {
        'high': 3,
        'medium': 2,
        'low': 1
    }
    
    def get_priority_value(elem: Dict[str, Any]) -> int:
        priority = elem.get('priority', 'medium')
        return priority_map.get(priority, 2)
    
    return sorted(elements, key=get_priority_value, reverse=True)


def estimate_token_count(text: str) -> int:
    """
    Estimate token count for a text string.
    
    Args:
        text: Text to estimate tokens for
        
    Returns:
        Estimated token count
    """
    # Rough estimation: ~4 characters per token
    # More accurate would use tiktoken, but this works for estimation
    return len(text) // 4


def smart_context_window(messages: List[str], window_size: int = 10) -> List[str]:
    """
    Create a smart context window from messages.
    
    Args:
        messages: List of messages
        window_size: Size of the window
        
    Returns:
        List of messages in the window
    """
    if len(messages) <= window_size:
        return messages
    
    # Keep most recent messages
    return messages[-window_size:]


# Export utility functions
__all__ = [
    'ContextOptimizer',
    'DocumentChunk',
    'RelevantContext',
    'create_context_optimizer',
    'optimize_context',
    'truncate_code_context',
    'compress_history',
    'prioritize_context_elements',
    'estimate_token_count',
    'smart_context_window'
]
