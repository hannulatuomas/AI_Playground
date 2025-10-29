"""
Multi-modal Retrieval Module - Full Implementation

Retrieves based on both code and documentation.
Provides cross-modal search and weighted combination.

Features:
- Separate embeddings for code and documentation
- Weighted score combination
- Cross-modal search (query code, get docs or vice versa)
- Documentation extraction from code
- Hybrid retrieval strategies

Example:
    >>> mm_retriever = MultiModalRetriever(code_embedder, doc_embedder)
    >>> results = mm_retriever.retrieve_multimodal(
    ...     query="JWT authentication",
    ...     mode='hybrid',
    ...     code_weight=0.6
    ... )
"""

from typing import List, Dict, Optional, Any, Tuple
import numpy as np
import re
import ast
from pathlib import Path


class MultiModalRetriever:
    """
    Multi-modal retrieval for code and documentation.
    
    Features:
    - Separate embeddings for code and docs
    - Weighted score combination
    - Cross-modal search
    - Documentation extraction
    """
    
    def __init__(
        self,
        code_embedder=None,
        doc_embedder=None,
        default_code_weight: float = 0.6,
        doc_weight: float = 0.4
    ):
        """
        Initialize multi-modal retriever.
        
        Args:
            code_embedder: Embedder for code (CodeEmbedder)
            doc_embedder: Embedder for documentation (SentenceTransformer)
            default_code_weight: Default weight for code (0-1)
            doc_weight: Weight for documentation (0-1)
            
        Example:
            >>> from features.rag_advanced import CodeEmbedder
            >>> from sentence_transformers import SentenceTransformer
            >>> 
            >>> code_emb = CodeEmbedder('codebert')
            >>> doc_emb = SentenceTransformer('all-MiniLM-L6-v2')
            >>> 
            >>> mm_retriever = MultiModalRetriever(code_emb, doc_emb)
        """
        self.code_embedder = code_embedder
        self.doc_embedder = doc_embedder
        self.default_code_weight = default_code_weight
        self.default_doc_weight = doc_weight
        
        # Validate weights
        if not (0 <= default_code_weight <= 1):
            raise ValueError("code_weight must be between 0 and 1")
        if not (0 <= doc_weight <= 1):
            raise ValueError("doc_weight must be between 0 and 1")
        
        print("MultiModalRetriever initialized:")
        print(f"  Code embedder: {'✓' if code_embedder else '✗'}")
        print(f"  Doc embedder: {'✓' if doc_embedder else '✗'}")
        print(f"  Default weights: code={default_code_weight}, docs={doc_weight}")
    
    def index_multimodal(
        self,
        code: str,
        docs: str,
        metadata: Dict[str, Any],
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Index code and documentation separately.
        
        Args:
            code: Source code
            docs: Documentation/comments
            metadata: Additional metadata
            language: Programming language
            
        Returns:
            Dictionary with embeddings and metadata
            
        Example:
            >>> result = mm_retriever.index_multimodal(
            ...     code="def login(user, pwd): ...",
            ...     docs="Authenticate user with username and password",
            ...     metadata={'file': 'auth.py', 'line': 10},
            ...     language='python'
            ... )
        """
        result = {'metadata': metadata}
        
        # Embed code
        if self.code_embedder and code.strip():
            try:
                result['code_embedding'] = self.code_embedder.embed_code(
                    code,
                    language=language,
                    normalize=True
                )
            except Exception as e:
                print(f"Warning: Code embedding failed: {e}")
                result['code_embedding'] = None
        else:
            result['code_embedding'] = None
        
        # Embed documentation
        if self.doc_embedder and docs.strip():
            try:
                result['doc_embedding'] = self.doc_embedder.encode(
                    [docs],
                    convert_to_numpy=True
                )[0]
                # Normalize
                norm = np.linalg.norm(result['doc_embedding'])
                if norm > 0:
                    result['doc_embedding'] = result['doc_embedding'] / norm
            except Exception as e:
                print(f"Warning: Doc embedding failed: {e}")
                result['doc_embedding'] = None
        else:
            result['doc_embedding'] = None
        
        # Extract doc quality metrics
        result['has_docstring'] = len(docs.strip()) > 0
        result['doc_length'] = len(docs)
        result['doc_quality_score'] = self._assess_doc_quality(docs)
        
        return result
    
    def retrieve_multimodal(
        self,
        query: str,
        indexed_chunks: List[Dict[str, Any]],
        mode: str = 'hybrid',
        code_weight: Optional[float] = None,
        doc_weight: Optional[float] = None,
        language: Optional[str] = None,
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve using multi-modal search.
        
        Args:
            query: Search query
            indexed_chunks: List of indexed chunks with embeddings
            mode: 'code', 'docs', or 'hybrid'
            code_weight: Weight for code vs docs (0-1)
            doc_weight: Weight for documentation
            language: Programming language
            top_k: Number of results
            threshold: Minimum score
            
        Returns:
            List of results with combined scores
            
        Example:
            >>> results = mm_retriever.retrieve_multimodal(
            ...     query="user authentication",
            ...     indexed_chunks=chunks,
            ...     mode='hybrid',
            ...     code_weight=0.7,
            ...     top_k=5
            ... )
        """
        if not indexed_chunks:
            return []
        
        # Use default weights if not specified
        if code_weight is None:
            code_weight = self.default_code_weight
        if doc_weight is None:
            doc_weight = self.default_doc_weight
        
        # Normalize weights to sum to 1
        total_weight = code_weight + doc_weight
        if total_weight > 0:
            code_weight = code_weight / total_weight
            doc_weight = doc_weight / total_weight
        
        # Embed query
        query_code_emb = None
        query_doc_emb = None
        
        if mode in ['code', 'hybrid'] and self.code_embedder:
            try:
                query_code_emb = self.code_embedder.embed_code(
                    query,
                    language=language,
                    normalize=True
                )
            except Exception as e:
                print(f"Warning: Query code embedding failed: {e}")
        
        if mode in ['docs', 'hybrid'] and self.doc_embedder:
            try:
                query_doc_emb = self.doc_embedder.encode(
                    [query],
                    convert_to_numpy=True
                )[0]
                # Normalize
                norm = np.linalg.norm(query_doc_emb)
                if norm > 0:
                    query_doc_emb = query_doc_emb / norm
            except Exception as e:
                print(f"Warning: Query doc embedding failed: {e}")
        
        # Compute scores for each chunk
        results = []
        for chunk in indexed_chunks:
            code_score = 0.0
            doc_score = 0.0
            
            # Code similarity
            if query_code_emb is not None and chunk.get('code_embedding') is not None:
                code_score = float(np.dot(query_code_emb, chunk['code_embedding']))
            
            # Doc similarity
            if query_doc_emb is not None and chunk.get('doc_embedding') is not None:
                doc_score = float(np.dot(query_doc_emb, chunk['doc_embedding']))
            
            # Combined score based on mode
            if mode == 'code':
                combined_score = code_score
            elif mode == 'docs':
                combined_score = doc_score
            else:  # hybrid
                # Weight by quality if docs available
                doc_quality = chunk.get('doc_quality_score', 0.5)
                adjusted_doc_weight = doc_weight * (0.5 + 0.5 * doc_quality)
                adjusted_code_weight = 1.0 - adjusted_doc_weight
                
                combined_score = (
                    adjusted_code_weight * code_score +
                    adjusted_doc_weight * doc_score
                )
            
            # Apply threshold
            if combined_score >= threshold:
                results.append({
                    **chunk,
                    'score': combined_score,
                    'code_score': code_score,
                    'doc_score': doc_score,
                    'mode': mode
                })
        
        # Sort by score and return top-k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def extract_documentation(
        self,
        code: str,
        language: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Extract documentation from code.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            Tuple of (documentation_text, metadata)
            
        Example:
            >>> docs, meta = mm_retriever.extract_documentation(
            ...     'def login(user, pwd):\n    \"\"\"User login.\"\"\"\\n    pass',
            ...     'python'
            ... )
            >>> print(docs)
            User login.
        """
        language = language.lower()
        
        if language == 'python':
            return self._extract_python_docs(code)
        elif language in ['javascript', 'typescript']:
            return self._extract_js_docs(code)
        elif language == 'java':
            return self._extract_java_docs(code)
        elif language in ['c', 'cpp', 'csharp']:
            return self._extract_c_style_docs(code)
        else:
            # Generic extraction
            return self._extract_generic_docs(code)
    
    def _extract_python_docs(self, code: str) -> Tuple[str, Dict[str, Any]]:
        """Extract Python docstrings."""
        docs_list = []
        metadata = {'has_docstring': False, 'docstring_count': 0}
        
        try:
            tree = ast.parse(code)
            # Only get docstrings from nodes that can have them
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        docs_list.append(docstring)
                        metadata['docstring_count'] += 1
                        metadata['has_docstring'] = True
        except SyntaxError:
            # Fallback to regex
            docstrings = re.findall(r'"""(.*?)"""', code, re.DOTALL)
            docstrings += re.findall(r"'''(.*?)'''", code, re.DOTALL)
            docs_list.extend([d.strip() for d in docstrings])
            metadata['docstring_count'] = len(docs_list)
            metadata['has_docstring'] = len(docs_list) > 0
        
        docs_text = '\n'.join(docs_list)
        return docs_text, metadata
    
    def _extract_js_docs(self, code: str) -> Tuple[str, Dict[str, Any]]:
        """Extract JSDoc comments."""
        # Match /** ... */ style comments
        jsdocs = re.findall(r'/\*\*(.*?)\*/', code, re.DOTALL)
        docs_list = []
        for doc in jsdocs:
            # Clean up JSDoc formatting
            clean_doc = re.sub(r'\s*\*\s*', ' ', doc).strip()
            docs_list.append(clean_doc)
        
        docs_text = '\n'.join(docs_list)
        metadata = {
            'has_docstring': len(docs_list) > 0,
            'docstring_count': len(docs_list)
        }
        return docs_text, metadata
    
    def _extract_java_docs(self, code: str) -> Tuple[str, Dict[str, Any]]:
        """Extract JavaDoc comments."""
        # Similar to JSDoc
        javadocs = re.findall(r'/\*\*(.*?)\*/', code, re.DOTALL)
        docs_list = []
        for doc in javadocs:
            # Clean JavaDoc tags
            clean_doc = re.sub(r'@\w+\s+', '', doc)  # Remove @param, @return, etc.
            clean_doc = re.sub(r'\s*\*\s*', ' ', clean_doc).strip()
            docs_list.append(clean_doc)
        
        docs_text = '\n'.join(docs_list)
        metadata = {
            'has_docstring': len(docs_list) > 0,
            'docstring_count': len(docs_list)
        }
        return docs_text, metadata
    
    def _extract_c_style_docs(self, code: str) -> Tuple[str, Dict[str, Any]]:
        """Extract C-style /// or /** comments."""
        # Match /// comments (C#, C++)
        triple_slash = re.findall(r'///\s*(.*?)$', code, re.MULTILINE)
        # Match /** */ comments
        block_comments = re.findall(r'/\*\*(.*?)\*/', code, re.DOTALL)
        
        docs_list = triple_slash.copy()
        for doc in block_comments:
            clean_doc = re.sub(r'\s*\*\s*', ' ', doc).strip()
            docs_list.append(clean_doc)
        
        docs_text = '\n'.join(docs_list)
        metadata = {
            'has_docstring': len(docs_list) > 0,
            'docstring_count': len(docs_list)
        }
        return docs_text, metadata
    
    def _extract_generic_docs(self, code: str) -> Tuple[str, Dict[str, Any]]:
        """Generic comment extraction."""
        # Extract # comments (Python, Shell, etc.)
        hash_comments = re.findall(r'#\s*(.*?)$', code, re.MULTILINE)
        # Extract // comments
        slash_comments = re.findall(r'//\s*(.*?)$', code, re.MULTILINE)
        # Extract /* */ comments
        block_comments = re.findall(r'/\*(.*?)\*/', code, re.DOTALL)
        
        docs_list = hash_comments + slash_comments
        for doc in block_comments:
            clean_doc = re.sub(r'\s*\*\s*', ' ', doc).strip()
            docs_list.append(clean_doc)
        
        docs_text = '\n'.join(docs_list)
        metadata = {
            'has_docstring': len(docs_list) > 0,
            'docstring_count': len(docs_list)
        }
        return docs_text, metadata
    
    def _assess_doc_quality(self, docs: str) -> float:
        """
        Assess documentation quality.
        
        Returns score 0-1 based on:
        - Length (longer is better, up to a point)
        - Structure (has sentences)
        - Content (not just TODO or empty)
        """
        if not docs or not docs.strip():
            return 0.0
        
        score = 0.0
        docs = docs.strip()
        
        # Length score (0-0.4)
        length = len(docs)
        if length > 10:
            score += 0.1
        if length > 50:
            score += 0.1
        if length > 100:
            score += 0.1
        if length > 200:
            score += 0.1
        
        # Has sentences (0-0.3)
        sentences = len(re.findall(r'[.!?]+', docs))
        if sentences >= 1:
            score += 0.1
        if sentences >= 2:
            score += 0.1
        if sentences >= 3:
            score += 0.1
        
        # Not placeholder (0-0.3)
        placeholder_words = ['todo', 'fixme', 'xxx', 'tbd', 'placeholder']
        has_placeholder = any(word in docs.lower() for word in placeholder_words)
        if not has_placeholder:
            score += 0.3
        
        return min(score, 1.0)
    
    def get_statistics(
        self,
        indexed_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get statistics about indexed chunks.
        
        Args:
            indexed_chunks: List of indexed chunks
            
        Returns:
            Statistics dictionary
        """
        stats = {
            'total_chunks': len(indexed_chunks),
            'with_code_embeddings': 0,
            'with_doc_embeddings': 0,
            'with_both_embeddings': 0,
            'with_docstrings': 0,
            'avg_doc_quality': 0.0,
            'avg_doc_length': 0.0
        }
        
        if not indexed_chunks:
            return stats
        
        doc_qualities = []
        doc_lengths = []
        
        for chunk in indexed_chunks:
            if chunk.get('code_embedding') is not None:
                stats['with_code_embeddings'] += 1
            if chunk.get('doc_embedding') is not None:
                stats['with_doc_embeddings'] += 1
            if (chunk.get('code_embedding') is not None and 
                chunk.get('doc_embedding') is not None):
                stats['with_both_embeddings'] += 1
            if chunk.get('has_docstring'):
                stats['with_docstrings'] += 1
            
            if 'doc_quality_score' in chunk:
                doc_qualities.append(chunk['doc_quality_score'])
            if 'doc_length' in chunk:
                doc_lengths.append(chunk['doc_length'])
        
        if doc_qualities:
            stats['avg_doc_quality'] = sum(doc_qualities) / len(doc_qualities)
        if doc_lengths:
            stats['avg_doc_length'] = sum(doc_lengths) / len(doc_lengths)
        
        return stats


if __name__ == "__main__":
    print("Multi-modal Retrieval Module - Full Implementation")
    print("=" * 60)
    print("\nThis module provides code + documentation retrieval.")
    print("\nFeatures:")
    print("  - Separate code and doc embeddings")
    print("  - Weighted score combination")
    print("  - Cross-modal search")
    print("  - Documentation extraction")
    print("\nExample usage:")
    print("""
    from features.rag_advanced import CodeEmbedder, MultiModalRetriever
    from sentence_transformers import SentenceTransformer
    
    code_emb = CodeEmbedder('codebert')
    doc_emb = SentenceTransformer('all-MiniLM-L6-v2')
    mm_retriever = MultiModalRetriever(code_emb, doc_emb)
    
    # Index code with documentation
    result = mm_retriever.index_multimodal(
        code='def login(user, pwd): ...',
        docs='Authenticate user credentials',
        metadata={'file': 'auth.py'},
        language='python'
    )
    
    # Retrieve with hybrid search
    results = mm_retriever.retrieve_multimodal(
        query='user authentication',
        indexed_chunks=[result],
        mode='hybrid',
        top_k=5
    )
    """)
