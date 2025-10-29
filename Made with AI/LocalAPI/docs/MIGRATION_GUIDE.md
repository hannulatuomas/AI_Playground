# Migration Guide: From Postman/Insomnia to LocalAPI

## Overview

This guide helps you migrate your API collections, environments, and workflows from Postman or Insomnia to LocalAPI. LocalAPI provides native import support for both tools, preserving your data, scripts, and configurations.

## Quick Migration

### From Postman

1. **Export from Postman:**
   - Open Postman
   - Click on your collection → "..." → "Export"
   - Choose "Collection v2.1" format
   - Save the JSON file

2. **Import to LocalAPI:**
   - Open LocalAPI
   - Go to File → Import → Postman Collection
   - Select your exported JSON file
   - Click "Import"

**What's Preserved:**
- ✅ Collections and folders
- ✅ Requests (all methods)
- ✅ Headers, query parameters, body
- ✅ Authentication settings
- ✅ Pre-request scripts (converted to JavaScript)
- ✅ Test scripts (converted to JavaScript)
- ✅ Variables (collection and environment)
- ✅ Request descriptions and documentation

**What's Converted:**
- Postman scripts → JavaScript (pm.* API converted to LocalAPI API)
- Postman variables → LocalAPI variables
- Postman environments → LocalAPI environments

### From Insomnia

1. **Export from Insomnia:**
   - Open Insomnia
   - Click Application Menu → Import/Export → Export Data
   - Choose "Export Workspace"
   - Save the JSON file

2. **Import to LocalAPI:**
   - Open LocalAPI
   - Go to File → Import → Insomnia Workspace
   - Select your exported JSON file
   - Click "Import"

**What's Preserved:**
- ✅ Workspaces and folders
- ✅ Requests (REST, GraphQL, gRPC)
- ✅ Headers, query parameters, body
- ✅ Authentication (all types)
- ✅ Environments and variables
- ✅ Request chaining
- ✅ Plugins (converted to LocalAPI plugins where possible)

## Detailed Migration Steps

### Step 1: Prepare Your Data

**Postman:**
```bash
1. Export all collections individually
2. Export environments: Settings → Data → Export Data
3. Export globals: Settings → Data → Export Data
4. Document any custom scripts or workflows
```

**Insomnia:**
```bash
1. Export entire workspace (includes everything)
2. Document any plugins you're using
3. Note any custom request chaining
```

### Step 2: Import to LocalAPI

**Using the Import Dialog:**
1. File → Import (Ctrl+I)
2. Select format: Postman v2.1 or Insomnia v4
3. Choose file(s) to import
4. Configure import options:
   - Merge with existing collections
   - Create new workspace
   - Import environments
   - Import variables
5. Click "Import"
6. Review import summary

**Using Drag & Drop:**
1. Drag exported JSON file into LocalAPI window
2. LocalAPI auto-detects format
3. Confirm import options
4. Import completes automatically

### Step 3: Verify Migration

**Check Collections:**
- [ ] All folders and requests imported
- [ ] Request methods correct
- [ ] URLs and parameters intact
- [ ] Headers preserved
- [ ] Body content correct

**Check Authentication:**
- [ ] Auth types recognized
- [ ] Credentials imported (if not sensitive)
- [ ] OAuth flows configured

**Check Scripts:**
- [ ] Pre-request scripts converted
- [ ] Test scripts converted
- [ ] Variable references updated

**Check Variables:**
- [ ] Environment variables imported
- [ ] Collection variables imported
- [ ] Global variables imported
- [ ] Variable scopes correct

### Step 4: Update Scripts

**Postman Script Conversion:**

Postman scripts use the `pm.*` API. LocalAPI converts these automatically, but you may need to adjust some:

```javascript
// Postman
pm.environment.set("token", pm.response.json().token);
pm.test("Status is 200", () => {
  pm.response.to.have.status(200);
});

// LocalAPI (auto-converted)
localapi.env.set("token", localapi.response.json().token);
localapi.test("Status is 200", () => {
  localapi.expect(localapi.response.status).toBe(200);
});
```

**Common Conversions:**
| Postman | LocalAPI |
|---------|----------|
| `pm.environment.get()` | `localapi.env.get()` |
| `pm.environment.set()` | `localapi.env.set()` |
| `pm.globals.get()` | `localapi.global.get()` |
| `pm.globals.set()` | `localapi.global.set()` |
| `pm.variables.get()` | `localapi.var.get()` |
| `pm.request.*` | `localapi.request.*` |
| `pm.response.*` | `localapi.response.*` |
| `pm.test()` | `localapi.test()` |
| `pm.expect()` | `localapi.expect()` |

**Insomnia Script Conversion:**

Insomnia uses template tags. LocalAPI converts these to variables:

```javascript
// Insomnia
{% request.header.Authorization %}
{{ _.token }}

// LocalAPI
{{Authorization}}
{{token}}
```

### Step 5: Configure Environments

**Postman Environments:**
- Imported as LocalAPI environments
- Active environment preserved
- Variable values maintained

**Insomnia Environments:**
- Base environment → Global variables
- Sub-environments → LocalAPI environments
- Private environments → Secure storage

