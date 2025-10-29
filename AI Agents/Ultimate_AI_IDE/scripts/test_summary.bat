@echo off
REM Show test summary and statistics
REM Ultimate AI-Powered IDE

echo ========================================
echo UAIDE Test Summary
echo ========================================
echo.

REM Count test files
set TEST_COUNT=0
for %%f in (tests\test_*.py) do set /a TEST_COUNT+=1

echo Test Files: %TEST_COUNT%
echo.

REM List all test files
echo Test Modules:
for %%f in (tests\test_*.py) do (
    echo   - %%~nxf
)

echo.
echo ========================================
echo.
echo To run all tests:
echo   .\scripts\run_tests.bat
echo.
echo To run specific test:
echo   pytest tests/test_bloat_detector.py -v
echo.
echo To run with coverage:
echo   pytest tests/ --cov=src --cov-report=html
echo.
echo ========================================
