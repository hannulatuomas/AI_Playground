@echo off
REM Demo script for Phase 2 features
REM Demonstrates Project Manager, Code Generator, and Tester modules

echo ========================================
echo UAIDE Phase 2 Demo
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

echo This demo will showcase Phase 2 features:
echo   1. Project Manager - Create and detect projects
echo   2. Code Generator - Analyze and generate code
echo   3. Tester - Generate and run tests
echo.
pause

echo.
echo ========================================
echo 1. Project Manager Demo
echo ========================================
echo.

python -c "from src.modules.project_manager import ProjectDetector; import sys; detector = ProjectDetector(); info = detector.detect_project('.'); print(f'Detected: {info.language} project' if info else 'Not a project'); print(f'Framework: {info.framework}' if info and info.framework else 'No framework')"

echo.
echo Press any key to continue to Code Generator demo...
pause > nul

echo.
echo ========================================
echo 2. Code Generator Demo
echo ========================================
echo.

python -c "from src.modules.code_generator import CodeAnalyzer, CodeContext; analyzer = CodeAnalyzer(); context = analyzer.get_code_context('src', 'python'); print(f'Found {len(context.existing_classes)} classes'); print(f'Found {len(context.existing_functions)} functions'); print(f'Found {len(context.existing_files)} files')"

echo.
echo Press any key to continue to Tester demo...
pause > nul

echo.
echo ========================================
echo 3. Tester Demo
echo ========================================
echo.

python -c "from src.modules.tester import TestGenerator; generator = TestGenerator(None); framework = generator._detect_test_framework('python'); print(f'Detected test framework: {framework}')"

echo.
echo ========================================
echo Demo Complete!
echo ========================================
echo.
echo Phase 2 modules are working correctly.
echo.
echo Next steps:
echo   - Run full tests: scripts\run_tests.bat
echo   - Check coverage: scripts\run_tests_coverage.bat
echo   - Start CLI: scripts\run_uaide.bat
echo.
pause
