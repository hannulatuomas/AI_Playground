# Import/Export Guide

## Overview

LocalAPI provides a modular and extensible import/export system that allows you to transfer data between LocalAPI and other tools. The system supports multiple formats and is designed to be easily extended with new formats.

## Supported Formats

### Current Formats

1. **JSON** - LocalAPI native format
   - Full-featured with collections, requests, environments, and variables
   - Human-readable and editable
   - Supports prettified output

2. **cURL** - Command-line format
   - Import cURL commands from documentation or browser dev tools
   - Export requests as executable shell scripts
   - Supports multi-line format with backslashes

### Future Formats (Extensible)

The architecture supports adding:
- Postman collections
- Insomnia workspaces
- OpenAPI/Swagger specifications
- HAR (HTTP Archive) files
- And more...

## Architecture

### Modular Design

```
ImportExportService (Registry)
    ├── JsonImporterExporter
    ├── CurlImporterExporter
    └── [Future handlers...]
```

### Key Components

1. **Importer Interface** - Defines how to import content
2. **Exporter Interface** - Defines how to export data
3. **ImportExportService** - Registry that manages handlers
4. **IPC Layer** - Bridges main and renderer processes
5. **UI Component** - User-friendly dialog for import/export

## Usage

### Importing Data

#### From UI

1. Open Import/Export dialog
2. Select "Import" tab
3. Choose format (or let auto-detection handle it)
4. Paste content or upload file
5. Configure options (environments, variables)
6. Click "Import"

#### Programmatically

```typescript
// Auto-detect format
const result = await window.electronAPI.importExport.import(content);

// Specify format
const result = await window.electronAPI.importExport.import(
  content,
  'json',
  { includeEnvironments: true }
);

// Check result
if (result.success) {
  console.log(`Imported ${result.collections.length} collections`);
} else {
  console.error(result.errors);
}
```

### Exporting Data

#### From UI

1. Select collections or requests
2. Open Import/Export dialog
3. Select "Export" tab
4. Choose format
5. Configure options (prettify, include environments)
6. Click "Export"
7. Copy to clipboard or download file

#### Programmatically

```typescript
// Export collections
const result = await window.electronAPI.importExport.exportCollections(
  ['col-1', 'col-2'],
  'json',
  { prettify: true }
);

// Export single request
const result = await window.electronAPI.importExport.exportRequest(
  'req-1',
  'curl'
);

// Export multiple requests
const result = await window.electronAPI.importExport.exportRequests(
  ['req-1', 'req-2'],
  'curl'
);
```

## JSON Format

### Structure

```json
{
  "version": "1.0.0",
  "exportedAt": "2025-01-23T12:00:00.000Z",
  "collections": [
    {
      "id": "col-1",
      "name": "My API",
      "description": "API endpoints",
      "folders": [],
      "requests": [
        {
          "id": "req-1",
          "name": "Get Users",
          "protocol": "REST",
          "method": "GET",
          "url": "https://api.example.com/users",
          "headers": [
            {
              "key": "Authorization",
              "value": "Bearer {{token}}",
              "enabled": true
            }
          ],
          "queryParams": [
            {
              "key": "page",
              "value": "1",
              "enabled": true
            }
          ],
          "body": {
            "type": "json",
            "content": "{}"
          }
        }
      ]
    }
  ],
  "environments": [],
  "variables": []
}
```

### Features

- **Full Data Preservation** - All request details preserved
- **Variable Support** - Includes environment and collection variables
- **Nested Collections** - Supports folder hierarchy
- **Metadata** - Timestamps and version information

### Import Options

```typescript
{
  includeEnvironments: boolean,  // Import environment data
  includeVariables: boolean,     // Import variables
  prettify: boolean              // Format JSON output
}
```

## cURL Format

### Syntax

```bash
# Simple GET request
curl -X GET 'https://api.example.com/users'

# POST with headers and body
curl -X POST 'https://api.example.com/users' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer token123' \
  -d '{"name":"John Doe","email":"john@example.com"}'

# With query parameters
curl 'https://api.example.com/users?page=1&limit=10'
```

