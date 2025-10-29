@echo off
REM Debug file split command

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found
    exit /b 1
)

echo Testing split detect command...
echo.

python -c "print('1. Importing...'); from src.core.orchestrator import UAIDE; print('2. Creating UAIDE...'); u = UAIDE(); print('3. Calling detect_large_files...'); result = u.detect_large_files('.'); print('4. Done!'); print(result.message)"

echo.
echo Test complete!
