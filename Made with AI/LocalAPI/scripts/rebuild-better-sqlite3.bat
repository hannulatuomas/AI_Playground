@echo off
echo ========================================
echo Rebuilding better-sqlite3 for Electron
echo ========================================
echo.

REM Set Visual Studio environment variables that node-gyp looks for
set "VSINSTALLDIR=C:\Program Files\Microsoft Visual Studio\2022\Professional\"
set "VCINSTALLDIR=C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\"
set GYP_MSVS_VERSION=2022

echo Deleting old build...
if exist "node_modules\better-sqlite3\build" (
    rmdir /s /q "node_modules\better-sqlite3\build"
    echo Old build deleted
)
echo.

echo Rebuilding with @electron/rebuild...
call npx @electron/rebuild -f -w better-sqlite3

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Rebuild failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! better-sqlite3 rebuilt for Electron
echo ========================================
echo.
pause
