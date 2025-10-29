
# Batch/Windows CMD User Preferences

## Script Type and Compatibility

### File Extension
```yaml
# Script file extension
file_extension: bat

# Options:
# - bat: .bat (universal)
# - cmd: .cmd (CMD.exe specific)

# Both work the same in modern Windows, but .bat is more universal
```

### Windows Version Support
```yaml
# Minimum Windows version
min_windows_version: windows_7

# Options:
# - windows_xp: Windows XP and above
# - windows_7: Windows 7 and above (recommended)
# - windows_10: Windows 10 and above

# Target CMD version
cmd_version: modern

# Options:
# - modern: Windows 7+ CMD features
# - legacy: XP-compatible
```

## Code Style Preferences

### Case Style
```yaml
# Command case
command_case: lowercase

# Options:
# - lowercase: echo, set, if
# - UPPERCASE: ECHO, SET, IF
# - mixed: Mixed case

# Variable case
variable_case: UPPERCASE

# Options:
# - UPPERCASE: %USERNAME%, %TEMP%
# - PascalCase: %UserName%, %Temp%
# - mixed: Mixed case (not recommended)
```

### Indentation
```yaml
# Indentation style
indent_style: spaces
indent_size: 4

# Indent blocks
indent_blocks: true

# Example:
# if condition (
#     command1
#     command2
# )
```

### Echo Off
```yaml
# Use @echo off
use_echo_off: true

# Position
echo_off_position: first_line

# Options:
# - first_line: @echo off (first line)
# - after_header: After comment header
```

### Comments
```yaml
# Comment style
comment_style: REM

# Options:
# - REM: REM comment
# - double_colon: :: comment (faster but can cause issues)
# - mixed: Use both appropriately

# Block comments
block_comment_style: REM_lines

# Options:
# - REM_lines: Multiple REM lines
# - separator_lines: Lines with === or ---
```

## Variable Handling

### Variable Quoting
```yaml
# Quote variables
quote_variables: always

# Options:
# - always: Always quote "%variable%"
# - when_needed: Only when spaces expected
# - never: Never quote (not recommended)

# Set command quoting
set_quote_style: quotes

# Options:
# - quotes: set "variable=value"
# - no_quotes: set variable=value
```

### Delayed Expansion
```yaml
# Use delayed expansion
delayed_expansion: when_needed

# Options:
# - always: setlocal enabledelayedexpansion (always)
# - when_needed: Only in loops/blocks
# - never: Don't use

# Delayed expansion preference
delayed_expansion_default: enabled

# Options:
# - enabled: Enable by default in scripts
# - disabled: Enable only when needed
```

### Variable Naming
```yaml
# Variable naming convention
variable_naming: UPPER_CASE

# Options:
# - UPPER_CASE: MAX_RETRIES, FILE_PATH
# - PascalCase: MaxRetries, FilePath
# - snake_case: max_retries, file_path

# Private variable prefix
private_variable_prefix: underscore

# Options:
# - underscore: _privateVar
# - none: No prefix
```

## Control Flow

### If Statement Style
```yaml
# If statement formatting
if_style: compact

# Options:
# - compact: if condition ( ... )
# - expanded: if condition (
#              ...
#             )

# Comparison operators
comparison_style: symbolic

# Options:
# - symbolic: EQU, NEQ, LSS, GTR
# - mixed: Use both as appropriate
```

### For Loop Preferences
```yaml
# For loop usage
for_loop_preference: appropriate_type

# Options:
# - appropriate_type: Use correct for variant
# - minimal: Use basic for when possible

# For /F options
for_f_options: explicit

# Always specify tokens, delims, etc. explicitly

# Loop variable naming
loop_variable: lowercase

# Options:
# - lowercase: %%i, %%j
# - uppercase: %%I, %%J
```

### Goto vs Call
```yaml
# Function implementation
function_style: call_label

# Options:
# - call_label: Use call :function
# - goto_label: Use goto :function (avoid)

# Return from functions
function_return: exit_b

# Always use exit /b for functions
```

## Error Handling

### Error Checking
```yaml
# Check error levels
check_error_levels: always

# Options:
# - always: Check after every command
# - critical: Only critical commands
# - minimal: Minimal checking

# Error level checking style
errorlevel_check_style: errorlevel_1

# Options:
# - errorlevel_1: if errorlevel 1
# - errorlevel_var: if %errorlevel% neq 0
# - both: Use appropriately
```

