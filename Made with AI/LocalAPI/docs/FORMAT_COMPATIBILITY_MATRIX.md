# Format Compatibility Matrix

## Overview

LocalAPI supports 15+ import and export formats for maximum compatibility with other API tools and standards. This matrix shows what features are supported for each format.

## Import Formats

### Supported Formats

| Format | Version | Status | Collections | Requests | Auth | Scripts | Variables | Environments |
|--------|---------|--------|-------------|----------|------|---------|-----------|--------------|
| **Postman** | v2.1 | ✅ Full | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Insomnia** | v4 | ✅ Full | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **OpenAPI** | 3.0, 3.1 | ✅ Full | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **Swagger** | 2.0 | ✅ Full | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **HAR** | 1.2 | ✅ Full | ✅ | ✅ | ⚠️ Partial | ❌ | ❌ | ❌ |
| **cURL** | - | ✅ Full | ⚠️ Single | ✅ | ✅ | ❌ | ❌ | ❌ |
| **RAML** | 1.0 | ✅ Full | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **GraphQL** | - | ✅ Full | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| **AsyncAPI** | 2.0, 3.0 | ✅ Full | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **WSDL** | 1.1, 2.0 | ✅ Full | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **WADL** | - | ✅ Full | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **SoapUI** | - | ✅ Full | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Protobuf** | 3 | ✅ Full | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **API Gateway** | AWS | ✅ Full | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **Paw** | - | ⚠️ Partial | ✅ | ✅ | ✅ | ⚠️ Limited | ✅ | ✅ |

**Legend:**
- ✅ Full: Complete support with all features
- ⚠️ Partial: Basic support, some features may be limited
- ❌ Not Supported: Feature not available in this format

## Export Formats

### Supported Formats

| Format | Version | Status | Collections | Requests | Auth | Scripts | Variables | Environments |
|--------|---------|--------|-------------|----------|------|---------|-----------|--------------|
| **Postman** | v2.1 | ✅ Full | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Insomnia** | v4 | ✅ Full | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **OpenAPI** | 3.0, 3.1 | ✅ Full | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **Swagger** | 2.0 | ✅ Full | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **HAR** | 1.2 | ✅ Full | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **cURL** | - | ✅ Full | ⚠️ Multiple | ✅ | ✅ | ❌ | ⚠️ Inline | ❌ |
| **Markdown** | - | ✅ Full | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **HTML** | 5 | ✅ Full | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **PDF** | - | ✅ Full | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CSV** | - | ✅ Full | ⚠️ Flat | ✅ | ⚠️ Basic | ❌ | ✅ | ❌ |
| **JSON** | - | ✅ Full | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **YAML** | - | ✅ Full | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

## Feature Support Details

### Postman v2.1

**Import:**
- ✅ Collections with nested folders
- ✅ All HTTP methods
- ✅ Headers, query params, body (all types)
- ✅ Authentication (all types)
- ✅ Pre-request scripts (converted to JavaScript)
- ✅ Test scripts (converted to JavaScript)
- ✅ Collection variables
- ✅ Environment variables
- ✅ Global variables
- ✅ Request descriptions
- ✅ Examples/responses

**Export:**
- ✅ Full collection structure
- ✅ All request types
- ✅ Scripts (converted from LocalAPI format)
- ✅ Variables (all scopes)
- ✅ Authentication settings
- ✅ Documentation

**Limitations:**
- Postman Cloud features not supported (monitors, mocks in cloud)
- Team collaboration features not exported

### Insomnia v4

**Import:**
- ✅ Workspaces
- ✅ Request groups (folders)
- ✅ All request types (REST, GraphQL, gRPC)
- ✅ Environments
- ✅ Template tags (converted to variables)
- ✅ Plugins (converted where possible)
- ✅ Request chaining
- ✅ Authentication (all types)

**Export:**
- ✅ Full workspace structure
- ✅ All request types
- ✅ Environments
- ✅ Variables
- ✅ Authentication

**Limitations:**
- Some plugins may not have LocalAPI equivalents
- Cloud sync features not supported

### OpenAPI 3.0/3.1

**Import:**
- ✅ Paths and operations
- ✅ Parameters (path, query, header, cookie)
- ✅ Request bodies (all content types)
- ✅ Responses with examples
- ✅ Security schemes
- ✅ Servers (as environments)
- ✅ Components (schemas, parameters, etc.)
- ✅ Tags (as folders)

**Export:**
- ✅ Complete OpenAPI specification
- ✅ All endpoints documented
- ✅ Request/response schemas
- ✅ Security definitions
- ✅ Examples from requests
- ✅ Server configurations

**Limitations:**
- Scripts not supported (OpenAPI is specification only)
- Dynamic behavior not captured

