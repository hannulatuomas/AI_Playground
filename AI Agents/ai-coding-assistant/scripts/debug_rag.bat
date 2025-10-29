@echo off
echo Running RAG Debug Script...
echo.

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo Warning: Virtual environment not found, using global Python
)

echo.
echo Running debug...
python debug_rag.py

echo.
pause
