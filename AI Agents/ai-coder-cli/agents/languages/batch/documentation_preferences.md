
# Batch/Windows CMD Documentation Preferences

This document defines documentation standards for Windows Batch and CMD scripts.
These preferences guide AI agents in maintaining consistent documentation.

---

## General Documentation Philosophy

**Core Principles:**
1. **Clear Comments** - Batch has limited documentation features, use comments extensively
2. **Usage Information** - Provide clear usage instructions
3. **Error Codes** - Document all ERRORLEVEL values
4. **Environment Variables** - Document all variables used
5. **Windows Version** - Note Windows version requirements

---

## Script Documentation Standards

### Script Header

Every batch file should start with a comprehensive header:

```batch
@echo off
REM ===========================================================================
REM Script Name: script_name.bat
REM Description: Brief description of what this script does
REM
REM Usage: script_name.bat [OPTIONS] ARGS
REM
REM Options:
REM   /h, /?         Display this help message
REM   /v             Enable verbose output
REM   /d             Enable debug mode
REM
REM Arguments:
REM   ARG1           Description of first argument
REM   ARG2           Description of second argument (optional)
REM
REM Examples:
REM   script_name.bat /v arg1 arg2
REM   script_name.bat /d arg1
REM
REM Requirements:
REM   - Windows 7 or later
REM   - Additional tools: none
REM
REM Error Codes:
REM   0  Success
REM   1  General error
REM   2  Invalid arguments
REM   3  File not found
REM   4  Permission denied
REM
REM Author: Author Name
REM Created: YYYY-MM-DD
REM Modified: YYYY-MM-DD
REM Version: 1.0.0
REM ===========================================================================

setlocal enabledelayedexpansion

REM Set script constants
set "SCRIPT_NAME=%~n0"
set "SCRIPT_VERSION=1.0.0"
set "SCRIPT_DIR=%~dp0"
```

### Section Documentation

```batch
REM ---------------------------------------------------------------------------
REM Section: Initialize Variables
REM Purpose: Set up all script variables and defaults
REM ---------------------------------------------------------------------------
set "LOG_FILE=%TEMP%\%SCRIPT_NAME%.log"
set "DEBUG=0"
set "VERBOSE=0"

REM ---------------------------------------------------------------------------
REM Section: Parse Command Line Arguments
REM Purpose: Process command line options and arguments
REM ---------------------------------------------------------------------------
:parse_args
if "%~1"=="" goto :parse_args_done
if /i "%~1"=="/h" goto :show_help
if /i "%~1"=="/?" goto :show_help
if /i "%~1"=="/v" set "VERBOSE=1" & shift & goto :parse_args
if /i "%~1"=="/d" set "DEBUG=1" & shift & goto :parse_args

REM Store positional arguments
set "ARG1=%~1"
shift
goto :parse_args

:parse_args_done
```

### Function Documentation

```batch
REM ---------------------------------------------------------------------------
REM Function: FunctionName
REM Purpose: Brief description of what this function does
REM
REM Arguments:
REM   %1 - Description of first argument
REM   %2 - Description of second argument (optional)
REM
REM Returns:
REM   ERRORLEVEL 0 on success, non-zero on error
REM
REM Examples:
REM   call :FunctionName "arg1" "arg2"
REM   call :FunctionName "%VAR1%" "%VAR2%"
REM ---------------------------------------------------------------------------
:FunctionName
    setlocal
    set "param1=%~1"
    set "param2=%~2"
    
    REM Function implementation
    if "%param1%"=="" (
        echo Error: Parameter 1 required >&2
        exit /b 1
    )
    
    REM Do work
    echo Processing %param1%
    
    endlocal & exit /b 0
```

### Inline Comments

```batch
REM Single-line comment explaining the next command
set "variable=value"

REM Multi-line comment explaining
REM a more complex block of code
REM across several lines

REM TODO: Future enhancement needed
REM FIXME: Known bug to fix
REM NOTE: Important information
REM HACK: Temporary workaround

REM Check if file exists before processing
if exist "%FILE%" (
    REM Process the file
    call :ProcessFile "%FILE%"
)
```

---

## Project Documentation Structure

### Required Files

