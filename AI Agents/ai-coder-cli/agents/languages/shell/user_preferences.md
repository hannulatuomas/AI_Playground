
# Bash/Zsh/Sh User Preferences

## Shell Type Preferences

### Shell Compatibility
```yaml
# Target shell
target_shell: bash

# Options:
# - bash: Bash (most common)
# - zsh: Zsh (modern features)
# - sh: POSIX sh (maximum compatibility)
# - dash: Dash (faster, minimal)

# Minimum bash version
min_bash_version: "4.0"

# Options:
# - "4.0": Associative arrays support
# - "4.3": nameref support
# - "5.0": Latest features
```

### POSIX Compliance
```yaml
# POSIX compliance level
posix_compliance: prefer_posix

# Options:
# - strict_posix: Strict POSIX sh only
# - prefer_posix: Use POSIX when possible
# - bash_specific: Use bash-specific features
# - zsh_specific: Use zsh-specific features
```

## Code Style Preferences

### Indentation and Formatting
```yaml
# Indentation
indent_style: spaces
indent_size: 4  # or 2

# Line length
max_line_length: 80

# Brace style
brace_style: same_line

# Options:
# - same_line: function_name() {
# - next_line: function_name()
#              {
```

### Shebang
```yaml
# Shebang preference
shebang: env_bash

# Options:
# - env_bash: #!/usr/bin/env bash (portable)
# - direct_bash: #!/bin/bash (direct path)
# - env_sh: #!/usr/bin/env sh (POSIX)
# - direct_sh: #!/bin/sh (direct POSIX)
```

### Quoting Style
```yaml
# Variable quoting
quoting_style: always_quote

# Options:
# - always_quote: Always quote variables "${var}"
# - quote_when_needed: Quote only when needed
# - minimal: Minimal quoting

# String quotes
string_quotes: double

# Options:
# - double: "string" (allows expansion)
# - single: 'string' (literal)
```

### Naming Conventions
```yaml
# Variable naming
variable_naming: lowercase_underscore

# Options:
# - lowercase_underscore: my_variable
# - camelCase: myVariable

# Constant naming
constant_naming: UPPER_CASE

# Function naming
function_naming: lowercase_underscore

# Options:
# - lowercase_underscore: my_function
# - kebab-case: my-function
```

### Error Handling
```yaml
# Strict error handling
strict_mode: true  # set -euo pipefail

# Options:
# - true: Enable set -euo pipefail
# - false: Manual error handling

# Trap usage
use_traps: true  # For cleanup

# Error reporting
error_reporting: verbose

# Options:
# - verbose: Detailed error messages
# - minimal: Basic error messages
# - quiet: Silent errors (not recommended)
```

## Tooling Preferences

### Linter
```yaml
# Shell script linter
linter: shellcheck

# ShellCheck severity
shellcheck_severity: warning

# Options:
# - error: Only errors
# - warning: Warnings and errors
# - info: Include informational messages
# - style: Include style suggestions

# ShellCheck exceptions
shellcheck_exclude:
  # - SC2034  # Unused variable
  # - SC2086  # Double quote to prevent globbing
```

### Formatter
```yaml
# Shell script formatter
formatter: shfmt

# shfmt options
shfmt_indent: 4
shfmt_binary_next_line: false  # Operators on next line
shfmt_switch_case_indent: true
shfmt_redirect_follow: false   # Redirect ops follow command

# Format on save
format_on_save: true
```

### Testing Framework
```yaml
# Testing framework
test_framework: bats

# Options:
# - bats: Bash Automated Testing System
# - shunit2: shUnit2 (xUnit-style)
# - shellspec: ShellSpec (BDD-style)
# - manual: Manual testing scripts

# Test file naming
test_file_pattern: "test_*.sh"  # or "*.bats"
```

## Project Structure Preferences

### Directory Layout
```yaml
# Project structure
project_structure: standard

# Standard structure:
# project/
#   bin/           # Executable scripts
#   lib/           # Library/function files
#   tests/         # Test scripts
#   docs/          # Documentation
#   config/        # Configuration files
#   README.md
```

### Library Organization
```yaml
# Source common libraries
use_library_files: true

# Library location
lib_directory: lib

# Automatic sourcing
auto_source_libs: true
```

