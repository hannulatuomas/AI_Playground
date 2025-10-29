
# C#/.NET/ASP.NET User Preferences

## Framework and Library Preferences

### Target Framework
```yaml
# Preferred .NET version
target_framework: net8.0

# Alternative options: net7.0, net6.0, netstandard2.1
# For legacy projects: net48, net472
```

### Web Framework
```yaml
# Preferred web framework
web_framework: aspnet_core

# Options:
# - aspnet_core: ASP.NET Core (recommended)
# - aspnet_mvc: ASP.NET MVC (legacy)
# - blazor_server: Blazor Server
# - blazor_wasm: Blazor WebAssembly
# - minimal_api: Minimal APIs (ASP.NET Core 6+)
```

### ORM/Data Access
```yaml
# Preferred data access technology
orm: entity_framework_core

# Options:
# - entity_framework_core: EF Core (recommended)
# - dapper: Dapper (lightweight)
# - nhibernate: NHibernate
# - ado_net: Raw ADO.NET
```

### Testing Framework
```yaml
# Unit testing framework
test_framework: xunit

# Options:
# - xunit: xUnit.net (modern, recommended)
# - nunit: NUnit (traditional)
# - mstest: MSTest (Visual Studio integrated)

# Mocking library
mocking_library: moq

# Options:
# - moq: Moq (most popular)
# - nsubstitute: NSubstitute (fluent syntax)
# - fakeiteasy: FakeItEasy
```

### Logging
```yaml
# Logging framework
logging: serilog

# Options:
# - serilog: Serilog (structured logging)
# - nlog: NLog (traditional)
# - log4net: log4net (Java-like)
# - microsoft_logging: Microsoft.Extensions.Logging (built-in)
```

### Dependency Injection
```yaml
# DI Container
di_container: microsoft_di

# Options:
# - microsoft_di: Microsoft.Extensions.DependencyInjection (built-in)
# - autofac: Autofac (feature-rich)
# - ninject: Ninject (simple)
```

## Code Style Preferences

### Naming Conventions
```yaml
# Class naming style
class_naming: PascalCase

# Method naming style
method_naming: PascalCase

# Private field naming
private_field_prefix: underscore  # _fieldName

# Options:
# - underscore: _fieldName
# - none: fieldName
# - this: this.fieldName
```

### Indentation and Formatting
```yaml
# Indentation
indent_style: spaces
indent_size: 4

# Line length
max_line_length: 120

# Brace style
brace_style: same_line  # Opening brace on same line as declaration

# Options:
# - same_line: public void Method() {
# - next_line: public void Method()
#              {
# - next_line_shifted: public void Method()
#                          {

# Blank lines
blank_lines_between_members: 1
blank_lines_around_namespaces: 1
```

### Using Directives
```yaml
# Using statements organization
using_directives_order:
  - system_first  # System.* namespaces first
  - alphabetical  # Then alphabetically

# Prefer file-scoped namespaces (C# 10+)
file_scoped_namespaces: true

# Options:
# - true: namespace MyApp;
# - false: namespace MyApp { }
```

### var vs Explicit Types
```yaml
# Use var keyword
var_preference: prefer_var_when_obvious

# Options:
# - prefer_var_when_obvious: var list = new List<int>();
# - prefer_var_always: var i = 0;
# - prefer_explicit: List<int> list = new List<int>();
```

### Expression Preferences
```yaml
# Prefer expression-bodied members
expression_bodied_members: true

# Example when true:
# public int Count => items.Count;
# public void Clear() => items.Clear();

# Example when false:
# public int Count { get { return items.Count; } }

# Pattern matching preferences
pattern_matching: prefer_pattern_matching

# Null checking
null_checking: null_coalescing_operator  # value ?? defaultValue

# Options:
# - null_coalescing_operator: value ?? defaultValue
# - null_conditional_operator: value?.Property
# - is_null_check: if (value is null)
# - equality_check: if (value == null)
```

## Design Pattern Preferences

### Architectural Patterns
```yaml
# Preferred architecture
architecture: clean_architecture

# Options:
# - clean_architecture: Clean Architecture (DDD-inspired)
# - onion_architecture: Onion Architecture
# - layered_architecture: Traditional N-tier
# - vertical_slice: Vertical Slice Architecture
# - cqrs: CQRS (Command Query Responsibility Segregation)
```

