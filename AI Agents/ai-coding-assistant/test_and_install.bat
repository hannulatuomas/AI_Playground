@echo off
REM Install pytest and run all tests with better error handling
REM Version: 2.1.0

echo ============================================================
echo Installing pytest and running all tests
echo ============================================================
echo.

REM Check if pytest is installed
python -c "import pytest" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing pytest...
    pip install pytest
    echo.
)

echo Running all tests...
echo.

REM Run all tests
python run_all_tests.py

echo.
pause
