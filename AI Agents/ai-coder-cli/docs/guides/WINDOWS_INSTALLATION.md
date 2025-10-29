# Windows Installation Guide

Complete guide for installing and running AI Agent Console on Windows systems.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
  - [Method 1: Binary Installation (Recommended)](#method-1-binary-installation-recommended)
  - [Method 2: Python Installation via pip](#method-2-python-installation-via-pip)
  - [Method 3: Installation from Source](#method-3-installation-from-source)
- [Initial Configuration](#initial-configuration)
- [First-Time Usage](#first-time-usage)
- [LLM Provider Setup](#llm-provider-setup)
- [Common Issues and Troubleshooting](#common-issues-and-troubleshooting)
- [Uninstallation](#uninstallation)
- [Advanced Configuration](#advanced-configuration)
- [Building Your Own Binary](#building-your-own-binary)

---

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10 (64-bit) or later
- **Memory**: 4 GB RAM (8 GB recommended)
- **Storage**: 500 MB free disk space (1 GB recommended for models and data)
- **Display**: 1280x720 or higher resolution

### Required Software (for Binary Installation)

- **None!** The binary package includes all necessary dependencies

### Required Software (for Python Installation)

- **Python**: 3.9 or later (3.11 recommended)
- **pip**: Latest version (included with Python)
- **Git**: Latest version (optional, for version control features)

### LLM Provider Requirements

Choose at least one:

**Option A: Ollama (Local, Free)**
- Download from: https://ollama.ai/
- Requires: 4 GB RAM minimum (8 GB recommended)
- Storage: Depends on model size (2-10 GB per model)

**Option B: OpenAI (Cloud, Paid)**
- Requires: OpenAI API key
- Internet connection required
- No local storage needed

**Option C: llama-cpp (Local, Free)**
- Python-based, no server required
- Requires: GGUF model files
- Optional: GPU for acceleration

---

## Installation Methods

### Method 1: Binary Installation (Recommended)

The easiest way to install AI Agent Console on Windows is using the pre-built binary.

#### Step 1: Download

Download the latest Windows binary package:
- **From GitHub Releases**: `ai-agent-console-windows-vX.X.X.zip`
- **From Build**: If you received a ZIP file from the development team

#### Step 2: Extract

1. Right-click the ZIP file
2. Select **Extract All...**
3. Choose a destination folder (e.g., `C:\Program Files\AI-Agent-Console`)
4. Click **Extract**

#### Step 3: Verify Installation

Open Command Prompt or PowerShell and navigate to the installation directory:

```cmd
cd "C:\Program Files\AI-Agent-Console\ai-agent-console"
ai-agent-console.exe --help
```

You should see the help message with available commands.

#### Step 4: Add to PATH (Optional but Recommended)

To run `ai-agent-console` from anywhere:

**Using PowerShell (Run as Administrator):**
```powershell
$installPath = "C:\Program Files\AI-Agent-Console\ai-agent-console"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$installPath", "Machine")
```

**Using System Properties GUI:**
1. Press `Win + X` and select **System**
2. Click **Advanced system settings**
3. Click **Environment Variables**
4. Under **System variables**, select **Path** and click **Edit**
5. Click **New** and add: `C:\Program Files\AI-Agent-Console\ai-agent-console`
6. Click **OK** to save

After adding to PATH, you can run from anywhere:
```cmd
ai-agent-console --help
```

---

### Method 2: Python Installation via pip

**Note**: This method is not yet available. Package will be published to PyPI in a future release.

When available, installation will be:
```cmd
pip install ai-agent-console
```

---

### Method 3: Installation from Source

For developers or advanced users who want to run from source code.

#### Prerequisites

1. **Install Python 3.9+**
   - Download from: https://www.python.org/downloads/
   - During installation, check **"Add Python to PATH"**
   - Verify installation:
     ```cmd
     python --version
     pip --version
     ```

2. **Install Git** (Optional)
   - Download from: https://git-scm.com/download/win
   - Use default installation settings

#### Installation Steps

1. **Clone the Repository**

   ```cmd
   git clone https://github.com/your-org/ai-agent-console.git
   cd ai-agent-console
   ```

   Or download and extract the ZIP from GitHub.

2. **Create Virtual Environment** (Recommended)

   **Using PowerShell:**
   ```powershell
   .\setup_venv.ps1
   .\venv\Scripts\Activate.ps1
   ```

   **Using Command Prompt:**
   ```cmd
   setup_venv.bat
   venv\Scripts\activate.bat
   ```

3. **Install Dependencies**

   If you didn't use the setup script:
   ```cmd
   pip install -r requirements.txt
   ```

4. **Verify Installation**

   ```cmd
   python main.py --help
   ```

---

## Initial Configuration

After installation, you need to configure AI Agent Console.

### Step 1: Copy Configuration Template

Navigate to your installation directory and copy the configuration template:

**Binary Installation:**
```cmd
cd "C:\Program Files\AI-Agent-Console\ai-agent-console"
copy config.yaml my_config.yaml
```

**Source Installation:**
```cmd
cd ai-agent-console
copy config.yaml my_config.yaml
```

### Step 2: Edit Configuration

Open `my_config.yaml` in your favorite text editor (Notepad++, VS Code, etc.).

**Minimum Configuration:**

```yaml
# LLM Provider Configuration
ollama:
  enabled: true
  host: "http://localhost:11434"

# OR use OpenAI
openai:
  enabled: false
  api_key: ""  # Add your API key here

# Agent Configuration
agents:
  enabled: true
  auto_confirm: false  # Set to true to skip confirmations (USE WITH CAUTION!)

# Logging
logging:
  level: "INFO"
  file: "logs/app.log"
```

**Important Settings:**

- `auto_confirm`: Set to `true` to skip all confirmation prompts (dangerous!)
- `ollama.host`: Change if Ollama runs on a different host/port
- `openai.api_key`: Add your OpenAI API key if using OpenAI

### Step 3: Create Necessary Directories

The application will create these automatically, but you can create them manually:

```cmd
mkdir logs
mkdir memory_storage
mkdir projects
```

---

## First-Time Usage

### Check System Status

Verify everything is working:

**Binary Installation:**
```cmd
ai-agent-console.exe status
```

**Source Installation:**
```cmd
python main.py status
```

Expected output:
```
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║        🤖 AI AGENT CONSOLE 🤖                        ║
║                                                       ║
║     LLM-Powered Agent Management System              ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

Engine Status:
────────────────────────────────────────────────────────
✓ Engine initialized: True
✓ Configuration loaded: True
✓ Agents system: Available
✓ Tools system: Available

LLM Providers:
────────────────────────────────────────────────────────
  ✓ ollama
```

### List Available Agents

```cmd
ai-agent-console.exe agents
```

### List Available Tools

```cmd
ai-agent-console.exe tools
```

### Simple Query Test

**Using Binary:**
```cmd
ai-agent-console.exe run "What is the meaning of life?"
```

**Using Source:**
```cmd
python main.py run "What is the meaning of life?"
```

### Execute a Task with Agents

**Using Binary:**
```cmd
ai-agent-console.exe task "Create a hello world Python script"
```

**Using Source:**
```cmd
python main.py task "Create a hello world Python script"
```

---

## LLM Provider Setup

Choose and set up at least one LLM provider.

### Option A: Ollama (Local, Recommended)

Ollama provides local LLM inference without requiring cloud services.

#### Installation

1. **Download Ollama**
   - Visit: https://ollama.ai/download
   - Download the Windows installer
   - Run the installer (default settings are fine)

2. **Start Ollama**
   - Ollama starts automatically as a Windows service
   - Or run manually: `ollama serve`

3. **Pull Models**

   Open Command Prompt and pull models:

   ```cmd
   ollama pull llama3.2:latest
   ollama pull qwen2.5-coder:latest
   ollama pull deepseek-r1:latest
   ollama pull phi4:latest
   ```

   **Recommended Models:**
   - `llama3.2:latest` - General purpose (3-7 GB)
   - `qwen2.5-coder:latest` - Code generation (10-30 GB)
   - `deepseek-r1:latest` - Advanced reasoning (30-60 GB)
   - `phi4:latest` - Small, fast model (2-4 GB)

4. **Verify Ollama**

   ```cmd
   ollama list
   ```

   You should see your downloaded models.

5. **Configure AI Agent Console**

   Edit `my_config.yaml`:
   ```yaml
   ollama:
     enabled: true
     host: "http://localhost:11434"
     timeout: 120
   ```

#### Troubleshooting Ollama

**Ollama not responding:**
- Check if Ollama service is running: `tasklist | findstr ollama`
- Restart Ollama: `ollama serve`
- Check port 11434 is not blocked by firewall

**Models not loading:**
- Check available disk space
- Verify models: `ollama list`
- Try pulling a smaller model: `ollama pull phi4`

---

### Option B: OpenAI (Cloud)

Use OpenAI's cloud-based models (GPT-4, GPT-3.5, etc.).

#### Setup

1. **Get API Key**
   - Go to: https://platform.openai.com/api-keys
   - Create an account or log in
   - Click **Create new secret key**
   - Copy the key (starts with `sk-`)

2. **Configure AI Agent Console**

   Edit `my_config.yaml`:
   ```yaml
   openai:
     enabled: true
     api_key: "sk-your-api-key-here"
     base_url: "https://api.openai.com/v1"
     timeout: 120
   ```

   **Security Note**: Keep your API key secure! Never commit it to version control.

3. **Set via Environment Variable** (Recommended)

   Instead of putting the key in the config file:

   **PowerShell:**
   ```powershell
   $env:AI_AGENT_OPENAI__API_KEY = "sk-your-api-key-here"
   ```

   **Command Prompt:**
   ```cmd
   set AI_AGENT_OPENAI__API_KEY=sk-your-api-key-here
   ```

   **Permanent (System-wide):**
   1. Press `Win + X` → **System**
   2. **Advanced system settings** → **Environment Variables**
   3. Under **User variables**, click **New**
   4. Variable name: `AI_AGENT_OPENAI__API_KEY`
   5. Variable value: Your API key

4. **Verify Configuration**

   ```cmd
   ai-agent-console.exe run "Test message" --provider openai
   ```

---

### Option C: llama-cpp (Local, Advanced)

Direct GGUF model loading without a server.

#### Setup

1. **Install llama-cpp-python**

   ```cmd
   pip install llama-cpp-python
   ```

   **With GPU Support (NVIDIA):**
   ```cmd
   set CMAKE_ARGS=-DLLAMA_CUBLAS=on
   pip install llama-cpp-python
   ```

2. **Download GGUF Models**

   Download from Hugging Face (example):
   ```cmd
   mkdir models
   REM Download manually or use wget/curl
   REM Example: llama-2-7b-chat.Q4_K_M.gguf
   ```

3. **Configure AI Agent Console**

   Edit `my_config.yaml`:
   ```yaml
   llamacpp:
     enabled: true
     model_path: "./models/llama-2-7b-chat.Q4_K_M.gguf"
     context_size: 4096
     n_gpu_layers: 35  # Number of layers to offload to GPU (0 for CPU only)
     n_threads: 8      # CPU threads
     verbose: false
   ```

For more details, see [Llama-cpp Integration Guide](../LLAMA_CPP_INTEGRATION.md).

---

## Common Issues and Troubleshooting

### Issue: "Python is not recognized"

**Problem**: Python not found in PATH

**Solution**:
1. Reinstall Python with "Add to PATH" option checked
2. Or manually add Python to PATH:
   - Find Python installation: `C:\Users\<YourName>\AppData\Local\Programs\Python\Python311`
   - Add to PATH using System Properties

---

### Issue: "No LLM providers available"

**Problem**: No LLM provider configured or running

**Solution**:
1. For Ollama: Start Ollama service (`ollama serve`)
2. For OpenAI: Set API key in config or environment variable
3. Check configuration: `ai-agent-console.exe config --show`

---

### Issue: "Agent system not available"

**Problem**: Agents failed to load

**Solution**:
1. Check logs: `logs/app.log`
2. Verify installation: All files present in `agents/` directory
3. For binary installation: Ensure `agents/` folder is in the same directory as executable
4. Try reinstalling

---

### Issue: "Access Denied" when running executable

**Problem**: Windows SmartScreen or antivirus blocking execution

**Solution**:
1. **SmartScreen**: Click "More info" → "Run anyway"
2. **Antivirus**: Add exception for the executable
3. **UAC**: Run as administrator (right-click → "Run as administrator")

---

### Issue: "DLL load failed" or "Module not found"

**Problem**: Missing system dependencies

**Solution**:
1. Install Visual C++ Redistributable:
   - Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Run the installer
2. Restart computer
3. Try running the application again

---

### Issue: Slow performance or high memory usage

**Problem**: Large model or insufficient resources

**Solution**:
1. **Use smaller models**: Try `phi4` or `llama3.2:3b` instead of larger models
2. **Close other applications**: Free up RAM
3. **For Ollama**: Limit concurrent requests in config
4. **For llama-cpp**: Reduce context size or GPU layers

---

### Issue: Configuration not loading

**Problem**: Wrong config file location or syntax error

**Solution**:
1. Verify config file location: `config.yaml` in same directory as executable
2. Check YAML syntax: Use online YAML validator
3. Use `--config` flag to specify custom location:
   ```cmd
   ai-agent-console.exe --config "C:\path\to\my_config.yaml" status
   ```

---

## Uninstallation

### Binary Installation

1. **Remove Installation Directory**
   ```cmd
   rmdir /s "C:\Program Files\AI-Agent-Console"
   ```

2. **Remove from PATH** (if added)
   - System Properties → Environment Variables → Edit PATH
   - Remove the AI Agent Console entry

3. **Remove User Data** (Optional)
   ```cmd
   rmdir /s "%USERPROFILE%\.ai-agent-console"
   ```

### Source Installation

1. **Deactivate Virtual Environment**
   ```cmd
   deactivate
   ```

2. **Remove Directory**
   ```cmd
   cd ..
   rmdir /s ai-agent-console
   ```

### Ollama (Optional)

If you no longer need Ollama:

1. **Uninstall via Windows Settings**
   - Settings → Apps → Ollama → Uninstall

2. **Remove Models** (Optional)
   ```cmd
   rmdir /s "%USERPROFILE%\.ollama"
   ```

---

## Advanced Configuration

### Custom Configuration File

Use a custom configuration file:

```cmd
ai-agent-console.exe --config "C:\configs\custom.yaml" status
```

### Environment Variable Overrides

Override any configuration setting:

**PowerShell:**
```powershell
$env:AI_AGENT_OLLAMA__HOST = "http://192.168.1.100:11434"
$env:AI_AGENT_LOGGING__LEVEL = "DEBUG"
$env:AI_AGENT_AGENTS__AUTO_CONFIRM = "false"
```

**Command Prompt:**
```cmd
set AI_AGENT_OLLAMA__HOST=http://192.168.1.100:11434
set AI_AGENT_LOGGING__LEVEL=DEBUG
set AI_AGENT_AGENTS__AUTO_CONFIRM=false
```

### Proxy Configuration

If behind a corporate proxy:

**PowerShell:**
```powershell
$env:HTTP_PROXY = "http://proxy.company.com:8080"
$env:HTTPS_PROXY = "http://proxy.company.com:8080"
```

**Command Prompt:**
```cmd
set HTTP_PROXY=http://proxy.company.com:8080
set HTTPS_PROXY=http://proxy.company.com:8080
```

### Logging Configuration

Enable debug logging in `my_config.yaml`:

```yaml
logging:
  level: "DEBUG"
  file: "logs/app.log"
  console: true
  format: "detailed"
```

---

## Building Your Own Binary

If you want to build the Windows executable yourself:

### Prerequisites

1. Python 3.9+ installed
2. All project dependencies
3. PyInstaller

### Build Steps

**Using PowerShell (Recommended):**
```powershell
.\build_windows.ps1
```

**Using Command Prompt:**
```cmd
build_windows.bat
```

The build process will:
1. Create a virtual environment
2. Install all dependencies
3. Run PyInstaller
4. Create the executable in `dist/ai-agent-console/`
5. Package everything into a ZIP file

**Output:**
- Executable: `dist/ai-agent-console/ai-agent-console.exe`
- Package: `ai-agent-console-windows-<timestamp>.zip`

For detailed information, see the build script documentation.

---

## Additional Resources

- **Main Documentation**: [../README.md](../../README.md)
- **User Guide**: [user_guide.md](./user_guide.md)
- **Example Usage**: [EXAMPLE_USAGE.md](./EXAMPLE_USAGE.md)
- **Agent Catalog**: [../reference/AGENT_CATALOG.md](../reference/AGENT_CATALOG.md)
- **Troubleshooting**: Check `logs/app.log` for detailed error messages

## Support

For issues, questions, or contributions:
- **GitHub Issues**: https://github.com/your-org/ai-agent-console/issues
- **Documentation**: https://github.com/your-org/ai-agent-console/tree/main/docs
- **Email**: support@your-org.com

---

## Quick Reference Card

**Common Commands:**

```cmd
# Check status
ai-agent-console.exe status

# List agents
ai-agent-console.exe agents

# List tools
ai-agent-console.exe tools

# Simple query
ai-agent-console.exe run "Your question"

# Execute task
ai-agent-console.exe task "Create hello.py"

# Interactive mode
ai-agent-console.exe run --interactive

# Show configuration
ai-agent-console.exe config --show

# Get help
ai-agent-console.exe --help
ai-agent-console.exe <command> --help
```

**Configuration File:**
- Location: `config.yaml` (in same directory as executable)
- Custom location: Use `--config` flag

**Log Files:**
- Location: `logs/app.log`
- Debug mode: Set `logging.level: "DEBUG"` in config

---

**Last Updated**: 2025-10-14  
**Version**: 2.5.0
