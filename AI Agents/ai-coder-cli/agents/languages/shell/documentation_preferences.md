
# Bash/Shell Script Documentation Preferences

This document defines documentation standards for Bash, Zsh, and shell script projects.
These preferences guide AI agents in maintaining consistent documentation.

---

## General Documentation Philosophy

**Core Principles:**
1. **Clarity and Simplicity** - Scripts should be self-documenting
2. **Function Documentation** - Clear function headers
3. **Usage Examples** - Show how to use the script
4. **Error Handling** - Document exit codes and error conditions
5. **Portability** - Note shell compatibility requirements

---

## Script Documentation Standards

### Script Header

Every script should start with a comprehensive header:

```bash
#!/usr/bin/env bash
#
# Script Name: script_name.sh
# Description: Brief one-line description of what the script does
#
# Usage: script_name.sh [OPTIONS] ARGS
#
# Options:
#   -h, --help       Show this help message
#   -v, --verbose    Enable verbose output
#   -d, --debug      Enable debug mode
#
# Arguments:
#   ARG1            Description of first argument
#   ARG2            Description of second argument
#
# Examples:
#   script_name.sh -v arg1 arg2
#   script_name.sh --debug arg1
#
# Dependencies:
#   - bash 4.0+
#   - jq (for JSON processing)
#   - curl (for HTTP requests)
#
# Exit Codes:
#   0  Success
#   1  General error
#   2  Invalid arguments
#   3  Missing dependency
#
# Author: Name
# Created: YYYY-MM-DD
# Modified: YYYY-MM-DD
# Version: 1.0.0
#
# shellcheck disable=SC2034  # Explanation of disabled check if needed
#

set -euo pipefail  # Exit on error, undefined variable, pipe failure
```

### Function Documentation

```bash
#######################################
# Brief description of function purpose
#
# Detailed description if needed. Explain what the function does,
# not how it does it.
#
# Globals:
#   GLOBAL_VAR - Description of global variable read
#   ANOTHER_VAR - Description of global variable written
#
# Arguments:
#   $1 - Description of first argument
#   $2 - Description of second argument (optional)
#
# Outputs:
#   Writes success/error messages to stdout/stderr
#
# Returns:
#   0 on success, non-zero on error
#
# Examples:
#   function_name "arg1" "arg2"
#   result=$(function_name "arg1")
#######################################
function_name() {
    local arg1="$1"
    local arg2="${2:-default}"  # Second arg with default
    
    # Function implementation
}
```

### Inline Comments

```bash
# Comment explaining the following block of code
command1

# Multi-line comment explaining
# a more complex operation
# that requires several lines
command2

# TODO: Future enhancement needed
# FIXME: Known issue, needs fixing
# NOTE: Important information
# HACK: Temporary workaround

# Explain non-obvious regex or complex logic
if [[ "$var" =~ ^[0-9]+$ ]]; then  # Check if var is numeric
    echo "Numeric"
fi
```

---

## Project Documentation Structure

### Required Files

