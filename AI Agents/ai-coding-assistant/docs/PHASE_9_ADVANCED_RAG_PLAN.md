# Phase 9: Advanced RAG Features Implementation Plan

## Overview
Implement 5 advanced RAG features to significantly improve code retrieval quality and user experience.

**Version**: 1.9.0  
**Estimated Effort**: Large (15-20 implementation units)  
**Priority**: High

---

## Features to Implement

### 1. Fine-tuned Embeddings on Code
**Goal**: Better code understanding through domain-specific embeddings

**Approach**:
- Use CodeBERT or similar pre-trained code model
- Fine-tune on our codebase patterns
- Support multiple embedding models with fallback

**Benefits**:
- 40-60% better code similarity detection
- Understanding of code semantics vs just text
- Language-specific nuances captured

### 2. Multi-modal: Code + Documentation
**Goal**: Retrieve based on both code and its documentation

**Approach**:
- Separate embeddings for code and docstrings/comments
- Weighted combination of scores
- Cross-modal retrieval (query code, get docs)

**Benefits**:
- Better context understanding
- Find relevant examples with explanations
- Improved learning from codebase

### 3. Graph-based Retrieval
**Goal**: Leverage code structure and relationships

**Approach**:
- Build AST-based call graph
- Find related functions/classes
- Graph traversal for context expansion

**Benefits**:
- Find dependencies automatically
- Understand code flow
- Better context for LLM

### 4. Query Expansion
**Goal**: Improve retrieval recall through query variations

**Approach**:
- Synonym expansion (function → method)
- Language-specific expansions (authenticate → auth, login)
- LLM-based query reformulation

**Benefits**:
- 20-30% better recall
- Handle terminology variations
- More flexible search

### 5. User Feedback Learning
**Goal**: Continuously improve through user interactions

**Approach**:
- Track click-through rates on results
- Learn from corrections/selections
- Adjust ranking based on feedback

**Benefits**:
- Personalized results
- Adaptive to codebase
- Continuous improvement

---

## Implementation Order

### Phase 9.1: Foundation (Days 1-3)
1. Multi-modal infrastructure
2. Feedback collection system
3. Query expansion basics

### Phase 9.2: Code Understanding (Days 4-7)
1. CodeBERT integration
2. Fine-tuning pipeline
3. Multi-modal retrieval

### Phase 9.3: Graph & Learning (Days 8-12)
1. AST graph builder
2. Graph-based retrieval
3. Feedback learning system

### Phase 9.4: Integration & Testing (Days 13-15)
1. Integrate all features
2. Comprehensive testing
3. Performance optimization

---

## Architecture

```
Query Input
    ↓
Query Expansion → [synonyms, reformulations]
    ↓
Multi-modal Encoding
    ├─→ Code Embeddings (CodeBERT)
    └─→ Doc Embeddings (MiniLM)
    ↓
Vector Search (ChromaDB)
    ↓
Graph Expansion
    ├─→ Find related functions
    └─→ Add context
    ↓
Re-ranking
    ├─→ Feedback learning
    └─→ Personalization
    ↓
Final Results
```

---

## File Structure

```
src/features/
├── rag_advanced/
│   ├── __init__.py
│   ├── code_embeddings.py      # CodeBERT integration
│   ├── multimodal.py            # Code + doc retrieval
│   ├── graph_retrieval.py       # AST graph-based
│   ├── query_expansion.py       # Query variations
│   └── feedback_learning.py     # User feedback
├── rag_indexer.py               # Extended for multi-modal
└── rag_retriever.py             # Extended with new features
```

---

## Detailed Implementation

### Feature 1: Fine-tuned Embeddings on Code

**File**: `src/features/rag_advanced/code_embeddings.py`

**Key Components**:
1. CodeBERT model loader
2. Fine-tuning utilities
3. Fallback to general embeddings

**API**:
```python
class CodeEmbedder:
    def __init__(self, model_name='microsoft/codebert-base'):
        """Load pre-trained code model."""
        
    def embed_code(self, code: str, language: str) -> np.ndarray:
        """Embed code with language-specific handling."""
        
    def fine_tune(self, training_data: List[Dict], epochs: int = 3):
        """Fine-tune on project-specific code."""
```

### Feature 2: Multi-modal: Code + Documentation

**File**: `src/features/rag_advanced/multimodal.py`

**Key Components**:
1. Separate code and doc embeddings
2. Score combination strategies
3. Cross-modal search

**API**:
```python
class MultiModalRetriever:
    def __init__(self, code_embedder, doc_embedder):
        """Initialize with separate embedders."""
        
    def index_multimodal(self, code: str, docs: str, metadata: Dict):
        """Index code and documentation separately."""
        
    def retrieve_multimodal(
        self,
        query: str,
        mode: str = 'hybrid',  # 'code', 'docs', 'hybrid'
        code_weight: float = 0.6
    ) -> List[Dict]:
        """Retrieve using multi-modal search."""
```

### Feature 3: Graph-based Retrieval

**File**: `src/features/rag_advanced/graph_retrieval.py`

**Key Components**:
1. AST-based call graph builder
2. Graph traversal algorithms
3. Context expansion

**API**:
```python
class CodeGraphRetriever:
    def __init__(self, project_root: str):
        """Build code graph for project."""
        
    def build_graph(self):
        """Extract AST and build call graph."""
        
    def expand_context(
        self,
        node_ids: List[str],
        depth: int = 2,
        include_callers: bool = True,
        include_callees: bool = True
    ) -> List[Dict]:
        """Expand context using graph traversal."""
        
    def find_related(self, function_name: str) -> List[str]:
        """Find related functions/classes."""
```

### Feature 4: Query Expansion

**File**: `src/features/rag_advanced/query_expansion.py`

**Key Components**:
1. Synonym dictionary
2. Language-specific expansions
3. LLM-based reformulation

**API**:
```python
class QueryExpander:
    def __init__(self, llm_interface=None):
        """Initialize with optional LLM."""
        
    def expand_query(
        self,
        query: str,
        language: Optional[str] = None,
        max_expansions: int = 3
    ) -> List[str]:
        """Generate query variations."""
        
    def get_synonyms(self, term: str) -> List[str]:
        """Get synonyms for programming terms."""
        
    def reformulate_with_llm(self, query: str) -> List[str]:
        """Use LLM to reformulate query."""
```

### Feature 5: User Feedback Learning

**File**: `src/features/rag_advanced/feedback_learning.py`

**Key Components**:
1. Feedback collection
2. Click-through rate tracking
3. Ranking adjustment

**API**:
```python
class FeedbackLearner:
    def __init__(self, learning_db):
        """Initialize with learning database."""
        
    def record_feedback(
        self,
        query: str,
        result_id: str,
        feedback_type: str,  # 'click', 'useful', 'not_useful'
        rank: int
    ):
        """Record user feedback."""
        
    def get_query_history(self, query: str) -> Dict:
        """Get historical performance for query."""
        
    def adjust_ranking(
        self,
        results: List[Dict],
        query: str
    ) -> List[Dict]:
        """Re-rank based on feedback."""
        
    def get_personalization(self, user_id: str = None) -> Dict:
        """Get personalized ranking factors."""
```

---

## Integration Plan

### Update RAGIndexer

**Changes**:
```python
class RAGIndexer:
    def __init__(
        self,
        embedding_model='all-MiniLM-L6-v2',
        use_code_embeddings=False,  # NEW
        use_multimodal=False,        # NEW
        ...
    ):
        if use_code_embeddings:
            from features.rag_advanced import CodeEmbedder
            self.code_embedder = CodeEmbedder()
        
        if use_multimodal:
            from features.rag_advanced import MultiModalRetriever
            self.multimodal = MultiModalRetriever(...)
```

### Update RAGRetriever