### Configuration Files
```yaml
# Configuration file format
config_format: dotenv

# Options:
# - dotenv: .env files
# - conf: .conf files
# - ini: .ini files
# - shell: Shell source files

# Configuration location
config_directory: config
```

## Function and Script Preferences

### Function Declaration Style
```yaml
# Function declaration style
function_style: function_keyword

# Options:
# - function_keyword: function my_func { }
# - parentheses: my_func() { }
# - both: function my_func() { }

# Return values
return_method: exit_code

# Options:
# - exit_code: Use exit codes
# - echo_output: Echo output and capture
# - global_variable: Set global variable
```

### Script Initialization
```yaml
# Include standard header
include_header: true

# Set options
set_options:
  - errexit    # -e: Exit on error
  - nounset    # -u: Exit on undefined variable
  - pipefail   # -o pipefail: Exit on pipe failure

# Set IFS
reset_ifs: true  # IFS=$' \t\n'
```

### Error Handling Pattern
```yaml
# Error handling approach
error_handling: trap_and_functions

# Options:
# - trap_and_functions: Use trap and error functions
# - manual_checking: Manual error checking
# - ignore: Minimal error handling (not recommended)

# Cleanup on exit
cleanup_on_exit: true
```

## Command Preferences

### Command Substitution
```yaml
# Command substitution style
command_substitution: dollar_parentheses

# Options:
# - dollar_parentheses: $(command)
# - backticks: `command` (legacy, avoid)
```

### Test Commands
```yaml
# Test command style
test_command: double_brackets

# Options:
# - double_brackets: [[ condition ]] (bash/zsh)
# - single_brackets: [ condition ] (POSIX)
# - test_command: test condition (POSIX)
```

### Arithmetic
```yaml
# Arithmetic evaluation style
arithmetic_style: double_parentheses

# Options:
# - double_parentheses: $((expression))
# - expr: expr expression (POSIX)
# - bc: echo "expression" | bc (for floating point)
```

## Loop and Conditional Preferences

### Loop Style
```yaml
# Preferred loop for files
file_loop: find_while

# Options:
# - find_while: find ... | while read
# - for_loop: for file in *
# - globstar: for file in **/* (bash 4+)

# Read loop
read_loop: while_ifs_read

# Options:
# - while_ifs_read: while IFS= read -r line
# - for_loop: for line in $(cat file) (avoid)
```

### Conditional Style
```yaml
# If-else formatting
conditional_style: compact

# Options:
# - compact: if [[ condition ]]; then
# - expanded: if [[ condition ]]
#             then

# Case statement indentation
case_indent: true
```

## Variable and String Preferences

### Variable Declaration
```yaml
# Declare variables explicitly
explicit_declaration: true  # Use declare/local

# Local variables in functions
always_local: true

# Readonly for constants
readonly_constants: true
```

### String Manipulation
```yaml
# String manipulation method
string_manipulation: parameter_expansion

# Options:
# - parameter_expansion: ${var//old/new}
# - external_commands: sed, awk, etc.
# - mixed: Use appropriate method

# Prefer built-ins over external commands
prefer_builtins: true
```

### Array Usage
```yaml
# Use arrays
use_arrays: true

# Array declaration style
array_style: parentheses

# Options:
# - parentheses: arr=(item1 item2)
# - explicit: declare -a arr; arr[0]=item1

# Associative arrays (bash 4+)
use_associative_arrays: true
```

## Documentation Preferences

### Script Header
```yaml
# Include detailed header
detailed_header: true

# Header sections
header_sections:
  - script_name
  - description
  - author
  - date
  - version
  - usage
  - examples
  - dependencies
  - exit_codes
```

### Function Documentation
```yaml
# Document functions
document_functions: true

# Function documentation style
function_docs_style: multi_line

# Options:
# - multi_line: Multi-line comment block
# - inline: Single line above function
# - minimal: No documentation

# Documentation format
docs_format: structured

# Include:
# - Description
# - Globals used
# - Arguments
# - Returns/Outputs
# - Examples
```

### Inline Comments
```yaml
# Inline comment style
comment_style: descriptive

# Options:
# - descriptive: Explain why, not what
# - minimal: Only for complex logic
# - verbose: Comment everything
```

## Logging and Output Preferences

