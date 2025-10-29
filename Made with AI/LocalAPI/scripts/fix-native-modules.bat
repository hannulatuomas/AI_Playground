@echo off
REM Fix Native Module Compilation Issues
REM Run this if you get "NODE_MODULE_VERSION" errors

echo ========================================
echo Fixing Native Module Compilation
echo ========================================
echo.

echo Step 1: Rebuilding better-sqlite3...
call npm rebuild better-sqlite3
if %errorlevel% neq 0 (
    echo ERROR: Failed to rebuild better-sqlite3
    exit /b 1
)
echo ✓ better-sqlite3 rebuilt successfully
echo.

echo Step 2: Running electron-rebuild...
call npx electron-rebuild -f -w better-sqlite3
if %errorlevel% neq 0 (
    echo ERROR: Failed to run electron-rebuild
    exit /b 1
)
echo ✓ electron-rebuild completed successfully
echo.

echo Step 3: Rebuilding application...
call npm run build
if %errorlevel% neq 0 (
    echo ERROR: Failed to build application
    exit /b 1
)
echo ✓ Application built successfully
echo.

echo ========================================
echo Native modules fixed successfully!
echo You can now run: npm run dev
echo ========================================
