@echo off
REM Install Full Dependencies for Phase 9.2 and 9.3
REM This includes transformers and torch for CodeBERT
REM Version: 2.1.0

echo ============================================================
echo AI Coding Assistant - Full Dependencies Installation
echo ============================================================
echo.
echo This will install:
echo   - transformers (for CodeBERT embeddings)
echo   - torch (required by transformers)
echo.
echo These are large packages (~2GB download):
echo   - transformers: ~400MB
echo   - torch: ~1.5GB
echo.
echo This enables:
echo   - Phase 9.2: Full CodeBERT embeddings (no fallback)
echo   - Phase 9.3: Advanced cross-encoder reranking
echo   - test_similarity test will run (no more skips)
echo.
echo Requirements:
echo   - Good internet connection
echo   - 3GB+ free disk space
echo   - 5-10 minutes installation time
echo.
echo ============================================================
echo.

set /p "CONTINUE=Continue with installation? (y/n): "
if /i not "%CONTINUE%"=="y" (
    echo.
    echo Installation cancelled.
    echo.
    pause
    exit /b 0
)

echo.
echo ============================================================
echo Starting installation...
echo ============================================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install torch first (CPU version for compatibility)
echo [1/2] Installing torch (CPU version)...
echo This is the largest package (~1.5GB)...
echo.

set TORCH_INDEX=https://download.pytorch.org/whl/cpu
pip install torch --index-url %TORCH_INDEX%

if not %ERRORLEVEL%==0 (
    echo.
    echo [ERROR] Failed to install torch.
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] torch installed!
echo.

REM Then install transformers
echo [2/2] Installing transformers...
echo.
pip install transformers

if not %ERRORLEVEL%==0 (
    echo.
    echo [ERROR] Failed to install transformers.
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Successfully installed:
echo   * torch (CPU version)
echo   * transformers
echo.
echo The following features are now available:
echo   * Phase 9.2: Full CodeBERT embeddings
echo   * Phase 9.3: Advanced cross-encoder reranking
echo   * test_similarity test will now run
echo.
echo ============================================================
echo Next Steps
echo ============================================================
echo.
echo Run all tests to verify (no skips):
echo   python run_all_tests.py
echo.
echo OR run just Phase 9.2 tests:
echo   python tests\test_phase_92.py
echo.
echo Expected result:
echo   Ran 10 tests in ~30s
echo   OK (no skips!)
echo.
echo ============================================================
echo.
pause
