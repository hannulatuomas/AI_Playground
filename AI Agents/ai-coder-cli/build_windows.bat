@echo off
REM AI Agent Console - Windows Build Script (Batch)
REM 
REM This script builds a Windows executable using PyInstaller.
REM It handles environment setup, dependency installation, and build execution.
REM
REM Usage:
REM   build_windows.bat
REM
REM Prerequisites:
REM   - Python 3.9 or later (3.12 recommended)
REM   - pip
REM   - For source builds: Visual Studio Build Tools + CMake
REM
REM Output:
REM   dist\ai-agent-console\ai-agent-console.exe

setlocal enabledelayedexpansion

REM ============================================================================
REM Configuration
REM ============================================================================

set APP_NAME=ai-agent-console
set PYTHON_VERSION_MIN=3.9
set VENV_DIR=build_venv
set DIST_DIR=dist
set BUILD_DIR=build

REM ============================================================================
REM Main Script
REM ============================================================================

echo.
echo ====================================================================
echo.
echo        AI Agent Console - Windows Build Script
echo.
echo ====================================================================
echo.

REM Check Python
echo [STEP] Checking prerequisites...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python %PYTHON_VERSION_MIN% or later from https://www.python.org/
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found Python %PYTHON_VERSION%

pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not installed or not in PATH
    exit /b 1
)
echo [OK] pip is available

if not exist "main.py" (
    echo [ERROR] main.py not found in current directory
    exit /b 1
)

if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found in current directory
    exit /b 1
)
echo [OK] All prerequisites met
echo.

REM Clean up
echo [STEP] Cleaning up previous build artifacts...
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%" >nul 2>&1
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%" >nul 2>&1
if exist "__pycache__" rmdir /s /q "__pycache__" >nul 2>&1
if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%" >nul 2>&1
echo [OK] Cleanup complete
echo.

REM Create virtual environment
echo [STEP] Creating virtual environment for build...
python -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    exit /b 1
)
echo [OK] Virtual environment created
echo.

REM Activate virtual environment
echo [STEP] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo [STEP] Installing dependencies...
echo   Upgrading pip...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip
    call deactivate >nul 2>&1
    exit /b 1
)

echo.
echo   Installing project dependencies...
echo   (This may take 5-10 minutes^)
echo.
pip install --prefer-binary -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install project dependencies
    call deactivate >nul 2>&1
    exit /b 1
)
echo [OK] Project dependencies installed
echo.

REM llama-cpp-python configuration
echo ========================================
echo   llama-cpp-python Configuration
echo ========================================
echo.
echo Do you want to include llama-cpp-python?
echo (Required for loading GGUF models directly^)
echo.
echo   Y^) Yes, install llama-cpp-python
echo   N^) No, skip (use Ollama for local LLMs^)
echo.
set /p INCLUDE_LLAMA="Choice [Y/N] (default: Y): "
if "%INCLUDE_LLAMA%"=="" set INCLUDE_LLAMA=Y

if /i not "%INCLUDE_LLAMA%"=="Y" (
    echo.
    echo [WARNING] Skipping llama-cpp-python installation
    echo   You can use Ollama for local LLM support
    goto :after_llama
)

echo.
echo Choose installation method:
echo.
echo   1^) Pre-built wheels (RECOMMENDED - fast, no compilation^)
echo   2^) Build from source (advanced - requires build tools^)
echo.
set /p INSTALL_METHOD="Choice [1/2] (default: 1): "
if "%INSTALL_METHOD%"=="" set INSTALL_METHOD=1

if "%INSTALL_METHOD%"=="1" goto :prebuilt_wheels
if "%INSTALL_METHOD%"=="2" goto :source_build
echo [WARNING] Invalid choice, defaulting to pre-built wheels
goto :prebuilt_wheels

:prebuilt_wheels
echo.
echo Choose pre-built wheel version:
echo.
echo   1^) CPU only (no GPU, ~250MB, works everywhere^)
echo   2^) CUDA 12.1 (NVIDIA GPU, ~400MB^)
echo   3^) CUDA 12.2 (NVIDIA GPU, newer^)
echo   4^) CUDA 11.8 (NVIDIA GPU, older^)
echo.
set /p WHEEL_CHOICE="Choice [1-4] (default: 1): "
if "%WHEEL_CHOICE%"=="" set WHEEL_CHOICE=1

