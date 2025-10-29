
# PowerShell Documentation Preferences

This document defines documentation standards for PowerShell scripts and modules.
These preferences guide AI agents in maintaining consistent documentation.

---

## General Documentation Philosophy

**Core Principles:**
1. **Comment-Based Help** - Use PowerShell's built-in help system
2. **Cmdlet Standards** - Follow approved verb-noun naming
3. **Parameter Documentation** - Document all parameters thoroughly
4. **Examples Required** - Include multiple working examples
5. **Pipeline Support** - Document pipeline input/output

---

## Code Documentation Standards

### Comment-Based Help

Every function should include comment-based help:

```powershell
<#
.SYNOPSIS
    Brief one-line description of the function.

.DESCRIPTION
    Detailed description of what the function does, its purpose,
    and any important behavioral notes.
    
    Can span multiple paragraphs to explain complex functionality.

.PARAMETER ParameterName
    Description of the parameter, including expected values,
    format, and any constraints.

.PARAMETER AnotherParameter
    Description of another parameter.

.INPUTS
    System.String
    You can pipe strings to this function.

.OUTPUTS
    System.Management.Automation.PSCustomObject
    Returns a custom object with properties X, Y, and Z.

.EXAMPLE
    Get-Something -Name "Test"
    
    Description of what this example does.

.EXAMPLE
    "Item1", "Item2" | Get-Something -Verbose
    
    Description of this example showing pipeline usage.

.EXAMPLE
    Get-Something -Name "Test" -Force
    
    Description of this example with multiple parameters.

.NOTES
    Author: Name
    Created: YYYY-MM-DD
    Modified: YYYY-MM-DD
    Version: 1.0.0
    
    Requires: PowerShell 5.1 or later
    Dependencies: Module1, Module2

.LINK
    https://docs.example.com/Get-Something
    
.LINK
    Related-Command
#>
function Get-Something {
    [CmdletBinding()]
    param(
        [Parameter(
            Mandatory = $true,
            ValueFromPipeline = $true,
            ValueFromPipelineByPropertyName = $true,
            Position = 0,
            HelpMessage = "Enter the name to process"
        )]
        [ValidateNotNullOrEmpty()]
        [string]$Name,
        
        [Parameter(Mandatory = $false)]
        [switch]$Force
    )
    
    begin {
        Write-Verbose "Starting $($MyInvocation.MyCommand)"
    }
    
    process {
        # Implementation
    }
    
    end {
        Write-Verbose "Completed $($MyInvocation.MyCommand)"
    }
}
```

### Script File Header

```powershell
<#
.SYNOPSIS
    Script name and brief description.

.DESCRIPTION
    Detailed description of what the script does.
    
    This script performs the following actions:
    1. Action 1
    2. Action 2
    3. Action 3

.PARAMETER Parameter1
    Description of first parameter.

.PARAMETER Parameter2
    Description of second parameter.

.EXAMPLE
    .\Script-Name.ps1 -Parameter1 "Value"
    
    Description of example.

.NOTES
    File Name      : Script-Name.ps1
    Author         : Name
    Prerequisite   : PowerShell 5.1, Module1, Module2
    Created        : YYYY-MM-DD
    Modified       : YYYY-MM-DD
    Version        : 1.0.0
    
    Copyright YYYY - Company Name

.LINK
    https://github.com/user/repo
#>

#Requires -Version 5.1
#Requires -Modules Module1, Module2

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Parameter1,
    
    [Parameter(Mandatory = $false)]
    [string]$Parameter2 = "Default"
)

# Script implementation
```

### Module Manifest Documentation

