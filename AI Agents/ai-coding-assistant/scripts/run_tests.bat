@echo off
REM Run tests for the AI Coding Assistant

cd /d "%~dp0.."

echo [INFO] Running tests...

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found.
    echo Please run 'scripts\setup.bat' first to set up the environment.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run tests
python tests\tests.py

if %errorlevel% neq 0 (
    echo [ERROR] Tests failed with error code: %errorlevel%
    pause
    exit /b %errorlevel%
)

echo [INFO] All tests passed successfully!
pause
