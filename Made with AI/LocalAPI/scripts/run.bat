@echo off
echo ========================================
echo Starting LocalAPI Development Server
echo ========================================
echo.

echo Checking if node_modules exists...
if not exist "node_modules\" (
    echo ERROR: Dependencies not installed!
    echo Please run: scripts\setup.bat
    echo Or: npm install
    pause
    exit /b 1
)

echo Starting Vite dev server and Electron...
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev
