#!/bin/bash
# Kali Linux MCP Server - Setup Script
# This script helps set up the MCP server on your system

set -e  # Exit on error

echo "=========================================="
echo "Kali Linux MCP Server - Setup"
echo "Version 4.0.0"
echo "=========================================="
echo ""

# Check Python version
echo "[1/5] Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✓ Python3 found: $PYTHON_VERSION"
else
    echo "✗ Python3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check pip
echo ""
echo "[2/5] Checking pip..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    echo "✓ pip3 found: $PIP_VERSION"
else
    echo "✗ pip3 not found. Installing..."
    sudo apt update && sudo apt install -y python3-pip
fi

# Install MCP
echo ""
echo "[3/5] Installing MCP..."
pip3 install mcp 2>&1 | grep -i "success\|installed\|requirement" || true
echo "✓ MCP package ready"

# Check optional dependencies
echo ""
echo "[4/5] Checking optional system tools..."
TOOLS=(curl wget nc nmap dig netstat tar zip gzip bzip2 xz)
MISSING=()

for tool in "${TOOLS[@]}"; do
    if command -v $tool &> /dev/null; then
        echo "  ✓ $tool"
    else
        echo "  ✗ $tool (missing)"
        MISSING+=($tool)
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo ""
    echo "Some optional tools are missing. Install them with:"
    echo "  sudo apt update"
    echo "  sudo apt install -y curl wget netcat-traditional nmap dnsutils net-tools tar zip gzip bzip2 xz-utils"
fi

# Test import
echo ""
echo "[5/5] Testing server..."
cd "$(dirname "$0")"
if python3 -c "from tools import register_shell_tools; print('✓ Import successful')" 2>&1; then
    echo "✓ Server modules load correctly"
else
    echo "✗ Import failed. Check dependencies."
    exit 1
fi

# Summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the server:"
echo "  python3 server.py"
echo ""
echo "Documentation:"
echo "  README.md          - Full documentation"
echo "  QUICK_REFERENCE.md - Quick reference guide"
echo "  PROJECT_SUMMARY.md - Project overview"
echo ""
echo "Total Tools: 37"
echo "Categories: 7"
echo "Version: 4.0.0"
echo ""
echo "Happy automating! 🚀"
