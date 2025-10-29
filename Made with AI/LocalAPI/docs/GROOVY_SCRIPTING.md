# Groovy-Style Scripting Guide

**Version:** 0.5.0

LocalAPI supports Groovy-style scripting syntax for test scripts, providing a familiar interface for developers coming from tools like SoapUI or other Groovy-based testing frameworks.

**Note:** This is a JavaScript implementation with Groovy-style API, not actual Groovy/JVM. Scripts run in Node.js VM with Groovy-like syntax.

## Table of Contents

- [Groovy-Style Assertions](#groovy-style-assertions)
- [Collection Methods](#collection-methods)
- [String Methods](#string-methods)
- [pm API](#pm-api)
- [Examples](#examples)

## Groovy-Style Assertions

### assert(condition, message?)

Basic assertion that throws if condition is false.

```groovy
assert pm.response.status == 200, "Expected status 200"
assert pm.response.time < 1000, "Response too slow"
```

### assertEquals(expected, actual, message?)

Assert two values are equal.

```groovy
def jsonData = pm.response.json()
assertEquals(200, pm.response.status, "Status should be 200")
assertEquals("John Doe", jsonData.name, "Name mismatch")
```

### assertNotEquals(expected, actual, message?)

Assert two values are not equal.

```groovy
assertNotEquals(404, pm.response.status, "Should not be 404")
assertNotEquals(null, jsonData.id, "ID should not be null")
```

### assertTrue(condition, message?)

Assert condition is true.

```groovy
def jsonData = pm.response.json()
assertTrue(jsonData.active, "User should be active")
assertTrue(jsonData.roles.contains("admin"), "Should have admin role")
```

### assertFalse(condition, message?)

Assert condition is false.

```groovy
assertFalse(jsonData.deleted, "Should not be deleted")
assertFalse(jsonData.email.isEmpty(), "Email should not be empty")
```

### assertNull(value, message?)

Assert value is null.

```groovy
assertNull(jsonData.error, "Should have no error")
```

### assertNotNull(value, message?)

Assert value is not null or undefined.

```groovy
def jsonData = pm.response.json()
assertNotNull(jsonData.id, "ID should exist")
assertNotNull(jsonData.email, "Email should exist")
```

### assertContains(collection, item, message?)

Assert collection contains item.

```groovy
def jsonData = pm.response.json()
assertContains(jsonData.tags, "important", "Should have important tag")
```

## Collection Methods

### each(collection, closure)

Iterate over collection (Groovy-style).

```groovy
def users = pm.response.json()
each(users, { user ->
    assertNotNull(user.id, "Each user should have ID")
    assertNotNull(user.email, "Each user should have email")
})

// With index
each(users, { user, index ->
    println("User ${index}: ${user.name}")
})
```

### collect(collection, closure)

Transform collection (map).

```groovy
def users = pm.response.json()
def userIds = collect(users, { user -> user.id })
println("User IDs: ${userIds}")

def userNames = collect(users, { user -> user.name })
```

### find(collection, closure)

Find first matching element.

```groovy
def users = pm.response.json()
def admin = find(users, { user -> user.role == "admin" })
assertNotNull(admin, "Should have at least one admin")
```

### findAll(collection, closure)

Find all matching elements (filter).

```groovy
def users = pm.response.json()
def activeUsers = findAll(users, { user -> user.active == true })
assertTrue(activeUsers.length > 0, "Should have active users")

def admins = findAll(users, { user -> user.role == "admin" })
```

## String Methods

### capitalize(str)

Capitalize first letter.

```groovy
def name = capitalize("john")
assertEquals("John", name)
```

### reverse(str)

Reverse string.

```groovy
def reversed = reverse("hello")
assertEquals("olleh", reversed)
```

## pm API

The `pm` object provides the same API as JavaScript mode:

### pm.test(name, closure)

```groovy
pm.test("Status code is 200", {
    assertEquals(200, pm.response.status)
})

pm.test("Response has user data", {
    def jsonData = pm.response.json()
    assertNotNull(jsonData.id)
    assertNotNull(jsonData.name)
})
```

### pm.response

```groovy
pm.response.status        // HTTP status code
pm.response.statusText    // HTTP status text
pm.response.headers       // Response headers object
pm.response.body          // Response body
pm.response.time          // Response time in ms
pm.response.size          // Response size in bytes
pm.response.json()        // Parse as JSON
pm.response.text()        // Get as text
```

### pm.variables

```groovy
pm.variables.set("userId", jsonData.id)
def userId = pm.variables.get("userId")
```

### pm.environment

```groovy
pm.environment.set("authToken", jsonData.token)
def token = pm.environment.get("authToken")
```

### pm.globals

```groovy
pm.globals.set("apiUrl", "https://api.example.com")
def apiUrl = pm.globals.get("apiUrl")
```

### pm.jsonPath(obj, path)

```groovy
def jsonData = pm.response.json()
def userIds = pm.jsonPath(jsonData, '$.users[*].id')
def activeUsers = pm.jsonPath(jsonData, '$.users[?(@.active==true)]')
```

### pm.extractJson(path, varName?)

```groovy
def userId = pm.extractJson('$.data.user.id', 'userId')
def email = pm.extractJson('$.data.user.email')
```

## Console Output

### println(...args)

Print with newline (Groovy-style).

```groovy
println("Test started")
println("User ID:", userId)
println("Response:", jsonData)
```

### print(...args)

Print without newline.

```groovy
print("Processing...")
```

### console.log / error / warn

Standard console methods also available.

```groovy
console.log("Test completed")
console.error("An error occurred")
console.warn("Warning message")
```

## Examples

### Example 1: Basic Groovy-Style Test

```groovy
// Test status code
pm.test("Status code is 200", {
    assertEquals(200, pm.response.status)
})

// Test response time
pm.test("Response time is acceptable", {
    assert pm.response.time < 1000, "Response took ${pm.response.time}ms"
})

// Parse and test JSON
def jsonData = pm.response.json()
pm.test("Response has required fields", {
    assertNotNull(jsonData.id)
    assertNotNull(jsonData.name)
    assertNotNull(jsonData.email)
})
```

### Example 2: Collection Processing

```groovy
def users = pm.response.json()

pm.test("All users have valid data", {
    each(users, { user ->
        assertNotNull(user.id, "User should have ID")
        assertNotNull(user.email, "User should have email")
        assertTrue(user.email.contains("@"), "Email should be valid")
    })
})

pm.test("Has active users", {
    def activeUsers = findAll(users, { user -> user.active == true })
    assertTrue(activeUsers.length > 0, "Should have active users")
})

pm.test("Can find admin", {
    def admin = find(users, { user -> user.role == "admin" })
    assertNotNull(admin, "Should have admin user")
})
```

### Example 3: Data Extraction

```groovy
def jsonData = pm.response.json()

pm.test("Extract and save user data", {
    // Extract values
    def userId = pm.extractJson('$.data.user.id', 'userId')
    def userName = pm.extractJson('$.data.user.name', 'userName')
    def userEmail = pm.extractJson('$.data.user.email', 'userEmail')
    
    // Validate
    assertNotNull(userId, "User ID should exist")
    assertNotNull(userName, "User name should exist")
    assertNotNull(userEmail, "User email should exist")
    
    // Log
    println("Extracted user: ${userName} (${userEmail})")
})
```

### Example 4: JSONPath Queries

```groovy
def jsonData = pm.response.json()

pm.test("JSONPath queries work", {
    // Get all user IDs
    def userIds = pm.jsonPath(jsonData, '$.users[*].id')
    assertTrue(userIds.length > 0, "Should have user IDs")
    
    // Get active users
    def activeUsers = pm.jsonPath(jsonData, '$.users[?(@.active==true)]')
    assertTrue(activeUsers.length > 0, "Should have active users")
    
    // Get admin emails
    def adminEmails = pm.jsonPath(jsonData, '$.users[?(@.role=="admin")].email')
    
    println("Found ${userIds.length} users")
    println("Found ${activeUsers.length} active users")
    println("Admin emails: ${adminEmails}")
})
```

### Example 5: String Manipulation

```groovy
def jsonData = pm.response.json()

pm.test("String operations", {
    def name = jsonData.name
    def capitalizedName = capitalize(name.toLowerCase())
    
    assertEquals("John", capitalizedName)
    
    // Reverse check
    def reversed = reverse("test")
    assertEquals("tset", reversed)
})
```

### Example 6: Complex Validation

```groovy
def jsonData = pm.response.json()

pm.test("Comprehensive validation", {
    // Status validation
    assertEquals(200, pm.response.status, "Status should be 200")
    
    // Response time validation
    assert pm.response.time < 2000, "Response time should be under 2s"
    
    // Header validation
    assertNotNull(pm.response.headers['content-type'])
    assert pm.response.headers['content-type'].contains('application/json')
    
    // Data structure validation
    assertNotNull(jsonData.data)
    assertNotNull(jsonData.data.users)
    assertTrue(jsonData.data.users instanceof Array)
    
    // Collection validation
    def users = jsonData.data.users
    assertTrue(users.length > 0, "Should have users")
    
    // Each user validation
    each(users, { user ->
        assertNotNull(user.id)
        assertNotNull(user.email)
        assertTrue(user.email.contains("@"))
        assertNotNull(user.createdAt)
    })
    
    // Find specific user
    def admin = find(users, { user -> user.role == "admin" })
    assertNotNull(admin, "Should have admin")
    
    // Count active users
    def activeUsers = findAll(users, { user -> user.active == true })
    println("Active users: ${activeUsers.length}")
})
```

### Example 7: Authentication Flow

```groovy
// Login response
def jsonData = pm.response.json()

pm.test("Login successful", {
    assertEquals(200, pm.response.status)
    assertNotNull(jsonData.token, "Should have auth token")
    assertNotNull(jsonData.user, "Should have user data")
    
    // Save token for next requests
    pm.environment.set("authToken", jsonData.token)
    pm.variables.set("userId", jsonData.user.id)
    
    println("Logged in as: ${jsonData.user.email}")
    println("Token saved to environment")
})
```

### Example 8: Error Handling

```groovy
def jsonData = pm.response.json()

pm.test("Error handling", {
    if (pm.response.status >= 400) {
        assertNotNull(jsonData.error, "Error response should have error field")
        assertNotNull(jsonData.message, "Error response should have message")
        println("Error: ${jsonData.message}")
    } else {
        assertNull(jsonData.error, "Success response should not have error")
        assertNotNull(jsonData.data, "Success response should have data")
    }
})
```

## Differences from Java Groovy

This is a JavaScript-based implementation with Groovy-style syntax. Key differences:

1. **No JVM** - Runs in Node.js VM, not JVM
2. **JavaScript types** - Uses JavaScript types (Array, Object, etc.)
3. **No Groovy classes** - Cannot import Groovy classes
4. **No GPath** - Use JSONPath instead
5. **Limited syntax** - Core Groovy features only
6. **No compilation** - Scripts are interpreted

## Best Practices

1. **Use def for variables** - `def userId = jsonData.id`
2. **Use closures** - `{ user -> user.id }`
3. **Use assertions** - `assertEquals`, `assertNotNull`, etc.
4. **Use println** - Groovy-style output
5. **Use each/collect** - Groovy-style iteration
6. **Keep it simple** - Complex Groovy features not supported

## Migration from JavaScript

```javascript
// JavaScript
pm.test('Test', () => {
  pm.expect(value).to.equal(expected);
});

// Groovy-style
pm.test("Test", {
    assertEquals(expected, value)
})
```

```javascript
// JavaScript
const users = response.json();
users.forEach(user => {
  // process user
});

// Groovy-style
def users = pm.response.json()
each(users, { user ->
    // process user
})
```

## Limitations

- No actual Groovy/JVM features
- No Groovy classes or imports
- No GPath (use JSONPath)
- No Groovy metaprogramming
- 5-second timeout
- No async/await
- JavaScript semantics

## Troubleshooting

### Script doesn't run
- Check for syntax errors
- Ensure using JavaScript-compatible syntax
- Check console for errors

### Assertions failing
- Use `println` to debug values
- Check assertion message
- Verify data types

### Variables not saving
- Use `pm.variables.set()`
- Check variable scope
- Verify variable names
