@echo off
REM Reset Database - Deletes existing database (will be recreated with new schema)

cd /d "%~dp0.."

echo.
echo ========================================
echo  Database Reset Tool
echo  AI Coding Assistant v1.7.0
echo ========================================
echo.
echo WARNING: This will delete your learning history!
echo A backup will be created first.
echo.
echo Press Ctrl+C to cancel, or
pause

python scripts\migrate_db.py --reset

echo.
echo ========================================
echo  Reset Complete
echo ========================================
echo.
echo The database has been reset.
echo A new database will be created automatically when you run the app.
echo.
echo Run the application:
echo   scripts\run.bat
echo   or
echo   python src\ui\cli.py
echo   python src\ui\gui_enhanced.py
echo.

pause
