@echo off
REM Cleanup Script - Remove old scripts from project root

cd /d "%~dp0.."

echo.
echo ========================================
echo Cleanup Old Scripts from Root
echo ========================================
echo.
echo This will DELETE the following files from project root:
echo - setup.bat
echo - setup.sh
echo - run.bat
echo - run.sh
echo - run_tests.bat
echo - run_tests.sh
echo - migrate_db.bat
echo - migrate_db.py
echo - reset_db.bat
echo - verify_fixes.bat
echo.
echo These files have been moved to scripts/ folder.
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Removing old scripts...
echo.

REM Remove old batch/shell scripts
if exist "setup.bat" (
    del setup.bat
    echo ✓ Removed setup.bat
)

if exist "setup.sh" (
    del setup.sh
    echo ✓ Removed setup.sh
)

if exist "run.bat" (
    del run.bat
    echo ✓ Removed run.bat
)

if exist "run.sh" (
    del run.sh
    echo ✓ Removed run.sh
)

if exist "run_tests.bat" (
    del run_tests.bat
    echo ✓ Removed run_tests.bat
)

if exist "run_tests.sh" (
    del run_tests.sh
    echo ✓ Removed run_tests.sh
)

if exist "migrate_db.bat" (
    del migrate_db.bat
    echo ✓ Removed migrate_db.bat
)

if exist "migrate_db.py" (
    del migrate_db.py
    echo ✓ Removed migrate_db.py
)

if exist "reset_db.bat" (
    del reset_db.bat
    echo ✓ Removed reset_db.bat
)

if exist "verify_fixes.bat" (
    del verify_fixes.bat
    echo ✓ Removed verify_fixes.bat
)

echo.
echo ========================================
echo Cleanup Complete!
echo ========================================
echo.
echo All old scripts have been removed from project root.
echo.
echo Use the new scripts in scripts/ folder:
echo - scripts\setup.bat
echo - scripts\run.bat
echo - scripts\run_tests.bat
echo - scripts\migrate_db.bat
echo - scripts\reset_db.bat
echo.

pause
