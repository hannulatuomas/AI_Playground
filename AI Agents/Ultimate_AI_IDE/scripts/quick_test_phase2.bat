@echo off
REM Quick test for Phase 2 modules only
REM Runs tests for Project Manager, Code Generator, and Tester

echo ========================================
echo Quick Test - Phase 2 Features
echo ========================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found!
    echo Please run setup_venv.bat first
    pause
    exit /b 1
)

echo Testing Phase 2 modules:
echo   - Project Manager
echo   - Code Generator  
echo   - Tester
echo.

REM Run only Phase 2 tests
python -m pytest tests/test_project_manager.py tests/test_code_generator.py tests/test_tester.py -v --tb=short

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Phase 2 tests passed!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Phase 2 tests failed!
    echo ========================================
    exit /b 1
)

pause
