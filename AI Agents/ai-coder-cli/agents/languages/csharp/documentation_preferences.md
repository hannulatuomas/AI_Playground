
# C#/.NET Documentation Preferences

This document defines the documentation standards and preferences for C# and .NET projects.
These preferences guide AI agents in maintaining consistent, high-quality documentation.

---

## General Documentation Philosophy

**Core Principles:**
1. **XML Documentation Comments** - Primary documentation format
2. **IntelliSense Support** - Documentation should enhance IDE experience
3. **API Surface Clarity** - Public APIs must be well-documented
4. **Examples and Remarks** - Provide context and usage examples
5. **Professional Standards** - Follow Microsoft's documentation guidelines

---

## Code Documentation Standards

### XML Documentation Comments

**Standard Format:**

```csharp
/// <summary>
/// Brief one-line summary of the member.
/// </summary>
/// <remarks>
/// More detailed explanation of the member's purpose, behavior, and usage.
/// Can include multiple paragraphs.
/// <para>
/// Additional paragraph of explanation.
/// </para>
/// </remarks>
/// <param name="paramName">Description of the parameter.</param>
/// <returns>Description of the return value.</returns>
/// <exception cref="ArgumentNullException">
/// Thrown when paramName is null.
/// </exception>
/// <example>
/// <code>
/// var result = MethodName("value");
/// Console.WriteLine(result);
/// </code>
/// </example>
public ReturnType MethodName(string paramName)
{
    // Implementation
}
```

### Class Documentation

```csharp
/// <summary>
/// Represents a [brief description of class purpose].
/// </summary>
/// <remarks>
/// Detailed description of the class, its responsibilities, and when to use it.
/// <para>
/// This class is thread-safe / not thread-safe.
/// </para>
/// </remarks>
/// <example>
/// <code>
/// var instance = new ClassName();
/// instance.DoSomething();
/// </code>
/// </example>
public class ClassName
{
    /// <summary>
    /// Gets or sets the [property description].
    /// </summary>
    /// <value>
    /// The [description of what the property contains].
    /// </value>
    public string PropertyName { get; set; }
    
    /// <summary>
    /// Initializes a new instance of the <see cref="ClassName"/> class.
    /// </summary>
    /// <param name="param">Description of constructor parameter.</param>
    public ClassName(string param)
    {
        // Constructor implementation
    }
}
```

### Interface Documentation

```csharp
/// <summary>
/// Defines the contract for [interface purpose].
/// </summary>
/// <remarks>
/// Implementations of this interface should [requirements/expectations].
/// </remarks>
public interface IInterfaceName
{
    /// <summary>
    /// [Method description].
    /// </summary>
    /// <param name="param">Parameter description.</param>
    /// <returns>Description of return value.</returns>
    ReturnType MethodName(string param);
}
```

### Property Documentation

```csharp
/// <summary>
/// Gets or sets the user's full name.
/// </summary>
/// <value>
/// A string containing the user's full name.
/// </value>
/// <remarks>
/// This property is required and cannot be null or empty.
/// </remarks>
public string FullName { get; set; }

/// <summary>
/// Gets a value indicating whether the user is active.
/// </summary>
/// <value>
/// <c>true</c> if the user is active; otherwise, <c>false</c>.
/// </value>
public bool IsActive { get; }
```

### Event Documentation

```csharp
/// <summary>
/// Occurs when the value changes.
/// </summary>
/// <remarks>
/// Subscribe to this event to be notified when [specific condition].
/// </remarks>
public event EventHandler<ValueChangedEventArgs> ValueChanged;
```

### Async Method Documentation

```csharp
/// <summary>
/// Asynchronously retrieves data from the source.
/// </summary>
/// <param name="id">The identifier of the item to retrieve.</param>
/// <param name="cancellationToken">
/// A token to cancel the operation.
/// </param>
/// <returns>
/// A task that represents the asynchronous operation.
/// The task result contains the retrieved data.
/// </returns>
/// <exception cref="OperationCanceledException">
/// Thrown when the operation is canceled via the cancellation token.
/// </exception>
public async Task<DataModel> GetDataAsync(
    int id, 
    CancellationToken cancellationToken = default)
{
    // Implementation
}
```

---

## Project Documentation Structure

### Required Files

