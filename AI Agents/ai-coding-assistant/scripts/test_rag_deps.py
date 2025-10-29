"""
Test script to verify RAG dependencies are installed correctly
"""

import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}\n")

print("Testing imports:")
print("-" * 60)

# Test numpy
try:
    import numpy
    print(f"✓ numpy {numpy.__version__} - OK")
except ImportError as e:
    print(f"✗ numpy - FAILED: {e}")

# Test sentence-transformers
try:
    import sentence_transformers
    print(f"✓ sentence-transformers {sentence_transformers.__version__} - OK")
except ImportError as e:
    print(f"✗ sentence-transformers - FAILED: {e}")

# Test chromadb
try:
    import chromadb
    print(f"✓ chromadb {chromadb.__version__} - OK")
except ImportError as e:
    print(f"✗ chromadb - FAILED: {e}")

print("-" * 60)
print("\nIf any modules failed, install them with:")
print("pip install numpy sentence-transformers chromadb")
print("\nMake sure you're using the same Python that pip installs to:")
print(f"  {sys.executable}")
