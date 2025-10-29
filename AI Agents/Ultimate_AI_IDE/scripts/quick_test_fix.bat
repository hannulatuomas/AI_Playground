@echo off
REM Quick test of the fix

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found
    exit /b 1
)

echo Testing file splitter...
python -m src.main split detect --project .
echo.

echo Testing dead code detector...
python -m src.main deadcode detect --project .
echo.

echo Testing automation status...
python -m src.main automation status
echo.

echo All tests complete!
