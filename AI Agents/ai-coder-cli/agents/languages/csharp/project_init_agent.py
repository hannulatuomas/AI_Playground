

"""
CSharp/.NET Project Initialization Agent

This agent handles CSharp and .NET project initialization with support for various
project types including console apps, web APIs, ASP.NET applications, and libraries.
"""

from typing import Dict, Any, List, Optional
from ...base import ProjectInitBase


class CSharpProjectInitAgent(ProjectInitBase):
    """
    CSharp/.NET-specific project initialization agent.
    
    Capabilities:
    - Initialize .NET projects (console, classlib, webapi, mvc, etc.)
    - Create proper .NET solution and project structure
    - Generate .csproj files with correct dependencies
    - Support for multiple .NET versions
    - NuGet package configuration
    """
    
    def __init__(
        self,
        name: str = "project_init_csharp",
        description: str = "CSharp/.NET project initialization",
        llm_router: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[Any] = None
    ):
        super().__init__(
            name=name,
            description=description,
            language="CSharp",
            llm_router=llm_router,
            tool_registry=tool_registry,
            config=config,
            memory_manager=memory_manager
        )
    
    def _get_project_types(self) -> List[str]:
        """Get supported CSharp project types."""
        return [
            'console',      # Console application
            'classlib',     # Class library
            'webapi',       # Web API
            'mvc',          # ASP.NET MVC
            'blazor',       # Blazor application
            'worker',       # Worker service
            'winforms',     # Windows Forms
            'wpf',          # WPF application
            'xunit',        # Test project
        ]
    
    def _get_project_structure(self, project_type: str) -> Dict[str, Any]:
        """Get directory structure for project type."""
        structures = {
            'console': {
                'directories': [
                    'src',
                    'tests',
                    'docs',
                ],
            },
            'classlib': {
                'directories': [
                    'src',
                    'tests',
                    'docs',
                ],
            },
            'webapi': {
                'directories': [
                    'src/Controllers',
                    'src/Models',
                    'src/Services',
                    'src/Data',
                    'tests',
                    'docs',
                ],
            },
            'mvc': {
                'directories': [
                    'src/Controllers',
                    'src/Models',
                    'src/Views',
                    'src/wwwroot',
                    'tests',
                    'docs',
                ],
            },
            'blazor': {
                'directories': [
                    'src/Pages',
                    'src/Shared',
                    'src/wwwroot',
                    'src/Data',
                    'tests',
                    'docs',
                ],
            },
        }
        
        return structures.get(project_type, structures['console'])
    
    def _get_default_files(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate default CSharp configuration files."""
        files = {}
        project_name = config['project_name'].replace('-', '').replace(' ', '')
        project_type = config['project_type']
        dotnet_version = config.get('dotnet_version', 'net8.0')
        
        # README.md
        files['README.md'] = f"""# {config['project_name']}

{config.get('description', 'A CSharp .NET project')}

## Prerequisites

- .NET SDK {config.get('dotnet_version', '8.0')}+

## Build

```bash
dotnet build
```

## Run

```bash
dotnet run --project src/{project_name}.csproj
```

## Test

```bash
dotnet test
```

## Author

{config.get('author', 'N/A')}

## License

{config.get('license', 'MIT')}
"""
        
        # .csproj file
        files[f'src/{project_name}.csproj'] = f"""<Project Sdk="Microsoft.NET.Sdk{self._get_sdk_suffix(project_type)}">

  <PropertyGroup>
    <TargetFramework>{dotnet_version}</TargetFramework>
    {self._get_output_type(project_type)}
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
{self._get_package_references(project_type)}
  </ItemGroup>

</Project>
"""
        
        # Solution file
        files[f'{project_name}.sln'] = f"""
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31903.59
MinimumVisualStudioVersion = 10.0.40219.1
Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = "{project_name}", "src\\{project_name}.csproj", "{{GUID-HERE}}"
EndProject
Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Debug|Any CPU = Debug|Any CPU
		Release|Any CPU = Release|Any CPU
	EndGlobalSection
	GlobalSection(ProjectConfigurationPlatforms) = postSolution
		{{GUID-HERE}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
		{{GUID-HERE}}.Debug|Any CPU.Build.0 = Debug|Any CPU
		{{GUID-HERE}}.Release|Any CPU.ActiveCfg = Release|Any CPU
		{{GUID-HERE}}.Release|Any CPU.Build.0 = Release|Any CPU
	EndGlobalSection
EndGlobal
"""
        
        # Program.cs
        if project_type in ['console', 'classlib']:
            files['src/Program.cs'] = f"""namespace {project_name};

class Program
{{
    static void Main(string[] args)
    {{
        Console.WriteLine("Hello from {project_name}!");
    }}
}}
"""
        elif project_type == 'webapi':
            files['src/Program.cs'] = f"""var builder = WebApplication.CreateBuilder(args);

// Add services
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Configure middleware
if (app.Environment.IsDevelopment())
{{
    app.UseSwagger();
    app.UseSwaggerUI();
}}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

app.Run();
"""
        
        # .gitignore
        files['.gitignore'] = """## .NET
bin/
obj/
*.user
*.suo
*.cache
*.dll
*.exe
*.pdb
*.log

# Visual Studio
.vs/
*.vsidx
*.vssscc

# Rider
.idea/
*.sln.iml

# User-specific files
*.rsuser
*.suo
*.user
*.userosscache
*.sln.docstates

# Build results
[Dd]ebug/
[Dd]ebugPublic/
[Rr]elease/
[Rr]eleases/
x64/
x86/
[Aa][Rr][Mm]/
[Aa][Rr][Mm]64/
bld/
[Bb]in/
[Oo]bj/
[Ll]og/
[Ll]ogs/

# NuGet
*.nupkg
*.snupkg
**/packages/*
!**/packages/build/
project.lock.json
project.fragment.lock.json
artifacts/
"""
        
        return files
    
    def _get_sdk_suffix(self, project_type: str) -> str:
        """Get SDK suffix for project type."""
        if project_type in ['webapi', 'mvc', 'blazor']:
            return '.Web'
        elif project_type == 'worker':
            return '.Worker'
        return ''
    
    def _get_output_type(self, project_type: str) -> str:
        """Get output type for project type."""
        if project_type == 'console':
            return '<OutputType>Exe</OutputType>'
        elif project_type == 'classlib':
            return '<OutputType>Library</OutputType>'
        return ''
    
    def _get_package_references(self, project_type: str) -> str:
        """Get NuGet package references for project type."""
        packages = {
            'webapi': [
                '<PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="8.0.0" />',
                '<PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />',
            ],
            'xunit': [
                '<PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.8.0" />',
                '<PackageReference Include="xunit" Version="2.6.1" />',
                '<PackageReference Include="xunit.runner.visualstudio" Version="2.5.3" />',
            ],
        }
        
        refs = packages.get(project_type, [])
        return '\n'.join(f'    {ref}' for ref in refs)
    
    def _generate_language_rules(self, config: Dict[str, Any]) -> str:
        """Generate CSharp-specific rules."""
        return f"""## CSharp/.NET-Specific Rules

### .NET Version

- **Target Framework**: {config.get('dotnet_version', 'net8.0')}
- **Language Version**: CSharp 12 (latest)

### Code Style

1. **Naming Conventions**:
   - PascalCase for classes, methods, properties
   - camelCase for local variables and parameters
   - _camelCase for private fields (optional underscore prefix)
   - UPPER_CASE for constants
   
2. **Formatting**:
   - Use 4 spaces for indentation
   - Opening braces on new line (Allman style)
   - Use `var` when type is obvious
   
3. **Nullable Reference Types**:
   - Enable nullable reference types
   - Use `?` suffix for nullable types
   - Avoid null reference exceptions

### Project Type: {config['project_type']}

### Best Practices

1. **Async/Await**: Use async/await for I/O operations
2. **Dependency Injection**: Use built-in DI container
3. **Configuration**: Use IConfiguration for settings
4. **Logging**: Use ILogger for logging
5. **Error Handling**: Use try-catch with specific exceptions

### Testing

1. **Framework**: Use xUnit or NUnit
2. **Mocking**: Use Moq for mocking
3. **Coverage**: Aim for >80% code coverage
4. **Naming**: Test methods should describe what they test

### NuGet Packages

1. **Versioning**: Use semantic versioning
2. **Updates**: Keep packages up to date
3. **Security**: Regular security audits

### Performance

1. **LINQ**: Be aware of deferred execution
2. **String**: Use StringBuilder for string concatenation
3. **Collections**: Choose appropriate collection types
4. **Memory**: Use Span<T> and Memory<T> for performance-critical code

### Security

1. **Input Validation**: Validate all inputs
2. **SQL Injection**: Use parameterized queries
3. **Authentication**: Use ASP.NET Core Identity
4. **Authorization**: Implement proper authorization policies
"""
    
    def _get_language_specific_questions(self) -> List[Dict[str, Any]]:
        """Get CSharp-specific questions."""
        return [
            {
                'key': 'dotnet_version',
                'question': '.NET version?',
                'type': 'choice',
                'options': ['net6.0', 'net7.0', 'net8.0'],
                'default': 'net8.0',
                'required': False
            },
            {
                'key': 'use_nullable',
                'question': 'Enable nullable reference types?',
                'type': 'bool',
                'default': True,
                'required': False
            },
        ]