**Changes**:
```python
class RAGRetriever:
    def retrieve(
        self,
        query: str,
        use_query_expansion=False,    # NEW
        use_graph_context=False,      # NEW
        use_feedback_ranking=False,   # NEW
        ...
    ) -> List[Dict]:
        
        # Query expansion
        queries = [query]
        if use_query_expansion:
            queries = self.query_expander.expand_query(query)
        
        # Retrieve from all queries
        all_results = []
        for q in queries:
            results = self._vector_search(q)
            all_results.extend(results)
        
        # Graph expansion
        if use_graph_context:
            all_results = self.graph_retriever.expand_context(all_results)
        
        # Feedback-based re-ranking
        if use_feedback_ranking:
            all_results = self.feedback_learner.adjust_ranking(all_results, query)
        
        return all_results
```

---

## Database Schema Extensions

### Feedback Table
```sql
CREATE TABLE rag_feedback (
    id INTEGER PRIMARY KEY,
    query TEXT NOT NULL,
    result_id TEXT NOT NULL,
    feedback_type TEXT NOT NULL,  -- 'click', 'useful', 'not_useful'
    rank INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT
);

CREATE INDEX idx_feedback_query ON rag_feedback(query);
CREATE INDEX idx_feedback_result ON rag_feedback(result_id);
```

### Multi-modal Metadata
```sql
CREATE TABLE multimodal_chunks (
    id INTEGER PRIMARY KEY,
    chunk_id TEXT NOT NULL,
    code_embedding BLOB,
    doc_embedding BLOB,
    has_docstring BOOLEAN,
    doc_quality_score REAL
);
```

---

## Configuration

**config/rag_advanced.json**:
```json
{
  "code_embeddings": {
    "enabled": true,
    "model": "microsoft/codebert-base",
    "fallback_to_general": true
  },
  "multimodal": {
    "enabled": true,
    "code_weight": 0.6,
    "doc_weight": 0.4,
    "separate_collections": false
  },
  "graph_retrieval": {
    "enabled": true,
    "max_depth": 2,
    "include_callers": true,
    "include_callees": true
  },
  "query_expansion": {
    "enabled": true,
    "max_expansions": 3,
    "use_llm": true,
    "use_synonyms": true
  },
  "feedback_learning": {
    "enabled": true,
    "learning_rate": 0.1,
    "min_feedback_count": 3
  }
}
```

---

## Testing Strategy

### Unit Tests
- Test each feature independently
- Mock external dependencies
- Test edge cases

### Integration Tests
- Test feature combinations
- Test with real codebase
- Performance benchmarks

### User Testing
- A/B testing with/without features
- Measure retrieval quality metrics
- Gather user feedback

---

## Success Metrics

### Quantitative
- **Retrieval Quality**: +30% MRR (Mean Reciprocal Rank)
- **Query Coverage**: +40% recall
- **User Satisfaction**: +25% positive feedback
- **Performance**: < 500ms query time

### Qualitative
- Better code understanding
- More relevant results
- Improved user experience
- Continuous improvement

---

## Rollout Plan

### Week 1: Foundation
- Implement query expansion
- Implement feedback collection
- Basic testing

### Week 2: Code Understanding
- Integrate CodeBERT
- Multi-modal indexing
- Quality testing

### Week 3: Graph & Learning
- Graph builder
- Feedback learning
- Integration testing

### Week 4: Polish & Deploy
- Performance optimization
- Documentation
- User training

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| CodeBERT memory usage | High | Lazy loading, model quantization |
| Graph building slow | Medium | Incremental updates, caching |
| Feedback bias | Medium | Normalize by query frequency |
| Feature complexity | High | Modular design, feature flags |

---

**Status**: 📋 Ready for Implementation  
**Priority**: High  
**Dependencies**: Phase 8 (RAG) complete ✅

---

## Next Steps

1. Review and approve plan
2. Implement Phase 9.1 (Foundation)
3. Test each feature incrementally
4. Deploy with feature flags
5. Monitor and iterate