**Manual Setup:**
1. Go to Environments panel
2. Review imported environments
3. Set active environment
4. Verify variable values
5. Update any sensitive values (passwords, tokens)

### Step 6: Test Your Requests

**Verification Checklist:**
1. Send a simple GET request
2. Test POST with body
3. Verify authentication works
4. Check variable substitution
5. Run pre-request scripts
6. Run test scripts
7. Test request chaining
8. Verify file uploads
9. Check GraphQL queries
10. Test WebSocket connections

## Feature Comparison

### Postman vs LocalAPI

| Feature | Postman | LocalAPI | Notes |
|---------|---------|----------|-------|
| Collections | ✅ | ✅ | Fully compatible |
| Environments | ✅ | ✅ | Fully compatible |
| Pre-request Scripts | ✅ | ✅ | Auto-converted |
| Test Scripts | ✅ | ✅ | Auto-converted |
| Variables | ✅ | ✅ | All scopes supported |
| Authentication | ✅ | ✅ | All types supported |
| GraphQL | ✅ | ✅ | Full support |
| WebSocket | ✅ | ✅ | Full support |
| gRPC | ✅ | ✅ | Full support |
| Mock Servers | ✅ | ✅ | Local only |
| Monitors | ✅ | ✅ | Local only |
| Team Sync | ✅ | ❌ | LocalAPI is offline |
| Cloud Storage | ✅ | ❌ | LocalAPI is local |

### Insomnia vs LocalAPI

| Feature | Insomnia | LocalAPI | Notes |
|---------|----------|----------|-------|
| Workspaces | ✅ | ✅ | Fully compatible |
| Requests | ✅ | ✅ | All types supported |
| Environments | ✅ | ✅ | Fully compatible |
| Template Tags | ✅ | ✅ | Converted to variables |
| Plugins | ✅ | ✅ | Most plugins supported |
| GraphQL | ✅ | ✅ | Full support |
| gRPC | ✅ | ✅ | Full support |
| Design Tools | ✅ | ✅ | OpenAPI/Swagger |
| Git Sync | ✅ | ✅ | Local Git integration |
| Cloud Sync | ✅ | ❌ | LocalAPI is offline |

## Advanced Migration

### Batch Import

Import multiple collections at once:

```bash
# Using CLI (if available)
localapi import --format postman --files *.json

# Using UI
File → Import → Select Multiple Files
```

### Automated Migration

Use the LocalAPI API to automate migration:

```javascript
const collections = ['collection1.json', 'collection2.json'];

for (const file of collections) {
  await localapi.import.fromFile(file, {
    format: 'postman-v2.1',
    merge: false,
    createWorkspace: true
  });
}
```

### Custom Script Migration

If you have complex Postman scripts, you may need manual conversion:

1. **Identify custom pm.* calls**
2. **Map to LocalAPI equivalents**
3. **Test thoroughly**
4. **Document changes**

### Plugin Migration (Insomnia)

Insomnia plugins may need conversion:

1. Check if equivalent LocalAPI plugin exists
2. Convert plugin code if needed
3. Test plugin functionality
4. Document any limitations

## Troubleshooting

### Common Issues

**Issue: Scripts don't work after import**
- **Solution:** Review script conversion, update API calls

**Issue: Variables not substituting**
- **Solution:** Check variable scopes, ensure environment is active

**Issue: Authentication fails**
- **Solution:** Re-enter sensitive credentials (not imported for security)

**Issue: GraphQL queries fail**
- **Solution:** Verify schema, check introspection settings

**Issue: File uploads don't work**
- **Solution:** Update file paths to local system

### Getting Help

- Check documentation: `docs/USER_GUIDE.md`
- Review examples: `examples/` folder
- Report issues: GitHub Issues
- Community: Discord/Forum

## Best Practices

### Before Migration
1. ✅ Backup your Postman/Insomnia data
2. ✅ Document custom workflows
3. ✅ Export all data (collections, environments, globals)
4. ✅ Note any plugins or extensions used

### During Migration
1. ✅ Import one collection at a time initially
2. ✅ Verify each import before proceeding
3. ✅ Test critical requests immediately
4. ✅ Document any issues encountered

### After Migration
1. ✅ Test all collections thoroughly
2. ✅ Update team documentation
3. ✅ Configure auto-save and backups
4. ✅ Set up Git integration if needed
5. ✅ Train team on LocalAPI features

## Next Steps

After successful migration:

1. **Explore LocalAPI Features:**
   - Variable extraction
   - Mock servers
   - Performance testing
   - Security scanning
   - Reporting

2. **Optimize Workflows:**
   - Set up collections
   - Configure environments
   - Create templates
   - Automate testing

3. **Integrate with Tools:**
   - Git version control
   - CI/CD pipelines
   - Documentation generators
   - Test frameworks

## Conclusion

Migrating from Postman or Insomnia to LocalAPI is straightforward with native import support. Most features are preserved automatically, with only minor script adjustments needed. LocalAPI's offline-first approach ensures your API data stays local and secure.

For additional help, see:
- [Import/Export Guide](IMPORT_EXPORT_GUIDE.md)
- [User Guide](USER_GUIDE.md)
- [Variable Extraction Guide](VARIABLE_EXTRACTION_GUIDE.md)