```powershell
@{
    # Script module or binary module file associated with this manifest
    RootModule = 'ModuleName.psm1'
    
    # Version number of this module
    ModuleVersion = '1.0.0'
    
    # ID used to uniquely identify this module
    GUID = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
    
    # Author of this module
    Author = 'Author Name'
    
    # Company or vendor of this module
    CompanyName = 'Company Name'
    
    # Copyright statement for this module
    Copyright = '(c) 2025 Author Name. All rights reserved.'
    
    # Description of the functionality provided by this module
    Description = 'Detailed description of what this module does.'
    
    # Minimum version of PowerShell needed
    PowerShellVersion = '5.1'
    
    # Functions to export from this module
    FunctionsToExport = @(
        'Get-Something',
        'Set-Something',
        'New-Something',
        'Remove-Something'
    )
    
    # Cmdlets to export from this module
    CmdletsToExport = @()
    
    # Variables to export from this module
    VariablesToExport = @()
    
    # Aliases to export from this module
    AliasesToExport = @()
    
    # Private data to pass to the module
    PrivateData = @{
        PSData = @{
            # Tags applied to this module
            Tags = @('Tag1', 'Tag2', 'Tag3')
            
            # A URL to the license for this module
            LicenseUri = 'https://github.com/user/repo/blob/main/LICENSE'
            
            # A URL to the main website for this project
            ProjectUri = 'https://github.com/user/repo'
            
            # ReleaseNotes of this module
            ReleaseNotes = 'See CHANGELOG.md'
        }
    }
}
```

### Inline Comments

```powershell
# Single-line comment explaining the next line

# Multi-line comment explaining
# a more complex block of code
# across several lines

<# Block comment for
   longer explanations that
   span multiple lines #>

# TODO: Future enhancement needed
# FIXME: Known issue that needs fixing
# HACK: Temporary workaround
# NOTE: Important information

# Validate input before processing
if ($Name -match '^\w+$') {
    # Name is valid
    Write-Verbose "Valid name: $Name"
}
```

---

## Project Documentation Structure

### Required Files

