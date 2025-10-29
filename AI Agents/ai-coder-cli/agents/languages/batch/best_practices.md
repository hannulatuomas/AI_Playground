
# Batch/Windows CMD Best Practices

## Code Organization and Structure

### Script Structure
```batch
@echo off
REM ============================================================================
REM Script Name: backup_files.bat
REM Description: Backs up specified directories to a backup location
REM Author: Your Name
REM Date: 2024-01-01
REM Version: 1.0.0
REM
REM Usage: backup_files.bat [source] [destination]
REM
REM Example: backup_files.bat "C:\Data" "D:\Backup"
REM ============================================================================

REM Enable delayed expansion for variable handling in loops
setlocal enabledelayedexpansion

REM Set error level handling
if errorlevel 1 goto :error

REM Configuration
set "LOG_FILE=%~dp0backup.log"
set "MAX_RETRIES=3"

REM Validate arguments
if "%~1"=="" (
    echo Error: Source directory not specified
    goto :usage
)

if "%~2"=="" (
    echo Error: Destination directory not specified
    goto :usage
)

REM Main logic
call :main "%~1" "%~2"
goto :end

REM ============================================================================
REM Functions
REM ============================================================================

:main
    set "source=%~1"
    set "destination=%~2"
    
    echo Starting backup from %source% to %destination%
    call :log "Backup started"
    
    REM Backup logic here
    xcopy "%source%" "%destination%" /E /I /Y
    
    if errorlevel 1 (
        call :log "ERROR: Backup failed"
        exit /b 1
    )
    
    call :log "Backup completed successfully"
    exit /b 0

:log
    echo [%date% %time%] %~1 >> "%LOG_FILE%"
    echo [%date% %time%] %~1
    exit /b 0

:usage
    echo.
    echo Usage: %~nx0 [source] [destination]
    echo.
    echo   source        Source directory to backup
    echo   destination   Destination directory
    echo.
    echo Example:
    echo   %~nx0 "C:\Data" "D:\Backup"
    echo.
    exit /b 1

:error
    echo An error occurred during execution
    exit /b 1

:end
    endlocal
    exit /b 0
```

### Project Organization
```
project/
├── bin/                    # Main executable scripts
│   ├── deploy.bat
│   └── start.bat
├── lib/                    # Library/utility scripts
│   ├── common.bat
│   └── logging.bat
├── config/                 # Configuration files
│   ├── dev.config
│   └── prod.config
├── logs/                   # Log files
└── README.txt
```

## Naming Conventions

### Variables
```batch
REM Constants: UPPER_CASE
set "MAX_RETRIES=3"
set "LOG_DIR=C:\Logs"
set "API_URL=https://api.example.com"

REM Variables: PascalCase or lowercase
set "FileName=document.txt"
set "userCount=0"

REM Environment variables: UPPER_CASE
set "PATH=%PATH%;C:\MyApp\bin"
set "TEMP_DIR=%TEMP%"

REM Quote variables to handle spaces
set "FilePath=C:\Program Files\MyApp\file.txt"
```

### Labels and Functions
```batch
REM Labels: lowercase_with_underscores or camelCase
:main
:process_files
:validate_input
:cleanup

REM Use descriptive names
:check_prerequisites
:backup_database
:send_notification
```

### File Names
```batch
REM Script files: lowercase with .bat or .cmd extension
backup_database.bat
deploy_application.cmd
start_service.bat

REM Configuration files
app.config
settings.ini
```

## Error Handling Patterns

### Error Level Checking
```batch
@echo off
setlocal enabledelayedexpansion

REM Check command success
xcopy "source" "dest" /E /I /Y
if errorlevel 1 (
    echo Error: Copy failed
    exit /b 1
)

REM Check specific error level
some_command
if %errorlevel% equ 0 (
    echo Success
) else if %errorlevel% equ 1 (
    echo Warning
) else (
    echo Error: %errorlevel%
    exit /b %errorlevel%
)

REM Store error level immediately
command
set "EXIT_CODE=%errorlevel%"
if %EXIT_CODE% neq 0 (
    echo Command failed with error code %EXIT_CODE%
    exit /b %EXIT_CODE%
)
```

### Error Handling Functions
```batch
:handle_error
    set "error_message=%~1"
    set "error_code=%~2"
    
    call :log "ERROR: %error_message%"
    echo ERROR: %error_message%
    
    REM Cleanup before exit
    call :cleanup
    
    exit /b %error_code%

REM Usage
if not exist "%FILE%" (
    call :handle_error "File not found: %FILE%" 2
)
```

### Validation
```batch
:validate_file
    set "file=%~1"
    
    if "%file%"=="" (
        echo Error: File parameter is empty
        exit /b 1
    )
    
    if not exist "%file%" (
        echo Error: File does not exist: %file%
        exit /b 2
    )
    
    exit /b 0

:validate_directory
    set "dir=%~1"
    
    if "%dir%"=="" exit /b 1
    if not exist "%dir%" exit /b 2
    if not exist "%dir%\*" exit /b 3
    
    exit /b 0
```

### Cleanup on Exit
```batch
@echo off
setlocal

REM Create temp file
set "TEMP_FILE=%TEMP%\myapp_%RANDOM%.tmp"
echo Data > "%TEMP_FILE%"

REM Ensure cleanup happens
call :main
set "EXIT_CODE=%errorlevel%"

REM Always run cleanup
call :cleanup

exit /b %EXIT_CODE%

:cleanup
    if exist "%TEMP_FILE%" del /Q "%TEMP_FILE%"
    exit /b 0
```

## Performance Considerations

### Minimize External Commands
```batch
REM BAD: Multiple calls to external commands
for /f %%i in ('dir /b *.txt') do (
    for /f %%j in ('type "%%i" ^| find /c /v ""') do (
        echo %%i has %%j lines
    )
)

REM BETTER: Minimize command calls
for %%i in (*.txt) do (
    call :count_lines "%%i"
)

:count_lines
    set "file=%~1"
    set "count=0"
    for /f %%j in ('type "%file%" ^| find /c /v ""') do set "count=%%j"
    echo %file% has %count% lines
    exit /b 0
```

### Use Built-in Commands
```batch
REM Check if file exists - built-in
if exist "file.txt" echo File exists

REM Check if directory exists
if exist "C:\Directory\*" echo Directory exists

REM String operations
set "str=Hello World"
set "length=0"
for /l %%i in (0,1,100) do (
    if "!str:~%%i,1!" neq "" set /a length+=1
)
```

### Batch File Performance
```batch
REM Reduce disk I/O by batching operations
REM BAD: Write to file in loop
for %%i in (*.txt) do (
    echo Processing %%i >> log.txt
)

REM BETTER: Accumulate then write once
set "LOG_CONTENT="
for %%i in (*.txt) do (
    set "LOG_CONTENT=!LOG_CONTENT!Processing %%i%NL%"
)
echo !LOG_CONTENT! > log.txt
```

### Delayed Expansion
```batch
REM Use delayed expansion for variables in loops
setlocal enabledelayedexpansion

set "count=0"
for %%i in (*.txt) do (
    set /a count+=1
    echo Processing file !count!: %%i
)

REM Without delayed expansion, %count% would always be 0
```

## Security Best Practices

### Input Validation
```batch
:validate_input
    set "input=%~1"
    
    REM Check if empty
    if "%input%"=="" (
        echo Error: Input cannot be empty
        exit /b 1
    )
    
    REM Check for dangerous characters
    echo %input% | findstr /R "[&|<>^]" >nul
    if not errorlevel 1 (
        echo Error: Input contains invalid characters
        exit /b 1
    )
    
    exit /b 0
```

### Quote Variables
```batch
REM Always quote variables to prevent injection
REM BAD:
set input=%1
del %input%

REM GOOD:
set "input=%~1"
if exist "%input%" del "%input%"

REM Quote paths with spaces
set "ProgramPath=C:\Program Files\MyApp\app.exe"
"%ProgramPath%" --help
```