set WHEEL_URL=
set VERSION_NAME=

if "%WHEEL_CHOICE%"=="1" (
    set WHEEL_URL=https://abetlen.github.io/llama-cpp-python/whl/cpu
    set VERSION_NAME=CPU
)
if "%WHEEL_CHOICE%"=="2" (
    set WHEEL_URL=https://abetlen.github.io/llama-cpp-python/whl/cu121
    set VERSION_NAME=CUDA 12.1
)
if "%WHEEL_CHOICE%"=="3" (
    set WHEEL_URL=https://abetlen.github.io/llama-cpp-python/whl/cu122
    set VERSION_NAME=CUDA 12.2
)
if "%WHEEL_CHOICE%"=="4" (
    set WHEEL_URL=https://abetlen.github.io/llama-cpp-python/whl/cu118
    set VERSION_NAME=CUDA 11.8
)

if "%WHEEL_URL%"=="" (
    echo [WARNING] Invalid choice, defaulting to CPU
    set WHEEL_URL=https://abetlen.github.io/llama-cpp-python/whl/cpu
    set VERSION_NAME=CPU
)

echo.
echo   Installing llama-cpp-python (%VERSION_NAME%^) from pre-built wheels...
pip install llama-cpp-python --prefer-binary --only-binary llama-cpp-python --extra-index-url %WHEEL_URL%
if not errorlevel 1 (
    echo [OK] llama-cpp-python installed successfully (%VERSION_NAME%^)
    goto :verify_llama
) else (
    echo [ERROR] Failed to install llama-cpp-python (%VERSION_NAME%^)
    echo   The build will continue without llama-cpp-python
    goto :after_llama
)

:source_build
echo.
echo Choose build configuration:
echo.
echo   1^) CPU only (no GPU acceleration^)
echo   2^) CUDA 12.1 (NVIDIA GPU^)
echo   3^) CUDA 12.2 (NVIDIA GPU, newer^)
echo   4^) CUDA 11.8 (NVIDIA GPU, older^)
echo   5^) SYCL (Intel GPU/CPU^)
echo.
set /p SOURCE_CHOICE="Choice [1-5] (default: 1): "
if "%SOURCE_CHOICE%"=="" set SOURCE_CHOICE=1

set "CMAKE_ARGS="
set "VERSION_NAME="
set "NEEDS_CUDA=0"
set "NEEDS_SYCL=0"

if "%SOURCE_CHOICE%"=="1" (
    set "VERSION_NAME=CPU (source)"
)
if "%SOURCE_CHOICE%"=="2" (
    set "CMAKE_ARGS=-DLLAMA_CUDA=on"
    set "VERSION_NAME=CUDA 12.1 (source)"
    set "NEEDS_CUDA=1"
)
if "%SOURCE_CHOICE%"=="3" (
    set "CMAKE_ARGS=-DLLAMA_CUDA=on"
    set "VERSION_NAME=CUDA 12.2 (source)"
    set "NEEDS_CUDA=1"
)
if "%SOURCE_CHOICE%"=="4" (
    set "CMAKE_ARGS=-DLLAMA_CUDA=on"
    set "VERSION_NAME=CUDA 11.8 (source)"
    set "NEEDS_CUDA=1"
)
if "%SOURCE_CHOICE%"=="5" (
    set "CMAKE_ARGS=-DLLAMA_SYCL=on -DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icx"
    set "VERSION_NAME=SYCL (source)"
    set "NEEDS_SYCL=1"
)

if not defined VERSION_NAME (
    echo [WARNING] Invalid choice, defaulting to CPU
    set "VERSION_NAME=CPU (source)"
)

echo.
echo   Building llama-cpp-python from source (%VERSION_NAME%^)...
echo   This will take 10-30 minutes depending on your system...
echo.

REM Check for build tools
echo   Checking build prerequisites...

REM Check for Visual Studio Build Tools
set "HAS_VS=0"

REM First check if cl.exe already in PATH
where cl.exe >nul 2>&1
if not errorlevel 1 (
    set "HAS_VS=1"
    echo     [OK] C++ compiler found in PATH
    goto :check_cmake
)

