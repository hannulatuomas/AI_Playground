@echo off
REM Launch GUI with Phase 9 Advanced RAG Features

echo.
echo ================================================
echo   AI Coding Assistant - Phase 9 GUI
echo   Advanced RAG with 8 powerful features
echo ================================================
echo.

REM Change to project root (parent of scripts/)
cd /d "%~dp0\.."

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Launch GUI
python src\ui\gui_phase9.py

pause
