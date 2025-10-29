@echo off
echo ========================================
echo Building LocalAPI for Production
echo ========================================
echo.

echo Checking if node_modules exists...
if not exist "node_modules\" (
    echo ERROR: Dependencies not installed!
    echo Please run: scripts\setup.bat
    pause
    exit /b 1
)

echo Running TypeScript type check...
call npm run type-check
if %errorlevel% neq 0 (
    echo ERROR: Type check failed!
    pause
    exit /b 1
)

echo.
echo Building application...
call npm run build

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Output directory: dist\
echo.
pause
