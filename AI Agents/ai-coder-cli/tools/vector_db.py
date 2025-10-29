"""
Vector Database Module using ChromaDB

This module provides vector database functionality using ChromaDB for semantic
search, document storage, and retrieval operations.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import uuid

import chromadb
from chromadb.config import Settings
from chromadb.api.types import QueryResult

from .embeddings import EmbeddingGenerator, create_embedding_generator
from .base import Tool


logger = logging.getLogger(__name__)


class ChromaVectorDB:
    """
    Vector database using ChromaDB for semantic search and document storage.
    
    Features:
        - Document storage with metadata
        - Semantic search using embeddings
        - Collection management
        - Persistent storage
        - Filtering and querying
    
    Usage:
        ```python
        # Initialize
        db = ChromaVectorDB(persist_directory="./chroma_db")
        
        # Add documents
        db.add_documents(
            collection_name="code_snippets",
            documents=["def hello():\n    print('Hello')", "class MyClass:\n    pass"],
            metadatas=[{"lang": "python"}, {"lang": "python"}],
            ids=["snippet1", "snippet2"]
        )
        
        # Search
        results = db.search(
            collection_name="code_snippets",
            query="python function",
            n_results=5
        )
        ```
    """
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        embedding_generator: Optional[EmbeddingGenerator] = None,
        embedding_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize ChromaDB vector database.
        
        Args:
            persist_directory: Directory for persistent storage
            embedding_generator: Custom embedding generator (optional)
            embedding_config: Config for default embedding generator
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding generator
        if embedding_generator:
            self.embedding_generator = embedding_generator
        else:
            self.embedding_generator = create_embedding_generator(embedding_config or {})
        
        logger.info(f"ChromaVectorDB initialized with persist_directory={persist_directory}")
    
    def create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
        get_or_create: bool = True
    ) -> None:
        """
        Create a new collection in the database.
        
        Args:
            name: Collection name
            metadata: Optional collection metadata
            get_or_create: Return existing collection if it exists
            
        Raises:
            ValueError: If collection exists and get_or_create is False
        """
        try:
            if get_or_create:
                collection = self.client.get_or_create_collection(
                    name=name,
                    metadata=metadata
                )
                logger.info(f"Collection '{name}' created or retrieved")
            else:
                collection = self.client.create_collection(
                    name=name,
                    metadata=metadata
                )
                logger.info(f"Collection '{name}' created")
        except Exception as e:
            logger.error(f"Failed to create collection '{name}': {e}")
            raise
    
    def delete_collection(self, name: str) -> None:
        """
        Delete a collection from the database.
        
        Args:
            name: Collection name
        """
        try:
            self.client.delete_collection(name=name)
            logger.info(f"Collection '{name}' deleted")
        except Exception as e:
            logger.error(f"Failed to delete collection '{name}': {e}")
            raise
    
    def list_collections(self) -> List[str]:
        """
        List all collections in the database.
        
        Returns:
            List of collection names
        """
        try:
            collections = self.client.list_collections()
            names = [c.name for c in collections]
            logger.debug(f"Found {len(names)} collection(s)")
            return names
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            raise
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to a collection.
        
        Args:
            collection_name: Collection name
            documents: List of document texts
            metadatas: Optional list of metadata dicts (one per document)
            ids: Optional list of document IDs (auto-generated if not provided)
            
        Returns:
            List of document IDs
            
        Raises:
            ValueError: If documents list is empty or lengths don't match
        """
        if not documents:
            raise ValueError("Documents list cannot be empty")
        
        if metadatas and len(metadatas) != len(documents):
            raise ValueError("Length of metadatas must match documents")
        
        if ids and len(ids) != len(documents):
            raise ValueError("Length of ids must match documents")
        
        try:
            # Get or create collection
            collection = self.client.get_or_create_collection(name=collection_name)
            
            # Generate IDs if not provided
            if not ids:
                ids = [str(uuid.uuid4()) for _ in documents]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(documents)} document(s)")
            embeddings = self.embedding_generator.generate_batch(documents)
            
            # Add to collection
            collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} document(s) to collection '{collection_name}'")
            return ids
            
        except Exception as e:
            logger.error(f"Failed to add documents to collection '{collection_name}': {e}")
            raise
    
    def search(
        self,
        collection_name: str,
        query: str,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar documents in a collection.
        
        Args:
            collection_name: Collection name
            query: Search query text
            n_results: Number of results to return
            where: Metadata filter (e.g., {"lang": "python"})
            where_document: Document content filter
            
        Returns:
            Dictionary with search results:
                - ids: List of document IDs
                - documents: List of document texts
                - metadatas: List of metadata dicts
                - distances: List of distance scores
                
        Raises:
            ValueError: If collection doesn't exist
        """
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception as e:
            logger.error(f"Collection '{collection_name}' not found: {e}")
            raise ValueError(f"Collection '{collection_name}' does not exist") from e
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.generate(query)
            
            # Perform search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            
            # Format results
            formatted_results = {
                'ids': results['ids'][0] if results['ids'] else [],
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else [],
                'distances': results['distances'][0] if results['distances'] else []
            }
            
            logger.info(
                f"Search in '{collection_name}' returned {len(formatted_results['ids'])} result(s)"
            )
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed in collection '{collection_name}': {e}")
            raise
    
    def get_documents(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieve documents from a collection.
        
        Args:
            collection_name: Collection name
            ids: Specific document IDs to retrieve
            where: Metadata filter
            limit: Maximum number of documents to return
            
        Returns:
            Dictionary with documents:
                - ids: List of document IDs
                - documents: List of document texts
                - metadatas: List of metadata dicts
        """
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception as e:
            logger.error(f"Collection '{collection_name}' not found: {e}")
            raise ValueError(f"Collection '{collection_name}' does not exist") from e
        
        try:
            results = collection.get(
                ids=ids,
                where=where,
                limit=limit
            )
            
            logger.info(f"Retrieved {len(results['ids'])} document(s) from '{collection_name}'")
            return results
            
        except Exception as e:
            logger.error(f"Failed to get documents from '{collection_name}': {e}")
            raise
    
    def update_documents(
        self,
        collection_name: str,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Update documents in a collection.
        
        Args:
            collection_name: Collection name
            ids: Document IDs to update
            documents: Updated document texts (optional)
            metadatas: Updated metadata dicts (optional)
            
        Raises:
            ValueError: If neither documents nor metadatas is provided
        """
        if not documents and not metadatas:
            raise ValueError("Must provide documents and/or metadatas to update")
        
        if documents and len(documents) != len(ids):
            raise ValueError("Length of documents must match ids")
        
        if metadatas and len(metadatas) != len(ids):
            raise ValueError("Length of metadatas must match ids")
        
        try:
            collection = self.client.get_collection(name=collection_name)
            
            update_kwargs = {'ids': ids}
            
            if documents:
                # Generate new embeddings if documents are updated
                embeddings = self.embedding_generator.generate_batch(documents)
                update_kwargs['embeddings'] = embeddings
                update_kwargs['documents'] = documents
            
            if metadatas:
                update_kwargs['metadatas'] = metadatas
            
            collection.update(**update_kwargs)
            
            logger.info(f"Updated {len(ids)} document(s) in collection '{collection_name}'")
            
        except Exception as e:
            logger.error(f"Failed to update documents in '{collection_name}': {e}")
            raise
    
    def delete_documents(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Delete documents from a collection.
        
        Args:
            collection_name: Collection name
            ids: Document IDs to delete
            where: Metadata filter for documents to delete
            
        Raises:
            ValueError: If neither ids nor where is provided
        """
        if not ids and not where:
            raise ValueError("Must provide ids or where filter")
        
        try:
            collection = self.client.get_collection(name=collection_name)
            collection.delete(ids=ids, where=where)
            
            logger.info(f"Deleted documents from collection '{collection_name}'")
            
        except Exception as e:
            logger.error(f"Failed to delete documents from '{collection_name}': {e}")
            raise
    
    def get_collection_count(self, collection_name: str) -> int:
        """
        Get the number of documents in a collection.
        
        Args:
            collection_name: Collection name
            
        Returns:
            Number of documents
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()
            logger.debug(f"Collection '{collection_name}' has {count} document(s)")
            return count
        except Exception as e:
            logger.error(f"Failed to get count for collection '{collection_name}': {e}")
            raise
    
    def reset(self) -> None:
        """
        Reset the entire database (delete all collections).
        
        WARNING: This is a destructive operation that cannot be undone.
        """
        try:
            self.client.reset()
            logger.warning("Database reset - all collections deleted")
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            raise


def create_vector_db(config: Optional[Dict[str, Any]] = None) -> ChromaVectorDB:
    """
    Factory function to create a ChromaVectorDB from configuration.
    
    Args:
        config: Configuration dictionary with keys:
            - persist_directory: Database storage directory
            - embedding: Embedding configuration
            
    Returns:
        Configured ChromaVectorDB instance
    """
    config = config or {}
    
    persist_directory = config.get('persist_directory', './chroma_db')
    embedding_config = config.get('embedding', {})
    
    return ChromaVectorDB(
        persist_directory=persist_directory,
        embedding_config=embedding_config
    )


class VectorDBTool(Tool):
    """
    Tool wrapper for ChromaVectorDB that provides a Tool interface.
    
    This class wraps ChromaVectorDB functionality and exposes it through
    the Tool interface so it can be used by agents.
    
    Supported actions:
        - create_collection: Create a new collection
        - delete_collection: Delete a collection
        - list_collections: List all collections
        - add_documents: Add documents to a collection
        - search: Search for similar documents
        - get_documents: Retrieve documents by ID or filter
        - update_documents: Update existing documents
        - delete_documents: Delete documents
        - get_count: Get document count in a collection
    """
    
    def __init__(
        self,
        name: str = "vector_db",
        description: str = "Vector database tool for semantic search and document storage",
        config: Optional[Dict[str, Any]] = None,
        plugin_loader: Optional[Any] = None
    ):
        """
        Initialize VectorDBTool.
        
        Args:
            name: Tool name
            description: Tool description
            config: Configuration with vector_db settings
            plugin_loader: Optional plugin loader
        """
        super().__init__(name, description, config, plugin_loader)
        
        # Extract vector DB config
        db_config = self.config.get('vector_db', {})
        persist_directory = db_config.get('persist_directory', './chroma_db')
        embedding_config = db_config.get('embedding', {})
        
        # Initialize the underlying ChromaVectorDB
        self.db = ChromaVectorDB(
            persist_directory=persist_directory,
            embedding_config=embedding_config
        )
    
    def invoke(self, params: Dict[str, Any]) -> Any:
        """
        Invoke the vector database tool with the given parameters.
        
        Args:
            params: Dictionary with 'action' key and action-specific parameters
            
        Returns:
            Result of the operation
            
        Raises:
            ValueError: If action is invalid or required parameters are missing
        """
        action = params.get('action')
        
        if not action:
            raise ValueError("Parameter 'action' is required")
        
        # Route to appropriate method based on action
        if action == 'create_collection':
            self.validate_params(params, ['collection', 'action'])
            return self._create_collection(params)
        
        elif action == 'delete_collection':
            self.validate_params(params, ['collection', 'action'])
            return self._delete_collection(params)
        
        elif action == 'list_collections':
            return self._list_collections()
        
        elif action == 'add_documents':
            self.validate_params(params, ['collection', 'documents', 'action'])
            return self._add_documents(params)
        
        elif action == 'search':
            self.validate_params(params, ['collection', 'query', 'action'])
            return self._search(params)
        
        elif action == 'get_documents':
            self.validate_params(params, ['collection', 'action'])
            return self._get_documents(params)
        
        elif action == 'update_documents':
            self.validate_params(params, ['collection', 'ids', 'action'])
            return self._update_documents(params)
        
        elif action == 'delete_documents':
            self.validate_params(params, ['collection', 'action'])
            return self._delete_documents(params)
        
        elif action == 'get_count':
            self.validate_params(params, ['collection', 'action'])
            return self._get_count(params)
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _create_collection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new collection."""
        collection = params['collection']
        metadata = params.get('metadata')
        get_or_create = params.get('get_or_create', True)
        
        self.db.create_collection(collection, metadata, get_or_create)
        
        return {
            'success': True,
            'collection': collection,
            'message': f"Collection '{collection}' created successfully"
        }
    
    def _delete_collection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a collection."""
        collection = params['collection']
        
        self.db.delete_collection(collection)
        
        return {
            'success': True,
            'collection': collection,
            'message': f"Collection '{collection}' deleted successfully"
        }
    
    def _list_collections(self) -> Dict[str, Any]:
        """List all collections."""
        collections = self.db.list_collections()
        
        return {
            'success': True,
            'collections': collections,
            'count': len(collections)
        }
    
    def _add_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add documents to a collection."""
        collection = params['collection']
        documents = params['documents']
        metadatas = params.get('metadatas')
        ids = params.get('ids')
        
        document_ids = self.db.add_documents(collection, documents, metadatas, ids)
        
        return {
            'success': True,
            'collection': collection,
            'ids': document_ids,
            'count': len(document_ids),
            'message': f"Added {len(document_ids)} document(s) to '{collection}'"
        }
    
    def _search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for similar documents."""
        collection = params['collection']
        query = params['query']
        n_results = params.get('n_results', 10)
        where = params.get('where')
        where_document = params.get('where_document')
        
        results = self.db.search(collection, query, n_results, where, where_document)
        
        return {
            'success': True,
            'collection': collection,
            'query': query,
            'results': results,
            'count': len(results['ids'])
        }
    
    def _get_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve documents from a collection."""
        collection = params['collection']
        ids = params.get('ids')
        where = params.get('where')
        limit = params.get('limit')
        
        results = self.db.get_documents(collection, ids, where, limit)
        
        return {
            'success': True,
            'collection': collection,
            'results': results,
            'count': len(results['ids'])
        }
    
    def _update_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update documents in a collection."""
        collection = params['collection']
        ids = params['ids']
        documents = params.get('documents')
        metadatas = params.get('metadatas')
        
        self.db.update_documents(collection, ids, documents, metadatas)
        
        return {
            'success': True,
            'collection': collection,
            'ids': ids,
            'count': len(ids),
            'message': f"Updated {len(ids)} document(s) in '{collection}'"
        }
    
    def _delete_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete documents from a collection."""
        collection = params['collection']
        ids = params.get('ids')
        where = params.get('where')
        
        self.db.delete_documents(collection, ids, where)
        
        return {
            'success': True,
            'collection': collection,
            'message': "Documents deleted successfully"
        }
    
    def _get_count(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get document count in a collection."""
        collection = params['collection']
        
        count = self.db.get_collection_count(collection)
        
        return {
            'success': True,
            'collection': collection,
            'count': count
        }