### Avoid Command Injection
```batch
REM BAD: Unsanitized user input
set /p userInput="Enter filename: "
type %userInput%

REM BETTER: Validate and quote
set /p "userInput=Enter filename: "
call :validate_input "%userInput%"
if errorlevel 1 goto :error

if exist "%userInput%" (
    type "%userInput%"
) else (
    echo File not found
)
```

### Secure File Operations
```batch
REM Check file paths are within expected directory
:validate_path
    set "file=%~f1"
    set "base=%~f2"
    
    REM Get full paths
    if not "%file:~0,100%"=="%base%" (
        echo Error: File is outside base directory
        exit /b 1
    )
    
    exit /b 0
```

### Don't Echo Sensitive Data
```batch
REM Don't echo passwords or sensitive data
@echo off

REM BAD:
echo Password is: %PASSWORD%

REM GOOD:
REM Use password without displaying
net use \\server\share /user:username %PASSWORD% >nul 2>&1
```

## Testing Approaches

### Manual Testing
```batch
REM Enable test mode
set "TEST_MODE=1"

if "%TEST_MODE%"=="1" (
    echo Running in TEST MODE
    set "DATA_DIR=C:\TestData"
) else (
    set "DATA_DIR=C:\Production"
)

REM Mock external commands in test mode
if "%TEST_MODE%"=="1" (
    REM Use test implementations
    call :mock_database_query
) else (
    REM Use real implementations
    call :database_query
)
```

### Validation Functions
```batch
:test_validate_email
    call :validate_email "user@example.com"
    if errorlevel 1 (
        echo FAIL: Valid email rejected
        exit /b 1
    )
    
    call :validate_email "invalid"
    if not errorlevel 1 (
        echo FAIL: Invalid email accepted
        exit /b 1
    )
    
    echo PASS: Email validation works
    exit /b 0

:validate_email
    set "email=%~1"
    echo %email% | findstr /R "@.*\." >nul
    exit /b %errorlevel%
```

### Debug Mode
```batch
@echo off
setlocal

REM Enable debug output
set "DEBUG=1"

REM Debug logging function
:debug
    if "%DEBUG%"=="1" echo [DEBUG] %~1
    exit /b 0

REM Usage
call :debug "Starting process"
call :debug "Variable value: %VAR%"
```

### Assertions
```batch
:assert_equals
    set "expected=%~1"
    set "actual=%~2"
    set "message=%~3"
    
    if not "%expected%"=="%actual%" (
        echo ASSERTION FAILED: %message%
        echo   Expected: %expected%
        echo   Actual:   %actual%
        exit /b 1
    )
    exit /b 0

REM Usage
call :get_value
call :assert_equals "expected_value" "%RESULT%" "get_value should return expected_value"
```

## Documentation Standards

### Script Header
```batch
@echo off
REM ============================================================================
REM Script Name: process_data.bat
REM Description: Processes data files and generates reports
REM
REM Author: John Doe
REM Email: john.doe@example.com
REM Date: 2024-01-01
REM Version: 1.2.0
REM
REM Usage:
REM   process_data.bat [input_dir] [output_dir] [options]
REM
REM Parameters:
REM   input_dir     Directory containing input files
REM   output_dir    Directory for output files
REM   options       Optional: /verbose /test
REM
REM Options:
REM   /verbose      Enable verbose output
REM   /test         Run in test mode
REM   /help         Display this help message
REM
REM Examples:
REM   process_data.bat "C:\Input" "C:\Output"
REM   process_data.bat "C:\Input" "C:\Output" /verbose
REM
REM Exit Codes:
REM   0   Success
REM   1   Invalid arguments
REM   2   Input directory not found
REM   3   Processing error
REM
REM Dependencies:
REM   - Windows 7 or later
REM   - Administrator privileges required
REM
REM Notes:
REM   - Ensure input files are in UTF-8 format
REM   - Output directory will be created if it doesn't exist
REM
REM ============================================================================
```

