@echo off
REM Database Migration Script for AI Coding Assistant v1.7.0

cd /d "%~dp0.."

echo.
echo ========================================
echo  Database Migration Tool
echo  AI Coding Assistant v1.7.0
echo ========================================
echo.
echo This script will migrate your existing database to the new schema.
echo Your existing data will be preserved.
echo A backup will be created automatically.
echo.

pause

python scripts\migrate_db.py

echo.
echo ========================================
echo  Migration Complete
echo ========================================
echo.
echo You can now run the application:
echo   scripts\run.bat
echo   or
echo   python src\ui\cli.py
echo   python src\ui\gui_enhanced.py
echo.

pause
