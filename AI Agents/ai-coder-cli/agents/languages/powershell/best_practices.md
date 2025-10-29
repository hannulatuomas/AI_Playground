
# PowerShell Best Practices

## Code Organization and Structure

### Script Structure
```powershell
<#
.SYNOPSIS
    Brief description of the script

.DESCRIPTION
    Detailed description of what the script does,
    its purpose, and important notes.

.PARAMETER ComputerName
    Description of the ComputerName parameter

.PARAMETER Credential
    Description of the Credential parameter

.EXAMPLE
    .\Script.ps1 -ComputerName "SERVER01"
    
    Description of what this example does

.EXAMPLE
    .\Script.ps1 -ComputerName "SERVER01" -Credential $cred
    
    Description of what this example does with credentials

.NOTES
    Author: Your Name
    Date: 2024-01-01
    Version: 1.0.0
    
.LINK
    https://docs.example.com/script-documentation
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
    [string]$ComputerName,
    
    [Parameter(Mandatory = $false)]
    [PSCredential]$Credential
)

begin {
    # Initialization code
    Write-Verbose "Starting script execution"
    $ErrorActionPreference = 'Stop'
}

process {
    # Main logic here
    try {
        Write-Verbose "Processing $ComputerName"
        # Your code
    }
    catch {
        Write-Error "Error processing $ComputerName: $_"
        throw
    }
}

end {
    # Cleanup code
    Write-Verbose "Script execution completed"
}
```

### Module Structure
```
MyModule/
├── MyModule.psd1          # Module manifest
├── MyModule.psm1          # Module script
├── Public/                # Public functions (exported)
│   ├── Get-Something.ps1
│   └── Set-Something.ps1
├── Private/               # Private functions (not exported)
│   ├── Helper.ps1
│   └── Validator.ps1
├── Classes/               # PowerShell classes
│   └── MyClass.ps1
├── Tests/                 # Pester tests
│   ├── MyModule.Tests.ps1
│   └── Integration.Tests.ps1
├── en-US/                 # Help files
│   └── about_MyModule.help.txt
└── README.md
```

### Module Manifest (.psd1)
```powershell
@{
    RootModule = 'MyModule.psm1'
    ModuleVersion = '1.0.0'
    GUID = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    Author = 'Your Name'
    CompanyName = 'Your Company'
    Copyright = '(c) 2024. All rights reserved.'
    Description = 'Module description'
    PowerShellVersion = '5.1'
    
    FunctionsToExport = @(
        'Get-Something',
        'Set-Something'
    )
    
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
    
    PrivateData = @{
        PSData = @{
            Tags = @('Tag1', 'Tag2')
            LicenseUri = 'https://license.url'
            ProjectUri = 'https://project.url'
        }
    }
}
```

## Naming Conventions

### Cmdlets and Functions
```powershell
# Use approved verbs: Get, Set, New, Remove, Add, etc.
# Full list: Get-Verb

# Cmdlet naming: Verb-SingularNoun
function Get-UserAccount { }
function Set-NetworkConfig { }
function New-DatabaseConnection { }
function Remove-TempFile { }
function Test-PathExists { }

# Use singular nouns
# GOOD:
function Get-Process { }

# BAD:
function Get-Processes { }

# Use PascalCase for cmdlets
function Get-ServiceStatus { }
function Invoke-WebhookNotification { }
```

### Variables
```powershell
# Variables: PascalCase or camelCase (be consistent)
$UserName = "John"
$ServiceAccount = "admin"

# Private/internal variables: lowercase with underscore
$_internalCache = @{}
$_connectionString = ""

# Constants: Use New-Variable with -Option Constant
New-Variable -Name MaxRetries -Value 3 -Option Constant

# Or readonly
New-Variable -Name ApiUrl -Value "https://api.example.com" -Option ReadOnly

# Boolean variables: use descriptive names
$IsEnabled = $true
$HasPermission = $false
$ShouldContinue = $true
```

### Parameters
```powershell
function Get-UserData {
    [CmdletBinding()]
    param(
        # Use PascalCase
        [Parameter(Mandatory = $true)]
        [string]$UserId,
        
        [Parameter(Mandatory = $false)]
        [switch]$IncludeDetails,
        
        [Parameter(ValueFromPipeline = $true)]
        [string[]]$ComputerName
    )
}
```

