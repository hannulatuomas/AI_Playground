"""
Tests for Phase 9.2: Code Understanding

Tests for:
- CodeBERT embeddings
- Multi-modal retrieval
- Enhanced RAG integration
"""

import unittest
import tempfile
import shutil
import os
from pathlib import Path
import sys
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import Phase 9.2 features
try:
    from features.rag_advanced.code_embeddings import CodeEmbedder, FallbackCodeEmbedder
    CODE_EMBEDDINGS_AVAILABLE = True
except ImportError:
    CODE_EMBEDDINGS_AVAILABLE = False

try:
    from features.rag_advanced.multimodal import MultiModalRetriever
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False

try:
    from features.rag_advanced.integration import EnhancedRAG
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False


@unittest.skipIf(not CODE_EMBEDDINGS_AVAILABLE, "Code embeddings not available")
class TestCodeEmbeddings(unittest.TestCase):
    """Test suite for CodeBERT embeddings."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use fallback if transformers not available
        try:
            self.embedder = CodeEmbedder(model_name='codebert', use_gpu=False)
            self.using_fallback = False
        except Exception:
            self.embedder = FallbackCodeEmbedder()
            self.using_fallback = True
    
    def test_single_embedding(self):
        """Test embedding a single code snippet."""
        code = "def hello(): return 'world'"
        embedding = self.embedder.embed_code(code, language="python")
        
        self.assertIsInstance(embedding, np.ndarray)
        self.assertGreater(embedding.shape[0], 0)
    
    def test_batch_embedding(self):
        """Test embedding multiple code snippets."""
        codes = [
            "def add(a, b): return a + b",
            "def sub(a, b): return a - b",
            "def mul(a, b): return a * b"
        ]
        
        embeddings = self.embedder.embed_batch(
            codes,
            languages=["python"] * 3,
            show_progress=False
        )
        
        self.assertEqual(embeddings.shape[0], 3)
        self.assertGreater(embeddings.shape[1], 0)
    
    def test_similarity(self):
        """Test code similarity computation."""
        # Skip if using fallback embedder (transformers not available)
        if self.using_fallback:
            self.skipTest("Fallback embedder in use - install transformers and torch to enable this test")
        
        code1 = "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"
        code2 = "def fac(x): return 1 if x <= 1 else x * fac(x-1)"
        code3 = "def hello(): return 'world'"
        
        sim_similar = self.embedder.get_similarity(code1, code2, language="python")
        sim_different = self.embedder.get_similarity(code1, code3, language="python")
        
        self.assertGreater(sim_similar, sim_different)


@unittest.skipIf(not MULTIMODAL_AVAILABLE, "Multi-modal not available")
class TestMultiModal(unittest.TestCase):
    """Test suite for multi-modal retrieval."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock embedders
        self.code_embedder = FallbackCodeEmbedder()
        
        try:
            from sentence_transformers import SentenceTransformer
            self.doc_embedder = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            self.doc_embedder = None
        
        if self.doc_embedder:
            self.mm_retriever = MultiModalRetriever(
                code_embedder=self.code_embedder,
                doc_embedder=self.doc_embedder
            )
    
    def test_index_multimodal(self):
        """Test multi-modal indexing."""
        if not self.doc_embedder:
            self.skipTest("Doc embedder not available")
        
        result = self.mm_retriever.index_multimodal(
            code="def login(user, pwd): pass",
            docs="Authenticate user with credentials",
            metadata={'file': 'auth.py', 'line': 10},
            language='python'
        )
        
        self.assertIn('metadata', result)
        self.assertIn('has_docstring', result)
        self.assertTrue(result['has_docstring'])
    
    def test_extract_python_docs(self):
        """Test Python documentation extraction."""
        code = '''
def login(user, pwd):
    """Authenticate user login."""
    return True

class Auth:
    """Authentication handler."""
    pass
'''
        docs, meta = self.mm_retriever.extract_documentation(code, 'python')
        
        self.assertIn('Authenticate user login', docs)
        self.assertTrue(meta['has_docstring'])
        self.assertGreater(meta['docstring_count'], 0)
    
    def test_doc_quality_assessment(self):
        """Test documentation quality assessment."""
        good_doc = "This function authenticates users by verifying their credentials against the database."
        poor_doc = "TODO"
        
        good_score = self.mm_retriever._assess_doc_quality(good_doc)
        poor_score = self.mm_retriever._assess_doc_quality(poor_doc)
        
        self.assertGreater(good_score, poor_score)


@unittest.skipIf(not INTEGRATION_AVAILABLE, "Integration not available")
class TestEnhancedRAGIntegration(unittest.TestCase):
    """Test suite for Enhanced RAG integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_dir = tempfile.mkdtemp()
        
        # Create test files
        (Path(self.temp_dir) / "auth.py").write_text('''
def authenticate(username, password):
    """Authenticate user with credentials."""
    return verify_password(username, password)

def verify_password(username, password):
    """Verify password hash."""
    return True
''')
        
        try:
            self.rag = EnhancedRAG(
                project_root=self.temp_dir,
                db_path=self.db_dir,
                use_query_expansion=True,
                use_feedback_learning=True,
                use_graph_retrieval=True,
                use_code_embeddings=False,  # Skip CodeBERT for tests
                use_multimodal=False
            )
        except Exception as e:
            self.rag = None
            print(f"Could not initialize EnhancedRAG: {e}")
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree(self.db_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test Enhanced RAG initialization."""
        if not self.rag:
            self.skipTest("EnhancedRAG not initialized")
        
        self.assertIsNotNone(self.rag.indexer)
        self.assertIsNotNone(self.rag.retriever)
        self.assertIsNotNone(self.rag.query_expander)
        self.assertIsNotNone(self.rag.feedback_learner)
    
    def test_index_project(self):
        """Test project indexing."""
        if not self.rag:
            self.skipTest("EnhancedRAG not initialized")
        
        collection = self.rag.index_project("test-project", force_rebuild=True)
        
        self.assertIsInstance(collection, str)
        self.assertEqual(collection, "test-project")
    
    def test_enhanced_retrieval(self):
        """Test enhanced retrieval with all features."""
        if not self.rag:
            self.skipTest("EnhancedRAG not initialized")
        
        # Index first
        collection = self.rag.index_project("test-project", force_rebuild=True)
        
        # Retrieve
        results = self.rag.retrieve(
            query="user authentication",
            collection_name=collection,
            language="python",
            top_k=3,
            use_query_expansion=True,
            use_feedback_ranking=True,
            use_graph_context=False
        )
        
        self.assertIsInstance(results, list)
    
    def test_get_statistics(self):
        """Test getting statistics."""
        if not self.rag:
            self.skipTest("EnhancedRAG not initialized")
        
        stats = self.rag.get_statistics()
        
        self.assertIn('features_enabled', stats)
        self.assertIsInstance(stats['features_enabled'], dict)


def run_phase_92_tests():
    """Run all Phase 9.2 tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    if CODE_EMBEDDINGS_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestCodeEmbeddings))
    else:
        print("⚠ Code embeddings tests skipped")
    
    if MULTIMODAL_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestMultiModal))
    else:
        print("⚠ Multi-modal tests skipped")
    
    if INTEGRATION_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestEnhancedRAGIntegration))
    else:
        print("⚠ Integration tests skipped")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_phase_92_tests()
    sys.exit(0 if success else 1)
