# AI Agent Console - Windows Build Script (PowerShell)
# 
# This script builds a Windows executable using PyInstaller.
# It handles environment setup, dependency installation, and build execution.
#
# Usage:
#   .\build_windows.ps1
#
# Prerequisites:
#   - Python 3.9 or later (3.12 recommended)
#   - pip
#   - For source builds: Visual Studio Build Tools + CMake
#
# Output:
#   dist/ai-agent-console/ai-agent-console.exe

# ============================================================================
# Configuration
# ============================================================================

$ErrorActionPreference = "Stop"
$APP_NAME = "ai-agent-console"
$PYTHON_VERSION_MIN = "3.9"
$VENV_DIR = "build_venv"
$DIST_DIR = "dist"
$BUILD_DIR = "build"

# ============================================================================
# Functions
# ============================================================================

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "`n==> $Message" "Cyan"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "[OK] $Message" "Green"
}

function Write-Error-Message {
    param([string]$Message)
    Write-ColorOutput "[ERROR] $Message" "Red"
}

function Write-Warning-Message {
    param([string]$Message)
    Write-ColorOutput "[WARNING] $Message" "Yellow"
}

function Check-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

function Check-PythonVersion {
    try {
        $version = python --version 2>&1
        $versionNumber = ($version -split " ")[1]
        $major = [int]($versionNumber -split "\.")[0]
        $minor = [int]($versionNumber -split "\.")[1]
        
        $minMajor = [int]($PYTHON_VERSION_MIN -split "\.")[0]
        $minMinor = [int]($PYTHON_VERSION_MIN -split "\.")[1]
        
        if ($major -gt $minMajor -or ($major -eq $minMajor -and $minor -ge $minMinor)) {
            Write-Success "Found Python $versionNumber"
            
            # Warn about Python 3.14 wheel availability issues
            if ($major -eq 3 -and $minor -eq 14) {
                Write-Warning-Message "Python 3.14 detected - Limited pre-built wheel availability"
                Write-Host "  RECOMMENDATION: Use Python 3.12 for best compatibility" -ForegroundColor Yellow
            }
            return $true
        } else {
            Write-Error-Message "Python $versionNumber is too old (need $PYTHON_VERSION_MIN or later)"
            return $false
        }
    } catch {
        Write-Error-Message "Failed to check Python version"
        return $false
    }
}

function Cleanup-Build {
    Write-Step "Cleaning up previous build artifacts"
    
    if (Test-Path $DIST_DIR) {
        Write-Host "  Removing $DIST_DIR..."
        Remove-Item -Recurse -Force $DIST_DIR
    }
    
    if (Test-Path $BUILD_DIR) {
        Write-Host "  Removing $BUILD_DIR..."
        Remove-Item -Recurse -Force $BUILD_DIR
    }
    
    if (Test-Path "__pycache__") {
        Write-Host "  Removing __pycache__..."
        Remove-Item -Recurse -Force "__pycache__"
    }
    
    Get-ChildItem -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force
    Get-ChildItem -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
    
    Write-Success "Cleanup complete"
}

function Create-VirtualEnv {
    Write-Step "Creating virtual environment for build"
    
    if (Test-Path $VENV_DIR) {
        Write-Host "  Removing existing virtual environment..."
        Remove-Item -Recurse -Force $VENV_DIR
    }
    
    python -m venv $VENV_DIR
    
    if (-not (Test-Path $VENV_DIR)) {
        Write-Error-Message "Failed to create virtual environment"
        exit 1
    }
    
    Write-Success "Virtual environment created"
}

function Activate-VirtualEnv {
    Write-Step "Activating virtual environment"
    
    $activateScript = Join-Path $VENV_DIR "Scripts\Activate.ps1"
    
    if (-not (Test-Path $activateScript)) {
        Write-Error-Message "Virtual environment activation script not found"
        exit 1
    }
    
    & $activateScript
    Write-Success "Virtual environment activated"
}

