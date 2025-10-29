@echo off
REM Demo script for v1.4.0 features
REM Demonstrates: Workflow Engine, File Splitter, Dead Code Detector, Automation Engine

echo ========================================
echo UAIDE v1.4.0 Feature Demo
echo ========================================
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found
    echo Please run scripts\setup_venv.bat first
    exit /b 1
)

echo [Demo 1] Workflow Engine
echo -------------------------
echo.
echo Listing available workflow templates...
python -m src.main workflow list
echo.
pause

echo.
echo Showing workflow template info...
python -m src.main workflow info feature_implementation
echo.
pause

echo.
echo [Demo 2] File Splitter
echo ----------------------
echo.
echo Detecting large files in project...
python -m src.main split detect --project .
echo.
pause

echo.
echo [Demo 3] Dead Code Detection
echo ----------------------------
echo.
echo Analyzing project for dead code...
python -m src.main deadcode detect --project .
echo.
pause

echo.
echo [Demo 4] Automation Engine
echo --------------------------
echo.
echo Showing automation engine status...
python -m src.main automation status
echo.
pause

echo.
echo Listing automation triggers...
python -m src.main automation triggers
echo.
pause

echo.
echo ========================================
echo Demo completed!
echo ========================================
echo.
echo Try these commands yourself:
echo   uaide workflow list
echo   uaide workflow execute feature_implementation --project ./my_project
echo   uaide split detect
echo   uaide deadcode detect
echo   uaide automation status
echo.
