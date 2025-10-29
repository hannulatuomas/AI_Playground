@echo off
REM Complete UAIDE Setup - One-Click Installation
REM Creates venv, installs dependencies, initializes database, creates directories
REM Ultimate AI-Powered IDE

echo ========================================
echo UAIDE - Complete Setup
echo ========================================
echo.

REM Check Python version
python --version 2>nul
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Step 1: Creating virtual environment...
if exist "venv\" (
    echo Virtual environment already exists, skipping creation.
) else (
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
)
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

echo Step 4: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    call deactivate
    pause
    exit /b 1
)
echo ✓ All dependencies installed successfully!
echo.

echo Step 5: Running full setup (directories, config, database)...
python scripts\setup.py
if errorlevel 1 (
    echo Error: Setup script failed
    call deactivate
    pause
    exit /b 1
)
echo.

echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo UAIDE is ready to use!
echo.
echo Next Steps:
echo   1. Download llama.cpp binary for your system
echo      See: docs\LLAMA_CPP_SETUP.md
echo   2. Place binary in llama-cpp/ directory
echo   3. Download an AI model (.gguf) and place in llama-cpp/models/
echo   4. Update config.json with model path
echo.
echo Common Commands:
echo   scripts\run_uaide.bat init          - Initialize UAIDE
echo   scripts\run_uaide.bat status        - Check status
echo   scripts\run_uaide.bat --help        - Show all commands
echo   scripts\run_tests.bat               - Run tests
echo.
echo To activate venv manually:
echo   venv\Scripts\activate.bat
echo.

call deactivate
pause
