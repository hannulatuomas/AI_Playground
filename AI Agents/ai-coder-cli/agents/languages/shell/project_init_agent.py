

"""
Bash/Shell Script Project Initialization Agent

This agent handles Bash, Zsh, and Shell script project initialization.
"""

from typing import Dict, Any, List, Optional
from ...base import ProjectInitBase


class ShellProjectInitAgent(ProjectInitBase):
    """
    Bash/Shell script project initialization agent.
    
    Capabilities:
    - Initialize shell script projects
    - Create proper directory structure for scripts
    - Generate configuration and utility scripts
    - Support for different shell types (bash, zsh, sh)
    """
    
    def __init__(
        self,
        name: str = "project_init_bash",
        description: str = "Bash/Shell script project initialization",
        llm_router: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[Any] = None
    ):
        super().__init__(
            name=name,
            description=description,
            language="Bash",
            llm_router=llm_router,
            tool_registry=tool_registry,
            config=config,
            memory_manager=memory_manager
        )
    
    def _get_project_types(self) -> List[str]:
        """Get supported Bash project types."""
        return [
            'cli_tool',      # CLI utility
            'automation',    # Automation scripts
            'installer',     # Installation script
            'library',       # Shell library/functions
            'deployment',    # Deployment scripts
        ]
    
    def _get_project_structure(self, project_type: str) -> Dict[str, Any]:
        """Get directory structure for project type."""
        return {
            'directories': [
                'bin',
                'lib',
                'tests',
                'docs',
                'examples',
            ],
        }
    
    def _get_default_files(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate default Bash configuration files."""
        files = {}
        project_name = config['project_name'].lower().replace(' ', '-')
        shell_type = config.get('shell_type', 'bash')
        
        # README.md
        files['README.md'] = f"""# {config['project_name']}

{config.get('description', 'A Bash script project')}

## Installation

```bash
chmod +x install.sh
./install.sh
```

## Usage

```bash
./{project_name}
```

## Author

{config.get('author', 'N/A')}

## License

{config.get('license', 'MIT')}
"""
        
        # Main script
        files[f'bin/{project_name}'] = f"""#!/usr/bin/env {shell_type}

#
# {config['project_name']} - {config.get('description', 'A Bash script')}
#
# Author: {config.get('author', 'Author')}
# License: {config.get('license', 'MIT')}
#

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load library functions
# shellcheck source=../lib/common.sh
source "$PROJECT_ROOT/lib/common.sh"

# Configuration
readonly VERSION="0.1.0"
readonly PROGRAM_NAME="$(basename "$0")"

# Functions
show_help() {{
    cat << EOF
Usage: $PROGRAM_NAME [OPTIONS]

{config.get('description', 'A Bash script')}

OPTIONS:
    -h, --help      Show this help message
    -v, --version   Show version
    -d, --debug     Enable debug mode

EXAMPLES:
    $PROGRAM_NAME
    $PROGRAM_NAME --debug

EOF
}}

show_version() {{
    echo "$PROGRAM_NAME $VERSION"
}}

main() {{
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                show_version
                exit 0
                ;;
            -d|--debug)
                set -x
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Main logic here
    log_info "Starting {config['project_name']}..."
    
    # Your code here
    
    log_success "Completed successfully!"
}}

# Run main function
main "$@"
"""
        
        # Library functions
        files['lib/common.sh'] = f"""#!/usr/bin/env {shell_type}

#
# Common library functions for {config['project_name']}
#

# Colors for output
readonly RED='\\033[0;31m'
readonly GREEN='\\033[0;32m'
readonly YELLOW='\\033[1;33m'
readonly BLUE='\\033[0;34m'
readonly NC='\\033[0m' # No Color

# Logging functions
log_info() {{
    echo -e "${{BLUE}}[INFO]${{NC}} $*"
}}

log_success() {{
    echo -e "${{GREEN}}[SUCCESS]${{NC}} $*"
}}

log_warn() {{
    echo -e "${{YELLOW}}[WARNING]${{NC}} $*" >&2
}}

log_error() {{
    echo -e "${{RED}}[ERROR]${{NC}} $*" >&2
}}