### Swagger 2.0

**Import:**
- ✅ Paths and operations
- ✅ Parameters
- ✅ Definitions (schemas)
- ✅ Security definitions
- ✅ Host and basePath
- ✅ Consumes/produces

**Export:**
- ✅ Complete Swagger specification
- ✅ All endpoints
- ✅ Definitions
- ✅ Security schemes

**Limitations:**
- Older format, some OpenAPI 3.0 features not available
- Scripts not supported

### HAR (HTTP Archive)

**Import:**
- ✅ Requests with full details
- ✅ Headers
- ✅ Query parameters
- ✅ Request/response bodies
- ✅ Timing information
- ⚠️ Basic auth only (other auth types not in HAR)

**Export:**
- ✅ Request/response pairs
- ✅ Headers
- ✅ Timing data
- ✅ Content

**Limitations:**
- No collection structure
- No scripts or variables
- Limited authentication support

### cURL

**Import:**
- ✅ Single request per command
- ✅ Method, URL, headers
- ✅ Request body
- ✅ Basic auth
- ✅ File uploads

**Export:**
- ✅ Individual requests as cURL commands
- ✅ All headers
- ✅ Authentication
- ⚠️ Variables inlined (not as shell variables)

**Limitations:**
- No collection structure
- No scripts
- Variables are substituted, not preserved

### RAML 1.0

**Import:**
- ✅ Resources and methods
- ✅ URI parameters
- ✅ Query parameters
- ✅ Headers
- ✅ Request/response bodies
- ✅ Security schemes
- ✅ Traits and resource types
- ✅ Data types

**Export:**
- Not currently supported

**Limitations:**
- Import only
- Some RAML-specific features may not translate perfectly

### GraphQL

**Import:**
- ✅ Schema introspection
- ✅ Queries
- ✅ Mutations
- ✅ Subscriptions
- ✅ Variables
- ✅ Fragments

**Export:**
- ✅ GraphQL queries
- ✅ Schema documentation

**Limitations:**
- Schema must be accessible for introspection

### AsyncAPI 2.0/3.0

**Import:**
- ✅ Channels
- ✅ Messages
- ✅ Operations (publish/subscribe)
- ✅ Servers
- ✅ Security schemes
- ✅ Components

**Export:**
- Not currently supported

**Limitations:**
- Import only
- Async operations converted to appropriate LocalAPI request types

### WSDL 1.1/2.0

**Import:**
- ✅ Services and ports
- ✅ Operations
- ✅ Messages
- ✅ Types (XSD schemas)
- ✅ Bindings

**Export:**
- Not currently supported

**Limitations:**
- Import only
- SOAP operations converted to REST-like requests

### WADL

**Import:**
- ✅ Resources
- ✅ Methods
- ✅ Parameters
- ✅ Representations

**Export:**
- Not currently supported

**Limitations:**
- Import only
- Less common format

### SoapUI

**Import:**
- ✅ Projects
- ✅ Test suites
- ✅ Test cases
- ✅ Requests
- ✅ Assertions (converted to tests)
- ✅ Properties (converted to variables)

**Export:**
- Not currently supported

**Limitations:**
- Import only
- Some SoapUI-specific features may not translate

### Protocol Buffers (Protobuf)

**Import:**
- ✅ Service definitions
- ✅ RPC methods
- ✅ Message types

**Export:**
- Not currently supported

**Limitations:**
- Import only
- Requires .proto files

### AWS API Gateway

**Import:**
- ✅ REST APIs
- ✅ Resources and methods
- ✅ Integration settings
- ✅ Authorizers
- ✅ Models

**Export:**
- Not currently supported

**Limitations:**
- Import only
- AWS-specific features may not translate

## Request Type Support

### HTTP Methods

| Method | Import | Export | Notes |
|--------|--------|--------|-------|
| GET | ✅ All formats | ✅ All formats | Fully supported |
| POST | ✅ All formats | ✅ All formats | Fully supported |
| PUT | ✅ All formats | ✅ All formats | Fully supported |
| PATCH | ✅ All formats | ✅ All formats | Fully supported |
| DELETE | ✅ All formats | ✅ All formats | Fully supported |
| HEAD | ✅ All formats | ✅ All formats | Fully supported |
| OPTIONS | ✅ All formats | ✅ All formats | Fully supported |

### Body Types

| Type | Import | Export | Formats |
|------|--------|--------|---------|
| JSON | ✅ | ✅ | All |
| XML | ✅ | ✅ | All |
| Form Data | ✅ | ✅ | All |
| Form URL Encoded | ✅ | ✅ | All |
| Raw Text | ✅ | ✅ | All |
| Binary | ✅ | ✅ | Most |
| GraphQL | ✅ | ✅ | Postman, Insomnia, GraphQL |
| File Upload | ✅ | ⚠️ | Most (path only) |

