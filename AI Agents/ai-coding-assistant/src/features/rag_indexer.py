"""
RAG Indexer Module

Implements Retrieval-Augmented Generation (RAG) indexing for semantic code search.
Provides:
- Semantic chunking (AST-based for Python, sliding window for others)
- Batch embedding generation with progress tracking
- ChromaDB integration for vector storage
- Incremental updates with SHA256 change detection
- Metadata storage (file path, line numbers, language, chunk IDs)

Features:
- Preserves function/class boundaries in Python
- GPU acceleration support
- Memory-efficient batch processing
- Persistent vector database per project
"""

import ast
import os
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class RAGIndexer:
    """
    Index codebase into vector database for semantic search.
    
    Uses sentence-transformers for embeddings and ChromaDB for storage.
    Supports semantic chunking and incremental updates.
    """
    
    # Default embedding model
    DEFAULT_MODEL = 'all-MiniLM-L6-v2'  # Fast, 80MB, good quality
    
    # Alternative models
    ALTERNATIVE_MODELS = {
        'fast': 'all-MiniLM-L6-v2',           # 80MB, fastest
        'balanced': 'all-mpnet-base-v2',      # 420MB, better quality
        'code': 'microsoft/codebert-base',    # 500MB, code-optimized
        'large': 'sentence-transformers/all-MiniLM-L12-v2'  # Larger, more accurate
    }
    
    # Chunking parameters
    DEFAULT_CHUNK_SIZE = 500  # tokens (approx 375 words)
    DEFAULT_OVERLAP = 50  # tokens overlap between chunks
    
    def __init__(
        self,
        embedding_model: str = DEFAULT_MODEL,
        db_path: str = "data/rag_db",
        batch_size: int = 32,
        use_gpu: bool = False,
        quantize: bool = False
    ):
        """
        Initialize the RAG indexer.
        
        Args:
            embedding_model: Name of sentence-transformers model or alias
                           Aliases: 'fast', 'balanced', 'code', 'large'
            db_path: Path to ChromaDB persistent storage
            batch_size: Batch size for embedding generation
            use_gpu: Whether to use GPU acceleration
            quantize: Whether to use INT8 quantization (reduces memory, slight speed loss)
            
        Example:
            >>> # Use default fast model
            >>> indexer = RAGIndexer()
            
            >>> # Use balanced model with quantization
            >>> indexer = RAGIndexer(
            ...     embedding_model='balanced',
            ...     quantize=True
            ... )
            
            >>> # Use code-optimized model on GPU
            >>> indexer = RAGIndexer(
            ...     embedding_model='code',
            ...     use_gpu=True
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
        
        # Resolve model alias if provided
        if embedding_model in self.ALTERNATIVE_MODELS:
            self.embedding_model_name = self.ALTERNATIVE_MODELS[embedding_model]
            print(f"Using '{embedding_model}' model: {self.embedding_model_name}")
        else:
            self.embedding_model_name = embedding_model
        
        self.db_path = Path(db_path)
        self.batch_size = batch_size
        self.use_gpu = use_gpu
        self.quantize = quantize
        
        # Initialize model (lazy loading)
        self._model = None
        
        # Initialize ChromaDB client (lazy loading)
        self._chroma_client = None
        
        # Ensure database directory exists
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Metadata file for tracking indexed files
        self.metadata_file = self.db_path / "index_metadata.json"
        self.metadata = self._load_metadata()
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the embedding model with optional quantization."""
        if self._model is None:
            print(f"Loading embedding model: {self.embedding_model_name}...")
            device = 'cuda' if self.use_gpu else 'cpu'
            
            # Load model
            self._model = SentenceTransformer(self.embedding_model_name, device=device)
            
            # Apply quantization if requested
            if self.quantize:
                try:
                    import torch
                    if hasattr(torch, 'quantization'):
                        print("Applying INT8 quantization...")
                        self._model = torch.quantization.quantize_dynamic(
                            self._model,
                            {torch.nn.Linear},
                            dtype=torch.qint8
                        )
                        print("✓ Model quantized (INT8)")
                    else:
                        print("⚠ Quantization not available, using full precision")
                except Exception as e:
                    print(f"⚠ Quantization failed: {e}, using full precision")
            
            print(f"✓ Model loaded on {device}")
        return self._model
    
    @property
    def chroma_client(self):
        """Lazy load ChromaDB client."""
        if self._chroma_client is None:
            print("Initializing ChromaDB client...")
            self._chroma_client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            print("✓ ChromaDB client initialized")
        return self._chroma_client
    
    def chunk_file(
        self,
        content: str,
        file_path: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP
    ) -> List[Dict[str, Any]]:
        """
        Split file into semantic chunks with metadata.
        
        Uses AST-based chunking for Python files (preserves functions/classes).
        Uses sliding window chunking for other languages.
        
        Args:
            content: File content as string
            file_path: Path to file (for language detection)
            chunk_size: Target chunk size in tokens
            overlap: Overlap between chunks in tokens
            
        Returns:
            List of chunk dictionaries with metadata
            
        Example:
            >>> chunks = indexer.chunk_file(
            ...     content=python_code,
            ...     file_path="src/main.py"
            ... )
            >>> print(f"Created {len(chunks)} chunks")
            >>> print(chunks[0]['metadata'])
        """
        # Detect language
        extension = Path(file_path).suffix.lower()
        
        # Use AST-based chunking for Python
        if extension in ['.py', '.pyw']:
            try:
                return self._chunk_python_ast(content, file_path, chunk_size)
            except SyntaxError:
                # Fallback to sliding window if syntax error
                pass
        
        # Use sliding window for other languages
        return self._chunk_sliding_window(content, file_path, chunk_size, overlap)
    
    def _chunk_python_ast(
        self,
        content: str,
        file_path: str,
        chunk_size: int
    ) -> List[Dict[str, Any]]:
        """
        Chunk Python code using AST to preserve function/class boundaries.
        
        Args:
            content: Python source code
            file_path: File path
            chunk_size: Target chunk size in tokens
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        lines = content.split('\n')
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            # If parse fails, fall back to sliding window
            return self._chunk_sliding_window(content, file_path, chunk_size, chunk_size // 10)
        
        # Extract top-level nodes (functions, classes, etc.)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                # Get the source segment
                try:
                    if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                        start_line = node.lineno - 1
                        end_line = node.end_lineno
                        
                        if start_line >= 0 and end_line <= len(lines):
                            chunk_content = '\n'.join(lines[start_line:end_line])
                            
                            # Estimate tokens (words / 0.75)
                            estimated_tokens = len(chunk_content.split()) / 0.75
                            
                            # Only include if under size limit
                            if estimated_tokens <= chunk_size * 1.5:  # Allow 50% overflow
                                chunk_id = f"{file_path}:{start_line}:{end_line}"
                                
                                chunks.append({
                                    'content': chunk_content,
                                    'metadata': {
                                        'file_path': file_path,
                                        'chunk_id': chunk_id,
                                        'start_line': start_line + 1,
                                        'end_line': end_line,
                                        'type': type(node).__name__,
                                        'name': node.name if hasattr(node, 'name') else 'anonymous',
                                        'language': 'python'
                                    }
                                })
                except Exception as e:
                    # Skip problematic nodes
                    continue
        
        # If no chunks extracted (empty file or only imports), create one chunk
        if not chunks:
            chunks = self._chunk_sliding_window(content, file_path, chunk_size, chunk_size // 10)
        
        return chunks
    
    def _chunk_sliding_window(
        self,
        content: str,
        file_path: str,
        chunk_size: int,
        overlap: int
    ) -> List[Dict[str, Any]]:
        """
        Chunk content using sliding window with overlap.
        
        Args:
            content: File content
            file_path: File path
            chunk_size: Chunk size in tokens
            overlap: Overlap in tokens
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        words = content.split()
        
        # Convert chunk_size from tokens to words (tokens ≈ words / 0.75)
        words_per_chunk = int(chunk_size * 0.75)
        overlap_words = int(overlap * 0.75)
        
        if not words:
            return chunks
        
        # Get language from extension
        extension = Path(file_path).suffix.lower()
        language_map = {
            '.js': 'javascript', '.jsx': 'javascript',
            '.ts': 'typescript', '.tsx': 'typescript',
            '.cpp': 'cpp', '.c': 'c', '.h': 'c/cpp',
            '.cs': 'csharp',
            '.go': 'go', '.rs': 'rust', '.java': 'java',
            '.rb': 'ruby', '.php': 'php', '.swift': 'swift',
            '.kt': 'kotlin', '.html': 'html', '.css': 'css',
            '.sh': 'bash', '.bat': 'batch', '.ps1': 'powershell',
        }
        language = language_map.get(extension, 'unknown')
        
        chunk_num = 0
        for i in range(0, len(words), words_per_chunk - overlap_words):
            chunk_words = words[i:i + words_per_chunk]
            chunk_content = ' '.join(chunk_words)
            
            # Estimate line numbers (approximate)
            start_word = i
            end_word = min(i + words_per_chunk, len(words))
            
            chunk_id = f"{file_path}:chunk_{chunk_num}"
            
            chunks.append({
                'content': chunk_content,
                'metadata': {
                    'file_path': file_path,
                    'chunk_id': chunk_id,
                    'chunk_num': chunk_num,
                    'word_start': start_word,
                    'word_end': end_word,
                    'language': language
                }
            })
            
            chunk_num += 1
        
        return chunks
    
    def embed_chunks(
        self,
        chunks: List[Dict[str, Any]],
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for chunks in batches.
        
        Args:
            chunks: List of chunk dictionaries
            show_progress: Whether to show progress
            
        Returns:
            NumPy array of embeddings (shape: [num_chunks, embedding_dim])
            
        Example:
            >>> chunks = indexer.chunk_file(content, "main.py")
            >>> embeddings = indexer.embed_chunks(chunks)
            >>> print(f"Embedding shape: {embeddings.shape}")
        """
        if not chunks:
            return np.array([])
        
        # Extract content for embedding
        texts = [chunk['content'] for chunk in chunks]
        
        # Generate embeddings in batches
        embeddings = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            if show_progress:
                batch_num = i // self.batch_size + 1
                print(f"  Embedding batch {batch_num}/{total_batches}...", end='\r')
            
            batch_embeddings = self.model.encode(
                batch,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            embeddings.append(batch_embeddings)
        
        if show_progress:
            print(f"  ✓ Embedded {len(texts)} chunks" + " " * 20)
        
        # Concatenate all batches
        return np.vstack(embeddings)
    
    def build_vector_db(
        self,
        root_folder: str,
        project_name: Optional[str] = None,
        force_rebuild: bool = False
    ) -> str:
        """
        Index entire project into ChromaDB.
        
        Scans all files, chunks them, generates embeddings, and stores in vector DB.
        
        Args:
            root_folder: Path to project root
            project_name: Optional project name (defaults to folder name)
            force_rebuild: Force rebuild even if already indexed
            
        Returns:
            Collection name
            
        Example:
            >>> collection = indexer.build_vector_db('/path/to/project')
            >>> print(f"Indexed into collection: {collection}")
        """
        root_path = Path(root_folder).resolve()
        
        if not root_path.exists():
            raise ValueError(f"Root folder does not exist: {root_folder}")
        
        if project_name is None:
            project_name = root_path.name
        
        # Sanitize collection name (ChromaDB requirements)
        collection_name = self._sanitize_collection_name(project_name)
        
        print(f"\n=== Indexing project: {project_name} ===")
        print(f"Root folder: {root_path}")
        print(f"Collection: {collection_name}")
        
        # Check if already indexed
        if not force_rebuild:
            existing = self.metadata.get(collection_name, {})
            if existing.get('root_folder') == str(root_path):
                print(f"✓ Project already indexed (use force_rebuild=True to rebuild)")
                return collection_name
        
        # Get or create collection
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
            if force_rebuild:
                self.chroma_client.delete_collection(name=collection_name)
                collection = self.chroma_client.create_collection(name=collection_name)
                print("✓ Existing collection deleted, creating new one")
        except:
            collection = self.chroma_client.create_collection(name=collection_name)
            print("✓ Created new collection")
        
        # Scan and index files
        total_files = 0
        total_chunks = 0
        skipped_files = 0
        
        # Patterns to exclude
        exclude_patterns = {
            '.git', '__pycache__', 'node_modules', 'venv', 'env',
            '.venv', 'dist', 'build', '.cache', 'target', '.vs', '.idea'
        }
        
        # Binary extensions to skip
        binary_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.jpg', '.jpeg', '.png',
            '.gif', '.pdf', '.zip', '.tar', '.gz', '.mp3', '.mp4',
            '.pyc', '.pyo', '.class', '.jar', '.db', '.sqlite'
        }
        
        print("\nScanning files...")
        files_to_process = []
        
        for root, dirs, files in os.walk(root_path):
            # Filter directories
            dirs[:] = [d for d in dirs if d not in exclude_patterns]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip binary files
                if file_path.suffix.lower() in binary_extensions:
                    continue
                
                # Skip very large files (>1MB)
                try:
                    if file_path.stat().st_size > 1024 * 1024:
                        skipped_files += 1
                        continue
                except:
                    continue
                
                files_to_process.append(file_path)
        
        print(f"Found {len(files_to_process)} files to index")
        
        # Process files
        for file_path in files_to_process:
            try:
                # Read file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if not content.strip():
                    continue
                
                # Get relative path
                rel_path = file_path.relative_to(root_path)
                rel_path_str = str(rel_path).replace('\\', '/')
                
                # Chunk file
                chunks = self.chunk_file(
                    content=content,
                    file_path=rel_path_str,
                    chunk_size=self.DEFAULT_CHUNK_SIZE,
                    overlap=self.DEFAULT_OVERLAP
                )
                
                if not chunks:
                    continue
                
                # Generate embeddings
                embeddings = self.embed_chunks(chunks, show_progress=False)
                
                # Prepare data for ChromaDB
                ids = [chunk['metadata']['chunk_id'] for chunk in chunks]
                documents = [chunk['content'] for chunk in chunks]
                metadatas = [chunk['metadata'] for chunk in chunks]
                
                # Compute file hash for change detection
                file_hash = self._compute_file_hash(file_path)
                for meta in metadatas:
                    meta['file_hash'] = file_hash
                
                # Add to collection
                collection.add(
                    ids=ids,
                    embeddings=embeddings.tolist(),
                    documents=documents,
                    metadatas=metadatas
                )
                
                total_files += 1
                total_chunks += len(chunks)
                print(f"  [{total_files}/{len(files_to_process)}] {rel_path_str}: {len(chunks)} chunks")
                
            except Exception as e:
                skipped_files += 1
                print(f"  Warning: Could not process {file_path.name}: {e}")
                continue
        
        # Update metadata
        self.metadata[collection_name] = {
            'root_folder': str(root_path),
            'project_name': project_name,
            'indexed_at': datetime.now().isoformat(),
            'total_files': total_files,
            'total_chunks': total_chunks,
            'embedding_model': self.embedding_model_name
        }
        self._save_metadata()
        
        print(f"\n✓ Indexing complete!")
        print(f"  Files indexed: {total_files}")
        print(f"  Total chunks: {total_chunks}")
        print(f"  Skipped: {skipped_files}")
        
        return collection_name
    
    def incremental_update(
        self,
        file_path: str,
        collection_name: str,
        project_root: str
    ) -> int:
        """
        Update embeddings for a single changed file.
        
        Detects changes via SHA256 hash and only updates if file changed.
        
        Args:
            file_path: Path to the file (absolute or relative to project_root)
            collection_name: ChromaDB collection name
            project_root: Project root folder
            
        Returns:
            Number of chunks updated (0 if unchanged)
            
        Example:
            >>> updated = indexer.incremental_update(
            ...     file_path="src/main.py",
            ...     collection_name="my-project",
            ...     project_root="/path/to/project"
            ... )
            >>> print(f"Updated {updated} chunks")
        """
        file_path = Path(file_path)
        project_root = Path(project_root)
        
        if not file_path.is_absolute():
            file_path = project_root / file_path
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get relative path
        rel_path = file_path.relative_to(project_root)
        rel_path_str = str(rel_path).replace('\\', '/')
        
        # Compute current file hash
        current_hash = self._compute_file_hash(file_path)
        
        # Get collection
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
        except:
            raise ValueError(f"Collection not found: {collection_name}")
        
        # Check if file is already indexed with same hash
        existing = collection.get(where={"file_path": rel_path_str})
        if existing and existing['metadatas']:
            old_hash = existing['metadatas'][0].get('file_hash')
            if old_hash == current_hash:
                print(f"✓ File unchanged: {rel_path_str}")
                return 0
        
        # Delete old chunks for this file
        if existing and existing['ids']:
            collection.delete(ids=existing['ids'])
            print(f"  Deleted {len(existing['ids'])} old chunks")
        
        # Read and chunk file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        chunks = self.chunk_file(
            content=content,
            file_path=rel_path_str,
            chunk_size=self.DEFAULT_CHUNK_SIZE,
            overlap=self.DEFAULT_OVERLAP
        )
        
        if not chunks:
            return 0
        
        # Generate embeddings
        print(f"  Embedding {len(chunks)} new chunks...")
        embeddings = self.embed_chunks(chunks, show_progress=False)
        
        # Prepare data
        ids = [chunk['metadata']['chunk_id'] for chunk in chunks]
        documents = [chunk['content'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # Add file hash to metadata
        for meta in metadatas:
            meta['file_hash'] = current_hash
        
        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"✓ Updated {len(chunks)} chunks for {rel_path_str}")
        return len(chunks)
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get information about an indexed collection.
        
        Args:
            collection_name: Collection name
            
        Returns:
            Dictionary with collection information
        """
        metadata = self.metadata.get(collection_name, {})
        
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
            count = collection.count()
        except:
            count = 0
        
        return {
            'collection_name': collection_name,
            'exists': count > 0,
            'total_chunks': count,
            'metadata': metadata
        }
    
    def list_collections(self) -> List[str]:
        """
        List all indexed collections.
        
        Returns:
            List of collection names
        """
        collections = self.chroma_client.list_collections()
        return [c.name for c in collections]
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection from the vector database.
        
        Args:
            collection_name: Collection to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            self.chroma_client.delete_collection(name=collection_name)
            if collection_name in self.metadata:
                del self.metadata[collection_name]
                self._save_metadata()
            print(f"✓ Deleted collection: {collection_name}")
            return True
        except Exception as e:
            print(f"✗ Error deleting collection: {e}")
            return False
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file for change detection."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _sanitize_collection_name(self, name: str) -> str:
        """Sanitize collection name for ChromaDB."""
        # ChromaDB requires: 3-63 chars, alphanumeric + _ - .
        sanitized = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c in '_-.')
        sanitized = sanitized[:63]  # Max 63 characters
        if len(sanitized) < 3:
            sanitized = sanitized + '_collection'
        return sanitized
    
    def _load_metadata(self) -> Dict:
        """Load metadata from disk."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_metadata(self) -> None:
        """Save metadata to disk."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save metadata: {e}")
    
    def unload_model(self) -> None:
        """Unload the embedding model to free memory."""
        if self._model is not None:
            del self._model
            self._model = None
            print("✓ Embedding model unloaded")


