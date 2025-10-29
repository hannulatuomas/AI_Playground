@echo off
REM Quick verification script to test all fixes

cd /d "%~dp0.."

echo.
echo ========================================
echo AI Coding Assistant - Quick Verification
echo ========================================
echo.

echo [TEST 1] Checking if application can import modules...
python -c "import sys; sys.path.insert(0, 'src'); from features import CodeGenerator, Debugger, LanguageSupport; from ui import CLI; print('[PASS] All imports successful')" 2>nul
if %errorlevel% neq 0 (
    echo [FAIL] Import test failed
    goto :failed
)

echo [TEST 2] Checking if tests can import modules...
python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('src'))); from core import LLMInterface; from features import CodeGenerator; print('[PASS] Test imports work')" 2>nul
if %errorlevel% neq 0 (
    echo [FAIL] Test import failed
    goto :failed
)

echo [TEST 3] Checking setup script exists...
if exist "scripts\setup.bat" (
    echo [PASS] scripts\setup.bat exists
) else (
    echo [FAIL] scripts\setup.bat missing
    goto :failed
)

echo [TEST 4] Checking run script exists...
if exist "scripts\run.bat" (
    echo [PASS] scripts\run.bat exists
) else (
    echo [FAIL] scripts\run.bat missing
    goto :failed
)

echo [TEST 5] Checking test runner exists...
if exist "scripts\run_tests.bat" (
    echo [PASS] scripts\run_tests.bat exists
) else (
    echo [FAIL] scripts\run_tests.bat missing
    goto :failed
)

echo.
echo ========================================
echo All Verification Tests PASSED!
echo ========================================
echo.
echo Your AI Coding Assistant is ready!
echo.
echo Next steps:
echo 1. Run: scripts\migrate_db.bat (if upgrading)
echo 2. Start using: scripts\run.bat
echo 3. Run tests: scripts\run_tests.bat
echo.
goto :end

:failed
echo.
echo ========================================
echo Some Tests FAILED
echo ========================================
echo.
echo Please review the errors above.
echo.

:end
pause
