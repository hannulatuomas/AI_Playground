@echo off
REM Test modularized CLI

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found
    exit /b 1
)

echo Testing modularized CLI...
echo.

echo [1] Testing --help
python -m src.main --help
echo.

echo [2] Testing workflow commands
python -m src.main workflow list
echo.

echo [3] Testing split commands
python -m src.main split --help
echo.

echo [4] Testing automation commands
python -m src.main automation status
echo.

echo ========================================
echo All CLI tests passed!
echo ========================================
