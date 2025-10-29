"""
Tests for ContextPruner module
"""

import pytest
import time
import tempfile
from pathlib import Path
from src.modules.context_pruner import ContextPruner, ContextItem, ContextBudget


@pytest.fixture
def pruner():
    """Create a ContextPruner instance."""
    return ContextPruner()


@pytest.fixture
def pruner_with_items():
    """Create a ContextPruner with some items."""
    pruner = ContextPruner(ContextBudget(max_tokens=2000, reserved_tokens=100))
    
    # Add various items
    pruner.add_context(ContextItem(
        id='item1',
        content='This is a test item',
        type='code',
        timestamp=time.time(),
        token_count=50,
        relevance_score=0.8,
        priority=2
    ))
    
    pruner.add_context(ContextItem(
        id='item2',
        content='Another test item',
        type='documentation',
        timestamp=time.time() - 3600,  # 1 hour old
        token_count=100,
        relevance_score=0.3,
        priority=1
    ))
    
    pruner.add_context(ContextItem(
        id='item3',
        content='Critical item',
        type='code',
        timestamp=time.time(),
        token_count=75,
        relevance_score=0.9,
        priority=4
    ))
    
    return pruner


class TestContextPruner:
    """Test ContextPruner functionality."""
    
    def test_init(self):
        """Test ContextPruner initialization."""
        pruner = ContextPruner()
        assert pruner.budget.max_tokens == 8000
        assert pruner.current_tokens == 0
        assert len(pruner.context_items) == 0
    
    def test_init_with_custom_budget(self):
        """Test initialization with custom budget."""
        budget = ContextBudget(max_tokens=5000, reserved_tokens=500)
        pruner = ContextPruner(budget)
        
        assert pruner.budget.max_tokens == 5000
        assert pruner.budget.reserved_tokens == 500
    
    def test_add_context(self, pruner):
        """Test adding context items."""
        item = ContextItem(
            id='test1',
            content='Test content',
            type='code',
            timestamp=time.time(),
            token_count=100
        )
        
        result = pruner.add_context(item)
        
        assert result is True
        assert len(pruner.context_items) == 1
        assert pruner.current_tokens == 100
    
    def test_add_context_exceeds_budget(self, pruner):
        """Test adding context that exceeds budget."""
        # Fill up the budget
        large_item = ContextItem(
            id='large',
            content='Large content',
            type='code',
            timestamp=time.time(),
            token_count=9000  # Exceeds default budget
        )
        
        result = pruner.add_context(large_item)
        
        # Should fail or trigger auto-pruning
        assert isinstance(result, bool)
    
    def test_remove_context(self, pruner_with_items):
        """Test removing context items."""
        initial_count = len(pruner_with_items.context_items)
        initial_tokens = pruner_with_items.current_tokens
        
        result = pruner_with_items.remove_context('item1')
        
        assert result is True
        assert len(pruner_with_items.context_items) == initial_count - 1
        assert pruner_with_items.current_tokens < initial_tokens
    
    def test_calculate_context_size(self, pruner_with_items):
        """Test context size calculation."""
        size = pruner_with_items.calculate_context_size()
        
        assert size == pruner_with_items.current_tokens
        assert size > 0
    
    def test_get_available_tokens(self, pruner_with_items):
        """Test available tokens calculation."""
        available = pruner_with_items.get_available_tokens()
        
        expected = pruner_with_items.budget.max_tokens - pruner_with_items.current_tokens - pruner_with_items.budget.reserved_tokens
        assert available == expected
    
    def test_get_usage_percentage(self, pruner_with_items):
        """Test usage percentage calculation."""
        usage = pruner_with_items.get_usage_percentage()
        
        assert 0 <= usage <= 100
        assert usage > 0  # Should have some usage
    
    def test_should_prune(self, pruner):
        """Test pruning threshold detection."""
        # Empty pruner shouldn't need pruning
        assert pruner.should_prune() is False
        
        # Fill to warning threshold
        large_item = ContextItem(
            id='large',
            content='Large',
            type='code',
            timestamp=time.time(),
            token_count=int(pruner.budget.max_tokens * 0.85)
        )
        pruner.add_context(large_item)
        
        assert pruner.should_prune() is True
    
    def test_prune_old_context(self, pruner_with_items):
        """Test pruning old context."""
        initial_count = len(pruner_with_items.context_items)
        
        # Prune items older than 0.5 hours
        pruned_count = pruner_with_items.prune_old_context(max_age_hours=0.5)
        
        assert pruned_count >= 1  # Should prune item2 (1 hour old)
        assert len(pruner_with_items.context_items) < initial_count
    
    def test_prune_by_relevance(self, pruner_with_items):
        """Test pruning by relevance score."""
        initial_count = len(pruner_with_items.context_items)
        
        # Prune items with relevance < 0.5
        pruned_count = pruner_with_items.prune_by_relevance(min_relevance=0.5)
        
        assert pruned_count >= 1  # Should prune item2 (relevance 0.3)
        assert len(pruner_with_items.context_items) < initial_count
    
    def test_auto_prune(self, pruner_with_items):
        """Test automatic pruning."""
        # Request space for new item
        result = pruner_with_items.auto_prune(tokens_needed=100)
        
        assert isinstance(result, bool)
        # Should have freed some space
        assert pruner_with_items.get_available_tokens() >= 100
    
    def test_prioritize_context(self, pruner_with_items):
        """Test context prioritization."""
        query = "test code"
        
        prioritized = pruner_with_items.prioritize_context(query)
        
        assert len(prioritized) == len(pruner_with_items.context_items)
        # Should be sorted by relevance and priority
        assert prioritized[0].relevance_score >= prioritized[-1].relevance_score
    
    def test_compress_context(self, pruner):
        """Test context compression."""
        # Add a large old item
        large_item = ContextItem(
            id='large',
            content=' '.join(['word'] * 1000),  # 1000 words
            type='code',
            timestamp=time.time() - 10000,  # Old
            token_count=1000,
            priority=1
        )
        pruner.add_context(large_item)
        
        initial_tokens = pruner.current_tokens
        tokens_saved = pruner.compress_context()
        
        assert tokens_saved >= 0
        assert pruner.current_tokens <= initial_tokens
    
    def test_select_context_for_budget(self, pruner_with_items):
        """Test selecting context within budget."""
        selected = pruner_with_items.select_context_for_budget(target_tokens=150)
        
        total_tokens = sum(item.token_count for item in selected)
        assert total_tokens <= 150 or any(item.priority >= 4 for item in selected)
    
    def test_get_statistics(self, pruner_with_items):
        """Test statistics generation."""
        stats = pruner_with_items.get_statistics()
        
        assert 'total_items' in stats
        assert 'total_tokens' in stats
        assert 'available_tokens' in stats
        assert 'usage_percentage' in stats
        assert 'items_by_type' in stats
        assert 'items_by_priority' in stats
        
        assert stats['total_items'] == len(pruner_with_items.context_items)
    
    def test_save_and_load_state(self, pruner_with_items, tmp_path):
        """Test saving and loading state."""
        save_file = tmp_path / 'context_state.json'
        
        # Save state
        pruner_with_items.save_state(str(save_file))
        assert save_file.exists()
        
        # Load state into new pruner
        new_pruner = ContextPruner()
        new_pruner.load_state(str(save_file))
        
        assert len(new_pruner.context_items) == len(pruner_with_items.context_items)
        assert new_pruner.current_tokens == pruner_with_items.current_tokens


class TestContextPrunerEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_pruner_statistics(self, pruner):
        """Test statistics on empty pruner."""
        stats = pruner.get_statistics()
        
        assert stats['total_items'] == 0
        assert stats['total_tokens'] == 0
        assert stats['usage_percentage'] >= 0
    
    def test_remove_nonexistent_item(self, pruner):
        """Test removing nonexistent item."""
        result = pruner.remove_context('nonexistent')
        
        assert result is False
    
    def test_critical_priority_always_included(self, pruner):
        """Test that critical priority items are always included."""
        critical_item = ContextItem(
            id='critical',
            content='Critical',
            type='code',
            timestamp=time.time(),
            token_count=5000,
            priority=4  # Critical
        )
        
        pruner.add_context(critical_item)
        
        # Even with small budget, critical should be selected
        selected = pruner.select_context_for_budget(target_tokens=100)
        
        assert any(item.id == 'critical' for item in selected)
    
    def test_get_context_with_dependencies(self, pruner):
        """Test getting context with dependencies."""
        item1 = ContextItem(
            id='item1',
            content='Item 1',
            type='code',
            timestamp=time.time(),
            token_count=50,
            dependencies=['item2']
        )
        
        item2 = ContextItem(
            id='item2',
            content='Item 2',
            type='code',
            timestamp=time.time(),
            token_count=50
        )
        
        pruner.add_context(item1)
        pruner.add_context(item2)
        
        items_with_deps = pruner.get_context_with_dependencies('item1')
        
        assert len(items_with_deps) == 2
        assert any(item.id == 'item1' for item in items_with_deps)
        assert any(item.id == 'item2' for item in items_with_deps)