echo     [INFO] Searching for Visual Studio...

REM Try using vswhere to find Visual Studio
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if exist "%VSWHERE%" (
    for /f "usebackq delims=" %%i in (`"%VSWHERE%" -latest -property installationPath 2^>nul`) do (
        set "VS_INSTALL_PATH=%%i"
    )
    
    if defined VS_INSTALL_PATH (
        set "VCVARS_PATH=!VS_INSTALL_PATH!\VC\Auxiliary\Build\vcvars64.bat"
        if exist "!VCVARS_PATH!" (
            echo     [INFO] Found Visual Studio at: !VS_INSTALL_PATH!
            echo     [INFO] Initializing Visual Studio environment...
            call "!VCVARS_PATH!" >nul 2>&1
            
            where cl.exe >nul 2>&1
            if not errorlevel 1 (
                set "HAS_VS=1"
                echo     [OK] Visual Studio environment initialized
                goto :check_cmake
            )
        )
    )
)

REM Try common Visual Studio installation paths manually
call :try_vs_path "%ProgramFiles%\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
if "%HAS_VS%"=="1" goto :check_cmake

call :try_vs_path "%ProgramFiles%\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat"
if "%HAS_VS%"=="1" goto :check_cmake

call :try_vs_path "%ProgramFiles%\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars64.bat"
if "%HAS_VS%"=="1" goto :check_cmake

call :try_vs_path "%ProgramFiles%\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
if "%HAS_VS%"=="1" goto :check_cmake

call :try_vs_path "%ProgramFiles%\Microsoft Visual Studio\2025\Preview\VC\Auxiliary\Build\vcvars64.bat"
if "%HAS_VS%"=="1" goto :check_cmake

call :try_vs_path "%ProgramFiles%\Microsoft Visual Studio\2025\Community\VC\Auxiliary\Build\vcvars64.bat"
if "%HAS_VS%"=="1" goto :check_cmake

call :try_vs_path "%ProgramFiles%\Microsoft Visual Studio\18\Insiders\VC\Auxiliary\Build\vcvars64.bat"
if "%HAS_VS%"=="1" goto :check_cmake

call :try_vs_path "%ProgramFiles%\Microsoft Visual Studio\17\Preview\VC\Auxiliary\Build\vcvars64.bat"
if "%HAS_VS%"=="1" goto :check_cmake

call :try_vs_path "%ProgramFiles(x86)%\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"
if "%HAS_VS%"=="1" goto :check_cmake

call :try_vs_path "%ProgramFiles(x86)%\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build\vcvars64.bat"
if "%HAS_VS%"=="1" goto :check_cmake

call :try_vs_path "%ProgramFiles(x86)%\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
if "%HAS_VS%"=="1" goto :check_cmake

REM If we get here, no VS was found
goto :check_cmake

:try_vs_path
if not exist %1 goto :eof
echo     [INFO] Found Visual Studio at: %~1
echo     [INFO] Initializing Visual Studio environment...
call %1 >nul 2>&1
where cl.exe >nul 2>&1
if not errorlevel 1 (
    set "HAS_VS=1"
    echo     [OK] Visual Studio environment initialized
)
goto :eof

:check_cmake
if "%HAS_VS%"=="0" (
    echo     [ERROR] Visual Studio Build Tools not detected
    echo.
    echo   Visual Studio Build Tools are REQUIRED for source builds.
    echo.
    echo   TROUBLESHOOTING:
    echo   1. Make sure Visual Studio Build Tools are installed
    echo      Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo.
    echo   2. During installation, select:
    echo      - Desktop development with C++
    echo.
    echo   3. After installation, you have two options:
    echo.
    echo      Option A - Run from Developer Command Prompt:
    echo        - Search for "Developer Command Prompt" in Start Menu
    echo        - Run this script from that prompt
    echo.
    echo      Option B - Use pre-built wheels (RECOMMENDED^):
    echo        - Re-run this script
    echo        - Choose option 1 (pre-built wheels^) instead
    echo.
    goto :after_llama
)

