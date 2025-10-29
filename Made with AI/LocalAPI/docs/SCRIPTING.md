# Scripting Guide

**Version:** 0.7.0

LocalAPI supports JavaScript scripting for pre-request and test scripts, similar to Postman. Scripts run in a secure Node.js VM sandbox with a `pm` API.

## Table of Contents

- [Pre-Request Scripts](#pre-request-scripts)
- [Test Scripts](#test-scripts)
- [pm API Reference](#pm-api-reference)
- [Examples](#examples)

## Pre-Request Scripts

Pre-request scripts run before the HTTP request is sent. Use them to:
- Set variables dynamically
- Generate timestamps or UUIDs
- Modify request data
- Log debugging information

```javascript
// Set a variable
pm.variables.set('timestamp', Date.now());

// Set an environment variable
pm.environment.set('authToken', 'Bearer xyz123');

// Log to console
console.log('Pre-request script executed');
```

## Test Scripts

Test scripts run after the response is received. Use them to:
- Validate response status, headers, and body
- Extract data from responses
- Set variables for subsequent requests
- Write automated tests

```javascript
// Test response status
pm.test('Status code is 200', () => {
  pm.expect(pm.response.code).to.equal(200);
});

// Test response body
pm.test('Response has user data', () => {
  const jsonData = pm.response.json();
  pm.expect(jsonData).to.have.property('id');
  pm.expect(jsonData.name).to.be.a('string');
});

// Extract and save data
const responseData = pm.response.json();
pm.variables.set('userId', responseData.id);
```

## pm API Reference

### pm.test(name, fn)

Define a test assertion.

**Parameters:**
- `name` (string): Test name
- `fn` (function): Test function containing assertions

**Example:**
```javascript
pm.test('Response time is acceptable', () => {
  pm.expect(pm.response.responseTime).to.be.below(500);
});
```

### pm.expect(value)

Chai-like assertion library.

**Chainable Assertions:**

#### Equality
```javascript
pm.expect(value).to.equal(expected);
pm.expect(value).to.eql(expected); // Deep equality
pm.expect(value).not.to.equal(expected);
```

#### Type Checking
```javascript
pm.expect(value).to.be.a('string');
pm.expect(value).to.be.an('array');
pm.expect(value).to.be.true;
pm.expect(value).to.be.false;
pm.expect(value).to.be.null;
pm.expect(value).to.be.undefined;
pm.expect(value).not.to.be.null;
```

#### Properties
```javascript
pm.expect(obj).to.have.property('key');
pm.expect(obj).to.have.property('key', 'value');
pm.expect(arr).to.have.length(5);
```

#### Inclusion
```javascript
pm.expect(array).to.include(item);
pm.expect(string).to.include('substring');
```

#### Pattern Matching
```javascript
pm.expect(string).to.match(/pattern/);
```

#### Numeric Comparisons
```javascript
pm.expect(value).to.be.above(10);
pm.expect(value).to.be.below(100);
pm.expect(value).to.be.greaterThan(10);
pm.expect(value).to.be.lessThan(100);
```

### pm.response

Access response data.

**Properties:**
- `pm.response.code` (number): HTTP status code
- `pm.response.status` (string): HTTP status text
- `pm.response.headers` (object): Response headers
- `pm.response.responseTime` (number): Response time in milliseconds
- `pm.response.responseSize` (number): Response size in bytes

**Methods:**
- `pm.response.json()`: Parse response as JSON
- `pm.response.text()`: Get response as text

**Example:**
```javascript
pm.test('Status is OK', () => {
  pm.expect(pm.response.code).to.equal(200);
  pm.expect(pm.response.status).to.equal('OK');
});

pm.test('Response is JSON', () => {
  const data = pm.response.json();
  pm.expect(data).to.be.an('object');
});

pm.test('Has correct header', () => {
  pm.expect(pm.response.headers['content-type']).to.include('application/json');
});
```

### pm.variables

Manage request-scoped variables.

**Methods:**
- `pm.variables.get(key)`: Get variable value
- `pm.variables.set(key, value)`: Set variable value

**Example:**
```javascript
// Set variable
pm.variables.set('userId', 123);

// Get variable
const userId = pm.variables.get('userId');
```

### pm.environment

Manage environment variables.

**Methods:**
- `pm.environment.get(key)`: Get environment variable
- `pm.environment.set(key, value)`: Set environment variable

**Example:**
```javascript
// Set environment variable
pm.environment.set('apiUrl', 'https://api.example.com');

// Get environment variable
const apiUrl = pm.environment.get('apiUrl');
```

### pm.globals

Manage global variables.

**Methods:**
- `pm.globals.get(key)`: Get global variable
- `pm.globals.set(key, value)`: Set global variable

**Example:**
```javascript
// Set global variable
pm.globals.set('authToken', 'Bearer xyz123');

// Get global variable
const token = pm.globals.get('authToken');
```

### pm.request

Access request data.

**Properties:**
- `pm.request.url` (string): Request URL
- `pm.request.method` (string): HTTP method
- `pm.request.headers` (object): Request headers
- `pm.request.body` (any): Request body

**Example:**
```javascript
console.log('Request URL:', pm.request.url);
console.log('Request method:', pm.request.method);
```

### console

Standard console methods for debugging.

**Methods:**
- `console.log(...args)`: Log messages
- `console.error(...args)`: Log errors
- `console.warn(...args)`: Log warnings

**Example:**
```javascript
console.log('Test started');
console.error('An error occurred');
console.warn('Warning message');
```

### pm.jsonPath(obj, path)

Query JSON data using JSONPath expressions.

**Parameters:**
- `obj` (object): The JSON object to query
- `path` (string): JSONPath expression

**Returns:** Array of matching values

**Example:**
```javascript
const jsonData = pm.response.json();

// Get all user emails
const emails = pm.jsonPath(jsonData, '$.users[*].email');

// Get users where active is true
const activeUsers = pm.jsonPath(jsonData, '$.users[?(@.active==true)]');

// Get first user's name
const firstName = pm.jsonPath(jsonData, '$.users[0].name');
```

### pm.extractJson(path, varName?)

Extract data from response using JSONPath and optionally save to variable.

**Parameters:**
- `path` (string): JSONPath expression
- `varName` (string, optional): Variable name to save the extracted value

**Returns:** Extracted value (single value if one result, array if multiple)

**Example:**
```javascript
// Extract and save user ID
const userId = pm.extractJson('$.data.user.id', 'userId');

// Extract email without saving
const email = pm.extractJson('$.data.user.email');

// Extract array of names
const names = pm.extractJson('$.users[*].name', 'userNames');

pm.test('Extracted data is valid', () => {
  pm.expect(userId).to.be.a('number');
  pm.expect(email).to.include('@');
});
```

## JSONPath Syntax

### Basic Selectors
- `$` - Root object
- `@` - Current object (in filters)
- `.property` - Child property
- `['property']` - Child property (bracket notation)
- `[index]` - Array index
- `[*]` - All elements

### Advanced Selectors
- `..property` - Recursive descent
- `[start:end]` - Array slice
- `[?(@.property)]` - Filter expression
- `[?(@.price < 10)]` - Filter with comparison
- `[(@.length-1)]` - Script expression

### Examples
```javascript
// Get all book titles
pm.jsonPath(data, '$.store.book[*].title')

// Get books cheaper than $10
pm.jsonPath(data, '$.store.book[?(@.price < 10)]')

// Get all prices in the store
pm.jsonPath(data, '$..price')

// Get the last book
pm.jsonPath(data, '$.store.book[(@.length-1)]')

// Get books by specific author
pm.jsonPath(data, '$.store.book[?(@.author=="J.K. Rowling")]')
```

## Examples

### Example 1: Authentication Flow

```javascript
// Pre-request script for login
pm.variables.set('username', 'testuser');
pm.variables.set('password', 'password123');

// Test script for login response
pm.test('Login successful', () => {
  pm.expect(pm.response.code).to.equal(200);
  
  const jsonData = pm.response.json();
  pm.expect(jsonData).to.have.property('token');
  
  // Save token for subsequent requests
  pm.environment.set('authToken', jsonData.token);
  console.log('Auth token saved:', jsonData.token);
});
```

### Example 2: Data Validation

```javascript
pm.test('User data is valid', () => {
  const user = pm.response.json();
  
  // Validate structure
  pm.expect(user).to.have.property('id');
  pm.expect(user).to.have.property('email');
  pm.expect(user).to.have.property('name');
  
  // Validate types
  pm.expect(user.id).to.be.a('number');
  pm.expect(user.email).to.be.a('string');
  pm.expect(user.name).to.be.a('string');
  
  // Validate values
  pm.expect(user.email).to.match(/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/);
  pm.expect(user.name).to.have.length.above(0);
});
```

### Example 3: Response Time Check

```javascript
pm.test('Response time is acceptable', () => {
  pm.expect(pm.response.responseTime).to.be.below(1000);
});

pm.test('Response size is reasonable', () => {
  pm.expect(pm.response.responseSize).to.be.below(1000000); // 1MB
});
```

### Example 4: Array Validation

```javascript
pm.test('Returns array of users', () => {
  const users = pm.response.json();
  
  pm.expect(users).to.be.an('array');
  pm.expect(users).to.have.length.above(0);
  
  // Validate first user
  const firstUser = users[0];
  pm.expect(firstUser).to.have.property('id');
  pm.expect(firstUser).to.have.property('name');
});
```

### Example 5: Header Validation

```javascript
pm.test('Has correct headers', () => {
  pm.expect(pm.response.headers).to.have.property('content-type');
  pm.expect(pm.response.headers['content-type']).to.include('application/json');
  pm.expect(pm.response.headers).to.have.property('x-api-version');
});
```

### Example 6: Extract Nested Data

```javascript
pm.test('Extract nested data', () => {
  const response = pm.response.json();
  
  pm.expect(response).to.have.property('data');
  pm.expect(response.data).to.have.property('user');
  pm.expect(response.data.user).to.have.property('profile');
  
  // Save nested value
  const userId = response.data.user.profile.id;
  pm.variables.set('profileId', userId);
});
```

### Example 7: Dynamic Timestamps

```javascript
// Pre-request script
const now = new Date();
pm.variables.set('timestamp', now.toISOString());
pm.variables.set('unixTime', Math.floor(now.getTime() / 1000));

console.log('Timestamp:', pm.variables.get('timestamp'));
```

### Example 8: Conditional Tests

```javascript
pm.test('Status code is success', () => {
  pm.expect(pm.response.code).to.be.above(199).and.below(300);
});

const jsonData = pm.response.json();

if (jsonData.hasOwnProperty('error')) {
  pm.test('No error in response', () => {
    pm.expect(jsonData.error).to.be.null;
  });
}

if (Array.isArray(jsonData)) {
  pm.test('Array is not empty', () => {
    pm.expect(jsonData.length).to.be.above(0);
  });
}
```

### Example 9: JSONPath Auto-Extraction

```javascript
// Extract authentication token
const token = pm.extractJson('$.data.auth.token', 'authToken');

pm.test('Token extracted successfully', () => {
  pm.expect(token).to.be.a('string');
  pm.expect(token).to.have.length.above(0);
});

// Extract user profile data
const userId = pm.extractJson('$.data.user.id', 'userId');
const userName = pm.extractJson('$.data.user.name', 'userName');
const userEmail = pm.extractJson('$.data.user.email', 'userEmail');

console.log('User Profile:', { userId, userName, userEmail });

// Extract array of IDs
const productIds = pm.extractJson('$.products[*].id', 'productIds');

pm.test('Product IDs extracted', () => {
  pm.expect(productIds).to.be.an('array');
  pm.expect(productIds).to.have.length.above(0);
});
```

### Example 10: Advanced JSONPath Queries

```javascript
const jsonData = pm.response.json();

// Find all active users
const activeUsers = pm.jsonPath(jsonData, '$.users[?(@.status=="active")]');

pm.test('Has active users', () => {
  pm.expect(activeUsers).to.be.an('array');
  pm.expect(activeUsers.length).to.be.above(0);
});

// Get emails of admin users
const adminEmails = pm.jsonPath(jsonData, '$.users[?(@.role=="admin")].email');

// Get products with price less than 100
const cheapProducts = pm.jsonPath(jsonData, '$.products[?(@.price < 100)]');

// Get all nested tags
const allTags = pm.jsonPath(jsonData, '$..tags[*]');

pm.test('Query results are valid', () => {
  pm.expect(adminEmails).to.be.an('array');
  pm.expect(cheapProducts).to.be.an('array');
  pm.expect(allTags).to.be.an('array');
  
  console.log('Admin emails:', adminEmails);
  console.log('Cheap products:', cheapProducts.length);
  console.log('All tags:', allTags);
});
```

## Security

Scripts run in a secure VM sandbox with:
- 5-second timeout
- No access to file system
- No access to network (except through pm API)
- No access to Node.js modules
- Isolated from main process

## Best Practices

1. **Keep scripts simple** - Complex logic should be in your API
2. **Use descriptive test names** - Makes debugging easier
3. **Log important values** - Use console.log for debugging
4. **Handle errors gracefully** - Use try/catch for JSON parsing
5. **Clean up variables** - Remove variables when no longer needed
6. **Test edge cases** - Validate null, undefined, empty arrays
7. **Use meaningful variable names** - Makes scripts maintainable

## Limitations

- Scripts timeout after 5 seconds
- No access to external libraries
- No async/await support (use synchronous code only)
- No access to DOM or browser APIs
- No access to Node.js built-in modules

## Troubleshooting

### Script doesn't run
- Check for syntax errors in the script
- Ensure script is saved in the request
- Check console for error messages

### Variables not updating
- Ensure you're using `pm.variables.set()` correctly
- Check variable scope (request vs environment vs global)
- Verify variable names match exactly

### Tests failing unexpectedly
- Log actual values with `console.log()`
- Check response structure with `console.log(pm.response.json())`
- Verify assertions match actual data types
- Check for null/undefined values

### Timeout errors
- Simplify complex scripts
- Remove unnecessary loops
- Optimize JSON parsing
- Split into multiple smaller scripts