1. **README.md** - Project overview
2. **CHANGELOG.md** - Version history
3. **CONTRIBUTING.md** - Contribution guidelines
4. **LICENSE.md** - License information
5. **docs/** - Additional documentation
   - **API.md** - API reference
   - **ARCHITECTURE.md** - System architecture
   - **DEPLOYMENT.md** - Deployment guide

### README.md Structure

```markdown
# Project Name

Brief description of the .NET project.

[![Build Status](badge-url)](link)
[![NuGet Version](badge-url)](link)
[![License](badge-url)](link)

## Features

- Feature 1
- Feature 2
- Feature 3

## Requirements

- .NET 6.0 or later
- Additional dependencies

## Installation

### NuGet Package

```powershell
Install-Package PackageName
```

Or via .NET CLI:

```bash
dotnet add package PackageName
```

### Build from Source

```bash
git clone https://github.com/user/repo.git
cd repo
dotnet restore
dotnet build
```

## Quick Start

```csharp
using NamespaceName;

var service = new ServiceName();
var result = await service.ProcessAsync();
```

## Configuration

### appsettings.json

```json
{
  "ServiceSettings": {
    "Option1": "value",
    "Option2": true
  }
}
```

### Environment Variables

- `VAR_NAME` - Description

## Usage Examples

### Example 1: Basic Usage

```csharp
// Example code
```

### Example 2: Advanced Usage

```csharp
// Example code
```

## API Documentation

API documentation is generated using DocFX/Sandcastle.
View online at: [link]

Or generate locally:

```bash
dotnet tool restore
dotnet docfx docs/docfx.json
```

## Development

### Prerequisites

- Visual Studio 2022 or later / JetBrains Rider
- .NET 6.0 SDK

### Building

```bash
dotnet build
```

### Testing

```bash
dotnet test
```

### Code Style

This project follows:
- C# Coding Conventions
- .NET Framework Design Guidelines
- EditorConfig settings included

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

Licensed under [License Name]. See [LICENSE.md](LICENSE.md) for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md)
```

### Solution Structure Documentation

```markdown
# Solution Structure

## Projects

### ProjectName.Core

Core business logic and domain models.

- `Models/` - Domain models
- `Interfaces/` - Service interfaces
- `Services/` - Business logic implementation

### ProjectName.Api

Web API project.

- `Controllers/` - API controllers
- `Middleware/` - Custom middleware
- `Filters/` - Action filters

### ProjectName.Tests

Unit and integration tests.

- `Unit/` - Unit tests
- `Integration/` - Integration tests
- `Fixtures/` - Test fixtures
```

---

## Documentation Generation Tools

### DocFX (Recommended)

```bash
# Install DocFX
dotnet tool install -g docfx

# Initialize DocFX
docfx init -q

# Build documentation
docfx docs/docfx.json --serve
```

**docfx.json Configuration:**

```json
{
  "metadata": [
    {
      "src": [
        {
          "src": "../src",
          "files": [
            "**/*.csproj"
          ]
        }
      ],
      "dest": "api"
    }
  ],
  "build": {
    "content": [
      {
        "files": [
          "api/**.yml",
          "api/index.md"
        ]
      },
      {
        "files": [
          "articles/**.md",
          "toc.yml",
          "*.md"
        ]
      }
    ],
    "dest": "_site"
  }
}
```

### Sandcastle Help File Builder

Alternative for generating compiled help files (.chm).

---

## XML Documentation File

### Enable XML Documentation

**In .csproj:**

```xml
<PropertyGroup>
  <DocumentationFile>bin\$(Configuration)\$(TargetFramework)\$(AssemblyName).xml</DocumentationFile>
  <GenerateDocumentationFile>true</GenerateDocumentationFile>
  <NoWarn>$(NoWarn);1591</NoWarn> <!-- Suppress missing XML comment warnings -->
</PropertyGroup>
```

### XML Tags Reference

#### Essential Tags

- `<summary>` - Brief description
- `<remarks>` - Detailed explanation
- `<param>` - Parameter description
- `<returns>` - Return value description
- `<exception>` - Exception thrown
- `<example>` - Usage example
- `<code>` - Code sample
- `<see>` / `<seealso>` - Cross-references
- `<value>` - Property value description
- `<para>` - Paragraph within other tags
- `<c>` - Inline code
- `<list>` - Lists

#### Advanced Tags

```csharp
/// <summary>
/// Complex method with various documentation elements.
/// </summary>
/// <typeparam name="T">The type of items to process.</typeparam>
/// <param name="items">
/// The collection of items.
/// <list type="bullet">
/// <item><description>Must not be null</description></item>
/// <item><description>Must not be empty</description></item>
/// </list>
/// </param>
/// <returns>
/// The processed result as <see cref="ProcessResult{T}"/>.
/// </returns>
/// <exception cref="ArgumentNullException">
/// Thrown when <paramref name="items"/> is null.
/// </exception>
/// <seealso cref="RelatedClass"/>
public ProcessResult<T> Process<T>(IEnumerable<T> items)
{
    // Implementation
}
```

---

## Code Comments

### Inline Comments

```csharp
// Single-line comment for explaining the next line

