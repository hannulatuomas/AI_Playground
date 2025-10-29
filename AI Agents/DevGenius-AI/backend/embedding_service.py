"""
Embedding Service for Semantic Search and Context Management
Uses local sentence-transformers model and ChromaDB for vector storage
"""

from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Manages embeddings and semantic search for conversation context"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedding service with local model
        
        Args:
            model_name: Sentence-transformers model name (default: all-MiniLM-L6-v2)
                       This is a lightweight model (~80MB) good for semantic similarity
        """
        try:
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            
            # Initialize ChromaDB with new configuration
            self.chroma_client = chromadb.PersistentClient(
                path="/app/backend/chroma_db"
            )
            
            # Create or get collections
            self.conversations_collection = self.chroma_client.get_or_create_collection(
                name="conversations",
                metadata={"description": "Conversation messages for semantic search"}
            )
            
            logger.info("Embedding service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {str(e)}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            return []
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing for efficiency)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Batch embedding failed: {str(e)}")
            return []
    
    def store_message(self, conversation_id: str, message_id: str, role: str, content: str, 
                     metadata: Optional[Dict] = None):
        """
        Store a message with its embedding for later retrieval
        
        Args:
            conversation_id: ID of the conversation
            message_id: Unique message ID
            role: Message role (user/assistant)
            content: Message content
            metadata: Additional metadata (timestamp, agent_type, etc.)
        """
        try:
            if not content.strip():
                return
            
            embedding = self.embed_text(content)
            
            if not embedding:
                logger.warning(f"Failed to generate embedding for message {message_id}")
                return
            
            meta = metadata or {}
            meta.update({
                'conversation_id': conversation_id,
                'role': role,
                'timestamp': datetime.now().isoformat()
            })
            
            self.conversations_collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[meta],
                ids=[message_id]
            )
            
            logger.debug(f"Stored message {message_id} in vector database")
            
        except Exception as e:
            logger.error(f"Failed to store message: {str(e)}")
    
    def semantic_search(self, query: str, conversation_id: str, top_k: int = 5, 
                       exclude_recent: int = 3) -> List[Dict]:
        """
        Perform semantic search for relevant messages in a conversation
        
        Args:
            query: Search query (usually recent user message)
            conversation_id: ID of the conversation to search within
            top_k: Number of most similar messages to return
            exclude_recent: Number of recent messages to exclude (already in context)
            
        Returns:
            List of relevant messages with similarity scores
        """
        try:
            query_embedding = self.embed_text(query)
            
            if not query_embedding:
                return []
            
            # Search in the specific conversation
            results = self.conversations_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k + exclude_recent,  # Get extra to filter recent ones
                where={"conversation_id": conversation_id}
            )
            
            if not results['documents'] or not results['documents'][0]:
                return []
            
            # Format results
            relevant_messages = []
            for i, (doc, meta, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                # Skip if too similar (likely duplicate or very recent)
                if distance < 0.1 and i < exclude_recent:
                    continue
                
                # Convert distance to similarity score (0-1, higher is more similar)
                similarity = 1 - (distance / 2)  # Cosine distance is 0-2
                
                relevant_messages.append({
                    'content': doc,
                    'role': meta.get('role', 'unknown'),
                    'similarity': round(similarity, 3),
                    'timestamp': meta.get('timestamp'),
                    'distance': round(distance, 3)
                })
            
            # Return top_k most relevant (excluding recent duplicates)
            return relevant_messages[:top_k]
            
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            return []
    
    def detect_redundant_messages(self, messages: List[Dict], threshold: float = 0.95) -> List[int]:
        """
        Detect redundant/duplicate messages based on semantic similarity
        
        Args:
            messages: List of message dicts with 'content' field
            threshold: Similarity threshold (0-1, higher is more strict)
            
        Returns:
            List of indices of redundant messages to remove
        """
        try:
            if len(messages) < 2:
                return []
            
            # Extract content and generate embeddings
            contents = [msg['content'] for msg in messages]
            embeddings = self.embed_batch(contents)
            
            if not embeddings or len(embeddings) != len(messages):
                return []
            
            # Convert to numpy for efficient computation
            embeddings_np = np.array(embeddings)
            
            # Compute cosine similarity matrix
            norms = np.linalg.norm(embeddings_np, axis=1, keepdims=True)
            normalized = embeddings_np / norms
            similarity_matrix = np.dot(normalized, normalized.T)
            
            # Find redundant messages
            redundant_indices = set()
            for i in range(len(messages)):
                if i in redundant_indices:
                    continue
                for j in range(i + 1, len(messages)):
                    if j in redundant_indices:
                        continue
                    if similarity_matrix[i, j] >= threshold:
                        # Keep first occurrence, mark second as redundant
                        redundant_indices.add(j)
                        logger.debug(f"Redundant message detected: {j} similar to {i} "
                                   f"(similarity: {similarity_matrix[i, j]:.3f})")
            
            return sorted(list(redundant_indices))
            
        except Exception as e:
            logger.error(f"Redundancy detection failed: {str(e)}")
            return []
    
    def get_smart_context(self, conversation_id: str, recent_messages: List[Dict], 
                         current_message: str, max_context_messages: int = 8) -> List[Dict]:
        """
        Get smart context combining recent messages and semantically similar past messages
        
        Args:
            conversation_id: ID of the conversation
            recent_messages: List of recent messages (already in context)
            current_message: Current user message
            max_context_messages: Maximum messages to include in context
            
        Returns:
            Optimized list of messages for context
        """
        try:
            # Start with recent messages (already important)
            context = recent_messages.copy()
            
            # If we have room for more context, add semantically relevant messages
            remaining_slots = max_context_messages - len(context)
            
            if remaining_slots > 0:
                # Search for relevant past messages
                relevant = self.semantic_search(
                    query=current_message,
                    conversation_id=conversation_id,
                    top_k=remaining_slots,
                    exclude_recent=len(recent_messages)
                )
                
                # Add relevant messages (they come with similarity scores)
                for msg in relevant:
                    if msg['similarity'] > 0.6:  # Only add if reasonably similar
                        context.append({
                            'role': msg['role'],
                            'content': f"[Relevant context (similarity: {msg['similarity']})]\n{msg['content']}"
                        })
            
            # Remove redundant messages from context
            if len(context) > 3:
                redundant_indices = self.detect_redundant_messages(context, threshold=0.92)
                if redundant_indices:
                    logger.info(f"Removing {len(redundant_indices)} redundant messages from context")
                    context = [msg for i, msg in enumerate(context) if i not in redundant_indices]
            
            return context[:max_context_messages]
            
        except Exception as e:
            logger.error(f"Smart context generation failed: {str(e)}")
            return recent_messages  # Fallback to recent messages only

# Global instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get or create global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