### Classes
```powershell
# Classes: PascalCase
class UserAccount {
    # Properties: PascalCase
    [string]$UserName
    [string]$Email
    [datetime]$CreatedDate
    
    # Private properties: lowercase with underscore
    hidden [string]$_passwordHash
    
    # Constructor
    UserAccount([string]$userName, [string]$email) {
        $this.UserName = $userName
        $this.Email = $email
        $this.CreatedDate = Get-Date
    }
    
    # Methods: PascalCase
    [void]UpdateEmail([string]$newEmail) {
        $this.Email = $newEmail
    }
    
    [string]GetDisplayName() {
        return "$($this.UserName) <$($this.Email)>"
    }
}
```

## Error Handling Patterns

### Try-Catch-Finally
```powershell
# Basic error handling
try {
    Get-Content -Path "C:\file.txt" -ErrorAction Stop
}
catch {
    Write-Error "Failed to read file: $_"
    throw
}
finally {
    # Cleanup code runs regardless of error
    Write-Verbose "Cleanup completed"
}

# Catch specific exceptions
try {
    Invoke-RestMethod -Uri $ApiUrl
}
catch [System.Net.WebException] {
    Write-Error "Network error: $($_.Exception.Message)"
}
catch [System.UnauthorizedAccessException] {
    Write-Error "Access denied: $($_.Exception.Message)"
}
catch {
    Write-Error "Unexpected error: $_"
    throw
}
```

### Error Action Preference
```powershell
# Set error action preference
$ErrorActionPreference = 'Stop'        # Throw errors
$ErrorActionPreference = 'Continue'    # Display error and continue (default)
$ErrorActionPreference = 'SilentlyContinue'  # Suppress errors
$ErrorActionPreference = 'Inquire'     # Ask user what to do

# Per-command error action
Get-Content -Path $Path -ErrorAction Stop

# Check if error occurred
Get-Process -Name "NonExistent" -ErrorAction SilentlyContinue -ErrorVariable err
if ($err) {
    Write-Warning "Process not found"
}
```

### Custom Error Handling
```powershell
# Throw custom errors
function Get-UserData {
    [CmdletBinding()]
    param([string]$UserId)
    
    if ([string]::IsNullOrWhiteSpace($UserId)) {
        throw [System.ArgumentException]::new("UserId cannot be empty")
    }
    
    $user = Find-User -Id $UserId
    if (-not $user) {
        throw [System.InvalidOperationException]::new("User not found: $UserId")
    }
    
    return $user
}

# Custom error record
function Write-CustomError {
    param(
        [string]$Message,
        [string]$ErrorId,
        [System.Management.Automation.ErrorCategory]$Category
    )
    
    $exception = [System.Exception]::new($Message)
    $errorRecord = [System.Management.Automation.ErrorRecord]::new(
        $exception,
        $ErrorId,
        $Category,
        $null
    )
    
    $PSCmdlet.WriteError($errorRecord)
}
```

### Should Process Pattern
```powershell
function Remove-UserAccount {
    [CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
    param(
        [Parameter(Mandatory = $true)]
        [string]$UserId
    )
    
    if ($PSCmdlet.ShouldProcess($UserId, "Remove user account")) {
        # Perform the removal
        Write-Verbose "Removing user account: $UserId"
    }
}

# Usage:
# Remove-UserAccount -UserId "user123" -WhatIf
# Remove-UserAccount -UserId "user123" -Confirm
```

## Performance Considerations

### Pipeline Usage
```powershell
# Use pipeline for efficient processing
# GOOD: Stream processing
Get-ChildItem -Path $Path -Recurse | Where-Object { $_.Length -gt 1MB }

# BAD: Load everything into memory first
$files = Get-ChildItem -Path $Path -Recurse
$largeFiles = foreach ($file in $files) {
    if ($file.Length -gt 1MB) {
        $file
    }
}

# Use ForEach-Object for pipeline
1..1000 | ForEach-Object { Process-Item $_ }

# For simple transformations, use .ForEach() method
$numbers = 1..1000
$numbers.ForEach({ $_ * 2 })
```

### Filtering Early
```powershell
# Filter early in the pipeline
# GOOD:
Get-Process | Where-Object CPU -gt 100 | Select-Object Name, CPU

# Better (filter at source):
Get-Process -Name "chrome" | Select-Object Name, CPU

# Use -Filter instead of Where-Object when possible
# GOOD:
Get-ChildItem -Path $Path -Filter "*.log"

# SLOWER:
Get-ChildItem -Path $Path | Where-Object Extension -eq ".log"
```