### Authentication Types

| Type | Import | Export | Notes |
|------|--------|--------|-------|
| None | ✅ | ✅ | All formats |
| Basic | ✅ | ✅ | All formats |
| Bearer | ✅ | ✅ | All formats |
| API Key | ✅ | ✅ | Most formats |
| OAuth 1.0 | ✅ | ✅ | Postman, Insomnia |
| OAuth 2.0 | ✅ | ✅ | Postman, Insomnia, OpenAPI |
| Digest | ✅ | ✅ | Postman, Insomnia |
| AWS Signature | ✅ | ✅ | Postman, API Gateway |
| NTLM | ✅ | ✅ | Postman |

## Variable Support

### Variable Scopes

| Scope | Import From | Export To | Notes |
|-------|-------------|-----------|-------|
| Global | Postman, Insomnia | Postman, Insomnia, JSON | Fully supported |
| Environment | All formats | Most formats | Widely supported |
| Collection | Postman, SoapUI | Postman, JSON | Collection-specific |
| Request | Postman | Postman, JSON | Request-level only |

### Variable Syntax

| Format | Syntax | Import | Export |
|--------|--------|--------|--------|
| Postman | `{{variable}}` | ✅ | ✅ |
| Insomnia | `{{ _.variable }}` | ✅ Converted | ✅ Converted |
| OpenAPI | `{variable}` | ✅ | ✅ |
| LocalAPI | `{{variable}}` | N/A | ✅ |

## Script Support

### Script Types

| Type | Import From | Export To | Conversion |
|------|-------------|-----------|------------|
| Pre-request | Postman, SoapUI | Postman, JSON | ✅ Auto |
| Test/Assertion | Postman, SoapUI | Postman, JSON | ✅ Auto |
| Setup | SoapUI | JSON | ✅ Auto |
| Teardown | SoapUI | JSON | ✅ Auto |

### Script APIs

| API | Import | Export | Notes |
|-----|--------|--------|-------|
| Postman `pm.*` | ✅ Converted | ✅ Converted | Full conversion |
| Insomnia tags | ✅ Converted | ✅ Converted | To variables |
| SoapUI Groovy | ✅ Converted | ⚠️ Limited | To JavaScript |
| LocalAPI | N/A | ✅ | Native format |

## Best Practices

### Importing

1. **Choose the right format:**
   - Use native format (Postman/Insomnia) for full fidelity
   - Use OpenAPI/Swagger for API specifications
   - Use HAR for browser captures

2. **Prepare your data:**
   - Export from source tool in latest version
   - Include all dependencies (environments, variables)
   - Document any custom scripts

3. **Verify after import:**
   - Check collection structure
   - Test sample requests
   - Verify variables and environments
   - Review converted scripts

### Exporting

1. **Choose appropriate format:**
   - Postman/Insomnia for migration
   - OpenAPI for documentation
   - Markdown/HTML for sharing
   - JSON for backup

2. **Consider your audience:**
   - Developers: OpenAPI, Postman
   - Documentation: Markdown, HTML, PDF
   - Automation: JSON, YAML
   - Quick sharing: cURL

3. **Include necessary data:**
   - Select collections to export
   - Include environments if needed
   - Add documentation/descriptions
   - Consider security (don't export secrets)

## Troubleshooting

### Common Issues

**Issue: Import fails with "Unsupported format"**
- Verify file format and version
- Check file is valid JSON/YAML
- Try re-exporting from source tool

**Issue: Scripts don't work after import**
- Review script conversion
- Check API compatibility
- Update variable references

**Issue: Variables not substituting**
- Verify variable scope
- Check environment is active
- Ensure variable names match

**Issue: Authentication fails**
- Re-enter sensitive credentials
- Check auth type is supported
- Verify token/key format

## Future Format Support

### Planned

- ⏳ Paw (full support)
- ⏳ Thunder Client
- ⏳ REST Client (VS Code)
- ⏳ HTTPie
- ⏳ Bruno

### Under Consideration

- 🔍 Hoppscotch
- 🔍 Talend API Tester
- 🔍 Advanced REST Client
- 🔍 Katalon

## Conclusion

LocalAPI provides comprehensive import/export support for industry-standard formats, ensuring easy migration and integration with your existing tools and workflows. Most formats support full round-trip conversion, preserving your data, scripts, and configurations.

For format-specific details, see:
- [Import/Export Guide](IMPORT_EXPORT_GUIDE.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- [User Guide](USER_GUIDE.md)