### Function Documentation
```batch
REM ============================================================================
REM Function: backup_directory
REM Description: Backs up a directory to a specified location
REM Parameters:
REM   %1 - Source directory path
REM   %2 - Destination directory path
REM   %3 - (Optional) Backup mode: full|incremental
REM Returns:
REM   0 - Success
REM   1 - Invalid parameters
REM   2 - Source not found
REM   3 - Backup failed
REM Example:
REM   call :backup_directory "C:\Data" "D:\Backup" "full"
REM ============================================================================
:backup_directory
    set "source=%~1"
    set "destination=%~2"
    set "mode=%~3"
    if "%mode%"=="" set "mode=full"
    
    REM Implementation
    exit /b 0
```

### Inline Comments
```batch
REM Use comments to explain complex logic
REM Not necessary for obvious operations

REM BAD:
set /a count+=1  REM Increment count

REM GOOD:
REM Track retry attempts for exponential backoff calculation
set /a retryCount+=1

REM Document sections
REM ============================================================================
REM Initialization
REM ============================================================================
set "LOG_FILE=%~dp0log.txt"
set "MAX_RETRIES=3"

REM ============================================================================
REM Main Processing
REM ============================================================================
call :process_files

REM ============================================================================
REM Cleanup
REM ============================================================================
call :cleanup
```

## Common Pitfalls to Avoid

### 1. Unquoted Variables
```batch
REM BAD:
set file=my file.txt
if exist %file% echo Found

REM GOOD:
set "file=my file.txt"
if exist "%file%" echo Found
```

### 2. Variable Expansion in Loops
```batch
REM BAD: Variable not updated in loop
set count=0
for %%i in (*.txt) do (
    set /a count+=1
    echo %count%  REM Always shows 0
)

REM GOOD: Use delayed expansion
setlocal enabledelayedexpansion
set count=0
for %%i in (*.txt) do (
    set /a count+=1
    echo !count!  REM Shows actual count
)
```

### 3. Not Checking Error Levels
```batch
REM BAD:
copy "source.txt" "dest.txt"
echo Copy complete

REM GOOD:
copy "source.txt" "dest.txt"
if errorlevel 1 (
    echo Copy failed
    exit /b 1
)
echo Copy complete
```

### 4. Using goto Instead of call
```batch
REM BAD: goto doesn't return
:main
    goto :function1
    echo This never executes
:function1
    echo In function1
    exit /b 0

REM GOOD: call returns
:main
    call :function1
    echo This executes
    exit /b 0
:function1
    echo In function1
    exit /b 0
```

### 5. Not Using setlocal
```batch
REM BAD: Variables persist globally
set "temp_var=value"
REM ... script continues

REM GOOD: Variables are local
setlocal
set "temp_var=value"
REM ... script continues
endlocal  REM temp_var is removed
```

## Language-Specific Idioms and Patterns

### String Manipulation
```batch
REM Substring extraction
set "str=Hello World"
set "sub=%str:~0,5%"  REM "Hello"
set "sub=%str:~6%"    REM "World"

REM String replacement
set "str=Hello World"
set "new=%str:World=Universe%"  REM "Hello Universe"

REM Remove substring
set "str=Hello World"
set "new=%str:World=%"  REM "Hello "

REM Case conversion (limited)
REM Convert to uppercase (requires external tool or workaround)
for %%i in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    set "str=!str:%%i=%%i!"
)
```

### File Operations
```batch
REM Get file extension
set "file=document.txt"
for %%i in ("%file%") do set "ext=%%~xi"  REM .txt

REM Get filename without extension
for %%i in ("%file%") do set "name=%%~ni"  REM document

REM Get full path
for %%i in ("%file%") do set "path=%%~fi"

REM Get drive
for %%i in ("%file%") do set "drive=%%~di"

REM Get directory
for %%i in ("%file%") do set "dir=%%~pi"

REM Get file size
for %%i in ("%file%") do set "size=%%~zi"

REM Get file date/time
for %%i in ("%file%") do set "date=%%~ti"
```