if __name__ == "__main__":
    # Test the RAG indexer
    print("Testing RAG Indexer...")
    
    try:
        # Create indexer
        indexer = RAGIndexer(
            embedding_model='all-MiniLM-L6-v2',
            db_path='data/rag_db_test',
            use_gpu=False
        )
        print("✓ RAG Indexer created")
        
        # Test chunking
        print("\n=== Test: Python AST Chunking ===")
        python_code = '''
def hello_world():
    """Say hello."""
    print("Hello, World!")

class MyClass:
    def __init__(self):
        self.value = 42
        
    def method(self):
        return self.value
'''
        chunks = indexer.chunk_file(python_code, "test.py")
        print(f"✓ Created {len(chunks)} chunks from Python code")
        for chunk in chunks:
            print(f"  - {chunk['metadata']['type']}: {chunk['metadata']['name']}")
        
        # Test embedding
        print("\n=== Test: Embedding ===")
        embeddings = indexer.embed_chunks(chunks)
        print(f"✓ Generated embeddings: shape {embeddings.shape}")
        
        # Test collection info
        print("\n=== Test: List Collections ===")
        collections = indexer.list_collections()
        print(f"✓ Found {len(collections)} collections: {collections}")
        
        print("\n✓ All tests passed!")
        
    except ImportError as e:
        print(f"✗ Required packages not installed: {e}")
        print("Install with: pip install sentence-transformers==2.2.2 chromadb==0.4.18 numpy==1.24.3")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
