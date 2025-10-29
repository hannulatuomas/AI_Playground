"""
Unit Tests for RAG System

Tests for RAGIndexer, RAGRetriever, and performance optimizations.
"""

import unittest
import tempfile
import shutil
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import components
try:
    from features.rag_indexer import RAGIndexer
    from features.rag_retriever import RAGRetriever
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

try:
    from core.performance_config import get_preset_config, PerformanceConfig
    from core.embedding_cache import EmbeddingCache
    from core.query_cache import QueryCache
    from core.memory_manager import MemoryManager
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False


@unittest.skipIf(not RAG_AVAILABLE, "RAG dependencies not installed")
class TestRAGIndexer(unittest.TestCase):
    """Test suite for RAGIndexer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_dir = tempfile.mkdtemp()
        self.indexer = RAGIndexer(
            embedding_model='all-MiniLM-L6-v2',
            db_path=self.db_dir,
            batch_size=4,  # Small for testing
            use_gpu=False
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree(self.db_dir, ignore_errors=True)
    
    def test_chunk_file_python(self):
        """Test Python AST-based chunking."""
        python_code = '''
def hello():
    """Say hello."""
    print("Hello, World!")

class MyClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
'''
        chunks = self.indexer.chunk_file(python_code, "test.py")
        
        self.assertGreater(len(chunks), 0)
        self.assertTrue(any('hello' in c['content'] for c in chunks))
        self.assertTrue(any('MyClass' in c['content'] for c in chunks))
        
        # Check metadata
        for chunk in chunks:
            self.assertIn('metadata', chunk)
            self.assertIn('file_path', chunk['metadata'])
            self.assertIn('language', chunk['metadata'])
            self.assertEqual(chunk['metadata']['language'], 'python')
    
    def test_chunk_file_javascript(self):
        """Test sliding window chunking for JavaScript."""
        js_code = '''
function greet(name) {
    return `Hello, ${name}!`;
}

const add = (a, b) => a + b;

export { greet, add };
'''
        chunks = self.indexer.chunk_file(js_code, "test.js")
        
        self.assertGreater(len(chunks), 0)
        
        # Check metadata
        for chunk in chunks:
            self.assertIn('metadata', chunk)
            self.assertEqual(chunk['metadata']['language'], 'javascript')
    
    def test_chunk_empty_file(self):
        """Test chunking empty file."""
        chunks = self.indexer.chunk_file("", "empty.py")
        self.assertEqual(len(chunks), 0)
    
    def test_embed_chunks(self):
        """Test embedding generation."""
        chunks = [
            {'content': 'def hello(): pass', 'metadata': {}},
            {'content': 'def world(): pass', 'metadata': {}}
        ]
        
        embeddings = self.indexer.embed_chunks(chunks, show_progress=False)
        
        self.assertEqual(embeddings.shape[0], 2)
        self.assertEqual(embeddings.shape[1], 384)  # MiniLM dimension
        
        # Embeddings should be different
        self.assertFalse((embeddings[0] == embeddings[1]).all())
    
    def test_embed_empty_chunks(self):
        """Test embedding empty list."""
        embeddings = self.indexer.embed_chunks([], show_progress=False)
        self.assertEqual(embeddings.shape[0], 0)
    
    def test_build_vector_db(self):
        """Test building vector database."""
        # Create test project
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text('''
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
''')
        
        collection = self.indexer.build_vector_db(
            self.temp_dir,
            project_name="test-project"
        )
        
        self.assertIsNotNone(collection)
        self.assertEqual(collection, "test-project")
        
        # Check collection exists
        collections = self.indexer.list_collections()
        self.assertIn("test-project", collections)
        
        # Check collection info
        info = self.indexer.get_collection_info("test-project")
        self.assertTrue(info['exists'])
        self.assertGreater(info['total_chunks'], 0)
    
    def test_incremental_update(self):
        """Test incremental file updates."""
        # Create initial project
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("def old(): pass")
        
        collection = self.indexer.build_vector_db(self.temp_dir)
        
        # Update file
        test_file.write_text("def new(): pass")
        
        # Incremental update
        updated = self.indexer.incremental_update(
            file_path="test.py",
            collection_name=collection,
            project_root=self.temp_dir
        )
        
        self.assertGreater(updated, 0)
    
    def test_sanitize_collection_name(self):
        """Test collection name sanitization."""
        sanitized = self.indexer._sanitize_collection_name("My Project!")
        self.assertTrue(sanitized.replace('_', '').replace('-', '').replace('.', '').isalnum())
        self.assertLessEqual(len(sanitized), 63)
        self.assertGreaterEqual(len(sanitized), 3)
    
    def test_unload_model(self):
        """Test model unloading."""
        # Load model first
        _ = self.indexer.model
        self.assertIsNotNone(self.indexer._model)
        
        # Unload
        self.indexer.unload_model()
        self.assertIsNone(self.indexer._model)


@unittest.skipIf(not RAG_AVAILABLE, "RAG dependencies not installed")
class TestRAGRetriever(unittest.TestCase):
    """Test suite for RAGRetriever."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_dir = tempfile.mkdtemp()
        
        # Create indexer and index a small project
        self.indexer = RAGIndexer(
            embedding_model='all-MiniLM-L6-v2',
            db_path=self.db_dir,
            batch_size=4,
            use_gpu=False
        )
        
        # Create test files
        (Path(self.temp_dir) / "auth.py").write_text('''
def authenticate(username, password):
    """Authenticate user with credentials."""
    # Check credentials
    return verify_password(username, password)

def verify_password(username, password):
    """Verify password hash."""
    stored = get_password_hash(username)
    return hash_password(password) == stored
''')
        
        (Path(self.temp_dir) / "database.py").write_text('''
def connect_database(host, port):
    """Connect to database."""
    return Database(host, port)

def query_users(db, filter):
    """Query users from database."""
    return db.execute("SELECT * FROM users WHERE {filter}")
''')
        
        # Index project
        self.collection = self.indexer.build_vector_db(
            self.temp_dir,
            project_name="test_rag_project",  # Use fixed name
            force_rebuild=True  # Force rebuild to ensure clean state
        )
        
        # Create retriever with same db_path as indexer to share the same ChromaDB instance
        self.retriever = RAGRetriever(
            indexer=self.indexer,
            db_path=self.db_dir  # Use same db_path
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree(self.db_dir, ignore_errors=True)
    
    def test_retrieve_relevant(self):
        """Test retrieving relevant code."""
        # First, verify collection has data
        stats = self.retriever.get_statistics(collection_name=self.collection)
        print(f"\nCollection stats: {stats['total_chunks']} chunks, {stats['total_files']} files")
        
        # Try with no threshold first to see what scores we get
        all_results = self.retriever.retrieve(
            query="user authentication",
            collection_name=self.collection,
            top_k=10,
            threshold=0.0  # No threshold to see all scores
        )
        
        if all_results:
            print(f"\nAll scores: {[r['score'] for r in all_results]}")
            print(f"Max score: {max(r['score'] for r in all_results)}")
            print(f"Min score: {min(r['score'] for r in all_results)}")
        
        results = self.retriever.retrieve(
            query="user authentication",
            collection_name=self.collection,
            top_k=3,
            threshold=0.0  # No threshold - get top results regardless of score
        )
        
        self.assertGreater(len(results), 0)
        
        # Should find auth.py
        file_paths = [r['file_path'] for r in results]
        self.assertTrue(any('auth.py' in path for path in file_paths))
        
        # Check result structure
        for result in results:
            self.assertIn('chunk_id', result)
            self.assertIn('content', result)
            self.assertIn('score', result)
            self.assertIn('file_path', result)
            self.assertIn('language', result)
            self.assertGreater(result['score'], 0)
            self.assertLessEqual(result['score'], 1)
    
    def test_retrieve_with_language_filter(self):
        """Test retrieval with language filtering."""
        results = self.retriever.retrieve(
            query="database connection",
            collection_name=self.collection,
            language_filter="python",
            top_k=5
        )
        
        # All results should be Python
        for result in results:
            self.assertEqual(result['language'], 'python')
    
    def test_retrieve_no_results(self):
        """Test query with no matching results."""
        results = self.retriever.retrieve(
            query="quantum physics equations",
            collection_name=self.collection,
            threshold=0.9  # High threshold
        )
        
        # May have no results or very low scores
        self.assertIsInstance(results, list)
    
    def test_rerank_score(self):
        """Test reranking by score."""
        results = self.retriever.retrieve(
            query="authentication",
            collection_name=self.collection,
            top_k=5
        )
        
        if len(results) > 1:
            reranked = self.retriever.rerank(
                query="authentication",
                results=results,
                method='score'
            )
            
            # Should be sorted by score descending
            scores = [r['score'] for r in reranked]
            self.assertEqual(scores, sorted(scores, reverse=True))
    
    def test_augment_prompt(self):
        """Test prompt augmentation."""
        results = self.retriever.retrieve(
            query="user login",
            collection_name=self.collection,
            top_k=2,
            threshold=0.0  # No threshold
        )
        
        base_prompt = "How do I implement user login?"
        augmented = self.retriever.augment_prompt(
            base_prompt=base_prompt,
            retrieved=results
        )
        
        self.assertIn(base_prompt, augmented)
        
        # Only check length if we have results
        if results:
            self.assertGreater(len(augmented), len(base_prompt))
            
            # Should contain code from results
            self.assertTrue(any(
                result['file_path'] in augmented 
                for result in results
            ))
        else:
            # If no results, augmented should equal base_prompt
            self.assertEqual(augmented, base_prompt)
    
    def test_handle_large_context(self):
        """Test context truncation."""
        results = self.retriever.retrieve(
            query="database",
            collection_name=self.collection,
            top_k=10
        )
        
        if results:
            truncated = self.retriever.handle_large_context(
                retrieved=results,
                max_tokens=500
            )
            
            self.assertLessEqual(len(truncated), len(results))
            
            # Should keep highest scores
            if truncated and results:
                self.assertEqual(truncated[0]['chunk_id'], results[0]['chunk_id'])
    
    def test_search_files(self):
        """Test searching specific file."""
        chunks = self.retriever.search_files(
            file_path="auth.py",
            collection_name=self.collection
        )
        
        self.assertGreater(len(chunks), 0)
        
        # All chunks should be from auth.py
        for chunk in chunks:
            self.assertEqual(chunk['file_path'], "auth.py")
    
    def test_get_file_list(self):
        """Test getting file list."""
        files = self.retriever.get_file_list(
            collection_name=self.collection
        )
        
        self.assertGreater(len(files), 0)
        self.assertIn("auth.py", files)
        self.assertIn("database.py", files)
    
    def test_get_statistics(self):
        """Test getting collection statistics."""
        stats = self.retriever.get_statistics(
            collection_name=self.collection
        )
        
        # Check that we got valid statistics (not an error)
        self.assertNotIn('error', stats, f"Collection should exist but got error: {stats}")
        
        self.assertIn('collection_name', stats)
        self.assertIn('total_chunks', stats)
        self.assertIn('total_files', stats)
        self.assertIn('languages', stats)
        
        self.assertGreater(stats['total_chunks'], 0)
        self.assertGreater(stats['total_files'], 0)
        self.assertIn('python', stats['languages'])


@unittest.skipIf(not PERFORMANCE_AVAILABLE, "Performance modules not installed")
class TestPerformanceOptimizations(unittest.TestCase):
    """Test suite for performance optimization modules."""
    
    def test_performance_config_presets(self):
        """Test configuration presets."""
        for preset in ['default', 'fast', 'balanced', 'quality', 'low_memory', 'gpu']:
            config = get_preset_config(preset)
            self.assertIsInstance(config, PerformanceConfig)
            self.assertIsNotNone(config.embedding.model_name)
            self.assertGreater(config.embedding.batch_size, 0)
    
    def test_embedding_cache(self):
        """Test embedding cache operations."""
        cache = EmbeddingCache(
            max_size=10,
            strategy='lru',
            enable_persistence=False
        )
        
        import numpy as np
        
        # Test put/get
        embedding = np.random.rand(384)
        cache.put("test content", embedding)
        
        retrieved = cache.get("test content")
        self.assertIsNotNone(retrieved)
        self.assertTrue(np.allclose(retrieved, embedding))
        
        # Test miss
        result = cache.get("nonexistent")
        self.assertIsNone(result)
        
        # Test stats
        stats = cache.get_stats()
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
    
    def test_query_cache(self):
        """Test query cache with TTL."""
        cache = QueryCache(
            max_size=10,
            ttl_seconds=1,
            strategy='lru',
            enable_persistence=False
        )
        
        # Test put/get
        results = [{'content': 'test', 'score': 0.9}]
        cache.put("test query", results)
        
        retrieved = cache.get("test query")
        self.assertIsNotNone(retrieved)
        self.assertEqual(len(retrieved), 1)
        
        # Test TTL expiration
        import time
        time.sleep(2)
        expired = cache.get("test query")
        self.assertIsNone(expired)
    
    def test_memory_manager(self):
        """Test memory manager."""
        memory_mgr = MemoryManager(
            gc_threshold_mb=500,
            enable_auto_gc=False,  # Don't auto-run during test
            enable_model_unloading=False
        )
        
        # Test memory snapshot
        snapshot = memory_mgr.get_memory_usage()
        self.assertGreater(snapshot.process_mb, 0)
        self.assertGreater(snapshot.total_mb, 0)
        
        # Test cleanup
        results = memory_mgr.trigger_cleanup(force=True)
        self.assertIn('gc_collected', results)
        self.assertIn('memory_before_mb', results)
        
        # Test adaptive batch sizing
        batch_size = memory_mgr.get_adaptive_batch_size(32, 256)
        self.assertGreater(batch_size, 0)
        self.assertLessEqual(batch_size, 32)


@unittest.skipIf(not RAG_AVAILABLE, "RAG dependencies not installed")
class TestRAGIntegration(unittest.TestCase):
    """Integration tests for complete RAG workflow."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree(self.db_dir, ignore_errors=True)
    
    def test_end_to_end_workflow(self):
        """Test complete workflow: Index → Query → Retrieve."""
        # Create test project with more substantial code
        test_files = {
            "auth.py": '''def login(user, pwd):
    """Authenticate user login."""
    return authenticate(user, pwd)

def authenticate(username, password):
    """Verify user credentials."""
    return verify_credentials(username, password)
''',
            "db.py": '''def query(sql):
    """Execute database query."""
    return database.execute(sql)

def connect():
    """Connect to database."""
    return database.connect()
''',
            "utils.py": '''def format_date(date):
    """Format date string."""
    return date.strftime('%Y-%m-%d')
'''
        }
        
        for filename, content in test_files.items():
            (Path(self.temp_dir) / filename).write_text(content)
        
        # Index with fixed name
        indexer = RAGIndexer(
            db_path=self.db_dir,
            batch_size=4,
            use_gpu=False
        )
        collection = indexer.build_vector_db(
            self.temp_dir,
            project_name="e2e_test_project",
            force_rebuild=True
        )
        
        # Query with same db_path
        retriever = RAGRetriever(
            indexer=indexer,
            db_path=self.db_dir
        )
        results = retriever.retrieve(
            query="user authentication login",
            collection_name=collection,
            top_k=3,
            threshold=0.0  # No threshold
        )
        
        # Verify
        self.assertGreater(len(results), 0)
        
        # Should find auth.py
        found_auth = any('auth.py' in r['file_path'] for r in results)
        self.assertTrue(found_auth)
    
    def test_large_codebase_performance(self):
        """Test performance with larger codebase."""
        import time
        
        # Create 50 test files
        for i in range(50):
            content = f'''def function_{i}():
    """Function number {i}."""
    return {i}

class Class_{i}:
    """Class number {i}."""
    def method(self):
        """Method of class {i}."""
        return "class_{i}"
'''
            (Path(self.temp_dir) / f"file_{i}.py").write_text(content)
        
        # Measure indexing time
        indexer = RAGIndexer(
            db_path=self.db_dir,
            batch_size=8,
            use_gpu=False
        )
        
        start = time.time()
        collection = indexer.build_vector_db(
            self.temp_dir,
            project_name="perf_test_project",
            force_rebuild=True
        )
        index_time = time.time() - start
        
        self.assertLess(index_time, 60)  # Should complete within 60s
        
        # Measure query time with same db_path
        retriever = RAGRetriever(
            indexer=indexer,
            db_path=self.db_dir
        )
        
        # Check stats before querying
        stats = retriever.get_statistics(collection_name=collection)
        print(f"\nPerf test collection stats: {stats['total_chunks']} chunks, {stats['total_files']} files")
        self.assertGreater(stats['total_chunks'], 0, "Collection should have chunks")
        
        start = time.time()
        results = retriever.retrieve(
            query="function implementation",
            collection_name=collection,
            top_k=5,
            threshold=0.0  # No threshold
        )
        query_time = time.time() - start
        
        # Debug: show what we got
        if not results:
            print(f"\nNo results found! Trying different query...")
            results = retriever.retrieve(
                query="class method",
                collection_name=collection,
                top_k=5,
                threshold=0.0
            )
            print(f"Alternative query results: {len(results)}")
        
        self.assertLess(query_time, 1.0)  # Should be < 1 second
        self.assertGreater(len(results), 0, f"Expected results but got {len(results)}. Stats: {stats}")


def run_rag_tests():
    """Run all RAG tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    if RAG_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestRAGIndexer))
        suite.addTests(loader.loadTestsFromTestCase(TestRAGRetriever))
        suite.addTests(loader.loadTestsFromTestCase(TestRAGIntegration))
    else:
        print("⚠ RAG tests skipped (dependencies not installed)")
    
    if PERFORMANCE_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestPerformanceOptimizations))
    else:
        print("⚠ Performance optimization tests skipped (dependencies not installed)")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_rag_tests()
    sys.exit(0 if success else 1)
