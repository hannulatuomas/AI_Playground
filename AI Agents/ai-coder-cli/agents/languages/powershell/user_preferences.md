
# PowerShell User Preferences

## Version and Compatibility

### PowerShell Version
```yaml
# Target PowerShell version
powershell_version: "7.4"

# Options:
# - "7.4": Latest PowerShell 7
# - "7.0": PowerShell 7 LTS
# - "5.1": Windows PowerShell (legacy)

# Minimum supported version
min_powershell_version: "5.1"

# Cross-platform support
cross_platform: true  # Support Windows, Linux, macOS
```

### Module System
```yaml
# Module format
module_format: script_module

# Options:
# - script_module: .psm1 (script module)
# - binary_module: .dll (binary module)
# - manifest_module: .psd1 + .psm1

# Module structure
module_structure: advanced

# Options:
# - simple: Single .psm1 file
# - advanced: Public/Private folders
# - full: Complete module with tests, docs
```

## Code Style Preferences

### Indentation and Formatting
```yaml
# Indentation
indent_style: spaces
indent_size: 4

# Line length
max_line_length: 120

# Brace style
brace_style: same_line

# Options:
# - same_line: function Get-Data {
# - next_line: function Get-Data
#              {

# Blank lines
blank_lines_between_functions: 2
```

### Naming Conventions
```yaml
# Cmdlet/Function naming
cmdlet_naming: approved_verbs

# Use only approved verbs (Get-Verb)
# - Get, Set, New, Remove, Add, Clear, etc.

# Noun style
noun_style: SingularNoun

# Options:
# - SingularNoun: Get-User (not Get-Users)

# Parameter naming
parameter_naming: PascalCase

# Variable naming
variable_naming: PascalCase

# Options:
# - PascalCase: $UserName
# - camelCase: $userName

# Private variable prefix
private_prefix: underscore

# Options:
# - underscore: $_privateVar
# - none: $privateVar

# Constant naming
constant_naming: PascalCase  # With New-Variable -Option Constant
```

### Parameter Definitions
```yaml
# Parameter block style
parameter_block: advanced

# Options:
# - simple: param($Name)
# - advanced: [CmdletBinding()] param([string]$Name)

# Parameter attributes
parameter_attributes: full

# Options:
# - full: [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
# - minimal: [Parameter(Mandatory=$true)]

# Type constraints
use_type_constraints: true  # [string]$Name vs $Name

# Default values
provide_defaults: true

# Help messages
include_help_messages: true  # HelpMessage parameter attribute
```

### Pipeline Support
```yaml
# Support pipeline input
pipeline_support: true

# Pipeline implementation
pipeline_implementation: begin_process_end

# Options:
# - begin_process_end: Use begin, process, end blocks
# - process_only: Only process block
# - simple: No pipeline support

# Accept ValueFromPipeline
value_from_pipeline: true

# Accept ValueFromPipelineByPropertyName
value_from_pipeline_by_property_name: true
```

## Script Structure Preferences

### Script Header
```yaml
# Include comment-based help
include_help: true

# Help sections
help_sections:
  - synopsis
  - description
  - parameter
  - example
  - inputs
  - outputs
  - notes
  - link

# File encoding
file_encoding: utf8_bom  # UTF-8 with BOM for Windows compatibility

# Options:
# - utf8_bom: UTF-8 with BOM
# - utf8: UTF-8 without BOM
# - ascii: ASCII
```

### Error Handling
```yaml
# Error action preference
error_action_default: Stop

# Options:
# - Stop: Throw errors
# - Continue: Display and continue (default)
# - SilentlyContinue: Suppress errors
# - Inquire: Ask user

# Use try-catch-finally
use_try_catch: true

# Catch specific exceptions
catch_specific: true

# Write-Error vs throw
error_method: throw

# Options:
# - throw: throw (terminates)
# - write_error: Write-Error (non-terminating)
# - both: Use appropriately
```

### Output Preferences
```yaml
# Write-Output vs return
output_method: return

# Options:
# - return: Use return
# - write_output: Use Write-Output
# - both: Use appropriately

# Verbose output
use_verbose: true  # Write-Verbose

# Debug output
use_debug: true  # Write-Debug

# Progress bars
use_progress: true  # Write-Progress

# Warning messages
use_warnings: true  # Write-Warning
```

