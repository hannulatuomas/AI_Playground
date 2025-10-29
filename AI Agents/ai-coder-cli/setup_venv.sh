
#!/bin/bash

# AI Agent Console - Virtual Environment Setup Script (Linux/Mac)
# 
# This script creates and configures a Python virtual environment for the AI Agent Console.
# 
# Usage:
#   ./setup_venv.sh [OPTIONS]
#
# Options:
#   --dev     Install development dependencies (includes testing, linting, etc.)
#   --help    Show this help message

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_DIR="venv"
PYTHON_CMD="python3"
MIN_PYTHON_VERSION="3.9"
INSTALL_DEV=false

# Parse command line arguments
for arg in "$@"; do
    case $arg in
        --dev)
            INSTALL_DEV=true
            shift
            ;;
        --help|-h)
            echo "AI Agent Console - Virtual Environment Setup"
            echo ""
            echo "Usage: ./setup_venv.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dev     Install development dependencies"
            echo "  --help    Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}AI Agent Console - Virtual Environment Setup${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Check if Python is installed
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed or not in PATH${NC}"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓${NC} Found Python $PYTHON_VERSION"

# Compare versions
if [ "$(printf '%s\n' "$MIN_PYTHON_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$MIN_PYTHON_VERSION" ]; then
    echo -e "${RED}Error: Python $MIN_PYTHON_VERSION or higher is required${NC}"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if venv already exists
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Warning: Virtual environment directory '$VENV_DIR' already exists${NC}"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Removing existing virtual environment...${NC}"
        rm -rf "$VENV_DIR"
    else
        echo -e "${YELLOW}Using existing virtual environment${NC}"
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo -e "${BLUE}Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv "$VENV_DIR"
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo ""
echo -e "${BLUE}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Upgrade pip, setuptools, and wheel
echo ""
echo -e "${BLUE}Upgrading pip, setuptools, and wheel...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓${NC} Core packages upgraded"

# Install dependencies
echo ""
if [ "$INSTALL_DEV" = true ]; then
    echo -e "${BLUE}Installing development dependencies...${NC}"
    pip install -r requirements-dev.txt
    echo -e "${GREEN}✓${NC} Development dependencies installed"
else
    echo -e "${BLUE}Installing production dependencies...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓${NC} Production dependencies installed"
fi

# Verify installation
echo ""
echo -e "${BLUE}Verifying installation...${NC}"
python -c "import typer; import pydantic; import yaml; import ollama" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Core dependencies verified"
else
    echo -e "${RED}Warning: Some core dependencies could not be imported${NC}"
fi

# Create activation helper script
cat > activate_venv.sh << 'EOF'
#!/bin/bash
# Quick activation script for the virtual environment
source venv/bin/activate
echo "Virtual environment activated!"
echo "To deactivate, run: deactivate"
EOF
chmod +x activate_venv.sh

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "To activate the virtual environment:"
echo -e "  ${BLUE}source venv/bin/activate${NC}"
echo "  or use the helper script:"
echo -e "  ${BLUE}source ./activate_venv.sh${NC}"
echo ""
echo "To deactivate the virtual environment:"
echo -e "  ${BLUE}deactivate${NC}"
echo ""
echo "To run the AI Agent Console:"
echo -e "  ${BLUE}python main.py${NC}"
echo ""

if [ "$INSTALL_DEV" = true ]; then
    echo "Development tools available:"
    echo "  - Testing: pytest"
    echo "  - Linting: flake8, pylint"
    echo "  - Formatting: black, isort"
    echo "  - Type checking: mypy"
    echo ""
fi
