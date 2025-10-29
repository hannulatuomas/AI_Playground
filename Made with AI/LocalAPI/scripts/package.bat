@echo off
echo ========================================
echo Packaging LocalAPI for Windows
echo ========================================
echo.

echo Checking if node_modules exists...
if not exist "node_modules\" (
    echo ERROR: Dependencies not installed!
    echo Please run: scripts\setup.bat
    pause
    exit /b 1
)

echo Building and packaging application...
echo This may take several minutes...
echo.

call npm run package:win

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Packaging failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Packaging completed successfully!
echo ========================================
echo.
echo Output directory: release\
echo.
pause
