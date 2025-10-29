@echo off
echo Running RAG Tests...
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
echo Running tests...
python tests\test_rag.py

echo.
echo Tests complete!
pause