### String Building
```powershell
# Use StringBuilder for large strings
$sb = [System.Text.StringBuilder]::new()
foreach ($item in $items) {
    [void]$sb.AppendLine($item.ToString())
}
$result = $sb.ToString()

# Use -join for concatenation
# GOOD:
$csv = $values -join ','

# BAD:
$csv = ""
foreach ($value in $values) {
    $csv += "$value,"
}
```

### Avoid Expensive Operations in Loops
```powershell
# BAD: Expensive operation in loop
foreach ($file in Get-ChildItem) {
    $content = Get-Content $file.FullName
    # Process content
}

# GOOD: Pipeline processing
Get-ChildItem | ForEach-Object {
    $content = Get-Content $_.FullName
    # Process content
}
```

### Use .NET Methods When Faster
```powershell
# String operations
# Faster:
[string]::IsNullOrWhiteSpace($value)
# vs
if ($value -eq $null -or $value.Trim() -eq "") { }

# File operations
# Faster for simple file reading:
[System.IO.File]::ReadAllText($path)
# vs
Get-Content -Path $path -Raw

# Check if file exists
# Faster:
[System.IO.File]::Exists($path)
# vs
Test-Path -Path $path -PathType Leaf
```

### Measure Performance
```powershell
# Measure script block execution time
$elapsed = Measure-Command {
    # Your code here
}
Write-Host "Execution time: $($elapsed.TotalSeconds) seconds"

# Compare approaches
$time1 = Measure-Command { Approach1 }
$time2 = Measure-Command { Approach2 }
Write-Host "Approach1: $($time1.TotalMilliseconds)ms"
Write-Host "Approach2: $($time2.TotalMilliseconds)ms"
```

## Security Best Practices

### Credentials Management
```powershell
# Use PSCredential objects
$credential = Get-Credential

# Create credential from secure string
$securePassword = ConvertTo-SecureString "P@ssw0rd" -AsPlainText -Force
$credential = [PSCredential]::new("username", $securePassword)

# Store credentials securely
$credential | Export-Clixml -Path "C:\secure\creds.xml"
$credential = Import-Clixml -Path "C:\secure\creds.xml"

# Use Windows Credential Manager
Install-Module -Name CredentialManager
New-StoredCredential -Target "MyApp" -Credential $credential
$credential = Get-StoredCredential -Target "MyApp"

# Never store plain text passwords
# BAD:
$password = "P@ssw0rd"

# GOOD:
$password = Read-Host "Enter password" -AsSecureString
```

### Input Validation
```powershell
function Get-UserData {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string]$UserId,
        
        [Parameter(Mandatory = $false)]
        [ValidateRange(1, 100)]
        [int]$PageSize = 10,
        
        [Parameter(Mandatory = $false)]
        [ValidatePattern('^\d{3}-\d{2}-\d{4}$')]
        [string]$SSN,
        
        [Parameter(Mandatory = $false)]
        [ValidateSet('Active', 'Inactive', 'Suspended')]
        [string]$Status = 'Active',
        
        [Parameter(Mandatory = $false)]
        [ValidateScript({
            Test-Path $_ -PathType Container
        })]
        [string]$OutputPath
    )
}
```

### SQL Injection Prevention
```powershell
# Use parameterized queries
$query = "SELECT * FROM Users WHERE UserId = @UserId"
$command = $connection.CreateCommand()
$command.CommandText = $query
$command.Parameters.AddWithValue("@UserId", $userId)

# BAD: String concatenation
$query = "SELECT * FROM Users WHERE UserId = '$userId'"
```

### Script Signing
```powershell
# Require signed scripts (in execution policy)
Set-ExecutionPolicy -ExecutionPolicy AllSigned -Scope CurrentUser

# Sign a script
$cert = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert
Set-AuthenticodeSignature -FilePath .\Script.ps1 -Certificate $cert

# Verify signature
Get-AuthenticodeSignature -FilePath .\Script.ps1
```

### Secure Communication
```powershell
# Use TLS 1.2 or higher
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Validate SSL certificates
$webRequest = [System.Net.WebRequest]::Create($url)
$webRequest.ServerCertificateValidationCallback = {
    param($sender, $certificate, $chain, $sslPolicyErrors)
    return $sslPolicyErrors -eq [System.Net.Security.SslPolicyErrors]::None
}
```

