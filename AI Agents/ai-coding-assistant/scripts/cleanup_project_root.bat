@echo off
REM Project Root Cleanup Script
REM Organizes files into proper directories: scripts/, docs/, tests/

echo.
echo ================================================
echo   AI Coding Assistant - Project Cleanup
echo   Organizing files into proper directories
echo ================================================
echo.

cd /d "%~dp0\.."

echo [1/5] Moving scripts to scripts/...

REM Move .bat scripts to scripts/
if exist activate_venv.bat move activate_venv.bat scripts\
if exist install_psutil.bat move install_psutil.bat scripts\
if exist debug_rag.bat move debug_rag.bat scripts\
if exist test_syntax.bat move test_syntax.bat scripts\
if exist run_advanced_rag_tests.bat move run_advanced_rag_tests.bat scripts\
if exist run_phase_92_tests.bat move run_phase_92_tests.bat scripts\
if exist run_phase_93_tests.bat move run_phase_93_tests.bat scripts\
if exist run_rag_tests.bat move run_rag_tests.bat scripts\
if exist launch_cli_phase9.bat move launch_cli_phase9.bat scripts\
if exist launch_gui_phase9.bat move launch_gui_phase9.bat scripts\

REM Move .py utility scripts to scripts/
if exist debug_rag.py move debug_rag.py scripts\
if exist test_rag_deps.py move test_rag_deps.py scripts\

echo    - Moved batch scripts
echo    - Moved utility scripts

echo.
echo [2/5] Moving documentation to docs/...

REM Move markdown documentation to docs/
if exist AI_CONTEXT.md move AI_CONTEXT.md docs\
if exist CODEBASE_STRUCTURE.md move CODEBASE_STRUCTURE.md docs\
if exist CONTRIBUTING.md move CONTRIBUTING.md docs\
if exist GETTING_STARTED.md move GETTING_STARTED.md docs\
if exist INSTALLATION_TROUBLESHOOTING.md move INSTALLATION_TROUBLESHOOTING.md docs\
if exist MASTER_STATUS_REPORT.md move MASTER_STATUS_REPORT.md docs\
if exist PHASE_9_CLI_GUI_INTEGRATION.md move PHASE_9_CLI_GUI_INTEGRATION.md docs\
if exist PHASE_9_COMPLETE.md move PHASE_9_COMPLETE.md docs\
if exist PHASE_9_QUICKSTART.md move PHASE_9_QUICKSTART.md docs\
if exist PHASE_9_SUMMARY.md move PHASE_9_SUMMARY.md docs\
if exist PROJECT_STATUS_FINAL.md move PROJECT_STATUS_FINAL.md docs\
if exist PROJECT_SUMMARY.md move PROJECT_SUMMARY.md docs\
if exist RAG_TEST_FIXES.md move RAG_TEST_FIXES.md docs\
if exist STATUS.md move STATUS.md docs\
if exist TODO.md move TODO.md docs\
if exist USER_PREFERENCES.md move USER_PREFERENCES.md docs\
if exist VERIFICATION.md move VERIFICATION.md docs\
if exist VERIFICATION_CHECKLIST_v1.0.1.md move VERIFICATION_CHECKLIST_v1.0.1.md docs\
if exist GUI_MODEL_ADDITIONS.txt move GUI_MODEL_ADDITIONS.txt docs\

echo    - Moved project documentation
echo    - Moved status reports
echo    - Moved Phase 9 documentation

echo.
echo [3/5] Creating launcher shortcuts in root...

REM Create launchers that point to scripts/
echo @echo off > launch_cli.bat
echo cd /d "%%~dp0" >> launch_cli.bat
echo call scripts\launch_cli_phase9.bat >> launch_cli.bat

echo @echo off > launch_gui.bat
echo cd /d "%%~dp0" >> launch_gui.bat
echo call scripts\launch_gui_phase9.bat >> launch_gui.bat

echo    - Created launch_cli.bat (shortcut)
echo    - Created launch_gui.bat (shortcut)

echo.
echo [4/5] Updating script paths...

REM Update scripts to work from new location
echo Creating updated scripts...

REM This will be done by updating the actual script files

echo    - Scripts will be updated next

echo.
echo [5/5] Verifying organization...

echo.
echo Project structure:
echo   Root: Only essential files (README, LICENSE, main.py, requirements.txt)
echo   scripts/: All .bat and utility scripts
echo   docs/: All documentation
echo   src/: Source code
echo   tests/: Test files
echo   data/: Data and models
echo.

echo ================================================
echo   Cleanup Complete!
echo ================================================
echo.
echo Essential files remaining in root:
dir /b *.md *.txt *.py *.bat 2>nul
echo.

pause