### Error Handling Functions
```yaml
# Use error handling functions
use_error_functions: true

# Error reporting style
error_reporting: descriptive

# Options:
# - descriptive: Detailed error messages
# - minimal: Basic error messages
# - silent: No error messages (not recommended)

# Exit on error
exit_on_error: critical_only

# Options:
# - always: Exit on any error
# - critical_only: Only critical errors
# - never: Never exit (handle in script)
```

### Cleanup
```yaml
# Use cleanup functions
use_cleanup: true

# Cleanup trigger
cleanup_trigger: label_call

# Options:
# - label_call: Call :cleanup before exit
# - inline: Cleanup code inline

# Cleanup temp files
auto_cleanup_temp: true
```

## Script Structure

### Script Header
```yaml
# Include header
include_header: true

# Header style
header_style: block_comment

# Options:
# - block_comment: REM block
# - separator_lines: Lines with ===

# Header sections
header_sections:
  - script_name
  - description
  - author
  - date
  - version
  - usage
  - examples
  - exit_codes
```

### Function Organization
```yaml
# Function organization
function_organization: end_of_file

# Options:
# - end_of_file: All functions at end
# - inline: Functions where used
# - separate_section: Dedicated function section

# Function documentation
document_functions: true

# Function naming
function_naming: descriptive_lowercase

# Options:
# - descriptive_lowercase: :check_prerequisites
# - snake_case: :check_prerequisites
# - camelCase: :checkPrerequisites
```

### Main Logic
```yaml
# Main script pattern
main_pattern: call_main

# Options:
# - call_main: call :main, goto :end
# - inline: Direct execution
# - function_first: Define functions first

# Script flow
script_flow: structured

# Example:
# @echo off
# setlocal
# REM Header
# REM Main logic
# call :main
# goto :end
# REM Functions
# :main
# ...
# :end
# endlocal
```

## Input/Output

### User Input
```yaml
# Input method
input_method: set_p

# Options:
# - set_p: set /p variable=prompt
# - choice: choice command
# - both: Use appropriately

# Input validation
validate_input: always

# Validate all user input for safety
```

### Output
```yaml
# Output command
output_command: echo

# Output redirection
output_redirection: explicit

# Always be explicit with > >> 2>&1

# Progress indicators
show_progress: true

# Options:
# - true: Show progress messages
# - false: Silent execution
# - verbose_only: Only in verbose mode
```

### Logging
```yaml
# Use logging
use_logging: true

# Log level
default_log_level: INFO

# Options:
# - DEBUG: Detailed debugging
# - INFO: General information
# - WARNING: Warnings only
# - ERROR: Errors only

# Log destination
log_destination: file

# Options:
# - file: Log to file
# - console: Console only
# - both: Both file and console

# Log file location
log_file_location: script_directory

# Options:
# - script_directory: Same as script
# - temp: %TEMP% directory
# - custom: Custom location
```

## File Operations

### File Existence Checks
```yaml
# Check file existence
check_file_existence: before_operations

# Options:
# - always: Before every operation
# - before_operations: Before file operations
# - minimal: Only when critical

# Directory checks
check_directory: before_use
```

### Path Handling
```yaml
# Path quoting
quote_paths: always

# Handle spaces in paths
space_handling: quotes

# Use %~dp0 for script directory
use_dp0: true

# Get full paths
full_path_method: for_loop

# Example: for %%i in ("%file%") do set "fullpath=%%~fi"
```

## Performance

### Command Optimization
```yaml
# Minimize external command calls
minimize_external_calls: true

# Use internal commands
prefer_internal_commands: true

# Example: use 'if exist' instead of calling 'dir'

# Batch file redirection
use_redirection_optimization: true

# Example: (echo line1 & echo line2) > file
```

### Loop Optimization
```yaml
# Loop optimization
optimize_loops: true

# Avoid nested loops when possible
minimize_nested_loops: true
```

## Security

### Input Sanitization
```yaml
# Sanitize input
sanitize_input: always

# Options:
# - always: Always sanitize
# - user_input_only: Only user input
# - never: No sanitization (dangerous)

# Check for dangerous characters
dangerous_char_check: true

# Dangerous: & | < > ^ ( )
```

### Secure File Operations
```yaml
# Validate file paths
validate_paths: true

# Prevent path traversal
check_path_traversal: true

# Example: Ensure paths don't contain ../
```

### Credential Handling
```yaml
# Never echo passwords
echo_passwords: never

# Store credentials
credential_storage: environment_variable

# Options:
# - environment_variable: Use environment variables
# - file: Secure file (encrypted)
# - credential_manager: Windows Credential Manager
# - none: Don't store (prompt)
```

