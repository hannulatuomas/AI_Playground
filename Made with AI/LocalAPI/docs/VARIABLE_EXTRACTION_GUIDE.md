# Visual Variable Extraction Guide

**Version:** 0.8.0  
**Last Updated:** October 23, 2025

Complete guide to using the Visual Variable Extraction feature in LocalAPI.

## Overview

Visual Variable Extraction allows you to easily extract values from API responses and save them as variables for use in subsequent requests. This feature supports multiple extraction methods and provides a complete workflow for managing variables.

## Features

### 1. Quick Variable Extraction

Extract variables directly from response body or headers with a single click.

**Supported Methods:**
- **JSONPath** - Extract from JSON responses using JSONPath expressions
- **XPath** - Extract from XML responses using XPath syntax
- **Header** - Extract values from response headers
- **Regex** - Extract using regular expression patterns

### 2. Click-to-Extract

Click on any value in the response viewer to quickly extract it as a variable.

**From JSON Responses:**
- Click on any value in the JSON response
- Automatically generates JSONPath expression
- Preview extracted value before saving

**From XML Responses:**
- Click on XML elements
- Automatically generates XPath expression
- Supports nested XML structures

**From Headers:**
- Click extract button next to any header
- Case-insensitive header matching
- Instant variable creation

### 3. Variable Preview Panel

View all your variables in one place with filtering and search capabilities.

**Features:**
- View variables by scope (Global, Environment, Collection)
- Search and filter variables
- Copy variable values
- Edit or delete variables
- View variable history

### 4. Auto-Extraction Rules

Create rules to automatically extract variables from responses.

**Rule Configuration:**
- Name and description
- Extraction method (JSONPath, XPath, Regex, Header)
- Source (Body or Headers)
- Variable name and scope
- Enable/disable toggle

**Rule Management:**
- Create, edit, and delete rules
- Test rules against current response
- Import/export rules as JSON
- Apply multiple rules at once

### 5. Variable Mapping Wizard

Extract multiple variables in a single operation.

**Batch Extraction:**
- Define multiple variable mappings
- Test all extractions at once
- Save successful extractions
- Skip failed extractions automatically

### 6. Variable History Tracking

Track all changes to variables over time.

**History Features:**
- View old and new values
- See extraction source
- Filter by variable name
- Search history entries
- Clear history (all or by variable)

## Usage Examples

### Example 1: Extract Authentication Token

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 3600
  }
}
```

**Steps:**
1. Click "Extract Variable" button in response viewer
2. Select extraction method: JSONPath
3. Enter path: `$.data.token`
4. Enter variable name: `authToken`
5. Select scope: Global
6. Click "Test Extraction" to preview
7. Click "Save Variable"

**Result:** Variable `authToken` is now available for use in other requests as `{{authToken}}`

### Example 2: Extract User ID from XML

**Response:**
```xml
<response>
  <user>
    <id>12345</id>
    <name>John Doe</name>
  </user>
</response>
```

**Steps:**
1. Open Variable Extractor Dialog
2. Select extraction method: XPath
3. Enter path: `response.user.id`
4. Enter variable name: `userId`
5. Test and save

### Example 3: Extract from Header

**Response Headers:**
```
X-Request-Id: abc-123-xyz
X-Rate-Limit: 1000
```

**Steps:**
1. Go to Headers tab in response viewer
2. Click extract icon next to `X-Request-Id`
3. Variable name auto-filled as `requestId`
4. Adjust scope if needed
5. Save

### Example 4: Batch Extract Multiple Values

**Response:**
```json
{
  "user": {
    "id": 42,
    "email": "user@example.com",
    "token": "abc123"
  },
  "session": {
    "id": "sess-xyz",
    "expires": "2025-12-31"
  }
}
```

**Steps:**
1. Click "More options" → "Batch Extract (Mapping Wizard)"
2. Add mappings:
   - Variable: `userId`, Type: JSONPath, Path: `$.user.id`, Scope: Global
   - Variable: `userEmail`, Type: JSONPath, Path: `$.user.email`, Scope: Global
   - Variable: `sessionId`, Type: JSONPath, Path: `$.session.id`, Scope: Environment
3. Click "Test All Mappings"
4. Review results
5. Click "Save All Variables"

### Example 5: Create Auto-Extraction Rule

**Scenario:** Always extract auth token from login responses

**Steps:**
1. Open "Manage Extraction Rules"
2. Click "Add Rule"
3. Configure:
   - Name: "Extract Auth Token"
   - Variable Name: `authToken`
   - Scope: Global
   - Source: Response Body
   - Extraction Type: JSONPath
   - Pattern: `$.data.token`
   - Enabled: Yes
4. Test with current response
5. Save rule

**Result:** Every time you receive a response matching this pattern, the token will be automatically extracted.

## JSONPath Syntax

### Basic Selectors
- `$.data` - Root level property
- `$.user.name` - Nested property
- `$.users[0]` - First array element
- `$.users[*]` - All array elements
- `$..name` - Recursive descent

### Filters
- `$.users[?(@.active)]` - Filter by property
- `$.products[?(@.price < 100)]` - Filter by condition
- `$.items[?(@.id == 1)]` - Filter by equality

### Examples
```javascript
// Extract single value
$.data.token

// Extract array element
$.users[0].email

// Extract all IDs
$.users[*].id

// Filter and extract
$.products[?(@.inStock)].name
```

## XPath Syntax

### Basic Paths
- `root.element` - Direct path
- `root.element.subelement` - Nested path
- `/root/element` - Absolute path with slash

### Examples
```xml
<!-- XML Structure -->
<response>
  <data>
    <user>
      <id>123</id>
    </user>
  </data>
