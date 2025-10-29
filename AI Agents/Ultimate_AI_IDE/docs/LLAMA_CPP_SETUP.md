# llama.cpp Setup Guide

UAIDE uses **llama.cpp binaries directly** instead of Python bindings. This means:
- ✅ No compilation needed
- ✅ No C++ build tools required
- ✅ Easy to update - just replace the binary
- ✅ Works on any system with the right binary

---

## Quick Start

### 1. Download llama.cpp Binary

Choose the binary for your system:

#### **Windows**

**Option A: Pre-built Releases (Recommended)**
1. Visit: https://github.com/ggerganov/llama.cpp/releases
2. Download the latest release for Windows:
   - **CPU only**: `llama-*-bin-win-avx2-x64.zip`
   - **NVIDIA GPU (CUDA)**: `llama-*-bin-win-cuda-cu12.2.0-x64.zip`
   - **AMD GPU (ROCm)**: `llama-*-bin-win-rocm-x64.zip`
3. Extract the ZIP file
4. Find the executable (usually `llama-cli.exe` or `main.exe`)

**Option B: Build from Source**
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

#### **Linux**

**Option A: Pre-built Releases**
1. Visit: https://github.com/ggerganov/llama.cpp/releases
2. Download for Linux:
   - **CPU**: `llama-*-bin-ubuntu-x64.zip`
   - **CUDA**: `llama-*-bin-ubuntu-cuda-cu12.2.0-x64.zip`

**Option B: Build from Source**
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
```

#### **macOS**

**Option A: Homebrew**
```bash
brew install llama.cpp
```

**Option B: Build from Source**
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
```

---

### 2. Place Binary in llama-cpp/ Directory

Create the `llama-cpp/` directory in your UAIDE project root and place the binary there:

```
Ultimate_AI_IDE/
├── llama-cpp/
│   ├── llama-cli.exe    (Windows)
│   ├── llama-cli        (Linux/Mac)
│   ├── main.exe         (alternative name)
│   ├── main             (alternative name)
│   └── models/          (AI models go here)
├── src/
└── ...
```

**Supported binary names:**
- `llama-cli.exe` / `llama-cli` (recommended)
- `main.exe` / `main` (older versions)
- `llama.exe` / `llama`

UAIDE will automatically detect which one you have!

---

### 3. Download AI Model

Download a GGUF format model:

**Recommended Models:**

