@echo off
REM Run all tests with coverage report
REM Ultimate AI-Powered IDE

echo ========================================
echo Running UAIDE Test Suite with Coverage
echo ========================================
echo.

REM Check if venv exists, if not run setup
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Running one-click setup...
    echo.
    call scripts\setup_venv.bat
    if errorlevel 1 (
        echo Setup failed. Cannot run tests.
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run pytest with coverage
echo.
echo Running tests with coverage...
echo.
python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

REM Store exit code
set TEST_EXIT_CODE=%ERRORLEVEL%

echo.
if %TEST_EXIT_CODE% EQU 0 (
    echo.
    echo Coverage report generated in htmlcov/index.html
    echo To view: start htmlcov\index.html
)

REM Deactivate venv
call deactivate

echo.
echo ========================================
if %TEST_EXIT_CODE% EQU 0 (
    echo Tests completed successfully!
) else (
    echo Tests failed with exit code: %TEST_EXIT_CODE%
)
echo ========================================
echo.

exit /b %TEST_EXIT_CODE%
