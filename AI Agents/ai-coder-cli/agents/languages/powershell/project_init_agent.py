

"""
PowerShell Project Initialization Agent

This agent handles PowerShell script and module project initialization.
"""

from typing import Dict, Any, List, Optional
from ...base import ProjectInitBase


class PowerShellProjectInitAgent(ProjectInitBase):
    """
    PowerShell project initialization agent.
    
    Capabilities:
    - Initialize PowerShell projects
    - Create PowerShell modules
    - Generate manifest files
    - Support for different project types
    """
    
    def __init__(
        self,
        name: str = "project_init_powershell",
        description: str = "PowerShell project initialization",
        llm_router: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[Any] = None
    ):
        super().__init__(
            name=name,
            description=description,
            language="PowerShell",
            llm_router=llm_router,
            tool_registry=tool_registry,
            config=config,
            memory_manager=memory_manager
        )
    
    def _get_project_types(self) -> List[str]:
        """Get supported PowerShell project types."""
        return [
            'module',        # PowerShell module
            'script',        # Standalone script
            'automation',    # Automation scripts
            'tool',          # PowerShell tool/cmdlet
        ]
    
    def _get_project_structure(self, project_type: str) -> Dict[str, Any]:
        """Get directory structure for project type."""
        if project_type == 'module':
            return {
                'directories': [
                    'Public',
                    'Private',
                    'Tests',
                    'Docs',
                ],
            }
        else:
            return {
                'directories': [
                    'Scripts',
                    'Tests',
                    'Docs',
                ],
            }
    
    def _get_default_files(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate default PowerShell configuration files."""
        files = {}
        project_name = config['project_name'].replace('-', '').replace(' ', '')
        project_type = config['project_type']
        
        # README.md
        files['README.md'] = f"""# {config['project_name']}

{config.get('description', 'A PowerShell project')}

## Installation

```powershell
# Import module
Import-Module .\\{project_name}.psd1
```

## Usage

```powershell
# Example usage
Get-Help {project_name}
```

## Author

{config.get('author', 'N/A')}

## License

{config.get('license', 'MIT')}
"""
        
        if project_type == 'module':
            # Module manifest
            files[f'{project_name}.psd1'] = f"""@{{
    # Module Manifest
    ModuleVersion = '0.1.0'
    GUID = 'GENERATE-NEW-GUID'
    Author = '{config.get('author', 'Author')}'
    Description = '{config.get('description', 'A PowerShell module')}'
    PowerShellVersion = '5.1'
    
    # Files
    RootModule = '{project_name}.psm1'
    
    # Exported functions
    FunctionsToExport = @('*')
    
    # Exported cmdlets
    CmdletsToExport = @()
    
    # Exported variables
    VariablesToExport = @()
    
    # Exported aliases
    AliasesToExport = @()
}}
"""
            
            # Module file
            files[f'{project_name}.psm1'] = f"""#
# {config['project_name']} Module
# {config.get('description', 'A PowerShell module')}
#

# Import public functions
$Public = @( Get-ChildItem -Path $PSScriptRoot\\Public\\*.ps1 -ErrorAction SilentlyContinue )

# Import private functions
$Private = @( Get-ChildItem -Path $PSScriptRoot\\Private\\*.ps1 -ErrorAction SilentlyContinue )

# Dot source all functions
foreach ($import in @($Public + $Private)) {{
    try {{
        . $import.FullName
    }}
    catch {{
        Write-Error -Message "Failed to import function $($import.FullName): $_"
    }}
}}

# Export public functions
Export-ModuleMember -Function $Public.BaseName
"""
            
            # Example public function
            files[f'Public/Get-{project_name}Info.ps1'] = f"""function Get-{project_name}Info {{
    <#
    .SYNOPSIS
        Gets information about {config['project_name']}
    
    .DESCRIPTION
        Returns version and basic information about the {config['project_name']} module.
    
    .EXAMPLE
        Get-{project_name}Info
        
        Returns module information.
    
    .OUTPUTS
        PSCustomObject
    #>
    [CmdletBinding()]
    param()
    
    $info = @{{
        Name = '{config['project_name']}'
        Version = '0.1.0'
        Author = '{config.get('author', 'Author')}'
    }}
    
    return [PSCustomObject]$info
}}
"""
        else:
            # Standalone script
            files[f'Scripts/{project_name}.ps1'] = f"""<#
.SYNOPSIS
    {config.get('description', 'A PowerShell script')}

.DESCRIPTION
    {config.get('description', 'A PowerShell script')}

.PARAMETER Name
    Example parameter

.EXAMPLE
    .\\{project_name}.ps1 -Name "Example"

.NOTES
    Author: {config.get('author', 'Author')}
    Version: 0.1.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$Name = "World"
)

