
#!/usr/bin/env pwsh

<#
.SYNOPSIS
    AI Agent Console - Virtual Environment Setup Script (PowerShell)

.DESCRIPTION
    This script creates and configures a Python virtual environment for the AI Agent Console.

.PARAMETER Dev
    Install development dependencies (includes testing, linting, etc.)

.PARAMETER Help
    Show this help message

.EXAMPLE
    .\setup_venv.ps1
    Creates a virtual environment with production dependencies

.EXAMPLE
    .\setup_venv.ps1 -Dev
    Creates a virtual environment with development dependencies
#>

[CmdletBinding()]
param(
    [Parameter(HelpMessage="Install development dependencies")]
    [switch]$Dev,
    
    [Parameter(HelpMessage="Show help message")]
    [switch]$Help
)

# Configuration
$VenvDir = "venv"
$PythonCmd = "python"
$MinPythonVersion = [version]"3.9.0"

# Show help if requested
if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Detailed
    exit 0
}

# Helper function for colored output
function Write-ColorOutput {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [string]$Color = "White"
    )
    
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput "==========================================" "Blue"
Write-ColorOutput "AI Agent Console - Virtual Environment Setup" "Blue"
Write-ColorOutput "==========================================" "Blue"
Write-Host ""

# Check if Python is installed
try {
    $PythonVersion = & $PythonCmd --version 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed"
    }
} catch {
    Write-ColorOutput "Error: Python is not installed or not in PATH" "Red"
    Write-Host "Please install Python 3.9 or higher"
    exit 1
}

# Parse Python version
$VersionMatch = $PythonVersion -match "Python (\d+\.\d+\.\d+)"
if ($VersionMatch) {
    $CurrentVersion = [version]$matches[1]
    Write-ColorOutput "[OK] Found Python $CurrentVersion" "Green"
    
    if ($CurrentVersion -lt $MinPythonVersion) {
        Write-ColorOutput "Error: Python $MinPythonVersion or higher is required" "Red"
        Write-Host "Current version: $CurrentVersion"
        exit 1
    }
} else {
    Write-ColorOutput "Warning: Could not parse Python version" "Yellow"
}

# Check if venv already exists
if (Test-Path $VenvDir) {
    Write-ColorOutput "Warning: Virtual environment directory '$VenvDir' already exists" "Yellow"
    $Recreate = Read-Host "Do you want to recreate it? (y/N)"
    if ($Recreate -eq 'y' -or $Recreate -eq 'Y') {
        Write-ColorOutput "Removing existing virtual environment..." "Yellow"
        Remove-Item -Recurse -Force $VenvDir
    } else {
        Write-ColorOutput "Using existing virtual environment" "Yellow"
        $SkipCreate = $true
    }
}

# Create virtual environment if it doesn't exist
if (-not $SkipCreate -and -not (Test-Path $VenvDir)) {
    Write-Host ""
    Write-ColorOutput "Creating virtual environment..." "Blue"
    & $PythonCmd -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "Error: Failed to create virtual environment" "Red"
        exit 1
    }
    Write-ColorOutput "[OK] Virtual environment created" "Green"
}

# Activate virtual environment
Write-Host ""
Write-ColorOutput "Activating virtual environment..." "Blue"

if ($IsWindows -or $env:OS -like "*Windows*") {
    $ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
} else {
    $ActivateScript = Join-Path $VenvDir "bin/Activate.ps1"
}

if (Test-Path $ActivateScript) {
    & $ActivateScript
    Write-ColorOutput "[OK] Virtual environment activated" "Green"
} else {
    Write-ColorOutput "Warning: Activation script not found at $ActivateScript" "Yellow"
}

# Upgrade pip, setuptools, and wheel
Write-Host ""
Write-ColorOutput "Upgrading pip, setuptools, and wheel..." "Blue"
& python -m pip install --upgrade pip setuptools wheel
Write-ColorOutput "[OK] Core packages upgraded" "Green"

# Install dependencies
Write-Host ""
if ($Dev) {
    Write-ColorOutput "Installing development dependencies..." "Blue"
    & pip install -r requirements-dev.txt
    Write-ColorOutput "[OK] Development dependencies installed" "Green"
} else {
    Write-ColorOutput "Installing production dependencies..." "Blue"
    & pip install -r requirements.txt
    Write-ColorOutput "[OK] Production dependencies installed" "Green"
}

# Verify installation
Write-Host ""
Write-ColorOutput "Verifying installation..." "Blue"
try {
    & python -c "import typer; import pydantic; import yaml; import ollama" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "[OK] Core dependencies verified" "Green"
    } else {
        Write-ColorOutput "Warning: Some core dependencies could not be imported" "Yellow"
    }
} catch {
    Write-ColorOutput "Warning: Some core dependencies could not be imported" "Yellow"
}

# Create activation helper script
$ActivateHelperContent = @"
# Quick activation script for the virtual environment
`$ActivateScript = if (`$IsWindows -or `$env:OS -like "*Windows*") {
    "venv\Scripts\Activate.ps1"
} else {
    "venv/bin/Activate.ps1"
}

if (Test-Path `$ActivateScript) {
    & `$ActivateScript
    Write-Host "Virtual environment activated!" -ForegroundColor Green
    Write-Host "To deactivate, run: deactivate"
} else {
    Write-Host "Error: Virtual environment not found" -ForegroundColor Red
}
"@

Set-Content -Path "activate_venv.ps1" -Value $ActivateHelperContent

Write-Host ""
Write-ColorOutput "==========================================" "Green"
Write-ColorOutput "Setup Complete!" "Green"
Write-ColorOutput "==========================================" "Green"
Write-Host ""
Write-Host "To activate the virtual environment:"
Write-ColorOutput "  .\venv\Scripts\Activate.ps1" "Blue"
Write-Host "  or use the helper script:"
Write-ColorOutput "  .\activate_venv.ps1" "Blue"
Write-Host ""
Write-Host "To deactivate the virtual environment:"
Write-ColorOutput "  deactivate" "Blue"
Write-Host ""
Write-Host "To run the AI Agent Console:"
Write-ColorOutput "  python main.py" "Blue"
Write-Host ""

if ($Dev) {
    Write-Host "Development tools available:"
    Write-Host "  - Testing: pytest"
    Write-Host "  - Linting: flake8, pylint"
    Write-Host "  - Formatting: black, isort"
    Write-Host "  - Type checking: mypy"
    Write-Host ""
}
