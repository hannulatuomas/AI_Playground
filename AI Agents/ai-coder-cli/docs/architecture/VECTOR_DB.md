# Vector Database Integration Guide

**Version:** 1.0.0  
**Last Updated:** October 12, 2025  
**Status:** Production Ready

This document describes the vector database integration in the AI Agent Console, using ChromaDB and nomic-embed-text embeddings for semantic search and document retrieval.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [API Reference](#api-reference)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### What is a Vector Database?

A vector database stores and retrieves data based on semantic similarity rather than exact matches. It uses embeddings (numerical vector representations) to enable:

- **Semantic Search**: Find content by meaning, not just keywords
- **Code Search**: Discover similar code snippets
- **Documentation Retrieval**: Find relevant documentation
- **Context Management**: Store and retrieve conversation history

### Technology Stack

- **ChromaDB**: Open-source vector database with persistent storage
- **nomic-embed-text**: Ollama embedding model optimized for text
- **Ollama**: Local LLM and embedding model runtime

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent Console                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────┐        ┌──────────────────┐            │
│  │   Agents      │◄──────►│  Vector DB API   │            │
│  └───────────────┘        └────────┬─────────┘            │
│                                    │                        │
│  ┌───────────────┐        ┌────────▼─────────┐            │
│  │  Embeddings   │◄──────►│   ChromaVectorDB │            │
│  │  (nomic)      │        └────────┬─────────┘            │
│  └───────────────┘                 │                       │
│         ▲                          │                       │
│         │                          ▼                       │
│  ┌──────┴──────┐         ┌────────────────┐              │
│  │   Ollama    │         │  Persistent    │              │
│  │   Server    │         │  Storage       │              │
│  └─────────────┘         └────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Classes

1. **EmbeddingGenerator** (`tools/embeddings.py`)
   - Generates embeddings using Ollama
   - Handles batch processing
   - Provides similarity calculations

2. **ChromaVectorDB** (`tools/vector_db.py`)
   - Manages collections and documents
   - Performs semantic search
   - Handles persistence

---

## Installation

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# This installs:
# - chromadb>=0.4.20
# - ollama (already included)
```

### 2. Install Ollama Embedding Model

```bash
# Pull the nomic-embed-text model
ollama pull nomic-embed-text:latest

# Verify installation
ollama list | grep nomic-embed-text
```

### 3. Verify Ollama is Running

```bash
# Check Ollama server status
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve
```

---

## Configuration

### config.yaml Settings

The vector database is configured in `config.yaml`:

```yaml
vector_db:
  enabled: true
  provider: "chromadb"
  persist_directory: "./data/chroma_db"
  
  embedding:
    model: "nomic-embed-text:latest"
    host: "http://localhost:11434"
    timeout: 120
    normalize: true
  
  collections:
    code_snippets:
      auto_create: true
      metadata:
        description: "Code snippets and examples"
    
    documentation:
      auto_create: true
      metadata:
        description: "Project and API documentation"
  
  search:
    default_n_results: 10
    similarity_metric: "cosine"
    min_similarity: 0.5
  
  performance:
    batch_size: 32
    cache_embeddings: true
    max_cache_size: 1000
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | bool | `true` | Enable/disable vector DB |
| `persist_directory` | str | `"./data/chroma_db"` | Storage location |
| `embedding.model` | str | `"nomic-embed-text:latest"` | Embedding model |
| `embedding.host` | str | `"http://localhost:11434"` | Ollama server URL |
| `embedding.normalize` | bool | `true` | Normalize embeddings |
| `search.default_n_results` | int | `10` | Default search results |
| `search.similarity_metric` | str | `"cosine"` | Similarity metric |
| `search.min_similarity` | float | `0.5` | Minimum similarity threshold |

---

## Usage Examples

### Basic Example

```python
from tools.vector_db import create_vector_db

# Initialize vector database
db = create_vector_db()

# Add documents
db.add_documents(
    collection_name="code_snippets",
    documents=[
        "def hello_world():\n    print('Hello, World!')",
        "function greet(name) {\n    return `Hello, ${name}!`;\n}",
        "public void sayHello() {\n    System.out.println(\"Hello\");\n}"
    ],
    metadatas=[
        {"language": "python", "type": "function"},
        {"language": "javascript", "type": "function"},
        {"language": "java", "type": "method"}
    ],
    ids=["py_hello", "js_greet", "java_hello"]
)

# Semantic search
results = db.search(
    collection_name="code_snippets",
    query="how to print hello in python",
    n_results=5
)

# Access results
for i, doc in enumerate(results['documents']):
    metadata = results['metadatas'][i]
    distance = results['distances'][i]
    print(f"Match {i+1} ({metadata['language']}): {distance:.3f}")
    print(doc)
    print()
```

### Advanced Search with Filters

```python
# Search with metadata filters
results = db.search(
    collection_name="code_snippets",
    query="async function",
    n_results=10,
    where={"language": "javascript"}  # Only JavaScript
)

# Search with document content filters
results = db.search(
    collection_name="code_snippets",
    query="error handling",
    where_document={"$contains": "try"}  # Contains 'try'
)
```

### Collection Management

```python
# Create a new collection
db.create_collection(
    name="api_documentation",
    metadata={"version": "1.0", "project": "my-app"}
)

# List all collections
collections = db.list_collections()
print(f"Collections: {collections}")

# Get document count
count = db.get_collection_count("code_snippets")
print(f"Documents in collection: {count}")

# Delete a collection
db.delete_collection("old_collection")
```

### Update and Delete Documents

```python
# Update document
db.update_documents(
    collection_name="code_snippets",
    ids=["py_hello"],
    documents=["def hello_world(name='World'):\n    print(f'Hello, {name}!')"],
    metadatas=[{"language": "python", "type": "function", "updated": True}]
)

# Delete specific documents
db.delete_documents(
    collection_name="code_snippets",
    ids=["old_snippet_1", "old_snippet_2"]
)

# Delete documents by metadata filter
db.delete_documents(
    collection_name="code_snippets",
    where={"language": "deprecated"}
)
```

### Batch Operations

```python
# Add many documents efficiently
documents = [f"Code snippet {i}" for i in range(1000)]
metadatas = [{"index": i} for i in range(1000)]

ids = db.add_documents(
    collection_name="code_snippets",
    documents=documents,
    metadatas=metadatas
)

print(f"Added {len(ids)} documents")
```

### Retrieve Documents

```python
# Get specific documents by ID
docs = db.get_documents(
    collection_name="code_snippets",
    ids=["py_hello", "js_greet"]
)

# Get documents by metadata filter
docs = db.get_documents(
    collection_name="code_snippets",
    where={"language": "python"},
    limit=10
)

# Get all documents (use with caution)
all_docs = db.get_documents(
    collection_name="code_snippets"
)
```

---

## API Reference

### EmbeddingGenerator

#### `__init__(model, host, timeout)`

Initialize the embedding generator.

```python
from tools.embeddings import EmbeddingGenerator

generator = EmbeddingGenerator(
    model="nomic-embed-text:latest",
    host="http://localhost:11434",
    timeout=120
)
```

#### `generate(text, normalize=True)`

Generate embeddings for text.

```python
# Single text
embedding = generator.generate("Hello, world!")

# Multiple texts
embeddings = generator.generate([
    "First text",
    "Second text"
])
```

#### `generate_batch(texts, normalize=True, batch_size=32)`

Generate embeddings in batches.

```python
texts = ["text" + str(i) for i in range(1000)]
embeddings = generator.generate_batch(texts, batch_size=50)
```

#### `similarity(embedding1, embedding2, metric="cosine")`

Calculate similarity between embeddings.

```python
emb1 = generator.generate("Python programming")
emb2 = generator.generate("JavaScript development")

similarity = generator.similarity(emb1, emb2)
print(f"Similarity: {similarity:.3f}")
```

### ChromaVectorDB

#### `__init__(persist_directory, embedding_generator, embedding_config)`

Initialize vector database.

```python
from tools.vector_db import ChromaVectorDB

db = ChromaVectorDB(
    persist_directory="./my_db",
    embedding_config={
        "model": "nomic-embed-text:latest",
        "host": "http://localhost:11434"
    }
)
```

#### `add_documents(collection_name, documents, metadatas, ids)`

Add documents to collection.

```python
ids = db.add_documents(
    collection_name="my_collection",
    documents=["doc1", "doc2"],
    metadatas=[{"key": "value1"}, {"key": "value2"}]
)
```

#### `search(collection_name, query, n_results, where, where_document)`

Search for similar documents.

```python
results = db.search(
    collection_name="my_collection",
    query="search query",
    n_results=5,
    where={"key": "value"}
)
```

#### Other Methods

- `create_collection(name, metadata, get_or_create)`
- `delete_collection(name)`
- `list_collections()`
- `get_documents(collection_name, ids, where, limit)`
- `update_documents(collection_name, ids, documents, metadatas)`
- `delete_documents(collection_name, ids, where)`
- `get_collection_count(collection_name)`
- `reset()` - ⚠️ Deletes all collections

---

## Best Practices

### 1. Collection Design

```python
# ✅ GOOD: Organize by domain
db.create_collection("python_code")
db.create_collection("javascript_code")
db.create_collection("documentation")

# ❌ BAD: One collection for everything
db.create_collection("all_data")
```

### 2. Metadata Usage

```python
# ✅ GOOD: Rich metadata for filtering
metadata = {
    "language": "python",
    "type": "function",
    "author": "john",
    "created": "2025-10-12",
    "tags": ["async", "api"]
}

# ❌ BAD: Minimal or no metadata
metadata = {}
```

### 3. Document Chunking

```python
# ✅ GOOD: Chunk large documents
def chunk_document(text, max_length=500):
    chunks = []
    for i in range(0, len(text), max_length):
        chunks.append(text[i:i+max_length])
    return chunks

# ❌ BAD: Store entire large files
db.add_documents(["entire 10MB file content"])
```

### 4. Error Handling

```python
# ✅ GOOD: Handle errors gracefully
try:
    results = db.search("collection", "query")
except ValueError as e:
    print(f"Collection not found: {e}")
except Exception as e:
    print(f"Search failed: {e}")

# ❌ BAD: No error handling
results = db.search("collection", "query")
```

### 5. Batch Operations

```python
# ✅ GOOD: Use batch operations
db.add_documents(collection, documents, metadatas)

# ❌ BAD: Add one at a time
for doc in documents:
    db.add_documents(collection, [doc], [metadata])
```

---

## Troubleshooting

### Issue: "Embedding model not found"

**Solution:**
```bash
# Pull the embedding model
ollama pull nomic-embed-text:latest

# Verify
ollama list | grep nomic
```

### Issue: "Ollama connection refused"

**Solution:**
```bash
# Start Ollama server
ollama serve

# Or check if running
ps aux | grep ollama
```

### Issue: "Collection already exists"

**Solution:**
```python
# Use get_or_create=True
db.create_collection("my_collection", get_or_create=True)

# Or delete and recreate
db.delete_collection("my_collection")
db.create_collection("my_collection")
```

### Issue: "Slow embedding generation"

**Solutions:**

1. Use batch operations:
```python
# Instead of this:
for doc in documents:
    embedding = generator.generate(doc)

# Do this:
embeddings = generator.generate_batch(documents)
```

2. Reduce batch size:
```python
embeddings = generator.generate_batch(documents, batch_size=16)
```

3. Check Ollama performance:
```bash
# Monitor Ollama
htop

# Check GPU usage (if available)
nvidia-smi
```

### Issue: "High memory usage"

**Solutions:**

1. Process in smaller batches
2. Limit cache size in config
3. Use document chunking
4. Periodically clear old data

---

## Performance Tuning

### Optimization Tips

1. **Batch Size**: Adjust based on available memory
   ```yaml
   performance:
     batch_size: 32  # Increase if you have more RAM
   ```

2. **Caching**: Enable for repeated searches
   ```yaml
   performance:
     cache_embeddings: true
     max_cache_size: 1000
   ```

3. **Normalization**: Enable for cosine similarity
   ```yaml
   embedding:
     normalize: true  # Better for cosine similarity
   ```

4. **Collection Design**: Separate collections for different domains
   - Faster searches within specific domains
   - Better organization
   - Easier maintenance

---

## Integration Examples

### With Code Search Agent

```python
from tools.vector_db import create_vector_db

class CodeSearchAgent:
    def __init__(self):
        self.db = create_vector_db()
    
    def index_codebase(self, directory):
        """Index all code files in directory."""
        code_files = find_code_files(directory)
        
        documents = []
        metadatas = []
        ids = []
        
        for file_path in code_files:
            with open(file_path) as f:
                content = f.read()
            
            documents.append(content)
            metadatas.append({
                "file_path": str(file_path),
                "language": detect_language(file_path),
                "size": len(content)
            })
            ids.append(str(file_path))
        
        self.db.add_documents(
            collection_name="codebase",
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def find_similar_code(self, query, language=None):
        """Find similar code snippets."""
        where = {"language": language} if language else None
        
        results = self.db.search(
            collection_name="codebase",
            query=query,
            n_results=10,
            where=where
        )
        
        return results
```

### With Documentation Agent

```python
class DocumentationAgent:
    def __init__(self):
        self.db = create_vector_db()
    
    def add_documentation(self, doc_text, metadata):
        """Add documentation with metadata."""
        self.db.add_documents(
            collection_name="documentation",
            documents=[doc_text],
            metadatas=[metadata]
        )
    
    def answer_question(self, question):
        """Answer question using documentation."""
        # Search for relevant documentation
        results = self.db.search(
            collection_name="documentation",
            query=question,
            n_results=5
        )
        
        # Build context from top results
        context = "\n\n".join(results['documents'])
        
        # Generate answer using LLM with context
        answer = self.generate_answer(question, context)
        
        return answer
```

---

## Next Steps

1. **Experiment**: Try different embedding models
2. **Tune**: Adjust configuration for your use case
3. **Monitor**: Track search performance and relevance
4. **Extend**: Build custom agents using vector DB
5. **Scale**: Consider distributed setups for large datasets

---

## References

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Ollama Models](https://ollama.ai/library)
- [nomic-embed-text](https://ollama.ai/library/nomic-embed-text)
- [Vector Embeddings Guide](https://www.pinecone.io/learn/vector-embeddings/)

---

**Version:** 1.0.0  
**Last Updated:** October 12, 2025  
**Maintained by:** AI Agent Console Development Team