## Testing Preferences

### Testing Framework
```yaml
# Test framework
test_framework: pester

# Pester version
pester_version: "5.x"

# Options:
# - "5.x": Pester 5 (modern)
# - "4.x": Pester 4 (legacy)

# Test structure
test_structure: describe_context_it

# Describe blocks for grouping
use_describe_blocks: true

# Context blocks for scenarios
use_context_blocks: true
```

### Test Organization
```yaml
# Test file naming
test_file_pattern: "*.Tests.ps1"

# Test location
test_location: tests_folder

# Options:
# - tests_folder: Separate tests/ folder
# - next_to_source: Tests next to source files

# Test coverage
min_coverage: 80  # percentage

# Code coverage tool
coverage_tool: pester  # Built-in Pester coverage
```

### Mocking
```yaml
# Use Pester mocking
use_mocking: true

# Mock external dependencies
mock_external_commands: true

# Mock file system operations
mock_filesystem: true
```

## Tooling Preferences

### Code Analysis
```yaml
# Static analysis tool
analyzer: psscriptanalyzer

# PSScriptAnalyzer severity
severity_level: Warning

# Options:
# - Error: Only errors
# - Warning: Warnings and errors
# - Information: All messages

# Rules to enforce
rule_enforcement: recommended

# Options:
# - all: All rules
# - recommended: Recommended rules
# - custom: Custom rule set

# Custom rules
custom_rules:
  # - PSAvoidUsingCmdletAliases
  # - PSAvoidUsingPlainTextForPassword
  # - PSUseShouldProcessForStateChangingFunctions
```

### Formatter
```yaml
# Code formatter
formatter: built_in

# Options:
# - built_in: VS Code / ISE formatter
# - custom: Custom formatting rules

# Format on save
format_on_save: true

# Formatting rules
formatting_rules:
  align_assignment_statements: true
  use_correct_casing: true
```

### Documentation Generator
```yaml
# Documentation tool
docs_generator: platyps

# Options:
# - platyps: PlatyPS (Markdown-based help)
# - comment_based: Comment-based help only
# - both: Both approaches

# Generate external help
generate_external_help: true

# Update help
updatable_help: true
```

## Module Development Preferences

### Module Manifest
```yaml
# Create module manifest
create_manifest: true

# Manifest properties
manifest_properties:
  - root_module
  - module_version
  - guid
  - author
  - company_name
  - copyright
  - description
  - powershell_version
  - functions_to_export
  - cmdlets_to_export
  - variables_to_export
  - aliases_to_export
  - private_data

# Semantic versioning
use_semver: true
```

### Function Export
```yaml
# Export functions
export_method: manifest

# Options:
# - manifest: FunctionsToExport in manifest
# - export_modulemember: Export-ModuleMember in .psm1
# - both: Use both

# Public vs Private functions
function_organization: folders

# Options:
# - folders: Public/ and Private/ folders
# - naming: Prefix (e.g., _PrivateFunction)
# - manual: Manual export control
```

### Dependencies
```yaml
# Dependency management
dependency_management: manifest

# Options:
# - manifest: RequiredModules in manifest
# - install_module: Install-Module in code
# - psget: PSGet/PowerShellGet

# Specify module versions
pin_module_versions: true

# Minimum versions vs exact
version_spec: minimum

# Options:
# - minimum: Minimum version
# - exact: Exact version
# - range: Version range
```

## Advanced Function Preferences

### CmdletBinding
```yaml
# Use CmdletBinding
use_cmdlet_binding: true

# Default parameter set
use_parameter_sets: true

# Support ShouldProcess
support_should_process: when_appropriate

# Options:
# - always: Always include
# - when_appropriate: Only for state-changing functions
# - never: Never include

# ConfirmImpact
default_confirm_impact: Medium

# Options:
# - Low: Minor changes
# - Medium: Standard changes (default)
# - High: Significant changes
```

### Output Types
```yaml
# Declare output types
declare_output_types: true

# Example: [OutputType([PSCustomObject])]

# Return type consistency
enforce_consistent_output: true
```