1. **README.md** - Project overview and usage
2. **INSTALL.md** - Installation instructions
3. **CONTRIBUTING.md** - Contribution guidelines
4. **CHANGELOG.md** - Version history
5. **examples/** - Usage examples
6. **docs/** - Additional documentation

### README.md Structure

```markdown
# Project Name

Brief description of the shell script project.

![Shell](https://img.shields.io/badge/shell-bash-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- Feature 1
- Feature 2
- Feature 3

## Requirements

- Bash 4.0 or later (or Zsh 5.0+)
- Dependencies:
  - `jq` - JSON processor
  - `curl` - HTTP client
  - `awk` - Text processing

## Installation

### Quick Install

```bash
# Download and install
curl -fsSL https://raw.githubusercontent.com/user/repo/main/install.sh | bash
```

### Manual Install

```bash
# Clone repository
git clone https://github.com/user/repo.git
cd repo

# Make scripts executable
chmod +x *.sh

# Optional: Add to PATH
sudo ln -s $(pwd)/script.sh /usr/local/bin/script
```

## Usage

### Basic Usage

```bash
./script.sh [OPTIONS] ARGS
```

### Options

- `-h, --help` - Show help message
- `-v, --verbose` - Enable verbose output
- `-d, --debug` - Enable debug mode
- `-c, --config FILE` - Use custom config file

### Examples

#### Example 1: Basic Usage

```bash
./script.sh input.txt
```

#### Example 2: With Options

```bash
./script.sh -v --config custom.conf input.txt
```

#### Example 3: Piped Input

```bash
cat input.txt | ./script.sh -
```

## Configuration

### Configuration File

Create `~/.config/script/config.conf`:

```bash
# Configuration options
OPTION1="value1"
OPTION2="value2"
```

### Environment Variables

- `SCRIPT_DEBUG` - Enable debug mode (set to 1)
- `SCRIPT_CONFIG` - Path to config file

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - Missing dependency
- `4` - File not found
- `5` - Permission denied

## Troubleshooting

### Common Issues

#### Issue 1

**Problem:** Description of problem

**Solution:**
```bash
# Solution command
```

#### Issue 2

**Problem:** Description

**Solution:**
```bash
# Solution
```

## Development

### Testing

```bash
# Run tests
./tests/run_tests.sh

# Run specific test
./tests/test_feature.sh
```

### Linting

```bash
# Install shellcheck
# On macOS: brew install shellcheck
# On Ubuntu: apt-get install shellcheck

# Run shellcheck
shellcheck *.sh
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE)

## Changelog

See [CHANGELOG.md](CHANGELOG.md)
```

### Function Library Documentation

```bash
#!/usr/bin/env bash
#
# Library: lib_name.sh
# Description: Collection of utility functions for [purpose]
#
# Usage:
#   source lib_name.sh
#   function_name args
#
# Functions:
#   function1    - Brief description
#   function2    - Brief description
#   function3    - Brief description
#

#######################################
# Library initialization
#######################################
_lib_init() {
    # Initialization code
    readonly LIB_VERSION="1.0.0"
}

#######################################
# Function 1 description
#######################################
function1() {
    # Implementation
}

#######################################
# Function 2 description
#######################################
function2() {
    # Implementation
}

# Initialize library
_lib_init
```

---

## Help Function

Every script should include a help function:

```bash
#######################################
# Display help message
#
# Outputs:
#   Writes help text to stdout
#######################################
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS] ARGS

Description of what the script does.

Options:
    -h, --help          Show this help message
    -v, --verbose       Enable verbose output
    -d, --debug         Enable debug mode
    -c, --config FILE   Use custom config file

Arguments:
    ARG1                Description of first argument
    ARG2                Description of second argument (optional)

Examples:
    $(basename "$0") -v arg1 arg2
    $(basename "$0") --config custom.conf arg1

Exit Codes:
    0   Success
    1   General error
    2   Invalid arguments

For more information, see the README.md file.
EOF
}
```

---

## Best Practices

### Variables

```bash
# Use descriptive names
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly CONFIG_FILE="/etc/script/config.conf"

# Document globals at the top
declare -g GLOBAL_VAR=""  # Description of global variable

# Use local variables in functions
function example() {
    local input="$1"
    local output=""
    # ...
}

# Use uppercase for constants
readonly MAX_RETRIES=3
readonly DEFAULT_TIMEOUT=30

# Use lowercase for local variables
local file_name="example.txt"
local counter=0
```

### Error Handling

```bash
#######################################
# Error handler function
#
# Arguments:
#   $1 - Error message
#   $2 - Exit code (default: 1)
#######################################
error_exit() {
    local message="$1"
    local code="${2:-1}"
    
    echo "Error: $message" >&2
    exit "$code"
}

# Usage
[[ -f "$file" ]] || error_exit "File not found: $file" 2

# Trap errors
trap 'error_exit "Script failed at line $LINENO"' ERR
```

### Logging

```bash
#######################################
# Logging functions
#######################################

# Log levels
readonly LOG_DEBUG=0
readonly LOG_INFO=1
readonly LOG_WARN=2
readonly LOG_ERROR=3

# Current log level
LOG_LEVEL=${LOG_LEVEL:-$LOG_INFO}

log_debug() {
    [[ $LOG_LEVEL -le $LOG_DEBUG ]] && echo "[DEBUG] $*" >&2
}

log_info() {
    [[ $LOG_LEVEL -le $LOG_INFO ]] && echo "[INFO] $*"
}

log_warn() {
    [[ $LOG_LEVEL -le $LOG_WARN ]] && echo "[WARN] $*" >&2
}

log_error() {
    [[ $LOG_LEVEL -le $LOG_ERROR ]] && echo "[ERROR] $*" >&2
}
```

---

## Testing Documentation

### Test Script Structure

```bash
#!/usr/bin/env bash
#
# Test Suite: test_feature.sh
# Description: Tests for [feature] functionality
#
# Usage: ./test_feature.sh
#

# Source the script to test
source ../script.sh

# Test counter
tests_run=0
tests_passed=0

#######################################
# Test helper function
#
# Arguments:
#   $1 - Test name
#   $2 - Expected result
#   $3 - Actual result
#######################################
assert_equals() {
    local test_name="$1"
    local expected="$2"
    local actual="$3"
    
    ((tests_run++))
    
    if [[ "$expected" == "$actual" ]]; then
        echo "✓ $test_name"
        ((tests_passed++))
    else
        echo "✗ $test_name"
        echo "  Expected: $expected"
        echo "  Actual:   $actual"
    fi
}

#######################################
# Run all tests
#######################################
run_tests() {
    echo "Running tests..."
    
    # Test 1
    result=$(function_name "arg")
    assert_equals "Test function_name" "expected" "$result"
    
    # Test 2
    # ...
    
    echo ""
    echo "Tests run: $tests_run"
    echo "Tests passed: $tests_passed"
    
    [[ $tests_run -eq $tests_passed ]] || exit 1
}

run_tests
```

---

## Man Page (Optional)

For distribution as system commands:

```
.TH SCRIPT_NAME 1 "October 2025" "Version 1.0" "User Commands"

.SH NAME
script_name \- brief description

.SH SYNOPSIS
.B script_name
[\fIOPTIONS\fR] \fIARGS\fR

.SH DESCRIPTION
Detailed description of what the script does.

.SH OPTIONS
.TP
.BR \-h ", " \-\-help
Show help message

.TP
.BR \-v ", " \-\-verbose
Enable verbose output

.SH EXAMPLES
.PP
Basic usage:
.RS
script_name arg1 arg2
.RE

.SH EXIT STATUS
.TP
.B 0
Success

.TP
.B 1
General error

.SH AUTHOR
Name <email@example.com>

.SH SEE ALSO
Related commands
```

---

## Documentation Maintenance

### Maintenance Checklist

- [ ] Script header is complete and current
- [ ] All functions have comment blocks
- [ ] Help function is up to date
- [ ] README.md reflects current usage
- [ ] Examples are tested and working
- [ ] Exit codes are documented
- [ ] Dependencies are listed
- [ ] CHANGELOG.md is updated
- [ ] Passes shellcheck with no warnings

---

## AI Agent Guidelines

**For AI Agents Maintaining Documentation:**

1. **Comprehensive Headers** - Every script needs full header
2. **Function Documentation** - Use standard comment block format
3. **Help Functions** - Keep usage help current
4. **Exit Codes** - Document all exit codes
5. **Dependencies** - List all external commands
6. **Examples** - Include working examples
7. **ShellCheck** - Ensure code passes shellcheck
8. **Portability** - Note Bash/Zsh requirements

**Priority Order:**
1. Script headers
2. Function documentation
3. Help function
4. README.md
5. Examples

---

**Last Updated:** 2025-10-12
**Version:** 1.0
