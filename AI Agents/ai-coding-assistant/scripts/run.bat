@echo off
REM Run the AI Coding Assistant

cd /d "%~dp0.."

echo [INFO] Starting AI Coding Assistant...

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found.
    echo Please run 'scripts\setup.bat' first to set up the environment.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application
python src\main.py %*

if %errorlevel% neq 0 (
    echo [ERROR] Application exited with error code: %errorlevel%
    pause
    exit /b %errorlevel%
)

echo [INFO] Application exited normally.
