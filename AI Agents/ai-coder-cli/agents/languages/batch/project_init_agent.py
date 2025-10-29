

"""
Batch/Windows CMD Project Initialization Agent

This agent handles Windows Batch script project initialization.
"""

from typing import Dict, Any, List, Optional
from ...base import ProjectInitBase


class BatchProjectInitAgent(ProjectInitBase):
    """
    Batch/Windows CMD script project initialization agent.
    
    Capabilities:
    - Initialize batch script projects
    - Create proper directory structure
    - Generate Windows-specific scripts
    """
    
    def __init__(
        self,
        name: str = "project_init_batch",
        description: str = "Batch/Windows CMD project initialization",
        llm_router: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[Any] = None
    ):
        super().__init__(
            name=name,
            description=description,
            language="Batch",
            llm_router=llm_router,
            tool_registry=tool_registry,
            config=config,
            memory_manager=memory_manager
        )
    
    def _get_project_types(self) -> List[str]:
        """Get supported Batch project types."""
        return [
            'automation',   # Automation scripts
            'installer',    # Installation script
            'tool',         # CLI tool
            'deployment',   # Deployment scripts
        ]
    
    def _get_project_structure(self, project_type: str) -> Dict[str, Any]:
        """Get directory structure for project type."""
        return {
            'directories': [
                'scripts',
                'lib',
                'logs',
                'docs',
            ],
        }
    
    def _get_default_files(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate default Batch configuration files."""
        files = {}
        project_name = config['project_name'].replace(' ', '_')
        
        # README.md
        files['README.md'] = f"""# {config['project_name']}

{config.get('description', 'A Batch script project')}

## Usage

```cmd
{project_name}.bat
```

## Author

{config.get('author', 'N/A')}

## License

{config.get('license', 'MIT')}
"""
        
        # Main batch script
        files[f'{project_name}.bat'] = f"""@echo off
REM {config['project_name']} - {config.get('description', 'A Batch script')}
REM Author: {config.get('author', 'Author')}
REM Version: 0.1.0

setlocal enabledelayedexpansion

REM Script directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%

REM Load library functions
call "%PROJECT_ROOT%lib\\common.bat"

REM Configuration
set VERSION=0.1.0
set PROGRAM_NAME=%~n0

REM Parse arguments
:parse_args
if "%1"=="" goto main
if /i "%1"=="-h" goto show_help
if /i "%1"=="--help" goto show_help
if /i "%1"=="-v" goto show_version
if /i "%1"=="--version" goto show_version
shift
goto parse_args

:show_help
echo Usage: %PROGRAM_NAME% [OPTIONS]
echo.
echo {config.get('description', 'A Batch script')}
echo.
echo OPTIONS:
echo   -h, --help      Show this help message
echo   -v, --version   Show version
echo.
goto end

:show_version
echo %PROGRAM_NAME% %VERSION%
goto end

:main
REM Main logic here
call :log_info "Starting {config['project_name']}..."

REM Your code here

call :log_success "Completed successfully!"
goto end

:end
endlocal
exit /b 0
"""
        
        # Library functions
        files['lib/common.bat'] = f"""@echo off
REM Common library functions for {config['project_name']}

REM Logging functions
:log_info
echo [INFO] %~1
exit /b 0

:log_success
echo [SUCCESS] %~1
exit /b 0

:log_warn
echo [WARNING] %~1 1>&2
exit /b 0

:log_error
echo [ERROR] %~1 1>&2
exit /b 0

REM Check if command exists
:command_exists
where %1 >nul 2>&1
exit /b %errorlevel%

REM Check if running as administrator
:is_admin
net session >nul 2>&1
exit /b %errorlevel%

REM Confirm action
:confirm
set /p response="%~1 [y/N] "
if /i "%response%"=="y" exit /b 0
if /i "%response%"=="yes" exit /b 0
exit /b 1
"""
        
        # Install script
        files['install.bat'] = f"""@echo off
REM Installation script for {config['project_name']}

echo Installing {config['project_name']}...

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script must be run as administrator
    exit /b 1
)

REM Copy main script to Program Files
set INSTALL_DIR=%ProgramFiles%\\{project_name}
mkdir "%INSTALL_DIR%" 2>nul
copy "{project_name}.bat" "%INSTALL_DIR%\\" >nul

REM Add to PATH (optional)
REM setx PATH "%PATH%;%INSTALL_DIR%" /M

echo Installation complete!
echo Run: {project_name}.bat --help

exit /b 0
"""
        
        # .gitignore
        files['.gitignore'] = """# Logs
*.log
logs/

# Temporary
*.tmp
temp/

# Editor
*~
.vscode/
.idea/

# OS
Thumbs.db
desktop.ini
"""
        
        return files
    
    def _generate_language_rules(self, config: Dict[str, Any]) -> str:
        """Generate Batch-specific rules."""
        return f"""## Batch/Windows CMD Rules

### Script Structure

1. **Header**:
   - Start with @echo off
   - Add comments with script info
   - Use setlocal for scope control

2. **Error Handling**:
   - Check %errorlevel% after commands
   - Use error codes consistently
   - Provide meaningful error messages

3. **Functions**:
   - Use :label for functions
   - Call with 'call :function_name'
   - Use exit /b for returns

### Code Style

1. **Naming**:
   - UPPERCASE for variables
   - lowercase_with_underscores for labels
   - Clear, descriptive names

2. **Formatting**:
   - Indent nested blocks
   - Add blank lines for readability
   - Comment complex logic

3. **Comments**:
   - Use REM for comments
   - Add header comments
   - Document parameters

### Project Type: {config['project_type']}

### Best Practices

1. **Variables**:
   - Use %VAR% for expansion
   - Use !VAR! for delayed expansion
   - Set variables locally with setlocal

2. **Arguments**:
   - Use %1, %2, etc. for arguments
   - Parse with if statements or loops
   - Provide --help option

3. **Paths**:
   - Use %~dp0 for script directory
   - Quote paths with spaces
   - Use full paths when possible

### Error Handling

1. **Check Errors**: Always check %errorlevel%
2. **Exit Codes**: Use meaningful exit codes
3. **Error Messages**: Write to stderr (1>&2)
4. **Cleanup**: Clean up on errors

### Functions

1. **Organization**: Group related functions
2. **Labels**: Use descriptive label names
3. **Parameters**: Document parameters
4. **Return Values**: Use exit /b with code

### Testing

1. **Manual Testing**: Test on different Windows versions
2. **Edge Cases**: Test error conditions
3. **Permissions**: Test with different permission levels

### Security

1. **Input Validation**: Validate all inputs
2. **Paths**: Be careful with path injection
3. **Permissions**: Check administrator rights
4. **Temporary Files**: Clean up temp files

### Documentation

1. **Help Text**: Provide --help option
2. **Comments**: Comment complex logic
3. **README**: Document usage and installation
4. **Examples**: Include usage examples

### Compatibility

1. **Windows Versions**: Test on multiple versions
2. **Commands**: Check command availability
3. **Environment**: Document requirements
4. **Dependencies**: List external dependencies
"""
    
    def _get_language_specific_questions(self) -> List[Dict[str, Any]]:
        """Get Batch-specific questions."""
        return []