### Validation Attributes
```yaml
# Use validation attributes
use_validation: true

# Common validations:
# - ValidateNotNullOrEmpty
# - ValidateRange
# - ValidateSet
# - ValidatePattern
# - ValidateScript

# Parameter aliases
use_parameter_aliases: true  # [Alias("Name")]
```

## Scripting Patterns

### Object Creation
```yaml
# Object creation method
object_creation: pscustomobject

# Options:
# - pscustomobject: [PSCustomObject]@{...}
# - new_object: New-Object PSObject
# - hashtable: @{...} (limited)
# - class: PowerShell classes (v5+)

# Add type names
add_type_names: true  # PSTypeName
```

### Splatting
```yaml
# Use splatting for parameters
use_splatting: true

# Splatting preference
splat_preference: always_for_multiple

# Options:
# - always: Always use splatting
# - always_for_multiple: 3+ parameters
# - optional: Use when improves readability
```

### String Formatting
```yaml
# String interpolation
string_interpolation: double_quotes

# Options:
# - double_quotes: "Value: $Variable"
# - format_operator: "Value: {0}" -f $Variable
# - string_builder: [System.Text.StringBuilder]

# Here-strings for multi-line
use_here_strings: true
```

### Loops and Iteration
```yaml
# Preferred loop for collections
loop_preference: foreach_object

# Options:
# - foreach_object: | ForEach-Object (pipeline)
# - foreach_statement: foreach ($item in $collection)
# - for_loop: for ($i=0; $i -lt $n; $i++)

# Use .ForEach() method
use_foreach_method: true  # $array.ForEach({...})

# Use .Where() method
use_where_method: true  # $array.Where({...})
```

## Performance Preferences

### Optimization
```yaml
# Measure performance
measure_performance: development_only

# Use ArrayList instead of Array
use_arraylist_for_growth: true

# Generic collections
use_generic_collections: true  # [System.Collections.Generic.List[string]]

# String concatenation
string_concat_method: join

# Options:
# - join: -join operator
# - stringbuilder: [System.Text.StringBuilder]
# - concatenation: + operator (avoid in loops)
```

### Caching
```yaml
# Cache repeated operations
use_caching: true

# Script-scoped cache
use_script_scope_cache: true

# Example: script:_cache = @{}
```

### Parallel Execution
```yaml
# Parallel processing (PS 7+)
use_parallel: true

# ForEach-Object -Parallel
foreach_parallel: true

# ThreadJob vs Start-Job
job_type: thread_job

# Options:
# - thread_job: Start-ThreadJob (faster)
# - start_job: Start-Job (traditional)
# - foreach_parallel: ForEach-Object -Parallel (PS 7+)
```

## Security Preferences

### Execution Policy
```yaml
# Recommended execution policy
execution_policy: RemoteSigned

# Options:
# - Restricted: No scripts
# - AllSigned: Only signed scripts
# - RemoteSigned: Downloaded scripts must be signed
# - Unrestricted: All scripts (not recommended)

# Sign scripts
sign_scripts: production_only

# Options:
# - always: Always sign
# - production_only: Only for production
# - never: Never sign
```

### Credential Management
```yaml
# Credential handling
credential_handling: pscredential

# Use PSCredential objects
use_pscredential: true

# Store credentials
credential_storage: credential_manager

# Options:
# - credential_manager: Windows Credential Manager
# - secure_string: Export-Clixml (encrypted)
# - secret_management: Microsoft.PowerShell.SecretManagement
# - vault: External vault (Azure Key Vault, etc.)

# Never store plain text passwords
enforce_secure_passwords: true
```

### Input Validation
```yaml
# Validate all input
validate_input: true

# Use parameter validation attributes
use_validation_attributes: true

# Sanitize file paths
sanitize_paths: true

# SQL injection prevention
use_parameterized_queries: true
```

## Configuration Management

### Configuration Files
```yaml
# Configuration format
config_format: psd1

# Options:
# - psd1: PowerShell Data File
# - json: JSON
# - xml: XML
# - ini: INI file

# Configuration location
config_location: user_profile

# Options:
# - user_profile: $env:USERPROFILE or $HOME
# - appdata: $env:APPDATA
# - module_root: Module root directory
# - custom: Custom location
```

