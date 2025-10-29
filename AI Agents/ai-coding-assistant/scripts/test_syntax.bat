@echo off
echo Testing syntax...
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Just test if Python can parse the file
python -m py_compile src\ui\cli.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] No syntax errors found!
    echo.
) else (
    echo.
    echo [ERROR] Syntax errors detected!
    echo.
)

pause