### Supported Features

**Import:**
- HTTP methods (-X, --request)
- Headers (-H, --header)
- Request body (-d, --data, --data-raw)
- Query parameters (in URL)
- Multi-line commands (backslash continuation)
- Multiple commands (one per line)

**Export:**
- All HTTP methods
- Headers
- Query parameters
- Request body
- Multi-line format with backslashes
- Comments with request names

### Limitations

- Authentication is exported as headers (not separate auth config)
- Binary data not supported
- File uploads not supported
- Some advanced cURL options not supported

## API Reference

### ImportExportService

#### Methods

```typescript
// Get supported formats
getSupportedImportFormats(): ImportExportFormat[]
getSupportedExportFormats(): ImportExportFormat[]

// Auto-detect format
detectFormat(content: string): ImportExportFormat | null

// Import
import(
  content: string,
  format?: ImportExportFormat,
  options?: ImportExportOptions
): Promise<ImportResult>

// Export
exportCollections(
  collections: Collection[],
  format: ImportExportFormat,
  options?: ImportExportOptions
): Promise<ExportResult>

exportRequest(
  request: Request,
  format: ImportExportFormat,
  options?: ImportExportOptions
): Promise<ExportResult>

exportRequests(
  requests: Request[],
  format: ImportExportFormat,
  options?: ImportExportOptions
): Promise<ExportResult>

// Utilities
getHandlerInfo(format: ImportExportFormat): HandlerInfo | null
getExample(format: ImportExportFormat): string | null
```

### Types

```typescript
interface ImportResult {
  success: boolean;
  collections?: Collection[];
  requests?: Request[];
  environments?: any[];
  variables?: any[];
  errors?: string[];
  warnings?: string[];
  metadata?: {
    format: ImportExportFormat;
    itemCount: number;
    importedAt: Date;
  };
}

interface ExportResult {
  success: boolean;
  data?: string;
  format: ImportExportFormat;
  errors?: string[];
  metadata?: {
    exportedAt: Date;
    itemCount: number;
    size: number;
  };
}
```

## Adding New Formats

### Step 1: Create Handler Class

```typescript
import type { ImporterExporter } from '../types/import-export';

export class MyFormatHandler implements ImporterExporter {
  readonly format = 'myformat';
  readonly name = 'My Format';
  readonly description = 'Description of my format';
  readonly fileExtensions = ['.myext'];

  canImport(content: string): boolean {
    // Check if content is valid for this format
    return content.startsWith('MYFORMAT');
  }

  async import(content: string, options?: ImportExportOptions): Promise<ImportResult> {
    // Parse content and return collections/requests
  }

  async exportCollections(collections: Collection[], options?: ImportExportOptions): Promise<ExportResult> {
    // Convert collections to format
  }

  async exportRequest(request: Request, options?: ImportExportOptions): Promise<ExportResult> {
    // Convert single request to format
  }

  async exportRequests(requests: Request[], options?: ImportExportOptions): Promise<ExportResult> {
    // Convert multiple requests to format
  }

  getExample?(): string {
    // Return example content
  }
}
```

### Step 2: Register Handler

```typescript
// In ImportExportService constructor or initialization
const myHandler = new MyFormatHandler();
importExportService.registerHandler('myformat', myHandler, myHandler);
```

### Step 3: Use It

```typescript
// Import
const result = await importExportService.import(content, 'myformat');

// Export
const result = await importExportService.exportRequest(request, 'myformat');
```

## Best Practices

### When Importing

1. **Validate First** - Use `detectFormat()` to verify content
2. **Handle Errors** - Check `result.success` and `result.errors`
3. **Review Warnings** - Check `result.warnings` for non-critical issues
4. **Backup Data** - Export current data before importing
5. **Test Small** - Import a small sample first

### When Exporting