1. **README.md** - Project overview
2. **CHANGELOG.md** - Version history
3. **CONTRIBUTING.md** - Contribution guidelines
4. **LICENSE** - License information
5. **docs/**
   - **USAGE.md** - Detailed usage guide
   - **API.md** - Function reference
   - **EXAMPLES.md** - Extended examples

### README.md Structure

```markdown
# Module/Script Name

Brief description of the PowerShell module or script.

![PowerShell Gallery](https://img.shields.io/powershellgallery/v/ModuleName.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- Feature 1
- Feature 2
- Feature 3

## Requirements

- PowerShell 5.1 or later (PowerShell 7+ recommended)
- Required modules:
  - Module1
  - Module2
- Operating System: Windows, Linux, macOS

## Installation

### From PowerShell Gallery

```powershell
Install-Module -Name ModuleName -Scope CurrentUser
```

### Manual Installation

```powershell
# Clone repository
git clone https://github.com/user/repo.git
cd repo

# Import module
Import-Module .\ModuleName.psd1
```

## Quick Start

```powershell
# Import module
Import-Module ModuleName

# Basic usage
Get-Something -Name "Example"

# Pipeline usage
"Item1", "Item2" | Get-Something

# With parameters
Get-Something -Name "Example" -Verbose
```

## Commands

### Get-Something

Retrieves something based on name.

```powershell
Get-Something [-Name] <String> [-Force] [<CommonParameters>]
```

**Parameters:**

- `-Name` (String, Mandatory) - The name to search for
- `-Force` (Switch) - Force the operation

**Examples:**

```powershell
Get-Something -Name "Test"
"Name1", "Name2" | Get-Something
```

### Set-Something

Sets or updates something.

```powershell
Set-Something [-Name] <String> [-Value] <String> [<CommonParameters>]
```

## Configuration

### Configuration File

Create or modify `$HOME\.modulename\config.json`:

```json
{
  "DefaultOption": "value",
  "Timeout": 30
}
```

### Environment Variables

- `MODULE_DEBUG` - Enable debug output (set to 1)
- `MODULE_CONFIG` - Path to config file

## Common Scenarios

### Scenario 1: Basic Usage

```powershell
# Description
Get-Something -Name "Example"
```

### Scenario 2: Advanced Usage

```powershell
# Description
Get-Something -Name "Example" -Verbose | 
    Where-Object { $_.Property -eq "Value" } |
    Set-Something -Value "NewValue"
```

## Troubleshooting

### Issue: Error Message

**Cause:** Description of cause

**Solution:**
```powershell
# Solution command
```

### Issue: Another Error

**Cause:** Description

**Solution:**
```powershell
# Solution
```

## Development

### Building the Module

```powershell
# Run build script
.\build.ps1
```

### Running Tests

```powershell
# Install Pester if needed
Install-Module -Name Pester -Force

# Run tests
Invoke-Pester
```

### Code Style

This project follows:
- PowerShell Practice and Style Guide
- PSScriptAnalyzer rules
- Approved verbs (Get-Verb)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE)

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

## Support

- Issues: https://github.com/user/repo/issues
- Discussions: https://github.com/user/repo/discussions
```

---

## Function Documentation Best Practices

### Parameter Attributes

```powershell
[Parameter(
    Mandatory = $true,                           # Required parameter
    ValueFromPipeline = $true,                   # Accept pipeline input
    ValueFromPipelineByPropertyName = $true,     # Accept by property name
    Position = 0,                                 # Positional parameter
    ParameterSetName = "SetName",                # Parameter set
    HelpMessage = "Help text for parameter"      # Help message
)]
[ValidateNotNullOrEmpty()]                       # Validation attribute
[ValidateSet("Option1", "Option2", "Option3")]   # Valid values
[ValidateRange(1, 100)]                          # Range validation
[ValidatePattern('^\w+$')]                       # Regex validation
[ValidateScript({ Test-Path $_ })]               # Script validation
[Alias("Alias1", "Alias2")]                      # Parameter aliases
[string]$ParameterName
```

### Advanced Function Template

```powershell
<#
.SYNOPSIS
    Function synopsis.

.DESCRIPTION
    Detailed description.

.PARAMETER InputObject
    Description of InputObject parameter.

.PARAMETER Name
    Description of Name parameter.

.INPUTS
    System.Management.Automation.PSCustomObject
    
.OUTPUTS
    System.Management.Automation.PSCustomObject

.EXAMPLE
    Get-Advanced -Name "Test"

.NOTES
    Author: Name
    Version: 1.0.0
#>
function Get-Advanced {
    [CmdletBinding(
        DefaultParameterSetName = 'ByName',
        SupportsShouldProcess = $true,
        ConfirmImpact = 'Medium'
    )]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(
            Mandatory = $true,
            ValueFromPipeline = $true,
            ParameterSetName = 'ByObject'
        )]
        [PSCustomObject]$InputObject,
        
        [Parameter(
            Mandatory = $true,
            Position = 0,
            ParameterSetName = 'ByName'
        )]
        [ValidateNotNullOrEmpty()]
        [string]$Name
    )
    
    begin {
        Write-Verbose "[$($MyInvocation.MyCommand)] Starting"
        Write-Debug "Parameter Set: $($PSCmdlet.ParameterSetName)"
    }
    
    process {
        try {
            if ($PSCmdlet.ShouldProcess($Name, "Get-Advanced")) {
                # Implementation
                $result = [PSCustomObject]@{
                    Name = $Name
                    Value = "Result"
                }
                
                Write-Output $result
            }
        }
        catch {
            Write-Error "Failed to process: $_"
            throw
        }
    }
    
    end {
        Write-Verbose "[$($MyInvocation.MyCommand)] Completed"
    }
}
```

---

## Module Documentation

### Module README.md

```markdown
# ModuleName PowerShell Module

## Exported Functions

- `Get-Something` - Retrieve items
- `Set-Something` - Update items
- `New-Something` - Create new items
- `Remove-Something` - Delete items
- `Test-Something` - Validate items

## Function Reference

See [docs/FUNCTIONS.md](docs/FUNCTIONS.md) for detailed function documentation.

## Architecture

The module is organized as follows:

```
ModuleName/
├── ModuleName.psd1          # Module manifest
├── ModuleName.psm1          # Root module
├── Public/                  # Public functions
│   ├── Get-Something.ps1
│   ├── Set-Something.ps1
│   └── ...
├── Private/                 # Private helper functions
│   ├── Helper1.ps1
│   └── Helper2.ps1
├── Classes/                 # PowerShell classes
├── Tests/                   # Pester tests
│   ├── Public.Tests.ps1
│   └── Integration.Tests.ps1
└── docs/                    # Documentation
    ├── FUNCTIONS.md
    └── EXAMPLES.md
```
```

---

## Testing Documentation

### Pester Test Structure

```powershell
<#
.SYNOPSIS
    Pester tests for Get-Something function.

.DESCRIPTION
    Tests all functionality of Get-Something including:
    - Parameter validation
    - Pipeline input
    - Error handling
    - Output format
#>

BeforeAll {
    # Import module
    Import-Module "$PSScriptRoot\..\ModuleName.psd1" -Force
}

Describe "Get-Something" {
    Context "Parameter Validation" {
        It "Should require Name parameter" {
            { Get-Something } | Should -Throw
        }
        
        It "Should accept string Name" {
            { Get-Something -Name "Test" } | Should -Not -Throw
        }
    }
    
    Context "Functionality" {
        It "Should return expected object type" {
            $result = Get-Something -Name "Test"
            $result | Should -BeOfType [PSCustomObject]
        }
        
        It "Should have required properties" {
            $result = Get-Something -Name "Test"
            $result.PSObject.Properties.Name | Should -Contain "Name"
            $result.PSObject.Properties.Name | Should -Contain "Value"
        }
    }
    
    Context "Pipeline Input" {
        It "Should accept pipeline input" {
            { "Test" | Get-Something } | Should -Not -Throw
        }
        
        It "Should process multiple items" {
            $results = "Item1", "Item2" | Get-Something
            $results.Count | Should -Be 2
        }
    }
}
```

---

## Help Usage

### Accessing Help

```powershell
# Get help for a function
Get-Help Get-Something

# Get detailed help
Get-Help Get-Something -Detailed

# Get full help including technical details
Get-Help Get-Something -Full

# Get examples only
Get-Help Get-Something -Examples

# Get parameter help
Get-Help Get-Something -Parameter Name

# Online help (if .LINK provided)
Get-Help Get-Something -Online
```

---

## Documentation Maintenance

### Maintenance Checklist

- [ ] All functions have comment-based help
- [ ] All parameters documented with descriptions
- [ ] Multiple examples provided for each function
- [ ] .INPUTS and .OUTPUTS documented
- [ ] Module manifest up to date
- [ ] README.md current
- [ ] CHANGELOG.md updated
- [ ] Pester tests written and passing
- [ ] PSScriptAnalyzer passes with no warnings
- [ ] Help accessible via Get-Help

### Update Process

```powershell
# Update module version
Update-ModuleManifest -Path .\ModuleName.psd1 -ModuleVersion "1.1.0"

# Run PSScriptAnalyzer
Invoke-ScriptAnalyzer -Path .\ -Recurse

# Run tests
Invoke-Pester

# Generate external help (optional)
New-ExternalHelp -Path .\docs -OutputPath .\en-US
```

---

## AI Agent Guidelines

**For AI Agents Maintaining Documentation:**

1. **Comment-Based Help** - Use PowerShell's standard format
2. **Complete Parameter Documentation** - Document all attributes
3. **Multiple Examples** - Provide varied, working examples
4. **Pipeline Support** - Document pipeline input/output
5. **Error Handling** - Document exceptions and errors
6. **Approved Verbs** - Use Get-Verb approved verbs only
7. **Parameter Validation** - Use appropriate validation attributes
8. **Pester Tests** - Maintain test documentation

**Priority Order:**
1. Function comment-based help
2. Parameter documentation
3. Examples in help
4. README.md
5. Module manifest
6. CHANGELOG.md

---

**Last Updated:** 2025-10-12
**Version:** 1.0
