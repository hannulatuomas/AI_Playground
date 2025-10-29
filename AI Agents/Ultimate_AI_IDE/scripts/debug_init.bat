@echo off
REM Debug initialization

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found
    exit /b 1
)

echo Testing UAIDE initialization...
python -c "from src.core.orchestrator import UAIDE; print('Creating UAIDE...'); u = UAIDE(); print('Success!')"