</response>

<!-- XPath Expressions -->
response.data.user.id
/response/data/user/id
```

## Regular Expression Patterns

### Common Patterns
```regex
// Extract email
\S+@\S+\.\S+

// Extract JWT token
eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+

// Extract number
\d+

// Extract with capture group
"token":\s*"([^"]+)"

// Extract UUID
[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}
```

### Tips
- Use capture groups `()` to extract specific parts
- Without capture groups, the full match is extracted
- Test your regex before saving

## Variable Scopes

### Global
- Available in all requests across all collections
- Persists across sessions
- Use for: API keys, base URLs, common tokens

### Environment
- Specific to the active environment
- Switch between dev/staging/prod
- Use for: Environment-specific URLs, credentials

### Collection
- Specific to a collection
- Isolated from other collections
- Use for: Collection-specific data, test data

## Best Practices

### 1. Naming Conventions
- Use camelCase: `authToken`, `userId`
- Be descriptive: `userAuthToken` not `token`
- Avoid special characters
- Use consistent prefixes for related variables

### 2. Scope Selection
- Use Global for truly global values (API keys)
- Use Environment for environment-specific values
- Use Collection for test data and temporary values

### 3. Rule Management
- Create rules for frequently extracted values
- Disable rules when not needed
- Export rules for backup
- Document complex patterns

### 4. History Management
- Review history periodically
- Clear old history to save space
- Use history to debug variable issues

### 5. Testing
- Always test extractions before saving
- Verify extracted values are correct
- Use mapping wizard for complex extractions

## Troubleshooting

### Extraction Fails
**Problem:** "No matches found for JSONPath expression"

**Solutions:**
- Verify the response structure
- Check JSONPath syntax
- Use JSONPath tester online
- Try simpler path first

### Wrong Value Extracted
**Problem:** Extracted value is not what you expected

**Solutions:**
- Review the JSONPath/XPath expression
- Check if multiple values match (returns array)
- Use more specific path
- Test with different responses

### Variable Not Available
**Problem:** Variable doesn't appear in other requests

**Solutions:**
- Check variable scope
- Verify variable was saved successfully
- Check Variable Preview Panel
- Ensure variable name is correct

### Rule Not Working
**Problem:** Auto-extraction rule doesn't trigger

**Solutions:**
- Verify rule is enabled
- Check extraction pattern matches response
- Test rule manually
- Review rule source (body vs header)

## Keyboard Shortcuts

- `Ctrl+E` - Open Variable Extractor Dialog
- `Ctrl+Shift+V` - Open Variable Preview Panel
- `Ctrl+Shift+R` - Open Extraction Rules Manager
- `Ctrl+Shift+M` - Open Mapping Wizard
- `Ctrl+Shift+H` - Open Variable History

## API Reference

### electronAPI.extractor

```typescript
// Extract from JSON
await electronAPI.extractor.extractFromJSON(body, path, variableName, scope);

// Extract from XML
await electronAPI.extractor.extractFromXML(body, xpath, variableName, scope);

// Extract from Header
await electronAPI.extractor.extractFromHeader(headers, headerName, variableName, scope);

// Extract with Regex
await electronAPI.extractor.extractWithRegex(content, pattern, variableName, scope, source);

// Extract with Rules
await electronAPI.extractor.extractWithRules(response, rules);

// Rule Management
await electronAPI.extractor.addRule(rule);
await electronAPI.extractor.updateRule(id, updates);
await electronAPI.extractor.deleteRule(id);
await electronAPI.extractor.getRules();

// History
await electronAPI.extractor.getHistory(variableName, limit);
await electronAPI.extractor.clearHistory(variableName);
await electronAPI.extractor.recordHistory(variableName, oldValue, newValue, scope, source);

// Utilities
await electronAPI.extractor.suggestMethod(response);
await electronAPI.extractor.exportRules();
await electronAPI.extractor.importRules(json);
```

## Advanced Features

### Chaining Extractions
Extract a value and use it in the next extraction:

1. Extract token from login response
2. Use `{{authToken}}` in Authorization header
3. Extract user data from profile response
4. Use `{{userId}}` in subsequent requests

### Conditional Extraction
Create rules with specific conditions:

```javascript
// Only extract if status is success
$.data[?(@.status == 'success')].token
```

### Batch Processing
Use mapping wizard to extract multiple related values:

- Extract all user IDs
- Extract all product names
- Extract all timestamps

### Rule Templates
Export commonly used rules and share with team:

1. Export rules to JSON
2. Share file with team
3. Team imports rules
4. Consistent variable extraction across team

## FAQ

**Q: Can I extract from nested arrays?**  
A: Yes, use JSONPath like `$.users[*].addresses[0].city`

**Q: How many variables can I create?**  
A: No limit, but consider performance with thousands of variables

**Q: Can I extract binary data?**  
A: No, extraction works with text-based responses only

**Q: Are variables encrypted?**  
A: Secret-type variables use OS-level secure storage (Keytar)

**Q: Can I use variables in pre-request scripts?**  
A: Yes, access via `pm.variables.get('variableName')`

**Q: How long is history kept?**  
A: Last 1000 entries per variable, older entries are automatically removed

## See Also

- [Scripting Guide](SCRIPTING.md) - Using variables in scripts
- [Collections Guide](USER_GUIDE.md#collections) - Managing collections
- [Environments Guide](USER_GUIDE.md#environments) - Environment management
- [API Documentation](API.md) - Complete API reference

---

**Version:** 0.8.0  
**Last Updated:** October 23, 2025