function Install-LlamaCppPython {
    Write-Host ""
    Write-ColorOutput "========================================" "Cyan"
    Write-ColorOutput "  llama-cpp-python Configuration" "Cyan"
    Write-ColorOutput "========================================" "Cyan"
    Write-Host ""
    
    # Step 1: Ask if user wants llama-cpp-python
    Write-Host "Do you want to include llama-cpp-python?" -ForegroundColor Yellow
    Write-Host "  (Required for loading GGUF models directly)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Y) Yes, install llama-cpp-python" -ForegroundColor White
    Write-Host "  N) No, skip (use Ollama for local LLMs)" -ForegroundColor White
    Write-Host ""
    
    $includeLlama = Read-Host "Choice [Y/N] (default: Y)"
    if ([string]::IsNullOrWhiteSpace($includeLlama)) { $includeLlama = "Y" }
    
    if ($includeLlama -ne "Y" -and $includeLlama -ne "y") {
        Write-Host ""
        Write-Warning-Message "Skipping llama-cpp-python installation"
        Write-Host "  You can use Ollama for local LLM support" -ForegroundColor Gray
        return
    }
    
    # Step 2: Ask for installation method
    Write-Host ""
    Write-Host "Choose installation method:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1) Pre-built wheels (RECOMMENDED - fast, no compilation)" -ForegroundColor White
    Write-Host "  2) Build from source (advanced - requires build tools)" -ForegroundColor White
    Write-Host ""
    
    $method = Read-Host "Choice [1/2] (default: 1)"
    if ([string]::IsNullOrWhiteSpace($method)) { $method = "1" }
    
    if ($method -eq "1") {
        Install-LlamaCppPrebuilt
    } elseif ($method -eq "2") {
        Install-LlamaCppSource
    } else {
        Write-Warning-Message "Invalid choice, defaulting to pre-built wheels"
        Install-LlamaCppPrebuilt
    }
}

function Install-LlamaCppPrebuilt {
    Write-Host ""
    Write-Host "Choose pre-built wheel version:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1) CPU only (no GPU, ~250MB, works everywhere)" -ForegroundColor White
    Write-Host "  2) CUDA 12.1 (NVIDIA GPU, ~400MB)" -ForegroundColor White
    Write-Host "  3) CUDA 12.2 (NVIDIA GPU, newer)" -ForegroundColor White
    Write-Host "  4) CUDA 11.8 (NVIDIA GPU, older)" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Choice [1-4] (default: 1)"
    if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "1" }
    
    $wheelUrl = ""
    $versionName = ""
    
    switch ($choice) {
        "1" { 
            $wheelUrl = "https://abetlen.github.io/llama-cpp-python/whl/cpu"
            $versionName = "CPU"
        }
        "2" {
            $wheelUrl = "https://abetlen.github.io/llama-cpp-python/whl/cu121"
            $versionName = "CUDA 12.1"
        }
        "3" {
            $wheelUrl = "https://abetlen.github.io/llama-cpp-python/whl/cu122"
            $versionName = "CUDA 12.2"
        }
        "4" {
            $wheelUrl = "https://abetlen.github.io/llama-cpp-python/whl/cu118"
            $versionName = "CUDA 11.8"
        }
        default {
            Write-Warning-Message "Invalid choice, defaulting to CPU"
            $wheelUrl = "https://abetlen.github.io/llama-cpp-python/whl/cpu"
            $versionName = "CPU"
        }
    }
    
    Write-Host ""
    Write-Host "  Installing llama-cpp-python ($versionName) from pre-built wheels..." -ForegroundColor Yellow
    Write-Host "  This may take a few minutes..." -ForegroundColor Gray
    
    pip install llama-cpp-python --prefer-binary --only-binary llama-cpp-python --extra-index-url $wheelUrl
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "llama-cpp-python installed successfully ($versionName)"
        Verify-LlamaCppInstallation
    } else {
        Write-Error-Message "Failed to install llama-cpp-python ($versionName)"
        Write-Host "  The build will continue without llama-cpp-python" -ForegroundColor Yellow
    }
}