REM Check for CMake
cmake --version >nul 2>&1
if errorlevel 1 (
    echo     [INFO] CMake not found, installing...
    pip install cmake
    if errorlevel 1 (
        echo     [ERROR] Failed to install CMake
        goto :after_llama
    )
    echo     [OK] CMake installed
) else (
    echo     [OK] CMake found
)

REM Check for CUDA if needed
if "%NEEDS_CUDA%"=="1" (
    if defined CUDA_PATH (
        echo     [OK] CUDA Toolkit found: %CUDA_PATH%
    ) else (
        echo     [WARNING] CUDA Toolkit not detected (CUDA_PATH not set^)
        echo.
        echo   For CUDA builds, you need NVIDIA CUDA Toolkit installed.
        echo   Download from: https://developer.nvidia.com/cuda-downloads
        echo.
        echo   Continuing anyway, but build may fail...
    )
)

REM Check for SYCL if needed
if "%NEEDS_SYCL%"=="1" goto :check_sycl
goto :after_sycl_check

:check_sycl
echo     [INFO] Checking for Intel oneAPI...

REM Check if oneAPI is already initialized
if defined ONEAPI_ROOT (
    echo     [OK] Intel oneAPI found: %ONEAPI_ROOT%
    goto :after_sycl_check
)

REM Expand paths NOW before any issues
set "ONEAPI_PATH1=%ProgramFiles(x86)%\Intel\oneAPI\setvars.bat"
set "ONEAPI_PATH2=%ProgramFiles%\Intel\oneAPI\setvars.bat"

REM Check which path exists and store in a simple variable
if exist "%ONEAPI_PATH1%" (
    set "ONEAPI_FOUND=%ONEAPI_PATH1%"
    goto :init_oneapi
)
if exist "%ONEAPI_PATH2%" (
    set "ONEAPI_FOUND=%ONEAPI_PATH2%"
    goto :init_oneapi
)
goto :oneapi_not_found

:init_oneapi
echo     [INFO] Found Intel oneAPI at: %ONEAPI_FOUND%
echo     [INFO] Initializing Intel oneAPI environment...
REM Get short path (8.3 format) to avoid spaces and parentheses
for %%A in ("%ONEAPI_FOUND%") do set "ONEAPI_SHORT=%%~sA"
call "%ONEAPI_SHORT%" >nul 2>&1

REM Check if icx compiler is now available
where icx >nul 2>&1
if not errorlevel 1 (
    echo     [OK] Intel oneAPI environment initialized
    if defined ONEAPI_ROOT (
        echo     [OK] ONEAPI_ROOT: %ONEAPI_ROOT%
    )
) else (
    echo     [WARNING] oneAPI initialized but icx compiler not found in PATH
)
goto :after_sycl_check

:oneapi_not_found
echo     [WARNING] Intel oneAPI not detected
echo.
echo   For SYCL builds, you need Intel oneAPI Base Toolkit.
echo   Download from: https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit-download.html
echo.
echo   Searched locations:
echo     - !ONEAPI_PATH1!
echo     - !ONEAPI_PATH2!
echo.
echo   Continuing anyway, but build will likely fail...
goto :after_sycl_check

:after_sycl_check

echo.
echo   Starting compilation...

REM Set CMAKE_ARGS environment variable if needed
if defined CMAKE_ARGS (
    echo   CMake args: %CMAKE_ARGS%
)

echo   Installing llama-cpp-python (this will take a while^)...

REM Use pip install with --no-binary to force source build
pip install --no-binary llama-cpp-python --force-reinstall llama-cpp-python
if not errorlevel 1 (
    echo [OK] llama-cpp-python built successfully (%VERSION_NAME%^)
    goto :verify_llama
) else (
    echo [ERROR] Failed to build llama-cpp-python (%VERSION_NAME%^)
    echo.
    echo   Common issues:
    echo     1. Visual Studio Build Tools not properly installed
    echo        - Ensure 'Desktop development with C++' workload is installed
    echo     2. CMake not available or too old
    echo        - Try: pip install --upgrade cmake
    echo     3. CUDA Toolkit not installed (for CUDA builds^)
    echo        - Download from: https://developer.nvidia.com/cuda-downloads
    echo     4. Compiler not in PATH
    echo        - Run build from 'Developer Command Prompt for VS'
    echo.
    echo   TIP: Use pre-built wheels instead (much easier!^)
    echo        Re-run script and choose option 1 (pre-built wheels^)
    echo.
    echo   The build will continue without llama-cpp-python
    goto :after_llama
)