1. **Choose Right Format** - JSON for full features, cURL for sharing
2. **Prettify JSON** - Makes it human-readable and editable
3. **Include Context** - Export environments/variables when needed
4. **Version Control** - Export to files for Git tracking
5. **Document Changes** - Add comments or descriptions

### For Developers

1. **Implement Both** - Provide import and export for symmetry
2. **Validate Input** - Check format before processing
3. **Handle Errors** - Return meaningful error messages
4. **Preserve Data** - Don't lose information in conversion
5. **Test Thoroughly** - Test round-trip (export → import → export)

## Examples

### Import cURL from Browser DevTools

1. Open browser DevTools (F12)
2. Go to Network tab
3. Right-click on request → Copy → Copy as cURL
4. Paste into LocalAPI import dialog
5. Import creates a new request

### Export Collection for Documentation

```typescript
// Export as JSON for documentation
const result = await window.electronAPI.importExport.exportCollections(
  ['api-collection'],
  'json',
  { prettify: true, includeEnvironments: false }
);

// Save to file
const blob = new Blob([result.data], { type: 'application/json' });
// ... download logic
```

### Share Request as cURL

```typescript
// Export single request as cURL
const result = await window.electronAPI.importExport.exportRequest(
  'req-123',
  'curl'
);

// Copy to clipboard
navigator.clipboard.writeText(result.data);
```

### Batch Import from File

```typescript
// Read file
const fileContent = await file.text();

// Auto-detect and import
const result = await window.electronAPI.importExport.import(fileContent);

if (result.success) {
  // Save to database
  for (const collection of result.collections) {
    await window.electronAPI.collections.create(collection);
  }
}
```

## Troubleshooting

### Import Issues

**Problem:** "Unable to detect format"
- **Solution:** Specify format explicitly or check content validity

**Problem:** "No valid requests found"
- **Solution:** Verify content structure matches expected format

**Problem:** "Import succeeded but no data"
- **Solution:** Check if content has empty collections/requests arrays

### Export Issues

**Problem:** "No collections or requests selected"
- **Solution:** Select items before opening export dialog

**Problem:** "Export data is empty"
- **Solution:** Check if selected items exist in database

**Problem:** "cURL command doesn't work"
- **Solution:** Check for special characters, use proper escaping

## Performance

### Import Performance

- **JSON**: Fast, direct parsing
- **cURL**: Moderate, regex parsing
- **Large Files**: Process in chunks for files >10MB

### Export Performance

- **JSON**: Fast, direct serialization
- **cURL**: Fast, string concatenation
- **Large Collections**: May take a few seconds for 1000+ requests

## Security

### Import Security

- **Validate Input**: All imports are validated before processing
- **Sanitize Data**: Special characters are escaped
- **No Code Execution**: Imports don't execute scripts
- **Secrets Handling**: Secrets are not imported by default

### Export Security

- **Sensitive Data**: Review exported data before sharing
- **Secrets**: Exclude secrets from exports when sharing
- **Variables**: Consider excluding environment-specific variables
- **URLs**: Check for sensitive information in URLs

## Future Enhancements

### Planned Features

1. **Postman Import/Export** - Full Postman collection support
2. **OpenAPI Import** - Generate requests from OpenAPI specs
3. **HAR Import** - Import from browser HAR files
4. **Insomnia Support** - Import/export Insomnia workspaces
5. **Batch Operations** - Import/export multiple files at once
6. **Transformation** - Convert between formats (e.g., Postman → LocalAPI)
7. **Validation** - Schema validation before import
8. **Diff View** - Compare before/after import

### Contributing

To add a new format:

1. Create handler class implementing `Importer` and/or `Exporter`
2. Add tests for the handler
3. Register in `ImportExportService`
4. Update documentation
5. Submit PR

## Related Documentation

- [API Documentation](API.md)
- [User Guide](USER_GUIDE.md)
- [Extending Guide](EXTENDING_GUIDE.md)
- [Codebase Structure](CODEBASE_STRUCTURE.md)