function Install-LlamaCppSource {
    Write-Host ""
    Write-Host "Choose build configuration:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1) CPU only (no GPU acceleration)" -ForegroundColor White
    Write-Host "  2) CUDA 12.1 (NVIDIA GPU)" -ForegroundColor White
    Write-Host "  3) CUDA 12.2 (NVIDIA GPU, newer)" -ForegroundColor White
    Write-Host "  4) CUDA 11.8 (NVIDIA GPU, older)" -ForegroundColor White
    Write-Host "  5) SYCL (Intel GPU/CPU)" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Choice [1-5] (default: 1)"
    if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "1" }
    
    $cmakeArgs = ""
    $versionName = ""
    $needsCuda = $false
    $needsSycl = $false
    
    switch ($choice) {
        "1" {
            $cmakeArgs = ""
            $versionName = "CPU (source)"
        }
        "2" {
            $cmakeArgs = "-DLLAMA_CUDA=on"
            $versionName = "CUDA 12.1 (source)"
            $needsCuda = $true
        }
        "3" {
            $cmakeArgs = "-DLLAMA_CUDA=on"
            $versionName = "CUDA 12.2 (source)"
            $needsCuda = $true
        }
        "4" {
            $cmakeArgs = "-DLLAMA_CUDA=on"
            $versionName = "CUDA 11.8 (source)"
            $needsCuda = $true
        }
        "5" {
            $cmakeArgs = "-DLLAMA_SYCL=on -DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icx"
            $versionName = "SYCL (source)"
            $needsSycl = $true
        }
        default {
            Write-Warning-Message "Invalid choice, defaulting to CPU"
            $cmakeArgs = ""
            $versionName = "CPU (source)"
        }
    }
    
    Write-Host ""
    Write-Host "  Building llama-cpp-python from source ($versionName)..." -ForegroundColor Yellow
    Write-Host "  This will take 10-30 minutes depending on your system..." -ForegroundColor Gray
    Write-Host ""
    
    # Check for build tools
    Write-Host "  Checking build prerequisites..." -ForegroundColor Gray
    
    $hasVS = $false
    $hasCMake = $false
    $hasCuda = $false
    $hasSycl = $false
    
    # Check for Visual Studio / Build Tools
    $vsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
    if (Test-Path $vsWhere) {
        try {
            $vsPath = & $vsWhere -latest -property installationPath 2>$null
            if ($vsPath) {
                $vcVarsPath = Join-Path $vsPath "VC\Auxiliary\Build\vcvars64.bat"
                if (Test-Path $vcVarsPath) {
                    $hasVS = $true
                    Write-Host "    [OK] Visual Studio Build Tools found at: $vsPath" -ForegroundColor Green
                    
                    # Initialize Visual Studio environment
                    Write-Host "    [INFO] Initializing Visual Studio environment..." -ForegroundColor Gray
                    
                    # Run vcvars64.bat and capture environment
                    $tempFile = [System.IO.Path]::GetTempFileName()
                    cmd /c "`"$vcVarsPath`" && set" | Out-File -FilePath $tempFile -Encoding ASCII
                    
                    # Parse and set environment variables
                    Get-Content $tempFile | ForEach-Object {
                        if ($_ -match "^([^=]+)=(.*)$") {
                            $name = $matches[1]
                            $value = $matches[2]
                            # Update current session
                            Set-Item -Path "Env:$name" -Value $value -ErrorAction SilentlyContinue
                        }
                    }
                    Remove-Item $tempFile
                    
                    Write-Host "    [OK] Visual Studio environment initialized" -ForegroundColor Green
                }
            }
        } catch {
            # vswhere failed, continue checking
        }
    }
    
    if (-not $hasVS) {
        # Check for cl.exe in PATH
        try {
            $null = Get-Command cl.exe -ErrorAction SilentlyContinue
            if ($?) {
                $hasVS = $true
                Write-Host "    [OK] C++ compiler found in PATH" -ForegroundColor Green
            }
        } catch {}
    }
    
    if (-not $hasVS) {
        # Last resort: try common VS installation paths
        $commonPaths = @(
            "${env:ProgramFiles}\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat",
            "${env:ProgramFiles}\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat",
            "${env:ProgramFiles}\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars64.bat",
            "${env:ProgramFiles}\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat",
            "${env:ProgramFiles}\Microsoft Visual Studio\2025\Preview\VC\Auxiliary\Build\vcvars64.bat",
            "${env:ProgramFiles}\Microsoft Visual Studio\2025\Community\VC\Auxiliary\Build\vcvars64.bat",
            "${env:ProgramFiles}\Microsoft Visual Studio\18\Insiders\VC\Auxiliary\Build\vcvars64.bat",
            "${env:ProgramFiles}\Microsoft Visual Studio\17\Preview\VC\Auxiliary\Build\vcvars64.bat",
            "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat",
            "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build\vcvars64.bat",
            "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
        )
        
        foreach ($path in $commonPaths) {
            if (Test-Path $path) {
                Write-Host "    [INFO] Found Visual Studio at: $path" -ForegroundColor Gray
                Write-Host "    [INFO] Initializing environment..." -ForegroundColor Gray
                
                # Run vcvars64.bat and capture environment
                $tempFile = [System.IO.Path]::GetTempFileName()
                cmd /c "`"$path`" && set" | Out-File -FilePath $tempFile -Encoding ASCII
                
                # Parse and set environment variables
                Get-Content $tempFile | ForEach-Object {
                    if ($_ -match "^([^=]+)=(.*)$") {
                        $name = $matches[1]
                        $value = $matches[2]
                        Set-Item -Path "Env:$name" -Value $value -ErrorAction SilentlyContinue
                    }
                }
                Remove-Item $tempFile
                
                # Verify cl.exe is now available
                try {
                    $null = Get-Command cl.exe -ErrorAction SilentlyContinue
                    if ($?) {
                        $hasVS = $true
                        Write-Host "    [OK] Visual Studio environment initialized" -ForegroundColor Green
                        break
                    }
                } catch {}
            }
        }
    }
    
    if (-not $hasVS) {
        Write-Host "    [ERROR] Visual Studio Build Tools not detected" -ForegroundColor Red
        Write-Host ""
        Write-Host "  Visual Studio Build Tools are REQUIRED for source builds." -ForegroundColor Yellow
        Write-Host "  Download and install from:" -ForegroundColor Yellow
        Write-Host "  https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  During installation, select:" -ForegroundColor Yellow
        Write-Host "    - Desktop development with C++" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  After installation, restart your terminal and try again." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Alternatively, use pre-built wheels (option 1)." -ForegroundColor Yellow
        return
    }
    
    # Check for CMake
    try {
        $cmakeVersion = cmake --version 2>&1
        if ($?) {
            $hasCMake = $true
            Write-Host "    [OK] CMake found" -ForegroundColor Green
        }
    } catch {}
    
    if (-not $hasCMake) {
        Write-Host "    [INFO] CMake not found, installing..." -ForegroundColor Yellow
        pip install cmake
        if ($LASTEXITCODE -eq 0) {
            $hasCMake = $true
            Write-Host "    [OK] CMake installed" -ForegroundColor Green
        } else {
            Write-Host "    [ERROR] Failed to install CMake" -ForegroundColor Red
            return
        }
    }
    
    # Check for CUDA if needed
    if ($needsCuda) {
        if ($env:CUDA_PATH) {
            $hasCuda = $true
            Write-Host "    [OK] CUDA Toolkit found: $env:CUDA_PATH" -ForegroundColor Green
        } else {
            Write-Host "    [WARNING] CUDA Toolkit not detected (CUDA_PATH not set)" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "  For CUDA builds, you need NVIDIA CUDA Toolkit installed." -ForegroundColor Yellow
            Write-Host "  Download from: https://developer.nvidia.com/cuda-downloads" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "  Continuing anyway, but build may fail..." -ForegroundColor Yellow
        }
    }
    
    # Check for SYCL if needed
    if ($needsSycl) {
        Write-Host "    [INFO] Checking for Intel oneAPI..." -ForegroundColor Gray
        
        # Check if oneAPI is already initialized
        if ($env:ONEAPI_ROOT) {
            $hasSycl = $true
            Write-Host "    [OK] Intel oneAPI found: $env:ONEAPI_ROOT" -ForegroundColor Green
        } else {
            # Try to find and initialize oneAPI
            $oneApiSetvars = $null
            
            # Check common oneAPI installation paths
            $oneApiPaths = @(
                "${env:ProgramFiles(x86)}\Intel\oneAPI\setvars.bat",
                "${env:ProgramFiles}\Intel\oneAPI\setvars.bat"
            )
            
            foreach ($path in $oneApiPaths) {
                if (Test-Path $path) {
                    $oneApiSetvars = $path
                    break
                }
            }
            
            if ($oneApiSetvars) {
                Write-Host "    [INFO] Found Intel oneAPI at: $oneApiSetvars" -ForegroundColor Gray
                Write-Host "    [INFO] Initializing Intel oneAPI environment..." -ForegroundColor Gray
                
                # Run setvars.bat and capture environment
                $tempFile = [System.IO.Path]::GetTempFileName()
                cmd /c "`"$oneApiSetvars`" && set" | Out-File -FilePath $tempFile -Encoding ASCII
                
                # Parse and set environment variables
                Get-Content $tempFile | ForEach-Object {
                    if ($_ -match "^([^=]+)=(.*)$") {
                        $name = $matches[1]
                        $value = $matches[2]
                        Set-Item -Path "Env:$name" -Value $value -ErrorAction SilentlyContinue
                    }
                }
                Remove-Item $tempFile
                
                # Check if icx compiler is now available
                try {
                    $null = Get-Command icx -ErrorAction SilentlyContinue
                    if ($?) {
                        $hasSycl = $true
                        Write-Host "    [OK] Intel oneAPI environment initialized" -ForegroundColor Green
                        if ($env:ONEAPI_ROOT) {
                            Write-Host "    [OK] ONEAPI_ROOT: $env:ONEAPI_ROOT" -ForegroundColor Green
                        }
                    } else {
                        Write-Host "    [WARNING] oneAPI initialized but icx compiler not found in PATH" -ForegroundColor Yellow
                    }
                } catch {
                    Write-Host "    [WARNING] Failed to verify icx compiler" -ForegroundColor Yellow
                }
            } else {
                Write-Host "    [WARNING] Intel oneAPI not detected" -ForegroundColor Yellow
                Write-Host ""
                Write-Host "  For SYCL builds, you need Intel oneAPI Base Toolkit." -ForegroundColor Yellow
                Write-Host "  Download from: https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit-download.html" -ForegroundColor Cyan
                Write-Host ""
                Write-Host "  Searched locations:" -ForegroundColor Yellow
                foreach ($path in $oneApiPaths) {
                    Write-Host "    - $path" -ForegroundColor Gray
                }
                Write-Host ""
                Write-Host "  Continuing anyway, but build will likely fail..." -ForegroundColor Yellow
            }
        }
    }
    
    Write-Host ""
    Write-Host "  Starting compilation..." -ForegroundColor Yellow
    
    # Set CMAKE_ARGS environment variable
    if ($cmakeArgs) {
        $env:CMAKE_ARGS = $cmakeArgs
        Write-Host "  CMake args: $cmakeArgs" -ForegroundColor Gray
    }
    
    # Force reinstall to ensure clean build
    Write-Host "  Installing llama-cpp-python (this will take a while)..." -ForegroundColor Gray
    
    # Use pip install with --no-binary to force source build
    pip install --no-binary llama-cpp-python --force-reinstall llama-cpp-python
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "llama-cpp-python built successfully ($versionName)"
        Verify-LlamaCppInstallation
    } else {
        Write-Error-Message "Failed to build llama-cpp-python ($versionName)"
        Write-Host ""
        Write-Host "  Common issues:" -ForegroundColor Yellow
        Write-Host "    1. Visual Studio Build Tools not properly installed" -ForegroundColor Gray
        Write-Host "       - Ensure 'Desktop development with C++' workload is installed" -ForegroundColor Gray
        Write-Host "    2. CMake not available or too old" -ForegroundColor Gray
        Write-Host "       - Try: pip install --upgrade cmake" -ForegroundColor Gray
        Write-Host "    3. CUDA Toolkit not installed (for CUDA builds)" -ForegroundColor Gray
        Write-Host "       - Download from: https://developer.nvidia.com/cuda-downloads" -ForegroundColor Gray
        Write-Host "    4. Compiler not in PATH" -ForegroundColor Gray
        Write-Host "       - Run build from 'Developer Command Prompt for VS'" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  TIP: Use pre-built wheels instead (much easier!)" -ForegroundColor Cyan
        Write-Host "       Re-run script and choose option 1 (pre-built wheels)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  The build will continue without llama-cpp-python" -ForegroundColor Yellow
    }
    
    # Clean up environment variable
    if ($env:CMAKE_ARGS) {
        Remove-Item Env:\CMAKE_ARGS -ErrorAction SilentlyContinue
    }
}

function Verify-LlamaCppInstallation {
    Write-Host "  Verifying installation..." -ForegroundColor Gray
    $verification = python -c "import importlib.util; spec = importlib.util.find_spec('llama_cpp'); print('OK' if spec else 'FAIL')" 2>&1
    if ($verification -match "OK") {
        Write-Success "llama-cpp-python verified and ready for bundling"
    } else {
        Write-Warning-Message "llama-cpp-python installed but may have import issues"
        Write-Host "  This is usually fine - the files will still be bundled" -ForegroundColor Gray
    }
}

function Install-Dependencies {
    Write-Step "Installing dependencies"
    
    Write-Host "  Upgrading pip, setuptools, and wheel..."
    python -m pip install --upgrade pip setuptools wheel
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Message "Failed to upgrade pip/setuptools/wheel"
        exit 1
    }
    
    Write-Host "`n  Installing project dependencies..."
    Write-Host "  (This may take 5-10 minutes)" -ForegroundColor Gray
    Write-Host ""
    
    pip install --prefer-binary -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Message "Failed to install dependencies"
        Write-Host ""
        Write-Host "Troubleshooting:" -ForegroundColor Yellow
        Write-Host "  1. Check error messages above for specific package failures"
        Write-Host "  2. Ensure internet connectivity"
        Write-Host "  3. For Python 3.14: Use Python 3.12 instead"
        exit 1
    }
    
    Write-Success "Project dependencies installed"
    
    # Install llama-cpp-python with interactive prompts
    Install-LlamaCppPython
    
    Write-Host "`n  Installing PyInstaller..."
    pip install pyinstaller>=6.3.0
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Message "Failed to install PyInstaller"
        exit 1
    }
    
    Write-Success "All dependencies installed"
}

function Build-Executable {
    Write-Step "Building Windows executable with PyInstaller"
    
    if (-not (Test-Path "$APP_NAME.spec")) {
        Write-Warning-Message "Spec file not found, PyInstaller will auto-generate one"
        Write-Host "  Running PyInstaller with basic options...`n"
        pyinstaller --clean --onedir --console --name $APP_NAME main.py
    } else {
        Write-Host "  Using spec file: $APP_NAME.spec"
        Write-Host "  Running PyInstaller...`n"
        pyinstaller --clean "$APP_NAME.spec"
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Message "PyInstaller build failed"
        Write-Host ""
        Write-Host "Note: 'Hidden import not found' warnings are often harmless" -ForegroundColor Yellow
        Write-Host "Test the executable to see if it works" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Success "Build complete"
}

function Verify-Build {
    Write-Step "Verifying build output"
    
    $exePath = Join-Path $DIST_DIR "$APP_NAME\$APP_NAME.exe"
    
    if (-not (Test-Path $exePath)) {
        Write-Error-Message "Executable not found: $exePath"
        exit 1
    }
    
    $fileSize = (Get-Item $exePath).Length / 1MB
    Write-Success "Executable created: $exePath"
    Write-Host "  Size: $([math]::Round($fileSize, 2)) MB"
    
    # Check for config file
    $configPath = Join-Path $DIST_DIR "$APP_NAME\config.yaml"
    if (Test-Path $configPath) {
        Write-Success "Configuration file included"
    } else {
        Write-Warning-Message "Configuration file not found in distribution"
    }
    
    # Check for agents directory
    $agentsPath = Join-Path $DIST_DIR "$APP_NAME\agents"
    if (Test-Path $agentsPath) {
        Write-Success "Agents directory included"
    } else {
        Write-Warning-Message "Agents directory not found in distribution"
    }
}

function Create-Distribution-Package {
    Write-Step "Creating distribution package"
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $zipName = "$APP_NAME-windows-$timestamp.zip"
    
    $sourcePath = Join-Path $DIST_DIR $APP_NAME
    
    if (-not (Test-Path $sourcePath)) {
        Write-Error-Message "Distribution directory not found: $sourcePath"
        return
    }
    
    Write-Host "  Creating ZIP archive: $zipName"
    Compress-Archive -Path $sourcePath -DestinationPath $zipName -Force
    
    $zipSize = (Get-Item $zipName).Length / 1MB
    Write-Success "Distribution package created: $zipName"
    Write-Host "  Size: $([math]::Round($zipSize, 2)) MB"
}

function Show-Summary {
    $separator = "=" * 70
    Write-ColorOutput "`n$separator" "Cyan"
    Write-ColorOutput "Build Summary" "Cyan"
    Write-ColorOutput "$separator" "Cyan"
    
    $exePath = Join-Path $DIST_DIR "$APP_NAME\$APP_NAME.exe"
    
    Write-Host "`nExecutable Location:"
    Write-ColorOutput "  $exePath" "Green"
    
    Write-Host "`nNext Steps:"
    Write-ColorOutput "  1. Test the executable:" "Yellow"
    Write-Host "     cd $DIST_DIR\$APP_NAME"
    Write-Host "     .\$APP_NAME.exe --help"
    
    Write-ColorOutput "`n  2. Configure the application:" "Yellow"
    Write-Host "     Edit config.yaml in the distribution directory"
    
    Write-ColorOutput "`n  3. Distribute:" "Yellow"
    Write-Host "     Copy the entire $DIST_DIR\$APP_NAME directory to target systems"
    Write-Host "     Or use the generated ZIP file"
    
    Write-ColorOutput "`n$separator" "Cyan"
}

# ============================================================================
# Main Script
# ============================================================================

$banner = @"

====================================================================

        AI Agent Console - Windows Build Script

====================================================================

"@

Write-ColorOutput $banner "Cyan"

# Check prerequisites
Write-Step "Checking prerequisites"

if (-not (Check-Command "python")) {
    Write-Error-Message "Python is not installed or not in PATH"
    Write-Host "Please install Python $PYTHON_VERSION_MIN or later from https://www.python.org/"
    exit 1
}

if (-not (Check-PythonVersion)) {
    exit 1
}

if (-not (Check-Command "pip")) {
    Write-Error-Message "pip is not installed or not in PATH"
    exit 1
}

if (-not (Test-Path "main.py")) {
    Write-Error-Message "main.py not found in current directory"
    Write-Host "Current directory: $(Get-Location)"
    exit 1
}

if (-not (Test-Path "requirements.txt")) {
    Write-Error-Message "requirements.txt not found in current directory"
    exit 1
}

Write-Success "All prerequisites met"

# Perform build steps
try {
    Cleanup-Build
    Create-VirtualEnv
    Activate-VirtualEnv
    Install-Dependencies
    Build-Executable
    Verify-Build
    Create-Distribution-Package
    Show-Summary
    
    Write-ColorOutput "`n[SUCCESS] Build completed successfully!`n" "Green"
    exit 0
    
} catch {
    Write-ColorOutput "`n[ERROR] Build failed with error:" "Red"
    Write-ColorOutput $_.Exception.Message "Red"
    Write-ColorOutput $_.ScriptStackTrace "Red"
    exit 1
}
