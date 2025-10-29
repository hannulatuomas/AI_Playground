#!/bin/bash
# Run the AI Coding Assistant

cd "$(dirname "$0")/.."

echo "[INFO] Starting AI Coding Assistant..."

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "[ERROR] Virtual environment not found."
    echo "Please run 'scripts/setup.sh' first to set up the environment."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the application
python src/main.py "$@"

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "[ERROR] Application exited with error code: $EXIT_CODE"
    exit $EXIT_CODE
fi

echo "[INFO] Application exited normally."
