@echo off
echo ========================================
echo Running LocalAPI Tests
echo ========================================
echo.

echo Checking if node_modules exists...
if not exist "node_modules\" (
    echo ERROR: Dependencies not installed!
    echo Please run: scripts\setup.bat
    pause
    exit /b 1
)

echo Running Jest tests...
echo.

call npm test

if %errorlevel% neq 0 (
    echo.
    echo Tests failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo All tests passed!
echo ========================================
pause