| Model | Size | Use Case | Link |
|-------|------|----------|------|
| Llama 3.2 3B | 2GB | Fast, lightweight | [HuggingFace](https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF) |
| Llama 3.1 8B | 5GB | Balanced | [HuggingFace](https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF) |
| Qwen 2.5 7B | 4.5GB | Code-focused | [HuggingFace](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF) |
| DeepSeek Coder 6.7B | 4GB | Coding | [HuggingFace](https://huggingface.co/TheBloke/deepseek-coder-6.7B-instruct-GGUF) |

**Quantization levels:**
- `Q4_K_M` - Good balance (recommended)
- `Q5_K_M` - Better quality, larger size
- `Q8_0` - Highest quality, largest size

Place the downloaded `.gguf` file in the `llama-cpp/models/` directory.

---

### 4. Update Configuration

Edit `config.json`:

```json
{
  "ai": {
    "model_path": "llama-cpp/models/your-model-name-Q4_K_M.gguf",
    "max_tokens": 2048,
    "temperature": 0.7,
    "context_length": 8192,
    "threads": 4
  }
}
```

**Configuration options:**
- `model_path` - Path to your .gguf model file
- `max_tokens` - Maximum tokens to generate (default: 2048)
- `temperature` - Creativity (0.0-1.0, default: 0.7)
- `context_length` - Context window size (default: 8192)
- `threads` - CPU threads to use (default: 4)

---

### 5. Verify Setup

Check if everything is working:

```bash
scripts\run_uaide.bat status
```

You should see:
```
AI Backend:
  llama.cpp binary: llama-cpp/llama-cli.exe
  Status: ✓ Found

AI Model:
  Path: llama-cpp/models/your-model.gguf
  Status: ✓ Found
```

---

## Advanced Configuration

### GPU Acceleration

#### NVIDIA GPU (CUDA)
1. Download CUDA-enabled llama.cpp binary
2. Install CUDA Toolkit (12.2 or compatible)
3. Binary will automatically use GPU

#### AMD GPU (ROCm)
1. Download ROCm-enabled llama.cpp binary
2. Install ROCm drivers
3. Binary will automatically use GPU

#### Apple Silicon (Metal)
1. Use standard macOS binary
2. Metal acceleration is built-in
3. No additional setup needed

### Performance Tuning

**For faster inference:**
- Use Q4_K_M quantization (smaller, faster)
- Reduce `context_length` to 4096 or 2048
- Increase `threads` to match your CPU cores

**For better quality:**
- Use Q5_K_M or Q8_0 quantization
- Increase `context_length` to 16384 or 32768
- Lower `temperature` to 0.5 or 0.3

---

## Troubleshooting

### "llama.cpp binary not found"

**Solution:**
1. Check that `llama-cpp/` directory exists
2. Verify binary is named correctly (`llama-cli.exe`, `main.exe`, etc.)
3. Make sure binary is executable (Linux/Mac: `chmod +x llama-cpp/llama-cli`)

### "Model file not found"

**Solution:**
1. Check `llama-cpp/models/` directory contains your .gguf file
2. Verify `config.json` has correct path
3. Use forward slashes in path: `llama-cpp/models/model.gguf`

### Binary crashes or errors

**Solution:**
1. Download the correct binary for your system (CPU vs GPU)
2. Try a different quantization level (Q4_K_M is most compatible)
3. Reduce `context_length` if running out of memory
4. Check llama.cpp version matches model format

### Slow inference

**Solution:**
1. Use GPU-enabled binary if you have a GPU
2. Use smaller quantization (Q4_K_M instead of Q8_0)
3. Increase `threads` in config
4. Use a smaller model (3B instead of 8B)

---

## Updating llama.cpp

To update to a newer version:

1. Download new binary from releases
2. Replace old binary in `llama-cpp/` directory
3. Restart UAIDE

That's it! No recompilation needed.

---

## Directory Structure

```
Ultimate_AI_IDE/
├── llama-cpp/              ← llama.cpp directory
│   ├── llama-cli.exe       ← Binary here
│   └── models/             ← Models here
│       ├── llama-3.1-8b-q4.gguf
│       └── qwen-2.5-7b-q4.gguf
├── config.json            ← Configure model path here
└── ...
```

---

## Recommended Setup

**For Development (Fast):**
- Binary: CPU version
- Model: Llama 3.2 3B Q4_K_M (~2GB)
- Context: 4096
- Threads: 4-8

**For Production (Quality):**
- Binary: GPU version (if available)
- Model: Llama 3.1 8B Q5_K_M (~5GB)
- Context: 8192
- Threads: 8-16

**For Coding (Specialized):**
- Binary: GPU version (if available)
- Model: DeepSeek Coder 6.7B Q4_K_M (~4GB)
- Context: 8192
- Threads: 8

---

## Resources

- **llama.cpp GitHub**: https://github.com/ggerganov/llama.cpp
- **llama.cpp Releases**: https://github.com/ggerganov/llama.cpp/releases
- **Model Hub**: https://huggingface.co/models?library=gguf
- **Quantization Guide**: https://github.com/ggerganov/llama.cpp/blob/master/examples/quantize/README.md

---

## Benefits of Using Binary Directly

1. **No Compilation** - Download and use immediately
2. **Easy Updates** - Just replace the binary file
3. **Platform Flexibility** - Use the best binary for your system
4. **No Python Dependencies** - No llama-cpp-python build issues
5. **GPU Support** - Easy to switch between CPU and GPU versions
6. **Latest Features** - Always use the newest llama.cpp version

---

**You're all set!** The binary approach makes UAIDE work on any system without compilation headaches. 🚀
