@echo off
REM Activate venv and run AI Coding Assistant

cd /d "%~dp0.."

if not exist venv (
    echo ERROR: venv not found!
    echo Run scripts\fix_venv.bat first to create it
    pause
    exit /b 1
)

echo Activating venv...
call venv\Scripts\activate.bat

echo.
echo ================================================================
echo  AI Coding Assistant - venv activated
echo ================================================================
echo.
echo Python: 
python --version
echo.
echo To run the assistant: python main.py
echo To exit venv: deactivate
echo.
echo ================================================================
echo.

REM Keep the window open with venv activated
cmd /k