1. **README.md** - Project overview
2. **INSTALL.md** - Installation instructions
3. **USAGE.md** - Detailed usage guide
4. **CHANGELOG.md** - Version history
5. **examples/** - Example scripts

### README.md Structure

```markdown
# Script Name

Brief description of the batch script project.

![Windows](https://img.shields.io/badge/platform-Windows-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- Feature 1
- Feature 2
- Feature 3

## Requirements

- Windows 7 or later (Windows 10 recommended)
- Administrator privileges (if required)
- Additional tools:
  - Tool1 (optional)
  - Tool2 (optional)

## Installation

### Quick Install

Download `script_name.bat` and place in desired location.

### Adding to PATH

```batch
REM Run as Administrator
set "SCRIPT_DIR=C:\path\to\scripts"
setx PATH "%PATH%;%SCRIPT_DIR%" /M
```

### Manual Setup

1. Download all files
2. Extract to `C:\Scripts\`
3. Run `setup.bat` as Administrator

## Usage

### Basic Usage

```batch
script_name.bat [OPTIONS] ARGS
```

### Options

- `/h`, `/?` - Display help message
- `/v` - Enable verbose output
- `/d` - Enable debug mode
- `/c CONFIG` - Use custom config file

### Arguments

- `ARG1` - Description of first argument
- `ARG2` - Description of second argument (optional)

### Examples

#### Example 1: Basic Usage

```batch
script_name.bat input.txt
```

#### Example 2: With Options

```batch
script_name.bat /v /c custom.conf input.txt
```

#### Example 3: Debug Mode

```batch
script_name.bat /d input.txt
```

## Configuration

### Configuration File

Create `config.bat` in the script directory:

```batch
@echo off
REM Configuration settings
set "OPTION1=value1"
set "OPTION2=value2"
```

### Environment Variables

- `SCRIPT_DEBUG` - Enable debug mode (set to 1)
- `SCRIPT_LOG` - Path to log file

## Error Codes

- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - File not found
- `4` - Permission denied
- `5` - Configuration error

## Troubleshooting

### Common Issues

#### "Access Denied" Error

**Cause:** Script requires administrator privileges

**Solution:**
```batch
REM Right-click script and select "Run as administrator"
```

#### Path Contains Spaces

**Cause:** Spaces in file paths not properly quoted

**Solution:**
```batch
REM Always use quotes around paths
script_name.bat "C:\Path With Spaces\file.txt"
```

## Development

### Testing

```batch
REM Run test suite
test_runner.bat

REM Run specific test
test_specific.bat
```

### Style Guidelines

- Use `@echo off` at script start
- Use `setlocal` for variable scoping
- Quote all file paths
- Check ERRORLEVEL after commands
- Use descriptive variable names

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE)

## Changelog

See [CHANGELOG.md](CHANGELOG.md)
```

---

## Best Practices

### Variable Naming

```batch
REM Use descriptive uppercase names for global variables
set "SCRIPT_VERSION=1.0.0"
set "LOG_FILE=%TEMP%\script.log"

REM Use local scoping when possible
setlocal
set "local_var=value"
endlocal

REM Quote all paths and values with spaces
set "PATH_TO_FILE=C:\Program Files\App\file.txt"

REM Use delayed expansion for complex operations
setlocal enabledelayedexpansion
set "count=0"
for %%F in (*.txt) do (
    set /a count+=1
    echo Processing !count!: %%F
)
endlocal
```

### Error Handling

```batch
REM ---------------------------------------------------------------------------
REM Function: CheckError
REM Purpose: Check ERRORLEVEL and exit on error
REM
REM Arguments:
REM   %1 - Error message to display
REM   %2 - Error code (optional, default 1)
REM ---------------------------------------------------------------------------
:CheckError
    if errorlevel 1 (
        echo ERROR: %~1 >&2
        exit /b %2
    )
    exit /b 0

REM Usage
some_command.exe
call :CheckError "Command failed" 1

REM Alternative: Inline error checking
some_command.exe || (
    echo ERROR: Command failed >&2
    exit /b 1
)

REM Check file existence
if not exist "%FILE%" (
    echo ERROR: File not found: %FILE% >&2
    exit /b 3
)
```

### Help Function

```batch
REM ---------------------------------------------------------------------------
REM Function: ShowHelp
REM Purpose: Display help message
REM ---------------------------------------------------------------------------
:show_help
    echo.
    echo %SCRIPT_NAME% version %SCRIPT_VERSION%
    echo.
    echo Description:
    echo   Brief description of what this script does.
    echo.
    echo Usage:
    echo   %SCRIPT_NAME% [OPTIONS] ARGS
    echo.
    echo Options:
    echo   /h, /?        Display this help message
    echo   /v            Enable verbose output
    echo   /d            Enable debug mode
    echo   /c CONFIG     Use custom configuration file
    echo.
    echo Arguments:
    echo   ARG1          Description of first argument
    echo   ARG2          Description of second argument (optional)
    echo.
    echo Examples:
    echo   %SCRIPT_NAME% /v arg1 arg2
    echo   %SCRIPT_NAME% /d /c custom.conf arg1
    echo.
    echo Error Codes:
    echo   0  Success
    echo   1  General error
    echo   2  Invalid arguments
    echo   3  File not found
    echo.
    exit /b 0
```

### Logging

```batch
REM ---------------------------------------------------------------------------
REM Function: Log
REM Purpose: Write message to log file and optionally console
REM
REM Arguments:
REM   %1 - Log level (INFO, WARN, ERROR)
REM   %2 - Message to log
REM ---------------------------------------------------------------------------
:Log
    setlocal
    set "level=%~1"
    set "message=%~2"
    set "timestamp=%DATE% %TIME%"
    
    REM Write to log file
    echo [%timestamp%] [%level%] %message% >> "%LOG_FILE%"
    
    REM Write to console if verbose or error
    if "%VERBOSE%"=="1" (
        echo [%level%] %message%
    )
    if "%level%"=="ERROR" (
        echo [ERROR] %message% >&2
    )
    
    endlocal
    exit /b 0

REM Usage
call :Log "INFO" "Processing started"
call :Log "WARN" "Warning message"
call :Log "ERROR" "Error occurred"
```

---

## Template Script

```batch
@echo off
REM ===========================================================================
REM Script Name: template.bat
REM Description: Template batch script with documentation
REM
REM Usage: template.bat [OPTIONS] ARGS
REM
REM Options:
REM   /h, /?         Display help
REM   /v             Verbose mode
REM   /d             Debug mode
REM
REM Arguments:
REM   INPUT          Input file or directory
REM
REM Examples:
REM   template.bat /v input.txt
REM
REM Author: Name
REM Version: 1.0.0
REM ===========================================================================

setlocal enabledelayedexpansion

REM ---------------------------------------------------------------------------
REM Initialize Variables
REM ---------------------------------------------------------------------------
set "SCRIPT_NAME=%~n0"
set "SCRIPT_VERSION=1.0.0"
set "SCRIPT_DIR=%~dp0"
set "LOG_FILE=%TEMP%\%SCRIPT_NAME%.log"
set "VERBOSE=0"
set "DEBUG=0"

REM ---------------------------------------------------------------------------
REM Parse Arguments
REM ---------------------------------------------------------------------------
:parse_args
if "%~1"=="" goto :parse_args_done
if /i "%~1"=="/h" goto :show_help
if /i "%~1"=="/?" goto :show_help
if /i "%~1"=="/v" set "VERBOSE=1" & shift & goto :parse_args
if /i "%~1"=="/d" set "DEBUG=1" & shift & goto :parse_args

set "INPUT=%~1"
shift
goto :parse_args

:parse_args_done

REM ---------------------------------------------------------------------------
REM Validate Arguments
REM ---------------------------------------------------------------------------
if "%INPUT%"=="" (
    echo ERROR: Input required >&2
    goto :show_help
)

REM ---------------------------------------------------------------------------
REM Main Logic
REM ---------------------------------------------------------------------------
call :Log "INFO" "Script started"

REM Your code here

call :Log "INFO" "Script completed"
exit /b 0

REM ===========================================================================
REM Functions
REM ===========================================================================

REM ---------------------------------------------------------------------------
REM Function: ShowHelp
REM ---------------------------------------------------------------------------
:show_help
    echo %SCRIPT_NAME% version %SCRIPT_VERSION%
    echo.
    echo Usage: %SCRIPT_NAME% [OPTIONS] INPUT
    echo.
    echo Options:
    echo   /h, /?    Show this help
    echo   /v        Verbose mode
    echo   /d        Debug mode
    echo.
    exit /b 0

REM ---------------------------------------------------------------------------
REM Function: Log
REM Arguments: %1 = Level, %2 = Message
REM ---------------------------------------------------------------------------
:Log
    set "timestamp=%DATE% %TIME%"
    echo [%timestamp%] [%~1] %~2 >> "%LOG_FILE%"
    if "%VERBOSE%"=="1" echo [%~1] %~2
    exit /b 0
```

---

## Documentation Maintenance

### Maintenance Checklist

- [ ] Script header is complete and current
- [ ] All functions have comment blocks
- [ ] Help function is up to date
- [ ] Error codes are documented
- [ ] README.md reflects current usage
- [ ] Examples are tested and working
- [ ] Environment variables documented
- [ ] CHANGELOG.md updated

---

## AI Agent Guidelines

**For AI Agents Maintaining Documentation:**

1. **Comprehensive Headers** - Every script needs full header
2. **Function Comments** - Document all functions/subroutines
3. **Help Function** - Keep usage help current
4. **Error Codes** - Document all ERRORLEVEL values
5. **Environment Variables** - List all variables used
6. **Examples** - Include working examples
7. **Windows Compatibility** - Note Windows version requirements
8. **Path Handling** - Document proper path quoting

**Priority Order:**
1. Script headers
2. Function documentation
3. Help function
4. README.md
5. Error code documentation

---

**Last Updated:** 2025-10-12
**Version:** 1.0
