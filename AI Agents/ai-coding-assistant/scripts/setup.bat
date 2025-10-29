@echo off
REM ========================================================================
REM AI Coding Assistant - Windows Setup Script
REM ========================================================================
REM This script sets up the development environment for the AI Coding Assistant
REM Python version: 3.12.10
REM Version: 2.1.0
REM ========================================================================

setlocal enabledelayedexpansion

cd /d "%~dp0.."

echo.
echo ========================================
echo AI Coding Assistant - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.12.10 from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check Python version
echo [INFO] Checking Python version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Found Python version: %PYTHON_VERSION%

REM Verify Python version is 3.12
echo %PYTHON_VERSION% | findstr /C:"3.12" >nul
if errorlevel 1 (
    echo [WARNING] Expected Python 3.12.10, but found %PYTHON_VERSION%
    echo The application may still work, but compatibility is best with Python 3.12.10
    echo.
)

REM Check if virtual environment exists
if exist "venv\" (
    echo [INFO] Virtual environment already exists.
    echo [INFO] To recreate it, delete the 'venv' folder and run this script again.
) else (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip.
    pause
    exit /b 1
)

REM Install requirements
echo [INFO] Installing requirements...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install requirements.
        pause
        exit /b 1
    )
    echo [SUCCESS] Requirements installed.
) else (
    echo [WARNING] requirements.txt not found. Skipping package installation.
)

REM Ask about full dependencies
echo.
echo ========================================
echo Optional: Full Dependencies
echo ========================================
echo.
echo The application is now functional with basic dependencies.
echo.
echo Would you like to install FULL dependencies for advanced features?
echo This includes:
echo   - transformers (400MB) - for CodeBERT embeddings
echo   - torch (1.5GB) - for neural network models
echo.
echo Benefits:
echo   + Phase 9.2: Full CodeBERT code similarity
echo   + Phase 9.3: Advanced cross-encoder reranking
echo   + All tests pass without skips
echo.
echo Drawbacks:
echo   - Large download (2GB)
echo   - Takes 5-10 minutes to install
echo   - Requires 3GB+ disk space
echo.
set /p INSTALL_FULL=Install full dependencies? (y/n): 

if /i "!INSTALL_FULL!"=="y" (
    echo.
    echo [INFO] Installing full dependencies...
    echo This may take 5-10 minutes...
    echo.
    
    REM Install torch first (CPU version)
    echo [INFO] Installing torch CPU version...
    set TORCH_URL=https://download.pytorch.org/whl/cpu
    pip install torch --index-url !TORCH_URL!
    if !ERRORLEVEL! NEQ 0 (
        echo [ERROR] Failed to install torch.
        echo You can install it manually later with: install_full_deps.bat
        goto skip_full_deps
    )
    
    REM Install transformers
    echo [INFO] Installing transformers...
    pip install transformers
    if !ERRORLEVEL! NEQ 0 (
        echo [ERROR] Failed to install transformers.
        echo You can install it manually later with: install_full_deps.bat
        goto skip_full_deps
    )
    
    echo.
    echo [SUCCESS] Full dependencies installed!
    echo All Phase 9.2 and 9.3 features are now available.
    echo.
) else (
    echo.
    echo [INFO] Skipping full dependencies.
    echo You can install them later by running: install_full_deps.bat
    echo.
)

:skip_full_deps

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "data\db\" mkdir data\db
if not exist "data\models\" mkdir data\models
if not exist "logs\" mkdir logs

REM Check for llama.cpp
echo [INFO] Checking for llama.cpp...
if exist "llama.cpp\llama-cli.exe" (
    echo [SUCCESS] llama.cpp found at llama.cpp\llama-cli.exe
) else (
    echo [WARNING] llama.cpp not found at expected location: llama.cpp\llama-cli.exe
    echo.
    echo Please download llama.cpp from: https://github.com/ggerganov/llama.cpp
    echo And extract it to the llama.cpp folder in this directory.
    echo.
)

REM Check for models
echo [INFO] Checking for models...
if exist "data\models\*.gguf" (
    echo [SUCCESS] Found GGUF models in data\models\
    dir /b data\models\*.gguf
) else (
    echo [WARNING] No GGUF models found in data\models\
    echo.
    echo Please download a model and place it in data\models\
    echo Recommended: https://huggingface.co/models?search=gguf
    echo.
)

REM Create config file if it doesn't exist
if not exist "data\config.json" (
    if exist "data\config.json.template" (
        echo [INFO] Creating default config.json from template...
        copy data\config.json.template data\config.json >nul
        echo [SUCCESS] config.json created. Please edit it to configure your model path.
    ) else (
        echo [WARNING] config.json.template not found. Skipping config creation.
    )
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Your AI Coding Assistant is ready!
echo.
if /i "!INSTALL_FULL!"=="y" (
    echo Installed: Full dependencies - all features enabled
) else (
    echo Installed: Basic dependencies - Phase 11.1 ready
    echo To enable all features later: install_full_deps.bat
)
echo.
echo Next steps:
echo 1. Ensure llama.cpp is in the llama.cpp\ folder
echo 2. Place your GGUF model in data\models\
echo 3. Edit data\config.json to configure your model path
echo 4. Run scripts\run.bat to start the application
echo 5. Run run_all_tests.bat to run all tests
echo.
echo For more information, see README.md
echo.

endlocal
pause
