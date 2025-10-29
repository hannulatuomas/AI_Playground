# Llama-cpp Integration Guide

This document provides comprehensive information about the llama-cpp-python integration for local LLM support.

## Overview

The llama-cpp integration provides an alternative to Ollama for running local LLMs. It supports GGUF format models and offers:

- Direct model file loading (no server required)
- GPU acceleration support
- Configurable context windows
- Thread control for performance tuning
- Seamless fallback with Ollama and OpenAI

## Installation

### Install llama-cpp-python

The `llama-cpp-python` package is included in `requirements.txt`. To install all dependencies:

```bash
# Install all dependencies (includes llama-cpp-python)
pip install -r requirements.txt
```

For GPU acceleration, you may want to reinstall with specific build flags:

```bash
# With CUDA support (NVIDIA GPUs)
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install --force-reinstall llama-cpp-python

# With Metal support (Apple Silicon)
CMAKE_ARGS="-DLLAMA_METAL=on" pip install --force-reinstall llama-cpp-python

# With OpenBLAS support
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" pip install --force-reinstall llama-cpp-python

# CPU only (default from requirements.txt)
pip install llama-cpp-python
```

### Download Models

Download GGUF format models from Hugging Face:

```bash
# Create models directory
mkdir -p models

# Example: Download a model
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf -O models/llama-2-7b-chat.gguf
```

