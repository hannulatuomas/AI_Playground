# Phase 9 - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Verify Installation
```bash
# Check if features are available
cd ai-coding-assistant
python -c "from features.rag_advanced import QueryExpander, FeedbackLearner, CodeGraphRetriever; print('✓ All features available!')"
```

### Step 2: Run Tests
```bash
# Windows
run_advanced_rag_tests.bat

# Linux/Mac
python tests/test_rag_advanced.py
```

Expected output:
```
test_basic_expansion ... ok
test_record_feedback ... ok
test_build_graph ... ok
...
Ran 17 tests in 2.5s
OK
```

### Step 3: Try Query Expansion
Create `test_query_expansion.py`:

```python
from features.rag_advanced import QueryExpander

# Initialize
expander = QueryExpander()

# Expand a query
query = "JWT authentication function"
expansions = expander.expand_query(query, language="python", max_expansions=5)

print(f"Original query: {query}")
print(f"\nExpanded to {len(expansions)} variations:")
for i, expansion in enumerate(expansions, 1):
    print(f"  {i}. {expansion}")
```

Run it:
```bash
python test_query_expansion.py
```

Expected output:
```
Original query: JWT authentication function

Expanded to 5 variations:
  1. JWT authentication function
  2. JSON Web Token authentication function
  3. JWT auth function
  4. JWT authentication def
  5. token authentication function
```

### Step 4: Try Feedback Learning
Create `test_feedback.py`:

```python
from features.rag_advanced import FeedbackLearner

# Initialize
learner = FeedbackLearner(db_path="test_feedback.db")

# Simulate user interactions
print("Recording feedback...")

# User searches and clicks result at rank 2
learner.record_feedback(
    query="user authentication",
    result_id="auth.py:login:15",
    feedback_type="click",
    rank=2,
    score=0.75
)

# User marks it as useful
learner.record_feedback(
    query="user authentication",
    result_id="auth.py:login:15",
    feedback_type="useful",
    rank=2
)

# Check result quality
quality = learner.get_result_quality("auth.py:login:15", "user authentication")
print(f"\nResult quality score: {quality['quality_score']:.2f}")
print(f"Useful count: {quality['useful_count']}")

# Simulate ranking adjustment
mock_results = [
    {'chunk_id': 'auth.py:login:15', 'score': 0.70},
    {'chunk_id': 'token.py:verify:10', 'score': 0.85}
]

adjusted = learner.adjust_ranking(mock_results, "user authentication")

print("\nRanking adjustment:")
for r in adjusted:
    print(f"  {r['chunk_id']}: {r['score']:.3f} (was {r.get('original_score', r['score']):.3f})")
```

Run it:
```bash
python test_feedback.py
```

Expected output:
```
Recording feedback...

Result quality score: 0.75
Useful count: 1

Ranking adjustment:
  auth.py:login:15: 0.775 (was 0.700)
  token.py:verify:10: 0.850 (was 0.850)
```

### Step 5: Try Graph Retrieval
Create `test_graph.py`:

```python
from features.rag_advanced import CodeGraphRetriever
from pathlib import Path

# Create a test project
test_dir = Path("test_project")
test_dir.mkdir(exist_ok=True)

# Create test files
(test_dir / "auth.py").write_text('''
def login(username, password):
    """User login function."""
    return authenticate(username, password)

def authenticate(username, password):
    """Authenticate credentials."""
    return verify_password(username, password)

def verify_password(username, password):
    """Verify password hash."""
    return True
''')

# Build graph
print("Building call graph...")
graph = CodeGraphRetriever(project_root=test_dir)
stats = graph.build_graph()

print(f"\nGraph statistics:")
print(f"  Total nodes: {stats['total_nodes']}")
print(f"  Functions: {stats['functions']}")
print(f"  Files: {stats['files']}")

# Find related functions
if 'login' in graph.node_lookup:
    print(f"\nFinding functions related to 'login':")
    related = graph.find_related('login')
    for node in related[:5]:
        print(f"  - {node['name']} ({node['file']}) at depth {node['depth']}")

# Cleanup
import shutil
shutil.rmtree(test_dir)
```

