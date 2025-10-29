
# C#/.NET/ASP.NET Best Practices

## Code Organization and Structure

### Project Structure
- Use solution (.sln) files to organize multiple related projects
- Organize code into logical namespaces that mirror folder structure
- Separate concerns: Domain, Application, Infrastructure, Presentation layers
- Keep one class per file with the filename matching the class name
- Use partial classes sparingly and only for generated code separation

### Namespace Conventions
- Use PascalCase for namespace names
- Follow pattern: `CompanyName.ProductName.Feature.SubFeature`
- Avoid deeply nested namespaces (max 4-5 levels)
- Don't use `using` statements inside namespaces

### Assembly Organization
- Create separate assemblies for different architectural layers
- Use class libraries (.csproj) for reusable components
- Keep API contracts in separate assemblies from implementations

## Naming Conventions

### General Rules
- **PascalCase**: Classes, methods, properties, constants, public fields
- **camelCase**: Local variables, private fields, parameters
- **_camelCase**: Private instance fields (prefix with underscore)
- **UPPER_CASE**: Constants that are truly constant across application

### Specific Guidelines
```csharp
// Classes and interfaces
public class CustomerService { }
public interface ICustomerRepository { }

// Methods and properties
public string GetFullName() { }
public int TotalCount { get; set; }

// Fields
private readonly ILogger _logger;
private string _connectionString;

// Local variables and parameters
public void ProcessOrder(int orderId)
{
    var orderDetails = GetOrderDetails(orderId);
}

// Constants
public const int MaxRetryAttempts = 3;
private const string DefaultConnectionString = "...";
```

### Interfaces
- Prefix with 'I': `ICustomerService`, `IRepository<T>`
- Use descriptive names that indicate capability: `IDisposable`, `IEnumerable`

### Async Methods
- Suffix async methods with 'Async': `GetCustomerAsync()`, `SaveChangesAsync()`

## Error Handling Patterns

### Exception Handling
```csharp
// Use specific exception types
try
{
    await ProcessOrderAsync(orderId);
}
catch (OrderNotFoundException ex)
{
    _logger.LogWarning(ex, "Order {OrderId} not found", orderId);
    throw;
}
catch (DbUpdateException ex)
{
    _logger.LogError(ex, "Database error processing order {OrderId}", orderId);
    throw new OrderProcessingException("Failed to process order", ex);
}

// Don't catch and swallow exceptions
// BAD: catch (Exception) { }

// Don't use exceptions for control flow
// BAD: try { var item = list[index]; } catch { item = null; }
```

### Custom Exceptions
```csharp
// Create domain-specific exceptions
public class OrderNotFoundException : Exception
{
    public int OrderId { get; }
    
    public OrderNotFoundException(int orderId) 
        : base($"Order with ID {orderId} was not found")
    {
        OrderId = orderId;
    }
    
    public OrderNotFoundException(int orderId, Exception innerException)
        : base($"Order with ID {orderId} was not found", innerException)
    {
        OrderId = orderId;
    }
}
```

### Validation
```csharp
// Use guard clauses
public void ProcessOrder(Order order)
{
    ArgumentNullException.ThrowIfNull(order);
    
    if (order.Items.Count == 0)
        throw new ArgumentException("Order must contain at least one item", nameof(order));
    
    // Process order
}

// Use FluentValidation for complex validation
public class OrderValidator : AbstractValidator<Order>
{
    public OrderValidator()
    {
        RuleFor(o => o.CustomerId).GreaterThan(0);
        RuleFor(o => o.Items).NotEmpty();
    }
}
```

## Performance Considerations

### Async/Await Best Practices
```csharp
// Use ConfigureAwait(false) in library code
await SomeOperationAsync().ConfigureAwait(false);

// Don't use async void (except for event handlers)
// GOOD:
public async Task ProcessDataAsync() { }

// BAD (except event handlers):
public async void ProcessData() { }

// Use ValueTask for hot paths
public ValueTask<int> GetCachedValueAsync(string key)
{
    if (_cache.TryGetValue(key, out var value))
        return new ValueTask<int>(value);
    
    return LoadValueAsync(key);
}

// Avoid Task.Wait() or .Result - use await
// BAD: var result = SomeMethodAsync().Result;
// GOOD: var result = await SomeMethodAsync();
```

### LINQ and Collections
```csharp
// Use efficient collection types
// List<T> for dynamic lists
// IReadOnlyList<T> or IReadOnlyCollection<T> for read-only collections
// HashSet<T> for unique items with fast lookups
// Dictionary<TKey, TValue> for key-value pairs

// Avoid multiple enumeration
// BAD:
if (items.Any())
{
    foreach (var item in items) { }
}

// GOOD:
var itemList = items.ToList();
if (itemList.Count > 0)
{
    foreach (var item in itemList) { }
}

// Use efficient LINQ methods
var exists = collection.Any(x => x.Id == id); // Better than Count() > 0
var first = collection.FirstOrDefault(x => x.Active); // Better than Where().FirstOrDefault()
```

### String Operations
```csharp
// Use StringBuilder for concatenation in loops
var sb = new StringBuilder();
foreach (var item in items)
{
    sb.AppendLine(item.ToString());
}

// Use string interpolation for simple concatenation
var message = $"Hello, {name}!";

// Use StringComparison for case-insensitive comparisons
if (value.Equals("test", StringComparison.OrdinalIgnoreCase))
```

### Memory Management
```csharp
// Implement IDisposable for unmanaged resources
public class ResourceHolder : IDisposable
{
    private bool _disposed = false;
    
    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }
    
    protected virtual void Dispose(bool disposing)
    {
        if (_disposed) return;
        
        if (disposing)
        {
            // Dispose managed resources
        }
        
        // Free unmanaged resources
        _disposed = true;
    }
}

// Use using statements
using (var connection = new SqlConnection(connectionString))
{
    // Use connection
}

// Or using declarations (C# 8.0+)
using var connection = new SqlConnection(connectionString);
```

## Security Best Practices

### Input Validation
```csharp
// Always validate and sanitize user input
public async Task<IActionResult> CreateUser(CreateUserRequest request)
{
    if (!ModelState.IsValid)
        return BadRequest(ModelState);
    
    // Additional validation
    if (string.IsNullOrWhiteSpace(request.Email))
        return BadRequest("Email is required");
    
    // Process request
}
```

### SQL Injection Prevention
```csharp
// Use parameterized queries
// GOOD:
var users = await _context.Users
    .Where(u => u.Username == username)
    .ToListAsync();

// BAD:
var query = $"SELECT * FROM Users WHERE Username = '{username}'";
```

### Authentication and Authorization
```csharp
// Use built-in ASP.NET Core authentication
[Authorize(Roles = "Admin")]
public class AdminController : Controller { }

// Use policy-based authorization
[Authorize(Policy = "RequireManagerRole")]
public async Task<IActionResult> ApproveRequest() { }

// Check authorization explicitly when needed
var authResult = await _authorizationService
    .AuthorizeAsync(User, resource, "EditPolicy");
if (!authResult.Succeeded)
    return Forbid();
```

### Secure Configuration
```csharp
// Use Secret Manager for development
// Use Azure Key Vault or similar for production
// Never commit secrets to source control

// appsettings.json
{
  "ConnectionStrings": {
    "Default": "Server=localhost;Database=MyDb"
  }
}

// Use IOptions pattern
public class DatabaseSettings
{
    public string ConnectionString { get; set; }
}

services.Configure<DatabaseSettings>(
    Configuration.GetSection("ConnectionStrings"));
```

## Testing Approaches

### Unit Testing
```csharp
// Use xUnit, NUnit, or MSTest
// Follow AAA pattern: Arrange, Act, Assert

[Fact]
public async Task GetCustomer_ValidId_ReturnsCustomer()
{
    // Arrange
    var customerId = 1;
    var repository = new Mock<ICustomerRepository>();
    repository.Setup(r => r.GetByIdAsync(customerId))
        .ReturnsAsync(new Customer { Id = customerId });
    var service = new CustomerService(repository.Object);
    
    // Act
    var result = await service.GetCustomerAsync(customerId);
    
    // Assert
    Assert.NotNull(result);
    Assert.Equal(customerId, result.Id);
}

// Use descriptive test names
// Pattern: MethodName_Scenario_ExpectedBehavior
```

### Mocking
```csharp
// Use Moq or NSubstitute for mocking
var mockLogger = new Mock<ILogger<CustomerService>>();
var mockRepository = new Mock<ICustomerRepository>();

// Verify method calls
mockRepository.Verify(
    r => r.SaveAsync(It.IsAny<Customer>()), 
    Times.Once);
```

### Integration Testing
```csharp
// Use WebApplicationFactory for ASP.NET Core integration tests
public class CustomersControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;
    
    public CustomersControllerTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }
    
    [Fact]
    public async Task GetCustomers_ReturnsSuccessStatusCode()
    {
        var response = await _client.GetAsync("/api/customers");
        response.EnsureSuccessStatusCode();
    }
}
```

## Documentation Standards

### XML Documentation Comments
```csharp
/// <summary>
/// Retrieves a customer by their unique identifier.
/// </summary>
/// <param name="customerId">The unique identifier of the customer.</param>
/// <param name="cancellationToken">Cancellation token for the operation.</param>
/// <returns>The customer if found; otherwise, null.</returns>
/// <exception cref="ArgumentException">Thrown when customerId is less than or equal to zero.</exception>
public async Task<Customer?> GetCustomerAsync(
    int customerId, 
    CancellationToken cancellationToken = default)
{
    // Implementation
}
```

### Code Comments
```csharp
// Use comments for "why", not "what"
// BAD: Increment counter
counter++;

// GOOD: Track retry attempts for exponential backoff
retryCount++;

// Use TODO comments with context
// TODO: Implement caching for frequently accessed customers (Issue #123)
```

## Common Pitfalls to Avoid

### 1. Not Disposing Resources
```csharp
// BAD:
var stream = File.OpenRead(path);
// ... use stream

// GOOD:
using var stream = File.OpenRead(path);
// ... use stream
```

### 2. Modifying Collections During Iteration
```csharp
// BAD:
foreach (var item in list)
{
    if (condition)
        list.Remove(item); // Exception!
}

// GOOD:
list.RemoveAll(item => condition);
// Or: var toRemove = list.Where(item => condition).ToList();
```

### 3. Catching Generic Exceptions
```csharp
// BAD:
try { }
catch (Exception) { } // Too broad

// GOOD:
try { }
catch (SpecificException ex) 
{ 
    _logger.LogError(ex, "Error occurred");
    throw;
}
```

### 4. Blocking Async Code
```csharp
// BAD:
var result = SomeAsyncMethod().Result; // Can cause deadlocks

// GOOD:
var result = await SomeAsyncMethod();
```

### 5. Not Using Null-Coalescing Operators
```csharp
// Use modern C# features
var value = nullableValue ?? defaultValue;
var name = customer?.Name ?? "Unknown";
```

## Language-Specific Idioms and Patterns

### SOLID Principles

#### Single Responsibility
```csharp
// Each class should have one reason to change
public class CustomerService
{
    // Only handles business logic for customers
}

public class CustomerRepository
{
    // Only handles data access for customers
}
```

#### Dependency Injection
```csharp
public class CustomerService
{
    private readonly ICustomerRepository _repository;
    private readonly ILogger<CustomerService> _logger;
    
    public CustomerService(
        ICustomerRepository repository,
        ILogger<CustomerService> logger)
    {
        _repository = repository;
        _logger = logger;
    }
}

// Register in Startup/Program.cs
builder.Services.AddScoped<ICustomerService, CustomerService>();
```

### Design Patterns

#### Repository Pattern
```csharp
public interface IRepository<T> where T : class
{
    Task<T?> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();
    Task AddAsync(T entity);
    Task UpdateAsync(T entity);
    Task DeleteAsync(int id);
}
```

#### Unit of Work Pattern
```csharp
public interface IUnitOfWork : IDisposable
{
    ICustomerRepository Customers { get; }
    IOrderRepository Orders { get; }
    Task<int> SaveChangesAsync();
}
```

#### Options Pattern
```csharp
public class EmailSettings
{
    public string SmtpServer { get; set; }
    public int Port { get; set; }
}

// Configure
services.Configure<EmailSettings>(
    Configuration.GetSection("Email"));

// Inject
public class EmailService
{
    private readonly EmailSettings _settings;
    
    public EmailService(IOptions<EmailSettings> options)
    {
        _settings = options.Value;
    }
}
```

### Entity Framework Core Best Practices
```csharp
// Use Include for eager loading
var customers = await _context.Customers
    .Include(c => c.Orders)
    .ThenInclude(o => o.OrderItems)
    .ToListAsync();

// Use AsNoTracking for read-only queries
var customers = await _context.Customers
    .AsNoTracking()
    .ToListAsync();

// Use projections to select only needed data
var customerNames = await _context.Customers
    .Select(c => new { c.Id, c.Name })
    .ToListAsync();

// Use transactions when needed
using var transaction = await _context.Database.BeginTransactionAsync();
try
{
    await _context.SaveChangesAsync();
    await transaction.CommitAsync();
}
catch
{
    await transaction.RollbackAsync();
    throw;
}
```

### Modern C# Features

#### Pattern Matching
```csharp
// Switch expressions (C# 8.0+)
var result = value switch
{
    0 => "Zero",
    > 0 and < 10 => "Small",
    >= 10 and < 100 => "Medium",
    _ => "Large"
};

// Property patterns
var isValid = customer switch
{
    { IsActive: true, Age: >= 18 } => true,
    _ => false
};
```

#### Records (C# 9.0+)
```csharp
// Immutable data structures
public record Customer(int Id, string Name, string Email);

// With expressions
var updatedCustomer = customer with { Name = "New Name" };
```

#### Nullable Reference Types (C# 8.0+)
```csharp
#nullable enable

public class CustomerService
{
    // Cannot be null
    public string GetName(Customer customer)
    {
        return customer.Name;
    }
    
    // Can be null
    public string? GetMiddleName(Customer customer)
    {
        return customer.MiddleName;
    }
}
```

#### Init-Only Setters (C# 9.0+)
```csharp
public class Customer
{
    public int Id { get; init; }
    public string Name { get; init; }
}

var customer = new Customer { Id = 1, Name = "John" };
// customer.Id = 2; // Compilation error
```