### Project Organization
```yaml
# Folder structure
folder_structure: feature_folders

# Options:
# - feature_folders: Organize by feature
# - layer_folders: Organize by layer (Controllers, Services, etc.)
# - mixed: Hybrid approach

# Example feature_folders:
# /Features
#   /Users
#     - UsersController.cs
#     - UserService.cs
#     - User.cs
#   /Orders
#     - OrdersController.cs
#     - OrderService.cs
#     - Order.cs

# Example layer_folders:
# /Controllers
# /Services
# /Models
# /Repositories
```

### Dependency Management
```yaml
# Dependency injection style
di_registration: extension_methods

# Options:
# - extension_methods: Use extension methods in separate class
# - startup_inline: Register in Startup/Program.cs
# - modules: Use module/registry pattern

# Constructor injection
prefer_constructor_injection: true

# Interface naming
interface_prefix: I  # IUserService

# Use interfaces for services
use_interfaces_for_services: true
```

## ASP.NET Core Preferences

### API Style
```yaml
# API routing style
api_routing: attribute_routing

# Options:
# - attribute_routing: [Route("api/[controller]")]
# - conventional_routing: app.MapControllers()
# - minimal_apis: app.MapGet("/users", ...)

# API versioning
api_versioning: url_segment

# Options:
# - url_segment: /api/v1/users
# - query_string: /api/users?api-version=1.0
# - header: API-Version: 1.0
# - media_type: Accept: application/json;v=1.0
```

### Authentication
```yaml
# Authentication scheme
authentication: jwt_bearer

# Options:
# - jwt_bearer: JWT Bearer tokens
# - cookie: Cookie-based authentication
# - identity_server: IdentityServer4/Duende
# - azure_ad: Azure Active Directory
# - oauth: OAuth 2.0
```

### API Documentation
```yaml
# API documentation tool
api_docs: swagger

# Options:
# - swagger: Swagger/OpenAPI (Swashbuckle)
# - nswag: NSwag
# - none: No auto-documentation

# XML comments for Swagger
include_xml_comments: true
```

### Error Handling
```yaml
# Error handling middleware
error_handling: exception_middleware

# Options:
# - exception_middleware: Global exception middleware
# - problem_details: ProblemDetails (RFC 7807)
# - custom_filter: Custom exception filter
```

## Tooling Preferences

### Code Analysis
```yaml
# Static analysis tools
code_analysis: roslyn_analyzers

# Enable StyleCop analyzers
stylecop_analyzers: true

# Enable code quality rules
enable_ca_rules: true

# Treat warnings as errors
warnings_as_errors: false  # Set to true for stricter builds
```

### Code Formatter
```yaml
# Code formatter
formatter: built_in

# Options:
# - built_in: Visual Studio/Rider built-in
# - csharpier: CSharpier
# - dotnet_format: dotnet format tool

# Format on save
format_on_save: true
```

### Build Tools
```yaml
# Build system
build_system: msbuild

# Options:
# - msbuild: MSBuild (default)
# - dotnet_cli: dotnet CLI
# - cake: Cake build system
# - nuke: NUKE build system
```

### Package Management
```yaml
# Package manager
package_manager: nuget

# Package restore on build
restore_on_build: true

# Central package management (NuGet 6.2+)
central_package_management: false

# PackageReference vs packages.config
package_reference_format: true  # Use PackageReference
```

## Project Structure Preferences

### Solution Organization
```yaml
# Solution structure
solution_structure: src_tests_docs

# Example:
# MySolution.sln
# /src
#   /MyProject.Api
#   /MyProject.Core
#   /MyProject.Infrastructure
# /tests
#   /MyProject.UnitTests
#   /MyProject.IntegrationTests
# /docs
```

### Project References
```yaml
# Project dependency direction
dependency_direction: inward

# Core dependencies:
# Api -> Application -> Domain
# Infrastructure -> Domain
# (Domain has no dependencies)
```

### Configuration Management
```yaml
# Configuration files
configuration_files: appsettings_json

# Options:
# - appsettings_json: appsettings.json + environment variants
# - user_secrets: User Secrets for development
# - environment_variables: Environment variables
# - azure_key_vault: Azure Key Vault

# Environment-specific configs
environment_configs: true  # appsettings.Development.json, etc.
```

