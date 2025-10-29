"""
Agent Memory and Self-Improvement System
Tracks errors, resolutions, user preferences, and builds agent knowledge base
"""

from typing import Dict, List, Optional
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import os

logger = logging.getLogger(__name__)

class AgentMemory:
    """Manages agent learning, error tracking, and knowledge base"""
    
    def __init__(self, db):
        """
        Initialize agent memory system
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.memory_collection = db.agent_memory
        self.preferences_collection = db.user_preferences
        logger.info("Agent memory system initialized")
    
    async def store_error_resolution(self, agent_type: str, error_pattern: str, 
                                     resolution: str, conversation_id: str,
                                     success: bool = True, metadata: Optional[Dict] = None):
        """
        Store an error pattern and its resolution for learning
        
        Args:
            agent_type: Type of agent (programming, website, etc.)
            error_pattern: Description or pattern of the error
            resolution: How it was resolved
            conversation_id: ID of the conversation where this occurred
            success: Whether the resolution was successful
            metadata: Additional context (error message, stack trace, etc.)
        """
        try:
            memory_entry = {
                "type": "error_resolution",
                "agent_type": agent_type,
                "error_pattern": error_pattern,
                "resolution": resolution,
                "conversation_id": conversation_id,
                "success": success,
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc).isoformat(),
                "times_encountered": 1,
                "times_resolved": 1 if success else 0
            }
            
            # Check if similar error exists
            existing = await self.memory_collection.find_one({
                "type": "error_resolution",
                "agent_type": agent_type,
                "error_pattern": error_pattern
            })
            
            if existing:
                # Update existing entry
                await self.memory_collection.update_one(
                    {"_id": existing["_id"]},
                    {"$inc": {
                        "times_encountered": 1,
                        "times_resolved": 1 if success else 0
                    },
                     "$set": {
                        "last_encountered": datetime.now(timezone.utc).isoformat(),
                        "latest_resolution": resolution
                    }}
                )
                logger.info(f"Updated existing error pattern for {agent_type}")
            else:
                # Insert new entry
                await self.memory_collection.insert_one(memory_entry)
                logger.info(f"Stored new error pattern for {agent_type}")
                
        except Exception as e:
            logger.error(f"Failed to store error resolution: {str(e)}")
    
    async def get_similar_errors(self, agent_type: str, error_pattern: str, 
                                 limit: int = 5) -> List[Dict]:
        """
        Retrieve similar error patterns and their resolutions
        
        Args:
            agent_type: Type of agent
            error_pattern: Error pattern to search for
            limit: Maximum number of results
            
        Returns:
            List of similar error resolutions
        """
        try:
            # Simple keyword matching for now (can be enhanced with embeddings)
            keywords = error_pattern.lower().split()[:5]  # First 5 significant words
            
            pipeline = [
                {
                    "$match": {
                        "type": "error_resolution",
                        "agent_type": agent_type,
                        "success": True
                    }
                },
                {
                    "$addFields": {
                        "relevance_score": {
                            "$sum": [
                                1 if keyword in "$error_pattern" else 0
                                for keyword in keywords
                            ]
                        }
                    }
                },
                {"$match": {"relevance_score": {"$gt": 0}}},
                {"$sort": {"relevance_score": -1, "times_resolved": -1}},
                {"$limit": limit}
            ]
            
            results = await self.memory_collection.aggregate(pipeline).to_list(limit)
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve similar errors: {str(e)}")
            return []
    
    async def store_conversation_outcome(self, conversation_id: str, agent_type: str,
                                        outcome: str, user_feedback: Optional[str] = None,
                                        metrics: Optional[Dict] = None):
        """
        Store conversation outcome for learning
        
        Args:
            conversation_id: ID of the conversation
            agent_type: Type of agent used
            outcome: Outcome classification (success, partial_success, failure, abandoned)
            user_feedback: Optional user feedback
            metrics: Optional metrics (response time, turns, etc.)
        """
        try:
            outcome_entry = {
                "type": "conversation_outcome",
                "conversation_id": conversation_id,
                "agent_type": agent_type,
                "outcome": outcome,
                "user_feedback": user_feedback,
                "metrics": metrics or {},
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await self.memory_collection.insert_one(outcome_entry)
            logger.info(f"Stored conversation outcome for {agent_type}: {outcome}")
            
        except Exception as e:
            logger.error(f"Failed to store conversation outcome: {str(e)}")
    
    async def learn_user_preference(self, user_id: str, preference_type: str,
                                   preference_value: any, context: Optional[Dict] = None):
        """
        Learn and store user preferences
        
        Args:
            user_id: User identifier (can be session-based or account-based)
            preference_type: Type of preference (code_style, verbosity, framework, etc.)
            preference_value: The preference value
            context: Additional context about when this preference was learned
        """
        try:
            preference_entry = {
                "user_id": user_id,
                "preference_type": preference_type,
                "preference_value": preference_value,
                "context": context or {},
                "learned_at": datetime.now(timezone.utc).isoformat(),
                "confidence": 1,  # Can be updated based on reinforcement
                "times_observed": 1
            }
            
            # Check if preference exists
            existing = await self.preferences_collection.find_one({
                "user_id": user_id,
                "preference_type": preference_type
            })
            
            if existing:
                # Update existing preference
                await self.preferences_collection.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        "preference_value": preference_value,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    },
                     "$inc": {"times_observed": 1}}
                )
                logger.info(f"Updated user preference: {preference_type}")
            else:
                # Insert new preference
                await self.preferences_collection.insert_one(preference_entry)
                logger.info(f"Learned new user preference: {preference_type}")
                
        except Exception as e:
            logger.error(f"Failed to learn user preference: {str(e)}")
    
    async def get_user_preferences(self, user_id: str, 
                                   preference_types: Optional[List[str]] = None) -> Dict:
        """
        Retrieve user preferences
        
        Args:
            user_id: User identifier
            preference_types: Optional list of specific preference types to retrieve
            
        Returns:
            Dictionary of preferences
        """
        try:
            query = {"user_id": user_id}
            if preference_types:
                query["preference_type"] = {"$in": preference_types}
            
            preferences = await self.preferences_collection.find(query).to_list(100)
            
            # Convert to simple dict
            prefs_dict = {}
            for pref in preferences:
                prefs_dict[pref["preference_type"]] = pref["preference_value"]
            
            return prefs_dict
            
        except Exception as e:
            logger.error(f"Failed to retrieve user preferences: {str(e)}")
            return {}
    
    async def add_to_knowledge_base(self, agent_type: str, category: str,
                                   title: str, content: str, tags: List[str],
                                   source: Optional[str] = None):
        """
        Add entry to agent knowledge base
        
        Args:
            agent_type: Type of agent
            category: Category of knowledge (best_practice, pattern, tip, etc.)
            title: Title of the knowledge entry
            content: Detailed content
            tags: List of tags for easy retrieval
            source: Source of knowledge (conversation_id, documentation, etc.)
        """
        try:
            kb_entry = {
                "type": "knowledge_base",
                "agent_type": agent_type,
                "category": category,
                "title": title,
                "content": content,
                "tags": tags,
                "source": source,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "usefulness_score": 1.0,  # Can be updated based on usage
                "times_used": 0
            }
            
            await self.memory_collection.insert_one(kb_entry)
            logger.info(f"Added knowledge base entry for {agent_type}: {title}")
            
        except Exception as e:
            logger.error(f"Failed to add knowledge base entry: {str(e)}")
    
    async def search_knowledge_base(self, agent_type: str, query_tags: List[str],
                                   category: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """
        Search agent knowledge base
        
        Args:
            agent_type: Type of agent
            query_tags: Tags to search for
            category: Optional category filter
            limit: Maximum results
            
        Returns:
            List of matching knowledge base entries
        """
        try:
            match_query = {
                "type": "knowledge_base",
                "agent_type": agent_type,
                "tags": {"$in": query_tags}
            }
            
            if category:
                match_query["category"] = category
            
            results = await self.memory_collection.find(match_query)\
                                                  .sort("usefulness_score", -1)\
                                                  .limit(limit)\
                                                  .to_list(limit)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search knowledge base: {str(e)}")
            return []
    
    async def get_agent_performance_stats(self, agent_type: str) -> Dict:
        """
        Get performance statistics for an agent
        
        Args:
            agent_type: Type of agent
            
        Returns:
            Dictionary with performance metrics
        """
        try:
            # Get conversation outcomes
            outcomes = await self.memory_collection.find({
                "type": "conversation_outcome",
                "agent_type": agent_type
            }).to_list(1000)
            
            # Get error resolutions
            errors = await self.memory_collection.find({
                "type": "error_resolution",
                "agent_type": agent_type
            }).to_list(1000)
            
            # Calculate statistics
            total_conversations = len(outcomes)
            success_count = sum(1 for o in outcomes if o["outcome"] == "success")
            
            total_errors = sum(e.get("times_encountered", 0) for e in errors)
            resolved_errors = sum(e.get("times_resolved", 0) for e in errors)
            
            stats = {
                "agent_type": agent_type,
                "total_conversations": total_conversations,
                "success_rate": round(success_count / total_conversations, 2) if total_conversations > 0 else 0,
                "total_errors_encountered": total_errors,
                "error_resolution_rate": round(resolved_errors / total_errors, 2) if total_errors > 0 else 0,
                "knowledge_base_entries": await self.memory_collection.count_documents({
                    "type": "knowledge_base",
                    "agent_type": agent_type
                })
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get performance stats: {str(e)}")
            return {}
    
    async def append_learning_to_summary(self, conversation_id: str, 
                                        learnings: List[str]) -> str:
        """
        Append learnings to conversation summary
        
        Args:
            conversation_id: ID of the conversation
            learnings: List of learning points
            
        Returns:
            Updated summary text
        """
        try:
            if not learnings:
                return ""
            
            learning_text = "\n\nLEARNINGS FROM THIS CONVERSATION:\n" + "\n".join(
                f"- {learning}" for learning in learnings
            )
            
            return learning_text
            
        except Exception as e:
            logger.error(f"Failed to append learnings to summary: {str(e)}")
            return ""

# Global instance
_agent_memory = None

async def get_agent_memory(db) -> AgentMemory:
    """Get or create global agent memory instance"""
    global _agent_memory
    if _agent_memory is None:
        _agent_memory = AgentMemory(db)
    return _agent_memory
