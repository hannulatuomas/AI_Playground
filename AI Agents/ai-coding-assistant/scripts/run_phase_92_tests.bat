@echo off
echo Running Phase 9.2 Tests...
echo.

cd /d "%~dp0"

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
)

echo.
echo Running tests...
python tests\test_phase_92.py

echo.
echo Tests complete!
pause