Run it:
```bash
python test_graph.py
```

Expected output:
```
Building call graph...

Graph statistics:
  Total nodes: 3
  Functions: 3
  Files: 1

Finding functions related to 'login':
  - login (auth.py) at depth 0
  - authenticate (auth.py) at depth 1
  - verify_password (auth.py) at depth 2
```

---

## 🎯 Common Use Cases

### Use Case 1: Improve Search Recall
```python
from features.rag_advanced import QueryExpander

expander = QueryExpander()

# User searches for "config file"
variations = expander.expand_query("config file", max_expansions=3)
# Returns: ['config file', 'configuration file', 'settings file']

# Search with all variations for better recall
```

### Use Case 2: Learn from User Behavior
```python
from features.rag_advanced import FeedbackLearner

learner = FeedbackLearner()

# Track which results users find useful
# Over time, better results rank higher automatically
```

### Use Case 3: Find Related Code
```python
from features.rag_advanced import CodeGraphRetriever

graph = CodeGraphRetriever(project_root="./my_project")
graph.build_graph()

# User views authenticate() function
# Show related functions automatically
related = graph.find_related("authenticate")
```

---

## 📊 Monitoring Performance

Create `monitor_performance.py`:

```python
import time
from features.rag_advanced import QueryExpander, FeedbackLearner

# Test query expansion performance
expander = QueryExpander()

queries = ["JWT auth", "database connection", "user login", "API endpoint"]
start = time.time()
for query in queries:
    expander.expand_query(query)
elapsed = time.time() - start

print(f"Query expansion: {elapsed*1000:.1f}ms for {len(queries)} queries")
print(f"Average: {elapsed*1000/len(queries):.1f}ms per query")

# Test feedback learning performance
learner = FeedbackLearner(db_path=":memory:")  # In-memory for speed

start = time.time()
for i in range(100):
    learner.record_feedback(
        query=f"query_{i}",
        result_id=f"result_{i}",
        feedback_type="click",
        rank=1
    )
elapsed = time.time() - start

print(f"\nFeedback recording: {elapsed*1000:.1f}ms for 100 records")
print(f"Average: {elapsed*1000/100:.1f}ms per record")
```

Expected output:
```
Query expansion: 25.3ms for 4 queries
Average: 6.3ms per query

Feedback recording: 150.2ms for 100 records
Average: 1.5ms per record
```

---

## 🔧 Troubleshooting

### Problem: Import errors
```python
# Solution: Check Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
```

### Problem: Database locked
```python
# Solution: Use different database or timeout
learner = FeedbackLearner(db_path="data/learning.db")
# Or use in-memory for testing
learner = FeedbackLearner(db_path=":memory:")
```

### Problem: No query expansions
```python
# Solution: Check query has known terms
synonyms = expander.get_synonyms('function')
print(f"Known synonyms: {synonyms}")
# Add custom terms if needed
```

---

## 📚 Next Steps

1. **Integrate with existing RAG**
   - See integration example in PHASE_9_SUMMARY.md
   - Start with query expansion only
   - Add feedback learning gradually
   - Enable graph retrieval when needed

2. **Customize for your codebase**
   - Add domain-specific synonyms
   - Adjust learning rate
   - Configure graph depth

3. **Monitor and optimize**
   - Track query performance
   - Analyze feedback patterns
   - Tune parameters

4. **Explore advanced features**
   - Try LLM-based query reformulation
   - Experiment with graph visualization
   - Export feedback for analysis

---

## ✅ Checklist

- [ ] Run tests successfully
- [ ] Try query expansion
- [ ] Try feedback learning
- [ ] Try graph retrieval
- [ ] Read full documentation
- [ ] Plan integration
- [ ] Configure for your needs

---

## 🤝 Getting Help

- **Documentation**: `src/features/rag_advanced/README.md`
- **Examples**: `tests/test_rag_advanced.py`
- **Architecture**: `docs/PHASE_9_ADVANCED_RAG_PLAN.md`
- **Summary**: `PHASE_9_SUMMARY.md`

Happy coding! 🎉