### Path Validation
```powershell
function Get-SafePath {
    param(
        [string]$Path,
        [string]$BaseDirectory
    )
    
    # Resolve to absolute path
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $baseFullPath = [System.IO.Path]::GetFullPath($BaseDirectory)
    
    # Ensure path is under base directory
    if (-not $fullPath.StartsWith($baseFullPath)) {
        throw "Path is outside base directory"
    }
    
    return $fullPath
}
```

## Testing Approaches

### Pester Testing
```powershell
# Install Pester
Install-Module -Name Pester -Force -SkipPublisherCheck

# Basic test structure
Describe "Get-UserData" {
    Context "When user exists" {
        It "Returns user object" {
            $result = Get-UserData -UserId "user123"
            $result | Should -Not -BeNullOrEmpty
            $result.UserId | Should -Be "user123"
        }
    }
    
    Context "When user does not exist" {
        It "Throws error" {
            { Get-UserData -UserId "invalid" } | Should -Throw
        }
    }
}

# Setup and teardown
Describe "DatabaseOperations" {
    BeforeAll {
        # Runs once before all tests
        $script:connection = New-DatabaseConnection
    }
    
    AfterAll {
        # Runs once after all tests
        $script:connection.Close()
    }
    
    BeforeEach {
        # Runs before each test
        Initialize-TestData
    }
    
    AfterEach {
        # Runs after each test
        Clear-TestData
    }
    
    It "Can insert data" {
        $result = Insert-Data -Value "test"
        $result | Should -Be $true
    }
}
```

### Mocking
```powershell
# Mock cmdlets
Describe "Get-ServerStatus" {
    It "Handles connection errors" {
        Mock Test-Connection { return $false }
        Mock Write-Warning { }
        
        $result = Get-ServerStatus -ComputerName "SERVER01"
        
        Assert-MockCalled Test-Connection -Times 1
        Assert-MockCalled Write-Warning -Times 1
        $result | Should -Be "Offline"
    }
}

# Mock with parameters
Mock Get-Content { return "mocked content" } -ParameterFilter {
    $Path -eq "C:\test.txt"
}

# Mock return values based on parameters
Mock Invoke-RestMethod {
    if ($Uri -like "*users*") {
        return @{ Users = @() }
    }
    else {
        return @{ Data = "test" }
    }
}
```

### Test Data
```powershell
# Use TestCases for data-driven tests
Describe "Validate-Email" {
    It "Validates email: <Email>" -TestCases @(
        @{ Email = "user@example.com"; Expected = $true }
        @{ Email = "invalid"; Expected = $false }
        @{ Email = "user@domain.co.uk"; Expected = $true }
    ) {
        param($Email, $Expected)
        
        $result = Validate-Email -Email $Email
        $result | Should -Be $Expected
    }
}
```

### Code Coverage
```powershell
# Run tests with code coverage
$config = [PesterConfiguration]::Default
$config.CodeCoverage.Enabled = $true
$config.CodeCoverage.Path = ".\MyModule.psm1"
$config.CodeCoverage.OutputPath = ".\coverage.xml"

Invoke-Pester -Configuration $config
```

## Documentation Standards

### Comment-Based Help
```powershell
function Get-UserAccount {
    <#
    .SYNOPSIS
        Retrieves user account information.
    
    .DESCRIPTION
        The Get-UserAccount cmdlet retrieves detailed information about
        user accounts from Active Directory or local system.
        
        This cmdlet supports filtering by various criteria and can
        retrieve both enabled and disabled accounts.
    
    .PARAMETER UserId
        Specifies the user ID of the account to retrieve.
        This parameter is mandatory and accepts pipeline input.
    
    .PARAMETER IncludeGroups
        When specified, includes group membership information in the output.
    
    .PARAMETER Credential
        Specifies credentials to use for the query.
        If not specified, uses the current user's credentials.
    
    .EXAMPLE
        Get-UserAccount -UserId "john.doe"
        
        Retrieves information for user "john.doe".
    
    .EXAMPLE
        "user1", "user2" | Get-UserAccount -IncludeGroups
        
        Retrieves information for multiple users including their group memberships.
    
    .EXAMPLE
        Get-UserAccount -UserId "admin" -Credential $cred
        
        Retrieves information using alternate credentials.
    
    .INPUTS
        System.String
        You can pipe user IDs to this cmdlet.
    
    .OUTPUTS
        PSCustomObject
        Returns custom objects containing user information.
    
    .NOTES
        Author: Your Name
        Date: 2024-01-01
        Version: 1.0.0
        
        Requires Active Directory module for AD queries.
    
    .LINK
        https://docs.example.com/Get-UserAccount
    
    .LINK
        Set-UserAccount
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [string]$UserId,
        
        [Parameter()]
        [switch]$IncludeGroups,
        
        [Parameter()]
        [PSCredential]$Credential
    )
    
    process {
        # Implementation
    }
}
```

