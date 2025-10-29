
# C++ Best Practices

## Code Organization and Structure

### Project Structure
```
project/
├── include/           # Public header files
│   └── mylib/
│       ├── module1.h
│       └── module2.h
├── src/              # Implementation files
│   ├── module1.cpp
│   ├── module2.cpp
│   └── main.cpp
├── tests/            # Test files
│   ├── test_module1.cpp
│   └── test_module2.cpp
├── lib/              # Third-party libraries
├── build/            # Build output (gitignored)
├── docs/             # Documentation
├── CMakeLists.txt    # CMake build configuration
├── .gitignore
└── README.md
```

### Header File Organization
```cpp
// myclass.h
#ifndef MYLIB_MYCLASS_H_  // Header guard (or use #pragma once)
#define MYLIB_MYCLASS_H_

// System headers
#include <string>
#include <vector>
#include <memory>

// Third-party headers
#include <boost/optional.hpp>

// Local headers
#include "mylib/utils.h"

namespace mylib {

/**
 * @brief Brief description of MyClass.
 * 
 * Detailed description of what MyClass does,
 * its purpose, and usage notes.
 */
class MyClass {
public:
    // Public interface first
    MyClass();
    explicit MyClass(int value);
    ~MyClass();
    
    // Prevent copying if not needed
    MyClass(const MyClass&) = delete;
    MyClass& operator=(const MyClass&) = delete;
    
    // Allow moving
    MyClass(MyClass&&) noexcept = default;
    MyClass& operator=(MyClass&&) noexcept = default;
    
    void doSomething();
    int getValue() const;

private:
    // Private implementation details last
    int value_;
    std::string name_;
    
    void helperFunction();
};

}  // namespace mylib

#endif  // MYLIB_MYCLASS_H_
```

### Implementation File Organization
```cpp
// myclass.cpp
#include "mylib/myclass.h"

#include <algorithm>
#include <iostream>

namespace mylib {

MyClass::MyClass() : value_(0), name_("default") {
    // Constructor implementation
}

MyClass::MyClass(int value) : value_(value), name_("") {
    if (value < 0) {
        throw std::invalid_argument("Value must be non-negative");
    }
}

MyClass::~MyClass() {
    // Destructor - cleanup resources
}

void MyClass::doSomething() {
    // Implementation
}

int MyClass::getValue() const {
    return value_;
}

void MyClass::helperFunction() {
    // Private helper implementation
}

}  // namespace mylib
```

## Naming Conventions

### General Rules
```cpp
// Namespaces: lowercase
namespace mylib {
namespace details {
}  // namespace details
}  // namespace mylib

// Classes/Structs/Enums: PascalCase
class UserAccount { };
struct Point2D { };
enum class Color { Red, Green, Blue };

// Functions/Methods: camelCase or snake_case (be consistent)
void doSomething();
int calculate_sum();

// Variables: camelCase or snake_case
int userCount = 0;
std::string user_name = "John";

// Member variables: trailing underscore
class MyClass {
private:
    int value_;
    std::string name_;
};

// Constants: kPascalCase or UPPER_SNAKE_CASE
const int kMaxUsers = 100;
constexpr int MAX_BUFFER_SIZE = 1024;

// Template parameters: PascalCase
template <typename T, typename Allocator>
class Container { };

// Macros: UPPER_SNAKE_CASE (avoid when possible)
#define MAX_SIZE 100

// File names: match class names
// UserAccount class -> UserAccount.h, UserAccount.cpp
// Or use snake_case: user_account.h, user_account.cpp
```

### Specific Patterns
```cpp
// Boolean variables/functions: use is/has/can prefix
bool isEmpty() const;
bool hasPermission() const;
bool canExecute() const;

// Getters/Setters
int getValue() const;        // Getter
void setValue(int value);    // Setter

// Factory functions
static std::unique_ptr<MyClass> create();
static MyClass makeDefault();

// Predicates
bool isValid(const std::string& str);
bool contains(int value) const;
```

## Error Handling Patterns

### Exception Handling
```cpp
#include <stdexcept>
#include <exception>

// Use standard exception types
void processFile(const std::string& filename) {
    if (filename.empty()) {
        throw std::invalid_argument("Filename cannot be empty");
    }
    
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open file: " + filename);
    }
    
    // Process file
}

// Custom exception classes
class FileProcessingError : public std::runtime_error {
public:
    explicit FileProcessingError(const std::string& filename)
        : std::runtime_error("Error processing file: " + filename),
          filename_(filename) {}
    
    const std::string& getFilename() const { return filename_; }

private:
    std::string filename_;
};

// Exception safety with RAII
void safeFunction() {
    auto resource = std::make_unique<Resource>();  // RAII
    
    try {
        riskyOperation();
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        throw;  // Re-throw to propagate
    }
    // resource automatically cleaned up
}
```

### Error Codes Pattern
```cpp
#include <system_error>

// For code that shouldn't throw
enum class ErrorCode {
    Success = 0,
    InvalidInput,
    FileNotFound,
    PermissionDenied
};

struct Result {
    ErrorCode code;
    std::string message;
    
    bool isSuccess() const { return code == ErrorCode::Success; }
    explicit operator bool() const { return isSuccess(); }
};

Result processData(const std::string& data) noexcept {
    if (data.empty()) {
        return {ErrorCode::InvalidInput, "Data cannot be empty"};
    }
    
    // Process data
    return {ErrorCode::Success, ""};
}

// Usage
if (auto result = processData(data); result) {
    // Success
} else {
    std::cerr << "Error: " << result.message << std::endl;
}
```

### std::optional and std::expected (C++23)
```cpp
#include <optional>

// Use optional for nullable return values
std::optional<User> findUser(int userId) {
    if (auto user = database.query(userId)) {
        return user;
    }
    return std::nullopt;
}

// Usage
if (auto user = findUser(123)) {
    std::cout << user->getName() << std::endl;
} else {
    std::cout << "User not found" << std::endl;
}

// C++23 std::expected for error handling
#include <expected>

std::expected<int, std::string> divide(int a, int b) {
    if (b == 0) {
        return std::unexpected("Division by zero");
    }
    return a / b;
}

// Usage
auto result = divide(10, 0);
if (result) {
    std::cout << "Result: " << *result << std::endl;
} else {
    std::cerr << "Error: " << result.error() << std::endl;
}
```

## Performance Considerations

### Memory Management
```cpp
// Prefer stack allocation
void stackAllocation() {
    std::vector<int> vec;  // Automatic storage
    std::string str;       // Automatic storage
    // Automatically cleaned up when out of scope
}

// Use smart pointers for heap allocation
#include <memory>

// Unique ownership
auto ptr = std::make_unique<MyClass>();

// Shared ownership
auto shared = std::make_shared<MyClass>();

// Avoid raw new/delete
// BAD:
MyClass* obj = new MyClass();
delete obj;

// GOOD:
auto obj = std::make_unique<MyClass>();
```

### Move Semantics
```cpp
// Implement move constructor and assignment
class MyClass {
public:
    // Move constructor
    MyClass(MyClass&& other) noexcept
        : data_(std::move(other.data_)) {
        other.data_ = nullptr;
    }
    
    // Move assignment
    MyClass& operator=(MyClass&& other) noexcept {
        if (this != &other) {
            delete data_;
            data_ = other.data_;
            other.data_ = nullptr;
        }
        return *this;
    }

private:
    int* data_;
};

// Use std::move for transferring ownership
std::vector<std::string> source;
std::vector<std::string> dest = std::move(source);  // source is now empty

// Return by value (RVO/NRVO)
std::vector<int> createVector() {
    std::vector<int> result;
    // Fill result
    return result;  // No copy, move or RVO
}
```

### Const Correctness
```cpp
class MyClass {
public:
    // Const member function - doesn't modify object
    int getValue() const {
        return value_;
    }
    
    // Non-const member function
    void setValue(int value) {
        value_ = value;
    }
    
    // Const parameters
    void processData(const std::string& data) {
        // data cannot be modified
    }
    
    // Const reference for large objects
    void process(const std::vector<int>& vec) const {
        // No copying, read-only access
    }

private:
    int value_;
};

// Const variables
const int MAX_SIZE = 100;
constexpr int BUFFER_SIZE = 1024;  // Compile-time constant
```

### Avoiding Copies
```cpp
// Pass by const reference for read-only
void processVector(const std::vector<int>& vec) {
    for (const auto& item : vec) {  // Reference to avoid copy
        // Process item
    }
}

// Pass by value when taking ownership
void storeString(std::string str) {  // Copy or move
    data_ = std::move(str);
}

// Return by value (rely on RVO)
std::vector<int> createVector() {
    std::vector<int> result;
    // ...
    return result;  // No copy!
}

// Use string_view for string parameters (C++17)
#include <string_view>

void processString(std::string_view str) {
    // No allocation, view into existing string
}
```

### Template Metaprogramming
```cpp
// Use templates for compile-time polymorphism
template <typename T>
T max(T a, T b) {
    return (a > b) ? a : b;
}

// Constexpr for compile-time computation
constexpr int factorial(int n) {
    return (n <= 1) ? 1 : n * factorial(n - 1);
}

constexpr int result = factorial(5);  // Computed at compile time

// Use concepts (C++20) for template constraints
#include <concepts>

template <typename T>
concept Numeric = std::is_arithmetic_v<T>;

template <Numeric T>
T add(T a, T b) {
    return a + b;
}
```

## Security Best Practices

### Buffer Safety
```cpp
// Use std::string and std::vector instead of C arrays
// BAD:
char buffer[100];
strcpy(buffer, userInput);  // Buffer overflow risk

// GOOD:
std::string buffer = userInput;

// Use std::array for fixed-size arrays
#include <array>
std::array<int, 100> arr;  // Size known at compile time

// Bounds checking with at()
std::vector<int> vec = {1, 2, 3};
try {
    int value = vec.at(10);  // Throws std::out_of_range
} catch (const std::out_of_range& e) {
    std::cerr << "Index out of range" << std::endl;
}
```

### Input Validation
```cpp
#include <regex>

bool validateEmail(const std::string& email) {
    static const std::regex pattern(
        R"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})");
    return std::regex_match(email, pattern);
}

bool validateInteger(const std::string& str) {
    try {
        std::size_t pos;
        int value = std::stoi(str, &pos);
        return pos == str.length();  // Entire string is valid
    } catch (...) {
        return false;
    }
}

// Sanitize input
std::string sanitizePath(const std::string& path) {
    std::string sanitized;
    for (char c : path) {
        if (std::isalnum(c) || c == '/' || c == '.') {
            sanitized += c;
        }
    }
    return sanitized;
}
```

### Secure String Handling
```cpp
// Use secure string operations
#include <algorithm>

// Clear sensitive data
void clearSensitiveData(std::string& data) {
    std::fill(data.begin(), data.end(), '\0');
    data.clear();
}

// Or use secure_string (if available)
// secure_string password;
// Automatically zeroed on destruction
```

### Avoid Common Vulnerabilities
```cpp
// Integer overflow checking
#include <limits>

bool safeMultiply(int a, int b, int& result) {
    if (a > 0 && b > 0 && a > std::numeric_limits<int>::max() / b) {
        return false;  // Overflow would occur
    }
    result = a * b;
    return true;
}

// Use std::span for safe array access (C++20)
#include <span>

void processArray(std::span<const int> data) {
    // Safe access to array-like data
    for (int value : data) {
        // Process value
    }
}
```

## Testing Approaches

### Unit Testing with Google Test
```cpp
#include <gtest/gtest.h>

// Test fixture
class MyClassTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Setup before each test
        obj_ = std::make_unique<MyClass>();
    }
    
    void TearDown() override {
        // Cleanup after each test
        obj_.reset();
    }
    
    std::unique_ptr<MyClass> obj_;
};

// Test cases
TEST_F(MyClassTest, InitializesWithZero) {
    EXPECT_EQ(0, obj_->getValue());
}

TEST_F(MyClassTest, SetValueWorks) {
    obj_->setValue(42);
    EXPECT_EQ(42, obj_->getValue());
}

TEST_F(MyClassTest, ThrowsOnInvalidInput) {
    EXPECT_THROW({
        MyClass invalid(-1);
    }, std::invalid_argument);
}

// Parameterized tests
class CalculatorTest : public ::testing::TestWithParam<std::tuple<int, int, int>> {
};

TEST_P(CalculatorTest, Addition) {
    auto [a, b, expected] = GetParam();
    EXPECT_EQ(expected, add(a, b));
}

INSTANTIATE_TEST_SUITE_P(
    AdditionTests,
    CalculatorTest,
    ::testing::Values(
        std::make_tuple(1, 2, 3),
        std::make_tuple(0, 0, 0),
        std::make_tuple(-1, 1, 0)
    )
);
```

### Mock Objects
```cpp
#include <gmock/gmock.h>

// Interface to mock
class Database {
public:
    virtual ~Database() = default;
    virtual User getUser(int id) = 0;
    virtual void saveUser(const User& user) = 0;
};

// Mock implementation
class MockDatabase : public Database {
public:
    MOCK_METHOD(User, getUser, (int id), (override));
    MOCK_METHOD(void, saveUser, (const User& user), (override));
};

// Test using mock
TEST(UserServiceTest, GetUserCallsDatabase) {
    MockDatabase mockDb;
    UserService service(&mockDb);
    
    User expectedUser("John");
    EXPECT_CALL(mockDb, getUser(123))
        .WillOnce(::testing::Return(expectedUser));
    
    auto user = service.getUserById(123);
    EXPECT_EQ("John", user.getName());
}
```

### Test-Driven Development
```cpp
// 1. Write test first (it will fail)
TEST(StringUtils, TrimsWhitespace) {
    EXPECT_EQ("hello", trim("  hello  "));
    EXPECT_EQ("world", trim("world\n"));
    EXPECT_EQ("", trim("   "));
}

// 2. Implement function to pass test
std::string trim(const std::string& str) {
    size_t start = str.find_first_not_of(" \t\n\r");
    if (start == std::string::npos) return "";
    
    size_t end = str.find_last_not_of(" \t\n\r");
    return str.substr(start, end - start + 1);
}

// 3. Refactor if needed
```

## Documentation Standards

### Doxygen Comments
```cpp
/**
 * @file myclass.h
 * @brief Brief description of file
 * @author Your Name
 * @date 2024-01-01
 */

/**
 * @class MyClass
 * @brief Brief description of MyClass
 * 
 * Detailed description of what MyClass does,
 * its purpose, and usage examples.
 * 
 * @code
 * MyClass obj(42);
 * obj.doSomething();
 * int value = obj.getValue();
 * @endcode
 */
class MyClass {
public:
    /**
     * @brief Constructs MyClass with a value
     * 
     * @param value Initial value (must be non-negative)
     * @throws std::invalid_argument if value is negative
     */
    explicit MyClass(int value);
    
    /**
     * @brief Performs an operation
     * 
     * Detailed description of what doSomething does,
     * any side effects, and important notes.
     * 
     * @return true if successful, false otherwise
     * @note This function is thread-safe
     */
    bool doSomething();
    
    /**
     * @brief Gets the current value
     * 
     * @return Current value
     * @see setValue()
     */
    int getValue() const;
    
    /**
     * @brief Sets a new value
     * 
     * @param value New value to set
     * @pre value must be non-negative
     * @post getValue() returns the new value
     */
    void setValue(int value);

private:
    int value_;  ///< Current value (non-negative)
};
```

### Inline Comments
```cpp
// Use comments to explain why, not what
// BAD:
counter++;  // Increment counter

// GOOD:
counter++;  // Track retry attempts for exponential backoff

// Complex algorithms need explanation
/**
 * Implementation of Quicksort algorithm.
 * Time complexity: O(n log n) average, O(n²) worst case
 * Space complexity: O(log n) due to recursion
 */
template <typename T>
void quicksort(std::vector<T>& arr, int low, int high) {
    // Implementation
}
```

## Common Pitfalls to Avoid

### 1. Memory Leaks
```cpp
// BAD: Manual memory management
MyClass* obj = new MyClass();
// ... (exception thrown, obj never deleted)
delete obj;

// GOOD: Use smart pointers
auto obj = std::make_unique<MyClass>();
// Automatically cleaned up
```

### 2. Dangling Pointers
```cpp
// BAD:
int* getPointer() {
    int x = 42;
    return &x;  // Dangling pointer!
}

// GOOD:
int getValue() {
    int x = 42;
    return x;  // Return by value
}
```

### 3. Uninitialized Variables
```cpp
// BAD:
int value;  // Uninitialized
std::cout << value << std::endl;  // Undefined behavior

// GOOD:
int value = 0;  // Initialized
// Or use member initializer lists
MyClass::MyClass() : value_(0), name_("") { }
```

### 4. Incorrect Copy/Move
```cpp
// BAD: Implicit copy can be expensive
std::vector<int> getLargeVector() {
    return largeVector;
}
std::vector<int> copy = getLargeVector();  // Unnecessary copy

// GOOD: Use move semantics
std::vector<int> moved = std::move(largeVector);
```

### 5. Iterator Invalidation
```cpp
// BAD:
std::vector<int> vec = {1, 2, 3, 4, 5};
for (auto it = vec.begin(); it != vec.end(); ++it) {
    if (*it == 3) {
        vec.erase(it);  // Invalidates iterator!
    }
}

// GOOD:
vec.erase(
    std::remove(vec.begin(), vec.end(), 3),
    vec.end()
);
```

## Language-Specific Idioms and Patterns

### RAII (Resource Acquisition Is Initialization)
```cpp
// RAII for file handling
class FileHandler {
public:
    explicit FileHandler(const std::string& filename)
        : file_(filename) {
        if (!file_.is_open()) {
            throw std::runtime_error("Failed to open file");
        }
    }
    
    ~FileHandler() {
        // File automatically closed
    }
    
    std::ifstream& get() { return file_; }

private:
    std::ifstream file_;
};

// Usage
void processFile(const std::string& filename) {
    FileHandler handler(filename);
    // Use handler.get()
    // File automatically closed when handler goes out of scope
}
```

### Rule of Zero/Three/Five
```cpp
// Rule of Zero: If you don't need custom resource management,
// don't define any special member functions
class SimpleClass {
    std::string name_;
    std::vector<int> data_;
    // Compiler-generated special members are fine
};

// Rule of Five: If you need custom resource management,
// define all five special member functions
class ResourceClass {
public:
    ResourceClass();  // Constructor
    ~ResourceClass();  // Destructor
    ResourceClass(const ResourceClass&);  // Copy constructor
    ResourceClass& operator=(const ResourceClass&);  // Copy assignment
    ResourceClass(ResourceClass&&) noexcept;  // Move constructor
    ResourceClass& operator=(ResourceClass&&) noexcept;  // Move assignment

private:
    int* data_;
};
```

### STL Algorithms
```cpp
#include <algorithm>
#include <numeric>

std::vector<int> vec = {1, 2, 3, 4, 5};

// Find
auto it = std::find(vec.begin(), vec.end(), 3);
if (it != vec.end()) {
    std::cout << "Found: " << *it << std::endl;
}

// Find with predicate
auto even = std::find_if(vec.begin(), vec.end(), 
    [](int x) { return x % 2 == 0; });

// Transform
std::vector<int> doubled;
std::transform(vec.begin(), vec.end(), std::back_inserter(doubled),
    [](int x) { return x * 2; });

// Accumulate
int sum = std::accumulate(vec.begin(), vec.end(), 0);

// Sort
std::sort(vec.begin(), vec.end());

// Remove-erase idiom
vec.erase(
    std::remove_if(vec.begin(), vec.end(), 
        [](int x) { return x % 2 == 0; }),
    vec.end()
);
```

### Modern C++ Features

#### Lambda Expressions
```cpp
// Basic lambda
auto add = [](int a, int b) { return a + b; };

// Capture by value
int multiplier = 10;
auto multiply = [multiplier](int x) { return x * multiplier; };

// Capture by reference
int counter = 0;
auto increment = [&counter]() { counter++; };

// Capture all by value/reference
auto captureAll = [=]() { /* All by value */ };
auto captureAllRef = [&]() { /* All by reference */ };

// Generic lambda (C++14)
auto generic = [](auto x, auto y) { return x + y; };

// Lambda with trailing return type
auto divide = [](int a, int b) -> double {
    return static_cast<double>(a) / b;
};
```

#### Structured Bindings (C++17)
```cpp
// Tuple decomposition
std::tuple<int, std::string, double> getData() {
    return {42, "hello", 3.14};
}

auto [id, name, value] = getData();

// Pair decomposition
std::map<std::string, int> map;
for (const auto& [key, value] : map) {
    std::cout << key << ": " << value << std::endl;
}

// Struct decomposition
struct Point { int x; int y; };
Point p{10, 20};
auto [x, y] = p;
```

#### Ranges (C++20)
```cpp
#include <ranges>

std::vector<int> vec = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

// Filter and transform with ranges
auto result = vec 
    | std::views::filter([](int x) { return x % 2 == 0; })
    | std::views::transform([](int x) { return x * 2; });

for (int value : result) {
    std::cout << value << " ";
}
```

#### Coroutines (C++20)
```cpp
#include <coroutine>

// Generator example
template <typename T>
struct Generator {
    struct promise_type {
        T current_value;
        
        auto get_return_object() {
            return Generator{std::coroutine_handle<promise_type>::from_promise(*this)};
        }
        
        auto initial_suspend() { return std::suspend_always{}; }
        auto final_suspend() noexcept { return std::suspend_always{}; }
        
        auto yield_value(T value) {
            current_value = value;
            return std::suspend_always{};
        }
        
        void return_void() {}
        void unhandled_exception() { std::terminate(); }
    };
    
    std::coroutine_handle<promise_type> handle;
    
    Generator(std::coroutine_handle<promise_type> h) : handle(h) {}
    ~Generator() { if (handle) handle.destroy(); }
    
    bool move_next() {
        handle.resume();
        return !handle.done();
    }
    
    T current_value() {
        return handle.promise().current_value;
    }
};

Generator<int> fibonacci(int n) {
    int a = 0, b = 1;
    for (int i = 0; i < n; ++i) {
        co_yield a;
        auto temp = a;
        a = b;
        b = temp + b;
    }
}
```

### Design Patterns

#### Singleton
```cpp
class Singleton {
public:
    static Singleton& getInstance() {
        static Singleton instance;  // Thread-safe in C++11+
        return instance;
    }
    
    // Delete copy and move
    Singleton(const Singleton&) = delete;
    Singleton& operator=(const Singleton&) = delete;

private:
    Singleton() = default;
};
```

#### Factory
```cpp
class Shape {
public:
    virtual ~Shape() = default;
    virtual void draw() const = 0;
};

class Circle : public Shape {
public:
    void draw() const override {
        std::cout << "Drawing circle" << std::endl;
    }
};

class Square : public Shape {
public:
    void draw() const override {
        std::cout << "Drawing square" << std::endl;
    }
};

class ShapeFactory {
public:
    static std::unique_ptr<Shape> createShape(const std::string& type) {
        if (type == "circle") {
            return std::make_unique<Circle>();
        } else if (type == "square") {
            return std::make_unique<Square>();
        }
        return nullptr;
    }
};
```

#### Observer
```cpp
class Observer {
public:
    virtual ~Observer() = default;
    virtual void update(const std::string& message) = 0;
};

class Subject {
public:
    void attach(std::shared_ptr<Observer> observer) {
        observers_.push_back(observer);
    }
    
    void notify(const std::string& message) {
        for (auto& observer : observers_) {
            if (auto obs = observer.lock()) {
                obs->update(message);
            }
        }
    }

private:
    std::vector<std::weak_ptr<Observer>> observers_;
};
```
