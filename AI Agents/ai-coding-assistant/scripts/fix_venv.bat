@echo off
REM Fix and activate venv for AI Coding Assistant
REM This script ensures venv is created correctly and packages are installed

echo.
echo ================================================================
echo  Fixing Virtual Environment for AI Coding Assistant
echo ================================================================
echo.

cd /d "%~dp0.."

REM Check if venv exists
if exist venv (
    echo Found existing venv
) else (
    echo Creating new venv...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create venv
        echo Make sure Python is installed correctly
        pause
        exit /b 1
    )
    echo ✓ venv created
)

echo.
echo Activating venv...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate venv
    echo Trying alternative activation method...
    call venv\Scripts\activate
)

REM Check if we're in venv
where python
echo.

echo Upgrading pip in venv...
python -m pip install --upgrade pip setuptools wheel

echo.
echo Installing core dependencies...
pip install colorama>=0.4.6
pip install regex>=2023.10.3

echo.
echo Installing RAG dependencies...
pip install numpy>=1.26.0
pip install sentence-transformers>=2.2.2
pip install chromadb>=0.4.18

echo.
echo ================================================================
echo  Verifying Installation
echo ================================================================
echo.

python test_rag_deps.py

echo.
echo ================================================================
echo  IMPORTANT: To use the venv, run this command first:
echo  venv\Scripts\activate
echo.
echo  Then run: python main.py
echo ================================================================
echo.

pause
