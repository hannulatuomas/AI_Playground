@echo off
REM Quick Fix Setup Script for Python 3.12 Compatibility
REM This script installs dependencies with Python 3.12 compatible versions

echo.
echo ============================================================
echo  AI Coding Assistant - Setup Fix for Python 3.12
echo ============================================================
echo.

REM Check Python version
python --version
echo.

echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
echo.

echo.
echo Choose installation option:
echo 1. Full install (Core + RAG semantic search)
echo 2. Core only (without RAG)
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Installing full dependencies including RAG...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Full installation failed.
        echo Trying core only installation...
        pip install -r requirements-core.txt
        echo.
        echo Core installed. You can try RAG separately with:
        echo   pip install -r requirements-rag.txt
    ) else (
        echo.
        echo ✓ Full installation successful!
    )
) else if "%choice%"=="2" (
    echo.
    echo Installing core dependencies only...
    pip install -r requirements-core.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Installation failed.
        echo See INSTALLATION_TROUBLESHOOTING.md for help.
    ) else (
        echo.
        echo ✓ Core installation successful!
        echo.
        echo Note: RAG features will not be available.
        echo To add RAG later, run:
        echo   pip install -r requirements-rag.txt
    )
) else (
    echo.
    echo Invalid choice. Please run again and select 1 or 2.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Installation Complete
echo ============================================================
echo.
echo Verifying installation...
python -c "import colorama; print('✓ colorama installed')" 2>nul || echo "✗ colorama not installed"
python -c "import regex; print('✓ regex installed')" 2>nul || echo "✗ regex not installed"
python -c "import numpy; print('✓ numpy installed')" 2>nul || echo "✗ numpy not installed (RAG disabled)"
python -c "import sentence_transformers; print('✓ sentence-transformers installed')" 2>nul || echo "✗ sentence-transformers not installed (RAG disabled)"
python -c "import chromadb; print('✓ chromadb installed')" 2>nul || echo "✗ chromadb not installed (RAG disabled)"

echo.
echo Next steps:
echo 1. Configure llama.cpp: python main.py --setup
echo 2. Run the assistant: python main.py
echo.
echo For troubleshooting, see: INSTALLATION_TROUBLESHOOTING.md
echo.

pause
