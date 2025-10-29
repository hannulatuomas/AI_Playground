@echo off
REM Install missing psutil dependency
REM Date: October 17, 2025

echo ================================================
echo   Installing Missing Dependencies
echo ================================================
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo Installing psutil for performance optimization...
pip install psutil>=5.9.0

echo.
echo ================================================
echo   Installation Complete
echo ================================================
echo.
echo psutil has been installed!
echo.
echo Now run: run_rag_tests.bat
echo.
pause