# Check if command exists
command_exists() {{
    command -v "$1" >/dev/null 2>&1
}}

# Check if running as root
is_root() {{
    [[ $EUID -eq 0 ]]
}}

# Confirm action
confirm() {{
    local prompt="$1"
    local response
    
    read -r -p "${{prompt}} [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY])
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}}
"""
        
        # Install script
        files['install.sh'] = f"""#!/usr/bin/env {shell_type}

#
# Installation script for {config['project_name']}
#

set -euo pipefail

readonly INSTALL_DIR="/usr/local/bin"
readonly PROGRAM_NAME="{project_name}"

echo "Installing {config['project_name']}..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (use sudo)"
    exit 1
fi

# Copy main script
cp "bin/$PROGRAM_NAME" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/$PROGRAM_NAME"

echo "Installation complete!"
echo "Run: $PROGRAM_NAME --help"
"""
        
        # .gitignore
        files['.gitignore'] = """# Logs
*.log

# OS
.DS_Store
Thumbs.db

# Editor
*~
*.swp
*.swo
.vscode/
.idea/

# Temporary
tmp/
*.tmp
"""
        
        # Makefile
        files['Makefile'] = f"""# Makefile for {config['project_name']}

.PHONY: install uninstall test lint clean

install:
\tchmod +x install.sh
\tsudo ./install.sh

uninstall:
\tsudo rm -f /usr/local/bin/{project_name}

test:
\t@echo "Running tests..."
\t@shellcheck bin/* lib/*.sh

lint:
\t@echo "Linting scripts..."
\t@shellcheck bin/* lib/*.sh

clean:
\t@echo "Cleaning temporary files..."
\t@rm -rf tmp/
"""
        
        return files
    
    def _generate_language_rules(self, config: Dict[str, Any]) -> str:
        """Generate Bash-specific rules."""
        return f"""## Bash/Shell Script Rules

### Shell Type

- **Default Shell**: {config.get('shell_type', 'bash')}
- **Shebang**: Use `#!/usr/bin/env bash` for portability

### Code Style

1. **Naming**:
   - lowercase_with_underscores for variables and functions
   - UPPERCASE for constants and environment variables
   - Prefix readonly variables with `readonly`

2. **Formatting**:
   - 2-space indentation
   - Use `[[` instead of `[` for conditionals
   - Quote all variables: `"$var"`

3. **Best Practices**:
   - Use `set -euo pipefail` for error handling
   - Use shellcheck for linting
   - Add comments for complex logic
   - Use functions to organize code

### Error Handling

1. **Exit Codes**: Use meaningful exit codes
2. **Error Messages**: Write errors to stderr
3. **Cleanup**: Use trap for cleanup on exit
4. **Validation**: Check prerequisites and inputs

### Project Type: {config['project_type']}

### Functions

1. **Organization**: Group related functions
2. **Naming**: Clear, descriptive names
3. **Documentation**: Comment function purpose
4. **Return Values**: Use return codes consistently

### Arguments

1. **Parsing**: Use getopts or case statements
2. **Validation**: Validate all inputs
3. **Help**: Provide --help option
4. **Examples**: Include usage examples

### Dependencies

1. **Check Commands**: Check if required commands exist
2. **Portability**: Test on multiple shells if needed
3. **External Tools**: Document required tools

### Testing

1. **Tool**: Use BATS (Bash Automated Testing System)
2. **Linting**: Use shellcheck
3. **Coverage**: Test all code paths

### Security

1. **Input Sanitization**: Sanitize all user inputs
2. **Temporary Files**: Use mktemp for temp files
3. **Permissions**: Check and set proper permissions
4. **Sudo**: Minimize sudo usage

### Documentation

1. **Comments**: Add comments for complex logic
2. **Help Text**: Comprehensive --help output
3. **Examples**: Include usage examples
4. **README**: Document installation and usage
"""
    
    def _get_language_specific_questions(self) -> List[Dict[str, Any]]:
        """Get Bash-specific questions."""
        return [
            {
                'key': 'shell_type',
                'question': 'Shell type?',
                'type': 'choice',
                'options': ['bash', 'zsh', 'sh'],
                'default': 'bash',
                'required': False
            },
        ]


