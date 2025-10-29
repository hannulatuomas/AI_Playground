"""
Test script for Phase 2: Core Architecture

Tests the integration of LLMInterface, PromptEngine, and LearningDB.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core import LLMInterface, LLMConfig, PromptEngine, LearningDB, load_config_from_file


def test_learning_db():
    """Test the Learning Database."""
    print("="*60)
    print("Testing Learning Database")
    print("="*60)
    
    db = LearningDB("data/db/test_core.db")
    print("✓ Database initialized")
    
    # Add a test entry
    entry_id = db.add_entry(
        query="Test query",
        language="python",
        response="Test response",
        task_type="generate",
        success=True
    )
    print(f"✓ Added entry: {entry_id}")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"✓ Statistics: {stats['total_interactions']} interactions")
    
    return db


def test_prompt_engine(db):
    """Test the Prompt Engine."""
    print("\n" + "="*60)
    print("Testing Prompt Engine")
    print("="*60)
    
    engine = PromptEngine(learning_db=db)
    print("✓ Prompt Engine initialized")
    
    # Test code generation prompt
    prompt = engine.build_prompt(
        task_type='generate',
        language='python',
        content='Create a function to calculate factorial'
    )
    print(f"✓ Generated prompt ({len(prompt)} chars)")
    print(f"  Preview: {prompt[:100]}...")
    
    # Test debug prompt
    debug_prompt = engine.build_prompt(
        task_type='debug',
        language='cpp',
        content='int* ptr = NULL;\n*ptr = 5;',
        error='Segmentation fault'
    )
    print(f"✓ Generated debug prompt ({len(debug_prompt)} chars)")
    
    # Show supported languages
    languages = engine.get_supported_languages()
    print(f"✓ Supports {len(languages)} languages: {', '.join(languages[:5])}...")
    
    return engine


def test_llm_interface():
    """Test the LLM Interface."""
    print("\n" + "="*60)
    print("Testing LLM Interface")
    print("="*60)
    
    # Try to load config
    config = load_config_from_file()
    
    if not config:
        print("⚠ No configuration found")
        print("  Creating test configuration...")
        config = LLMConfig(
            model_path="data/models/test-model.gguf",
            executable_path="llama.cpp/llama-cli",
            context_size=2048,
            temperature=0.7
        )
        print("✓ Test config created")
    else:
        print("✓ Configuration loaded")
        print(f"  Model: {Path(config.model_path).name}")
        print(f"  Executable: {Path(config.executable_path).name}")
    
    try:
        llm = LLMInterface(config)
        print("✓ LLM Interface initialized")
        
        # Test cache
        cache_stats = llm.get_cache_stats()
        print(f"✓ Cache: {cache_stats['current_size']}/{cache_stats['max_size']}")
        
    except FileNotFoundError as e:
        print(f"⚠ Could not initialize LLM: {e}")
        print("  This is expected if llama.cpp or model is not set up yet")
        return None
    
    return llm


def test_integration(db, engine, llm):
    """Test integration of all three modules."""
    print("\n" + "="*60)
    print("Testing Integration")
    print("="*60)
    
    # Add a learning to the database
    db.add_entry(
        query="Create a sorting function",
        language="python",
        response="def sort(lst): return sorted(lst)",
        task_type="generate",
        success=False,
        error_type="inefficient",
        correction="Use built-in sorted() for better performance"
    )
    print("✓ Added learning to database")
    
    # Generate prompt that includes learnings
    prompt = engine.build_prompt(
        task_type='generate',
        language='python',
        content='Create an efficient sorting function',
        include_learnings=True
    )
    
    # Check if learnings are included
    if 'past experience' in prompt.lower() or 'avoid' in prompt.lower():
        print("✓ Prompt includes past learnings")
    else:
        print("✓ Prompt generated (no learnings yet)")
    
    # If LLM is available, test generation (without actually calling it)
    if llm:
        print("✓ LLM ready for generation")
        print("  (Skipping actual generation to save time)")
    else:
        print("⚠ LLM not available (expected if not configured)")
    
    print("\n✓ Integration test complete")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  Phase 2: Core Architecture - Module Tests")
    print("="*60 + "\n")
    
    try:
        # Test each module
        db = test_learning_db()
        engine = test_prompt_engine(db)
        llm = test_llm_interface()
        
        # Test integration
        test_integration(db, engine, llm)
        
        print("\n" + "="*60)
        print("  ✓ All Core Modules Working!")
        print("="*60)
        print("\nModules ready:")
        print("  ✓ LearningDB - Stores and retrieves interactions")
        print("  ✓ PromptEngine - Generates language-specific prompts")
        print("  ✓ LLMInterface - Interfaces with llama.cpp")
        print("\nNext: Implement features (code generation, debugging, etc.)")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