Popular GGUF models:
- [TheBloke's GGUF Models](https://huggingface.co/TheBloke?search_models=GGUF)
- [Mistral Models](https://huggingface.co/mistralai)
- [Llama 2 Models](https://huggingface.co/meta-llama)

## Configuration

### config.yaml

Add llama-cpp configuration to your `config.yaml`:

```yaml
llamacpp:
  model_path: "./models/llama-2-7b-chat.gguf"  # Path to your GGUF model
  models_dir: "./models"                        # Directory for model files
  context_size: 4096                            # Context window (tokens)
  n_threads: 4                                  # Number of CPU threads (null = auto)
  n_gpu_layers: 35                              # GPU layers (0 = CPU only)
  verbose: false                                # Enable verbose logging

models:
  llamacpp_default: "llama-2-7b-chat.gguf"      # Default model name

fallback:
  enabled: true
  primary_provider: "llamacpp"                  # Use llama-cpp as primary
  fallback_provider: "ollama"                   # Fallback to Ollama
  secondary_fallback_provider: "openai"         # Then try OpenAI
```

### Environment Variables

You can also configure using environment variables:

```bash
export AI_AGENT_LLAMACPP__MODEL_PATH="./models/llama-2-7b-chat.gguf"
export AI_AGENT_LLAMACPP__CONTEXT_SIZE=4096
export AI_AGENT_LLAMACPP__N_GPU_LAYERS=35
```

## Usage

### Basic Usage

The llama-cpp provider is automatically initialized when configured:

```python
from core.llm_router import LLMRouter
from core.config import AppConfig

# Load configuration
config = AppConfig.load()

# Initialize router (automatically includes llama-cpp if configured)
router = LLMRouter(config)

# Query using the configured provider chain
result = router.query(
    prompt="Explain quantum computing",
    temperature=0.7
)

print(result['response'])
print(f"Provider used: {result['provider']}")
```

### Using Llama-cpp Specifically

```python
# Force use of llama-cpp provider
result = router.query(
    prompt="Write a Python function",
    provider="llamacpp",
    temperature=0.8,
    max_tokens=512
)
```

### Using the LlamaCpp Manager Directly

```python
from tools.llamacpp_manager import LlamaCppManager

# Initialize manager
config = {'llamacpp': {...}}
manager = LlamaCppManager(config=config)

# Health check
health = manager.health_check()
print(health)

# Load a model
result = manager.load_model("./models/my-model.gguf")
print(result['message'])

# Generate text
result = manager.generate(
    "Explain machine learning",
    config={'temperature': 0.7, 'max_tokens': 512}
)
print(result['data']['generated_text'])

# List available models
models = manager.list_models()
for model in models['data']['models']:
    print(f"{model['name']} - {model['size_mb']}MB")

# Unload model to free memory
manager.unload_model()
```

## Features

### Automatic Fallback

The system automatically falls back to other providers if llama-cpp fails:

```python
# Configure fallback chain
config.fallback.primary_provider = "llamacpp"
config.fallback.fallback_provider = "ollama"
config.fallback.secondary_fallback_provider = "openai"

router = LLMRouter(config)

# Will try llama-cpp -> ollama -> openai automatically
result = router.query("Hello, world!")
```

### GPU Acceleration

Configure GPU layers for better performance:

```yaml
llamacpp:
  n_gpu_layers: 35  # Number of layers to offload to GPU
                    # 0 = CPU only
                    # -1 = all layers on GPU
                    # 35 = recommended for 8GB VRAM
```

### Context Window Configuration

Adjust context size based on your needs and available memory:

```yaml
llamacpp:
  context_size: 2048   # Smaller, faster, less memory
  # context_size: 4096  # Balanced
  # context_size: 8192  # Larger context, more memory
```

### Thread Configuration

Optimize CPU thread usage:

```yaml
llamacpp:
  n_threads: null  # Auto-detect (recommended)
  # n_threads: 4   # Fixed thread count
  # n_threads: 8   # More threads (if you have cores available)
```

## Performance Tuning

### Memory Considerations

| Context Size | Model Size | Approximate RAM |
|--------------|------------|-----------------|
| 2048         | 7B Q4      | ~4-6 GB         |
| 4096         | 7B Q4      | ~6-8 GB         |
| 8192         | 7B Q4      | ~10-12 GB       |
| 2048         | 13B Q4     | ~8-10 GB        |

### GPU Layers

- **0 layers**: CPU only, slower but works anywhere
- **10-20 layers**: Partial GPU, balanced performance
- **35+ layers**: Most/all on GPU, fastest (requires sufficient VRAM)
- **-1**: All layers on GPU (auto-calculate)

### Quantization Levels

Different quantization levels trade off quality for size:

- **Q2_K**: Smallest, lowest quality
- **Q4_K_M**: Good balance (recommended)
- **Q5_K_M**: Better quality, larger size
- **Q8_0**: Best quality, largest size

## Error Handling

### Model Not Found

```python
# If model file doesn't exist
result = manager.load_model("/nonexistent/model.gguf")
# Returns: {'success': False, 'message': 'Model file not found: ...'}
```

### Out of Memory

If you encounter OOM errors:

1. Reduce `context_size`
2. Reduce `n_gpu_layers`
3. Use a smaller quantized model (Q4 instead of Q5)
4. Close other applications

### Provider Not Available

The system provides helpful error messages:

```
No LLM providers are available. Please configure at least one provider:

  ✗ Llama-cpp: Not installed
    → Install: pip install llama-cpp-python
    → Configure model_path in config.yaml
```

## Troubleshooting

### Installation Issues

**Problem**: Compilation fails during installation

**Solution**: Install build tools:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential cmake

# macOS
xcode-select --install

# Then retry installation
pip install llama-cpp-python
```

**Problem**: CUDA not detected

**Solution**: Ensure CUDA toolkit is installed and specify CUDA path:
```bash
CMAKE_ARGS="-DLLAMA_CUBLAS=on -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc" pip install llama-cpp-python
```

### Runtime Issues

**Problem**: Model loads but inference is very slow

**Solutions**:
1. Increase `n_gpu_layers` if you have a GPU
2. Increase `n_threads` for CPU
3. Use a smaller quantized model

**Problem**: "CUDA out of memory"

**Solutions**:
1. Reduce `n_gpu_layers`
2. Reduce `context_size`
3. Use a smaller model

## Best Practices

1. **Start with small models**: Test with 7B Q4 models before trying larger ones
2. **Monitor memory**: Use `nvidia-smi` or Activity Monitor to track usage
3. **Use quantized models**: Q4_K_M offers good quality/size balance
4. **Configure fallback**: Always have backup providers configured
5. **Test performance**: Benchmark different settings for your hardware

## Comparison with Ollama

| Feature | Llama-cpp | Ollama |
|---------|-----------|--------|
| Server required | No | Yes |
| Model format | GGUF | GGUF |
| GPU support | Yes | Yes |
| Memory usage | Lower | Higher (server overhead) |
| Model management | Manual | Automatic |
| Ease of use | Moderate | Easy |
| Performance | Fast | Fast |

## Resources

- [llama-cpp-python Documentation](https://github.com/abetlen/llama-cpp-python)
- [GGUF Models on Hugging Face](https://huggingface.co/models?library=gguf)
- [Model Quantization Guide](https://github.com/ggerganov/llama.cpp/blob/master/examples/quantize/README.md)

## Support

For issues or questions:
1. Check the [llama-cpp-python issues](https://github.com/abetlen/llama-cpp-python/issues)
2. Review this documentation
3. Check logs for specific error messages