### Environment Variables
```yaml
# Use environment variables
use_env_vars: true

# Environment variable prefix
env_var_prefix: MYAPP_

# .env file support
use_dotenv: false  # PowerShell doesn't have native support
```

## Logging Preferences

### Logging Framework
```yaml
# Logging approach
logging_approach: custom_functions

# Options:
# - custom_functions: Custom logging functions
# - write_verbose: Write-Verbose (built-in)
# - psframework: PSFramework module
# - nlog: NLog
# - log4net: log4net

# Log levels
log_levels:
  - Verbose
  - Information
  - Warning
  - Error
  - Critical

# Log to file
log_to_file: true

# Log file location
log_directory: logs  # or $env:TEMP
```

### Event Logging
```yaml
# Use Windows Event Log
use_event_log: false

# Create custom event source
custom_event_source: false
```

## Module Publishing

### PowerShell Gallery
```yaml
# Publish to PowerShell Gallery
publish_to_gallery: true

# Gallery API key storage
api_key_storage: secure_string

# Prerelease versions
use_prerelease: true  # -Prerelease tag

# Release notes
include_release_notes: true
```

### Versioning
```yaml
# Version scheme
version_scheme: semver

# Auto-increment version
auto_increment: minor

# Options:
# - major: Breaking changes
# - minor: New features
# - patch: Bug fixes

# Version in manifest and script
sync_versions: true
```

## CI/CD Preferences

### CI Platform
```yaml
# CI/CD platform
ci_platform: github_actions

# Options:
# - github_actions: GitHub Actions
# - azure_pipelines: Azure Pipelines
# - gitlab_ci: GitLab CI
# - jenkins: Jenkins

# CI steps
ci_steps:
  - lint          # PSScriptAnalyzer
  - test          # Pester
  - coverage      # Code coverage
  - build         # Module build
  - publish       # Publish to Gallery
```

### Build System
```yaml
# Build automation
build_system: invoke_build

# Options:
# - invoke_build: Invoke-Build
# - psake: psake
# - custom: Custom build script
# - none: No build system

# Build tasks
build_tasks:
  - clean
  - analyze
  - test
  - build
  - publish
```

## Cross-Platform Considerations

### OS Compatibility
```yaml
# Target operating systems
target_os:
  - windows
  - linux
  - macos

# Check OS before execution
check_os: true

# OS-specific code
use_os_checks: true

# Example: if ($IsWindows) { ... }
```

### Path Separators
```yaml
# Path handling
path_handling: system_io_path

# Options:
# - system_io_path: [System.IO.Path]::Combine()
# - join_path: Join-Path
# - manual: Manual concatenation (avoid)

# Use forward slashes
prefer_forward_slashes: false  # Use OS-appropriate
```

## Additional Preferences

### Aliases
```yaml
# Use cmdlet aliases
use_aliases: never

# Options:
# - never: Never use aliases in scripts
# - interactive_only: Only in interactive sessions
# - approved: Only approved aliases

# Create custom aliases
create_aliases: false  # In modules
```

### Comment Style
```yaml
# Comment style
comment_style: descriptive

# Options:
# - descriptive: Explain why
# - minimal: Only for complex logic
# - verbose: Extensive comments

# Use regions
use_regions: true

# Example:
# #region Initialization
# ...
# #endregion
```

### Classes
```yaml
# Use PowerShell classes (PS 5+)
use_classes: true

# Class usage
class_usage: advanced_scenarios

# Options:
# - always: Prefer classes
# - advanced_scenarios: For complex types
# - never: Avoid classes

# Inheritance
use_inheritance: true
```

### DSC (Desired State Configuration)
```yaml
# Use DSC (if applicable)
use_dsc: false

# DSC resource style
dsc_resource_style: class_based

# Options:
# - class_based: Class-based resources
# - mof_based: MOF-based resources
```

### Jobs and Background Tasks
```yaml
# Background processing
background_processing: thread_jobs

# Options:
# - thread_jobs: Start-ThreadJob
# - start_job: Start-Job
# - foreach_parallel: ForEach-Object -Parallel
# - runspaces: Custom runspace pools

# Job cleanup
auto_cleanup_jobs: true
```