## Testing

### Testing Approach
```yaml
# Test scripts
use_testing: true

# Test mode
test_mode: environment_variable

# Options:
# - environment_variable: set TEST_MODE=1
# - parameter: Pass /test parameter
# - separate_script: Separate test script

# Mock external commands
mock_external_commands: test_mode

# Options:
# - always: Always mock in tests
# - test_mode: Only in test mode
# - never: Don't mock
```

### Validation
```yaml
# Validate script logic
use_validation: true

# Validation functions
validation_functions: dedicated

# Options:
# - dedicated: Dedicated validation functions
# - inline: Inline validation
# - both: Mix of both
```

## Documentation

### Comment Density
```yaml
# Comment level
comment_level: moderate

# Options:
# - verbose: Comment most lines
# - moderate: Comment complex logic
# - minimal: Only essential comments

# Explain "why" not "what"
explain_why: true
```

### Usage Information
```yaml
# Include usage function
include_usage: true

# Usage trigger
usage_trigger: help_parameter

# Options:
# - help_parameter: /?, /h, /help
# - no_parameters: When no parameters provided
# - both: Both conditions

# Usage format
usage_format: detailed

# Options:
# - detailed: Full usage with examples
# - brief: Brief usage only
```

### Examples
```yaml
# Include examples in header
include_examples: true

# Number of examples
example_count: 2-3

# Example complexity
example_complexity: simple_to_complex

# Start with simple example, add complex ones
```

## Maintenance

### Version Control
```yaml
# Include version in script
include_version: true

# Version format
version_format: semver

# Options:
# - semver: 1.0.0 (Semantic Versioning)
# - date: YYYY-MM-DD
# - simple: 1.0

# Version location
version_location: header

# Options:
# - header: In script header
# - variable: In variable (set VERSION=1.0.0)
# - both: Both locations
```

### Change Log
```yaml
# Maintain change log
maintain_changelog: true

# Change log location
changelog_location: header

# Options:
# - header: In script header comments
# - separate_file: CHANGELOG.txt
# - both: Both locations
```

## Compatibility

### PowerShell Consideration
```yaml
# PowerShell compatibility notes
powershell_compat: document

# Options:
# - document: Document PS alternatives
# - ignore: Don't consider PowerShell
# - hybrid: Provide PS version too

# Recommend PowerShell
recommend_powershell_when: complex_logic

# Options:
# - complex_logic: For complex scripts
# - always: Always recommend
# - never: Never recommend
```

### Alternative Shells
```yaml
# Support other shells
other_shells: cmd_only

# Options:
# - cmd_only: CMD only
# - command_com: Also support COMMAND.COM
# - document: Document limitations
```

## Deployment

### Distribution
```yaml
# Distribution method
distribution_method: single_file

# Options:
# - single_file: Single .bat file
# - directory: Directory with supporting files
# - installer: Windows installer

# Include dependencies
bundle_dependencies: when_necessary

# Options:
# - always: Always bundle
# - when_necessary: Only if needed
# - never: Assume installed
```

### Installation
```yaml
# Installation script
include_installer: complex_scripts

# Options:
# - always: Always include
# - complex_scripts: Only for complex scripts
# - never: No installer

# Install location
default_install_location: program_files

# Options:
# - program_files: C:\Program Files
# - user_profile: %USERPROFILE%
# - custom: Let user choose
```

## Advanced Features

### Advanced Commands
```yaml
# Use advanced CMD features
advanced_features: when_beneficial

# Options:
# - always: Use all features
# - when_beneficial: Only when helpful
# - minimal: Stick to basics

# Features to use:
# - Delayed expansion
# - For /F parsing
# - String manipulation
# - Array simulation
```

### External Tools
```yaml
# Allow external tools
external_tools: documented

# Options:
# - allowed: Allow external tools
# - documented: Document requirements
# - avoid: Avoid if possible

# Required tools documentation
document_requirements: true
```

## Error Codes

### Exit Code Convention
```yaml
# Use exit codes
use_exit_codes: true

# Exit code convention
exit_code_convention: standard

# Standard:
# 0 - Success
# 1 - General error
# 2 - Misuse/invalid arguments
# 3+ - Specific errors

# Document exit codes
document_exit_codes: true

# Location
exit_code_documentation: header

# Options:
# - header: In script header
# - usage: In usage function
# - both: Both locations
```