:verify_llama
echo   Verifying installation...
python -c "import importlib.util; spec = importlib.util.find_spec('llama_cpp'); print('OK' if spec else 'FAIL')" 2>nul | findstr "OK" >nul
if not errorlevel 1 (
    echo [OK] llama-cpp-python verified and ready for bundling
) else (
    echo [WARNING] llama-cpp-python installed but may have import issues
    echo   This is usually fine - the files will still be bundled
)

:after_llama

echo.
echo   Installing PyInstaller...
pip install pyinstaller>=6.3.0
if errorlevel 1 (
    echo [ERROR] Failed to install PyInstaller
    call deactivate >nul 2>&1
    exit /b 1
)
echo [OK] All dependencies installed
echo.

REM Build executable
echo [STEP] Building Windows executable with PyInstaller...
if not exist "%APP_NAME%.spec" (
    echo [WARNING] Spec file not found, PyInstaller will auto-generate one
    echo   Running PyInstaller with basic options...
    pyinstaller --clean --onedir --console --name %APP_NAME% main.py
) else (
    echo   Using spec file: %APP_NAME%.spec
    echo   Running PyInstaller...
    pyinstaller --clean "%APP_NAME%.spec"
)

if errorlevel 1 (
    echo [ERROR] PyInstaller build failed
    echo.
    echo Note: 'Hidden import not found' warnings are often harmless
    echo Test the executable to see if it works
    call deactivate >nul 2>&1
    exit /b 1
)
echo [OK] Build complete
echo.

REM Verify build
echo [STEP] Verifying build output...
set "EXE_PATH=%DIST_DIR%\%APP_NAME%\%APP_NAME%.exe"
if not exist "%EXE_PATH%" (
    echo [ERROR] Executable not found: %EXE_PATH%
    call deactivate >nul 2>&1
    exit /b 1
)
echo [OK] Executable created: %EXE_PATH%

set "CONFIG_PATH=%DIST_DIR%\%APP_NAME%\config.yaml"
if exist "%CONFIG_PATH%" (
    echo [OK] Configuration file included
) else (
    echo [WARNING] Configuration file not found in distribution
)

set "AGENTS_PATH=%DIST_DIR%\%APP_NAME%\agents"
if exist "%AGENTS_PATH%" (
    echo [OK] Agents directory included
) else (
    echo [WARNING] Agents directory not found in distribution
)
echo.

REM Create distribution package
echo [STEP] Creating distribution package...
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set BUILD_DATE=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set BUILD_TIME=%%a%%b)
set BUILD_TIME=!BUILD_TIME: =0!
set "TIMESTAMP=%BUILD_DATE%_%BUILD_TIME%"
set "ZIP_NAME=%APP_NAME%-windows-%TIMESTAMP%.zip"

echo   Creating ZIP archive: %ZIP_NAME%
powershell -Command "Compress-Archive -Path '%DIST_DIR%\%APP_NAME%' -DestinationPath '%ZIP_NAME%' -Force"
if errorlevel 1 (
    echo [WARNING] Failed to create ZIP archive
) else (
    echo [OK] Distribution package created: %ZIP_NAME%
)
echo.

REM Show summary
echo ====================================================================
echo Build Summary
echo ====================================================================
echo.
echo Executable Location:
echo   %EXE_PATH%
echo.
echo Next Steps:
echo   1. Test the executable:
echo      cd %DIST_DIR%\%APP_NAME%
echo      %APP_NAME%.exe --help
echo.
echo   2. Configure the application:
echo      Edit config.yaml in the distribution directory
echo.
echo   3. Distribute:
echo      Copy the entire %DIST_DIR%\%APP_NAME% directory to target systems
echo      Or use the generated ZIP file
echo.
echo ====================================================================
echo.
echo [SUCCESS] Build completed successfully!
echo.

REM Deactivate virtual environment
call deactivate >nul 2>&1

endlocal
exit /b 0
