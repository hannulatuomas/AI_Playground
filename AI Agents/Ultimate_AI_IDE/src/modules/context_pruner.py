"""
Context Pruner Module

Manages AI context size, prunes old context, and implements smart context selection.
Ensures efficient use of limited context windows for large codebases.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class ContextItem:
    """Represents a single context item."""
    id: str
    content: str
    type: str  # 'code', 'documentation', 'conversation', 'file'
    timestamp: float
    token_count: int
    relevance_score: float = 0.0
    priority: int = 1  # 1=low, 2=medium, 3=high, 4=critical
    file_path: Optional[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class ContextBudget:
    """Context budget configuration."""
    max_tokens: int = 8000
    reserved_tokens: int = 1000  # Reserved for system prompts
    warning_threshold: float = 0.8  # Warn at 80% usage
    critical_threshold: float = 0.95  # Critical at 95% usage


class ContextPruner:
    """Manages and prunes AI context to stay within token limits."""
    
    def __init__(self, budget: Optional[ContextBudget] = None):
        """
        Initialize context pruner.
        
        Args:
            budget: Context budget configuration
        """
        self.budget = budget or ContextBudget()
        self.context_items: List[ContextItem] = []
        self.pruned_items: List[ContextItem] = []
        self.current_tokens = 0
    
    def add_context(self, item: ContextItem) -> bool:
        """
        Add context item.
        
        Args:
            item: Context item to add
            
        Returns:
            True if added successfully
        """
        # Check if adding would exceed budget
        available = self.get_available_tokens()
        
        if item.token_count > available:
            logger.warning(f"Cannot add context item: would exceed budget by {item.token_count - available} tokens")
            
            # Try to make space
            if self.auto_prune(item.token_count):
                # Retry after pruning
                available = self.get_available_tokens()
                if item.token_count <= available:
                    self._add_item(item)
                    return True
            
            return False
        
        self._add_item(item)
        return True
    
    def _add_item(self, item: ContextItem):
        """Internal method to add item."""
        self.context_items.append(item)
        self.current_tokens += item.token_count
        logger.debug(f"Added context item: {item.id} ({item.token_count} tokens)")
    
    def remove_context(self, item_id: str) -> bool:
        """
        Remove context item by ID.
        
        Args:
            item_id: ID of item to remove
            
        Returns:
            True if removed
        """
        for i, item in enumerate(self.context_items):
            if item.id == item_id:
                removed = self.context_items.pop(i)
                self.current_tokens -= removed.token_count
                self.pruned_items.append(removed)
                logger.debug(f"Removed context item: {item_id}")
                return True
        
        return False
    
    def calculate_context_size(self) -> int:
        """
        Calculate current context size in tokens.
        
        Returns:
            Total token count
        """
        return self.current_tokens
    
    def get_available_tokens(self) -> int:
        """
        Get available token budget.
        
        Returns:
            Available tokens
        """
        used = self.current_tokens + self.budget.reserved_tokens
        return max(0, self.budget.max_tokens - used)
    
    def get_usage_percentage(self) -> float:
        """
        Get context usage as percentage.
        
        Returns:
            Usage percentage (0-100)
        """
        used = self.current_tokens + self.budget.reserved_tokens
        return (used / self.budget.max_tokens) * 100
    
    def should_prune(self) -> bool:
        """
        Check if pruning is needed.
        
        Returns:
            True if should prune
        """
        usage = self.get_usage_percentage()
        return usage >= (self.budget.warning_threshold * 100)
    
    def is_critical(self) -> bool:
        """
        Check if context usage is critical.
        
        Returns:
            True if critical
        """
        usage = self.get_usage_percentage()
        return usage >= (self.budget.critical_threshold * 100)
    
    def prune_old_context(self, max_age_hours: float = 24.0) -> int:
        """
        Prune context items older than specified age.
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of items pruned
        """
        cutoff_time = time.time() - (max_age_hours * 3600)
        pruned_count = 0
        
        # Keep items newer than cutoff or with high priority
        items_to_keep = []
        for item in self.context_items:
            if item.timestamp > cutoff_time or item.priority >= 3:
                items_to_keep.append(item)
            else:
                self.pruned_items.append(item)
                self.current_tokens -= item.token_count
                pruned_count += 1
        
        self.context_items = items_to_keep
        logger.info(f"Pruned {pruned_count} old context items")
        
        return pruned_count
    
    def prune_by_relevance(self, min_relevance: float = 0.3) -> int:
        """
        Prune context items below relevance threshold.
        
        Args:
            min_relevance: Minimum relevance score (0-1)
            
        Returns:
            Number of items pruned
        """
        pruned_count = 0
        
        items_to_keep = []
        for item in self.context_items:
            # Keep high priority items regardless of relevance
            if item.priority >= 3 or item.relevance_score >= min_relevance:
                items_to_keep.append(item)
            else:
                self.pruned_items.append(item)
                self.current_tokens -= item.token_count
                pruned_count += 1
        
        self.context_items = items_to_keep
        logger.info(f"Pruned {pruned_count} low-relevance context items")
        
        return pruned_count
    
    def auto_prune(self, tokens_needed: int = 0) -> bool:
        """
        Automatically prune context to make space.
        
        Args:
            tokens_needed: Additional tokens needed
            
        Returns:
            True if enough space was freed
        """
        target_tokens = tokens_needed if tokens_needed > 0 else int(self.budget.max_tokens * 0.2)
        
        logger.info(f"Auto-pruning to free {target_tokens} tokens")
        
        # Strategy 1: Remove old items
        self.prune_old_context(max_age_hours=12.0)
        
        if self.get_available_tokens() >= target_tokens:
            return True
        
        # Strategy 2: Remove low relevance items
        self.prune_by_relevance(min_relevance=0.5)
        
        if self.get_available_tokens() >= target_tokens:
            return True
        
        # Strategy 3: Remove lowest priority items
        self._prune_by_priority(target_tokens)
        
        return self.get_available_tokens() >= target_tokens
    
    def _prune_by_priority(self, tokens_needed: int):
        """Prune lowest priority items until target is met."""
        # Sort by priority (ascending) and timestamp (oldest first)
        sorted_items = sorted(
            self.context_items,
            key=lambda x: (x.priority, x.timestamp)
        )
        
        freed_tokens = 0
        items_to_keep = []
        
        for item in sorted_items:
            if freed_tokens >= tokens_needed and item.priority >= 2:
                items_to_keep.append(item)
            else:
                self.pruned_items.append(item)
                self.current_tokens -= item.token_count
                freed_tokens += item.token_count
        
        self.context_items = items_to_keep
        logger.info(f"Pruned by priority: freed {freed_tokens} tokens")
    
    def prioritize_context(self, query: str) -> List[ContextItem]:
        """
        Prioritize and select most relevant context for a query.
        
        Args:
            query: Query string
            
        Returns:
            Prioritized list of context items
        """
        # Update relevance scores based on query
        for item in self.context_items:
            item.relevance_score = self._calculate_relevance(item, query)
        
        # Sort by relevance (descending) and priority (descending)
        sorted_items = sorted(
            self.context_items,
            key=lambda x: (x.relevance_score, x.priority),
            reverse=True
        )
        
        return sorted_items
    
    def _calculate_relevance(self, item: ContextItem, query: str) -> float:
        """
        Calculate relevance score for context item.
        
        Args:
            item: Context item
            query: Query string
            
        Returns:
            Relevance score (0-1)
        """
        query_lower = query.lower()
        content_lower = item.content.lower()
        
        # Simple keyword matching (can be enhanced with embeddings)
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())
        
        if not query_words:
            return 0.5
        
        # Calculate word overlap
        overlap = len(query_words & content_words)
        relevance = overlap / len(query_words)
        
        # Boost for file path matches
        if item.file_path and any(word in item.file_path.lower() for word in query_words):
            relevance += 0.2
        
        # Boost for recent items
        age_hours = (time.time() - item.timestamp) / 3600
        if age_hours < 1:
            relevance += 0.1
        
        return min(1.0, relevance)
    
    def compress_context(self) -> int:
        """
        Compress context by summarizing old items.
        
        Returns:
            Tokens saved
        """
        tokens_saved = 0
        compressed_items = []
        
        cutoff_time = time.time() - (6 * 3600)  # 6 hours
        
        for item in self.context_items:
            if item.timestamp < cutoff_time and item.priority < 3 and item.token_count > 500:
                # Compress long old items
                summary = self._summarize_content(item.content)
                tokens_saved += item.token_count - len(summary.split())
                
                compressed_item = ContextItem(
                    id=f"{item.id}_compressed",
                    content=summary,
                    type=f"{item.type}_summary",
                    timestamp=item.timestamp,
                    token_count=len(summary.split()),
                    relevance_score=item.relevance_score,
                    priority=item.priority,
                    file_path=item.file_path,
                    dependencies=item.dependencies
                )
                compressed_items.append(compressed_item)
            else:
                compressed_items.append(item)
        
        self.context_items = compressed_items
        self.current_tokens -= tokens_saved
        
        logger.info(f"Compressed context: saved {tokens_saved} tokens")
        return tokens_saved
    
    def _summarize_content(self, content: str, max_length: int = 200) -> str:
        """
        Summarize content to reduce token count.
        
        Args:
            content: Content to summarize
            max_length: Maximum summary length in words
            
        Returns:
            Summarized content
        """
        # Simple summarization: take first and last parts
        words = content.split()
        
        if len(words) <= max_length:
            return content
        
        # Take first 60% and last 40% of max_length
        first_part = int(max_length * 0.6)
        last_part = max_length - first_part
        
        summary = ' '.join(words[:first_part]) + ' [...] ' + ' '.join(words[-last_part:])
        return summary
    
    def select_context_for_budget(self, target_tokens: int) -> List[ContextItem]:
        """
        Select best context items within token budget.
        
        Args:
            target_tokens: Target token count
            
        Returns:
            Selected context items
        """
        # Sort by priority and relevance
        sorted_items = sorted(
            self.context_items,
            key=lambda x: (x.priority, x.relevance_score),
            reverse=True
        )
        
        selected = []
        total_tokens = 0
        
        for item in sorted_items:
            if total_tokens + item.token_count <= target_tokens:
                selected.append(item)
                total_tokens += item.token_count
            elif item.priority >= 4:  # Always include critical items
                selected.append(item)
                total_tokens += item.token_count
        
        logger.info(f"Selected {len(selected)} items ({total_tokens} tokens) from {len(self.context_items)} available")
        
        return selected
    
    def get_context_with_dependencies(self, item_id: str) -> List[ContextItem]:
        """
        Get context item with all its dependencies.
        
        Args:
            item_id: ID of context item
            
        Returns:
            List of items including dependencies
        """
        items = []
        visited = set()
        
        def collect_dependencies(id: str):
            if id in visited:
                return
            
            visited.add(id)
            
            for item in self.context_items:
                if item.id == id:
                    items.append(item)
                    for dep_id in item.dependencies:
                        collect_dependencies(dep_id)
                    break
        
        collect_dependencies(item_id)
        return items
    
    def save_state(self, file_path: str):
        """
        Save context state to file.
        
        Args:
            file_path: Path to save file
        """
        state = {
            'budget': asdict(self.budget),
            'context_items': [asdict(item) for item in self.context_items],
            'pruned_items': [asdict(item) for item in self.pruned_items],
            'current_tokens': self.current_tokens,
            'timestamp': time.time()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Saved context state to {file_path}")
    
    def load_state(self, file_path: str):
        """
        Load context state from file.
        
        Args:
            file_path: Path to load file
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        self.budget = ContextBudget(**state['budget'])
        self.context_items = [ContextItem(**item) for item in state['context_items']]
        self.pruned_items = [ContextItem(**item) for item in state['pruned_items']]
        self.current_tokens = state['current_tokens']
        
        logger.info(f"Loaded context state from {file_path}")
    
    def get_statistics(self) -> Dict:
        """
        Get context statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'total_items': len(self.context_items),
            'total_tokens': self.current_tokens,
            'available_tokens': self.get_available_tokens(),
            'usage_percentage': round(self.get_usage_percentage(), 2),
            'pruned_items': len(self.pruned_items),
            'items_by_type': self._count_by_type(),
            'items_by_priority': self._count_by_priority(),
            'average_relevance': self._calculate_average_relevance(),
            'oldest_item_age_hours': self._get_oldest_item_age(),
            'should_prune': self.should_prune(),
            'is_critical': self.is_critical()
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count items by type."""
        counts = {}
        for item in self.context_items:
            counts[item.type] = counts.get(item.type, 0) + 1
        return counts
    
    def _count_by_priority(self) -> Dict[int, int]:
        """Count items by priority."""
        counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for item in self.context_items:
            counts[item.priority] = counts.get(item.priority, 0) + 1
        return counts
    
    def _calculate_average_relevance(self) -> float:
        """Calculate average relevance score."""
        if not self.context_items:
            return 0.0
        
        total = sum(item.relevance_score for item in self.context_items)
        return round(total / len(self.context_items), 3)
    
    def _get_oldest_item_age(self) -> float:
        """Get age of oldest item in hours."""
        if not self.context_items:
            return 0.0
        
        oldest = min(item.timestamp for item in self.context_items)
        age_seconds = time.time() - oldest
        return round(age_seconds / 3600, 2)
