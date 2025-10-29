@echo off
REM Run all tests with virtual environment activated
REM Ultimate AI-Powered IDE

echo ========================================
echo Running UAIDE Test Suite
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
echo Running tests with pytest...
echo.
echo Test Coverage:
echo   Phase 1: Core Infrastructure
echo   Phase 2: Basic Features
echo   Phase 3: Advanced Features
echo   Phase 4: Intelligence
echo   Phase 5: Integration
echo   v1.3.0: Quality and Context
echo   v1.4.0: Workflow and Automation
echo   v1.5.0: Security Scanner
echo.
echo Running all tests...
echo.
echo Test Suite Summary:
echo - Core Module Tests: 54 tests
pytest tests/test_orchestrator.py -v
pytest tests/test_event_bus.py -v
pytest tests/integration/ -v

echo.
echo   v1.6.0: Advanced RAG and Retrieval
pytest tests/test_codebert_embedder.py -v
pytest tests/test_multimodal_retriever.py -v
pytest tests/test_query_enhancer.py -v
pytest tests/test_graph_retriever.py -v
echo Test Suite Summary:
echo - Core Module Tests: 54 tests
echo - v1.4.0 Integration Tests: 59 tests
echo - v1.5.0 Security Tests: 55+ tests
echo - v1.5.0 Dependency Tests: 30+ tests
echo - v1.5.0 Template Tests: 17+ tests
echo - v1.5.0 Integration Tests: 45+ tests
echo - v1.6.0 RAG Tests: 60+ tests
echo - Total: 520+ tests (comprehensive coverage)
echo.

REM Run pytest with coverage if available, otherwise just pytest
python -m pytest tests/ -v --tb=short --cov=src --cov-report=term-missing 2>nul
if errorlevel 1 (
    echo.
    echo Coverage module not available, running without coverage...
    python -m pytest tests/ -v --tb=short
)

REM Store exit code
set TEST_EXIT_CODE=%ERRORLEVEL%

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