## Technology Stack Choices

### Frontend Integration
```yaml
# Frontend choice for full-stack apps
frontend_choice: react

# Options:
# - react: React
# - angular: Angular
# - vue: Vue.js
# - blazor: Blazor
# - razor_pages: Razor Pages
# - mvc_views: MVC Views
```

### Database
```yaml
# Preferred database
database: postgresql

# Options:
# - postgresql: PostgreSQL
# - sqlserver: SQL Server
# - mysql: MySQL
# - sqlite: SQLite (dev/testing)
# - mongodb: MongoDB (NoSQL)
# - cosmosdb: Azure Cosmos DB
```

### Caching
```yaml
# Caching strategy
caching: redis

# Options:
# - redis: Redis
# - memory_cache: In-memory cache
# - distributed_cache: IDistributedCache abstraction
# - none: No caching
```

### Message Queue
```yaml
# Message queue/service bus
message_queue: rabbitmq

# Options:
# - rabbitmq: RabbitMQ
# - azure_service_bus: Azure Service Bus
# - kafka: Apache Kafka
# - mass_transit: MassTransit (abstraction)
# - none: No message queue
```

### Cloud Platform
```yaml
# Preferred cloud platform
cloud_platform: azure

# Options:
# - azure: Microsoft Azure
# - aws: Amazon Web Services
# - gcp: Google Cloud Platform
# - on_premise: On-premise deployment
# - agnostic: Cloud-agnostic
```

## Testing Preferences

### Test Structure
```yaml
# Test project organization
test_organization: mirror_source

# Options:
# - mirror_source: Mirror source project structure
# - flat: Flat structure with descriptive names
```

### Test Naming
```yaml
# Test method naming convention
test_naming: method_scenario_expected

# Example: GetUser_ValidId_ReturnsUser()

# Options:
# - method_scenario_expected: MethodName_Scenario_ExpectedBehavior
# - given_when_then: GivenValidId_WhenGetUser_ThenReturnsUser
# - should_style: ShouldReturnUser_WhenGivenValidId
```

### Test Coverage
```yaml
# Minimum code coverage target
min_coverage: 80  # percentage

# Coverage tool
coverage_tool: coverlet

# Options:
# - coverlet: Coverlet
# - dotcover: JetBrains dotCover
# - visual_studio: Visual Studio Code Coverage
```

### Integration Tests
```yaml
# Integration test framework
integration_test_framework: webapplicationfactory

# Options:
# - webapplicationfactory: WebApplicationFactory (ASP.NET Core)
# - testcontainers: Testcontainers for external dependencies
# - in_memory_db: In-memory database
```

## Documentation Preferences

### XML Documentation
```yaml
# Generate XML documentation
generate_xml_docs: true

# Documentation level
documentation_level: public_members_only

# Options:
# - all_members: Document all members
# - public_members_only: Only public members
# - public_and_protected: Public and protected members
# - minimal: Only public APIs
```

### README Structure
```yaml
# README.md sections
readme_sections:
  - overview
  - getting_started
  - architecture
  - configuration
  - development
  - testing
  - deployment
  - contributing
  - license
```

### API Documentation
```yaml
# Include examples in API docs
include_examples: true

# Include request/response schemas
include_schemas: true

# Include authentication docs
include_auth_docs: true
```

## Additional Preferences

### Async/Await
```yaml
# Async suffix convention
async_suffix: true  # GetUserAsync vs GetUser

# Use ConfigureAwait
configure_await_usage: library_code_only

# Options:
# - always: Always use ConfigureAwait(false)
# - library_code_only: Only in library code
# - never: Never use (application code)
```

### Nullable Reference Types
```yaml
# Enable nullable reference types (C# 8.0+)
nullable_reference_types: enable

# Options:
# - enable: <Nullable>enable</Nullable>
# - disable: <Nullable>disable</Nullable>
# - warnings: <Nullable>warnings</Nullable>
```

### Language Version
```yaml
# C# language version
language_version: latest

# Options:
# - latest: Use latest C# features
# - latestmajor: Latest major version
# - 11.0, 10.0, 9.0, etc.: Specific version
# - default: Default for target framework
```

### Code Generation
```yaml
# Use source generators
use_source_generators: true

# Use T4 templates
use_t4_templates: false

# Use code scaffolding
use_scaffolding: true
```
