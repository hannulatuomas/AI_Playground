# First Time Setup Guide

**AI Coding Assistant v1.0.1**

---

## ✅ Good News!

Your application is **working correctly**! The message you saw:

```
✗ Configuration not found
  Run: python main.py --setup
```

This is **expected** for first-time use. The app needs to be configured before it can connect to llama.cpp.

---

## Quick Setup (3 Steps)

### Step 1: Have llama.cpp Ready

Make sure you have:
- ✅ llama.cpp executable in `llama.cpp/` folder
- ✅ A GGUF model file in `data/models/` folder

If you don't have these yet, see the full README.md for download instructions.

### Step 2: Create Configuration

Create a file `data/config.json` with this content:

```json
{
  "model_path": "data/models/your-model-name.gguf",
  "executable_path": "llama.cpp/llama-cli.exe",
  "context_size": 4096,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "repeat_penalty": 1.1,
  "threads": 4,
  "gpu_layers": 0
}
```

**Replace:**
- `your-model-name.gguf` with your actual model filename
- `llama-cli.exe` with `llama-cli` if on Linux/macOS

### Step 3: Run the Application

```batch
run.bat
```

That's it! The application will now start.

---

## Alternative: Use Template

If you have the config template:

```batch
# Windows
copy data\config.json.template data\config.json
notepad data\config.json

# Linux/macOS
cp data/config.json.template data/config.json
nano data/config.json
```

Then edit the paths to match your setup.

---

## Verification

After creating config.json, run:

```batch
run.bat
```

You should see:
```
✓ Configuration loaded
✓ Database initialized
✓ Prompt engine ready
✓ LLM interface ready
✓ Code generator ready
✓ Debugger ready
✓ Language support loaded

✓ All components initialized!
```

---

## Troubleshooting

### "File not found: llama.cpp executable"

**Solution:** Check that `executable_path` in config.json points to the correct location.

### "File not found: Model file"

**Solution:** 
1. Download a GGUF model from HuggingFace
2. Place it in `data/models/` folder
3. Update `model_path` in config.json

### Still having issues?

1. Check that paths in config.json are correct
2. Verify llama.cpp exists and is executable
3. Verify model file exists and is a valid GGUF file

---

## Example Working Configuration

**Windows:**
```json
{
  "model_path": "data/models/codellama-7b-instruct.Q4_K_M.gguf",
  "executable_path": "llama.cpp/llama-cli.exe",
  "context_size": 4096,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "repeat_penalty": 1.1,
  "threads": 4,
  "gpu_layers": 0
}
```

**Linux/macOS:**
```json
{
  "model_path": "data/models/codellama-7b-instruct.Q4_K_M.gguf",
  "executable_path": "llama.cpp/llama-cli",
  "context_size": 4096,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "repeat_penalty": 1.1,
  "threads": 4,
  "gpu_layers": 0
}
```

---

## Quick Test

After configuration, test it works:

```batch
# Start the app
run.bat

# You should see all components initialize
# Then try a simple command:
ai-assistant> help
```

---

## Summary

The message "Configuration not found" is **not an error** - it's the app correctly telling you it needs to be configured for first use. Just create `data/config.json` with your llama.cpp and model paths, and you're ready to go!

**Your application is working perfectly!** ✅

---

**Need Help?**
- See README.md for full setup instructions
- See QUICKSTART.md for quick start guide
- Check that llama.cpp and model files exist
