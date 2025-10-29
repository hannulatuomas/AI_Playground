@echo off
echo Running Phase 9.3 Tests...
echo.

cd /d "%~dp0"

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
)

echo.
echo Testing Phase 9.3 Advanced Features...
python -c "from features.rag_advanced import reranking; reranking.print_feature_status()"

echo.
echo Phase 9.3 features verified!
pause
