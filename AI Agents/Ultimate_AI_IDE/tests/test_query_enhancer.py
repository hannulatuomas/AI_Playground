"""
Tests for Query Enhancer

Tests for v1.6.0 Advanced RAG features.
"""

import pytest

from src.modules.context_manager import QueryEnhancer


class TestQueryEnhancer:
    """Test query enhancer functionality."""
    
    @pytest.fixture
    def enhancer(self):
        """Create enhancer instance."""
        return QueryEnhancer()
    
    def test_enhancer_initialization(self, enhancer):
        """Test enhancer initialization."""
        assert enhancer.ai_backend is None
        assert len(enhancer.synonyms) > 0
        assert len(enhancer.patterns) > 0
    
    def test_expand_query(self, enhancer):
        """Test query expansion."""
        query = "find function to validate data"
        expansions = enhancer.expand_query(query, max_expansions=5)
        
        assert isinstance(expansions, list)
        assert len(expansions) > 0
        assert query in expansions  # Original should be included
    
    def test_add_synonyms(self, enhancer):
        """Test synonym addition."""
        query = "function to process data"
        enhanced = enhancer.add_synonyms(query)
        
        assert isinstance(enhanced, str)
        assert "function" in enhanced or "method" in enhanced
    
    def test_enhance_query(self, enhancer):
        """Test full query enhancement."""
        query = "create authentication function"
        result = enhancer.enhance_query(
            query,
            use_synonyms=True,
            use_expansion=True,
            use_llm=False
        )
        
        assert 'original' in result
        assert 'enhanced' in result
        assert 'expansions' in result
        assert 'reformulations' in result
        assert result['original'] == query
    
    def test_detect_intent(self, enhancer):
        """Test intent detection."""
        # Implementation intent
        assert enhancer.detect_intent("how to implement login") == "implementation"
        assert enhancer.detect_intent("create a function") == "implementation"
        
        # Debugging intent
        assert enhancer.detect_intent("fix this bug") == "debugging"
        assert enhancer.detect_intent("error in code") == "debugging"
        
        # Explanation intent
        assert enhancer.detect_intent("what does this do") == "explanation"
        assert enhancer.detect_intent("explain the algorithm") == "explanation"
        
        # Optimization intent
        assert enhancer.detect_intent("optimize performance") == "optimization"
        assert enhancer.detect_intent("make it faster") == "optimization"
        
        # Testing intent
        assert enhancer.detect_intent("test the function") == "testing"
        assert enhancer.detect_intent("verify the output") == "testing"
        
        # Refactoring intent
        assert enhancer.detect_intent("refactor this code") == "refactoring"
        assert enhancer.detect_intent("cleanup the structure") == "refactoring"
    
    def test_suggest_filters(self, enhancer):
        """Test filter suggestions."""
        # Python query
        filters = enhancer.suggest_filters("python function for data processing")
        assert 'python' in filters['languages']
        
        # JavaScript query
        filters = enhancer.suggest_filters("javascript react component")
        assert 'javascript' in filters['languages']
        
        # Test file query
        filters = enhancer.suggest_filters("unittest for authentication")
        assert 'test' in filters['file_types']
        
        # Documentation query
        filters = enhancer.suggest_filters("readme documentation")
        assert 'documentation' in filters['file_types']
        
        # CRUD pattern
        filters = enhancer.suggest_filters("create and update records")
        assert 'crud' in filters['patterns']
    
    def test_get_related_terms(self, enhancer):
        """Test related term retrieval."""
        related = enhancer.get_related_terms("function")
        assert isinstance(related, list)
        assert len(related) > 0
        assert any(term in ['method', 'procedure', 'routine'] for term in related)
        
        related = enhancer.get_related_terms("error")
        assert any(term in ['exception', 'bug', 'issue'] for term in related)
    
    def test_add_custom_synonym(self, enhancer):
        """Test custom synonym addition."""
        enhancer.add_custom_synonym("myterm", ["synonym1", "synonym2"])
        assert "myterm" in enhancer.synonyms
        assert enhancer.synonyms["myterm"] == ["synonym1", "synonym2"]
    
    def test_get_statistics(self, enhancer):
        """Test statistics retrieval."""
        stats = enhancer.get_statistics()
        assert 'synonym_groups' in stats
        assert 'total_synonyms' in stats
        assert 'pattern_groups' in stats
        assert 'total_patterns' in stats
        assert stats['synonym_groups'] > 0
        assert stats['total_synonyms'] > 0
    
    def test_extract_terms(self, enhancer):
        """Test term extraction."""
        query = "find the authentication function in the database module"
        terms = enhancer._extract_terms(query)
        
        assert isinstance(terms, list)
        assert 'find' in terms
        assert 'authentication' in terms
        assert 'function' in terms
        assert 'database' in terms
        assert 'module' in terms
        # Stopwords should be filtered
        assert 'the' not in terms
        assert 'in' not in terms


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
