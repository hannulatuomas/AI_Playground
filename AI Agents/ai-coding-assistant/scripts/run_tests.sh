#!/bin/bash
# Run tests for the AI Coding Assistant

cd "$(dirname "$0")/.."

echo "[INFO] Running tests..."

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "[ERROR] Virtual environment not found."
    echo "Please run 'scripts/setup.sh' first to set up the environment."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run tests
python tests/tests.py

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "[ERROR] Tests failed with error code: $EXIT_CODE"
    exit $EXIT_CODE
fi

echo "[INFO] All tests passed successfully!"
