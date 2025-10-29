"""
Vector-Enhanced Memory System

This module extends the base memory system with vector database capabilities
for semantic search and context retrieval. It integrates ChromaDB for storing
and retrieving agent interactions, task history, and context based on semantic
similarity rather than just recency.

Features:
- Semantic search across conversation history
- Context-aware memory retrieval
- Automatic embedding generation for messages
- Hybrid retrieval (vector + recency + metadata filters)
- Integration with existing MemoryManager
- Task and interaction tracking
- Agent collaboration context
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from .memory import MemoryManager, MemorySession, Message, MessageRole
from tools.vector_db import ChromaVectorDB, create_vector_db
from tools.embeddings import EmbeddingGenerator, create_embedding_generator


logger = logging.getLogger(__name__)


class VectorMemoryManager(MemoryManager):
    """
    Enhanced memory manager with vector database integration.
    
    Extends the base MemoryManager with semantic search capabilities using
    ChromaDB vector database. Stores messages with embeddings for context-aware
    retrieval across sessions and agents.
    
    Features:
    - All base MemoryManager features
    - Semantic search across messages
    - Context retrieval based on query similarity
    - Task history tracking with embeddings
    - Agent interaction patterns
    - Cross-session context discovery
    
    Collections:
    - messages: All conversation messages with embeddings
    - tasks: Task definitions and outcomes
    - contexts: Important context snapshots
    - agent_outputs: Agent execution results
    
    Example:
        >>> vm = VectorMemoryManager(
        ...     storage_path=Path("./memory"),
        ...     vector_db_path="./vector_db"
        ... )
        >>> session_id = vm.create_session()
        >>> vm.add_user_message(session_id, "How do I use async in Python?")
        >>> # Later, retrieve similar past interactions
        >>> similar = vm.semantic_search("python asyncio examples")
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        vector_db_path: str = "./chroma_db",
        default_max_context_window: int = 4096,
        auto_save: bool = True,
        enable_summarization: bool = True,
        llm_router: Optional[Any] = None,
        embedding_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize vector-enhanced memory manager.
        
        Args:
            storage_path: Path for memory file storage
            vector_db_path: Path for vector database
            default_max_context_window: Default context window size
            auto_save: Enable auto-save
            enable_summarization: Enable memory summarization
            llm_router: LLM router for summarization
            embedding_config: Embedding generator configuration
        """
        # Initialize base memory manager
        super().__init__(
            storage_path=storage_path,
            default_max_context_window=default_max_context_window,
            auto_save=auto_save,
            enable_summarization=enable_summarization,
            llm_router=llm_router
        )
        
        # Initialize vector database
        self.vector_db = create_vector_db({
            'persist_directory': vector_db_path,
            'embedding': embedding_config or {}
        })
        
        # Initialize collections
        self._init_collections()
        
        logger.info(f"VectorMemoryManager initialized with vector_db at {vector_db_path}")
    
    def _init_collections(self) -> None:
        """Initialize vector database collections."""
        collections = {
            'messages': {'description': 'Conversation messages with context'},
            'tasks': {'description': 'Task definitions and outcomes'},
            'contexts': {'description': 'Important context snapshots'},
            'agent_outputs': {'description': 'Agent execution results'},
            'file_references': {'description': 'References to code and files'},
        }
        
        for collection_name, metadata in collections.items():
            try:
                self.vector_db.create_collection(collection_name, metadata=metadata, get_or_create=True)
                logger.debug(f"Collection '{collection_name}' ready")
            except Exception as e:
                logger.error(f"Failed to create collection '{collection_name}': {e}")
    
    # ========================================================================
    # Enhanced Message Management
    # ========================================================================
    
    def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        store_in_vector_db: bool = True
    ) -> bool:
        """
        Add a message to session and optionally store in vector database.
        
        Args:
            session_id: Session ID
            role: Message role
            content: Message content
            agent_name: Agent name (for agent messages)
            metadata: Message metadata
            store_in_vector_db: Whether to store in vector DB
            
        Returns:
            True if added successfully
        """
        # Add to base memory system
        success = super().add_message(session_id, role, content, agent_name, metadata)
        
        if not success:
            return False
        
        # Store in vector database if enabled
        if store_in_vector_db and content.strip():
            try:
                self._store_message_in_vector_db(
                    session_id=session_id,
                    role=role,
                    content=content,
                    agent_name=agent_name,
                    metadata=metadata or {}
                )
            except Exception as e:
                logger.error(f"Failed to store message in vector DB: {e}")
                # Don't fail the entire operation if vector storage fails
        
        return True
    
    def _store_message_in_vector_db(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        agent_name: Optional[str],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Store a message in the vector database.
        
        Args:
            session_id: Session ID
            role: Message role
            content: Message content
            agent_name: Agent name
            metadata: Message metadata
        """
        # Prepare metadata for vector storage
        vec_metadata = {
            'session_id': session_id,
            'role': role.value,
            'agent_name': agent_name or 'unknown',
            'timestamp': datetime.now().isoformat(),
            'type': 'message',
            **metadata
        }
        
        # Generate unique ID
        message_id = str(uuid.uuid4())
        
        # Store in vector database
        self.vector_db.add_documents(
            collection_name='messages',
            documents=[content],
            metadatas=[vec_metadata],
            ids=[message_id]
        )
        
        logger.debug(f"Stored message {message_id[:8]} in vector DB")
    
    # ========================================================================
    # Semantic Search and Context Retrieval
    # ========================================================================
    
    def semantic_search(
        self,
        query: str,
        collection: str = 'messages',
        n_results: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for semantically similar content in memory.
        
        Args:
            query: Search query
            collection: Collection to search in
            n_results: Number of results to return
            filter_metadata: Metadata filters
            session_id: Optional session filter
            
        Returns:
            List of matching documents with metadata
        """
        try:
            # Add session filter if provided
            where_filter = filter_metadata or {}
            if session_id:
                where_filter['session_id'] = session_id
            
            # Perform vector search
            results = self.vector_db.search(
                collection_name=collection,
                query=query,
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'])):
                formatted_results.append({
                    'id': results['ids'][i],
                    'content': results['documents'][i],
                    'metadata': results['metadatas'][i],
                    'distance': results['distances'][i]
                })
            
            logger.info(f"Semantic search for '{query[:50]}...' returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    def get_relevant_context(
        self,
        query: str,
        session_id: Optional[str] = None,
        max_results: int = 5,
        include_recent: bool = True,
        recent_count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get relevant context for a query using hybrid retrieval.
        
        Combines semantic search with recency to provide the most relevant
        context for answering a query or executing a task.
        
        Args:
            query: Query or task description
            session_id: Optional session filter
            max_results: Maximum semantic search results
            include_recent: Include recent messages
            recent_count: Number of recent messages to include
            
        Returns:
            List of context items (messages, tasks, etc.)
        """
        context_items = []
        
        # 1. Get semantically similar messages
        semantic_results = self.semantic_search(
            query=query,
            collection='messages',
            n_results=max_results,
            session_id=session_id
        )
        
        for result in semantic_results:
            context_items.append({
                'type': 'semantic',
                'content': result['content'],
                'metadata': result['metadata'],
                'relevance': 1.0 - result['distance']  # Convert distance to similarity
            })
        
        # 2. Get recent messages if requested
        if include_recent and session_id:
            session = self.get_session(session_id)
            if session:
                recent_messages = session.get_recent_messages(recent_count)
                for msg in recent_messages:
                    context_items.append({
                        'type': 'recent',
                        'content': msg.content,
                        'metadata': {
                            'role': msg.role.value,
                            'agent_name': msg.agent_name,
                            'timestamp': msg.timestamp.isoformat()
                        },
                        'relevance': 1.0  # Recent messages are always relevant
                    })
        
        # 3. Sort by relevance
        context_items.sort(key=lambda x: x['relevance'], reverse=True)
        
        logger.info(f"Retrieved {len(context_items)} context items for query")
        return context_items
    
    def find_similar_past_interactions(
        self,
        query: str,
        agent_name: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar past interactions for learning from history.
        
        Args:
            query: Query to find similar interactions for
            agent_name: Optional filter by agent
            n_results: Number of results
            
        Returns:
            List of similar past interactions
        """
        filter_metadata = {}
        if agent_name:
            filter_metadata['agent_name'] = agent_name
        
        return self.semantic_search(
            query=query,
            collection='messages',
            n_results=n_results,
            filter_metadata=filter_metadata
        )
    
    # ========================================================================
    # Task and Context Storage
    # ========================================================================
    
    def store_task(
        self,
        task_id: str,
        task_description: str,
        agent_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a task in the vector database.
        
        Args:
            task_id: Unique task identifier
            task_description: Task description
            agent_name: Agent executing the task
            metadata: Additional metadata
            
        Returns:
            True if stored successfully
        """
        try:
            task_metadata = {
                'task_id': task_id,
                'agent_name': agent_name,
                'timestamp': datetime.now().isoformat(),
                'type': 'task',
                **(metadata or {})
            }
            
            self.vector_db.add_documents(
                collection_name='tasks',
                documents=[task_description],
                metadatas=[task_metadata],
                ids=[task_id]
            )
            
            logger.info(f"Stored task {task_id[:8]} in vector DB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store task: {e}")
            return False
    
    def update_task(
        self,
        task_id: str,
        outcome: str,
        status: str,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a task with outcome and status.
        
        Args:
            task_id: Task identifier
            outcome: Task outcome description
            status: Task status (completed, failed, etc.)
            additional_metadata: Additional metadata
            
        Returns:
            True if updated successfully
        """
        try:
            # Get existing task
            existing = self.vector_db.get_documents(
                collection_name='tasks',
                ids=[task_id]
            )
            
            if not existing['ids']:
                logger.warning(f"Task {task_id} not found for update")
                return False
            
            # Update metadata
            metadata = existing['metadatas'][0]
            metadata.update({
                'outcome': outcome,
                'status': status,
                'updated_at': datetime.now().isoformat(),
                **(additional_metadata or {})
            })
            
            # Update in vector DB
            self.vector_db.update_documents(
                collection_name='tasks',
                ids=[task_id],
                metadatas=[metadata]
            )
            
            logger.info(f"Updated task {task_id[:8]} with status {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task: {e}")
            return False
    
    def store_context_snapshot(
        self,
        context_id: str,
        context_data: str,
        context_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store an important context snapshot.
        
        Args:
            context_id: Unique context identifier
            context_data: Context content
            context_type: Type of context (e.g., 'code', 'decision', 'error')
            metadata: Additional metadata
            
        Returns:
            True if stored successfully
        """
        try:
            context_metadata = {
                'context_id': context_id,
                'context_type': context_type,
                'timestamp': datetime.now().isoformat(),
                'type': 'context',
                **(metadata or {})
            }
            
            self.vector_db.add_documents(
                collection_name='contexts',
                documents=[context_data],
                metadatas=[context_metadata],
                ids=[context_id]
            )
            
            logger.info(f"Stored context snapshot {context_id[:8]}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store context: {e}")
            return False
    
    def store_agent_output(
        self,
        output_id: str,
        agent_name: str,
        output_content: str,
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store agent execution output.
        
        Args:
            output_id: Unique output identifier
            agent_name: Agent that produced the output
            output_content: Output content
            task_id: Associated task ID
            metadata: Additional metadata
            
        Returns:
            True if stored successfully
        """
        try:
            output_metadata = {
                'output_id': output_id,
                'agent_name': agent_name,
                'task_id': task_id or 'unknown',
                'timestamp': datetime.now().isoformat(),
                'type': 'agent_output',
                **(metadata or {})
            }
            
            self.vector_db.add_documents(
                collection_name='agent_outputs',
                documents=[output_content],
                metadatas=[output_metadata],
                ids=[output_id]
            )
            
            logger.info(f"Stored agent output {output_id[:8]}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store agent output: {e}")
            return False
    
    def store_file_reference(
        self,
        file_path: str,
        content_summary: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a reference to a file for context retrieval.
        
        Args:
            file_path: Path to the file
            content_summary: Summary of file content
            metadata: Additional metadata
            
        Returns:
            True if stored successfully
        """
        try:
            ref_id = str(uuid.uuid4())
            ref_metadata = {
                'file_path': file_path,
                'timestamp': datetime.now().isoformat(),
                'type': 'file_reference',
                **(metadata or {})
            }
            
            self.vector_db.add_documents(
                collection_name='file_references',
                documents=[content_summary],
                metadatas=[ref_metadata],
                ids=[ref_id]
            )
            
            logger.debug(f"Stored file reference for {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store file reference: {e}")
            return False
    
    # ========================================================================
    # Convenience API Methods (for backward compatibility and simpler usage)
    # ========================================================================
    
    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        collection: str = 'messages'
    ) -> bool:
        """
        Add a document to the vector database.
        
        This is a convenience method for direct document addition without
        going through the message system.
        
        Args:
            doc_id: Unique document identifier
            text: Document text content
            metadata: Document metadata
            collection: Collection to add to (default: 'messages')
            
        Returns:
            True if added successfully
        """
        try:
            doc_metadata = metadata or {}
            doc_metadata.update({
                'timestamp': datetime.now().isoformat(),
                'type': 'document'
            })
            
            self.vector_db.add_documents(
                collection_name=collection,
                documents=[text],
                metadatas=[doc_metadata],
                ids=[doc_id]
            )
            
            logger.debug(f"Added document {doc_id[:8]} to collection '{collection}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False
    
    def search(
        self,
        query: str,
        n_results: int = 10,
        collection: str = 'messages',
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for documents in the vector database.
        
        This is a convenience method that wraps semantic_search with a
        simpler interface for direct searches.
        
        Args:
            query: Search query
            n_results: Number of results to return
            collection: Collection to search in
            filter_metadata: Optional metadata filters
            
        Returns:
            Dictionary with search results (ids, documents, metadatas, distances)
        """
        try:
            where_filter = filter_metadata if filter_metadata else None
            
            results = self.vector_db.search(
                collection_name=collection,
                query=query,
                n_results=n_results,
                where=where_filter
            )
            
            logger.debug(f"Search in '{collection}' returned {len(results.get('ids', []))} results")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {'ids': [], 'documents': [], 'metadatas': [], 'distances': []}
    
    def delete_document(
        self,
        doc_id: str,
        collection: str = 'messages'
    ) -> bool:
        """
        Delete a document from the vector database.
        
        Args:
            doc_id: Document identifier to delete
            collection: Collection to delete from
            
        Returns:
            True if deleted successfully
        """
        try:
            self.vector_db.delete_documents(
                collection_name=collection,
                ids=[doc_id]
            )
            
            logger.debug(f"Deleted document {doc_id[:8]} from collection '{collection}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    def count(self, collection: str = 'messages') -> int:
        """
        Get the number of documents in a collection.
        
        Args:
            collection: Collection to count
            
        Returns:
            Number of documents in collection
        """
        try:
            return self.vector_db.get_collection_count(collection)
        except Exception as e:
            logger.error(f"Failed to get count: {e}")
            return 0
    
    # ========================================================================
    # Search Helpers
    # ========================================================================
    
    def search_tasks(
        self,
        query: str,
        agent_name: Optional[str] = None,
        status: Optional[str] = None,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for similar tasks.
        
        Args:
            query: Search query
            agent_name: Optional agent filter
            status: Optional status filter
            n_results: Number of results
            
        Returns:
            List of matching tasks
        """
        filter_metadata = {}
        if agent_name:
            filter_metadata['agent_name'] = agent_name
        if status:
            filter_metadata['status'] = status
        
        return self.semantic_search(
            query=query,
            collection='tasks',
            n_results=n_results,
            filter_metadata=filter_metadata
        )
    
    def search_contexts(
        self,
        query: str,
        context_type: Optional[str] = None,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for similar contexts.
        
        Args:
            query: Search query
            context_type: Optional context type filter
            n_results: Number of results
            
        Returns:
            List of matching contexts
        """
        filter_metadata = {}
        if context_type:
            filter_metadata['context_type'] = context_type
        
        return self.semantic_search(
            query=query,
            collection='contexts',
            n_results=n_results,
            filter_metadata=filter_metadata
        )
    
    def search_agent_outputs(
        self,
        query: str,
        agent_name: Optional[str] = None,
        task_id: Optional[str] = None,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for similar agent outputs.
        
        Args:
            query: Search query
            agent_name: Optional agent filter
            task_id: Optional task filter
            n_results: Number of results
            
        Returns:
            List of matching outputs
        """
        filter_metadata = {}
        if agent_name:
            filter_metadata['agent_name'] = agent_name
        if task_id:
            filter_metadata['task_id'] = task_id
        
        return self.semantic_search(
            query=query,
            collection='agent_outputs',
            n_results=n_results,
            filter_metadata=filter_metadata
        )
    
    def search_file_references(
        self,
        query: str,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant file references.
        
        Args:
            query: Search query
            n_results: Number of results
            
        Returns:
            List of matching file references
        """
        return self.semantic_search(
            query=query,
            collection='file_references',
            n_results=n_results
        )
    
    # ========================================================================
    # Statistics and Utilities
    # ========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory system statistics.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'sessions': len(self.sessions),
            'vector_collections': {}
        }
        
        collections = ['messages', 'tasks', 'contexts', 'agent_outputs', 'file_references']
        for collection in collections:
            try:
                count = self.vector_db.get_collection_count(collection)
                stats['vector_collections'][collection] = count
            except Exception as e:
                logger.warning(f"Could not get count for collection {collection}: {e}")
                stats['vector_collections'][collection] = 0
        
        return stats
    
    def clear_vector_memory(self, collection: Optional[str] = None) -> bool:
        """
        Clear vector database memory.
        
        Args:
            collection: Specific collection to clear (None = all)
            
        Returns:
            True if cleared successfully
        """
        try:
            if collection:
                self.vector_db.delete_collection(collection)
                self._init_collections()  # Recreate
                logger.info(f"Cleared vector collection: {collection}")
            else:
                collections = ['messages', 'tasks', 'contexts', 'agent_outputs', 'file_references']
                for coll in collections:
                    try:
                        self.vector_db.delete_collection(coll)
                    except Exception as e:
                        logger.warning(f"Could not delete collection {coll}: {e}")
                self._init_collections()
                logger.info("Cleared all vector collections")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear vector memory: {e}")
            return False


def create_vector_memory_manager(config: Optional[Dict[str, Any]] = None) -> VectorMemoryManager:
    """
    Factory function to create a VectorMemoryManager from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured VectorMemoryManager instance
    """
    config = config or {}
    
    return VectorMemoryManager(
        storage_path=Path(config.get('storage_path', './memory')) if config.get('storage_path') else None,
        vector_db_path=config.get('vector_db_path', './chroma_db'),
        default_max_context_window=config.get('max_context_window', 4096),
        auto_save=config.get('auto_save', True),
        enable_summarization=config.get('enable_summarization', True),
        llm_router=config.get('llm_router'),
        embedding_config=config.get('embedding', {})
    )



# Backward compatibility alias
VectorMemory = VectorMemoryManager
