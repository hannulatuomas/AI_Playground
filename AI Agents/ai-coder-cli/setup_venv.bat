
@echo off
REM AI Agent Console - Virtual Environment Setup Script (Windows CMD)
REM
REM This script creates and configures a Python virtual environment for the AI Agent Console.
REM
REM Usage:
REM   setup_venv.bat [OPTIONS]
REM
REM Options:
REM   --dev     Install development dependencies
REM   --help    Show this help message

setlocal enabledelayedexpansion

REM Configuration
set VENV_DIR=venv
set PYTHON_CMD=python
set MIN_PYTHON_VERSION=3.9
set INSTALL_DEV=0

REM Parse command line arguments
:parse_args
if "%~1"=="" goto start_setup
if /i "%~1"=="--dev" (
    set INSTALL_DEV=1
    shift
    goto parse_args
)
if /i "%~1"=="--help" (
    echo AI Agent Console - Virtual Environment Setup
    echo.
    echo Usage: setup_venv.bat [OPTIONS]
    echo.
    echo Options:
    echo   --dev     Install development dependencies
    echo   --help    Show this help message
    exit /b 0
)
if /i "%~1"=="-h" (
    echo AI Agent Console - Virtual Environment Setup
    echo.
    echo Usage: setup_venv.bat [OPTIONS]
    echo.
    echo Options:
    echo   --dev     Install development dependencies
    echo   --help    Show this help message
    exit /b 0
)
echo Unknown option: %~1
echo Use --help for usage information
exit /b 1

:start_setup
echo ==========================================
echo AI Agent Console - Virtual Environment Setup
echo ==========================================
echo.

REM Check if Python is installed
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found Python %PYTHON_VERSION%

REM Check if venv already exists
if exist "%VENV_DIR%" (
    echo Warning: Virtual environment directory '%VENV_DIR%' already exists
    set /p RECREATE="Do you want to recreate it? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q "%VENV_DIR%"
    ) else (
        echo Using existing virtual environment
        goto activate_venv
    )
)

REM Create virtual environment
echo.
echo Creating virtual environment...
%PYTHON_CMD% -m venv %VENV_DIR%
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    exit /b 1
)
echo [OK] Virtual environment created

:activate_venv
REM Activate virtual environment
echo.
echo Activating virtual environment...
call %VENV_DIR%\Scripts\activate.bat
echo [OK] Virtual environment activated

REM Upgrade pip, setuptools, and wheel
echo.
echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
echo [OK] Core packages upgraded

REM Install dependencies
echo.
if %INSTALL_DEV%==1 (
    echo Installing development dependencies...
    pip install -r requirements-dev.txt
    echo [OK] Development dependencies installed
) else (
    echo Installing production dependencies...
    pip install -r requirements.txt
    echo [OK] Production dependencies installed
)

REM Verify installation
echo.
echo Verifying installation...
python -c "import typer; import pydantic; import yaml; import ollama" 2>nul
if errorlevel 1 (
    echo Warning: Some core dependencies could not be imported
) else (
    echo [OK] Core dependencies verified
)

REM Create activation helper script
echo @echo off > activate_venv.bat
echo REM Quick activation script for the virtual environment >> activate_venv.bat
echo call venv\Scripts\activate.bat >> activate_venv.bat
echo echo Virtual environment activated! >> activate_venv.bat
echo echo To deactivate, run: deactivate >> activate_venv.bat

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To activate the virtual environment:
echo   venv\Scripts\activate.bat
echo   or use the helper script:
echo   activate_venv.bat
echo.
echo To deactivate the virtual environment:
echo   deactivate
echo.
echo To run the AI Agent Console:
echo   python main.py
echo.

if %INSTALL_DEV%==1 (
    echo Development tools available:
    echo   - Testing: pytest
    echo   - Linting: flake8, pylint
    echo   - Formatting: black, isort
    echo   - Type checking: mypy
    echo.
)

endlocal