### Loops
```batch
REM For loop with files
for %%i in (*.txt) do (
    echo Processing %%i
)

REM For loop with directories
for /d %%i in (*) do (
    echo Directory: %%i
)

REM Recursive loop
for /r "C:\Path" %%i in (*.txt) do (
    echo Found: %%i
)

REM For loop with command output
for /f "tokens=*" %%i in ('dir /b *.txt') do (
    echo %%i
)

REM For loop with counter
for /l %%i in (1,1,10) do (
    echo Number: %%i
)

REM While-like loop
:while_loop
if %count% lss 10 (
    echo Count: %count%
    set /a count+=1
    goto :while_loop
)
```

### Arithmetic
```batch
REM Basic arithmetic
set /a result=5+3          REM 8
set /a result=10-4         REM 6
set /a result=3*4          REM 12
set /a result=15/3         REM 5
set /a result=17%%5        REM 2 (modulo)

REM Compound operations
set /a result=(5+3)*2      REM 16
set /a result=5+(3*2)      REM 11

REM Increment/Decrement
set /a count+=1
set /a count-=1
set /a count*=2
set /a count/=2

REM Variables in expressions
set /a sum=num1+num2
set /a average=(num1+num2)/2
```

### Conditional Statements
```batch
REM If-else
if "%VAR%"=="value" (
    echo Match
) else (
    echo No match
)

REM If-else if-else
if %NUM% lss 10 (
    echo Less than 10
) else if %NUM% equ 10 (
    echo Equal to 10
) else (
    echo Greater than 10
)

REM String comparisons
if "%STR1%"=="%STR2%" echo Equal
if /i "%STR1%"=="%STR2%" echo Equal (case-insensitive)

REM Numeric comparisons
if %NUM% equ 10 echo Equal
if %NUM% neq 10 echo Not equal
if %NUM% lss 10 echo Less than
if %NUM% leq 10 echo Less than or equal
if %NUM% gtr 10 echo Greater than
if %NUM% geq 10 echo Greater than or equal

REM File/Directory checks
if exist "file.txt" echo File exists
if not exist "file.txt" echo File not found
if exist "C:\Directory\*" echo Directory exists

REM Defined variable check
if defined VAR echo Variable is set
if not defined VAR echo Variable is not set
```

### Functions and Subroutines
```batch
REM Simple function
:my_function
    echo In my_function
    exit /b 0

REM Function with parameters
:add_numbers
    set /a result=%1+%2
    echo Result: %result%
    exit /b 0

REM Usage
call :add_numbers 5 3

REM Function with return value (via variable)
:get_date
    set "return_value=%date%"
    exit /b 0

call :get_date
echo Current date: %return_value%

REM Function with error handling
:safe_function
    if "%~1"=="" (
        echo Error: Parameter required
        exit /b 1
    )
    
    REM Do something with %1
    exit /b 0
```

### Working with Environment
```batch
REM Get script directory
set "SCRIPT_DIR=%~dp0"

REM Get script name
set "SCRIPT_NAME=%~nx0"

REM Get script drive
set "SCRIPT_DRIVE=%~d0"

REM Current directory
set "CURRENT_DIR=%CD%"

REM Temporary files
set "TEMP_FILE=%TEMP%\myapp_%RANDOM%.tmp"

REM User profile
set "USER_PROFILE=%USERPROFILE%"

REM Computer name
set "COMPUTER=%COMPUTERNAME%"

REM User name
set "USER=%USERNAME%"
```

### Error Handling Patterns
```batch
REM Try-catch pattern
call :risky_operation
if errorlevel 1 (
    call :handle_error "Operation failed"
    goto :cleanup
)

:risky_operation
    REM Risky code here
    if exist "file.txt" (
        exit /b 0
    ) else (
        exit /b 1
    )

:handle_error
    echo Error: %~1
    exit /b 0

:cleanup
    REM Cleanup code
    exit /b 0
```