### Logging
```yaml
# Use logging function
use_logging_function: true

# Log levels
log_levels:
  - DEBUG
  - INFO
  - WARNING
  - ERROR

# Log to file
log_to_file: true

# Log file location
log_file: /var/log/script.log  # or ./script.log
```

### Output Formatting
```yaml
# Colorized output
colorized_output: true

# Use echo vs printf
output_command: printf

# Options:
# - printf: printf (more portable, safer)
# - echo: echo (simpler)

# Progress indicators
show_progress: true
```

## Portability Preferences

### External Command Usage
```yaml
# Allowed external commands
allowed_external_commands:
  - grep
  - sed
  - awk
  - find
  - xargs

# Avoid GNU-specific options
avoid_gnu_specific: false

# Options:
# - true: Stick to POSIX options
# - false: Allow GNU extensions
```

### System Compatibility
```yaml
# Target operating systems
target_os:
  - linux
  - macos
  # - bsd
  # - windows_wsl

# Check OS before running
check_os: true

# Check required commands
check_dependencies: true
```

## Security Preferences

### Input Validation
```yaml
# Validate all inputs
validate_inputs: true

# Sanitize file paths
sanitize_paths: true

# Check for dangerous characters
check_dangerous_chars: true
```

### Secure Coding
```yaml
# Use secure temp files
use_mktemp: true

# Secure file permissions
set_secure_permissions: true

# Avoid eval
avoid_eval: true

# Quote all variables
quote_all_variables: true
```

## Performance Preferences

### Optimization
```yaml
# Minimize subprocess calls
minimize_subprocesses: true

# Use built-in commands
prefer_bash_builtins: true

# Cache repeated operations
use_caching: true
```

### Parallel Execution
```yaml
# Parallel processing tool
parallel_tool: gnu_parallel

# Options:
# - gnu_parallel: GNU Parallel
# - xargs: xargs -P
# - background_jobs: Background jobs with wait
# - none: Sequential execution

# Maximum parallel jobs
max_jobs: 4  # or "auto"
```

## Debugging Preferences

### Debug Mode
```yaml
# Enable debug mode
debug_mode: optional

# Options:
# - always: Always enabled
# - optional: Enable via flag/env var
# - never: No debug mode

# Debug output
debug_output: verbose

# Use set -x
use_set_x: true
```

### Tracing
```yaml
# PS4 for better tracing
custom_ps4: true

# Example: PS4='+(${BASH_SOURCE}:${LINENO}): ${FUNCNAME[0]:+${FUNCNAME[0]}(): }'

# Trap DEBUG
use_debug_trap: false
```

## CI/CD Preferences

### CI Platform
```yaml
# Preferred CI platform
ci_platform: github_actions

# Options:
# - github_actions: GitHub Actions
# - gitlab_ci: GitLab CI
# - jenkins: Jenkins
# - travis: Travis CI

# CI steps
ci_steps:
  - lint          # shellcheck
  - format_check  # shfmt
  - test          # bats/shunit2
```

### Version Control
```yaml
# Git hooks
use_git_hooks: true

# Pre-commit checks
pre_commit_checks:
  - shellcheck
  - shfmt
  - test
```

## Distribution Preferences

### Packaging
```yaml
# Script distribution method
distribution_method: single_file

# Options:
# - single_file: Single executable script
# - directory: Directory with multiple files
# - package: System package (deb/rpm)
# - container: Docker container

# Include dependencies
bundle_dependencies: false
```

### Installation
```yaml
# Installation method
installation_method: make

# Options:
# - make: Makefile
# - install_script: install.sh
# - package_manager: apt/yum/homebrew
# - manual: Manual instructions

# Install location
install_prefix: /usr/local  # or ~/.local
```

## Additional Preferences

### Signal Handling
```yaml
# Handle signals
handle_signals: true

# Signals to trap
trap_signals:
  - EXIT
  - INT
  - TERM
  - HUP

# Cleanup on signal
cleanup_on_signal: true
```

### Argument Parsing
```yaml
# Argument parsing method
arg_parsing: getopts

# Options:
# - getopts: Built-in getopts
# - getopt: External getopt (GNU)
# - manual: Manual parsing
# - library: Use a library (e.g., bashly)

# Support long options
long_options: true
```

### Environment Variables
```yaml
# Environment variable prefix
env_var_prefix: APP_

# Use .env files
use_env_files: true

# Validate environment
validate_environment: true
```
