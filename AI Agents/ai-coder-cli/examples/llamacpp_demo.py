#!/usr/bin/env python3
"""
Llama-cpp Integration Demo

Demonstrates the llama-cpp-python integration for local LLM support
with automatic fallback to other providers.
"""

import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.llm_router import LLMRouter
from core.config import AppConfig
from tools.llamacpp_manager import LlamaCppManager


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def demo_llamacpp_manager():
    """Demonstrate LlamaCpp manager capabilities."""
    print_section("Llama-cpp Manager Demo")
    
    # Initialize configuration
    config = {
        'llamacpp': {
            'model_path': './models/llama-2-7b-chat.gguf',
            'context_size': 2048,
            'n_threads': 4,
            'n_gpu_layers': 0,  # CPU only for demo
            'verbose': False,
            'models_dir': './models'
        }
    }
    
    # Create manager
    manager = LlamaCppManager(config=config)
    
    # 1. Health Check
    print("1. Performing health check...")
    health_result = manager.health_check()
    print(f"   Status: {health_result['message']}")
    
    if health_result.get('data'):
        data = health_result['data']
        print(f"   Available: {data.get('status')}")
        print(f"   Model configured: {data.get('model_configured')}")
        print(f"   Model loaded: {data.get('model_loaded')}")
    
    # 2. List Available Models
    print("\n2. Listing available models...")
    models_result = manager.list_models()
    
    if models_result['success']:
        models = models_result['data']['models']
        print(f"   Found {len(models)} model(s):")
        
        for model in models:
            print(f"   - {model['name']} ({model['size_mb']:.2f} MB)")
    else:
        print(f"   {models_result['message']}")
    
    # 3. Load Model (if available)
    if health_result.get('data', {}).get('model_configured'):
        print("\n3. Loading model...")
        
        model_path = config['llamacpp']['model_path']
        load_result = manager.load_model(model_path)
        
        if load_result['success']:
            print(f"   ✓ {load_result['message']}")
            print(f"   Context size: {load_result['data']['context_size']}")
            print(f"   GPU layers: {load_result['data']['n_gpu_layers']}")
            
            # 4. Generate Text
            print("\n4. Generating text...")
            
            prompt = "Explain what a neural network is in one sentence."
            gen_result = manager.generate(prompt, {
                'temperature': 0.7,
                'max_tokens': 100
            })
            
            if gen_result['success']:
                print(f"   Prompt: {prompt}")
                print(f"   Response: {gen_result['data']['generated_text']}")
                print(f"   Tokens: {gen_result['data'].get('tokens_used', 'N/A')}")
            else:
                print(f"   Generation failed: {gen_result['message']}")
            
            # 5. Unload Model
            print("\n5. Unloading model...")
            unload_result = manager.unload_model()
            print(f"   {unload_result['message']}")
        else:
            print(f"   ✗ {load_result['message']}")
    else:
        print("\n3. Skipping model loading (no model configured)")


def demo_llm_router_with_fallback():
    """Demonstrate LLM Router with llama-cpp and fallback."""
    print_section("LLM Router with Fallback Demo")
    
    # Load configuration
    config = AppConfig.load()
    
    # Configure for llama-cpp as primary with fallback
    config.fallback.primary_provider = "llamacpp"
    config.fallback.fallback_provider = "ollama"
    config.fallback.secondary_fallback_provider = "openai"
    
    print("Configuration:")
    print(f"  Primary provider: {config.fallback.primary_provider}")
    print(f"  Fallback provider: {config.fallback.fallback_provider}")
    print(f"  Secondary fallback: {config.fallback.secondary_fallback_provider}")
    
    # Initialize router
    print("\nInitializing LLM Router...")
    router = LLMRouter(config)
    
    # Check available providers
    available = router.get_available_providers()
    print(f"\nAvailable providers: {', '.join(available) if available else 'None'}")
    
    if not available:
        print("\n⚠ No LLM providers available!")
        print("Please configure at least one provider:")
        print("  - Llama-cpp: Set model_path in config.yaml")
        print("  - Ollama: Start Ollama server")
        print("  - OpenAI: Set OPENAI_API_KEY environment variable")
        return
    
    # Test queries
    test_queries = [
        "What is machine learning?",
        "Write a Python function to calculate fibonacci numbers.",
        "Explain the concept of recursion."
    ]
    
    print("\nTesting queries with automatic fallback:")
    
    for i, prompt in enumerate(test_queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"Prompt: {prompt}")
        
        try:
            result = router.query(
                prompt=prompt,
                temperature=0.7,
                max_tokens=150
            )
            
            print(f"Provider used: {result['provider']}")
            print(f"Model: {result['model']}")
            print(f"Response: {result['response'][:200]}...")
            
        except Exception as e:
            print(f"Error: {e}")


def demo_provider_comparison():
    """Demonstrate querying different providers."""
    print_section("Provider Comparison Demo")
    
    config = AppConfig.load()
    router = LLMRouter(config)
    
    prompt = "What is the capital of France?"
    print(f"Prompt: {prompt}\n")
    
    # Try each provider
    providers = ['llamacpp', 'ollama', 'openai']
    
    for provider in providers:
        print(f"--- {provider.upper()} ---")
        
        if not router.is_available(provider):
            print(f"✗ Not available\n")
            continue
        
        try:
            result = router.query(
                prompt=prompt,
                provider=provider,
                temperature=0.7,
                max_tokens=50
            )
            
            print(f"✓ Response: {result['response']}")
            print(f"  Model: {result['model']}\n")
            
        except Exception as e:
            print(f"✗ Error: {e}\n")


def demo_configuration_examples():
    """Show configuration examples."""
    print_section("Configuration Examples")
    
    print("Example config.yaml configuration:")
    print("""
llamacpp:
  model_path: "./models/llama-2-7b-chat.gguf"
  models_dir: "./models"
  context_size: 4096
  n_threads: 4
  n_gpu_layers: 35
  verbose: false

models:
  llamacpp_default: "llama-2-7b-chat.gguf"

fallback:
  enabled: true
  primary_provider: "llamacpp"
  fallback_provider: "ollama"
  secondary_fallback_provider: "openai"
    """)


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("  LLAMA-CPP INTEGRATION DEMONSTRATION")
    print("=" * 60)
    
    # Run demos
    demo_configuration_examples()
    demo_llamacpp_manager()
    demo_llm_router_with_fallback()
    demo_provider_comparison()
    
    print("\n" + "=" * 60)
    print("  Demo completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