// Multi-line comment explaining
// a more complex block of code
// across several lines

/* Block comment for
   multiple lines of explanation */

// TODO: Future improvement needed
// HACK: Temporary workaround, fix later
// NOTE: Important information
```

### Comment Best Practices

**DO:**
- Explain WHY, not WHAT
- Document non-obvious business rules
- Explain complex algorithms
- Note performance considerations
- Mark incomplete implementations (TODO, HACK)

**DON'T:**
- State the obvious
- Leave commented-out code
- Use comments to disable warnings
- Repeat what the code clearly shows

---

## Special Documentation Scenarios

### Generic Types

```csharp
/// <summary>
/// Represents a generic repository for entities of type <typeparamref name="TEntity"/>.
/// </summary>
/// <typeparam name="TEntity">
/// The type of entity. Must implement <see cref="IEntity"/>.
/// </typeparam>
public class Repository<TEntity> where TEntity : IEntity
{
    /// <summary>
    /// Gets an entity by its identifier.
    /// </summary>
    /// <param name="id">The entity identifier.</param>
    /// <returns>
    /// The entity of type <typeparamref name="TEntity"/> if found; otherwise, null.
    /// </returns>
    public TEntity GetById(int id)
    {
        // Implementation
    }
}
```

### Extension Methods

```csharp
/// <summary>
/// Provides extension methods for <see cref="string"/>.
/// </summary>
public static class StringExtensions
{
    /// <summary>
    /// Determines whether the string is null or empty.
    /// </summary>
    /// <param name="value">The string to check.</param>
    /// <returns>
    /// <c>true</c> if the string is null or empty; otherwise, <c>false</c>.
    /// </returns>
    /// <example>
    /// <code>
    /// string text = "hello";
    /// bool isEmpty = text.IsNullOrEmpty(); // Returns false
    /// </code>
    /// </example>
    public static bool IsNullOrEmpty(this string value)
    {
        return string.IsNullOrEmpty(value);
    }
}
```

### Nullable Reference Types

```csharp
/// <summary>
/// Processes the input value.
/// </summary>
/// <param name="value">
/// The input value. Can be null.
/// </param>
/// <returns>
/// The processed result, or null if input was null.
/// </returns>
public string? Process(string? value)
{
    // Implementation
}
```

---

## API Documentation Structure

### Controller Documentation

```csharp
/// <summary>
/// API controller for managing users.
/// </summary>
/// <remarks>
/// This controller provides endpoints for CRUD operations on users.
/// All endpoints require authentication.
/// </remarks>
[ApiController]
[Route("api/[controller]")]
[Authorize]
public class UsersController : ControllerBase
{
    /// <summary>
    /// Gets a user by ID.
    /// </summary>
    /// <param name="id">The user identifier.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>
    /// Returns the user if found.
    /// </returns>
    /// <response code="200">User found and returned.</response>
    /// <response code="404">User not found.</response>
    /// <response code="401">Unauthorized access.</response>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(UserDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<UserDto>> GetUser(
        int id,
        CancellationToken cancellationToken)
    {
        // Implementation
    }
}
```

---

## Documentation Maintenance

### Maintenance Schedule

1. **On Every Commit**: Update relevant XML documentation
2. **Weekly**: Review TODO comments, update TODO.md
3. **Sprint End**: Update README.md, documentation site
4. **Release**: Update CHANGELOG.md, regenerate documentation

### Documentation Checklist

- [ ] All public APIs have XML documentation
- [ ] All parameters documented
- [ ] Return values documented
- [ ] Exceptions documented
- [ ] Examples provided for complex APIs
- [ ] README.md is current
- [ ] CHANGELOG.md updated
- [ ] API documentation generated successfully
- [ ] No documentation warnings in build

---

## AI Agent Guidelines

**For AI Agents Maintaining Documentation:**

1. **Use XML Documentation** - Always use XML comments for code
2. **Follow .NET Conventions** - Match Microsoft's style
3. **Be IntelliSense-Friendly** - Summaries should be concise
4. **Include Examples** - Especially for complex APIs
5. **Document Exceptions** - All thrown exceptions
6. **Type References** - Use `<see cref=""/>` for cross-references
7. **Async Patterns** - Document cancellation tokens
8. **Nullable Annotations** - Be clear about nullability

**Priority Order:**
1. XML documentation comments (public APIs)
2. README.md
3. codebase_structure.md
4. API.md
5. CHANGELOG.md

---

**Last Updated:** 2025-10-12
**Version:** 1.0
