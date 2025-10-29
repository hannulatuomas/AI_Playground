"""Quick RAG debug script to check embedding and retrieval."""
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from features.rag_indexer import RAGIndexer
from features.rag_retriever import RAGRetriever

# Create temp directories
temp_dir = tempfile.mkdtemp()
db_dir = tempfile.mkdtemp()

try:
    print("Creating test files...")
    
    # Create simple test file
    test_file = Path(temp_dir) / "test.py"
    test_file.write_text('''
def authenticate(username, password):
    """Authenticate user with credentials."""
    return verify_password(username, password)

def verify_password(username, password):
    """Verify password hash."""
    return hash_password(password) == get_password_hash(username)
''')
    
    print(f"Test file created: {test_file}")
    
    # Index
    print("\nIndexing...")
    indexer = RAGIndexer(
        db_path=db_dir,
        batch_size=4,
        use_gpu=False
    )
    
    collection = indexer.build_vector_db(
        temp_dir,
        project_name="debug_test",
        force_rebuild=True
    )
    
    print(f"Collection created: {collection}")
    
    # Check stats
    retriever = RAGRetriever(indexer=indexer, db_path=db_dir)
    stats = retriever.get_statistics(collection_name=collection)
    print(f"\nStats: {stats}")
    
    # Try query with no threshold
    print("\nQuerying with 'user authentication'...")
    results = retriever.retrieve(
        query="user authentication",
        collection_name=collection,
        top_k=5,
        threshold=-10.0  # Very low threshold to get all results
    )
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n[{i}] Score: {result['score']:.4f}")
        print(f"    File: {result['file_path']}")
        print(f"    Content preview: {result['content'][:100]}...")
        
    if not results:
        print("\n⚠ No results found! This indicates an issue with embedding or retrieval.")
        print("Checking raw ChromaDB query...")
        
        # Try direct ChromaDB query
        collection_obj = retriever.chroma_client.get_collection(name=collection)
        query_embedding = indexer.model.encode(["user authentication"], convert_to_numpy=True)[0]
        
        raw_results = collection_obj.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=5
        )
        
        print(f"\nRaw ChromaDB results:")
        print(f"IDs: {raw_results['ids']}")
        print(f"Distances: {raw_results['distances']}")
        if raw_results['distances'] and raw_results['distances'][0]:
            distances = raw_results['distances'][0]
            similarities = [1 - d for d in distances]
            print(f"Converted similarities: {similarities}")
    
finally:
    # Cleanup
    print("\n\nCleaning up...")
    shutil.rmtree(temp_dir, ignore_errors=True)
    shutil.rmtree(db_dir, ignore_errors=True)
    print("Done!")
