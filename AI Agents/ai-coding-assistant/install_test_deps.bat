@echo off
REM Quick Fix for Test Dependencies
REM Installs missing pytest and runs all tests

echo ============================================================
echo AI Coding Assistant - Test Setup
echo ============================================================
echo.

echo Installing missing test dependencies...
echo.

REM Install pytest
pip install pytest

echo.
echo ============================================================
echo Dependencies installed successfully!
echo ============================================================
echo.
echo Running all tests...
echo.

REM Run all tests
call run_all_tests.bat

echo.
echo ============================================================
echo Setup complete!
echo ============================================================
echo.
pause
