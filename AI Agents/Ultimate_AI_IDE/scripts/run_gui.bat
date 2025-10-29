@echo off
REM Run UAIDE GUI with virtual environment activated
REM Ultimate AI-Powered IDE - Graphical User Interface

REM Check if venv exists, if not run setup
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Running one-click setup...
    echo.
    call scripts\setup_venv.bat
    if errorlevel 1 (
        echo Setup failed. Cannot run UAIDE GUI.
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run UAIDE GUI
python -m src.ui.gui.main_window

REM Store exit code
set EXIT_CODE=%ERRORLEVEL%

REM Deactivate venv
call deactivate

exit /b %EXIT_CODE%
