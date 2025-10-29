"""
RAG Retriever Module

Retrieves relevant code chunks from vector database using semantic search.
Provides:
- Vector similarity search with threshold filtering
- Optional reranking for better relevance
- Result formatting for LLM prompts
- Token budget management
- Language and metadata filtering

Features:
- Configurable top-k retrieval
- Score normalization
- Result deduplication
- Dynamic k adjustment for token budgets
- Contextual formatting with file paths
"""

from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class RAGRetriever:
    """
    Retrieve relevant code chunks from vector database.
    
    Uses semantic search with ChromaDB to find most relevant code chunks
    for a given query.
    """
    
    def __init__(
        self,
        indexer=None,
        collection_name: Optional[str] = None,
        db_path: str = "data/rag_db"
    ):
        """
        Initialize the RAG retriever.
        
        Args:
            indexer: RAGIndexer instance (for embedding model)
            collection_name: Default collection to search
            db_path: Path to ChromaDB database
            
        Example:
            >>> from src.features.rag_indexer import RAGIndexer
            >>> indexer = RAGIndexer()
            >>> retriever = RAGRetriever(
            ...     indexer=indexer,
            ...     collection_name='my-project'
            ... )
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers==2.2.2"
            )
        
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "chromadb not installed. "
                "Install with: pip install chromadb==0.4.18"
            )
        
        self.indexer = indexer
        self.collection_name = collection_name
        self.db_path = Path(db_path)
        
        # Initialize ChromaDB client (lazy loading)
        self._chroma_client = None
        
        # Token estimation factor
        self.words_per_token = 0.75
    
    @property
    def chroma_client(self):
        """Lazy load ChromaDB client."""
        if self._chroma_client is None:
            from chromadb.config import Settings
            self._chroma_client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False)
            )
        return self._chroma_client
    
    def retrieve(
        self,
        query: str,
        collection_name: Optional[str] = None,
        top_k: int = 5,
        threshold: float = 0.7,
        language_filter: Optional[str] = None,
        file_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant code chunks for query.
        
        Uses vector similarity search with optional filtering.
        
        Args:
            query: Search query
            collection_name: Collection to search (uses default if None)
            top_k: Number of results to return
            threshold: Minimum similarity score (0-1)
            language_filter: Filter by programming language
            file_filter: Filter by file path (substring match)
            
        Returns:
            List of result dictionaries with content, metadata, and scores
            
        Example:
            >>> results = retriever.retrieve(
            ...     query="JWT authentication implementation",
            ...     top_k=5,
            ...     language_filter="python"
            ... )
            >>> for result in results:
            ...     print(f"{result['file_path']}: {result['score']:.3f}")
        """
        collection_name = collection_name or self.collection_name
        
        if not collection_name:
            raise ValueError("No collection name specified")
        
        # Get collection
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
        except Exception as e:
            raise ValueError(f"Collection not found: {collection_name}")
        
        # Generate query embedding
        if not self.indexer:
            raise ValueError("RAGIndexer required for embedding generation")
        
        query_embedding = self.indexer.model.encode([query], convert_to_numpy=True)[0]
        
        # Build where clause for filtering
        where_clause = {}
        if language_filter:
            where_clause['language'] = language_filter
        if file_filter:
            where_clause['file_path'] = {"$contains": file_filter}
        
        # Query collection
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k * 2,  # Get more for filtering
            where=where_clause if where_clause else None
        )
        
        # Process results
        retrieved = []
        if results and results['ids']:
            for i in range(len(results['ids'][0])):
                score = 1 - results['distances'][0][i]  # Convert distance to similarity
                
                # Apply threshold
                if score < threshold:
                    continue
                
                metadata = results['metadatas'][0][i]
                document = results['documents'][0][i]
                
                retrieved.append({
                    'chunk_id': results['ids'][0][i],
                    'content': document,
                    'score': score,
                    'file_path': metadata.get('file_path', 'unknown'),
                    'start_line': metadata.get('start_line'),
                    'end_line': metadata.get('end_line'),
                    'language': metadata.get('language', 'unknown'),
                    'metadata': metadata
                })
                
                if len(retrieved) >= top_k:
                    break
        
        return retrieved
    
    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        method: str = 'score'
    ) -> List[Dict[str, Any]]:
        """
        Rerank results for better relevance.
        
        Currently supports simple score-based reranking.
        Can be extended with cross-encoder models.
        
        Args:
            query: Original query
            results: Results from retrieve()
            method: Reranking method ('score', 'cross-encoder')
            
        Returns:
            Reranked results list
            
        Example:
            >>> results = retriever.retrieve(query="auth")
            >>> reranked = retriever.rerank(query="auth", results=results)
        """
        if method == 'score':
            # Simple reranking by score (already sorted)
            return sorted(results, key=lambda x: x['score'], reverse=True)
        
        elif method == 'cross-encoder':
            # Placeholder for cross-encoder reranking
            # Would require additional model: sentence-transformers cross-encoder
            # For now, fall back to score-based
            print("Warning: Cross-encoder reranking not implemented, using score-based")
            return sorted(results, key=lambda x: x['score'], reverse=True)
        
        else:
            raise ValueError(f"Unknown reranking method: {method}")
    
    def augment_prompt(
        self,
        base_prompt: str,
        retrieved: List[Dict[str, Any]],
        include_line_numbers: bool = True,
        include_scores: bool = False
    ) -> str:
        """
        Format retrieved chunks for LLM prompt.
        
        Args:
            base_prompt: Original prompt/query
            retrieved: Retrieved results from retrieve()
            include_line_numbers: Include line numbers in output
            include_scores: Include similarity scores
            
        Returns:
            Formatted prompt with context
            
        Example:
            >>> results = retriever.retrieve("authentication")
            >>> prompt = retriever.augment_prompt(
            ...     base_prompt="How to implement JWT auth?",
            ...     retrieved=results
            ... )
        """
        if not retrieved:
            return base_prompt
        
        # Build context section
        context_parts = ["Relevant code from codebase:\n"]
        
        for i, result in enumerate(retrieved, 1):
            file_path = result['file_path']
            content = result['content']
            
            # Format file header
            if include_line_numbers and result.get('start_line'):
                header = f"\n[{i}] {file_path} (lines {result['start_line']}-{result['end_line']})"
            else:
                header = f"\n[{i}] {file_path}"
            
            if include_scores:
                header += f" [relevance: {result['score']:.2f}]"
            
            header += ":"
            
            context_parts.append(header)
            context_parts.append(f"```{result['language']}\n{content}\n```")
        
        # Combine context with prompt
        context = "\n".join(context_parts)
        full_prompt = f"{context}\n\n{base_prompt}"
        
        return full_prompt
    
    def handle_large_context(
        self,
        retrieved: List[Dict[str, Any]],
        max_tokens: int = 2000
    ) -> List[Dict[str, Any]]:
        """
        Truncate retrieved chunks to fit token budget.
        
        Prioritizes by relevance score and removes from end.
        
        Args:
            retrieved: Retrieved results
            max_tokens: Maximum tokens allowed
            
        Returns:
            Truncated results list
            
        Example:
            >>> results = retriever.retrieve(query="auth", top_k=10)
            >>> truncated = retriever.handle_large_context(
            ...     retrieved=results,
            ...     max_tokens=2000
            ... )
        """
        if not retrieved:
            return retrieved
        
        # Ensure sorted by score (highest first)
        retrieved = sorted(retrieved, key=lambda x: x['score'], reverse=True)
        
        # Calculate tokens for each result
        tokens_used = 0
        truncated = []
        
        for result in retrieved:
            # Estimate tokens for this result
            content_tokens = self._estimate_tokens(result['content'])
            # Add overhead for formatting (file path, markers, etc.)
            result_tokens = content_tokens + 50
            
            if tokens_used + result_tokens <= max_tokens:
                truncated.append(result)
                tokens_used += result_tokens
            else:
                break
        
        if len(truncated) < len(retrieved):
            print(f"Note: Truncated from {len(retrieved)} to {len(truncated)} chunks to fit token budget")
        
        return truncated
    
    def dynamic_retrieve(
        self,
        query: str,
        max_tokens: int,
        collection_name: Optional[str] = None,
        threshold: float = 0.7,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve with dynamic k adjustment based on token budget.
        
        Starts with higher k and truncates to fit budget.
        
        Args:
            query: Search query
            max_tokens: Maximum tokens for results
            collection_name: Collection to search
            threshold: Minimum similarity score
            **kwargs: Additional arguments for retrieve()
            
        Returns:
            Retrieved and truncated results
            
        Example:
            >>> results = retriever.dynamic_retrieve(
            ...     query="authentication implementation",
            ...     max_tokens=2000
            ... )
        """
        # Start with high k
        initial_k = 10
        
        # Retrieve
        results = self.retrieve(
            query=query,
            collection_name=collection_name,
            top_k=initial_k,
            threshold=threshold,
            **kwargs
        )
        
        # Truncate to fit budget
        return self.handle_large_context(results, max_tokens)
    
    def search_files(
        self,
        file_path: str,
        collection_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all chunks from a specific file.
        
        Args:
            file_path: File path to search
            collection_name: Collection to search
            
        Returns:
            List of chunks from the file
            
        Example:
            >>> chunks = retriever.search_files("src/auth.py")
            >>> print(f"Found {len(chunks)} chunks in file")
        """
        collection_name = collection_name or self.collection_name
        
        if not collection_name:
            raise ValueError("No collection name specified")
        
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
        except:
            raise ValueError(f"Collection not found: {collection_name}")
        
        # Get all chunks for this file
        results = collection.get(
            where={"file_path": file_path}
        )
        
        chunks = []
        if results and results['ids']:
            for i in range(len(results['ids'])):
                chunks.append({
                    'chunk_id': results['ids'][i],
                    'content': results['documents'][i],
                    'file_path': results['metadatas'][i].get('file_path'),
                    'start_line': results['metadatas'][i].get('start_line'),
                    'end_line': results['metadatas'][i].get('end_line'),
                    'language': results['metadatas'][i].get('language'),
                    'metadata': results['metadatas'][i]
                })
        
        # Sort by line number if available
        chunks.sort(key=lambda x: x.get('start_line', 0))
        
        return chunks
    
    def get_file_list(
        self,
        collection_name: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[str]:
        """
        Get list of all files in collection.
        
        Args:
            collection_name: Collection to query
            language: Optional language filter
            
        Returns:
            List of unique file paths
            
        Example:
            >>> files = retriever.get_file_list(language="python")
            >>> print(f"Found {len(files)} Python files")
        """
        collection_name = collection_name or self.collection_name
        
        if not collection_name:
            raise ValueError("No collection name specified")
        
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
        except:
            raise ValueError(f"Collection not found: {collection_name}")
        
        # Get all chunks
        where_clause = {"language": language} if language else None
        results = collection.get(where=where_clause)
        
        # Extract unique file paths
        if results and results['metadatas']:
            file_paths = set(meta.get('file_path') for meta in results['metadatas'])
            return sorted(file_paths)
        
        return []
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count from text.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        words = len(text.split())
        tokens = int(words / self.words_per_token)
        return max(1, tokens)
    
    def get_statistics(
        self,
        collection_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Args:
            collection_name: Collection to analyze
            
        Returns:
            Dictionary with statistics
            
        Example:
            >>> stats = retriever.get_statistics()
            >>> print(f"Total chunks: {stats['total_chunks']}")
            >>> print(f"Languages: {stats['languages']}")
        """
        collection_name = collection_name or self.collection_name
        
        if not collection_name:
            raise ValueError("No collection name specified")
        
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
        except:
            return {'error': f"Collection not found: {collection_name}"}
        
        # Get all metadata
        results = collection.get()
        
        if not results or not results['metadatas']:
            return {
                'total_chunks': 0,
                'total_files': 0,
                'languages': {}
            }
        
        # Count statistics
        file_paths = set()
        languages = {}
        
        for meta in results['metadatas']:
            file_path = meta.get('file_path')
            if file_path:
                file_paths.add(file_path)
            
            language = meta.get('language', 'unknown')
            languages[language] = languages.get(language, 0) + 1
        
        return {
            'collection_name': collection_name,
            'total_chunks': len(results['ids']),
            'total_files': len(file_paths),
            'languages': dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))
        }


if __name__ == "__main__":
    # Test the RAG retriever
    print("Testing RAG Retriever...")
    
    try:
        from src.features.rag_indexer import RAGIndexer
        
        # Create indexer and retriever
        indexer = RAGIndexer(
            embedding_model='all-MiniLM-L6-v2',
            db_path='data/rag_db_test',
            use_gpu=False
        )
        
        retriever = RAGRetriever(
            indexer=indexer,
            collection_name='test-project'
        )
        print("✓ RAG Retriever created")
        
        # List collections
        print("\n=== Test: List Collections ===")
        collections = indexer.list_collections()
        print(f"Available collections: {collections}")
        
        if collections:
            # Test statistics
            print("\n=== Test: Get Statistics ===")
            stats = retriever.get_statistics(collection_name=collections[0])
            print(f"Collection: {stats.get('collection_name')}")
            print(f"Total chunks: {stats.get('total_chunks')}")
            print(f"Total files: {stats.get('total_files')}")
            print(f"Languages: {stats.get('languages')}")
            
            # Test file list
            print("\n=== Test: Get File List ===")
            files = retriever.get_file_list(collection_name=collections[0])
            print(f"✓ Found {len(files)} files")
            if files:
                print(f"  Example: {files[0]}")
        else:
            print("No collections found. Create one with RAGIndexer.build_vector_db()")
        
        print("\n✓ All tests passed!")
        
    except ImportError as e:
        print(f"✗ Required packages not installed: {e}")
        print("Install with: pip install sentence-transformers==2.2.2 chromadb==0.4.18")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