# Main script logic
Write-Host "Hello, $Name!"
"""
        
        # .gitignore
        files['.gitignore'] = """# PowerShell
*.ps1xml
*.ps1x
*.psc1

# Test results
TestResults/
*.trx

# Coverage
coverage/

# Editor
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
"""
        
        # Pester tests
        files[f'Tests/{project_name}.Tests.ps1'] = f"""BeforeAll {{
    $ModulePath = Join-Path -Path $PSScriptRoot -ChildPath "..\\{project_name}.psd1"
    Import-Module $ModulePath -Force
}}

Describe '{project_name} Module Tests' {{
    
    Context 'Module Import' {{
        It 'Module should import successfully' {{
            $Module = Get-Module -Name '{project_name}'
            $Module | Should -Not -BeNullOrEmpty
        }}
    }}
    
    Context 'Exported Functions' {{
        It 'Should export expected functions' {{
            $Functions = (Get-Command -Module '{project_name}').Name
            $Functions | Should -Not -BeNullOrEmpty
        }}
    }}
}}
"""
        
        return files
    
    def _generate_language_rules(self, config: Dict[str, Any]) -> str:
        """Generate PowerShell-specific rules."""
        return f"""## PowerShell-Specific Rules

### PowerShell Version

- **Target Version**: PowerShell 5.1+
- **Core Support**: PowerShell 7+ recommended

### Code Style

1. **Naming**:
   - PascalCase for functions (Verb-Noun format)
   - PascalCase for parameters
   - camelCase for variables
   - UPPERCASE for constants

2. **Formatting**:
   - 4-space indentation
   - Open braces on same line
   - Use approved verbs (Get, Set, New, Remove, etc.)

3. **Comment-Based Help**:
   - Add .SYNOPSIS, .DESCRIPTION, .EXAMPLE
   - Document all parameters
   - Include .NOTES with author and version

### Project Type: {config['project_type']}

### Best Practices

1. **Parameters**:
   - Use [CmdletBinding()]
   - Define parameter types
   - Add validation attributes
   - Use parameter sets when needed

2. **Error Handling**:
   - Use try/catch blocks
   - Set $ErrorActionPreference appropriately
   - Write meaningful error messages

3. **Output**:
   - Use Write-Output for pipeline output
   - Use Write-Host for informational messages
   - Use Write-Verbose for debug info
   - Return objects, not strings

### Functions

1. **Verb-Noun**: Follow PowerShell verb-noun convention
2. **Single Responsibility**: One function, one purpose
3. **Pipeline Support**: Support pipeline input where appropriate
4. **Return Types**: Return consistent object types

### Module Development

1. **Manifest**: Always create a .psd1 manifest
2. **Organization**: Separate public and private functions
3. **Export**: Explicitly export public functions
4. **Versioning**: Use semantic versioning

### Testing

1. **Framework**: Use Pester for testing
2. **Coverage**: Test all public functions
3. **Mocking**: Use Pester mocking for external dependencies
4. **Structure**: Mirror module structure in tests

### Documentation

1. **Comment-Based Help**: Required for all public functions
2. **Examples**: Provide realistic examples
3. **About Topics**: Create about_ModuleName.help.txt
4. **README**: Document installation and usage

### Security

1. **Execution Policy**: Document required execution policy
2. **Credentials**: Use PSCredential objects
3. **Secrets**: Never hardcode secrets
4. **Validation**: Validate all inputs

### Performance

1. **Pipeline**: Use pipeline for large datasets
2. **Filtering**: Filter left, format right
3. **Object Creation**: Use [PSCustomObject] for efficiency
4. **Loops**: Prefer pipeline over foreach loops
"""
    
    def _get_language_specific_questions(self) -> List[Dict[str, Any]]:
        """Get PowerShell-specific questions."""
        return [
            {
                'key': 'ps_version',
                'question': 'Target PowerShell version?',
                'type': 'choice',
                'options': ['5.1', '7.0', '7.2', '7.4'],
                'default': '5.1',
                'required': False
            },
        ]


