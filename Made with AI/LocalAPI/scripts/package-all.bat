@echo off
echo ========================================
echo Packaging LocalAPI for All Platforms
echo ========================================
echo.

echo Checking if node_modules exists...
if not exist "node_modules\" (
    echo ERROR: Dependencies not installed!
    echo Please run: scripts\setup.bat
    pause
    exit /b 1
)

echo Building application...
call npm run build

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo Packaging for Windows...
call npm run package:win

echo.
echo Packaging for macOS...
call npm run package:mac

echo.
echo Packaging for Linux...
call npm run package:linux

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
echo Created installers:
dir /b release\*.exe 2>nul
dir /b release\*.dmg 2>nul
dir /b release\*.AppImage 2>nul
dir /b release\*.deb 2>nul
echo.
pause
