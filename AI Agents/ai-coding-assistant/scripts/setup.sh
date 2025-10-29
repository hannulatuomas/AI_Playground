#!/bin/bash
# ========================================================================
# AI Coding Assistant - Linux/Mac Setup Script
# ========================================================================
# This script sets up the development environment for the AI Coding Assistant
# Python version: 3.12.10
# ========================================================================

cd "$(dirname "$0")/.."

echo ""
echo "========================================"
echo "AI Coding Assistant - Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo "Please install Python 3.12.10"
    exit 1
fi

# Check Python version
echo "[INFO] Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "[INFO] Found Python version: $PYTHON_VERSION"

# Verify Python version is 3.12
if [[ ! "$PYTHON_VERSION" =~ ^3\.12 ]]; then
    echo "[WARNING] Expected Python 3.12.10, but found $PYTHON_VERSION"
    echo "The application may still work, but compatibility is best with Python 3.12.10"
    echo ""
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "[INFO] Virtual environment already exists."
    echo "[INFO] To recreate it, delete the 'venv' folder and run this script again."
else
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment."
        exit 1
    fi
    echo "[SUCCESS] Virtual environment created."
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment."
    exit 1
fi

# Upgrade pip
echo "[INFO] Upgrading pip..."
python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to upgrade pip."
    exit 1
fi

# Install requirements
echo "[INFO] Installing requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install requirements."
        exit 1
    fi
    echo "[SUCCESS] Requirements installed."
else
    echo "[WARNING] requirements.txt not found. Skipping package installation."
fi

# Create necessary directories
echo "[INFO] Creating necessary directories..."
mkdir -p data/db
mkdir -p data/models
mkdir -p logs

# Check for llama.cpp
echo "[INFO] Checking for llama.cpp..."
if [ -f "llama.cpp/llama-cli" ] || [ -f "llama.cpp/main" ]; then
    echo "[SUCCESS] llama.cpp found"
else
    echo "[WARNING] llama.cpp not found at expected location"
    echo ""
    echo "Please download llama.cpp from: https://github.com/ggerganov/llama.cpp"
    echo "And place the executable in the llama.cpp folder."
    echo ""
fi

# Check for models
echo "[INFO] Checking for models..."
if ls data/models/*.gguf 1> /dev/null 2>&1; then
    echo "[SUCCESS] Found GGUF models in data/models/"
    ls -1 data/models/*.gguf
else
    echo "[WARNING] No GGUF models found in data/models/"
    echo ""
    echo "Please download a model (e.g., Llama 3 7B or 13B) and place it in data/models/"
    echo "Recommended: https://huggingface.co/models?search=gguf"
    echo ""
fi

# Create config file if it doesn't exist
if [ ! -f "data/config.json" ]; then
    if [ -f "data/config.json.template" ]; then
        echo "[INFO] Creating default config.json from template..."
        cp data/config.json.template data/config.json
        echo "[SUCCESS] config.json created. Please edit it to configure your model path."
    else
        echo "[WARNING] config.json.template not found. Skipping config creation."
    fi
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Ensure llama.cpp is in the llama.cpp/ folder"
echo "2. Place your GGUF model in data/models/"
echo "3. Edit data/config.json to configure your model path"
echo "4. Run 'scripts/run.sh' to start the application"
echo "5. Run 'scripts/run_tests.sh' to run all tests"
echo ""
echo "For more information, see README.md"
echo ""