### Inline Comments
```powershell
# Use comments to explain why, not what
# BAD: Increment counter
$counter++

# GOOD: Track number of retry attempts for exponential backoff
$retryCount++

# Use regions for organizing large scripts
#region Initialization
$ErrorActionPreference = 'Stop'
$VerbosePreference = 'Continue'
#endregion

#region Helper Functions
function Get-Helper { }
#endregion

#region Main Logic
# Main script code
#endregion
```

## Common Pitfalls to Avoid

### 1. Not Using -ErrorAction Stop
```powershell
# BAD: Error is not caught
try {
    Get-Content -Path "NonExistent.txt"
}
catch {
    Write-Error "This won't catch the error"
}

# GOOD:
try {
    Get-Content -Path "NonExistent.txt" -ErrorAction Stop
}
catch {
    Write-Error "Error caught: $_"
}
```

### 2. Implicit Type Conversions
```powershell
# Be aware of type conversions
$port = "8080"
$port -eq 8080  # True (string converted to int)

# Use explicit comparisons
$port = "8080"
$port -ceq "8080"  # Case-sensitive string comparison

# Or explicit casting
[int]$port = "8080"
$port -eq 8080  # True (both are int)
```

### 3. Comparing with $null
```powershell
# Always put $null on the left
# GOOD:
if ($null -eq $value) { }

# BAD: Can give unexpected results with arrays
if ($value -eq $null) { }

# Example of the problem:
$array = @($null, 1, 2)
$array -eq $null  # Returns @($null) not $true/$false
```

### 4. Not Using [CmdletBinding()]
```powershell
# Without [CmdletBinding()], you don't get:
# - Common parameters (-Verbose, -Debug, etc.)
# - Advanced function features
# - Pipeline support

# GOOD:
function Get-Data {
    [CmdletBinding()]
    param([string]$Name)
    
    Write-Verbose "Getting data for $Name"
}

# Now supports: Get-Data -Name "test" -Verbose
```

### 5. Write-Host vs Write-Output
```powershell
# BAD: Can't be redirected or captured
Write-Host "Result: $result"

# GOOD: Can be captured and redirected
Write-Output "Result: $result"

# Use Write-Host only for:
# - Interactive messages
# - Color-coded output for users
# - UI-specific formatting

# Use Write-Output for:
# - Function results
# - Data that should be in the pipeline
```

## Language-Specific Idioms and Patterns

### Splatting
```powershell
# Use splatting for readability
# Instead of:
Get-ChildItem -Path "C:\Temp" -Recurse -Filter "*.log" -ErrorAction Stop

# Use:
$params = @{
    Path        = "C:\Temp"
    Recurse     = $true
    Filter      = "*.log"
    ErrorAction = "Stop"
}
Get-ChildItem @params

# Array splatting for positional parameters
$args = "C:\Temp", "*.log"
Get-ChildItem @args
```

### Pipeline Patterns
```powershell
# Process pipeline input properly
function Process-Item {
    [CmdletBinding()]
    param(
        [Parameter(ValueFromPipeline = $true)]
        [string[]]$Name
    )
    
    begin {
        Write-Verbose "Starting processing"
        $count = 0
    }
    
    process {
        foreach ($item in $Name) {
            Write-Verbose "Processing: $item"
            $count++
        }
    }
    
    end {
        Write-Verbose "Processed $count items"
    }
}
```

### Hash Tables and PSCustomObjects
```powershell
# Create hash table
$user = @{
    Name  = "John"
    Email = "john@example.com"
    Age   = 30
}

# Convert to PSCustomObject for better output
$userObject = [PSCustomObject]@{
    Name  = "John"
    Email = "john@example.com"
    Age   = 30
}

# Add type name for formatting
$userObject.PSObject.TypeNames.Insert(0, 'Custom.UserAccount')

# Ordered hash tables
$ordered = [ordered]@{
    First  = 1
    Second = 2
    Third  = 3
}
```

