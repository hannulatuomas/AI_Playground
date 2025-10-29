@echo off
REM Complete test suite for v1.4.0

echo ========================================
echo Running Complete v1.4.0 Test Suite
echo ========================================
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found
    exit /b 1
)

echo Running all v1.4.0 tests...
echo.

REM Run all tests with verbose output
python -m pytest tests/ -v --tb=short

echo.
echo ========================================
echo Test Summary
echo ========================================
echo.
echo Test files:
echo - test_workflow_engine.py (20 tests)
echo - test_file_splitter.py (12 tests)
echo - test_dead_code_detector.py (12 tests)
echo - test_automation_engine.py (10 tests)
echo - test_workflow_integration.py (15 tests)
echo - test_file_splitter_integration.py (11 tests)
echo - test_cli_commands.py (20 tests)
echo - test_v1.4.0_integration.py (13 tests)
echo.
echo Total: 113+ tests
echo.