### Filtering and Selection
```powershell
# Where-Object patterns
# Short form:
Get-Process | Where-Object CPU -gt 100

# Script block:
Get-Process | Where-Object { $_.CPU -gt 100 }

# Select-Object patterns
# Select properties:
Get-Process | Select-Object Name, CPU

# Calculated properties:
Get-Process | Select-Object Name, 
    @{Name="CPUSeconds"; Expression={$_.CPU}},
    @{Name="Memory MB"; Expression={$_.WorkingSet64 / 1MB}}

# First/Last:
Get-ChildItem | Select-Object -First 10
Get-ChildItem | Select-Object -Last 5
```

### Switch Statement
```powershell
# Switch with multiple conditions
switch ($value) {
    { $_ -lt 0 } {
        "Negative"
    }
    { $_ -eq 0 } {
        "Zero"
    }
    { $_ -gt 0 } {
        "Positive"
    }
}

# Switch with regex
switch -Regex ($input) {
    '^\d{3}-\d{2}-\d{4}$' {
        "Social Security Number"
    }
    '^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$' {
        "Email Address"
    }
}

# Switch with file processing
switch -File "C:\data.txt" {
    { $_ -match "ERROR" } {
        Write-Error $_
    }
    { $_ -match "WARNING" } {
        Write-Warning $_
    }
}
```

### Classes
```powershell
class UserAccount {
    # Properties
    [string]$UserName
    [string]$Email
    [datetime]$CreatedDate
    
    # Hidden property
    hidden [string]$PasswordHash
    
    # Static property
    static [int]$TotalUsers = 0
    
    # Constructor
    UserAccount([string]$userName, [string]$email) {
        $this.UserName = $userName
        $this.Email = $email
        $this.CreatedDate = Get-Date
        [UserAccount]::TotalUsers++
    }
    
    # Method
    [void]UpdateEmail([string]$newEmail) {
        if ($this.ValidateEmail($newEmail)) {
            $this.Email = $newEmail
        }
    }
    
    # Private method
    hidden [bool]ValidateEmail([string]$email) {
        return $email -match '^\w+@\w+\.\w+$'
    }
    
    # Static method
    static [int]GetTotalUsers() {
        return [UserAccount]::TotalUsers
    }
    
    # Operator overload (ToString)
    [string]ToString() {
        return "$($this.UserName) <$($this.Email)>"
    }
}

# Inheritance
class AdminAccount : UserAccount {
    [string[]]$Permissions
    
    AdminAccount([string]$userName, [string]$email, [string[]]$permissions) : base($userName, $email) {
        $this.Permissions = $permissions
    }
    
    [bool]HasPermission([string]$permission) {
        return $this.Permissions -contains $permission
    }
}
```

### Advanced Functions
```powershell
function Invoke-AdvancedFunction {
    [CmdletBinding(DefaultParameterSetName = 'Default')]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(
            Mandatory = $true,
            ValueFromPipeline = $true,
            ValueFromPipelineByPropertyName = $true,
            ParameterSetName = 'Default',
            Position = 0
        )]
        [ValidateNotNullOrEmpty()]
        [Alias('CN', 'Name')]
        [string[]]$ComputerName,
        
        [Parameter(ParameterSetName = 'Alternate')]
        [switch]$AlternateMode,
        
        [Parameter()]
        [PSCredential]$Credential
    )
    
    begin {
        Write-Verbose "[$($MyInvocation.MyCommand.Name)] Starting"
        $results = [System.Collections.Generic.List[PSCustomObject]]::new()
    }
    
    process {
        foreach ($computer in $ComputerName) {
            Write-Progress -Activity "Processing" -Status $computer
            
            try {
                # Process computer
                $result = [PSCustomObject]@{
                    ComputerName = $computer
                    Status       = "Success"
                    Data         = "Some data"
                }
                
                $results.Add($result)
            }
            catch {
                $PSCmdlet.WriteError($_)
            }
        }
    }
    
    end {
        Write-Verbose "[$($MyInvocation.MyCommand.Name)] Completed"
        return $results
    }
}
```

### Parallel Processing (PowerShell 7+)
```powershell
# ForEach-Object -Parallel
$servers = @("server1", "server2", "server3")
$servers | ForEach-Object -Parallel {
    Test-Connection -ComputerName $_ -Count 1
} -ThrottleLimit 5

# With variable passing
$timeout = 30
1..10 | ForEach-Object -Parallel {
    Start-Sleep -Seconds $using:timeout
    "Completed $_"
}

# Thread jobs
$job = Start-ThreadJob -ScriptBlock {
    Get-Process
}
Wait-Job $job
$result = Receive-Job $job
```
